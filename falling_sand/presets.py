"""Пресеты сцен для falling sand симулятора."""

import random
from falling_sand.world import World
from falling_sand.materials import Material
from falling_sand.config import W, H, FIRE_LIFE_MIN, FIRE_LIFE_MAX


def preset_dune(world: World) -> None:
    """
    Пресет: Дюна с песком.
    
    Создает слой песка сверху, который будет осыпаться.
    
    Args:
        world: Мир для заполнения
    """
    world.clear()
    
    # Слой песка сверху (примерно 1/4 высоты)
    sand_height = H // 4
    
    for y in range(sand_height):
        for x in range(W):
            if random.random() < 0.7:  # Не все клетки заполняем для естественности
                world.set(x, y, Material.SAND, 0)
    
    # Несколько случайных блоков песка ниже
    for _ in range(50):
        x = random.randint(0, W - 1)
        y = random.randint(sand_height, H - 20)
        world.set(x, y, Material.SAND, 0)


def preset_lake(world: World) -> None:
    """
    Пресет: Озеро со стенками.
    
    Создает чашу со стенками и водой внутри, песок сверху.
    
    Args:
        world: Мир для заполнения
    """
    world.clear()
    
    # Стенки по бокам и снизу
    wall_thickness = 3
    
    # Нижняя стенка
    for x in range(W):
        for y in range(H - wall_thickness, H):
            world.set(x, y, Material.WALL, 0)
    
    # Боковые стенки
    for y in range(H):
        for x in range(wall_thickness):
            world.set(x, y, Material.WALL, 0)
        for x in range(W - wall_thickness, W):
            world.set(x, y, Material.WALL, 0)
    
    # Вода в чаше
    water_level = H - wall_thickness - 30
    for y in range(water_level, H - wall_thickness):
        for x in range(wall_thickness, W - wall_thickness):
            world.set(x, y, Material.WATER, 0)
    
    # Песок сверху (будет падать в воду)
    for y in range(10):
        for x in range(wall_thickness + 5, W - wall_thickness - 5):
            if random.random() < 0.5:
                world.set(x, y, Material.SAND, 0)


def preset_forest(world: World) -> None:
    """
    Пресет: Лес с деревьями.
    
    Создает деревья (WOOD) и огонь в углу для пожара.
    
    Args:
        world: Мир для заполнения
    """
    world.clear()
    
    # Слой земли снизу
    ground_level = H - 10
    for x in range(W):
        for y in range(ground_level, H):
            world.set(x, y, Material.SAND, 0)
    
    # Деревья (столбы WOOD)
    tree_count = 15
    for _ in range(tree_count):
        x = random.randint(10, W - 10)
        tree_height = random.randint(15, 30)
        
        # Ствол дерева
        for y in range(ground_level - tree_height, ground_level):
            world.set(x, y, Material.WOOD, 0)
        
        # Крона (несколько блоков дерева сверху)
        for dx in range(-2, 3):
            for dy in range(-2, 1):
                nx = x + dx
                ny = ground_level - tree_height + dy
                if world.is_valid(nx, ny) and random.random() < 0.6:
                    world.set(nx, ny, Material.WOOD, 0)
    
    # Огонь в левом нижнем углу
    fire_x = 5
    fire_y = ground_level - 1
    
    # Несколько источников огня
    for dx in range(-1, 2):
        for dy in range(-1, 1):
            nx = fire_x + dx
            ny = fire_y + dy
            if world.is_valid(nx, ny):
                fire_life = random.randint(FIRE_LIFE_MIN, FIRE_LIFE_MAX)
                world.set(nx, ny, Material.FIRE, fire_life)


def preset_rain(world: World) -> None:
    """
    Пресет: Дождь.
    
    Создает простую сцену и включает режим дождя (должен быть включен отдельно).
    
    Args:
        world: Мир для заполнения
    """
    world.clear()
    
    # Небольшая платформа снизу
    platform_y = H - 20
    for x in range(W // 4, 3 * W // 4):
        world.set(x, platform_y, Material.WALL, 0)
    
    # Несколько блоков песка на платформе
    for x in range(W // 4 + 10, 3 * W // 4 - 10):
        if random.random() < 0.3:
            world.set(x, platform_y - 1, Material.SAND, 0)
    
    # Небольшое озеро слева
    lake_x_start = 20
    lake_x_end = 60
    lake_y_start = platform_y - 15
    lake_y_end = platform_y
    
    for y in range(lake_y_start, lake_y_end):
        for x in range(lake_x_start, lake_x_end):
            world.set(x, y, Material.WATER, 0)


def preset_empty(world: World) -> None:
    """
    Пресет: Пустой мир.
    
    Просто очищает мир.
    
    Args:
        world: Мир для очистки
    """
    world.clear()

