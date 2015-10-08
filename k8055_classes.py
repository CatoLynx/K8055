#!/usr/bin/env python
# -*- coding: utf-8 -*-

from k8055_functions import *
# import pygst
# pygst.require("0.10")
# import gst
# import gobject
import sys
import thread
import time
import os
import re
# from PIL import Image
import wiringpi

class K8055StepperMotorController:
	def __init__(self, board, coil_count = 4, steps_per_revolution = 48):
		self.board = board
		self.coil_count = coil_count
		self.steps_per_revolution = steps_per_revolution
		self.steps_in = 0
		self.last_coil = 1
		self.reset()
	
	def reset(self):
		self.board.ClearAllDigital()
		if self.steps_in <= self.steps_per_revolution / 2:
			self.rotate(self.steps_in, ccw = True, delay = 0.04)
		else:
			self.rotate(self.steps_per_revolution - self.steps_in, delay = 0.04)
	
	def coil_impulse(self, coil, delay = 0.00625):
		self.board.SetDigitalChannel(coil)
		time.sleep(delay)
		self.board.ClearDigitalChannel(coil)
	
	def step(self, ccw = False, delay = 0.00625):
		if ccw:
			if self.last_coil == self.coil_count:
				next_coil = 1
			else:
				next_coil = self.last_coil + 1
			if self.steps_in == 0:
				self.steps_in = self.steps_per_revolution - 1
			else:
				self.steps_in -= 1
		else:
			if self.last_coil == 1:
				next_coil = self.coil_count
			else:
				next_coil = self.last_coil - 1
			if self.steps_in == self.steps_per_revolution - 1:
				self.steps_in = 0
			else:
				self.steps_in += 1
		self.coil_impulse(next_coil, delay)
		self.last_coil = next_coil
	
	def rotate(self, count = 1, ccw = False, delay = 0.00625):
		for i in range(count):
			self.step(ccw, delay)
	
	def rotate_to(self, position, ccw = False, auto = True, delay = 0.00625):
		if position == 0:
			position = self.steps_per_revolution
		position = divmod(position, self.steps_per_revolution)[1]
		if position == self.steps_in:
			return
		if auto:
			if position < self.steps_in:
				ccw = True
			else:
				ccw = False
		if not ccw:
			if position < self.steps_in:
				steps = self.steps_per_revolution - abs(position - self.steps_in)
			else:
				steps = abs(position - self.steps_in)
		else:
			if position > self.steps_in:
				steps = self.steps_per_revolution - abs(position - self.steps_in)
			else:
				steps = abs(position - self.steps_in)
		self.rotate(steps, ccw, delay)
	
	def revolution(self, timespan = 1.0, ccw = False):
		self.rotate(self.steps_per_revolution, ccw, delay = float(timespan) / self.steps_per_revolution)

class K8055IncrementalEncoder:
	def __init__(self, board):
		self.board = board
		self.exit_loop = False
		self.reset()
	
	def reset(self):
		self.board.ClearAllDigital()
		self.board.ClearAllAnalog()
	
	def event_loop(self):
		last_inputs = [False, False]
		changes = [False, False]
		while not self.exit_loop:
			inputs = mask_to_bool_list(self.board.ReadAllValues()[1])[:2]
			if inputs != last_inputs:
				changes = [inputs[0] != last_inputs[0], inputs[1] != last_inputs[1]]
				self.exit_loop = not self.on_change(changes)
				ccw = None
				tick = None
				if last_inputs == [False, False] and inputs == [True, False]:
					ccw = True
					tick = False
				elif last_inputs == [True, False] and inputs == [True, True]:
					ccw = True
					tick = True
				elif last_inputs == [True, True] and inputs == [False, False]:
					ccw = True
					tick = True
				elif last_inputs == [False, False] and inputs == [True, True]:
					ccw = False
					tick = True
				elif last_inputs == [True, True] and inputs == [True, False]:
					ccw = False
					tick = False
				elif last_inputs == [True, False] and inputs == [False, False]:
					ccw = False
					tick = True
				if tick:
					self.exit_loop = not self.on_rotate(ccw)
				last_inputs = inputs[:]
	
	def on_change(self, changes):
		return True
	
	def on_rotate(self, ccw):
		return True

