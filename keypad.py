#!/usr/bin/env python
# -*- coding: utf-8 -*-
# K8055 Keypad reader
# © 2013 Mezgrman

from k8055_classes import K8055MatrixKeypad
import pyk8055
import sys

KEYMAP = (
	("7", "8", "9"),
	("4", "5", "6"),
	("1", "2", "3"),
	("+", "0", "."),
)

class Keypad(K8055MatrixKeypad):
	def on_keys(self, keys):
		for key in keys:
			if key == ".":
				sys.stdout.write("\n")
			elif key == "+":
				return False
			else:
				sys.stdout.write(key)
		sys.stdout.flush()
		return True

def run():
	k = pyk8055.k8055(0)
	pad = Keypad(k, cols = 3, rows = 4, keymap = KEYMAP)
	try:
		pad.read_loop()
	except KeyboardInterrupt:
		pass
	pad.reset()

run()
