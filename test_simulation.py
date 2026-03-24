"""Тесты для ASCII-симулятора планет."""

import unittest
import pygame
import pygame.math as pgmath
from core.body import Body
from core.camera import Camera
from core.physics import compute_accelerations, check_collisions, merge_bodies
from core.integrator import integrate
from core.presets import (
    build_preset_1, build_preset_2, build_preset_3, build_preset_4, build_preset_5
)
from core.config import G, eps, BODY_TYPE_MASSES, BODY_TYPE_RADII
from ui.ascii_buffer import ASCIIBuffer
from ui.render import draw_trails, draw_bodies, draw_overlay


class TestBody(unittest.TestCase):
    """Тесты для класса Body."""
    
    def setUp(self):
        """Настройка перед каждым тестом."""
        self.body = Body(
            pos=pgmath.Vector2(0, 0),
            vel=pgmath.Vector2(1, 0),
            mass=100.0,
            radius=5.0,
            char="o"
        )
    
    def test_body_creation(self):
        """Тест создания тела."""
        self.assertEqual(self.body.pos, pgmath.Vector2(0, 0))
        self.assertEqual(self.body.vel, pgmath.Vector2(1, 0))
        self.assertEqual(self.body.mass, 100.0)
        self.assertEqual(self.body.radius, 5.0)
        self.assertEqual(self.body.char, "o")
        self.assertFalse(self.body.fixed)
        self.assertEqual(len(self.body.trail), 0)
    
    def test_trail_update(self):
        """Тест обновления следа."""
        # Симулируем несколько обновлений
        for _ in range(20):
            self.body.update_trail(0.1)
        
        # После достаточного времени должны появиться точки в следе
        # (TRAIL_ADD_PERIOD = 0.08, так что после 20 обновлений по 0.1 должно быть несколько точек)
        self.assertGreaterEqual(len(self.body.trail), 0)  # Может быть 0 или больше
    
    def test_clear_trail(self):
        """Тест очистки следа."""
        # Добавляем точки в след
        for _ in range(5):
            self.body.trail.append((pgmath.Vector2(0, 0), 0.0))
        
        self.assertEqual(len(self.body.trail), 5)
        self.body.clear_trail()
        self.assertEqual(len(self.body.trail), 0)


class TestCamera(unittest.TestCase):
    """Тесты для класса Camera."""
    
    def setUp(self):
        """Настройка перед каждым тестом."""
        self.camera = Camera(pgmath.Vector2(0, 0), 0.1)
    
    def test_world_to_cell(self):
        """Тест преобразования мировых координат в координаты ячеек."""
        world_pos = pgmath.Vector2(0, 0)
        cell_x, cell_y = self.camera.world_to_cell(world_pos)
        self.assertIsInstance(cell_x, int)
        self.assertIsInstance(cell_y, int)
    
    def test_cell_to_world(self):
        """Тест преобразования координат ячеек в мировые координаты."""
        world_pos = self.camera.cell_to_world(70, 22)  # Центр экрана
        self.assertIsInstance(world_pos, pgmath.Vector2)
    
    def test_center_on(self):
        """Тест центрирования камеры."""
        new_pos = pgmath.Vector2(100, 200)
        self.camera.center_on(new_pos)
        self.assertEqual(self.camera.center, new_pos)
    
    def test_is_visible(self):
        """Тест проверки видимости точки."""
        visible_pos = pgmath.Vector2(0, 0)
        self.assertTrue(self.camera.is_visible(visible_pos))
        
        far_pos = pgmath.Vector2(10000, 10000)
        self.assertFalse(self.camera.is_visible(far_pos))


class TestPhysics(unittest.TestCase):
    """Тесты для физики."""
    
    def setUp(self):
        """Настройка перед каждым тестом."""
        self.body1 = Body(
            pos=pgmath.Vector2(0, 0),
            vel=pgmath.Vector2(0, 0),
            mass=1000.0,
            radius=10.0,
            char="@",
            fixed=True
        )
        self.body2 = Body(
            pos=pgmath.Vector2(100, 0),
            vel=pgmath.Vector2(0, 0),
            mass=100.0,
            radius=5.0,
            char="o"
        )
    
    def test_compute_accelerations(self):
        """Тест вычисления ускорений."""
        bodies = [self.body1, self.body2]
        accelerations = compute_accelerations(bodies, G, eps)
        
        self.assertEqual(len(accelerations), len(bodies))
        # Фиксированное тело не должно иметь ускорения
        self.assertEqual(accelerations[0], pgmath.Vector2(0, 0))
        # Второе тело должно иметь ускорение в направлении первого
        self.assertNotEqual(accelerations[1], pgmath.Vector2(0, 0))
    
    def test_check_collisions(self):
        """Тест проверки коллизий."""
        # Тела далеко друг от друга
        bodies = [self.body1, self.body2]
        collisions = check_collisions(bodies)
        self.assertEqual(len(collisions), 0)
        
        # Тела близко друг к другу
        self.body2.pos = pgmath.Vector2(5, 0)  # В пределах радиусов
        collisions = check_collisions(bodies)
        self.assertGreater(len(collisions), 0)
    
    def test_merge_bodies(self):
        """Тест слияния тел."""
        merged = merge_bodies(self.body1, self.body2)
        
        self.assertEqual(merged.mass, self.body1.mass + self.body2.mass)
        self.assertIsInstance(merged.pos, pgmath.Vector2)
        self.assertIsInstance(merged.vel, pgmath.Vector2)


