#!/usr/bin/env python3

import sys
sys.dont_write_bytecode = True
import os

import findgreendot


class Test:


	def main(self):

		fgd = findgreendot.FindGreenDot()
		for entry in os.scandir("sample"):
		#for entry in ("morning-none-1.avi","sunshine-blink-1.avi","sunshine-light-1.avi"):
			name = entry.name
			result = fgd.procFrames("sample/" + name)
			print(name,end=": ")
			if result == 0: print("none")
			if result == 1: print("light")
			if result == 2: print("blink")


	def fatal(self,msg):
		sys.stderr.write("ERROR: " + str(msg) + "\n")
		os._exit(1)


if __name__ == '__main__':

	try:
		(Test()).main()
	except KeyboardInterrupt:
		print(" - interrupted")
