#!/usr/bin/python

import pyk8055
import sys

def do_write():
	k = pyk8055.k8055(0)
	f = open("levels.txt", 'w')
	try:
		while True:
			level = k.ReadAnalogChannel(1)
			f.write(str(level) + ";")
	except KeyboardInterrupt:
		f.close()

def do_read():
	k = pyk8055.k8055(0)
	with open("levels.txt", 'r') as f:
		levels = f.read().split(";")[:-1]
	for level in levels:
		k.OutputAnalogChannel(1, int(level))

def main():
	try:
		read = sys.argv[1] == "r"
	except:
		read = False
	if read:
		do_read()
	else:
		do_write()

main()