class K8055MatrixDisplayController:
	def __init__(self, board, pixmap = {}, iconmap = {}):
		self.board = board
		self.pixmap = pixmap
		self.iconmap = iconmap
		self.reset()
	
	def stop(self):
		self.board.ClearAllDigital()
		self.reset()
	
	def reset(self):
		self.board.SetDigitalChannel(1)
		self.board.ClearDigitalChannel(1)
	
	def next_row(self):
		self.board.SetDigitalChannel(2)
		self.board.ClearDigitalChannel(2)
	
	def update(self, outputs):
		exit = False
		row = 1
		while True:
			if row == len(outputs) + 1:
				row = 1
				exit = True
				actual_outputs = [1] + outputs[row - 1]
			else:
				actual_outputs = [2] + outputs[row - 1]
				row += 1
			self.board.ClearAllDigital()
			self.board.WriteAllDigital(list_to_mask(actual_outputs))
			if exit:
				break
	
	def write_char(self, char):
		try:
			outputs = [[pixel + 2 for pixel in row] for row in self.pixmap[char]]
		except KeyError:
			try:
				outputs = [[pixel + 2 for pixel in row] for row in self.pixmap[char.upper()]]
			except KeyError:
				return False
		return self.update(outputs)
	
	def write_text(self, text, cycles = 20):
		for find, replace in self.iconmap:
			text = text.replace(find, replace)
		for char in text:
			count = 0
			while count < cycles:
				self.write_char(char)
				count += 1

class AudioSpectrum:
	def __init__(self, interval = 15000000, threshold = -60, bands = 8):
		self.interval = interval
		self.threshold = threshold
		self.bands = bands
		listener_desc = 'pulsesrc device="alsa_output.pci-0000_00_07.0.analog-stereo.monitor" ! spectrum interval=%i threshold=%i bands=%i ! fakesink' % (self.interval, self.threshold, self.bands)
		self.listener = gst.parse_launch(listener_desc)
		bus = self.listener.get_bus()
		bus.add_signal_watch()
		bus.connect('message', self.on_message)
 
	def on_message(self, bus, message):
		return True
 
	def _run(self):
		self.listener.set_state(gst.STATE_PLAYING)
		while True:
			time.sleep(1)
	
	def start(self):
		thread.start_new_thread(self._run, ())
		gobject.threads_init()
		loop = gobject.MainLoop()
		loop.run()

class K8055MatrixKeypad:
	def __init__(self, board, cols, rows, keymap = None):
		self.board = board
		self.cols = cols
		self.rows = rows
		self.keymap = keymap
		self.loop = False
		self.reset()
	
	def reset(self):
		self.board.ClearAllDigital()
	
	def get_key(self, col, row):
		if self.keymap:
			return self.keymap[row][col]
		return "%i,%i" % (col + 1, row + 1)
	
	def get_keys(self, keys):
		key_values = []
		for y in range(len(keys)):
			row = keys[y]
			for x in range(len(row)):
				col = row[x]
				if col:
					key_values.append(self.get_key(x, y))
		return key_values
	
	def scan_keypad(self):
		keys = []
		for i in range(self.rows):
			self.board.SetDigitalChannel(i + 2)
			columns = self.scan_columns()
			keys.append(columns)
			self.board.ClearDigitalChannel(i + 2)
		return keys
	
	def scan_columns(self):
		columns = mask_to_bool_list(self.board.ReadAllDigital())[:self.cols]
		return columns
	
	def read_keys(self):
		return self.get_keys(self.scan_keypad())
	
	def read_loop(self, new_only = True):
		old_keys = []
		self.loop = True
		while self.loop:
			keys = self.read_keys()
			if new_only and keys == old_keys:
				continue
			new_keys = [key for key in keys if key not in old_keys] if new_only else keys
			for key in new_keys:
				self.loop = self.on_keys(new_keys)
			old_keys = keys[:]
	
	def on_keys(self, keys):
		return True

class K8055Stroboscope:
	def __init__(self, board, channel = 1):
		self.board = board
		self.channel = channel
		self.duration_multiplier = 1.0
		self.reset()
		self.get_duration_multiplier()
	
	def reset(self):
		self.board.ClearAllDigital()
	
	def get_duration_multiplier(self):
		self.duration_multiplier = self.board.ReadAnalogChannel(1) / 127.0
	
	def strobe(self):
		self.board.SetDigitalChannel(self.channel)
		self.board.ClearDigitalChannel(self.channel)
	
	def strobe_pattern(self, pattern):
		self.get_duration_multiplier()
		for item in pattern.split(","):
			self.strobe()
			try:
				time.sleep((1.0 / float(item)) * self.duration_multiplier)
			except KeyboardInterrupt:
				break
			except:
				pass

