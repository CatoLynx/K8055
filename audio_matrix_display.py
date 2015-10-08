#!/usr/bin/python
# -*- coding: utf-8 -*-

from k8055_classes import AudioSpectrum, K8055MatrixDisplayController
import pyk8055
import sys
import thread
import time

class MyAudioSpectrum(AudioSpectrum):
	def on_message(self, bus, message):
		s = message.structure
		if s and s.get_name() == 'spectrum':
			bands = [band - self.threshold for band in s['magnitude'][:5]]
			outputs = [[i + 3 for i in range(int(band / 10))] for band in bands]
			self.display.outputs = outputs
		return True

class Display(K8055MatrixDisplayController):
	def update_loop(self):
		self.outputs = [[], [], [], [], []]
		while True:
			self.update(self.outputs)

def main():
	board = pyk8055.k8055(0)
	spectrum = MyAudioSpectrum(bands = 8, interval = 15000000)
	display = Display(board)
	spectrum.display = display
	
	thread.start_new_thread(display.update_loop, ())
	
	try:
		spectrum.start()
	except KeyboardInterrupt:
		display.stop()

main()
