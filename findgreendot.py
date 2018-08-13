#!/usr/bin/env python3

import sys
sys.dont_write_bytecode = True
import os


class FindGreenDot:
	
	
	def main(self):
		
		try: 
			self.find( sys.argv[1] ) 
		except IndexError:
			print("FindGreenDot - find blinking or static green led in a video using ffmpeg")
	
	
	def find(self,fnam):
		
		if not os.path.isfile(fnam): raise IndexError
		
	

if __name__ == '__main__':

	try: 
		(FindGreenDot()).main()
	except KeyboardInterrupt:
		print(" - interrupted")
