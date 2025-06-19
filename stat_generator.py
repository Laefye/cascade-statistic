from PIL import ImageFont, ImageDraw, Image
from PIL.ImageFont import FreeTypeFont as Th
from elements import *
from components import MatrixComponent, BoxComponent
from typing import List
from datetime import datetime

def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert a hex color string to an RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

BG_COLOR = hex_to_rgb('#1E1E1E')
DEFAULT_TEXT_COLOR = hex_to_rgb('#9D9D9D')
GREEN_TEXT_COLOR = hex_to_rgb('#5CB798')

class Renderer:
    def __init__(self, bg_color=(255, 255, 255), font_path="FiraCode.ttf", font_size=24):
        self.bg_color = bg_color
        self.font = ImageFont.truetype(font_path, font_size)
        self.const_size = (15, 35)
        self.padding = (15, 15)

    def draw_element(self, element: Element, draw: ImageDraw.ImageDraw = None):
        x, y = element.x, element.y
    
        if isinstance(element, Matrix):
            for i, row in enumerate(element.matrix):
                for j, char in enumerate(row):
                    if char:
                        draw.text(
                            (x * self.const_size[0] + j * self.const_size[0] + self.padding[0], y * self.const_size[1] + i * self.const_size[1] + self.padding[1]),
                            char.char,
                            fill=char.color,
                            font=self.font
                        )

    def render(self, elements: List[Element]):
        width = max(element.x + element.width for element in elements) * self.const_size[0] + self.padding[0] * 2
        height = max(element.y + element.height for element in elements) * self.const_size[1] + self.padding[1] * 2
        image = Image.new("RGB", (width, height), self.bg_color)
        draw = ImageDraw.Draw(image)
        for element in elements:
            self.draw_element(element, draw)
        return image


def generate_stats(username: str, display_name: str, count_messages: int = 0, time_in_voice_seconds: int = 0) -> Image:
    # Пример использования Renderer:
    first_line = MatrixComponent(Text(f"{username}@cascade ~$ cat /var/stats/{username}.txt", 0, 0, DEFAULT_TEXT_COLOR))
    for i in range(len(username)):
        first_line.matrix.matrix[0][i].color = GREEN_TEXT_COLOR
    for i in range(len(username) + 1, len(username) + 1 + 7):
        first_line.matrix.matrix[0][i].color = GREEN_TEXT_COLOR

    stats = '\n'.join([
        f"Имя: {display_name}",
        "",
        f"Количество сообщений: {count_messages}",
        f"Время в голосе: {time_in_voice_seconds // 3600}ч {time_in_voice_seconds % 3600 // 60}м {time_in_voice_seconds % 60}с",
        "",
        f"Дата статистики: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    ])

    box = BoxComponent(MatrixComponent(Text(stats, 0, 0, DEFAULT_TEXT_COLOR)))
    box.style.color = DEFAULT_TEXT_COLOR
    box.set_bounds(0, 1, box.width, box.height)

    renderer = Renderer(bg_color=BG_COLOR)
    image = renderer.render([*first_line.create_element(), *box.create_element()])
    return image

def generate_top_by_messages(username: str, users: List[tuple[str, int]], top_n: int = 10) -> Image:
    """Generate an image with the top users by message count."""

    first_line = MatrixComponent(Text(f"{username}@cascade ~$ cat /var/stats/top/messages.txt", 0, 0, DEFAULT_TEXT_COLOR))
    for i in range(len(username)):
        first_line.matrix.matrix[0][i].color = GREEN_TEXT_COLOR
    for i in range(len(username) + 1, len(username) + 1 + 7):
        first_line.matrix.matrix[0][i].color = GREEN_TEXT_COLOR

    users = sorted(users, key=lambda x: x[1], reverse=True)[:top_n]
    lines = [f"{i + 1}. {user[0]} - {user[1]} сообщений" for i, user in enumerate(users)]
    text = "\n".join([*lines])

    matrix = MatrixComponent(Text(text, 0, 0, DEFAULT_TEXT_COLOR))
    box = BoxComponent(matrix)
    box.style.color = DEFAULT_TEXT_COLOR
    box.set_bounds(0, 1, box.width, box.height)

    renderer = Renderer(bg_color=BG_COLOR)
    image = renderer.render([*first_line.create_element(), *box.create_element()])
    return image

def generate_top_by_voice(username: str, users: List[tuple[str, int]], top_n: int = 10) -> Image:
    """Generate an image with the top users by voice time."""

    first_line = MatrixComponent(Text(f"{username}@cascade ~$ cat /var/stats/top/voice.txt", 0, 0, DEFAULT_TEXT_COLOR))
    for i in range(len(username)):
        first_line.matrix.matrix[0][i].color = GREEN_TEXT_COLOR
    for i in range(len(username) + 1, len(username) + 1 + 7):
        first_line.matrix.matrix[0][i].color = GREEN_TEXT_COLOR

    users = sorted(users, key=lambda x: x[1], reverse=True)[:top_n]
    lines = [f"{i + 1}. {user[0]} - {user[1] // 3600}ч {user[1] % 3600 // 60}м {user[1] % 60}с" for i, user in enumerate(users)]
    text = "\n".join([*lines])

    matrix = MatrixComponent(Text(text, 0, 0, DEFAULT_TEXT_COLOR))
    box = BoxComponent(matrix)
    box.style.color = DEFAULT_TEXT_COLOR
    box.set_bounds(0, 1, box.width, box.height)

    renderer = Renderer(bg_color=BG_COLOR)
    image = renderer.render([*first_line.create_element(), *box.create_element()])
    return image
