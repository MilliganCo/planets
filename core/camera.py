"""Камера для преобразования мировых координат в координаты экрана."""

import pygame.math as pgmath
from core.config import COLS, ROWS


class Camera:
    """Камера для преобразования координат между миром и ASCII-экраном."""
    
    def __init__(self, center: pgmath.Vector2 = None, zoom: float = 0.08):
        """
        Инициализация камеры.
        
        Args:
            center: Центр камеры в мировых координатах (по умолчанию (0, 0))
            zoom: Количество клеток на мировую единицу (больше = ближе)
        """
        self.center = center if center is not None else pgmath.Vector2(0, 0)
        self.zoom = zoom
    
    def world_to_cell(self, world_pos: pgmath.Vector2) -> tuple[int, int]:
        """
        Преобразует мировые координаты в координаты ячейки ASCII-экрана.
        
        Args:
            world_pos: Позиция в мировых координатах
            
        Returns:
            Кортеж (cell_x, cell_y) - координаты ячейки на экране
        """
        # Смещение относительно центра камеры
        offset = world_pos - self.center
        
        # Масштабирование
        screen_x = offset.x * self.zoom + COLS / 2
        screen_y = offset.y * self.zoom + ROWS / 2
        
        # Округление до целых
        cell_x = int(round(screen_x))
        cell_y = int(round(screen_y))
        
        return cell_x, cell_y
    
    def cell_to_world(self, cell_x: int, cell_y: int) -> pgmath.Vector2:
        """
        Преобразует координаты ячейки экрана в мировые координаты.
        
        Args:
            cell_x: X координата ячейки
            cell_y: Y координата ячейки
            
        Returns:
            Вектор мировых координат
        """
        # Смещение от центра экрана
        offset_x = (cell_x - COLS / 2) / self.zoom
        offset_y = (cell_y - ROWS / 2) / self.zoom
        
        # Мировые координаты
        world_pos = self.center + pgmath.Vector2(offset_x, offset_y)
        
        return world_pos
    
    def is_visible(self, world_pos: pgmath.Vector2, margin: int = 5) -> bool:
        """
        Проверяет, видна ли точка на экране.
        
        Args:
            world_pos: Позиция в мировых координатах
            margin: Запас по краям экрана
            
        Returns:
            True если точка видна на экране
        """
        cell_x, cell_y = self.world_to_cell(world_pos)
        return (-margin <= cell_x < COLS + margin and 
                -margin <= cell_y < ROWS + margin)
    
    def center_on(self, world_pos: pgmath.Vector2) -> None:
        """Центрирует камеру на указанной позиции."""
        self.center = pgmath.Vector2(world_pos)

