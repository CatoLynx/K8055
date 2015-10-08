#!/usr/bin/python

from k8055_functions import *
from global_functions import beep
import pyk8055
import time
import thread

FIXED_FREQ = 440.0
FIXED_NOTE = "A"
FIXED_NOTE_OCTAVE = 4
FIXED_NOTE_MOD = 0
NOTE_SEQ = "C|D|EF|G|A|B"
VALUES = []

def calculate_absolute_pos(note, octave, mod):
	pos = NOTE_SEQ.find(note) + ((octave - 1) * len(NOTE_SEQ)) + mod
	return pos

def calculate_dist_from_a(note, octave, mod):
	absolute_pos = calculate_absolute_pos(note, octave, mod)
	fixed_pos = calculate_absolute_pos(FIXED_NOTE, FIXED_NOTE_OCTAVE, FIXED_NOTE_MOD)
	dist = absolute_pos - fixed_pos
	return dist

def calculate_freq(note, octave, mod):
	if(note == "P"):
		freq = 1.0
	else:
		freq = FIXED_FREQ * ((2 ** (1.0 / 12.0)) ** calculate_dist_from_a(note, octave, mod))
	return freq

def get_values(board):
	global VALUES
	VALUES = board.ReadAllValues()

def main():
	k = pyk8055.k8055(0)
	get_values(k)
	while True:
		mask = VALUES[1]
		analog1 = float(VALUES[2])
		analog2 = float(VALUES[3])
		inputs = mask_to_bool_list(mask)
		freq_mod = (analog1 / 127.0) ** 2
		dur_mod = (analog2 / 127.0) ** 2
		thread.start_new_thread(get_values, (k, ))
		if inputs[0]:
			beep([100.0 * freq_mod], [100.0 * dur_mod])
		if inputs[1]:
			beep([200.0 * freq_mod], [100.0 * dur_mod])
		if inputs[2]:
			beep([300.0 * freq_mod], [100.0 * dur_mod])
		if inputs[3]:
			beep([400.0 * freq_mod], [100.0 * dur_mod])
		if inputs[4]:
			beep([500.0 * freq_mod], [100.0 * dur_mod])

def main2():
	k = pyk8055.k8055(0)
	get_values(k)
	old_octave = 0
	while True:
		frequencies = []
		durations = []
		mask = VALUES[1]
		analog1 = VALUES[2]
		analog2 = float(VALUES[3])
		inputs = mask_to_bool_list(mask)
		true_inputs = float(len([input for input in inputs if input]))
		new_octave = divmod(analog1, 32)[0] + 1
		dur_mod = (analog2 / 127.0) ** 2
		thread.start_new_thread(get_values, (k, ))
		if new_octave != old_octave:
			k.ClearDigitalChannel(old_octave)
			k.SetDigitalChannel(new_octave)
			old_octave = new_octave
		if inputs[0]:
			frequencies.append(calculate_freq("C", new_octave, 0))
			durations.append((100.0 * dur_mod) / true_inputs)
		if inputs[1]:
			frequencies.append(calculate_freq("D", new_octave, 0))
			durations.append((100.0 * dur_mod) / true_inputs)
		if inputs[2]:
			frequencies.append(calculate_freq("E", new_octave, 0))
			durations.append((100.0 * dur_mod) / true_inputs)
		if inputs[3]:
			frequencies.append(calculate_freq("F", new_octave, 0))
			durations.append((100.0 * dur_mod) / true_inputs)
		if inputs[4]:
			frequencies.append(calculate_freq("G", new_octave, 0))
			durations.append((100.0 * dur_mod) / true_inputs)
		if len(frequencies) > 0:
			beep(frequencies, durations)

def main3():
	k = pyk8055.k8055(0)
	get_values(k)
	old_octave = 0
	all_frequencies = []
	all_durations = []
	try:
		while True:
			frequencies = []
			durations = []
			mask = VALUES[1]
			analog1 = VALUES[2]
			analog2 = float(VALUES[3])
			inputs = mask_to_bool_list(mask)
			true_inputs = float(len([input for input in inputs if input]))
			new_octave = divmod(analog1, 32)[0] + 1
			dur_mod = (analog2 / 127.0) ** 2
			thread.start_new_thread(get_values, (k, ))
			if new_octave != old_octave:
				k.ClearDigitalChannel(old_octave)
				k.SetDigitalChannel(new_octave)
				old_octave = new_octave
			if inputs[0]:
				frequencies.append(calculate_freq("C", new_octave, 0))
				durations.append((100.0 * dur_mod) / true_inputs)
			if inputs[1]:
				frequencies.append(calculate_freq("D", new_octave, 0))
				durations.append((100.0 * dur_mod) / true_inputs)
			if inputs[2]:
				frequencies.append(calculate_freq("E", new_octave, 0))
				durations.append((100.0 * dur_mod) / true_inputs)
			if inputs[3]:
				frequencies.append(calculate_freq("F", new_octave, 0))
				durations.append((100.0 * dur_mod) / true_inputs)
			if inputs[4]:
				frequencies.append(calculate_freq("G", new_octave, 0))
				durations.append((100.0 * dur_mod) / true_inputs)
			if mask > 0:
				beep(frequencies, durations)
				all_frequencies += frequencies
				all_durations += durations
	except KeyboardInterrupt:
		time.sleep(1)
		print "Replaying melody."
		beep(all_frequencies, all_durations)

main3()
