#!/usr/bin/env python3

import sys
sys.dont_write_bytecode = True
import os

from PIL import Image


class FindGreenDot:
	
	
	def main(self):		
		
		try: fnam = sys.argv[1]
		except: self.fatal("filename must be specified")
		self.checkFileExistence(fnam)

		try: specifiedFrame = sys.argv[2]
		except: specifiedFrame = None

		result = self.procFrames(fnam,specifiedFrame)
		print(result)


	def __init__(self):

		if os.path.isdir("/mnt/ram"): 
			self.tmpdir = "/mnt/ram"
		else:
			self.tmpdir = "/tmp"


	def fatal(self,msg):
		sys.stderr.write("ERROR: " + str(msg) + "\n")
		os._exit(1)


	def checkFileExistence(self,fnam):
		
		if not os.path.isfile(fnam): 
			self.fatal("file not found: " + str(fnam))
					
		
	def mkTmpImgPath(self,fnam):
		return (
			self.tmpdir
			+ "/" 
			+ os.path.basename(fnam)
			+ "-frame.png"
		)		
		
	
	def countNumberOfFrames(self,fnam):
		
		output = os.popen(
			"ffprobe "
			" -v error"
			" -count_frames"
			" -select_streams v:0"
			" -show_entries"
			" stream=nb_frames"
			" -of default=nokey=1:noprint_wrappers=1"
			" " + fnam
		).read()		
				
		try: return int(output)
		except: self.fatal("ffprobe failed")
	

	def extractFrame(self,fnam,frameNo):
		
		try: os.unlink(self.mkTmpImgPath(fnam))
		except: pass
		
		output = os.popen(
			"ffmpeg"
			" -v error"
			" -i " + fnam +
			" -vf select=\"eq(n\\," + str(frameNo) + ")\""
			" -vsync 0"
			" " + self.mkTmpImgPath(fnam)
		).read()
		
		
	def procImage(self,fnam):
		
		source = Image.open(self.mkTmpImgPath(fnam))
		(width,height) = source.size
		pixels = source.load()

		target = Image.new(
			"RGB",
			(width * 2 + 1, height),
			"black"
		)
		result = target.load()

		# copy source and draw separator
		if self.saveImage:
			for y in range(0,height):
				result[width,y] = (0,255,0)
				for x in range(0,width):
					result[x + width + 1, y] = pixels[x,y]

		found = 0

		# make sobelish
		for y in range(0,height):
			for x in range(0,width - 2):

				(r,g,b) = pixels[x,y]
				(r1,g1,b1) = pixels[x + 1, y]
				(r2,g2,b2) = pixels[x + 2, y]

				delta = (
					abs(r - r1) + abs(g - g1) * 3 + abs(b - b1) +
					abs(r - r2) + abs(g - g2)	* 2 + abs(b - b2)
				)				
				if g < r: delta = 0
				elif g < b: delta = 0
				elif delta < 256 * 5: delta = 0

				if delta != 0: found += 1

				if self.saveImage:
					if delta != 0: delta = 255
					result[x,y] = (delta,delta,delta)

		if self.saveImage:
			target.save("/tmp/image.png","PNG")

		return found


	def procFrames(self,fnam,specifiedFrame = None):

		frameCount = self.countNumberOfFrames(fnam)

		if specifiedFrame is None:
			frameRange = range(0,frameCount)
			self.saveImage = False
		else:
			frameRange = [ specifiedFrame, ]
			self.saveImage = True

		valueCount = [0,0]				
		for i in frameRange:
			
			self.extractFrame(fnam,i)
			found = self.procImage(fnam)
			if found > 0: value = 1
			else: value = 0

			valueCount[value] += 1

			sys.stderr.write(
				fnam 
				+ ":" 
				+ str(i)
				+ " "
			)

			for i in range(0,found):
				sys.stderr.write("#") 

			sys.stderr.write(
				" " 
				+ str(found)
				+ "\n"
			)

			sys.stderr.flush()

		sys.stderr.write(
			" dark="
			+ str(valueCount[0])
			+ " light="
			+ str(valueCount[1])
			+ "\n"
		)
		sys.stderr.flush()

		if valueCount[0] == 0: return 1
		if valueCount[1] == 0: return 0
		if valueCount[0] > valueCount[1]: return 2
		return 0


if __name__ == '__main__':

	try: 
		(FindGreenDot()).main()
	except KeyboardInterrupt:
		print(" - interrupted")
