#! /usr/bin/env python3
# coding: utf-8
import random
import time

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


class Path:
    color = (180, 180, 180)

    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.pixels = [(self.x1, self.y1)]
        self._generate()

    def _generate(self):
        next_x = self.x1
        next_y = self.y1
        while next_x != self.x2 or next_y != self.y2:
            next_pos = self._get_next_pos(next_x, next_y, self.x2, self.y2)
            self.pixels.append(next_pos)
            next_x, next_y = next_pos

    def _get_next_pos(self, x1, y1, x2, y2):
        if x1 < x2:
            res_x = x1 + 1
        elif x1 > x2:
            res_x = x1 - 1
        else:
            res_x = x1
        if y1 < y2:
            res_y = y1 + 1
        elif y1 > y2:
            res_y = y1 - 1
        else:
            res_y = y1
        return res_x, res_y


def create_led_near(led):
    new_x = led.x + random.randint(-15, 15)
    new_y = led.y + random.randint(-15, 15)
    new_led = Led(None, new_x, new_y)
    return new_led


def get_drawdata(w, h, frame_count):
    frame = Frame()

    prev_led = Led('led_0', WIDTH / 2, HEIGHT / 2)
    frame.draw(prev_led)

    for i in range(50):
        led = create_led_near(prev_led)
        frame.draw(led)
        path = Path(prev_led.y, prev_led.x, led.y, led.x)
        frame.draw(path)
        prev_led = led

    return frame.raw


game = pixelqt.Game(get_drawdata=get_drawdata)
game.init_controls(
    'resolution', 'zoom', 'draw_each', 'save_each', 'over', 'grid',
    'gridcolor',
)
game.config['name'] = 'Light Chain'
game.config['w'] = WIDTH
game.config['h'] = HEIGHT
game.config['over'] = False
game.config['background'] = (0, 0, 0)
game.run()
