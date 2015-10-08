#!/usr/bin/python
# -*- coding: utf-8 -*-
# Graphical frontend to read and write data from / to the K8055 or K8055N.
# © 2012 Mezgrman

import k8055_functions as functions
import gobject
import gtk
import os
import pyk8055
import time

class NumberEntry(gtk.Entry):
	def __init__(self):
		super(NumberEntry, self).__init__()
		self.connect('changed', self.on_changed)
	
	def on_changed(self, *args):
		text = self.get_text().strip()
		self.set_text("".join([i for i in text if i in "-0123456789"]))

class GUI:
	def __init__(self):
		self.board = pyk8055.k8055(0)
		self.window = gtk.Window()
		self.window.connect('destroy', self.quit)
		self.window.set_title("K8055 control panel")
		self.window.set_border_width(10)
		self.window.set_position(gtk.WIN_POS_CENTER_ALWAYS)
		self.icon = self.window.render_icon(gtk.STOCK_PREFERENCES, gtk.ICON_SIZE_MENU)
		self.window.set_icon(self.icon)
		self.build_ui()
		gtk.timeout_add(100, self.update_from_board)
	
	def quit(self, widget, data = None):
		gtk.main_quit()
	
	def build_ui(self):
		# Gauge for analog input 1
		self.box_ai1 = gtk.VBox()
		self.gauge_ai1 = gtk.ProgressBar()
		self.gauge_ai1.set_text("0")
		self.gauge_ai1.set_orientation(gtk.PROGRESS_BOTTOM_TO_TOP)
		self.gauge_ai1.set_size_request(25, 150)
		self.label_ai1 = gtk.Label("Analog 1")
		self.box_ai1.pack_start(self.gauge_ai1)
		self.box_ai1.pack_start(self.label_ai1)
		
		# Gauge for analog input 2
		self.box_ai2 = gtk.VBox()
		self.gauge_ai2 = gtk.ProgressBar()
		self.gauge_ai2.set_text("0")
		self.gauge_ai2.set_orientation(gtk.PROGRESS_BOTTOM_TO_TOP)
		self.gauge_ai2.set_size_request(25, 150)
		self.label_ai2 = gtk.Label("Analog 2")
		self.box_ai2.pack_start(self.gauge_ai2)
		self.box_ai2.pack_start(self.label_ai2)
		
		# Label for counter 1
		self.box_c1 = gtk.HBox()
		self.label_c1 = gtk.Label("Counter 1")
		self.label_c1.set_alignment(0.0, 0.5)
		self.value_c1 = gtk.Label("0")
		self.value_c1.set_alignment(1.0, 0.5)
		self.box_c1.pack_start(self.label_c1, padding = 10)
		self.box_c1.pack_start(self.value_c1, padding = 10)
		
		# Label for counter 2
		self.box_c2 = gtk.HBox()
		self.label_c2 = gtk.Label("Counter 2")
		self.label_c2.set_alignment(0.0, 0.5)
		self.value_c2 = gtk.Label("0")
		self.value_c2.set_alignment(1.0, 0.5)
		self.box_c2.pack_start(self.label_c2, padding = 10)
		self.box_c2.pack_start(self.value_c2, padding = 10)
		
		# Extra container to keep the counter labels together
		self.box_counters = gtk.VBox()
		self.box_counters.pack_start(self.box_c1, expand = False)
		self.box_counters.pack_start(self.box_c2, expand = False)
		
		# Label for digital input 1
		self.box_di1 = gtk.HBox()
		self.label_di1 = gtk.Label("Digital 1")
		self.label_di1.set_alignment(0.0, 0.5)
		self.value_di1 = gtk.Label(" Low")
		self.value_di1.set_sensitive(False)
		self.value_di1.set_alignment(1.0, 0.5)
		self.box_di1.pack_start(self.label_di1, padding = 10)
		self.box_di1.pack_start(self.value_di1, padding = 10)
		
		# Label for digital input 2
		self.box_di2 = gtk.HBox()
		self.label_di2 = gtk.Label("Digital 2")
		self.label_di2.set_alignment(0.0, 0.5)
		self.value_di2 = gtk.Label(" Low")
		self.value_di2.set_sensitive(False)
		self.value_di2.set_alignment(1.0, 0.5)
		self.box_di2.pack_start(self.label_di2, padding = 10)
		self.box_di2.pack_start(self.value_di2, padding = 10)
		
		# Label for digital input 3
		self.box_di3 = gtk.HBox()
		self.label_di3 = gtk.Label("Digital 3")
		self.label_di3.set_alignment(0.0, 0.5)
		self.value_di3 = gtk.Label(" Low")
		self.value_di3.set_sensitive(False)
		self.value_di3.set_alignment(1.0, 0.5)
		self.box_di3.pack_start(self.label_di3, padding = 10)
		self.box_di3.pack_start(self.value_di3, padding = 10)
		
		# Label for digital input 4
		self.box_di4 = gtk.HBox()
		self.label_di4 = gtk.Label("Digital 4")
		self.label_di4.set_alignment(0.0, 0.5)
		self.value_di4 = gtk.Label(" Low")
		self.value_di4.set_sensitive(False)
		self.value_di4.set_alignment(1.0, 0.5)
		self.box_di4.pack_start(self.label_di4, padding = 10)
		self.box_di4.pack_start(self.value_di4, padding = 10)
		
		# Label for digital input 5
		self.box_di5 = gtk.HBox()
		self.label_di5 = gtk.Label("Digital 5")
		self.label_di5.set_alignment(0.0, 0.5)
		self.value_di5 = gtk.Label(" Low")
		self.value_di5.set_sensitive(False)
		self.value_di5.set_alignment(1.0, 0.5)
		self.box_di5.pack_start(self.label_di5, padding = 10)
		self.box_di5.pack_start(self.value_di5, padding = 10)
		
		# Extra container to keep the digital input labels together
		self.box_digital_inputs = gtk.VBox()
		self.box_digital_inputs.pack_start(self.box_di1, expand = False)
		self.box_digital_inputs.pack_start(self.box_di2, expand = False)
		self.box_digital_inputs.pack_start(self.box_di3, expand = False)
		self.box_digital_inputs.pack_start(self.box_di4, expand = False)
		self.box_digital_inputs.pack_start(self.box_di5, expand = False)
		
		# Vertical box for the non-analog inputs
		self.box_more_inputs = gtk.VBox()
		self.box_more_inputs.pack_start(self.box_counters)
		self.box_more_inputs.pack_start(self.box_digital_inputs)
		
		# Horizontal box for all inputs
		self.box_input = gtk.HBox()
		self.box_input.pack_start(self.box_ai1, padding = 10)
		self.box_input.pack_start(self.box_ai2, padding = 10)
		self.box_input.pack_start(self.box_more_inputs, padding = 10)
		
		# Extra box to add vertical padding to the inputs
		self.padding_input = gtk.VBox()
		self.padding_input.pack_start(self.box_input, padding = 10)
		
		# Frame for the inputs
		self.frame_input = gtk.Frame(label = "Inputs")
		self.frame_input.add(self.padding_input)
		
		# Checkboxes for digital outputs
		self.btn_do1 = gtk.CheckButton("Digital 1")
		self.btn_do1.connect('toggled', self.toggle_callback)
		self.btn_do2 = gtk.CheckButton("Digital 2")
		self.btn_do2.connect('toggled', self.toggle_callback)
		self.btn_do3 = gtk.CheckButton("Digital 3")
		self.btn_do3.connect('toggled', self.toggle_callback)
		self.btn_do4 = gtk.CheckButton("Digital 4")
		self.btn_do4.connect('toggled', self.toggle_callback)
		self.btn_do5 = gtk.CheckButton("Digital 5")
		self.btn_do5.connect('toggled', self.toggle_callback)
		self.btn_do6 = gtk.CheckButton("Digital 6")
		self.btn_do6.connect('toggled', self.toggle_callback)
		self.btn_do7 = gtk.CheckButton("Digital 7")
		self.btn_do7.connect('toggled', self.toggle_callback)
		self.btn_do8 = gtk.CheckButton("Digital 8")
		self.btn_do8.connect('toggled', self.toggle_callback)
		
		# Extra container to keep the digital output checkboxes together
		self.box_digital_outputs = gtk.VBox()
		self.box_digital_outputs.pack_start(self.btn_do1, expand = False)
		self.box_digital_outputs.pack_start(self.btn_do2, expand = False)
		self.box_digital_outputs.pack_start(self.btn_do3, expand = False)
		self.box_digital_outputs.pack_start(self.btn_do4, expand = False)
		self.box_digital_outputs.pack_start(self.btn_do5, expand = False)
		self.box_digital_outputs.pack_start(self.btn_do6, expand = False)
		self.box_digital_outputs.pack_start(self.btn_do7, expand = False)
		self.box_digital_outputs.pack_start(self.btn_do8, expand = False)
		
		# Slider for analog output 1
		self.box_ao1 = gtk.HBox()
		self.slider_ao1 = gtk.HScale()
		self.slider_ao1.set_range(0, 255)
		self.slider_ao1.connect('value-changed', self.slider_callback)
		self.slider_ao1.set_update_policy(gtk.UPDATE_DELAYED)
		self.slider_ao1.set_value_pos(gtk.POS_RIGHT)
		self.slider_ao1.set_digits(0)
		self.slider_ao1.set_size_request(400, -1)
		self.label_ao1 = gtk.Label("Analog 1")
		self.label_ao1.set_alignment(0.0, 0.5)
		self.box_ao1.pack_start(self.label_ao1, padding = 10)
		self.box_ao1.pack_start(self.slider_ao1, padding = 10)
		
		# Slider for analog output 2
		self.box_ao2 = gtk.HBox()
		self.slider_ao2 = gtk.HScale()
		self.slider_ao2.set_range(0, 255)
		self.slider_ao2.connect('value-changed', self.slider_callback)
		self.slider_ao2.set_update_policy(gtk.UPDATE_DELAYED)
		self.slider_ao2.set_value_pos(gtk.POS_RIGHT)
		self.slider_ao2.set_digits(0)
		self.slider_ao2.set_size_request(400, -1)
		self.label_ao2 = gtk.Label("Analog 2")
		self.label_ao2.set_alignment(0.0, 0.5)
		self.box_ao2.pack_start(self.label_ao2, padding = 10)
		self.box_ao2.pack_start(self.slider_ao2, padding = 10)
		
		# Extra container to keep the analog output sliders together
		self.box_analog_outputs = gtk.VBox()
		self.box_analog_outputs.pack_start(self.box_ao1, expand = False)
		self.box_analog_outputs.pack_start(self.box_ao2, expand = False)
		
		# Slider for counter 1 debounce time
		self.box_dtc1 = gtk.HBox()
		self.slider_dtc1 = gtk.HScale()
		self.slider_dtc1.set_range(1, 1000) # Possible maximum value is 7450
		self.slider_dtc1.connect('value-changed', self.slider_callback)
		self.slider_dtc1.set_update_policy(gtk.UPDATE_DISCONTINUOUS)
		self.slider_dtc1.set_value_pos(gtk.POS_RIGHT)
		self.slider_dtc1.set_digits(0)
		self.slider_dtc1.set_size_request(400, -1)
		self.label_dtc1 = gtk.Label("Counter 1 debounce time (ms)")
		self.label_dtc1.set_alignment(0.0, 0.5)
		self.box_dtc1.pack_start(self.label_dtc1, padding = 10)
		self.box_dtc1.pack_start(self.slider_dtc1, padding = 10)
		
		# Slider for counter 2 debounce time
		self.box_dtc2 = gtk.HBox()
		self.slider_dtc2 = gtk.HScale()
		self.slider_dtc2.set_range(1, 1000) # Possible maximum value is 7450
		self.slider_dtc2.connect('value-changed', self.slider_callback)
		self.slider_dtc2.set_update_policy(gtk.UPDATE_DISCONTINUOUS)
		self.slider_dtc2.set_value_pos(gtk.POS_RIGHT)
		self.slider_dtc2.set_digits(0)
		self.slider_dtc2.set_size_request(400, -1)
		self.label_dtc2 = gtk.Label("Counter 2 debounce time (ms)")
		self.label_dtc2.set_alignment(0.0, 0.5)
		self.box_dtc2.pack_start(self.label_dtc2, padding = 10)
		self.box_dtc2.pack_start(self.slider_dtc2, padding = 10)
		
		# Extra container to keep the counter debounce time sliders together
		self.box_debounce_times = gtk.VBox()
		self.box_debounce_times.pack_start(self.box_dtc1, expand = False)
		self.box_debounce_times.pack_start(self.box_dtc2, expand = False)
		
		# Value setting widgets
		self.box_value_setting = gtk.HBox()
		self.entry_value = NumberEntry()
		self.entry_value.set_size_request(100, -1)
		self.btn_set_value_digital = gtk.Button("Set digital outputs to binary representation")
		self.btn_set_value_digital.connect('clicked', self.button_callback)
		self.box_value_setting.pack_start(self.entry_value, expand = False)
		self.box_value_setting.pack_start(self.btn_set_value_digital)
		
		# Reset buttons
		self.box_reset_buttons = gtk.HBox()
		self.btn_reset_c1 = gtk.Button("Reset counter 1")
		self.btn_reset_c1.connect('clicked', self.button_callback)
		self.btn_reset_c2 = gtk.Button("Reset counter 2")
		self.btn_reset_c2.connect('clicked', self.button_callback)
		self.btn_reset_outputs = gtk.Button("Reset outputs")
		self.btn_reset_outputs.connect('clicked', self.button_callback)
		self.box_reset_buttons.pack_start(self.btn_reset_c1)
		self.box_reset_buttons.pack_start(self.btn_reset_c2)
		self.box_reset_buttons.pack_start(self.btn_reset_outputs)
		
		# Animation buttons
		self.box_animation_buttons = gtk.HBox()
		self.btn_anim1 = gtk.Button("Animation 1")
		self.btn_anim1.connect('clicked', self.button_callback)
		self.btn_anim2 = gtk.Button("Animation 2")
		self.btn_anim2.connect('clicked', self.button_callback)
		self.btn_anim3 = gtk.Button("Animation 3")
		self.btn_anim3.connect('clicked', self.button_callback)
		self.btn_anim4 = gtk.Button("Animation 4")
		self.btn_anim4.connect('clicked', self.button_callback)
		self.box_animation_buttons.pack_start(self.btn_anim1)
		self.box_animation_buttons.pack_start(self.btn_anim2)
		self.box_animation_buttons.pack_start(self.btn_anim3)
		self.box_animation_buttons.pack_start(self.btn_anim4)
		
		# Vertical box for the rest of the outputs
		self.box_more_outputs = gtk.VBox()
		self.box_more_outputs.pack_start(self.box_analog_outputs)
		self.box_more_outputs.pack_start(self.box_debounce_times)
		self.box_more_outputs.pack_start(self.box_value_setting, expand = False)
		self.box_more_outputs.pack_start(self.box_reset_buttons, expand = False)
		self.box_more_outputs.pack_start(self.box_animation_buttons, expand = False)
		
		# Horizontal box for all outputs
		self.box_output = gtk.HBox()
		self.box_output.pack_start(self.box_digital_outputs, padding = 10)
		self.box_output.pack_start(self.box_more_outputs, padding = 10)
		
		# Extra box to add vertical padding to the outputs
		self.padding_output = gtk.VBox()
		self.padding_output.pack_start(self.box_output, padding = 10)
		
		# Frame for the outputs
		self.frame_output = gtk.Frame(label = "Outputs")
		self.frame_output.add(self.padding_output)
		
		# Main horizontal box
		self.box_main = gtk.HBox(spacing = 10)
		self.box_main.pack_start(self.frame_input)
		self.box_main.pack_start(self.frame_output)
		
		# Add the box to the window
		self.window.add(self.box_main)
		self.window.show_all()
	
	def button_callback(self, widget, data = None):
		if widget is self.btn_reset_c1:
			self.board.ResetCounter(1)
		elif widget is self.btn_reset_c2:
			self.board.ResetCounter(2)
		elif widget is self.btn_reset_outputs:
			self.board.ClearAllDigital()
			self.board.ClearAllAnalog()
			self.update(do1 = False, do2 = False, do3 = False, do4 = False, do5 = False, do6 = False, do7 = False, do8 = False, ao1 = 0, ao2 = 0)
		elif widget is self.btn_set_value_digital:
			text = self.entry_value.get_text()
			if len(text) == 0:
				return
			mask = int(text)
			self.board.WriteAllDigital(mask)
			do = functions.mask_to_bool_list(mask, bits = 8)
			self.update(do1 = do[0], do2 = do[1], do3 = do[2], do4 = do[3], do5 = do[4], do6 = do[5], do7 = do[6], do8 = do[7])
		elif widget is self.btn_anim1:
			functions.animate(self.board, ["10000000", "01000000", "00100000", "00010000", "00001000", "00000100", "00000010", "00000001", "00000010", "00000100", "00001000", "00010000", "00100000", "01000000", "10000000"])
		elif widget is self.btn_anim2:
			functions.animate(self.board, ["10000001", "01000010", "00100100", "00011000", "00100100", "01000010", "10000001"])
		elif widget is self.btn_anim3:
			functions.animate(self.board, ["00011000", "00100100", "01000010", "10000001", "01000010", "00100100", "00011000"])
		elif widget is self.btn_anim4:
			functions.animate(self.board, ["01010101", "10101010", "01010101", "10101010", "01010101", "10101010", "01010101", "10101010", "01010101", "10101010", "01010101", "10101010", "01010101", "10101010", "01010101", "10101010"], 250)
	
	def toggle_callback(self, widget, data = None):
		state = widget.get_active()
		if widget is self.btn_do1:
			if state:
				self.board.SetDigitalChannel(1)
			else:
				self.board.ClearDigitalChannel(1)
		elif widget is self.btn_do2:
			if state:
				self.board.SetDigitalChannel(2)
			else:
				self.board.ClearDigitalChannel(2)
		elif widget is self.btn_do3:
			if state:
				self.board.SetDigitalChannel(3)
			else:
				self.board.ClearDigitalChannel(3)
		elif widget is self.btn_do4:
			if state:
				self.board.SetDigitalChannel(4)
			else:
				self.board.ClearDigitalChannel(4)
		elif widget is self.btn_do5:
			if state:
				self.board.SetDigitalChannel(5)
			else:
				self.board.ClearDigitalChannel(5)
		elif widget is self.btn_do6:
			if state:
				self.board.SetDigitalChannel(6)
			else:
				self.board.ClearDigitalChannel(6)
		elif widget is self.btn_do7:
			if state:
				self.board.SetDigitalChannel(7)
			else:
				self.board.ClearDigitalChannel(7)
		elif widget is self.btn_do8:
			if state:
				self.board.SetDigitalChannel(8)
			else:
				self.board.ClearDigitalChannel(8)
	
	def slider_callback(self, widget, data = None):
		value = int(widget.get_value())
		if widget is self.slider_ao1:
			self.board.OutputAnalogChannel(1, value)
		elif widget is self.slider_ao2:
			self.board.OutputAnalogChannel(2, value)
		if widget is self.slider_dtc1:
			self.board.SetCounterDebounceTime(1, value)
		if widget is self.slider_dtc2:
			self.board.SetCounterDebounceTime(2, value)
	
	def update(self, ai1 = None, ai2 = None, c1 = None, c2 = None, di1 = None, di2 = None, di3 = None, di4 = None, di5 = None, do1 = None, do2 = None, do3 = None, do4 = None, do5 = None, do6 = None, do7 = None, do8 = None, ao1 = None, ao2 = None, dtc1 = None, dtc2 = None, value = None):
		if ai1 is not None:
			self.gauge_ai1.set_fraction(float(ai1) / 255.0)
			self.gauge_ai1.set_text(str(ai1))
		if ai2 is not None:
			self.gauge_ai2.set_fraction(float(ai2) / 255.0)
			self.gauge_ai2.set_text(str(ai2))
		if c1 is not None:
			self.value_c1.set_text(str(c1))
		if c2 is not None:
			self.value_c2.set_text(str(c2))
		if di1 is not None:
			self.value_di1.set_text("High" if di1 else " Low")
			self.value_di1.set_sensitive(di1)
		if di2 is not None:
			self.value_di2.set_text("High" if di2 else " Low")
			self.value_di2.set_sensitive(di2)
		if di3 is not None:
			self.value_di3.set_text("High" if di3 else " Low")
			self.value_di3.set_sensitive(di3)
		if di4 is not None:
			self.value_di4.set_text("High" if di4 else " Low")
			self.value_di4.set_sensitive(di4)
		if di5 is not None:
			self.value_di5.set_text("High" if di5 else " Low")
			self.value_di5.set_sensitive(di5)
		if do1 is not None:
			self.btn_do1.set_active(do1)
		if do2 is not None:
			self.btn_do2.set_active(do2)
		if do3 is not None:
			self.btn_do3.set_active(do3)
		if do4 is not None:
			self.btn_do4.set_active(do4)
		if do5 is not None:
			self.btn_do5.set_active(do5)
		if do6 is not None:
			self.btn_do6.set_active(do6)
		if do7 is not None:
			self.btn_do7.set_active(do7)
		if do8 is not None:
			self.btn_do8.set_active(do8)
		if ao1 is not None:
			self.slider_ao1.set_value(int(ao1))
		if ao2 is not None:
			self.slider_ao2.set_value(int(ao2))
		if dtc1 is not None:
			self.slider_dtc1.set_value(int(dtc1))
		if dtc2 is not None:
			self.slider_dtc2.set_value(int(dtc2))
		if value is not None:
			self.entry_value.set_text(str(value))
		return True
	
	def update_from_board(self):
		values = self.board.ReadAllValues()
		di = functions.mask_to_bool_list(values[1])
		return self.update(ai1 = values[2], ai2 = values[3], c1 = values[4], c2 = values[5], di1 = di[0], di2 = di[1], di3 = di[2], di4 = di[3], di5 = di[4])

def run():
	gui = GUI()
	gui.update(dtc1 = 20, dtc2 = 20)
	gtk.main()

run()
