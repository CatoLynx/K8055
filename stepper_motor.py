#!/usr/bin/python
# -*- coding: utf-8 -*-

from k8055_classes import K8055StepperMotorController
import pyk8055
import sys
import time
import random

def getTimeList():
	"""
	Fetches a list of time units the cpu has spent in various modes
	Detailed explanation at http://www.linuxhowtos.org/System/procstat.htm
	"""
	cpuStats = file("/proc/stat", "r").readline()
	columns = cpuStats.replace("cpu", "").split(" ")
	return map(int, filter(None, columns))

def deltaTime(interval):
	"""
	Returns the difference of the cpu statistics returned by getTimeList
	that occurred in the given time delta
	"""
	timeList1 = getTimeList()
	time.sleep(interval)
	timeList2 = getTimeList()
	return [(t2-t1) for t1, t2 in zip(timeList1, timeList2)]

def getCpuLoad():
	"""
	Returns the cpu load as a value from the interval [0.0, 1.0]
	"""
	dt = list(deltaTime(0.05))
	idle_time = float(dt[3])
	total_time = sum(dt)
	load = 1-(idle_time/total_time)
	return load * 100.0

def cpu_load(stepper):
	while True:
		load = int(getCpuLoad())
		pos = int(load * (stepper.steps_per_revolution / 100.0))
		stepper.rotate_to(pos)
		time.sleep(1)

def randomness(stepper):
	while True:
			stepper.rotate(random.randrange(1, 10), ccw = random.choice([True, False]), delay = random.uniform(0.00625, 0.00625))

def change_directions(stepper):
	while True:
			stepper.revolution()
			stepper.revolution(ccw = True)

def rotate(stepper):
	while True:
		stepper.revolution(48)

def main():
	board = pyk8055.k8055(0)
	stepper = K8055StepperMotorController(board)
	
	try:
		rotate(stepper)
	except KeyboardInterrupt:
		time.sleep(1)
		stepper.reset()

main()
