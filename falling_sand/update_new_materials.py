"""Логика обновления новых материалов."""

import random
from falling_sand.world import World
from falling_sand.materials import Material, is_flammable
from falling_sand.config import (
    P_IGNITE, FIRE_LIFE_MIN, FIRE_LIFE_MAX,
    STEAM_LIFE_MIN, STEAM_LIFE_MAX,
    LAVA_LIFE_MIN, LAVA_LIFE_MAX,
    EMBER_LIFE_MIN, EMBER_LIFE_MAX,
    ICE_MELT_CHANCE,
)


def update_oil(world: World, x: int, y: int, gravity: tuple) -> None:
    """
    Обновляет клетку с маслом.
    
    Масло плавает на воде, течет как жидкость, легко загорается.
    
    Args:
        world: Мир
        x, y: Координаты клетки
        gravity: Направление гравитации
    """
    if world.is_updated(x, y):
        return
    
    gx, gy = gravity
    nx, ny = x + gx, y + gy
    
    # Проверка падения вниз
    if world.is_valid(nx, ny):
        below_mat = world.get(nx, ny)
        
        if below_mat == Material.EMPTY:
            world.swap(x, y, nx, ny)
            world.mark_updated(nx, ny)
            world.mark_updated(x, y)
            return
        elif below_mat == Material.WATER:
            # Масло плавает на воде (меняется местами)
            world.swap(x, y, nx, ny)
            world.mark_updated(nx, ny)
            world.mark_updated(x, y)
            return
    
    # Течение как жидкость (аналогично воде)
    directions = [(-1, 1), (1, 1)] if gy > 0 else [(-1, -1), (1, -1)]
    random.shuffle(directions)
    
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if world.is_valid(nx, ny):
            diag_mat = world.get(nx, ny)
            if diag_mat == Material.EMPTY or diag_mat == Material.WATER:
                world.swap(x, y, nx, ny)
                world.mark_updated(nx, ny)
                world.mark_updated(x, y)
                return
    
    # Течение вбок
    side_dirs = [(-1, 0), (1, 0)]
    random.shuffle(side_dirs)
    
    for dx, dy in side_dirs:
        flow_dist = random.randint(1, 3)
        for dist in range(1, flow_dist + 1):
            nx, ny = x + dx * dist, y
            if world.is_valid(nx, ny):
                side_mat = world.get(nx, ny)
                if side_mat == Material.EMPTY or side_mat == Material.WATER:
                    world.swap(x, y, nx, ny)
                    world.mark_updated(nx, ny)
                    world.mark_updated(x, y)
                    return
                elif side_mat != Material.OIL:
                    break
    
    # Проверка зажигания от соседнего огня (масло загорается легче)
    neighbors = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
    random.shuffle(neighbors)
    
    for nx, ny in neighbors:
        if world.is_valid(nx, ny):
            neighbor_mat = world.get(nx, ny)
            if neighbor_mat == Material.FIRE:
                # Масло загорается с большей вероятностью
                if random.random() < P_IGNITE * 2.0:  # В 2 раза выше вероятность
                    fire_life = random.randint(FIRE_LIFE_MIN, FIRE_LIFE_MAX)
                    world.set(x, y, Material.FIRE, fire_life)
                    world.mark_updated(x, y)
                    return
    
    world.mark_updated(x, y)


