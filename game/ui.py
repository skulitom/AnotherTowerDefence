import pygame
import math
import random
from game.utils import draw_gradient_rect, create_element_icon, draw_hp_bar
from game.settings import tower_types, upgrade_paths


class Button:
    def __init__(self, rect, text, color=(100, 100, 200), hover_color=(120, 120, 255), text_color=(255, 255, 255), 
                 icon=None, icon_size=None, tooltip=None, enabled=True, font_size=18):
        self.rect = rect
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.icon = icon
        self.icon_size = icon_size
        self.tooltip = tooltip
        self.enabled = enabled
        self.hover = False
        self.font = pygame.font.SysFont(None, font_size)
        self.pressed = False
        self.press_time = 0
        self.shadow_offset = 3
        self.border_radius = 8
        
    def draw(self, surface):
        # Draw button shadow
        if self.enabled and not self.pressed:
            shadow_rect = pygame.Rect(self.rect.x + self.shadow_offset, 
                                     self.rect.y + self.shadow_offset,
                                     self.rect.width, self.rect.height)
            pygame.draw.rect(surface, (30, 30, 30, 150), shadow_rect, border_radius=self.border_radius)
        
        # Create button surface with gradient
        button_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        
        if not self.enabled:
            # Disabled state - gray gradient
            color_top = (80, 80, 80)
            color_bottom = (60, 60, 60)
        elif self.hover or self.pressed:
            # Hover state - brighter gradient
            color_top = (self.hover_color[0], self.hover_color[1], self.hover_color[2])
            color_bottom = (max(0, self.hover_color[0]-40), max(0, self.hover_color[1]-40), max(0, self.hover_color[2]-40))
        else:
            # Normal state - standard gradient
            color_top = (self.color[0], self.color[1], self.color[2])
            color_bottom = (max(0, self.color[0]-40), max(0, self.color[1]-40), max(0, self.color[2]-40))
        
        # Draw gradient background
        for y in range(self.rect.height):
            progress = y / self.rect.height
            r = int(color_top[0] * (1 - progress) + color_bottom[0] * progress)
            g = int(color_top[1] * (1 - progress) + color_bottom[1] * progress)
            b = int(color_top[2] * (1 - progress) + color_bottom[2] * progress)
            pygame.draw.line(button_surf, (r, g, b), (0, y), (self.rect.width, y))
        
        # Draw border with rounded corners
        pygame.draw.rect(button_surf, (0, 0, 0, 0), (0, 0, self.rect.width, self.rect.height), border_radius=self.border_radius)
        
        # Add highlight to the top edge for 3D effect
        if self.enabled and not self.pressed:
            highlight_color = (255, 255, 255, 70)
            pygame.draw.rect(button_surf, highlight_color, (2, 2, self.rect.width-4, 3), border_radius=self.border_radius)
        
        # Draw border
        border_color = (255, 255, 255, 100) if self.hover and self.enabled else (120, 120, 120, 100)
        pygame.draw.rect(button_surf, border_color, (0, 0, self.rect.width, self.rect.height), 2, border_radius=self.border_radius)
        
        # Blit button surface
        if self.pressed:
            # Pressed state - move button down slightly
            surface.blit(button_surf, (self.rect.x + 1, self.rect.y + 1))
        else:
            surface.blit(button_surf, self.rect.topleft)
            
        # Draw button text
        text_color = self.text_color if self.enabled else (150, 150, 150)
        text_surf = self.font.render(self.text, True, text_color)
        
        # Position based on whether there's an icon
        if self.icon:
            if isinstance(self.icon, pygame.Surface):
                # Use provided surface
                icon = self.icon
                if self.icon_size:
                    icon = pygame.transform.scale(icon, self.icon_size)
            else:
                # Create an icon based on text
                icon = create_element_icon(self.icon, 24)
                
            # Adjust positions for pressed state
            offset_x = 1 if self.pressed else 0
            offset_y = 1 if self.pressed else 0
                
            icon_rect = icon.get_rect(midleft=(self.rect.x + 10 + offset_x, self.rect.centery + offset_y))
            surface.blit(icon, icon_rect)
            
            # Position text next to icon
            text_rect = text_surf.get_rect(midleft=(icon_rect.right + 10, self.rect.centery + offset_y))
            surface.blit(text_surf, text_rect)
        else:
            # Center text in button
            text_rect = text_surf.get_rect(center=(
                self.rect.centerx + (1 if self.pressed else 0), 
                self.rect.centery + (1 if self.pressed else 0)
            ))
            surface.blit(text_surf, text_rect)
        
        # Draw press animation
        if self.pressed:
            pulse = min(1.0, (pygame.time.get_ticks() - self.press_time) / 200)
            alpha = int(150 * (1 - pulse))
            pulse_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            pulse_surface.fill((255, 255, 255, alpha))
            # Apply rounded corners to the pulse
            mask = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            pygame.draw.rect(mask, (255, 255, 255), (0, 0, self.rect.width, self.rect.height), border_radius=self.border_radius)
            pulse_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            surface.blit(pulse_surface, (self.rect.x + 1, self.rect.y + 1))
            
        # Draw tooltip if hovering
        if self.hover and self.tooltip:
            tooltip_font = pygame.font.SysFont(None, 16)
            tooltip_lines = self.tooltip.split('\n')
            tooltip_surfs = [tooltip_font.render(line, True, (255, 255, 255)) for line in tooltip_lines]
            
            # Calculate tooltip dimensions
            tooltip_width = max(surf.get_width() for surf in tooltip_surfs) + 10
            tooltip_height = sum(surf.get_height() for surf in tooltip_surfs) + 10
            
            tooltip_rect = pygame.Rect(
                self.rect.centerx - tooltip_width // 2, 
                self.rect.bottom + 5,
                tooltip_width,
                tooltip_height
            )
            
            # Make sure tooltip stays on screen
            if tooltip_rect.right > surface.get_width():
                tooltip_rect.right = surface.get_width() - 5
            if tooltip_rect.bottom > surface.get_height():
                tooltip_rect.bottom = self.rect.top - 5
            
            # Background for tooltip with gradient
            background_rect = tooltip_rect
            tooltip_surf = pygame.Surface((background_rect.width, background_rect.height), pygame.SRCALPHA)
            
            # Draw gradient background
            for y in range(background_rect.height):
                progress = y / background_rect.height
                r = int(50 * (1 - progress) + 20 * progress)
                g = int(50 * (1 - progress) + 20 * progress)
                b = int(70 * (1 - progress) + 40 * progress)
                pygame.draw.line(tooltip_surf, (r, g, b, 220), (0, y), (background_rect.width, y))
            
            # Add border
            pygame.draw.rect(tooltip_surf, (140, 140, 180), (0, 0, background_rect.width, background_rect.height), 1, border_radius=4)
            
            # Add highlight to the top
            pygame.draw.line(tooltip_surf, (200, 200, 255, 100), (1, 1), (background_rect.width-2, 1))
            
            surface.blit(tooltip_surf, background_rect.topleft)
            
            # Draw tooltip text
            y_offset = 5
            for surf in tooltip_surfs:
                surface.blit(surf, (tooltip_rect.x + 5, tooltip_rect.y + y_offset))
                y_offset += surf.get_height()
    
    def update(self, mouse_pos, mouse_pressed):
        self.hover = self.rect.collidepoint(mouse_pos)
        
        if self.hover and mouse_pressed and self.enabled and not self.pressed:
            self.pressed = True
            self.press_time = pygame.time.get_ticks()
            return True
        
        # Reset pressed state after animation time
        if self.pressed and pygame.time.get_ticks() - self.press_time > 200:
            self.pressed = False
            
        return False