class K8055VFDController:
	# SANYO LC75712 chip
	
	def __init__(self, board):
		self.DI = 2
		self.CL = 3
		self.CE = 4
		self.RES = 5
		self.CHIP_ADDRESS = 0xE6
		self.RIGHT = "0"
		self.LEFT = "1"
		
		self.board = board
		self.board.ClearAllDigital()
		self.disable(self.DI)
		self.disable(self.CL)
		self.disable(self.CE)
		self.disable(self.RES)
		self.enable(self.RES)
		self.dcram_write(0x4F, 0x00)
		self.set_grid_count(9)
		self.set_intensity(255)
		self.set_state(state = "1")
	
	def shutdown(self):
		self.set_state(state = "0")
	
	def reverse(self, string):
		return "".join(reversed(string))
	
	def num_to_bits(self, num, digits = -1, reverse = False):
		bits = bin(num)[2:]
		if digits != -1:
			bits = (("%%%is" % digits) % bits).replace(" ", "0")
		if reverse:
			bits = self.reverse(bits)
		return bits
	
	def enable(self, output):
		self.board.SetDigitalChannel(output)
	
	def disable(self, output):
		self.board.ClearDigitalChannel(output)
	
	def pulse(self, output):
		self.enable(output)
		self.disable(output)
	
	def send_bits(self, bits, hexa = False):
		if hexa:
			bits = self.num_to_bits(bits)
		for bit in bits:
			sys.stdout.write(bit)
			if bit == "1":
				self.enable(self.DI)
			self.pulse(self.CL)
			self.disable(self.DI)
		sys.stdout.write("\n")
		sys.stdout.flush()
	
	def instruction(self, bits):
		self.disable(self.CE)
		self.send_bits(self.CHIP_ADDRESS, hexa = True)
		self.enable(self.CE)
		self.send_bits(bits)
		self.disable(self.CE)
	
	def blink(self, grids = "1111111111111111", speed = 7, adata = "1", mdata = "1"):
		return self.instruction(grids + self.num_to_bits(speed, digits = 3, reverse = True) + adata + mdata + "101")
	
	def set_state(self, grids = "1111111111111111", state = "1", adata = "1", mdata = "1"):
		return self.instruction(grids + state + adata + mdata + "01000")
	
	def shift(self, direction = "1", adata = "1", mdata = "1"):
		return self.instruction("0000000000000000" + direction + adata + mdata + "00100")
	
	def set_grid_count(self, count = 16):
		if count == 16:
			count = 0
		return self.instruction("0000000000000000" + self.num_to_bits(count, digits = 4, reverse = True) + "1100")
	
	def set_ac_address(self, dcram_address = 0x00, adram_address = 0x00):
		return self.instruction("00000000" + self.num_to_bits(dcram_address, digits = 6, reverse = True) + "00" + self.num_to_bits(adram_address, digits = 4, reverse = True) + "0010")
	
	def set_intensity(self, intensity = 255):
		return self.instruction("00000000" + self.num_to_bits(intensity, digits = 8, reverse = True) + "00001010")
	
	def dcram_write(self, character_code, address):
		return self.instruction(self.num_to_bits(character_code, digits = 8, reverse = True) + self.num_to_bits(address, digits = 6, reverse = True) + "0000000110")
	
	def adram_write(self, dots, address):
		return self.instruction("00000000" + dots + self.num_to_bits(address, digits = 4, reverse = True) + "1110")
	
	def cgram_write(self, dots, address):
		return self.instruction(dots + "00000" + self.num_to_bits(address, digits = 8, reverse = True) + "00000001")