def update_steam(world: World, x: int, y: int, wind: tuple) -> None:
    """
    Обновляет клетку с паром.
    
    Пар поднимается вверх, конденсируется в воду со временем.
    
    Args:
        world: Мир
        x, y: Координаты клетки
        wind: Направление ветра
    """
    if world.is_updated(x, y):
        return
    
    # Уменьшаем таймер жизни
    life = world.get_life(x, y)
    if life > 0:
        life -= 1
        world.set(x, y, Material.STEAM, life)
    else:
        # Пар конденсируется в воду
        world.set(x, y, Material.WATER, 0)
        world.mark_updated(x, y)
        return
    
    wx, wy = wind
    
    # Подъем вверх
    nx, ny = x + wx, y - 1 + wy
    
    if world.is_valid(nx, ny):
        above_mat = world.get(nx, ny)
        if above_mat == Material.EMPTY:
            world.swap(x, y, nx, ny)
            world.mark_updated(nx, ny)
            world.mark_updated(x, y)
            return
    
    # Подъем по диагонали
    directions = [(-1, -1), (1, -1)]
    random.shuffle(directions)
    
    for dx, dy in directions:
        nx, ny = x + dx + wx, y + dy + wy
        if world.is_valid(nx, ny):
            diag_mat = world.get(nx, ny)
            if diag_mat == Material.EMPTY:
                world.swap(x, y, nx, ny)
                world.mark_updated(nx, ny)
                world.mark_updated(x, y)
                return
    
    # Рассеивание вбок
    side_dirs = [(-1, 0), (1, 0)]
    if wx != 0:
        if wx < 0:
            side_dirs = [(-1, 0), (1, 0)]
        else:
            side_dirs = [(1, 0), (-1, 0)]
    
    random.shuffle(side_dirs)
    
    for dx, dy in side_dirs:
        nx, ny = x + dx + wx, y + dy + wy
        if world.is_valid(nx, ny):
            side_mat = world.get(nx, ny)
            if side_mat == Material.EMPTY:
                world.swap(x, y, nx, ny)
                world.mark_updated(nx, ny)
                world.mark_updated(x, y)
                return
    
    world.mark_updated(x, y)


def update_ice(world: World, x: int, y: int) -> None:
    """
    Обновляет клетку со льдом.
    
    Лед тает от соседнего огня или лавы, превращаясь в воду.
    
    Args:
        world: Мир
        x, y: Координаты клетки
    """
    if world.is_updated(x, y):
        return
    
    # Проверка соседей на огонь/лаву
    neighbors = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
    
    for nx, ny in neighbors:
        if world.is_valid(nx, ny):
            neighbor_mat = world.get(nx, ny)
            if neighbor_mat == Material.FIRE or neighbor_mat == Material.LAVA:
                # Лед тает от огня/лавы
                if random.random() < ICE_MELT_CHANCE:
                    world.set(x, y, Material.WATER, 0)
                    world.mark_updated(x, y)
                    return
    
    world.mark_updated(x, y)


def update_stone(world: World, x: int, y: int, gravity: tuple) -> None:
    """
    Обновляет клетку с камнем.
    
    Камень падает вниз, тяжелее песка.
    
    Args:
        world: Мир
        x, y: Координаты клетки
        gravity: Направление гравитации
    """
    if world.is_updated(x, y):
        return
    
    gx, gy = gravity
    nx, ny = x + gx, y + gy
    
    # Проверка падения вниз
    if world.is_valid(nx, ny):
        below_mat = world.get(nx, ny)
        
        if below_mat == Material.EMPTY:
            world.swap(x, y, nx, ny)
            world.mark_updated(nx, ny)
            world.mark_updated(x, y)
            return
        elif below_mat == Material.WATER or below_mat == Material.SAND:
            # Камень тонет в воде и вытесняет песок
            world.swap(x, y, nx, ny)
            world.mark_updated(nx, ny)
            world.mark_updated(x, y)
            return
    
    # Попытка скатиться диагонально
    directions = [(-1, 1), (1, 1)] if gy > 0 else [(-1, -1), (1, -1)]
    random.shuffle(directions)
    
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if world.is_valid(nx, ny):
            diag_mat = world.get(nx, ny)
            if diag_mat == Material.EMPTY or diag_mat == Material.WATER or diag_mat == Material.SAND:
                world.swap(x, y, nx, ny)
                world.mark_updated(nx, ny)
                world.mark_updated(x, y)
                return
    
    world.mark_updated(x, y)


