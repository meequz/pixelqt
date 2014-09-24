#! /usr/bin/env python3
# coding: utf-8
import pixelqt
import numpy


def get_imdata(w, h):
	pic = numpy.random.random((w,h,3)) * 255
	pic8 = numpy.uint8(pic)
	return pic8


mygame = pixelqt.Game(draw_func=get_imdata)
mygame.config['name'] = 'Random colors'
mygame.config['w'] = 120
mygame.config['h'] = 90
mygame.config['gl'] = True
mygame.init_controls('resolution', 'zoom', 'background')
mygame.run()
