#! /usr/bin/env python3
# coding: utf-8
import pixelqt
from random import randint
import copy


class GoL():
    def __init__(self):
        pass
    
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
                
                if n == 3:
                    new[line][col] = 1
                elif n == 2  and  self.matrix[line][col]:
                    pass    # because the cell already alive
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
                if self.matrix[coos[0]][coos[1]]:
                    res += 1
            except IndexError:
                pass
        
        return res


def get_imdata(w, h, frame_count):
    res = {}
    life.w, life.h = w, h
    
    if frame_count == 0:
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

mygame = pixelqt.Game(draw_func=get_imdata)
mygame.config['name'] = 'Conway\'s Game of Life'
mygame.config['w'] = 160
mygame.config['h'] = 120
mygame.config['background'] = (50,50,50)
mygame.config['zoom'] = 2
mygame.init_controls('resolution', 'zoom', 'background')
mygame.run()
