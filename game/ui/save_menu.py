"""
Save Game Menu - UI component for managing game saves
"""
import pygame
import os
from datetime import datetime
from game.ui.button import Button

class SaveGameMenu:
    def __init__(self, screen_width, screen_height, game_manager):
        """Initialize the save game menu"""
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.game = game_manager
        self.visible = False
        self.menu_type = "save"  # "save" or "load"
        
        # Calculate menu dimensions
        self.width = int(screen_width * 0.6)
        self.height = int(screen_height * 0.7)
        self.x = (screen_width - self.width) // 2
        self.y = (screen_height - self.height) // 2
        
        # Fonts
        self.title_font = pygame.font.SysFont(None, 32)
        self.item_font = pygame.font.SysFont(None, 24)
        self.detail_font = pygame.font.SysFont(None, 18)
        
        # Colors
        self.bg_color = (30, 30, 40, 200)
        self.title_color = (220, 220, 220)
        self.item_color = (200, 200, 200)
        self.highlight_color = (100, 180, 255)
        self.button_color = (80, 80, 100)
        
        # Save list
        self.save_files = []
        self.selected_save = None
        self.scroll_offset = 0
        self.max_visible_saves = 8
        
        # Create buttons
        self.create_buttons()
        
    def create_buttons(self):
        """Create UI buttons"""
        button_width = 120
        button_height = 40
        button_margin = 20
        button_y = self.y + self.height - button_height - button_margin
        
        # Create button rectangles for hit testing
        # Close button (right)
        close_x = self.x + self.width - button_width - button_margin
        self.close_rect = pygame.Rect(close_x, button_y, button_width, button_height)
        
        # Action button (left) - changes based on menu type
        action_x = self.x + button_margin
        self.action_rect = pygame.Rect(action_x, button_y, button_width, button_height)
        
        # Delete button (middle)
        delete_x = self.x + (self.width - button_width) // 2
        self.delete_rect = pygame.Rect(delete_x, button_y, button_width, button_height)
        
        # Scroll buttons
        scroll_button_size = 30
        scroll_y_up = self.y + 50
        scroll_y_down = self.y + self.height - button_height - button_margin - 50
        
        self.scroll_up_rect = pygame.Rect(
            self.x + self.width - scroll_button_size - 10, 
            scroll_y_up, 
            scroll_button_size, 
            scroll_button_size
        )
        
        self.scroll_down_rect = pygame.Rect(
            self.x + self.width - scroll_button_size - 10, 
            scroll_y_down, 
            scroll_button_size, 
            scroll_button_size
        )
        
        # Create visual button objects that match these rectangles
        self.close_button = Button(
            self.close_rect,
            "Close", (220, 220, 220), self.button_color
        )
        
        # Action button (left) - changes based on menu type
        self.action_button = Button(
            self.action_rect,
            "Save Game", (220, 220, 220), (80, 120, 80)
        )
        
        # Delete button (middle)
        self.delete_button = Button(
            self.delete_rect,
            "Delete Save", (220, 220, 220), (150, 80, 80)
        )
        
        # Scroll buttons
        self.scroll_up_button = Button(
            self.scroll_up_rect,
            "▲", (220, 220, 220), self.button_color
        )
        
        self.scroll_down_button = Button(
            self.scroll_down_rect,
            "▼", (220, 220, 220), self.button_color
        )
    
    def show(self, menu_type="save"):
        """Show the menu with specified type"""
        self.visible = True
        self.menu_type = menu_type
        self.selected_save = None
        self.scroll_offset = 0
        
        print(f"Save menu shown in {menu_type} mode")
        
        # Update button text based on menu type
        if menu_type == "save":
            self.action_button.text = "Save Game"
            self.action_button.bg_color = (80, 120, 80)  # Green
        else:  # "load"
            self.action_button.text = "Load Game"
            self.action_button.bg_color = (80, 80, 160)  # Blue
        
        # Update save files list
        self.refresh_save_files()
        
    def hide(self):
        """Hide the menu"""
        print("Save menu hidden")
        self.visible = False
        
    def refresh_save_files(self):
        """Refresh the list of save files"""
        self.save_files = self.game.get_save_files()
        # Sort by date, newest first
        self.save_files.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
    def draw(self, surface):
        """Draw the menu"""
        if not self.visible:
            return
        
        # Create a semi-transparent background
        menu_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        menu_surface.fill(self.bg_color)
        
        # Draw title
        title_text = f"{self.menu_type.capitalize()} Game"
        title_surface = self.title_font.render(title_text, True, self.title_color)
        title_x = (self.width - title_surface.get_width()) // 2
        menu_surface.blit(title_surface, (title_x, 20))
        
        # Draw save file list
        list_y_start = 70
        item_height = 60
        
        if not self.save_files:
            # Show message if no saves
            no_saves_text = "No saved games found."
            no_saves_surface = self.item_font.render(no_saves_text, True, self.item_color)
            no_saves_x = (self.width - no_saves_surface.get_width()) // 2
            menu_surface.blit(no_saves_surface, (no_saves_x, list_y_start + 30))
        else:
            # Draw visible saves
            visible_range = min(self.max_visible_saves, len(self.save_files) - self.scroll_offset)
            
            for i in range(visible_range):
                save_index = i + self.scroll_offset
                if save_index >= len(self.save_files):
                    break
                    
                save = self.save_files[save_index]
                
                # Item rectangle
                item_y = list_y_start + (i * item_height)
                item_rect = pygame.Rect(20, item_y, self.width - 60, item_height - 5)
                
                # Highlight selected item
                if self.selected_save == save_index:
                    pygame.draw.rect(menu_surface, self.highlight_color, item_rect)
                
                # Draw border
                pygame.draw.rect(menu_surface, self.item_color, item_rect, 1)
                
                # Draw save file info
                save_name = save.get("filename", "Unknown Save")
                timestamp = save.get("timestamp", "Unknown Date")
                wave = save.get("wave", 0)
                score = save.get("score", 0)
                
                # Filename
                name_surface = self.item_font.render(save_name, True, self.item_color)
                menu_surface.blit(name_surface, (item_rect.x + 10, item_rect.y + 5))
                
                # Details
                details_text = f"Wave: {wave} | Score: {score} | {timestamp}"
                details_surface = self.detail_font.render(details_text, True, self.item_color)
                menu_surface.blit(details_surface, (item_rect.x + 10, item_rect.y + 35))
        
        # Draw buttons
        self.close_button.draw(menu_surface)
        
        # Only show action and delete buttons if relevant
        if self.menu_type == "save" or (self.menu_type == "load" and self.selected_save is not None):
            self.action_button.draw(menu_surface)
        
        if self.selected_save is not None:
            self.delete_button.draw(menu_surface)
        
        # Draw scroll buttons if needed
        if len(self.save_files) > self.max_visible_saves:
            self.scroll_up_button.draw(menu_surface)
            self.scroll_down_button.draw(menu_surface)
        
        # Finally, draw the menu surface on the screen
        surface.blit(menu_surface, (self.x, self.y))
    
    def handle_event(self, event):
        """Handle UI events"""
        if not self.visible:
            return False
        
        # Mouse position for hit testing
        mouse_pos = pygame.mouse.get_pos()
        
        # For save file selection, use relative position
        rel_pos = (mouse_pos[0] - self.x, mouse_pos[1] - self.y)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Direct hit testing using rectangles instead of Button.update
            print(f"Mouse click at: {mouse_pos}")
            print(f"Close button rect: {self.close_rect}")
            print(f"Action button rect: {self.action_rect}")
            
            # Check button clicks using direct rectangle collision
            if self.close_rect.collidepoint(mouse_pos):
                print("Close button clicked")
                self.hide()
                return True
            
            if self.action_rect.collidepoint(mouse_pos):
                print(f"Action button clicked ({self.menu_type})")
                self.perform_action()
                return True
            
            if self.delete_rect.collidepoint(mouse_pos) and self.selected_save is not None:
                print("Delete button clicked")
                self.delete_save()
                return True
            
            # Check scroll buttons
            if len(self.save_files) > self.max_visible_saves:
                if self.scroll_up_rect.collidepoint(mouse_pos) and self.scroll_offset > 0:
                    self.scroll_offset -= 1
                    return True
                
                if self.scroll_down_rect.collidepoint(mouse_pos) and \
                   self.scroll_offset < len(self.save_files) - self.max_visible_saves:
                    self.scroll_offset += 1
                    return True
                    
            # Check if clicking on a save file
            list_y_start = 70
            item_height = 60
            visible_range = min(self.max_visible_saves, len(self.save_files) - self.scroll_offset)
            
            for i in range(visible_range):
                save_index = i + self.scroll_offset
                if save_index >= len(self.save_files):
                    break
                
                item_y = list_y_start + (i * item_height)
                item_rect = pygame.Rect(20, item_y, self.width - 60, item_height - 5)
                
                if item_rect.collidepoint(rel_pos):
                    self.selected_save = save_index
                    return True
        
        # Mousewheel scrolling
        if event.type == pygame.MOUSEWHEEL and len(self.save_files) > self.max_visible_saves:
            self.scroll_offset = max(0, min(self.scroll_offset - event.y, 
                                           len(self.save_files) - self.max_visible_saves))
            return True
            
        # Handle keyboard events
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.hide()
                return True
                
        return True  # Event was handled
    
    def perform_action(self):
        """Perform the main action (save or load)"""
        print(f"Performing action: {self.menu_type}")
        
        if self.menu_type == "save":
            # Save game
            print("Attempting to save game...")
            success = self.game.save_game()
            print(f"Save result: {success}")
            if success:
                self.refresh_save_files()
                self.hide()
        elif self.menu_type == "load" and self.selected_save is not None:
            # Load game
            save_filepath = self.save_files[self.selected_save]["filepath"]
            print(f"Attempting to load game from: {save_filepath}")
            success = self.game.load_game(save_filepath)
            print(f"Load result: {success}")
            if success:
                self.hide()
    
    def delete_save(self):
        """Delete selected save file"""
        if self.selected_save is None or self.selected_save >= len(self.save_files):
            return
        
        save_filepath = self.save_files[self.selected_save]["filepath"]
        
        try:
            os.remove(save_filepath)
            self.refresh_save_files()
            self.selected_save = None
            
            # Update scroll offset if list is shorter now
            if self.scroll_offset > 0 and self.scroll_offset >= len(self.save_files) - self.max_visible_saves:
                self.scroll_offset = max(0, len(self.save_files) - self.max_visible_saves)
        except Exception as e:
            print(f"Error deleting save file: {e}")
    
    def update_screen_size(self, screen_width, screen_height):
        """Update menu dimensions based on new screen size"""
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Recalculate dimensions
        self.width = int(screen_width * 0.6)
        self.height = int(screen_height * 0.7)
        self.x = (screen_width - self.width) // 2
        self.y = (screen_height - self.height) // 2
        
        # Recreate buttons with new positions
        self.create_buttons() 