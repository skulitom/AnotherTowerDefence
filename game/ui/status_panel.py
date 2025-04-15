import pygame
from game.utils import draw_gradient_rect, create_element_icon, draw_panel_background
from game.settings import tower_types

class StatusPanel:
    def __init__(self, rect):
        self.rect = rect
        self.money = 0
        self.lives = 0
        self.selected_tower_type = None
        self.tower_placement_mode = False
        self.placement_rect = None  # Rectangle for the placement mode text for click detection
    
    def update(self, money, lives, selected_tower_type, tower_placement_mode=False):
        self.money = money
        self.lives = lives
        self.selected_tower_type = selected_tower_type
        self.tower_placement_mode = tower_placement_mode
    
    def draw(self, surface, assets):
        # Get fonts from assets
        font_title = assets["fonts"].get("title")
        font_info = assets["fonts"].get("body")
        font_small = assets["fonts"].get("body_small")
        
        # Draw panel background using the utility function, pass the title font
        content_y = draw_panel_background(surface, self.rect, title="Resources", font=font_title)
        
        icon_size = 20
        icon_padding = 5
        text_padding = 8
        line_spacing = 10 # Spacing between lines
        
        # Draw money with icon
        money_icon = assets["ui"].get("money_icon")
        money_text = f"${self.money}" # Changed format slightly
        money_surf = font_info.render(money_text, True, (255, 255, 100))
        
        # Calculate positions
        total_width = (icon_size if money_icon else 0) + text_padding + money_surf.get_width()
        start_x = self.rect.centerx - total_width // 2
        
        if money_icon:
            money_icon_rect = money_icon.get_rect(midleft=(start_x, content_y + money_surf.get_height() // 2))
            surface.blit(money_icon, money_icon_rect)
            text_x = money_icon_rect.right + text_padding
        else:
            text_x = start_x
        
        money_rect = money_surf.get_rect(midleft=(text_x, content_y + money_surf.get_height() // 2))
        surface.blit(money_surf, money_rect)
        
        content_y += money_surf.get_height() + line_spacing
        
        # Draw lives with icon
        lives_icon = assets["ui"].get("lives_icon")
        lives_text = f"{self.lives}" # Just the number
        lives_color = (255, 255, 255) if self.lives > 5 else (255, 100, 100)
        lives_surf = font_info.render(lives_text, True, lives_color)
        
        # Calculate positions
        total_width = (icon_size if lives_icon else 0) + text_padding + lives_surf.get_width()
        start_x = self.rect.centerx - total_width // 2
        
        if lives_icon:
            lives_icon_rect = lives_icon.get_rect(midleft=(start_x, content_y + lives_surf.get_height() // 2))
            surface.blit(lives_icon, lives_icon_rect)
            text_x = lives_icon_rect.right + text_padding
        else:
            text_x = start_x
            
        lives_rect = lives_surf.get_rect(midleft=(text_x, content_y + lives_surf.get_height() // 2))
        surface.blit(lives_surf, lives_rect)
        
        content_y += lives_surf.get_height() + line_spacing * 1.5 # Add extra spacing before next section
        
        # Draw placement mode status (clickable)
        placement_text = f"Placement Mode: {'ON' if self.tower_placement_mode else 'OFF'}"
        placement_color = (100, 255, 100) if self.tower_placement_mode else (200, 200, 200)
        placement_surf = font_info.render(placement_text, True, placement_color)
        self.placement_rect = placement_surf.get_rect(midtop=(self.rect.centerx, content_y))
        
        # Draw highlight if this is clickable
        if self.placement_rect.collidepoint(pygame.mouse.get_pos()):
            # Draw a highlight behind the text
            highlight_rect = self.placement_rect.inflate(10, 4)
            pygame.draw.rect(surface, (60, 60, 80), highlight_rect, 0, 3)
            pygame.draw.rect(surface, (100, 100, 140), highlight_rect, 1, 3)
        
        surface.blit(placement_surf, self.placement_rect)
        
        # Draw selected tower information
        if self.selected_tower_type:
            selected_y = self.placement_rect.bottom + line_spacing * 2 # Use line spacing
            
            selected_text = f"Selected Tower:"
            selected_surf = font_info.render(selected_text, True, (255, 255, 255))
            selected_rect = selected_surf.get_rect(midtop=(self.rect.centerx, selected_y))
            surface.blit(selected_surf, selected_rect)
            
            # Draw tower icon
            tower_img_list = assets["towers"].get(self.selected_tower_type)
            tower_img = tower_img_list[0] if tower_img_list else None # Get the base sprite (index 0)
            
            if tower_img:
                # Now tower_img is a Surface, safe to scale
                img = pygame.transform.scale(tower_img, (48, 48))
                img_rect = img.get_rect(midtop=(self.rect.centerx, selected_rect.bottom + 5))
                surface.blit(img, img_rect)
            else:
                icon = create_element_icon(self.selected_tower_type, 48)
                icon_rect = icon.get_rect(midtop=(self.rect.centerx, selected_rect.bottom + 5))
                surface.blit(icon, icon_rect)
            
            # Draw tower cost
            cost = tower_types[self.selected_tower_type]["cost"]
            cost_text = f"Cost: ${cost}"
            cost_color = (255, 255, 255) if self.money >= cost else (255, 100, 100)
            cost_surf = font_info.render(cost_text, True, cost_color)
            # Adjust positioning based on whether img or icon was drawn
            cost_rect_top = (img_rect.bottom if tower_img else icon_rect.bottom) + 10
            cost_rect = cost_surf.get_rect(midtop=(self.rect.centerx, cost_rect_top))
            surface.blit(cost_surf, cost_rect)
            
            # Draw tower description with text wrapping
            description = tower_types[self.selected_tower_type].get("description", "")
            desc_color = (200, 200, 200)
            line_spacing = 2 # Extra pixels between lines
            line_height = font_small.get_linesize() + line_spacing
            max_width = self.rect.width - 20 # Allow 10px padding on each side
            
            words = description.split(' ')
            lines = []
            current_line = ""
            
            for word in words:
                # Test adding the new word
                test_line = current_line + word + " "
                test_surf = font_small.render(test_line, True, desc_color)
                
                if test_surf.get_width() <= max_width:
                    current_line = test_line
                else:
                    # Add the previous line to the list
                    lines.append(current_line.strip())
                    # Start new line with the current word
                    current_line = word + " "
            
            # Add the last line
            lines.append(current_line.strip())
            
            # Render and blit each line
            desc_y = cost_rect.bottom + 10
            for line in lines:
                if not line: continue # Skip empty lines if any
                line_surf = font_small.render(line, True, desc_color)
                # Center each line horizontally within the panel
                line_rect = line_surf.get_rect(midtop=(self.rect.centerx, desc_y))
                surface.blit(line_surf, line_rect)
                desc_y += line_height

    def handle_event(self, event):
        """Handle mouse events on the status panel"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            # Check if clicked on placement mode text
            if self.placement_rect and self.placement_rect.collidepoint(event.pos):
                return {"action": "toggle_placement_mode"}
        
        return {"action": None} 