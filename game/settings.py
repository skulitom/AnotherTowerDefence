tower_types = {
    "Fire": {
        "color": (255, 0, 0),
        "range": 150,
        "damage": 20,
        "cooldown": 1.0,  
        "bullet_speed": 300,  
        "cost": 50,
        "special_ability": "burn",  # DoT effect
        "special_chance": 0.3,      # 30% chance to apply burn
        "special_damage": 5,        # Damage per tick
        "special_duration": 3.0,    # Duration in seconds
        "particle_color": (255, 100, 0),
        "description": "Deals damage and has a chance to burn enemies"
    },
    "Water": {
        "color": (0, 0, 255),
        "range": 150,
        "damage": 15,
        "cooldown": 0.8,
        "bullet_speed": 300,
        "cost": 40,
        "special_ability": "slow",  # Slows enemies
        "special_chance": 0.4,      # 40% chance to slow
        "special_amount": 0.5,      # Slow by 50%
        "special_duration": 2.0,    # Duration in seconds
        "particle_color": (100, 100, 255),
        "description": "Medium damage with chance to slow enemies"
    },
    "Air": {
        "color": (135, 206, 235),
        "range": 175,
        "damage": 10,
        "cooldown": 0.4,
        "bullet_speed": 350,
        "cost": 45,
        "special_ability": "chain",  # Chain lightning
        "special_chance": 0.25,      # 25% chance to chain
        "special_targets": 3,        # Number of additional targets
        "special_damage_falloff": 0.7, # Damage multiplier per chain
        "particle_color": (200, 230, 255),
        "description": "Rapid fire with chance for chain lightning"
    },
    "Earth": {
        "color": (139, 69, 19),
        "range": 200,
        "damage": 25,
        "cooldown": 1.5,
        "bullet_speed": 250,
        "cost": 60,
        "special_ability": "stun",   # Stuns enemies
        "special_chance": 0.2,       # 20% chance to stun
        "special_duration": 1.0,     # Duration in seconds
        "particle_color": (100, 70, 20),
        "description": "High damage with chance to stun enemies"
    },
    "Darkness": {
        "color": (128, 0, 128),
        "range": 150,
        "damage": 30,
        "cooldown": 1.4,
        "bullet_speed": 300,
        "cost": 55,
        "special_ability": "weaken", # Increases damage taken
        "special_chance": 0.3,       # 30% chance to weaken
        "special_amount": 1.5,       # 50% more damage
        "special_duration": 4.0,     # Duration in seconds
        "particle_color": (100, 0, 100),
        "description": "Deals high damage and can weaken enemies"
    },
    "Light": {
        "color": (255, 255, 0),
        "range": 175,
        "damage": 25,
        "cooldown": 0.6,
        "bullet_speed": 350,
        "cost": 50,
        "special_ability": "reveal",  # Reveal cloaked enemies
        "special_aoe": 100,           # Range of revealing effect
        "special_duration": 5.0,      # Duration in seconds
        "particle_color": (255, 255, 150),
        "description": "Good all-rounder and reveals invisible enemies"
    },
    "Life": {
        "color": (255, 105, 180),
        "range": 150,
        "damage": 15,
        "cooldown": 1.2,
        "bullet_speed": 300,
        "cost": 45,
        "special_ability": "buff",   # Buff nearby towers
        "buff_range": 200,           # Range of buff effect
        "buff_damage": 1.2,          # Damage multiplier
        "buff_cooldown": 0.8,        # Cooldown multiplier (lower is better)
        "particle_color": (255, 150, 200),
        "description": "Buffs nearby towers' damage and attack speed"
    }
}

