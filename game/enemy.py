import pygame
from pygame.math import Vector2
import random
from game.settings import enemy_types
import math


class Enemy:
    def __init__(self, path_points, enemy_type="Normal", wave_level=1):
        # Convert path points into Vector2 objects for easier math
        self.path_points = [Vector2(p) for p in path_points]
        self.pos = self.path_points[0].copy()
        self.current_point_index = 0
        
        # Set base stats and apply type multipliers
        self.enemy_type = enemy_type
        self.type_stats = enemy_types[enemy_type]
        self.base_speed = 60 + (wave_level - 1) * 5
        self.speed = self.base_speed * self.type_stats["speed_multiplier"]
        self.base_health = 100 * wave_level
        self.max_health = self.base_health * self.type_stats["health_multiplier"]
        self.health = self.max_health
        self.reward = int(20 * wave_level * self.type_stats["reward_multiplier"])
        self.color = self.type_stats["color"]
        self.radius = 10 if enemy_type != "Boss" else 20
        self.reached_end = False
        
        # Status effects
        self.status_effects = {}  # {effect_name: {"duration": time_left, "value": effect_value}}
        
        # Special abilities
        self.special_ability = self.type_stats.get("special_ability")
        self.ability_cooldown = 0
        self.is_cloaked = False
        self.alpha = 255
        self.pulse_offset = random.random() * 6.28  # Random starting phase
        
        # Visual effects
        self.trail_positions = []
        self.hit_flash = 0
        self.has_shield = enemy_type == "Boss"
        self.shield_health = self.max_health * 0.3 if self.has_shield else 0
        self.max_shield_health = self.shield_health
        
        # Track who killed this enemy (for evolution credit)
        self.last_damage_source = None
        
        # Transformation effect from Druid evolution
        self.is_transformed = False
        self.original_size = self.radius
        
        # Direction for knockback effects
        self.knockback_dir = Vector2(0, 0)
        self.knockback_remaining = 0

    def update(self, dt, enemies=None):
        # Update status effect durations
        effects_to_remove = []
        for effect, data in self.status_effects.items():
            data["duration"] -= dt
            if data["duration"] <= 0:
                effects_to_remove.append(effect)
        
        for effect in effects_to_remove:
            if effect == "slow" or effect == "super_slow":
                self.speed = self.base_speed * self.type_stats["speed_multiplier"]
            del self.status_effects[effect]
        
        # Handle freeze status
        if "freeze" in self.status_effects:
            # Frozen enemies don't move
            return
        
        # Apply knockback effect
        if self.knockback_remaining > 0:
            knockback_speed = 200  # Pixels per second
            move_amount = knockback_speed * dt
            if move_amount > self.knockback_remaining:
                move_amount = self.knockback_remaining
            
            self.pos += self.knockback_dir * move_amount
            self.knockback_remaining -= move_amount
        
        # Update special abilities
        if self.special_ability == "heal" and enemies and self.ability_cooldown <= 0:
            for enemy in enemies:
                if enemy != self and enemy.pos.distance_to(self.pos) <= self.type_stats.get("heal_radius", 80):
                    enemy.health = min(enemy.health + self.type_stats.get("heal_amount", 5), enemy.max_health)
                    
                    # Visual healing effect
                    effect_pos = Vector2(
                        (self.pos.x + enemy.pos.x) / 2,
                        (self.pos.y + enemy.pos.y) / 2
                    )
                    
            # Reset cooldown
            self.ability_cooldown = 2.0
        
        elif self.special_ability == "cloak" and self.ability_cooldown <= 0:
            # Apply cloaking
            cloak_duration = self.type_stats.get("cloak_duration", 3.0)
            self.apply_effect("cloak", cloak_duration)
            self.is_cloaked = True
            self.alpha = 80
            
            # Reset cooldown
            self.ability_cooldown = self.type_stats.get("cloak_cooldown", 5.0)
        
        # Update cloaking
        if "cloak" in self.status_effects:
            self.is_cloaked = True
            self.alpha = 80
        else:
            self.is_cloaked = False
            self.alpha = 255
        
        # Update reveal effect (counter to cloaking)
        if "reveal" in self.status_effects:
            self.is_cloaked = False
            self.alpha = 255
        
        # Update cooldowns
        if self.ability_cooldown > 0:
            self.ability_cooldown -= dt
        
        # Move along path
        if not self.reached_end and self.current_point_index < len(self.path_points):
            # Get current target point
            target = self.path_points[self.current_point_index]
            
            # Calculate distance to target
            direction = target - self.pos
            distance = direction.length()
            
            # If close enough to target, move to next point
            if distance < self.speed * dt:
                self.pos = target.copy()
                self.current_point_index += 1
                
                # If we've reached the end of the path
                if self.current_point_index >= len(self.path_points):
                    self.reached_end = True
            else:
                # Move towards target
                if distance > 0:
                    direction.normalize_ip()
                
                # Check for path modifications from vortex effect
                if "vortex" in self.status_effects:
                    vortex_data = self.status_effects["vortex"]
                    vortex_pos = vortex_data["position"]
                    vortex_strength = vortex_data["strength"]
                    
                    # Calculate pull direction
                    pull_dir = vortex_pos - self.pos
                    pull_dist = pull_dir.length()
                    
                    if pull_dist > 0:
                        pull_dir.normalize_ip()
                        
                        # Pull strength decreases with distance
                        pull_factor = max(0, 1 - (pull_dist / vortex_data["radius"]))
                        pull_strength = vortex_strength * pull_factor * dt
                        
                        # Add pull to movement
                        direction = direction * 0.7 + pull_dir * 0.3
                        direction.normalize_ip()
                
                # Apply spin effect which makes enemies move in circles
                if "spin" in self.status_effects:
                    spin_data = self.status_effects["spin"]
                    spin_center = spin_data["position"]
                    
                    # Calculate perpendicular direction for spin
                    to_center = spin_center - self.pos
                    if to_center.length() > 0:
                        perp_dir = Vector2(-to_center.y, to_center.x)
                        perp_dir.normalize_ip()
                        
                        # Blend with original direction
                        direction = direction * 0.3 + perp_dir * 0.7
                        direction.normalize_ip()
                
                # Apply movement
                self.pos += direction * self.speed * dt
                
                # Add to trail
                if len(self.trail_positions) == 0 or (self.pos - self.trail_positions[-1]).length() > 5:
                    self.trail_positions.append(self.pos.copy())
                    if len(self.trail_positions) > 10:
                        self.trail_positions.pop(0)
        
        # Update visual effects
        if self.hit_flash > 0:
            self.hit_flash -= dt

    def take_damage(self, amount, damage_type=None, source=None):
        """Deal damage to the enemy"""
        # Apply damage resistance for bosses
        if self.enemy_type == "Boss" and self.special_ability == "resist":
            amount *= (1 - self.type_stats.get("resist_amount", 0.5))
        
        # Apply weakness effect
        if "weaken" in self.status_effects:
            amount *= self.status_effects["weaken"]["value"]
        
        # Apply evasion effect
        if "evasion" in self.status_effects:
            # Check if damage is evaded
            if random.random() < self.status_effects["evasion"]["value"]:
                # Damage evaded
                return 0
        
        # Apply shield damage first
        damage_dealt = 0
        if self.has_shield and self.shield_health > 0:
            if amount >= self.shield_health:
                damage_dealt = self.shield_health
                amount -= self.shield_health
                self.shield_health = 0
                self.has_shield = False
            else:
                self.shield_health -= amount
                damage_dealt = amount
                amount = 0
        
        # Apply remaining damage to health
        if amount > 0:
            self.health -= amount
            damage_dealt += amount
        
        # Track who damaged this enemy last (for kill attribution)
        if source is not None:
            self.last_damage_source = source
        
        # Visual effect
        self.hit_flash = 0.1
        
        return damage_dealt

    def apply_effect(self, effect_name, duration, value=None, source=None, **kwargs):
        """Apply a status effect to the enemy"""
        # Different effects have different default values and behaviors
        if effect_name == "burn":
            # DoT effect
            self.status_effects[effect_name] = {
                "duration": duration,
                "value": value or 5,  # Damage per second
                "tick_timer": 0,
                "source": source
            }
        
        elif effect_name == "slow" or effect_name == "super_slow":
            # Movement speed reduction
            self.status_effects[effect_name] = {
                "duration": duration,
                "value": value or 0.5  # 50% speed
            }
            # Apply slow immediately
            self.speed = self.base_speed * self.type_stats["speed_multiplier"] * (value or 0.5)
        
        elif effect_name == "stun":
            # Prevent movement
            self.status_effects[effect_name] = {
                "duration": duration
            }
        
        elif effect_name == "weaken":
            # Take more damage
            self.status_effects[effect_name] = {
                "duration": duration,
                "value": value or 1.5  # 50% more damage
            }
        
        elif effect_name == "cloak" or effect_name == "reveal":
            # Visibility effects
            self.status_effects[effect_name] = {
                "duration": duration
            }
        
        elif effect_name == "freeze":
            # Complete immobilization
            self.status_effects[effect_name] = {
                "duration": duration
            }
        
        elif effect_name == "vortex":
            # Pulled toward a point
            self.status_effects[effect_name] = {
                "duration": duration,
                "position": kwargs.get("position", Vector2(0, 0)),
                "strength": kwargs.get("strength", 50),
                "radius": kwargs.get("radius", 150)
            }
        
        elif effect_name == "push":
            # Apply knockback
            push_direction = kwargs.get("direction", Vector2(0, 0))
            push_distance = kwargs.get("distance", 100)
            
            if push_direction.length() > 0:
                self.knockback_dir = push_direction.normalize()
                self.knockback_remaining = push_distance
        
        elif effect_name == "spin":
            # Make enemy move in circles
            self.status_effects[effect_name] = {
                "duration": duration,
                "position": kwargs.get("position", self.pos.copy()),
                "radius": kwargs.get("radius", 100)
            }
        
        elif effect_name == "transform":
            # Transform into weaker version
            if not self.is_transformed:
                health_reduction = kwargs.get("health_reduction", 0.5)
                self.is_transformed = True
                self.max_health *= health_reduction
                self.health = min(self.health, self.max_health)
                self.radius = int(self.original_size * 0.7)
                self.speed *= 1.2  # Faster but weaker
                
                # Visual effect: change color to be more greenish
                r, g, b = self.color
                self.color = (r * 0.7, g * 1.3, b * 0.7)
        
        elif effect_name == "curse":
            # Take more damage from all sources
            self.status_effects[effect_name] = {
                "duration": duration,
                "value": value or 1.5  # 50% more damage
            }

    def get_path_progress(self):
        """Calculate a metric representing how far the enemy has progressed along the path."""
        if self.reached_end:
            # Return a large number if the enemy reached the end
            return float('inf')
            
        if self.current_point_index == 0:
            # Enemy hasn't started moving along the main path yet
            return 0.0

        # Calculate progress based on completed segments and position on current segment
        # Index of the point the enemy just passed
        last_point_index = self.current_point_index - 1
        
        # Points defining the current segment
        last_point = self.path_points[last_point_index]
        next_point = self.path_points[self.current_point_index]
        
        segment_vector = next_point - last_point
        segment_length = segment_vector.length()
        
        if segment_length < 1e-6: # Avoid division by zero for very short/zero-length segments
            # If segment is tiny, consider progress as just the index of the passed point
            return float(last_point_index)
            
        vector_from_last = self.pos - last_point
        
        # Project the enemy's position onto the segment vector
        # Ensure the projection distance isn't negative or beyond the segment length
        distance_along_segment = vector_from_last.dot(segment_vector.normalize())
        distance_along_segment = max(0.0, min(distance_along_segment, segment_length))
        
        fraction_along_segment = distance_along_segment / segment_length
        
        # Total progress: number of segments passed + fraction along current segment
        progress = float(last_point_index) + fraction_along_segment
        return progress

    def draw(self, surface, assets=None, camera=None, show_hp=False):
        """Draw the enemy"""
        # Apply camera transform if provided
        pos = self.pos
        radius = self.radius
        
        if camera:
            pos = camera.world_to_screen(self.pos)
            radius = int(self.radius * camera.zoom)
        
        # Pulsation effect
        pulse_factor = 1.0 + math.sin(pygame.time.get_ticks() * 0.005 + self.pulse_offset) * 0.1
        pulsating_radius = max(1, int(radius * pulse_factor))

        # Prepare enemy color with transparency
        if len(self.color) == 3:
            draw_color = self.color + (self.alpha,)
        else:
            # Use base color but apply current alpha
            draw_color = self.color[:3] + (self.alpha,)
        
        # Flash effect when hit
        if self.hit_flash > 0:
            # Blend white flash with base color for a less harsh effect
            flash_amount = min(1.0, self.hit_flash / 0.2) # Assuming hit_flash duration is ~0.2s
            flash_color = (
                int(draw_color[0] + (255 - draw_color[0]) * flash_amount),
                int(draw_color[1] + (255 - draw_color[1]) * flash_amount),
                int(draw_color[2] + (255 - draw_color[2]) * flash_amount),
                self.alpha
            )
            final_draw_color = flash_color
        else:
            final_draw_color = draw_color

        # --- Start Shape and Type-Specific Modifications ---
        num_sides = 6 # Base shape: hexagon
        points = []
        current_time_sec = pygame.time.get_ticks() / 1000.0
        base_angle_offset = self.pulse_offset
        
        # Make Bosses larger
        display_radius = pulsating_radius * 1.5 if self.enemy_type == "Boss" else pulsating_radius
        
        for i in range(num_sides):
            angle = base_angle_offset + i * (2 * math.pi / num_sides)
            # Slight radius variation per vertex for irregularity
            vertex_radius_factor = 1.0 + 0.08 * math.sin(current_time_sec * 1.5 + i * math.pi)
            current_radius = display_radius * vertex_radius_factor
            
            x = pos[0] + math.cos(angle) * current_radius
            y = pos[1] + math.sin(angle) * current_radius
            points.append((int(x), int(y)))

        # --- Advanced Visual Polish ---
        # Draw radial gradient body
        body_surface = pygame.Surface((display_radius*2, display_radius*2), pygame.SRCALPHA)
        center = display_radius
        for r in range(display_radius, 0, -1):
            grad_alpha = int(final_draw_color[3] * (r / display_radius) ** 1.7)
            grad_color = (
                int(final_draw_color[0] * (0.7 + 0.3 * r / display_radius)),
                int(final_draw_color[1] * (0.7 + 0.3 * r / display_radius)),
                int(final_draw_color[2] * (0.7 + 0.3 * r / display_radius)),
                grad_alpha
            )
            pygame.draw.circle(body_surface, grad_color, (center, center), r)
        # Add highlight (shiny spot)
        highlight_radius = max(2, display_radius // 3)
        highlight_pos = (center - display_radius // 3, center - display_radius // 3)
        pygame.draw.circle(body_surface, (255,255,255,60), highlight_pos, highlight_radius)
        # Mask body_surface to polygon shape
        mask_surface = pygame.Surface((display_radius*2, display_radius*2), pygame.SRCALPHA)
        poly_points = [(int(x-pos[0]+center), int(y-pos[1]+center)) for (x, y) in points]
        if len(poly_points) >= 3:
            pygame.draw.polygon(mask_surface, (255,255,255,255), poly_points)
            body_surface.blit(mask_surface, (0,0), special_flags=pygame.BLEND_RGBA_MULT)
        surface.blit(body_surface, (int(pos[0])-center, int(pos[1])-center))

        # Draw double outline (bright inner, dark outer)
        if len(points) >= 3:
            # Outer dark outline
            outline_color_outer = (40, 40, 40, self.alpha)
            outline_width_outer = max(2, display_radius // 5)
            pygame.draw.polygon(surface, outline_color_outer, points, outline_width_outer)
            # Inner bright outline
            outline_color_inner = (220, 220, 255, min(160, self.alpha))
            outline_width_inner = 2
            pygame.draw.polygon(surface, outline_color_inner, points, outline_width_inner)
        
        # Draw shield if present (using display_radius for positioning)
        if self.has_shield and self.shield_health > 0:
            shield_radius = display_radius + max(2, display_radius // 8) # Position outside outline
            shield_percentage = self.shield_health / self.max_shield_health
            shield_color = (100, 100, 255, int(self.alpha * shield_percentage))
            
            shield_surface = pygame.Surface((shield_radius*2, shield_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(shield_surface, shield_color, (shield_radius, shield_radius), shield_radius)
            surface.blit(shield_surface, (int(pos[0])-shield_radius, int(pos[1])-shield_radius))
        
        # Draw status effect indicators (using display_radius for positioning)
        status_indicator_base_radius = display_radius + max(4, display_radius // 5)
        status_count = len(self.status_effects)
        if status_count > 0:
            angle_step = 360 / status_count
            for i, (effect_name, _) in enumerate(self.status_effects.items()):
                angle = math.radians(i * angle_step)
                indicator_pos = (
                    int(pos[0] + math.cos(angle) * status_indicator_base_radius),
                    int(pos[1] + math.sin(angle) * status_indicator_base_radius)
                )
                
                # Choose color based on effect type
                if effect_name == "burn":
                    indicator_color = (255, 100, 0)
                elif effect_name == "slow" or effect_name == "super_slow":
                    indicator_color = (0, 100, 255)
                elif effect_name == "stun" or effect_name == "freeze":
                    indicator_color = (150, 150, 255)
                elif effect_name == "weaken" or effect_name == "curse":
                    indicator_color = (200, 0, 200)
                elif effect_name == "cloak":
                    indicator_color = (200, 200, 200)
                elif effect_name == "reveal":
                    indicator_color = (255, 255, 0)
                elif effect_name == "vortex":
                    indicator_color = (0, 200, 255)
                elif effect_name == "spin":
                    indicator_color = (200, 230, 255)
                else:
                    indicator_color = (200, 200, 200)
                
                # Draw small indicator
                indicator_draw_radius = max(2, display_radius // 4)
                pygame.draw.circle(surface, indicator_color, indicator_pos, indicator_draw_radius)
                pygame.draw.circle(surface, (0,0,0,150), indicator_pos, indicator_draw_radius, 1) # Add outline
        
        # Draw health bar (using display_radius for positioning)
        health_bar_width = display_radius * 1.8 # Make slightly wider than polygon
        health_bar_height = 4
        health_percentage = max(0, self.health / self.max_health)
        
        health_bar_y = int(pos[1] - display_radius - health_bar_height - 5) # Adjust vertical position slightly further up
        
        # Background
        health_bg_rect = pygame.Rect(
            int(pos[0] - health_bar_width / 2),
            health_bar_y,
            health_bar_width,
            health_bar_height
        )
        pygame.draw.rect(surface, (60, 60, 60, self.alpha), health_bg_rect, border_radius=1)
        
        # Health fill
        if health_percentage > 0:
            fill_width = int(health_bar_width * health_percentage)
            
            # Color based on health percentage
            if health_percentage > 0.6:
                fill_color = (0, 200, 0, self.alpha)
            elif health_percentage > 0.3:
                fill_color = (200, 200, 0, self.alpha)
            else:
                fill_color = (200, 0, 0, self.alpha)
            
            health_fill_rect = pygame.Rect(
                int(pos[0] - health_bar_width / 2),
                health_bar_y,
                fill_width,
                health_bar_height
            )
            pygame.draw.rect(surface, fill_color, health_fill_rect, border_radius=1)

        # --- Animated Energy Core ---
        core_radius = int(display_radius * (0.21 + 0.04 * math.sin(current_time_sec * 3 + self.pulse_offset)))
        core_color = (
            min(255, int(final_draw_color[0] * 1.2)),
            min(255, int(final_draw_color[1] * 1.2)),
            min(255, int(final_draw_color[2] * 1.2)),
            160
        )
        pygame.draw.circle(surface, core_color, (int(pos[0]), int(pos[1])), core_radius)
        # Add a soft glow around the core
        for i in range(3, 0, -1):
            alpha = int(30 * i)
            pygame.draw.circle(surface, core_color[:3] + (alpha,), (int(pos[0]), int(pos[1])), core_radius + i*2)

        # --- Orbiting Particles ---
        num_particles = 5
        particle_radius = max(2, display_radius // 8)
        orbit_r = int(display_radius * 0.75)
        for i in range(num_particles):
            angle = current_time_sec * 1.5 + i * (2 * math.pi / num_particles) + self.pulse_offset
            px = pos[0] + math.cos(angle) * orbit_r
            py = pos[1] + math.sin(angle) * orbit_r
            particle_alpha = 90 + 60 * math.sin(current_time_sec * 2 + i)
            pygame.draw.circle(surface, (255,255,255,int(particle_alpha)), (int(px), int(py)), particle_radius)

        # --- Rotating Internal Lines ---
        if len(points) >= 3:
            if self.enemy_type == "Fast":
                inner_angle = current_time_sec * 4.0 # Faster rotation
            elif self.enemy_type == "Tank" or self.enemy_type == "Boss":
                inner_angle = current_time_sec * 1.0 # Slower rotation
            else:
                inner_angle = current_time_sec * 1.8 # Normal rotation
            inner_len = display_radius * 0.5
            line_color = (min(255, final_draw_color[0]+50), min(255, final_draw_color[1]+50), min(255, final_draw_color[2]+50), self.alpha)
            line_width = max(1, display_radius // 8)
            for i in range(2):
                rot_angle = inner_angle + i * (math.pi / 2)
                x1 = pos[0] + math.cos(rot_angle) * inner_len
                y1 = pos[1] + math.sin(rot_angle) * inner_len
                x2 = pos[0] - math.cos(rot_angle) * inner_len
                y2 = pos[1] - math.sin(rot_angle) * inner_len
                pygame.draw.line(surface, line_color, (int(x1), int(y1)), (int(x2), int(y2)), line_width)