class TowerInfoPanel:
    def __init__(self, rect):
        self.rect = rect
        self.tower = None
        self.font_title = pygame.font.SysFont(None, 32)
        self.font_stat = pygame.font.SysFont(None, 20)
        self.font_description = pygame.font.SysFont(None, 18)
        self.border_radius = 10
        
        self.upgrade_buttons = []
        self.sell_button = None
        self.create_buttons()
        
    def create_buttons(self):
        button_height = 40
        button_width = self.rect.width - 20
        
        # Create upgrade buttons
        self.upgrade_buttons = []
        for i, upgrade_type in enumerate(["damage", "range", "speed", "special"]):
            y_pos = self.rect.y + 160 + i * (button_height + 10)
            button_rect = pygame.Rect(self.rect.x + 10, y_pos, button_width, button_height)
            
            name = upgrade_paths[upgrade_type]["name"]
            description = upgrade_paths[upgrade_type]["description"]
            button = Button(
                button_rect, 
                name, 
                color=(60, 120, 180),
                hover_color=(80, 150, 220),
                tooltip=description
            )
            self.upgrade_buttons.append((upgrade_type, button))
        
        # Create sell button
        sell_rect = pygame.Rect(self.rect.x + 10, self.rect.bottom - 50, button_width, button_height)
        self.sell_button = Button(
            sell_rect,
            "Sell Tower",
            color=(180, 60, 60),
            hover_color=(220, 80, 80),
            tooltip="Sell this tower to reclaim some money"
        )
        
    def set_tower(self, tower, money=0):
        self.tower = tower
        
        # Update upgrade buttons
        for upgrade_type, button in self.upgrade_buttons:
            if tower and tower.can_upgrade(upgrade_type):
                cost = tower.get_upgrade_cost(upgrade_type)
                button.enabled = money >= cost
                button.text = f"{upgrade_paths[upgrade_type]['name']} (${cost})"
            else:
                button.enabled = False
                button.text = upgrade_paths[upgrade_type]['name']
        
        # Update sell button
        if tower:
            # Sell value is 70% of total investment
            base_cost = tower_types[tower.tower_type]["cost"]
            upgrade_cost = 0
            for upgrade_type, level in tower.upgrades.items():
                for i in range(level):
                    if i < len(upgrade_paths[upgrade_type]["levels"]):
                        upgrade_cost += upgrade_paths[upgrade_type]["levels"][i]["cost"]
            
            sell_value = int((base_cost + upgrade_cost) * 0.7)
            self.sell_button.text = f"Sell Tower (${sell_value})"
            self.sell_button.enabled = True
        else:
            self.sell_button.text = "Sell Tower"
            self.sell_button.enabled = False
    
    def draw(self, surface, assets):
        if not self.tower:
            return
            
        # Create panel surface with rounded corners and glow
        panel_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        
        # Draw panel background gradient
        for y in range(self.rect.height):
            progress = y / self.rect.height
            r = int(50 * (1 - progress) + 30 * progress)
            g = int(50 * (1 - progress) + 30 * progress)
            b = int(80 * (1 - progress) + 60 * progress)
            pygame.draw.line(panel_surf, (r, g, b, 230), (0, y), (self.rect.width, y))
        
        # Draw border with glow
        pygame.draw.rect(panel_surf, (0, 0, 0, 0), (0, 0, self.rect.width, self.rect.height), border_radius=self.border_radius)
        pygame.draw.rect(panel_surf, (120, 160, 200, 150), (0, 0, self.rect.width, self.rect.height), 2, border_radius=self.border_radius)
        
        # Add top highlight
        pygame.draw.line(panel_surf, (200, 220, 255, 100), (5, 2), (self.rect.width-5, 2))
        
        # Blit panel surface
        surface.blit(panel_surf, self.rect.topleft)
        
        # Draw header strip
        header_height = 40
        header_surf = pygame.Surface((self.rect.width, header_height), pygame.SRCALPHA)
        for y in range(header_height):
            progress = y / header_height
            r = int(80 * (1 - progress) + 50 * progress)
            g = int(80 * (1 - progress) + 50 * progress)
            b = int(120 * (1 - progress) + 80 * progress)
            pygame.draw.line(header_surf, (r, g, b), (0, y), (self.rect.width, y))
        # Round corners only on top
        pygame.draw.rect(header_surf, (0, 0, 0, 0), (0, 0, self.rect.width, header_height), border_radius=self.border_radius)
        surface.blit(header_surf, self.rect.topleft)
        
        # Draw tower name with shadow
        title_text = f"{self.tower.tower_type} Tower (Level {self.tower.level})"
        shadow_surf = self.font_title.render(title_text, True, (0, 0, 0))
        title_surf = self.font_title.render(title_text, True, (255, 255, 255))
        title_rect = title_surf.get_rect(midtop=(self.rect.centerx, self.rect.y + 10))
        surface.blit(shadow_surf, (title_rect.x+1, title_rect.y+1))
        surface.blit(title_surf, title_rect)
        
        # Draw tower info
        tower_img = assets["towers"].get(self.tower.tower_type)
        if tower_img:
            img = pygame.transform.scale(tower_img, (64, 64))
            img_rect = img.get_rect(midtop=(self.rect.centerx, title_rect.bottom + 10))
            # Add glow behind tower image
            glow_surf = pygame.Surface((80, 80), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*self.tower.color, 90), (40, 40), 32)
            surface.blit(glow_surf, (img_rect.centerx-40, img_rect.centery-40))
            surface.blit(img, img_rect)
        else:
            icon = create_element_icon(self.tower.tower_type, 64)
            icon_rect = icon.get_rect(midtop=(self.rect.centerx, title_rect.bottom + 10))
            # Add glow behind tower icon
            glow_surf = pygame.Surface((80, 80), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*self.tower.color, 90), (40, 40), 32)
            surface.blit(glow_surf, (icon_rect.centerx-40, icon_rect.centery-40))
            surface.blit(icon, icon_rect)
        
        # Draw tower stats with improved styling
        stats_y = title_rect.bottom + 80
        stat_x = self.rect.x + 20
        
        # Draw stat box
        stat_box = pygame.Rect(stat_x-10, stats_y-5, self.rect.width-20, 75)
        stat_surf = pygame.Surface((stat_box.width, stat_box.height), pygame.SRCALPHA)
        stat_surf.fill((0, 0, 0, 40))
        pygame.draw.rect(stat_surf, (100, 100, 150, 80), (0, 0, stat_box.width, stat_box.height), 1, border_radius=5)
        surface.blit(stat_surf, stat_box.topleft)
        
        # Draw damage stat
        damage_text = f"Damage: {self.tower.current_damage:.1f}"
        if self.tower.buff_multiplier > 1.0:
            damage_text += f" (Buffed)"
            damage_color = (100, 255, 100)
        else:
            damage_color = (255, 200, 100)
        damage_surf = self.font_stat.render(damage_text, True, damage_color)
        surface.blit(damage_surf, (stat_x, stats_y))
        
        # Draw range stat
        range_text = f"Range: {self.tower.range:.0f}"
        range_surf = self.font_stat.render(range_text, True, (100, 200, 255))
        surface.blit(range_surf, (stat_x, stats_y + 20))
        
        # Draw speed stat
        speed_text = f"Attack Speed: {1/self.tower.cooldown:.1f}/s"
        speed_surf = self.font_stat.render(speed_text, True, (200, 150, 255))
        surface.blit(speed_surf, (stat_x, stats_y + 40))
        
        # Draw special ability description with style
        if self.tower.special_ability:
            description = tower_types[self.tower.tower_type].get("description", "")
            desc_box = pygame.Rect(stat_x-10, stats_y+75, self.rect.width-20, 30)
            desc_surf = pygame.Surface((desc_box.width, desc_box.height), pygame.SRCALPHA)
            desc_surf.fill((100, 100, 100, 30))
            pygame.draw.rect(desc_surf, (150, 150, 150, 80), (0, 0, desc_box.width, desc_box.height), 1, border_radius=5)
            surface.blit(desc_surf, desc_box.topleft)
            
            ability_surf = self.font_description.render(description, True, (220, 220, 220))
            ability_rect = ability_surf.get_rect(center=(self.rect.centerx, stats_y + 90))
            surface.blit(ability_surf, ability_rect)
        
        # Draw upgrade buttons
        for _, button in self.upgrade_buttons:
            button.draw(surface)
            
        # Draw sell button
        self.sell_button.draw(surface)
    
    def handle_event(self, event, money):
        if not self.tower:
            return None, None
            
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
        
        # Check upgrade buttons
        for upgrade_type, button in self.upgrade_buttons:
            if button.update(mouse_pos, mouse_pressed):
                return "upgrade", upgrade_type
                
        # Check sell button
        if self.sell_button.update(mouse_pos, mouse_pressed):
            return "sell", None
            
        return None, None


