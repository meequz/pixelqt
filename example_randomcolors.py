#! /usr/bin/env python3
# coding: utf-8
import pixelqt
from random import randint


# Function that returns dict if format: {(coordinates): (rgb color)}
# Other areas will be filled by background color.
def get_imdata(w, h, frame_count):
    res = {}
    for line in range(h):
        for col in range(w):
            if randint(0, 1):
                res[(line, col)] = (line*col//(w*h/255), randint(0,150), randint(0,255))
    return res


# Create game and specify function that will be called periodically.
mygame = pixelqt.Game(draw_func=get_imdata)

# Set your own default options. No one is required.
# If you don't set them, the defaults will be used.
mygame.config['name'] = 'Almost random colors'
mygame.config['w'] = 120
mygame.config['h'] = 90
mygame.config['background'] = (255, 255, 150)
mygame.config['gl'] = True
mygame.config['save_each'] = 17

# Add controls which you want to see in game's window.
mygame.init_controls('resolution', 'zoom', 'background', 'gl')

# Run the simulation.
mygame.run()
