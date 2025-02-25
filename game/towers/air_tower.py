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
        
        # Draw swirling wind effect
        for i in range(3):
            angle = ((pygame.time.get_ticks() / 500) + i * 2.0944 + self.wind_direction/60) % 6.28
            size = screen_radius + 8
            x = screen_pos.x + math.cos(angle) * size * zoom_factor
            y = screen_pos.y + math.sin(angle) * size * zoom_factor
            
            cloud_radius = (3 + math.sin(pygame.time.get_ticks() / 200 + i) * 1) * zoom_factor
            cloud_surf = pygame.Surface((int(cloud_radius * 2), int(cloud_radius * 2)), pygame.SRCALPHA)
            pygame.draw.circle(cloud_surf, (200, 230, 255, 150), (cloud_radius, cloud_radius), cloud_radius)
            surface.blit(cloud_surf, (int(x - cloud_radius), int(y - cloud_radius)))
        
        # Draw magical cloud formations
        current_time = pygame.time.get_ticks() / 1000
        for cloud in self.clouds:
            # Calculate cloud position with vertical bobbing
            cloud_x = screen_pos.x + math.cos(math.radians(cloud['angle'])) * cloud['distance'] * zoom_factor
            cloud_y = screen_pos.y + math.sin(math.radians(cloud['angle'])) * cloud['distance'] * zoom_factor
            
            # Cloud size varies with air magic level
            cloud_size = cloud['size'] * zoom_factor * self.air_magic_level
            
            # Draw cloud with multiple overlapping circles
            alpha = int(200 * cloud['opacity'])
            for j in range(3):
                offset_x = random.uniform(-cloud_size * 0.3, cloud_size * 0.3)
                offset_y = random.uniform(-cloud_size * 0.3, cloud_size * 0.3)
                
                pygame.draw.circle(surface, (200, 230, 255, alpha), 
                                 (int(cloud_x + offset_x), int(cloud_y + offset_y)), 
                                 int(cloud_size))
        
        # Draw lightning effect between clouds
        if self.lightning_active and len(self.lightning_points) >= 2:
            # Draw with a glow
            for glow in range(2):
                width = 3 if glow == 0 else 1
                color = (180, 220, 255, 200) if glow == 0 else (220, 240, 255, 255)
                
                for i in range(len(self.lightning_points) - 1):
                    start = self.lightning_points[i]
                    end = self.lightning_points[i+1]
                    
                    if camera:
                        start_screen = camera.apply(start[0], start[1])
                        end_screen = camera.apply(end[0], end[1])
                        pygame.draw.line(surface, color, start_screen, end_screen, 
                                       max(1, int(width * camera.zoom)))
                    else:
                        pygame.draw.line(surface, color, start, end, width)
        
        # Draw tornado effect
        if self.tornado_active:
            tornado_radius = self.tornado_radius * self.air_magic_level * zoom_factor
            
            # Draw circular swirl effect
            swirl_layers = 5
            for layer in range(swirl_layers):
                layer_progress = layer / swirl_layers
                radius = tornado_radius * (1 - layer_progress * 0.7)
                alpha = int(150 * (1 - layer_progress))
                
                # Calculate rotation speed - faster toward the center
                rotation = self.tornado_timer * 180 * (1 + layer_progress)
                
                # Draw swirling pattern
                for arc in range(3):
                    arc_rotation = rotation + arc * 120
                    start_angle = math.radians(arc_rotation)
                    end_angle = math.radians(arc_rotation + 60)
                    
                    arc_surf = pygame.Surface((int(radius * 2), int(radius * 2)), pygame.SRCALPHA)
                    pygame.draw.arc(arc_surf, (180, 220, 255, alpha), 
                                  (0, 0, int(radius * 2), int(radius * 2)), 
                                  start_angle, end_angle, 
                                  max(1, int(3 * zoom_factor * (1 - layer_progress))))
                    
                    surface.blit(arc_surf, (int(screen_pos.x - radius), int(screen_pos.y - radius)))
            
            # Add wind lines showing air flow
            line_count = 8
            for i in range(line_count):
                angle = math.radians(i * (360 / line_count) + pygame.time.get_ticks() / 20)
                inner_x = screen_pos.x + math.cos(angle) * (tornado_radius * 0.3)
                inner_y = screen_pos.y + math.sin(angle) * (tornado_radius * 0.3)
                outer_x = screen_pos.x + math.cos(angle) * tornado_radius
                outer_y = screen_pos.y + math.sin(angle) * tornado_radius
                
                # Draw line with gradient alpha
                segments = 5
                for j in range(segments):
                    progress = j / segments
                    next_progress = (j+1) / segments
                    
                    start_x = inner_x + (outer_x - inner_x) * progress
                    start_y = inner_y + (outer_y - inner_y) * progress
                    end_x = inner_x + (outer_x - inner_x) * next_progress
                    end_y = inner_y + (outer_y - inner_y) * next_progress
                    
                    alpha = int(150 * (1 - progress))
                    pygame.draw.line(surface, (200, 230, 255, alpha),
                                   (int(start_x), int(start_y)),
                                   (int(end_x), int(end_y)),
                                   max(1, int(2 * zoom_factor * (1 - progress))))
        
        # Draw ambient wind lines
        wind_count = int(6 * self.air_magic_level)
        for i in range(wind_count):
            if random.random() < 0.1:
                # Random position around tower
                angle = random.uniform(0, math.pi * 2)
                distance = random.uniform(screen_radius, screen_radius * 3)
                x = screen_pos.x + math.cos(angle) * distance
                y = screen_pos.y + math.sin(angle) * distance
                
                # Line follows wind direction
                wind_angle = math.radians(self.wind_direction)
                length = random.uniform(10, 30) * zoom_factor
                end_x = x + math.cos(wind_angle) * length
                end_y = y + math.sin(wind_angle) * length
                
                # Draw wind line
                alpha = random.randint(30, 80)
                pygame.draw.line(surface, (220, 240, 255, alpha),
                               (int(x), int(y)),
                               (int(end_x), int(end_y)),
                               max(1, int(1 * zoom_factor)))
                               
        # Draw crackling energy at tower top
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