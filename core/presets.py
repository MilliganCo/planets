"""Пресеты стартовых сцен для симулятора."""

import pygame.math as pgmath
import math
from typing import List
from core.body import Body
from core.config import BODY_TYPE_MASSES, BODY_TYPE_RADII, G


def build_preset_1() -> List[Body]:
    """
    Пресет 1: Одна звезда + 5 планет (круговые орбиты).
    
    Returns:
        Список тел для симуляции
    """
    bodies = []
    
    # Центральная звезда
    star = Body(
        pos=pgmath.Vector2(0, 0),
        vel=pgmath.Vector2(0, 0),
        mass=BODY_TYPE_MASSES[4]["default"],
        radius=BODY_TYPE_RADII[4],
        char=BODY_TYPE_MASSES[4]["char"],
        fixed=True,
        name="Star"
    )
    bodies.append(star)
    
    # 5 планет на разных орбитах
    num_planets = 5
    for i in range(num_planets):
        angle = (2 * math.pi * i) / num_planets
        radius = 50 + i * 30  # Разные радиусы орбит
        
        # Позиция планеты
        pos_x = radius * math.cos(angle)
        pos_y = radius * math.sin(angle)
        pos = pgmath.Vector2(pos_x, pos_y)
        
        # Круговая скорость: v = sqrt(G * M / r)
        v_magnitude = math.sqrt(G * star.mass / radius)
        
        # Направление перпендикулярно радиусу (по часовой стрелке)
        r_vec = pos - star.pos
        if r_vec.length() > 0:
            r_normalized = r_vec.normalize()
            tangent = pgmath.Vector2(-r_normalized.y, r_normalized.x)
            vel = tangent * v_magnitude
        else:
            vel = pgmath.Vector2(0, v_magnitude)
        
        planet = Body(
            pos=pos,
            vel=vel,
            mass=BODY_TYPE_MASSES[2]["default"],
            radius=BODY_TYPE_RADII[2],
            char=BODY_TYPE_MASSES[2]["char"],
            name=f"Planet {i+1}"
        )
        bodies.append(planet)
    
    return bodies


def build_preset_2() -> List[Body]:
    """
    Пресет 2: Бинарные звёзды + планеты вокруг барицентра.
    
    Returns:
        Список тел для симуляции
    """
    bodies = []
    
    # Две звезды в бинарной системе
    star1_mass = BODY_TYPE_MASSES[4]["default"]
    star2_mass = BODY_TYPE_MASSES[4]["default"] * 0.8
    
    # Расстояние между звёздами
    separation = 80.0
    
    # Барицентр в начале координат
    star1_pos = pgmath.Vector2(-separation * star2_mass / (star1_mass + star2_mass), 0)
    star2_pos = pgmath.Vector2(separation * star1_mass / (star1_mass + star2_mass), 0)
    
    # Круговая скорость для бинарной системы
    total_mass = star1_mass + star2_mass
    r1 = star1_pos.length()
    r2 = star2_pos.length()
    
    # Орбитальная скорость
    v1_magnitude = math.sqrt(G * star2_mass * separation / (total_mass * r1))
    v2_magnitude = math.sqrt(G * star1_mass * separation / (total_mass * r2))
    
    star1_vel = pgmath.Vector2(0, v1_magnitude)
    star2_vel = pgmath.Vector2(0, -v2_magnitude)
    
    star1 = Body(
        pos=star1_pos,
        vel=star1_vel,
        mass=star1_mass,
        radius=BODY_TYPE_RADII[4],
        char=BODY_TYPE_MASSES[4]["char"],
        name="Star 1"
    )
    
    star2 = Body(
        pos=star2_pos,
        vel=star2_vel,
        mass=star2_mass,
        radius=BODY_TYPE_RADII[4],
        char=BODY_TYPE_MASSES[4]["char"],
        name="Star 2"
    )
    
    bodies.extend([star1, star2])
    
    # Планеты вокруг барицентра
    num_planets = 3
    for i in range(num_planets):
        angle = (2 * math.pi * i) / num_planets
        radius = 150 + i * 40
        
        pos_x = radius * math.cos(angle)
        pos_y = radius * math.sin(angle)
        pos = pgmath.Vector2(pos_x, pos_y)
        
        # Скорость относительно барицентра
        v_magnitude = math.sqrt(G * total_mass / radius)
        if pos.length() > 0:
            r_normalized = pos.normalize()
            tangent = pgmath.Vector2(-r_normalized.y, r_normalized.x)
            vel = tangent * v_magnitude
        else:
            vel = pgmath.Vector2(0, v_magnitude)
        
        planet = Body(
            pos=pos,
            vel=vel,
            mass=BODY_TYPE_MASSES[2]["default"],
            radius=BODY_TYPE_RADII[2],
            char=BODY_TYPE_MASSES[2]["char"],
            name=f"Planet {i+1}"
        )
        bodies.append(planet)
    
    return bodies


