import pygame
from typing import Union
from abc import ABC
from multipledispatch import dispatch
import typing
import types
import math
import warnings
from warnings import warn


pygame.init()


Vector2 = pygame.Vector2
Rectangle = pygame.Rect
Pixel = pygame.Color
Font = pygame.font.Font



class Direction:
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3


class Color:
    BLACK = Pixel(0, 0, 0)
    GREY = Pixel(127, 127, 127)
    GRAY = Pixel(127, 127, 127)
    WHITE = Pixel(255, 255, 255)
    RED = Pixel(255, 0, 0)
    GREEN = Pixel(0, 255, 0)
    BLUE = Pixel(0, 0, 255)
    YELLOW = Pixel(255, 255, 0)
    CYAN = Pixel(0, 255, 255)
    MAGENTA = Pixel(255, 0, 255)


default_ui_font = Font("fonts/NES_Font.ttf", 32)

def null_function():
    pass


def point_vs_rect(point: Union[Vector2, list[float]], rectangle: Rectangle):
    return (rectangle[0] <= point[0] <= rectangle[0] + rectangle[2] and
            rectangle[1] <= point[1] <= rectangle[1] + rectangle[3])


def rect_vs_rect(rectangle1: Rectangle, rectangle2: Rectangle):
    for i in range(4):
        rectangle1[i] = round(rectangle1[i])
    for i in range(4):
        rectangle2[i] = round(rectangle2[i])

    hitboxes = set()
    hitboxes.add((rectangle1[0], rectangle1[1]))
    hitboxes.add((rectangle1[0] + rectangle1[2], rectangle1[1]))
    hitboxes.add((rectangle1[0] + rectangle1[2], rectangle1[1] + rectangle1[3]))
    hitboxes.add((rectangle1[0], rectangle1[1] + rectangle1[3]))

    for hitbox in hitboxes:
        if point_vs_rect(hitbox, rectangle2):
            return True

    return False


def collide_float(rectangle1: Rectangle, rectangle2: Rectangle):
    hitboxes = set()
    hitboxes.add((rectangle1[0], rectangle1[1]))
    hitboxes.add((rectangle1[0] + rectangle1[2], rectangle1[1]))
    hitboxes.add((rectangle1[0] + rectangle1[2], rectangle1[1] + rectangle1[3]))
    hitboxes.add((rectangle1[0], rectangle1[1] + rectangle1[3]))

    for hitbox in hitboxes:
        if point_vs_rect(hitbox, rectangle2):
            return True

    return False


def draw_border(surface: pygame.Surface, rectangle: Rectangle, border_color: Pixel, thickness: float):
    # UP
    pygame.draw.rect(surface, border_color, [rectangle[0] - thickness, rectangle[1] - thickness,
                                             rectangle[2] + 2 * thickness, thickness])
    # DOWN
    pygame.draw.rect(surface, border_color, [rectangle[0] - thickness, rectangle[1] + rectangle[3],
                                             rectangle[2] + 2 * thickness, thickness])
    # RIGHT
    pygame.draw.rect(surface, border_color, [rectangle[0] + rectangle[2], rectangle[1],
                                             thickness, rectangle[3]])
    # LEFT
    pygame.draw.rect(surface, border_color, [rectangle[0] - thickness, rectangle[1],
                                             thickness, rectangle[3]])


def draw_rectangle(surface: pygame.Surface, rectangle: Rectangle, rectangle_color: Pixel,
                   outline: float = 0, outline_color: Pixel = None):
    if rectangle_color is not None:
        pygame.draw.rect(surface, rectangle_color, rectangle)

    if outline != 0 and outline_color is not None:
        draw_border(surface, rectangle, outline_color, outline)


def draw_rounded_border(surface: pygame.Surface, rectangle: Rectangle, border_color: Pixel, thickness: float, offset: float = 1):
    if thickness == 0:
        return
    # UP
    pygame.draw.rect(surface, border_color, [rectangle[0] - thickness + offset, rectangle[1] - thickness,
                                             rectangle[2] + 2 * thickness - offset * 2, thickness])
    # DOWN
    pygame.draw.rect(surface, border_color, [rectangle[0] - thickness + offset, rectangle[1] + rectangle[3],
                                             rectangle[2] + 2 * thickness - offset * 2, thickness])
    # RIGHT
    pygame.draw.rect(surface, border_color, [rectangle[0] + rectangle[2], rectangle[1] - thickness + offset,
                                             thickness, rectangle[3] + thickness * 2 - offset * 2])
    # LEFT
    pygame.draw.rect(surface, border_color, [rectangle[0] - thickness, rectangle[1] - thickness + 1,
                                             thickness, rectangle[3] + thickness * 2 - offset * 2])





