"""
Game Manager - Central manager for game state
"""
import pygame
import random
from pygame import Vector2

from game.core.camera import Camera
from game.settings import tower_types, upgrade_paths
from game.enemy import Enemy
from game.towers import create_tower
from game.projectile import Projectile
from game.assets import load_assets
from game.utils import ParticleSystem
from game.ui import GameUI, FloatingText
from game.managers.input_manager import InputManager
from game.managers.wave_manager import WaveManager
from game.managers.renderer import Renderer
from game.managers.synergy_manager import SynergyManager
from game.managers.weather_manager import WeatherManager
from game.managers.evolution_manager import EvolutionManager

class GameManager:
    def __init__(self, screen_width=1400, screen_height=900):
        """Initialize the game manager"""
        # Initialize window
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
        pygame.display.set_caption("Element Crystal Tower Defense")
        
        # Load assets
        self.assets = load_assets()
        
        # Create path for enemies
        self.base_path_points = [(0, 0.222), (0.25, 0.222), (0.25, 0.722), (0.5, 0.722),
                          (0.5, 0.222), (0.75, 0.222), (0.75, 0.722), (1.0, 0.722)]
        self.path_points = [(p[0] * screen_width, p[1] * screen_height) for p in self.base_path_points]
        
        # Initialize game state
        self.reset()
        
        # Setup systems
        self.create_systems()
        
        # Added missing attribute
        self.game_over = False
    
    def create_systems(self):
        """Initialize game subsystems"""
        # Calculate the sidebar width
        self.sidebar_width = int(self.screen_width * 0.185)
        
        # Create camera
        self.gameplay_area = (0, 0, self.screen_width, self.screen_height)
        self.camera = Camera(self.screen_width, self.screen_height, self.gameplay_area)
        self.camera.x = self.screen_width / 2
        self.camera.y = self.screen_height / 2
        
        # Create UI
        self.ui = GameUI(self.screen_width, self.screen_height)
        
        # Create particle system
        self.particles = ParticleSystem(max_particles=500)
        
        # Create managers
        self.input_manager = InputManager(self)
        self.wave_manager = WaveManager(self)
        self.renderer = Renderer(self)
        
        # Add our new systems
        self.synergy_manager = SynergyManager(self)
        self.weather_manager = WeatherManager(self)
        self.evolution_manager = EvolutionManager(self)
        
        # Visual effects
        self.screen_flash = 0
        self.screen_flash_color = (255, 255, 255)
    
    def reset(self):
        """Reset the game state to initial values"""
        # Game objects
        self.towers = []
        self.enemies = []
        self.projectiles = []
        self.floating_texts = []
        
        # Game state
        self.lives = 10
        self.money = 150
        self.score = 0
        self.wave = 0
        self.current_tower_type = "Fire"
        self.selected_tower = None
        self.hover_tower = None
        self.wave_active = False
        self.fullscreen = False
        self.game_over = False  # Reset game over flag
        
        # Tower placement
        self.is_shift_pressed = False
        self.dragging_tower = False
        self.tower_drag_start = None
        self.tower_preview_pos = None
        
        # Camera state
        self.is_panning = False
        
        # Tower ID counter (for uniquely identifying towers)
        self.next_tower_id = 0
        
        # If systems are initialized, reset them too
        if hasattr(self, 'synergy_manager'):
            self.active_synergies = {}
        
        if hasattr(self, 'weather_manager'):
            self.weather_manager.current_weather = "clear"
            self.weather_manager.weather_timer = 0
        
        # If camera exists, reset it
        if hasattr(self, 'camera'):
            self.camera.x = self.screen_width / 2
            self.camera.y = self.screen_height / 2
            self.camera.zoom = 1.0
    
    def handle_event(self, event):
        """Handle pygame events"""
        # Let input manager handle the events first
        if self.input_manager.handle_event(event):
            return True
        
        # Handle mouse events
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Convert mouse position to world coordinates
                world_pos = self.camera.screen_to_world(event.pos)
                
                # Check if clicked on a tower
                clicked_tower = None
                for tower in self.towers:
                    if (world_pos - tower.pos).length() <= tower.radius:
                        clicked_tower = tower
                        break
                
                if clicked_tower:
                    # Select tower
                    self.selected_tower = clicked_tower
                    return True
                elif self.is_valid_tower_position(world_pos):
                    # Create tower at click position
                    new_tower = self.create_tower(self.current_tower_type, world_pos)
                    if new_tower:
                        self.selected_tower = new_tower
                    return True
                else:
                    # Deselect tower if clicking empty space
                    self.selected_tower = None
                    return True
            
            elif event.button == 3:  # Right click
                # Deselect tower
                self.selected_tower = None
                return True
                
        # Handle key events
        elif event.type == pygame.KEYDOWN:
            # Start wave
            if event.key == pygame.K_SPACE and not self.wave_active:
                self.wave_manager.start_wave()
                return True
            
            # Tower type selection
            tower_keys = {
                pygame.K_1: "Fire",
                pygame.K_2: "Water",
                pygame.K_3: "Air",
                pygame.K_4: "Earth",
                pygame.K_5: "Darkness",
                pygame.K_6: "Light",
                pygame.K_7: "Life"
            }
            
            if event.key in tower_keys:
                self.current_tower_type = tower_keys[event.key]
                return True
            
            # Handle tower upgrades
            if self.selected_tower:
                upgrade_keys = {
                    pygame.K_q: "damage",
                    pygame.K_w: "range",
                    pygame.K_e: "speed",
                    pygame.K_r: "special"
                }
                
                if event.key in upgrade_keys:
                    upgrade_type = upgrade_keys[event.key]
                    self.upgrade_tower(self.selected_tower, upgrade_type)
                    return True
                
                # Sell tower
                if event.key == pygame.K_x:
                    self.sell_tower(self.selected_tower)
                    return True
        
        # Check for UI interaction - evolution buttons
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.selected_tower:
            # Check if an evolution button was clicked
            if self.evolution_manager.can_evolve(self.selected_tower) and hasattr(self.evolution_manager, "evolution_buttons"):
                for button, evo_index in self.evolution_manager.evolution_buttons:
                    if button.collidepoint(event.pos):
                        self.evolution_manager.evolve_tower(self.selected_tower, evo_index)
                        return True
        
        return False
    
    def update(self, dt):
        """Update the game state"""
        # Skip updates if game is over
        if self.game_over:
            return
        
        # Update input
        self.input_manager.update(dt)
        
        # Update tower synergies
        self.synergy_manager.check_synergies()
        self.synergy_manager.update(dt)
        
        # Update weather
        self.weather_manager.update(dt)
        
        # Process tower evolutions
        for tower in self.towers:
            self.evolution_manager.apply_evolution_effects(tower, dt)
        
        # Update world mouse position
        self.update_mouse_position()
        
        # Update towers
        self.update_towers(dt)
        
        # Update enemies
        self.update_enemies(dt)
        
        # Update projectiles
        self.update_projectiles(dt)
        
        # Update particles
        self.particles.update(dt)
        
        # Update floating texts
        self.update_floating_texts(dt)
        
        # Update UI
        self.ui.update(dt)
        
        # Update wave progression
        if self.wave_active:
            self.wave_manager.update(dt)
            
            # Check if wave is complete
            if len(self.enemies) == 0 and len(self.wave_manager.current_wave_enemies) == 0:
                self.wave_active = False
                self.on_wave_complete()
        
        # Update screen flash effect
        if self.screen_flash > 0:
            self.screen_flash -= dt
    
    def update_mouse_position(self):
        """Update mouse-related state"""
        mouse_pos = pygame.mouse.get_pos()
        world_mouse_pos = Vector2(*self.camera.unapply(mouse_pos[0], mouse_pos[1]))
        
        # Find hovered tower
        self.hover_tower = None
        for tower in self.towers:
            if (tower.pos - world_mouse_pos).length() <= tower.radius:
                self.hover_tower = tower
                break
    
    def update_towers(self, dt):
        """Update all towers"""
        for tower in self.towers:
            # Apply buffs from Life towers
            if tower.tower_type != "Life":
                tower.buff_multiplier = 1.0
                for buff_tower in self.towers:
                    if buff_tower.tower_type == "Life":
                        buff_range = tower_types["Life"].get("buff_range", 200)
                        if (tower.pos - buff_tower.pos).length() <= buff_range:
                            tower.buff_multiplier *= tower_types["Life"].get("buff_damage", 1.2)
                tower.current_damage = tower.damage * tower.buff_multiplier
            
            # Update tower
            tower.update(dt, self.enemies, self.projectiles, self.particles)
    
    def update_enemies(self, dt):
        """Update all enemies"""
        for enemy in self.enemies[:]:
            # Update enemy position
            enemy.update(dt, self.enemies)
            
            # Handle enemy reaching end of path
            if enemy.reached_end:
                self.lives -= 1
                self.enemies.remove(enemy)
                self.floating_texts.append(
                    FloatingText("-1 Life!", 
                               (enemy.pos.x, enemy.pos.y - 20),
                               (255, 100, 100), 24)
                )
                self.particles.add_explosion(enemy.pos.x, enemy.pos.y, (255, 0, 0), count=15)
                
                # Check for game over
                if self.lives <= 0:
                    self.game_over = True
                    self.show_game_over()
            
            # Handle enemy death
            elif enemy.health <= 0:
                self.money += enemy.reward
                self.enemies.remove(enemy)
                
                # Show reward text
                self.floating_texts.append(
                    FloatingText(f"+${enemy.reward}", 
                               (enemy.pos.x, enemy.pos.y - 20),
                               (255, 255, 0), 20)
                )
                
                # Show death explosion effect
                self.particles.add_explosion(enemy.pos.x, enemy.pos.y, enemy.color, count=20)
                
                # If target of any tower, clear reference
                for tower in self.towers:
                    if tower.targeting_enemy == enemy:
                        tower.targeting_enemy = None
            
            # Apply burn damage if enemy has burn status
            elif "burn" in enemy.status_effects:
                burn_data = enemy.status_effects["burn"]
                if enemy.take_damage(burn_data["value"] * dt):
                    self.money += enemy.reward
                    self.enemies.remove(enemy)
                    self.floating_texts.append(
                        FloatingText(f"+${enemy.reward}", 
                                   (enemy.pos.x, enemy.pos.y - 20),
                                   (255, 255, 0), 20)
                    )
                    self.particles.add_explosion(enemy.pos.x, enemy.pos.y, enemy.color, count=20)
    
    def update_projectiles(self, dt):
        """Update all projectiles"""
        for projectile in self.projectiles[:]:
            chain_proj = projectile.update(dt, self.enemies, self.particles)
            if chain_proj:
                self.projectiles.append(chain_proj)
            if not projectile.active:
                self.projectiles.remove(projectile)
    
    def update_floating_texts(self, dt):
        """Update all floating texts"""
        for text in self.floating_texts[:]:
            if not text.update(dt):
                self.floating_texts.remove(text)
    
    def update_path_points(self):
        """Recalculate path points when window is resized"""
        self.path_points = [(p[0] * self.screen_width, p[1] * self.screen_height) 
                          for p in self.base_path_points]
        
        # Update paths for all existing enemies
        for enemy in self.enemies:
            enemy.path = self.path_points
            
        return self.path_points
    
    def add_tower(self, position):
        """Add a new tower at the specified position"""
        cost = tower_types[self.current_tower_type]["cost"]
        if self.money >= cost:
            self.money -= cost
            new_tower = create_tower(position, self.current_tower_type)
            
            # Assign a unique ID to the tower
            new_tower.id = self.next_tower_id
            self.next_tower_id += 1
            
            self.towers.append(new_tower)
            self.selected_tower = new_tower
            
            # Add build effect
            self.particles.add_explosion(new_tower.pos.x, new_tower.pos.y, 
                                    tower_types[self.current_tower_type]["color"], 
                                    count=20, size_range=(2, 6))
            return True
        return False
    
    def sell_tower(self, tower):
        """Sell a tower and get some money back"""
        if tower in self.towers:
            # Calculate sell value (70% of investment)
            base_cost = tower_types[tower.tower_type]["cost"]
            upgrade_cost = 0
            for upgrade_type, level in tower.upgrades.items():
                for i in range(level):
                    if i < len(upgrade_paths[upgrade_type]["levels"]):
                        upgrade_cost += upgrade_paths[upgrade_type]["levels"][i]["cost"]
            
            sell_value = int((base_cost + upgrade_cost) * 0.7)
            self.money += sell_value
            
            # Create a selling effect
            self.particles.add_explosion(tower.pos.x, tower.pos.y, 
                                      (255, 215, 0), count=30, size_range=(3, 8))
            self.floating_texts.append(
                FloatingText(f"+${sell_value}", 
                           (tower.pos.x, tower.pos.y - 30),
                           (255, 255, 0), 24)
            )
            
            # Remove the tower
            self.towers.remove(tower)
            if self.selected_tower == tower:
                self.selected_tower = None
            
            return sell_value
        return 0
    
    def upgrade_tower(self, tower, upgrade_type):
        """Upgrade a tower"""
        if tower in self.towers:
            upgrade_cost = tower.get_upgrade_cost(upgrade_type)
            if self.money >= upgrade_cost:
                self.money -= upgrade_cost
                tower.upgrade(upgrade_type)
                self.floating_texts.append(
                    FloatingText(f"Upgraded {upgrade_type}!", 
                               (tower.pos.x, tower.pos.y - 30),
                               (100, 255, 100), 20)
                )
                return True
        return False
    
    def is_valid_tower_placement(self, position):
        """Check if tower placement is valid"""
        # Check if too close to path
        for i in range(len(self.path_points) - 1):
            p1 = Vector2(self.path_points[i])
            p2 = Vector2(self.path_points[i + 1])
            dist = self.distance_to_line_segment(position, p1, p2)
            if dist < 40:  # Minimum distance from path
                return False
        
        # Check if too close to other towers
        for tower in self.towers:
            if (tower.pos - position).length() < 40:
                return False
        
        return True
    
    def is_valid_tower_position(self, position):
        """Check if tower position is valid (alias for is_valid_tower_placement)"""
        return self.is_valid_tower_placement(position)
    
    def distance_to_line_segment(self, p, v, w):
        """Calculate minimum distance from point p to line segment vw"""
        l2 = (v - w).length_squared()
        if l2 == 0:
            return (p - v).length()
        
        t = max(0, min(1, Vector2.dot(p - v, w - v) / l2))
        projection = v + t * (w - v)
        return (p - projection).length()
    
    def handle_resize(self, width, height):
        """Handle window resize event"""
        self.screen_width = width
        self.screen_height = height
        self.screen = pygame.display.set_mode((width, height), 
                                          pygame.RESIZABLE | (pygame.FULLSCREEN if self.fullscreen else 0))
        
        # Update UI and camera with new dimensions
        self.sidebar_width = int(width * 0.185)
        self.gameplay_area = (0, 0, width, height)
        self.camera.update_screen_size(width, height, self.gameplay_area)
        self.ui.update_screen_size(width, height)
        
        # Update path for enemies
        self.update_path_points()
        
        # Re-center camera based on new dimensions
        self.camera.x = width / 2
        self.camera.y = height / 2
    
    def render(self):
        """Render the game"""
        # Fill background
        self.screen.fill((20, 20, 30))
        
        # Apply weather background modifications
        bg_mod = self.weather_manager.get_background_color_mod()
        if bg_mod != (0, 0, 0, 0):
            # Apply color modification
            overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            r, g, b, a = bg_mod
            overlay.fill((
                max(0, min(255, 128 + r)),
                max(0, min(255, 128 + g)),
                max(0, min(255, 128 + b)),
                a
            ))
            self.screen.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
        
        # Let the renderer handle most drawing
        self.renderer.render(self.screen)
        
        # Render weather effects
        self.weather_manager.render(self.screen)
        
        # Render synergy effects
        self.synergy_manager.render(self.screen, self.camera)
        
        # Render screen flash effect
        if self.screen_flash > 0:
            flash_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            alpha = int(255 * self.screen_flash * 0.5)  # 50% max opacity
            flash_surface.fill(self.screen_flash_color + (alpha,))
            self.screen.blit(flash_surface, (0, 0))
    
    def is_game_over(self):
        """Check if the game is over"""
        return self.lives <= 0
    
    def show_game_over(self):
        """Display the game over screen"""
        self.renderer.show_game_over(self.wave)
    
    def on_wave_complete(self):
        """Handle wave completion"""
        self.wave += 1
        self.money += 100  # Assuming a default reward for completing a wave
        self.ui.add_floating_text(self.screen_width / 2, self.screen_height / 2, f"Wave {self.wave} completed!", (0, 255, 0), size=24, lifetime=3.0)
    
    def on_enemy_killed(self, enemy, tower=None):
        """Handle enemy death"""
        # Add money
        self.money += enemy.reward
        
        # Add score
        self.score += enemy.reward
        
        # If killed by a tower, increment its kill count for evolution tracking
        if tower:
            if not hasattr(tower, "kills"):
                tower.kills = 0
            tower.kills += 1
            
            # Check if tower can now evolve
            if self.evolution_manager.can_evolve(tower) and not hasattr(tower, "evolution_notified"):
                self.ui.add_floating_text(
                    tower.pos.x, tower.pos.y - 20,
                    "Tower can evolve! Select to view options.",
                    (255, 215, 0),
                    size=14,
                    lifetime=3.0
                )
                tower.evolution_notified = True
    
    def create_tower(self, tower_type, position):
        """Create a tower of the specified type at the given position (alias for add_tower)"""
        # Store the current tower type
        previous_tower_type = self.current_tower_type
        
        # Temporarily set the current tower type to the requested type
        self.current_tower_type = tower_type
        
        # Create the tower
        result = self.add_tower(position)
        
        # Restore the previous tower type
        self.current_tower_type = previous_tower_type
        
        # Return the created tower or None
        if result:
            return self.selected_tower
        return None 