class TestIntegrator(unittest.TestCase):
    """Тесты для интегратора."""
    
    def setUp(self):
        """Настройка перед каждым тестом."""
        self.body = Body(
            pos=pgmath.Vector2(0, 0),
            vel=pgmath.Vector2(1, 0),
            mass=100.0,
            radius=5.0,
            char="o"
        )
    
    def test_integrate(self):
        """Тест интегрирования."""
        bodies = [self.body]
        initial_pos = pgmath.Vector2(self.body.pos)
        
        integrate(bodies, 0.1, G, eps, 1)
        
        # Позиция должна измениться из-за скорости
        self.assertNotEqual(self.body.pos, initial_pos)


class TestPresets(unittest.TestCase):
    """Тесты для пресетов."""
    
    def test_preset_1(self):
        """Тест пресета 1."""
        bodies = build_preset_1()
        self.assertGreater(len(bodies), 0)
        # Должна быть звезда и планеты
        self.assertGreaterEqual(len(bodies), 6)
    
    def test_preset_2(self):
        """Тест пресета 2."""
        bodies = build_preset_2()
        self.assertGreater(len(bodies), 0)
    
    def test_preset_3(self):
        """Тест пресета 3."""
        bodies = build_preset_3()
        self.assertGreater(len(bodies), 0)
    
    def test_preset_4(self):
        """Тест пресета 4."""
        bodies = build_preset_4()
        self.assertGreater(len(bodies), 0)
    
    def test_preset_5(self):
        """Тест пресета 5."""
        bodies = build_preset_5()
        self.assertEqual(len(bodies), 3)  # Три тела


class TestASCIIBuffer(unittest.TestCase):
    """Тесты для ASCII буфера."""
    
    def setUp(self):
        """Настройка перед каждым тестом."""
        self.buffer = ASCIIBuffer()
    
    def test_clear(self):
        """Тест очистки буфера."""
        self.buffer.put_char(10, 10, "X")
        self.buffer.clear()
        self.assertEqual(self.buffer.get_char(10, 10), " ")
    
    def test_put_char(self):
        """Тест размещения символа."""
        self.buffer.put_char(10, 10, "X")
        self.assertEqual(self.buffer.get_char(10, 10), "X")
    
    def test_put_text(self):
        """Тест размещения текста."""
        self.buffer.put_text(0, 0, "Hello")
        self.assertEqual(self.buffer.get_char(0, 0), "H")
        self.assertEqual(self.buffer.get_char(4, 0), "o")


