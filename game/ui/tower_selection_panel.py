import pygame
from game.utils import draw_gradient_rect, draw_panel_background
from game.settings import tower_types
from game.ui.button import Button

class TowerSelectionPanel:
    def __init__(self, rect):
        self.rect = rect
        self.font = pygame.font.SysFont(None, 24)
        self.tower_buttons = []
        self.selected_tower = None
        self.saveload_button = None
        self.create_buttons()
        
    def create_buttons(self):
        # Calculate optimal button sizes based on panel dimensions
        num_towers = 7  # Fire, Water, Air, Earth, Darkness, Light, Life
        
        # Calculate available space after accounting for title and save/load button
        title_height = 30
        saveload_height = 35  # Height for the save/load button
        available_height = self.rect.height - title_height - saveload_height - 30  # 30px padding (20 at bottom + 10 between buttons)
        
        # Calculate optimal button height and spacing
        max_button_height = 40
        min_button_height = 25
        ideal_total_height = num_towers * max_button_height + (num_towers - 1) * 10  # 10px spacing
        
        if ideal_total_height <= available_height:
            # Can use max button height with plenty of spacing
            button_height = max_button_height
            button_spacing = min(12, (available_height - (num_towers * button_height)) / (num_towers - 1))
        else:
            # Need to adjust button height and spacing
            button_height = min(max_button_height, max(min_button_height, available_height / (num_towers * 1.2)))
            button_spacing = min(8, (available_height - (num_towers * button_height)) / (num_towers - 1))
            button_spacing = max(3, button_spacing)  # Ensure minimum spacing
            
        button_width = self.rect.width - 20
        
        # Create tower selection buttons
        self.tower_buttons = []
        tower_order = ["Fire", "Water", "Air", "Earth", "Darkness", "Light", "Life"]
        
        for i, tower_type in enumerate(tower_order):
            y_pos = self.rect.y + title_height + 10 + i * (button_height + button_spacing)
            button_rect = pygame.Rect(self.rect.x + 10, y_pos, button_width, button_height)
            
            cost = tower_types[tower_type]["cost"]
            button = Button(
                button_rect, 
                f"{tower_type} (${cost})", 
                color=(60, 60, 100),
                hover_color=(80, 80, 150),
                tooltip=tower_types[tower_type].get("description", ""),
                icon=tower_type,
                font_size=min(18, int(button_height * 0.45))  # Scale font to button size
            )
            self.tower_buttons.append((tower_type, button))
            
        # Create save/load button at bottom
        saveload_y = self.rect.y + self.rect.height - saveload_height - 10
        saveload_rect = pygame.Rect(self.rect.x + 10, saveload_y, button_width, saveload_height)
        self.saveload_button = Button(
            saveload_rect,
            "Save/Load Game",
            color=(80, 100, 80),
            hover_color=(100, 150, 100),
            tooltip="Open the save and load game dialog",
            font_size=min(18, int(saveload_height * 0.5))
        )
    
    def update(self, selected_tower, money):
        self.selected_tower = selected_tower
        
        # Update button appearance based on selection and affordability
        for tower_type, button in self.tower_buttons:
            # Change color if selected
            if tower_type == selected_tower:
                button.color = (100, 100, 180)
                button.hover_color = (120, 120, 220)
            else:
                button.color = (60, 60, 100)
                button.hover_color = (80, 80, 150)
            
            # Enable/disable based on affordability
            cost = tower_types[tower_type]["cost"]
            button.enabled = money >= cost
    
    def draw(self, surface):
        # Draw panel background with title
        draw_panel_background(surface, self.rect, title="Tower Selection")
        
        # Draw tower buttons
        for _, button in self.tower_buttons:
            button.draw(surface)
            
        # Draw save/load button
        if self.saveload_button:
            self.saveload_button.draw(surface)
    
    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
        
        # Check tower buttons
        for tower_type, button in self.tower_buttons:
            if button.update(mouse_pos, mouse_pressed):
                return tower_type
                
        # Check save/load button
        if self.saveload_button and self.saveload_button.update(mouse_pos, mouse_pressed):
            return "save_load"
                
        return None 