class WavePanel:
    def __init__(self, rect):
        self.rect = rect
        self.font_title = pygame.font.SysFont(None, 28)
        self.font_info = pygame.font.SysFont(None, 20)
        self.current_wave = 0
        self.enemies_remaining = 0
        self.next_wave_button = None
        self.wave_progress = 0.0  # 0.0 to 1.0
        self.is_wave_active = False
        self.create_buttons()
        
    def create_buttons(self):
        button_rect = pygame.Rect(
            self.rect.x + 20, 
            self.rect.bottom - 45, 
            self.rect.width - 40, 
            35
        )
        self.next_wave_button = Button(
            button_rect,
            "Start Wave",
            color=(60, 180, 60),
            hover_color=(80, 220, 80),
            tooltip="Start the next wave of enemies"
        )
    
    def update(self, current_wave, enemies_remaining, wave_progress=0.0, is_wave_active=False):
        self.current_wave = current_wave
        self.enemies_remaining = enemies_remaining
        self.wave_progress = wave_progress
        self.is_wave_active = is_wave_active
        
        if is_wave_active:
            self.next_wave_button.enabled = False
            self.next_wave_button.text = f"Wave in Progress..."
        else:
            self.next_wave_button.enabled = True
            self.next_wave_button.text = f"Start Wave {current_wave + 1}"
    
    def draw(self, surface):
        # Draw panel background
        draw_gradient_rect(surface, self.rect, (40, 70, 40), (60, 100, 60))
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 2)
        
        # Draw wave information
        title_text = f"Wave {self.current_wave}"
        title_surf = self.font_title.render(title_text, True, (255, 255, 255))
        title_rect = title_surf.get_rect(midtop=(self.rect.centerx, self.rect.y + 10))
        surface.blit(title_surf, title_rect)
        
        # Draw enemies remaining
        enemies_text = f"Enemies Remaining: {self.enemies_remaining}"
        enemies_surf = self.font_info.render(enemies_text, True, (255, 255, 255))
        enemies_rect = enemies_surf.get_rect(midtop=(self.rect.centerx, title_rect.bottom + 10))
        surface.blit(enemies_surf, enemies_rect)
        
        # Draw wave progress bar
        if self.is_wave_active:
            progress_rect = pygame.Rect(
                self.rect.x + 20,
                enemies_rect.bottom + 10,
                self.rect.width - 40,
                15
            )
            pygame.draw.rect(surface, (80, 80, 80), progress_rect)
            fill_rect = progress_rect.copy()
            fill_rect.width = int(progress_rect.width * self.wave_progress)
            pygame.draw.rect(surface, (100, 200, 100), fill_rect)
            pygame.draw.rect(surface, (200, 200, 200), progress_rect, 1)
        
        # Draw next wave button
        self.next_wave_button.draw(surface)
    
    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
        
        if self.next_wave_button.update(mouse_pos, mouse_pressed):
            return "start_wave"
            
        return None


