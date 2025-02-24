import pygame
import sys
import math
import random

from game.settings import tower_types
from game.enemy import Enemy
from game.tower import Tower
from game.projectile import Projectile
from game.assets import load_assets
from game.utils import draw_gradient_background, draw_gradient_rect


def main():
    pygame.init()
    screen_width, screen_height = 1400, 900
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Element Crystal Tower Defense (Enhanced UI)")
    clock = pygame.time.Clock()

    assets = load_assets()

    path_points = [(0, 200), (350, 200), (350, 650), (700, 650),
                   (700, 200), (1050, 200), (1050, 650), (1400, 650)]
    font = pygame.font.SysFont(None, 32)

    towers = []
    enemies = []
    projectiles = []

    lives = 10
    money = 100
    wave = 0
    current_tower_type = "Fire"

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    wave += 1
                    for i in range(5):
                        enemy = Enemy(path_points)
                        enemy.health = 100 * wave
                        enemy.speed = 60 + (wave - 1) * 5
                        enemy.reward = 20 * wave
                        enemy.pos.x -= i * 30
                        enemies.append(enemy)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    pos = pygame.mouse.get_pos()
                    tower_order = ["Fire", "Water", "Air", "Earth", "Darkness", "Light", "Life"]
                    button_width = 35
                    button_height = 35
                    gap = 10
                    start_x = 10 + 10
                    start_y = 10 + 140
                    selected = False
                    for i, t_type in enumerate(tower_order):
                        btn_rect = pygame.Rect(start_x + i * (button_width + gap), start_y, button_width, button_height)
                        if btn_rect.collidepoint(pos):
                            current_tower_type = t_type
                            selected = True
                            break
                    if not selected:
                        cost = tower_types[current_tower_type]["cost"]
                        if money >= cost:
                            money -= cost
                            towers.append(Tower(pos, current_tower_type))
                elif event.button == 3:
                    pos = pygame.mouse.get_pos()
                    for tower in towers:
                        if (tower.pos - pygame.Vector2(pos)).length() <= tower.radius:
                            upgrade_cost = 50
                            if money >= upgrade_cost:
                                money -= upgrade_cost
                                tower.damage += 5
                                tower.range += 10
                                tower.cooldown = max(0.2, tower.cooldown - 0.1)
                            break

        for tower in towers:
            if tower.tower_type != "Life":
                tower.buff_multiplier = 1.0
                for buff_tower in towers:
                    if buff_tower.tower_type == "Life":
                        if (tower.pos - buff_tower.pos).length() <= buff_tower.range:
                            tower.buff_multiplier *= 1.2
                tower.current_damage = tower.damage * tower.buff_multiplier

        for enemy in enemies[:]:
            enemy.update(dt)
            if enemy.reached_end:
                lives -= 1
                enemies.remove(enemy)
            elif enemy.health <= 0:
                money += enemy.reward
                enemies.remove(enemy)

        for projectile in projectiles[:]:
            projectile.update(dt)
            if not projectile.active:
                projectiles.remove(projectile)

        for tower in towers:
            tower.update(dt, enemies, projectiles)

        draw_gradient_background(screen, (20, 20, 40), (70, 70, 100))
        pygame.draw.lines(screen, (200, 200, 200), False, path_points, 5)

        for tower in towers:
            range_surf = pygame.Surface((tower.range * 2, tower.range * 2), pygame.SRCALPHA)
            pygame.draw.circle(range_surf, (255, 255, 255, 40), (tower.range, tower.range), tower.range)
            screen.blit(range_surf, (int(tower.pos.x - tower.range), int(tower.pos.y - tower.range)))
            tower_img = assets["towers"].get(tower.tower_type)
            if tower_img:
                img = pygame.transform.scale(tower_img, (tower.radius * 2, tower.radius * 2))
                screen.blit(img, (int(tower.pos.x) - tower.radius, int(tower.pos.y) - tower.radius))
            else:
                pygame.draw.circle(screen, tower.color, (int(tower.pos.x), int(tower.pos.y)), tower.radius)
            if tower.tower_type != "Life" and tower.buff_multiplier > 1.0:
                pygame.draw.circle(screen, (0, 255, 0), (int(tower.pos.x), int(tower.pos.y)), tower.radius + 5, 2)
            elif tower.tower_type == "Life":
                pulse = 3 * math.sin(pygame.time.get_ticks() / 200)
                pygame.draw.circle(screen, (255, 255, 255), (int(tower.pos.x), int(tower.pos.y)), int(tower.radius + 5 + pulse), 2)

        for enemy in enemies:
            if assets["enemy"]:
                enemy_img = pygame.transform.scale(assets["enemy"], (enemy.radius * 2, enemy.radius * 2))
                screen.blit(enemy_img, (int(enemy.pos.x) - enemy.radius, int(enemy.pos.y) - enemy.radius))
            else:
                pygame.draw.circle(screen, (0, 255, 0), (int(enemy.pos.x), int(enemy.pos.y)), enemy.radius)

        for projectile in projectiles:
            base_color = tower_types.get(projectile.tower_type, {}).get("color", (255, 255, 255))
            if assets["projectile"]:
                proj_img = pygame.transform.scale(assets["projectile"], (projectile.radius * 2, projectile.radius * 2))
                screen.blit(proj_img, (int(projectile.pos.x) - projectile.radius, int(projectile.pos.y) - projectile.radius))
            else:
                if projectile.tower_type == "Fire":
                    flicker_radius = projectile.radius + random.randint(0, 2)
                    flame_color = (255, random.randint(100, 150), 0)
                    pygame.draw.circle(screen, flame_color, (int(projectile.pos.x), int(projectile.pos.y)), flicker_radius)
                elif projectile.tower_type == "Water":
                    pygame.draw.circle(screen, base_color, (int(projectile.pos.x), int(projectile.pos.y)), projectile.radius)
                    pygame.draw.circle(screen, (200, 200, 255), (int(projectile.pos.x), int(projectile.pos.y)), projectile.radius + 3, 1)
                elif projectile.tower_type == "Earth":
                    pygame.draw.circle(screen, base_color, (int(projectile.pos.x), int(projectile.pos.y)), projectile.radius)
                    for offset in [(-3, -3), (3, -3), (-3, 3), (3, 3)]:
                        pygame.draw.circle(screen, (100, 50, 0), (int(projectile.pos.x) + offset[0], int(projectile.pos.y) + offset[1]), 1)
                elif projectile.tower_type == "Air":
                    pygame.draw.circle(screen, base_color, (int(projectile.pos.x), int(projectile.pos.y)), projectile.radius)
                    s = pygame.Surface((projectile.radius * 2, projectile.radius * 2), pygame.SRCALPHA)
                    pygame.draw.circle(s, (255, 255, 255, 100), (projectile.radius, projectile.radius), projectile.radius)
                    screen.blit(s, (int(projectile.pos.x) - projectile.radius, int(projectile.pos.y) - projectile.radius))
                elif projectile.tower_type == "Darkness":
                    pygame.draw.circle(screen, (50, 0, 50), (int(projectile.pos.x), int(projectile.pos.y)), projectile.radius + 2)
                    pygame.draw.circle(screen, base_color, (int(projectile.pos.x), int(projectile.pos.y)), projectile.radius)
                elif projectile.tower_type == "Light":
                    pygame.draw.circle(screen, base_color, (int(projectile.pos.x), int(projectile.pos.y)), projectile.radius)
                    pygame.draw.circle(screen, (255, 255, 200), (int(projectile.pos.x), int(projectile.pos.y)), projectile.radius + 4, 1)
                else:
                    pygame.draw.circle(screen, base_color, (int(projectile.pos.x), int(projectile.pos.y)), projectile.radius)

        stats_panel_rect = pygame.Rect(10, 10, 350, 180)
        draw_gradient_rect(screen, stats_panel_rect, (40, 40, 60), (70, 70, 90))
        pygame.draw.rect(screen, (200, 200, 200), stats_panel_rect, 2)
        stat_x = stats_panel_rect.x + 10
        stat_y = stats_panel_rect.y + 10
        tower_text = font.render("Tower: " + current_tower_type, True, (255, 255, 255))
        screen.blit(tower_text, (stat_x, stat_y))
        lives_text = font.render("Lives: " + str(lives), True, (255, 255, 255))
        screen.blit(lives_text, (stat_x, stat_y + 30))
        money_text = font.render("Money: $" + str(money), True, (255, 255, 255))
        screen.blit(money_text, (stat_x, stat_y + 60))
        wave_text = font.render("Wave: " + str(wave), True, (255, 255, 255))
        screen.blit(wave_text, (stat_x, stat_y + 90))

        tower_order = ["Fire", "Water", "Air", "Earth", "Darkness", "Light", "Life"]
        button_width = 35
        button_height = 35
        gap = 10
        start_x = stats_panel_rect.x + 10
        buttons_y = stats_panel_rect.y + 140
        for i, t_type in enumerate(tower_order):
            btn_rect = pygame.Rect(start_x + i * (button_width + gap), buttons_y, button_width, button_height)
            color = (255, 255, 255) if t_type == current_tower_type else (150, 150, 150)
            pygame.draw.rect(screen, color, btn_rect)
            if t_type in tower_types:
                inner_rect = btn_rect.inflate(-6, -6)
                pygame.draw.rect(screen, tower_types[t_type]["color"], inner_rect)

        instructions_text = font.render(
            "SPACE: New Wave | Left-click: Build Tower | Right-click: Upgrade Tower (-$50)", True, (255, 255, 255)
        )
        instructions_rect = instructions_text.get_rect(center=(screen_width // 2, screen_height - 20))
        screen.blit(instructions_text, instructions_rect)

        pygame.display.flip()

        if lives <= 0:
            game_over_text = font.render("Game Over!", True, (255, 0, 0))
            game_over_rect = game_over_text.get_rect(center=(screen_width // 2, screen_height // 2))
            screen.blit(game_over_text, game_over_rect)
            pygame.display.flip()
            pygame.time.wait(3000)
            running = False

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main() 