#! /usr/bin/env python3
# coding: utf-8
import sys
from PyQt4 import QtGui as qg
from PyQt4 import QtCore as qc
from PyQt4 import QtOpenGL
from OpenGL import GL	# need for nvidia cards
import numpy


class Game():
	'''Creates all classes and config.'''
	def __init__(self, draw_func):
		self.config = self.get_default_config()
		self.newconfig = {}
		
		self.draw_func = draw_func
		self.app = qg.QApplication(sys.argv)
		
		self.field = Field(game_instanse=self)
		self.controls = Controls(game_instanse=self)
		self.actions = Actions(game_instanse=self)
		
		self.win = Window(game_instanse=self)
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
		'''Perform actions that are not takes from config
		on each frame drawing.
		'''
		self.actions.set_name()
		self.actions.set_gl()
		
		sys.exit(self.app.exec_())
		

class Window(qg.QMainWindow):
	'''Creates main widget and set window parameters (title, size etc).'''
	def __init__(self, game_instanse):
		super(Window, self).__init__()
		self.game = game_instanse
		
		self.widget = Widget(game_instanse)
		self.setCentralWidget(self.widget)
		
		self.setWindowTitle(self.game.config['name'])
		self.statusBar()
		self.show()


class Widget(qg.QWidget):
	'''Implements UI in window.'''
	def __init__(self, game_instanse):
		super(Widget, self).__init__()
		self.game = game_instanse
		self.init_ui()
	
	def init_ui(self):
		btn_pause = self.game.controls.button_pause()
		btn_restart = self.game.controls.button_restart()
		self.bottom_btns = qg.QHBoxLayout()		# bottom buttons
		self.bottom_btns.addWidget(btn_pause)
		self.bottom_btns.addWidget(btn_restart)
		
		self.vbox_left = qg.QVBoxLayout()		# left vbox with graphics and buttons
		self.vbox_left.addWidget(self.game.field)
		self.vbox_left.addLayout(self.bottom_btns)
		
		self.vbox_right = qg.QVBoxLayout()		# right vbox with controls
		
		#~ global horizontal box with two vertical boxes
		self.global_hbox = qg.QHBoxLayout()
		self.global_hbox.addLayout(self.vbox_left, 1)
		self.global_hbox.addLayout(self.vbox_right)
		self.setLayout(self.global_hbox)
	
	def init_controls(self, *args):
		if 'resolution' in args:
			hbox_res = self.game.controls.resolution()
			self.vbox_right.addLayout(hbox_res)
		if 'zoom' in args:
			hbox_zoom = self.game.controls.zoom()
			self.vbox_right.addLayout(hbox_zoom)
		if 'background' in args:
			hbox_background = self.game.controls.background()
			self.vbox_right.addLayout(hbox_background)


class Field(qg.QGraphicsView):
	'''QGraphicsView widget. Implements drawing according to
	drawing parameters in self.game.config
	'''
	def __init__(self, game_instanse):
		super(Field, self).__init__()
		self.game = game_instanse
		
		self.scene = qg.QGraphicsScene()
		self.setScene(self.scene)
		
		self.timer=qc.QTimer()						# timer
		self.timer.timeout.connect(self.draw_frame)	# when it triggers, it calls the draw_frame method
		self.timer.start()
	
	def draw_frame(self):
		w = self.game.config['w']
		h = self.game.config['h']
		zoom = self.game.config['zoom']
		
		imdata = self.game.draw_func(w, h)
		imdata = numpy.uint8(imdata)
		
		qimage = qg.QImage(imdata.data, w, h, qg.QImage.Format_RGB888)
		self.qpix = qg.QPixmap(w, h)
		self.qpix.convertFromImage(qimage)
		self.qpix = self.qpix.scaled(self.qpix.size()*zoom, qc.Qt.KeepAspectRatio)
		
		self.scene.clear()
		self.scene.addPixmap(self.qpix)
		

class Actions():
	'''Makes non-drawing changes accordig to config parameters.'''
	def __init__(self, game_instanse):
		self.game = game_instanse
	
	def pause(self):
		if self.game.field.timer.isActive():
			self.game.field.timer.stop()
		else:
			self.game.field.timer.start()
	
	def restart(self):
		config = self.game.config
		newconfig = self.game.newconfig
		
		for key in newconfig:
			config[key] = newconfig[key]
		newconfig = {}
		
		self.game.field.timer.start()
	
	def set_name(self):
		self.game.win.setWindowTitle(self.game.config['name'])
	
	def set_resolution(self):
		sender = self.game.win.sender()
		text = sender.text()
		if sender is self.game.controls.w_lineedit:
			self.game.newconfig['w'] = int(text)
		elif sender is self.game.controls.h_lineedit:
			self.game.newconfig['h'] = int(text)
		else:
			print('oops!')
	
	def set_zoom(self):
		zoom_factor = self.game.win.sender().value()
		self.game.newconfig['zoom'] = zoom_factor
	
	def set_background(self):
		col = qg.QColorDialog.getColor()
		if col.isValid():
			color = ...		# TODO: convert col to (255, 255, 255) format
			self.game.config['background'] = color
	
	def set_gl(self):
		if self.game.config['gl']:
			self.game.field.setViewport(QtOpenGL.QGLWidget())
		else:
			self.game.field.setViewport(qg.QWidget())


class Controls():
	'''Contains base hboxes, connects them with actions
	and adds to vbox_right.
	'''
	def __init__(self, game_instanse):
		self.game = game_instanse
	
	def button_pause(self):
		btn_pause = qg.QPushButton('Pause/Play')
		btn_pause.clicked.connect(self.game.actions.pause)
		return btn_pause
	
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
		spin_zoom.valueChanged[str].connect(self.game.actions.set_zoom)		# str?
		
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
