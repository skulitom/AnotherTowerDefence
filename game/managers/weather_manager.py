"""
Weather Manager - Handles dynamic weather conditions that affect gameplay
"""
import pygame
import random
import math
from pygame.math import Vector2

class WeatherManager:
    def __init__(self, game_manager):
        """Initialize the weather manager"""
        self.game = game_manager
        
        # Current weather state
        self.current_weather = "clear"
        self.weather_timer = 0
        self.weather_duration = 60.0  # Weather changes every 60 seconds
        self.transition_time = 0
        self.transition_duration = 5.0  # 5 second transition
        self.previous_weather = "clear"
        
        # Weather particles
        self.weather_particles = []
        
        # Weather types and their effects
        self.weather_types = [
            "clear",    # No special effects
            "rain",     # Water+ Fire-
            "sunny",    # Light+ Dark-
            "windy",    # Air+ (range boost)
            "night",    # Dark+ Light-
            "storm"     # Air+ Earth+ (special effects)
        ]
        
        # Weather effect multipliers
        self.weather_effects = {
            "clear": {
                "description": "Normal conditions",
                "effects": {}  # No modifiers
            },
            "rain": {
                "description": "Water towers enhanced, Fire towers weakened",
                "effects": {
                    "Water": {"damage": 1.3, "cooldown": 0.8},
                    "Fire": {"damage": 0.8, "cooldown": 1.2}
                },
                "particle_rate": 30,
                "particle_color": (100, 100, 255),
                "background_mod": (0, 0, 50, 0)
            },
            "sunny": {
                "description": "Light towers enhanced, Darkness towers weakened",
                "effects": {
                    "Light": {"damage": 1.3, "range": 1.2},
                    "Darkness": {"damage": 0.8}
                },
                "particle_rate": 5,
                "particle_color": (255, 255, 180),
                "background_mod": (50, 50, 0, 0)
            },
            "windy": {
                "description": "Air towers gain range, projectiles affected by wind",
                "effects": {
                    "Air": {"range": 1.4}
                },
                "particle_rate": 15, 
                "particle_color": (200, 200, 200),
                "wind_direction": Vector2(1, 0.2),
                "wind_strength": 50,
                "background_mod": (20, 20, 20, 0)
            },
            "night": {
                "description": "Darkness towers enhanced, Light towers weakened",
                "effects": {
                    "Darkness": {"damage": 1.4, "range": 1.2},
                    "Light": {"damage": 0.7}
                },
                "particle_rate": 8,
                "particle_color": (100, 100, 150),
                "background_mod": (-50, -50, -50, 0)
            },
            "storm": {
                "description": "Random lightning strikes, Air & Earth towers enhanced",
                "effects": {
                    "Air": {"damage": 1.2, "cooldown": 0.8},
                    "Earth": {"damage": 1.2}
                },
                "particle_rate": 40,
                "particle_color": (180, 180, 255),
                "lightning_chance": 0.05,
                "lightning_damage": 30,
                "background_mod": (-20, -20, 30, 0)
            }
        }
    
    def update(self, dt):
        """Update the weather system"""
        self.weather_timer += dt
        
        # Check if it's time to change weather
        if self.weather_timer >= self.weather_duration:
            self.change_weather()
            self.weather_timer = 0
        
        # Update transition
        if self.transition_time < self.transition_duration:
            self.transition_time += dt
        
        # Update weather particles
        self.update_weather_particles(dt)
        
        # Apply special weather effects
        self.apply_weather_effects(dt)
    
    def change_weather(self):
        """Change to a new random weather type"""
        # Store previous weather
        self.previous_weather = self.current_weather
        
        # Select new weather (not the same as current)
        available_types = [w for w in self.weather_types if w != self.current_weather]
        self.current_weather = random.choice(available_types)
        
        # Reset transition
        self.transition_time = 0
        
        # Announce weather change
        weather_data = self.weather_effects[self.current_weather]
        self.game.ui.add_floating_text(
            self.game.screen_width * 0.5, 
            50, 
            f"Weather change: {self.current_weather.capitalize()} - {weather_data['description']}", 
            (255, 255, 255), 
            size=24, 
            lifetime=5.0
        )
    
    def update_weather_particles(self, dt):
        """Update and manage weather particles"""
        # Remove expired particles
        self.weather_particles = [p for p in self.weather_particles if p["life"] > 0]
        
        # Update existing particles
        for particle in self.weather_particles:
            particle["pos"].x += particle["vel"].x * dt
            particle["pos"].y += particle["vel"].y * dt
            particle["life"] -= dt
            
            # Apply wind if applicable
            if self.current_weather == "windy" and "wind_direction" in self.weather_effects[self.current_weather]:
                wind = self.weather_effects[self.current_weather]["wind_direction"] * self.weather_effects[self.current_weather]["wind_strength"]
                particle["vel"] += wind * dt
        
        # Add new particles based on weather
        if self.current_weather in self.weather_effects and "particle_rate" in self.weather_effects[self.current_weather]:
            rate = self.weather_effects[self.current_weather]["particle_rate"]
            color = self.weather_effects[self.current_weather]["particle_color"]
            
            # Calculate spawn count based on rate and dt
            spawn_count = int(rate * dt)
            
            # Spawn particles
            for _ in range(spawn_count):
                if self.current_weather == "rain":
                    # Rain particles fall from top
                    pos = Vector2(
                        random.uniform(0, self.game.screen_width),
                        -10
                    )
                    vel = Vector2(random.uniform(-20, 20), random.uniform(200, 300))
                    self.add_weather_particle(pos, vel, color, random.uniform(0.5, 1.0))
                
                elif self.current_weather == "windy":
                    # Wind particles move horizontally
                    pos = Vector2(
                        -10 if random.random() < 0.5 else self.game.screen_width + 10,
                        random.uniform(0, self.game.screen_height)
                    )
                    wind_dir = self.weather_effects[self.current_weather]["wind_direction"]
                    vel = wind_dir * random.uniform(100, 200)
                    self.add_weather_particle(pos, vel, color, random.uniform(0.5, 2.0))
                
                elif self.current_weather == "sunny":
                    # Sunshine particles appear randomly
                    pos = Vector2(
                        random.uniform(0, self.game.screen_width),
                        random.uniform(0, self.game.screen_height * 0.3)
                    )
                    vel = Vector2(random.uniform(-10, 10), random.uniform(-5, 15))
                    self.add_weather_particle(pos, vel, color, random.uniform(1.0, 3.0), size=random.randint(2, 4))
                
                elif self.current_weather == "night":
                    # Night stars
                    pos = Vector2(
                        random.uniform(0, self.game.screen_width),
                        random.uniform(0, self.game.screen_height * 0.5)
                    )
                    vel = Vector2(0, 0)
                    self.add_weather_particle(pos, vel, color, random.uniform(2.0, 5.0), size=random.randint(1, 3))
                
                elif self.current_weather == "storm":
                    # Storm raindrops and occasional lightning
                    pos = Vector2(
                        random.uniform(0, self.game.screen_width),
                        -10
                    )
                    vel = Vector2(random.uniform(-40, 40), random.uniform(250, 350))
                    self.add_weather_particle(pos, vel, color, random.uniform(0.3, 0.8))
    
    def add_weather_particle(self, pos, vel, color, life, size=2):
        """Add a new weather particle"""
        self.weather_particles.append({
            "pos": pos,
            "vel": vel,
            "color": color,
            "life": life,
            "size": size
        })
    
    def apply_weather_effects(self, dt):
        """Apply special effects based on current weather"""
        # Apply global tower effects
        self.apply_tower_effects()
        
        # Apply special effects for storm weather (lightning strikes)
        if self.current_weather == "storm" and random.random() < self.weather_effects[self.current_weather]["lightning_chance"] * dt:
            self.create_lightning_strike()
    
    def apply_tower_effects(self):
        """Apply weather effects to towers"""
        # Get current weather effects
        weather_data = self.weather_effects[self.current_weather]
        
        if "effects" not in weather_data:
            return
        
        # Apply effects to all towers
        for tower in self.game.towers:
            # Skip towers that were already affected
            if hasattr(tower, "weather_affected") and tower.weather_affected == self.current_weather:
                continue
            
            # Reset previous weather effects
            if hasattr(tower, "orig_damage") and hasattr(tower, "weather_affected"):
                # Restore original values
                tower.damage = tower.orig_damage
                tower.cooldown = tower.orig_cooldown
                tower.range = tower.orig_range
            
            # Store original values
            if not hasattr(tower, "orig_damage"):
                tower.orig_damage = tower.damage
                tower.orig_cooldown = tower.cooldown
                tower.orig_range = tower.range
            
            # Apply new effects if tower type is affected
            if tower.tower_type in weather_data["effects"]:
                effects = weather_data["effects"][tower.tower_type]
                
                if "damage" in effects:
                    tower.damage = tower.orig_damage * effects["damage"]
                
                if "cooldown" in effects:
                    tower.cooldown = tower.orig_cooldown * effects["cooldown"]
                
                if "range" in effects:
                    tower.range = tower.orig_range * effects["range"]
            
            # Mark tower as affected by current weather
            tower.weather_affected = self.current_weather
    
    def create_lightning_strike(self):
        """Create a lightning strike at a random position during a storm"""
        # Choose random position
        pos = Vector2(
            random.uniform(0, self.game.screen_width),
            random.uniform(0, self.game.screen_height)
        )
        
        # Flash screen
        self.game.screen_flash = 0.2
        self.game.screen_flash_color = (200, 200, 255)
        
        # Add particle effects
        for _ in range(20):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(50, 200)
            vel = Vector2(math.cos(angle) * speed, math.sin(angle) * speed)
            self.game.particle_system.add_particle(
                pos.x, pos.y,
                vel.x, vel.y,
                (200, 200, 255),
                random.uniform(0.3, 0.8),
                size=random.randint(3, 6)
            )
        
        # Damage enemies in radius
        damage = self.weather_effects[self.current_weather]["lightning_damage"]
        for enemy in self.game.enemies:
            if enemy.pos.distance_to(pos) < 100:
                enemy.take_damage(damage, "energy")
        
        # Show floating text
        self.game.ui.add_floating_text(
            pos.x, pos.y, 
            f"Lightning Strike! ({damage})", 
            (200, 200, 255), 
            size=18, 
            lifetime=1.0
        )
    
    def get_background_color_mod(self):
        """Get the background color modification for current weather"""
        if self.current_weather in self.weather_effects and "background_mod" in self.weather_effects[self.current_weather]:
            # Calculate transition progress
            if self.transition_time < self.transition_duration:
                progress = self.transition_time / self.transition_duration
                
                # Get previous color mod
                prev_mod = (0, 0, 0, 0)  # Default (no change)
                if self.previous_weather in self.weather_effects and "background_mod" in self.weather_effects[self.previous_weather]:
                    prev_mod = self.weather_effects[self.previous_weather]["background_mod"]
                
                # Get target color mod
                target_mod = self.weather_effects[self.current_weather]["background_mod"]
                
                # Interpolate
                r = prev_mod[0] + (target_mod[0] - prev_mod[0]) * progress
                g = prev_mod[1] + (target_mod[1] - prev_mod[1]) * progress
                b = prev_mod[2] + (target_mod[2] - prev_mod[2]) * progress
                a = prev_mod[3] + (target_mod[3] - prev_mod[3]) * progress
                
                return (r, g, b, a)
            else:
                return self.weather_effects[self.current_weather]["background_mod"]
        
        return (0, 0, 0, 0)  # No modification
    
    def render(self, surface):
        """Render weather effects"""
        # Render particles
        for particle in self.weather_particles:
            pygame.draw.circle(
                surface, 
                particle["color"], 
                (int(particle["pos"].x), int(particle["pos"].y)), 
                particle["size"]
            )
        
        # Render weather indicator in corner
        font = pygame.font.SysFont('arial', 16)
        weather_text = f"Weather: {self.current_weather.capitalize()}"
        text = font.render(weather_text, True, (255, 255, 255))
        surface.blit(text, (10, 10))
        
        # Draw weather icon
        icon_pos = (10 + text.get_width() + 10, 10)
        icon_size = 16
        
        if self.current_weather == "rain":
            pygame.draw.rect(surface, (100, 100, 255), (icon_pos[0], icon_pos[1], icon_size, icon_size))
        elif self.current_weather == "sunny":
            pygame.draw.circle(surface, (255, 255, 0), (icon_pos[0] + icon_size//2, icon_pos[1] + icon_size//2), icon_size//2)
        elif self.current_weather == "windy":
            for i in range(3):
                pygame.draw.line(surface, (200, 200, 200), 
                    (icon_pos[0], icon_pos[1] + i*5 + 3), 
                    (icon_pos[0] + icon_size, icon_pos[1] + i*5 + 3), 2)
        elif self.current_weather == "night":
            pygame.draw.circle(surface, (150, 150, 255), (icon_pos[0] + icon_size//2, icon_pos[1] + icon_size//2), icon_size//2)
        elif self.current_weather == "storm":
            pygame.draw.rect(surface, (100, 100, 200), (icon_pos[0], icon_pos[1], icon_size, icon_size))
            pygame.draw.line(surface, (255, 255, 100), 
                (icon_pos[0] + icon_size//2, icon_pos[1]), 
                (icon_pos[0] + 2, icon_pos[1] + icon_size), 2) 