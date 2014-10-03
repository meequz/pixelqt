#! /usr/bin/env python3
# coding: utf-8
import pixelqt
from random import randint
import copy


class GoL():
    def __init__(self):
        self.alive_const = 3
        self.notchange_const = 2
    
    def generate_random(self):
        self.matrix = [[0]*self.w for i in range(self.h)]
        
        for line in range(self.h):
            for col in range(self.w):
                self.matrix[line][col] = randint(0,1)
    
    def compute(self):
        new = copy.deepcopy(self.matrix)
        
        for line in range(self.h):
            for col in range(self.w):
                n = self.get_neighbors(line, col)
                
                if n == self.alive_const:
                    new[line][col] = 1
                elif n == self.notchange_const:
                    pass    # the cell is not changed
                else:
                    new[line][col] = 0
        
        self.matrix = new
    
    def get_neighbors(self, line, col):
        res = 0
        
        n_coos = [(line-1, col-1), (line-1, col), (line-1, col+1),
                (line, col-1), (line, col+1),
                (line+1, col-1), (line+1, col), (line+1, col+1) ]
        
        for coos in n_coos:
            try:
                res += self.matrix[coos[0]][coos[1]]
            except IndexError:
                pass
        
        return res


def get_drawdata(w, h, frame_count):
    res = {}
    
    life.alive_const = mygame.own_params['Always alive if']
    life.notchange_const = mygame.own_params['Dont change if']
    
    if frame_count == 0:
        life.w, life.h = w, h
        life.generate_random()
    else:
        life.compute()
    
    # create result dict to draw
    for line in range(h):
        for col in range(w):
            if life.matrix[line][col]:
                res[(line, col)] = (150,255,150)
    
    return res


life = GoL()
mygame = pixelqt.Game(get_drawdata=get_drawdata)
mygame.config['name'] = 'Conway\'s Game of Life'
mygame.config['w'] = 160
mygame.config['h'] = 120
mygame.config['background'] = (50,50,50)
mygame.config['zoom'] = 2
mygame.init_controls('resolution', 'zoom', 'background', 'invert_colors', 'draw_each', 'save_each')

mygame.add_own_num(name='Always alive if', default = 3, need_to_restart=False, minimum=0, maximum=8, step=1)
mygame.add_own_num(name='Dont change if', default = 2, need_to_restart=False, minimum=0, maximum=8, step=1)

mygame.run()
