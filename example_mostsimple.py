#! /usr/bin/env python3
# coding: utf-8
import pixelqt


def get_drawdata(w, h, frame_count):
    
    if frame_count % 2 == 0:
        return {(20,10): (0,255,0)}
    else:
        return {(50,40): (255,255,0),
                 (50,50): (255,255,0)}


mygame = pixelqt.Game(get_drawdata=get_drawdata)
mygame.run()
