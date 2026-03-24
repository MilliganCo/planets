"""Логика обновления материалов в симуляции."""

import random
from falling_sand.world import World
from falling_sand.materials import Material, get_density
from falling_sand.config import (
    WATER_FLOW_DISTANCE,
    P_OIL_IGNITE, P_EMBER_IGNITE, P_LAVA_IGNITE,
    P_ICE_MELT, P_ACID_DISSOLVE, P_GAS_EXPLODE, P_STEAM_CONDENSE,
    STEAM_LIFE_MIN, STEAM_LIFE_MAX,
    EMBER_LIFE_MIN, EMBER_LIFE_MAX,
    LAVA_LIFE_MIN, LAVA_LIFE_MAX,
    GAS_LIFE_MIN, GAS_LIFE_MAX,
    ASH_LIFE_MIN, ASH_LIFE_MAX,
    MOLTEN_METAL_LIFE_MIN, MOLTEN_METAL_LIFE_MAX,
    P_SNOW_MELT, P_ASH_TO_SOIL, P_PLANT_GROW,
    P_SALT_DISSOLVE, P_CEMENT_HARDEN, P_METAL_MELT,
)


def tick(world: World, gravity: tuple = (0, 1), wind: tuple = (0, 0)) -> None:
    """
    Выполняет один тик симуляции (высокооптимизированная версия).
    
    Оптимизации:
    - Обновляет только активные клетки и их соседей
    - Пропускает пустые клетки
    - Использует прямые обращения к массивам
    
    Args:
        world: Мир для обновления
        gravity: Направление гравитации (dx, dy)
        wind: Направление ветра (dx, dy) для дыма
    """
    world.start_tick()
    
    # Оптимизация: используем прямые обращения к массивам
    width = world.width
    height = world.height
    mat_array = world.mat
    EMPTY_VAL = Material.EMPTY.value
    
    # Оптимизация по принципам Noita: обновляем только активные НЕ-спящие клетки
    # "Спящие" частицы не обновляются до тех пор, пока их не потревожат
    cells_to_update = world.active_cells - world.sleeping_cells
    
    # Разделяем на падающие и поднимающиеся материалы
    falling_cells = []
    rising_cells = []
    
    for x, y in cells_to_update:
        if not world.is_valid(x, y):
            continue
        idx = x + y * width
        mat_val = mat_array[idx]
        
        if mat_val == EMPTY_VAL:
            continue
        
        # Падающие материалы
        if mat_val in (Material.SAND.value, Material.WATER.value, Material.OIL.value,
                       Material.EMBER.value, Material.LAVA.value, Material.ACID.value,
                       Material.SNOW.value, Material.SOIL.value, Material.SALT.value,
                       Material.CEMENT.value, Material.MOLTEN_METAL.value):
            falling_cells.append((x, y, mat_val))
        # Поднимающиеся материалы
        elif mat_val in (Material.FIRE.value, Material.SMOKE.value, Material.STEAM.value, 
                         Material.GAS.value, Material.ASH.value):
            rising_cells.append((x, y, mat_val))
        # Статичные материалы, которые могут взаимодействовать
        elif mat_val in (Material.ICE.value, Material.STONE.value, Material.PLANT.value, Material.METAL.value):
            falling_cells.append((x, y, mat_val))
    
    # Сортируем падающие снизу вверх
    falling_cells.sort(key=lambda c: -c[1])
    
    # Сортируем поднимающиеся сверху вниз
    rising_cells.sort(key=lambda c: c[1])
    
    # Обновляем падающие материалы
    for x, y, mat_val in falling_cells:
        if mat_val == Material.SAND.value:
            update_sand(world, x, y, gravity)
        elif mat_val == Material.WATER.value:
            update_water(world, x, y, gravity)
        elif mat_val == Material.OIL.value:
            update_oil(world, x, y, gravity)
        elif mat_val == Material.EMBER.value:
            update_ember(world, x, y, gravity)
        elif mat_val == Material.LAVA.value:
            update_lava(world, x, y, gravity)
        elif mat_val == Material.ACID.value:
            update_acid(world, x, y, gravity)
        elif mat_val == Material.ICE.value:
            update_ice(world, x, y)
        elif mat_val == Material.SNOW.value:
            update_snow(world, x, y, gravity)
        elif mat_val == Material.SOIL.value:
            update_soil(world, x, y, gravity)
        elif mat_val == Material.SALT.value:
            update_salt(world, x, y, gravity)
        elif mat_val == Material.CEMENT.value:
            update_cement(world, x, y, gravity)
        elif mat_val == Material.MOLTEN_METAL.value:
            update_molten_metal(world, x, y, gravity)
        elif mat_val == Material.STONE.value:
            update_stone(world, x, y)
        elif mat_val == Material.PLANT.value:
            update_plant(world, x, y)
        elif mat_val == Material.METAL.value:
            update_metal(world, x, y)
    
    # Обновляем поднимающиеся материалы
    for x, y, mat_val in rising_cells:
        if mat_val == Material.FIRE.value:
            update_fire(world, x, y)
        elif mat_val == Material.SMOKE.value:
            update_smoke(world, x, y, wind)
        elif mat_val == Material.STEAM.value:
            update_steam(world, x, y, wind)
        elif mat_val == Material.GAS.value:
            update_gas(world, x, y, wind)
        elif mat_val == Material.ASH.value:
            update_ash(world, x, y, wind)


