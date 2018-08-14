#!/usr/bin/env python3

import sys
sys.dont_write_bytecode = True
import os

from PIL import Image


class FindGreenDot:
	
	
	def main(self):		
		
		try: tmpdir = sys.argv[2]
		except: tmpdir = None
		self.checkTmpDir(tmpdir)
		
		try: fnam = sys.argv[1]
		except: fnam = None
		self.checkFileExistence(fnam)
		
		self.frameCount = self.countNumberOfFrames()
		
		while True:
			
			self.extractFrame(40)
			self.procImage()
			break;


	def fatal(self,msg):
		sys.stderr.write("ERROR: " + str(msg) + "\n")
		os._exit(1)


	def checkTmpDir(self,tmpdir):
		
		self.tmpdir = "/tmp"
			
		if tmpdir is None: return
		if tmpdir == "": return
		if not os.path.isdir(tmpdir): return
			
		self.tmpdir = tmpdir
		

	def checkFileExistence(self,fnam):
		
		if not os.path.isfile(fnam): 
			self.fatal("file not found: " + str(fnam))
			
		self.fnam = fnam
		
		
	def mkTmpImgPath(self):
		return self.tmpdir + "/frame.png"		
		
	
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
				
		try: return int(output)
		except: self.fatal("ffprobe failed")
	

	def extractFrame(self,frameNo):
		
		try: os.unlink(self.mkTmpImgPath())
		except: pass
		
		output = os.popen(
			"ffmpeg"
			" -v error"
			" -i " + self.fnam +
			" -vf select=\"eq(n\\," + str(frameNo) + ")\""
			" -vsync 0"
			" " + self.mkTmpImgPath()
		).read()
		
		
	def procImage(self):
		
		image = Image.open(self.mkTmpImgPath())
		pixels = image.load()
		
		(width,height) = image.size
		
		for x in range(0,width):
			for y in range(0,height):
				
				(r,g,b) = pixels[x,y]

				if g < 50: continue
				if g < 50: continue
				
				print(x,y,g)	
		

if __name__ == '__main__':

	try: 
		(FindGreenDot()).main()
	except KeyboardInterrupt:
		print(" - interrupted")
