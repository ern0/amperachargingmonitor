#!/usr/bin/env python3

import sys
sys.dont_write_bytecode = True
import os


class FindGreenDot:
	
	
	def find(self,fnam):
		
		self.checkFileExistence(fnam)
		self.countNumberOfFrames()


	def fatal(self,msg):
		sys.stderr.write("ERROR: " + str(msg) + "\n")
		os._exit(1)


	def checkFileExistence(self,fnam):
		
		if not os.path.isfile(fnam): 
			self.fatal("file not found: " + str(fnam))
			
		self.fnam = fnam
		
		
	def countNumberOfFrames(self):
		
		output = os.popen(
			"ffprobe "
			" -v error"
			" -count_frames"
			" -select_streams v:0"
			" -show_entries"
			" stream=nb_frames"
			" -of default=nokey=1:noprint_wrappers=1"
			" " + self.fnam
		).read()		
				
		try: self.frameCount = int(output)
		except: self.fatal("ffprobe failed")
	

if __name__ == '__main__':

	try: 
		(FindGreenDot()).find(sys.argv[1])
	except KeyboardInterrupt:
		print(" - interrupted")
