#! /usr/bin/env python3
# coding: utf-8
import pixelqt
import random


class RandLinesCol:
    def __init__(self):
        self.main_color = (255,255,255)
        self.color_x = (0,0,255)
        self.color_y = (255,130,0)
    
    def set_antirandom_chance(self, k_y, k_x):
        self.ar_chance_y = [-1] + [0]*k_y + [1]
        self.ar_chance_x = [-1] + [0]*k_x + [1]
    
    def generate_first_line(self):
        self.line = [(0, 0)] * self.w
        res = {item: self.main_color for item in self.line}
        return res
    
    def make_shift(self, current_shift):
        rand_y = random.choice(self.ar_chance_y)
        rand_x = random.choice(self.ar_chance_x)
        return (rand_y, rand_x)
    
    def get_color(self, shift):
        ...
    
    def get_connect(self, shift_0, shift_1):
        ...
    
    def generate_next_line(self, prev_line):
        self.line = []
        # make shift
        for prev_item in prev_line:
            shift = self.make_shift(prev_item)
            self.line.append(shift)
        
        # fill spaces
        
        # colorize each item according to shift
        for shift in self.line:
            color = self.get_color(shift)
        
        self.line = ...
        return self.line
    
    def line_to_coordinates(self, line, line_i):
        sum_dist = line_i * self.dist
        for item in line:
            item[0] += sum_dist     # add sum distance to heigth
        return line
    
    def apply_instant_params(self):
        self.dist = mygame.own_params['Distance']
    
    def apply_restart_params(self):
        randomlines.set_antirandom_chance(mygame.own_params['Antirandom chance by y'],
                                          mygame.own_params['Antirandom chance by x'])
    
    def get_drawdata(self, w, h, frame_count):
        self.apply_instant_params()
        if frame_count == 0:
            self.w, self.h = w, h
            self.apply_restart_params()
            res = self.generate_first_line()
        else:
            line = self.generate_next_line(self.line)
            res = self.line_to_coordinates(line, frame_count)
        return res



rlc = RandLinesCol()
mygame = pixelqt.Game(get_drawdata=rlc.get_drawdata)

mygame.config['name'] = 'Color lines with random'
mygame.config['w'] = 800
mygame.config['h'] = 2000
mygame.config['zoom'] = 1

mygame.init_controls('resolution', 'zoom', 'draw_each')

mygame.add_own_num(name='Distance', default=16, need_to_restart=False, minimum=1, maximum=20, step=1)
mygame.add_own_num(name='Antirandom chance by x', default=32, need_to_restart=True, minimum=1, maximum=99, step=1)
mygame.add_own_num(name='Antirandom chance by y', default=32, need_to_restart=True, minimum=1, maximum=99, step=1)

mygame.run()
