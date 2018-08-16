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

		try: 
			dummy = sys.argv[3]
			self.showProgress = True
		except:
			self.showProgress = False

		self.frameCount = self.countNumberOfFrames()

		if True: ############## set to False pls
			#for i in range(0,self.frameCount):
			for i in (0,1):
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

		target = Image.new("RGB",source.size,"black")
		result = target.load()

		for y in range(0,height):
			for x in range(0,width - 1):

				(r,g,b) = pixels[x,y]
				if r < 20: continue
				if g < 20: continue
				if b < 20: continue

				(r1,g1,b1) = pixels[x + 1,y]
				d = abs(g - g1) * 3
				d -= abs(r - r1)
				d -= int( abs(b - b1) / 2 )
				result[x,y] = (d,d,d)

		threshold = 0
		for y in range(0,height):
			for x in range(0,width - 1):

				(d1,d2,d3) = result[x,y]
				if d1 > threshold: threshold = d1

		threshold *= 0.8

		for y in range(0,height):
			count = 0
			for x in range(0,width - 1):

				(d1,d2,d3) = result[x,y]
				if d1 > threshold: 
					result[x,y] = (255,255,255)
					count += 1

			if count > 0: 
				print(y,count)

		source.save("/tmp/image.png","PNG")
		target.save("/tmp/result.png","PNG")

		found = False
		return found


	def procFrames(self):
		
		print(self.fnam)

		strokeType = -1		 	
		strokeCount = [0,0]
		strokeLength = [0,0]
				
		for i in range(0,self.frameCount):
			
			if self.showProgress:
				print(" frame",i,"/",self.frameCount)

			self.extractFrame(i)
			found = self.procImage()

			if found: value = 1
			else: value = 0
			
			if strokeType != value:
				strokeType = value				
				strokeCount[strokeType] += 1
			
			strokeLength[strokeType] += 1
				
		for i in range(0,1):
			if strokeCount[i] == 0: continue
			strokeLength[i] = strokeLength[i] / strokeCount[i]
			
		print(self.fnam,strokeCount,strokeLength)


if __name__ == '__main__':

	try: 
		(FindGreenDot()).main()
	except KeyboardInterrupt:
		print(" - interrupted")
