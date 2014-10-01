#! /usr/bin/env python3
# coding: utf-8
import sys
from PyQt4 import QtGui as qg
from PyQt4 import QtCore as qc
from PyQt4 import QtOpenGL
from OpenGL import GL    # need for nvidia cards
import numpy
import datetime
import os


class Game():
    """Creates all classes and config."""
    def __init__(self, get_drawdata):
        self.config = self.get_default_config()
        self.newconfig = {}
        
        self.frame_count = 0
        self.state = 'running'
        
        self.get_drawdata = get_drawdata
        self.app = qg.QApplication(sys.argv)
        
        self.field = Field(game_instance=self)
        self.controls = Controls(game_instance=self)
        self.actions = Actions(game_instance=self)
        
        self.win = Window(game_instance=self)
        self.widget = self.win.widget
        self.init_controls = self.win.widget.init_controls
    
    def get_default_config(self):
        config = {'name': 'Game is not loaded',
            'w': 80,
            'h': 60,
            'zoom': 2,
            'background': (0, 0, 0),
            'draw_each': 1,
            'save_each': 0,
            'grid': False,
            'invert_colors': False,
            'label': False,
            'gl': False
        }
        return config
    
    def run(self):
        """Perform actions that are not takes from config
        on each frame drawing.
        """
        # Preparing
        self.actions.set_name()
        if self.config['gl']:
            self.actions.set_gl(qc.Qt.Checked)
        
        # Fit window size. TODO: make it properly
        fitsize = self.win.sizeHint() +\
            qc.QSize(self.config['w']*self.config['zoom'] + 40,
            self.config['h']*self.config['zoom'] - 50)
        self.win.resize(fitsize)
        
        # Actual start
        self.field.start()
        sys.exit(self.app.exec_())
        

class Window(qg.QMainWindow):
    """Creates main widget and set window parameters (title, size etc)."""
    def __init__(self, game_instance):
        super(Window, self).__init__()
        self.game = game_instance
        
        self.widget = Widget(game_instance)
        self.setCentralWidget(self.widget)
        
        self.setWindowTitle(self.game.config['name'])
        self.statusbar = self.statusBar()
        self.set_status()
        
        self.show()
    
    def set_status(self):
        message = 'Frame ' + str(self.game.frame_count) + ', ' + self.game.state
        if self.game.newconfig:
            message += '. Changes will take effect after restart'
        self.statusbar.showMessage(message)


class Widget(qg.QWidget):
    """Implements UI in window."""
    def __init__(self, game_instance):
        super(Widget, self).__init__()
        self.game = game_instance
        self.init_ui()
    
    def init_ui(self):
        btn_pause_or_play = self.game.controls.button_pause_or_play()
        btn_restart = self.game.controls.button_restart()
        
        # bottom buttons
        self.bottom_btns = qg.QHBoxLayout()
        self.bottom_btns.addWidget(btn_pause_or_play)
        self.bottom_btns.addWidget(btn_restart)
        
        # left vbox with graphics and buttons
        self.vbox_left = qg.QVBoxLayout()
        self.vbox_left.addWidget(self.game.field)
        self.vbox_left.addLayout(self.bottom_btns)
        
        # right vbox with controls
        self.vbox_right = qg.QVBoxLayout()
        
        # global horizontal box with two vertical boxes
        self.global_hbox = qg.QHBoxLayout()
        self.global_hbox.addLayout(self.vbox_left, 1)
        self.global_hbox.addLayout(self.vbox_right)
        self.setLayout(self.global_hbox)
    
    def init_controls(self, *args):
        if len(args) != len(set(args)):
            print('You added the same control twice or more. The program may work incorrectly.')
        
        for arg in args:
            if arg == 'resolution':
                hbox_res = self.game.controls.resolution()
                self.vbox_right.addLayout(hbox_res)
            if arg == 'zoom':
                hbox_zoom = self.game.controls.zoom()
                self.vbox_right.addLayout(hbox_zoom)
            if arg == 'background':
                hbox_background = self.game.controls.background()
                self.vbox_right.addLayout(hbox_background)
            if arg == 'gl':
                hbox_gl = self.game.controls.gl()
                self.vbox_right.addLayout(hbox_gl)
            if arg == 'draw_each':
                hbox_draw_each = self.game.controls.draw_each()
                self.vbox_right.addLayout(hbox_draw_each)
            if arg == 'save_each':
                hbox_save_each = self.game.controls.save_each()
                self.vbox_right.addLayout(hbox_save_each)
            if arg == 'invert_colors':
                hbox_invert_colors = self.game.controls.invert_colors()
                self.vbox_right.addLayout(hbox_invert_colors)


