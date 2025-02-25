import pygame
from game.utils import create_element_icon

class Button:
    def __init__(self, rect, text, color=(100, 100, 200), hover_color=(120, 120, 255), text_color=(255, 255, 255), 
                 icon=None, icon_size=None, tooltip=None, enabled=True, font_size=18):
        self.rect = rect
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.icon = icon
        self.icon_size = icon_size
        self.tooltip = tooltip
        self.enabled = enabled
        self.hover = False
        self.font = pygame.font.SysFont(None, font_size)
        self.pressed = False
        self.press_time = 0
        self.shadow_offset = 2  # Reduced shadow for sleeker look
        self.border_radius = 6  # Slightly smaller radius for modern look
        
        # Cache for pre-rendered button surfaces
        self._cached_surfaces = {}
        self._last_state = None  # Track state to detect changes
        
    def _create_button_surface(self, state):
        """Create and cache button surface for a specific state (enabled, hover, pressed)"""
        button_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        
        if state == "disabled":
            # Disabled state - darker gray gradient
            color_top = (50, 50, 60)
            color_bottom = (35, 35, 45)
        elif state == "hover" or state == "pressed":
            # Hover state - brighter gradient
            color_top = (self.hover_color[0], self.hover_color[1], self.hover_color[2])
            color_bottom = (max(0, self.hover_color[0]-30), max(0, self.hover_color[1]-30), max(0, self.hover_color[2]-30))
        else:  # normal
            # Normal state - standard gradient
            color_top = (self.color[0], self.color[1], self.color[2])
            color_bottom = (max(0, self.color[0]-30), max(0, self.color[1]-30), max(0, self.color[2]-30))
        
        # Draw gradient background
        for y in range(self.rect.height):
            progress = y / self.rect.height
            r = int(color_top[0] * (1 - progress) + color_bottom[0] * progress)
            g = int(color_top[1] * (1 - progress) + color_bottom[1] * progress)
            b = int(color_top[2] * (1 - progress) + color_bottom[2] * progress)
            pygame.draw.line(button_surf, (r, g, b), (0, y), (self.rect.width, y))
        
        # Draw border with rounded corners
        pygame.draw.rect(button_surf, (0, 0, 0, 0), (0, 0, self.rect.width, self.rect.height), border_radius=self.border_radius)
        
        # Add highlight to the top edge for subtle 3D effect (except for pressed state)
        if state != "pressed" and state != "disabled":
            highlight_color = (255, 255, 255, 40)  # More subtle highlight
            pygame.draw.rect(button_surf, highlight_color, (2, 2, self.rect.width-4, 2), border_radius=self.border_radius)
        
        # Draw border
        border_color = (180, 180, 255, 70) if state == "hover" else (80, 80, 120, 50)
        pygame.draw.rect(button_surf, border_color, (0, 0, self.rect.width, self.rect.height), 1, border_radius=self.border_radius)
        
        return button_surf
    
    def _get_current_state(self):
        """Get the current button state as a string"""
        if not self.enabled:
            return "disabled"
        elif self.pressed:
            return "pressed"
        elif self.hover:
            return "hover"
        else:
            return "normal"
        
    def draw(self, surface):
        current_state = self._get_current_state()
        
        # Draw button shadow (only for enabled, non-pressed buttons)
        if self.enabled and not self.pressed:
            shadow_rect = pygame.Rect(self.rect.x + self.shadow_offset, 
                                     self.rect.y + self.shadow_offset,
                                     self.rect.width, self.rect.height)
            pygame.draw.rect(surface, (10, 10, 15, 150), shadow_rect, border_radius=self.border_radius)
        
        # Check if we need to create or use a cached surface
        if current_state not in self._cached_surfaces:
            self._cached_surfaces[current_state] = self._create_button_surface(current_state)
        
        button_surf = self._cached_surfaces[current_state]
        
        # Blit button surface with offset for pressed state
        if self.pressed:
            surface.blit(button_surf, (self.rect.x + 1, self.rect.y + 1))
        else:
            surface.blit(button_surf, self.rect.topleft)
            
        # Draw button text
        text_color = self.text_color if self.enabled else (150, 150, 150)
        text_surf = self.font.render(self.text, True, text_color)
        
        # Position based on whether there's an icon
        if self.icon:
            if isinstance(self.icon, pygame.Surface):
                # Use provided surface
                icon = self.icon
                if self.icon_size:
                    icon = pygame.transform.scale(icon, self.icon_size)
            else:
                # Create an icon based on text
                icon = create_element_icon(self.icon, 24)
                
            # Adjust positions for pressed state
            offset_x = 1 if self.pressed else 0
            offset_y = 1 if self.pressed else 0
                
            icon_rect = icon.get_rect(midleft=(self.rect.x + 10 + offset_x, self.rect.centery + offset_y))
            surface.blit(icon, icon_rect)
            
            # Position text next to icon
            text_rect = text_surf.get_rect(midleft=(icon_rect.right + 10, self.rect.centery + offset_y))
            surface.blit(text_surf, text_rect)
        else:
            # Center text in button
            text_rect = text_surf.get_rect(center=(
                self.rect.centerx + (1 if self.pressed else 0), 
                self.rect.centery + (1 if self.pressed else 0)
            ))
            surface.blit(text_surf, text_rect)
        
        # Draw press animation
        if self.pressed:
            pulse = min(1.0, (pygame.time.get_ticks() - self.press_time) / 200)
            alpha = int(150 * (1 - pulse))
            pulse_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            pulse_surface.fill((255, 255, 255, alpha))
            # Apply rounded corners to the pulse
            mask = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            pygame.draw.rect(mask, (255, 255, 255), (0, 0, self.rect.width, self.rect.height), border_radius=self.border_radius)
            pulse_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            surface.blit(pulse_surface, (self.rect.x + 1, self.rect.y + 1))
            
        # Draw tooltip if hovering
        if self.hover and self.tooltip:
            tooltip_font = pygame.font.SysFont(None, 16)
            tooltip_lines = self.tooltip.split('\n')
            tooltip_surfs = [tooltip_font.render(line, True, (255, 255, 255)) for line in tooltip_lines]
            
            # Calculate tooltip dimensions
            tooltip_width = max(surf.get_width() for surf in tooltip_surfs) + 10
            tooltip_height = sum(surf.get_height() for surf in tooltip_surfs) + 10
            
            tooltip_rect = pygame.Rect(
                self.rect.centerx - tooltip_width // 2, 
                self.rect.bottom + 5,
                tooltip_width,
                tooltip_height
            )
            
            # Make sure tooltip stays on screen
            if tooltip_rect.right > surface.get_width():
                tooltip_rect.right = surface.get_width() - 5
            if tooltip_rect.bottom > surface.get_height():
                tooltip_rect.bottom = self.rect.top - 5
            
            # Background for tooltip with gradient
            background_rect = tooltip_rect
            tooltip_surf = pygame.Surface((background_rect.width, background_rect.height), pygame.SRCALPHA)
            
            # Draw gradient background
            for y in range(background_rect.height):
                progress = y / background_rect.height
                r = int(50 * (1 - progress) + 20 * progress)
                g = int(50 * (1 - progress) + 20 * progress)
                b = int(70 * (1 - progress) + 40 * progress)
                pygame.draw.line(tooltip_surf, (r, g, b, 220), (0, y), (background_rect.width, y))
            
            # Add border
            pygame.draw.rect(tooltip_surf, (140, 140, 180), (0, 0, background_rect.width, background_rect.height), 1, border_radius=4)
            
            # Add highlight to the top
            pygame.draw.line(tooltip_surf, (200, 200, 255, 100), (1, 1), (background_rect.width-2, 1))
            
            surface.blit(tooltip_surf, background_rect.topleft)
            
            # Draw tooltip text
            y_offset = 5
            for surf in tooltip_surfs:
                surface.blit(surf, (tooltip_rect.x + 5, tooltip_rect.y + y_offset))
                y_offset += surf.get_height()
    
    def update(self, mouse_pos, mouse_pressed):
        old_hover = self.hover
        self.hover = self.rect.collidepoint(mouse_pos)
        
        # Clear cache if appearance changes
        if old_hover != self.hover:
            self._cached_surfaces = {}
        
        if self.hover and mouse_pressed and self.enabled and not self.pressed:
            self.pressed = True
            self.press_time = pygame.time.get_ticks()
            self._cached_surfaces = {}  # Clear cache when state changes
            return True
        
        # Reset pressed state after animation time
        if self.pressed and pygame.time.get_ticks() - self.press_time > 200:
            old_pressed = self.pressed
            self.pressed = False
            if old_pressed != self.pressed:
                self._cached_surfaces = {}  # Clear cache when state changes
            
        return False 