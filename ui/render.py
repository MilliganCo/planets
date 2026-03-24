"""Рендеринг следов, тел и UI overlay."""

from typing import List, Optional
import pygame.math as pgmath
from core.body import Body
from core.camera import Camera
from core.config import COLS, ROWS
from ui.ascii_buffer import ASCIIBuffer


def get_trail_char(age_normalized: float) -> str:
    """
    Возвращает символ для точки следа в зависимости от возраста.
    
    Args:
        age_normalized: Нормализованный возраст (0.0 - 1.0)
        
    Returns:
        Символ для отрисовки
    """
    if age_normalized < 0.2:
        return '*'
    elif age_normalized < 0.5:
        return '+'
    elif age_normalized < 0.8:
        return '.'
    else:
        return ','


def draw_trails(buffer: ASCIIBuffer, bodies: List[Body], camera: Camera) -> None:
    """
    Отрисовывает следы орбит тел.
    
    Args:
        buffer: ASCII буфер для отрисовки
        bodies: Список тел
        camera: Камера для преобразования координат
    """
    for body in bodies:
        if not body.trail:
            continue
        
        # Вычисляем максимальный возраст для нормализации
        from core.config import TRAIL_MAX_AGE
        max_age = TRAIL_MAX_AGE  # Используем константу максимального возраста
        
        if max_age == 0:
            max_age = 1.0  # Избегаем деления на ноль
        
        for pos, age in body.trail:
            if not camera.is_visible(pos):
                continue
            
            cell_x, cell_y = camera.world_to_cell(pos)
            
            # Нормализуем возраст
            age_normalized = age / max_age if max_age > 0 else 0.0
            char = get_trail_char(age_normalized)
            
            # Рисуем только если позиция валидна и не перекрыта телом
            buffer.put_char(cell_x, cell_y, char)


def draw_bodies(buffer: ASCIIBuffer, bodies: List[Body], camera: Camera, selected: Optional[Body] = None) -> None:
    """
    Отрисовывает тела на экране.
    
    Args:
        buffer: ASCII буфер для отрисовки
        bodies: Список тел
        camera: Камера для преобразования координат
        selected: Выбранное тело (подсвечивается)
    """
    for body in bodies:
        if not camera.is_visible(body.pos):
            continue
        
        cell_x, cell_y = camera.world_to_cell(body.pos)
        
        # Выбираем символ
        char = body.char
        
        # Подсветка выбранного тела
        if body == selected:
            # Рисуем скобки вокруг
            buffer.put_char(cell_x - 1, cell_y, '[')
            buffer.put_char(cell_x, cell_y, body.char)
            buffer.put_char(cell_x + 1, cell_y, ']')
        else:
            buffer.put_char(cell_x, cell_y, char)


def draw_overlay(buffer: ASCIIBuffer, state: dict) -> None:
    """
    Отрисовывает UI overlay с информацией о симуляции.
    
    Args:
        buffer: ASCII буфер для отрисовки
        state: Словарь состояния симуляции со следующими ключами:
            - fps: FPS
            - body_count: Количество тел
            - time_scale: Множитель времени
            - substeps: Количество подшагов
            - g: Гравитационная постоянная
            - eps: Параметр смягчения
            - selected_body: Выбранное тело (опционально)
            - trails_enabled: Включены ли следы
            - orbit_builder_enabled: Включён ли Orbit Builder
            - collisions_enabled: Включены ли коллизии
            - event_log: Список последних событий (опционально)
    """
    y = 0
    
    # Строка 1: FPS, количество тел, параметры времени
    fps = state.get('fps', 0)
    body_count = state.get('body_count', 0)
    time_scale = state.get('time_scale', 1.0)
    substeps = state.get('substeps', 1)
    
    line1 = f"FPS: {fps:.1f} | Bodies: {body_count} | Time: {time_scale:.2f}x | Substeps: {substeps}"
    buffer.put_text(0, y, line1)
    y += 1
    
    # Строка 2: Физические параметры
    g = state.get('g', 0)
    eps_val = state.get('eps', 0)
    line2 = f"G: {g:.1f} | eps: {eps_val:.1f}"
    buffer.put_text(0, y, line2)
    y += 1
    
    # Строка 3: Выбранное тело
    selected_body = state.get('selected_body')
    if selected_body:
        mass = selected_body.mass
        speed = selected_body.vel.length()
        pos_x = selected_body.pos.x
        pos_y = selected_body.pos.y
        name = selected_body.name or f"Body"
        fixed = "FIXED" if selected_body.fixed else ""
        line3 = f"Selected: {name} | Mass: {mass:.1f} | Speed: {speed:.2f} | Pos: ({pos_x:.1f}, {pos_y:.1f}) {fixed}"
        buffer.put_text(0, y, line3)
        y += 1
    
    # Строка 4: Режимы
    trails_enabled = state.get('trails_enabled', True)
    orbit_builder = state.get('orbit_builder_enabled', False)
    collisions_enabled = state.get('collisions_enabled', True)
    
    modes = []
    if trails_enabled:
        modes.append("Trails: ON")
    else:
        modes.append("Trails: OFF")
    
    if orbit_builder:
        modes.append("Orbit Builder: ON")
    else:
        modes.append("Orbit Builder: OFF")
    
    if collisions_enabled:
        modes.append("Collisions: ON")
    else:
        modes.append("Collisions: OFF")
    
    line4 = " | ".join(modes)
    buffer.put_text(0, y, line4)
    y += 1
    
    # Строка 5: Лог событий (последние 3)
    event_log = state.get('event_log', [])
    if event_log:
        # Берём последние 3 события
        recent_events = event_log[-3:]
        events_text = " | ".join(recent_events)
        buffer.put_text(0, y, f"Events: {events_text}")
        y += 1
    
    # Подсказки внизу (если включены)
    show_hints = state.get('show_hints', False)
    if show_hints:
        y = ROWS - 5
        buffer.put_text(0, y, "H - Hide hints | Space - Pause | [ ] Q/E PageUp/Down - Zoom | - = - Time scale")
        y += 1
        buffer.put_text(0, y, "Tab - Select | C - Center | T - Trails | O/Shift+O - Orbit Builder")
        y += 1
        buffer.put_text(0, y, "1-4 - Body type | M/Shift+M - Mass +/- | Delete - Remove | F - Fix")
        y += 1
        buffer.put_text(0, y, "F1-F5 - Presets | R - Reset | Backspace - Clear trails | K - Collisions")

