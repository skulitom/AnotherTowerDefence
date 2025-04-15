import pygame
import random
import math
from pygame.math import Vector2
from game.settings import tower_types
from game.towers.base_tower import BaseTower


class FireTower(BaseTower):
    """
    Fire Tower - Conjures arcane flames that burn enemies over time
    
    Special ability: Ignites enemies with magical fire that continues to burn
    them over time. Higher levels increase burn chance and damage.
    """
    
    def initialize(self):
        """Initialize fire tower specific properties"""
        # Magical runes and symbols
        self.rune_count = random.randint(3, 5)
        self.rune_angles = [random.uniform(0, 360) for _ in range(self.rune_count)]
        self.rune_sizes = [random.uniform(3, 5) for _ in range(self.rune_count)]
        self.rune_colors = [(255, 150, 0), (255, 100, 0), (255, 50, 0)]
        
        # Flame effects
        self.flame_intensity = 1.0
        self.ember_timer = 0
        self.ember_particles = []  # Tracks ember particles for tower-specific animation
        
        # Enhanced fire glow
        self.glow_pulse_speeds = [random.uniform(0.8, 1.2) for _ in range(3)]
        self.glow_sizes = [random.uniform(0.9, 1.1) for _ in range(3)]
        
        # Upgrade level visualization
        self.flame_height_multiplier = 1.0
        
    def upgrade_special(self, multiplier):
        """Enhance fire tower special ability with upgrade"""
        super().upgrade_special(multiplier)
        
        # Visual enhancements on upgrade
        self.flame_intensity += 0.2
        self.flame_height_multiplier += 0.15
        
        # Add more runes at higher levels
        if self.level % 2 == 0 and self.rune_count < 8:
            self.rune_count += 1
            self.rune_angles.append(random.uniform(0, 360))
            self.rune_sizes.append(random.uniform(3, 5))
    
    def is_preferred_target(self, enemy, distance, current_best, current_best_distance):
        """Fire towers target enemies with highest health"""
        if not current_best:
            return True
        return enemy.health > current_best.health
        
    def update_tower(self, dt, enemies, projectiles, particles=None):
        """Update fire tower state"""
        super().update_tower(dt, enemies, projectiles, particles)
        
        # Update ember timer for particle effects
        self.ember_timer += dt
        if self.ember_timer > 0.1 * (1 / self.flame_intensity):
            self.ember_timer = 0
            if particles:
                # Generate ember particles that float up from the tower
                angle = random.uniform(0, math.pi * 2)
                distance = random.uniform(0, self.radius * 0.8)
                x = self.pos.x + math.cos(angle) * distance
                y = self.pos.y + math.sin(angle) * distance
                
                # Ember rises up with slightly random trajectory
                velocity = (random.uniform(-10, 10), random.uniform(-40, -20))
                
                # Add ember particle
                particles.add_particle_params(
                    Vector2(x, y),
                    (255, random.randint(50, 200), 0),
                    velocity,
                    random.uniform(1, 3) * self.flame_intensity,
                    random.uniform(0.5, 1.0)
                )
                
                # Every few embers, add a smoke particle too
                if random.random() < 0.3:
                    smoke_vel = (random.uniform(-5, 5), random.uniform(-30, -15))
                    particles.add_particle_params(
                        Vector2(x, y),
                        (100, 100, 100),
                        smoke_vel,
                        random.uniform(2, 4),
                        random.uniform(1.0, 2.0)
                    )
    
    def fire_at_target(self, target, projectiles, particles=None):
        """Fire at target with enhanced magical effects"""
        super().fire_at_target(target, projectiles, particles)
        
        # Add additional fire burst effect
        if particles:
            # Create a circle of fire particles around the tower when firing
            for _ in range(int(8 * self.flame_intensity)):
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(10, 30) * self.flame_intensity
                velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
                
                # Add fire burst particle
                particles.add_particle_params(
                    Vector2(self.pos),
                    (255, random.randint(50, 150), 0),
                    velocity,
                    random.uniform(3, 6) * self.flame_intensity,
                    random.uniform(0.3, 0.6)
                )
    
    def apply_projectile_effects(self, projectile):
        """Apply enhanced fire effects to projectile"""
        super().apply_projectile_effects(projectile)
        
        # Magical fire projectiles have a chance to cause a small explosion on impact
        if random.random() < 0.2 * self.flame_intensity:
            projectile.additional_effects = {
                "explosion": {
                    "radius": 30 + (self.level * 5),
                    "damage": self.current_damage * 0.3,
                    "color": (255, 100, 0)
                }
            }
    
    def draw_effects(self, surface, screen_pos, screen_radius, camera=None):
        """Draw fire tower specific magical effects"""
        zoom_factor = camera.zoom if camera else 1
        
        # Draw multiple layers of pulsing fire glow
        for i in range(3):
            pulse_time = pygame.time.get_ticks() / (200 / self.glow_pulse_speeds[i])
            glow_size = (screen_radius + 2 + math.sin(pulse_time + self.pulse_offset) * 3) 
            glow_size *= self.glow_sizes[i] * self.flame_intensity
            
            glow_surf = pygame.Surface((int(glow_size * 2), int(glow_size * 2)), pygame.SRCALPHA)
            alpha = max(30, min(120, int(70 * self.flame_intensity)))
            color = (255, 100 - (i * 20), 0, alpha - (i * 20))
            
            pygame.draw.circle(glow_surf, color, (glow_size, glow_size), glow_size)
            surface.blit(glow_surf, (int(screen_pos.x - glow_size), int(screen_pos.y - glow_size)))
        
        # Draw arcane runes orbiting the tower
        rune_radius = screen_radius * 1.5
        for i in range(self.rune_count):
            rune_angle = self.rune_angles[i] + (pygame.time.get_ticks() / 1000 * (30 + i * 5)) % 360
            rune_x = screen_pos.x + math.cos(math.radians(rune_angle)) * rune_radius
            rune_y = screen_pos.y + math.sin(math.radians(rune_angle)) * rune_radius
            
            # Draw magical rune (simple shapes for now)
            rune_size = self.rune_sizes[i] * zoom_factor
            rune_color = self.rune_colors[i % len(self.rune_colors)]
            
            # Draw a magical rune (pentagon)
            points = []
            for j in range(5):
                angle = math.radians(j * 72 + pygame.time.get_ticks() / 50)
                px = rune_x + math.cos(angle) * rune_size * 2
                py = rune_y + math.sin(angle) * rune_size * 2
                points.append((px, py))
                
            # Draw rune with glow
            for glow in range(2):
                glow_alpha = 150 if glow == 0 else 50
                glow_width = 0 if glow == 0 else 2
                pygame.draw.polygon(surface, (*rune_color, glow_alpha), points, glow_width)
        
        # Draw flame crown above tower (higher with upgrades)
        flame_y_offset = -screen_radius * 0.8
        flame_count = 5 + self.level
        flame_width = screen_radius * 0.4
        flame_height = screen_radius * 0.8 * self.flame_height_multiplier
        
        for i in range(flame_count):
            # Calculate flame position in a semicircle above tower
            angle = i * (180 / (flame_count - 1)) - 90  # -90 to 90 degrees
            base_flame_x = screen_pos.x + math.cos(math.radians(angle)) * flame_width
            flame_base_y = screen_pos.y + flame_y_offset
            
            # Draw flame with dynamic flickering
            current_time_ms = pygame.time.get_ticks()
            flicker_speed_1 = 0.008 + (i * 0.0005) # Vary speed per flame
            flicker_speed_2 = 0.011 + (i * 0.0003)
            
            height_variation = flame_height * (0.9 + 0.3 * math.sin(current_time_ms * flicker_speed_1 + i))
            width_variation = flame_width * (0.8 + 0.4 * math.sin(current_time_ms * flicker_speed_2 + i + 1.5)) # Use different speed/offset
            horizontal_flicker = math.sin(current_time_ms * 0.006 + i * 0.5) * flame_width * 0.15 # Subtle side-to-side motion
            
            flame_x = base_flame_x + horizontal_flicker
            
            # Create flame points
            flame_points = [
                (flame_x, flame_base_y),  # Base of flame
                (flame_x - width_variation * 0.3, flame_base_y - height_variation * 0.5),  # Left point
                (flame_x, flame_base_y - height_variation),  # Top point
                (flame_x + width_variation * 0.3, flame_base_y - height_variation * 0.5)   # Right point
            ]
            
            # Draw flame with gradient from yellow to red
            for j in range(3):
                alpha = 180 - j * 40
                size_reduction = j * 0.15
                reduced_points = []
                for x, y in flame_points:
                    # Move points toward flame center for smaller flames
                    reduced_x = flame_x + (x - flame_x) * (1 - size_reduction)
                    reduced_y = flame_base_y + (y - flame_base_y) * (1 - size_reduction)
                    reduced_points.append((reduced_x, reduced_y))
                
                # Color gradient from yellow (outer) to red (inner)
                r = 255
                g = max(0, min(255, 200 - j * 80))
                b = 0
                
                pygame.draw.polygon(surface, (r, g, b, alpha), reduced_points)
                
        # Draw heat distortion effect
        if random.random() < 0.1 * self.flame_intensity:
            distortion_height = screen_radius * 2.5 * self.flame_height_multiplier
            distortion_width = screen_radius * 1.5
            
            for i in range(int(5 * self.flame_intensity)):
                wave_x = screen_pos.x + random.uniform(-distortion_width, distortion_width)
                wave_y = screen_pos.y + flame_y_offset - random.uniform(0, distortion_height)
                wave_size = random.uniform(2, 5) * zoom_factor
                
                pygame.draw.circle(surface, (255, 255, 255, 20), (int(wave_x), int(wave_y)), int(wave_size)) 