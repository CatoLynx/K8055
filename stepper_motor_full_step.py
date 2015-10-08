#!/usr/bin/python
# -*- coding: utf-8 -*-

import pyk8055
import sys
import time

def main():
	delay = float(sys.argv[1])
	k = pyk8055.k8055(0)
	while True:
		k.SetDigitalChannel(2)
		k.ClearDigitalChannel(4)
		time.sleep(delay)
		k.SetDigitalChannel(3)
		k.ClearDigitalChannel(5)
		time.sleep(delay)
		k.SetDigitalChannel(4)
		k.ClearDigitalChannel(2)
		time.sleep(delay)
		k.SetDigitalChannel(5)
		k.ClearDigitalChannel(3)
		time.sleep(delay)

main()
