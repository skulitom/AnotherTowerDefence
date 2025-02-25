import pygame
import random
import math
from pygame.math import Vector2
from game.settings import tower_types
from game.towers.base_tower import BaseTower


class EarthTower(BaseTower):
    """
    Earth Tower - Wields the elemental power of stone and crystal
    
    Special ability: Creates crystal formations that damage enemies
    and can erupt from the ground at higher levels.
    """
    
    def initialize(self):
        """Initialize earth tower specific properties"""
        # Crystal formations
        self.crystal_count = 3 + random.randint(0, 2)
        self.crystals = []
        for _ in range(self.crystal_count):
            self.crystals.append({
                'angle': random.uniform(0, 360),
                'distance': random.uniform(self.radius * 0.6, self.radius * 1.2),
                'height': random.uniform(5, 12),
                'color': (
                    random.randint(30, 70),
                    random.randint(160, 200), 
                    random.randint(120, 150)
                ),
                'pulse_offset': random.uniform(0, math.pi * 2),
                'points': random.randint(3, 5)
            })
        
        # Ground effects
        self.ground_cracks = []
        crack_count = random.randint(3, 5)
        for _ in range(crack_count):
            angle = random.uniform(0, math.pi * 2)
            length = random.uniform(self.radius * 1.2, self.radius * 2.5)
            self.ground_cracks.append({
                'start_angle': angle,
                'length': length,
                'width': random.uniform(2, 4),
                'segments': random.randint(3, 6),
                'jitter': random.uniform(0.2, 0.4)
            })
        
        # Crystal eruption
        self.eruption_active = False
        self.eruption_timer = 0
        self.eruption_cooldown = 8.0
        self.eruption_duration = 0
        self.eruption_radius = 0
        self.eruption_crystals = []
        
        # Floating stone circle
        self.stone_circle = {
            'angle': 0,
            'stones': [],
            'radius': self.radius * 1.3
        }
        
        stone_count = 5 + self.level
        for i in range(stone_count):
            angle = (i / stone_count) * math.pi * 2
            self.stone_circle['stones'].append({
                'angle': angle,
                'size': random.uniform(3, 6),
                'height_offset': random.uniform(-5, 5),
                'orbit_speed': random.uniform(0.3, 0.6) * (1 if random.random() > 0.2 else -1)
            })
        
        # Magic enhancement level
        self.earth_magic_level = 1.0
        
    def upgrade_special(self, multiplier):
        """Enhance earth tower special ability with upgrade"""
        super().upgrade_special(multiplier)
        
        # Visual and effect enhancements
        self.earth_magic_level += 0.2
        
        # Enhanced crystal eruption at higher levels
        if self.upgrades["special"] >= 1:
            self.eruption_duration = 3.0 + self.upgrades["special"] * 0.5
            self.eruption_cooldown = max(3.0, 8.0 - self.upgrades["special"])
            self.eruption_radius = 40 + self.upgrades["special"] * 10
            
            # Add more crystals around the tower with upgrades
            if self.upgrades["special"] % 2 == 0 and self.crystal_count < 8:
                for _ in range(2):
                    self.crystals.append({
                        'angle': random.uniform(0, 360),
                        'distance': random.uniform(self.radius * 0.6, self.radius * 1.2),
                        'height': random.uniform(5, 12) * self.earth_magic_level,
                        'color': (
                            random.randint(30, 70),
                            random.randint(160, 200), 
                            random.randint(120, 150)
                        ),
                        'pulse_offset': random.uniform(0, math.pi * 2),
                        'points': random.randint(3, 5)
                    })
                    self.crystal_count += 1
                    
        # Add more stones to orbit at higher levels
        if self.level % 2 == 0:
            stone_count = len(self.stone_circle['stones'])
            for i in range(2):
                angle = random.uniform(0, math.pi * 2)
                self.stone_circle['stones'].append({
                    'angle': angle,
                    'size': random.uniform(3, 6) * self.earth_magic_level,
                    'height_offset': random.uniform(-5, 5),
                    'orbit_speed': random.uniform(0.3, 0.6) * (1 if random.random() > 0.2 else -1)
                })
        
    def is_preferred_target(self, enemy, distance, current_best, current_best_distance):
        """Earth towers target enemies with the highest health"""
        if not current_best:
            return True
        return enemy.health > current_best.health
        
    def update_tower(self, dt, enemies, projectiles, particles=None):
        """Update earth tower state"""
        super().update_tower(dt, enemies, projectiles, particles)
        
        # Update floating stone circle
        for stone in self.stone_circle['stones']:
            stone['angle'] = (stone['angle'] + stone['orbit_speed'] * dt) % (math.pi * 2)
        
        # Create dust particles occasionally
        if particles and random.random() < 0.05 * self.earth_magic_level:
            # Random position around tower
            angle = random.uniform(0, math.pi * 2)
            distance = random.uniform(self.radius * 0.8, self.radius * 1.5)
            x = self.pos.x + math.cos(angle) * distance
            y = self.pos.y + math.sin(angle) * distance
            
            # Gentle rising dust
            velocity = (random.uniform(-5, 5), random.uniform(-20, -10))
            
            # Earth-tone color
            r = random.randint(100, 140)
            g = random.randint(80, 110)
            b = random.randint(60, 90)
            
            particles.add_particle_params(
                Vector2(x, y),
                (r, g, b),
                velocity,
                random.uniform(2, 4),
                random.uniform(0.5, 1.2)
            )
        
        # Update crystal eruption
        if self.eruption_active:
            self.eruption_timer += dt
            if self.eruption_timer <= self.eruption_duration:
                # Apply eruption effect to enemies
                eruption_radius = self.eruption_radius * self.earth_magic_level
                
                # Find enemies in eruption range
                for enemy in enemies:
                    distance = (enemy.pos - self.pos).length()
                    if distance < eruption_radius:
                        # Calculate damage over time
                        damage = 0.5 * self.damage * dt
                        enemy.take_damage(damage)
                        
                        # Slow effect from crystals
                        enemy.apply_effect("slow", 0.3, 0.5)
                        
                        # Generate crystal hit particles
                        if particles and random.random() < 0.1:
                            particles.add_particle_params(
                                Vector2(enemy.pos),
                                (random.randint(30, 70), random.randint(160, 200), random.randint(120, 150)),
                                (random.uniform(-30, 30), random.uniform(-30, 30)),
                                random.uniform(3, 5),
                                random.uniform(0.2, 0.4)
                            )
                
                # Generate eruption crystals
                if random.random() < 0.1 * self.earth_magic_level:
                    angle = random.uniform(0, math.pi * 2)
                    distance = random.uniform(0, eruption_radius)
                    
                    self.eruption_crystals.append({
                        'x': self.pos.x + math.cos(angle) * distance,
                        'y': self.pos.y + math.sin(angle) * distance,
                        'height': random.uniform(10, 20) * self.earth_magic_level,
                        'growth_time': random.uniform(0.5, 1.0),
                        'current_time': 0,
                        'duration': random.uniform(1.0, 2.0),
                        'color': (
                            random.randint(30, 70),
                            random.randint(160, 200), 
                            random.randint(120, 150)
                        ),
                        'points': random.randint(3, 5)
                    })
                    
                # Update existing eruption crystals
                for crystal in list(self.eruption_crystals):
                    crystal['current_time'] += dt
                    
                    if crystal['current_time'] > crystal['growth_time'] + crystal['duration']:
                        self.eruption_crystals.remove(crystal)
            else:
                self.eruption_active = False
                self.eruption_timer = 0
                self.eruption_crystals.clear()
        elif self.upgrades["special"] >= 1:
            # Automatically activate eruption when cooldown is reached
            self.eruption_timer += dt
            if self.eruption_timer >= self.eruption_cooldown:
                self.eruption_active = True
                self.eruption_timer = 0
    
    def fire_at_target(self, target, projectiles, particles=None):
        """Fire at target with enhanced earth magic effects"""
        super().fire_at_target(target, projectiles, particles)
        
        # Add stone burst effect when firing
        if particles:
            burst_count = int(4 * self.earth_magic_level)
            for _ in range(burst_count):
                # Direction toward target with wide spread
                target_angle = math.atan2(target.pos.y - self.pos.y, target.pos.x - self.pos.x)
                angle_spread = random.uniform(-1.0, 1.0)
                angle = target_angle + angle_spread
                
                speed = random.uniform(30, 60) * self.earth_magic_level
                velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
                
                # Earth-tone colors
                r = random.randint(100, 140)
                g = random.randint(80, 110)
                b = random.randint(60, 90)
                
                particles.add_particle_params(
                    Vector2(self.pos),
                    (r, g, b),
                    velocity,
                    random.uniform(3, 5),
                    random.uniform(0.3, 0.5)
                )
    
    def apply_projectile_effects(self, projectile):
        """Apply enhanced earth effects to projectile"""
        super().apply_projectile_effects(projectile)
        
        # Magical earth projectiles can stun enemies at higher levels
        if self.upgrades["special"] >= 3 and random.random() < 0.3:
            projectile.effect["stun"] = 0.5 + (0.2 * (self.upgrades["special"] - 3))
        
    def draw_effects(self, surface, screen_pos, screen_radius, camera=None):
        """Draw earth tower specific magical effects"""
        zoom_factor = camera.zoom if camera else 1
        
        # Draw ground cracks
        for crack in self.ground_cracks:
            start_angle = crack['start_angle']
            current_pos = Vector2(screen_pos)
            
            # Create jagged crack effect
            prev_pos = current_pos.copy()
            for segment in range(crack['segments']):
                segment_progress = (segment + 1) / crack['segments']
                segment_length = crack['length'] * segment_progress
                
                # Add jitter to the crack direction
                jitter_angle = start_angle + random.uniform(-crack['jitter'], crack['jitter'])
                
                # Calculate next position
                next_x = screen_pos.x + math.cos(jitter_angle) * segment_length * zoom_factor
                next_y = screen_pos.y + math.sin(jitter_angle) * segment_length * zoom_factor
                
                # Determine alpha based on distance from tower
                distance_factor = segment_progress
                alpha = int(150 * (1 - distance_factor))
                
                # Draw crack segment
                width = max(1, int(crack['width'] * (1 - distance_factor * 0.7) * zoom_factor))
                pygame.draw.line(surface, (60, 170, 120, alpha),
                               (int(prev_pos.x), int(prev_pos.y)),
                               (int(next_x), int(next_y)), width)
                
                # Occasionally add small crystals along the crack
                if random.random() < 0.3 and segment > 0:
                    crystal_size = random.uniform(2, 4) * zoom_factor
                    crystal_color = (
                        random.randint(30, 70),
                        random.randint(160, 200),
                        random.randint(120, 150),
                        alpha
                    )
                    
                    # Draw small crystal
                    pygame.draw.circle(surface, crystal_color,
                                     (int(next_x), int(next_y)), 
                                     int(crystal_size))
                
                prev_pos = Vector2(next_x, next_y)
        
        # Draw crystals around tower
        current_time = pygame.time.get_ticks() / 1000
        for crystal in self.crystals:
            # Calculate crystal position
            crystal_x = screen_pos.x + math.cos(math.radians(crystal['angle'])) * crystal['distance'] * zoom_factor
            crystal_y = screen_pos.y + math.sin(math.radians(crystal['angle'])) * crystal['distance'] * zoom_factor
            
            # Crystal height varies with magic level and pulsates slowly
            pulse = 0.2 * math.sin(current_time * 2 + crystal['pulse_offset'])
            crystal_height = crystal['height'] * (1 + pulse) * zoom_factor * self.earth_magic_level
            
            # Draw crystal with glowing effect
            points = []
            for i in range(crystal['points']):
                angle = (i / crystal['points']) * math.pi * 2
                
                # Crystal shape gets more elaborate at higher levels
                if i % 2 == 0:
                    point_length = crystal_height * 0.8  # Shorter points
                else:
                    point_length = crystal_height
                
                point_x = crystal_x + math.cos(angle) * point_length
                point_y = crystal_y + math.sin(angle) * point_length - (crystal_height * 0.5)  # Raise point
                
                points.append((point_x, point_y))
            
            # Draw crystal shape
            if len(points) >= 3:
                # Underlying glow
                glow_surface = pygame.Surface((int(crystal_height * 3), int(crystal_height * 3)), pygame.SRCALPHA)
                glow_center = (glow_surface.get_width() // 2, glow_surface.get_height() // 2)
                
                # Use crystal color but with alpha for glow
                glow_color = (crystal['color'][0], crystal['color'][1], crystal['color'][2], 100)
                pygame.draw.circle(glow_surface, glow_color, glow_center, int(crystal_height * 1.2))
                
                # Blit glow
                glow_pos = (int(crystal_x - glow_center[0]), int(crystal_y - glow_center[1]))
                surface.blit(glow_surface, glow_pos)
                
                # Draw crystal
                pygame.draw.polygon(surface, crystal['color'], points)
                
                # Draw inner highlight
                if len(points) >= 3:
                    # Scale points toward center for highlight
                    center_x = sum(p[0] for p in points) / len(points)
                    center_y = sum(p[1] for p in points) / len(points)
                    
                    highlight_points = []
                    for px, py in points:
                        # Move 30% toward center
                        highlight_x = px * 0.7 + center_x * 0.3
                        highlight_y = py * 0.7 + center_y * 0.3
                        highlight_points.append((highlight_x, highlight_y))
                    
                    # Brighter version of the crystal color
                    highlight_color = (
                        min(255, crystal['color'][0] + 50),
                        min(255, crystal['color'][1] + 50),
                        min(255, crystal['color'][2] + 50)
                    )
                    
                    pygame.draw.polygon(surface, highlight_color, highlight_points)
        
        # Draw eruption crystals
        for crystal in self.eruption_crystals:
            if camera:
                crystal_pos = camera.apply(crystal['x'], crystal['y'])
            else:
                crystal_pos = (crystal['x'], crystal['y'])
                
            # Calculate growth progress
            if crystal['current_time'] < crystal['growth_time']:
                # Growing phase
                growth_progress = crystal['current_time'] / crystal['growth_time']
            else:
                # Fully grown or shrinking
                remaining_time = crystal['growth_time'] + crystal['duration'] - crystal['current_time']
                if remaining_time < 0.5:  # Last 0.5 seconds for shrinking
                    growth_progress = remaining_time / 0.5
                else:
                    growth_progress = 1.0
                    
            # Adjust crystal height based on growth progress
            height = crystal['height'] * growth_progress * zoom_factor
            
            # Draw crystal with same technique as permanent crystals
            points = []
            for i in range(crystal['points']):
                angle = (i / crystal['points']) * math.pi * 2
                
                if i % 2 == 0:
                    point_length = height * 0.8
                else:
                    point_length = height
                
                point_x = crystal_pos[0] + math.cos(angle) * point_length
                point_y = crystal_pos[1] + math.sin(angle) * point_length - (height * 0.5)
                
                points.append((point_x, point_y))
                
            # Draw crystal shape if it has enough points
            if len(points) >= 3:
                pygame.draw.polygon(surface, crystal['color'], points)
        
        # Draw floating stone circle
        for stone in self.stone_circle['stones']:
            # Calculate 3D-like position with height offset
            angle = stone['angle']
            radius = self.stone_circle['radius'] * zoom_factor
            
            # Basic position on the circle
            stone_x = screen_pos.x + math.cos(angle) * radius
            stone_y = screen_pos.y + math.sin(angle) * radius
            
            # Apply height offset for 3D effect (higher stones appear further back)
            height_factor = math.sin(angle) * 0.2  # Stones in back are higher
            height_offset = (stone['height_offset'] + height_factor * 10) * zoom_factor
            stone_y -= height_offset
            
            # Size varies with height to simulate perspective
            size = stone['size'] * zoom_factor * (1 - height_factor * 0.3) * self.earth_magic_level
            
            # Draw with shadow for depth
            shadow_offset = int(2 * zoom_factor)
            
            # Shadow first
            pygame.draw.circle(surface, (50, 50, 50, 100),
                             (int(stone_x + shadow_offset), int(stone_y + shadow_offset)),
                             int(size))
            
            # Stone with earth tone color that varies with position in orbit
            # Stones in the back are darker
            brightness = 0.7 + 0.3 * (1 - math.sin(angle) * 0.5)
            stone_color = (
                int(110 * brightness),
                int(90 * brightness),
                int(70 * brightness)
            )
            
            pygame.draw.circle(surface, stone_color, (int(stone_x), int(stone_y)), int(size))
            
            # Add highlight to give stones dimension
            highlight_pos = (
                int(stone_x - size * 0.3),
                int(stone_y - size * 0.3)
            )
            highlight_size = max(1, int(size * 0.4))
            highlight_color = (
                min(255, int(stone_color[0] * 1.6)),
                min(255, int(stone_color[1] * 1.6)),
                min(255, int(stone_color[2] * 1.6))
            )
            
            pygame.draw.circle(surface, highlight_color, highlight_pos, highlight_size)
        
        # Draw magical runes on the ground
        if self.level >= 2:
            rune_count = 1 + self.level // 2
            for i in range(rune_count):
                angle = (i / rune_count) * math.pi * 2
                distance = screen_radius * 0.8 * zoom_factor
                
                rune_x = screen_pos.x + math.cos(angle) * distance
                rune_y = screen_pos.y + math.sin(angle) * distance
                
                # Rune size
                rune_size = (5 + self.level) * zoom_factor
                
                # Draw rune circle
                glow_alpha = int(180 + 75 * math.sin(current_time * 2 + i))
                pygame.draw.circle(surface, (60, 180, 120, glow_alpha),
                                 (int(rune_x), int(rune_y)),
                                 int(rune_size))
                
                # Draw rune symbol - simple shapes for now
                symbol_color = (30, 80, 60)
                
                # Different symbols based on position
                if i % 3 == 0:
                    # Triangle
                    triangle_size = rune_size * 0.6
                    points = []
                    for j in range(3):
                        point_angle = angle + (j / 3) * math.pi * 2
                        point_x = rune_x + math.cos(point_angle) * triangle_size
                        point_y = rune_y + math.sin(point_angle) * triangle_size
                        points.append((point_x, point_y))
                    
                    pygame.draw.polygon(surface, symbol_color, points, max(1, int(zoom_factor)))
                    
                elif i % 3 == 1:
                    # Square
                    square_size = rune_size * 0.6
                    pygame.draw.rect(surface, symbol_color,
                                   (int(rune_x - square_size/2), int(rune_y - square_size/2),
                                    int(square_size), int(square_size)),
                                   max(1, int(zoom_factor)))
                    
                else:
                    # Cross
                    line_length = rune_size * 0.7
                    pygame.draw.line(surface, symbol_color,
                                   (int(rune_x - line_length), int(rune_y)),
                                   (int(rune_x + line_length), int(rune_y)),
                                   max(1, int(zoom_factor)))
                    
                    pygame.draw.line(surface, symbol_color,
                                   (int(rune_x), int(rune_y - line_length)),
                                   (int(rune_x), int(rune_y + line_length)),
                                   max(1, int(zoom_factor))) 