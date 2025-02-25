import pygame
import random
import math
from pygame.math import Vector2
from game.settings import tower_types
from game.towers.base_tower import BaseTower


class LifeTower(BaseTower):
    """
    Life Tower - Channels nature's vitality to empower allies
    
    Special ability: Buffs nearby towers, increasing their damage and attack speed.
    At higher levels, can periodically heal player's lives and generate gold.
    """
    
    def initialize(self):
        """Initialize life tower specific properties"""
        # Nature growth effects
        self.leaf_particles = []
        self.growth_timer = 0
        self.growth_interval = 0.2
        
        # Floating flowers
        self.flowers = []
        flower_count = 3 + self.level
        for _ in range(flower_count):
            self.flowers.append({
                'angle': random.uniform(0, 360),
                'distance': random.uniform(self.radius * 1.0, self.radius * 1.5),
                'size': random.uniform(3, 5),
                'speed': random.uniform(10, 20) * (1 if random.random() > 0.5 else -1),
                'color': random.choice([(255, 105, 180), (255, 150, 200), (255, 182, 193)])
            })
        
        # Nature vines
        self.vine_count = 4 + self.level
        self.vine_length = self.radius * 1.2
        self.vine_growth = 0.8  # How "grown" the vines are (increases with level)
        self.vine_speeds = [random.uniform(0.5, 1.0) for _ in range(self.vine_count)]
        
        # Buff effect properties
        self.buff_range = tower_types["Life"].get("buff_range", 200)
        self.buff_damage = tower_types["Life"].get("buff_damage", 1.2)
        self.buff_cooldown = tower_types["Life"].get("buff_cooldown", 0.8)
        self.buff_active = False
        self.buff_pulse = 0
        
        # Gold generation
        self.gold_timer = random.uniform(0, 3.0)  # Random initial delay
        self.gold_interval = 15.0  # Seconds between gold generation
        self.gold_amount = 0  # Increases with upgrades
        
        # Life restoration
        self.heal_timer = random.uniform(0, 5.0)  # Random initial delay
        self.heal_interval = 25.0  # Seconds between healing player lives
        self.heal_amount = 0  # Increases with upgrades
        
        # Magic enhancement level
        self.life_magic_level = 1.0
        
    def upgrade_special(self, multiplier):
        """Enhance life tower special ability with upgrade"""
        super().upgrade_special(multiplier)
        
        # Visual and effect enhancements
        self.life_magic_level += 0.2
        self.vine_growth += 0.1
        
        # Buff ability enhancements
        self.buff_damage = 1.2 + (0.1 * self.upgrades["special"])
        self.buff_cooldown = max(0.6, 0.8 - (0.05 * self.upgrades["special"]))
        
        # Add more flowers at higher levels
        if self.level % 2 == 0 and len(self.flowers) < 10:
            for _ in range(2):
                self.flowers.append({
                    'angle': random.uniform(0, 360),
                    'distance': random.uniform(self.radius * 1.0, self.radius * 1.5),
                    'size': random.uniform(3, 5),
                    'speed': random.uniform(10, 20) * (1 if random.random() > 0.5 else -1),
                    'color': random.choice([(255, 105, 180), (255, 150, 200), (255, 182, 193)])
                })
        
        # Enable gold generation at level 2 special
        if self.upgrades["special"] >= 2:
            self.gold_amount = 5 + (3 * (self.upgrades["special"] - 2))
            self.gold_interval = max(5.0, 15.0 - (self.upgrades["special"] * 2))
        
        # Enable life healing at level 3 special
        if self.upgrades["special"] >= 3:
            self.heal_amount = 1
            self.heal_interval = max(10.0, 25.0 - (self.upgrades["special"] * 3))
            
    def is_preferred_target(self, enemy, distance, current_best, current_best_distance):
        """Life towers prioritize enemies with special abilities"""
        if not current_best:
            return True
            
        # Target healing enemies first (they heal other enemies)
        enemy_has_healing = enemy.type.get("special_ability") == "heal" if hasattr(enemy, "type") else False
        current_has_healing = current_best.type.get("special_ability") == "heal" if hasattr(current_best, "type") else False
        
        if enemy_has_healing and not current_has_healing:
            return True
        elif not enemy_has_healing and current_has_healing:
            return False
            
        # Otherwise target closest enemy
        return distance < current_best_distance
        
    def update_tower(self, dt, enemies, projectiles, particles=None):
        """Update life tower state"""
        super().update_tower(dt, enemies, projectiles, particles)
        
        # Update floating flowers
        for flower in self.flowers:
            flower['angle'] = (flower['angle'] + flower['speed'] * dt) % 360
        
        # Generate leaf particles
        self.growth_timer += dt
        if particles and self.growth_timer >= self.growth_interval * (1 / self.life_magic_level):
            self.growth_timer = 0
            
            # Random position near tower
            angle = random.uniform(0, math.pi * 2)
            distance = random.uniform(0, self.radius * 0.8)
            x = self.pos.x + math.cos(angle) * distance
            y = self.pos.y + math.sin(angle) * distance
            
            # Leaf particle rises upward
            rise_angle = -math.pi/2 + random.uniform(-0.5, 0.5)
            speed = random.uniform(10, 20)
            velocity = (math.cos(rise_angle) * speed, math.sin(rise_angle) * speed)
            
            # Random green shade
            g = random.randint(150, 250) 
            r = int(g * random.uniform(0.5, 0.8))
            b = int(g * random.uniform(0.5, 0.8))
            
            particles.add_particle_params(
                Vector2(x, y),
                (r, g, b),
                velocity,
                random.uniform(2, 4) * self.life_magic_level,
                random.uniform(0.8, 1.5)
            )
        
        # Update buff effect - find towers to buff
        self.buff_active = False
        if hasattr(self, 'game') and hasattr(self.game, 'towers'):
            for tower in self.game.towers:
                if tower != self and (tower.pos - self.pos).length() <= self.buff_range:
                    self.buff_active = True
                    tower.buff_multiplier = self.buff_damage
        
        # Update gold generation
        if self.gold_amount > 0:
            self.gold_timer += dt
            if self.gold_timer >= self.gold_interval:
                self.gold_timer = 0
                
                # Generate gold
                if hasattr(self, 'game') and hasattr(self.game, 'money'):
                    self.game.money += self.gold_amount
                    
                    # Add floating text for gold generated
                    if hasattr(self.game, 'floating_texts'):
                        from game.ui import FloatingText
                        self.game.floating_texts.append(
                            FloatingText(f"+{self.gold_amount} gold", 
                                       (self.pos.x, self.pos.y - 30),
                                       (255, 215, 0), 20)
                        )
                
                # Create gold particle burst
                if particles:
                    for _ in range(10):
                        angle = random.uniform(0, math.pi * 2)
                        speed = random.uniform(20, 40)
                        velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
                        
                        particles.add_particle_params(
                            Vector2(self.pos),
                            (255, 215, 0),  # Gold color
                            velocity,
                            random.uniform(3, 5),
                            random.uniform(0.5, 1.0)
                        )
        
        # Update life restoration
        if self.heal_amount > 0:
            self.heal_timer += dt
            if self.heal_timer >= self.heal_interval:
                self.heal_timer = 0
                
                # Restore player lives
                if hasattr(self, 'game') and hasattr(self.game, 'lives'):
                    self.game.lives += self.heal_amount
                    
                    # Add floating text for lives restored
                    if hasattr(self.game, 'floating_texts'):
                        from game.ui import FloatingText
                        self.game.floating_texts.append(
                            FloatingText(f"+{self.heal_amount} life", 
                                       (self.pos.x, self.pos.y - 30),
                                       (255, 50, 50), 20)
                        )
                
                # Create healing particle burst
                if particles:
                    for _ in range(15):
                        angle = random.uniform(0, math.pi * 2)
                        speed = random.uniform(20, 50)
                        velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
                        
                        particles.add_particle_params(
                            Vector2(self.pos),
                            (255, 50, 100),  # Pink/red for healing
                            velocity,
                            random.uniform(3, 6),
                            random.uniform(0.5, 1.2)
                        )
    
    def fire_at_target(self, target, projectiles, particles=None):
        """Fire at target with enhanced life magic effects"""
        super().fire_at_target(target, projectiles, particles)
        
        # Add nature-themed burst effect when firing
        if particles:
            # Create flower petal burst
            petal_count = int(6 * self.life_magic_level)
            for _ in range(petal_count):
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(20, 40) * self.life_magic_level
                velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
                
                # Random petal color
                color = random.choice([
                    (255, 105, 180),  # Pink
                    (255, 150, 200),  # Light pink
                    (255, 182, 193)   # Very light pink
                ])
                
                particles.add_particle_params(
                    Vector2(self.pos),
                    color,
                    velocity,
                    random.uniform(2, 4),
                    random.uniform(0.3, 0.6)
                )
    
    def apply_projectile_effects(self, projectile):
        """Apply enhanced life effects to projectile"""
        super().apply_projectile_effects(projectile)
        
        # Life projectiles are prettier but same damage
        projectile.heart_trail = True
        
        # At higher levels, projectiles have a chance to heal player on hit
        if self.heal_amount > 0 and random.random() < 0.2:
            projectile.heal_on_hit = min(1, self.heal_amount // 2)
    
    def draw_effects(self, surface, screen_pos, screen_radius, camera=None):
        """Draw life tower specific magical effects"""
        zoom_factor = camera.zoom if camera else 1
        
        # Draw nature aura
        current_time = pygame.time.get_ticks() / 1000
        aura_pulse = 0.2 * math.sin(current_time + self.pulse_offset)
        aura_radius = screen_radius * (1.3 + aura_pulse) * self.life_magic_level
        
        # Draw multiple layers of aura
        for i in range(2):
            alpha = 70 - (i * 30)
            size = aura_radius * (1 + i * 0.2)
            
            # Check for valid size before creating surface
            if size <= 0:
                continue
                
            surf_size = max(1, int(size * 2))  # Ensure positive surface size
            aura_surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
            
            # Create gradient of color from center
            pygame.draw.circle(aura_surf, (200, 255, 200, alpha), (size, size), size)
            
            # Blit aura to surface
            surface.blit(aura_surf, (int(screen_pos.x - size), int(screen_pos.y - size)))
        
        # Draw buff range indicator if active
        if self.buff_active:
            # Pulsing buff circle
            self.buff_pulse = (self.buff_pulse + 0.02) % 1
            buff_size = self.buff_range * zoom_factor * (0.95 + self.buff_pulse * 0.1)
            
            if buff_size > 0:
                buff_surf = pygame.Surface((int(buff_size * 2), int(buff_size * 2)), pygame.SRCALPHA)
                alpha = int(30 * (1 - self.buff_pulse))
                pygame.draw.circle(buff_surf, (100, 255, 100, alpha),
                                 (buff_size, buff_size),
                                 buff_size, 
                                 max(1, int(2 * zoom_factor)))
                surface.blit(buff_surf, (int(screen_pos.x - buff_size), int(screen_pos.y - buff_size)))
        
        # Draw heart shape above tower
        heart_height = screen_radius * 1.5 * zoom_factor
        heart_width = screen_radius * 1.2 * zoom_factor
        heart_y_offset = -heart_height * 0.3
        
        # Draw heart with slight pulsing
        heart_pulse = 1.0 + 0.1 * math.sin(current_time * 2)
        heart_size = heart_width * heart_pulse
        
        if heart_size > 0:
            # Create heart surface
            heart_surf = pygame.Surface((int(heart_size * 2), int(heart_size * 2)), pygame.SRCALPHA)
            
            # Draw the two circles of the heart
            circle_radius = heart_size * 0.5
            circle_offset = heart_size * 0.25
            
            pygame.draw.circle(heart_surf, (255, 105, 180, 200), 
                             (int(heart_size - circle_offset), int(heart_size - circle_offset)), 
                             int(circle_radius))
            pygame.draw.circle(heart_surf, (255, 105, 180, 200), 
                             (int(heart_size + circle_offset), int(heart_size - circle_offset)), 
                             int(circle_radius))
            
            # Draw the bottom point of the heart
            points = [
                (heart_size, heart_size + circle_radius * 1.2),  # Bottom point
                (heart_size - heart_size * 0.8, heart_size - circle_offset),  # Left corner
                (heart_size + heart_size * 0.8, heart_size - circle_offset)   # Right corner
            ]
            pygame.draw.polygon(heart_surf, (255, 105, 180, 200), points)
            
            # Add glow to heart
            glow_surf = pygame.Surface((int(heart_size * 2.4), int(heart_size * 2.4)), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 105, 180, 50), 
                             (int(heart_size * 1.2), int(heart_size * 1.2)), 
                             int(heart_size * 1.2))
            surface.blit(glow_surf, (int(screen_pos.x - heart_size * 1.2), int(screen_pos.y + heart_y_offset - heart_size * 1.2)))
            
            # Position the heart
            heart_pos = (int(screen_pos.x - heart_size), int(screen_pos.y + heart_y_offset - heart_size))
            surface.blit(heart_surf, heart_pos)
        
        # Draw nature vines
        for i in range(self.vine_count):
            vine_angle = (i / self.vine_count) * math.pi * 2
            vine_wave = math.sin(current_time * self.vine_speeds[i] + i) * 0.2
            
            # Create growing vine with leaves
            points = []
            leaf_positions = []
            
            vine_segments = 10
            for j in range(vine_segments + 1):
                seg_progress = j / vine_segments
                # Only draw up to the current growth level
                if seg_progress > self.vine_growth:
                    break
                    
                # Vine follows a wavy, growing path
                angle = vine_angle + vine_wave * seg_progress * 2
                length = self.vine_length * zoom_factor * seg_progress
                
                x = screen_pos.x + math.cos(angle) * length
                y = screen_pos.y + math.sin(angle) * length
                
                points.append((x, y))
                
                # Add leaf positions at intervals
                if j > 0 and j % 3 == 0:
                    leaf_positions.append({
                        'pos': (x, y),
                        'angle': angle + math.pi/2 * (1 if i % 2 == 0 else -1)
                    })
            
            # Draw vine
            if len(points) >= 2:
                pygame.draw.lines(surface, (100, 200, 100, 200), False, points, 
                                max(1, int(2 * zoom_factor)))
            
            # Draw leaves
            for leaf in leaf_positions:
                # Leaf shape
                leaf_size = 5 * zoom_factor
                leaf_points = []
                
                # Create leaf shape
                leaf_points.append(leaf['pos'])  # Base of leaf
                
                # Leaf tip
                tip_x = leaf['pos'][0] + math.cos(leaf['angle']) * leaf_size * 2
                tip_y = leaf['pos'][1] + math.sin(leaf['angle']) * leaf_size * 2
                leaf_points.append((tip_x, tip_y))
                
                # Leaf sides
                side_angle1 = leaf['angle'] + math.pi/4
                side_angle2 = leaf['angle'] - math.pi/4
                
                side_x1 = leaf['pos'][0] + math.cos(side_angle1) * leaf_size
                side_y1 = leaf['pos'][1] + math.sin(side_angle1) * leaf_size
                leaf_points.append((side_x1, side_y1))
                
                side_x2 = leaf['pos'][0] + math.cos(side_angle2) * leaf_size
                side_y2 = leaf['pos'][1] + math.sin(side_angle2) * leaf_size
                leaf_points.append((side_x2, side_y2))
                
                # Draw leaf
                if len(leaf_points) >= 3:
                    pygame.draw.polygon(surface, (100, 200, 100, 180), leaf_points)
        
        # Draw floating flowers
        for flower in self.flowers:
            flower_angle = math.radians(flower['angle'])
            
            # Calculate position with slight bobbing
            bob_offset = math.sin(current_time * 1.5 + flower['angle']) * 3 * zoom_factor
            flower_x = screen_pos.x + math.cos(flower_angle) * flower['distance'] * zoom_factor
            flower_y = screen_pos.y + math.sin(flower_angle) * flower['distance'] * zoom_factor + bob_offset
            
            # Draw flower with petals
            flower_size = flower['size'] * zoom_factor * self.life_magic_level
            petal_count = 5
            
            if flower_size > 0:
                # Draw petals in a circle
                for i in range(petal_count):
                    petal_angle = (i / petal_count) * math.pi * 2
                    
                    petal_x = flower_x + math.cos(petal_angle) * flower_size
                    petal_y = flower_y + math.sin(petal_angle) * flower_size
                    
                    # Draw petal as small ellipse
                    petal_rect = pygame.Rect(
                        int(petal_x - flower_size), 
                        int(petal_y - flower_size*0.7),
                        int(flower_size * 2),
                        int(flower_size * 1.4)
                    )
                    
                    # Rotate petal to face outward
                    petal_surf = pygame.Surface((petal_rect.width, petal_rect.height), pygame.SRCALPHA)
                    pygame.draw.ellipse(petal_surf, flower['color'], (0, 0, petal_rect.width, petal_rect.height))
                    petal_surf = pygame.transform.rotate(petal_surf, -math.degrees(petal_angle))
                    
                    # Position petal
                    rotated_rect = petal_surf.get_rect(center=(petal_x, petal_y))
                    surface.blit(petal_surf, rotated_rect.topleft)
                
                # Draw flower center
                pygame.draw.circle(surface, (255, 255, 100), (int(flower_x), int(flower_y)), int(flower_size * 0.5))
        
        # Draw gold generation effect
        if self.gold_amount > 0 and self.gold_timer >= self.gold_interval * 0.8:
            # Draw charging effect as gold generation is about to happen
            charge_percent = (self.gold_timer - (self.gold_interval * 0.8)) / (self.gold_interval * 0.2)
            
            if charge_percent > 0:
                # Draw gold sparkles
                for _ in range(int(5 * charge_percent)):
                    angle = random.uniform(0, math.pi * 2)
                    distance = random.uniform(0, screen_radius * 1.5)
                    sparkle_x = screen_pos.x + math.cos(angle) * distance * zoom_factor
                    sparkle_y = screen_pos.y + math.sin(angle) * distance * zoom_factor
                    
                    # Draw gold sparkle
                    sparkle_size = max(1, int(random.uniform(1, 3) * zoom_factor))
                    pygame.draw.circle(surface, (255, 215, 0, 200), 
                                     (int(sparkle_x), int(sparkle_y)), 
                                     sparkle_size)
                    
                    # Add sparkle lines
                    for i in range(4):
                        line_angle = (i / 4) * math.pi * 2
                        line_end_x = sparkle_x + math.cos(line_angle) * sparkle_size * 2
                        line_end_y = sparkle_y + math.sin(line_angle) * sparkle_size * 2
                        
                        pygame.draw.line(surface, (255, 215, 0, 150),
                                       (int(sparkle_x), int(sparkle_y)),
                                       (int(line_end_x), int(line_end_y)),
                                       max(1, int(1 * zoom_factor)))
        
        # Draw healing effect
        if self.heal_amount > 0 and self.heal_timer >= self.heal_interval * 0.85:
            # Draw radiant effect as healing is about to happen
            charge_percent = (self.heal_timer - (self.heal_interval * 0.85)) / (self.heal_interval * 0.15)
            
            if charge_percent > 0:
                # Draw healing circle
                heal_radius = screen_radius * (1 + charge_percent) * zoom_factor
                
                if heal_radius > 0:
                    heal_surf = pygame.Surface((int(heal_radius * 2), int(heal_radius * 2)), pygame.SRCALPHA)
                    heal_alpha = int(100 * charge_percent)
                    pygame.draw.circle(heal_surf, (255, 50, 50, heal_alpha),
                                     (heal_radius, heal_radius),
                                     heal_radius)
                    surface.blit(heal_surf, (int(screen_pos.x - heal_radius), int(screen_pos.y - heal_radius)))
                    
                    # Draw healing cross
                    cross_size = heal_radius * 0.7
                    cross_width = max(1, int(3 * zoom_factor * charge_percent))
                    
                    pygame.draw.line(heal_surf, (255, 255, 255, heal_alpha),
                                   (heal_radius, heal_radius - cross_size),
                                   (heal_radius, heal_radius + cross_size),
                                   cross_width)
                    
                    pygame.draw.line(heal_surf, (255, 255, 255, heal_alpha),
                                   (heal_radius - cross_size, heal_radius),
                                   (heal_radius + cross_size, heal_radius),
                                   cross_width)
                    
                    surface.blit(heal_surf, (int(screen_pos.x - heal_radius), int(screen_pos.y - heal_radius))) 