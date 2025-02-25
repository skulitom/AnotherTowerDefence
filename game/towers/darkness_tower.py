import pygame
import random
import math
from pygame.math import Vector2
from game.settings import tower_types
from game.towers.base_tower import BaseTower


class DarknessTower(BaseTower):
    """
    Darkness Tower - Channels shadow magic to weaken enemies
    
    Special ability: Curses enemies with shadow marks that increase damage taken
    from all towers. At higher levels, can drain enemy health and temporarily stun targets.
    """
    
    def initialize(self):
        """Initialize darkness tower specific properties"""
        # Shadow effects
        self.shadow_tendrils = []
        for _ in range(4 + self.level):
            self.shadow_tendrils.append({
                'angle': random.uniform(0, 360),
                'length': random.uniform(0.6, 1.0) * self.radius,
                'width': random.uniform(3, 5),
                'speed': random.uniform(5, 15) * (1 if random.random() > 0.5 else -1),
                'pulses': False,
                'pulse_speed': random.uniform(1, 3)
            })
        
        # Shadow orbs
        self.shadow_orbs = []
        orb_count = 2 + (self.level // 2)
        for _ in range(orb_count):
            self.shadow_orbs.append({
                'angle': random.uniform(0, 360),
                'distance': random.uniform(self.radius * 0.8, self.radius * 1.2),
                'size': random.uniform(3, 5),
                'speed': random.uniform(20, 40) * (1 if random.random() > 0.5 else -1),
                'pulse': 0,
                'pulse_speed': random.uniform(3, 5)
            })
        
        # Shadow mark effect
        self.mark_damage_multiplier = 1.2  # Enemies take more damage when marked
        self.mark_duration = 5.0  # Seconds
        self.mark_chance = 0.3  # Base chance to apply mark
        
        # Life drain effect
        self.drain_enabled = False
        self.drain_percent = 0  # % of damage returned as player health
        
        # Stun effect
        self.stun_enabled = False
        self.stun_duration = 0  # Seconds
        self.stun_chance = 0  # % chance to stun on hit
        
        # Shadow vortex for higher levels
        self.vortex_active = False
        self.vortex_cooldown = 0
        self.vortex_max_cooldown = 15.0
        self.vortex_duration = 0 
        self.vortex_max_duration = 5.0
        
        # Magic enhancement level
        self.darkness_magic_level = 1.0
        
    def upgrade_special(self, multiplier):
        """Enhance darkness tower special ability with upgrade"""
        super().upgrade_special(multiplier)
        
        # Visual and effect enhancements
        self.darkness_magic_level += 0.2
        
        # Mark effect enhancements
        self.mark_damage_multiplier = 1.2 + (0.1 * self.upgrades["special"])
        self.mark_duration = 5.0 + (1.0 * self.upgrades["special"])
        self.mark_chance = 0.3 + (0.1 * self.upgrades["special"])
        
        # Add more shadow tendrils
        if self.upgrades["special"] >= 2:
            for i in range(2):
                self.shadow_tendrils.append({
                    'angle': random.uniform(0, 360),
                    'length': random.uniform(0.8, 1.2) * self.radius,
                    'width': random.uniform(4, 6),
                    'speed': random.uniform(5, 15) * (1 if random.random() > 0.5 else -1),
                    'pulses': True,
                    'pulse_speed': random.uniform(1, 3)
                })
            
            # Add more shadow orbs
            self.shadow_orbs.append({
                'angle': random.uniform(0, 360),
                'distance': random.uniform(self.radius * 0.8, self.radius * 1.2),
                'size': random.uniform(4, 6),
                'speed': random.uniform(20, 40) * (1 if random.random() > 0.5 else -1),
                'pulse': 0,
                'pulse_speed': random.uniform(3, 5)
            })
        
        # Enable life drain at level 3
        if self.upgrades["special"] >= 3 and not self.drain_enabled:
            self.drain_enabled = True
            self.drain_percent = 5 + (5 * (self.upgrades["special"] - 3))
        elif self.drain_enabled:
            self.drain_percent = 5 + (5 * (self.upgrades["special"] - 3))
            
        # Enable stun at level 4
        if self.upgrades["special"] >= 4 and not self.stun_enabled:
            self.stun_enabled = True
            self.stun_duration = 0.5 + (0.25 * (self.upgrades["special"] - 4))
            self.stun_chance = 0.1 + (0.05 * (self.upgrades["special"] - 4))
        elif self.stun_enabled:
            self.stun_duration = 0.5 + (0.25 * (self.upgrades["special"] - 4))
            self.stun_chance = 0.1 + (0.05 * (self.upgrades["special"] - 4))
            
        # Enable shadow vortex at level 5
        if self.upgrades["special"] >= 5:
            self.vortex_max_cooldown = 15.0 - (self.upgrades["special"] - 5)
            self.vortex_max_duration = 5.0 + (self.upgrades["special"] - 5) * 0.5
            
    def is_preferred_target(self, enemy, distance, current_best, current_best_distance):
        """Darkness towers prioritize unmarked enemies or those with most health"""
        if not current_best:
            return True
            
        # Target unmarked enemies first
        enemy_marked = hasattr(enemy, 'shadow_marked') and enemy.shadow_marked
        current_marked = hasattr(current_best, 'shadow_marked') and current_best.shadow_marked
        
        if not enemy_marked and current_marked:
            return True
        elif enemy_marked and not current_marked:
            return False
            
        # Then target enemies with most health
        enemy_health_ratio = enemy.health / enemy.max_health if hasattr(enemy, 'health') and hasattr(enemy, 'max_health') else 0
        current_health_ratio = current_best.health / current_best.max_health if hasattr(current_best, 'health') and hasattr(current_best, 'max_health') else 0
        
        if enemy_health_ratio > current_health_ratio:
            return True
            
        # Consider distance as tie-breaker
        return distance < current_best_distance
        
    def update_tower(self, dt, enemies, projectiles, particles=None):
        """Update darkness tower state"""
        super().update_tower(dt, enemies, projectiles, particles)
        
        current_time = pygame.time.get_ticks() / 1000
        
        # Update shadow tendrils
        for tendril in self.shadow_tendrils:
            tendril['angle'] = (tendril['angle'] + tendril['speed'] * dt) % 360
            if tendril.get('pulses', False):
                tendril['length'] = (self.radius * 0.8) + (math.sin(current_time * tendril['pulse_speed']) * self.radius * 0.3)
        
        # Update shadow orbs
        for orb in self.shadow_orbs:
            orb['angle'] = (orb['angle'] + orb['speed'] * dt) % 360
            orb['pulse'] = (orb['pulse'] + orb['pulse_speed'] * dt) % (2 * math.pi)
        
        # Update shadow vortex
        if self.upgrades["special"] >= 5:
            if self.vortex_active:
                self.vortex_duration -= dt
                if self.vortex_duration <= 0:
                    self.vortex_active = False
                    self.vortex_cooldown = self.vortex_max_cooldown
                else:
                    # Apply vortex effects to enemies in range
                    for enemy in enemies:
                        if enemy.is_alive and (enemy.pos - self.pos).length() <= self.range:
                            # Pull enemies toward tower
                            direction = self.pos - enemy.pos
                            if direction.length() > 0:
                                direction.normalize_ip()
                                pull_strength = 50 * dt * self.darkness_magic_level
                                enemy.pos += direction * pull_strength
                            
                            # Apply shadow mark with higher chance during vortex
                            if not hasattr(enemy, 'shadow_marked') or not enemy.shadow_marked:
                                if random.random() < self.mark_chance * 2:
                                    enemy.shadow_marked = True
                                    enemy.shadow_mark_timer = self.mark_duration
                                    
                                    # Show mark effect
                                    if particles:
                                        for _ in range(5):
                                            angle = random.uniform(0, math.pi * 2)
                                            speed = random.uniform(10, 30)
                                            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
                                            
                                            particles.add_particle_params(
                                                Vector2(enemy.pos),
                                                (100, 0, 100),  # Purple
                                                velocity,
                                                random.uniform(2, 5),
                                                random.uniform(0.5, 1.0)
                                            )
            else:
                self.vortex_cooldown -= dt
                if self.vortex_cooldown <= 0:
                    self.vortex_active = True
                    self.vortex_duration = self.vortex_max_duration
                    
                    # Show vortex activation effect
                    if particles:
                        # Create dark portal effect
                        for i in range(30):
                            angle = random.uniform(0, math.pi * 2)
                            speed = random.uniform(10, 50) * self.darkness_magic_level
                            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
                            
                            # Dark purple to black gradient
                            darkness = random.randint(0, 100)
                            color = (darkness, 0, darkness)
                            
                            particles.add_particle_params(
                                Vector2(self.pos),
                                color,
                                velocity,
                                random.uniform(3, 8),
                                random.uniform(1.0, 2.0)
                            )
        
        # Create shadow particle effects
        if particles and random.random() < 0.1 * self.darkness_magic_level:
            # Create shadow smoke
            angle = random.uniform(0, math.pi * 2)
            distance = random.uniform(0, self.radius * 0.7)
            pos = Vector2(
                self.pos.x + math.cos(angle) * distance,
                self.pos.y + math.sin(angle) * distance
            )
            
            # Slow rising smoke
            rise_angle = -math.pi/2 + random.uniform(-0.3, 0.3)
            speed = random.uniform(5, 15)
            velocity = (math.cos(rise_angle) * speed, math.sin(rise_angle) * speed)
            
            # Dark purple color
            darkness = random.randint(20, 80)
            
            particles.add_particle_params(
                pos,
                (darkness, 0, darkness),
                velocity,
                random.uniform(3, 7) * self.darkness_magic_level,
                random.uniform(1.0, 2.0)
            )
    
    def fire_at_target(self, target, projectiles, particles=None):
        """Fire at target with enhanced darkness effects"""
        super().fire_at_target(target, projectiles, particles)
        
        # Add shadow burst effect when firing
        if particles:
            # Create shadow burst
            for _ in range(int(10 * self.darkness_magic_level)):
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(20, 50) * self.darkness_magic_level
                velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
                
                # Dark purple color
                darkness = random.randint(20, 100)
                
                particles.add_particle_params(
                    Vector2(self.pos),
                    (darkness, 0, darkness),
                    velocity,
                    random.uniform(2, 4),
                    random.uniform(0.3, 0.6)
                )
    
    def apply_projectile_effects(self, projectile):
        """Apply enhanced darkness effects to projectile"""
        super().apply_projectile_effects(projectile)
        
        # Shadow projectiles have trail effect
        projectile.shadow_trail = True
        
        # Add mark effect
        projectile.apply_mark = True
        projectile.mark_chance = self.mark_chance
        projectile.mark_duration = self.mark_duration
        projectile.mark_multiplier = self.mark_damage_multiplier
        
        # Add life drain effect
        if self.drain_enabled:
            projectile.life_drain = True
            projectile.drain_percent = self.drain_percent
        
        # Add stun effect
        if self.stun_enabled:
            projectile.can_stun = True
            projectile.stun_chance = self.stun_chance
            projectile.stun_duration = self.stun_duration
    
    def draw_effects(self, surface, screen_pos, screen_radius, camera=None, particles=None):
        """Draw darkness tower specific magical effects"""
        try:
            zoom_factor = camera.zoom if camera else 1
            current_time = pygame.time.get_ticks() / 1000
            
            # Draw shadow aura
            aura_pulse = 0.2 * math.sin(current_time * 1.5 + self.pulse_offset)
            aura_radius = screen_radius * (1.3 + aura_pulse) * self.darkness_magic_level
            
            if aura_radius > 0:
                # Draw multiple layers of aura
                for i in range(2):
                    alpha = 100 - (i * 40)
                    size = aura_radius * (1 + i * 0.2)
                    
                    # Check for valid size before creating surface
                    surf_size = max(1, int(size * 2))  # Ensure positive surface size
                    aura_surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
                    
                    # Create gradient of black/purple from center
                    pygame.draw.circle(aura_surf, (50, 0, 50, alpha), (size, size), size)
                    
                    # Blit aura to surface
                    surface.blit(aura_surf, (int(screen_pos.x - size), int(screen_pos.y - size)))
            
            # Draw shadow vortex if active
            if self.vortex_active:
                # Calculate vortex progress
                vortex_progress = self.vortex_duration / self.vortex_max_duration
                vortex_radius = self.range * zoom_factor * vortex_progress
                
                if vortex_radius > 0:
                    # Create vortex surface
                    vortex_size = int(vortex_radius * 2)
                    if vortex_size > 0:
                        vortex_surf = pygame.Surface((vortex_size, vortex_size), pygame.SRCALPHA)
                        
                        # Draw swirling vortex
                        for i in range(5):
                            alpha = 30 - (i * 5)
                            start_angle = (current_time * 50) % 360
                            end_angle = start_angle + 270
                            
                            pygame.draw.arc(vortex_surf, (80, 0, 80, alpha),
                                          pygame.Rect(i * 10, i * 10, vortex_size - i * 20, vortex_size - i * 20),
                                          math.radians(start_angle), math.radians(end_angle),
                                          max(1, int(3 * zoom_factor)))
                        
                        # Add swirl lines
                        for i in range(8):
                            angle = (i / 8) * math.pi * 2 + current_time
                            inner_x = vortex_radius + math.cos(angle) * (vortex_radius * 0.2)
                            inner_y = vortex_radius + math.sin(angle) * (vortex_radius * 0.2)
                            outer_x = vortex_radius + math.cos(angle) * vortex_radius * 0.9
                            outer_y = vortex_radius + math.sin(angle) * vortex_radius * 0.9
                            
                            pygame.draw.line(vortex_surf, (100, 0, 100, 40),
                                           (inner_x, inner_y),
                                           (outer_x, outer_y),
                                           max(1, int(2 * zoom_factor)))
                        
                        # Blit vortex to screen
                        surface.blit(vortex_surf, (int(screen_pos.x - vortex_radius), int(screen_pos.y - vortex_radius)))
            
            # Draw vortex cooldown indicator for player
            elif self.upgrades["special"] >= 5:
                cooldown_percent = 1 - (self.vortex_cooldown / self.vortex_max_cooldown)
                indicator_radius = screen_radius * 0.7
                
                if indicator_radius > 0:
                    # Draw arc showing cooldown progress
                    pygame.draw.arc(surface, (150, 0, 150, 150),
                                  pygame.Rect(
                                      int(screen_pos.x - indicator_radius),
                                      int(screen_pos.y - indicator_radius),
                                      int(indicator_radius * 2),
                                      int(indicator_radius * 2)
                                  ),
                                  0, math.pi * 2 * cooldown_percent,
                                  max(1, int(2 * zoom_factor)))
            
            # Draw shadow tendrils
            for tendril in self.shadow_tendrils:
                tendril_angle = math.radians(tendril['angle'])
                tendril_length = tendril['length'] * zoom_factor
                tendril_width = max(1, int(tendril['width'] * zoom_factor))
                
                # Calculate end point
                end_x = screen_pos.x + math.cos(tendril_angle) * tendril_length
                end_y = screen_pos.y + math.sin(tendril_angle) * tendril_length
                
                # Draw wavy tendril
                points = []
                segments = 10
                
                for i in range(segments + 1):
                    segment_percent = i / segments
                    segment_length = tendril_length * segment_percent
                    
                    # Add waviness
                    wave_angle = tendril_angle
                    if i > 0:  # Don't wave the base of the tendril
                        wave_factor = segment_percent * 0.3  # Increase wave at tip
                        wave_offset = math.sin(current_time * 2 + tendril['angle'] + i) * wave_factor
                        wave_angle = tendril_angle + wave_offset
                    
                    point_x = screen_pos.x + math.cos(wave_angle) * segment_length
                    point_y = screen_pos.y + math.sin(wave_angle) * segment_length
                    
                    points.append((point_x, point_y))
                
                # Draw tendril as a series of fading segments
                for i in range(len(points) - 1):
                    segment_alpha = 150 - (i * 10)  # Fade toward the end
                    pygame.draw.line(surface, (60, 0, 60, max(0, segment_alpha)),
                                   points[i], points[i+1], 
                                   tendril_width)
                
                # Add a particle effect at the end occasionally
                if random.random() < 0.05 * self.darkness_magic_level and particles:
                    particles.add_particle_params(
                        Vector2(end_x, end_y),
                        (80, 0, 80),
                        (random.uniform(-20, 20), random.uniform(-20, 20)),
                        random.uniform(2, 4),
                        random.uniform(0.3, 0.8)
                    )
            
            # Draw orbiting shadow orbs
            for orb in self.shadow_orbs:
                orb_angle = math.radians(orb['angle'])
                orb_distance = orb['distance'] * zoom_factor
                
                # Calculate position with pulsing distance
                pulse_offset = math.sin(orb['pulse']) * screen_radius * 0.2
                orb_x = screen_pos.x + math.cos(orb_angle) * (orb_distance + pulse_offset)
                orb_y = screen_pos.y + math.sin(orb_angle) * (orb_distance + pulse_offset)
                
                # Draw orb with pulsing size
                orb_size = max(1, int(orb['size'] * zoom_factor * (1 + math.sin(orb['pulse']) * 0.3)))
                
                # Create orb gradient
                if orb_size > 0:
                    orb_surf = pygame.Surface((orb_size * 2, orb_size * 2), pygame.SRCALPHA)
                    
                    # Draw core
                    pygame.draw.circle(orb_surf, (150, 0, 150, 200), (orb_size, orb_size), orb_size)
                    
                    # Draw outer glow
                    glow_size = int(orb_size * 1.5)
                    glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surf, (100, 0, 100, 50), (glow_size, glow_size), glow_size)
                    
                    # Position and blit orb and glow
                    surface.blit(glow_surf, (int(orb_x - glow_size), int(orb_y - glow_size)))
                    surface.blit(orb_surf, (int(orb_x - orb_size), int(orb_y - orb_size)))
                
                # Occasionally emit small shadow particles
                if random.random() < 0.1 * self.darkness_magic_level and particles:
                    particles.add_particle_params(
                        Vector2(orb_x, orb_y),
                        (100, 0, 100),
                        (random.uniform(-30, 30), random.uniform(-30, 30)),
                        random.uniform(1, 3),
                        random.uniform(0.2, 0.5)
                    )
        except Exception as e:
            # Silently handle exceptions to prevent game crashes
            pass 