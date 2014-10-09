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
        self.game = self
        self.app = qg.QApplication(sys.argv)
        
        self.config = {'name': 'Game is not loaded',
                  'w': 80,
                  'h': 60,
                  'zoom': 2,
                  'background': [80, 80, 80],
                  'draw_each': 1,
                  'save_each': 0,
                  'grid': False,
                  'gridcolor': [0, 0, 0],
                  'invert_colors': False,
                  'label': False,
                  'gl': False
        }
        
        self.newconfig = {}
        self.own_params = {}
        self.new_own_params = {}
        
        self.frame_count = 0
        self.get_drawdata = get_drawdata
        
        self.field = Field(game_instance=self)
        self.controls = Controls(game_instance=self)
        self.actions = Actions(game_instance=self)
        
        self.win = Window(game_instance=self)
        self.init_controls = self.win.init_controls
        
        self.owns = Owns(game_instance=self)
        self.add_own_num = self.owns.add_own_num
        self.add_own_bool = self.owns.add_own_bool
        self.add_own_choice = self.owns.add_own_choice
    
    def run(self):
        """Perform actions that are not takes from config
        on each frame drawing.
        """
        # delete own_params dock if it is empty
        if not self.own_params:
            self.win.dock_ownparams.deleteLater()
        
        # preparing
        self.actions.set_name()
        if self.config['gl']:
            self.actions.set_gl(qc.Qt.Checked)
        
        # fit window size. TODO: make it properly
        fitsize = self.win.sizeHint() +\
                  qc.QSize(self.config['w']*self.config['zoom'] + 40,
                  self.config['h']*self.config['zoom'] - 50)
        self.win.resize(fitsize)
        
        # actual start
        self.field.start()
        sys.exit(self.app.exec_())
    
    def restore_def_config(self):
        for widget in self.controls.ctr_widgets:
            
            widgetname = self.controls.ctr_widgets[widget]['widgetname']
            def_value = self.controls.ctr_widgets[widget]['def_value']
            
            # resolution
            if widgetname in ('w_lineedit', 'h_lineedit'):
                widget.setText(str(def_value))
            
            # background color
            if widgetname == 'btn_background':
                self.config['background'] = def_value
                self.field.generate_basis()
                self.actions.colorize_button(widget, qg.QColor(*def_value))
            
            # grid color
            if widgetname == 'btn_gridcolor':
                self.config['gridcolor'] = def_value
                self.field.generate_grid()
                self.actions.colorize_button(widget, qg.QColor(*def_value))
            
            # draw each, save each, zoom
            if widgetname in ('spin_draw_each',
                              'spin_save_each',
                              'spin_zoom'):
                widget.setValue(def_value)
            
            # grid, invert_colors, gl
            if widgetname in ('checkbox_grid',
                              'checkbox_invert_colors',
                              'checkbox_gl'):
                if def_value:
                    widget.setChecked(True)
                else:
                    widget.setChecked(False)
            
    
    def restore_def_ownparams(self):
        for widget in self.owns.param_widgets:
            
            widgetname = self.owns.param_widgets[widget]['name']
            def_value = self.owns.param_widgets[widget]['default']
            
            # spinboxes
            if isinstance(widget, qg.QSpinBox):
                widget.setValue(def_value)
            
            # checkboxes
            if isinstance(widget, qg.QCheckBox):
                if def_value:
                    widget.setChecked(True)
                else:
                    widget.setChecked(False)
            
            # comboboxes
            if isinstance(widget, qg.QComboBox):
                widget.setCurrentIndex(def_value)


