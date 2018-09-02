#!/usr/bin/env python3

import sys
sys.dont_write_bytecode = True
import os

import findgreendot


class Test:


	def main(self):

		fgd = findgreendot.FindGreenDot()
		fgd.dumpParams()

		for entry in os.scandir("sample"):

			result = fgd.procFrames("sample/" + entry.name)
			text = "wtf"
			if result == 0: text = "none"
			if result == 1: text = "light"
			if result == 2: text = "blink"

			if text in entry.name:
				print("[X]",end=" ")
			else:
				print("[ ]",end=" ")
			print(entry.name,end=": ")
			print(text)


	def fatal(self,msg):
		sys.stderr.write("ERROR: " + str(msg) + "\n")
		os._exit(1)


if __name__ == '__main__':

	try:
		(Test()).main()
	except KeyboardInterrupt:
		print(" - interrupted")
