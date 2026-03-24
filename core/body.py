"""Класс Body для представления небесных тел."""

from collections import deque
from dataclasses import dataclass, field
from typing import Optional
import pygame.math as pgmath

from core.config import TRAIL_LEN, TRAIL_ADD_PERIOD, TRAIL_MAX_AGE, TRAIL_AGE_MULTIPLIER


@dataclass
class Body:
    """Небесное тело с позицией, скоростью, массой и следом орбиты."""
    
    pos: pgmath.Vector2
    vel: pgmath.Vector2
    mass: float
    radius: float
    char: str
    fixed: bool = False
    name: Optional[str] = None
    
    # След орбиты: deque кортежей (Vector2, age)
    trail: deque = field(default_factory=deque)
    trail_time_accumulator: float = 0.0  # Накопитель времени для периодического добавления точек
    
    def update_trail(self, dt: float) -> None:
        """Обновляет след орбиты, добавляя новую точку периодически."""
        if self.fixed:
            return
        
        # Обновляем возраст всех существующих точек с учётом множителя старения
        updated_trail = deque()
        for pos, age in self.trail:
            new_age = age + dt * TRAIL_AGE_MULTIPLIER
            # Удаляем точки, которые превысили максимальный возраст
            if new_age < TRAIL_MAX_AGE:
                updated_trail.append((pos, new_age))
        self.trail = updated_trail
        
        self.trail_time_accumulator += dt
        
        if self.trail_time_accumulator >= TRAIL_ADD_PERIOD:
            # Добавляем текущую позицию в след (возраст 0)
            self.trail.append((pgmath.Vector2(self.pos), 0.0))
            
            # Ограничиваем длину следа
            while len(self.trail) > TRAIL_LEN:
                self.trail.popleft()
            
            self.trail_time_accumulator = 0.0
    
    def clear_trail(self) -> None:
        """Очищает след орбиты."""
        self.trail.clear()
        self.trail_time_accumulator = 0.0
    
    def get_trail_age_normalized(self, index: int) -> float:
        """Возвращает нормализованный возраст точки следа (0.0 - 1.0)."""
        if not self.trail or index >= len(self.trail):
            return 1.0
        
        _, age = self.trail[index]
        if len(self.trail) == 0:
            return 1.0
        
        max_age = len(self.trail) * TRAIL_ADD_PERIOD
        if max_age == 0:
            return 0.0
        
        return min(age / max_age, 1.0)

