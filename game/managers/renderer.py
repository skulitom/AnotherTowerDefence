"""
Renderer - Handles all game rendering operations
"""
import pygame
import math

from game.utils import draw_gradient_background, draw_gradient_rect

class Renderer:
    def __init__(self, game_manager):
        """Initialize the renderer"""
        self.game = game_manager
    
    def render(self):
        """Render the game state"""
        # Draw background and grid
        self.draw_background()
        self.draw_grid()
        self.draw_path()
        
        # Draw gameplay elements
        self.draw_towers()
        self.draw_enemies()
        self.draw_projectiles()
        self.draw_particles()
        self.draw_preview()
        self.draw_floating_texts()
        
        # Draw UI
        self.draw_ui()
        self.draw_controls_info()
    
    def draw_background(self):
        """Draw the game background"""
        draw_gradient_background(self.game.screen, (12, 12, 24), (30, 30, 50))
        
        # Draw gameplay area separator
        pygame.draw.line(
            self.game.screen, 
            (60, 60, 100), 
            (self.game.sidebar_width, 0), 
            (self.game.sidebar_width, self.game.screen_height), 
            2
        )
        pygame.draw.line(
            self.game.screen, 
            (60, 60, 100), 
            (self.game.screen_width - self.game.sidebar_width, 0), 
            (self.game.screen_width - self.game.sidebar_width, self.game.screen_height), 
            2
        )
    
    def draw_grid(self):
        """Draw the grid"""
        # Draw subtle grid for better visibility in dark mode
        grid_size = 100 * self.game.camera.zoom  # Scale grid size with zoom
        grid_alpha = max(20, min(40, int(40 * self.game.camera.zoom)))  # Adjust opacity based on zoom
        grid_color = (40, 40, 60, grid_alpha)
        
        # Calculate grid bounds based on camera view
        grid_surf = pygame.Surface((self.game.screen_width, self.game.screen_height), pygame.SRCALPHA)
        
        # Calculate world boundaries visible on screen
        left, top = self.game.camera.unapply(0, 0)
        right, bottom = self.game.camera.unapply(self.game.screen_width, self.game.screen_height)
        
        # Draw vertical grid lines
        start_x = int(left // grid_size) * grid_size
        for x in range(int(start_x), int(right) + int(grid_size), int(grid_size)):
            screen_x = self.game.camera.apply(x, 0)[0]
            if self.game.sidebar_width < screen_x < self.game.screen_width - self.game.sidebar_width:
                pygame.draw.line(
                    grid_surf, 
                    grid_color, 
                    (screen_x, 0), 
                    (screen_x, self.game.screen_height), 
                    max(1, int(self.game.camera.zoom))
                )
        
        # Draw horizontal grid lines
        start_y = int(top // grid_size) * grid_size
        for y in range(int(start_y), int(bottom) + int(grid_size), int(grid_size)):
            screen_y = self.game.camera.apply(0, y)[1]
            pygame.draw.line(
                grid_surf, 
                grid_color, 
                (self.game.sidebar_width, screen_y), 
                (self.game.screen_width - self.game.sidebar_width, screen_y), 
                max(1, int(self.game.camera.zoom))
            )
        
        self.game.screen.blit(grid_surf, (0, 0))
    
    def draw_path(self):
        """Draw the enemy path"""
        points = []
        for point in self.game.path_points:
            screen_point = self.game.camera.apply(point[0], point[1])
            points.append(screen_point)
        
        # Calculate path width that scales with zoom but has min/max limits
        path_width = max(2, min(10, int(5 * self.game.camera.zoom)))
        pygame.draw.lines(self.game.screen, (120, 120, 160), False, points, path_width)
        
        # Add some path decoration
        for i in range(len(self.game.path_points) - 1):
            p1 = pygame.Vector2(self.game.path_points[i])
            p2 = pygame.Vector2(self.game.path_points[i + 1])
            # Draw direction arrows along path
            if (p2 - p1).length() > 50:
                direction = (p2 - p1).normalize()
                num_arrows = int((p2 - p1).length() / 100)
                for j in range(num_arrows):
                    pos = p1 + direction * (j + 0.5) * ((p2 - p1).length() / num_arrows)
                    angle = math.atan2(direction.y, direction.x)
                    
                    # Apply camera transform to arrow position
                    screen_pos = self.game.camera.apply(pos.x, pos.y)
                    
                    # Draw arrow
                    arrow_size = max(3, 10 * self.game.camera.zoom)
                    arrow_points = [
                        (screen_pos[0] + math.cos(angle) * arrow_size, 
                         screen_pos[1] + math.sin(angle) * arrow_size),
                        (screen_pos[0] + math.cos(angle + 2.5) * arrow_size * 0.6, 
                         screen_pos[1] + math.sin(angle + 2.5) * arrow_size * 0.6),
                        (screen_pos[0] + math.cos(angle - 2.5) * arrow_size * 0.6, 
                         screen_pos[1] + math.sin(angle - 2.5) * arrow_size * 0.6)
                    ]
                    pygame.draw.polygon(self.game.screen, (100, 100, 140), arrow_points)
    
    def draw_towers(self):
        """Draw all towers"""
        for tower in self.game.towers:
            is_selected = tower == self.game.selected_tower
            tower.draw(
                self.game.screen, 
                self.game.assets, 
                show_range=is_selected,
                selected=is_selected, 
                camera=self.game.camera
            )
    
    def draw_enemies(self):
        """Draw all enemies"""
        for enemy in self.game.enemies:
            enemy.draw(self.game.screen, show_hp=True, camera=self.game.camera)
    
    def draw_projectiles(self):
        """Draw all projectiles"""
        for projectile in self.game.projectiles:
            projectile.draw(self.game.screen, camera=self.game.camera)
    
    def draw_particles(self):
        """Draw all particles"""
        self.game.particles.draw(self.game.screen, camera=self.game.camera)
    
    def draw_preview(self):
        """Draw tower placement preview"""
        if self.game.dragging_tower and self.game.tower_preview_pos:
            # Check tower placement validity
            valid_placement = self.game.is_valid_tower_placement(self.game.tower_preview_pos)
            
            # Draw tower preview
            screen_pos = self.game.camera.apply(
                self.game.tower_preview_pos.x, 
                self.game.tower_preview_pos.y
            )
            preview_radius = 15 * self.game.camera.zoom
            preview_surf = pygame.Surface(
                (int(preview_radius * 2), int(preview_radius * 2)), 
                pygame.SRCALPHA
            )
            
            from game.settings import tower_types
            preview_color = tower_types[self.game.current_tower_type]["color"]
            
            # Draw base circle with transparency
            if valid_placement:
                pygame.draw.circle(
                    preview_surf, 
                    (*preview_color, 150), 
                    (int(preview_radius), int(preview_radius)), 
                    int(preview_radius)
                )
                # Add range indicator
                range_radius = tower_types[self.game.current_tower_type]["range"] * self.game.camera.zoom
                range_surf = pygame.Surface(
                    (int(range_radius * 2), int(range_radius * 2)), 
                    pygame.SRCALPHA
                )
                pygame.draw.circle(
                    range_surf, 
                    (255, 255, 255, 30), 
                    (int(range_radius), int(range_radius)), 
                    int(range_radius)
                )
                pygame.draw.circle(
                    range_surf, 
                    (255, 255, 255, 60), 
                    (int(range_radius), int(range_radius)), 
                    int(range_radius), 
                    2
                )
                self.game.screen.blit(
                    range_surf, 
                    (int(screen_pos[0] - range_radius), int(screen_pos[1] - range_radius))
                )
            else:
                # Use red color for invalid placement
                pygame.draw.circle(
                    preview_surf, 
                    (255, 100, 100, 150), 
                    (int(preview_radius), int(preview_radius)), 
                    int(preview_radius)
                )
                # Draw X mark
                pygame.draw.line(
                    preview_surf, 
                    (255, 50, 50, 200), 
                    (preview_radius * 0.5, preview_radius * 0.5), 
                    (preview_radius * 1.5, preview_radius * 1.5), 
                    max(1, int(2 * self.game.camera.zoom))
                )
                pygame.draw.line(
                    preview_surf, 
                    (255, 50, 50, 200), 
                    (preview_radius * 1.5, preview_radius * 0.5), 
                    (preview_radius * 0.5, preview_radius * 1.5), 
                    max(1, int(2 * self.game.camera.zoom))
                )
            
            # Blit the preview
            self.game.screen.blit(
                preview_surf, 
                (int(screen_pos[0] - preview_radius), int(screen_pos[1] - preview_radius))
            )
    
    def draw_floating_texts(self):
        """Draw all floating texts"""
        for text in self.game.floating_texts:
            # Apply camera transform for floating texts
            if hasattr(text, 'pos'):  # Only transform in-game floating texts, not UI texts
                screen_pos = self.game.camera.apply(text.pos[0], text.pos[1])
                text.draw(self.game.screen, screen_pos=screen_pos, scale=self.game.camera.zoom)
            else:
                text.draw(self.game.screen)
    
    def draw_ui(self):
        """Draw the game UI"""
        self.game.ui.draw(
            self.game.screen, 
            {
                "money": self.game.money,
                "lives": self.game.lives,
                "wave": self.game.wave,
                "current_tower_type": self.game.current_tower_type,
                "selected_tower": self.game.selected_tower,
                "hover_tower": self.game.hover_tower,
                "enemies_remaining": len(self.game.enemies),
                "wave_progress": self.game.wave_manager.wave_progress,
                "wave_active": self.game.wave_active,
                "camera_zoom": self.game.camera.zoom
            },
            self.game.assets
        )
    
    def draw_controls_info(self):
        """Draw controls information panel"""
        font_size = max(14, min(18, int(self.game.screen_width / 70)))
        font_small = pygame.font.SysFont(None, font_size)
        
        zoom_text = font_small.render(f"Zoom: {self.game.camera.zoom:.1f}x (Mouse Wheel to Zoom)", True, (160, 160, 180))
        pan_text = font_small.render("Pan: Hold Right Mouse Button and Drag", True, (160, 160, 180))
        alt_pan_text = font_small.render("Alt. Pan: SHIFT+Left Mouse or Middle Mouse", True, (160, 160, 180))
        build_text = font_small.render("Build: Left-Click and Drag", True, (160, 160, 180))
        reset_text = font_small.render("Reset Camera: Press R", True, (160, 160, 180))
        fs_text = font_small.render("Toggle Fullscreen: F11", True, (160, 160, 180))
        
        # Calculate help panel dimensions based on screen size
        help_panel_width = min(300, int(self.game.screen_width * 0.22))
        help_panel_height = min(115, int(self.game.screen_height * 0.13))
        
        control_bg = pygame.Surface((help_panel_width, help_panel_height), pygame.SRCALPHA)
        control_bg.fill((20, 20, 30, 150))
        self.game.screen.blit(
            control_bg, 
            (self.game.screen_width - help_panel_width - 20, self.game.screen_height - help_panel_height - 5)
        )
        
        # Calculate text positions based on panel
        text_padding = help_panel_height / 6
        for i, text in enumerate([zoom_text, pan_text, alt_pan_text, build_text, reset_text, fs_text]):
            self.game.screen.blit(
                text, 
                (self.game.screen_width - help_panel_width - 10, 
                 self.game.screen_height - help_panel_height + text_padding * i)
            )
        
        # Show current interaction mode
        mouse_buttons = pygame.mouse.get_pressed()
        right_mouse_pressed = mouse_buttons[2]
        
        if self.game.is_panning:
            mode_text = font_small.render("Mode: Pan", True, (100, 200, 255))
        else:
            mode_text = font_small.render(
                f"Mode: {'Pan' if self.game.is_shift_pressed or right_mouse_pressed else 'Build'}", 
                True, 
                (100, 200, 255) if self.game.is_shift_pressed or right_mouse_pressed else (100, 255, 100)
            )
        
        # Position the mode text with proper padding
        panel_padding = int(self.game.screen_height * 0.022)
        self.game.screen.blit(mode_text, (self.game.sidebar_width + panel_padding, panel_padding))
    
    def show_game_over(self, wave):
        """Show the game over screen"""
        # Draw game over screen
        overlay = pygame.Surface((self.game.screen_width, self.game.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.game.screen.blit(overlay, (0, 0))
        
        # Scale font sizes based on screen dimensions
        large_font_size = max(48, min(64, int(self.game.screen_width / 22)))
        medium_font_size = max(24, min(36, int(self.game.screen_width / 36)))
        
        font_large = pygame.font.SysFont(None, large_font_size)
        font_medium = pygame.font.SysFont(None, medium_font_size)
        
        game_over_text = font_large.render("Game Over!", True, (255, 50, 50))
        game_over_rect = game_over_text.get_rect(
            center=(self.game.screen_width // 2, self.game.screen_height // 2 - int(self.game.screen_height * 0.05))
        )
        self.game.screen.blit(game_over_text, game_over_rect)
        
        wave_text = font_medium.render(f"You survived until wave {wave}", True, (255, 255, 255))
        wave_rect = wave_text.get_rect(
            center=(self.game.screen_width // 2, self.game.screen_height // 2 + int(self.game.screen_height * 0.02))
        )
        self.game.screen.blit(wave_text, wave_rect)
        
        continue_text = font_medium.render("Press ESC to exit or SPACE to restart", True, (200, 200, 200))
        continue_rect = continue_text.get_rect(
            center=(self.game.screen_width // 2, self.game.screen_height // 2 + int(self.game.screen_height * 0.08))
        )
        self.game.screen.blit(continue_text, continue_rect)
        
        pygame.display.flip() 