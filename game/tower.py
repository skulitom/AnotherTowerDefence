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
        
        # Give tower a unique ID for synergy tracking
        self.id = 0  # Will be set by GameManager
        
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
        
        # Evolution attributes
        self.evolved = False
        self.evolution_name = None
        self.evolution_special = None
        self.evolution_data = None
        
        # Synergy attributes
        self.synergy_damage_multiplier = 1.0
        
        # Weather effects tracking
        self.weather_affected = None
        self.orig_damage = self.damage
        self.orig_cooldown = self.cooldown
        self.orig_range = self.range
        
        # Special evolution abilities state
        self.special_timers = {}
        
        # Acceleration for Cyclone evolution
        self.current_acceleration = 1.0
        
        # Targeting
        self.targeting_priority = "First" # Default targeting priority
        
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

    def update(self, dt, enemies, projectiles, particles=None, game_manager=None):
        """Update tower state"""
        # Update timers
        self.time_since_last_shot += dt
        
        # Update visual effects
        self.rotation += self.rotation_speed * dt
        
        # Update target lock timer
        if self.targeting_enemy:
            self.target_lock_timer -= dt
            if self.target_lock_timer <= 0:
                self.targeting_enemy = None
        
        # Find target if none exists
        if not self.targeting_enemy:
            self.find_new_target(enemies)
        
        # Check if target is still valid
        elif self.targeting_enemy not in enemies or self.targeting_enemy.health <= 0 or \
             self.pos.distance_to(self.targeting_enemy.pos) > self.range:
            self.targeting_enemy = None
            self.find_new_target(enemies)
        
        # Update acceleration for Cyclone evolution
        if self.evolved and self.evolution_special == "accelerate":
            max_accel = self.evolution_data["max_acceleration"]
            accel_rate = self.evolution_data["acceleration_rate"]
            
            # Apply acceleration if we're shooting
            if self.targeting_enemy:
                self.current_acceleration = max(
                    max_accel,
                    self.current_acceleration - accel_rate * dt
                )
            else:
                # Reset when not shooting
                self.current_acceleration = 1.0
        
        # Apply evolution special effects
        self.update_special_evolution_effects(dt, enemies, particles)
        
        # Check if can shoot
        effective_cooldown = self.cooldown
        if hasattr(self, "current_acceleration") and self.current_acceleration < 1.0:
            effective_cooldown *= self.current_acceleration
            
        if self.targeting_enemy and self.time_since_last_shot >= effective_cooldown:
            self.shoot(projectiles, particles, game_manager)
    
    def update_special_evolution_effects(self, dt, enemies, particles):
        """Update any special effects from evolution"""
        if not self.evolved:
            return
        
        # Periodic effects
        if self.evolution_special == "eruption":
            # Initialize timer if it doesn't exist
            if "eruption" not in self.special_timers:
                self.special_timers["eruption"] = self.evolution_data["eruption_interval"]
            
            # Update timer
            self.special_timers["eruption"] -= dt
            
            # Trigger eruption
            if self.special_timers["eruption"] <= 0:
                self.special_timers["eruption"] = self.evolution_data["eruption_interval"]
                
                # Visual effect
                if particles:
                    particles.create_explosion(
                        self.pos.x, self.pos.y,
                        count=20,
                        color=self.color,
                        min_speed=30, max_speed=100,
                        lifetime=1.0
                    )
                
                # Damage enemies in radius
                radius = self.evolution_data["eruption_radius"]
                damage = self.evolution_data["eruption_damage"]
                for enemy in enemies:
                    if enemy.pos.distance_to(self.pos) <= radius:
                        enemy.take_damage(damage, "fire")
        
        elif self.evolution_special == "pulse":
            # Initialize timer if it doesn't exist
            if "pulse" not in self.special_timers:
                self.special_timers["pulse"] = self.evolution_data["pulse_interval"]
            
            # Update timer
            self.special_timers["pulse"] -= dt
            
            # Trigger pulse
            if self.special_timers["pulse"] <= 0:
                self.special_timers["pulse"] = self.evolution_data["pulse_interval"]
                
                # Visual effect
                if particles:
                    particles.create_ring(
                        self.pos.x, self.pos.y,
                        radius=self.range,
                        color=self.color,
                        lifetime=0.5
                    )
                
                # Damage all enemies in range
                for enemy in enemies:
                    if enemy.pos.distance_to(self.pos) <= self.range:
                        enemy.take_damage(self.evolution_data["pulse_damage"], "light")
    
    def shoot(self, projectiles, particles=None, game_manager=None):
        """Fire at the current target"""
        # Reset shot timer
        self.time_since_last_shot = 0
        
        # Calculate damage with all multipliers
        total_damage = self.damage * self.buff_multiplier * self.synergy_damage_multiplier
        
        # Special damage calculation for evolution abilities
        if self.evolved:
            if self.evolution_special == "sunfire" and self.targeting_enemy:
                # More damage to higher health enemies
                health_ratio = self.targeting_enemy.health / self.targeting_enemy.max_health
                scale = self.evolution_data["damage_scale_factor"]
                total_damage *= 1.0 + (health_ratio * (scale - 1.0))
            
            elif self.evolution_special == "execute" and self.targeting_enemy:
                # Check for execute threshold
                health_ratio = self.targeting_enemy.health / self.targeting_enemy.max_health
                if health_ratio <= self.evolution_data["execute_threshold"]:
                    # Instant kill
                    total_damage = self.targeting_enemy.health * 2
        
        # Create projectile
        if projectiles is not None:
            new_projectile = Projectile(
                self.pos.copy(), 
                self.targeting_enemy, 
                total_damage, 
                self.bullet_speed,
                self.tower_type,
                self.color
            )
            projectiles.append(new_projectile)
            
            # Apply special evolution effects to projectile
            if self.evolved:
                new_projectile.tower_source = self
                
                if self.evolution_special == "impact":
                    new_projectile.has_aoe = True
                    new_projectile.aoe_radius = self.evolution_data["impact_aoe"]
                    new_projectile.aoe_damage = self.evolution_data["impact_damage"]
                
                elif self.evolution_special == "knockback":
                    new_projectile.has_knockback = True
                    new_projectile.knockback_distance = self.evolution_data["knockback_distance"]
                
                elif self.evolution_special == "shatter":
                    new_projectile.will_shatter = True
                    new_projectile.shard_count = self.evolution_data["shard_count"]
                    new_projectile.shard_damage = self.evolution_data["shard_damage"]
                    new_projectile.shard_range = self.evolution_data["shard_range"]
        
        # Multi-shot for Phoenix evolution
        if self.evolved and self.evolution_special == "multishot" and game_manager:
            # Find additional targets
            additional_targets = []
            for enemy in game_manager.enemies:
                if enemy != self.targeting_enemy and enemy.pos.distance_to(self.pos) <= self.range:
                    additional_targets.append(enemy)
                    if len(additional_targets) >= self.evolution_data["multishot_count"] - 1:
                        break
            
            # Fire at additional targets
            for add_target in additional_targets:
                extra_projectile = Projectile(
                    self.pos.copy(), 
                    add_target, 
                    total_damage, 
                    self.bullet_speed,
                    self.tower_type,
                    self.color
                )
                projectiles.append(extra_projectile)
        
        # Visual effects
        if particles:
            particles.add_particle(
                self.pos.x, self.pos.y,
                0, 0,
                self.particle_color,
                0.2,
                size=5
            )

    def find_new_target(self, enemies):
        """Find a new enemy to target based on the current priority."""
        in_range_enemies = [
            enemy for enemy in enemies 
            if enemy.health > 0 and self.pos.distance_to(enemy.pos) <= self.range
        ]

        if not in_range_enemies:
            self.targeting_enemy = None
            return

        if self.targeting_priority == "First":
            # Assuming enemy has 'distance_traveled' attribute, higher is further
            # Target the enemy that has traveled the furthest along the path
            target = max(in_range_enemies, key=lambda e: e.get_path_progress())
        elif self.targeting_priority == "Last":
            # Target the enemy that has traveled the least
            target = min(in_range_enemies, key=lambda e: e.get_path_progress())
        elif self.targeting_priority == "Strongest":
            # Target the enemy with the most current health
            target = max(in_range_enemies, key=lambda e: e.health)
        elif self.targeting_priority == "Weakest":
            # Target the enemy with the least current health
            target = min(in_range_enemies, key=lambda e: e.health)
        else: # Default to "First" if priority is invalid
            target = max(in_range_enemies, key=lambda e: e.get_path_progress())
            
        self.targeting_enemy = target
        # Reset target lock timer when finding a new target
        self.target_lock_timer = 0.5 # Give a short lock duration

    def draw(self, surface, assets, show_range=False, selected=False, camera=None):
        """Draw the tower"""
        # Apply camera transform if provided
        pos = self.pos
        range_val = self.range
        if camera:
            pos = Vector2(camera.world_to_screen(self.pos))
            range_val = self.range * camera.scale
        
        # Draw tower range if needed
        if show_range or selected:
            pygame.draw.circle(surface, (200, 200, 200, 100), (int(pos.x), int(pos.y)), int(range_val), 1)
        
        # Calculate pulse effect (makes tower "breathe")
        pulse = math.sin(pygame.time.get_ticks() * 0.005 + self.pulse_offset) * 0.2 + 1.0
        size = int(self.radius * pulse)
        
        # Draw tower body
        pygame.draw.circle(surface, self.color, (int(pos.x), int(pos.y)), size)
        
        # Draw tower outline
        if selected:
            pygame.draw.circle(surface, (255, 255, 255), (int(pos.x), int(pos.y)), size + 2, 2)
        else:
            pygame.draw.circle(surface, (50, 50, 50), (int(pos.x), int(pos.y)), size, 1)
        
        # Draw tower type indicator
        if self.tower_type == "Fire":
            # Fire icon
            pygame.draw.polygon(surface, (255, 100, 0), [
                (pos.x, pos.y - size//2),
                (pos.x - size//3, pos.y + size//3),
                (pos.x + size//3, pos.y + size//3)
            ])
        elif self.tower_type == "Water":
            # Water icon
            pygame.draw.circle(surface, (0, 100, 255), (int(pos.x), int(pos.y)), size//2)
        elif self.tower_type == "Air":
            # Air icon
            for i in range(3):
                pygame.draw.line(surface, (200, 200, 255), 
                    (pos.x - size//2, pos.y - size//2 + i*size//3),
                    (pos.x + size//2, pos.y - size//2 + i*size//3), 
                    2)
        elif self.tower_type == "Earth":
            # Earth icon
            pygame.draw.rect(surface, (139, 69, 19), (pos.x - size//3, pos.y - size//3, 2*size//3, 2*size//3))
        elif self.tower_type == "Darkness":
            # Darkness icon
            pygame.draw.circle(surface, (0, 0, 0), (int(pos.x), int(pos.y)), size//2)
        elif self.tower_type == "Light":
            # Light icon
            pygame.draw.circle(surface, (255, 255, 200), (int(pos.x), int(pos.y)), size//2)
            for i in range(4):
                angle = i * math.pi / 2
                pygame.draw.line(surface, (255, 255, 200),
                    (pos.x + math.cos(angle) * size//2, pos.y + math.sin(angle) * size//2),
                    (pos.x + math.cos(angle) * size, pos.y + math.sin(angle) * size),
                    2)
        elif self.tower_type == "Life":
            # Life icon
            pygame.draw.line(surface, (0, 200, 0), (pos.x, pos.y - size//2), (pos.x, pos.y + size//2), 2)
            pygame.draw.line(surface, (0, 200, 0), (pos.x - size//2, pos.y), (pos.x + size//2, pos.y), 2)
        
        # Draw evolution indicator if evolved
        if self.evolved:
            # Draw a glowing halo around the tower
            for i in range(3):
                glow_size = size + 3 + i*2
                alpha = 150 - i*40
                glow_surface = pygame.Surface((glow_size*2, glow_size*2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, self.color + (alpha,), (glow_size, glow_size), glow_size)
                surface.blit(glow_surface, (pos.x - glow_size, pos.y - glow_size), special_flags=pygame.BLEND_ADD)
            
            # Draw evolution name
            if self.evolution_name:
                font = pygame.font.SysFont('arial', 12)
                text = font.render(self.evolution_name, True, (255, 255, 255))
                surface.blit(text, (pos.x - text.get_width()//2, pos.y + size + 5))
            
            # Draw targeting priority if selected
            if selected:
                priority_font = pygame.font.SysFont('arial', 14)
                priority_text = priority_font.render(f"Target: {self.targeting_priority}", True, (220, 220, 255))
                # Position text below evolution name (if present) or below tower
                text_y_offset = size + 20 # Default offset below tower center
                if self.evolved and self.evolution_name:
                    text_y_offset += 15 # Add more offset if evolution name is shown
                    
                surface.blit(priority_text, (pos.x - priority_text.get_width()//2, pos.y + text_y_offset)) 