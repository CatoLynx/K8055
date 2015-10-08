#!/usr/bin/python

from k8055_functions import *
import ledsign
import pyk8055
import time

def main():
	k = pyk8055.k8055(0)
	sign = ledsign.LEDSign()
	sign.set_pages("K")
	old_mask = 0
	while True:
		mask = k.ReadAllDigital()
		if mask != old_mask:
			inputs = mask_to_bool_list(mask)
			if inputs[0]:
				sign.send([{'text': "Ponies"}], page = "K", lead_effect = 'twinkle', display_time = 0.5)
			elif inputs[1]:
				sign.set_brightness(1)
			elif inputs[2]:
				sign.set_brightness(2)
			elif inputs[3]:
				sign.set_brightness(3)
			elif inputs[4]:
				sign.set_brightness(4)
			old_mask = mask
		time.sleep(0.1)

main()
