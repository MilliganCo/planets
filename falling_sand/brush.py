"""Кисть для рисования материалов."""

import math
from falling_sand.world import World
from falling_sand.materials import Material
from falling_sand.config import BRUSH_MIN_RADIUS, BRUSH_MAX_RADIUS


class Brush:
    """Кисть для рисования материалов в мире."""
    
    def __init__(self, radius: int = 3):
        """
        Инициализация кисти.
        
        Args:
            radius: Радиус кисти
        """
        self.radius = max(BRUSH_MIN_RADIUS, min(BRUSH_MAX_RADIUS, radius))
        self.last_x = None
        self.last_y = None
    
    def set_radius(self, radius: int) -> None:
        """
        Устанавливает радиус кисти.
        
        Args:
            radius: Новый радиус
        """
        self.radius = max(BRUSH_MIN_RADIUS, min(BRUSH_MAX_RADIUS, radius))
    
    def draw_circle(self, world: World, x: int, y: int, mat: Material, life: int = 0) -> None:
        """
        Рисует круг материала в указанной позиции.
        
        Args:
            world: Мир для рисования
            x, y: Центр круга
            mat: Тип материала
            life: Таймер жизни (для FIRE/SMOKE)
        """
        radius_sq = self.radius * self.radius
        
        for dy in range(-self.radius, self.radius + 1):
            for dx in range(-self.radius, self.radius + 1):
                if dx * dx + dy * dy <= radius_sq:
                    nx, ny = x + dx, y + dy
                    if world.is_valid(nx, ny):
                        world.set(nx, ny, mat, life)
    
    def erase_circle(self, world: World, x: int, y: int) -> None:
        """
        Стирает круг (устанавливает EMPTY).
        
        Args:
            world: Мир для стирания
            x, y: Центр круга
        """
        self.draw_circle(world, x, y, Material.EMPTY, 0)
    
    def draw_line(self, world: World, x1: int, y1: int, x2: int, y2: int, mat: Material, life: int = 0) -> None:
        """
        Рисует линию материала между двумя точками.
        
        Args:
            world: Мир для рисования
            x1, y1: Начальная точка
            x2, y2: Конечная точка
            mat: Тип материала
            life: Таймер жизни
        """
        dx = x2 - x1
        dy = y2 - y1
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance == 0:
            self.draw_circle(world, x1, y1, mat, life)
            return
        
        steps = int(distance) + 1
        
        for i in range(steps + 1):
            t = i / steps if steps > 0 else 0
            x = int(x1 + dx * t)
            y = int(y1 + dy * t)
            self.draw_circle(world, x, y, mat, life)
    
    def update_line(self, world: World, x: int, y: int, mat: Material, life: int = 0) -> None:
        """
        Обновляет линию от последней точки до текущей.
        
        Args:
            world: Мир для рисования
            x, y: Текущая позиция мыши
            mat: Тип материала
            life: Таймер жизни
        """
        if self.last_x is not None and self.last_y is not None:
            self.draw_line(world, self.last_x, self.last_y, x, y, mat, life)
        
        self.last_x = x
        self.last_y = y
    
    def reset_line(self) -> None:
        """Сбрасывает последнюю точку линии."""
        self.last_x = None
        self.last_y = None

