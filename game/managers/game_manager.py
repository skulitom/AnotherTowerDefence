"""
Game Manager - Central manager for game state
"""
import pygame
import random
from pygame import Vector2

from game.core.camera import Camera
from game.settings import tower_types, upgrade_paths
from game.enemy import Enemy
from game.tower import Tower
from game.projectile import Projectile
from game.assets import load_assets
from game.utils import ParticleSystem
from game.ui import GameUI, FloatingText
from game.managers.input_manager import InputManager
from game.managers.wave_manager import WaveManager
from game.managers.renderer import Renderer

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
        self.wave = 0
        self.current_tower_type = "Fire"
        self.selected_tower = None
        self.hover_tower = None
        self.wave_active = False
        self.fullscreen = False
        
        # Tower placement
        self.is_shift_pressed = False
        self.dragging_tower = False
        self.tower_drag_start = None
        self.tower_preview_pos = None
        
        # Camera state
        self.is_panning = False
        
        # If camera exists, reset it
        if hasattr(self, 'camera'):
            self.camera.x = self.screen_width / 2
            self.camera.y = self.screen_height / 2
            self.camera.zoom = 1.0
    
    def handle_event(self, event):
        """Process a pygame event"""
        # Let the input manager handle the event
        self.input_manager.handle_event(event)
    
    def update(self, dt):
        """Update the game state"""
        # Update camera based on keyboard input
        self.input_manager.update_camera(dt)
        
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
        
        # Handle wave progression
        if self.wave_active:
            self.wave_manager.update(dt)
    
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
            new_tower = Tower(position, self.current_tower_type)
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
        self.renderer.render()
    
    def is_game_over(self):
        """Check if the game is over"""
        return self.lives <= 0
    
    def show_game_over(self):
        """Display the game over screen"""
        self.renderer.show_game_over(self.wave) 