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
                
                if self.alive_more <= n <= self.alive_less:
                    new[line][col] = 1
                elif self.same_more <= n <= self.same_less:
                    pass    # the cell stay the same
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


# function that returns dict to draw
def get_drawdata(w, h, frame_count):
    # apply own parameters
    life.alive_more = mygame.own_params['Alive if n between A']
    life.alive_less = mygame.own_params['and B']
    life.same_more = mygame.own_params['Same if n between C']
    life.same_less = mygame.own_params['and D']
    
    # handle if restart
    if frame_count == 0:
        life.w, life.h = w, h
        life.generate_random()
    else:
        life.compute()
    
    # create result dict to draw
    res = {}
    for line in range(h):
        for col in range(w):
            if life.matrix[line][col]:
                res[(line, col)] = (150,255,150)
    
    return res


life = GoL()

# Create main instance and specify function that will be called periodically.
mygame = pixelqt.Game(get_drawdata=get_drawdata)

# Set your own default options. No one is required.
# If you don't set them, the defaults will be used.
mygame.config['name'] = 'Conway\'s Game of Life'
mygame.config['w'] = 160
mygame.config['h'] = 120
mygame.config['zoom'] = 2
mygame.init_controls('resolution', 'zoom', 'background', 'invert_colors', 'draw_each', 'save_each')

# Add own parameter which will affect on game's behavior
mygame.add_own_num(name='Alive if n between A', default=3, need_to_restart=False, minimum=0, maximum=8, step=1)
mygame.add_own_num(name='and B', default=3, need_to_restart=False, minimum=0, maximum=8, step=1)
mygame.add_own_num(name='Same if n between C', default=2, need_to_restart=False, minimum=0, maximum=8, step=1)
mygame.add_own_num(name='and D', default=2, need_to_restart=False, minimum=0, maximum=8, step=1)

mygame.run()
