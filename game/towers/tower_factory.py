from game.towers.base_tower import BaseTower
from game.towers.fire_tower import FireTower
from game.towers.water_tower import WaterTower
from game.towers.air_tower import AirTower
from game.towers.earth_tower import EarthTower
from game.towers.life_tower import LifeTower
from game.towers.darkness_tower import DarknessTower
from game.towers.light_tower import LightTower


class TowerFactory:
    """
    Factory class to create appropriate tower instances
    based on the requested tower type.
    """
    
    @staticmethod
    def create_tower(pos, tower_type):
        """
        Create a tower of the specified type at the given position.
        
        Args:
            pos: Position for the tower
            tower_type: Type of tower to create ("Fire", "Water", "Air", etc.)
            
        Returns:
            Tower instance of the appropriate type
        """
        if tower_type == "Fire":
            return FireTower(pos, tower_type)
        elif tower_type == "Water":
            return WaterTower(pos, tower_type)
        elif tower_type == "Air":
            return AirTower(pos, tower_type)
        elif tower_type == "Earth":
            return EarthTower(pos, tower_type)
        elif tower_type == "Life":
            return LifeTower(pos, tower_type)
        elif tower_type == "Darkness":
            return DarknessTower(pos, tower_type)
        elif tower_type == "Light":
            return LightTower(pos, tower_type)
        else:
            # For other tower types, use the base tower for now
            # These will be implemented as specific classes later
            return BaseTower(pos, tower_type) 