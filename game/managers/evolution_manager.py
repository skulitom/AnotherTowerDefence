"""
Evolution Manager - Handles tower evolutions and specializations
"""
import pygame
from pygame import Vector2
import random

class EvolutionManager:
    def __init__(self, game_manager):
        """Initialize the evolution manager"""
        self.game = game_manager
        
        # Define evolution paths for each tower type
        self.evolution_paths = {
            "Fire": {
                "requirements": {
                    "kills": 20,
                    "level": 2  # Tower upgrade level
                },
                "options": [
                    {
                        "name": "Volcano",
                        "description": "Deals periodic AOE damage around the tower",
                        "color": (180, 30, 0),
                        "damage_multiplier": 1.5,
                        "cooldown_multiplier": 1.1,
                        "range_multiplier": 0.9,
                        "special_ability": "eruption",
                        "eruption_damage": 30,
                        "eruption_radius": 120,
                        "eruption_interval": 5.0
                    },
                    {
                        "name": "Meteor",
                        "description": "Long range with heavy damage but slower firing",
                        "color": (200, 50, 0),
                        "damage_multiplier": 2.2,
                        "cooldown_multiplier": 1.8,
                        "range_multiplier": 1.4,
                        "special_ability": "impact",
                        "impact_aoe": 80,
                        "impact_damage": 15
                    },
                    {
                        "name": "Phoenix",
                        "description": "Attacks multiple targets with burning trails",
                        "color": (255, 60, 0),
                        "damage_multiplier": 0.8,
                        "cooldown_multiplier": 0.7,
                        "range_multiplier": 1.2,
                        "special_ability": "multishot",
                        "multishot_count": 3,
                        "burn_damage": 8,
                        "burn_duration": 3.0
                    }
                ]
            },
            "Water": {
                "requirements": {
                    "kills": 20,
                    "level": 2
                },
                "options": [
                    {
                        "name": "Glacier",
                        "description": "Chance to freeze enemies completely",
                        "color": (0, 100, 180),
                        "damage_multiplier": 1.2,
                        "cooldown_multiplier": 1.4,
                        "range_multiplier": 1.0,
                        "special_ability": "freeze",
                        "freeze_chance": 0.25,
                        "freeze_duration": 2.0
                    },
                    {
                        "name": "Tsunami",
                        "description": "Pushes enemies back with waves",
                        "color": (0, 150, 220),
                        "damage_multiplier": 1.0,
                        "cooldown_multiplier": 1.2,
                        "range_multiplier": 1.3,
                        "special_ability": "push",
                        "push_distance": 100,
                        "push_cooldown": 3.0
                    },
                    {
                        "name": "Whirlpool",
                        "description": "Creates vortex that pulls enemies toward it",
                        "color": (0, 180, 255),
                        "damage_multiplier": 0.9,
                        "cooldown_multiplier": 0.8,
                        "range_multiplier": 1.1,
                        "special_ability": "vortex",
                        "vortex_radius": 150,
                        "vortex_strength": 50
                    }
                ]
            },
            "Air": {
                "requirements": {
                    "kills": 20,
                    "level": 2
                },
                "options": [
                    {
                        "name": "Tornado",
                        "description": "Spins enemies around, disorienting them",
                        "color": (180, 220, 255),
                        "damage_multiplier": 0.8,
                        "cooldown_multiplier": 0.6,
                        "range_multiplier": 1.2,
                        "special_ability": "spin",
                        "spin_duration": 2.0,
                        "spin_radius": 100
                    },
                    {
                        "name": "Lightning",
                        "description": "Chains electricity between enemies",
                        "color": (160, 160, 255),
                        "damage_multiplier": 1.4,
                        "cooldown_multiplier": 1.2,
                        "range_multiplier": 0.9,
                        "special_ability": "super_chain",
                        "chain_count": 5,
                        "chain_damage_falloff": 0.8
                    },
                    {
                        "name": "Cyclone",
                        "description": "Rapid-fire that speeds up over time",
                        "color": (200, 230, 255),
                        "damage_multiplier": 0.6,
                        "cooldown_multiplier": 0.9,
                        "range_multiplier": 1.0,
                        "special_ability": "accelerate",
                        "max_acceleration": 0.3,  # Final cooldown is 30% of original
                        "acceleration_rate": 0.05  # 5% faster per second
                    }
                ]
            },
            "Earth": {
                "requirements": {
                    "kills": 20,
                    "level": 2
                },
                "options": [
                    {
                        "name": "Mountain",
                        "description": "High damage with knockback effect",
                        "color": (120, 80, 40),
                        "damage_multiplier": 1.8,
                        "cooldown_multiplier": 1.6,
                        "range_multiplier": 0.9,
                        "special_ability": "knockback",
                        "knockback_distance": 80
                    },
                    {
                        "name": "Crystal",
                        "description": "Projectiles split on impact",
                        "color": (170, 150, 220),
                        "damage_multiplier": 1.0,
                        "cooldown_multiplier": 1.3,
                        "range_multiplier": 1.1,
                        "special_ability": "shatter",
                        "shard_count": 4,
                        "shard_damage": 10,
                        "shard_range": 100
                    },
                    {
                        "name": "Golem",
                        "description": "Summons temporary stone minions",
                        "color": (100, 80, 60),
                        "damage_multiplier": 1.2,
                        "cooldown_multiplier": 1.5,
                        "range_multiplier": 1.0,
                        "special_ability": "summon",
                        "summon_interval": 10.0,
                        "summon_count": 2,
                        "summon_duration": 8.0,
                        "summon_damage": 15
                    }
                ]
            },
            "Darkness": {
                "requirements": {
                    "kills": 20,
                    "level": 2
                },
                "options": [
                    {
                        "name": "Void",
                        "description": "Creates black holes that damage over time",
                        "color": (80, 0, 120),
                        "damage_multiplier": 1.3,
                        "cooldown_multiplier": 1.5,
                        "range_multiplier": 0.9,
                        "special_ability": "black_hole",
                        "black_hole_radius": 80,
                        "black_hole_damage": 5,
                        "black_hole_duration": 4.0
                    },
                    {
                        "name": "Shadow",
                        "description": "Curses enemies to take more damage from all sources",
                        "color": (100, 0, 100),
                        "damage_multiplier": 0.9,
                        "cooldown_multiplier": 1.0,
                        "range_multiplier": 1.2,
                        "special_ability": "curse",
                        "curse_multiplier": 1.5,
                        "curse_duration": 5.0
                    },
                    {
                        "name": "Reaper",
                        "description": "Instantly kills low health enemies",
                        "color": (80, 0, 80),
                        "damage_multiplier": 1.1,
                        "cooldown_multiplier": 1.2,
                        "range_multiplier": 0.8,
                        "special_ability": "execute",
                        "execute_threshold": 0.2  # 20% health
                    }
                ]
            },
            "Light": {
                "requirements": {
                    "kills": 20,
                    "level": 2
                },
                "options": [
                    {
                        "name": "Solar",
                        "description": "Deals increased damage to stronger enemies",
                        "color": (255, 200, 0),
                        "damage_multiplier": 1.0,
                        "cooldown_multiplier": 1.0,
                        "range_multiplier": 1.2,
                        "special_ability": "sunfire",
                        "damage_scale_factor": 2.0  # More damage to higher health enemies
                    },
                    {
                        "name": "Radiance",
                        "description": "Damages all enemies in range",
                        "color": (255, 220, 50),
                        "damage_multiplier": 0.8,
                        "cooldown_multiplier": 1.1,
                        "range_multiplier": 1.0,
                        "special_ability": "pulse",
                        "pulse_damage": 15,
                        "pulse_interval": 2.0
                    },
                    {
                        "name": "Prismatic",
                        "description": "Attacks with all elements",
                        "color": (200, 200, 200),
                        "damage_multiplier": 1.1,
                        "cooldown_multiplier": 1.3,
                        "range_multiplier": 0.9,
                        "special_ability": "elemental",
                        "element_types": ["fire", "water", "air", "earth", "darkness"],
                        "element_chance": 0.2  # Chance for each element effect
                    }
                ]
            },
            "Life": {
                "requirements": {
                    "kills": 20,
                    "level": 2
                },
                "options": [
                    {
                        "name": "Nature",
                        "description": "Spawns plants that attack nearby enemies",
                        "color": (0, 180, 0),
                        "damage_multiplier": 0.7,
                        "cooldown_multiplier": 1.0,
                        "range_multiplier": 1.1,
                        "special_ability": "plant",
                        "plant_count": 3,
                        "plant_damage": 8,
                        "plant_duration": 10.0
                    },
                    {
                        "name": "Angel",
                        "description": "Heals player and provides damage shield",
                        "color": (255, 200, 220),
                        "damage_multiplier": 0.9,
                        "cooldown_multiplier": 1.2,
                        "range_multiplier": 1.0,
                        "special_ability": "shield",
                        "shield_amount": 10,
                        "shield_interval": 15.0,
                        "heal_amount": 5,
                        "heal_interval": 5.0
                    },
                    {
                        "name": "Druid",
                        "description": "Transforms enemies into smaller, weaker versions",
                        "color": (150, 210, 150),
                        "damage_multiplier": 1.0,
                        "cooldown_multiplier": 1.4,
                        "range_multiplier": 0.8,
                        "special_ability": "transform",
                        "transform_chance": 0.2,
                        "health_reduction": 0.5  # 50% of original health
                    }
                ]
            }
        }
    
    def can_evolve(self, tower):
        """Check if a tower can be evolved"""
        # Skip towers that are already evolved
        if hasattr(tower, "evolved") and tower.evolved:
            return False
        
        # Check if evolution paths exist for this tower type
        if tower.tower_type not in self.evolution_paths:
            return False
        
        # Get requirements for this tower type
        requirements = self.evolution_paths[tower.tower_type]["requirements"]
        
        # Check kill count
        if not hasattr(tower, "kills") or tower.kills < requirements["kills"]:
            return False
        
        # Check upgrade level (simplified - in real game would check specific upgrades)
        if not hasattr(tower, "upgrade_level") or tower.upgrade_level < requirements["level"]:
            return False
        
        return True
    
    def get_evolution_options(self, tower):
        """Get available evolution options for a tower"""
        if not self.can_evolve(tower):
            return []
        
        return self.evolution_paths[tower.tower_type]["options"]
    
    def evolve_tower(self, tower, evolution_index):
        """Evolve a tower to a new specialized form"""
        if not self.can_evolve(tower):
            return False
        
        # Get evolution data
        evolution_options = self.evolution_paths[tower.tower_type]["options"]
        if evolution_index < 0 or evolution_index >= len(evolution_options):
            return False
        
        evolution_data = evolution_options[evolution_index]
        
        # Store original values if not already stored
        if not hasattr(tower, "original_damage"):
            tower.original_damage = tower.damage
            tower.original_cooldown = tower.cooldown
            tower.original_range = tower.range
        
        # Apply evolution stats
        tower.damage = tower.original_damage * evolution_data["damage_multiplier"]
        tower.cooldown = tower.original_cooldown * evolution_data["cooldown_multiplier"]
        tower.range = tower.original_range * evolution_data["range_multiplier"]
        
        # Apply evolution special ability
        tower.evolution_special = evolution_data["special_ability"]
        tower.evolution_data = evolution_data
        
        # Mark as evolved
        tower.evolved = True
        tower.evolution_name = evolution_data["name"]
        tower.color = evolution_data["color"]
        
        # Visual feedback
        self.game.particle_system.create_explosion(
            tower.pos.x, tower.pos.y, 
            count=30, 
            color=tower.color, 
            min_speed=50, max_speed=150, 
            lifetime=1.0,
            size_range=(3, 8)
        )
        
        # Show notification
        self.game.ui.add_floating_text(
            tower.pos.x, tower.pos.y - 30,
            f"Evolved to {evolution_data['name']}!",
            tower.color,
            size=18,
            lifetime=3.0
        )
        
        return True
    
    def apply_evolution_effects(self, tower, dt, target=None, projectile=None):
        """Apply evolution-specific effects during tower attacks"""
        if not hasattr(tower, "evolved") or not tower.evolved:
            return
        
        special = tower.evolution_special
        data = tower.evolution_data
        
        # Different effects based on evolution type
        if special == "eruption" and hasattr(tower, "eruption_timer"):
            tower.eruption_timer -= dt
            if tower.eruption_timer <= 0:
                # Reset timer
                tower.eruption_timer = data["eruption_interval"]
                
                # Create eruption effect
                self.game.particle_system.create_explosion(
                    tower.pos.x, tower.pos.y,
                    count=20,
                    color=tower.color,
                    min_speed=30, max_speed=100,
                    lifetime=1.0
                )
                
                # Damage enemies in radius
                for enemy in self.game.enemies:
                    if enemy.pos.distance_to(tower.pos) <= data["eruption_radius"]:
                        enemy.take_damage(data["eruption_damage"], "fire")
        
        elif special == "impact" and projectile and projectile.hit:
            # AOE impact damage
            impact_pos = projectile.pos
            for enemy in self.game.enemies:
                if enemy != target and enemy.pos.distance_to(impact_pos) <= data["impact_aoe"]:
                    enemy.take_damage(data["impact_damage"], "fire")
                    
                    # Visual effect
                    self.game.particle_system.add_particle(
                        enemy.pos.x, enemy.pos.y,
                        0, 0,
                        tower.color,
                        0.3,
                        size=5
                    )
        
        elif special == "multishot" and target and not projectile:
            # Find additional targets
            additional_targets = []
            for enemy in self.game.enemies:
                if enemy != target and enemy.pos.distance_to(tower.pos) <= tower.range:
                    additional_targets.append(enemy)
                    if len(additional_targets) >= data["multishot_count"] - 1:
                        break
            
            # Fire at additional targets
            for add_target in additional_targets:
                self.game.create_projectile(tower, add_target)
        
        # Initialize timers for periodic abilities on first call
        if special == "eruption" and not hasattr(tower, "eruption_timer"):
            tower.eruption_timer = data["eruption_interval"]
    
    def render_evolution_ui(self, surface, tower, ui_rect):
        """Render UI for tower evolution options"""
        if not self.can_evolve(tower):
            return
        
        options = self.get_evolution_options(tower)
        font = pygame.font.SysFont('arial', 16)
        title_font = pygame.font.SysFont('arial', 18, bold=True)
        
        # Draw title
        title = title_font.render("Evolution Options", True, (255, 255, 255))
        surface.blit(title, (ui_rect.x + 10, ui_rect.y + 10))
        
        # Draw options
        for i, option in enumerate(options):
            y_pos = ui_rect.y + 40 + i * 80
            
            # Draw option box
            option_rect = pygame.Rect(ui_rect.x + 10, y_pos, ui_rect.width - 20, 70)
            pygame.draw.rect(surface, (50, 50, 50), option_rect)
            pygame.draw.rect(surface, option["color"], option_rect, 2)
            
            # Draw name
            name_text = font.render(option["name"], True, (255, 255, 255))
            surface.blit(name_text, (option_rect.x + 10, option_rect.y + 5))
            
            # Draw description (wrapped)
            desc = option["description"]
            words = desc.split()
            line = ""
            line_height = font.get_height()
            y_offset = 25
            
            for word in words:
                test_line = line + word + " "
                if font.size(test_line)[0] < option_rect.width - 20:
                    line = test_line
                else:
                    text = font.render(line, True, (200, 200, 200))
                    surface.blit(text, (option_rect.x + 10, option_rect.y + y_offset))
                    y_offset += line_height
                    line = word + " "
            
            if line:
                text = font.render(line, True, (200, 200, 200))
                surface.blit(text, (option_rect.x + 10, option_rect.y + y_offset))
            
            # Draw "Evolve" button
            button_rect = pygame.Rect(option_rect.x + option_rect.width - 70, option_rect.y + option_rect.height - 25, 60, 20)
            pygame.draw.rect(surface, (70, 70, 70), button_rect)
            pygame.draw.rect(surface, (150, 150, 150), button_rect, 1)
            
            button_text = font.render("Evolve", True, (255, 255, 255))
            text_x = button_rect.x + (button_rect.width - button_text.get_width()) // 2
            text_y = button_rect.y + (button_rect.height - button_text.get_height()) // 2
            surface.blit(button_text, (text_x, text_y))
            
            # Store button position for click handling
            if not hasattr(self, "evolution_buttons"):
                self.evolution_buttons = []
            
            # Ensure we don't add duplicates by clearing and re-adding
            if i == 0 and len(options) > 0:
                self.evolution_buttons = []
            
            self.evolution_buttons.append((button_rect, i)) 