import pygame
from game.utils import create_element_icon
from game.settings import tower_types, upgrade_paths
from game.ui.button import Button

class TowerInfoPanel:
    def __init__(self, rect, assets):
        self.rect = rect
        self.tower = None
        self.border_radius = 10
        self.assets = assets
        
        self.upgrade_buttons = []
        self.sell_button = None
        self.create_buttons()
        
    def create_buttons(self):
        # Calculate button sizes based on panel dimensions
        button_height = min(40, int(self.rect.height * 0.09))  # Make button height proportional
        button_width = self.rect.width - 20
        
        # Calculate available space for buttons
        content_height = self.rect.height - 160  # Space after tower info
        buttons_needed = 6  # 4 upgrade buttons + targeting + sell button
        spacing = max(5, min(10, (content_height - buttons_needed * button_height) // (buttons_needed + 1)))
        
        # Create upgrade buttons with dynamic positioning
        self.upgrade_buttons = []
        for i, upgrade_type in enumerate(["damage", "range", "speed", "special"]):
            # Position based on available space
            y_pos = self.rect.y + 160 + spacing + i * (button_height + spacing)
            button_rect = pygame.Rect(self.rect.x + 10, y_pos, button_width, button_height)
            
            name = upgrade_paths[upgrade_type]["name"]
            description = upgrade_paths[upgrade_type]["description"]
            button = Button(
                button_rect, 
                name, 
                color=(60, 120, 180),
                hover_color=(80, 150, 220),
                tooltip=description,
                assets=self.assets
            )
            self.upgrade_buttons.append((upgrade_type, button))
        
        # Create targeting button
        targeting_rect = pygame.Rect(
            self.rect.x + 10,
            self.rect.y + 160 + spacing + 4 * (button_height + spacing),
            button_width,
            button_height
        )
        self.targeting_button = Button(
            targeting_rect,
            "Target: First",
            color=(80, 120, 80),
            hover_color=(100, 150, 100),
            tooltip="Change tower targeting priority",
            assets=self.assets
        )
        
        # Create sell button at the bottom with appropriate spacing
        sell_rect = pygame.Rect(
            self.rect.x + 10, 
            self.rect.y + 160 + spacing + 5 * (button_height + spacing),
            button_width, 
            button_height
        )
        self.sell_button = Button(
            sell_rect,
            "Sell Tower",
            color=(180, 60, 60),
            hover_color=(220, 80, 80),
            tooltip="Sell this tower to reclaim some money",
            assets=self.assets
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
        
        # Update targeting button
        if tower:
            self.targeting_button.text = f"Target: {tower.targeting_priority}"
            self.targeting_button.enabled = True
        else:
            self.targeting_button.text = "Target: None"
            self.targeting_button.enabled = False
        
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
            return [] # Return empty list instead of None
            
        # Get fonts from assets
        font_title = assets["fonts"].get("title")
        font_body = assets["fonts"].get("body")
        font_small = assets["fonts"].get("body_small")
        
        # Create panel surface with rounded corners and glow
        panel_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        
        # Draw panel background gradient
        for y in range(self.rect.height):
            progress = y / self.rect.height
            r = int(25 * (1 - progress) + 15 * progress)
            g = int(25 * (1 - progress) + 15 * progress)
            b = int(40 * (1 - progress) + 30 * progress)
            pygame.draw.line(panel_surf, (r, g, b, 230), (0, y), (self.rect.width, y))
        
        # Draw border with glow
        pygame.draw.rect(panel_surf, (0, 0, 0, 0), (0, 0, self.rect.width, self.rect.height), border_radius=self.border_radius)
        pygame.draw.rect(panel_surf, (80, 100, 180, 100), (0, 0, self.rect.width, self.rect.height), 1, border_radius=self.border_radius)
        
        # Add top highlight
        pygame.draw.line(panel_surf, (120, 140, 200, 60), (5, 2), (self.rect.width-5, 2))
        
        # Blit panel surface
        surface.blit(panel_surf, self.rect.topleft)
        
        # Calculate proportional sizing
        header_height = int(self.rect.height * 0.09)  # ~9% of panel height for header
        icon_size = min(64, int(self.rect.height * 0.13))  # Scale icon based on panel height
        
        # Draw header strip
        header_surf = pygame.Surface((self.rect.width, header_height), pygame.SRCALPHA)
        for y in range(header_height):
            progress = y / header_height
            r = int(40 * (1 - progress) + 25 * progress)
            g = int(40 * (1 - progress) + 25 * progress)
            b = int(70 * (1 - progress) + 45 * progress)
            pygame.draw.line(header_surf, (r, g, b), (0, y), (self.rect.width, y))
        # Round corners only on top
        pygame.draw.rect(header_surf, (0, 0, 0, 0), (0, 0, self.rect.width, header_height), border_radius=self.border_radius)
        surface.blit(header_surf, self.rect.topleft)
        
        # Draw tower name with shadow
        title_text = f"{self.tower.tower_type} Tower (Level {self.tower.level})"
        shadow_surf = font_title.render(title_text, True, (0, 0, 0))
        title_surf = font_title.render(title_text, True, (255, 255, 255))
        title_rect = title_surf.get_rect(midtop=(self.rect.centerx, self.rect.y + 10))
        surface.blit(shadow_surf, (title_rect.x+1, title_rect.y+1))
        surface.blit(title_surf, title_rect)
        
        # Draw tower info with better spacing
        tower_img = assets["towers"].get(self.tower.tower_type)
        icon_y_pos = title_rect.bottom + 5  # Position icon closer to title
        
        if tower_img:
            img = pygame.transform.scale(tower_img, (icon_size, icon_size))
            img_rect = img.get_rect(midtop=(self.rect.centerx, icon_y_pos))
            # Add glow behind tower image
            glow_surf = pygame.Surface((icon_size + 16, icon_size + 16), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*self.tower.color, 90), (glow_surf.get_width()//2, glow_surf.get_height()//2), icon_size//2)
            surface.blit(glow_surf, (img_rect.centerx - glow_surf.get_width()//2, img_rect.centery - glow_surf.get_height()//2))
            surface.blit(img, img_rect)
        else:
            icon = create_element_icon(self.tower.tower_type, icon_size)
            icon_rect = icon.get_rect(midtop=(self.rect.centerx, icon_y_pos))
            # Add glow behind tower icon
            glow_surf = pygame.Surface((icon_size + 16, icon_size + 16), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*self.tower.color, 90), (glow_surf.get_width()//2, glow_surf.get_height()//2), icon_size//2)
            surface.blit(glow_surf, (icon_rect.centerx - glow_surf.get_width()//2, icon_rect.centery - glow_surf.get_height()//2))
            surface.blit(icon, icon_rect)
        
        # Calculate stats position to be closer to icon
        stats_y = icon_y_pos + icon_size + 5  # Position stat box right after icon
        stat_x = self.rect.x + 20
        
        # Draw stat box with compact height
        stat_box_height = int(self.rect.height * 0.12)  # More compact stat box
        stat_box = pygame.Rect(stat_x-10, stats_y-5, self.rect.width-20, stat_box_height)
        stat_surf = pygame.Surface((stat_box.width, stat_box.height), pygame.SRCALPHA)
        stat_surf.fill((0, 0, 0, 40))
        pygame.draw.rect(stat_surf, (100, 100, 150, 80), (0, 0, stat_box.width, stat_box.height), 1, border_radius=5)
        surface.blit(stat_surf, stat_box.topleft)
        
        # Space stats vertically more efficiently
        line_height = font_body.get_height()
        
        # Draw damage stat
        damage_text = f"Damage: {self.tower.current_damage:.1f}"
        if self.tower.buff_multiplier > 1.0:
            damage_text += f" (Buffed)"
            damage_color = (100, 255, 100)
        else:
            damage_color = (255, 200, 100)
        damage_surf = font_body.render(damage_text, True, damage_color)
        surface.blit(damage_surf, (stat_x, stats_y))
        
        # Draw range stat
        range_text = f"Range: {self.tower.range:.0f}"
        range_surf = font_body.render(range_text, True, (100, 200, 255))
        surface.blit(range_surf, (stat_x, stats_y + line_height))
        
        # Draw speed stat
        speed_text = f"Attack Speed: {1/self.tower.cooldown:.1f}/s"
        speed_surf = font_body.render(speed_text, True, (200, 150, 255))
        surface.blit(speed_surf, (stat_x, stats_y + line_height * 2))
        
        # Draw special ability description with style (if it exists and fits)
        if self.tower.special_ability:
            description = tower_types[self.tower.tower_type].get("description", "")
            if description:
                # Position description box right after stats
                desc_y = stats_y + line_height * 3 + 5
                desc_box = pygame.Rect(stat_x-10, desc_y, self.rect.width-20, line_height + 10)
                
                # Check if description box would fit before upgrade buttons
                first_button_y = self.upgrade_buttons[0][1].rect.y if self.upgrade_buttons else self.rect.bottom
                if desc_box.bottom < first_button_y - 10:  # Only draw if it fits
                    desc_surf = pygame.Surface((desc_box.width, desc_box.height), pygame.SRCALPHA)
                    desc_surf.fill((100, 100, 100, 30))
                    pygame.draw.rect(desc_surf, (150, 150, 150, 80), (0, 0, desc_box.width, desc_box.height), 1, border_radius=5)
                    surface.blit(desc_surf, desc_box.topleft)
                    
                    # Use the loaded small body font for description
                    ability_surf = font_small.render(description, True, (220, 220, 220))
                    ability_rect = ability_surf.get_rect(center=(self.rect.centerx, desc_y + desc_box.height/2))
                    surface.blit(ability_surf, ability_rect)
        
        # Draw upgrade buttons
        for _, button in self.upgrade_buttons:
            button.draw(surface)
            
        # Draw targeting button
        self.targeting_button.draw(surface)
        
        # Draw sell button
        self.sell_button.draw(surface)
        
        # Collect tooltips
        tooltips_to_draw = []
        for _, button in self.upgrade_buttons:
            tooltip_surf, tooltip_rect = button.get_tooltip_surface(surface.get_width(), surface.get_height())
            if tooltip_surf:
                tooltips_to_draw.append((tooltip_surf, tooltip_rect))
                
        # Add targeting button tooltip
        tooltip_surf, tooltip_rect = self.targeting_button.get_tooltip_surface(surface.get_width(), surface.get_height())
        if tooltip_surf:
            tooltips_to_draw.append((tooltip_surf, tooltip_rect))
                
        if self.sell_button:
            tooltip_surf, tooltip_rect = self.sell_button.get_tooltip_surface(surface.get_width(), surface.get_height())
            if tooltip_surf:
                tooltips_to_draw.append((tooltip_surf, tooltip_rect))
                
        return tooltips_to_draw # Return the list
    
    def handle_event(self, event, money):
        if not self.tower:
            return None, None
            
        mouse_pos = pygame.mouse.get_pos()
        # Check specifically for MOUSEBUTTONDOWN event for this button click detection
        mouse_button_down_event = event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
        
        # Check upgrade buttons
        for upgrade_type, button in self.upgrade_buttons:
            # Pass mouse position and the specific click event flag
            if button.update(mouse_pos, mouse_button_down_event):
                return "upgrade", upgrade_type
                
        # Check targeting button
        # Pass mouse position and the specific click event flag
        if self.targeting_button.update(mouse_pos, mouse_button_down_event):
            return "target", None
                
        # Check sell button
        # Pass mouse position and the specific click event flag
        if self.sell_button.update(mouse_pos, mouse_button_down_event):
            return "sell", None
            
        return None, None 