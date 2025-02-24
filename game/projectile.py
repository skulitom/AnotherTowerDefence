import pygame
from pygame.math import Vector2
import random
import math
from game.settings import tower_types


class Projectile:
    def __init__(self, pos, target, damage, bullet_speed, tower_type):
        self.pos = Vector2(pos)
        self.target = target  # Enemy instance reference
        self.damage = damage
        self.speed = bullet_speed
        self.radius = 5  # for drawing projectile
        self.active = True
        self.tower_type = tower_type
        self.trail = []
        self.max_trail_length = 15 if tower_type in ["Fire", "Air", "Light"] else 8
        self.effect = None  # Special effect
        
        # Chain lightning variables
        self.chain_targets = []
        self.chain_countdown = 0
        self.chain_damage = damage
        
        # Visual effect variables
        self.angle = random.uniform(0, 360)
        self.spin_speed = random.uniform(-20, 20)
        self.pulse_offset = random.random() * 6.28
        self.pulse_speed = random.uniform(0.8, 1.2)
        self.size_oscillation = random.uniform(0.8, 1.2)
        
        # Determine projectile color based on tower type
        if tower_type in tower_types:
            self.color = tower_types[tower_type].get("particle_color", tower_types[tower_type]["color"])
        else:
            self.color = (255, 255, 255)

    def update(self, dt, all_enemies=None, particles=None):
        if not self.active:
            return
            
        # Update projectile position
        self.angle += self.spin_speed * dt
        
        # Add current position to trail (limit length based on tower type)
        self.trail.append(Vector2(self.pos))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)
        
        # Handle chain lightning effect
        if self.chain_countdown > 0:
            self.chain_countdown -= dt
            if self.chain_countdown <= 0 and self.chain_targets and all_enemies:
                # Find next target 
                next_target = self.chain_targets.pop(0)
                if next_target.health > 0:
                    # Create a new projectile for the chain lightning
                    chain_proj = Projectile(self.pos, next_target, self.chain_damage, self.speed * 1.5, self.tower_type)
                    chain_proj.radius = self.radius * 0.8  # Smaller radius for chain projectiles
                    chain_proj.chain_damage = self.chain_damage * tower_types[self.tower_type].get("special_damage_falloff", 0.7)
                    return chain_proj
        
        # If target is gone, mark projectile inactive
        if self.target is None or self.target.health <= 0:
            self.active = False
            if particles:
                particles.add_explosion(self.pos.x, self.pos.y, self.color, count=5, size_range=(2, 4))
            return None
            
        # Recalculate direction toward the target (homing behavior)
        direction = self.target.pos - self.pos
        if direction.length() == 0:
            direction = Vector2(0, 0)
        else:
            direction = direction.normalize()
            
        # Add slight variation to movement for some tower types
        if self.tower_type == "Fire":
            # Add flame-like random movement
            direction.x += random.uniform(-0.1, 0.1)
            direction.y += random.uniform(-0.1, 0.1)
            direction = direction.normalize()
        elif self.tower_type == "Air":
            # Add wind-like oscillation
            t = pygame.time.get_ticks() / 300
            direction.x += math.sin(t + self.pulse_offset) * 0.1
            direction.y += math.cos(t + self.pulse_offset) * 0.1
            direction = direction.normalize()
            
        # Move projectile
        self.pos += direction * self.speed * dt
        
        # Add particles based on tower type
        if particles:
            if self.tower_type == "Fire":
                if random.random() < 0.3:
                    particles.add_trail(self.pos.x, self.pos.y, (255, 100, 0), count=1)
            elif self.tower_type == "Water":
                if random.random() < 0.2:
                    particles.add_trail(self.pos.x, self.pos.y, (100, 100, 255), count=1, size_range=(1, 3))
            elif self.tower_type == "Air":
                if random.random() < 0.2:
                    particles.add_trail(self.pos.x, self.pos.y, (200, 230, 255), count=1, size_range=(1, 2))
            elif self.tower_type == "Light":
                if random.random() < 0.3:
                    angle = random.uniform(0, math.pi * 2)
                    offset = random.uniform(0, 3)
                    x = self.pos.x + math.cos(angle) * offset
                    y = self.pos.y + math.sin(angle) * offset
                    particles.add_particle_params(Vector2(x, y), (255, 255, 100), (0, 0), 2, 0.3)
        
        # If projectile is close enough to hit the enemy:
        if self.pos.distance_to(self.target.pos) < self.target.radius + self.radius:
            # Apply special effect if available
            if self.effect and random.random() < self.effect.get("chance", 0):
                effect_name = self.effect.get("name")
                
                if effect_name == "burn":
                    # Apply burn damage over time
                    self.target.apply_effect("burn", self.effect.get("duration", 3.0), self.effect.get("damage", 5))
                    
                elif effect_name == "slow":
                    # Apply slow effect
                    self.target.apply_effect("slow", self.effect.get("duration", 2.0), self.effect.get("amount", 0.5))
                    
                elif effect_name == "stun":
                    # Apply stun effect
                    self.target.apply_effect("stun", self.effect.get("duration", 1.0))
                    
                elif effect_name == "weaken":
                    # Apply weakness effect
                    self.target.apply_effect("weaken", self.effect.get("duration", 4.0), self.effect.get("amount", 1.5))
                    
                elif effect_name == "chain" and all_enemies:
                    # Find closest enemies for chain lightning
                    max_chains = self.effect.get("targets", 3)
                    potential_targets = []
                    
                    for enemy in all_enemies:
                        if enemy != self.target and enemy.health > 0 and "cloak" not in enemy.status_effects:
                            distance = (enemy.pos - self.target.pos).length()
                            if distance <= 150:  # Chain range
                                potential_targets.append((distance, enemy))
                    
                    # Sort by distance and take closest ones
                    potential_targets.sort(key=lambda x: x[0])
                    self.chain_targets = [enemy for _, enemy in potential_targets[:max_chains]]
                    
                    if self.chain_targets:
                        self.chain_countdown = 0.1  # Delay before chain lightning
                        self.chain_damage = self.damage * self.effect.get("damage_falloff", 0.7)
            
            # Apply damage to enemy
            self.target.take_damage(self.damage, self.tower_type)
            
            # Create hit effect
            if particles:
                particles.add_explosion(self.target.pos.x, self.target.pos.y, self.color, 
                                       count=10, size_range=(3, 6), life_range=(0.3, 0.8))
            
            # Deactivate projectile
            self.active = False
            
        # Return a chain projectile if we have one
        return None
        
    def draw(self, surface, camera=None):
        if not self.active:
            return
            
        # Apply camera transform if provided
        if camera:
            screen_pos = pygame.Vector2(*camera.apply(self.pos.x, self.pos.y))
            screen_radius = self.radius * camera.zoom
        else:
            screen_pos = self.pos.copy()
            screen_radius = self.radius
        
        if self.tower_type == "Fire":
            # Draw fire projectile with glow
            for i in range(3):
                glow_size = screen_radius * (3 - i) * 0.8
                alpha = 150 if i == 0 else 100 if i == 1 else 50
                glow_surf = pygame.Surface((int(glow_size * 2), int(glow_size * 2)), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*self.color, alpha), (glow_size, glow_size), glow_size)
                surface.blit(glow_surf, (int(screen_pos.x - glow_size), int(screen_pos.y - glow_size)))
        
        elif self.tower_type == "Water":
            # Draw water projectile with droplet shape
            drop_surf = pygame.Surface((int(screen_radius * 2), int(screen_radius * 3)), pygame.SRCALPHA)
            pygame.draw.ellipse(drop_surf, (*self.color, 200), (0, 0, int(screen_radius * 2), int(screen_radius * 3)))
            # Rotate droplet to point in direction of movement
            angle = math.degrees(math.atan2(self.velocity.y, self.velocity.x))
            drop_surf = pygame.transform.rotate(drop_surf, -angle - 90)
            drop_rect = drop_surf.get_rect(center=(int(screen_pos.x), int(screen_pos.y)))
            surface.blit(drop_surf, drop_rect.topleft)
        
        elif self.tower_type == "Air":
            # Draw air projectile as swirling wind
            angle = pygame.time.get_ticks() / 100
            for i in range(3):
                offset_angle = angle + i * 2.0944
                offset_x = math.cos(offset_angle) * screen_radius * 0.7
                offset_y = math.sin(offset_angle) * screen_radius * 0.7
                cloud_surf = pygame.Surface((int(screen_radius * 1.5), int(screen_radius * 1.5)), pygame.SRCALPHA)
                pygame.draw.circle(cloud_surf, (*self.color, 150), (int(screen_radius * 0.75), int(screen_radius * 0.75)), int(screen_radius * 0.75))
                cloud_rect = cloud_surf.get_rect(center=(int(screen_pos.x + offset_x), int(screen_pos.y + offset_y)))
                surface.blit(cloud_surf, cloud_rect.topleft)
        
        elif self.tower_type == "Earth":
            # Draw earth projectile as a rock
            pygame.draw.circle(surface, self.color, (int(screen_pos.x), int(screen_pos.y)), screen_radius)
            # Add some rock details
            for i in range(3):
                offset_angle = i * 2.0944
                offset_x = math.cos(offset_angle) * screen_radius * 0.5
                offset_y = math.sin(offset_angle) * screen_radius * 0.5
                detail_color = (self.color[0] * 0.7, self.color[1] * 0.7, self.color[2] * 0.7)
                pygame.draw.circle(surface, detail_color, (int(screen_pos.x + offset_x), int(screen_pos.y + offset_y)), screen_radius * 0.3)
        
        elif self.tower_type == "Light":
            # Draw light projectile with glow
            for i in range(3):
                glow_size = screen_radius * (3 - i) * 0.8
                alpha = 150 if i == 0 else 100 if i == 1 else 50
                glow_surf = pygame.Surface((int(glow_size * 2), int(glow_size * 2)), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*self.color, alpha), (glow_size, glow_size), glow_size)
                surface.blit(glow_surf, (int(screen_pos.x - glow_size), int(screen_pos.y - glow_size)))
            
            # Add rays
            ray_count = 4
            for i in range(ray_count):
                angle = ((pygame.time.get_ticks() / 200) + i * 6.28 / ray_count) % 6.28
                ray_length = screen_radius * 2
                end_x = screen_pos.x + math.cos(angle) * ray_length
                end_y = screen_pos.y + math.sin(angle) * ray_length
                pygame.draw.line(surface, (255, 255, 200, 100), (screen_pos.x, screen_pos.y), (end_x, end_y), max(1, int(2 * camera.zoom)) if camera else 2)
        
        elif self.tower_type == "Darkness":
            # Draw darkness projectile as shadow ball
            shadow_surf = pygame.Surface((int(screen_radius * 2.5), int(screen_radius * 2.5)), pygame.SRCALPHA)
            pygame.draw.circle(shadow_surf, (0, 0, 0, 150), (int(screen_radius * 1.25), int(screen_radius * 1.25)), int(screen_radius * 1.25))
            pygame.draw.circle(shadow_surf, (*self.color, 200), (int(screen_radius * 1.25), int(screen_radius * 1.25)), screen_radius)
            surface.blit(shadow_surf, (int(screen_pos.x - screen_radius * 1.25), int(screen_pos.y - screen_radius * 1.25)))
        
        elif self.tower_type == "Life":
            # Draw life projectile as a heart
            heart_surf = pygame.Surface((int(screen_radius * 2.5), int(screen_radius * 2.5)), pygame.SRCALPHA)
            pygame.draw.circle(heart_surf, (*self.color, 200), (int(screen_radius * 0.8), int(screen_radius * 1)), int(screen_radius * 0.8))
            pygame.draw.circle(heart_surf, (*self.color, 200), (int(screen_radius * 1.7), int(screen_radius * 1)), int(screen_radius * 0.8))
            
            # Draw the bottom point of the heart
            points = [
                (int(screen_radius * 1.25), int(screen_radius * 2.2)),
                (int(screen_radius * 0.3), int(screen_radius * 1.3)),
                (int(screen_radius * 2.2), int(screen_radius * 1.3))
            ]
            pygame.draw.polygon(heart_surf, (*self.color, 200), points)
            
            # Add glow
            glow_surf = pygame.Surface((int(screen_radius * 3), int(screen_radius * 3)), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*self.color, 50), (int(screen_radius * 1.5), int(screen_radius * 1.5)), int(screen_radius * 1.5))
            surface.blit(glow_surf, (int(screen_pos.x - screen_radius * 1.5), int(screen_pos.y - screen_radius * 1.5)))
            
            # Position the heart
            heart_rect = heart_surf.get_rect(center=(int(screen_pos.x), int(screen_pos.y)))
            surface.blit(heart_surf, heart_rect.topleft)
        
        else:
            # Default projectile drawing
            pygame.draw.circle(surface, self.color, (int(screen_pos.x), int(screen_pos.y)), screen_radius) 