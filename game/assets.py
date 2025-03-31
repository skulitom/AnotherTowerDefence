import pygame
import os
from game.settings import tower_types
import random
import math

# Define font paths
FONT_DIR = "assets/fonts"
TITLE_FONT_PATH = os.path.join(FONT_DIR, "TitleFont.ttf") # Example filename
BODY_FONT_PATH = os.path.join(FONT_DIR, "BodyFont.ttf")   # Example filename

# Move the create_element_icon function here to avoid circular imports
def create_element_icon(element_type, size):
    """Create a stylized element icon for the tower type"""
    colors = {
        "Fire": (255, 0, 0),
        "Water": (0, 0, 255),
        "Air": (135, 206, 235),
        "Earth": (139, 69, 19),
        "Darkness": (128, 0, 128),
        "Light": (255, 255, 0),
        "Life": (255, 105, 180)
    }
    
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    color = colors.get(element_type, (255, 255, 255))
    
    # Base circle for all elements
    pygame.draw.circle(surface, color, (size//2, size//2), size//2)
    
    # Add element-specific details
    if element_type == "Fire":
        points = [(size//2, size//5), (size//3, size//2), (size//2, size//1.5), (size//1.5, size//2)]
        pygame.draw.polygon(surface, (255, 165, 0), points)
    elif element_type == "Water":
        pygame.draw.arc(surface, (173, 216, 230), (size//4, size//4, size//2, size//2), 0, math.pi, 3)
        pygame.draw.arc(surface, (173, 216, 230), (size//4, size//2, size//2, size//2), math.pi, 2*math.pi, 3)
    
    return surface


def load_assets():
    """Load all game assets or create placeholder graphics when needed"""
    assets = {"towers": {}, "enemy": None, "projectile": None, "ui": {}, "fonts": {}}
    
    # --- Load Fonts ---
    # Ensure fonts directory exists
    if not os.path.exists(FONT_DIR):
        try:
            os.makedirs(FONT_DIR)
            print(f"Created font directory: {FONT_DIR}")
            print(f"Please place your .ttf or .otf font files there (e.g., TitleFont.ttf, BodyFont.ttf).")
        except OSError as e:
            print(f"Error creating font directory {FONT_DIR}: {e}")

    # Load Title Font
    try:
        assets["fonts"]["title"] = pygame.font.Font(TITLE_FONT_PATH, 28)
    except (pygame.error, FileNotFoundError):
        print(f"Warning: Title font '{TITLE_FONT_PATH}' not found. Using default font.")
        assets["fonts"]["title"] = pygame.font.SysFont(None, 30) # Default fallback
        
    # Load Body Font
    try:
        assets["fonts"]["body"] = pygame.font.Font(BODY_FONT_PATH, 22)
    except (pygame.error, FileNotFoundError):
        print(f"Warning: Body font '{BODY_FONT_PATH}' not found. Using default font.")
        assets["fonts"]["body"] = pygame.font.SysFont(None, 24) # Default fallback
        
    # Load Small Body Font (for descriptions, tooltips etc.)
    try:
        assets["fonts"]["body_small"] = pygame.font.Font(BODY_FONT_PATH, 18)
    except (pygame.error, FileNotFoundError):
        # No warning for this one if body font already failed
        assets["fonts"]["body_small"] = pygame.font.SysFont(None, 20) # Default fallback

    # Try to load tower images
    for tower_type in tower_types:
        try:
            assets["towers"][tower_type] = pygame.image.load(f"assets/{tower_type.lower()}.png").convert_alpha()
        except (pygame.error, FileNotFoundError):
            # Generate placeholder tower icon
            assets["towers"][tower_type] = create_element_icon(tower_type, 30)
    
    # Try to load enemy image
    try:
        assets["enemy"] = pygame.image.load("assets/enemy.png").convert_alpha()
    except (pygame.error, FileNotFoundError):
        # Create placeholder enemy image
        enemy_size = (20, 20)
        enemy_surf = pygame.Surface(enemy_size, pygame.SRCALPHA)
        pygame.draw.circle(enemy_surf, (0, 200, 0), (enemy_size[0]//2, enemy_size[1]//2), enemy_size[0]//2)
        
        # Add some detail to make it look better
        pygame.draw.circle(enemy_surf, (0, 255, 0, 150), (enemy_size[0]//2, enemy_size[1]//2), enemy_size[0]//3)
        pygame.draw.circle(enemy_surf, (0, 100, 0), (enemy_size[0]//2, enemy_size[1]//2), enemy_size[0]//2, 2)
        assets["enemy"] = enemy_surf
    
    # Try to load projectile image
    try:
        assets["projectile"] = pygame.image.load("assets/projectile.png").convert_alpha()
    except (pygame.error, FileNotFoundError):
        # Create placeholder projectile image
        proj_size = (10, 10)
        proj_surf = pygame.Surface(proj_size, pygame.SRCALPHA)
        
        # Add glow effect
        for i in range(5, 0, -1):
            alpha = 50 + 40 * (5-i)
            radius = proj_size[0]//2 * (i/5)
            pygame.draw.circle(proj_surf, (255, 255, 255, alpha), (proj_size[0]//2, proj_size[1]//2), radius)
        
        pygame.draw.circle(proj_surf, (255, 255, 255), (proj_size[0]//2, proj_size[1]//2), proj_size[0]//2 - 1)
        assets["projectile"] = proj_surf
        
    # Load UI elements
    try:
        assets["ui"]["button"] = pygame.image.load("assets/button.png").convert_alpha()
    except (pygame.error, FileNotFoundError):
        # Create placeholder button with modern style
        button_size = (100, 40)
        button_surf = pygame.Surface(button_size, pygame.SRCALPHA)
        
        # Draw gradient background
        for y in range(button_size[1]):
            progress = y / button_size[1]
            r = int(60 * (1 - progress) + 40 * progress)
            g = int(60 * (1 - progress) + 40 * progress)
            b = int(100 * (1 - progress) + 70 * progress)
            pygame.draw.line(button_surf, (r, g, b, 230), (0, y), (button_size[0], y))
            
        # Add rounded corners and border
        pygame.draw.rect(button_surf, (0, 0, 0, 0), (0, 0, button_size[0], button_size[1]), border_radius=8)
        pygame.draw.rect(button_surf, (100, 140, 200, 150), (0, 0, button_size[0], button_size[1]), 2, border_radius=8)
        
        # Add highlight to top edge
        pygame.draw.line(button_surf, (150, 150, 200, 100), (4, 2), (button_size[0]-4, 2))
        
        assets["ui"]["button"] = button_surf
    
    # Generate background image if needed
    if not os.path.exists("assets/background.png"):
        # Create a more interesting background pattern
        bg_size = (400, 400)  # Larger for more detail
        bg_surf = pygame.Surface(bg_size)
        
        # Fill with gradient
        for y in range(bg_size[1]):
            progress = y / bg_size[1]
            r = int(30 * (1 - progress) + 20 * progress)
            g = int(30 * (1 - progress) + 20 * progress)
            b = int(50 * (1 - progress) + 40 * progress)
            pygame.draw.line(bg_surf, (r, g, b), (0, y), (bg_size[0], y))
        
        # Add subtle grid pattern
        for x in range(0, bg_size[0], 40):
            for y in range(0, bg_size[1], 40):
                if (x + y) % 80 == 0:
                    # Draw lighter squares
                    pygame.draw.rect(bg_surf, (40, 40, 60, 150), (x, y, 20, 20))
                    # Add subtle highlights
                    pygame.draw.line(bg_surf, (50, 50, 70), (x, y), (x+20, y))
                    pygame.draw.line(bg_surf, (50, 50, 70), (x, y), (x, y+20))
                else:
                    # Draw darker squares
                    pygame.draw.rect(bg_surf, (25, 25, 45, 150), (x+20, y+20, 20, 20))
                    # Add subtle shadows
                    pygame.draw.line(bg_surf, (15, 15, 35), (x+20, y+40), (x+40, y+40))
                    pygame.draw.line(bg_surf, (15, 15, 35), (x+40, y+20), (x+40, y+40))
        
        # Add some random subtle dots for texture
        for _ in range(100):
            x = random.randint(0, bg_size[0]-1)
            y = random.randint(0, bg_size[1]-1)
            bright = random.randint(40, 60)
            pygame.draw.circle(bg_surf, (bright, bright, bright+10), (x, y), 1)
        
        assets["background"] = bg_surf
        
        # Try to save the generated background
        try:
            # Create assets directory if it doesn't exist
            if not os.path.exists("assets"):
                os.makedirs("assets")
            pygame.image.save(bg_surf, "assets/background.png")
        except Exception as e:
            print(f"Could not save background: {e}")
    else:
        try:
            assets["background"] = pygame.image.load("assets/background.png").convert()
        except:
            # Fallback
            bg_surf = pygame.Surface((200, 200))
            bg_surf.fill((30, 30, 50))
            assets["background"] = bg_surf
    
    # Generate UI panel background if needed
    panel_size = (200, 100)
    panel_surf = pygame.Surface(panel_size, pygame.SRCALPHA)
    
    # Create gradient background
    for y in range(panel_size[1]):
        progress = y / panel_size[1]
        r = int(40 * (1 - progress) + 30 * progress)
        g = int(40 * (1 - progress) + 30 * progress)
        b = int(70 * (1 - progress) + 50 * progress)
        pygame.draw.line(panel_surf, (r, g, b, 230), (0, y), (panel_size[0], y))
    
    # Add rounded corners and border
    pygame.draw.rect(panel_surf, (0, 0, 0, 0), (0, 0, panel_size[0], panel_size[1]), border_radius=10)
    pygame.draw.rect(panel_surf, (100, 120, 180, 150), (0, 0, panel_size[0], panel_size[1]), 2, border_radius=10)
    
    # Add highlight to top edge
    pygame.draw.line(panel_surf, (150, 150, 200, 100), (5, 2), (panel_size[0]-5, 2))
    
    assets["ui"]["panel"] = panel_surf
    
    # Generate UI Icons (Money and Lives)
    icon_size = 20 # Define a standard size for these icons
    
    # Money Icon (Gold Coin)
    money_icon_surf = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
    pygame.draw.circle(money_icon_surf, (255, 215, 0), (icon_size//2, icon_size//2), icon_size//2) # Gold color
    pygame.draw.circle(money_icon_surf, (218, 165, 32), (icon_size//2, icon_size//2), icon_size//2, 1) # Darker border
    # Add a simple '$' sign
    font = pygame.font.SysFont(None, 18)
    dollar_sign = font.render('$', True, (184, 134, 11))
    dollar_rect = dollar_sign.get_rect(center=(icon_size//2, icon_size//2))
    money_icon_surf.blit(dollar_sign, dollar_rect)
    assets["ui"]["money_icon"] = money_icon_surf
    
    # Lives Icon (Heart)
    lives_icon_surf = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
    # Draw heart shape (simplified)
    heart_color = (220, 20, 60) # Crimson red
    pygame.draw.circle(lives_icon_surf, heart_color, (icon_size*0.3, icon_size*0.35), icon_size*0.3)
    pygame.draw.circle(lives_icon_surf, heart_color, (icon_size*0.7, icon_size*0.35), icon_size*0.3)
    points = [
        (icon_size*0.5, icon_size*0.8), # Bottom point
        (icon_size*0.05, icon_size*0.4), # Top-left near circle edge
        (icon_size*0.95, icon_size*0.4)  # Top-right near circle edge
    ]
    pygame.draw.polygon(lives_icon_surf, heart_color, points)
    pygame.draw.polygon(lives_icon_surf, (139, 0, 0), points, 1) # Darker border
    assets["ui"]["lives_icon"] = lives_icon_surf
    
    return assets 