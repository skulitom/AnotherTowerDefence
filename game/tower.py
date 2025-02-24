import pygame
import random
import math
from pygame.math import Vector2
from game.settings import tower_types, upgrade_paths
from game.projectile import Projectile


class Tower:
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
        elif upgrade_type == "range":
            self.range *= multiplier
        elif upgrade_type == "speed":
            self.cooldown *= multiplier  # Lower cooldown means faster attack
        elif upgrade_type == "special":
            # Special upgrades depend on tower type
            if self.tower_type == "Fire":
                self.special_chance *= multiplier
                self.special_duration *= multiplier
            elif self.tower_type == "Water":
                self.special_chance *= multiplier
                self.special_duration *= multiplier
            elif self.tower_type == "Air":
                stats = tower_types[self.tower_type]
                self.special_chance *= multiplier
                self.special_targets = stats.get("special_targets", 3)
            elif self.tower_type == "Earth":
                self.special_chance *= multiplier
                self.special_duration *= multiplier
            elif self.tower_type == "Darkness":
                self.special_chance *= multiplier
                self.special_duration *= multiplier
            elif self.tower_type == "Light":
                tower_types[self.tower_type]["special_aoe"] *= multiplier
                self.special_duration *= multiplier
            elif self.tower_type == "Life":
                stats = tower_types[self.tower_type]
                self.buff_multiplier = stats.get("buff_damage", 1.2) * multiplier
        
        # Update upgrade level and total
        self.upgrades[upgrade_type] += 1
        self.total_upgrades += 1
        self.level = 1 + self.total_upgrades // 2  # Level increases every 2 upgrades
        
        return True
        
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
        self.time_since_last_shot += dt
        self.rotation += self.rotation_speed * dt
        
        # Update target lock timer
        if self.target_lock_timer > 0:
            self.target_lock_timer -= dt
            
        # Life towers only provide buffs.
        if self.tower_type == "Life":
            return  
            
        # Update targeting
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
                if "cloak" not in enemy.status_effects or self.tower_type == "Light":
                    distance = (enemy.pos - self.pos).length()
                    # Different targeting strategies based on tower type
                    if distance <= self.range:
                        # Fire targets enemies with highest health
                        if self.tower_type == "Fire" and (not closest_enemy or enemy.health > closest_enemy.health):
                            closest_enemy = enemy
                            closest_distance = distance
                        # Water targets closest enemies
                        elif self.tower_type == "Water" and distance < closest_distance:
                            closest_enemy = enemy
                            closest_distance = distance
                        # Air targets enemies furthest along the path
                        elif self.tower_type == "Air" and (not closest_enemy or enemy.current_point_index > closest_enemy.current_point_index):
                            closest_enemy = enemy
                            closest_distance = distance
                        # Earth targets enemies with lowest health
                        elif self.tower_type == "Earth" and (not closest_enemy or enemy.health < closest_enemy.health):
                            closest_enemy = enemy
                            closest_distance = distance
                        # Default targeting: closest enemy
                        elif self.tower_type not in ["Fire", "Water", "Air", "Earth"] and distance < closest_distance:
                            closest_enemy = enemy
                            closest_distance = distance
            
            target = closest_enemy
            self.targeting_enemy = closest_enemy
            
            # Set target lock timer (higher levels lock targets longer)
            if target:
                self.target_lock_timer = 1.0 + self.level * 0.5
        
        # Light towers can reveal cloaked enemies
        if self.tower_type == "Light":
            stats = tower_types[self.tower_type]
            reveal_range = stats.get("special_aoe", 100)
            for enemy in enemies:
                if (enemy.pos - self.pos).length() <= reveal_range and enemy.is_cloaked:
                    enemy.apply_effect("reveal", stats.get("special_duration", 5.0))
                    
                    # Add reveal particle effect
                    if particles:
                        angle = random.uniform(0, math.pi * 2)
                        distance = random.uniform(0, reveal_range)
                        x = self.pos.x + math.cos(angle) * distance
                        y = self.pos.y + math.sin(angle) * distance
                        particles.add_particle_params(Vector2(x, y), (255, 255, 150), (0, 0), 2, 0.5)
        
        # Fire projectile if we have a target and cooldown is ready
        if target and self.time_since_last_shot >= self.cooldown:
            # Create the projectile
            new_projectile = Projectile(self.pos, target, self.current_damage, self.bullet_speed, self.tower_type)
            
            # Add special abilities to projectile based on tower type
            if self.special_ability:
                if self.special_ability == "burn":
                    new_projectile.effect = {
                        "name": "burn",
                        "chance": self.special_chance,
                        "duration": self.special_duration,
                        "damage": tower_types[self.tower_type].get("special_damage", 5)
                    }
                elif self.special_ability == "slow":
                    new_projectile.effect = {
                        "name": "slow",
                        "chance": self.special_chance,
                        "duration": self.special_duration,
                        "amount": tower_types[self.tower_type].get("special_amount", 0.5)
                    }
                elif self.special_ability == "chain":
                    new_projectile.effect = {
                        "name": "chain",
                        "chance": self.special_chance,
                        "targets": tower_types[self.tower_type].get("special_targets", 3),
                        "damage_falloff": tower_types[self.tower_type].get("special_damage_falloff", 0.7)
                    }
                elif self.special_ability == "stun":
                    new_projectile.effect = {
                        "name": "stun",
                        "chance": self.special_chance,
                        "duration": self.special_duration
                    }
                elif self.special_ability == "weaken":
                    new_projectile.effect = {
                        "name": "weaken",
                        "chance": self.special_chance,
                        "duration": self.special_duration,
                        "amount": tower_types[self.tower_type].get("special_amount", 1.5)
                    }
            
            projectiles.append(new_projectile)
            self.time_since_last_shot = 0
            
            # Add muzzle flash effect
            if particles:
                for _ in range(5):
                    angle = random.uniform(0, math.pi * 2)
                    speed = random.uniform(20, 50)
                    velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
                    particles.add_particle_params(Vector2(self.pos), self.particle_color, velocity, random.uniform(2, 5), random.uniform(0.2, 0.5))
    
    def draw(self, surface, assets, show_range=False, selected=False, camera=None):
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
        
        # Draw special effects based on tower type
        if self.tower_type == "Fire":
            # Add fire glow
            glow_radius = screen_radius + 2 + math.sin(pygame.time.get_ticks() / 200 + self.pulse_offset) * 2
            glow_surf = pygame.Surface((int(glow_radius * 2), int(glow_radius * 2)), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 100, 0, 50), (glow_radius, glow_radius), glow_radius)
            surface.blit(glow_surf, (int(screen_pos.x - glow_radius), int(screen_pos.y - glow_radius)))
        
        elif self.tower_type == "Water":
            # Add water ripple effect
            ripple_time = pygame.time.get_ticks() / 1000 + self.pulse_offset
            ripple_count = 3
            for i in range(ripple_count):
                phase = (ripple_time + i / ripple_count) % 1
                ripple_radius = screen_radius * (1 + phase)
                alpha = int(100 * (1 - phase))
                ripple_surf = pygame.Surface((int(ripple_radius * 2), int(ripple_radius * 2)), pygame.SRCALPHA)
                pygame.draw.circle(ripple_surf, (100, 100, 255, alpha), (ripple_radius, ripple_radius), ripple_radius, 1)
                surface.blit(ripple_surf, (int(screen_pos.x - ripple_radius), int(screen_pos.y - ripple_radius)))
        
        elif self.tower_type == "Air":
            # Add swirling wind effect
            for i in range(3):
                angle = ((pygame.time.get_ticks() / 500) + i * 2.0944) % 6.28
                size = screen_radius + 8
                x = screen_pos.x + math.cos(angle) * size
                y = screen_pos.y + math.sin(angle) * size
                cloud_radius = 3 + math.sin(pygame.time.get_ticks() / 200 + i) * 1
                cloud_surf = pygame.Surface((int(cloud_radius * 2), int(cloud_radius * 2)), pygame.SRCALPHA)
                pygame.draw.circle(cloud_surf, (200, 230, 255, 150), (cloud_radius, cloud_radius), cloud_radius)
                surface.blit(cloud_surf, (int(x - cloud_radius), int(y - cloud_radius)))
        
        elif self.tower_type == "Earth":
            # Add floating rock particles
            rock_count = 4
            for i in range(rock_count):
                angle = ((pygame.time.get_ticks() / 800) + i * 6.28 / rock_count) % 6.28
                orbit_size = screen_radius + 6
                x = screen_pos.x + math.cos(angle) * orbit_size
                y = screen_pos.y + math.sin(angle) * orbit_size
                rock_size = 2 + i % 2
                pygame.draw.circle(surface, (100, 70, 20), (int(x), int(y)), rock_size)
        
        elif self.tower_type == "Darkness":
            # Add dark mist effect
            for i in range(5):
                angle = random.uniform(0, 6.28)
                distance = random.uniform(0, screen_radius + 5)
                x = screen_pos.x + math.cos(angle) * distance
                y = screen_pos.y + math.sin(angle) * distance
                size = random.uniform(1, 3)
                alpha = random.randint(30, 70)
                mist_surf = pygame.Surface((int(size * 2), int(size * 2)), pygame.SRCALPHA)
                pygame.draw.circle(mist_surf, (128, 0, 128, alpha), (size, size), size)
                surface.blit(mist_surf, (int(x - size), int(y - size)))
        
        elif self.tower_type == "Light":
            # Add light rays
            ray_count = 8
            for i in range(ray_count):
                angle = ((pygame.time.get_ticks() / 1000) + i * 6.28 / ray_count) % 6.28
                length = screen_radius + 6 + math.sin(pygame.time.get_ticks() / 200 + i) * 2
                start_x = screen_pos.x + math.cos(angle) * screen_radius
                start_y = screen_pos.y + math.sin(angle) * length
                end_x = screen_pos.x + math.cos(angle) * length
                end_y = screen_pos.y + math.sin(angle) * length
                ray_surf = pygame.Surface((int(length * 2), int(length * 2)), pygame.SRCALPHA)
                pygame.draw.line(ray_surf, (255, 255, 150, 100), (length, length), 
                                (length + math.cos(angle) * length, length + math.sin(angle) * length), 2)
                surface.blit(ray_surf, (int(screen_pos.x - length), int(screen_pos.y - length)))
        
        elif self.tower_type == "Life":
            # Add healing pulse effect
            pulse = 3 * math.sin(pygame.time.get_ticks() / 200 + self.pulse_offset)
            pulse_radius = screen_radius + 5 + pulse
            pulse_surf = pygame.Surface((int(pulse_radius * 2), int(pulse_radius * 2)), pygame.SRCALPHA)
            pygame.draw.circle(pulse_surf, (255, 150, 200, 50), (pulse_radius, pulse_radius), pulse_radius)
            pygame.draw.circle(pulse_surf, (255, 150, 200, 100), (pulse_radius, pulse_radius), pulse_radius, 2)
            surface.blit(pulse_surf, (int(screen_pos.x - pulse_radius), int(screen_pos.y - pulse_radius)))
            
            # Show buff range
            buff_range = tower_types[self.tower_type].get("buff_range", 200)
            buff_surf = pygame.Surface((buff_range * 2, buff_range * 2), pygame.SRCALPHA)
            pygame.draw.circle(buff_surf, (255, 150, 200, 20), (buff_range, buff_range), buff_range)
            pygame.draw.circle(buff_surf, (255, 150, 200, 40), (buff_range, buff_range), buff_range, 1)
            surface.blit(buff_surf, (int(screen_pos.x - buff_range), int(screen_pos.y - buff_range)))
        
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