import pygame


def draw_gradient_background(surface, top_color, bottom_color):
    height = surface.get_height()
    for y in range(height):
        ratio = y / height
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (surface.get_width(), y))


def draw_gradient_rect(surface, rect, top_color, bottom_color):
    temp_surface = pygame.Surface((rect.width, rect.height))
    draw_gradient_background(temp_surface, top_color, bottom_color)
    surface.blit(temp_surface, (rect.x, rect.y)) 