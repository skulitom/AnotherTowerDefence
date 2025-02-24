import pygame
import random
import math


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


class Camera:
    def __init__(self, width, height, gameplay_area):
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0
        self.zoom = 1.0
        self.min_zoom = 0.5
        self.max_zoom = 2.0
        self.drag_start = None
        
        # Define boundaries for camera movement
        # gameplay_area is a tuple (left, top, right, bottom)
        self.boundaries = gameplay_area
        
    def apply(self, x, y):
        """Convert world coordinates to screen coordinates"""
        screen_x = (x - self.x) * self.zoom + self.width / 2
        screen_y = (y - self.y) * self.zoom + self.height / 2
        return screen_x, screen_y
    
    def apply_rect(self, rect):
        """Convert a pygame Rect from world to screen coordinates"""
        x1, y1 = self.apply(rect.left, rect.top)
        x2, y2 = self.apply(rect.right, rect.bottom)
        width = x2 - x1
        height = y2 - y1
        return pygame.Rect(x1, y1, width, height)
        
    def unapply(self, screen_x, screen_y):
        """Convert screen coordinates to world coordinates"""
        x = (screen_x - self.width / 2) / self.zoom + self.x
        y = (screen_y - self.height / 2) / self.zoom + self.y
        return x, y
        
    def start_drag(self, screen_x, screen_y):
        """Start camera drag from screen coordinates"""
        self.drag_start = (screen_x, screen_y)
        
    def update_drag(self, screen_x, screen_y):
        """Update camera position based on drag"""
        if self.drag_start:
            # Calculate the movement in world space
            dx = (screen_x - self.drag_start[0]) / self.zoom
            dy = (screen_y - self.drag_start[1]) / self.zoom
            
            # Update camera position
            new_x = self.x - dx
            new_y = self.y - dy
            
            # Enforce boundaries
            if self.boundaries:
                # Calculate visible area in world coordinates
                half_width = self.width / (2 * self.zoom)
                half_height = self.height / (2 * self.zoom)
                
                # Enforce x-boundary
                if self.boundaries[0] is not None and new_x - half_width < self.boundaries[0]:
                    new_x = self.boundaries[0] + half_width
                if self.boundaries[2] is not None and new_x + half_width > self.boundaries[2]:
                    new_x = self.boundaries[2] - half_width
                
                # Enforce y-boundary
                if self.boundaries[1] is not None and new_y - half_height < self.boundaries[1]:
                    new_y = self.boundaries[1] + half_height
                if self.boundaries[3] is not None and new_y + half_height > self.boundaries[3]:
                    new_y = self.boundaries[3] - half_height
            
            self.x = new_x
            self.y = new_y
            
            # Update drag start position
            self.drag_start = (screen_x, screen_y)
            
    def end_drag(self):
        """End camera drag"""
        self.drag_start = None
        
    def zoom_at(self, screen_x, screen_y, factor):
        """Zoom camera centered at screen position"""
        # Convert screen position to world position
        world_x, world_y = self.unapply(screen_x, screen_y)
        
        # Calculate new zoom level
        new_zoom = max(self.min_zoom, min(self.max_zoom, self.zoom * factor))
        
        # Adjust camera position to keep the zoom point stationary
        if new_zoom != self.zoom:
            zoom_ratio = new_zoom / self.zoom
            self.x = world_x - (world_x - self.x) / zoom_ratio
            self.y = world_y - (world_y - self.y) / zoom_ratio
            self.zoom = new_zoom
            
            # Check boundaries after zooming
            self.enforce_boundaries()
            
    def move(self, dx, dy):
        """Move camera by the specified amount"""
        self.x += dx / self.zoom
        self.y += dy / self.zoom
        self.enforce_boundaries()
            
    def enforce_boundaries(self):
        """Ensure camera stays within boundaries"""
        if self.boundaries:
            # Calculate visible area in world coordinates
            half_width = self.width / (2 * self.zoom)
            half_height = self.height / (2 * self.zoom)
            
            # Enforce x-boundary
            if self.boundaries[0] is not None and self.x - half_width < self.boundaries[0]:
                self.x = self.boundaries[0] + half_width
            if self.boundaries[2] is not None and self.x + half_width > self.boundaries[2]:
                self.x = self.boundaries[2] - half_width
            
            # Enforce y-boundary
            if self.boundaries[1] is not None and self.y - half_height < self.boundaries[1]:
                self.y = self.boundaries[1] + half_height
            if self.boundaries[3] is not None and self.y + half_height > self.boundaries[3]:
                self.y = self.boundaries[3] - half_height


