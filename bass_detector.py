#!/usr/bin/python
# -*- coding: utf-8 -*-
# Script to control a stroboscope according to the bass in the music currently playing.
# © 2012 Mezgrman

from k8055_classes import K8055StepperMotorController
import datetime
import gobject
import pygst
import pyk8055
import random
import sys
import thread
import time
import traceback

pygst.require("0.10")
import gst

MODE = 'strobe' # 'strobe', 'flash' or 'motor'

class Spectrum:
	def __init__(self):
		self.interval = 15000000
		self.threshold = -60
		self.bands = 64
		self.last_levels = []
		self.old_bass = False
		self.bass = False
		self.basses = []
		# listener_desc = 'alsasrc ! spectrum ! fakesink'
		listener_desc = 'pulsesrc device="alsa_output.pci-0000_00_07.0.analog-stereo.monitor" ! spectrum interval=%i threshold=%i bands=%i ! fakesink' % (self.interval, self.threshold, self.bands)
		self.listener = gst.parse_launch(listener_desc)
		bus = self.listener.get_bus()
		bus.add_signal_watch()
		bus.connect('message', self.on_message)

	def on_message(self, bus, message):
		s = message.structure
		if s and s.get_name() == 'spectrum':
			if not self.on_data(s):
				return False
		return True
	
	def on_data(self, data):
		raise NotImplementedError

	def start(self):
		self.listener.set_state(gst.STATE_PLAYING)
		while True:
			time.sleep(1)

class BassDetector:
	def __init__(self):
		self.state = True
		self.light = 1
		self.sensitivity = 7.5
		self.sensitivity_multiplier = 1.0
		self.min_bass_interval = 0.35
		self.min_bass_interval_multiplier = 1.0
		self.last_bass = datetime.datetime.now()
		self.mode = MODE
		try:
			self.board = pyk8055.k8055(0)
			self.board.ClearAllAnalog()
			self.board.ClearAllDigital()
		except IOError:
			self.board = None
		if self.board:
			self.stepper = K8055StepperMotorController(self.board)
		class BassDetectorSpectrum(Spectrum):
			def on_data(self_, data):
				levels = [level + abs(self_.threshold) for level in data['magnitude']]
				if len(self_.last_levels) >= 50:
					self_.last_levels.pop(-1)
				self_.last_levels.insert(0, levels[0])
				avg = sum(self_.last_levels) / len(self_.last_levels)
				difference = levels[0] - avg
				
				if difference > (self.sensitivity * self.sensitivity_multiplier) and not self_.bass:
					self_.bass = True
					if not self.on_bass():
						return False
				
				if difference < (self.sensitivity * self.sensitivity_multiplier) and self_.bass:
					self_.bass = False
				
				if self_.bass and not self_.old_bass:
					if len(self_.basses) > 10:
						self_.basses.pop(0)
					self_.basses.append(datetime.datetime.now())
				
				if self_.bass != self_.old_bass:
					self_.old_bass = self_.bass
				return True
		
		self.spectrum = BassDetectorSpectrum()
	
	def run(self):
		return self.spectrum.start()
	
	def on_bass(self):
		if (datetime.datetime.now() - self.last_bass).total_seconds() < (self.min_bass_interval * self.min_bass_interval_multiplier):
			return False
		self.state = not self.state
		if self.board is not None:
			if self.mode == 'strobe':
				self.strobe()
			elif self.mode == 'flash':
				self.flash()
			elif self.mode == 'motor':
				self.stepper.rotate(random.randrange(1, 20), ccw = self.state)
			values = self.board.ReadAllValues()
			self.sensitivity_multiplier = float(values[2]) / 127.0
			self.min_bass_interval_multiplier = float(values[3]) / 127.0
		print "WUB",
		sys.stdout.flush()
		self.set_title("####" if self.state else "----")
		self.last_bass = datetime.datetime.now()
		return True
	
	def strobe(self):
		self.board.SetDigitalChannel(7)
		# time.sleep(0.01)
		self.board.ClearDigitalChannel(7)
	
	def flash(self):
		if self.light == 1:
			self.board.ClearDigitalChannel(1)
			self.board.SetDigitalChannel(2)
			self.light = 2
		elif self.light == 2:
			self.board.ClearDigitalChannel(2)
			self.board.SetDigitalChannel(3)
			self.light = 3
		else:
			self.board.ClearDigitalChannel(3)
			self.board.SetDigitalChannel(1)
			self.light = 1
			
	
	def print_continuous_basses(self):
		while True:
			time_diffs = []
			for i in range(len(self.spectrum.basses)):
				if i > 0:
					diff = (self.spectrum.basses[i] - self.spectrum.basses[i - 1]).total_seconds()
					if diff > 0.1 and diff < 5.0:
						time_diffs.append(diff)
			try:
				bass_interval = sum(time_diffs) / len(time_diffs)
			except ZeroDivisionError:
				pass
			except:
				traceback.print_exc()
			else:
				if not self.on_bass():
					return False
				time.sleep(bass_interval)
	
	def set_title(self, title):
		sys.stdout.write("\x1b]2;%s\x07" % title)

def main():
	detector = BassDetector()
	thread.start_new_thread(detector.run, ())
	# thread.start_new_thread(detector.print_continuous_basses, ())
	gobject.threads_init()
	loop = gobject.MainLoop()
	loop.run()

main()
