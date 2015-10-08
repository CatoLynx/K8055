#!/usr/bin/python
# -*- coding: utf-8 -*-
# Graphical frontend to control a stroboscope.
# © 2012 Mezgrman

import k8055_functions as functions
import os
import pyk8055
import sys
import thread
import time
import traceback

class Strober:
	def __init__(self):
		self.auto_strobe = bool(sys.argv[2])
		self.strobe_interval = float(sys.argv[1])
		self.board = pyk8055.k8055(0)
	
	def strobe(self):
		self.board.SetDigitalChannel(1)
		time.sleep(0.01)
		self.board.ClearDigitalChannel(1)
	
	def do_strobes(self):
		while True:
			if self.auto_strobe:
				self.strobe()
			time.sleep(self.strobe_interval)

def run():
	strober = Strober()
	strober.do_strobes()

run()
