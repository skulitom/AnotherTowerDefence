import pygame
import random
import math
from pygame.math import Vector2
from game.settings import tower_types
from game.towers.base_tower import BaseTower


class LightTower(BaseTower):
    """
    Light Tower - Channels the power of radiant illumination
    
    Special ability: Reveals invisible enemies within its range and deals
    extra damage to them. At higher levels, creates bursts of purifying light
    that damage multiple enemies.
    """
    
    def initialize(self):
        """Initialize light tower specific properties"""
        # Light rays
        self.ray_count = 8
        self.ray_length = self.radius * 1.5
        self.ray_width = 2
        self.ray_rotation = random.uniform(0, 360)
        self.ray_spin_speed = random.uniform(5, 15) * (1 if random.random() > 0.5 else -1)
        
        # Orbiting light motes
        self.light_motes = []
        mote_count = 4 + self.level
        for _ in range(mote_count):
            self.light_motes.append({
                'angle': random.uniform(0, 360),
                'distance': random.uniform(self.radius * 0.8, self.radius * 1.2),
                'size': random.uniform(2, 4),
                'speed': random.uniform(20, 40),
                'pulse_speed': random.uniform(1.0, 2.0),
                'pulse_offset': random.uniform(0, math.pi * 2)
            })
        
        # Radiance effect
        self.radiance_pulse_speed = random.uniform(0.8, 1.2)
        self.radiance_size = random.uniform(0.9, 1.1)
        self.reveal_range = self.range * 0.8
        self.reveal_active = False
        self.reveal_pulse = 0
        
        # Light burst effect
        self.burst_cooldown = 5.0
        self.burst_timer = random.uniform(0, 2.0)  # Random initial delay
        self.burst_chance = 0  # Increases with upgrades
        self.burst_damage = 0  # Increases with upgrades
        self.burst_radius = self.range * 0.6
        
        # Magic enhancement level
        self.light_magic_level = 1.0
        
    def upgrade_special(self, multiplier):
        """Enhance light tower special ability with upgrade"""
        super().upgrade_special(multiplier)
        
        # Visual and effect enhancements
        self.light_magic_level += 0.2
        
        # Increase reveal range
        self.reveal_range = self.range * (0.8 + (0.05 * self.upgrades["special"]))
        
        # Add more light motes at higher levels
        if self.level % 2 == 0 and len(self.light_motes) < 12:
            for _ in range(2):
                self.light_motes.append({
                    'angle': random.uniform(0, 360),
                    'distance': random.uniform(self.radius * 0.8, self.radius * 1.2),
                    'size': random.uniform(2, 4),
                    'speed': random.uniform(20, 40),
                    'pulse_speed': random.uniform(1.0, 2.0),
                    'pulse_offset': random.uniform(0, math.pi * 2)
                })
        
        # Enable light burst at level 2 special
        if self.upgrades["special"] >= 2:
            self.burst_chance = 0.2 + (0.1 * (self.upgrades["special"] - 2))
            self.burst_damage = self.damage * (0.3 + (0.1 * (self.upgrades["special"] - 2)))
            self.burst_cooldown = max(2.0, 5.0 - (0.5 * (self.upgrades["special"] - 2)))
            
    def is_preferred_target(self, enemy, distance, current_best, current_best_distance):
        """Light towers prioritize invisible enemies"""
        if not current_best:
            return True
            
        # Target invisible enemies first
        enemy_is_cloaked = "cloak" in enemy.status_effects if hasattr(enemy, "status_effects") else False
        current_is_cloaked = "cloak" in current_best.status_effects if hasattr(current_best, "status_effects") else False
        
        if enemy_is_cloaked and not current_is_cloaked:
            return True
        elif not enemy_is_cloaked and current_is_cloaked:
            return False
            
        # Otherwise target closest enemy
        return distance < current_best_distance
        
    def update_tower(self, dt, enemies, projectiles, particles=None):
        """Update light tower state"""
        super().update_tower(dt, enemies, projectiles, particles)
        
        # Update light motes
        for mote in self.light_motes:
            mote['angle'] = (mote['angle'] + mote['speed'] * dt) % 360
        
        # Update light rays
        self.ray_rotation += self.ray_spin_speed * dt
        
        # Update reveal effect
        self.reveal_active = False
        for enemy in enemies:
            # Skip enemies that are too far
            if (enemy.pos - self.pos).length() > self.reveal_range:
                continue
                
            # Reveal invisible enemies
            if hasattr(enemy, "status_effects") and "cloak" in enemy.status_effects:
                self.reveal_active = True
                enemy.apply_effect("reveal", 0.5, None)  # Reveal for half a second
                
                # Apply reveal visual effect
                if particles and random.random() < 0.1 * self.light_magic_level:
                    angle = random.uniform(0, math.pi * 2)
                    distance = random.uniform(0, enemy.radius * 0.8)
                    x = enemy.pos.x + math.cos(angle) * distance
                    y = enemy.pos.y + math.sin(angle) * distance
                    
                    # Particles spread outward
                    speed = random.uniform(10, 20)
                    velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
                    
                    particles.add_particle_params(
                        Vector2(x, y),
                        (255, 255, 100),
                        velocity,
                        random.uniform(1, 3),
                        random.uniform(0.2, 0.4)
                    )
        
        # Update light burst
        if self.burst_chance > 0:
            self.burst_timer += dt
            if self.burst_timer >= self.burst_cooldown:
                self.burst_timer = 0
                
                # Check for burst activation
                if random.random() < self.burst_chance:
                    # Pass the particles parameter to activate_light_burst
                    self.activate_light_burst(enemies, particles)
                
    def activate_light_burst(self, enemies, particles=None):
        """Activate a burst of purifying light that damages enemies"""
        try:
            enemies_hit = []
            for enemy in enemies:
                distance = (enemy.pos - self.pos).length()
                if distance <= self.burst_radius:
                    # Add to hit list
                    enemies_hit.append(enemy)
                    
                    # Apply damage
                    enemy.take_damage(self.burst_damage, self.tower_type)
                    self.damage_dealt += self.burst_damage
                    
                    # Create hit effect
                    if particles:
                        particles.add_explosion(
                            enemy.pos.x, enemy.pos.y, 
                            (255, 255, 100), 
                            count=10, 
                            size_range=(3, 6), 
                            life_range=(0.3, 0.8)
                        )
            
            # Create burst visual effect
            if particles:
                # Create expanding ring
                for i in range(20):
                    angle = (i / 20) * math.pi * 2
                    distance = self.burst_radius * 0.5
                    
                    x = self.pos.x + math.cos(angle) * distance
                    y = self.pos.y + math.sin(angle) * distance
                    
                    # Particles expand outward
                    speed = self.burst_radius / 0.5  # Travel to radius in 0.5 seconds
                    velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
                    
                    particles.add_particle_params(
                        Vector2(x, y),
                        (255, 255, 200),
                        velocity,
                        random.uniform(3, 5),
                        random.uniform(0.4, 0.6)
                    )
        except Exception as e:
            # Silently handle particle errors to prevent game crashes
            pass
    
    def fire_at_target(self, target, projectiles, particles=None):
        """Fire at target with enhanced light magic effects"""
        super().fire_at_target(target, projectiles, particles)
        
        # Add light burst effect when firing
        if particles:
            burst_count = int(5 * self.light_magic_level)
            for _ in range(burst_count):
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(30, 60) * self.light_magic_level
                velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
                
                particles.add_particle_params(
                    Vector2(self.pos),
                    (255, 255, 150),
                    velocity,
                    random.uniform(2, 4),
                    random.uniform(0.2, 0.4)
                )
    
    def apply_projectile_effects(self, projectile):
        """Apply enhanced light effects to projectile"""
        super().apply_projectile_effects(projectile)
        
        # Light projectiles are faster
        projectile.speed *= 1.1
        
        # Extra damage to revealed invisible enemies
        if hasattr(projectile.target, "status_effects") and "reveal" in projectile.target.status_effects:
            projectile.damage *= 1.5
    
    def draw_effects(self, surface, screen_pos, screen_radius, camera=None):
        """Draw light tower specific magical effects"""
        try:
            zoom_factor = camera.zoom if camera else 1
            
            # Draw light aura
            current_time = pygame.time.get_ticks() / 1000
            aura_pulse = 0.2 * math.sin(current_time * self.radiance_pulse_speed + self.pulse_offset)
            aura_radius = screen_radius * (1.2 + aura_pulse) * self.radiance_size * self.light_magic_level
            
            # Aura glow
            for i in range(3):
                alpha = 100 - (i * 30)
                size = aura_radius * (1 + i * 0.3)
                
                # Check for valid size before creating surface
                if size <= 0:
                    continue
                    
                surf_size = max(1, int(size * 2))  # Ensure positive surface size
                aura_surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
                
                # Create gradient of color from center
                pygame.draw.circle(aura_surf, (255, 255, 100, alpha), (size, size), size)
                
                # Add rays of light at higher levels
                if self.level >= 2:
                    ray_count = 8 + self.level * 2
                    ray_extension = size * 0.3
                    
                    for j in range(ray_count):
                        ray_angle = j * (2 * math.pi / ray_count) + current_time
                        ray_x = size + math.cos(ray_angle) * (size + ray_extension)
                        ray_y = size + math.sin(ray_angle) * (size + ray_extension)
                        
                        # Draw ray
                        pygame.draw.line(aura_surf, (255, 255, 150, alpha // 2),
                                       (size, size),
                                       (ray_x, ray_y),
                                       max(1, int(2 * zoom_factor)))
                
                # Blit aura to surface
                surface.blit(aura_surf, (int(screen_pos.x - size), int(screen_pos.y - size)))
            
            # Draw reveal aura if active
            if self.reveal_active:
                # Pulsing reveal circle
                self.reveal_pulse = (self.reveal_pulse + 0.05) % 1
                reveal_size = self.reveal_range * zoom_factor * (0.8 + self.reveal_pulse * 0.4)
                
                # Create pulsing circle
                if reveal_size > 0:
                    # Use safe surface size
                    surf_width, surf_height = self.get_safe_surface_size(reveal_size * 2, reveal_size * 2, 2)
                    reveal_surf = pygame.Surface((surf_width, surf_height), pygame.SRCALPHA)
                    alpha = int(80 * (1 - self.reveal_pulse))
                    pygame.draw.circle(reveal_surf, (255, 255, 100, alpha),
                                     (surf_width // 2, surf_height // 2),
                                     min(surf_width // 2, surf_height // 2), 
                                     max(1, int(2 * zoom_factor)))
                    surface.blit(reveal_surf, (int(screen_pos.x - surf_width // 2), int(screen_pos.y - surf_height // 2)))
            
            # Draw light rays
            ray_length = max(2, self.ray_length * zoom_factor)
            # Use safe surface size
            surf_width, surf_height = self.get_safe_surface_size(ray_length * 2, ray_length * 2, 4)
            ray_surf = pygame.Surface((surf_width, surf_height), pygame.SRCALPHA)
            for i in range(self.ray_count):
                ray_angle = (i / self.ray_count) * math.pi * 2 + math.radians(self.ray_rotation)
                ray_end_x = surf_width // 2 + math.cos(ray_angle) * ray_length
                ray_end_y = surf_height // 2 + math.sin(ray_angle) * ray_length
                
                # Draw ray with glow
                ray_color = (255, 255, 100, 150)
                pygame.draw.line(ray_surf, ray_color,
                               (surf_width // 2, surf_height // 2),
                               (ray_end_x, ray_end_y),
                               max(1, int(2 * zoom_factor)))
            
            # Add glow to center of rays
            pygame.draw.circle(ray_surf, (255, 255, 150, 100), 
                             (int(surf_width // 2), int(surf_height // 2)), 
                             int(screen_radius * 0.8))
            
            # Blit rays to surface
            ray_pos = (int(screen_pos.x - surf_width // 2), int(screen_pos.y - surf_height // 2))
            surface.blit(ray_surf, ray_pos)
            
            # Draw light motes
            for mote in self.light_motes:
                mote_angle = math.radians(mote['angle'])
                
                # Calculate pulse effect
                pulse = math.sin(current_time * mote['pulse_speed'] + mote['pulse_offset']) * 0.3 + 0.7
                mote_size = mote['size'] * pulse * zoom_factor * self.light_magic_level
                
                # Calculate position
                mote_x = screen_pos.x + math.cos(mote_angle) * mote['distance'] * zoom_factor
                mote_y = screen_pos.y + math.sin(mote_angle) * mote['distance'] * zoom_factor
                
                # Draw light mote with glow
                if mote_size > 0:
                    # Core of the mote
                    pygame.draw.circle(surface, (255, 255, 255), 
                                     (int(mote_x), int(mote_y)), 
                                     max(1, int(mote_size)))
                    
                    # Outer glow
                    glow_size = max(2, mote_size * 2)
                    if glow_size > 0:
                        # Use safe surface size
                        surf_width, surf_height = self.get_safe_surface_size(glow_size * 2, glow_size * 2, 4)
                        glow_surf = pygame.Surface((surf_width, surf_height), pygame.SRCALPHA)
                        pygame.draw.circle(glow_surf, (255, 255, 150, 100), 
                                         (surf_width // 2, surf_height // 2), 
                                         min(surf_width // 2, surf_height // 2))
                        surface.blit(glow_surf, (int(mote_x - surf_width // 2), int(mote_y - surf_height // 2)))
            
            # Draw light crown above tower
            if self.level >= 2:
                crown_height = screen_radius * 1.2
                crown_points = []
                point_count = 5 + self.level
                
                for i in range(point_count):
                    angle = math.pi + (i * (math.pi / (point_count - 1))) - (math.pi / 2)
                    
                    # Add height variation for crown points
                    height_factor = 1.0 + (math.sin(i * 0.5 + current_time * 2) * 0.1)
                    
                    point_x = screen_pos.x + math.cos(angle) * crown_height * 0.8 * zoom_factor
                    point_y = screen_pos.y - crown_height * height_factor * zoom_factor
                    
                    crown_points.append((point_x, point_y))
                    
                    # Draw light emanating from crown points
                    if random.random() < 0.3 * self.light_magic_level:
                        # Light rays emanating upward
                        ray_length = random.uniform(5, 15) * zoom_factor
                        ray_angle = -math.pi/2 + random.uniform(-0.3, 0.3)
                        
                        ray_end_x = point_x + math.cos(ray_angle) * ray_length
                        ray_end_y = point_y + math.sin(ray_angle) * ray_length
                        
                        # Draw light ray with glow
                        pygame.draw.line(surface, (255, 255, 150, 150),
                                       (int(point_x), int(point_y)),
                                       (int(ray_end_x), int(ray_end_y)),
                                       max(1, int(1 * zoom_factor)))
                
                # Draw connecting lines between crown points
                if len(crown_points) >= 2:
                    pygame.draw.lines(surface, (255, 255, 150, 200), False, crown_points, 
                                    max(1, int(2 * zoom_factor)))
                    
                # Add glow to crown
                for point in crown_points:
                    glow_size = max(2, 3 * zoom_factor)
                    if glow_size > 0:
                        # Use safe surface size
                        surf_width, surf_height = self.get_safe_surface_size(glow_size * 2, glow_size * 2, 4)
                        glow_surf = pygame.Surface((surf_width, surf_height), pygame.SRCALPHA)
                        pygame.draw.circle(glow_surf, (255, 255, 150, 100), 
                                         (surf_width // 2, surf_height // 2), 
                                         min(surf_width // 2, surf_height // 2))
                        surface.blit(glow_surf, (int(point[0] - surf_width // 2), int(point[1] - surf_height // 2)))
            
            # Draw light burst effect
            if self.burst_chance > 0 and self.burst_timer >= self.burst_cooldown * 0.8:
                # Draw charging effect as burst is about to happen
                charge_percent = (self.burst_timer - (self.burst_cooldown * 0.8)) / (self.burst_cooldown * 0.2)
                charge_radius = max(2, self.burst_radius * charge_percent * zoom_factor)
                
                if charge_radius > 0:
                    # Use safe surface size
                    surf_width, surf_height = self.get_safe_surface_size(charge_radius * 2, charge_radius * 2, 4)
                    charge_surf = pygame.Surface((surf_width, surf_height), pygame.SRCALPHA)
                    charge_alpha = int(50 * charge_percent)
                    pygame.draw.circle(charge_surf, (255, 255, 100, charge_alpha),
                                     (surf_width // 2, surf_height // 2),
                                     min(surf_width // 2, surf_height // 2))
                    surface.blit(charge_surf, (int(screen_pos.x - surf_width // 2), int(screen_pos.y - surf_height // 2)))
        except Exception as e:
            print(f"Error in draw_effects: {e}")
            import traceback
            traceback.print_exc() 