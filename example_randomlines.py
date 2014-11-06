#! /usr/bin/env python3
# coding: utf-8
import pixelqt
import random


class RandomLines():
    def restart(self):
        self.line = []
        self.lines = []
        self.matrix = [[0]*self.w for x in range(self.h)]
        self.line = [0]*self.w
    
    def gen_line(self):
        prev_line = self.line[:]
        self.line = []
        if len(prev_line) < self.w:
            return
        
        # generate base line
        if max(prev_line) < self.h:
            for col_i in range(self.w):
                rand = random.choice((-1,0,1))
                line_i = prev_line[col_i] + self.dist + rand
                
                try:
                    self.matrix[line_i][col_i] = 1
                except IndexError:
                    return
                
                self.line.append(line_i)
            self.lines.append(self.line)
        # if end, repeat result
        else:
            return
        
        # fill the spaces
        if self.connect:
            for col_i, line_item in enumerate(self.line):
                try:
                    next_line_item = self.line[col_i+1]
                except IndexError:
                    break
                if abs(line_item - next_line_item) >= 2:
                    minimax = sorted((line_item, next_line_item))
                    for line_i in range(minimax[0]+1, minimax[1]):
                        self.matrix[line_i][col_i] = 1


def get_drawdata(w, h, frame_count):
    randomlines.dist = mygame.own_params['Distance']
    randomlines.connect = mygame.own_params['Connect dotes']
    
    if frame_count == 0:
        randomlines.w, randomlines.h = w, h
        randomlines.restart()
    else:
        randomlines.gen_line()
    
    res = {}
    for line in range(h):
        for col in range(w):
            if randomlines.matrix[line][col]:
                res[(line, col)] = (255,255,255)
    
    return res


randomlines = RandomLines()
mygame = pixelqt.Game(get_drawdata=get_drawdata)
mygame.config['w'] = 800
mygame.config['h'] = 2000
mygame.config['zoom'] = 1
mygame.init_controls('resolution', 'zoom', 'background', 'grid', 'invert_colors', 'draw_each', 'save_each')
mygame.add_own_num(name='Distance', default=14, need_to_restart=False, minimum=1, maximum=20, step=1)
mygame.add_own_bool(name='Connect dotes', default=False, need_to_restart=False)
mygame.run()
