#! /usr/bin/env python3
# coding: utf-8
import pixelqt
import random


class RandLinesCol:
    def __init__(self):
        self.main_color = [0, 0, 0]
        self.color_y = [0, 255, 0]
        self.color_x = [0, 0, 255]
    
    def set_antirandom_chance(self, k_y, k_x):
        self.ar_chance_y = [-1] + [0]*k_y + [1]
        self.ar_chance_x = [-1] + [0]*k_x + [1]
    
    def apply_instant_params(self, frame_count):
        self.line_i = frame_count
        self.dist = rlc_game.own_params['Distance']
    
    def apply_restart_params(self):
        self.set_antirandom_chance(rlc_game.own_params['Antirandom chance by y'],
                                   rlc_game.own_params['Antirandom chance by x'])
    
    def generate_first_line(self):
        self.line = [[0, i] for i in range(self.w)]
        return self.line
    
    def generate_first_line_colors(self):
        self.line_colors = [self.main_color] * self.w
        return self.line_colors
    
    def make_shift(self, current_shift):
        rand_y = current_shift[0] + random.choice(self.ar_chance_y)
        rand_x = current_shift[1] + random.choice(self.ar_chance_x)
        return [rand_y, rand_x]
    
    def get_color(self, shift):
        res_colors = []
        for sh_i, sh in enumerate(shift):
            end_color = (self.color_y, self.color_x)[sh_i]
            res_color = []
            for i in range(3):
                # calculate color
                channel_diff = self.main_color[i] - end_color[i]
                degree = (sh % 64) / 64
                res_channel = self.main_color[i] + int(channel_diff * degree)
                res_color.append(res_channel)
            res_colors.append(res_color)
        
        # calculate mean
        res = []
        for pair in zip(*res_colors):
            mean = (pair[0] + pair[1]) // 2
            res.append(mean)
        return res
    
    def get_connect(self, shift_0, shift_1):
        y = (shift_0[0] - shift_1[0]) // 2
        x = (shift_0[1] - shift_1[1]) // 2
        if y not in (shift_0[0], shift_1[0]) and \
           x not in (shift_0[1], shift_1[1]):
            return [y, x]
    
    def generate_next_line(self, prev_line):
        self.line = []
        # make shift
        for prev_item in prev_line:
            shift = self.make_shift(prev_item)
            self.line.append(shift)
        
        # fill spaces
        for i, item in enumerate(self.line):
            try:
                next_item = self.line[i+1]
            except IndexError:
                break
            connect = self.get_connect(item, next_item)
            if connect:
                self.line.insert(i+1, connect)
        return self.line
    
    def generate_next_line_colors(self):
        # colorize each item according to shift
        for shift in self.line:
            color = self.get_color(shift)
            self.line_colors.append(color)
        return self.line_colors
    
    def line_to_coordinates(self, line, line_i):
        sum_dist = line_i * self.dist
        for item in line:
            item[0] += sum_dist     # add sum distance to heigth
        return line
    
    def get_frame(self, is_first):
        if is_first:
            line = self.generate_first_line()
            line_colors = self.generate_first_line_colors()
        else:
            line = self.generate_next_line(self.prev_line)
            line_colors = self.generate_next_line_colors()
        
        self.prev_line = line
        real_line = self.line_to_coordinates(line, self.line_i)
        
        res = {}
        for i, coords in enumerate(real_line):
            res[tuple(coords)] = line_colors[i]
        return res
    
    def get_drawdata(self, w, h, frame_count):
        if frame_count == 0:
            self.w, self.h = w, h
            self.apply_restart_params()
            is_first = True
        else:
            is_first = False
        
        self.apply_instant_params(frame_count)
        res = self.get_frame(is_first)
        return res



rlc = RandLinesCol()
rlc_game = pixelqt.Game(get_drawdata=rlc.get_drawdata)

rlc_game.config['name'] = 'Color lines with random'
rlc_game.config['w'] = 400
rlc_game.config['h'] = 400
rlc_game.config['zoom'] = 1
rlc_game.config['save_each'] = 1
rlc_game.config['over'] = True

rlc_game.init_controls('resolution', 'zoom', 'draw_each')

rlc_game.add_own_num(name='Distance', default=16, need_to_restart=False, minimum=1, maximum=20, step=1)
rlc_game.add_own_num(name='Antirandom chance by x', default=32, need_to_restart=True, minimum=1, maximum=99, step=1)
rlc_game.add_own_num(name='Antirandom chance by y', default=32, need_to_restart=True, minimum=1, maximum=99, step=1)

rlc_game.run()
