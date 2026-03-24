"""Физика гравитации и коллизий."""

from typing import List, Dict
import pygame.math as pgmath
from core.body import Body
from core.config import G, eps


def compute_accelerations(bodies: List[Body], g: float = G, softening: float = eps) -> List[pgmath.Vector2]:
    """
    Вычисляет гравитационные ускорения для всех тел.
    
    Использует смягчение (softening) для предотвращения взрывов на малых дистанциях.
    
    Args:
        bodies: Список тел
        g: Гравитационная постоянная
        softening: Параметр смягчения (eps)
        
    Returns:
        Список ускорений, где индекс соответствует индексу тела в bodies
    """
    accelerations = [pgmath.Vector2(0, 0) for _ in bodies]
    
    for i, body_i in enumerate(bodies):
        if body_i.fixed:
            continue
            
        for j, body_j in enumerate(bodies):
            if i == j:
                continue
            
            # Вектор от i к j
            r = body_j.pos - body_i.pos
            
            # Квадрат расстояния с учётом смягчения
            d2 = r.length_squared() + softening * softening
            
            # Ускорение: a = G * m_j * r / (d^2)^(3/2)
            # d^3 = (d^2)^(3/2)
            d3 = d2 ** 1.5
            
            if d3 > 0:
                # Ускорение: a = G * m_j * r / d^3
                # где r - вектор от i к j
                acceleration = r * (g * body_j.mass / d3)
                accelerations[i] += acceleration
    
    return accelerations


def check_collisions(bodies: List[Body]) -> List[tuple[Body, Body]]:
    """
    Проверяет коллизии между телами.
    
    Args:
        bodies: Список тел
        
    Returns:
        Список пар тел, которые столкнулись [(body1, body2), ...]
    """
    collisions = []
    
    for i, body_i in enumerate(bodies):
        for j, body_j in enumerate(bodies[i+1:], start=i+1):
            if body_i.fixed and body_j.fixed:
                continue
            
            # Расстояние между центрами
            distance = body_i.pos.distance_to(body_j.pos)
            
            # Радиусы пересекаются
            if distance < (body_i.radius + body_j.radius):
                collisions.append((body_i, body_j))
    
    return collisions


def merge_bodies(body1: Body, body2: Body) -> Body:
    """
    Объединяет два тела в одно (слияние).
    
    Новая масса = сумма масс.
    Скорость вычисляется по сохранению импульса.
    Позиция = центр масс.
    
    Args:
        body1: Первое тело
        body2: Второе тело
        
    Returns:
        Новое объединённое тело
    """
    # Новая масса
    total_mass = body1.mass + body2.mass
    
    # Центр масс
    if total_mass > 0:
        center_pos = (body1.pos * body1.mass + body2.pos * body2.mass) / total_mass
    else:
        center_pos = (body1.pos + body2.pos) / 2
    
    # Скорость по сохранению импульса
    if total_mass > 0:
        new_vel = (body1.vel * body1.mass + body2.vel * body2.mass) / total_mass
    else:
        new_vel = (body1.vel + body2.vel) / 2
    
    # Определяем характеристики нового тела
    # Используем большее тело как основу
    if body1.mass >= body2.mass:
        base_body = body1
    else:
        base_body = body2
    
    # Выбираем символ и радиус по массе
    from core.config import BODY_TYPE_MASSES, BODY_TYPE_RADII
    
    if total_mass >= 2000:
        char = "@"
        radius = BODY_TYPE_RADII[4]
    elif total_mass >= 150:
        char = "O"
        radius = BODY_TYPE_RADII[3]
    elif total_mass >= 20:
        char = "o"
        radius = BODY_TYPE_RADII[2]
    else:
        char = "."
        radius = BODY_TYPE_RADII[1]
    
    # Создаём новое тело
    merged = Body(
        pos=center_pos,
        vel=new_vel,
        mass=total_mass,
        radius=max(body1.radius, body2.radius, radius),
        char=char,
        fixed=body1.fixed or body2.fixed,
        name=f"{body1.name or 'Body'}+{body2.name or 'Body'}" if (body1.name or body2.name) else None
    )
    
    # Объединяем следы (берём более длинный)
    if len(body1.trail) >= len(body2.trail):
        merged.trail = body1.trail.copy()
    else:
        merged.trail = body2.trail.copy()
    
    return merged