def draw_text(surface: pygame.Surface, position_up_left_corner: Vector2, text: str, color: Pixel,
              font: Font = default_ui_font, enable_antialiasing: bool = False):
    text_surface = font.render(text, enable_antialiasing, color)
    surface.blit(text_surface, position_up_left_corner)


class Key:
    def __init__(self):
        self.previous_state = False
        self.state = False

    @property
    def pressed(self):
        return (not self.previous_state) and self.state

    @property
    def held(self):
        return self.previous_state and self.state

    @property
    def released(self):
        return self.previous_state and not self.state


class ScanHardware:
    def __init__(self, buttons):
        self._buttons = []
        for i in range(buttons):
            self._buttons.append(Key())

    @property
    def buttons(self):
        return len(self._buttons)

    # Override the method to provide the keys for hardware
    def get_keys_raw_states(self):
        return

    def update_state(self):
        keys_pressed = self.get_keys_raw_states()

        for i in range(len(self._buttons)):
            self._buttons[i].previous_state = self._buttons[i].state
            self._buttons[i].state = keys_pressed[i]

    def get_pressed(self):
        return self._buttons


class Mouse(ScanHardware):
    LEFT = 0
    MIDDLE = 1
    RIGHT = 2
    BACK = 3
    FORWARD = 4

    BUTTONS_PRESS_KEY = LEFT

    def __init__(self):
        super().__init__(5)
        self._previous_position = Vector2(0, 0)
        self._position = Vector2(0, 0)

    def get_keys_raw_states(self):
        return pygame.mouse.get_pressed(self.buttons)

    def update_state(self):
        super().update_state()
        self._previous_position = self._position
        self._position = pygame.mouse.get_pos()

    def get_position(self):
        return pygame.mouse.get_pos()

    def get_previous_position(self):
        return self._previous_position


class UIElement(ABC):
    def __init__(self):
        self._collides_with_mouse = False
        self._active = False

    def on_update(self, collides_with_mouse: bool, mouse_position: Vector2, mouse_key: Key, delta_time_seconds: float):
        pass

    def draw(self, surface):
        pass

    @property
    def collides_with_mouse(self) -> bool:
        return self._collides_with_mouse

    @property
    def active(self) -> bool:
        return self._active


class UILayer:
    def __init__(self):
        self.elements: list[UIElement] = []

    def add_element(self, element: UIElement):
        self.elements.append(element)


class UIContext:
    def __init__(self, number_of_layers: int):
        if number_of_layers < 1 or type(number_of_layers) != int:
            warnings.warn("WARNING: number_of_layers is incorrect")
        self.layers: list[UILayer()] = [UILayer() for _ in range(max(1, int(number_of_layers)))]

    def insert_front_element(self, index_of_layer: int, element: UIElement):
        self.layers[index_of_layer].insert(0, element)

    def insert_element(self, index_of_layer: int, index_of_element: int, element: UIElement):
        self.layers[index_of_layer].insert(index_of_element, element)

    def append_element(self, index_of_layer: int, element: UIElement):
        self.layers[index_of_layer].append(element)

    def layer(self, index_of_layer: int):
        return self.layers[index_of_layer]

    def front_layer(self) -> UILayer:
        return self.layers[0]

    def back_layer(self) -> UILayer:
        return self.layers[len(self.layers) - 1]

    def update_state(self, mouse_position: Vector2, mouse_keys: list[Key], delta_time_seconds: float):
        mouse_collides_with_element = False
        mouse_controls_element = False
        mouse_left_key = mouse_keys[Mouse.LEFT]
        for layer in self.layers:
            for element in layer.elements:
                element.on_update(mouse_collides_with_element, mouse_position, mouse_left_key, delta_time_seconds)
                if element.collides_with_mouse:
                    mouse_collides_with_element = True

    def draw_elements(self, surface):
        for i in range(len(self.layers) - 1, -1, -1):
            layer = self.layers[i]
            for element in layer.elements:
                element.draw(surface)


