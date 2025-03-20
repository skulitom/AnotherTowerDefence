"""
Procedural Path Generator for Tower Defense Game

This module handles the generation of random, diverse paths for enemies to follow.
"""
import random
import math
from pygame import Vector2

class PathGenerator:
    """Class to generate procedural paths for tower defense levels"""
    
    def __init__(self):
        """Initialize the path generator"""
        self.complexity_min = 3  # Minimum number of path segments
        self.complexity_max = 8  # Maximum number of path segments
        self.grid_size = 8       # Higher values create more structured paths
        
    def generate_path(self, screen_width, screen_height, seed=1, complexity_override=None):
        """
        Generate a procedural path for a level
        
        Args:
            screen_width: Width of the game screen
            screen_height: Height of the game screen
            seed: Random seed for reproducible paths
            complexity_override: Override the automatic complexity calculation
            
        Returns:
            List of normalized path points [(x, y), ...]
        """
        # Use seed for reproducible paths
        random.seed(seed)
            
        # Adjust complexity based on seed
        if complexity_override is not None:
            complexity = complexity_override
        else:
            # Use seed to derive a complexity level - ensures same seed always gives same complexity
            seed_complexity = (seed % 5) + 1  # Convert seed to a value 1-5
            complexity = min(
                self.complexity_max,
                self.complexity_min + seed_complexity
            )
        
        # Create empty path
        path = []
        
        # Start from left edge at a random height
        start_y = random.uniform(0.2, 0.8)
        path.append((0, start_y))
        
        # Generate intermediate points
        x_step = 1.0 / (complexity + 1)
        current_x = x_step
        prev_y = start_y
        
        # Direction alternating (horizontal paths with vertical connections)
        for i in range(complexity):
            # For more advanced seeds, occasionally add diagonal paths
            use_diagonal = seed > 50 and random.random() < 0.3
            
            if use_diagonal:
                # Diagonal path segment
                next_x = current_x + x_step
                # Make sure we stay in bounds
                next_y = random.uniform(0.2, 0.8)
                path.append((next_x, next_y))
                current_x = next_x
                prev_y = next_y
            else:
                # Traditional horizontal then vertical path
                # Add horizontal segment
                next_y = random.uniform(0.2, 0.8)
                # Snap to grid for cleaner paths
                next_y = round(next_y * self.grid_size) / self.grid_size
                
                # Ensure we don't create paths that are too close together
                while abs(next_y - prev_y) < 0.15:
                    next_y = random.uniform(0.2, 0.8)
                    next_y = round(next_y * self.grid_size) / self.grid_size
                
                path.append((current_x, prev_y))
                path.append((current_x, next_y))
                
                current_x += x_step
                prev_y = next_y
        
        # End at right edge
        path.append((1.0, prev_y))
        
        # Reset random seed
        random.seed()
        
        return path
        
    def generate_wave_path(self, seed, screen_width, screen_height):
        """
        Generate a path with normalized coordinates based on a seed
        
        Args:
            seed: Seed value for reproducible path generation
            screen_width: Width of the game screen
            screen_height: Height of the game screen
            
        Returns:
            Two lists: 
                - base_path_points: Normalized points (0-1 range)
                - path_points: Actual screen coordinates
        """
        # Generate normalized path using the seed
        base_path = self.generate_path(screen_width, screen_height, seed)
        
        # Convert to screen coordinates
        path_points = [(p[0] * screen_width, p[1] * screen_height) for p in base_path]
        
        return base_path, path_points 