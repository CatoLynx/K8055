#!/usr/bin/python

import pyk8055
import time

def main():
	k = pyk8055.k8055(0)
	old_counter = 0
	while True:
		value = k.ReadAnalogChannel(1)
		k.WriteAllDigital(value)
		time.sleep(0.1)

main()
