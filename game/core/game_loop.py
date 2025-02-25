"""
Core game loop that handles the main update and render cycle
"""
import pygame
import sys

class GameLoop:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.clock = pygame.time.Clock()
        self.running = True
    
    def start(self):
        """Start the main game loop"""
        while self.running:
            # Calculate delta time
            dt = self.clock.tick(60) / 1000.0
            
            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.game_manager.handle_event(event)
            
            # Update game
            self.game_manager.update(dt)
            
            # Render
            self.game_manager.render()
            pygame.display.flip()
            
            # Check for game over
            if self.game_manager.is_game_over():
                self.game_manager.show_game_over()
                self.wait_for_restart_or_exit()
    
    def wait_for_restart_or_exit(self):
        """Wait for player to restart or exit the game"""
        waiting = True
        while waiting and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        waiting = False
                        self.running = False
                    elif event.key == pygame.K_SPACE:
                        # Reset game state
                        self.game_manager.reset()
                        waiting = False 