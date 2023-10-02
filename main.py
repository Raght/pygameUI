import pygame
import ui
from ui import Direction, Color
from ui import Vector2



SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_SIZE = Vector2(SCREEN_WIDTH, SCREEN_HEIGHT)

clock = pygame.time.Clock()
FRAMES_PER_SECOND = 70

sc = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

mouse = ui.Mouse()




ui_box_elements_idle_style = ui.UIBoxElementStyle(Color.BLACK, Color.CYAN, 10, Color.CYAN)

button_idle_style = ui_box_elements_idle_style
button_hovered_style = ui.UIBoxElementStyle(Color.CYAN, Color.BLACK, 10, Color.BLACK)

button_text_selected_color = ui.Pixel(255, 255, 0)

text_button_idle_style = ui.UIBoxElementStyle(None, Color.WHITE)
text_button_hovered_style = ui.UIBoxElementStyle(None, button_text_selected_color)


play_button_text = "PLAY"
text_button = ui.TextButton(SCREEN_SIZE / 2,
                            text_button_idle_style, text_button_hovered_style,
                            play_button_text, ui.default_ui_font, True,
                            ui.null_function)


triangle_button = ui.TriangleButton(SCREEN_SIZE / 2, SCREEN_SIZE / 2,
                                    button_idle_style, button_hovered_style, Vector2(1, 1), 0, False,
                                    ui.null_function)


ui_context = ui.UIContext(2)

ui_context.back_layer().add_element(triangle_button)
ui_context.front_layer().add_element(text_button)

delta_time = 0

if __name__ == "__main__":
    while True:
        sc.fill(Color.BLACK)

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        mouse.update_state()
        mouse_position = mouse.get_position()
        mouse_pressed = mouse.get_pressed()

        ui_context.update_state(mouse_position, mouse_pressed, delta_time)
        ui_context.draw_elements(sc)

        pygame.display.update()
        delta_time = clock.get_time() / 1000
        clock.tick(FRAMES_PER_SECOND)

