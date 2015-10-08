#!/usr/bin/python

import pyk8055
import time
from k8055_functions import inputs_to_mask

COMBINATION = [[4], [2], [3], [3], [1]]

def main():
	k = pyk8055.k8055(0)
	k.ResetCounter(1)
	k.ResetCounter(2)
	k.ClearAllDigital()
	stage = 0
	old_mask = 0
	while True:
		new_mask = k.ReadAllDigital()
		if new_mask != old_mask:
			if new_mask != 0:
				if new_mask == inputs_to_mask(COMBINATION[stage]):
					stage += 1
					k.SetDigitalChannel(stage)
				else:
					stage = 0
					k.ClearAllDigital()
				if stage == len(COMBINATION):
					print "Success!"
					for n in range(5):
						k.SetAllDigital()
						time.sleep(0.25)
						k.ClearAllDigital()
						time.sleep(0.25)
					for i in range(100):
						k.OutputAnalogChannel(1, i)
						k.OutputAnalogChannel(2, i)
					for i in range(100):
						k.OutputAnalogChannel(1, 100 - i)
						k.OutputAnalogChannel(2, 100 - i)
					return
			old_mask = new_mask
		time.sleep(0.1)

main()
