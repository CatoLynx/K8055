#!/usr/bin/env python
# -*- coding: utf-8 -*-
# K8055 VFD controller
# © 2013 Mezgrman

from k8055_classes import K8055VFDController
import pyk8055
import time

def run():
	k = pyk8055.k8055(0)
	display = K8055VFDController(k)
	for i in range(10):
		display.shift(display.LEFT)
		time.sleep(1)
	display.shutdown()

run()