# Enemy types with different properties
enemy_types = {
    "Normal": {
        "color": (0, 200, 0),
        "health_multiplier": 1.0,
        "speed_multiplier": 1.0,
        "reward_multiplier": 1.0,
        "special_ability": None
    },
    "Fast": {
        "color": (200, 200, 0),
        "health_multiplier": 0.7,
        "speed_multiplier": 1.5,
        "reward_multiplier": 1.2,
        "special_ability": None
    },
    "Tank": {
        "color": (100, 100, 100),
        "health_multiplier": 2.5,
        "speed_multiplier": 0.7,
        "reward_multiplier": 1.5,
        "special_ability": None
    },
    "Healing": {
        "color": (0, 200, 200),
        "health_multiplier": 1.2,
        "speed_multiplier": 0.9,
        "reward_multiplier": 1.7,
        "special_ability": "heal",
        "heal_amount": 5,
        "heal_radius": 80
    },
    "Invisible": {
        "color": (200, 200, 200),
        "health_multiplier": 0.8,
        "speed_multiplier": 1.1,
        "reward_multiplier": 1.8,
        "special_ability": "cloak",
        "cloak_duration": 3.0,
        "cloak_cooldown": 5.0
    },
    "Boss": {
        "color": (200, 0, 0),
        "health_multiplier": 10.0,
        "speed_multiplier": 0.5,
        "reward_multiplier": 5.0,
        "special_ability": "resist",
        "resist_amount": 0.5  # 50% damage resistance
    }
}

# Tower upgrade paths
upgrade_paths = {
    "damage": {
        "name": "Damage",
        "description": "Increases tower damage",
        "levels": [
            {"cost": 50, "multiplier": 1.2},
            {"cost": 100, "multiplier": 1.5},
            {"cost": 200, "multiplier": 2.0}
        ]
    },
    "range": {
        "name": "Range",
        "description": "Increases tower range",
        "levels": [
            {"cost": 40, "multiplier": 1.2},
            {"cost": 80, "multiplier": 1.4},
            {"cost": 160, "multiplier": 1.7}
        ]
    },
    "speed": {
        "name": "Attack Speed",
        "description": "Increases tower attack speed",
        "levels": [
            {"cost": 60, "multiplier": 0.8},  # Lower cooldown
            {"cost": 120, "multiplier": 0.6},
            {"cost": 240, "multiplier": 0.4}
        ]
    },
    "special": {
        "name": "Special",
        "description": "Enhances tower's special ability",
        "levels": [
            {"cost": 100, "multiplier": 1.5},
            {"cost": 200, "multiplier": 2.0},
            {"cost": 400, "multiplier": 3.0}
        ]
    }
}

# Wave configurations
wave_templates = [
    # Wave 1: Basic introduction
    {
        "enemies": [("Normal", 8)],
        "spawn_delay": 1.5,
        "reward_bonus": 50
    },
    # Wave 2: Introduces Fast enemies
    {
        "enemies": [("Normal", 6), ("Fast", 4)],
        "spawn_delay": 1.2,
        "reward_bonus": 75
    },
    # Wave 3: Introduces Tank enemies
    {
        "enemies": [("Normal", 8), ("Fast", 4), ("Tank", 2)],
        "spawn_delay": 1.0,
        "reward_bonus": 100
    },
    # Wave 4: Mix of types
    {
        "enemies": [("Normal", 10), ("Fast", 6), ("Tank", 4)],
        "spawn_delay": 0.9,
        "reward_bonus": 125
    },
    # Wave 5: Introduces Healing enemies
    {
        "enemies": [("Normal", 10), ("Fast", 6), ("Tank", 4), ("Healing", 2)],
        "spawn_delay": 0.8,
        "reward_bonus": 150
    },
    # Wave 6: Mix with Healing
    {
        "enemies": [("Normal", 12), ("Fast", 8), ("Tank", 6), ("Healing", 4)],
        "spawn_delay": 0.7,
        "reward_bonus": 200
    },
    # Wave 7: Introduces Invisible enemies
    {
        "enemies": [("Normal", 12), ("Fast", 8), ("Tank", 6), ("Healing", 4), ("Invisible", 2)],
        "spawn_delay": 0.7,
        "reward_bonus": 250
    },
    # Wave 8: Increased difficulty
    {
        "enemies": [("Normal", 15), ("Fast", 10), ("Tank", 8), ("Healing", 5), ("Invisible", 4)],
        "spawn_delay": 0.6,
        "reward_bonus": 300
    },
    # Wave 9: Pre-boss wave
    {
        "enemies": [("Normal", 15), ("Fast", 15), ("Tank", 10), ("Healing", 8), ("Invisible", 6)],
        "spawn_delay": 0.5,
        "reward_bonus": 400
    },
    # Wave 10: Boss wave
    {
        "enemies": [("Normal", 10), ("Fast", 10), ("Tank", 5), ("Healing", 5), ("Boss", 1)],
        "spawn_delay": 0.6,
        "reward_bonus": 500
    }
] 