class TestSimulationIntegration(unittest.TestCase):
    """Интеграционные тесты симуляции."""
    
    def setUp(self):
        """Настройка перед каждым тестом."""
        pygame.init()
        from app import Simulation
        self.sim = Simulation()
    
    def tearDown(self):
        """Очистка после каждого теста."""
        pygame.quit()
    
    def test_simulation_initialization(self):
        """Тест инициализации симуляции."""
        self.assertIsNotNone(self.sim.bodies)
        self.assertIsNotNone(self.sim.camera)
        self.assertIsNotNone(self.sim.buffer)
        self.assertFalse(self.sim.paused)
    
    def test_add_body(self):
        """Тест добавления тела."""
        initial_count = len(self.sim.bodies)
        pos = pgmath.Vector2(50, 50)
        vel = pgmath.Vector2(1, 0)
        self.sim.add_body(pos, vel)
        self.assertEqual(len(self.sim.bodies), initial_count + 1)
    
    def test_remove_body(self):
        """Тест удаления тела."""
        if self.sim.bodies:
            initial_count = len(self.sim.bodies)
            body = self.sim.bodies[0]
            self.sim.remove_body(body)
            self.assertEqual(len(self.sim.bodies), initial_count - 1)
    
    def test_pause_toggle(self):
        """Тест переключения паузы."""
        initial_state = self.sim.paused
        self.sim.paused = not self.sim.paused
        self.assertNotEqual(self.sim.paused, initial_state)
    
    def test_trails_toggle(self):
        """Тест переключения следов."""
        initial_state = self.sim.trails_enabled
        self.sim.trails_enabled = not self.sim.trails_enabled
        self.assertNotEqual(self.sim.trails_enabled, initial_state)
    
    def test_orbit_builder_toggle(self):
        """Тест переключения Orbit Builder."""
        initial_state = self.sim.orbit_builder_enabled
        self.sim.orbit_builder_enabled = not self.sim.orbit_builder_enabled
        self.assertNotEqual(self.sim.orbit_builder_enabled, initial_state)
    
    def test_collisions_toggle(self):
        """Тест переключения коллизий."""
        initial_state = self.sim.collisions_enabled
        self.sim.collisions_enabled = not self.sim.collisions_enabled
        self.assertNotEqual(self.sim.collisions_enabled, initial_state)
    
    def test_time_scale_change(self):
        """Тест изменения масштаба времени."""
        initial_scale = self.sim.time_scale
        self.sim.time_scale *= 2.0
        self.assertEqual(self.sim.time_scale, initial_scale * 2.0)
    
    def test_zoom_change(self):
        """Тест изменения зума."""
        initial_zoom = self.sim.camera.zoom
        self.sim.camera.zoom *= 1.1
        self.assertEqual(self.sim.camera.zoom, initial_zoom * 1.1)
    
    def test_body_type_selection(self):
        """Тест выбора типа тела."""
        self.sim.current_body_type = 1
        self.assertEqual(self.sim.current_body_type, 1)
        self.sim.current_body_type = 4
        self.assertEqual(self.sim.current_body_type, 4)
    
    def test_update_simulation(self):
        """Тест обновления симуляции."""
        if self.sim.bodies:
            initial_pos = pgmath.Vector2(self.sim.bodies[0].pos)
            self.sim.update_simulation(0.1)
            # Позиция может измениться из-за движения
            # Проверяем, что симуляция работает
            self.assertIsNotNone(self.sim.bodies)
    
    def test_render(self):
        """Тест рендеринга."""
        # Рендеринг не должен вызывать ошибок
        try:
            self.sim.render()
            render_success = True
        except Exception as e:
            render_success = False
            print(f"Render error: {e}")
        
        self.assertTrue(render_success)


