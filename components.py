from abc import ABC, abstractmethod
from typing import Tuple, Dict
from elements import *
from dataclasses import dataclass


class Component(ABC):
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

    @abstractmethod
    def set_bounds(self, x: int, y: int, width: int, height: int):
        """Set the bounds of the element."""
        pass
    
    @abstractmethod
    def create_element(self) -> list[Element]:
        """Create and return an Element representation of this component."""
        pass

class MatrixComponent(Component):
    def __init__(self, matrix: Matrix):
        self.matrix = matrix
        self._size = (matrix.width, matrix.height)

    @property
    def y(self):
        return self.matrix.x

    @property
    def x(self):
        return self.matrix.y

    @property
    def width(self):
        return self.matrix.width
    
    @property
    def height(self):
        return self.matrix.height

    def set_bounds(self, x: int, y: int, width: int, height: int):
        self.matrix.raw_x = x
        self.matrix.raw_y = y
        self._size = (width, height)

    def create_element(self) -> list[Element]:
        return [self.matrix]

# Пересечение границ для стилей рамки
TOP = 0b0001
BOTTOM = 0b0010
LEFT = 0b0100
RIGHT = 0b1000

@dataclass
class BorderStyle:
    def __init__(self, h: str, v: str, corners: Dict[int, str], color = (0, 0, 0)):
        self.horizontal = h
        self.vertical = v
        self.corners = corners
        self.color = color


VERY_SIMPLE_STYLE = BorderStyle(
    h="═",
    v="║",
    corners={
        TOP | LEFT: "╔",
        TOP | RIGHT: "╗",
        BOTTOM | LEFT: "╚",
        BOTTOM | RIGHT: "╝",
        TOP | BOTTOM: "═",
        LEFT | RIGHT: "║",
        TOP | LEFT | RIGHT: "╦",
        TOP | BOTTOM | LEFT: "╠",
        TOP | BOTTOM | RIGHT: "╣",
        BOTTOM | LEFT | RIGHT: "╩",
        TOP | BOTTOM | LEFT | RIGHT: "╬"
    }
)


class BoxComponent(Component):
    def __init__(self, children: Component, style: BorderStyle = VERY_SIMPLE_STYLE):
        self.children = children
        self.raw_x = children.x - 1
        self.raw_y = children.y - 1
        self.raw_width = children.width + 2
        self.raw_height = children.height + 2
        self.style = style

    def set_bounds(self, x: int, y: int, width: int, height: int):
        self.raw_x = x
        self.raw_y = y
        self.raw_width = width
        self.raw_height = height
        self.children.set_bounds(x + 1, y + 1, width - 2, height - 2)

    def create_element(self) -> list[Element]:
        border = self.style.corners[TOP | LEFT] + self.style.horizontal * (self.raw_width - 2) + self.style.corners[TOP | RIGHT] + "\n"
        for _ in range(self.raw_height - 2):
            border += self.style.vertical + " " * (self.raw_width - 2) + self.style.vertical + "\n"
        border += self.style.corners[BOTTOM | LEFT] + self.style.horizontal * (self.raw_width - 2) + self.style.corners[BOTTOM | RIGHT]
        return [
            Text(border, self.raw_x, self.raw_y, self.style.color),
            *self.children.create_element()
        ]
    
    @property
    def x(self):
        return self.raw_x
    
    @property
    def y(self):
        return self.raw_y
    
    @property
    def width(self):
        return self.raw_width
    
    @property
    def height(self):
        return self.raw_height

@dataclass
class Cell:
    children: Component
    span_x: int = 1