class StatusPanel:
    def __init__(self, rect):
        self.rect = rect
        self.font_title = pygame.font.SysFont(None, 28)
        self.font_info = pygame.font.SysFont(None, 24)
        self.money = 0
        self.lives = 0
        self.selected_tower_type = None
    
    def update(self, money, lives, selected_tower_type):
        self.money = money
        self.lives = lives
        self.selected_tower_type = selected_tower_type
    
    def draw(self, surface, assets):
        # Draw panel background
        draw_gradient_rect(surface, self.rect, (40, 40, 70), (60, 60, 100))
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 2)
        
        # Draw resources
        title_text = "Resources"
        title_surf = self.font_title.render(title_text, True, (255, 255, 255))
        title_rect = title_surf.get_rect(midtop=(self.rect.centerx, self.rect.y + 10))
        surface.blit(title_surf, title_rect)
        
        # Draw money
        money_text = f"Money: ${self.money}"
        money_surf = self.font_info.render(money_text, True, (255, 255, 100))
        money_rect = money_surf.get_rect(midtop=(self.rect.centerx, title_rect.bottom + 10))
        surface.blit(money_surf, money_rect)
        
        # Draw lives
        lives_text = f"Lives: {self.lives}"
        lives_color = (255, 255, 255) if self.lives > 5 else (255, 100, 100)
        lives_surf = self.font_info.render(lives_text, True, lives_color)
        lives_rect = lives_surf.get_rect(midtop=(self.rect.centerx, money_rect.bottom + 10))
        surface.blit(lives_surf, lives_rect)
        
        # Draw selected tower information
        if self.selected_tower_type:
            selected_y = lives_rect.bottom + 20
            
            selected_text = f"Selected Tower:"
            selected_surf = self.font_info.render(selected_text, True, (255, 255, 255))
            selected_rect = selected_surf.get_rect(midtop=(self.rect.centerx, selected_y))
            surface.blit(selected_surf, selected_rect)
            
            # Draw tower icon
            tower_img = assets["towers"].get(self.selected_tower_type)
            if tower_img:
                img = pygame.transform.scale(tower_img, (48, 48))
                img_rect = img.get_rect(midtop=(self.rect.centerx, selected_rect.bottom + 5))
                surface.blit(img, img_rect)
            else:
                icon = create_element_icon(self.selected_tower_type, 48)
                icon_rect = icon.get_rect(midtop=(self.rect.centerx, selected_rect.bottom + 5))
                surface.blit(icon, icon_rect)
            
            # Draw tower cost
            cost = tower_types[self.selected_tower_type]["cost"]
            cost_text = f"Cost: ${cost}"
            cost_color = (255, 255, 255) if self.money >= cost else (255, 100, 100)
            cost_surf = self.font_info.render(cost_text, True, cost_color)
            cost_rect = cost_surf.get_rect(midtop=(self.rect.centerx, selected_rect.bottom + 60))
            surface.blit(cost_surf, cost_rect)
            
            # Draw tower description
            description = tower_types[self.selected_tower_type].get("description", "")
            desc_font = pygame.font.SysFont(None, 18)
            desc_surf = desc_font.render(description, True, (200, 200, 200))
            desc_rect = desc_surf.get_rect(midtop=(self.rect.centerx, cost_rect.bottom + 10))
            surface.blit(desc_surf, desc_rect)


