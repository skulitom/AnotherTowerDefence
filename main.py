"""
Element Crystal Tower Defense

A tower defense game with elemental towers and enemies.
Features:
- Elemental tower synergies
- Dynamic weather system
- Tower evolution specializations
- Unique enemy types and abilities
"""
import pygame
import sys
import traceback

from game.core.game_loop import GameLoop
from game.managers.game_manager import GameManager

def main():
    """Main entry point for the game"""
    # Initialize pygame
    pygame.init()
    
    # Create game manager with all our new systems
    game_manager = GameManager()
    
    # Enable debug mode for development
    game_manager.debug_mode = True
    
    # Create game loop
    game_loop = GameLoop(game_manager)
    
    # Show welcome message
    print("Element Crystal Tower Defense")
    print("----------------------------")
    print("Controls:")
    print("  1-7: Select tower type")
    print("  P: Toggle tower placement mode")
    print("  Click: Select tower / Place tower (when in placement mode)")
    print("  Q/W/E/R: Upgrade tower damage/range/speed/special")
    print("  X: Sell tower")
    print("  Space: Start next wave")
    print("  Mouse Wheel: Zoom in/out")
    print("  Middle Mouse: Pan camera")
    print("----------------------------")
    print("New Features:")
    print("  - Elemental Synergies: Place compatible towers near each other")
    print("  - Dynamic Weather: Affects different tower types")
    print("  - Tower Evolution: Upgrade towers to specialized forms")
    
    # Start the game
    try:
        game_loop.start()
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
    finally:
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    main() 