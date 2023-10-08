import pygame
import ui
import math
from ui import Direction, Color
from ui import Vector2



SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_SIZE = Vector2(SCREEN_WIDTH, SCREEN_HEIGHT)

clock = pygame.time.Clock()
FRAMES_PER_SECOND = 70

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

mouse = ui.Mouse()


function_x_to_y = lambda x: math.sin(x)
function_y_to_x = lambda y: math.asin(y)


min_screen_side = min(SCREEN_WIDTH, SCREEN_HEIGHT)
max_screen_side = max(SCREEN_WIDTH, SCREEN_HEIGHT)

window_function_style = ui.UIBoxElementStyle(None, None, 1, Color.GREEN)
window_function = ui.Box(SCREEN_SIZE / 2, Vector2(min_screen_side, min_screen_side) / 2, window_function_style)


class RangeFloat:
    def __init__(self, start, stop, step: float = 1.0):
        self.start = start
        self.stop = stop
        self.step = step
        self._value = start

    def __iter__(self):
        while self._value < self.stop:
            yield self._value
            self._value += self.step


class FunctionRange:
    def __init__(self, start, stop):
        self.start = start
        self.stop = stop

    @property
    def length(self):
        return abs(self.stop - self.start)

function_range_x = FunctionRange(-math.pi / 2, math.pi / 2)
function_range_y = FunctionRange(-1, 1)
function_range_x_span = function_range_x.stop - function_range_x.start
function_range_y_span = function_range_y.stop - function_range_y.start

previous_point_x = (function_range_x.stop + function_range_x.start) / 2
previous_point_y = (function_range_y.stop + function_range_y.start) / 2
point_x = ui.Reference((function_range_x.stop + function_range_x.start) / 2)
point_y = ui.Reference((function_range_y.stop + function_range_y.start) / 2)

SALAD_COLOR = ui.Pixel(90, 198, 67)

slider_style = ui.UIBoxElementStyle(Color.GREEN, None, 0, None)
knob_style = ui.UIBoxElementStyle(Color.GREEN, None, 5, SALAD_COLOR)

window_to_slider_gap = 25

slider_x = ui.Slider(window_function.position_bottom_left_corner + Vector2(window_function.size.x / 2, window_to_slider_gap), window_function.size.x, False,
                     slider_style, knob_style,
                     point_x,
                     ui.SliderValue(function_range_x.stop, str(function_range_x.start)),
                     ui.SliderValue(function_range_x.start, str(function_range_x.stop)),
                     point_x.value,
                     [],
                     ui.default_ui_font, ui.null_function)
slider_y = ui.Slider(window_function.position_up_left_corner + Vector2(-window_to_slider_gap, window_function.size.y / 2), window_function.size.y * function_range_y_span / function_range_x_span, True,
                     slider_style, knob_style,
                     point_y,
                     ui.SliderValue(function_range_y.start, str(function_range_y.start)),
                     ui.SliderValue(function_range_y.stop, str(function_range_y.stop)),
                     point_y.value,
                     [],
                     ui.default_ui_font, ui.null_function)

ui_context = ui.UIContext(2)

ui_context.back_layer().add_element(window_function)
ui_context.front_layer().add_element(slider_x)
ui_context.front_layer().add_element(slider_y)

#slider_x = ui.Slider()
#slider_y = ui.Slider()
#
#ui_context.front_layer().add_element(slider_x)
#ui_context.front_layer().add_element(slider_y)

delta_time = 0

EPSILON = 10 ** (-6)


def approximately_equal(x, y):
    return abs(y - x) < EPSILON


if __name__ == "__main__":
    while True:
        screen.fill(Color.BLACK)

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        mouse.update_state()
        mouse_position = mouse.get_position()
        mouse_pressed = mouse.get_pressed()

        previous_point_x = point_x.value
        previous_point_y = point_y.value

        ui_context.update_state(mouse_position, mouse_pressed, delta_time)
        ui_context.draw_elements(screen)

        if approximately_equal(point_x.value, previous_point_x):
            point_x.value = function_y_to_x(point_y.value)
        elif approximately_equal(point_y.value, previous_point_y):
            point_y.value = function_x_to_y(point_x.value)

        counter = 0
        previous_point = None
        for x in RangeFloat(function_range_x.start, function_range_x.stop, function_range_x.length / window_function.size.x):
            y = function_x_to_y(x)

            counter += 1
            screen_dx = (x - function_range_x.start) / function_range_x.length * slider_x.length
            screen_dy = y / function_range_y.length * slider_y.length
            screen_point_position = window_function.position_up_left_corner + Vector2(0, window_function.size.y / 2) + Vector2(screen_dx, -screen_dy)

            if previous_point is None:
                pygame.draw.circle(screen, Color.GREEN, screen_point_position, 2)
            else:
                pygame.draw.line(screen, Color.GREEN, previous_point, screen_point_position)

            previous_point = screen_point_position

        ui.draw_text(screen, Vector2(0, 0), str(point_x.value), Color.GREEN, )
        ui.draw_text(screen, Vector2(0, ui.default_ui_font.size("A")[1]), str(point_y.value), Color.GREEN, )

        pygame.draw.line(screen, Color.GREEN,
                         Vector2(slider_x.knob_box.position.x, window_function.position_bottom_left_corner.y),
                         Vector2(slider_x.knob_box.position.x, slider_y.knob_box.position.y)
                         )
        pygame.draw.line(screen, Color.GREEN,
                         Vector2(window_function.position_bottom_left_corner.x, slider_y.knob_box.position.y),
                         Vector2(slider_x.knob_box.position.x, slider_y.knob_box.position.y)
                         )

        pygame.draw.circle(screen, Color.RED, Vector2(slider_x.knob_box.position.x, slider_y.knob_box.position.y), 5)

        pygame.display.update()
        delta_time = clock.get_time() / 1000
        clock.tick(FRAMES_PER_SECOND)

