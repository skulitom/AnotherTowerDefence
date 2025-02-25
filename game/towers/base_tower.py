import pygame
import random
import math
from pygame.math import Vector2
from game.settings import tower_types, upgrade_paths
from game.projectile import Projectile


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
        # Keep current target if valid
        target = self.targeting_enemy
        
        # Check if current target is still valid
        if target and (target.health <= 0 or (target.pos - self.pos).length() > self.range):
            target = None
            self.targeting_enemy = None
        
        # Find new target if needed
        if not target or self.target_lock_timer <= 0:
            closest_distance = float('inf')
            closest_enemy = None
            
            for enemy in enemies:
                # Skip cloaked enemies unless tower can see them
                if "cloak" in enemy.status_effects and self.tower_type != "Light":
                    continue
                
                distance = (enemy.pos - self.pos).length()
                if distance <= self.range:
                    # Tower-specific targeting strategies implemented in subclasses
                    if self.is_preferred_target(enemy, distance, closest_enemy, closest_distance):
                        closest_enemy = enemy
                        closest_distance = distance
            
            target = closest_enemy
            self.targeting_enemy = closest_enemy
            
            # Set target lock timer (higher levels lock targets longer)
            if target:
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
    
    def draw(self, surface, assets, show_range=False, selected=False, camera=None):
        """Draw the tower and its effects"""
        # Apply camera transform if provided
        if camera:
            screen_pos = pygame.Vector2(*camera.apply(self.pos.x, self.pos.y))
            screen_radius = self.radius * camera.zoom
            screen_range = self.range * camera.zoom
        else:
            screen_pos = self.pos.copy()
            screen_radius = self.radius
            screen_range = self.range
            
        # Draw range circle if showing range or tower is selected
        if show_range or selected:
            range_surf = pygame.Surface((screen_range * 2, screen_range * 2), pygame.SRCALPHA)
            if selected:
                pygame.draw.circle(range_surf, (255, 255, 255, 60), (screen_range, screen_range), screen_range)
                pygame.draw.circle(range_surf, (255, 255, 255, 100), (screen_range, screen_range), screen_range, 2)
            else:
                pygame.draw.circle(range_surf, (255, 255, 255, 30), (screen_range, screen_range), screen_range)
            surface.blit(range_surf, (int(screen_pos.x - screen_range), int(screen_pos.y - screen_range)))
        
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
        
        # Draw tower base (circular platform)
        base_radius = screen_radius + 5 * (camera.zoom if camera else 1)
        base_height = 6 * (camera.zoom if camera else 1)
        base_rect = pygame.Rect(
            int(screen_pos.x - base_radius), 
            int(screen_pos.y - base_height), 
            base_radius * 2, 
            base_height * 2
        )
        pygame.draw.ellipse(surface, (80, 80, 80), base_rect)
        pygame.draw.ellipse(surface, (120, 120, 120), base_rect, max(1, int(2 * camera.zoom)) if camera else 2)
        
        # Draw tower
        tower_img = assets["towers"].get(self.tower_type)
        
        if tower_img:
            # Scale and rotate tower image
            size = int(screen_radius * 2 * (1 + 0.1 * self.level))  # Bigger with higher levels
            img = pygame.transform.scale(tower_img, (size, size))
            
            if self.tower_type != "Life":  # Don't rotate life towers
                img = pygame.transform.rotate(img, self.rotation)
            
            img_rect = img.get_rect(center=(int(screen_pos.x), int(screen_pos.y)))
            surface.blit(img, img_rect.topleft)
        else:
            # Fallback to circle if no image
            pygame.draw.circle(surface, self.color, (int(screen_pos.x), int(screen_pos.y)), screen_radius)
        
        # Draw tower level indicator
        if self.level > 1:
            level_text = str(self.level)
            font = pygame.font.SysFont(None, 20)
            text_surf = font.render(level_text, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(int(screen_pos.x), int(screen_pos.y) - screen_radius - 10))
            surface.blit(text_surf, text_rect)
        
        # Draw tower-specific effects
        self.draw_effects(surface, screen_pos, screen_radius, camera)
        
        # Highlight if tower is buffed
        if self.tower_type != "Life" and self.buff_multiplier > 1.0:
            buff_circle_radius = screen_radius + 5
            buff_surf = pygame.Surface((int(buff_circle_radius * 2), int(buff_circle_radius * 2)), pygame.SRCALPHA)
            pygame.draw.circle(buff_surf, (0, 255, 0, 100), (buff_circle_radius, buff_circle_radius), buff_circle_radius)
            surface.blit(buff_surf, (int(screen_pos.x - buff_circle_radius), int(screen_pos.y - buff_circle_radius)))
        
        # Draw selection highlight
        if selected:
            select_pulse = math.sin(pygame.time.get_ticks() / 150) * 2
            select_radius = screen_radius + 10 + select_pulse
            select_surf = pygame.Surface((int(select_radius * 2), int(select_radius * 2)), pygame.SRCALPHA)
            pygame.draw.circle(select_surf, (255, 255, 255, 70), (select_radius, select_radius), select_radius, 2)
            surface.blit(select_surf, (int(screen_pos.x - select_radius), int(screen_pos.y - select_radius)))
    
    def draw_effects(self, surface, screen_pos, screen_radius, camera=None):
        """Tower-specific visual effects. Override in subclasses."""
        pass 