def update_lava(world: World, x: int, y: int, gravity: tuple) -> None:
    """
    Обновляет клетку с лавой.
    
    Лава течет как жидкость, застывает в камень, зажигает дерево.
    
    Args:
        world: Мир
        x, y: Координаты клетки
        gravity: Направление гравитации
    """
    if world.is_updated(x, y):
        return
    
    # Уменьшаем таймер жизни (лава застывает)
    life = world.get_life(x, y)
    if life > 0:
        life -= 1
        world.set(x, y, Material.LAVA, life)
    else:
        # Лава застывает в камень
        world.set(x, y, Material.STONE, 0)
        world.mark_updated(x, y)
        return
    
    gx, gy = gravity
    nx, ny = x + gx, y + gy
    
    # Проверка падения вниз
    if world.is_valid(nx, ny):
        below_mat = world.get(nx, ny)
        
        if below_mat == Material.EMPTY:
            world.swap(x, y, nx, ny)
            world.mark_updated(nx, ny)
            world.mark_updated(x, y)
            return
        elif below_mat == Material.WATER:
            # Лава + вода = пар
            world.set(x, y, Material.STEAM, random.randint(STEAM_LIFE_MIN, STEAM_LIFE_MAX))
            world.mark_updated(x, y)
            return
    
    # Течение как жидкость
    directions = [(-1, 1), (1, 1)] if gy > 0 else [(-1, -1), (1, -1)]
    random.shuffle(directions)
    
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if world.is_valid(nx, ny):
            diag_mat = world.get(nx, ny)
            if diag_mat == Material.EMPTY:
                world.swap(x, y, nx, ny)
                world.mark_updated(nx, ny)
                world.mark_updated(x, y)
                return
    
    # Течение вбок
    side_dirs = [(-1, 0), (1, 0)]
    random.shuffle(side_dirs)
    
    for dx, dy in side_dirs:
        flow_dist = random.randint(1, 2)
        for dist in range(1, flow_dist + 1):
            nx, ny = x + dx * dist, y
            if world.is_valid(nx, ny):
                side_mat = world.get(nx, ny)
                if side_mat == Material.EMPTY:
                    world.swap(x, y, nx, ny)
                    world.mark_updated(nx, ny)
                    world.mark_updated(x, y)
                    return
                elif side_mat != Material.LAVA:
                    break
    
    # Зажигание дерева
    neighbors = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
    random.shuffle(neighbors)
    
    for nx, ny in neighbors:
        if world.is_valid(nx, ny) and not world.is_updated(nx, ny):
            neighbor_mat = world.get(nx, ny)
            if is_flammable(neighbor_mat):
                if random.random() < P_IGNITE * 1.5:
                    fire_life = random.randint(FIRE_LIFE_MIN, FIRE_LIFE_MAX)
                    world.set(nx, ny, Material.FIRE, fire_life)
                    world.mark_updated(nx, ny)
    
    world.mark_updated(x, y)


def update_ember(world: World, x: int, y: int, gravity: tuple) -> None:
    """
    Обновляет клетку с угольками.
    
    Угольки падают, могут разжечь огонь при контакте с горючими материалами.
    
    Args:
        world: Мир
        x, y: Координаты клетки
        gravity: Направление гравитации
    """
    if world.is_updated(x, y):
        return
    
    # Уменьшаем таймер жизни
    life = world.get_life(x, y)
    if life > 0:
        life -= 1
        world.set(x, y, Material.EMBER, life)
    else:
        # Угольки остывают и превращаются в камень
        world.set(x, y, Material.STONE, 0)
        world.mark_updated(x, y)
        return
    
    gx, gy = gravity
    nx, ny = x + gx, y + gy
    
    # Проверка падения вниз
    if world.is_valid(nx, ny):
        below_mat = world.get(nx, ny)
        
        if below_mat == Material.EMPTY:
            world.swap(x, y, nx, ny)
            world.mark_updated(nx, ny)
            world.mark_updated(x, y)
            return
        elif below_mat == Material.WATER:
            # Вода гасит угольки быстрее
            world.set(x, y, Material.STONE, 0)
            world.mark_updated(x, y)
            return
    
    # Попытка скатиться диагонально
    directions = [(-1, 1), (1, 1)] if gy > 0 else [(-1, -1), (1, -1)]
    random.shuffle(directions)
    
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if world.is_valid(nx, ny):
            diag_mat = world.get(nx, ny)
            if diag_mat == Material.EMPTY:
                world.swap(x, y, nx, ny)
                world.mark_updated(nx, ny)
                world.mark_updated(x, y)
                return
    
    # Зажигание горючих материалов при контакте
    neighbors = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
    random.shuffle(neighbors)
    
    for nx, ny in neighbors:
        if world.is_valid(nx, ny) and not world.is_updated(nx, ny):
            neighbor_mat = world.get(nx, ny)
            if is_flammable(neighbor_mat):
                # Угольки могут разжечь огонь
                if random.random() < P_IGNITE * 0.5:  # Меньшая вероятность, чем от огня
                    fire_life = random.randint(FIRE_LIFE_MIN, FIRE_LIFE_MAX)
                    world.set(nx, ny, Material.FIRE, fire_life)
                    world.mark_updated(nx, ny)
    
    world.mark_updated(x, y)