class Field(qg.QGraphicsView):
    """QGraphicsView widget. Implements drawing according to
    drawing parameters in self.game.config
    """
    def __init__(self, game_instance):
        super(Field, self).__init__()
        self.game = game_instance
        
        self.scene = qg.QGraphicsScene()
        self.scene.setBackgroundBrush(qc.Qt.gray)
        self.setScene(self.scene)
        
        # when timer triggers, it calls the operate_frame method
        self.timer=qc.QTimer()
        self.timer.timeout.connect(self.operate_frame)
    
    def start(self):
        self.generate_basis()
        self.game.state = 'running'
        self.timer.start()
    
    def stop(self):
        self.timer.stop()
        self.game.state = 'pause'
        self.game.win.set_status()
    
    def generate_basis(self):
        line = numpy.array([self.game.config['background']] * self.game.config['w'])
        basis = numpy.array([line] * self.game.config['h'])
        self.basis = numpy.uint8(basis)
    
    def operate_frame(self):
        w = self.game.config['w']
        h = self.game.config['h']
        imdata = self.basis.copy()
        drawdata = self.game.get_drawdata(w, h, self.game.frame_count)
        
        try:
            will_save = self.game.frame_count % self.game.config['save_each'] == 0
        except ZeroDivisionError:
            will_save = False
        try:
            will_draw = self.game.frame_count % self.game.config['draw_each'] == 0
        except ZeroDivisionError:
            will_draw = False
        
        if will_save or will_draw:
            for coords in drawdata:
                imdata[coords[0]][coords[1]] = drawdata[coords]
            self.qimage = qg.QImage(imdata.data, w, h, qg.QImage.Format_RGB888)
        
        if will_save:
            self.save_frame()
        if will_draw:
            self.draw_frame()
        
        self.game.frame_count += 1
        self.game.win.set_status()
    
    def save_frame(self):
        # check if path exists
        directory = 'screenshots'
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        # get screenshot filename
        date = datetime.datetime.now().strftime('%G-%m-%d-%H-%M-%S-%f')
        filename = self.game.config['name'] + '_' +\
                    date + '_' +\
                    str(self.game.frame_count) + '.png'
        
        # convert and save
        qpix = qg.QPixmap(self.qimage)
        qpix.save(directory + '/' + filename)
    
    def draw_frame(self):
        # invert colors
        if self.game.config['invert_colors']:
            self.qimage.invertPixels()
        
        # convert to qpixmap, scale and draw
        qpix = qg.QPixmap(self.qimage)
        qpix = qpix.scaled(qpix.size()*self.game.config['zoom'], qc.Qt.KeepAspectRatio)
        self.scene.clear()
        self.scene.addPixmap(qpix)


class Actions():
    """Makes non-drawing changes accordig to config parameters."""
    def __init__(self, game_instance):
        self.game = game_instance
    
    def pause_or_play(self):
        # self.game.state may be bugged, but timer is never
        if self.game.field.timer.isActive():
            self.game.field.stop()
        else:
            self.game.field.start()
    
    def restart(self):
        # TODO: add centering in field
        for key in self.game.newconfig:
            self.game.config[key] = self.game.newconfig[key]
        self.game.newconfig = {}
        
        self.game.frame_count = 0
        self.game.field.start()
    
    def set_name(self):
        self.game.win.setWindowTitle(self.game.config['name'])
    
    def set_resolution(self):
        sender = self.game.win.sender()
        text = sender.text()
        if sender is self.game.controls.w_lineedit:
            try:
                self.game.newconfig['w'] = int(text)
            except ValueError:
                self.game.newconfig['w'] = self.game.config['w']
        elif sender is self.game.controls.h_lineedit:
            try:
                self.game.newconfig['h'] = int(text)
            except ValueError:
                self.game.newconfig['h'] = self.game.config['h']
        else:
            print('oops!')
    
    def set_zoom(self):
        # TODO: add centering in field
        zoom_factor = self.game.win.sender().value()
        self.game.config['zoom'] = zoom_factor
    
    def set_background(self):
        col = qg.QColorDialog.getColor()
        if col.isValid():
            color = col.getRgb()[:3]
            self.game.config['background'] = color
            self.game.field.generate_basis()
    
    def set_gl(self, state):
        if state == qc.Qt.Checked:
            self.game.field.setViewport(QtOpenGL.QGLWidget())
            self.game.config['gl'] = True
        else:
            self.game.field.setViewport(qg.QWidget())
            self.game.config['gl'] = False
    
    def set_save_each(self):
        save_each_number = self.game.win.sender().value()
        self.game.config['save_each'] = save_each_number
    
    def set_draw_each(self):
        draw_each_number = self.game.win.sender().value()
        self.game.config['draw_each'] = draw_each_number
    
    def set_invert_colors(self, state):
        if state == qc.Qt.Checked:
            self.game.config['invert_colors'] = True
        else:
            self.game.config['invert_colors'] = False


