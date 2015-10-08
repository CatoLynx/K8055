#!/usr/bin/python
# -*- coding: utf-8 -*-
# Graphical frontend to control a stroboscope.
# © 2012 Mezgrman

import k8055_functions as functions
import gobject
import gtk
import os
import pyk8055
import sys
import thread
import time
import traceback

class GUI:
	def __init__(self):
		self.auto_strobe = False
		self.strobe_interval = 1.0
		self.board = pyk8055.k8055(0)
		self.window = gtk.Window()
		self.window.connect('destroy', self.quit)
		self.window.set_title("K8055 stroboscope control panel")
		self.window.set_border_width(10)
		self.window.set_position(gtk.WIN_POS_CENTER_ALWAYS)
		self.icon = self.window.render_icon(gtk.STOCK_PREFERENCES, gtk.ICON_SIZE_MENU)
		self.window.set_icon(self.icon)
		self.build_ui()
	
	def quit(self, widget, data = None):
		gtk.main_quit()
	
	def build_ui(self):
		# Slider and check box for strobe frequency
		self.box_freq = gtk.HBox()
		self.chk_freq = gtk.CheckButton("Automatic")
		self.chk_freq.connect('toggled', self.toggle_callback)
		self.slider_freq = gtk.HScale()
		self.slider_freq.set_range(0.1, 20.0)
		self.slider_freq.connect('value-changed', self.slider_callback)
		self.slider_freq.set_update_policy(gtk.UPDATE_DELAYED)
		self.slider_freq.set_value_pos(gtk.POS_RIGHT)
		self.slider_freq.set_digits(1)
		self.slider_freq.set_value(1.0)
		self.slider_freq.set_size_request(400, -1)
		self.label_freq = gtk.Label("Frequency")
		self.label_freq.set_alignment(0.0, 0.5)
		self.box_freq.pack_start(self.chk_freq, padding = 10)
		self.box_freq.pack_start(self.label_freq, padding = 10)
		self.box_freq.pack_start(self.slider_freq, padding = 10)
		
		# Button for manual strobe
		self.btn_strobe = gtk.Button("Strobe")
		self.btn_strobe.connect('clicked', self.button_callback)
		
		# Main Box
		self.box_main = gtk.VBox()
		self.box_main.pack_start(self.box_freq)
		self.box_main.pack_start(self.btn_strobe)
		
		# Add the box to the window
		self.window.add(self.box_main)
		self.window.show_all()
	
	def button_callback(self, widget, data = None):
		if widget is self.btn_strobe:
			self.strobe()
	
	def toggle_callback(self, widget, data = None):
		state = widget.get_active()
		if widget is self.chk_freq:
			if state:
				self.auto_strobe = True
			else:
				self.auto_strobe = False
	
	def slider_callback(self, widget, data = None):
		value = widget.get_value()
		if widget is self.slider_freq:
			self.strobe_interval = 1.0 / value
	
	def strobe(self):
		self.board.SetDigitalChannel(2)
		time.sleep(0.01)
		self.board.ClearDigitalChannel(2)
	
	def do_strobes(self):
		while True:
			if self.auto_strobe:
				self.strobe()
			time.sleep(self.strobe_interval)

def run():
	gtk.threads_init()
	gui = GUI()
	thread.start_new_thread(gui.do_strobes, ())
	gtk.main()

run()
