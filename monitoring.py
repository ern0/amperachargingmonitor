#!/usr/bin/env python3

import sys
sys.dont_write_bytecode = True
import os
import time

import findgreendot



class Monitoring:
	
	
	def main(self):	

		fgd = findgreendot.FindGreenDot()	
		result = fgd.procFrames("sample/sunshine-light-1.avi")
		print(result)


	def fatal(self,msg):
		sys.stderr.write("ERROR: " + str(msg) + "\n")
		os._exit(1)


if __name__ == '__main__':

	try: 
		(Monitoring()).main()
	except KeyboardInterrupt:
		print(" - interrupted")