def update_sand(world: World, x: int, y: int, gravity: tuple) -> None:
    """
    Обновляет клетку с песком.
    
    Песок падает вниз, если возможно, иначе скатывается диагонально.
    Может вытеснять воду.
    
    Args:
        world: Мир
        x, y: Координаты клетки
        gravity: Направление гравитации (dx, dy)
    """
    if world.is_updated(x, y):
        return
    
    # Проверка на лаву рядом (песок превращается в камень/стекло)
    neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
    for nx, ny in neighbors:
        if world.is_valid(nx, ny):
            neighbor_mat = world.get(nx, ny)
            if neighbor_mat == Material.LAVA:
                # Лава обжигает песок в камень
                if random.random() < 0.4:
                    world.set(x, y, Material.STONE, 0)
                    world.wake_cell(x, y)
                    world.mark_updated(x, y)
                    return
    
    gx, gy = gravity
    nx, ny = x + gx, y + gy
    
    # Проверка падения вниз
    if world.is_valid(nx, ny):
        below_mat = world.get(nx, ny)
        
        if below_mat == Material.EMPTY:
            # Падение в пустоту
            world.swap(x, y, nx, ny)
            world.mark_updated(nx, ny)
            world.mark_updated(x, y)
            return
        elif below_mat == Material.WATER:
            # Песок тонет в воде (меняется местами)
            world.swap(x, y, nx, ny)
            world.mark_updated(nx, ny)
            world.mark_updated(x, y)
            return
    
    # Попытка скатиться диагонально
    # Случайный порядок для устранения перекоса
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
    
    world.mark_updated(x, y)


