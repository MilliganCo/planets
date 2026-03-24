"""Главное приложение ASCII-симулятора планет."""

import sys
import pygame
import pygame.math as pgmath
from typing import List, Optional
from collections import deque

from core.config import (
    COLS, ROWS, G, eps, TIME_SCALE, SUBSTEPS,
    TRAIL_ADD_PERIOD, DEFAULT_ZOOM, BODY_TYPE_MASSES, BODY_TYPE_RADII, VELOCITY_SCALE
)
from core.body import Body
from core.camera import Camera
from core.physics import compute_accelerations, check_collisions, merge_bodies
from core.integrator import integrate
from core.presets import (
    build_preset_1, build_preset_2, build_preset_3, build_preset_4, build_preset_5
)
from ui.ascii_buffer import ASCIIBuffer
from ui.render import draw_trails, draw_bodies, draw_overlay


class Simulation:
    """Главный класс симуляции."""
    
    def __init__(self):
        """Инициализация симуляции."""
        pygame.init()
        
        # Настройка шрифта
        self.font = pygame.font.Font(None, 16)  # Используем системный моноширинный шрифт
        # Попробуем найти моноширинный шрифт
        try:
            self.font = pygame.font.SysFont("consolas", 16)
        except:
            try:
                self.font = pygame.font.SysFont("courier", 16)
            except:
                pass  # Используем системный по умолчанию
        
        # Размеры ячейки
        char_width, char_height = self.font.size("M")
        self.cell_width = char_width
        self.cell_height = char_height
        
        # Размеры окна
        self.window_width = COLS * self.cell_width
        self.window_height = ROWS * self.cell_height
        
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("ASCII Planet Simulator")
        
        # Состояние симуляции
        self.bodies: List[Body] = []
        self.camera = Camera(pgmath.Vector2(0, 0), DEFAULT_ZOOM)
        self.selected_body: Optional[Body] = None
        self.paused = False
        self.trails_enabled = True
        self.orbit_builder_enabled = False
        self.collisions_enabled = True
        self.show_hints = True
        
        # Параметры симуляции
        self.time_scale = TIME_SCALE
        self.substeps = SUBSTEPS
        self.g = G
        self.eps_val = eps
        
        # Текущий тип тела для создания
        self.current_body_type = 2  # planet по умолчанию
        self.current_body_mass = BODY_TYPE_MASSES[2]["default"]
        
        # Состояние мыши для спавна тел
        self.mouse_spawn_start: Optional[pgmath.Vector2] = None
        self.mouse_spawn_end: Optional[pgmath.Vector2] = None
        self.mouse_dragging = False
        
        # Направление орбиты для Orbit Builder
        self.orbit_clockwise = True
        
        # Лог событий
        self.event_log: deque = deque(maxlen=5)
        
        # FPS
        self.clock = pygame.time.Clock()
        self.fps = 60.0
        
        # ASCII буфер
        self.buffer = ASCIIBuffer()
        
        # Время симуляции
        self.sim_time = 0.0
        
        # Загружаем начальный пресет
        self.bodies = build_preset_1()
        self.selected_body = self.bodies[0] if self.bodies else None
        self.camera.center_on(pgmath.Vector2(0, 0))
    
    def add_body(self, pos: pgmath.Vector2, vel: pgmath.Vector2, body_type: int = None) -> Body:
        """
        Добавляет новое тело в симуляцию.
        
        Args:
            pos: Позиция тела
            vel: Скорость тела
            body_type: Тип тела (1-4), если None - используется текущий тип
            
        Returns:
            Созданное тело
        """
        if body_type is None:
            body_type = self.current_body_type
        
        type_info = BODY_TYPE_MASSES[body_type]
        mass = self.current_body_mass if body_type == self.current_body_type else type_info["default"]
        
        body = Body(
            pos=pos,
            vel=vel,
            mass=mass,
            radius=BODY_TYPE_RADII[body_type],
            char=type_info["char"],
            name=f"{type_info['name']}"
        )
        
        self.bodies.append(body)
        self.log_event(f"Added {type_info['name']} mass={mass:.1f}")
        
        if self.selected_body is None:
            self.selected_body = body
        
        return body
    
    def log_event(self, message: str) -> None:
        """Добавляет событие в лог."""
        self.event_log.append(message)
    
    def remove_body(self, body: Body) -> None:
        """Удаляет тело из симуляции."""
        if body in self.bodies:
            self.bodies.remove(body)
            if self.selected_body == body:
                self.selected_body = self.bodies[0] if self.bodies else None
            self.log_event("Body removed")
    
    def handle_input(self) -> bool:
        """
        Обрабатывает ввод пользователя.
        
        Returns:
            True если нужно продолжить работу, False для выхода
        """
        dt_frame = self.clock.tick(60) / 1000.0  # В секундах
        self.fps = self.clock.get_fps()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                # Пауза
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                
                # Zoom
                elif event.key == pygame.K_LEFTBRACKET or event.key == pygame.K_q:
                    self.camera.zoom *= 0.9
                    self.log_event(f"Zoom: {self.camera.zoom:.3f}")
                elif event.key == pygame.K_RIGHTBRACKET or event.key == pygame.K_e:
                    self.camera.zoom *= 1.1
                    self.log_event(f"Zoom: {self.camera.zoom:.3f}")
                # Альтернативные клавиши для zoom (PageUp/PageDown)
                elif event.key == pygame.K_PAGEUP:
                    self.camera.zoom *= 0.9
                    self.log_event(f"Zoom: {self.camera.zoom:.3f}")
                elif event.key == pygame.K_PAGEDOWN:
                    self.camera.zoom *= 1.1
                    self.log_event(f"Zoom: {self.camera.zoom:.3f}")
                
                # Time scale
                elif event.key == pygame.K_MINUS or event.key == pygame.K_UNDERSCORE:
                    self.time_scale = max(0.1, self.time_scale * 0.5)
                    self.log_event(f"Time scale: {self.time_scale:.2f}x")
                elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                    self.time_scale = min(8.0, self.time_scale * 2.0)
                    self.log_event(f"Time scale: {self.time_scale:.2f}x")
                
                # Центрирование камеры
                elif event.key == pygame.K_c:
                    if self.selected_body:
                        self.camera.center_on(self.selected_body.pos)
                
                # Выбор тела
                elif event.key == pygame.K_TAB:
                    if self.bodies:
                        if self.selected_body and self.selected_body in self.bodies:
                            idx = self.bodies.index(self.selected_body)
                            idx = (idx + 1) % len(self.bodies)
                            self.selected_body = self.bodies[idx]
                        else:
                            self.selected_body = self.bodies[0]
                
                # Следы
                elif event.key == pygame.K_t:
                    self.trails_enabled = not self.trails_enabled
                
                # Очистка следов
                elif event.key == pygame.K_BACKSPACE:
                    for body in self.bodies:
                        body.clear_trail()
                    self.log_event("Trails cleared")
                
                # Orbit Builder
                elif event.key == pygame.K_o:
                    mods = event.mod if hasattr(event, 'mod') else pygame.key.get_mods()
                    if mods & pygame.KMOD_SHIFT:
                        self.orbit_clockwise = not self.orbit_clockwise
                        self.log_event(f"Orbit direction: {'clockwise' if self.orbit_clockwise else 'counter-clockwise'}")
                    else:
                        self.orbit_builder_enabled = not self.orbit_builder_enabled
                        self.log_event(f"Orbit Builder: {'ON' if self.orbit_builder_enabled else 'OFF'}")
                
                # Типы тел
                elif event.key == pygame.K_1:
                    self.current_body_type = 1
                    self.current_body_mass = BODY_TYPE_MASSES[1]["default"]
                elif event.key == pygame.K_2:
                    self.current_body_type = 2
                    self.current_body_mass = BODY_TYPE_MASSES[2]["default"]
                elif event.key == pygame.K_3:
                    self.current_body_type = 3
                    self.current_body_mass = BODY_TYPE_MASSES[3]["default"]
                elif event.key == pygame.K_4:
                    self.current_body_type = 4
                    self.current_body_mass = BODY_TYPE_MASSES[4]["default"]
                
                # Масса
                elif event.key == pygame.K_m:
                    type_info = BODY_TYPE_MASSES[self.current_body_type]
                    # Используем event.mod вместо pygame.key.get_mods() для более надёжного определения
                    mods = event.mod if hasattr(event, 'mod') else pygame.key.get_mods()
                    if mods & pygame.KMOD_SHIFT:
                        self.current_body_mass = max(type_info["min"], self.current_body_mass * 0.9)
                        self.log_event(f"Mass decreased: {self.current_body_mass:.1f}")
                    else:
                        self.current_body_mass = min(type_info["max"], self.current_body_mass * 1.1)
                        self.log_event(f"Mass increased: {self.current_body_mass:.1f}")
                
                # Удаление тела
                elif event.key == pygame.K_DELETE:
                    if self.selected_body:
                        self.remove_body(self.selected_body)
                
                # Фиксация тела
                elif event.key == pygame.K_f:
                    if self.selected_body:
                        self.selected_body.fixed = not self.selected_body.fixed
                        self.log_event(f"{'Fixed' if self.selected_body.fixed else 'Unfixed'} body")
                
                # Коллизии
                elif event.key == pygame.K_k:
                    self.collisions_enabled = not self.collisions_enabled
                
                # Подсказки
                elif event.key == pygame.K_h:
                    self.show_hints = not self.show_hints
                
                # Пресеты
                elif event.key == pygame.K_F1:
                    self.bodies = build_preset_1()
                    self.selected_body = self.bodies[0] if self.bodies else None
                    self.camera.center_on(pgmath.Vector2(0, 0))
                    self.log_event("Loaded: Star + 5 Planets")
                elif event.key == pygame.K_F2:
                    self.bodies = build_preset_2()
                    self.selected_body = self.bodies[0] if self.bodies else None
                    self.camera.center_on(pgmath.Vector2(0, 0))
                    self.log_event("Loaded: Binary Stars + Planets")
                elif event.key == pygame.K_F3:
                    self.bodies = build_preset_3()
                    self.selected_body = self.bodies[0] if self.bodies else None
                    self.camera.center_on(pgmath.Vector2(0, 0))
                    self.log_event("Loaded: Gravity Slingshot")
                elif event.key == pygame.K_F4:
                    self.bodies = build_preset_4()
                    self.selected_body = self.bodies[0] if self.bodies else None
                    self.camera.center_on(pgmath.Vector2(0, 0))
                    self.log_event("Loaded: Rings")
                elif event.key == pygame.K_F5:
                    self.bodies = build_preset_5()
                    self.selected_body = self.bodies[0] if self.bodies else None
                    self.camera.center_on(pgmath.Vector2(0, 0))
                    self.log_event("Loaded: Chaos (3 Bodies)")
                
                # Reset (загружает пресет 1)
                elif event.key == pygame.K_r:
                    self.bodies = build_preset_1()
                    self.selected_body = self.bodies[0] if self.bodies else None
                    self.camera.center_on(pgmath.Vector2(0, 0))
                    self.log_event("Reset to Preset 1")
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # ЛКМ
                    mouse_x, mouse_y = event.pos
                    cell_x = mouse_x // self.cell_width
                    cell_y = mouse_y // self.cell_height
                    world_pos = self.camera.cell_to_world(cell_x, cell_y)
                    
                    if self.orbit_builder_enabled:
                        # Orbit Builder режим
                        if self.selected_body and not self.selected_body.fixed:
                            # Вычисляем круговую скорость
                            r_vec = world_pos - self.selected_body.pos
                            r = r_vec.length()
                            
                            if r > 0:
                                # Круговая скорость: v = sqrt(G * M / r)
                                v_magnitude = (self.g * self.selected_body.mass / r) ** 0.5
                                
                                # Направление перпендикулярно радиусу
                                r_normalized = r_vec.normalize()
                                if self.orbit_clockwise:
                                    tangent = pgmath.Vector2(-r_normalized.y, r_normalized.x)
                                else:
                                    tangent = pgmath.Vector2(r_normalized.y, -r_normalized.x)
                                
                                vel = tangent * v_magnitude + self.selected_body.vel
                                self.add_body(world_pos, vel)
                    else:
                        # Обычный режим спавна
                        self.mouse_spawn_start = world_pos
                        self.mouse_dragging = True
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.mouse_dragging:  # ЛКМ отпущена
                    mouse_x, mouse_y = event.pos
                    cell_x = mouse_x // self.cell_width
                    cell_y = mouse_y // self.cell_height
                    world_pos = self.camera.cell_to_world(cell_x, cell_y)
                    
                    if self.mouse_spawn_start:
                        # Вычисляем скорость из вектора перетаскивания
                        vel_vec = world_pos - self.mouse_spawn_start
                        vel = vel_vec * VELOCITY_SCALE
                        self.add_body(self.mouse_spawn_start, vel)
                    
                    self.mouse_spawn_start = None
                    self.mouse_dragging = False
            
            elif event.type == pygame.MOUSEMOTION:
                if self.mouse_dragging:
                    mouse_x, mouse_y = event.pos
                    cell_x = mouse_x // self.cell_width
                    cell_y = mouse_y // self.cell_height
                    world_pos = self.camera.cell_to_world(cell_x, cell_y)
                    self.mouse_spawn_end = world_pos
        
        return True
    
    def update_simulation(self, dt: float) -> None:
        """Обновляет симуляцию на один кадр."""
        if self.paused:
            return
        
        dt_sim = dt * self.time_scale
        
        # Интеграция движения
        integrate(self.bodies, dt_sim, self.g, self.eps_val, self.substeps)
        
        # Обновление следов
        for body in self.bodies:
            body.update_trail(dt_sim)
        
        # Проверка коллизий
        if self.collisions_enabled and len(self.bodies) > 1:
            collisions = check_collisions(self.bodies)
            merged_bodies = []  # Список вместо set, так как Body не хэшируемый
            
            for body1, body2 in collisions:
                if body1 in merged_bodies or body2 in merged_bodies:
                    continue
                
                merged = merge_bodies(body1, body2)
                self.bodies.remove(body1)
                self.bodies.remove(body2)
                self.bodies.append(merged)
                
                merged_bodies.append(body1)
                merged_bodies.append(body2)
                
                if self.selected_body == body1 or self.selected_body == body2:
                    self.selected_body = merged
                
                self.log_event(f"Merged bodies m={merged.mass:.1f}")
        
        self.sim_time += dt_sim
    
    def render(self) -> None:
        """Отрисовывает кадр."""
        # Очистка буфера
        self.buffer.clear()
        
        # Отрисовка следов
        if self.trails_enabled:
            draw_trails(self.buffer, self.bodies, self.camera)
        
        # Отрисовка тел
        draw_bodies(self.buffer, self.bodies, self.camera, self.selected_body)
        
        # Отрисовка overlay
        state = {
            'fps': self.fps,
            'body_count': len(self.bodies),
            'time_scale': self.time_scale,
            'substeps': self.substeps,
            'g': self.g,
            'eps': self.eps_val,
            'selected_body': self.selected_body,
            'trails_enabled': self.trails_enabled,
            'orbit_builder_enabled': self.orbit_builder_enabled,
            'collisions_enabled': self.collisions_enabled,
            'event_log': list(self.event_log),
            'show_hints': self.show_hints,
        }
        draw_overlay(self.buffer, state)
        
        # Отрисовка вектора скорости при перетаскивании мыши
        if self.mouse_dragging and self.mouse_spawn_start and self.mouse_spawn_end:
            start_cell = self.camera.world_to_cell(self.mouse_spawn_start)
            end_cell = self.camera.world_to_cell(self.mouse_spawn_end)
            # Простая отрисовка линии (можно улучшить)
            # Пока просто рисуем точку в конце
            self.buffer.put_char(end_cell[0], end_cell[1], 'X')
        
        # Вывод буфера на экран
        buffer_text = self.buffer.render_to_string()
        lines = buffer_text.split('\n')
        
        self.screen.fill((0, 0, 0))  # Чёрный фон
        
        for y, line in enumerate(lines):
            text_surface = self.font.render(line, True, (255, 255, 255))  # Белый текст
            self.screen.blit(text_surface, (0, y * self.cell_height))
        
        pygame.display.flip()
    
    def run(self) -> None:
        """Главный цикл приложения."""
        running = True
        
        while running:
            running = self.handle_input()
            
            # Обновление симуляции
            dt = 1.0 / 60.0  # Фиксированный шаг времени
            self.update_simulation(dt)
            
            # Рендеринг
            self.render()
        
        pygame.quit()


def main():
    """Точка входа в приложение."""
    sim = Simulation()
    sim.run()


if __name__ == "__main__":
    main()

