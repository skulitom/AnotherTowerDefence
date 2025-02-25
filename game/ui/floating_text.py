import pygame
import random

class FloatingText:
    def __init__(self, text, pos, color=(255, 255, 255), size=24, duration=1.0):
        self.text = text
        self.pos = pos
        self.color = color
        self.size = size
        self.duration = duration
        self.life = duration
        self.font = pygame.font.SysFont(None, size)
        self.velocity = (random.uniform(-5, 5), -random.uniform(20, 40))
        
    def update(self, dt):
        self.life -= dt
        self.pos = (self.pos[0] + self.velocity[0] * dt, self.pos[1] + self.velocity[1] * dt)
        # Gradually slow down
        self.velocity = (self.velocity[0] * 0.95, self.velocity[1] * 0.95)
        return self.life > 0
        
    def draw(self, surface, screen_pos=None, scale=1.0):
        # Allow camera transform to provide screen coordinates
        if screen_pos:
            draw_pos = screen_pos
            font_size = int(self.size * scale)
            if font_size != self.font.get_height():
                self.font = pygame.font.SysFont(None, font_size)
        else:
            draw_pos = self.pos
            
        # Calculate alpha based on remaining life
        alpha = min(255, max(0, int(255 * (self.life / self.duration))))
        
        # Render text with shadow for better visibility
        shadow_surf = self.font.render(self.text, True, (0, 0, 0))
        shadow_rect = shadow_surf.get_rect(center=(int(draw_pos[0]) + 2, int(draw_pos[1]) + 2))
        
        text_surf = self.font.render(self.text, True, self.color)
        text_rect = text_surf.get_rect(center=(int(draw_pos[0]), int(draw_pos[1])))
        
        # Apply alpha
        if alpha < 255:
            shadow_surf.set_alpha(alpha)
            text_surf.set_alpha(alpha)
            
        surface.blit(shadow_surf, shadow_rect)
        surface.blit(text_surf, text_rect) 