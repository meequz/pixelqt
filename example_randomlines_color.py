#! /usr/bin/env python3
# coding: utf-8
import pixelqt
import random

const_main_color = [255, 255, 255]
const_color_y = [255, 0, 0]
const_color_x = [0, 0, 255]
const_color_minus_y = [255, 255, 0]
const_color_minus_x = [0, 255, 0]


def set_antirandom_chance(k_y, k_x):
    global ar_chance_y, ar_chance_x
    ar_chance_y = [-1] + [0]*k_y + [1]
    ar_chance_x = [-1] + [0]*k_x + [1]

def get_mix_color(from_color, to_color, share):
    share = share % 1
    res_color = []
    for i in range(3):
        channel_diff = from_color[i] - to_color[i]
        res_channel = from_color[i] + int(channel_diff * share)
        res_color.append(res_channel)
    return res_color

def get_drawdata(w, h, frame_count):
    global line
    
    if frame_count == 0:
        line = Line(w)
        set_antirandom_chance(line_game.own_params['Antirandom chance by y'],
                              line_game.own_params['Antirandom chance by x'])
    else:
        line.dist = line_game.own_params['Distance']
        
        line.make_shift()
        line.colorize()
        line.move_down(frame_count)
    
    res = line.get_dict()
    return res


class Pixel():
    def __init__(self, i):
        self.i = i
        self.basic = True
        self.shift_y = 0
        self.shift_x = 0
        self.color = [255, 255, 255]
        self.color_y = [255, 255, 255]
        self.color_x = [255, 255, 255]
        self.compute_coords()
        self.real_coords = self.coords.copy()
    
    def make_shift(self):
        self.shift_y += random.choice(ar_chance_y)
        self.shift_x += random.choice(ar_chance_x)
        self.compute_coords()
    
    def colorize(self):
        # color by y
        if self.shift_y > 0:
            self.color_y = get_mix_color(const_main_color,
                                         const_color_y,
                                         self.shift_y/100)
        if self.shift_y < 0:
            self.color_y = get_mix_color(const_main_color,
                                         const_color_minus_y,
                                         self.shift_y/100)
        # color by x
        if self.shift_x > 0:
            self.color_x = get_mix_color(const_main_color,
                                         const_color_x,
                                         self.shift_x/100)
        if self.shift_x < 0:
            self.color_x = get_mix_color(const_main_color,
                                         const_color_minus_x,
                                         self.shift_x/100)
        # mean color
        self.color = get_mix_color(self.color_y, self.color_x, 0.5)
    
    def compute_coords(self):
        self.coords = [self.shift_y, self.i + self.shift_x]


class Line():
    def __init__(self, w):
        self.w = w
        self.pixels = []
        for i in range(w):
            self.pixels.append(Pixel(i))
    
    def make_shift(self):
        for pix in self.pixels:
            pix.make_shift()
    
    def colorize(self):
        for pix in self.pixels:
            pix.colorize()
    
    def move_down(self, frame_i):
        for pix in self.pixels:
            pix.real_coords = [frame_i * self.dist + pix.coords[0], pix.coords[1]]
    
    def get_dict(self):
        res = {}
        for pix in self.pixels:
            res[tuple(pix.real_coords)] = pix.color
        return res
    

line_game = pixelqt.Game(get_drawdata=get_drawdata)

line_game.config['name'] = 'Color lines with random shift'
line_game.config['w'] = 400
line_game.config['h'] = 800
line_game.config['zoom'] = 1
line_game.config['save_each'] = 1
line_game.config['over'] = True

line_game.init_controls('resolution', 'zoom', 'draw_each', 'over')

line_game.add_own_num(name='Distance', default=6, need_to_restart=False, minimum=1, maximum=20, step=1)
line_game.add_own_num(name='Antirandom chance by x', default=32, need_to_restart=True, minimum=1, maximum=99, step=1)
line_game.add_own_num(name='Antirandom chance by y', default=32, need_to_restart=True, minimum=1, maximum=99, step=1)

line_game.run()
