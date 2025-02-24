import pygame
from game.settings import tower_types


def load_assets():
    assets = {"towers": {}, "enemy": None, "projectile": None}
    for tower_type in tower_types:
        try:
            assets["towers"][tower_type] = pygame.image.load("assets/" + tower_type.lower() + ".png").convert_alpha()
        except Exception:
            assets["towers"][tower_type] = None
    try:
        assets["enemy"] = pygame.image.load("assets/enemy.png").convert_alpha()
    except Exception:
        assets["enemy"] = None
    try:
        assets["projectile"] = pygame.image.load("assets/projectile.png").convert_alpha()
    except Exception:
        assets["projectile"] = None
    return assets 