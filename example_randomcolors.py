#! /usr/bin/env python3
# coding: utf-8
import pixelqt
import numpy

w, h = 120, 90


def get_imdata():
	pic = numpy.random.random((w,h,3)) * 255
	pic8 = numpy.uint8(pic)
	return pic8


mygame = pixelqt.Game(draw_func=get_imdata)
mygame.config['name'] = 'Random colors'
mygame.config['w'] = w
mygame.config['h'] = h
mygame.config['gl'] = False
mygame.init_controls('resolution', 'zoom')
mygame.run()
