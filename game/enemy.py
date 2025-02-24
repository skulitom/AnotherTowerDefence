import pygame
from pygame.math import Vector2


class Enemy:
    def __init__(self, path_points):
        # Convert path points into Vector2 objects for easier math.
        self.path_points = [Vector2(p) for p in path_points]
        self.pos = self.path_points[0].copy()
        self.current_point_index = 0
        self.speed = 60  # pixels per second
        self.health = 100
        self.radius = 10  # for drawing enemy
        self.reached_end = False
        self.reward = 0

    def update(self, dt):
        if self.current_point_index < len(self.path_points) - 1:
            target = self.path_points[self.current_point_index + 1]
            direction = target - self.pos
            distance = direction.length()
            if distance != 0:
                direction = direction.normalize()
            travel = self.speed * dt
            if travel >= distance:
                self.pos = target.copy()
                self.current_point_index += 1
            else:
                self.pos += direction * travel
        else:
            self.reached_end = True 