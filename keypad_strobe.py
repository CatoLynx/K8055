#!/usr/bin/env python
# -*- coding: utf-8 -*-
# K8055 Keypad reader
# © 2013 Mezgrman

from k8055_classes import K8055MatrixKeypad, K8055Stroboscope
import pyk8055
import sys

KEYMAP = (
	("10,10,10,10,10,10,10,10,10,10", "4,4,4,4", "2,2"),
	("8,8,8,8,4,4,4,4,2", "3,3,6,6,3,6,6,6,3,6,3", "3,4,5,6,7,8,9,10,9,8,7,6,5,4"),
	("4", "8", "16"),
	("CONT", "10", "QUIT"),
)

class StroboscopeKeypad(K8055MatrixKeypad):
	def __init__(self, board, cols, rows, keymap = None):
		K8055MatrixKeypad.__init__(self, board, cols, rows, keymap)
		self.strober = None
		self.continuous_strobe = False
		self.last_strobe_pattern = ""
	
	def read_loop(self):
		self.loop = True
		while self.loop:
			keys = self.read_keys()
			if self.continuous_strobe and keys == []:
				keys = [self.last_strobe_pattern]
			for key in keys:
				self.loop = self.on_keys(keys)
	
	def on_keys(self, keys):
		for key in keys:
			if key == "CONT":
				self.continuous_strobe = not self.continuous_strobe
			elif key == "QUIT":
				return False
			else:
				self.last_strobe_pattern = key
				self.strober.strobe_pattern(key)
		return True

def run():
	k = pyk8055.k8055(0)
	pad = StroboscopeKeypad(k, cols = 3, rows = 4, keymap = KEYMAP)
	strober = K8055Stroboscope(k, channel = 7)
	pad.strober = strober
	try:
		pad.read_loop()
	except KeyboardInterrupt:
		pass
	pad.reset()

run()
