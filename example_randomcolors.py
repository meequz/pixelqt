#! /usr/bin/env python3
# coding: utf-8
import pixelqt
from random import randint


# Function that returns dict in format: {(coordinates): (rgb color)}
# Other areas will be filled with background color.
def get_imdata(w, h, frame_count):
    res = {}
    for line in range(h):
        for col in range(w):
            if randint(0, 1):
                res[(line, col)] = (line*col//(w*h/255), randint(0,150), randint(0,255))
    return res


# Create main instance and specify function that will be called periodically.
mygame = pixelqt.Game(draw_func=get_imdata)


# Set your own default options. No one is required.
# If you don't set them, the defaults will be used.

# Window title
mygame.config['name'] = 'Almost random colors'
# Width
mygame.config['w'] = 120
# Height
mygame.config['h'] = 90
# Background color
mygame.config['background'] = (255, 255, 150)
# Enable/Disable OpenGL in drawing
mygame.config['gl'] = True
# Save each N frame into file (get screenshot)
mygame.config['save_each'] = 17
# Invert colors or not
mygame.config['invert_colors'] = True

# Add controls which you want to see in game's window.
mygame.init_controls('resolution', 'zoom', 'background', 'gl', 'invert_colors')

# Run the simulation.
mygame.run()