class TowerSelectionPanel:
    def __init__(self, rect):
        self.rect = rect
        self.font = pygame.font.SysFont(None, 24)
        self.tower_buttons = []
        self.selected_tower = None
        self.create_buttons()
        
    def create_buttons(self):
        button_height = 35
        button_width = self.rect.width - 20
        
        # Create tower selection buttons
        self.tower_buttons = []
        tower_order = ["Fire", "Water", "Air", "Earth", "Darkness", "Light", "Life"]
        
        for i, tower_type in enumerate(tower_order):
            y_pos = self.rect.y + 40 + i * (button_height + 8)
            button_rect = pygame.Rect(self.rect.x + 10, y_pos, button_width, button_height)
            
            cost = tower_types[tower_type]["cost"]
            button = Button(
                button_rect, 
                f"{tower_type} (${cost})", 
                color=(60, 60, 100),
                hover_color=(80, 80, 150),
                tooltip=tower_types[tower_type].get("description", ""),
                icon=tower_type
            )
            self.tower_buttons.append((tower_type, button))
    
    def update(self, selected_tower, money):
        self.selected_tower = selected_tower
        
        # Update button appearance based on selection and affordability
        for tower_type, button in self.tower_buttons:
            # Change color if selected
            if tower_type == selected_tower:
                button.color = (100, 100, 180)
                button.hover_color = (120, 120, 220)
            else:
                button.color = (60, 60, 100)
                button.hover_color = (80, 80, 150)
            
            # Enable/disable based on affordability
            cost = tower_types[tower_type]["cost"]
            button.enabled = money >= cost
    
    def draw(self, surface):
        # Draw panel background
        draw_gradient_rect(surface, self.rect, (40, 40, 70), (60, 60, 100))
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 2)
        
        # Draw panel title
        title_text = "Tower Selection"
        title_surf = self.font.render(title_text, True, (255, 255, 255))
        title_rect = title_surf.get_rect(midtop=(self.rect.centerx, self.rect.y + 10))
        surface.blit(title_surf, title_rect)
        
        # Draw tower buttons
        for _, button in self.tower_buttons:
            button.draw(surface)
    
    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
        
        for tower_type, button in self.tower_buttons:
            if button.update(mouse_pos, mouse_pressed):
                return tower_type
                
        return None


