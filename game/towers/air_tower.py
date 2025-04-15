import pygame
import random
import math
from pygame.math import Vector2
from game.settings import tower_types
from game.towers.base_tower import BaseTower


class AirTower(BaseTower):
    """
    Air Tower - Harnesses the elemental power of wind and storms
    
    Special ability: Chain lightning that arcs between enemies.
    Higher levels increase chain targets and can summon mini-tornados.
    """
    
    def initialize(self):
        """Initialize air tower specific properties"""
        # Wind effects
        self.wind_particles = []
        self.wind_timer = 0
        self.wind_direction = random.uniform(0, 360)
        self.wind_speed = random.uniform(0.5, 1.5)
        
        # Cloud formation
        self.cloud_count = random.randint(3, 5)
        self.clouds = []
        for _ in range(self.cloud_count):
            self.clouds.append({
                'angle': random.uniform(0, 360),
                'distance': random.uniform(self.radius * 0.8, self.radius * 1.5),
                'size': random.uniform(4, 7),
                'speed': random.uniform(15, 30),
                'opacity': random.uniform(0.7, 1.0)
            })
        
        # Lightning effects
        self.lightning_timer = 0
        self.lightning_cooldown = random.uniform(3, 5)
        self.lightning_active = False
        self.lightning_duration = 0.2
        self.lightning_points = []
        
        # Tornado effects
        self.tornado_active = False
        self.tornado_timer = 0
        self.tornado_cooldown = 10.0
        self.tornado_duration = 0
        self.tornado_radius = 0
        self.tornado_particles = []
        
        # Magic power level
        self.air_magic_level = 1.0
        
    def upgrade_special(self, multiplier):
        """Enhance air tower special ability with upgrade"""
        super().upgrade_special(multiplier)
        
        # Visual and effect enhancements
        self.air_magic_level += 0.15
        
        # Enhanced tornado at higher levels
        if self.upgrades["special"] >= 1:
            self.tornado_duration = 3.0 + self.upgrades["special"] * 0.5
            self.tornado_cooldown = max(3.0, 10.0 - self.upgrades["special"])
            self.tornado_radius = 30 + self.upgrades["special"] * 10
        
        # Add more clouds at higher levels
        if self.level % 2 == 0 and self.cloud_count < 8:
            self.clouds.append({
                'angle': random.uniform(0, 360),
                'distance': random.uniform(self.radius * 0.8, self.radius * 1.5),
                'size': random.uniform(4, 7),
                'speed': random.uniform(15, 30),
                'opacity': random.uniform(0.7, 1.0)
            })
            self.cloud_count += 1
        
    def is_preferred_target(self, enemy, distance, current_best, current_best_distance):
        """Air towers target enemies furthest along the path"""
        if not current_best:
            return True
        return enemy.current_point_index > current_best.current_point_index
        
    def update_tower(self, dt, enemies, projectiles, particles=None):
        """Update air tower state"""
        super().update_tower(dt, enemies, projectiles, particles)
        
        # Update wind direction occasionally
        self.wind_timer += dt
        if self.wind_timer > 2.0:
            self.wind_timer = 0
            self.wind_direction = (self.wind_direction + random.uniform(-30, 30)) % 360
            self.wind_speed = random.uniform(0.5, 1.5)
        
        # Generate wind particles
        if particles and random.random() < 0.1 * self.air_magic_level:
            # Create wind particles in the current wind direction
            angle = math.radians(self.wind_direction)
            # Start particles from random positions around tower
            distance = random.uniform(self.radius * 0.5, self.radius * 2)
            start_angle = random.uniform(0, math.pi * 2)
            x = self.pos.x + math.cos(start_angle) * distance
            y = self.pos.y + math.sin(start_angle) * distance
            
            # Set velocity in wind direction
            speed = random.uniform(30, 60) * self.wind_speed
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            
            # Add wind particle
            particles.add_particle_params(
                Vector2(x, y),
                (200 + random.randint(0, 55), 230 + random.randint(0, 25), 255),
                velocity,
                random.uniform(1, 3),
                random.uniform(0.3, 0.8)
            )
        
        # Update cloud positions
        for cloud in self.clouds:
            cloud['angle'] = (cloud['angle'] + cloud['speed'] * dt * 0.5) % 360
        
        # Random lightning effect
        self.lightning_timer += dt
        if self.upgrades["special"] >= 2 and self.lightning_timer > self.lightning_cooldown:
            self.lightning_timer = 0
            self.lightning_cooldown = random.uniform(3, 5) / self.air_magic_level
            self.lightning_active = True
            self.lightning_duration = 0.2
            
            # Generate random lightning path between clouds
            if len(self.clouds) >= 2:
                src_cloud = random.choice(self.clouds)
                dst_cloud = random.choice([c for c in self.clouds if c != src_cloud])
                
                # Create lightning path
                src_x = self.pos.x + math.cos(math.radians(src_cloud['angle'])) * src_cloud['distance']
                src_y = self.pos.y + math.sin(math.radians(src_cloud['angle'])) * src_cloud['distance']
                dst_x = self.pos.x + math.cos(math.radians(dst_cloud['angle'])) * dst_cloud['distance']
                dst_y = self.pos.y + math.sin(math.radians(dst_cloud['angle'])) * dst_cloud['distance']
                
                self.lightning_points = [(src_x, src_y)]
                current_x, current_y = src_x, src_y
                target_x, target_y = dst_x, dst_y
                
                segments = random.randint(3, 7)
                for i in range(segments):
                    # Move toward target with random deviation
                    progress = (i + 1) / segments
                    next_x = src_x + (dst_x - src_x) * progress
                    next_y = src_y + (dst_y - src_y) * progress
                    
                    # Add random jaggedness to lightning
                    jag_x = random.uniform(-20, 20) * (1 - progress)
                    jag_y = random.uniform(-20, 20) * (1 - progress)
                    
                    self.lightning_points.append((next_x + jag_x, next_y + jag_y))
        
        # Update lightning effect
        if self.lightning_active:
            self.lightning_duration -= dt
            if self.lightning_duration <= 0:
                self.lightning_active = False
        
        # Update tornado effect
        if self.tornado_active:
            self.tornado_timer += dt
            if self.tornado_timer <= self.tornado_duration:
                # Apply tornado effect to enemies
                tornado_radius = self.tornado_radius * self.air_magic_level
                
                # Find enemies in tornado range
                for enemy in enemies:
                    distance = (enemy.pos - self.pos).length()
                    if distance < tornado_radius:
                        # Calculate push factor - stronger near edge of tornado
                        push_factor = (distance / tornado_radius) * 50 * dt
                        
                        # Calculate push direction (tangential to tornado)
                        angle = math.atan2(enemy.pos.y - self.pos.y, enemy.pos.x - self.pos.x)
                        push_angle = angle + math.pi/2  # Tangential
                        
                        # Apply push force
                        push_x = math.cos(push_angle) * push_factor
                        push_y = math.sin(push_angle) * push_factor
                        
                        enemy.pos.x += push_x
                        enemy.pos.y += push_y
                        
                        # Apply slow effect
                        enemy.apply_effect("slow", 0.2, 0.3)
                
                # Generate tornado particles
                if particles and random.random() < 0.2 * self.air_magic_level:
                    angle = random.uniform(0, math.pi * 2)
                    distance = random.uniform(0, tornado_radius)
                    height = random.uniform(0, 30)  # Vertical height simulation
                    
                    x = self.pos.x + math.cos(angle) * distance
                    y = self.pos.y + math.sin(angle) * distance
                    
                    # Spiral velocity
                    tangent_angle = angle + math.pi/2
                    speed = distance / tornado_radius * 80
                    velocity = (math.cos(tangent_angle) * speed, math.sin(tangent_angle) * speed)
                    
                    # Lighter color with height
                    color_factor = min(1.0, height / 20)
                    color = (
                        int(200 + color_factor * 55),
                        int(230 + color_factor * 25),
                        255
                    )
                    
                    particles.add_particle_params(
                        Vector2(x, y),
                        color,
                        velocity,
                        random.uniform(1, 3 + height/10),
                        random.uniform(0.1, 0.3)
                    )
            else:
                self.tornado_active = False
                self.tornado_timer = 0
        elif self.upgrades["special"] >= 1:
            # Automatically activate tornado when cooldown is reached
            self.tornado_timer += dt
            if self.tornado_timer >= self.tornado_cooldown:
                self.tornado_active = True
                self.tornado_timer = 0
    
    def fire_at_target(self, target, projectiles, particles=None):
        """Fire at target with enhanced air magic effects"""
        super().fire_at_target(target, projectiles, particles)
        
        # Add wind burst effect when firing
        if particles:
            burst_count = int(5 * self.air_magic_level)
            for _ in range(burst_count):
                # Direction toward target with some spread
                target_angle = math.atan2(target.pos.y - self.pos.y, target.pos.x - self.pos.x)
                angle_spread = random.uniform(-0.5, 0.5)
                angle = target_angle + angle_spread
                
                speed = random.uniform(40, 80) * self.air_magic_level
                velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
                
                particles.add_particle_params(
                    Vector2(self.pos),
                    (200 + random.randint(0, 55), 230 + random.randint(0, 25), 255),
                    velocity,
                    random.uniform(2, 4),
                    random.uniform(0.2, 0.4)
                )
    
    def apply_projectile_effects(self, projectile):
        """Apply enhanced air effects to projectile"""
        super().apply_projectile_effects(projectile)
        
        # Magical air projectiles - enhanced chain targets at higher levels
        if self.special_ability == "chain":
            stats = tower_types[self.tower_type]
            base_targets = stats.get("special_targets", 3)
            if self.upgrades["special"] > 0:
                projectile.effect["targets"] = base_targets + self.upgrades["special"]
    
    def draw_effects(self, surface, screen_pos, screen_radius, camera=None):
        """Draw air tower specific magical effects"""
        zoom_factor = camera.zoom if camera else 1
        current_time_ms = pygame.time.get_ticks()
        
        # 1. Enhanced Swirling Wind Effect (More clouds, faster rotation)
        cloud_count = 5 # Increased from 3
        base_rotation_speed = 0.0015 # Slightly faster base speed
        for i in range(cloud_count):
            angle = ((current_time_ms * base_rotation_speed) + i * (6.28 / cloud_count) + self.wind_direction / 180 * math.pi) % 6.28
            orbit_radius = screen_radius * (1.2 + 0.3 * math.sin(current_time_ms * 0.001 + i)) # More dynamic orbit radius
            x = screen_pos.x + math.cos(angle) * orbit_radius * zoom_factor
            y = screen_pos.y + math.sin(angle) * orbit_radius * zoom_factor
            
            cloud_radius = (3 + math.sin(current_time_ms * 0.002 + i) * 1.5) * zoom_factor # Slightly larger clouds
            if cloud_radius > 1:
                cloud_surf = pygame.Surface((int(cloud_radius * 2), int(cloud_radius * 2)), pygame.SRCALPHA)
                pygame.draw.circle(cloud_surf, (200, 230, 255, 120), (cloud_radius, cloud_radius), cloud_radius) # Slightly less opaque
                surface.blit(cloud_surf, (int(x - cloud_radius), int(y - cloud_radius)))
        
        # 2. Base Vortex Effect (New)
        vortex_radius = screen_radius * 0.9
        vortex_segments = 8
        vortex_rotation_speed = -0.003 # Rotate opposite to clouds
        for i in range(vortex_segments):
            angle1 = ((current_time_ms * vortex_rotation_speed) + i * (6.28 / vortex_segments)) % 6.28
            angle2 = ((current_time_ms * vortex_rotation_speed) + (i + 0.5) * (6.28 / vortex_segments)) % 6.28 # Offset for curve
            
            start_radius_factor = 0.3 + 0.7 * (abs(math.sin(current_time_ms * 0.0005 + i))) # Pulsating start radius
            end_radius_factor = 1.0
            
            start_x = screen_pos.x + math.cos(angle1) * vortex_radius * start_radius_factor * zoom_factor
            start_y = screen_pos.y + math.sin(angle1) * vortex_radius * start_radius_factor * zoom_factor
            end_x = screen_pos.x + math.cos(angle2) * vortex_radius * end_radius_factor * zoom_factor
            end_y = screen_pos.y + math.sin(angle2) * vortex_radius * end_radius_factor * zoom_factor
            
            mid_x = (start_x + end_x) / 2 + math.cos(angle1 + math.pi/2) * vortex_radius * 0.2 * zoom_factor # Control point for curve
            mid_y = (start_y + end_y) / 2 + math.sin(angle1 + math.pi/2) * vortex_radius * 0.2 * zoom_factor

            points = [(start_x, start_y), (mid_x, mid_y), (end_x, end_y)]
            
            # Draw curved lines for vortex
            try:
                if all(0 <= p[0] < surface.get_width() and 0 <= p[1] < surface.get_height() for p in points):
                     # Crude bezier approximation with lines or use pygame.draw.aalines if thicker/smoother look desired
                    pygame.draw.aaline(surface, (180, 210, 230, 80), points[0], points[1])
                    pygame.draw.aaline(surface, (180, 210, 230, 80), points[1], points[2])
            except IndexError: # Handle potential index errors during rapid changes
                pass 

        # 3. Wind Gust Particles (New / Enhanced from old random lines)
        if random.random() < 0.15: # Increased frequency
            gust_angle = math.radians(self.wind_direction + random.uniform(-15, 15)) # Angle based on wind direction + spread
            start_dist = screen_radius * 1.1
            end_dist = screen_radius * random.uniform(2.5, 4.0) # Gusts travel further
            
            start_x = screen_pos.x + math.cos(gust_angle) * start_dist * zoom_factor
            start_y = screen_pos.y + math.sin(gust_angle) * start_dist * zoom_factor
            end_x = screen_pos.x + math.cos(gust_angle) * end_dist * zoom_factor
            end_y = screen_pos.y + math.sin(gust_angle) * end_dist * zoom_factor
            
            # Draw gust line (thin and fast)
            gust_alpha = random.randint(60, 120)
            gust_width = max(1, int(1 * zoom_factor))
            pygame.draw.line(surface, (220, 240, 255, gust_alpha), 
                           (int(start_x), int(start_y)), 
                           (int(end_x), int(end_y)), 
                           gust_width)

        # Existing Crackling Energy Effect (Keep as is or modify if desired)
        if self.level >= 2:
            arc_count = 3 + self.level
            for i in range(arc_count):
                angle = math.radians(i * (360 / arc_count) + pygame.time.get_ticks() / 50)
                length = (screen_radius * 0.6) * (0.7 + 0.3 * math.sin(pygame.time.get_ticks() / 200 + i))
                
                start_x = screen_pos.x
                start_y = screen_pos.y - screen_radius * 0.5
                
                # Create a jagged lightning arc
                points = [(start_x, start_y)]
                end_x = start_x + math.cos(angle) * length
                end_y = start_y + math.sin(angle) * length
                
                segments = random.randint(2, 4)
                for j in range(segments):
                    # Progress toward end point with jitter
                    progress = (j + 1) / segments
                    jitter_x = random.uniform(-length * 0.15, length * 0.15)
                    jitter_y = random.uniform(-length * 0.15, length * 0.15)
                    
                    point_x = start_x + (end_x - start_x) * progress + jitter_x
                    point_y = start_y + (end_y - start_y) * progress + jitter_y
                    points.append((point_x, point_y))
                
                # Draw jagged lightning
                if len(points) >= 2:
                    alpha = random.randint(150, 200)
                    for j in range(len(points) - 1):
                        pygame.draw.line(surface, (180, 220, 255, alpha),
                                       (int(points[j][0]), int(points[j][1])),
                                       (int(points[j+1][0]), int(points[j+1][1])),
                                       max(1, int(1 * zoom_factor))) 