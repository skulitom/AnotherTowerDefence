import pygame
import random
import math
from pygame.math import Vector2
from game.settings import tower_types
from game.towers.base_tower import BaseTower


class WaterTower(BaseTower):
    """
    Water Tower - Channels the ancient powers of the deep seas
    
    Special ability: Unleashes magical water that slows enemy movement.
    At higher levels, can create whirlpools that pull multiple enemies in
    and apply stronger slowing effects.
    """
    
    def initialize(self):
        """Initialize water tower specific properties"""
        # Magical water effects
        self.water_orbs = []
        self.orb_count = random.randint(3, 5)
        
        # Generate floating water orbs
        for _ in range(self.orb_count):
            self.water_orbs.append({
                'angle': random.uniform(0, 360),
                'distance': random.uniform(self.radius * 0.8, self.radius * 1.2),
                'size': random.uniform(3, 5),
                'speed': random.uniform(0.5, 1.5),
                'phase': random.uniform(0, math.pi * 2)
            })
        
        # Water ripple effect
        self.ripple_count = 3
        self.ripple_speeds = [random.uniform(0.8, 1.2) for _ in range(self.ripple_count)]
        self.ripple_opacity = [random.uniform(0.8, 1.0) for _ in range(self.ripple_count)]
        
        # Water vortex properties
        self.vortex_active = False
        self.vortex_timer = 0
        self.vortex_duration = 0
        self.vortex_cooldown = 5.0  # Seconds between vortex activations
        self.whirlpool_rotation = 0
        
        # Tide properties - water level rises and falls
        self.tide_height = 0
        self.tide_speed = random.uniform(0.1, 0.2)
        self.tide_phase = random.uniform(0, math.pi * 2)
        
        # Magic enhancement level
        self.water_magic_level = 1.0
        
    def upgrade_special(self, multiplier):
        """Enhance water tower special ability with upgrade"""
        super().upgrade_special(multiplier)
        
        # Visual enhancements on upgrade
        self.water_magic_level += 0.15
        
        # Add more water orbs at higher levels
        if self.level % 2 == 0 and self.orb_count < 8:
            self.water_orbs.append({
                'angle': random.uniform(0, 360),
                'distance': random.uniform(self.radius * 0.8, self.radius * 1.2),
                'size': random.uniform(3, 5),
                'speed': random.uniform(0.5, 1.5),
                'phase': random.uniform(0, math.pi * 2)
            })
            self.orb_count += 1
        
        # Enhance whirlpool abilities at higher levels
        if self.upgrades["special"] >= 1:
            self.vortex_duration = 2.0 + (self.upgrades["special"] * 0.5)
            self.vortex_cooldown = max(2.0, 5.0 - (self.upgrades["special"] * 0.5))
    
    def is_preferred_target(self, enemy, distance, current_best, current_best_distance):
        """Water towers target closest enemies"""
        if not current_best:
            return True
        return distance < current_best_distance
    
    def update_tower(self, dt, enemies, projectiles, particles=None):
        """Update water tower state"""
        super().update_tower(dt, enemies, projectiles, particles)
        
        # Update floating water orbs
        for orb in self.water_orbs:
            orb['angle'] += orb['speed'] * dt * 20  # Rotate around tower
            
            # Add water droplet particles occasionally
            if particles and random.random() < 0.02 * self.water_magic_level:
                orb_x = self.pos.x + math.cos(math.radians(orb['angle'])) * orb['distance']
                orb_y = self.pos.y + math.sin(math.radians(orb['angle'])) * orb['distance']
                
                # Droplet falls downward
                velocity = (random.uniform(-5, 5), random.uniform(20, 30))
                
                # Add droplet particle
                particles.add_particle_params(
                    Vector2(orb_x, orb_y),
                    (50, 100, 255),
                    velocity,
                    random.uniform(1, 2),
                    random.uniform(0.3, 0.6)
                )
        
        # Update tide level
        self.tide_height = math.sin(pygame.time.get_ticks() / 1000 * self.tide_speed + self.tide_phase) * 3
        
        # Update whirlpool effect
        if self.vortex_active:
            self.vortex_timer += dt
            self.whirlpool_rotation += dt * 180  # Rotate 180 degrees per second
            
            # Apply whirlpool effect to nearby enemies
            if self.vortex_timer <= self.vortex_duration:
                whirlpool_radius = self.range * 0.6
                whirlpool_center = self.pos
                
                for enemy in enemies:
                    distance = (enemy.pos - whirlpool_center).length()
                    if distance < whirlpool_radius:
                        # Calculate pull factor based on distance (stronger near center)
                        pull_strength = (1 - (distance / whirlpool_radius)) * 50 * dt
                        
                        # Pull enemy toward whirlpool center
                        direction = (whirlpool_center - enemy.pos).normalize()
                        enemy.pos += direction * pull_strength
                        
                        # Apply circular motion
                        angle = math.atan2(enemy.pos.y - whirlpool_center.y, 
                                           enemy.pos.x - whirlpool_center.x)
                        angle += dt * (1 - (distance / whirlpool_radius)) * 2
                        
                        new_x = whirlpool_center.x + math.cos(angle) * distance
                        new_y = whirlpool_center.y + math.sin(angle) * distance
                        enemy.pos = Vector2(new_x, new_y)
                        
                        # Apply slow effect
                        enemy.apply_effect("slow", 0.5, 0.7)
                
                # Generate whirlpool particles
                if particles and random.random() < 0.2 * self.water_magic_level:
                    angle = random.uniform(0, math.pi * 2)
                    distance = random.uniform(0, whirlpool_radius)
                    x = whirlpool_center.x + math.cos(angle) * distance
                    y = whirlpool_center.y + math.sin(angle) * distance
                    
                    # Particles follow circular motion
                    tangent_angle = angle + math.pi / 2
                    velocity = (math.cos(tangent_angle) * 20, math.sin(tangent_angle) * 20)
                    
                    particles.add_particle_params(
                        Vector2(x, y),
                        (100, 150, 255),
                        velocity,
                        random.uniform(1, 3),
                        random.uniform(0.2, 0.5)
                    )
            else:
                # Vortex duration ended
                self.vortex_active = False
                self.vortex_timer = 0
        elif self.upgrades["special"] >= 1:
            # Check for automatic vortex activation when special is upgraded
            self.vortex_timer += dt
            if self.vortex_timer >= self.vortex_cooldown:
                self.vortex_active = True
                self.vortex_timer = 0
    
    def fire_at_target(self, target, projectiles, particles=None):
        """Fire at target with enhanced water magic effects"""
        super().fire_at_target(target, projectiles, particles)
        
        # Add water splash effect when firing
        if particles:
            splash_count = int(6 * self.water_magic_level)
            for _ in range(splash_count):
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(10, 25) * self.water_magic_level
                velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
                
                particles.add_particle_params(
                    Vector2(self.pos),
                    (random.randint(50, 100), random.randint(100, 150), 255),
                    velocity,
                    random.uniform(2, 4),
                    random.uniform(0.3, 0.6)
                )
    
    def apply_projectile_effects(self, projectile):
        """Apply enhanced water effects to projectile"""
        super().apply_projectile_effects(projectile)
        
        # Magical water projectiles have additional effects
        if self.upgrades["special"] >= 2 and random.random() < 0.3:
            projectile.additional_effects = {
                "splash": {
                    "radius": 40 + (self.level * 3),
                    "slow_amount": 0.6 - (0.05 * self.upgrades["special"]),
                    "slow_duration": 1.5 + (0.2 * self.upgrades["special"])
                }
            }
    
    def draw_effects(self, surface, screen_pos, screen_radius, camera=None):
        """Draw water tower specific magical effects"""
        zoom_factor = camera.zoom if camera else 1
        
        # Draw magical water ripples
        ripple_time = pygame.time.get_ticks() / 1000 + self.pulse_offset
        for i in range(self.ripple_count):
            phase = (ripple_time * self.ripple_speeds[i] + i / self.ripple_count) % 1
            ripple_radius = max(1, screen_radius * (1 + phase * 2))  # Ensure minimum radius of 1
            alpha = int(100 * (1 - phase) * self.ripple_opacity[i])
            
            # Use safe surface size
            surf_width, surf_height = self.get_safe_surface_size(ripple_radius * 2, ripple_radius * 2, 2)
            ripple_surf = pygame.Surface((surf_width, surf_height), pygame.SRCALPHA)
            color = (100, 150, 255, alpha)
            pygame.draw.circle(ripple_surf, color, (surf_width // 2, surf_height // 2), 
                              min(surf_width // 2, surf_height // 2), 
                              max(1, int(1 * zoom_factor)))
            surface.blit(ripple_surf, (int(screen_pos.x - surf_width // 2), int(screen_pos.y - surf_height // 2)))
        
        # Draw water level indicator (base "floods" with water)
        base_radius = screen_radius * 1.3
        water_height = max(2, base_radius * 0.3 + (self.tide_height * zoom_factor))  # Ensure minimum height of 2
        water_rect = pygame.Rect(
            int(screen_pos.x - base_radius),
            int(screen_pos.y - (water_height/2)),
            max(2, int(base_radius * 2)),  # Ensure minimum width of 2
            max(2, int(water_height))      # Ensure minimum height of 2
        )
        
        # Draw water surface with multiple layers for depth
        for i in range(3):
            alpha = 150 - (i * 30)
            y_offset = i * 2 * zoom_factor
            adjusted_rect = pygame.Rect(
                water_rect.x,
                water_rect.y + y_offset,
                water_rect.width,
                max(1, water_rect.height - y_offset)  # Ensure height is at least 1
            )
            
            # Only draw if the dimensions are valid
            if adjusted_rect.width > 0 and adjusted_rect.height > 0:
                # Use safe surface size
                surf_width, surf_height = self.get_safe_surface_size(adjusted_rect.width, adjusted_rect.height, 2)
                water_surf = pygame.Surface((surf_width, surf_height), pygame.SRCALPHA)
                water_color = (50 + i*20, 100 + i*20, 200 + i*10, alpha)
                pygame.draw.ellipse(water_surf, water_color, 
                                  (0, 0, surf_width, surf_height))
                surface.blit(water_surf, adjusted_rect.topleft)
        
        # Draw water ripple lines on the surface
        ripple_count = 3
        for i in range(ripple_count):
            # Create ripple position with a sine wave
            ripple_phase = (pygame.time.get_ticks() / 1000 + i * 0.33) % 1
            ripple_width = base_radius * 1.8
            ripple_y = screen_pos.y - (water_height/2) + (ripple_phase * water_height * 0.8)
            
            # Draw wavy water line
            points = []
            wave_segments = 12
            for j in range(wave_segments + 1):
                x_pos = screen_pos.x - ripple_width + (j * (ripple_width * 2) / wave_segments)
                y_offset = math.sin(j * 0.5 + pygame.time.get_ticks() / 200) * 2 * zoom_factor
                points.append((x_pos, ripple_y + y_offset))
            
            if len(points) >= 2:
                pygame.draw.lines(surface, (200, 230, 255, 100), False, points, 
                                max(1, int(1 * zoom_factor)))
        
        # Draw floating water orbs
        current_time = pygame.time.get_ticks() / 1000
        for orb in self.water_orbs:
            # Calculate orb position with slight vertical bobbing
            vertical_offset = math.sin(current_time * 2 + orb['phase']) * 3 * zoom_factor
            orb_x = screen_pos.x + math.cos(math.radians(orb['angle'])) * orb['distance'] * zoom_factor
            orb_y = screen_pos.y + math.sin(math.radians(orb['angle'])) * orb['distance'] * zoom_factor + vertical_offset
            
            # Draw water orb with glowing aura
            orb_size = max(1, orb['size'] * zoom_factor * self.water_magic_level)  # Ensure minimum size of 1
            
            # Inner glow
            glow_size = max(4, int(orb_size * 4))  # Ensure minimum size of 4
            # Use safe surface size
            surf_width, surf_height = self.get_safe_surface_size(glow_size, glow_size, 4)
            glow_surf = pygame.Surface((surf_width, surf_height), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (100, 200, 255, 50), 
                             (surf_width // 2, surf_height // 2), 
                             min(surf_width // 2, surf_height // 2))
            surface.blit(glow_surf, (int(orb_x - surf_width // 2), int(orb_y - surf_height // 2)))
            
            # Orb itself
            pygame.draw.circle(surface, (100, 150, 255), (int(orb_x), int(orb_y)), max(1, int(orb_size * 1.2)))
            pygame.draw.circle(surface, (200, 230, 255), (int(orb_x), int(orb_y)), max(1, int(orb_size)))
            
            # Highlight
            highlight_x = orb_x - orb_size * 0.3
            highlight_y = orb_y - orb_size * 0.3
            pygame.draw.circle(surface, (255, 255, 255, 180), 
                             (int(highlight_x), int(highlight_y)), 
                             int(orb_size * 0.4))
        
        # Draw whirlpool effect when active
        if self.vortex_active:
            whirlpool_radius = max(2, self.range * 0.6 * zoom_factor)  # Ensure minimum radius of 2
            
            # Draw spiral effect
            spiral_segments = 20
            for segment in range(1, spiral_segments):
                segment_percent = segment / spiral_segments
                radius = max(2, whirlpool_radius * segment_percent)  # Ensure minimum radius of 2
                alpha = int(150 * (1 - segment_percent))
                
                spiral_surf_size = max(4, int(radius * 2))  # Ensure minimum size of 4
                # Use safe surface size
                surf_width, surf_height = self.get_safe_surface_size(spiral_surf_size, spiral_surf_size, 4)
                spiral_surf = pygame.Surface((surf_width, surf_height), pygame.SRCALPHA)
                
                start_angle = math.radians(self.whirlpool_rotation)
                end_angle = math.radians(self.whirlpool_rotation + 270 * segment_percent)
                
                # Draw arc
                pygame.draw.arc(spiral_surf, (100, 150, 255, alpha), 
                              (0, 0, surf_width, surf_height), 
                              start_angle, end_angle, 
                              max(1, int(3 * zoom_factor * segment_percent)))
                
                surface.blit(spiral_surf, (int(screen_pos.x - surf_width // 2), int(screen_pos.y - surf_height // 2)))
            
            # Draw center of whirlpool
            center_radius = max(1, whirlpool_radius * 0.15)  # Ensure minimum radius of 1
            pygame.draw.circle(surface, (50, 100, 200, 150), 
                             (int(screen_pos.x), int(screen_pos.y)), 
                             int(center_radius)) 