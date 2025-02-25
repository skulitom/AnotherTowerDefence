import pygame
from game.utils import draw_gradient_rect, create_element_icon, draw_panel_background
from game.settings import tower_types

class StatusPanel:
    def __init__(self, rect):
        self.rect = rect
        self.font_title = pygame.font.SysFont(None, 28)
        self.font_info = pygame.font.SysFont(None, 24)
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
        # Draw panel background using the utility function
        content_y = draw_panel_background(surface, self.rect, title="Resources")
        
        # Draw money
        money_text = f"Money: ${self.money}"
        money_surf = self.font_info.render(money_text, True, (255, 255, 100))
        money_rect = money_surf.get_rect(midtop=(self.rect.centerx, content_y))
        surface.blit(money_surf, money_rect)
        
        # Draw lives
        lives_text = f"Lives: {self.lives}"
        lives_color = (255, 255, 255) if self.lives > 5 else (255, 100, 100)
        lives_surf = self.font_info.render(lives_text, True, lives_color)
        lives_rect = lives_surf.get_rect(midtop=(self.rect.centerx, money_rect.bottom + 10))
        surface.blit(lives_surf, lives_rect)
        
        # Draw placement mode status (clickable)
        placement_text = f"Placement Mode: {'ON' if self.tower_placement_mode else 'OFF'}"
        placement_color = (100, 255, 100) if self.tower_placement_mode else (200, 200, 200)
        placement_surf = self.font_info.render(placement_text, True, placement_color)
        self.placement_rect = placement_surf.get_rect(midtop=(self.rect.centerx, lives_rect.bottom + 10))
        
        # Draw highlight if this is clickable
        if self.placement_rect.collidepoint(pygame.mouse.get_pos()):
            # Draw a highlight behind the text
            highlight_rect = self.placement_rect.inflate(10, 4)
            pygame.draw.rect(surface, (60, 60, 80), highlight_rect, 0, 3)
            pygame.draw.rect(surface, (100, 100, 140), highlight_rect, 1, 3)
        
        surface.blit(placement_surf, self.placement_rect)
        
        # Draw selected tower information
        if self.selected_tower_type:
            selected_y = self.placement_rect.bottom + 20
            
            selected_text = f"Selected Tower:"
            selected_surf = self.font_info.render(selected_text, True, (255, 255, 255))
            selected_rect = selected_surf.get_rect(midtop=(self.rect.centerx, selected_y))
            surface.blit(selected_surf, selected_rect)
            
            # Draw tower icon
            tower_img = assets["towers"].get(self.selected_tower_type)
            if tower_img:
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
            cost_surf = self.font_info.render(cost_text, True, cost_color)
            cost_rect = cost_surf.get_rect(midtop=(self.rect.centerx, selected_rect.bottom + 60))
            surface.blit(cost_surf, cost_rect)
            
            # Draw tower description
            description = tower_types[self.selected_tower_type].get("description", "")
            desc_font = pygame.font.SysFont(None, 18)
            desc_surf = desc_font.render(description, True, (200, 200, 200))
            desc_rect = desc_surf.get_rect(midtop=(self.rect.centerx, cost_rect.bottom + 10))
            surface.blit(desc_surf, desc_rect)

    def handle_event(self, event):
        """Handle mouse events on the status panel"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            # Check if clicked on placement mode text
            if self.placement_rect and self.placement_rect.collidepoint(event.pos):
                return {"action": "toggle_placement_mode"}
        
        return {"action": None} 