class K80554BitLCDController:
	PINMAP = {
		'RS': 1,
		'RW': 2,
		'E': 3,
		'D4': 4,
		'D5': 5,
		'D6': 6,
		'D7': 7,
		'LED': 1,
	}
	
	CONTROL_CHARACTERS = (0x0D, 0x18, 0x1B, 0x7F)
	
	def __init__(self, board = None, pinmap = PINMAP, charmap = None, lines = 2, columns = 16, characters = 40, skip_init = False, debug = False):
		self.board = board
		self.brightness = 0
		self.debug = debug
		self.line_count = lines
		self.column_count = columns
		self.character_count = characters
		self.max_chars_per_line = self.character_count / self.line_count
		self.lines = ("", "")
		self.cursor_pos = [0, 0]
		self.reverse_pinmap = dict([(value, key) for key, value in pinmap.iteritems()])
		if not self.board:
			self.gpio = wiringpi.GPIO(wiringpi.GPIO.WPI_MODE_GPIO)
		for pin, output in pinmap.iteritems():
			setattr(self, 'PIN_%s' % pin, output)
			if not self.board:
				self.gpio.pinMode(output, self.gpio.PWM_OUTPUT if pin == 'LED' else self.gpio.OUTPUT)
		self.all_low()
		self.set_brightness(1023)
		if not skip_init:
			self.initialize()
			if charmap:
				if 'dir' in charmap:
					files = os.listdir(charmap['dir'])
					for filename in files:
						charmap[int(filename.split(".")[0], 16)] = open(os.path.join(charmap['dir'], filename), 'rb')
					del charmap['dir']
				for pos, char in charmap.iteritems():
					self.load_custom_character(pos, char)
				self.set_cursor_position()
	
	def shutdown(self):
		self.all_low()
		self.set_brightness(0)
	
	def high(self, output):
		if self.debug:
			print "Enabling  %s" % self.reverse_pinmap[output]
		if self.board:
			self.board.SetDigitalChannel(output)
		else:
			self.gpio.digitalWrite(output, True)
	
	def low(self, output):
		if self.debug:
			print "Disabling %s" % self.reverse_pinmap[output]
		if self.board:
			self.board.ClearDigitalChannel(output)
		else:
			self.gpio.digitalWrite(output, False)
	
	def pulse(self, output):
		self.high(output)
		self.low(output)
	
	def all_low(self):
		if self.board:
			self.board.ClearAllDigital()
		else:
			for output in self.reverse_pinmap.keys():
				self.low(output)
	
	def set_brightness(self, level):
		assert level >= 0
		assert level <= 1023
		self.brightness = level
		if self.board:
			level = int(level * (255.0 / 1023.0))
			self.board.OutputAnalogChannel(self.PIN_LED, level)
		else:
			self.gpio.pwmWrite(self.PIN_LED, level)
	
	def value_to_nibbles(self, value):
		assert value >= 0
		assert value <= 255
		b = bin(value)[2:10]
		b = "0" * (8 - len(b)) + b
		bits = tuple([bit == "1" for bit in list(b)])
		nibbles = (bits[:4], bits[4:])
		return nibbles
	
	def nibble_to_mask(self, nibble, data = True):
		l = [False] * 8
		l[self.PIN_D4 - 1] = nibble[3]
		l[self.PIN_D5 - 1] = nibble[2]
		l[self.PIN_D6 - 1] = nibble[1]
		l[self.PIN_D7 - 1] = nibble[0]
		if data:
			l[self.PIN_RS - 1] = True
		mask = bool_list_to_mask(l)
		return mask
	
	def write_nibble(self, nibble, data = True):
		if self.board:
			mask = self.nibble_to_mask(nibble, data = data)
			self.board.WriteAllDigital(mask)
		else:
			self.gpio.digitalWrite(self.PIN_RS, data)
			self.gpio.digitalWrite(self.PIN_D4, nibble[3])
			self.gpio.digitalWrite(self.PIN_D5, nibble[2])
			self.gpio.digitalWrite(self.PIN_D6, nibble[1])
			self.gpio.digitalWrite(self.PIN_D7, nibble[0])
	
	def write_value(self, value, data = True):
		if self.debug:
			print "Writing   %i / %s / %s / %s" % (value, hex(value), bin(value), chr(value))
		nibbles = self.value_to_nibbles(value)
		if data:
			self.high(self.PIN_RS)
			self.cursor_pos[0] += 1
		self.write_nibble(nibbles[0], data = data)
		self.pulse(self.PIN_E)
		self.write_nibble(nibbles[1], data = data)
		self.pulse(self.PIN_E)
		self.all_low()
	
	def update_internal_lines(self, lines):
		self.lines = lines
		self.eol = (len(lines[0]), len(lines[1]))
	
	def split_lines(self, string):
		lines = string.splitlines()
		first_line = lines[0]
		second_line = " ".join(lines[1:])
		return first_line, second_line
	
	def _custom_sub(self, match):
		num = int(match.groupdict()['num'])
		return chr(num)
	
	def write_string(self, string, wrap = False, parse_custom = True, update = False, align = 'left'):
		if parse_custom:
			string = re.sub(r"<(?P<num>[0-7])>", self._custom_sub, string)
		first_line, second_line = self.split_lines(string)
		if wrap and len(first_line) > self.column_count:
			first_line, second_line = first_line[:self.column_count], first_line[self.column_count:] + second_line
		if align != 'left':
			free_first = self.column_count - len(first_line)
			free_second = self.column_count - len(second_line)
			if free_first > 0:
				if align == 'center':
					padding_first = divmod(free_first, 2)[0]
					first_line = " " * padding_first + first_line
				elif align == 'right':
					first_line = " " * free_first + first_line
			if free_second > 0:
				if align == 'center':
					padding_second = divmod(free_second, 2)[0]
					second_line = " " * padding_second + second_line
				elif align == 'right':
					second_line = " " * free_second + second_line
		if update:
			return self.update("\n".join((first_line, second_line)))
		for char in first_line:
			self.write_value(ord(char))
		if second_line:
			self.set_cursor_position(second_line = True)
			for char in second_line:
				self.write_value(ord(char))
		self.update_internal_lines((first_line, second_line))
	
	def cycle_strings(self, strings, delay = 5.0, count = -1, *args, **kwargs):
		i = 0
		while count == -1 or i < count:
			i += 1
			for string in strings:
				self.write_string(string, *args, **kwargs)
				time.sleep(delay)
	
	def update(self, string):
		first_line, second_line = self.split_lines(string)
		last_first_line, last_second_line = self.lines[:]
		first_len, second_len = len(first_line), len(second_line)
		last_first_len, last_second_len = len(last_first_line), len(last_second_line)
		for i in range(first_len):
			if first_line[i] != last_first_line[i:i + 1]:
				self.set_cursor_position(column = i)
				self.write_value(ord(first_line[i]))
		if first_len < last_first_len:
			self.set_cursor_position(column = first_len)
			self.write_string(" " * (last_first_len - first_len))
		for i in range(second_len):
			if second_line[i] != last_second_line[i:i + 1]:
				self.set_cursor_position(second_line = True, column = i)
				self.write_value(ord(second_line[i]))
		if second_len < last_second_len:
			self.set_cursor_position(second_line = True, column = second_len)
			self.write_string(" " * (last_second_len - second_len))
		self.update_internal_lines((first_line, second_line))
	
	def initialize(self):
		self.write_nibble((False, False, True, True), data = False)
		self.pulse(self.PIN_E)
		self.pulse(self.PIN_E)
		self.pulse(self.PIN_E)
		self.write_nibble((False, False, True, False), data = False)
		self.pulse(self.PIN_E)
		self.set_configuration(twolines = True)
		self.set_display_enable(enable = True, cursor = False)
		self.all_low()
	
	def clear(self):
		self.write_value(0b00000001, data = False)
	
	def home(self):
		self.write_value(0b00000010, data = False)
		self.cursor_pos = [0, 0]
	
	def set_entry_mode(self, rtl = False, scroll = True):
		_rtl = 0b00000010 if rtl else 0b00000000
		_scroll = 0b00000001 if scroll else 0b00000000
		self.write_value(0b00000100 + _rtl + _scroll, data = False)
	
	def set_display_enable(self, enable = True, cursor = False, cursor_blink = False):
		_enable = 0b00000100 if enable else 0b00000000
		_cursor = 0b00000010 if cursor else 0b00000000
		_cursor_blink = 0b00000001 if cursor_blink else 0b00000000
		self.write_value(0b00001000 + _enable + _cursor + _cursor_blink, data = False)
	
	def scroll(self, right = False):
		_right = 0b00000100 if right else 0b00000000
		self.write_value(0b00011000 + _right, data = False)
	
	def move_cursor(self, left = False):
		_left = 0b00000000 if left else 0b00000100
		self.write_value(0b00010000 + _left, data = False)
		if left:
			self.cursor_pos[0] -= 1
		else:
			self.cursor_pos[0] += 1
	
	def set_configuration(self, twolines = True, five_seven_font = True):
		_twolines = 0b00001000 if twolines else 0b00000000
		_five_seven_font = 0b00000100 if five_seven_font else 0b00000000
		self.write_value(0b00100000 + _twolines + _five_seven_font, data = False)
	
	def set_cursor_position(self, second_line = False, column = 0):
		_second_line = 0b01000000 if second_line else 0b00000000
		self.cursor_pos[1] = 1 if second_line else 0
		self.cursor_pos[0] = column
		self.write_value(0b10000000 + _second_line + column, data = False)
	
	def char_from_file(self, f):
		image = Image.open(f)
		pixels = image.load()
		f.close()
		if image.size != (5, 8):
			return False
		char = [[]] * 8
		for y in range(len(char)):
			char[y] = []
			for x in range(5):
				pix = pixels[4 - x, y]
				char[y].append(sum(pix) / len(pix) <= 127)
			char[y] = bool_list_to_mask(char[y])
		char = tuple(char)
		return char
	
	def load_custom_character(self, pos, char):
		if type(char) is file:
			_char = self.char_from_file(char)
			if not _char:
				return False
		else:
			_char = char
		for i in range(8):
			self.write_value(0b01000000 + (pos << 3) + i, data = False)
			self.write_value(_char[i])
	
	def backspace(self):
		self.move_cursor(left = True)
		self.write_value(0x20)
		self.move_cursor(left = True)
	
	def process_escape_sequence(self, seq):
		data = seq[1:]
		if data == "OH":
			return self.set_cursor_position(second_line = self.cursor_pos[1] == 1, column = 0)
		elif data == "OF":
			return self.set_cursor_position(second_line = self.cursor_pos[1] == 1, column = self.column_count - 1)
		elif data == "[A":
			return self.set_cursor_position(second_line = False, column = self.cursor_pos[0])
		elif data == "[B":
			return self.set_cursor_position(second_line = True, column = self.cursor_pos[0])
		elif data == "[C":
			return self.move_cursor()
		elif data == "[D":
			return self.move_cursor(left = True)
		elif data == "[3~":
			return self.write_value(0x20)
		else:
			return False
	
	def process_control_character(self, char):
		code = ord(char)
		if code == 0x0D:
			return self.set_cursor_position(second_line = True)
		elif code == 0x18:
			self.clear()
			self.home()
		elif code == 0x1B:
			return False
		elif code == 0x7F:
			return self.backspace()
		else:
			return False
	
	def write(self, data, *args, **kwargs):
		t = type(data)
		if t is int:
			return self.write_value(data)
		elif t is str or t is unicode:
			if data.startswith(chr(27)):
				return self.process_escape_sequence(data)
			else:
				if len(data) == 1 and ord(data) in self.CONTROL_CHARACTERS:
					return self.process_control_character(data)
				else:
					return self.write_string(data, *args, **kwargs)
		elif t is list or t is tuple:
			return self.cycle_strings(data, *args, **kwargs)
		elif t is file:
			return self.write_string(data.read(), *args, **kwargs)
		else:
			return self.write_string(str(data), *args, **kwargs)

