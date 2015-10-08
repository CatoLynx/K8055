#!/usr/bin/python

import time

def mask_to_bool_list(mask, bits = 5):
	rest, mask = divmod(int(mask), 256)
	return [bool(int(value)) for value in list(("{:0>%i}" % bits).format(bin(mask)[2:])[::-1])]

def list_to_mask(list):
	mask = 0
	for item in list:
		mask += 2 ** (item - 1)
	return mask

def bool_list_to_mask(list):
	mask = 0
	for i in range(len(list)):
		if bool(int(list[i])):
			mask += 2 ** i
	return mask

def animate(board, steps, delay = 75):
	for step in steps:
		board.WriteAllDigital(bool_list_to_mask(step))
		time.sleep(float(delay) / 1000.0)
