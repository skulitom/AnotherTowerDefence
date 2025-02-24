import pygame
from pygame.math import Vector2
import random
from game.settings import tower_types


class Projectile:
    def __init__(self, pos, target, damage, bullet_speed, tower_type):
        self.pos = Vector2(pos)
        self.target = target  # Enemy instance reference
        self.damage = damage
        self.speed = bullet_speed
        self.radius = 5  # for drawing projectile
        self.active = True
        self.tower_type = tower_type
        self.trail = []

    def update(self, dt):
        if not self.active:
            return
        self.trail.append(Vector2(self.pos))
        if len(self.trail) > 10:
            self.trail.pop(0)
        # If target is gone, mark projectile inactive
        if self.target is None or self.target.health <= 0:
            self.active = False
            return
        # Recalculate direction toward the target (homing behavior)
        direction = self.target.pos - self.pos
        if direction.length() == 0:
            direction = Vector2(0, 0)
        else:
            direction = direction.normalize()
        self.pos += direction * self.speed * dt
        # If projectile is close enough to hit the enemy:
        if self.pos.distance_to(self.target.pos) < 8:
            self.target.health -= self.damage
            self.active = False 