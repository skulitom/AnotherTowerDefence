"""
Input Manager - Handles all user input and controls
"""
import pygame
import os
import tkinter as tk
from tkinter import filedialog
from pygame import Vector2

from game.ui import FloatingText
from game.settings import tower_types

class InputManager:
    def __init__(self, game_manager):
        """Initialize the input manager"""
        self.game = game_manager
        # Key states
        self.keys_pressed = {}
        # Hide Tkinter root window
        self.tk_root = None
    
    def handle_event(self, event):
        """Process a pygame event"""
        handled = False
        
        if event.type == pygame.VIDEORESIZE:
            handled = self.handle_resize_event(event)
        elif event.type == pygame.KEYDOWN:
            handled = self.handle_key_down_event(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            handled = self.handle_mouse_down_event(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            handled = self.handle_mouse_up_event(event)
        elif event.type == pygame.MOUSEMOTION:
            handled = self.handle_mouse_motion_event(event)
        
        # Update keyboard state for continuous input detection
        self.update_key_state()
        
        # Update mouse button state
        self.update_mouse_state()
        
        return handled
    
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
    
    def update(self, dt):
        """Update input state based on continuous input"""
        # Update camera based on keyboard input
        self.update_camera(dt)
        
        # Update mouse state for continuous input
        self.update_mouse_state()
        
        # Update key state for continuous input
        self.update_key_state()
    
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
        return True
    
    def handle_key_down_event(self, event):
        """Handle key down events"""
        if event.key == pygame.K_ESCAPE:
            if self.game.fullscreen:
                # Exit fullscreen instead of quitting if in fullscreen mode
                pygame.display.set_mode((self.game.screen_width, self.game.screen_height), pygame.RESIZABLE)
                self.game.fullscreen = False
            elif self.game.dragging_tower:
                # Cancel tower placement
                self.game.dragging_tower = False
                self.game.tower_preview_pos = None
                self.game.ui.add_floating_text(
                    self.game.screen_width * 0.5,
                    50,
                    "Tower placement canceled",
                    (255, 100, 100),
                    size=24,
                    lifetime=1.5
                )
            elif self.game.selected_tower:
                # Deselect tower
                self.game.selected_tower = None
                self.game.ui.add_floating_text(
                    self.game.screen_width * 0.5,
                    50,
                    "Tower deselected",
                    (200, 200, 200),
                    size=20,
                    lifetime=1.0
                )
            elif self.game.tower_placement_mode:
                # Exit tower placement mode
                self.game.tower_placement_mode = False
                self.game.ui.add_floating_text(
                    self.game.screen_width * 0.5,
                    50,
                    "Tower placement mode: OFF",
                    (255, 100, 100),
                    size=24,
                    lifetime=1.5
                )
            else:
                # Quit game
                pygame.event.post(pygame.event.Event(pygame.QUIT))
        elif event.key == pygame.K_F11:
            # Toggle fullscreen
            if self.game.fullscreen:
                pygame.display.set_mode((self.game.screen_width, self.game.screen_height), pygame.RESIZABLE)
                self.game.fullscreen = False
            else:
                pygame.display.set_mode((self.game.screen_width, self.game.screen_height), pygame.FULLSCREEN)
                self.game.fullscreen = True
        elif event.key == pygame.K_p:
            # Toggle tower placement mode
            self.game.tower_placement_mode = not self.game.tower_placement_mode
            # If we're exiting placement mode, cancel any in-progress tower placement
            if not self.game.tower_placement_mode and self.game.dragging_tower:
                self.game.dragging_tower = False
                self.game.tower_preview_pos = None
            
            # Add visual feedback
            status = "ON" if self.game.tower_placement_mode else "OFF"
            color = (100, 255, 100) if self.game.tower_placement_mode else (255, 100, 100)
            self.game.ui.add_floating_text(
                self.game.screen_width * 0.5,
                50,
                f"Tower placement mode: {status}",
                color,
                size=24,
                lifetime=2.0
            )
        elif event.key == pygame.K_SPACE:
            # Start next wave if not active
            if not self.game.wave_active and not self.game.game_over:
                self.game.wave_manager.start_wave()
        elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7]:
            # Select tower type
            key_to_tower = {
                pygame.K_1: "Fire",
                pygame.K_2: "Water",
                pygame.K_3: "Earth",
                pygame.K_4: "Air",
                pygame.K_5: "Lightning",
                pygame.K_6: "Ice",
                pygame.K_7: "Nature"
            }
            if event.key in key_to_tower:
                self.game.current_tower_type = key_to_tower[event.key]
                self.game.selected_tower = None
                # Automatically enter tower placement mode
                self.game.tower_placement_mode = True
                # Add visual feedback
                self.game.ui.add_floating_text(
                    self.game.screen_width * 0.5,
                    50,
                    f"Selected: {self.game.current_tower_type} Tower",
                    (100, 255, 100),
                    size=24,
                    lifetime=2.0
                )
        elif event.key == pygame.K_x and self.game.selected_tower:
            # Sell selected tower
            tower_type = self.game.selected_tower.tower_type
            refund = self.game.sell_tower(self.game.selected_tower)
            self.game.ui.add_floating_text(
                self.game.screen_width * 0.5,
                50,
                f"Sold {tower_type} Tower for ${refund}",
                (255, 255, 100),
                size=24,
                lifetime=2.0
            )
        elif event.key in [pygame.K_q, pygame.K_w, pygame.K_e, pygame.K_r] and self.game.selected_tower:
            # Upgrade selected tower
            key_to_upgrade = {
                pygame.K_q: "damage",
                pygame.K_w: "range",
                pygame.K_e: "speed",
                pygame.K_r: "special"
            }
            upgrade_result = self.game.upgrade_tower(self.game.selected_tower, key_to_upgrade[event.key])
            if upgrade_result:
                self.game.ui.add_floating_text(
                    self.game.screen_width * 0.5,
                    50,
                    f"Upgraded {self.game.selected_tower.tower_type} Tower {key_to_upgrade[event.key]}",
                    (100, 255, 255),
                    size=24,
                    lifetime=2.0
                )
        elif event.key == pygame.K_F5:
            # Save game (F5)
            self.game.save_menu.show("save")
            return True
        elif event.key == pygame.K_F9:
            # Load game (F9)
            self.game.save_menu.show("load")
            return True
        elif event.key == pygame.K_F2:
            # New game (F2)
            self.game.reset()
            self.game.ui.add_floating_text(
                self.game.screen_width * 0.5,
                50,
                "New Game Started",
                (100, 255, 100),
                size=24,
                lifetime=2.0
            )
            return True
        return True
    
    def open_load_dialog(self):
        """Open a file dialog to select a save file to load"""
        # Get list of save files
        save_files = self.game.get_save_files()
        
        if not save_files:
            self.game.floating_texts.append(
                FloatingText(
                    "No save files found!",
                    (self.game.screen_width // 2, self.game.screen_height // 2 - 50),
                    (255, 100, 100),
                    24,
                    duration=3.0
                )
            )
            return False
            
        # Initialize tkinter for file dialog
        # We need to temporarily pause the game and switch to windowed mode
        was_fullscreen = self.game.fullscreen
        if was_fullscreen:
            pygame.display.set_mode((self.game.screen_width, self.game.screen_height), pygame.RESIZABLE)
            self.game.fullscreen = False
        
        # Create hidden tkinter root
        if self.tk_root is None:
            self.tk_root = tk.Tk()
            self.tk_root.withdraw()  # Hide the root window
        
        # Open file dialog
        file_path = filedialog.askopenfilename(
            initialdir=self.game.saves_dir,
            title="Load Saved Game",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
        )
        
        # Restore fullscreen if needed
        if was_fullscreen:
            pygame.display.set_mode((self.game.screen_width, self.game.screen_height), pygame.FULLSCREEN)
            self.game.fullscreen = True
        
        # Load the selected file
        if file_path:
            self.game.load_game(file_path)
            return True
            
        return False
    
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
            return True
        elif event.button == 3:  # Right mouse button for panning
            self.game.camera.start_drag(mouse_pos[0], mouse_pos[1])
            self.game.is_panning = True
            return True
        elif event.button == 4:  # Mouse wheel up for zoom in
            self.game.camera.zoom_at(mouse_pos[0], mouse_pos[1], 1.1)
            return True
        elif event.button == 5:  # Mouse wheel down for zoom out
            self.game.camera.zoom_at(mouse_pos[0], mouse_pos[1], 0.9)
            return True
        elif event.button == 1:  # Left mouse button
            if in_sidebar:
                return self.handle_sidebar_click(event, mouse_pos)
            else:
                return self.handle_game_click(event, mouse_pos)
                
        return True  # Default to handled
    
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
            # Automatically enter tower placement mode when selecting a tower type
            self.game.tower_placement_mode = True
            # Add a floating text to inform the user
            self.game.ui.add_floating_text(
                self.game.screen_width * 0.5,
                50,
                f"Tower placement mode: {self.game.current_tower_type} Tower",
                (100, 255, 100),
                size=24,
                lifetime=2.0
            )
            return True
        elif ui_result["action"] == "upgrade" and self.game.selected_tower:
            self.game.upgrade_tower(self.game.selected_tower, ui_result["target"])
            return True
        elif ui_result["action"] == "sell" and self.game.selected_tower:
            self.game.sell_tower(self.game.selected_tower)
            return True
        elif ui_result["action"] == "start_wave" and not self.game.wave_active:
            self.game.wave_manager.start_wave()
            return True
        elif ui_result["action"] == "toggle_placement_mode":
            self.game.tower_placement_mode = not self.game.tower_placement_mode
            # If turning off placement mode, cancel any in-progress placement
            if not self.game.tower_placement_mode and self.game.dragging_tower:
                self.game.dragging_tower = False 
                self.game.tower_preview_pos = None
            # Add a floating text to inform the user
            status = "ON" if self.game.tower_placement_mode else "OFF"
            color = (100, 255, 100) if self.game.tower_placement_mode else (255, 100, 100)
            self.game.ui.add_floating_text(
                self.game.screen_width * 0.5,
                50,
                f"Tower placement mode: {status}",
                color,
                size=24,
                lifetime=2.0
            )
            return True
        elif ui_result["action"] == "open_save_menu":
            self.game.save_menu.show("save")
            return True
            
        return True  # Default to handled
    
    def handle_game_click(self, event, mouse_pos):
        """Handle clicks in the game area"""
        world_pos = Vector2(*self.game.camera.unapply(mouse_pos[0], mouse_pos[1]))
        
        # If shift is pressed, start panning with left mouse button
        if self.game.is_shift_pressed:
            self.game.camera.start_drag(mouse_pos[0], mouse_pos[1])
            self.game.is_panning = True
            return True
        else:
            # Check if clicked on existing tower
            tower_clicked = False
            for tower in self.game.towers:
                if (tower.pos - world_pos).length() <= tower.radius:
                    self.game.selected_tower = tower
                    tower_clicked = True
                    # If a tower is selected, exit tower placement mode
                    self.game.tower_placement_mode = False
                    return True
                    
            # If no tower clicked and tower placement mode is active, start dragging a new tower
            if not tower_clicked:
                if self.game.tower_placement_mode:
                    cost = tower_types[self.game.current_tower_type]["cost"]
                    if self.game.money >= cost:
                        self.game.dragging_tower = True
                        self.game.tower_preview_pos = world_pos
                        return True
                    else:
                        self.game.floating_texts.append(
                            FloatingText("Not enough money!", 
                                      (world_pos.x, world_pos.y - 20),
                                      (255, 100, 100), 20)
                        )
                        return True
                else:
                    # If we're not in tower placement mode and no tower was clicked,
                    # just deselect the current tower
                    self.game.selected_tower = None
                    return True
        
        return True  # Default to handled
    
    def handle_mouse_up_event(self, event):
        """Handle mouse button up events"""
        if event.button == 1 and self.game.is_panning and self.game.is_shift_pressed:
            # End of shift+left click panning
            self.game.camera.end_drag()
            self.game.is_panning = False
            return True
        elif event.button == 2:  # Middle mouse button released
            if self.game.is_panning:
                self.game.camera.end_drag()
                self.game.is_panning = False
                return True
        elif event.button == 3:  # Right mouse button released
            if self.game.is_panning:
                self.game.camera.end_drag()
                self.game.is_panning = False
                return True
        elif event.button == 1 and self.game.dragging_tower:  # Complete tower placement
            mouse_pos = pygame.mouse.get_pos()
            world_pos = Vector2(*self.game.camera.unapply(mouse_pos[0], mouse_pos[1]))
            
            # Check tower placement validity
            valid_placement = self.game.is_valid_tower_placement(self.game.tower_preview_pos)
            
            if valid_placement:
                if self.game.add_tower(world_pos):
                    self.game.ui.add_floating_text(
                        self.game.screen_width * 0.5,
                        50,
                        f"Placed {self.game.current_tower_type} Tower",
                        (100, 255, 100),
                        size=24,
                        lifetime=1.5
                    )
                else:
                    self.game.ui.add_floating_text(
                        self.game.screen_width * 0.5,
                        50,
                        f"Not enough money for {self.game.current_tower_type} Tower!",
                        (255, 100, 100),
                        size=24,
                        lifetime=2.0
                    )
                    self.game.floating_texts.append(
                        FloatingText("Not enough money!", 
                                  (world_pos.x, world_pos.y - 20),
                                  (255, 100, 100), 20)
                    )
            else:
                self.game.ui.add_floating_text(
                    self.game.screen_width * 0.5,
                    50,
                    "Invalid tower placement location!",
                    (255, 100, 100),
                    size=24,
                    lifetime=2.0
                )
                self.game.floating_texts.append(
                    FloatingText("Invalid placement!", 
                              (world_pos.x, world_pos.y - 20),
                              (255, 100, 100), 20)
                )
            
            self.game.dragging_tower = False
            self.game.tower_preview_pos = None
            return True
            
        return False  # Not handled
    
    def handle_mouse_motion_event(self, event):
        """Handle mouse motion events"""
        # Update tower preview position when dragging
        if self.game.dragging_tower:
            mouse_pos = pygame.mouse.get_pos()
            self.game.tower_preview_pos = Vector2(*self.game.camera.unapply(mouse_pos[0], mouse_pos[1])) 
        return True 