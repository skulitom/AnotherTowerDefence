import pygame
from game.utils import draw_gradient_rect, draw_panel_background
from game.ui.button import Button

class WavePanel:
    def __init__(self, rect, assets):
        self.rect = rect
        self.assets = assets
        self.current_wave = 0
        self.enemies_remaining = 0
        self.next_wave_button = None
        self.wave_progress = 0.0  # 0.0 to 1.0
        self.is_wave_active = False
        self.create_buttons()
        
    def create_buttons(self):
        # Calculate button dimensions based on panel size
        button_height = min(35, max(30, int(self.rect.height * 0.23)))
        button_width = self.rect.width - 20
        
        # Position button at the bottom of the panel with proper padding
        bottom_padding = min(15, max(10, int(self.rect.height * 0.1)))
        
        button_rect = pygame.Rect(
            self.rect.x + 10, 
            self.rect.bottom - button_height - bottom_padding, 
            button_width, 
            button_height
        )
        
        self.next_wave_button = Button(
            button_rect,
            "Start Wave",
            color=(60, 180, 60),
            hover_color=(80, 220, 80),
            tooltip="Start the next wave of enemies",
            font_size=min(20, max(16, int(button_height * 0.6))),
            assets=self.assets
        )
    
    def update(self, current_wave, enemies_remaining, wave_progress=0.0, is_wave_active=False):
        self.current_wave = current_wave
        self.enemies_remaining = enemies_remaining
        self.wave_progress = wave_progress
        self.is_wave_active = is_wave_active
        
        if is_wave_active:
            self.next_wave_button.enabled = False
            self.next_wave_button.text = f"Wave in Progress..."
        else:
            self.next_wave_button.enabled = True
            self.next_wave_button.text = f"Start Wave {current_wave + 1}"
    
    def draw(self, surface, assets):
        # Get fonts from assets
        font_title = assets["fonts"].get("title")
        font_info = assets["fonts"].get("body")
        
        # Draw panel background
        title = f"Wave {self.current_wave}"
        content_y = draw_panel_background(surface, self.rect, title=title, dark_theme=True, font=font_title)
        
        # Draw enemies remaining
        enemies_text = f"Enemies Remaining: {self.enemies_remaining}"
        enemies_surf = font_info.render(enemies_text, True, (220, 220, 220))
        enemies_rect = enemies_surf.get_rect(midtop=(self.rect.centerx, content_y + 5))
        surface.blit(enemies_surf, enemies_rect)
        
        # Draw wave progress bar
        if self.is_wave_active:
            progress_rect = pygame.Rect(
                self.rect.x + 20,
                enemies_rect.bottom + 10,
                self.rect.width - 40,
                15
            )
            pygame.draw.rect(surface, (40, 40, 40), progress_rect)
            fill_rect = progress_rect.copy()
            fill_rect.width = int(progress_rect.width * self.wave_progress)
            pygame.draw.rect(surface, (80, 180, 80), fill_rect)
            pygame.draw.rect(surface, (100, 100, 100), progress_rect, 1)
        
        # Draw next wave button
        self.next_wave_button.draw(surface)
        
        # Collect tooltips
        tooltips_to_draw = []
        if self.next_wave_button:
            tooltip_surf, tooltip_rect = self.next_wave_button.get_tooltip_surface(surface.get_width(), surface.get_height())
            if tooltip_surf:
                tooltips_to_draw.append((tooltip_surf, tooltip_rect))
                
        return tooltips_to_draw # Return the list
    
    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
        
        if self.next_wave_button.update(mouse_pos, mouse_pressed):
            return "start_wave"
            
        return None 