class K8055LCDUI:
	DEBUG = True
	
	KEY_LEFT = "\x1b[D"
	KEY_RIGHT = "\x1b[C"
	KEY_UP = "\x1b[A"
	KEY_DOWN = "\x1b[B"
	KEY_ENTER = chr(13)
	
	class ProgressBar:
		def __init__(self, ui, title, fraction, char, align):
			self.ui = ui
			self.title = title
			self.fraction = fraction
			self.char = char
			self.align = align
		
		def update(self, title = None, fraction = None, char = None, align = None):
			self.title = title or self.title
			self.fraction = fraction or self.fraction
			self.char = char or self.char
			self.align = align or self.align
			self = self.ui.progress_bar(title = self.title, fraction = self.fraction, char = self.char, align = self.align)
	
	def __init__(self, display, keyreader):
		self.current_lines = ()
		self.display = display
		self.displayed_lines = ()
		self.h_scroll_pos = 0
		self.keyreader = keyreader
		self.line_buffer = []
		self.viewport = ()
		self.v_scroll_pos = 0
	
	def _chunks(self, seq, size):
		for i in range(0, len(seq), size):
			yield seq[i:i + size]
	
	def _shift(self, seq, amount):
		amount = divmod(amount, len(seq))[1]
		shifted = seq[-amount:] + seq[:-amount]
		return shifted
	
	def _align(self, line, align, width = None):
		width = width or self.display.column_count
		aligned_line = line
		if "\t" in line:
			parts = line.split("\t")
			parts = [parts[0], " ".join(parts[1:])]
			len2 = len(parts[1])
			len1 = width - (len2 + 1)
			parts[0] = parts[0][:len1].ljust(len1)
			aligned_line = " ".join(parts)
		else:
			if align == 'left':
				aligned_line = line.ljust(width)
			elif align == 'center':
				aligned_line = line.center(width)
			elif align == 'right':
				aligned_line = line.rjust(width)
		return aligned_line
	
	def update(self, lines = None, home = True):
		if home:
			self.h_scroll_pos = 0
		if lines is not None:
			self.line_buffer = list(lines[:])
			if home:
				self.v_scroll_pos = 0
		self.line_buffer += [""] * (self.display.line_count - len(self.line_buffer))
		self.v_scroll_pos = min(len(self.line_buffer) - self.display.line_count, self.v_scroll_pos)
		lines = self.line_buffer[self.v_scroll_pos:self.v_scroll_pos + self.display.line_count]
		self.stored_lines = tuple([line[:self.display.max_chars_per_line].ljust(self.display.max_chars_per_line) for line in lines])
		self.displayed_lines = tuple([line[:self.display.max_chars_per_line].ljust(self.display.max_chars_per_line * 2) for line in lines])
		self.viewport = tuple([self._shift(line, -self.h_scroll_pos)[:self.display.column_count] for line in self.displayed_lines])
	
	def redraw(self):
		if self.DEBUG:
			print "*** Viewport ***\n%s\n" % "\n".join(self.viewport)
		self.display.set_cursor_position()
		self.display.write("\n".join(self.stored_lines))
	
	def clear(self):
		self.line_buffer = []
		self.update()
		self.display.clear()
		self.display.home()
	
	def format_buttons(self, buttons, active = 0):
		btn_width = self.display.column_count / len(buttons) - 2
		row = ("%s" * len(buttons)) % tuple([("<%s>" if active == buttons.index(button) else " %s ") % button[0][:btn_width].center(btn_width) for button in buttons])
		return row
	
	def format_list_entries(self, entries, align = 'center', active = 0):
		entry_width = self.display.column_count - 2
		rows = tuple([("<%s>" if active == entries.index(entry) else " %s ") % self._align(entry[0][:entry_width], align, entry_width) for entry in entries])
		return rows
	
	def format_lines(self, lines, align = 'left'):
		formatted_lines = tuple([self._align(line, align) for line in lines])
		return formatted_lines
	
	def format_slider(self, minimum, maximum, value, align = 'left', char = "*"):
		val_width = max(len(str(minimum)), len(str(maximum))) + 1
		max_slider_width = self.display.column_count - val_width
		slider_width = int(max_slider_width * float(value) / (maximum - minimum))
		row = str(value).ljust(val_width) + char * slider_width
		return row
	
	def dialog(self, title, buttons = ("OK"), align = 'left', active = 0):
		done = False
		while not done:
			title = self._align(title, align)
			buttons = tuple([(button, None) if type(button) in [str, unicode] else button for button in buttons])
			button_row = self.format_buttons(buttons, active = active)
			self.update((title, button_row))
			self.redraw()
			key = None
			while key is None:
				key = self.keyreader.read_key()
			if key == self.KEY_LEFT:
				active = max(0, active - 1)
			elif key == self.KEY_RIGHT:
				active = min(active + 1, len(buttons) - 1)
			elif key == self.KEY_UP:
				self.v_scroll(-1)
			elif key == self.KEY_DOWN:
				self.v_scroll(1)
			elif key == self.KEY_ENTER:
				done = True
		selected = buttons[active]
		if selected[1]:
			try:
				selected[1][0](*selected[1][1], **selected[1][2])
			except:
				pass
		return active, selected[0]
	
	def progress_bar(self, title, fraction = 0.0, char = "#", align = 'left'):
		assert type(char) in [str, unicode]
		title = self._align(title, align)
		char = char[0]
		count = int(self.display.column_count * fraction)
		bar = char * count
		self.update((title, bar))
		self.redraw()
		return self.ProgressBar(self, title, fraction, char, align)
	
	def list_dialog(self, title, entries, align = 'left', active = 0):
		done = False
		first_loop = True
		while not done:
			title = self._align(title, align)
			entries = tuple([(entry, None) if type(entry) in [str, unicode] else entry for entry in entries])
			entry_rows = self.format_list_entries(entries, align = align, active = active)
			self.update([title] + list(entry_rows), home = first_loop)
			self.redraw()
			first_loop = False
			key = None
			while key is None:
				key = self.keyreader.read_key()
			if key == self.KEY_UP:
				active = max(0, active - 1)
				if active < self.v_scroll_pos - 1 or (active == 0 and divmod(len(entries), 2)[1] == 0):
					self.v_scroll(-2)
			elif key == self.KEY_DOWN:
				active = min(active + 1, len(entries) - 1)
				if active > self.v_scroll_pos:
					self.v_scroll(2)
			elif key == self.KEY_ENTER:
				done = True
		selected = entries[active]
		if selected[1]:
			try:
				selected[1][0](*selected[1][1], **selected[1][2])
			except:
				pass
		return active, selected[0]
	
	def input_dialog(self, title, align = 'left'):
		done = False
		while not done:
			title = self._align(title, align)
			self.update([title], home = False)
			self.redraw()
			self.display.set_cursor_position(second_line = True)
			response = ""
			while True:
				key = self.keyreader.read_key()
				if key == self.KEY_ENTER:
					done = True
					break
				else:
					response += key
					self.display.write(key)
		return response
	
	def slider_dialog(self, title, minimum = 0, maximum = 100, step = 1, big_step = 10, align = 'left', value = 0, char = "*"):
		assert value >= minimum
		assert value <= maximum
		done = False
		while not done:
			title = self._align(title, align)
			slider_row = self.format_slider(minimum, maximum, value, align = align, char = char)
			self.update((title, slider_row))
			self.redraw()
			key = None
			while key is None:
				key = self.keyreader.read_key()
			if key == self.KEY_LEFT:
				value = max(value - step, minimum)
			elif key == self.KEY_RIGHT:
				value = min(value + step, maximum)
			elif key == self.KEY_UP:
				value = min(value + big_step, maximum)
			elif key == self.KEY_DOWN:
				value = max(value - big_step, minimum)
			elif key == self.KEY_ENTER:
				done = True
		return value
	
	def message(self, data, align = 'left'):
		if type(data) in [str, unicode]:
			data = data.splitlines()
		data = self.format_lines(data, align)
		self.update(data)
		self.redraw()
	
	def v_scroll(self, amount = 1, to = None):
		if to is not None:
			amount = -(self.h_scroll_pos - to)
		l = len(self.line_buffer) - self.display.line_count
		self.v_scroll_pos = (self.v_scroll_pos + amount) if self.v_scroll_pos + amount > 0 else 0
		self.v_scroll_pos = self.v_scroll_pos if self.v_scroll_pos < l else l
		self.update(home = False)
		self.redraw()
	
	def h_scroll(self, amount = 1, to = None):
		if to is not None:
			amount1 = -(self.h_scroll_pos - to)
			amount2 = self.display.max_chars_per_line * 2 + amount1
			amount = amount1 if abs(amount1) < abs(amount2) else amount2
		for i in range(abs(amount)):
			self.display.scroll(right = amount < 0)
		self.h_scroll_pos += amount
		while self.h_scroll_pos < 0:
			self.h_scroll_pos = self.display.max_chars_per_line * 2 + self.h_scroll_pos
		self.update(home = False)
	
	def dim(self, level, animate = True, delay = 0.0025, duration = None):
		if level == self.display.brightness:
			return
		if animate:
			if duration is not None:
				p = duration / abs(level - self.display.brightness)
			else:
				p = delay
			mod = 1 if level > self.display.brightness else -1
			for i in range(self.display.brightness + mod, level + mod, mod):
				self.display.set_brightness(i)
				time.sleep(p)
		else:
			self.display.set_brightness(level)
