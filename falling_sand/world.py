"""Мир симуляции - сетка клеток с материалами."""

import array
from falling_sand.materials import Material
from falling_sand.config import W, H


class World:
    """Мир симуляции с сеткой клеток."""
    
    def __init__(self, width: int = W, height: int = H):
        """
        Инициализация мира.
        
        Args:
            width: Ширина сетки
            height: Высота сетки
        """
        self.width = width
        self.height = height
        self.size = width * height
        
        # 1D массивы для производительности
        # mat[i] - тип материала в клетке i
        # life[i] - таймер жизни (для FIRE/SMOKE) - используем 'H' (unsigned short, 0-65535)
        self.mat = array.array('B', [Material.EMPTY] * self.size)
        self.life = array.array('H', [0] * self.size)  # 'H' = unsigned short (0-65535)
        
        # Маска обновления (tick_id для каждой клетки)
        self.update_mask = array.array('I', [0] * self.size)
        self.current_tick = 0
        
        # Счетчик активных клеток (для оптимизации)
        self.active_cells = set()
        
        # Система "спящих" частиц (sleeping particles) - как в Noita
        # Частицы, которые не двигались несколько тиков, помечаются как "спящие"
        self.sleeping_cells = set()  # Клетки, которые не обновляются
        self.sleep_counter = array.array('B', [0] * self.size)  # Счетчик неподвижности
        
        # Система чанков для оптимизации (чанк = 16x16)
        self.chunk_size = 16
        self.chunks_x = (width + self.chunk_size - 1) // self.chunk_size
        self.chunks_y = (height + self.chunk_size - 1) // self.chunk_size
        self.active_chunks = set()  # Множество активных чанков
        
        # Порог для "засыпания" частиц (после N тиков неподвижности)
        self.SLEEP_THRESHOLD = 3
    
    def _index(self, x: int, y: int) -> int:
        """
        Преобразует координаты в индекс 1D массива.
        
        Args:
            x: X координата
            y: Y координата
            
        Returns:
            Индекс в массиве
        """
        return x + y * self.width
    
    def is_valid(self, x: int, y: int) -> bool:
        """
        Проверяет, валидны ли координаты.
        
        Args:
            x: X координата
            y: Y координата
            
        Returns:
            True если координаты в пределах сетки
        """
        return 0 <= x < self.width and 0 <= y < self.height
    
    def get(self, x: int, y: int) -> Material:
        """
        Получает материал в указанной позиции.
        
        Args:
            x: X координата
            y: Y координата
            
        Returns:
            Тип материала
        """
        if not self.is_valid(x, y):
            return Material.WALL  # Границы = стены
        
        idx = self._index(x, y)
        return Material(self.mat[idx])
    
    def get_life(self, x: int, y: int) -> int:
        """
        Получает таймер жизни в указанной позиции.
        
        Args:
            x: X координата
            y: Y координата
            
        Returns:
            Таймер жизни
        """
        if not self.is_valid(x, y):
            return 0
        
        idx = self._index(x, y)
        return self.life[idx]
    
    def set(self, x: int, y: int, mat: Material, life: int = 0) -> None:
        """
        Устанавливает материал и жизнь в указанной позиции.
        
        Args:
            x: X координата
            y: Y координата
            mat: Тип материала
            life: Таймер жизни (для FIRE/SMOKE)
        """
        if not self.is_valid(x, y):
            return
        
        idx = self._index(x, y)
        old_mat_val = self.mat[idx]
        self.mat[idx] = int(mat)
        # Ограничиваем life до максимума для unsigned short (65535)
        self.life[idx] = min(life, 65535)
        
        # Обновление активных клеток и чанков
        if mat != Material.EMPTY:
            self.active_cells.add((x, y))
            # Если материал изменился или клетка была спящей - разбудим её и соседей
            if old_mat_val != int(mat) or (x, y) in self.sleeping_cells:
                self.wake_cell(x, y)
            chunk_x, chunk_y = x // self.chunk_size, y // self.chunk_size
            self.active_chunks.add((chunk_x, chunk_y))
        else:
            self.active_cells.discard((x, y))
            self.sleeping_cells.discard((x, y))
            self.sleep_counter[idx] = 0
            # Чанк остается активным, если в нем есть другие активные клетки
            chunk_x, chunk_y = x // self.chunk_size, y // self.chunk_size
            # Проверяем, есть ли еще активные клетки в чанке
            chunk_active = False
            for cx in range(chunk_x * self.chunk_size, min((chunk_x + 1) * self.chunk_size, self.width)):
                for cy in range(chunk_y * self.chunk_size, min((chunk_y + 1) * self.chunk_size, self.height)):
                    if (cx, cy) in self.active_cells:
                        chunk_active = True
                        break
                if chunk_active:
                    break
            if not chunk_active:
                self.active_chunks.discard((chunk_x, chunk_y))
    
    def swap(self, x1: int, y1: int, x2: int, y2: int) -> bool:
        """
        Меняет местами материалы в двух позициях.
        
        Args:
            x1, y1: Координаты первой клетки
            x2, y2: Координаты второй клетки
            
        Returns:
            True если обмен выполнен успешно
        """
        if not (self.is_valid(x1, y1) and self.is_valid(x2, y2)):
            return False
        
        idx1 = self._index(x1, y1)
        idx2 = self._index(x2, y2)
        
        # Обмен материалами
        self.mat[idx1], self.mat[idx2] = self.mat[idx2], self.mat[idx1]
        # Обмен жизнями
        self.life[idx1], self.life[idx2] = self.life[idx2], self.life[idx1]
        # Обмен счетчиками сна (при обмене частицы просыпаются)
        self.sleep_counter[idx1] = 0
        self.sleep_counter[idx2] = 0
        
        # Обновление активных клеток и чанков
        for x, y, idx in [(x1, y1, idx1), (x2, y2, idx2)]:
            if self.mat[idx] != Material.EMPTY:
                self.active_cells.add((x, y))
                self.sleeping_cells.discard((x, y))  # Разбудим при движении
                # Будим соседей (как в Noita - движение частицы будит окружающие)
                self.wake_cell(x, y)
                chunk_x, chunk_y = x // self.chunk_size, y // self.chunk_size
                self.active_chunks.add((chunk_x, chunk_y))
            else:
                self.active_cells.discard((x, y))
                self.sleeping_cells.discard((x, y))
                self.sleep_counter[idx] = 0
        
        return True
    
    def is_updated(self, x: int, y: int) -> bool:
        """
        Проверяет, была ли клетка обновлена в текущем тике.
        
        Args:
            x: X координата
            y: Y координата
            
        Returns:
            True если клетка уже обновлена
        """
        if not self.is_valid(x, y):
            return True  # Границы всегда "обновлены"
        
        idx = self._index(x, y)
        return self.update_mask[idx] == self.current_tick
    
    def mark_updated(self, x: int, y: int) -> None:
        """
        Помечает клетку как обновленную в текущем тике.
        
        Args:
            x: X координата
            y: Y координата
        """
        if not self.is_valid(x, y):
            return
        
        idx = self._index(x, y)
        self.update_mask[idx] = self.current_tick
    
    def start_tick(self) -> None:
        """Начинает новый тик симуляции."""
        self.current_tick += 1
        
        # Обновляем счетчики "сна" для неподвижных частиц (как в Noita)
        # Это позволяет пропускать обновление статичных частиц
        for x, y in list(self.active_cells):
            idx = self._index(x, y)
            mat_val = self.mat[idx]
            
            # Статичные материалы (WALL, WOOD) всегда "спят"
            if mat_val in (Material.WALL.value, Material.WOOD.value):
                if (x, y) not in self.sleeping_cells:
                    self.sleeping_cells.add((x, y))
                continue
            
            # Материалы с таймерами жизни (FIRE, SMOKE, STEAM, EMBER, LAVA, GAS)
            # НИКОГДА не должны засыпать, так как их нужно обновлять каждый тик
            # для уменьшения таймера жизни
            from falling_sand.materials import MATERIAL_PROPERTIES
            mat_props = MATERIAL_PROPERTIES.get(Material(mat_val), {})
            if mat_props.get('has_life', False):
                # Разбудим материалы с таймерами жизни
                self.sleeping_cells.discard((x, y))
                self.sleep_counter[idx] = 0
                continue
            
            # Для движущихся материалов увеличиваем счетчик неподвижности
            # Если частица не двигалась несколько тиков - помечаем как "спящую"
            if (x, y) not in self.sleeping_cells:
                self.sleep_counter[idx] += 1
                if self.sleep_counter[idx] >= self.SLEEP_THRESHOLD:
                    self.sleeping_cells.add((x, y))
    
    def wake_cell(self, x: int, y: int) -> None:
        """
        "Будит" клетку и её соседей (как в Noita - соседи просыпаются при движении).
        
        Args:
            x, y: Координаты клетки
        """
        if not self.is_valid(x, y):
            return
        
        idx = self._index(x, y)
        self.sleep_counter[idx] = 0
        self.sleeping_cells.discard((x, y))
        
        # Будим соседей (как в Noita - движение частицы будит окружающие)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if self.is_valid(nx, ny):
                nidx = self._index(nx, ny)
                if (nx, ny) in self.sleeping_cells:
                    self.sleep_counter[nidx] = max(0, self.sleep_counter[nidx] - 1)
                    if self.sleep_counter[nidx] < self.SLEEP_THRESHOLD:
                        self.sleeping_cells.discard((nx, ny))
    
    def clear(self) -> None:
        """Очищает весь мир."""
        for i in range(self.size):
            self.mat[i] = Material.EMPTY
            self.life[i] = 0
        
        self.active_cells.clear()
        self.sleeping_cells.clear()
        self.active_chunks.clear()
        self.current_tick = 0
        # Очищаем счетчики сна
        for i in range(self.size):
            self.sleep_counter[i] = 0
    
    def get_changed_cells(self, last_state: dict) -> set:
        """
        Возвращает множество клеток, которые изменились с последнего состояния.
        
        Args:
            last_state: Словарь {(x, y): mat_value} предыдущего состояния
            
        Returns:
            Множество координат измененных клеток
        """
        changed = set()
        current_state = {}
        
        for x, y in self.active_cells:
            idx = self._index(x, y)
            mat_val = self.mat[idx]
            current_state[(x, y)] = mat_val
            
            if (x, y) not in last_state or last_state[(x, y)] != mat_val:
                changed.add((x, y))
        
        # Проверяем клетки, которые были активными, но теперь пустые
        for (x, y), old_val in last_state.items():
            if (x, y) not in current_state:
                changed.add((x, y))
        
        return changed

