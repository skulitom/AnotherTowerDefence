import pygame
from pygame.math import Vector2
from game.settings import tower_types
from game.projectile import Projectile


class Tower:
    def __init__(self, pos, tower_type):
        self.pos = Vector2(pos)
        stats = tower_types[tower_type]
        self.tower_type = tower_type
        self.color = stats["color"]
        self.range = stats["range"]
        self.damage = stats["damage"]
        self.cooldown = stats["cooldown"]
        self.bullet_speed = stats["bullet_speed"]
        self.time_since_last_shot = 0
        self.radius = 15  # for drawing tower
        self.buff_multiplier = 1.0
        self.current_damage = self.damage

    def update(self, dt, enemies, projectiles):
        self.time_since_last_shot += dt
        if self.tower_type == "Life":
            return  # Life towers only provide buffs.
        target = None
        for enemy in enemies:
            if (enemy.pos - self.pos).length() <= self.range:
                target = enemy
                break
        if target and self.time_since_last_shot >= self.cooldown:
            new_projectile = Projectile(self.pos, target, self.current_damage, self.bullet_speed, self.tower_type)
            projectiles.append(new_projectile)
            self.time_since_last_shot = 0 