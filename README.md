# Element Crystal Tower Defense

## Overview

**Element Crystal Tower Defense** is a tower defense game developed in Python using the Pygame library. Instead of traditional towers, you deploy various Element Crystals (Fire, Water, Air, Earth, Darkness, Light, and Life) to defend against waves of enemy bugs. Each crystal type has its own unique attributes and costs.

## Gameplay

In this game, you must strategically place and upgrade your Element Crystals to stop enemy bugs as they traverse a predetermined path. The game includes:

- **Multiple Tower Types:** Choose from seven different crystals, each with unique stats like range, damage, cooldown, and cost.
- **Waves of Enemies:** Press SPACE to spawn waves of enemy bugs with increasing difficulty. Each wave increases enemy health, speed, and rewards.
- **Currency System:** You start with a limited amount of money. Placing and upgrading towers deducts funds, while killing enemies rewards you with more money.
- **Tower Upgrades:** Right-click on a tower to upgrade it (for a fixed cost), which improves its damage, range, and shooting frequency.
- **Game Over:** Lose a life whenever an enemy reaches the end of the path, and the game ends when you run out of lives.

## Controls

- **1 - 7:** Switch the currently selected Element Crystal type.
  - 1: Fire
  - 2: Water
  - 3: Air
  - 4: Earth
  - 5: Darkness
  - 6: Light
  - 7: Life
- **SPACE:** Spawn a new wave of enemies.
- **Left-click:** Place a tower (if you have sufficient funds).
- **Right-click:** Upgrade an existing tower (costs \$50).
- **ESC:** Quit the game.

Note: Currently, only the main 7 types (Fire, Water, Air, Earth, Darkness, Light, and Life) are selectable using keys 1–7. The additional Element Crystal types listed below are envisioned for future updates and not yet mapped to controls.

## Element Crystal Types

The game features a variety of Element Crystal types. Though the current implementation includes 7 main types (Fire, Water, Air, Earth, Darkness, Light, and Life), this project envisions up to 50 unique Element Crystals. Below is a list of 50 distinct Element Crystal types that can be considered for future updates or custom modifications:

1. Fire  
2. Water  
3. Air  
4. Earth  
5. Darkness  
6. Light  
7. Life  
8. Metal  
9. Wood  
10. Ice  
11. Storm  
12. Nature  
13. Void  
14. Plasma  
15. Vapor  
16. Crystal  
17. Sand  
18. Magma  
19. Thunder  
20. Eclipse  
21. Radiance  
22. Gravity  
23. Quantum  
24. Neon  
25. Spirit  
26. Frost  
27. Breeze  
28. Torrent  
29. Spectrum  
30. Nova  
31. Cosmos  
32. Celestial  
33. Solar  
34. Lunar  
35. Mystic  
36. Inferno  
37. Glacier  
38. Arcane  
39. Obsidian  
40. Serpent  
41. Toxic  
42. Sandstorm  
43. Aurora  
44. Mirage  
45. Ironclad  
46. Whisper  
47. Tempest  
48. Aether  
49. Chronos  
50. Eternity

## Requirements

- **Python 3.x**
- **Pygame**  
  Install using:
  ```bash
  pip install pygame
  ```

## How to Run

1. Clone or download the repository.
2. Run the game by executing the following command in your terminal:
   ```bash
   python main.py
   ```
3. Enjoy defending your base from the invading enemy bugs!

## Future Improvements

- Adding more enemy types with unique abilities.
- Implementing advanced tower targeting algorithms.
- Graphical improvements and sound effects.
- Enhanced upgrade mechanics and game balancing.

## License

This project is open source. Feel free to modify and distribute it as needed. 