"""Буфер символов для ASCII-рендеринга."""

from core.config import COLS, ROWS


class ASCIIBuffer:
    """Буфер для хранения и управления ASCII-символами на экране."""
    
    def __init__(self):
        """Инициализация пустого буфера."""
        self.clear()
    
    def clear(self) -> None:
        """Очищает буфер, заполняя его пробелами."""
        self.buffer = [[' ' for _ in range(COLS)] for _ in range(ROWS)]
    
    def put_char(self, x: int, y: int, char: str) -> bool:
        """
        Помещает символ в указанную позицию.
        
        Args:
            x: X координата (колонка)
            y: Y координата (строка)
            char: Символ для размещения (берётся первый символ строки)
            
        Returns:
            True если позиция валидна и символ размещён
        """
        if not (0 <= x < COLS and 0 <= y < ROWS):
            return False
        
        if char:
            self.buffer[y][x] = char[0]
            return True
        
        return False
    
    def put_text(self, x: int, y: int, text: str) -> None:
        """
        Помещает текст в указанную позицию (горизонтально).
        
        Args:
            x: Начальная X координата
            y: Y координата
            text: Текст для размещения
        """
        for i, char in enumerate(text):
            self.put_char(x + i, y, char)
    
    def get_char(self, x: int, y: int) -> str:
        """
        Получает символ из указанной позиции.
        
        Args:
            x: X координата
            y: Y координата
            
        Returns:
            Символ в позиции или пробел если позиция невалидна
        """
        if not (0 <= x < COLS and 0 <= y < ROWS):
            return ' '
        return self.buffer[y][x]
    
    def render_to_string(self) -> str:
        """
        Преобразует буфер в строку для вывода.
        
        Returns:
            Многострочная строка с содержимым буфера
        """
        return '\n'.join(''.join(row) for row in self.buffer)

