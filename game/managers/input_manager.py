"""
Input Manager - Handles all user input and controls
"""
import pygame
from pygame import Vector2

from game.ui import FloatingText
from game.settings import tower_types

class InputManager:
    def __init__(self, game_manager):
        """Initialize the input manager"""
        self.game = game_manager
        # Key states
        self.keys_pressed = {}
    
    def handle_event(self, event):
        """Process a pygame event"""
        if event.type == pygame.VIDEORESIZE:
            self.handle_resize_event(event)
        elif event.type == pygame.KEYDOWN:
            self.handle_key_down_event(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.handle_mouse_down_event(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.handle_mouse_up_event(event)
        elif event.type == pygame.MOUSEMOTION:
            self.handle_mouse_motion_event(event)
        
        # Update keyboard state for continuous input detection
        self.update_key_state()
        
        # Update mouse button state
        self.update_mouse_state()
    
    def update_key_state(self):
        """Update the keyboard state for continuous input detection"""
        keys = pygame.key.get_pressed()
        self.game.is_shift_pressed = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
    
    def update_mouse_state(self):
        """Update mouse button states for continuous input detection"""
        mouse_buttons = pygame.mouse.get_pressed()
        middle_mouse_pressed = mouse_buttons[1]  # Middle mouse button
        right_mouse_pressed = mouse_buttons[2]  # Right mouse button
        left_mouse_pressed = mouse_buttons[0]  # Left mouse button
        
        # Detect which panning method is active
        using_right_click_pan = right_mouse_pressed
        using_middle_click_pan = middle_mouse_pressed
        using_shift_left_pan = self.game.is_shift_pressed and left_mouse_pressed and not self.game.dragging_tower
        
        # Panning logic - check if any panning method is active
        if using_right_click_pan or using_middle_click_pan or using_shift_left_pan:
            current_mouse_pos = pygame.mouse.get_pos()
            if not self.game.is_panning:
                # Start new pan operation
                self.game.camera.start_drag(current_mouse_pos[0], current_mouse_pos[1])
                self.game.is_panning = True
            else:
                # Update drag if already panning
                self.game.camera.update_drag(current_mouse_pos[0], current_mouse_pos[1])
        elif self.game.is_panning:
            # End panning when all panning method buttons are released
            self.game.camera.end_drag()
            self.game.is_panning = False
    
    def update_camera(self, dt):
        """Update camera position based on keyboard input"""
        keys = pygame.key.get_pressed()
        camera_speed = 300 * dt
        if keys[pygame.K_UP]:
            self.game.camera.move(0, -camera_speed)
        if keys[pygame.K_DOWN]:
            self.game.camera.move(0, camera_speed)
        if keys[pygame.K_LEFT]:
            self.game.camera.move(-camera_speed, 0)
        if keys[pygame.K_RIGHT]:
            self.game.camera.move(camera_speed, 0)
    
    def handle_resize_event(self, event):
        """Handle window resize event"""
        self.game.handle_resize(event.size[0], event.size[1])
    
    def handle_key_down_event(self, event):
        """Handle key down events"""
        if event.key == pygame.K_ESCAPE:
            if self.game.fullscreen:
                # Exit fullscreen instead of quitting if in fullscreen mode
                self.game.fullscreen = False
                self.game.screen = pygame.display.set_mode(
                    (self.game.screen_width, self.game.screen_height), pygame.RESIZABLE
                )
            else:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
        elif event.key == pygame.K_F11:
            # Toggle fullscreen
            self.game.fullscreen = not self.game.fullscreen
            if self.game.fullscreen:
                screen_width_before = self.game.screen_width
                screen_height_before = self.game.screen_height
                self.game.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                self.game.screen_width, self.game.screen_height = self.game.screen.get_size()
                
                # Only update UI and camera if size actually changed
                if (self.game.screen_width != screen_width_before or 
                    self.game.screen_height != screen_height_before):
                    self.game.handle_resize(self.game.screen_width, self.game.screen_height)
            else:
                self.game.screen = pygame.display.set_mode(
                    (self.game.screen_width, self.game.screen_height), pygame.RESIZABLE
                )
        elif event.key == pygame.K_SPACE and not self.game.wave_active:
            # Start next wave
            self.game.wave_manager.start_wave()
        elif event.key == pygame.K_r:
            # Reset camera
            self.game.camera.x = self.game.screen_width / 2
            self.game.camera.y = self.game.screen_height / 2
            self.game.camera.zoom = 1.0
    
    def handle_mouse_down_event(self, event):
        """Handle mouse button down events"""
        mouse_pos = pygame.mouse.get_pos()
        
        # Check if mouse is in sidebar
        sidebar_width = self.game.sidebar_width
        in_sidebar = (mouse_pos[0] < sidebar_width or 
                    mouse_pos[0] > self.game.screen_width - sidebar_width)
        
        if event.button == 2:  # Middle mouse button for panning
            self.game.camera.start_drag(mouse_pos[0], mouse_pos[1])
            self.game.is_panning = True
        elif event.button == 3:  # Right mouse button for panning
            self.game.camera.start_drag(mouse_pos[0], mouse_pos[1])
            self.game.is_panning = True
        elif event.button == 4:  # Mouse wheel up for zoom in
            self.game.camera.zoom_at(mouse_pos[0], mouse_pos[1], 1.1)
        elif event.button == 5:  # Mouse wheel down for zoom out
            self.game.camera.zoom_at(mouse_pos[0], mouse_pos[1], 0.9)
        elif event.button == 1:  # Left mouse button
            if in_sidebar:
                self.handle_sidebar_click(event, mouse_pos)
            else:
                self.handle_game_click(event, mouse_pos)
    
    def handle_sidebar_click(self, event, mouse_pos):
        """Handle clicks in the sidebar UI"""
        ui_result = self.game.ui.handle_event(event, {
            "money": self.game.money,
            "lives": self.game.lives,
            "wave": self.game.wave,
            "current_tower_type": self.game.current_tower_type,
            "selected_tower": self.game.selected_tower,
            "enemies_remaining": len(self.game.enemies)
        })
        
        if ui_result["action"] == "select_tower":
            self.game.current_tower_type = ui_result["target"]
            self.game.selected_tower = None
        elif ui_result["action"] == "upgrade" and self.game.selected_tower:
            self.game.upgrade_tower(self.game.selected_tower, ui_result["target"])
        elif ui_result["action"] == "sell" and self.game.selected_tower:
            self.game.sell_tower(self.game.selected_tower)
        elif ui_result["action"] == "start_wave" and not self.game.wave_active:
            self.game.wave_manager.start_wave()
    
    def handle_game_click(self, event, mouse_pos):
        """Handle clicks in the game area"""
        world_pos = Vector2(*self.game.camera.unapply(mouse_pos[0], mouse_pos[1]))
        
        # If shift is pressed, start panning with left mouse button
        if self.game.is_shift_pressed:
            self.game.camera.start_drag(mouse_pos[0], mouse_pos[1])
            self.game.is_panning = True
        else:
            # Check if clicked on existing tower
            tower_clicked = False
            for tower in self.game.towers:
                if (tower.pos - world_pos).length() <= tower.radius:
                    self.game.selected_tower = tower
                    tower_clicked = True
                    break
                    
            # If no tower clicked, start dragging a new tower
            if not tower_clicked:
                cost = tower_types[self.game.current_tower_type]["cost"]
                if self.game.money >= cost:
                    self.game.dragging_tower = True
                    self.game.tower_preview_pos = world_pos
                else:
                    self.game.floating_texts.append(
                        FloatingText("Not enough money!", 
                                  (world_pos.x, world_pos.y - 20),
                                  (255, 100, 100), 20)
                    )
    
    def handle_mouse_up_event(self, event):
        """Handle mouse button up events"""
        if event.button == 1 and self.game.is_panning and self.game.is_shift_pressed:
            # End of shift+left click panning
            self.game.camera.end_drag()
            self.game.is_panning = False
        elif event.button == 2:  # Middle mouse button released
            if self.game.is_panning:
                self.game.camera.end_drag()
                self.game.is_panning = False
        elif event.button == 3:  # Right mouse button released
            if self.game.is_panning:
                self.game.camera.end_drag()
                self.game.is_panning = False
        elif event.button == 1 and self.game.dragging_tower:  # Complete tower placement
            mouse_pos = pygame.mouse.get_pos()
            world_pos = Vector2(*self.game.camera.unapply(mouse_pos[0], mouse_pos[1]))
            
            # Check tower placement validity
            valid_placement = self.game.is_valid_tower_placement(self.game.tower_preview_pos)
            
            if valid_placement:
                if self.game.add_tower(world_pos):
                    pass  # Tower added successfully
                else:
                    self.game.floating_texts.append(
                        FloatingText("Not enough money!", 
                                  (world_pos.x, world_pos.y - 20),
                                  (255, 100, 100), 20)
                    )
            else:
                self.game.floating_texts.append(
                    FloatingText("Invalid placement!", 
                              (world_pos.x, world_pos.y - 20),
                              (255, 100, 100), 20)
                )
            
            self.game.dragging_tower = False
            self.game.tower_preview_pos = None
    
    def handle_mouse_motion_event(self, event):
        """Handle mouse motion events"""
        # Update tower preview position when dragging
        if self.game.dragging_tower:
            mouse_pos = pygame.mouse.get_pos()
            self.game.tower_preview_pos = Vector2(*self.game.camera.unapply(mouse_pos[0], mouse_pos[1])) 