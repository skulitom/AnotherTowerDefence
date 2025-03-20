"""
Wave Manager - Handles enemy wave generation and progression
"""
import random
from game.settings import wave_templates, enemy_types
from game.enemy import Enemy
from game.ui import FloatingText

class WaveManager:
    def __init__(self, game_manager):
        """Initialize the wave manager"""
        self.game = game_manager
        self.current_wave_enemies = []
        self.current_wave_config = None
        self.next_enemy_spawn = 0
        self.wave_progress = 0.0
    
    def start_wave(self):
        """Start the next wave of enemies"""
        # Increment wave counter
        self.game.wave += 1
        
        # Clear any remaining enemies from previous wave's queue
        self.current_wave_enemies.clear()
        
        # Do NOT generate a new path for each wave
        # Only update the paths for any existing enemies
        for enemy in self.game.enemies:
            enemy.path = self.game.path_points
        
        # Get wave configuration
        if self.game.wave <= len(wave_templates):
            # Use predefined wave template
            self.current_wave_config = wave_templates[self.game.wave - 1]
        else:
            # Generate procedural wave for infinite levels
            self.current_wave_config = self.generate_procedural_wave(self.game.wave)
        
        # Create enemy list
        for enemy_type, count in self.current_wave_config["enemies"]:
            for _ in range(count):
                # Tuple of (enemy_type, wave_level)
                self.current_wave_enemies.append((enemy_type, self.game.wave))
        
        # Shuffle enemy order for variety
        random.shuffle(self.current_wave_enemies)
        
        # Set flag to enable wave processing
        self.game.wave_active = True
        
        # Reset spawn timer
        self.next_enemy_spawn = 0
    
    def generate_procedural_wave(self, wave_level):
        """
        Generate a procedural wave configuration for waves beyond predefined templates
        
        Args:
            wave_level: Current wave level
            
        Returns:
            Wave configuration dict similar to templates
        """
        # Base difficulty scaling factor
        difficulty = wave_level / 10
        
        # Spawn delay decreases with wave level (faster spawns)
        spawn_delay = max(0.3, 1.5 - (wave_level * 0.05))
        
        # Reward increases with wave level
        reward_bonus = 50 + wave_level * 50
        
        # Calculate total number of enemies based on wave level
        total_enemies = 8 + int(wave_level * 1.5)
        
        # Available enemy types based on wave progression
        available_enemies = ["Normal", "Fast", "Tank"]
        
        if wave_level >= 5:
            available_enemies.append("Healing")
        
        if wave_level >= 7:
            available_enemies.append("Invisible")
        
        # Add boss every 10 waves
        has_boss = wave_level % 10 == 0
        
        # Generate enemy distribution
        enemies = []
        
        # Add boss first if this is a boss wave
        if has_boss:
            boss_count = 1 + (wave_level // 30)  # More bosses at higher levels
            enemies.append(("Boss", boss_count))
            total_enemies -= boss_count * 3  # Bosses count as multiple enemies for balancing
        
        # Distribute remaining enemies among available types
        remaining = total_enemies
        while remaining > 0:
            enemy_type = random.choice(available_enemies)
            
            # Calculate appropriate count based on enemy type
            if enemy_type == "Tank":
                count = max(1, int(remaining * 0.2))
            elif enemy_type == "Healing" or enemy_type == "Invisible":
                count = max(1, int(remaining * 0.15))
            else:
                count = max(1, int(remaining * 0.3))
            
            # Ensure we don't exceed remaining count
            count = min(count, remaining)
            
            enemies.append((enemy_type, count))
            remaining -= count
        
        # Create and return the wave config
        return {
            "enemies": enemies,
            "spawn_delay": spawn_delay,
            "reward_bonus": reward_bonus
        }
    
    def update(self, dt):
        """Update wave progression"""
        # Check if we need to spawn more enemies
        if self.current_wave_enemies:
            self.next_enemy_spawn -= dt
            if self.next_enemy_spawn <= 0:
                enemy_type, wave_level = self.current_wave_enemies.pop(0)
                spawn_enemy = Enemy(self.game.path_points, enemy_type, wave_level)
                self.game.enemies.append(spawn_enemy)
                self.next_enemy_spawn = self.current_wave_config["spawn_delay"]
                
                # Add spawn effect
                self.game.particles.add_explosion(
                    spawn_enemy.pos.x, 
                    spawn_enemy.pos.y, 
                    spawn_enemy.color, 
                    count=10
                )
        
        # Update wave progress
        self.update_wave_progress()
        
        # Check if wave is complete
        if len(self.current_wave_enemies) == 0 and len(self.game.enemies) == 0:
            self.complete_wave()
    
    def update_wave_progress(self):
        """Update the wave progress indicator"""
        if self.current_wave_config:
            total_enemies = sum(count for _, count in self.current_wave_config["enemies"])
            enemies_left = len(self.current_wave_enemies) + len(self.game.enemies)
            self.wave_progress = 1.0 - (enemies_left / total_enemies)
        else:
            self.wave_progress = 0.0
    
    def complete_wave(self):
        """Handle wave completion"""
        self.game.wave_active = False
        
        # Add wave complete bonus
        if self.current_wave_config:
            bonus = self.current_wave_config.get("reward_bonus", 0)
            if bonus > 0:
                self.game.money += bonus
                self.game.floating_texts.append(
                    FloatingText(
                        f"Wave {self.game.wave} Complete! +${bonus}", 
                        (self.game.screen_width // 2, self.game.screen_height // 2 - 50),
                        (255, 255, 0), 
                        32, 
                        duration=2.0
                    )
                )
        
        # Clear wave configuration
        self.current_wave_config = None
        self.wave_progress = 0.0 