def build_preset_3() -> List[Body]:
    """
    Пресет 3: Гравитационная праща (массивная планета + поток астероидов).
    
    Returns:
        Список тел для симуляции
    """
    bodies = []
    
    # Массивная планета (гигант)
    giant = Body(
        pos=pgmath.Vector2(0, 0),
        vel=pgmath.Vector2(0, 0),
        mass=BODY_TYPE_MASSES[3]["default"],
        radius=BODY_TYPE_RADII[3],
        char=BODY_TYPE_MASSES[3]["char"],
        fixed=True,
        name="Giant"
    )
    bodies.append(giant)
    
    # Поток астероидов, пролетающих мимо
    num_asteroids = 8
    for i in range(num_asteroids):
        # Позиция слева от гиганта
        start_x = -200 - i * 30
        start_y = -50 + i * 15
        
        pos = pgmath.Vector2(start_x, start_y)
        
        # Начальная скорость направлена вправо и немного вверх
        vel = pgmath.Vector2(15 + i * 2, 2 + i * 0.5)
        
        asteroid = Body(
            pos=pos,
            vel=vel,
            mass=BODY_TYPE_MASSES[1]["default"],
            radius=BODY_TYPE_RADII[1],
            char=BODY_TYPE_MASSES[1]["char"],
            name=f"Asteroid {i+1}"
        )
        bodies.append(asteroid)
    
    return bodies


def build_preset_4() -> List[Body]:
    """
    Пресет 4: Кольца (много мелких тел в диске вокруг гиганта).
    
    Returns:
        Список тел для симуляции
    """
    bodies = []
    
    # Центральный гигант
    giant = Body(
        pos=pgmath.Vector2(0, 0),
        vel=pgmath.Vector2(0, 0),
        mass=BODY_TYPE_MASSES[3]["default"],
        radius=BODY_TYPE_RADII[3],
        char=BODY_TYPE_MASSES[3]["char"],
        fixed=True,
        name="Giant"
    )
    bodies.append(giant)
    
    # Кольца мелких тел
    num_rings = 3
    particles_per_ring = 12
    
    for ring in range(num_rings):
        radius = 60 + ring * 25
        
        for i in range(particles_per_ring):
            angle = (2 * math.pi * i) / particles_per_ring + ring * 0.1  # Небольшой сдвиг для красоты
            
            pos_x = radius * math.cos(angle)
            pos_y = radius * math.sin(angle)
            pos = pgmath.Vector2(pos_x, pos_y)
            
            # Круговая скорость
            v_magnitude = math.sqrt(G * giant.mass / radius)
            if pos.length() > 0:
                r_normalized = pos.normalize()
                tangent = pgmath.Vector2(-r_normalized.y, r_normalized.x)
                vel = tangent * v_magnitude
            else:
                vel = pgmath.Vector2(0, v_magnitude)
            
            particle = Body(
                pos=pos,
                vel=vel,
                mass=BODY_TYPE_MASSES[1]["default"] * 0.5,  # Меньшая масса для частиц
                radius=BODY_TYPE_RADII[1],
                char=BODY_TYPE_MASSES[1]["char"],
                name=f"Particle {ring}-{i}"
            )
            bodies.append(particle)
    
    return bodies


def build_preset_5() -> List[Body]:
    """
    Пресет 5: Хаос (3 тела сопоставимых масс - тройная система).
    
    Returns:
        Список тел для симуляции
    """
    bodies = []
    
    # Три тела сопоставимых масс в треугольной конфигурации
    mass = BODY_TYPE_MASSES[3]["default"] * 0.6
    
    # Вершины равностороннего треугольника
    side_length = 100.0
    height = side_length * math.sqrt(3) / 2
    
    pos1 = pgmath.Vector2(0, -height * 2/3)
    pos2 = pgmath.Vector2(-side_length / 2, height / 3)
    pos3 = pgmath.Vector2(side_length / 2, height / 3)
    
    # Центр масс
    center = (pos1 + pos2 + pos3) / 3
    
    # Смещаем так, чтобы центр масс был в начале координат
    pos1 -= center
    pos2 -= center
    pos3 -= center
    
    # Начальные скорости для создания орбитального движения
    # Упрощённая версия - каждое тело движется перпендикулярно радиусу
    r1_normalized = pos1.normalize() if pos1.length() > 0 else pgmath.Vector2(1, 0)
    r2_normalized = pos2.normalize() if pos2.length() > 0 else pgmath.Vector2(1, 0)
    r3_normalized = pos3.normalize() if pos3.length() > 0 else pgmath.Vector2(1, 0)
    
    # Скорости для создания вращения
    v_magnitude = 8.0
    vel1 = pgmath.Vector2(-r1_normalized.y, r1_normalized.x) * v_magnitude
    vel2 = pgmath.Vector2(-r2_normalized.y, r2_normalized.x) * v_magnitude
    vel3 = pgmath.Vector2(-r3_normalized.y, r3_normalized.x) * v_magnitude
    
    body1 = Body(
        pos=pos1,
        vel=vel1,
        mass=mass,
        radius=BODY_TYPE_RADII[3],
        char=BODY_TYPE_MASSES[3]["char"],
        name="Body 1"
    )
    
    body2 = Body(
        pos=pos2,
        vel=vel2,
        mass=mass,
        radius=BODY_TYPE_RADII[3],
        char=BODY_TYPE_MASSES[3]["char"],
        name="Body 2"
    )
    
    body3 = Body(
        pos=pos3,
        vel=vel3,
        mass=mass,
        radius=BODY_TYPE_RADII[3],
        char=BODY_TYPE_MASSES[3]["char"],
        name="Body 3"
    )
    
    bodies.extend([body1, body2, body3])
    
    return bodies

