#!/usr/bin/python
# -*- coding: utf-8 -*-
# Audio visualization.
# © 2012 Mezgrman

import pygst
pygst.require("0.10")
import gst,gobject
import time, thread, sys
import pyk8055
from k8055_classes import K8055StepperMotorController
 
class Spectrum:
	def __init__(self, stepper):
		self.stepper = stepper
		listener_desc = 'pulsesrc device="alsa_output.pci-0000_00_07.0.analog-stereo.monitor" ! spectrum bands=8 ! fakesink'
		self.listener = gst.parse_launch(listener_desc)
		bus = self.listener.get_bus()
		bus.add_signal_watch()
		bus.connect("message", self.on_message)
 
	def on_message (self, bus, message):
		s = message.structure
		if s and s.get_name() == "spectrum":
			avg = 0.0
			for band in s['magnitude'][:4]:
				avg += abs(band)
			avg = int((60 - int((avg / 4))) ** 0.9)
			# print avg
			self.stepper.rotate_to(avg)
		return True
 
	def start(self):
		self.listener.set_state(gst.STATE_PLAYING)
		while True:
			time.sleep(1)
 
 
def main():
	board = pyk8055.k8055(0)
	stepper = K8055StepperMotorController(board, steps_per_revolution = 36)
	spectrum = Spectrum(stepper)
	thread.start_new_thread(spectrum.start, ())
	gobject.threads_init()
	loop = gobject.MainLoop()
	try:
		loop.run()
	except KeyboardInterrupt:
		stepper.reset()

main()
