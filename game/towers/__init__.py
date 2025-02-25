from game.towers.base_tower import BaseTower
from game.towers.fire_tower import FireTower
from game.towers.water_tower import WaterTower
from game.towers.air_tower import AirTower
from game.towers.earth_tower import EarthTower
from game.towers.life_tower import LifeTower
from game.towers.darkness_tower import DarknessTower
from game.towers.light_tower import LightTower
from game.towers.tower_factory import TowerFactory

# Expose the factory function for convenience
create_tower = TowerFactory.create_tower

# For convenience, expose TowerFactory.create_tower as a module function
def create_tower(pos, tower_type):
    """Create a tower of the specified type"""
    return TowerFactory.create_tower(pos, tower_type) 