class UIBoxElementStyle:
    def __init__(self, rectangle_color: Union[Pixel, None], content_color: Union[Pixel, None],
                 outline: float = 0, outline_color: Union[Pixel, None] = None,
                 antialiasing: bool = False):
        self.rectangle_color = rectangle_color
        self.content_color = content_color
        self.outline = outline
        self.outline_color = outline_color
        self.antialiasing = antialiasing


class UIBoxElement(UIElement, ABC):
    def __init__(self, position: Vector2, size: Vector2, style: UIBoxElementStyle):
        super().__init__()

        self.position = Vector2(position[0], position[1])
        self.size = size
        self.style = style

    @property
    def position_up_left_corner(self) -> Vector2:
        return self.position - self.size / 2

    @property
    def position_up_left_corner_outline(self) -> Vector2:
        return self.position - self.size / 2 - Vector2(self.style.outline, self.style.outline)

    @property
    def rectangle(self) -> pygame.Rect:
        return pygame.Rect(self.position_up_left_corner[0], self.position_up_left_corner[1], self.size[0], self.size[1])

    @property
    def rectangle_with_outline(self) -> pygame.Rect:
        position = self.position_up_left_corner_outline
        size = self.size + 2 * Vector2(self.style.outline, self.style.outline)
        return pygame.Rect(position[0], position[1], size[0], size[1])

    def on_update(self, collides_with_mouse: bool, mouse_position: Vector2, mouse_key: Key, delta_time_seconds: float):
        self._collides_with_mouse = collides_with_mouse and point_vs_rect(mouse_position, self.rectangle_with_outline)


class Text:
    def __init__(self, position: Union[Vector2, list[float]], color: Pixel, font: Font, text: str, antialiasing: bool = False):
        self.position = Vector2(position[0], position[1])
        self.color = color
        self.font = font
        self.text = text
        self.antialiasing = antialiasing

    def draw(self, surface):
        text_surface = self.font.render(self.text, self.antialiasing, self.color)
        text_size = Vector2(self.font.size(self.text)[0], self.font.size(self.text)[1])
        text_position = self.position - text_size / 2
        surface.blit(text_surface, text_position)


class TextBox(UIBoxElement):
    def __init__(self, position: Vector2, size: Vector2,
                 style: UIBoxElementStyle,
                 text: str, font: Font = default_ui_font, antialiasing: bool = False):
        super().__init__(position, size, style)
        self.text = text
        self.font = font
        self.antialiasing = antialiasing

    def draw(self, surface):
        draw_rectangle(surface, self.rectangle, self.style.rectangle_color, self.style.outline, self.style.outline_color)

        ui_text_element = Text(self.position, self.style.content_color, self.font, self.text, self.style.antialiasing)
        ui_text_element.draw(surface)


class Button(TextBox):
    def __init__(self, position: Vector2, size: Vector2,
                 style_idle: UIBoxElementStyle, style_hovered: UIBoxElementStyle,
                 text: str, font: Font, antialiasing: bool,
                 function, *args):
        super().__init__(position, size, style_idle, text, font, antialiasing)

        self.style_idle = style_idle
        self.style_hovered = style_hovered
        self.style_pressed = style_hovered

        self.function = function
        self.arguments = args

        self._hovered = False
        self._pressed = False

    @property
    def hovered(self):
        return self._hovered

    @property
    def pressed(self):
        return self._pressed

    def on_update(self, mouse_already_collides_with_element: bool, mouse_position: Vector2, mouse_key: Key, delta_time_seconds: float):
        self._collides_with_mouse = not mouse_already_collides_with_element and point_vs_rect(mouse_position, self.rectangle)
        self._active = self.collides_with_mouse and mouse_key.pressed
        if self.active:
            self.style = self.style_pressed
        elif self.collides_with_mouse:
            self.style = self.style_hovered
        else:
            self.style = self.style_idle

        self.call_function_if_pressed()

    # Must be called after the change_state function
    def call_function_if_pressed(self):
        if self.active:
            self.function(*self.arguments)


class TextButton(Button):
    def __init__(self, position: Vector2,
                 style_idle: UIBoxElementStyle, style_hovered: UIBoxElementStyle,
                 text: str, font: Font, antialiasing: bool,
                 function, *args):
        text_size = Vector2(Font.size(font, text))
        super().__init__(position, text_size, style_idle, style_hovered, text, font, antialiasing, function, *args)


