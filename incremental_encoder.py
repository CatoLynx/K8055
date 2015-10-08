#!/usr/bin/env python
# -*- coding: utf-8 -*-

from k8055_classes import K8055IncrementalEncoder
import pyk8055
import sys
import time
import random
from global_functions import beep

class IncrementalEncoder(K8055IncrementalEncoder):
	def on_rotate(self, ccw):
		self.board.ClearDigitalChannel(self.index)
		if ccw:
			self.index = (self.index - 1) if self.index > 1 else 8
		else:
			self.index = (self.index + 1) if self.index < 8 else 1
		self.board.SetDigitalChannel(self.index)
		self.counter += 1
		print self.counter
		beep([self.counter], [5.0])
		return True

def main():
	board = pyk8055.k8055(0)
	encoder = IncrementalEncoder(board)
	encoder.index = 1
	encoder.counter = 0
	try:
		encoder.event_loop()
	except KeyboardInterrupt:
		encoder.reset()

main()
