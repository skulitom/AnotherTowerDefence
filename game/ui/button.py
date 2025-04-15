import pygame
from game.utils import create_element_icon
from game.ui.ui_theme import (
    BUTTON_BG, BUTTON_BG_HOVER, BUTTON_BG_ACTIVE, ACCENT_COLOR, ACCENT_COLOR_HOVER, ACCENT_COLOR_ACTIVE,
    TEXT_COLOR, SUBTLE_TEXT, BUTTON_BORDER_RADIUS, FONT_NAME, BODY_FONT_SIZE, SHADOW_COLOR, ICON_TEXT_SPACING,
    BORDER_COLOR
)

class Button:
    def __init__(self, rect, text, color=BUTTON_BG, hover_color=BUTTON_BG_HOVER, text_color=TEXT_COLOR,
                 icon=None, icon_size=None, tooltip=None, enabled=True, font_size=BODY_FONT_SIZE, assets=None):
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
        # Use modern font
        self.font = pygame.font.SysFont(FONT_NAME, font_size, bold=True)
        self.tooltip_font = pygame.font.SysFont(FONT_NAME, 14)
        self.pressed = False
        self.press_time = 0
        self.shadow_offset = 4  # More pronounced shadow
        self.border_radius = BUTTON_BORDER_RADIUS
        self._cached_surfaces = {}
        self._last_state = None

    def _create_button_surface(self, state):
        """Create and cache button surface for a specific state (enabled, hover, pressed)"""
        button_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        # Draw solid rounded background
        if state == "disabled":
            color_top = (28, 30, 36)
            color_bottom = (20, 22, 26)
        elif state == "pressed":
            color_top = BUTTON_BG_ACTIVE
            color_bottom = BUTTON_BG
        elif state == "hover":
            color_top = BUTTON_BG_HOVER
            color_bottom = BUTTON_BG
        else:
            color_top = self.color
            color_bottom = (max(0, self.color[0]-8), max(0, self.color[1]-8), max(0, self.color[2]-8))
        grad_rect = pygame.Rect(0, 0, self.rect.width, self.rect.height)
        # Gradient fill, but always fully opaque
        temp_bg = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        for y in range(self.rect.height):
            progress = y / self.rect.height
            r = int(color_top[0] * (1 - progress) + color_bottom[0] * progress)
            g = int(color_top[1] * (1 - progress) + color_bottom[1] * progress)
            b = int(color_top[2] * (1 - progress) + color_bottom[2] * progress)
            pygame.draw.line(temp_bg, (r, g, b, 255), (0, y), (self.rect.width, y))  # Force alpha=255
        # Mask to rounded rect (full alpha)
        mask = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255,255,255,255), grad_rect, border_radius=self.border_radius)
        temp_bg.blit(mask, (0,0), special_flags=pygame.BLEND_RGBA_MULT)
        button_surf.blit(temp_bg, (0,0))
        # Border
        border_col = ACCENT_COLOR if state in ("hover", "pressed") else BORDER_COLOR
        pygame.draw.rect(button_surf, border_col, grad_rect, 2, border_radius=self.border_radius)
        # Soft glow for hover/active
        if state == "hover":
            glow = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow, ACCENT_COLOR_HOVER + (70,), grad_rect, border_radius=self.border_radius)
            button_surf.blit(glow, (0,0), special_flags=pygame.BLEND_RGBA_ADD)
        elif state == "pressed":
            glow = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow, ACCENT_COLOR_ACTIVE + (90,), grad_rect, border_radius=self.border_radius)
            button_surf.blit(glow, (0,0), special_flags=pygame.BLEND_RGBA_ADD)
        return button_surf

    def _get_current_state(self):
        """Get the current button state as a string"""
        import pygame
        mouse_pressed = pygame.mouse.get_pressed()[0]
        mouse_pos = pygame.mouse.get_pos()
        if not self.enabled:
            return "disabled"
        elif self.rect.collidepoint(mouse_pos) and mouse_pressed:
            return "pressed"
        elif self.rect.collidepoint(mouse_pos):
            return "hover"
        else:
            return "normal"

    def draw(self, surface):
        state = self._get_current_state()
        if state != self._last_state or state not in self._cached_surfaces:
            self._cached_surfaces[state] = self._create_button_surface(state)
            self._last_state = state
        button_surf = self._cached_surfaces[state].copy()
        # Icon and text layout with spacing and padding
        content_width = 0
        icon_surf = None
        text_surf = None
        if self.icon:
            if isinstance(self.icon, str):
                icon_surf = create_element_icon(self.icon, self.icon_size or 24)
            else:
                icon_surf = pygame.transform.smoothscale(self.icon, (self.icon_size, self.icon_size)) if self.icon_size else self.icon
            content_width += icon_surf.get_width()
        if self.text:
            text_surf = self.font.render(self.text, True, self.text_color)
            content_width += text_surf.get_width()
        if self.icon and self.text:
            content_width += ICON_TEXT_SPACING
        # Center content
        x = (self.rect.width - content_width) // 2
        y = (self.rect.height - (icon_surf.get_height() if icon_surf else (text_surf.get_height() if text_surf else 0))) // 2
        # Draw icon
        if icon_surf:
            icon_rect = icon_surf.get_rect()
            icon_rect.topleft = (x, y)
            button_surf.blit(icon_surf, icon_rect)
            x += icon_surf.get_width() + (ICON_TEXT_SPACING if self.text else 0)
        # Draw text
        if text_surf:
            text_rect = text_surf.get_rect()
            text_rect.topleft = (x, y + (icon_surf.get_height() - text_surf.get_height())//2 if icon_surf and text_surf else y)
            button_surf.blit(text_surf, text_rect)
        surface.blit(button_surf, self.rect.topleft)

    def get_tooltip_surface(self, screen_width, screen_height):
        """If hovered and has tooltip, return rendered tooltip surface and rect, else None."""
        if self.hover and self.tooltip:
            tooltip_lines = self.tooltip.split('\n')
            tooltip_surfs = [self.tooltip_font.render(line, True, (255, 255, 255)) for line in tooltip_lines]
            
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
            if tooltip_rect.right > screen_width:
                tooltip_rect.right = screen_width - 5
            if tooltip_rect.left < 0:
                tooltip_rect.left = 5
            if tooltip_rect.bottom > screen_height:
                tooltip_rect.bottom = self.rect.top - 5
            if tooltip_rect.top < 0:
                tooltip_rect.top = 5
            
            # Background for tooltip with gradient
            tooltip_bg_surf = pygame.Surface((tooltip_rect.width, tooltip_rect.height), pygame.SRCALPHA)
            
            # Draw gradient background
            for y in range(tooltip_rect.height):
                progress = y / tooltip_rect.height
                r = int(50 * (1 - progress) + 20 * progress)
                g = int(50 * (1 - progress) + 20 * progress)
                b = int(70 * (1 - progress) + 40 * progress)
                pygame.draw.line(tooltip_bg_surf, (r, g, b, 220), (0, y), (tooltip_rect.width, y))
            
            # Add border
            pygame.draw.rect(tooltip_bg_surf, (140, 140, 180), (0, 0, tooltip_rect.width, tooltip_rect.height), 1, border_radius=4)
            
            # Add highlight to the top
            pygame.draw.line(tooltip_bg_surf, (200, 200, 255, 100), (1, 1), (tooltip_rect.width-2, 1))
            
            # Draw tooltip text onto the background surface
            y_offset = 5
            for surf in tooltip_surfs:
                tooltip_bg_surf.blit(surf, (5, y_offset))
                y_offset += surf.get_height()
                
            return tooltip_bg_surf, tooltip_rect # Return surface and position
            
        return None, None # Return None if no tooltip needed

    def update(self, mouse_pos, mouse_button_down_event):
        """
        Checks for a click event on the button.
        Returns True if the button was clicked *in this event*.
        Sets the initial 'pressed' state and timer if clicked.
        Resetting the state is handled entirely within the draw method.
        """
        is_hovering = self.rect.collidepoint(mouse_pos)
        clicked_now = False

        # Detect initial press (only if a MOUSEBUTTONDOWN event occurred)
        if is_hovering and mouse_button_down_event and self.enabled:
            # Set pressed state regardless of current self.pressed value
            # This ensures a click always triggers the visual press effect
            self.pressed = True 
            self.press_time = pygame.time.get_ticks() 
            clicked_now = True  # Signal the action trigger
            print(f"Button '{self.text}' clicked! Setting pressed state.")
            # Cache invalidation will be handled by draw based on state change

        return clicked_now