class Polygon:
    def __init__(self, position: Vector2, points: list[Vector2]):
        self.position = position
        self.points = points
        self._scale = Vector2(1, 1)

    # Rotates the polygon in SCREEN space CLOCKWISE by degrees
    def rotate(self, degrees: Union[float, int]):
        cosine = math.cos(math.radians(degrees))
        sine = math.sin(math.radians(degrees))
        for i in range(len(self.points)):
            x0, y0 = self.points[i].x, self.points[i].y
            x = x0 * cosine - y0 * sine
            y = x0 * sine + y0 * cosine
            self.points[i] = Vector2(x, y)

    def get_scale(self) -> Vector2:
        return self._scale

    def scale(self, new_scale: Vector2):
        scale = Vector2(new_scale.x / self.get_scale().x, new_scale.y / self.get_scale().y)
        for i in range(len(self.points)):
            self.points[i].x = self.position.x + (self.points[i].x - self.position.x) * scale.x
            self.points[i].y = self.position.y + (self.points[i].y - self.position.y) * scale.y
        self._scale = new_scale

    def scale_by(self, relative_scale: Vector2):
        new_scale = Vector2(relative_scale.x * self.get_scale().x, relative_scale.y * self.get_scale().y)
        self.scale(new_scale)


# A button with a triangle inside
class TriangleButton(Button):
    def __init__(self, position: Vector2, size: Vector2,
                 style_idle: UIBoxElementStyle, style_hovered: UIBoxElementStyle,
                 triangle_scale: Vector2, angle_degrees: float, antialiasing: bool,
                 function, *args):
        super().__init__(position, size, style_idle, style_hovered, "", default_ui_font, antialiasing, function, *args)
        self.triangle_scale = triangle_scale
        self.triangle_mesh = Polygon(
            Vector2(0, 0),
            [Vector2(math.cos(math.radians(angle)), math.sin(math.radians(angle))) for angle in range(0, 360, 360 // 3)]
        )
        self.triangle_mesh.scale_by(triangle_scale / math.sqrt(3))
        triangle_side = min(size.x / 3, size.y / 3)
        self.triangle_mesh.scale_by(Vector2(triangle_side, triangle_side))
        self.triangle_mesh.rotate(angle_degrees)

    def draw(self, surface):
        super().draw(surface)
        draw_rectangle(surface, self.rectangle, self.style.rectangle_color)
        draw_rounded_border(surface, self.rectangle, self.style.outline_color, self.style.outline)

        translated_triangle_mesh_points = [point + self.position for point in self.triangle_mesh.points]

        pygame.draw.polygon(surface, self.style.content_color, translated_triangle_mesh_points)
        if self.antialiasing:
            pygame.draw.aalines(surface, self.style.content_color, True, translated_triangle_mesh_points)


class Reference:
    def __init__(self, value):
        self.value = value





class Slider:
    def __init__(self, pos, sliderSize, defaultValue, minValue, maxValue):
        self.pos = pos
        self.sliderSize = sliderSize
        self.currentValue = defaultValue
        self.minValue = minValue
        self.maxValue = maxValue

        self.valuePerPixel = (self.maxValue - self.minValue) / self.pos[2]
        self.sliderMidPointX = self.pos[0] + self.pos[2] * (
                    (self.currentValue - self.minValue) / (self.maxValue - minValue))
        self.sliderPos = [self.sliderMidPointX - ceil(self.sliderSize[0] / 2),
                          self.pos[1] - ceil((self.sliderSize[1] - self.pos[3]) / 2),
                          self.sliderSize[0], self.sliderSize[1]]

        self.flag = False

    def get_value(self):
        return self.currentValue

    def mouse_input(self, mousePos, mousePressed):
        sliderMidPointX_old = self.sliderMidPointX

        if point_vs_rect(mousePos, self.sliderPos) or self.flag:
            if mousePressed:
                self.flag = True
                if self.pos[0] <= mousePos[0] <= self.pos[0] + self.pos[2]:
                    self.sliderMidPointX = mousePos[0]
                elif self.pos[0] >= mousePos[0]:
                    self.sliderMidPointX = self.pos[0]
                elif mousePos[0] >= self.pos[0] + self.pos[2]:
                    self.sliderMidPointX = self.pos[0] + self.pos[2]
            else:
                self.flag = False
        elif point_vs_rect(mousePos, self.pos):
            if mousePressed:
                self.sliderMidPointX = mousePos[0]

        self.currentValue = round(self.currentValue + (self.sliderMidPointX - sliderMidPointX_old) * self.valuePerPixel,
                                  10)

    def draw(self, surface, sliderColor, lineColor):
        pygame.draw.rect(surface, lineColor, self.pos)

        self.sliderPos[0] = self.sliderMidPointX - ceil(self.sliderSize[0] / 2)
        draw_rectangle(surface, self.sliderPos, sliderColor, lineColor, 2)
        # draw_rounded_border(surface, self.pos, lineColor, outline)
        # pygame.draw.rect(surface, sliderColor, self.sliderPos)


def _new_point(p, scale, sign1, sign2, boxSide):
    """ Internal use """
    return [p[0] + sign1 * int(scale * boxSide),
            p[1] + sign2 * int(scale * boxSide)]


def _draw_check1(self, surface, pos, checkColor):
    """ Internal use """
    p1 = [pos[0] + self.checkGap, pos[1] + self.boxSide // 2 + (0.17333 * self.boxSide - self.checkGap)]
    p2 = _new_point(p1, 0.11333, 1, -1, self.boxSide)
    p3 = _new_point(p2, 0.14667, 1, 1, self.boxSide)
    p4 = _new_point(p3, 0.36, 1, -1, self.boxSide)
    p5 = _new_point(p4, 0.11333, 1, 1, self.boxSide)
    p6 = _new_point(p5, 0.47333, -1, 1, self.boxSide)
    p6[0] = p3[0]
    pygame.draw.polygon(surface, checkColor, (p1, p2, p3, p4, p5, p6))


def _draw_check2(self, surface, pos, checkColor):
    """ Internal use """
    pygame.draw.polygon(surface, checkColor,
                        [
                            [pos[0] + self.checkGap, pos[1] + self.checkGap],
                            [pos[0] + self.checkThickness + self.checkGap, pos[1] + self.checkGap],
                            [pos[0] + self.boxSide // 2,
                             pos[1] + self.boxSide - 2 * self.checkThickness - self.checkGap],
                            [pos[0] + self.boxSide - self.checkThickness - self.checkGap, pos[1] + self.checkGap],
                            [pos[0] + self.boxSide - self.checkGap, pos[1] + self.checkGap],
                            [pos[0] + self.boxSide // 2, pos[1] + self.boxSide - self.checkGap]
                        ])


def _draw_check3(self, surface, pos, checkColor):
    """ Internal use """
    pygame.draw.polygon(surface, checkColor,
                        [
                            pos,
                            [pos[0] + self.checkThickness, pos[1]],
                            [pos[0] + self.boxSide // 2, pos[1] + self.boxSide - 2 * self.checkThickness],
                            [pos[0] + self.boxSide - self.checkThickness, pos[1]],
                            [pos[0] + self.boxSide, pos[1]],
                            [pos[0] + self.boxSide // 2, pos[1] + self.boxSide]
                        ])


def _draw_cross1(self, surface, pos, checkColor):
    """ Internal use """
    pygame.draw.polygon(surface, checkColor,
                        [
                            [pos[0] + self.checkThickness + self.checkGap, pos[1] + self.checkGap],
                            [pos[0] + self.boxSide - self.checkGap,
                             pos[1] + self.boxSide - self.checkThickness - self.checkGap],
                            [pos[0] + self.boxSide - self.checkThickness - self.checkGap,
                             pos[1] + self.boxSide - self.checkGap],
                            [pos[0] + self.checkGap, pos[1] + self.checkThickness + self.checkGap]
                        ])
    pygame.draw.polygon(surface, checkColor,
                        [
                            [pos[0] + self.boxSide - self.checkGap, pos[1] + self.checkThickness + self.checkGap],
                            [pos[0] + self.checkThickness + self.checkGap, pos[1] + self.boxSide - self.checkGap],
                            [pos[0] + self.checkGap, pos[1] + self.boxSide - self.checkThickness - self.checkGap],
                            [pos[0] + self.boxSide - self.checkThickness - self.checkGap, pos[1] + self.checkGap]
                        ])


def _draw_cross2(self, surface, pos, checkColor):
    """ Internal use """
    pygame.draw.polygon(surface, checkColor,
                        [
                            pos,
                            [pos[0] + self.checkThickness, pos[1]],
                            [pos[0] + self.boxSide, pos[1] + self.boxSide - self.checkThickness],
                            [pos[0] + self.boxSide, pos[1] + self.boxSide],
                            [pos[0] + self.boxSide - self.checkThickness, pos[1] + self.boxSide],
                            [pos[0], pos[1] + self.checkThickness]
                        ])
    pygame.draw.polygon(surface, checkColor,
                        [
                            [pos[0] + self.boxSide, pos[1]],
                            [pos[0] + self.boxSide, pos[1] + self.checkThickness],
                            [pos[0] + self.checkThickness, pos[1] + self.boxSide],
                            [pos[0], pos[1] + self.boxSide],
                            [pos[0], pos[1] + self.boxSide - self.checkThickness],
                            [pos[0] + self.boxSide - self.checkThickness, pos[1]]
                        ])


def _draw_box(self, surface, pos, checkColor):
    """ Internal use """
    pygame.draw.rect(surface, checkColor,
                     [pos[0] + self.checkGap, pos[1] + self.checkGap] +
                     [self.boxSide - 2 * self.checkGap] * 2)


def _draw_none(self, surface, pos, checkColor):
    """ Internal use """
    pass


_checkStyleInfo = {
    "check1": [_draw_check1, 0.11333, 0.13667],
    "check2": [_draw_check2, 0.12, 0.22],
    "check3": [_draw_check3, 0.10, 0],
    "cross1": [_draw_cross1, 0.07, 0.20],
    "cross2": [_draw_cross2, 0.07, 0],
    "box": [_draw_box, 0, 0.22]
}


class Checkbox:
    """
    Checkbox (Tickbox)

    Available check styles:
    "check1",
    "check2",
    "check3",
    "cross1",
    "cross2",
    "box",
    """

    def __init__(self, pos, boxSide, outlineThickness, defaultState, checkStyle):
        self.pos = list(pos)
        self.boxSide = boxSide
        self.outlineThickness = outlineThickness
        self.state = defaultState

        self.checkStyle = checkStyle
        try:
            self.draw_check = _checkStyleInfo[checkStyle][0]
            self.checkThickness = int(boxSide * _checkStyleInfo[checkStyle][1])
            self.checkGap = int(boxSide * _checkStyleInfo[checkStyle][2])
        except KeyError:
            warn("CheckStyle has not been specified")
            self.draw_check = _draw_none
            self.checkThickness = None
            self.checkGap = None

    def get_state(self):
        return self.state

    def mouse_input(self, mousePos, mousePressed):
        if point_vs_rect(mousePos, list(self.pos) + [self.boxSide] * 2) and mousePressed:
            self.state = not self.state

    def draw(self, surface, boxColor, checkColor):
        if self.outlineThickness:
            draw_border(surface, list(self.pos) + [self.boxSide] * 2, boxColor, self.outlineThickness)
        else:
            pygame.draw.rect(surface, boxColor, list(self.pos) + [self.boxSide] * 2, self.outlineThickness)

        if self.state:
            self.draw_check(self, surface, self.pos, checkColor)

    def draw_text(self, surface, textColor, font, text, place, antialiasing=0):
        textSurface = font.render(text, antialiasing, textColor)
        textPos = self.pos[:]
        if place == Direction.UP:
            textPos[0] += (self.boxSide // 2 - font.size(text)[0] // 2)
            textPos[1] -= (self.outlineThickness + font.size(text)[1] + font.size(" ")[1])
        elif place == Direction.DOWN:
            textPos[0] += (self.boxSide // 2 - font.size(text)[0] // 2)
            textPos[1] += self.boxSide + self.outlineThickness + font.size(" ")[1]
        elif place == Direction.RIGHT:
            textPos[0] += self.boxSide + self.outlineThickness + font.size(" ")[0]
            textPos[1] += (self.boxSide // 2 - font.size(text)[1] // 2)
        elif place == Direction.LEFT:
            textPos[0] -= (self.outlineThickness + font.size(text)[0] + font.size(" ")[0])
            textPos[1] += (self.boxSide // 2 - font.size(text)[1] // 2)
        surface.blit(textSurface, textPos)

    def color(self, boxColorIfTrue, boxColorIfFalse):
        if self.state:
            return boxColorIfTrue
        return boxColorIfFalse