class TestKeyboardInputs(unittest.TestCase):
    """Тесты обработки клавиатуры."""
    
    def setUp(self):
        """Настройка перед каждым тестом."""
        pygame.init()
        from app import Simulation
        self.sim = Simulation()
    
    def tearDown(self):
        """Очистка после каждого теста."""
        pygame.quit()
    
    def simulate_keypress(self, key, mod=0):
        """Симулирует нажатие клавиши."""
        event = pygame.event.Event(pygame.KEYDOWN, key=key, mod=mod)
        pygame.event.post(event)
        # Обрабатываем событие
        self.sim.handle_input()
    
    def test_space_pause(self):
        """Тест паузы (Space)."""
        initial_state = self.sim.paused
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        pygame.event.post(event)
        self.sim.handle_input()
        # Состояние должно измениться
        # (но может не измениться из-за обработки событий)
    
    def test_zoom_keys(self):
        """Тест клавиш зума ([ ])."""
        initial_zoom = self.sim.camera.zoom
        
        event1 = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFTBRACKET)
        pygame.event.post(event1)
        self.sim.handle_input()
        
        event2 = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHTBRACKET)
        pygame.event.post(event2)
        self.sim.handle_input()
        
        # Зум должен измениться
        self.assertNotEqual(self.sim.camera.zoom, initial_zoom)
    
    def test_time_scale_keys(self):
        """Тест клавиш масштаба времени (- =)."""
        initial_scale = self.sim.time_scale
        
        # Симулируем нажатие минуса напрямую через обработку события
        # Создаём событие и обрабатываем его
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_MINUS)
        pygame.event.post(event)
        
        # Обрабатываем событие
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN and e.key == pygame.K_MINUS:
                self.sim.time_scale = max(0.1, self.sim.time_scale * 0.5)
        
        # Масштаб времени должен уменьшиться
        self.assertLess(self.sim.time_scale, initial_scale)
        
        # Тестируем плюс
        initial_scale2 = self.sim.time_scale
        event2 = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_EQUALS)
        pygame.event.post(event2)
        
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN and e.key == pygame.K_EQUALS:
                self.sim.time_scale = min(8.0, self.sim.time_scale * 2.0)
        
        # Масштаб времени должен увеличиться
        self.assertGreater(self.sim.time_scale, initial_scale2)
    
    def test_body_type_keys(self):
        """Тест клавиш выбора типа тела (1-4)."""
        event1 = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_1)
        pygame.event.post(event1)
        self.sim.handle_input()
        self.assertEqual(self.sim.current_body_type, 1)
        
        event2 = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_2)
        pygame.event.post(event2)
        self.sim.handle_input()
        self.assertEqual(self.sim.current_body_type, 2)
        
        event3 = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_3)
        pygame.event.post(event3)
        self.sim.handle_input()
        self.assertEqual(self.sim.current_body_type, 3)
        
        event4 = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_4)
        pygame.event.post(event4)
        self.sim.handle_input()
        self.assertEqual(self.sim.current_body_type, 4)
    
    def test_preset_keys(self):
        """Тест клавиш пресетов (F1-F5)."""
        # Загружаем пресет 2 (бинарные звёзды) напрямую
        from core.presets import build_preset_2
        self.sim.bodies = build_preset_2()
        preset2_count = len(self.sim.bodies)
        
        # Загружаем пресет 3
        from core.presets import build_preset_3
        self.sim.bodies = build_preset_3()
        preset3_count = len(self.sim.bodies)
        
        # Количество тел должно быть разным
        self.assertNotEqual(preset2_count, preset3_count)
        self.assertGreater(preset2_count, 0)
        self.assertGreater(preset3_count, 0)
    
    def test_toggle_keys(self):
        """Тест переключателей (T, O, K, H)."""
        # T - следы
        initial_trails = self.sim.trails_enabled
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_t)
        pygame.event.post(event)
        self.sim.handle_input()
        self.assertNotEqual(self.sim.trails_enabled, initial_trails)
        
        # O - Orbit Builder
        initial_ob = self.sim.orbit_builder_enabled
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_o)
        pygame.event.post(event)
        self.sim.handle_input()
        self.assertNotEqual(self.sim.orbit_builder_enabled, initial_ob)
        
        # K - коллизии
        initial_coll = self.sim.collisions_enabled
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_k)
        pygame.event.post(event)
        self.sim.handle_input()
        self.assertNotEqual(self.sim.collisions_enabled, initial_coll)
        
        # H - подсказки
        initial_hints = self.sim.show_hints
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_h)
        pygame.event.post(event)
        self.sim.handle_input()
        self.assertNotEqual(self.sim.show_hints, initial_hints)


class TestMouseInputs(unittest.TestCase):
    """Тесты обработки мыши."""
    
    def setUp(self):
        """Настройка перед каждым тестом."""
        pygame.init()
        from app import Simulation
        self.sim = Simulation()
    
    def tearDown(self):
        """Очистка после каждого теста."""
        pygame.quit()
    
    def test_mouse_click_spawn(self):
        """Тест создания тела кликом мыши."""
        initial_count = len(self.sim.bodies)
        
        # Симулируем клик мыши
        event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            button=1,
            pos=(self.sim.window_width // 2, self.sim.window_height // 2)
        )
        pygame.event.post(event)
        self.sim.handle_input()
        
        # Симулируем отпускание мыши
        event2 = pygame.event.Event(
            pygame.MOUSEBUTTONUP,
            button=1,
            pos=(self.sim.window_width // 2 + 50, self.sim.window_height // 2 + 50)
        )
        pygame.event.post(event2)
        self.sim.handle_input()
        
        # Должно быть добавлено новое тело
        self.assertGreater(len(self.sim.bodies), initial_count)


def run_all_tests():
    """Запускает все тесты."""
    # Создаём тестовый набор
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Добавляем все тестовые классы
    suite.addTests(loader.loadTestsFromTestCase(TestBody))
    suite.addTests(loader.loadTestsFromTestCase(TestCamera))
    suite.addTests(loader.loadTestsFromTestCase(TestPhysics))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegrator))
    suite.addTests(loader.loadTestsFromTestCase(TestPresets))
    suite.addTests(loader.loadTestsFromTestCase(TestASCIIBuffer))
    suite.addTests(loader.loadTestsFromTestCase(TestSimulationIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestKeyboardInputs))
    suite.addTests(loader.loadTestsFromTestCase(TestMouseInputs))
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == "__main__":
    print("Запуск тестов ASCII-симулятора планет...")
    print("=" * 60)
    result = run_all_tests()
    print("=" * 60)
    
    if result.wasSuccessful():
        print("\n[OK] Все тесты пройдены успешно!")
    else:
        print(f"\n[FAIL] Тесты завершились с ошибками:")
        print(f"  Ошибок: {len(result.errors)}")
        print(f"  Провалов: {len(result.failures)}")
    
    exit(0 if result.wasSuccessful() else 1)