class Window(qg.QMainWindow):
    """Creates main widget and set window parameters (title, size etc)."""
    def __init__(self, game_instance):
        super(Window, self).__init__()
        self.game = game_instance
        self.init_ui()
        
        self.setWindowTitle(self.game.config['name'])
        self.statusbar = self.statusBar()
        self.show()
    
    def init_ui(self):
        # field and buttons - central widget
        widget_field_and_bb = qg.QWidget()
        layout_field_and_bb = qg.QVBoxLayout()
        widget_field_and_bb.setLayout(layout_field_and_bb)
        
        bottom_buttons = self.create_bottom_buttons()
        layout_field_and_bb.addWidget(self.game.field)
        layout_field_and_bb.addLayout(bottom_buttons)
        
        self.setCentralWidget(widget_field_and_bb)
        
        # docks with controls and own parameters
        self.dock_controls, self.layout_controls = self.create_dock('Controls')
        self.dock_ownparams, self.layout_ownparams = self.create_dock('Game Parameters')
        
        # add Restore defaults buttons to dock's layouts
        btn_restore_def_config = self.create_button('restore defaults', self.game.restore_def_config)
        btn_restore_def_ownparams = self.create_button('restore defaults', self.game.restore_def_ownparams)
        self.layout_controls.addWidget(btn_restore_def_config)
        self.layout_ownparams.addWidget(btn_restore_def_ownparams)
        
        # add docks to window
        self.addDockWidget(qc.Qt.RightDockWidgetArea, self.dock_controls)
        self.addDockWidget(qc.Qt.RightDockWidgetArea, self.dock_ownparams)
    
    def create_button(self, name, connect_to):
        # TODO: use it everywhere
        btn = qg.QPushButton(name)
        btn.clicked.connect(connect_to)
        return btn
    
    def create_dock(self, name):
        dock = qg.QDockWidget(name)
        widget = qg.QWidget()
        layout = qg.QVBoxLayout()
        widget.setLayout(layout)
        dock.setWidget(widget)
        dock.setFeatures(qg.QDockWidget.DockWidgetMovable)
        return dock, layout
    
    def create_bottom_buttons(self):
        btn_pause_or_play = self.game.controls.button_pause_or_play()
        btn_restart = self.game.controls.button_restart()
        bottom_btns = qg.QHBoxLayout()
        bottom_btns.addWidget(btn_pause_or_play)
        bottom_btns.addWidget(btn_restart)
        return bottom_btns
    
    def set_status(self):
        message = 'Frame ' + str(self.game.frame_count) + ', ' + self.game.state
        # TODO: compare new and current dicts to consider only changed values
        if self.game.newconfig or self.game.new_own_params:
            message += '. Changes will take effect after restart'
        self.statusbar.showMessage(message)
    
    def init_controls(self, *args):
        if len(args) != len(set(args)):
            print('You can\'t init the same control twice or more.')
            exit(1)
        
        connects = {'resolution': self.game.controls.resolution,
                    'zoom': self.game.controls.zoom,
                    'background': self.game.controls.background,
                    'gl': self.game.controls.gl,
                    'grid': self.game.controls.grid,
                    'gridcolor': self.game.controls.gridcolor,
                    'draw_each': self.game.controls.draw_each,
                    'save_each': self.game.controls.save_each,
                    'invert_colors': self.game.controls.invert_colors}
        
        for arg in args:
            controls_method = connects[arg]
            self.place_to_layout_controls(controls_method)
    
    def place_to_layout_controls(self, controls_method):
        box = controls_method()
        self.layout_controls.addLayout(box)


