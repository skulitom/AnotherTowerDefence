import pygame
import random
import math
from pygame.math import Vector2
from game.settings import tower_types, upgrade_paths
from game.projectile import Projectile

# Define max visual levels, matching the value in assets.py
MAX_TOWER_VISUAL_LEVELS = 5

class BaseTower:
    """Base class for all tower types"""
    
    def __init__(self, pos, tower_type):
        self.pos = Vector2(pos)
        stats = tower_types[tower_type]
        self.tower_type = tower_type
        self.color = stats["color"]
        self.range = stats["range"]
        self.damage = stats["damage"]
        self.cooldown = stats["cooldown"]
        self.bullet_speed = stats["bullet_speed"]
        self.time_since_last_shot = 0
        self.radius = 15  # for drawing tower
        self.buff_multiplier = 1.0
        self.current_damage = self.damage
        
        # Game manager reference
        self.game = None  # Will be set by GameManager when tower is created
        
        # Special abilities
        self.special_ability = stats.get("special_ability")
        self.special_chance = stats.get("special_chance", 0)
        self.special_duration = stats.get("special_duration", 0)
        
        # Visual effects
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-10, 10)
        self.pulse_offset = random.random() * 6.28  # Random starting phase
        self.targeting_enemy = None
        self.target_lock_timer = 0
        self.particle_color = stats.get("particle_color", self.color)
        
        # Tower level and upgrade tracking
        self.level = 1
        self.upgrades = {"damage": 0, "range": 0, "speed": 0, "special": 0}
        self.total_upgrades = 0
        self.kills = 0
        self.damage_dealt = 0
        
        # Targeting
        self.targeting_priority = "First"  # Default targeting priority
        
        # Visuals
        self.current_sprite = None # Will hold the current sprite to draw
        
        # Tower-specific initialization
        self.initialize()
        
    def initialize(self):
        """Override this in subclasses for tower-specific initialization"""
        pass

    def upgrade(self, upgrade_type):
        """Upgrade the tower along a specific path"""
        if upgrade_type not in upgrade_paths:
            return False
            
        current_level = self.upgrades[upgrade_type]
        if current_level >= len(upgrade_paths[upgrade_type]["levels"]):
            return False  # Already at max level
            
        upgrade_info = upgrade_paths[upgrade_type]["levels"][current_level]
        
        # Apply the upgrade
        multiplier = upgrade_info["multiplier"]
        if upgrade_type == "damage":
            self.damage *= multiplier
            self.current_damage = self.damage * self.buff_multiplier
        elif upgrade_type == "range":
            self.range *= multiplier
        elif upgrade_type == "speed":
            self.cooldown *= multiplier  # Lower cooldown means faster attack
        elif upgrade_type == "special":
            # Special upgrades handled in subclasses
            self.upgrade_special(multiplier)
        
        # Update upgrade level and total
        self.upgrades[upgrade_type] += 1
        self.total_upgrades += 1
        self.level = 1 + self.total_upgrades // 2  # Level increases every 2 upgrades
        
        # Update the visual representation after upgrade
        self.update_visuals()
        
        return True
        
    def upgrade_special(self, multiplier):
        """Override in subclasses to handle special upgrades"""
        if self.special_chance:
            self.special_chance *= multiplier
        if self.special_duration:
            self.special_duration *= multiplier
        
    def can_upgrade(self, upgrade_type):
        """Check if the tower can be upgraded along a specific path"""
        if upgrade_type not in upgrade_paths:
            return False
            
        current_level = self.upgrades[upgrade_type]
        return current_level < len(upgrade_paths[upgrade_type]["levels"])
        
    def get_upgrade_cost(self, upgrade_type):
        """Get the cost of the next upgrade for this path"""
        if not self.can_upgrade(upgrade_type):
            return 0
            
        current_level = self.upgrades[upgrade_type]
        return upgrade_paths[upgrade_type]["levels"][current_level]["cost"]

    def update(self, dt, enemies, projectiles, particles=None):
        """Update tower state and target enemies"""
        self.time_since_last_shot += dt
        self.rotation += self.rotation_speed * dt
        
        # Update target lock timer
        if self.target_lock_timer > 0:
            self.target_lock_timer -= dt
        
        # Update the tower-specific logic
        self.update_tower(dt, enemies, projectiles, particles)
        
    def update_tower(self, dt, enemies, projectiles, particles=None):
        """Override in subclasses for tower-specific update logic"""
        # Find target
        target = self.find_target(enemies)
        
        # Fire at target if ready
        if target and self.time_since_last_shot >= self.cooldown:
            self.fire_at_target(target, projectiles, particles)
            self.time_since_last_shot = 0
    
    def find_target(self, enemies):
        """Find a suitable target based on tower targeting strategy"""
        # Keep current target if valid and target lock timer is active
        target = self.targeting_enemy
        
        # Check if current target is still valid
        if target and (target.health <= 0 or (target.pos - self.pos).length() > self.range):
            target = None
            self.targeting_enemy = None
        
        # Find new target if needed
        if not target or self.target_lock_timer <= 0:
            in_range_enemies = []
            
            for enemy in enemies:
                # Skip cloaked enemies unless tower can see them
                if "cloak" in enemy.status_effects and self.tower_type != "Light":
                    continue
                
                distance = (enemy.pos - self.pos).length()
                if distance <= self.range:
                    in_range_enemies.append(enemy)
            
            if in_range_enemies:
                # Choose target based on priority
                if self.targeting_priority == "First":
                    target = max(in_range_enemies, key=lambda e: e.get_path_progress())
                elif self.targeting_priority == "Last":
                    target = min(in_range_enemies, key=lambda e: e.get_path_progress())
                elif self.targeting_priority == "Strongest":
                    target = max(in_range_enemies, key=lambda e: e.health)
                elif self.targeting_priority == "Weakest":
                    target = min(in_range_enemies, key=lambda e: e.health)
                else:  # Default to First
                    target = max(in_range_enemies, key=lambda e: e.get_path_progress())
                
                self.targeting_enemy = target
                # Set target lock timer (higher levels lock targets longer)
                self.target_lock_timer = 1.0 + self.level * 0.5
                
        return target
        
    def is_preferred_target(self, enemy, distance, current_best, current_best_distance):
        """Default targeting strategy - closest enemy. Override in subclasses."""
        return distance < current_best_distance
    
    def fire_at_target(self, target, projectiles, particles=None):
        """Create a projectile aimed at the target"""
        # Create basic projectile
        new_projectile = Projectile(self.pos, target, self.current_damage, self.bullet_speed, self.tower_type)
        
        # Add special effect based on tower type
        self.apply_projectile_effects(new_projectile)
        
        # Add projectile to game
        projectiles.append(new_projectile)
        
        # Add muzzle flash effect
        if particles:
            for _ in range(5):
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(20, 50)
                velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
                particles.add_particle_params(
                    Vector2(self.pos), 
                    self.particle_color, 
                    velocity, 
                    random.uniform(2, 5), 
                    random.uniform(0.2, 0.5)
                )
    
    def apply_projectile_effects(self, projectile):
        """Apply tower-specific effects to projectile. Override in subclasses."""
        if self.special_ability and self.special_chance > 0:
            if self.special_ability == "burn":
                projectile.effect = {
                    "name": "burn",
                    "chance": self.special_chance,
                    "duration": self.special_duration,
                    "damage": tower_types[self.tower_type].get("special_damage", 5)
                }
            elif self.special_ability == "slow":
                projectile.effect = {
                    "name": "slow",
                    "chance": self.special_chance,
                    "duration": self.special_duration,
                    "amount": tower_types[self.tower_type].get("special_amount", 0.5)
                }
            elif self.special_ability == "chain":
                projectile.effect = {
                    "name": "chain",
                    "chance": self.special_chance,
                    "targets": tower_types[self.tower_type].get("special_targets", 3),
                    "damage_falloff": tower_types[self.tower_type].get("special_damage_falloff", 0.7)
                }
            elif self.special_ability == "stun":
                projectile.effect = {
                    "name": "stun",
                    "chance": self.special_chance,
                    "duration": self.special_duration
                }
            elif self.special_ability == "weaken":
                projectile.effect = {
                    "name": "weaken",
                    "chance": self.special_chance,
                    "duration": self.special_duration,
                    "amount": tower_types[self.tower_type].get("special_amount", 1.5)
                }
    
    def get_safe_surface_size(self, width, height, min_size=1):
        """Ensure surface dimensions are valid (positive and within reasonable limits)"""
        safe_width = max(min_size, int(width))
        safe_height = max(min_size, int(height))
        
        # Also set a reasonable maximum size to prevent performance issues
        max_size = 2000  # Arbitrary but reasonable maximum
        safe_width = min(safe_width, max_size)
        safe_height = min(safe_height, max_size)
        
        return safe_width, safe_height

    def get_visual_level_index(self):
        """Calculate the index for the tower sprite based on upgrades."""
        # Example: 0-1 upgrades = index 0, 2-3 upgrades = index 1, etc.
        # Ensure the index doesn't exceed the max number of loaded sprites - 1
        visual_level = min(self.total_upgrades // 2, MAX_TOWER_VISUAL_LEVELS - 1)
        return visual_level
        
    def update_visuals(self):
        """Update the tower's current sprite based on its level/upgrades."""
        print(f"[DEBUG] update_visuals called for {self.tower_type} (Upgrades: {self.total_upgrades})") # DEBUG
        if self.game and self.game.assets: # Ensure game manager and assets are available
            tower_sprite_list = self.game.assets["towers"].get(self.tower_type)
            if tower_sprite_list:
                visual_index = self.get_visual_level_index()
                print(f"[DEBUG]   Calculated visual_index: {visual_index}") # DEBUG
                if 0 <= visual_index < len(tower_sprite_list):
                    self.current_sprite = tower_sprite_list[visual_index]
                    print(f"[DEBUG]   Assigned sprite: {self.current_sprite}") # DEBUG
                else:
                    # Fallback to base sprite or last available if index is out of bounds
                    old_sprite = self.current_sprite
                    self.current_sprite = tower_sprite_list[0] if tower_sprite_list else None
                    print(f"Warning: Visual index {visual_index} out of bounds for {self.tower_type}. Using fallback sprite {self.current_sprite}. Old was {old_sprite}.")
            else:
                self.current_sprite = None # No sprites found for this tower type
                print(f"Warning: No sprites found for tower type {self.tower_type} in assets.")
        else:
            # Assets not ready yet, try again later or handle during initialization
            print(f"[DEBUG]   Assets not ready for {self.tower_type}") # DEBUG
            pass 

    def draw(self, surface, assets, show_range=False, selected=False, camera=None):
        """Draw the tower and its effects"""
        # Ensure visuals are updated if needed (e.g., if initialized before assets were loaded)
        if self.current_sprite is None and self.game and self.game.assets:
            self.update_visuals()

        # Apply camera transform if provided
        if camera:
            screen_pos = pygame.Vector2(*camera.apply(self.pos.x, self.pos.y))
            # Use sprite size for calculations if available, otherwise keep radius
            if self.current_sprite:
                sprite_width = self.current_sprite.get_width() * camera.zoom
                sprite_height = self.current_sprite.get_height() * camera.zoom
            else:
                sprite_width = self.radius * 2 * camera.zoom
                sprite_height = self.radius * 2 * camera.zoom
            screen_range = self.range * camera.zoom
        else:
            screen_pos = pygame.Vector2(self.pos)
            if self.current_sprite:
                sprite_width = self.current_sprite.get_width()
                sprite_height = self.current_sprite.get_height()
            else:
                sprite_width = self.radius * 2
                sprite_height = self.radius * 2
            screen_range = self.range
        
        # Draw range circle if selected or requested
        if show_range or selected:
            # Use average of sprite width/height for radius if sprite exists
            draw_radius = (sprite_width + sprite_height) / 4 if self.current_sprite else self.radius * (camera.zoom if camera else 1)
            pygame.draw.circle(surface, (200, 200, 200, 100), screen_pos, screen_range, max(1, int(1 * (camera.zoom if camera else 1))))
        
        # --- Draw Tower Sprite (Replaces Circle Drawing) --- 
        if self.current_sprite:
            # Scale the sprite if camera zoom is active
            if camera and camera.zoom != 1.0:
                try: # Add try-except for scaling issues
                    scaled_sprite = pygame.transform.smoothscale(self.current_sprite, (int(sprite_width), int(sprite_height)))
                except ValueError: # Handle potential zero dimensions
                    scaled_sprite = self.current_sprite 
                    print(f"[DEBUG] Scaling error for {self.tower_type}: width={sprite_width}, height={sprite_height}")
            else:
                scaled_sprite = self.current_sprite
                
            sprite_rect = scaled_sprite.get_rect(center=screen_pos)
            # DEBUG: Print sprite being drawn
            # print(f"[DEBUG] Drawing {self.tower_type} with sprite: {self.current_sprite} at {sprite_rect.topleft}") 
            surface.blit(scaled_sprite, sprite_rect)
            
            # Optional: Draw outline around the sprite if selected
            if selected:
                mask = pygame.mask.from_surface(scaled_sprite)
                outline_surf = mask.to_surface(setcolor=(255, 255, 255, 200), unsetcolor=(0,0,0,0))
                outline_offset = 2 # How far the outline extends
                for dx in [-outline_offset, 0, outline_offset]:
                    for dy in [-outline_offset, 0, outline_offset]:
                        if dx != 0 or dy != 0:
                            surface.blit(outline_surf, (sprite_rect.x + dx, sprite_rect.y + dy))
        else:
            # Fallback: Draw original circle if sprite is missing
            draw_radius = self.radius * (camera.zoom if camera else 1)
            pygame.draw.circle(surface, self.color, screen_pos, draw_radius)
            if selected:
                pygame.draw.circle(surface, (255, 255, 255), screen_pos, draw_radius + 2, 2)
            else:
                pygame.draw.circle(surface, (50, 50, 50), screen_pos, draw_radius, 1)
        # --- End Sprite Drawing ---
        
        # Draw targeting line if there's a target
        if self.targeting_enemy and self.targeting_enemy.health > 0:
            if not (self.targeting_enemy.is_cloaked and "reveal" not in self.targeting_enemy.status_effects):
                if camera:
                    target_screen_pos = pygame.Vector2(*camera.apply(self.targeting_enemy.pos.x, self.targeting_enemy.pos.y))
                    pygame.draw.line(surface, (200, 200, 200, 100), 
                                   (int(screen_pos.x), int(screen_pos.y)), 
                                   (int(target_screen_pos.x), int(target_screen_pos.y)), 
                                   max(1, int(1 * camera.zoom)))
                else:
                    target_pos = self.targeting_enemy.pos
                    pygame.draw.line(surface, (200, 200, 200, 100), 
                                   (int(self.pos.x), int(self.pos.y)), 
                                   (int(target_pos.x), int(target_pos.y)), 1)
        
        # Draw tower level indicator
        if self.level > 1:
            level_text = str(self.level)
            # Use asset font if available
            font = assets['fonts'].get('body_small', pygame.font.SysFont(None, 20))
            text_surf = font.render(level_text, True, (255, 255, 255))
            # Adjust position relative to sprite size or radius
            draw_radius = (sprite_width + sprite_height) / 4 if self.current_sprite else self.radius * (camera.zoom if camera else 1)
            text_rect = text_surf.get_rect(center=(int(screen_pos.x), int(screen_pos.y) - draw_radius - 10))
            surface.blit(text_surf, text_rect)
        
        # Draw tower effects
        draw_radius = (sprite_width + sprite_height) / 4 if self.current_sprite else self.radius * (camera.zoom if camera else 1)
        self.draw_effects(surface, screen_pos, draw_radius, camera)
        
        # Draw targeting priority if selected or hovered
        if selected or self.game.hover_tower == self:
            priority_font = pygame.font.SysFont('arial', 14)
            priority_text = priority_font.render(f"Target: {self.targeting_priority}", True, 
                                               (220, 220, 255) if selected else (180, 180, 220))
            # Adjust position relative to sprite size or radius
            draw_radius = (sprite_width + sprite_height) / 4 if self.current_sprite else self.radius * (camera.zoom if camera else 1)
            text_pos = (screen_pos.x - priority_text.get_width()//2, 
                       screen_pos.y + draw_radius + 5)
            # If selected, draw with a dark background for better visibility
            if selected:
                text_bg = pygame.Surface((priority_text.get_width() + 4, priority_text.get_height() + 4))
                text_bg.fill((0, 0, 0))
                text_bg.set_alpha(150)
                surface.blit(text_bg, (text_pos[0] - 2, text_pos[1] - 2))
            surface.blit(priority_text, text_pos)
        
        # Highlight if tower is buffed
        if self.tower_type != "Life" and self.buff_multiplier > 1.0:
            draw_radius = (sprite_width + sprite_height) / 4 if self.current_sprite else self.radius * (camera.zoom if camera else 1)
            buff_circle_radius = draw_radius + 5
            buff_surf = pygame.Surface((int(buff_circle_radius * 2), int(buff_circle_radius * 2)), pygame.SRCALPHA)
            pygame.draw.circle(buff_surf, (0, 255, 0, 100), (buff_circle_radius, buff_circle_radius), buff_circle_radius)
            surface.blit(buff_surf, (int(screen_pos.x - buff_circle_radius), int(screen_pos.y - buff_circle_radius)))
        
        # Draw selection highlight
        if selected:
            draw_radius = (sprite_width + sprite_height) / 4 if self.current_sprite else self.radius * (camera.zoom if camera else 1)
            select_pulse = math.sin(pygame.time.get_ticks() / 150) * 2
            select_radius = draw_radius + 10 + select_pulse
            select_surf = pygame.Surface((int(select_radius * 2), int(select_radius * 2)), pygame.SRCALPHA)
            pygame.draw.circle(select_surf, (255, 255, 255, 70), (select_radius, select_radius), select_radius, 2)
            surface.blit(select_surf, (int(screen_pos.x - select_radius), int(screen_pos.y - select_radius)))
    
    def draw_effects(self, surface, screen_pos, screen_radius, camera=None):
        """Tower-specific visual effects. Override in subclasses."""
        pass
        
    def set_game_manager(self, game_manager):
        """Set the game manager reference for this tower."""
        self.game = game_manager 