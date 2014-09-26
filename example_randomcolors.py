#! /usr/bin/env python3
# coding: utf-8
import pixelqt
from random import randint


def get_imdata(w, h):
    res = {}
    for line in range(h):
        for col in range(w):
            if randint(0, 1):
                res[(line, col)] = (line*col//(w*h/255), randint(0,150), randint(0,255))
    return res


mygame = pixelqt.Game(draw_func=get_imdata)
mygame.config['name'] = 'Random colors'
mygame.config['w'] = 120
mygame.config['h'] = 90
mygame.config['background'] = (255, 255, 0)
mygame.config['gl'] = True
mygame.init_controls('resolution', 'zoom', 'background')
mygame.run()
