import pygame
from game.ui.tower_info_panel import TowerInfoPanel
from game.ui.wave_panel import WavePanel
from game.ui.status_panel import StatusPanel
from game.ui.tower_selection_panel import TowerSelectionPanel
from game.ui.floating_text import FloatingText  # Fix circular import by importing directly

class GameUI:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Calculate optimal panel sizes
        self.calculate_panel_dimensions()
        
        # Create panels with the calculated dimensions
        self.create_panels()
        
        # Tower tooltip info for hover
        self.tooltip_font = pygame.font.SysFont(None, 18)
        self.hover_tower = None
        
        # Store floating texts
        self.floating_texts = []
        
    def calculate_panel_dimensions(self):
        """Calculate optimal panel dimensions based on screen size"""
        # Calculate sidebar width proportionally
        self.sidebar_width = int(self.screen_width * 0.185)  # ~260px at 1400px width
        
        # Calculate panel spacing
        self.panel_spacing = int(self.screen_height * 0.022)  # ~20px at 900px height
        
        # Calculate max heights with spacing
        usable_height = self.screen_height - (3 * self.panel_spacing)  # Top, middle, bottom spacing
        
        # Distribute available height proportionally
        # Right side (tower info + wave panel)
        self.info_panel_height = int(usable_height * 0.70)  # 70% for tower info
        self.wave_panel_height = int(usable_height * 0.25)  # 25% for wave info
        
        # Left side (status + tower selection)
        self.status_panel_height = int(usable_height * 0.38)  # 38% for status
        self.tower_selection_height = int(usable_height * 0.57)  # 57% for tower selection
        
        # Ensure the heights don't exceed the available space
        total_right = self.info_panel_height + self.wave_panel_height + self.panel_spacing
        total_left = self.status_panel_height + self.tower_selection_height + self.panel_spacing
        
        if total_right > usable_height:
            # Scale down proportionally
            scale = usable_height / total_right
            self.info_panel_height = int(self.info_panel_height * scale)
            self.wave_panel_height = int(self.wave_panel_height * scale)
            
        if total_left > usable_height:
            # Scale down proportionally
            scale = usable_height / total_left
            self.status_panel_height = int(self.status_panel_height * scale)
            self.tower_selection_height = int(self.tower_selection_height * scale)
    
    def create_panels(self):
        """Create UI panels with calculated dimensions"""
        # Right sidebar for tower info
        self.tower_info_panel = TowerInfoPanel(
            pygame.Rect(
                self.screen_width - self.sidebar_width, 
                self.panel_spacing, 
                self.sidebar_width - self.panel_spacing, 
                self.info_panel_height
            )
        )
        
        # Wave info panel below tower info
        self.wave_panel = WavePanel(
            pygame.Rect(
                self.screen_width - self.sidebar_width, 
                self.panel_spacing * 2 + self.info_panel_height, 
                self.sidebar_width - self.panel_spacing, 
                self.wave_panel_height
            )
        )
        
        # Left sidebar top for status
        self.status_panel = StatusPanel(
            pygame.Rect(
                self.panel_spacing, 
                self.panel_spacing, 
                self.sidebar_width - self.panel_spacing, 
                self.status_panel_height
            )
        )
        
        # Left sidebar bottom for tower selection
        self.tower_selection_panel = TowerSelectionPanel(
            pygame.Rect(
                self.panel_spacing, 
                self.panel_spacing * 2 + self.status_panel_height, 
                self.sidebar_width - self.panel_spacing, 
                self.tower_selection_height
            )
        )
    
    def update_screen_size(self, screen_width, screen_height):
        """Update UI layout when screen is resized"""
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Recalculate panel dimensions for new screen size
        self.calculate_panel_dimensions()
        
        # Update panel positions and sizes
        self.tower_info_panel.rect = pygame.Rect(
            self.screen_width - self.sidebar_width, 
            self.panel_spacing, 
            self.sidebar_width - self.panel_spacing, 
            self.info_panel_height
        )
        
        self.wave_panel.rect = pygame.Rect(
            self.screen_width - self.sidebar_width, 
            self.panel_spacing * 2 + self.info_panel_height,
            self.sidebar_width - self.panel_spacing, 
            self.wave_panel_height
        )
        
        self.status_panel.rect = pygame.Rect(
            self.panel_spacing, 
            self.panel_spacing, 
            self.sidebar_width - self.panel_spacing, 
            self.status_panel_height
        )
        
        self.tower_selection_panel.rect = pygame.Rect(
            self.panel_spacing, 
            self.panel_spacing * 2 + self.status_panel_height,
            self.sidebar_width - self.panel_spacing, 
            self.tower_selection_height
        )
        
        # Update buttons in each panel
        self.tower_info_panel.create_buttons()
        self.wave_panel.create_buttons()
        self.tower_selection_panel.create_buttons()
    
    def add_floating_text(self, x, y, text, color, size=20, lifetime=2.0):
        """Add a floating text message to the UI"""
        self.floating_texts.append(
            FloatingText(text, (x, y), color, size, duration=lifetime)
        )
    
    def update(self, dt, game_state=None):
        """Update UI elements"""
        # Update floating texts
        for text in self.floating_texts[:]:
            if not text.update(dt):
                self.floating_texts.remove(text)
                
    def draw(self, surface, game_state, assets):
        # Update panels with current game state
        self.tower_info_panel.set_tower(game_state.get("selected_tower"), game_state.get("money", 0))
        self.status_panel.update(
            game_state.get("money", 0), 
            game_state.get("lives", 0), 
            game_state.get("current_tower_type"),
            game_state.get("tower_placement_mode", False)
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
        
        # Draw floating texts
        for text in self.floating_texts:
            text.draw(surface)
        
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
        pygame.draw.rect(surface, (25, 25, 35, 230), tooltip_rect)
        pygame.draw.rect(surface, (80, 80, 120), tooltip_rect, 1)
        
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
            
        # Handle status panel events
        status_result = self.status_panel.handle_event(event)
        if status_result["action"]:
            result["action"] = status_result["action"]
            return result
        
        # Handle tower selection events
        tower_type = self.tower_selection_panel.handle_event(event)
        if tower_type:
            if tower_type == "save_load":
                result["action"] = "open_save_menu"
                return result
            else:
                result["action"] = "select_tower"
                result["target"] = tower_type
                return result
        
        # Handle wave panel events
        action = self.wave_panel.handle_event(event)
        if action:
            result["action"] = action
            return result
        
        return result 