class Particle:
    def __init__(self, x, y, color, velocity, size, life, gravity=0):
        self.x = x
        self.y = y
        self.color = color
        self.velocity = velocity
        self.size = size
        self.life = life
        self.max_life = life
        self.gravity = gravity
        self.alpha = 255

    def update(self, dt):
        self.x += self.velocity[0] * dt
        self.y += self.velocity[1] * dt
        self.velocity = (self.velocity[0], self.velocity[1] + self.gravity * dt)
        self.life -= dt
        self.alpha = int(255 * (self.life / self.max_life))
        self.size *= max(0.95, 1 - (dt * 2))
        return self.life > 0

    def draw(self, surface, camera=None):
        if self.alpha <= 0:
            return
            
        # Apply camera transformation if provided
        if camera:
            screen_x, screen_y = camera.apply(self.x, self.y)
            screen_size = self.size * camera.zoom
        else:
            screen_x, screen_y = self.x, self.y
            screen_size = self.size
            
        s = pygame.Surface((int(screen_size * 2), int(screen_size * 2)), pygame.SRCALPHA)
        r, g, b = self.color
        pygame.draw.circle(s, (r, g, b, self.alpha), (int(screen_size), int(screen_size)), int(screen_size))
        surface.blit(s, (int(screen_x - screen_size), int(screen_y - screen_size)))


class ParticleSystem:
    def __init__(self, max_particles=200):
        self.particles = []
        self.max_particles = max_particles

    def add_particle(self, particle):
        if len(self.particles) < self.max_particles:
            self.particles.append(particle)
            
    def add_particle_params(self, pos, color, velocity, size, life, gravity=0):
        """Convenience method that creates and adds a particle using parameters"""
        if len(self.particles) < self.max_particles:
            x = pos.x if hasattr(pos, 'x') else pos[0]
            y = pos.y if hasattr(pos, 'y') else pos[1]
            particle = Particle(x, y, color, velocity, size, life, gravity)
            self.particles.append(particle)

    def add_explosion(self, x, y, color, count=20, size_range=(3, 8), life_range=(0.5, 1.5), speed_range=(50, 150)):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(speed_range[0], speed_range[1])
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            size = random.uniform(size_range[0], size_range[1])
            life = random.uniform(life_range[0], life_range[1])
            
            # Add slight color variation
            r = min(255, max(0, color[0] + random.randint(-20, 20)))
            g = min(255, max(0, color[1] + random.randint(-20, 20)))
            b = min(255, max(0, color[2] + random.randint(-20, 20)))
            
            self.add_particle(Particle(x, y, (r, g, b), velocity, size, life))

    def add_trail(self, x, y, color, count=1, size_range=(2, 4), life_range=(0.2, 0.8), speed_range=(5, 20)):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(speed_range[0], speed_range[1])
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            size = random.uniform(size_range[0], size_range[1])
            life = random.uniform(life_range[0], life_range[1])
            
            r = min(255, max(0, color[0] + random.randint(-10, 10)))
            g = min(255, max(0, color[1] + random.randint(-10, 10)))
            b = min(255, max(0, color[2] + random.randint(-10, 10)))
            
            self.add_particle(Particle(x, y, (r, g, b), velocity, size, life, gravity=5))

    def update(self, dt):
        self.particles = [p for p in self.particles if p.update(dt)]

    def draw(self, surface, camera=None):
        for p in self.particles:
            p.draw(surface, camera)


def draw_hp_bar(surface, x, y, width, height, value, max_value, border_color=(200, 200, 200), fill_color=(0, 255, 0), background_color=(60, 60, 60), camera=None):
    if camera:
        screen_x, screen_y = camera.apply(x, y)
        scaled_width = width * camera.zoom
        scaled_height = height * camera.zoom
    else:
        screen_x, screen_y = x, y
        scaled_width = width
        scaled_height = height

    ratio = max(0, min(value / max_value, 1))
    outline_rect = pygame.Rect(screen_x, screen_y, scaled_width, scaled_height)
    fill_rect = pygame.Rect(screen_x, screen_y, scaled_width * ratio, scaled_height)
    
    pygame.draw.rect(surface, background_color, outline_rect)
    pygame.draw.rect(surface, fill_color, fill_rect)
    pygame.draw.rect(surface, border_color, outline_rect, 1)


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
    elif element_type == "Air":
        for i in range(3):
            offset = i * 5
            pygame.draw.arc(surface, (255, 255, 255, 150), (size//4 - offset, size//4, size//2 + offset*2, size//2), 0, math.pi, 2)
    elif element_type == "Earth":
        pygame.draw.rect(surface, (101, 67, 33), (size//4, size//4, size//2, size//2))
    elif element_type == "Darkness":
        pygame.draw.circle(surface, (30, 0, 30), (size//2, size//2), size//3)
        pygame.draw.circle(surface, (80, 0, 80), (size//2, size//2), size//4)
    elif element_type == "Light":
        # Draw sun rays
        for i in range(8):
            angle = i * math.pi / 4
            x1 = size//2 + math.cos(angle) * (size//4)
            y1 = size//2 + math.sin(angle) * (size//4)
            x2 = size//2 + math.cos(angle) * (size//1.5)
            y2 = size//2 + math.sin(angle) * (size//1.5)
            pygame.draw.line(surface, (255, 255, 200), (x1, y1), (x2, y2), 2)
    elif element_type == "Life":
        # Draw heart shape
        pygame.draw.circle(surface, (255, 200, 200), (size//3, size//2.5), size//5)
        pygame.draw.circle(surface, (255, 200, 200), (size//1.5, size//2.5), size//5)
        points = [(size//2, size//1.5), (size//4, size//3), (size//1.3, size//3)]
        pygame.draw.polygon(surface, (255, 200, 200), points)
    
    return surface 