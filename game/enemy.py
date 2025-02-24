import pygame
from pygame.math import Vector2
import random
from game.settings import enemy_types
import math


class Enemy:
    def __init__(self, path_points, enemy_type="Normal", wave_level=1):
        # Convert path points into Vector2 objects for easier math
        self.path_points = [Vector2(p) for p in path_points]
        self.pos = self.path_points[0].copy()
        self.current_point_index = 0
        
        # Set base stats and apply type multipliers
        self.enemy_type = enemy_type
        self.type_stats = enemy_types[enemy_type]
        self.base_speed = 60 + (wave_level - 1) * 5
        self.speed = self.base_speed * self.type_stats["speed_multiplier"]
        self.base_health = 100 * wave_level
        self.max_health = self.base_health * self.type_stats["health_multiplier"]
        self.health = self.max_health
        self.reward = int(20 * wave_level * self.type_stats["reward_multiplier"])
        self.color = self.type_stats["color"]
        self.radius = 10 if enemy_type != "Boss" else 20
        self.reached_end = False
        
        # Status effects
        self.status_effects = {}  # {effect_name: {"duration": time_left, "value": effect_value}}
        
        # Special abilities
        self.special_ability = self.type_stats.get("special_ability")
        self.ability_cooldown = 0
        self.is_cloaked = False
        self.alpha = 255
        self.pulse_offset = random.random() * 6.28  # Random starting phase
        
        # Visual effects
        self.trail_positions = []
        self.hit_flash = 0
        self.has_shield = enemy_type == "Boss"
        self.shield_health = self.max_health * 0.3 if self.has_shield else 0
        self.max_shield_health = self.shield_health

    def update(self, dt, enemies=None):
        # Update status effect durations
        effects_to_remove = []
        for effect, data in self.status_effects.items():
            data["duration"] -= dt
            if data["duration"] <= 0:
                effects_to_remove.append(effect)
        
        for effect in effects_to_remove:
            if effect == "slow":
                self.speed = self.base_speed * self.type_stats["speed_multiplier"]
            del self.status_effects[effect]
        
        # Update special abilities
        if self.special_ability == "heal" and enemies and self.ability_cooldown <= 0:
            for enemy in enemies:
                if enemy != self and (enemy.pos - self.pos).length() <= self.type_stats.get("heal_radius", 80):
                    enemy.health = min(enemy.max_health, enemy.health + self.type_stats.get("heal_amount", 5))
            self.ability_cooldown = 3.0
        elif self.special_ability == "cloak" and not self.is_cloaked and self.ability_cooldown <= 0:
            self.is_cloaked = True
            self.alpha = 70
            self.status_effects["cloak"] = {
                "duration": self.type_stats.get("cloak_duration", 3.0),
                "value": None
            }
            self.ability_cooldown = self.type_stats.get("cloak_cooldown", 5.0)
        
        # Update cooldowns
        if self.ability_cooldown > 0:
            self.ability_cooldown -= dt
        
        # Check if cloaking has expired
        if "cloak" not in self.status_effects and self.is_cloaked:
            self.is_cloaked = False
            self.alpha = 255
        
        # Update hit flash
        if self.hit_flash > 0:
            self.hit_flash -= dt * 2
        
        # Movement logic - apply slow effect if present
        current_speed = self.speed
        if "slow" in self.status_effects:
            current_speed *= self.status_effects["slow"]["value"]
        
        # Store position for trail effect
        self.trail_positions.append(Vector2(self.pos))
        if len(self.trail_positions) > 5:
            self.trail_positions.pop(0)
        
        # Move along path
        if self.current_point_index < len(self.path_points) - 1:
            target = self.path_points[self.current_point_index + 1]
            direction = target - self.pos
            distance = direction.length()
            if distance != 0:
                direction = direction.normalize()
            travel = current_speed * dt
            if travel >= distance:
                self.pos = target.copy()
                self.current_point_index += 1
            else:
                self.pos += direction * travel
        else:
            self.reached_end = True
    
    def take_damage(self, amount, tower_type=None):
        # Apply resistance for boss type
        if self.enemy_type == "Boss" and self.special_ability == "resist":
            amount *= (1 - self.type_stats.get("resist_amount", 0))
        
        # Apply weakness effect if present
        if "weaken" in self.status_effects:
            amount *= self.status_effects["weaken"]["value"]
        
        # Apply damage to shield first if present
        if self.has_shield and self.shield_health > 0:
            if self.shield_health >= amount:
                self.shield_health -= amount
                amount = 0
            else:
                amount -= self.shield_health
                self.shield_health = 0
        
        # Apply remaining damage to health
        self.health -= amount
        self.hit_flash = 1.0
        
        # Return true if enemy died
        return self.health <= 0
    
    def apply_effect(self, effect, duration, value=None):
        """Apply a status effect to the enemy"""
        # Don't apply effects to boss if it has shield
        if self.enemy_type == "Boss" and self.has_shield and self.shield_health > 0:
            return False
            
        self.status_effects[effect] = {"duration": duration, "value": value}
        
        # Apply effect immediately
        if effect == "slow":
            self.speed = self.base_speed * self.type_stats["speed_multiplier"] * value
        
        return True
    
    def draw(self, surface, show_hp=True, camera=None):
        # Apply camera transform if provided
        if camera:
            screen_pos = Vector2(*camera.apply(self.pos.x, self.pos.y))
            screen_radius = self.radius * camera.zoom
        else:
            screen_pos = self.pos.copy()
            screen_radius = self.radius
            
        # Draw trail
        if len(self.trail_positions) > 1 and not self.is_cloaked:
            for i in range(len(self.trail_positions) - 1):
                alpha = int(150 * (i / len(self.trail_positions)))
                if self.enemy_type == "Fast":
                    if camera:
                        pos1 = Vector2(*camera.apply(self.trail_positions[i].x, self.trail_positions[i].y))
                        pos2 = Vector2(*camera.apply(self.trail_positions[i+1].x, self.trail_positions[i+1].y))
                        pygame.draw.line(surface, (*self.color, alpha), pos1, pos2, 
                                       max(1, int(2 * camera.zoom)))
                    else:
                        pygame.draw.line(surface, (*self.color, alpha), self.trail_positions[i], self.trail_positions[i+1], 2)
        
        # Draw enemy
        if self.is_cloaked and "reveal" not in self.status_effects:
            # Skip drawing if cloaked and not revealed
            pass
        else:
            alpha = self.alpha
            if "reveal" in self.status_effects:
                alpha = min(255, alpha + 100)
            
            # Create a surface with the enemy
            surface_size = int(screen_radius * 2 + 4)
            enemy_surface = pygame.Surface((surface_size, surface_size), pygame.SRCALPHA)
            
            # Draw the enemy with type-specific visuals
            center_point = (surface_size // 2, surface_size // 2)
            
            if self.enemy_type == "Normal":
                pygame.draw.circle(enemy_surface, (*self.color, alpha), center_point, screen_radius)
            elif self.enemy_type == "Fast":
                points = [
                    (center_point[0], 0),
                    (surface_size, center_point[1]),
                    (center_point[0], surface_size),
                    (0, center_point[1])
                ]
                pygame.draw.polygon(enemy_surface, (*self.color, alpha), points)
            elif self.enemy_type == "Tank":
                pygame.draw.circle(enemy_surface, (*self.color, alpha), center_point, screen_radius)
                inner_radius = max(2, screen_radius - 4 * camera.zoom if camera else screen_radius - 4)
                pygame.draw.circle(enemy_surface, (50, 50, 50, alpha), center_point, inner_radius)
            elif self.enemy_type == "Healing":
                pygame.draw.circle(enemy_surface, (*self.color, alpha), center_point, screen_radius)
                # Draw a plus sign
                rect_thickness = max(1, int(2 * camera.zoom)) if camera else 2
                pygame.draw.rect(enemy_surface, (255, 255, 255, alpha), 
                              (center_point[0] - rect_thickness//2, 4, 
                               rect_thickness, surface_size - 8))
                pygame.draw.rect(enemy_surface, (255, 255, 255, alpha), 
                              (4, center_point[1] - rect_thickness//2, 
                               surface_size - 8, rect_thickness))
            elif self.enemy_type == "Invisible":
                pygame.draw.circle(enemy_surface, (*self.color, alpha), center_point, screen_radius)
                # Draw an eye
                pygame.draw.circle(enemy_surface, (255, 255, 255, alpha), 
                                center_point, screen_radius // 2)
                pygame.draw.circle(enemy_surface, (0, 0, 0, alpha), 
                                center_point, screen_radius // 4)
            elif self.enemy_type == "Boss":
                pygame.draw.circle(enemy_surface, (*self.color, alpha), center_point, screen_radius)
                # Draw a crown
                crown_scale = camera.zoom if camera else 1
                crown_points = [
                    (center_point[0] - 8 * crown_scale, center_point[1] - 5 * crown_scale),
                    (center_point[0] - 4 * crown_scale, center_point[1] - 10 * crown_scale),
                    (center_point[0], center_point[1] - 5 * crown_scale),
                    (center_point[0] + 4 * crown_scale, center_point[1] - 10 * crown_scale),
                    (center_point[0] + 8 * crown_scale, center_point[1] - 5 * crown_scale),
                    (center_point[0] + 10 * crown_scale, center_point[1]),
                    (center_point[0] - 10 * crown_scale, center_point[1])
                ]
                pygame.draw.polygon(enemy_surface, (255, 215, 0, alpha), crown_points)
            
            # Apply hit flash effect
            if self.hit_flash > 0:
                flash_surface = pygame.Surface((surface_size, surface_size), pygame.SRCALPHA)
                flash_alpha = int(150 * self.hit_flash)
                pygame.draw.circle(flash_surface, (255, 255, 255, flash_alpha), center_point, screen_radius + 2)
                enemy_surface.blit(flash_surface, (0, 0))
            
            # Draw status effect indicators
            status_radius = screen_radius + 4
            if "burn" in self.status_effects:
                pygame.draw.circle(enemy_surface, (255, 100, 0, 150), center_point, status_radius, 
                                max(1, int(2 * camera.zoom)) if camera else 2)
            elif "slow" in self.status_effects:
                pygame.draw.circle(enemy_surface, (0, 100, 255, 150), center_point, status_radius, 
                                max(1, int(2 * camera.zoom)) if camera else 2)
            elif "stun" in self.status_effects:
                pygame.draw.circle(enemy_surface, (255, 255, 0, 150), center_point, status_radius, 
                                max(1, int(2 * camera.zoom)) if camera else 2)
                # Draw stars around stunned enemy
                star_size = max(1, int(2 * camera.zoom)) if camera else 2
                for i in range(3):
                    angle = i * 2.0944 + pygame.time.get_ticks() / 200
                    x = center_point[0] + math.cos(angle) * status_radius
                    y = center_point[1] + math.sin(angle) * status_radius
                    pygame.draw.circle(enemy_surface, (255, 255, 0, 200), (x, y), star_size)
            elif "weaken" in self.status_effects:
                pygame.draw.circle(enemy_surface, (128, 0, 128, 150), center_point, status_radius, 
                                max(1, int(2 * camera.zoom)) if camera else 2)
            
            # Draw shield if present
            if self.has_shield and self.shield_health > 0:
                shield_ratio = self.shield_health / self.max_shield_health
                shield_pulse = (math.sin(pygame.time.get_ticks() / 200 + self.pulse_offset) + 1) * 2
                shield_radius = (screen_radius + 6 + shield_pulse)
                
                if camera:
                    shield_pos = screen_pos
                else:
                    shield_pos = self.pos
                    
                shield_surface = pygame.Surface((int(shield_radius * 2), int(shield_radius * 2)), pygame.SRCALPHA)
                shield_alpha = int(100 * shield_ratio)
                pygame.draw.circle(shield_surface, (100, 200, 255, shield_alpha), 
                                (shield_radius, shield_radius), shield_radius)
                pygame.draw.circle(shield_surface, (150, 220, 255, shield_alpha + 50), 
                                (shield_radius, shield_radius), shield_radius, 
                                max(1, int(2 * camera.zoom)) if camera else 2)
                surface.blit(shield_surface, (int(shield_pos.x - shield_radius), int(shield_pos.y - shield_radius)))
            
            # Blit the enemy to the screen
            surface.blit(enemy_surface, (int(screen_pos.x - surface_size//2), int(screen_pos.y - surface_size//2)))
            
            # Draw hp bar if needed
            if show_hp and self.enemy_type != "Normal":
                hp_width = screen_radius * 2
                hp_height = max(2, int(4 * camera.zoom)) if camera else 4
                from game.utils import draw_hp_bar
                draw_hp_bar(
                    surface, 
                    screen_pos.x - hp_width/2, 
                    screen_pos.y - screen_radius - hp_height - 5,
                    hp_width, hp_height, 
                    self.health, self.max_health, 
                    camera=None  # We've already applied the camera transform
                )
        
        # Draw healing effect
        if self.special_ability == "heal" and self.ability_cooldown <= 0:
            pulse = (math.sin(pygame.time.get_ticks() / 150) + 1) * 0.5
            heal_radius = self.type_stats.get("heal_radius", 80) * (0.8 + pulse * 0.2)
            heal_surface = pygame.Surface((int(heal_radius * 2), int(heal_radius * 2)), pygame.SRCALPHA)
            pygame.draw.circle(heal_surface, (0, 255, 100, 30), (heal_radius, heal_radius), heal_radius)
            pygame.draw.circle(heal_surface, (0, 255, 100, 70), (heal_radius, heal_radius), heal_radius, 2)
            surface.blit(heal_surface, (int(self.pos.x - heal_radius), int(self.pos.y - heal_radius))) 