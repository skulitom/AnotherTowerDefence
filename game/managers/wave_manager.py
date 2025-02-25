"""
Wave Manager - Handles enemy wave generation and progression
"""
import random
from game.settings import wave_templates
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
        
        # Get wave configuration
        wave_index = min(self.game.wave - 1, len(wave_templates) - 1)
        self.current_wave_config = wave_templates[wave_index]
        
        # Calculate wave scaling factor for games that go beyond predefined templates
        scaling = 1.0 + max(0, self.game.wave - len(wave_templates)) * 0.2
        
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
            total_enemies = len(self.current_wave_config["enemies"])
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
                        f"Wave Complete! +${bonus}", 
                        (self.game.screen_width // 2, self.game.screen_height // 2 - 50),
                        (255, 255, 0), 
                        32, 
                        duration=2.0
                    )
                )
        
        # Clear wave configuration
        self.current_wave_config = None
        self.wave_progress = 0.0 