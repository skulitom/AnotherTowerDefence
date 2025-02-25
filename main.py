"""
Element Crystal Tower Defense

A tower defense game with elemental towers and enemies.
"""
import pygame
import sys

from game.core.game_loop import GameLoop
from game.managers.game_manager import GameManager

def main():
    """Main entry point for the game"""
    # Initialize pygame
    pygame.init()
    
    # Create game manager
    game_manager = GameManager()
    
    # Create game loop
    game_loop = GameLoop(game_manager)
    
    # Start the game
    try:
        game_loop.start()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    main() 