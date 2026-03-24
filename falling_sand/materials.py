"""Константы материалов и их свойства."""

from enum import IntEnum
import pygame


class Material(IntEnum):
    """Типы материалов в симуляции."""
    EMPTY = 0
    WALL = 1
    SAND = 2
    WATER = 3
    WOOD = 4
    FIRE = 5
    SMOKE = 6
    OIL = 7
    STEAM = 8
    EMBER = 9
    LAVA = 10
    ICE = 11
    ACID = 12
    GAS = 13
    STONE = 14
    SNOW = 15
    SOIL = 16
    PLANT = 17
    ASH = 18
    SALT = 19
    CEMENT = 20
    METAL = 21
    MOLTEN_METAL = 22


# Цвета материалов (RGB)
MATERIAL_COLORS = {
    Material.EMPTY: (0, 0, 0),          # Черный
    Material.WALL: (100, 100, 100),    # Серый
    Material.SAND: (194, 178, 128),    # Желтовато-бежевый
    Material.WATER: (64, 164, 223),     # Синий
    Material.WOOD: (101, 67, 33),       # Коричневый
    Material.FIRE: (255, 100, 0),       # Оранжево-красный
    Material.SMOKE: (80, 80, 80),       # Темно-серый
    Material.OIL: (40, 40, 40),        # Темно-коричневый/черный
    Material.STEAM: (220, 220, 255),   # Светло-голубой/белый
    Material.EMBER: (150, 50, 0),       # Темно-красный
    Material.LAVA: (255, 50, 0),        # Ярко-красный/оранжевый
    Material.ICE: (200, 240, 255),      # Светло-голубой
    Material.ACID: (100, 255, 100),     # Ярко-зеленый
    Material.GAS: (150, 150, 200),      # Светло-фиолетовый
    Material.STONE: (120, 120, 120),    # Серый камень
    Material.SNOW: (255, 255, 255),     # Белый снег
    Material.SOIL: (139, 90, 43),       # Коричневая почва
    Material.PLANT: (34, 139, 34),      # Зеленое растение
    Material.ASH: (100, 100, 100),      # Серый пепел
    Material.SALT: (240, 240, 240),     # Белая соль
    Material.CEMENT: (200, 200, 200),   # Серый цемент
    Material.METAL: (169, 169, 169),    # Серебристый металл
    Material.MOLTEN_METAL: (255, 200, 100),  # Оранжевый расплавленный металл
}

# Символы для ASCII отображения (если понадобится)
MATERIAL_SYMBOLS = {
    Material.EMPTY: ' ',
    Material.WALL: '█',
    Material.SAND: ':',
    Material.WATER: '~',
    Material.WOOD: '#',
    Material.FIRE: '*',
    Material.SMOKE: '.',
    Material.OIL: 'o',
    Material.STEAM: '"',
    Material.EMBER: 'c',
    Material.LAVA: 'L',
    Material.ICE: 'I',
    Material.ACID: 'A',
    Material.GAS: 'G',
    Material.STONE: 'S',
    Material.SNOW: '*',
    Material.SOIL: 's',
    Material.PLANT: '&',
    Material.ASH: 'a',
    Material.SALT: 'l',
    Material.CEMENT: 'c',
    Material.METAL: 'M',
    Material.MOLTEN_METAL: 'm',
}

