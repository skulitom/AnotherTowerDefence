# Enhanced Tower System

## Overview

This tower system features a modular structure with unique magical effects and abilities for each elemental tower type. The implementation includes:

- Modular structure with a base class and specialized tower classes
- Magical effects for all elemental towers
- Unique visual effects and particle systems for each tower type
- Factory pattern for creating different tower types
- Special abilities that scale with tower upgrades

## Tower Types

### Fire Tower
- **Theme**: Fire and heat
- **Special Ability**: Creates floating fire orbs that enhance damage and can burst into flames at higher levels
- **Visual Effects**: Flame particles, ember trails, fire orbs, and heat distortion

### Water Tower
- **Theme**: Water and fluid dynamics
- **Special Ability**: Slows enemy movement with magical water and creates damaging whirlpools at higher levels
- **Visual Effects**: Water ripples, floating water orbs, splashes, and vortex effects

### Air Tower
- **Theme**: Wind and lightning
- **Special Ability**: Attacks multiple enemies with wind gusts and can summon lightning strikes at higher levels
- **Visual Effects**: Wind particles, cloud formations, lightning effects, and tornado formations

### Earth Tower
- **Theme**: Crystals and geological power
- **Special Ability**: Forms crystals that enhance damage and can cause eruptions that damage multiple enemies
- **Visual Effects**: Crystal formations, ground cracks, crystal eruptions, and floating stone circle

### Life Tower
- **Theme**: Nature and vitality
- **Special Ability**: Buffs nearby towers, increasing their damage output. At higher levels, it can heal player lives and generate gold.
- **Visual Effects**: Leaf particles, floating flowers, growing vines, and healing auras

### Darkness Tower
- **Theme**: Shadow and void
- **Special Ability**: Marks enemies to take increased damage from all towers. At higher levels, it can drain enemy health and stun targets.
- **Visual Effects**: Shadow tendrils, orbiting shadow orbs, shadow vortex, and dark purple particles

### Light Tower
- **Theme**: Radiance and illumination
- **Special Ability**: Reveals invisible enemies and deals extra damage to them. At higher levels, creates bursts of light that damage multiple enemies.
- **Visual Effects**: Light rays, orbiting light motes, revealing aura, and bright particle effects

## Usage

To create a tower, use the factory function `create_tower`:

```python
from game.towers import create_tower
from pygame.math import Vector2

# Create a fire tower at position (100, 200)
fire_tower = create_tower(Vector2(100, 200), "Fire")

# Create a water tower at position (300, 400)
water_tower = create_tower(Vector2(300, 400), "Water")

# Create an air tower at position (500, 300)
air_tower = create_tower(Vector2(500, 300), "Air")

# Create an earth tower at position (600, 200)
earth_tower = create_tower(Vector2(600, 200), "Earth")

# Create a life tower at position (400, 500)
life_tower = create_tower(Vector2(400, 500), "Life")

# Create a darkness tower at position (200, 500)
darkness_tower = create_tower(Vector2(200, 500), "Darkness")

# Create a light tower at position (200, 200)
light_tower = create_tower(Vector2(200, 200), "Light")
```

## Extending the System

To add a new tower type:

1. Create a new class that inherits from `BaseTower`
2. Implement the required methods (`initialize`, `upgrade_special`, etc.)
3. Add unique visual effects and special abilities
4. Update `TowerFactory` to recognize the new tower type
5. Add the new tower to the imports in `__init__.py` 