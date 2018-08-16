#!/usr/bin/env python3

import sys
sys.dont_write_bytecode = True
import os

from PIL import Image


class FindGreenDot:
	
	
	def main(self):		

		self.saveImage = False
		
		try: tmpdir = sys.argv[2]
		except: tmpdir = None
		self.checkTmpDir(tmpdir)
		
		try: fnam = sys.argv[1]
		except: fnam = None
		self.checkFileExistence(fnam)

		try: 
			dummy = sys.argv[3]
			self.showProgress = True
		except:
			self.showProgress = False

		self.frameCount = self.countNumberOfFrames()

		if False: ############## set to False pls
			#for i in range(0,self.frameCount):
			for i in (6,):
				print(self.fnam + ":" + str(i),end=" - ")
				self.extractFrame(i)
				found = self.procImage()
			quit()
		
		self.procFrames()
	

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
		return (
			self.tmpdir
			+ "/" 
			+ os.path.basename(self.fnam)
			+ "-frame.png"
		)		
		
	
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
		
		source = Image.open(self.mkTmpImgPath())
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

		found = False

		# make sobelish
		for y in range(0,height):
			for x in range(0,width - 2):

				(r,g,b) = pixels[x,y]
				(r1,g1,b1) = pixels[x + 1, y]
				(r2,g2,b2) = pixels[x + 2, y]

				delta = (
					abs(r - r1) + abs(g - g1) * 2 + abs(b - b1) +
					abs(r - r2) + abs(g - g2)	+ abs(b - b2)
				)				
				if g < r: delta = 0
				elif g < b: delta = 0
				elif abs(r - b) > g / 5: delta = 0
				elif delta < 256 * 4: delta = 0

				if delta != 0: found = True

				if self.saveImage:
					if delta > 255: delta = 255
					result[x,y] = (delta,delta,delta)

		if self.saveImage:
			target.save("/tmp/image.png","PNG")

		return found


	def procFrames(self):
		
		print(self.fnam)

		valueCount = [0,0]
				
		for i in range(0,self.frameCount):
			
			self.extractFrame(i)
			found = self.procImage()

			if found: value = 1
			else: value = 0
			valueCount[value] += 1

			if self.showProgress:
				print(" frame",i,"/",self.frameCount," - ",value)
				
		print(self.fnam,valueCount)


if __name__ == '__main__':

	try: 
		(FindGreenDot()).main()
	except KeyboardInterrupt:
		print(" - interrupted")