# Свойства материалов
MATERIAL_PROPERTIES = {
    Material.EMPTY: {
        'density': 0,
        'flammable': False,
        'movable': True,
        'has_life': False,
    },
    Material.WALL: {
        'density': 999,
        'flammable': False,
        'movable': False,
        'has_life': False,
    },
    Material.SAND: {
        'density': 2,
        'flammable': False,
        'movable': True,
        'has_life': False,
    },
    Material.WATER: {
        'density': 1,
        'flammable': False,
        'movable': True,
        'has_life': False,
    },
    Material.WOOD: {
        'density': 1,
        'flammable': True,
        'movable': False,
        'has_life': False,
    },
    Material.FIRE: {
        'density': 0,
        'flammable': False,
        'movable': True,
        'has_life': True,
    },
    Material.SMOKE: {
        'density': 0,
        'flammable': False,
        'movable': True,
        'has_life': True,
    },
    Material.OIL: {
        'density': 0.5,
        'flammable': True,
        'movable': True,
        'has_life': False,
    },
    Material.STEAM: {
        'density': 0,
        'flammable': False,
        'movable': True,
        'has_life': True,
    },
    Material.EMBER: {
        'density': 1.5,
        'flammable': False,
        'movable': True,
        'has_life': True,
    },
    Material.LAVA: {
        'density': 2.5,
        'flammable': False,
        'movable': True,
        'has_life': True,
    },
    Material.ICE: {
        'density': 0.9,
        'flammable': False,
        'movable': False,
        'has_life': False,
    },
    Material.ACID: {
        'density': 1.2,
        'flammable': False,
        'movable': True,
        'has_life': False,
    },
    Material.GAS: {
        'density': 0,
        'flammable': True,
        'movable': True,
        'has_life': True,
    },
    Material.STONE: {
        'density': 999,
        'flammable': False,
        'movable': False,
        'has_life': False,
    },
    Material.SNOW: {
        'density': 0.3,
        'flammable': False,
        'movable': True,
        'has_life': False,
    },
    Material.SOIL: {
        'density': 1.5,
        'flammable': False,
        'movable': True,
        'has_life': False,
    },
    Material.PLANT: {
        'density': 0.8,
        'flammable': True,
        'movable': False,
        'has_life': False,
    },
    Material.ASH: {
        'density': 0.1,
        'flammable': False,
        'movable': True,
        'has_life': True,
    },
    Material.SALT: {
        'density': 1.8,
        'movable': True,
        'flammable': False,
        'has_life': False,
    },
    Material.CEMENT: {
        'density': 2.0,
        'movable': True,
        'flammable': False,
        'has_life': False,
    },
    Material.METAL: {
        'density': 999,
        'movable': False,
        'flammable': False,
        'has_life': False,
    },
    Material.MOLTEN_METAL: {
        'density': 3.0,
        'movable': True,
        'flammable': False,
        'has_life': True,
    },
}


def get_color(mat: Material, variation: float = 0.0) -> tuple:
    """
    Получает цвет материала с возможной вариацией.
    
    Args:
        mat: Тип материала
        variation: Вариация цвета (0.0 - 1.0) для визуального разнообразия
        
    Returns:
        RGB кортеж цвета
    """
    base_color = MATERIAL_COLORS.get(mat, (0, 0, 0))
    
    if variation > 0 and mat == Material.FIRE:
        # Мерцание огня
        import random
        r, g, b = base_color
        r = min(255, int(r + random.randint(-30, 30) * variation))
        g = min(255, int(g + random.randint(-20, 20) * variation))
        return (r, g, b)
    
    return base_color


def get_symbol(mat: Material) -> str:
    """Получает символ для ASCII отображения."""
    return MATERIAL_SYMBOLS.get(mat, '?')


def is_flammable(mat: Material) -> bool:
    """Проверяет, является ли материал горючим."""
    return MATERIAL_PROPERTIES.get(mat, {}).get('flammable', False)


def is_movable(mat: Material) -> bool:
    """Проверяет, может ли материал двигаться."""
    return MATERIAL_PROPERTIES.get(mat, {}).get('movable', True)


def has_life(mat: Material) -> bool:
    """Проверяет, имеет ли материал таймер жизни."""
    return MATERIAL_PROPERTIES.get(mat, {}).get('has_life', False)


def get_density(mat: Material) -> int:
    """Получает плотность материала."""
    return MATERIAL_PROPERTIES.get(mat, {}).get('density', 0)