class Controls():
    """Contains base hboxes, connects them with actions
    and adds to vbox_right.
    """
    def __init__(self, game_instance):
        self.game = game_instance
    
    def button_pause_or_play(self):
        btn_pause_or_play = qg.QPushButton('Pause/Play')
        btn_pause_or_play.clicked.connect(self.game.actions.pause_or_play)
        return btn_pause_or_play
    
    def button_restart(self):
        btn_restart = qg.QPushButton('(Re)Start')
        btn_restart.clicked.connect(self.game.actions.restart)
        return btn_restart
    
    def resolution(self):
        w = self.game.config['w']
        h = self.game.config['h']
        
        label_w = qg.QLabel('Width:')
        label_h = qg.QLabel('Height:')
        
        self.w_lineedit = qg.QLineEdit(str(w))
        self.h_lineedit = qg.QLineEdit(str(h))
        self.w_lineedit.textChanged[str].connect(self.game.actions.set_resolution)
        self.h_lineedit.textChanged[str].connect(self.game.actions.set_resolution)
        
        hbox_w = qg.QHBoxLayout()
        hbox_h = qg.QHBoxLayout()
        
        hbox_w.addWidget(label_w)
        hbox_h.addWidget(label_h)
        hbox_w.addWidget(self.w_lineedit)
        hbox_h.addWidget(self.h_lineedit)
        
        vbox = qg.QVBoxLayout()
        vbox.addLayout(hbox_w)
        vbox.addLayout(hbox_h)
        
        return vbox
    
    def zoom(self):
        label_zoom = qg.QLabel('Zoom:')
        spin_zoom = qg.QSpinBox()
        spin_zoom.setValue(self.game.config['zoom'])
        spin_zoom.valueChanged[str].connect(self.game.actions.set_zoom)        # str?
        
        hbox_zoom = qg.QHBoxLayout()
        hbox_zoom.addWidget(label_zoom)
        hbox_zoom.addWidget(spin_zoom)
        
        return hbox_zoom
    
    def background(self):
        label_background = qg.QLabel('Background:')
        btn_background = qg.QPushButton('Choose')
        btn_background.clicked.connect(self.game.actions.set_background)
        
        hbox_background = qg.QHBoxLayout()
        hbox_background.addWidget(label_background)
        hbox_background.addWidget(btn_background)
        
        return hbox_background
    
    def gl(self):
        checkbox_gl = qg.QCheckBox('Use OpenGL')
        if self.game.config['gl']:
            checkbox_gl.toggle()
        checkbox_gl.stateChanged.connect(self.game.actions.set_gl)
        
        hbox_gl = qg.QHBoxLayout()
        hbox_gl.addWidget(checkbox_gl)
        
        return hbox_gl
    
    def save_each(self):
        label_save_each = qg.QLabel('Save each X frame')
        spin_save_each = qg.QSpinBox()
        spin_save_each.setValue(self.game.config['save_each'])
        spin_save_each.valueChanged[str].connect(self.game.actions.set_save_each)
        
        hbox_save_each = qg.QHBoxLayout()
        hbox_save_each.addWidget(label_save_each)
        hbox_save_each.addWidget(spin_save_each)
        
        return hbox_save_each
    
    def draw_each(self):
        label_draw_each = qg.QLabel('Draw each X frame')
        spin_draw_each = qg.QSpinBox()
        spin_draw_each.setValue(self.game.config['draw_each'])
        spin_draw_each.valueChanged[str].connect(self.game.actions.set_draw_each)
        
        hbox_draw_each = qg.QHBoxLayout()
        hbox_draw_each.addWidget(label_draw_each)
        hbox_draw_each.addWidget(spin_draw_each)
        
        return hbox_draw_each
    
    def invert_colors(self):
        checkbox_invert_colors = qg.QCheckBox('Invert colors')
        if self.game.config['invert_colors']:
            checkbox_invert_colors.toggle()
        checkbox_invert_colors.stateChanged.connect(self.game.actions.set_invert_colors)
        
        hbox_invert_colors = qg.QHBoxLayout()
        hbox_invert_colors.addWidget(checkbox_invert_colors)
        
        return hbox_invert_colors