def update_water(world: World, x: int, y: int, gravity: tuple) -> None:
    """
    Обновляет клетку с водой.
    
    Вода падает вниз, иначе течет вбок или по диагонали.
    
    Args:
        world: Мир
        x, y: Координаты клетки
        gravity: Направление гравитации (dx, dy)
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
    
    # Попытка течь по диагонали вниз
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
    
    # Течение вбок (случайное направление и дальность)
    side_dirs = [(-1, 0), (1, 0)]
    random.shuffle(side_dirs)
    
    for dx, dy in side_dirs:
        # Пытаемся сдвинуться на 1-3 клетки
        flow_dist = random.randint(1, min(WATER_FLOW_DISTANCE, world.width // 2))
        
        for dist in range(1, flow_dist + 1):
            nx, ny = x + dx * dist, y
            if world.is_valid(nx, ny):
                side_mat = world.get(nx, ny)
                if side_mat == Material.EMPTY:
                    world.swap(x, y, nx, ny)
                    world.mark_updated(nx, ny)
                    world.mark_updated(x, y)
                    return
                elif side_mat != Material.WATER:
                    # Встретили препятствие, останавливаемся
                    break
    
    # Проверка соседей на превращение в пар от огня/лавы
    neighbors = [
        (x - 1, y), (x + 1, y),
        (x, y - 1), (x, y + 1),
        (x - 1, y - 1), (x + 1, y - 1),
        (x - 1, y + 1), (x + 1, y + 1),
    ]
    
    for nx, ny in neighbors:
        if world.is_valid(nx, ny):
            neighbor_mat = world.get(nx, ny)
            if neighbor_mat == Material.FIRE or neighbor_mat == Material.LAVA:
                # Вода испаряется в пар от тепла (как в Noita)
                if random.random() < 0.2:
                    world.set(x, y, Material.STEAM, random.randint(STEAM_LIFE_MIN, STEAM_LIFE_MAX))
                    world.wake_cell(x, y)
                    world.mark_updated(x, y)
                    return
            elif neighbor_mat == Material.MOLTEN_METAL:
                # Вода испаряется от расплавленного металла
                if random.random() < 0.3:
                    world.set(x, y, Material.STEAM, random.randint(STEAM_LIFE_MIN, STEAM_LIFE_MAX))
                    world.wake_cell(x, y)
                    world.mark_updated(x, y)
                    return
            elif neighbor_mat == Material.ICE:
                # Вода замерзает рядом со льдом (как в Noita)
                if random.random() < 0.01:  # Низкая вероятность
                    world.set(x, y, Material.ICE, 0)
                    world.wake_cell(x, y)
                    world.mark_updated(x, y)
                    return
            elif neighbor_mat == Material.ACID:
                # Кислота разбавляется водой (нейтрализуется)
                if random.random() < 0.3:
                    # Вода нейтрализует кислоту, превращая её в воду
                    world.set(nx, ny, Material.WATER, 0)
                    world.wake_cell(nx, ny)
                    world.mark_updated(nx, ny)
    
    world.mark_updated(x, y)


def update_fire(world: World, x: int, y: int) -> None:
    """
    Обновляет клетку с огнем.
    
    Огонь имеет таймер жизни, распространяется на соседние горючие материалы.
    
    Args:
        world: Мир
        x, y: Координаты клетки
    """
    if world.is_updated(x, y):
        return
    
    # Уменьшаем таймер жизни
    life = world.get_life(x, y)
    if life > 0:
        life -= 1
        world.set(x, y, Material.FIRE, life)
    else:
        # Огонь погас, превращается в дым
        world.set(x, y, Material.SMOKE, random.randint(25, 60))
        world.mark_updated(x, y)
        return
    
    # Распространение на соседей
    from falling_sand.materials import is_flammable
    from falling_sand.config import P_IGNITE
    
    neighbors = [
        (x - 1, y), (x + 1, y),
        (x, y - 1), (x, y + 1),
        (x - 1, y - 1), (x + 1, y - 1),
        (x - 1, y + 1), (x + 1, y + 1),
    ]
    
    random.shuffle(neighbors)
    
    for nx, ny in neighbors:
        if world.is_valid(nx, ny) and not world.is_updated(nx, ny):
            neighbor_mat = world.get(nx, ny)
            
            if is_flammable(neighbor_mat):
                # Вероятностное зажигание
                if random.random() < P_IGNITE:
                    from falling_sand.config import FIRE_LIFE_MIN, FIRE_LIFE_MAX
                    fire_life = random.randint(FIRE_LIFE_MIN, FIRE_LIFE_MAX)
                    world.set(nx, ny, Material.FIRE, fire_life)
                    world.wake_cell(nx, ny)
                    world.mark_updated(nx, ny)
            elif neighbor_mat == Material.PLANT:
                # Растение горит, превращается в пепел
                if random.random() < P_IGNITE:
                    world.set(nx, ny, Material.ASH, random.randint(ASH_LIFE_MIN, ASH_LIFE_MAX))
                    world.wake_cell(nx, ny)
                    world.mark_updated(nx, ny)
            elif neighbor_mat == Material.OIL:
                # Масло зажигается от огня
                if random.random() < P_OIL_IGNITE:
                    from falling_sand.config import FIRE_LIFE_MIN, FIRE_LIFE_MAX
                    world.set(nx, ny, Material.FIRE, random.randint(FIRE_LIFE_MIN, FIRE_LIFE_MAX))
                    world.wake_cell(nx, ny)
                    world.mark_updated(nx, ny)
            elif neighbor_mat == Material.ASH:
                # Пепел сгорает полностью в дым
                if random.random() < 0.5:
                    world.set(nx, ny, Material.SMOKE, random.randint(10, 20))
                    world.wake_cell(nx, ny)
                    world.mark_updated(nx, ny)
            elif neighbor_mat == Material.SNOW:
                # Огонь тает снег
                if random.random() < P_SNOW_MELT:
                    world.set(nx, ny, Material.WATER, 0)
                    world.wake_cell(nx, ny)
                    world.mark_updated(nx, ny)
            elif neighbor_mat == Material.ICE:
                # Огонь тает лед
                if random.random() < P_ICE_MELT:
                    world.set(nx, ny, Material.WATER, 0)
                    world.wake_cell(nx, ny)
                    world.mark_updated(nx, ny)
            elif neighbor_mat == Material.WATER:
                # Вода гасит огонь быстрее
                if random.random() < 0.3:
                    world.set(x, y, Material.SMOKE, random.randint(10, 20))
                    world.mark_updated(x, y)
                    return
    
    world.mark_updated(x, y)


def update_smoke(world: World, x: int, y: int, wind: tuple) -> None:
    """
    Обновляет клетку с дымом.
    
    Дым поднимается вверх, рассеивается в стороны, исчезает со временем.
    
    Args:
        world: Мир
        x, y: Координаты клетки
        wind: Направление ветра (dx, dy)
    """
    if world.is_updated(x, y):
        return
    
    # Уменьшаем таймер жизни
    life = world.get_life(x, y)
    if life > 0:
        life -= 1
        world.set(x, y, Material.SMOKE, life)
    else:
        # Дым рассеялся
        world.set(x, y, Material.EMPTY, 0)
        world.mark_updated(x, y)
        return
    
    wx, wy = wind
    
    # Попытка подняться вверх (против гравитации)
    nx, ny = x + wx, y - 1 + wy
    
    if world.is_valid(nx, ny):
        above_mat = world.get(nx, ny)
        if above_mat == Material.EMPTY:
            world.swap(x, y, nx, ny)
            world.mark_updated(nx, ny)
            world.mark_updated(x, y)
            return
    
    # Попытка подняться по диагонали
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
    
    # Рассеивание вбок (с учетом ветра)
    side_dirs = [(-1, 0), (1, 0)]
    if wx != 0:
        # Ветер влияет на направление
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

def update_oil(world: World, x: int, y: int, gravity: tuple) -> None:
    """Обновляет клетку с маслом - плавает на воде, горит."""
    if world.is_updated(x, y):
        return
    
    gx, gy = gravity
    nx, ny = x + gx, y + gy
    
    if world.is_valid(nx, ny):
        below_mat = world.get(nx, ny)
        if below_mat == Material.EMPTY:
            world.swap(x, y, nx, ny)
            world.mark_updated(nx, ny)
            world.mark_updated(x, y)
            return
        elif below_mat == Material.WATER:
            world.swap(x, y, nx, ny)
            world.mark_updated(nx, ny)
            world.mark_updated(x, y)
            return
    
    side_dirs = [(-1, 0), (1, 0)]
    random.shuffle(side_dirs)
    for dx, dy in side_dirs:
        nx, ny = x + dx, y
        if world.is_valid(nx, ny):
            side_mat = world.get(nx, ny)
            if side_mat == Material.EMPTY or side_mat == Material.WATER:
                world.swap(x, y, nx, ny)
                world.mark_updated(nx, ny)
                world.mark_updated(x, y)
                return
    
    # Проверка на огонь/лаву рядом (масло загорается)
    neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
    for nx, ny in neighbors:
        if world.is_valid(nx, ny) and not world.is_updated(nx, ny):
            neighbor_mat = world.get(nx, ny)
            if neighbor_mat == Material.FIRE or neighbor_mat == Material.LAVA:
                if random.random() < P_OIL_IGNITE:
                    from falling_sand.config import FIRE_LIFE_MIN, FIRE_LIFE_MAX
                    world.set(x, y, Material.FIRE, random.randint(FIRE_LIFE_MIN, FIRE_LIFE_MAX))
                    world.wake_cell(x, y)
                    world.mark_updated(x, y)
                    return
    
    world.mark_updated(x, y)


def update_steam(world: World, x: int, y: int, wind: tuple) -> None:
    """Обновляет клетку с паром - поднимается, конденсируется."""
    if world.is_updated(x, y):
        return
    
    life = world.get_life(x, y)
    if life > 0:
        life -= 1
        world.set(x, y, Material.STEAM, life)
    else:
        if random.random() < P_STEAM_CONDENSE:
            world.set(x, y, Material.WATER, 0)
        else:
            world.set(x, y, Material.EMPTY, 0)
        world.mark_updated(x, y)
        return
    
    wx, wy = wind
    nx, ny = x + wx, y - 1 + wy
    
    if world.is_valid(nx, ny) and world.get(nx, ny) == Material.EMPTY:
        world.swap(x, y, nx, ny)
        world.mark_updated(nx, ny)
        world.mark_updated(x, y)
        return
    
    directions = [(-1, -1), (1, -1)]
    random.shuffle(directions)
    for dx, dy in directions:
        nx, ny = x + dx + wx, y + dy + wy
        if world.is_valid(nx, ny) and world.get(nx, ny) == Material.EMPTY:
            world.swap(x, y, nx, ny)
            world.mark_updated(nx, ny)
            world.mark_updated(x, y)
            return
    
    world.mark_updated(x, y)


def update_ember(world: World, x: int, y: int, gravity: tuple) -> None:
    """Обновляет клетку с угольками - падают, зажигают дерево."""
    if world.is_updated(x, y):
        return
    
    life = world.get_life(x, y)
    if life > 0:
        life -= 1
        world.set(x, y, Material.EMBER, life)
    else:
        world.set(x, y, Material.SMOKE, random.randint(10, 20))
        world.mark_updated(x, y)
        return
    
    gx, gy = gravity
    nx, ny = x + gx, y + gy
    
    if world.is_valid(nx, ny):
        below_mat = world.get(nx, ny)
        if below_mat == Material.EMPTY or below_mat == Material.WATER:
            world.swap(x, y, nx, ny)
            world.mark_updated(nx, ny)
            world.mark_updated(x, y)
            return
    
    neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
    for nx, ny in neighbors:
        if world.is_valid(nx, ny) and not world.is_updated(nx, ny):
            neighbor_mat = world.get(nx, ny)
            if neighbor_mat == Material.WOOD:
                if random.random() < P_EMBER_IGNITE:
                    from falling_sand.config import FIRE_LIFE_MIN, FIRE_LIFE_MAX
                    world.set(nx, ny, Material.FIRE, random.randint(FIRE_LIFE_MIN, FIRE_LIFE_MAX))
                    world.wake_cell(nx, ny)
                    world.mark_updated(nx, ny)
            elif neighbor_mat == Material.PLANT:
                # Угольки зажигают растения
                if random.random() < P_EMBER_IGNITE:
                    from falling_sand.config import FIRE_LIFE_MIN, FIRE_LIFE_MAX
                    world.set(nx, ny, Material.FIRE, random.randint(FIRE_LIFE_MIN, FIRE_LIFE_MAX))
                    world.wake_cell(nx, ny)
                    world.mark_updated(nx, ny)
            elif neighbor_mat == Material.OIL:
                # Угольки зажигают масло
                if random.random() < P_OIL_IGNITE:
                    from falling_sand.config import FIRE_LIFE_MIN, FIRE_LIFE_MAX
                    world.set(nx, ny, Material.FIRE, random.randint(FIRE_LIFE_MIN, FIRE_LIFE_MAX))
                    world.wake_cell(nx, ny)
                    world.mark_updated(nx, ny)
    
    world.mark_updated(x, y)


def update_lava(world: World, x: int, y: int, gravity: tuple) -> None:
    """Обновляет клетку с лавой - течет, зажигает, остывает."""
    if world.is_updated(x, y):
        return
    
    life = world.get_life(x, y)
    if life > 0:
        life -= 1
        world.set(x, y, Material.LAVA, life)
    else:
        # Лава остывает и превращается в камень
        world.set(x, y, Material.STONE, 0)
        world.mark_updated(x, y)
        return
    
    gx, gy = gravity
    nx, ny = x + gx, y + gy
    
    if world.is_valid(nx, ny):
        below_mat = world.get(nx, ny)
        if below_mat == Material.EMPTY:
            world.swap(x, y, nx, ny)
            world.mark_updated(nx, ny)
            world.mark_updated(x, y)
            return
        elif below_mat == Material.WATER:
            # Лава + Вода = Пар + Камень (как в Noita)
            world.set(x, y, Material.STONE, 0)  # Лава превращается в камень
            world.set(nx, ny, Material.STEAM, random.randint(STEAM_LIFE_MIN, STEAM_LIFE_MAX))
            world.wake_cell(x, y)  # Будим область реакции
            world.wake_cell(nx, ny)
            world.mark_updated(nx, ny)
            world.mark_updated(x, y)
            return
    
    directions = [(-1, 1), (1, 1)] if gy > 0 else [(-1, -1), (1, -1)]
    random.shuffle(directions)
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if world.is_valid(nx, ny) and world.get(nx, ny) == Material.EMPTY:
            world.swap(x, y, nx, ny)
            world.mark_updated(nx, ny)
            world.mark_updated(x, y)
            return
    
    neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
    for nx, ny in neighbors:
        if world.is_valid(nx, ny) and not world.is_updated(nx, ny):
            neighbor_mat = world.get(nx, ny)
            if neighbor_mat == Material.WOOD:
                if random.random() < P_LAVA_IGNITE:
                    from falling_sand.config import FIRE_LIFE_MIN, FIRE_LIFE_MAX
                    world.set(nx, ny, Material.FIRE, random.randint(FIRE_LIFE_MIN, FIRE_LIFE_MAX))
                    world.wake_cell(nx, ny)
                    world.mark_updated(nx, ny)
            elif neighbor_mat == Material.PLANT:
                # Лава сжигает растения
                if random.random() < P_LAVA_IGNITE:
                    world.set(nx, ny, Material.ASH, random.randint(ASH_LIFE_MIN, ASH_LIFE_MAX))
                    world.wake_cell(nx, ny)
                    world.mark_updated(nx, ny)
            elif neighbor_mat == Material.ICE:
                # Лава плавит лед в воду (как в Noita)
                world.set(nx, ny, Material.WATER, 0)
                world.wake_cell(nx, ny)
                world.mark_updated(nx, ny)
            elif neighbor_mat == Material.SNOW:
                # Лава тает снег
                if random.random() < P_SNOW_MELT:
                    world.set(nx, ny, Material.WATER, 0)
                    world.wake_cell(nx, ny)
                    world.mark_updated(nx, ny)
            elif neighbor_mat == Material.METAL:
                # Лава плавит металл
                if random.random() < P_METAL_MELT:
                    world.set(nx, ny, Material.MOLTEN_METAL, random.randint(MOLTEN_METAL_LIFE_MIN, MOLTEN_METAL_LIFE_MAX))
                    world.wake_cell(nx, ny)
                    world.mark_updated(nx, ny)
            elif neighbor_mat == Material.OIL:
                # Лава зажигает масло
                if random.random() < P_OIL_IGNITE:
                    from falling_sand.config import FIRE_LIFE_MIN, FIRE_LIFE_MAX
                    world.set(nx, ny, Material.FIRE, random.randint(FIRE_LIFE_MIN, FIRE_LIFE_MAX))
                    world.wake_cell(nx, ny)
                    world.mark_updated(nx, ny)
            elif neighbor_mat == Material.GAS:
                # Лава взрывает газ
                if random.random() < P_GAS_EXPLODE:
                    # Взрыв - создаем огонь вокруг
                    for ex, ey in neighbors:
                        if world.is_valid(ex, ey) and world.get(ex, ey) == Material.EMPTY:
                            from falling_sand.config import FIRE_LIFE_MIN, FIRE_LIFE_MAX
                            world.set(ex, ey, Material.FIRE, random.randint(FIRE_LIFE_MIN, FIRE_LIFE_MAX))
                            world.wake_cell(ex, ey)
                    world.set(nx, ny, Material.EMPTY, 0)
                    world.wake_cell(nx, ny)
                    world.mark_updated(nx, ny)
            elif neighbor_mat == Material.SOIL:
                # Лава превращает почву в камень (обжигает)
                if random.random() < 0.3:
                    world.set(nx, ny, Material.STONE, 0)
                    world.wake_cell(nx, ny)
                    world.mark_updated(nx, ny)
            elif neighbor_mat == Material.SAND:
                # Лава превращает песок в стекло/камень (обжигает)
                if random.random() < 0.4:
                    world.set(nx, ny, Material.STONE, 0)
                    world.wake_cell(nx, ny)
                    world.mark_updated(nx, ny)
    
    world.mark_updated(x, y)


def update_ice(world: World, x: int, y: int) -> None:
    """Обновляет клетку со льдом - тает от огня/лавы."""
    if world.is_updated(x, y):
        return
    
    neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
    for nx, ny in neighbors:
        if world.is_valid(nx, ny):
            neighbor_mat = world.get(nx, ny)
            if neighbor_mat == Material.FIRE or neighbor_mat == Material.LAVA:
                # Лед тает от огня/лавы (как в Noita)
                if random.random() < P_ICE_MELT:
                    world.set(x, y, Material.WATER, 0)
                    world.wake_cell(x, y)
                    world.mark_updated(x, y)
                    return
            elif neighbor_mat == Material.MOLTEN_METAL:
                # Лед тает от расплавленного металла
                if random.random() < P_ICE_MELT:
                    world.set(x, y, Material.WATER, 0)
                    world.wake_cell(x, y)
                    world.mark_updated(x, y)
                    return
    
    world.mark_updated(x, y)


def update_acid(world: World, x: int, y: int, gravity: tuple) -> None:
    """Обновляет клетку с кислотой - течет, разъедает материалы."""
    if world.is_updated(x, y):
        return
    
    gx, gy = gravity
    nx, ny = x + gx, y + gy
    
    if world.is_valid(nx, ny):
        below_mat = world.get(nx, ny)
        if below_mat == Material.EMPTY:
            world.swap(x, y, nx, ny)
            world.mark_updated(nx, ny)
            world.mark_updated(x, y)
            return
    
    directions = [(-1, 1), (1, 1)] if gy > 0 else [(-1, -1), (1, -1)]
    random.shuffle(directions)
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if world.is_valid(nx, ny) and world.get(nx, ny) == Material.EMPTY:
            world.swap(x, y, nx, ny)
            world.mark_updated(nx, ny)
            world.mark_updated(x, y)
            return
    
    side_dirs = [(-1, 0), (1, 0)]
    random.shuffle(side_dirs)
    for dx, dy in side_dirs:
        nx, ny = x + dx, y
        if world.is_valid(nx, ny) and world.get(nx, ny) == Material.EMPTY:
            world.swap(x, y, nx, ny)
            world.mark_updated(nx, ny)
            world.mark_updated(x, y)
            return
    
    neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
    for nx, ny in neighbors:
        if world.is_valid(nx, ny) and not world.is_updated(nx, ny):
            neighbor_mat = world.get(nx, ny)
            if neighbor_mat in [Material.WOOD, Material.ICE]:
                if random.random() < P_ACID_DISSOLVE:
                    world.set(nx, ny, Material.EMPTY, 0)
                    world.wake_cell(nx, ny)
                    world.mark_updated(nx, ny)
            elif neighbor_mat == Material.PLANT:
                # Кислота разъедает растения
                if random.random() < P_ACID_DISSOLVE:
                    world.set(nx, ny, Material.EMPTY, 0)
                    world.wake_cell(nx, ny)
                    world.mark_updated(nx, ny)
            elif neighbor_mat == Material.SAND:
                # Кислота разъедает песок
                if random.random() < P_ACID_DISSOLVE * 0.5:  # Медленнее чем дерево
                    world.set(nx, ny, Material.EMPTY, 0)
                    world.wake_cell(nx, ny)
                    world.mark_updated(nx, ny)
            elif neighbor_mat == Material.SOIL:
                # Кислота разъедает почву
                if random.random() < P_ACID_DISSOLVE * 0.7:
                    world.set(nx, ny, Material.EMPTY, 0)
                    world.wake_cell(nx, ny)
                    world.mark_updated(nx, ny)
            elif neighbor_mat == Material.CEMENT:
                # Кислота разъедает цемент
                if random.random() < P_ACID_DISSOLVE * 0.6:
                    world.set(nx, ny, Material.EMPTY, 0)
                    world.wake_cell(nx, ny)
                    world.mark_updated(nx, ny)
            elif neighbor_mat == Material.WATER:
                # Вода нейтрализует кислоту
                if random.random() < 0.3:
                    world.set(x, y, Material.WATER, 0)
                    world.wake_cell(x, y)
                    world.mark_updated(x, y)
                    return
    
    world.mark_updated(x, y)


def update_gas(world: World, x: int, y: int, wind: tuple) -> None:
    """Обновляет клетку с газом - поднимается, взрывается от огня."""
    if world.is_updated(x, y):
        return
    
    life = world.get_life(x, y)
    if life > 0:
        life -= 1
        world.set(x, y, Material.GAS, life)
    else:
        world.set(x, y, Material.EMPTY, 0)
        world.mark_updated(x, y)
        return
    
    neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
    for nx, ny in neighbors:
        if world.is_valid(nx, ny) and world.get(nx, ny) == Material.FIRE:
            if random.random() < P_GAS_EXPLODE:
                for ex, ey in neighbors:
                    if world.is_valid(ex, ey) and world.get(ex, ey) == Material.EMPTY:
                        from falling_sand.config import FIRE_LIFE_MIN, FIRE_LIFE_MAX
                        world.set(ex, ey, Material.FIRE, random.randint(FIRE_LIFE_MIN, FIRE_LIFE_MAX))
                world.set(x, y, Material.EMPTY, 0)
                world.mark_updated(x, y)
                return
    
    wx, wy = wind
    nx, ny = x + wx, y - 1 + wy
    
    if world.is_valid(nx, ny) and world.get(nx, ny) == Material.EMPTY:
        world.swap(x, y, nx, ny)
        world.mark_updated(nx, ny)
        world.mark_updated(x, y)
        return
    
    directions = [(-1, -1), (1, -1)]
    random.shuffle(directions)
    for dx, dy in directions:
        nx, ny = x + dx + wx, y + dy + wy
        if world.is_valid(nx, ny) and world.get(nx, ny) == Material.EMPTY:
            world.swap(x, y, nx, ny)
            world.mark_updated(nx, ny)
            world.mark_updated(x, y)
            return
    
    world.mark_updated(x, y)




def update_stone(world: World, x: int, y: int) -> None:
    """Обновляет клетку с камнем - статичный, может взаимодействовать с кислотой и лавой."""
    if world.is_updated(x, y):
        return
    
    # Камень может быть разъеден кислотой или расплавлен лавой
    neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
    for nx, ny in neighbors:
        if world.is_valid(nx, ny):
            neighbor_mat = world.get(nx, ny)
            if neighbor_mat == Material.ACID:
                # Кислота разъедает камень (медленно)
                if random.random() < P_ACID_DISSOLVE * 0.3:
                    world.set(x, y, Material.EMPTY, 0)
                    world.wake_cell(x, y)
                    world.mark_updated(x, y)
                    return
            elif neighbor_mat == Material.LAVA:
                # Лава может расплавить камень обратно в лаву (очень медленно)
                if random.random() < 0.01:
                    world.set(x, y, Material.LAVA, random.randint(LAVA_LIFE_MIN, LAVA_LIFE_MAX))
                    world.wake_cell(x, y)
                    world.mark_updated(x, y)
                    return
    
    world.mark_updated(x, y)


def update_snow(world: World, x: int, y: int, gravity: tuple) -> None:
    """Обновляет клетку со снегом - падает, тает от огня/лавы/воды."""
    if world.is_updated(x, y):
        return
    
    # Проверка таяния от соседей
    neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
    for nx, ny in neighbors:
        if world.is_valid(nx, ny):
            neighbor_mat = world.get(nx, ny)
            if neighbor_mat in (Material.FIRE, Material.LAVA):
                if random.random() < P_SNOW_MELT:
                    world.set(x, y, Material.WATER, 0)
                    world.wake_cell(x, y)
                    world.mark_updated(x, y)
                    return
            elif neighbor_mat == Material.MOLTEN_METAL:
                # Снег тает от расплавленного металла
                if random.random() < P_SNOW_MELT:
                    world.set(x, y, Material.WATER, 0)
                    world.wake_cell(x, y)
                    world.mark_updated(x, y)
                    return
            elif neighbor_mat == Material.WATER:
                # Снег тает в воде
                if random.random() < P_SNOW_MELT:
                    world.set(x, y, Material.WATER, 0)
                    world.wake_cell(x, y)
                    world.mark_updated(x, y)
                    return
    
    # Физика падения
    gx, gy = gravity
    nx, ny = x + gx, y + gy
    
    if world.is_valid(nx, ny):
        below_mat = world.get(nx, ny)
        if below_mat == Material.EMPTY:
            world.swap(x, y, nx, ny)
            world.mark_updated(nx, ny)
            world.mark_updated(x, y)
            return
    
    # Попытка скатиться диагонально
    directions = [(-1, 1), (1, 1)] if gy > 0 else [(-1, -1), (1, -1)]
    random.shuffle(directions)
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if world.is_valid(nx, ny) and world.get(nx, ny) == Material.EMPTY:
            world.swap(x, y, nx, ny)
            world.mark_updated(nx, ny)
            world.mark_updated(x, y)
            return
    
    world.mark_updated(x, y)


def update_soil(world: World, x: int, y: int, gravity: tuple) -> None:
    """Обновляет клетку с почвой - падает, поддерживает растения."""
    if world.is_updated(x, y):
        return
    
    # Проверка на лаву, огонь, кислоту рядом
    neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
    for nx, ny in neighbors:
        if world.is_valid(nx, ny):
            neighbor_mat = world.get(nx, ny)
            if neighbor_mat == Material.LAVA:
                # Лава обжигает почву в камень
                if random.random() < 0.3:
                    world.set(x, y, Material.STONE, 0)
                    world.wake_cell(x, y)
                    world.mark_updated(x, y)
                    return
            elif neighbor_mat == Material.FIRE:
                # Огонь обжигает почву в камень
                if random.random() < 0.2:
                    world.set(x, y, Material.STONE, 0)
                    world.wake_cell(x, y)
                    world.mark_updated(x, y)
                    return
            elif neighbor_mat == Material.ACID:
                # Кислота разъедает почву
                if random.random() < P_ACID_DISSOLVE * 0.7:
                    world.set(x, y, Material.EMPTY, 0)
                    world.wake_cell(x, y)
                    world.mark_updated(x, y)
                    return
    
    gx, gy = gravity
    nx, ny = x + gx, y + gy
    
    if world.is_valid(nx, ny):
        below_mat = world.get(nx, ny)
        if below_mat == Material.EMPTY:
            world.swap(x, y, nx, ny)
            world.mark_updated(nx, ny)
            world.mark_updated(x, y)
            return
    
    # Попытка скатиться диагонально
    directions = [(-1, 1), (1, 1)] if gy > 0 else [(-1, -1), (1, -1)]
    random.shuffle(directions)
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if world.is_valid(nx, ny) and world.get(nx, ny) == Material.EMPTY:
            world.swap(x, y, nx, ny)
            world.mark_updated(nx, ny)
            world.mark_updated(x, y)
            return
    
    world.mark_updated(x, y)


def update_plant(world: World, x: int, y: int) -> None:
    """Обновляет клетку с растением - статичный, горит, может расти."""
    if world.is_updated(x, y):
        return
    
    # Проверка на огонь, лаву, расплавленный металл, угольки, кислоту
    neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
    for nx, ny in neighbors:
        if world.is_valid(nx, ny):
            neighbor_mat = world.get(nx, ny)
            if neighbor_mat == Material.FIRE:
                # Растение горит, превращается в пепел и дым
                world.set(x, y, Material.ASH, random.randint(ASH_LIFE_MIN, ASH_LIFE_MAX))
                world.wake_cell(x, y)
                world.mark_updated(x, y)
                return
            elif neighbor_mat == Material.LAVA:
                # Лава сжигает растения
                if random.random() < P_LAVA_IGNITE:
                    world.set(x, y, Material.ASH, random.randint(ASH_LIFE_MIN, ASH_LIFE_MAX))
                    world.wake_cell(x, y)
                    world.mark_updated(x, y)
                    return
            elif neighbor_mat == Material.MOLTEN_METAL:
                # Расплавленный металл сжигает растения
                if random.random() < 0.5:
                    world.set(x, y, Material.ASH, random.randint(ASH_LIFE_MIN, ASH_LIFE_MAX))
                    world.wake_cell(x, y)
                    world.mark_updated(x, y)
                    return
            elif neighbor_mat == Material.EMBER:
                # Угольки зажигают растения
                if random.random() < P_EMBER_IGNITE:
                    from falling_sand.config import FIRE_LIFE_MIN, FIRE_LIFE_MAX
                    world.set(x, y, Material.FIRE, random.randint(FIRE_LIFE_MIN, FIRE_LIFE_MAX))
                    world.wake_cell(x, y)
                    world.mark_updated(x, y)
                    return
            elif neighbor_mat == Material.ACID:
                # Кислота разъедает растения
                if random.random() < P_ACID_DISSOLVE:
                    world.set(x, y, Material.EMPTY, 0)
                    world.wake_cell(x, y)
                    world.mark_updated(x, y)
                    return
    
    # Рост растений на почве/воде (низкая вероятность)
    if random.random() < P_PLANT_GROW:
        grow_dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        random.shuffle(grow_dirs)
        for dx, dy in grow_dirs:
            nx, ny = x + dx, y + dy
            if world.is_valid(nx, ny):
                below_mat = world.get(nx, ny)
                if below_mat in (Material.SOIL, Material.WATER) and world.is_valid(nx, ny - 1) and world.get(nx, ny - 1) == Material.EMPTY:
                    world.set(nx, ny - 1, Material.PLANT, 0)
                    world.wake_cell(nx, ny - 1)
                    break
    
    world.mark_updated(x, y)


def update_ash(world: World, x: int, y: int, wind: tuple) -> None:
    """Обновляет клетку с пеплом - поднимается, растворяется в воде в почву."""
    if world.is_updated(x, y):
        return
    
    # Уменьшаем таймер жизни
    life = world.get_life(x, y)
    if life > 0:
        life -= 1
        world.set(x, y, Material.ASH, life)
    else:
        # Пепел рассеивается
        world.set(x, y, Material.EMPTY, 0)
        world.mark_updated(x, y)
        return
    
    # Проверка взаимодействия с водой
    neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
    for nx, ny in neighbors:
        if world.is_valid(nx, ny):
            neighbor_mat = world.get(nx, ny)
            if neighbor_mat == Material.WATER:
                if random.random() < P_ASH_TO_SOIL:
                    world.set(x, y, Material.SOIL, 0)
                    world.wake_cell(x, y)
                    world.mark_updated(x, y)
                    return
    
    # Пепел поднимается вверх
    wx, wy = wind
    nx, ny = x + wx, y - 1 + wy
    
    if world.is_valid(nx, ny) and world.get(nx, ny) == Material.EMPTY:
        world.swap(x, y, nx, ny)
        world.mark_updated(nx, ny)
        world.mark_updated(x, y)
        return
    
    # Попытка подняться по диагонали
    directions = [(-1, -1), (1, -1)]
    random.shuffle(directions)
    for dx, dy in directions:
        nx, ny = x + dx + wx, y + dy + wy
        if world.is_valid(nx, ny) and world.get(nx, ny) == Material.EMPTY:
            world.swap(x, y, nx, ny)
            world.mark_updated(nx, ny)
            world.mark_updated(x, y)
            return
    
    world.mark_updated(x, y)


def update_salt(world: World, x: int, y: int, gravity: tuple) -> None:
    """Обновляет клетку с солью - падает, растворяется в воде."""
    if world.is_updated(x, y):
        return
    
    # Проверка растворения в воде
    neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
    for nx, ny in neighbors:
        if world.is_valid(nx, ny):
            neighbor_mat = world.get(nx, ny)
            if neighbor_mat == Material.WATER:
                if random.random() < P_SALT_DISSOLVE:
                    world.set(x, y, Material.EMPTY, 0)
                    world.wake_cell(x, y)
                    world.mark_updated(x, y)
                    return
    
    # Физика падения
    gx, gy = gravity
    nx, ny = x + gx, y + gy
    
    if world.is_valid(nx, ny):
        below_mat = world.get(nx, ny)
        if below_mat == Material.EMPTY:
            world.swap(x, y, nx, ny)
            world.mark_updated(nx, ny)
            world.mark_updated(x, y)
            return
    
    # Попытка скатиться диагонально
    directions = [(-1, 1), (1, 1)] if gy > 0 else [(-1, -1), (1, -1)]
    random.shuffle(directions)
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if world.is_valid(nx, ny) and world.get(nx, ny) == Material.EMPTY:
            world.swap(x, y, nx, ny)
            world.mark_updated(nx, ny)
            world.mark_updated(x, y)
            return
    
    world.mark_updated(x, y)


def update_cement(world: World, x: int, y: int, gravity: tuple) -> None:
    """Обновляет клетку с цементом - падает, затвердевает в камень при контакте с водой."""
    if world.is_updated(x, y):
        return
    
    # Проверка затвердевания при контакте с водой
    neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
    for nx, ny in neighbors:
        if world.is_valid(nx, ny):
            neighbor_mat = world.get(nx, ny)
            if neighbor_mat == Material.WATER:
                if random.random() < P_CEMENT_HARDEN:
                    world.set(x, y, Material.STONE, 0)
                    world.wake_cell(x, y)
                    world.mark_updated(x, y)
                    return
    
    # Физика падения
    gx, gy = gravity
    nx, ny = x + gx, y + gy
    
    if world.is_valid(nx, ny):
        below_mat = world.get(nx, ny)
        if below_mat == Material.EMPTY:
            world.swap(x, y, nx, ny)
            world.mark_updated(nx, ny)
            world.mark_updated(x, y)
            return
    
    # Попытка скатиться диагонально
    directions = [(-1, 1), (1, 1)] if gy > 0 else [(-1, -1), (1, -1)]
    random.shuffle(directions)
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if world.is_valid(nx, ny) and world.get(nx, ny) == Material.EMPTY:
            world.swap(x, y, nx, ny)
            world.mark_updated(nx, ny)
            world.mark_updated(x, y)
            return
    
    world.mark_updated(x, y)


def update_metal(world: World, x: int, y: int) -> None:
    """Обновляет клетку с металлом - статичный, плавится от лавы и расплавленного металла."""
    if world.is_updated(x, y):
        return
    
    # Проверка плавления от лавы или расплавленного металла
    neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
    for nx, ny in neighbors:
        if world.is_valid(nx, ny):
            neighbor_mat = world.get(nx, ny)
            if neighbor_mat == Material.LAVA:
                if random.random() < P_METAL_MELT:
                    world.set(x, y, Material.MOLTEN_METAL, random.randint(MOLTEN_METAL_LIFE_MIN, MOLTEN_METAL_LIFE_MAX))
                    world.wake_cell(x, y)
                    world.mark_updated(x, y)
                    return
            elif neighbor_mat == Material.MOLTEN_METAL:
                # Расплавленный металл также плавит металл
                if random.random() < P_METAL_MELT * 0.5:
                    world.set(x, y, Material.MOLTEN_METAL, random.randint(MOLTEN_METAL_LIFE_MIN, MOLTEN_METAL_LIFE_MAX))
                    world.wake_cell(x, y)
                    world.mark_updated(x, y)
                    return
    
    world.mark_updated(x, y)


def update_molten_metal(world: World, x: int, y: int, gravity: tuple) -> None:
    """Обновляет клетку с расплавленным металлом - течет как лава, остывает в металл."""
    if world.is_updated(x, y):
        return
    
    # Уменьшаем таймер жизни
    life = world.get_life(x, y)
    if life > 0:
        life -= 1
        world.set(x, y, Material.MOLTEN_METAL, life)
    else:
        # Расплавленный металл остывает
        world.set(x, y, Material.METAL, 0)
        world.mark_updated(x, y)
        return
    
    # Взаимодействие с водой
    gx, gy = gravity
    nx, ny = x + gx, y + gy
    
    if world.is_valid(nx, ny):
        below_mat = world.get(nx, ny)
        if below_mat == Material.WATER:
            # Расплавленный металл + вода = пар + металл
            world.set(x, y, Material.METAL, 0)
            world.set(nx, ny, Material.STEAM, random.randint(STEAM_LIFE_MIN, STEAM_LIFE_MAX))
            world.wake_cell(x, y)
            world.wake_cell(nx, ny)
            world.mark_updated(nx, ny)
            world.mark_updated(x, y)
            return
    
    # Взаимодействие с соседями (горячий расплавленный металл)
    neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
    for nx, ny in neighbors:
        if world.is_valid(nx, ny) and not world.is_updated(nx, ny):
            neighbor_mat = world.get(nx, ny)
            if neighbor_mat == Material.PLANT:
                # Расплавленный металл сжигает растения
                if random.random() < 0.5:
                    world.set(nx, ny, Material.ASH, random.randint(ASH_LIFE_MIN, ASH_LIFE_MAX))
                    world.wake_cell(nx, ny)
                    world.mark_updated(nx, ny)
            elif neighbor_mat == Material.WOOD:
                # Расплавленный металл зажигает дерево
                if random.random() < P_LAVA_IGNITE:
                    from falling_sand.config import FIRE_LIFE_MIN, FIRE_LIFE_MAX
                    world.set(nx, ny, Material.FIRE, random.randint(FIRE_LIFE_MIN, FIRE_LIFE_MAX))
                    world.wake_cell(nx, ny)
                    world.mark_updated(nx, ny)
            elif neighbor_mat == Material.SNOW:
                # Расплавленный металл тает снег
                if random.random() < P_SNOW_MELT:
                    world.set(nx, ny, Material.WATER, 0)
                    world.wake_cell(nx, ny)
                    world.mark_updated(nx, ny)
            elif neighbor_mat == Material.ICE:
                # Расплавленный металл плавит лед
                if random.random() < P_ICE_MELT:
                    world.set(nx, ny, Material.WATER, 0)
                    world.wake_cell(nx, ny)
                    world.mark_updated(nx, ny)
            elif neighbor_mat == Material.GAS:
                # Расплавленный металл взрывает газ
                if random.random() < P_GAS_EXPLODE:
                    # Взрыв - создаем огонь вокруг
                    for ex, ey in neighbors:
                        if world.is_valid(ex, ey) and world.get(ex, ey) == Material.EMPTY:
                            from falling_sand.config import FIRE_LIFE_MIN, FIRE_LIFE_MAX
                            world.set(ex, ey, Material.FIRE, random.randint(FIRE_LIFE_MIN, FIRE_LIFE_MAX))
                            world.wake_cell(ex, ey)
                    world.set(nx, ny, Material.EMPTY, 0)
                    world.wake_cell(nx, ny)
                    world.mark_updated(nx, ny)
    
    # Физика течения
    gx, gy = gravity
    nx, ny = x + gx, y + gy
    
    if world.is_valid(nx, ny):
        below_mat = world.get(nx, ny)
        if below_mat == Material.EMPTY:
            world.swap(x, y, nx, ny)
            world.mark_updated(nx, ny)
            world.mark_updated(x, y)
            return
    
    # Течение по диагонали
    directions = [(-1, 1), (1, 1)] if gy > 0 else [(-1, -1), (1, -1)]
    random.shuffle(directions)
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if world.is_valid(nx, ny) and world.get(nx, ny) == Material.EMPTY:
            world.swap(x, y, nx, ny)
            world.mark_updated(nx, ny)
            world.mark_updated(x, y)
            return
    
    world.mark_updated(x, y)

