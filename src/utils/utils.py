import math
import arcade

def get_angle_between_two_points(a, b):
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return math.degrees(math.atan2(dy, dx))

def convert_viewport_position_to_global_position(x, y):
    window = arcade.get_window()
    left, right, bottom, top = window.get_viewport()

    screen_width = window.SCREEN_WIDTH
    screen_height = window.SCREEN_HEIGHT

    x_ratio = screen_width / (right - left)
    y_ratio = screen_height / (top - bottom)

    global_x = x / x_ratio + left
    global_y = y / y_ratio + bottom

    return global_x, global_y