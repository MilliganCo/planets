"""Главное приложение falling sand симулятора."""

import pygame
import random
import sys
import os

# Добавляем родительскую директорию в путь для импортов
# Это позволяет запускать как из корня проекта, так и из папки falling_sand
_current_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_current_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

from falling_sand.world import World
from falling_sand.materials import Material
from falling_sand.brush import Brush
from falling_sand.update import tick
from falling_sand.render import Renderer
from falling_sand.config import (
    W, H, WINDOW_WIDTH, WINDOW_HEIGHT,
    TICKS_PER_FRAME, MIN_TICKS_PER_FRAME, MAX_TICKS_PER_FRAME,
    GRAVITY_MODES, WIND_MODES,
    FIRE_LIFE_MIN, FIRE_LIFE_MAX,
    STEAM_LIFE_MIN, STEAM_LIFE_MAX,
    EMBER_LIFE_MIN, EMBER_LIFE_MAX,
    LAVA_LIFE_MIN, LAVA_LIFE_MAX,
    GAS_LIFE_MIN, GAS_LIFE_MAX,
    ASH_LIFE_MIN, ASH_LIFE_MAX,
    MOLTEN_METAL_LIFE_MIN, MOLTEN_METAL_LIFE_MAX,
)


class Simulation:
    """Главный класс симуляции."""
    
    def __init__(self):
        """Инициализация симуляции."""
        pygame.init()
        
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Falling Sand Simulator")
        
        # Мир
        self.world = World(W, H)
        
        # Кисть
        self.brush = Brush()
        
        # Рендерер
        self.renderer = Renderer()
        
        # Состояние
        self.selected_material = Material.SAND
        self.paused = False
        self.ticks_per_frame = TICKS_PER_FRAME
        self.show_hints = True
        
        # Режимы
        self.gravity_index = 0
        self.wind_index = 0
        self.rain_enabled = False
        self.rain_timer = 0
        self.preset_index = 0
        
        # Загружаем начальный пресет
        from falling_sand.presets import preset_dune
        preset_dune(self.world)
        self.preset_index = 0
        
        # Загружаем начальный пресет
        from falling_sand.presets import preset_dune
        preset_dune(self.world)
        
        # Мышь
        self.mouse_down = False
        self.mouse_button = None
        self.last_mouse_pos = None
        
        # FPS (увеличено до 120)
        self.clock = pygame.time.Clock()
        self.fps = 120.0
        self.target_fps = 120
    
    def get_gravity(self) -> tuple:
        """Получает текущее направление гравитации."""
        return GRAVITY_MODES[self.gravity_index][1]
    
    def get_gravity_name(self) -> str:
        """Получает название текущего режима гравитации."""
        return GRAVITY_MODES[self.gravity_index][0]
    
    def get_wind(self) -> tuple:
        """Получает текущее направление ветра."""
        return WIND_MODES[self.wind_index][1]
    
    def get_wind_name(self) -> str:
        """Получает название текущего режима ветра."""
        return WIND_MODES[self.wind_index][0]
    
    def handle_input(self) -> bool:
        """
        Обрабатывает ввод пользователя.
        
        Returns:
            True если нужно продолжить работу, False для выхода
        """
        self.fps = self.clock.get_fps()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                # Выбор материала
                if event.key == pygame.K_1:
                    self.selected_material = Material.SAND
                elif event.key == pygame.K_2:
                    self.selected_material = Material.WATER
                elif event.key == pygame.K_3:
                    self.selected_material = Material.WOOD
                elif event.key == pygame.K_4:
                    self.selected_material = Material.FIRE
                elif event.key == pygame.K_5:
                    self.selected_material = Material.WALL
                elif event.key == pygame.K_6:
                    self.selected_material = Material.OIL
                elif event.key == pygame.K_7:
                    self.selected_material = Material.STEAM
                elif event.key == pygame.K_8:
                    self.selected_material = Material.EMBER
                elif event.key == pygame.K_9:
                    self.selected_material = Material.LAVA
                elif event.key == pygame.K_0:
                    self.selected_material = Material.ICE
                elif event.key == pygame.K_a:
                    self.selected_material = Material.ACID
                elif event.key == pygame.K_s:
                    self.selected_material = Material.GAS
                elif event.key == pygame.K_b:
                    self.selected_material = Material.STONE
                elif event.key == pygame.K_n:
                    self.selected_material = Material.SNOW
                elif event.key == pygame.K_m:
                    self.selected_material = Material.SOIL
                elif event.key == pygame.K_p:
                    self.selected_material = Material.PLANT
                elif event.key == pygame.K_x:
                    self.selected_material = Material.ASH
                elif event.key == pygame.K_l:
                    self.selected_material = Material.SALT
                elif event.key == pygame.K_c:
                    self.selected_material = Material.CEMENT
                elif event.key == pygame.K_k:
                    self.selected_material = Material.METAL
                elif event.key == pygame.K_j:
                    self.selected_material = Material.MOLTEN_METAL
                elif event.key == pygame.K_e:
                    self.selected_material = Material.EMPTY
                
                # Пауза
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                
                # Шаг (на паузе)
                elif event.key == pygame.K_PERIOD:
                    if self.paused:
                        gravity = self.get_gravity()
                        wind = self.get_wind()
                        tick(self.world, gravity, wind)
                
                # Очистка
                elif event.key == pygame.K_r:
                    self.world.clear()
                
                # Пресеты
                elif event.key == pygame.K_f:
                    from falling_sand.presets import preset_dune, preset_lake, preset_forest, preset_rain
                    # Циклически переключаем пресеты
                    if not hasattr(self, 'preset_index'):
                        self.preset_index = 0
                    
                    presets = [preset_dune, preset_lake, preset_forest, preset_rain]
                    presets[self.preset_index](self.world)
                    self.preset_index = (self.preset_index + 1) % len(presets)
                
                # Режим дождя
                elif event.key == pygame.K_t:
                    self.rain_enabled = not self.rain_enabled
                
                # Скорость симуляции
                elif event.key == pygame.K_LEFTBRACKET:
                    self.ticks_per_frame = max(MIN_TICKS_PER_FRAME, self.ticks_per_frame - 1)
                elif event.key == pygame.K_RIGHTBRACKET:
                    self.ticks_per_frame = min(MAX_TICKS_PER_FRAME, self.ticks_per_frame + 1)
                
                # Гравитация
                elif event.key == pygame.K_g:
                    self.gravity_index = (self.gravity_index + 1) % len(GRAVITY_MODES)
                
                # Ветер
                elif event.key == pygame.K_w:
                    self.wind_index = (self.wind_index + 1) % len(WIND_MODES)
                
                # Подсказки
                elif event.key == pygame.K_h:
                    self.show_hints = not self.show_hints
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_down = True
                self.mouse_button = event.button
                
                if event.button == 1:  # ЛКМ
                    x, y = self.world_coords(event.pos)
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        # Режим линии
                        self.brush.reset_line()
                        self.last_mouse_pos = (x, y)
                    else:
                        # Обычное рисование
                        if self.selected_material == Material.EMPTY:
                            self.brush.erase_circle(self.world, x, y)
                        else:
                            life = 0
                            life = 0
                            if self.selected_material == Material.FIRE:
                                life = random.randint(FIRE_LIFE_MIN, FIRE_LIFE_MAX)
                            elif self.selected_material == Material.STEAM:
                                life = random.randint(STEAM_LIFE_MIN, STEAM_LIFE_MAX)
                            elif self.selected_material == Material.EMBER:
                                life = random.randint(EMBER_LIFE_MIN, EMBER_LIFE_MAX)
                            elif self.selected_material == Material.LAVA:
                                life = random.randint(LAVA_LIFE_MIN, LAVA_LIFE_MAX)
                            elif self.selected_material == Material.GAS:
                                life = random.randint(GAS_LIFE_MIN, GAS_LIFE_MAX)
                            elif self.selected_material == Material.ASH:
                                life = random.randint(ASH_LIFE_MIN, ASH_LIFE_MAX)
                            elif self.selected_material == Material.MOLTEN_METAL:
                                life = random.randint(MOLTEN_METAL_LIFE_MIN, MOLTEN_METAL_LIFE_MAX)
                            self.brush.draw_circle(self.world, x, y, self.selected_material, life)
                            self.last_mouse_pos = (x, y)
                
                elif event.button == 3:  # ПКМ
                    x, y = self.world_coords(event.pos)
                    self.brush.erase_circle(self.world, x, y)
                    self.last_mouse_pos = (x, y)
                
                elif event.button == 4:  # Колесо вверх
                    self.brush.set_radius(self.brush.radius + 1)
                
                elif event.button == 5:  # Колесо вниз
                    self.brush.set_radius(self.brush.radius - 1)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouse_down = False
                self.mouse_button = None
                self.brush.reset_line()
            
            elif event.type == pygame.MOUSEMOTION:
                if self.mouse_down:
                    x, y = self.world_coords(event.pos)
                    
                    if self.mouse_button == 1:  # ЛКМ
                        if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                            # Режим линии
                            if self.last_mouse_pos:
                                x1, y1 = self.last_mouse_pos
                                life = 0
                                if self.selected_material == Material.FIRE:
                                    life = random.randint(FIRE_LIFE_MIN, FIRE_LIFE_MAX)
                                elif self.selected_material == Material.STEAM:
                                    life = random.randint(STEAM_LIFE_MIN, STEAM_LIFE_MAX)
                                elif self.selected_material == Material.EMBER:
                                    life = random.randint(EMBER_LIFE_MIN, EMBER_LIFE_MAX)
                                elif self.selected_material == Material.LAVA:
                                    life = random.randint(LAVA_LIFE_MIN, LAVA_LIFE_MAX)
                                elif self.selected_material == Material.GAS:
                                    life = random.randint(GAS_LIFE_MIN, GAS_LIFE_MAX)
                                elif self.selected_material == Material.ASH:
                                    life = random.randint(ASH_LIFE_MIN, ASH_LIFE_MAX)
                                elif self.selected_material == Material.MOLTEN_METAL:
                                    life = random.randint(MOLTEN_METAL_LIFE_MIN, MOLTEN_METAL_LIFE_MAX)
                                self.brush.draw_line(self.world, x1, y1, x, y, self.selected_material, life)
                                self.last_mouse_pos = (x, y)
                        else:
                            # Обычное рисование
                            if self.selected_material == Material.EMPTY:
                                self.brush.erase_circle(self.world, x, y)
                            else:
                                life = 0
                                if self.selected_material == Material.FIRE:
                                    life = random.randint(FIRE_LIFE_MIN, FIRE_LIFE_MAX)
                                elif self.selected_material == Material.STEAM:
                                    life = random.randint(STEAM_LIFE_MIN, STEAM_LIFE_MAX)
                                elif self.selected_material == Material.EMBER:
                                    life = random.randint(EMBER_LIFE_MIN, EMBER_LIFE_MAX)
                                elif self.selected_material == Material.LAVA:
                                    life = random.randint(LAVA_LIFE_MIN, LAVA_LIFE_MAX)
                                elif self.selected_material == Material.GAS:
                                    life = random.randint(GAS_LIFE_MIN, GAS_LIFE_MAX)
                                elif self.selected_material == Material.ASH:
                                    life = random.randint(ASH_LIFE_MIN, ASH_LIFE_MAX)
                                elif self.selected_material == Material.MOLTEN_METAL:
                                    life = random.randint(MOLTEN_METAL_LIFE_MIN, MOLTEN_METAL_LIFE_MAX)
                                self.brush.draw_circle(self.world, x, y, self.selected_material, life)
                    
                    elif self.mouse_button == 3:  # ПКМ
                        self.brush.erase_circle(self.world, x, y)
        
        return True
    
    def world_coords(self, screen_pos: tuple) -> tuple:
        """
        Преобразует координаты экрана в координаты мира.
        
        Args:
            screen_pos: Позиция на экране (x, y)
            
        Returns:
            Координаты в мире (x, y)
        """
        sx, sy = screen_pos
        wx = int(sx / WINDOW_WIDTH * W)
        wy = int(sy / WINDOW_HEIGHT * H)
        return (wx, wy)
    
    def update_simulation(self) -> None:
        """Обновляет симуляцию."""
        if self.paused:
            return
        
        gravity = self.get_gravity()
        wind = self.get_wind()
        
        # Выполняем несколько тиков за кадр
        for _ in range(self.ticks_per_frame):
            tick(self.world, gravity, wind)
        
        # Режим дождя (периодический спавн воды сверху)
        if self.rain_enabled:
            self.rain_timer += 1
            if self.rain_timer >= 3:  # Каждые 3 тика
                self.rain_timer = 0
                # Спавним воду в случайных позициях сверху
                for _ in range(2):
                    x = random.randint(0, W - 1)
                    if self.world.get(x, 0) == Material.EMPTY:
                        self.world.set(x, 0, Material.WATER, 0)
    
    def render(self) -> None:
        """Отрисовывает кадр."""
        # Рендерим мир
        world_surface = self.renderer.render_world(self.world)
        self.screen.blit(world_surface, (0, 0))
        
        # Рендерим overlay
        state = {
            'fps': self.fps,
            'selected_material': self.selected_material,
            'brush_radius': self.brush.radius,
            'paused': self.paused,
            'ticks_per_frame': self.ticks_per_frame,
            'gravity_mode': self.get_gravity_name(),
            'wind_mode': self.get_wind_name(),
            'rain_enabled': self.rain_enabled,
            'show_hints': self.show_hints,
        }
        self.renderer.render_overlay(self.screen, state)
        
        pygame.display.flip()
    
    def run(self) -> None:
        """Главный цикл приложения."""
        running = True
        
        while running:
            running = self.handle_input()
            self.update_simulation()
            self.render()
            self.clock.tick(self.target_fps)
        
        pygame.quit()


def main():
    """Точка входа в приложение."""
    sim = Simulation()
    sim.run()


if __name__ == "__main__":
    main()

