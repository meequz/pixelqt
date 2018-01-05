#! /usr/bin/env python3
# coding: utf-8
import random

import pixelqt


WIDTH = 320
HEIGHT = 240
OBJS = {}

PREV_PATH_POS = ()


class Led:

    def __init__(self, name=None, x=None, y=None):
        self._name = name
        self.x = x or random.randint(0, WIDTH)
        self.y = y or random.randint(0, HEIGHT)
        self.init_random_color()
        OBJS[self.name] = self

    def init_random_color(self):
        self.r = random.randint(40, 255)
        self.g = random.randint(40, 255)
        self.b = random.randint(40, 255)

    @property
    def name(self):
        return self._name or '{}: {}'.format(self.coords, self.color)

    @property
    def coords(self):
        return (self.y, self.x)

    @property
    def color(self):
        return (self.r, self.g, self.b)

    @property
    def pixels(self):
        return (
            (self.y-1, self.x-1), (self.y-1, self.x), (self.y-1, self.x+1),
            (self.y, self.x-1), (self.y, self.x), (self.y, self.x+1),
            (self.y+1, self.x+1), (self.y+1, self.x), (self.y+1, self.x-1),
        )


class Frame:

    def __init__(self):
        self.raw = {}

    def draw(self, obj):
        for pixel in obj.pixels:
            self.raw[pixel] = obj.color


def get_next_pos_to(init_x, init_y, target_x, target_y):
    if init_x < target_x:
        res_x = init_x + 1
    elif init_x > target_x:
        res_x = init_x - 1
    else:
        res_x = init_x

    if init_y < target_y:
        res_y = init_y + 1
    elif init_y > target_y:
        res_y = init_y - 1
    else:
        res_y = init_y

    return res_x, res_y


def get_or_create_leds(frame, frame_count):
    if frame_count == 0:
        Led('led_1')
        Led('led_2')

    led_1 = OBJS['led_1']
    led_2 = OBJS['led_2']
    frame.draw(led_1)
    frame.draw(led_2)
    return led_1, led_2


def get_or_create_next_path_dot(led_1, led_2, frame, frame_count):
    global PREV_PATH_POS
    if frame_count == 0:
        PREV_PATH_POS = led_1.y, led_1.x
    PREV_PATH_POS = get_next_pos_to(
        PREV_PATH_POS[0], PREV_PATH_POS[1], led_2.y, led_2.x)
    frame.raw[PREV_PATH_POS] = (180, 180, 180)


def get_drawdata(w, h, frame_count):
    frame = Frame()
    led_1, led_2 = get_or_create_leds(frame, frame_count)
    get_or_create_next_path_dot(led_1, led_2, frame, frame_count)
    return frame.raw


game = pixelqt.Game(get_drawdata=get_drawdata)
game.init_controls(
    'resolution', 'zoom', 'draw_each', 'save_each', 'over', 'grid',
    'gridcolor',
)
game.config['name'] = 'Light Chain'
game.config['w'] = WIDTH
game.config['h'] = HEIGHT
game.config['over'] = True
game.config['background'] = (0, 0, 0)
game.run()
