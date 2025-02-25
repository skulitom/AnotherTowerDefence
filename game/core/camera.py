import pygame

class Camera:
    """Camera class to handle panning and zooming of the game world"""
    
    def __init__(self, screen_width, screen_height, gameplay_area):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.gameplay_area = gameplay_area  # (x, y, width, height)
        self.x = 0  # Camera position (center of view)
        self.y = 0
        self.zoom = 1.0  # Zoom level
        self.dragging = False
        self.drag_start = (0, 0)
        self.drag_camera_start = (0, 0)
    
    def update_screen_size(self, screen_width, screen_height, gameplay_area=None):
        """Update camera parameters when screen size changes"""
        self.screen_width = screen_width
        self.screen_height = screen_height
        if gameplay_area:
            self.gameplay_area = gameplay_area
    
    def apply(self, x, y):
        """Convert world coordinates to screen coordinates"""
        # Calculate center offset based on camera position and zoom
        screen_center_x = self.screen_width / 2
        screen_center_y = self.screen_height / 2
        
        # Apply zoom and camera position
        screen_x = (x - self.x) * self.zoom + screen_center_x
        screen_y = (y - self.y) * self.zoom + screen_center_y
        
        return (screen_x, screen_y)
    
    def world_to_screen(self, x, y=None):
        """Convert world coordinates to screen coordinates (alias for apply)
        Can be called with either:
        - world_to_screen(x, y) - separate coordinates
        - world_to_screen((x, y)) - tuple of coordinates
        - world_to_screen(Vector2) - pygame Vector2 object
        """
        # Handle Vector2 input
        if y is None and hasattr(x, 'x') and hasattr(x, 'y'):
            return self.apply(x.x, x.y)
        # Handle tuple input
        elif y is None and isinstance(x, tuple) and len(x) == 2:
            return self.apply(x[0], x[1])
        # Handle separate x, y coordinates
        return self.apply(x, y)
    
    def unapply(self, screen_x, screen_y):
        """Convert screen coordinates to world coordinates"""
        screen_center_x = self.screen_width / 2
        screen_center_y = self.screen_height / 2
        
        # Undo zoom and camera position
        x = (screen_x - screen_center_x) / self.zoom + self.x
        y = (screen_y - screen_center_y) / self.zoom + self.y
        
        return (x, y)
    
    def screen_to_world(self, screen_x, screen_y=None):
        """Convert screen coordinates to world coordinates (alias for unapply)
        Can be called with either:
        - screen_to_world(x, y) - separate coordinates
        - screen_to_world((x, y)) - tuple of coordinates
        - screen_to_world(Vector2) - pygame Vector2 object
        """
        # Handle Vector2 input
        if screen_y is None and hasattr(screen_x, 'x') and hasattr(screen_x, 'y'):
            return self.unapply(screen_x.x, screen_x.y)
        # Handle tuple input
        elif screen_y is None and isinstance(screen_x, tuple) and len(screen_x) == 2:
            return self.unapply(screen_x[0], screen_x[1])
        # Handle separate x, y coordinates
        return self.unapply(screen_x, screen_y)
    
    def move(self, dx, dy):
        """Move the camera by the given amount"""
        self.x += dx
        self.y += dy
    
    def zoom_at(self, screen_x, screen_y, factor):
        """Zoom in/out at the given screen position"""
        # Convert screen position to world coordinates before zooming
        world_x, world_y = self.unapply(screen_x, screen_y)
        
        # Apply zoom factor
        old_zoom = self.zoom
        self.zoom *= factor
        
        # Clamp zoom level
        self.zoom = max(0.2, min(self.zoom, 3.0))
        
        # If zoom didn't change, return
        if old_zoom == self.zoom:
            return
        
        # Adjust camera position to zoom at cursor
        # This keeps the world point under the cursor in the same screen position
        new_world_x, new_world_y = self.unapply(screen_x, screen_y)
        self.x += (world_x - new_world_x)
        self.y += (world_y - new_world_y)
    
    def start_drag(self, screen_x, screen_y):
        """Start dragging the camera from the given screen position"""
        self.dragging = True
        self.drag_start = (screen_x, screen_y)
        self.drag_camera_start = (self.x, self.y)
    
    def update_drag(self, screen_x, screen_y):
        """Update camera position based on current drag position"""
        if self.dragging:
            dx = (screen_x - self.drag_start[0]) / self.zoom
            dy = (screen_y - self.drag_start[1]) / self.zoom
            self.x = self.drag_camera_start[0] - dx
            self.y = self.drag_camera_start[1] - dy
    
    def end_drag(self):
        """End camera dragging"""
        self.dragging = False 