class GameUI:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Create various panels
        sidebar_width = 260
        
        # Right sidebar for tower info
        info_panel_height = 400
        self.tower_info_panel = TowerInfoPanel(
            pygame.Rect(screen_width - sidebar_width, 10, sidebar_width - 10, info_panel_height)
        )
        
        # Wave info panel below tower info
        wave_panel_height = 150
        self.wave_panel = WavePanel(
            pygame.Rect(screen_width - sidebar_width, info_panel_height + 20, 
                       sidebar_width - 10, wave_panel_height)
        )
        
        # Left sidebar top for status
        status_panel_height = 230
        self.status_panel = StatusPanel(
            pygame.Rect(10, 10, sidebar_width - 10, status_panel_height)
        )
        
        # Left sidebar bottom for tower selection
        tower_selection_height = 320
        self.tower_selection_panel = TowerSelectionPanel(
            pygame.Rect(10, status_panel_height + 20, sidebar_width - 10, tower_selection_height)
        )
        
        # Tower tooltip info for hover
        self.tooltip_font = pygame.font.SysFont(None, 18)
        self.hover_tower = None
        
    def draw(self, surface, game_state, assets):
        # Update panels with current game state
        self.tower_info_panel.set_tower(game_state.get("selected_tower"), game_state.get("money", 0))
        self.status_panel.update(
            game_state.get("money", 0), 
            game_state.get("lives", 0), 
            game_state.get("current_tower_type")
        )
        self.tower_selection_panel.update(
            game_state.get("current_tower_type"),
            game_state.get("money", 0)
        )
        self.wave_panel.update(
            game_state.get("wave", 0),
            game_state.get("enemies_remaining", 0),
            game_state.get("wave_progress", 0.0),
            game_state.get("wave_active", False)
        )
        
        # Draw all panels
        self.tower_info_panel.draw(surface, assets)
        self.status_panel.draw(surface, assets)
        self.tower_selection_panel.draw(surface)
        self.wave_panel.draw(surface)
        
        # Draw hover tooltip for towers
        hover_tower = game_state.get("hover_tower")
        if hover_tower and hover_tower != game_state.get("selected_tower"):
            self.draw_tower_tooltip(surface, hover_tower, pygame.mouse.get_pos())
    
    def draw_tower_tooltip(self, surface, tower, mouse_pos):
        # Create tooltip text
        lines = [
            f"{tower.tower_type} Tower (Level {tower.level})",
            f"Damage: {tower.current_damage:.1f}",
            f"Range: {tower.range:.0f}",
            f"Attack Speed: {1/tower.cooldown:.1f}/s"
        ]
        
        # Measure tooltip size
        line_height = self.tooltip_font.get_height()
        max_width = 0
        for line in lines:
            text_surf = self.tooltip_font.render(line, True, (255, 255, 255))
            max_width = max(max_width, text_surf.get_width())
        
        tooltip_height = line_height * len(lines) + 15
        tooltip_width = max_width + 20
        
        # Position tooltip near mouse but ensure it stays on screen
        tooltip_x = mouse_pos[0] + 15
        tooltip_y = mouse_pos[1] + 15
        
        # Adjust if tooltip would go off screen
        if tooltip_x + tooltip_width > self.screen_width:
            tooltip_x = mouse_pos[0] - tooltip_width - 5
        if tooltip_y + tooltip_height > self.screen_height:
            tooltip_y = mouse_pos[1] - tooltip_height - 5
        
        # Draw tooltip background
        tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
        pygame.draw.rect(surface, (40, 40, 60, 230), tooltip_rect)
        pygame.draw.rect(surface, (200, 200, 200), tooltip_rect, 1)
        
        # Draw tooltip text
        for i, line in enumerate(lines):
            text_surf = self.tooltip_font.render(line, True, (255, 255, 255))
            surface.blit(text_surf, (tooltip_x + 10, tooltip_y + 8 + i * line_height))
    
    def handle_event(self, event, game_state):
        result = {
            "action": None,
            "target": None
        }
        
        # Handle tower info panel events
        action, target = self.tower_info_panel.handle_event(event, game_state.get("money", 0))
        if action:
            result["action"] = action
            result["target"] = target
            return result
        
        # Handle tower selection events
        tower_type = self.tower_selection_panel.handle_event(event)
        if tower_type:
            result["action"] = "select_tower"
            result["target"] = tower_type
            return result
        
        # Handle wave panel events
        action = self.wave_panel.handle_event(event)
        if action:
            result["action"] = action
            return result
        
        return result


