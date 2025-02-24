import pygame
import sys
import math
import random

from game.settings import tower_types, enemy_types, upgrade_paths, wave_templates
from game.enemy import Enemy
from game.tower import Tower
from game.projectile import Projectile
from game.assets import load_assets
from game.utils import draw_gradient_background, draw_gradient_rect, ParticleSystem, create_element_icon, draw_hp_bar, Camera
from game.ui import GameUI, FloatingText


def main():
    pygame.init()
    screen_width, screen_height = 1400, 900
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Element Crystal Tower Defense")
    clock = pygame.time.Clock()

    # Load assets
    assets = load_assets()

    # Create path for enemies
    path_points = [(0, 200), (350, 200), (350, 650), (700, 650),
                   (700, 200), (1050, 200), (1050, 650), (1400, 650)]
    
    # Create camera
    sidebar_width = 260
    gameplay_area = (0, 0, 1400, 900)  # Entire screen boundaries
    camera = Camera(screen_width, screen_height, gameplay_area)
    camera.x = 700  # Center the camera on the map
    camera.y = 450
    
    # Game objects
    towers = []
    enemies = []
    projectiles = []
    floating_texts = []
    
    # Particle systems for visual effects
    particles = ParticleSystem(max_particles=500)
    
    # Game state
    lives = 10
    money = 150
    wave = 0
    current_tower_type = "Fire"
    selected_tower = None
    hover_tower = None
    wave_active = False
    next_enemy_spawn = 0
    current_wave_config = None
    current_wave_enemies = []
    wave_progress = 0.0
    is_panning = False
    
    # New variables for drag-and-drop tower placement and panning
    is_shift_pressed = False
    dragging_tower = False
    tower_drag_start = None
    tower_preview_pos = None
    
    # Create UI
    ui = GameUI(screen_width, screen_height)
    
    # Main game loop
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        mouse_pos = pygame.mouse.get_pos()
        
        # Get current keyboard state for more reliable key detection
        keys = pygame.key.get_pressed()
        is_shift_pressed = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE and not wave_active:
                    current_wave_config = start_next_wave(wave, enemies, current_wave_enemies)
                    wave_active = True
                    wave += 1
                # Camera movement with arrow keys
                elif event.key == pygame.K_UP:
                    camera.move(0, -50)
                elif event.key == pygame.K_DOWN:
                    camera.move(0, 50)
                elif event.key == pygame.K_LEFT:
                    camera.move(-50, 0)
                elif event.key == pygame.K_RIGHT:
                    camera.move(50, 0)
                # Reset camera with R key
                elif event.key == pygame.K_r:
                    camera.x = 700
                    camera.y = 450
                    camera.zoom = 1.0
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check if mouse is in sidebar
                in_sidebar = mouse_pos[0] < sidebar_width or mouse_pos[0] > screen_width - sidebar_width
                
                if event.button == 2:  # Middle mouse button for panning
                    camera.start_drag(mouse_pos[0], mouse_pos[1])
                    is_panning = True
                elif event.button == 4:  # Mouse wheel up for zoom in
                    camera.zoom_at(mouse_pos[0], mouse_pos[1], 1.1)
                elif event.button == 5:  # Mouse wheel down for zoom out
                    camera.zoom_at(mouse_pos[0], mouse_pos[1], 0.9)
                elif event.button == 1:  # Left mouse button
                    if in_sidebar:
                        # Handle UI interaction
                        ui_result = ui.handle_event(event, {
                            "money": money,
                            "lives": lives,
                            "wave": wave,
                            "current_tower_type": current_tower_type,
                            "selected_tower": selected_tower,
                            "enemies_remaining": len(enemies)
                        })
                        
                        if ui_result["action"] == "select_tower":
                            current_tower_type = ui_result["target"]
                            selected_tower = None
                        elif ui_result["action"] == "upgrade" and selected_tower:
                            upgrade_type = ui_result["target"]
                            upgrade_cost = selected_tower.get_upgrade_cost(upgrade_type)
                            if money >= upgrade_cost:
                                money -= upgrade_cost
                                selected_tower.upgrade(upgrade_type)
                                floating_texts.append(
                                    FloatingText(f"Upgraded {upgrade_type}!", 
                                               (selected_tower.pos.x, selected_tower.pos.y - 30),
                                               (100, 255, 100), 20)
                                )
                        elif ui_result["action"] == "sell" and selected_tower:
                            # Calculate sell value (70% of investment)
                            base_cost = tower_types[selected_tower.tower_type]["cost"]
                            upgrade_cost = 0
                            for upgrade_type, level in selected_tower.upgrades.items():
                                for i in range(level):
                                    if i < len(upgrade_paths[upgrade_type]["levels"]):
                                        upgrade_cost += upgrade_paths[upgrade_type]["levels"][i]["cost"]
                            
                            sell_value = int((base_cost + upgrade_cost) * 0.7)
                            money += sell_value
                            
                            # Create a selling effect
                            particles.add_explosion(selected_tower.pos.x, selected_tower.pos.y, 
                                                  (255, 215, 0), count=30, size_range=(3, 8))
                            floating_texts.append(
                                FloatingText(f"+${sell_value}", 
                                           (selected_tower.pos.x, selected_tower.pos.y - 30),
                                           (255, 255, 0), 24)
                            )
                            
                            # Remove the tower
                            towers.remove(selected_tower)
                            selected_tower = None
                        elif ui_result["action"] == "start_wave" and not wave_active:
                            current_wave_config = start_next_wave(wave, enemies, current_wave_enemies)
                            wave_active = True
                            wave += 1
                    else:
                        # Direct mouse interaction with game
                        world_pos = pygame.Vector2(*camera.unapply(mouse_pos[0], mouse_pos[1]))
                        
                        # If shift is pressed, start panning with left mouse button
                        if is_shift_pressed:
                            camera.start_drag(mouse_pos[0], mouse_pos[1])
                            is_panning = True
                        else:
                            # Check if clicked on existing tower
                            tower_clicked = False
                            for tower in towers:
                                if (tower.pos - world_pos).length() <= tower.radius:
                                    selected_tower = tower
                                    tower_clicked = True
                                    break
                                    
                            # If no tower clicked, start dragging a new tower
                            if not tower_clicked:
                                cost = tower_types[current_tower_type]["cost"]
                                if money >= cost:
                                    dragging_tower = True
                                    tower_preview_pos = world_pos
                                else:
                                    floating_texts.append(
                                        FloatingText("Not enough money!", 
                                                   (world_pos.x, world_pos.y - 20),
                                                   (255, 100, 100), 20)
                                    )
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 2 or (event.button == 1 and is_panning):  # Mouse button released after panning
                    camera.end_drag()
                    is_panning = False
                elif event.button == 1 and dragging_tower:  # Complete tower placement
                    world_pos = pygame.Vector2(*camera.unapply(mouse_pos[0], mouse_pos[1]))
                    
                    # Check tower placement validity
                    valid_placement = True
                    cost = tower_types[current_tower_type]["cost"]
                    
                    # Check if too close to path
                    for i in range(len(path_points) - 1):
                        p1 = pygame.Vector2(path_points[i])
                        p2 = pygame.Vector2(path_points[i + 1])
                        dist = distance_to_line_segment(world_pos, p1, p2)
                        if dist < 40:  # Minimum distance from path
                            valid_placement = False
                            break
                    
                    # Check if too close to other towers
                    for tower in towers:
                        if (tower.pos - world_pos).length() < 40:
                            valid_placement = False
                            break
                    
                    if valid_placement and money >= cost:
                        money -= cost
                        new_tower = Tower(world_pos, current_tower_type)
                        towers.append(new_tower)
                        selected_tower = new_tower
                        
                        # Add build effect
                        particles.add_explosion(new_tower.pos.x, new_tower.pos.y, 
                                            tower_types[current_tower_type]["color"], 
                                            count=20, size_range=(2, 6))
                    elif not valid_placement:
                        floating_texts.append(
                            FloatingText("Invalid placement!", 
                                       (world_pos.x, world_pos.y - 20),
                                       (255, 100, 100), 20)
                        )
                    
                    dragging_tower = False
                    tower_preview_pos = None
                elif event.button == 3:  # Right click - deselect tower
                    selected_tower = None
                    dragging_tower = False
                    tower_preview_pos = None
            elif event.type == pygame.MOUSEMOTION:
                if is_panning:
                    camera.update_drag(mouse_pos[0], mouse_pos[1])
                elif dragging_tower:
                    # Update tower preview position
                    tower_preview_pos = pygame.Vector2(*camera.unapply(mouse_pos[0], mouse_pos[1]))
        
        # Direct check for shift+left mouse being held down (additional check for pan)
        mouse_buttons = pygame.mouse.get_pressed()
        # Make sure we detect when we should be panning
        if is_shift_pressed and mouse_buttons[0] and not dragging_tower:
            # If we're not already panning, start panning
            if not is_panning:
                camera.start_drag(mouse_pos[0], mouse_pos[1])
                is_panning = True
            else:
                # If we're already panning, update the drag continuously
                camera.update_drag(mouse_pos[0], mouse_pos[1])
        elif is_panning:
            # Stop panning if either shift or left mouse is released
            camera.end_drag()
            is_panning = False
        
        # Update camera position with keyboard if key is held down
        keys = pygame.key.get_pressed()
        camera_speed = 300 * dt
        if keys[pygame.K_UP]:
            camera.move(0, -camera_speed)
        if keys[pygame.K_DOWN]:
            camera.move(0, camera_speed)
        if keys[pygame.K_LEFT]:
            camera.move(-camera_speed, 0)
        if keys[pygame.K_RIGHT]:
            camera.move(camera_speed, 0)
        
        # Convert mouse position to world coordinates for game logic
        world_mouse_pos = pygame.Vector2(*camera.unapply(mouse_pos[0], mouse_pos[1]))
        
        # Check which tower is being hovered over
        hover_tower = None
        for tower in towers:
            if (tower.pos - world_mouse_pos).length() <= tower.radius:
                hover_tower = tower
                break
        
        # Update towers
        for tower in towers:
            # Apply buffs from Life towers
            if tower.tower_type != "Life":
                tower.buff_multiplier = 1.0
                for buff_tower in towers:
                    if buff_tower.tower_type == "Life":
                        buff_range = tower_types["Life"].get("buff_range", 200)
                        if (tower.pos - buff_tower.pos).length() <= buff_range:
                            tower.buff_multiplier *= tower_types["Life"].get("buff_damage", 1.2)
                tower.current_damage = tower.damage * tower.buff_multiplier
            
            # Update tower
            tower.update(dt, enemies, projectiles, particles)
        
        # Update enemies
        for enemy in enemies[:]:
            # Update enemy position
            enemy.update(dt, enemies)
            
            # Handle enemy reaching end of path
            if enemy.reached_end:
                lives -= 1
                enemies.remove(enemy)
                floating_texts.append(
                    FloatingText("-1 Life!", 
                               (enemy.pos.x, enemy.pos.y - 20),
                               (255, 100, 100), 24)
                )
                particles.add_explosion(enemy.pos.x, enemy.pos.y, (255, 0, 0), count=15)
            
            # Handle enemy death
            elif enemy.health <= 0:
                money += enemy.reward
                enemies.remove(enemy)
                
                # Show reward text
                floating_texts.append(
                    FloatingText(f"+${enemy.reward}", 
                               (enemy.pos.x, enemy.pos.y - 20),
                               (255, 255, 0), 20)
                )
                
                # Show death explosion effect
                particles.add_explosion(enemy.pos.x, enemy.pos.y, enemy.color, count=20)
                
                # If target of any tower, clear reference
                for tower in towers:
                    if tower.targeting_enemy == enemy:
                        tower.targeting_enemy = None
            
            # Apply burn damage if enemy has burn status
            elif "burn" in enemy.status_effects:
                burn_data = enemy.status_effects["burn"]
                if enemy.take_damage(burn_data["value"] * dt):
                    money += enemy.reward
                    enemies.remove(enemy)
                    floating_texts.append(
                        FloatingText(f"+${enemy.reward}", 
                                   (enemy.pos.x, enemy.pos.y - 20),
                                   (255, 255, 0), 20)
                    )
                    particles.add_explosion(enemy.pos.x, enemy.pos.y, enemy.color, count=20)
        
        # Update projectiles
        for projectile in projectiles[:]:
            chain_proj = projectile.update(dt, enemies, particles)
            if chain_proj:
                projectiles.append(chain_proj)
            if not projectile.active:
                projectiles.remove(projectile)
        
        # Update particles
        particles.update(dt)
        
        # Update floating texts
        for text in floating_texts[:]:
            if not text.update(dt):
                floating_texts.remove(text)
        
        # Handle wave progression
        if wave_active:
            # Check if we need to spawn more enemies
            if current_wave_enemies:
                next_enemy_spawn -= dt
                if next_enemy_spawn <= 0:
                    enemy_type, wave_level = current_wave_enemies.pop(0)
                    spawn_enemy = Enemy(path_points, enemy_type, wave_level)
                    enemies.append(spawn_enemy)
                    next_enemy_spawn = current_wave_config["spawn_delay"]
                    
                    # Add spawn effect
                    particles.add_explosion(spawn_enemy.pos.x, spawn_enemy.pos.y, 
                                          spawn_enemy.color, count=10)
            
            # Update wave progress
            if current_wave_enemies:
                total_enemies = len(current_wave_config["enemies"])
                enemies_left = len(current_wave_enemies) + len(enemies)
                wave_progress = 1.0 - (enemies_left / total_enemies)
            else:
                wave_progress = 1.0
            
            # Check if wave is complete
            if len(current_wave_enemies) == 0 and len(enemies) == 0:
                wave_active = False
                # Add wave complete bonus
                bonus = current_wave_config.get("reward_bonus", 0)
                if bonus > 0:
                    money += bonus
                    floating_texts.append(
                        FloatingText(f"Wave Complete! +${bonus}", 
                                   (screen_width // 2, screen_height // 2 - 50),
                                   (255, 255, 0), 32, duration=2.0)
                    )
        
        # Draw game
        draw_gradient_background(screen, (20, 20, 40), (70, 70, 100))
        
        # Draw gameplay area separator
        pygame.draw.line(screen, (100, 100, 150), (sidebar_width, 0), (sidebar_width, screen_height), 2)
        pygame.draw.line(screen, (100, 100, 150), (screen_width - sidebar_width, 0), 
                       (screen_width - sidebar_width, screen_height), 2)
        
        # Draw path with camera transform
        points = []
        for point in path_points:
            screen_point = camera.apply(point[0], point[1])
            points.append(screen_point)
        pygame.draw.lines(screen, (200, 200, 200), False, points, max(1, int(5 * camera.zoom)))
        
        # Add some path decoration
        for i in range(len(path_points) - 1):
            p1 = pygame.Vector2(path_points[i])
            p2 = pygame.Vector2(path_points[i + 1])
            # Draw direction arrows along path
            if (p2 - p1).length() > 50:
                direction = (p2 - p1).normalize()
                num_arrows = int((p2 - p1).length() / 100)
                for j in range(num_arrows):
                    pos = p1 + direction * (j + 0.5) * ((p2 - p1).length() / num_arrows)
                    angle = math.atan2(direction.y, direction.x)
                    
                    # Apply camera transform to arrow position
                    screen_pos = camera.apply(pos.x, pos.y)
                    
                    # Draw arrow
                    arrow_size = max(3, 10 * camera.zoom)
                    arrow_points = [
                        (screen_pos[0] + math.cos(angle) * arrow_size, 
                         screen_pos[1] + math.sin(angle) * arrow_size),
                        (screen_pos[0] + math.cos(angle + 2.5) * arrow_size * 0.6, 
                         screen_pos[1] + math.sin(angle + 2.5) * arrow_size * 0.6),
                        (screen_pos[0] + math.cos(angle - 2.5) * arrow_size * 0.6, 
                         screen_pos[1] + math.sin(angle - 2.5) * arrow_size * 0.6)
                    ]
                    pygame.draw.polygon(screen, (150, 150, 150), arrow_points)
        
        # Draw towers and their ranges
        for tower in towers:
            is_selected = tower == selected_tower
            tower.draw(screen, assets, show_range=is_selected, selected=is_selected, camera=camera)
        
        # Draw enemies
        for enemy in enemies:
            enemy.draw(screen, show_hp=True, camera=camera)
        
        # Draw projectiles
        for projectile in projectiles:
            projectile.draw(screen, camera=camera)
        
        # Draw particles
        particles.draw(screen, camera=camera)
        
        # Draw tower placement preview
        if dragging_tower and tower_preview_pos:
            preview_color = tower_types[current_tower_type]["color"]
            
            # Check tower placement validity
            valid_placement = True
            # Check if too close to path
            for i in range(len(path_points) - 1):
                p1 = pygame.Vector2(path_points[i])
                p2 = pygame.Vector2(path_points[i + 1])
                dist = distance_to_line_segment(tower_preview_pos, p1, p2)
                if dist < 40:  # Minimum distance from path
                    valid_placement = False
                    break
            
            # Check if too close to other towers
            for tower in towers:
                if (tower.pos - tower_preview_pos).length() < 40:
                    valid_placement = False
                    break
            
            # Draw tower preview
            screen_pos = camera.apply(tower_preview_pos.x, tower_preview_pos.y)
            preview_radius = 15 * camera.zoom
            preview_surf = pygame.Surface((int(preview_radius * 2), int(preview_radius * 2)), pygame.SRCALPHA)
            
            # Draw base circle with transparency
            if valid_placement:
                pygame.draw.circle(preview_surf, (*preview_color, 150), (int(preview_radius), int(preview_radius)), int(preview_radius))
                # Add range indicator
                range_radius = tower_types[current_tower_type]["range"] * camera.zoom
                range_surf = pygame.Surface((int(range_radius * 2), int(range_radius * 2)), pygame.SRCALPHA)
                pygame.draw.circle(range_surf, (255, 255, 255, 30), (int(range_radius), int(range_radius)), int(range_radius))
                pygame.draw.circle(range_surf, (255, 255, 255, 60), (int(range_radius), int(range_radius)), int(range_radius), 2)
                screen.blit(range_surf, (int(screen_pos[0] - range_radius), int(screen_pos[1] - range_radius)))
            else:
                # Use red color for invalid placement
                pygame.draw.circle(preview_surf, (255, 100, 100, 150), (int(preview_radius), int(preview_radius)), int(preview_radius))
                # Draw X mark
                pygame.draw.line(preview_surf, (255, 50, 50, 200), 
                              (preview_radius * 0.5, preview_radius * 0.5), 
                              (preview_radius * 1.5, preview_radius * 1.5), 
                              max(1, int(2 * camera.zoom)))
                pygame.draw.line(preview_surf, (255, 50, 50, 200), 
                              (preview_radius * 1.5, preview_radius * 0.5), 
                              (preview_radius * 0.5, preview_radius * 1.5), 
                              max(1, int(2 * camera.zoom)))
            
            # Blit the preview
            screen.blit(preview_surf, (int(screen_pos[0] - preview_radius), int(screen_pos[1] - preview_radius)))
        
        # Draw floating texts
        for text in floating_texts:
            # Apply camera transform for floating texts
            if hasattr(text, 'pos'):  # Only transform in-game floating texts, not UI texts
                screen_pos = camera.apply(text.pos[0], text.pos[1])
                text.draw(screen, screen_pos=screen_pos, scale=camera.zoom)
            else:
                text.draw(screen)
        
        # Draw UI
        ui.draw(screen, {
            "money": money,
            "lives": lives,
            "wave": wave,
            "current_tower_type": current_tower_type,
            "selected_tower": selected_tower,
            "hover_tower": hover_tower,
            "enemies_remaining": len(enemies),
            "wave_progress": wave_progress,
            "wave_active": wave_active,
            "camera_zoom": camera.zoom  # Pass camera zoom to UI
        }, assets)
        
        # Check game over condition
        if lives <= 0:
            # Draw game over screen
            overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            font_large = pygame.font.SysFont(None, 64)
            font_medium = pygame.font.SysFont(None, 36)
            
            game_over_text = font_large.render("Game Over!", True, (255, 50, 50))
            game_over_rect = game_over_text.get_rect(center=(screen_width // 2, screen_height // 2 - 40))
            screen.blit(game_over_text, game_over_rect)
            
            wave_text = font_medium.render(f"You survived until wave {wave}", True, (255, 255, 255))
            wave_rect = wave_text.get_rect(center=(screen_width // 2, screen_height // 2 + 20))
            screen.blit(wave_text, wave_rect)
            
            continue_text = font_medium.render("Press ESC to exit or SPACE to restart", True, (200, 200, 200))
            continue_rect = continue_text.get_rect(center=(screen_width // 2, screen_height // 2 + 70))
            screen.blit(continue_text, continue_rect)
            
            pygame.display.flip()
            
            # Wait for player decision
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        waiting = False
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            waiting = False
                            running = False
                        elif event.key == pygame.K_SPACE:
                            # Reset game state
                            towers = []
                            enemies = []
                            projectiles = []
                            particles = ParticleSystem(max_particles=500)
                            floating_texts = []
                            lives = 10
                            money = 150
                            wave = 0
                            current_tower_type = "Fire"
                            selected_tower = None
                            hover_tower = None
                            wave_active = False
                            waiting = False
                            
                            # Reset camera
                            camera.x = 700
                            camera.y = 450
                            camera.zoom = 1.0
        
        # Draw camera controls help
        font_small = pygame.font.SysFont(None, 18)
        zoom_text = font_small.render(f"Zoom: {camera.zoom:.1f}x (Mouse Wheel to Zoom)", True, (200, 200, 200))
        pan_text = font_small.render("Hold SHIFT + Left Mouse to Pan", True, (200, 200, 200))
        drag_text = font_small.render("Drag & Drop to Place Towers", True, (200, 200, 200))
        reset_text = font_small.render("Press R to Reset Camera", True, (200, 200, 200))
        
        control_bg = pygame.Surface((230, 75), pygame.SRCALPHA)
        control_bg.fill((0, 0, 0, 100))
        screen.blit(control_bg, (screen_width - 250, screen_height - 80))
        
        screen.blit(zoom_text, (screen_width - 240, screen_height - 75))
        screen.blit(pan_text, (screen_width - 240, screen_height - 55))
        screen.blit(drag_text, (screen_width - 240, screen_height - 35))
        screen.blit(reset_text, (screen_width - 240, screen_height - 15))
        
        # Show current interaction mode
        mode_text = font_small.render(f"Mode: {'Pan' if is_shift_pressed else 'Build'}", True, 
                                    (100, 200, 255) if is_shift_pressed else (100, 255, 100))
        screen.blit(mode_text, (sidebar_width + 10, 10))
        
        # Update display
        pygame.display.flip()

def start_next_wave(current_wave, enemies, current_wave_enemies):
    """Initialize the next wave of enemies"""
    # Clear any remaining enemies from previous wave
    current_wave_enemies.clear()
    
    # Get wave configuration
    wave_index = min(current_wave, len(wave_templates) - 1)
    wave_config = wave_templates[wave_index]
    
    # Calculate wave scaling factor
    scaling = 1.0 + max(0, current_wave - len(wave_templates) + 1) * 0.2
    
    # Create enemy list
    for enemy_type, count in wave_config["enemies"]:
        for _ in range(count):
            # Tuple of (enemy_type, wave_level)
            current_wave_enemies.append((enemy_type, current_wave + 1))
    
    # Shuffle enemy order for variety
    random.shuffle(current_wave_enemies)
    
    return wave_config

def distance_to_line_segment(p, v, w):
    """Calculate minimum distance from point p to line segment vw"""
    l2 = (v - w).length_squared()
    if l2 == 0:
        return (p - v).length()
    
    t = max(0, min(1, pygame.Vector2.dot(p - v, w - v) / l2))
    projection = v + t * (w - v)
    return (p - projection).length()


if __name__ == '__main__':
    main() 