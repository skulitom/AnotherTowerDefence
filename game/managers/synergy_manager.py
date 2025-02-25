"""
Synergy Manager - Handles elemental tower synergies and combinations
"""
import pygame
from pygame import Vector2
import math
import random

class SynergyManager:
    def __init__(self, game_manager):
        """Initialize the synergy manager"""
        self.game = game_manager
        self.active_synergies = {}  # {(tower1_id, tower2_id): {"type": synergy_type, "effect": effect_obj}}
        self.synergy_particles = []
        
        # Define synergy combinations and their effects
        self.synergy_types = {
            frozenset(["Fire", "Air"]): {
                "name": "Lightning Storm",
                "color": (255, 255, 0),
                "radius": 180,
                "effect": "area_damage",
                "damage": 15,
                "interval": 2.0,
                "description": "Creates periodic lightning strikes that damage all enemies in range"
            },
            frozenset(["Water", "Earth"]): {
                "name": "Mud Trap",
                "color": (139, 69, 19),
                "radius": 150,
                "effect": "super_slow",
                "slow_factor": 0.3,  # 70% slow
                "duration": 3.0,
                "description": "Creates a mud field that greatly slows enemies"
            },
            frozenset(["Light", "Darkness"]): {
                "name": "Twilight Field",
                "color": (186, 85, 211),
                "radius": 160,
                "effect": "damage_amp",
                "multiplier": 1.75,
                "description": "Amplifies damage of all towers in range"
            },
            frozenset(["Fire", "Water"]): {
                "name": "Steam Cloud",
                "color": (220, 220, 220),
                "radius": 170,
                "effect": "evasion",
                "evasion_chance": 0.3,  # 30% chance for enemies to miss
                "description": "Creates a dense steam that reduces enemy accuracy"
            },
            frozenset(["Life", "Earth"]): {
                "name": "Nature's Blessing",
                "color": (50, 205, 50),
                "radius": 200,
                "effect": "regen",
                "heal_amount": 5,
                "interval": 1.0,
                "description": "Regenerates player health slowly over time"
            }
        }
    
    def check_synergies(self):
        """Check for new potential synergies between towers"""
        # Clear obsolete synergies (if a tower was sold)
        self._clear_invalid_synergies()
        
        # Check all tower pairs for potential synergies
        checked_pairs = set()
        for tower1 in self.game.towers:
            for tower2 in self.game.towers:
                # Skip same tower or already checked pairs
                if tower1 == tower2 or frozenset([tower1.id, tower2.id]) in checked_pairs:
                    continue
                
                # Mark this pair as checked
                checked_pairs.add(frozenset([tower1.id, tower2.id]))
                
                # Check if towers are close enough for synergy (200px)
                distance = tower1.pos.distance_to(tower2.pos)
                if distance <= 200:
                    # Check if their elements can create a synergy
                    elements = frozenset([tower1.tower_type, tower2.tower_type])
                    if elements in self.synergy_types:
                        synergy_key = (tower1.id, tower2.id)
                        # If synergy doesn't exist yet, create it
                        if synergy_key not in self.active_synergies:
                            self._create_synergy(tower1, tower2, self.synergy_types[elements])
    
    def _create_synergy(self, tower1, tower2, synergy_data):
        """Create a new active synergy between two towers"""
        synergy_key = (tower1.id, tower2.id)
        
        # Create synergy effect
        mid_point = (tower1.pos + tower2.pos) / 2
        
        # Store synergy data
        self.active_synergies[synergy_key] = {
            "type": synergy_data["name"],
            "effect_type": synergy_data["effect"],
            "position": mid_point,
            "radius": synergy_data["radius"],
            "color": synergy_data["color"],
            "tower1": tower1,
            "tower2": tower2,
            "data": synergy_data,
            "active_time": 0,
            "last_effect_time": 0
        }
        
        # Notify player
        self.game.ui.add_floating_text(
            mid_point.x, mid_point.y, 
            f"Synergy: {synergy_data['name']}", 
            synergy_data["color"], 
            size=20, 
            lifetime=3.0
        )
    
    def _clear_invalid_synergies(self):
        """Remove synergies that are no longer valid (towers sold or moved)"""
        invalid_keys = []
        
        for key, synergy in self.active_synergies.items():
            tower1_id, tower2_id = key
            
            # Check if both towers still exist
            tower1_exists = any(t.id == tower1_id for t in self.game.towers)
            tower2_exists = any(t.id == tower2_id for t in self.game.towers)
            
            if not (tower1_exists and tower2_exists):
                invalid_keys.append(key)
                continue
            
            # Get current tower objects
            tower1 = next(t for t in self.game.towers if t.id == tower1_id)
            tower2 = next(t for t in self.game.towers if t.id == tower2_id)
            
            # Check if they're still close enough
            distance = tower1.pos.distance_to(tower2.pos)
            if distance > 200:
                invalid_keys.append(key)
        
        # Remove invalid synergies
        for key in invalid_keys:
            del self.active_synergies[key]
    
    def update(self, dt):
        """Update all active synergies"""
        for synergy_key, synergy in self.active_synergies.items():
            synergy["active_time"] += dt
            
            # Create visual particles
            if random.random() < dt * 5:  # Spawn particles occasionally
                angle = random.uniform(0, math.pi * 2)
                distance = random.uniform(10, synergy["radius"] * 0.8)
                particle_pos = Vector2(
                    synergy["position"].x + math.cos(angle) * distance,
                    synergy["position"].y + math.sin(angle) * distance
                )
                
                # Add particle effect
                self.game.particles.add_particle_params(
                    Vector2(particle_pos.x, particle_pos.y),
                    synergy["color"],
                    (random.uniform(-10, 10), random.uniform(-10, 10)),
                    random.randint(3, 6),
                    random.uniform(0.5, 1.5)
                )
            
            # Apply synergy effects
            self._apply_synergy_effect(synergy, dt)
    
    def _apply_synergy_effect(self, synergy, dt):
        """Apply the effect of a synergy"""
        effect_type = synergy["effect_type"]
        position = synergy["position"]
        radius = synergy["radius"]
        
        # Check if enough time has passed for effects that have intervals
        if "interval" in synergy["data"]:
            if synergy["last_effect_time"] + synergy["data"]["interval"] > synergy["active_time"]:
                return
            synergy["last_effect_time"] = synergy["active_time"]
        
        # Different effects based on synergy type
        if effect_type == "area_damage":
            # Deal damage to all enemies in radius
            for enemy in self.game.enemies:
                if enemy.pos.distance_to(position) <= radius:
                    damage = synergy["data"]["damage"]
                    enemy.take_damage(damage, "energy")
                    # Visual feedback
                    self.game.particles.add_particle_params(
                        Vector2(enemy.pos.x, enemy.pos.y),
                        synergy["color"],
                        (0, 0),
                        10,
                        0.3
                    )
        
        elif effect_type == "super_slow":
            # Apply extra slow to enemies
            for enemy in self.game.enemies:
                if enemy.pos.distance_to(position) <= radius:
                    slow_factor = synergy["data"]["slow_factor"]
                    duration = synergy["data"]["duration"]
                    # Apply or refresh slow effect
                    enemy.status_effects["super_slow"] = {
                        "duration": duration,
                        "value": slow_factor
                    }
                    enemy.speed = enemy.base_speed * enemy.type_stats["speed_multiplier"] * slow_factor
        
        elif effect_type == "damage_amp":
            # Amplify tower damage
            multiplier = synergy["data"]["multiplier"]
            for tower in self.game.towers:
                if tower.pos.distance_to(position) <= radius:
                    # Apply damage multiplier attribute if it doesn't exist
                    if not hasattr(tower, "synergy_damage_multiplier"):
                        tower.synergy_damage_multiplier = multiplier
        
        elif effect_type == "evasion":
            # Make enemies in area have a chance to miss
            for enemy in self.game.enemies:
                if enemy.pos.distance_to(position) <= radius:
                    enemy.status_effects["evasion"] = {
                        "duration": 0.5,  # Constantly refresh while in area
                        "value": synergy["data"]["evasion_chance"]
                    }
        
        elif effect_type == "regen":
            # Heal player slowly
            if self.game.player_health < self.game.max_player_health:
                heal_amount = synergy["data"]["heal_amount"] * dt
                self.game.player_health = min(
                    self.game.player_health + heal_amount,
                    self.game.max_player_health
                )
    
    def render(self, surface, camera):
        """Render visual effects for synergies"""
        for synergy_key, synergy in self.active_synergies.items():
            # Get screen position
            screen_pos = camera.world_to_screen(synergy["position"])
            screen_radius = camera.zoom * synergy["radius"]
            
            # Draw circle with pulsating alpha
            alpha = 30 + 15 * math.sin(synergy["active_time"] * 2)
            color = synergy["color"] + (alpha,)  # Add alpha to RGB
            
            # Create surface for transparent circle
            circle_surface = pygame.Surface((screen_radius * 2, screen_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(circle_surface, color, (screen_radius, screen_radius), screen_radius)
            
            # Draw on main surface
            surface.blit(circle_surface, (screen_pos[0] - screen_radius, screen_pos[1] - screen_radius))
            
            # Draw connection line between towers
            tower1_screen_pos = camera.world_to_screen(synergy["tower1"].pos)
            tower2_screen_pos = camera.world_to_screen(synergy["tower2"].pos)
            pygame.draw.line(surface, synergy["color"], tower1_screen_pos, tower2_screen_pos, 2)
            
            # Draw synergy name
            font = pygame.font.SysFont('arial', 14)
            text = font.render(synergy["type"], True, (255, 255, 255))
            surface.blit(text, (screen_pos[0] - text.get_width() // 2, screen_pos[1] - 10)) 