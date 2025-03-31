import pygame
from game.utils import create_element_icon

class Button:
    def __init__(self, rect, text, color=(100, 100, 200), hover_color=(120, 120, 255), text_color=(255, 255, 255), 
                 icon=None, icon_size=None, tooltip=None, enabled=True, font_size=18, assets=None):
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
        # Get fonts from assets, with fallbacks
        if assets and "fonts" in assets:
            self.font = assets["fonts"].get("body", pygame.font.SysFont(None, font_size))
            self.tooltip_font = assets["fonts"].get("body_small", pygame.font.SysFont(None, 16))
            # Adjust main font size if needed (could be refined)
            # For simplicity, we might rely on panels passing correct initial font_size or use a dedicated button font
            # self.font = pygame.font.Font(self.font.name, font_size) # Attempt to resize (might not work reliably with SysFont)
        else:
            # Fallback if assets not provided
            self.font = pygame.font.SysFont(None, font_size)
            self.tooltip_font = pygame.font.SysFont(None, 16)
            
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
        elif state == "pressed":
            # Pressed state - slightly darker but still clearly visible
            color_top = (max(0, self.color[0]-20), max(0, self.color[1]-20), max(0, self.color[2]-20))
            color_bottom = (max(0, self.color[0]-30), max(0, self.color[1]-30), max(0, self.color[2]-30))
        elif state == "hover":
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
        if state == "pressed":
            border_color = (100, 100, 150, 80)  # More visible border for pressed state
        elif state == "hover":
            border_color = (180, 180, 255, 70)
        else:
            border_color = (80, 80, 120, 50)
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
        # === State Management ===
        # 1. Check timer to reset internal pressed flag
        if self.pressed and pygame.time.get_ticks() - self.press_time > 200:
            self.pressed = False # Reset internal flag

        # 2. Determine hover status
        mouse_pos = pygame.mouse.get_pos()
        is_hovering = self.rect.collidepoint(mouse_pos) and self.enabled
        self.hover = is_hovering # Keep self.hover updated for tooltip

        # 3. Determine the definitive visual state for THIS FRAME
        current_visual_state = "normal"
        if not self.enabled:
            current_visual_state = "disabled"
        elif self.pressed: # This flag is True only for the 200ms after a click
            current_visual_state = "pressed"
        elif is_hovering: # Only if not disabled and not currently in the pressed state
            current_visual_state = "hover"
        
        # === Cache Management ===
        # If the determined visual state is different from the last one rendered, regenerate cache
        if current_visual_state != self._last_state:
            print(f"Button '{self.text}': Visual state changed ('{self._last_state}' -> '{current_visual_state}'). Regenerating surface.")
            # Clear the specific old state if needed, though regenerating the new one is key
            # self._cached_surfaces.pop(self._last_state, None)
            self._cached_surfaces[current_visual_state] = self._create_button_surface(current_visual_state)
            self._last_state = current_visual_state # IMPORTANT: Update last state *after* potential regeneration
        
        # Use the cached surface for the current visual state
        # If state didn't change and cache exists, this uses the existing cache
        # If state changed or cache didn't exist, it uses the newly generated surface
        if current_visual_state not in self._cached_surfaces:
             # Fallback just in case - should not happen with above logic
             print(f"Error: Button '{self.text}' surface for state '{current_visual_state}' not found in cache after check!")
             self._cached_surfaces[current_visual_state] = self._create_button_surface(current_visual_state)
        button_surf = self._cached_surfaces[current_visual_state]

        # === Drawing ===
        is_visually_pressed = (current_visual_state == "pressed")
        
        # Draw shadow (only for hover or normal states)
        if current_visual_state == "normal" or current_visual_state == "hover":
            shadow_rect = pygame.Rect(self.rect.x + self.shadow_offset, 
                                     self.rect.y + self.shadow_offset,
                                     self.rect.width, self.rect.height)
            pygame.draw.rect(surface, (10, 10, 15, 150), shadow_rect, border_radius=self.border_radius)
        
        # Blit button surface with offset for pressed state
        blit_pos = (self.rect.x + 1, self.rect.y + 1) if is_visually_pressed else self.rect.topleft
        surface.blit(button_surf, blit_pos)
            
        # Draw button text with shadow (adjusted for offset)
        text_color = self.text_color if self.enabled else (150, 150, 150)
        shadow_color = (max(0, text_color[0]-80), max(0, text_color[1]-80), max(0, text_color[2]-80))
        if not self.enabled:
             shadow_color = (70, 70, 70)
             
        text_surf = self.font.render(self.text, True, text_color)
        shadow_surf = self.font.render(self.text, True, shadow_color)
        
        offset_x = 1 if is_visually_pressed else 0
        offset_y = 1 if is_visually_pressed else 0
        shadow_offset_x = offset_x + 1
        shadow_offset_y = offset_y + 1
        
        # Position text/icon (same logic)
        if self.icon:
            # Icon drawing logic (uses offset_x, offset_y, shadow_offset_x, shadow_offset_y)
            if isinstance(self.icon, pygame.Surface):
                icon = self.icon
                if self.icon_size:
                    icon = pygame.transform.scale(icon, self.icon_size)
            else:
                icon = create_element_icon(self.icon, 24)
                
            icon_rect = icon.get_rect(midleft=(self.rect.x + 10 + offset_x, self.rect.centery + offset_y))
            surface.blit(icon, icon_rect)
            
            text_rect = text_surf.get_rect(midleft=(icon_rect.right + 10, self.rect.centery + offset_y))
            shadow_rect = shadow_surf.get_rect(midleft=(icon_rect.right + 10 + shadow_offset_x - offset_x, 
                                                      self.rect.centery + shadow_offset_y))
            surface.blit(shadow_surf, shadow_rect)
            surface.blit(text_surf, text_rect)
        else:
            # Text-only drawing logic (uses offset_x, offset_y, shadow_offset_x, shadow_offset_y)
            text_rect = text_surf.get_rect(center=(self.rect.centerx + offset_x, self.rect.centery + offset_y))
            shadow_rect = shadow_surf.get_rect(center=(self.rect.centerx + shadow_offset_x, self.rect.centery + shadow_offset_y))
            surface.blit(shadow_surf, shadow_rect)
            surface.blit(text_surf, text_rect)
        
        # Pulse animation is disabled

        # Draw press pulse animation (only when visually pressed) - TEMPORARILY DISABLED
            
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