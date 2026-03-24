"""Рендеринг сетки и UI overlay."""

import pygame
from falling_sand.world import World
from falling_sand.materials import Material, get_color, get_symbol
from falling_sand.config import W, H, PIXEL_SIZE, WINDOW_WIDTH, WINDOW_HEIGHT


class Renderer:
    """Рендерер для отрисовки мира и UI."""
    
    def __init__(self):
        """Инициализация рендерера."""
        # Поверхность для пиксельного рендеринга
        self.world_surface = pygame.Surface((W, H))
        
        # Шрифт для ASCII overlay
        try:
            self.font = pygame.font.SysFont("consolas", 14)
        except:
            try:
                self.font = pygame.font.SysFont("courier", 14)
            except:
                self.font = pygame.font.Font(None, 14)
        
        self.frame_count = 0
        self.fps = 60.0
    
    def render_world(self, world: World) -> pygame.Surface:
        """
        Рендерит мир в пиксельную поверхность (высокооптимизированная версия).
        
        Оптимизации:
        - Рендерит только активные клетки
        - Использует кэш цветов
        - Прямые обращения к массивам
        
        Args:
            world: Мир для отрисовки
            
        Returns:
            Поверхность с отрисованным миром
        """
        # Оптимизация: используем прямые обращения к массивам
        width = world.width
        height = world.height
        mat_array = world.mat
        EMPTY_VAL = Material.EMPTY.value
        
        # Кэш цветов для быстрого доступа
        if not hasattr(self, '_color_cache'):
            self._color_cache = {}
            for mat in Material:
                self._color_cache[mat.value] = get_color(mat, 0.0)
        
        # Отслеживаем измененные клетки для частичного обновления
        if not hasattr(self, '_last_mat_state'):
            # Первый рендер - рендерим все активные клетки
            self._last_mat_state = {}
            self.world_surface.fill((0, 0, 0))
            
            # Рендерим все активные клетки
            for x, y in world.active_cells:
                idx = x + y * width
                mat_val = mat_array[idx]
                
                if mat_val != EMPTY_VAL:
                    if mat_val == Material.FIRE.value:
                        color = get_color(Material.FIRE, 0.3)
                    else:
                        color = self._color_cache.get(mat_val, (0, 0, 0))
                    self.world_surface.set_at((x, y), color)
                    self._last_mat_state[(x, y)] = mat_val
        else:
            # Инкрементальный рендеринг - обновляем только измененные клетки
            cells_to_update = set()
            
            # Собираем все клетки, которые нужно проверить:
            # 1. Текущие активные клетки
            for x, y in world.active_cells:
                cells_to_update.add((x, y))
                # Добавляем соседей для очистки следов
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        cells_to_update.add((nx, ny))
            
            # 2. Клетки, которые были активными ранее, но теперь могут быть пустыми
            for x, y in list(self._last_mat_state.keys()):
                cells_to_update.add((x, y))
            
            # Обновляем только измененные клетки
            new_state = {}
            for x, y in cells_to_update:
                idx = x + y * width
                mat_val = mat_array[idx]
                
                # Сохраняем состояние только для активных клеток
                if mat_val != EMPTY_VAL:
                    new_state[(x, y)] = mat_val
                
                # Проверяем, изменилась ли клетка
                old_val = self._last_mat_state.get((x, y), EMPTY_VAL)
                if mat_val != old_val:
                    if mat_val != EMPTY_VAL:
                        # Рендерим новую клетку
                        if mat_val == Material.FIRE.value:
                            color = get_color(Material.FIRE, 0.3)
                        else:
                            color = self._color_cache.get(mat_val, (0, 0, 0))
                        self.world_surface.set_at((x, y), color)
                    else:
                        # Очищаем пустую клетку (частица переместилась)
                        self.world_surface.set_at((x, y), (0, 0, 0))
            
            # Обновляем состояние (только активные клетки)
            self._last_mat_state = new_state
        
        # Масштабируем поверхность
        scaled = pygame.transform.scale(self.world_surface, (WINDOW_WIDTH, WINDOW_HEIGHT))
        return scaled
    
    def render_overlay(self, screen: pygame.Surface, state: dict) -> None:
        """
        Рендерит ASCII overlay с информацией о симуляции.
        
        Args:
            screen: Поверхность экрана
            state: Словарь состояния со следующими ключами:
                - fps: FPS
                - selected_material: Выбранный материал
                - brush_radius: Радиус кисти
                - paused: Пауза
                - ticks_per_frame: Скорость симуляции
                - gravity_mode: Режим гравитации
                - wind_mode: Режим ветра
                - rain_enabled: Включен ли дождь
        """
        y_offset = 5
        x_offset = 5
        
        # Строка 1: FPS, материал, кисть
        fps = state.get('fps', 0)
        selected_mat = state.get('selected_material', Material.SAND)
        brush_radius = state.get('brush_radius', 3)
        mat_name = selected_mat.name if hasattr(selected_mat, 'name') else str(selected_mat)
        
        line1 = f"FPS: {fps:.1f} | Material: {mat_name} | Brush: {brush_radius}"
        text = self.font.render(line1, True, (255, 255, 255))
        screen.blit(text, (x_offset, y_offset))
        y_offset += 18
        
        # Строка 2: Режимы
        paused = state.get('paused', False)
        ticks_per_frame = state.get('ticks_per_frame', 2)
        gravity_mode = state.get('gravity_mode', 'Down')
        wind_mode = state.get('wind_mode', 'None')
        rain_enabled = state.get('rain_enabled', False)
        
        modes = []
        if paused:
            modes.append("PAUSED")
        else:
            modes.append("RUNNING")
        
        modes.append(f"Speed: {ticks_per_frame}x")
        modes.append(f"Gravity: {gravity_mode}")
        modes.append(f"Wind: {wind_mode}")
        
        if rain_enabled:
            modes.append("RAIN: ON")
        
        line2 = " | ".join(modes)
        text = self.font.render(line2, True, (255, 255, 255))
        screen.blit(text, (x_offset, y_offset))
        y_offset += 18
        
        # Строка 3: Подсказки (если включены)
        show_hints = state.get('show_hints', True)
        if show_hints:
            line3 = "1-5: SAND/WATER/WOOD/FIRE/WALL | 6-9: OIL/STEAM/EMBER/LAVA | 0: ICE | A: ACID | S: GAS"
            text = self.font.render(line3, True, (200, 200, 200))
            screen.blit(text, (x_offset, y_offset))
            y_offset += 18
            
            line4 = "B: STONE | N: SNOW | M: SOIL | P: PLANT | X: ASH | L: SALT | C: CEMENT | K: METAL | J: MOLTEN_METAL"
            text = self.font.render(line4, True, (200, 200, 200))
            screen.blit(text, (x_offset, y_offset))
            y_offset += 18
            
            line5 = "Space: Pause | .: Step | R: Clear | F: Preset | T: Rain | [ ]: Speed | G: Gravity | W: Wind"
            text = self.font.render(line5, True, (200, 200, 200))
            screen.blit(text, (x_offset, y_offset))
            y_offset += 18
            
            line6 = "Mouse: Draw | Wheel: Brush | Shift: Line | E: Erase | H: Hide hints"
            text = self.font.render(line5, True, (200, 200, 200))
            screen.blit(text, (x_offset, y_offset))
    
    def update_fps(self, fps: float) -> None:
        """
        Обновляет FPS для отображения.
        
        Args:
            fps: Текущий FPS
        """
        self.fps = fps

