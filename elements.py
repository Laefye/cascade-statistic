from abc import ABC, abstractmethod
from typing import Tuple


class Element(ABC):
    @property
    @abstractmethod
    def x(self):
        """X coordinate of the element."""
        pass

    @property
    @abstractmethod
    def y(self):
        """Y coordinate of the element."""
        pass

    @property
    @abstractmethod
    def width(self):
        """Width of the element."""
        pass

    @property
    @abstractmethod
    def height(self):
        """Height of the element."""
        pass

class Character:
    def __init__(self, char: str, color: Tuple[int, int, int] = (0, 0, 0)):
        self.char = char
        self.color = color

    def __repr__(self):
        return f"Character(char={self.char!r}, color={self.color!r})"

class Matrix(Element):
    def __init__(self, matrix: list[list[Character]], x: int, y: int):
        self.matrix = matrix
        self.raw_x = x
        self.raw_y = y

    @property
    def x(self):
        return self.raw_x
    
    @property
    def y(self):
        return self.raw_y
    
    @property
    def width(self):
        return max(len(row) for row in self.matrix) if self.matrix else 0
    
    @property
    def height(self):
        return len(self.matrix) if self.matrix else 0


class Text(Matrix):
    def __init__(self, text: str, x: int, y: int, color: Tuple[int, int, int] = (0, 0, 0)):
        matrix = [[Character(char, color) for char in line] for line in text.splitlines()]
        super().__init__(matrix, x, y)
    
    def __repr__(self):
        return f"Text(text={self.matrix!r}, x={self.x}, y={self.y})"