class Field(qg.QGraphicsView):
    """QGraphicsView widget. Implements drawing according to
    drawing parameters in self.game.config
    """
    def __init__(self, game_instance):
        super(Field, self).__init__()
        self.game = game_instance
        
        # create scene
        self.scene = qg.QGraphicsScene()
        self.scene.setBackgroundBrush(qc.Qt.gray)
        self.setScene(self.scene)
        
        self.setDragMode(self.ScrollHandDrag)
        
        # when timer triggers, it calls the operate_frame method
        self.timer=qc.QTimer()
        self.timer.timeout.connect(self.operate_frame)
    
    # zoom by mouse wheel
    def wheelEvent(self, event):
        # if control exists. TODO: make control compulsory and zoom action is permanent
        try:
            spin_zoom = self.game.controls.spin_zoom
            if event.delta() > 0:
                spin_zoom.setValue(self.game.config['zoom']+1)
            else:
                spin_zoom.setValue(self.game.config['zoom']-1)
        #~ else
        except AttributeError:
            if event.delta() > 0:
                self.game.actions.set_zoom(self.game.config['zoom']+1)
            else:
                self.game.actions.set_zoom(self.game.config['zoom']-1)
    
    def start(self):
        self.game.state = 'running'
        
        self.generate_basis()
        if self.game.config['grid']:
            self.generate_grid()
        self.center_scene()
        
        self.timer.start()
    
    def stop(self):
        self.timer.stop()
        self.game.state = 'pause'
        self.game.win.set_status()
    
    def generate_basis(self):
        # generate base image with background
        line = numpy.array([self.game.config['background']] * self.game.config['w'])
        basis = numpy.array([line] * self.game.config['h'])
        self.basis = numpy.uint8(basis)
    
    def generate_grid(self):
        w = self.game.config['w']
        h = self.game.config['h']
        zoom = self.game.config['zoom']
        
        # blue, green, red, alpha (0 is transparented)
        col = self.game.config['gridcolor']
        color_grid = [list(reversed(col)) + [255]]
        
        pattern = color_grid + [[0, 0, 0, 0]]*(zoom-1)
        line = numpy.array(pattern * w)
        grid = numpy.array([line] * (h*zoom))
        
        line_grid = numpy.array(color_grid * (w*zoom))
        for i in range(h*zoom):
            if i % zoom == 0:
                grid[i] = line_grid
        
        grid = numpy.uint8(grid)
        qimage = qg.QImage(grid.data, w*zoom, h*zoom, qg.QImage.Format_ARGB32)
        self.grid = qg.QPixmap(qimage)
    
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
        
        # add grid
        if self.game.config['grid'] and self.game.config['zoom'] >= 2:
            self.scene.addPixmap(self.grid)
    
    def center_scene(self):
        w = self.game.config['w']
        h = self.game.config['h']
        zoom = self.game.config['zoom']
        self.scene.setSceneRect(0, 0, w*zoom, h*zoom)


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
        # update config
        for key in self.game.newconfig:
            self.game.config[key] = self.game.newconfig[key]
        self.game.newconfig = {}
        
        # update own_params
        for key in self.game.new_own_params:
            self.game.own_params[key] = self.game.new_own_params[key]
        self.game.new_own_params = {}
        
        self.game.frame_count = 0
        self.game.field.start()
    
    def set_name(self):
        self.game.win.setWindowTitle(self.game.config['name'])
    
    def set_resolution(self):
        sender = self.game.win.sender()
        text = sender.text()
        
        if sender is self.game.controls.w_lineedit:
            dimension = 'w'
        elif sender is self.game.controls.h_lineedit:
            dimension = 'h'
        
        try:
            self.game.newconfig[dimension] = int(text)
        except ValueError:
            self.game.newconfig[dimension] = self.game.config[dimension]
    
    def set_zoom_catch(self):
        zoom_factor = self.game.win.sender().value()
        self.set_zoom(zoom_factor)
    
    def set_zoom(self, zoom_factor):
        if zoom_factor >= 1:
            self.game.config['zoom'] = zoom_factor
        else:
            return
        
        if self.game.field.timer.isActive():
            self.game.field.center_scene()
            if self.game.config['grid']:
                self.game.field.generate_grid()
    
    def set_background(self):
        col = qg.QColorDialog.getColor(qg.QColor(*self.game.config['background']))
        if col.isValid():
            color = col.getRgb()[:3]
            self.game.config['background'] = color
            self.game.field.generate_basis()
        self.colorize_button(self.game.controls.btn_background, col)
    
    def set_gridcolor(self):
        col = qg.QColorDialog.getColor(qg.QColor(*self.game.config['gridcolor']))
        if col.isValid():
            color = col.getRgb()[:3]
            self.game.config['gridcolor'] = color
            self.game.field.generate_grid()
        self.colorize_button(self.game.controls.btn_gridcolor, col)
    
    def colorize_button(self, button, color):
        palette = qg.QPalette()
        palette.setColor(qg.QPalette.Button, color)
        button.setPalette(palette)
    
    def set_gl(self, state):
        if state == qc.Qt.Checked:
            self.game.field.setViewport(QtOpenGL.QGLWidget())
            self.game.config['gl'] = True
        else:
            self.game.field.setViewport(qg.QWidget())
            self.game.config['gl'] = False
    
    def set_grid(self, state):
        if state == qc.Qt.Checked:
            self.game.config['grid'] = True
        else:
            self.game.config['grid'] = False
    
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
    """Contains base horizontal boxes and connects their widgets with actions"""
    def __init__(self, game_instance):
        self.game = game_instance
        # for store default values
        self.ctr_widgets = {}
    
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
        
        # labels
        label_w = qg.QLabel('Width:')
        label_h = qg.QLabel('Height:')
        
        # lineedits
        self.w_lineedit = qg.QLineEdit(str(w))
        self.h_lineedit = qg.QLineEdit(str(h))
        self.w_lineedit.textChanged[str].connect(self.game.actions.set_resolution)
        self.h_lineedit.textChanged[str].connect(self.game.actions.set_resolution)
        
        # remember connection to restore defaults
        self.ctr_widgets[self.w_lineedit] = {'widgetname': 'w_lineedit', 'def_value': w}
        self.ctr_widgets[self.h_lineedit] = {'widgetname': 'h_lineedit', 'def_value': h}
        
        # horizontal boxes
        hbox_w = qg.QHBoxLayout()
        hbox_h = qg.QHBoxLayout()
        
        hbox_w.addWidget(label_w)
        hbox_h.addWidget(label_h)
        hbox_w.addWidget(self.w_lineedit)
        hbox_h.addWidget(self.h_lineedit)
        
        # resulting vertical box
        vbox_resolution = qg.QVBoxLayout()
        vbox_resolution.addLayout(hbox_w)
        vbox_resolution.addLayout(hbox_h)
        
        return vbox_resolution
    
    def zoom(self):
        label_zoom = qg.QLabel('Zoom:')
        self.spin_zoom = qg.QSpinBox()
        self.spin_zoom.setMinimum(1)
        self.spin_zoom.setValue(self.game.config['zoom'])
        self.spin_zoom.valueChanged[str].connect(self.game.actions.set_zoom_catch)        # str?
        
        # remember connection to restore defaults
        self.ctr_widgets[self.spin_zoom] = {'widgetname': 'spin_zoom',
                                            'def_value': self.game.config['zoom']}
        
        hbox_zoom = qg.QHBoxLayout()
        hbox_zoom.addWidget(label_zoom)
        hbox_zoom.addWidget(self.spin_zoom)
        
        return hbox_zoom
    
    def background(self):
        # label and button
        label_background = qg.QLabel('Background:')
        self.btn_background = qg.QPushButton('Choose')
        self.game.actions.colorize_button(self.btn_background, qg.QColor(*self.game.config['background']))
        self.btn_background.clicked.connect(self.game.actions.set_background)
        
        # remember connection to restore defaults
        self.ctr_widgets[self.btn_background] = {'widgetname': 'btn_background',
                                                 'def_value': self.game.config['background']}
        
        hbox_background = qg.QHBoxLayout()
        hbox_background.addWidget(label_background)
        hbox_background.addWidget(self.btn_background)
        
        return hbox_background
    
    def gridcolor(self):
        label_gridcolor = qg.QLabel('Grid color:')
        
        self.btn_gridcolor = qg.QPushButton('Choose')
        self.game.actions.colorize_button(self.btn_gridcolor, qg.QColor(*self.game.config['gridcolor']))
        self.btn_gridcolor.clicked.connect(self.game.actions.set_gridcolor)
        
        # remember connection to restore defaults
        self.ctr_widgets[self.btn_gridcolor] = {'widgetname': 'btn_gridcolor',
                                                'def_value': self.game.config['gridcolor']}
        
        hbox_gridcolor = qg.QHBoxLayout()
        hbox_gridcolor.addWidget(label_gridcolor)
        hbox_gridcolor.addWidget(self.btn_gridcolor)
        
        return hbox_gridcolor
    
    def gl(self):
        self.checkbox_gl = qg.QCheckBox('Use OpenGL')
        if self.game.config['gl']:
            self.checkbox_gl.toggle()
        self.checkbox_gl.stateChanged.connect(self.game.actions.set_gl)
        
        # remember connection to restore defaults
        self.ctr_widgets[self.checkbox_gl] = {'widgetname': 'checkbox_gl',
                                              'def_value': self.game.config['gl']}
        
        hbox_gl = qg.QHBoxLayout()
        hbox_gl.addWidget(self.checkbox_gl)
        
        return hbox_gl
    
    def grid(self):
        self.checkbox_grid = qg.QCheckBox('Grid')
        if self.game.config['grid']:
            self.checkbox_grid.toggle()
        self.checkbox_grid.stateChanged.connect(self.game.actions.set_grid)
        
        # remember connection to restore defaults
        self.ctr_widgets[self.checkbox_grid] = {'widgetname': 'checkbox_grid',
                                                'def_value': self.game.config['grid']}
        
        hbox_grid = qg.QHBoxLayout()
        hbox_grid.addWidget(self.checkbox_grid)
        
        return hbox_grid
    
    def save_each(self):
        label_save_each = qg.QLabel('Save each X frame')
        self.spin_save_each = qg.QSpinBox()
        self.spin_save_each.setValue(self.game.config['save_each'])
        self.spin_save_each.valueChanged[str].connect(self.game.actions.set_save_each)
        
        # remember connection to restore defaults
        self.ctr_widgets[self.spin_save_each] = {'widgetname': 'spin_save_each',
                                                 'def_value': self.game.config['save_each']}
        
        hbox_save_each = qg.QHBoxLayout()
        hbox_save_each.addWidget(label_save_each)
        hbox_save_each.addWidget(self.spin_save_each)
        
        return hbox_save_each
    
    def draw_each(self):
        label_draw_each = qg.QLabel('Draw each X frame')
        self.spin_draw_each = qg.QSpinBox()
        self.spin_draw_each.setValue(self.game.config['draw_each'])
        self.spin_draw_each.valueChanged[str].connect(self.game.actions.set_draw_each)
        
        # remember connection to restore defaults
        self.ctr_widgets[self.spin_draw_each] = {'widgetname': 'spin_draw_each',
                                                 'def_value': self.game.config['draw_each']}
        
        hbox_draw_each = qg.QHBoxLayout()
        hbox_draw_each.addWidget(label_draw_each)
        hbox_draw_each.addWidget(self.spin_draw_each)
        
        return hbox_draw_each
    
    def invert_colors(self):
        self.checkbox_invert_colors = qg.QCheckBox('Invert colors')
        if self.game.config['invert_colors']:
            self.checkbox_invert_colors.toggle()
        self.checkbox_invert_colors.stateChanged.connect(self.game.actions.set_invert_colors)
        
        # remember connection to restore defaults
        self.ctr_widgets[self.checkbox_invert_colors] = {'widgetname': 'checkbox_invert_colors',
                                                         'def_value': self.game.config['invert_colors']}
        
        hbox_invert_colors = qg.QHBoxLayout()
        hbox_invert_colors.addWidget(self.checkbox_invert_colors)
        
        return hbox_invert_colors

