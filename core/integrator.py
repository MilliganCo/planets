"""Velocity Verlet интегратор для численного интегрирования."""

from typing import List
import pygame.math as pgmath
from core.body import Body
from core.physics import compute_accelerations


def verlet_step(bodies: List[Body], accelerations: List[pgmath.Vector2], dt: float) -> List[pgmath.Vector2]:
    """
    Выполняет один шаг Velocity Verlet интеграции.
    
    Velocity Verlet схема:
    1. pos += vel*dt + 0.5*a*dt^2
    2. Вычисляем новые ускорения (вне этой функции)
    3. vel += 0.5*(a_old + a_new)*dt
    
    Args:
        bodies: Список тел для обновления
        accelerations: Список текущих ускорений (индекс соответствует bodies)
        dt: Шаг времени
        
    Returns:
        Список новых ускорений (для следующего шага)
    """
    # Шаг 1: Обновляем позиции
    for i, body in enumerate(bodies):
        if body.fixed:
            continue
        
        accel = accelerations[i] if i < len(accelerations) else pgmath.Vector2(0, 0)
        body.pos += body.vel * dt + 0.5 * accel * dt * dt
    
    # Шаг 2: Вычисляем новые ускорения (используем функцию из physics)
    # Это делается вне функции, но для удобства можем вызвать здесь
    # В реальности новые ускорения будут вычислены после вызова этой функции
    
    # Возвращаем старые ускорения (они будут использованы на следующем шаге)
    return accelerations


def integrate(bodies: List[Body], dt: float, g: float, eps: float, substeps: int = 1) -> None:
    """
    Выполняет интегрирование движения тел с использованием Velocity Verlet.
    
    Args:
        bodies: Список тел
        dt: Шаг времени (общий)
        g: Гравитационная постоянная
        eps: Параметр смягчения
        substeps: Количество подшагов
    """
    if substeps < 1:
        substeps = 1
    
    dt_sub = dt / substeps
    
    # Вычисляем начальные ускорения
    accelerations = compute_accelerations(bodies, g, eps)
    
    for _ in range(substeps):
        # Velocity Verlet шаг
        # 1. Обновляем позиции
        for i, body in enumerate(bodies):
            if body.fixed:
                continue
            
            accel = accelerations[i] if i < len(accelerations) else pgmath.Vector2(0, 0)
            body.pos += body.vel * dt_sub + 0.5 * accel * dt_sub * dt_sub
        
        # 2. Вычисляем новые ускорения
        new_accelerations = compute_accelerations(bodies, g, eps)
        
        # 3. Обновляем скорости
        for i, body in enumerate(bodies):
            if body.fixed:
                continue
            
            old_accel = accelerations[i] if i < len(accelerations) else pgmath.Vector2(0, 0)
            new_accel = new_accelerations[i] if i < len(new_accelerations) else pgmath.Vector2(0, 0)
            body.vel += 0.5 * (old_accel + new_accel) * dt_sub
        
        # Обновляем ускорения для следующего подшага
        accelerations = new_accelerations