# Helper UI Effects

class FloatingText:
    def __init__(self, text, pos, color=(255, 255, 255), size=24, duration=1.0):
        self.text = text
        self.pos = pos
        self.color = color
        self.size = size
        self.duration = duration
        self.life = duration
        self.font = pygame.font.SysFont(None, size)
        self.velocity = (random.uniform(-5, 5), -random.uniform(20, 40))
        
    def update(self, dt):
        self.life -= dt
        self.pos = (self.pos[0] + self.velocity[0] * dt, self.pos[1] + self.velocity[1] * dt)
        # Gradually slow down
        self.velocity = (self.velocity[0] * 0.95, self.velocity[1] * 0.95)
        return self.life > 0
        
    def draw(self, surface, screen_pos=None, scale=1.0):
        # Allow camera transform to provide screen coordinates
        if screen_pos:
            draw_pos = screen_pos
            font_size = int(self.size * scale)
            if font_size != self.font.get_height():
                self.font = pygame.font.SysFont(None, font_size)
        else:
            draw_pos = self.pos
            
        # Calculate alpha based on remaining life
        alpha = min(255, max(0, int(255 * (self.life / self.duration))))
        
        # Render text with shadow for better visibility
        shadow_surf = self.font.render(self.text, True, (0, 0, 0))
        shadow_rect = shadow_surf.get_rect(center=(int(draw_pos[0]) + 2, int(draw_pos[1]) + 2))
        
        text_surf = self.font.render(self.text, True, self.color)
        text_rect = text_surf.get_rect(center=(int(draw_pos[0]), int(draw_pos[1])))
        
        # Apply alpha
        if alpha < 255:
            shadow_surf.set_alpha(alpha)
            text_surf.set_alpha(alpha)
            
        surface.blit(shadow_surf, shadow_rect)
        surface.blit(text_surf, text_rect) 