class Owns():
    """Operate controls and actions of own parameters"""
    def __init__(self, game_instance):
        self.game = game_instance
        self.param_widgets = {}
    
    
    def add_own_num(self, name, default, need_to_restart, minimum, maximum, step):
        label = qg.QLabel(name)
        spin = qg.QSpinBox()
        self.param_widgets[spin] = {'name': name,
                                    'default': default,
                                    'need_to_restart': need_to_restart,
                                    'minimum': minimum,
                                    'maximum': maximum,
                                    'step': step}
        
        spin.setValue(default)
        spin.setMinimum(minimum)
        spin.setMaximum(maximum)
        spin.setSingleStep(step)
        
        spin.valueChanged[str].connect(self.num_change)
        
        hbox = qg.QHBoxLayout()
        hbox.addWidget(label)
        hbox.addWidget(spin)
        
        self.game.own_params[name] = default
        self.game.win.layout_ownparams.addLayout(hbox)
    
    def num_change(self):
        sender = self.game.win.sender()
        value = sender.value()
        name = self.param_widgets[sender]['name']
        if self.param_widgets[sender]['need_to_restart']:
            self.game.new_own_params[name] = value
        else:
            self.game.own_params[name] = value

    
    def add_own_bool(self, name, default, need_to_restart):
        checkbox = qg.QCheckBox(name)
        if default:
            checkbox.toggle()
        checkbox.stateChanged.connect(self.bool_change)
        
        self.param_widgets[checkbox] = {'name': name,
                                        'default': default,
                                        'need_to_restart': need_to_restart}
        
        hbox = qg.QHBoxLayout()
        hbox.addWidget(checkbox)
        
        self.game.own_params[name] = default
        self.game.win.layout_ownparams.addLayout(hbox)
    
    def bool_change(self, state):
        sender = self.game.win.sender()
        name = self.param_widgets[sender]['name']
        
        if self.param_widgets[sender]['need_to_restart']:
            if state == qc.Qt.Checked:
                self.game.new_own_params[name] = True
            else:
                self.game.new_own_params[name] = False
        else:
            if state == qc.Qt.Checked:
                self.game.own_params[name] = True
            else:
                self.game.own_params[name] = False
    
    
    def add_own_choice(self, name, default, need_to_restart, choice_list):
        label = qg.QLabel(name)
        combo = qg.QComboBox()
        for item in choice_list:
            combo.addItem(item)
        combo.setCurrentIndex(default)
        combo.activated[str].connect(self.choice_change)
        
        self.param_widgets[combo] = {'name': name,
                                     'default': default,
                                     'need_to_restart': need_to_restart,
                                     'choice_list': choice_list}
        
        hbox = qg.QHBoxLayout()
        hbox.addWidget(label)
        hbox.addWidget(combo)
        
        self.game.own_params[name] = choice_list[default]
        self.game.win.layout_ownparams.addLayout(hbox)
        
    def choice_change(self, text):
        sender = self.game.win.sender()
        name = self.param_widgets[sender]['name']
        
        if self.param_widgets[sender]['need_to_restart']:
            self.game.new_own_params[name] = text
        else:
            self.game.own_params[name] = text
