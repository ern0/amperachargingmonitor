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

		# copy and analyze 3x3 region of the image

		mx = [
			[ (0,0,0), (0,0,0), (0,0,0) ],
			[ (0,0,0), (0,0,0), (0,0,0) ],
			[ (0,0,0), (0,0,0), (0,0,0) ]
		]
		for y in range(1,height - 1):
			for x in range(1,width - 1):

				# copy 3x3 region

				mx[0][0] = pixels[x - 1, y - 1]
				mx[0][1] = pixels[x    , y - 1]
				mx[0][2] = pixels[x + 1, y - 1]

				mx[1][0] = pixels[x - 1, y]
				mx[1][1] = pixels[x    , y]
				mx[1][2] = pixels[x + 1, y]

				mx[2][0] = pixels[x - 1, y + 1]
				mx[2][1] = pixels[x    , y + 1]
				mx[2][2] = pixels[x + 1, y + 1]

				# calc sobel-ish difference

				diff = (
					mx[0][0][1] - mx[0][2][1] +
					mx[1][0][1] - mx[1][2][1] +
					mx[1][0][1] - mx[1][2][1] +
					mx[2][0][1] - mx[2][2][1]
				)

				# filter for only green

				if mx[1][1][0] > mx[1][1][1]: diff = 0
				if mx[1][1][2] > mx[1][1][1]: diff = 0

				# mark difference types (lighten, darken, unchanged) with color codes

				if abs(diff) < 4 * 157:
					result[x,y] = (0,0,255)
				elif diff < 0:
					result[x,y] = (255,0,0)
				else:
					result[x,y] = (0,255,0)

		if self.saveImage:
			target.save("/tmp/image.png","PNG")

		found = 0
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
				+ str.zfill(str(i),3)
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

		total = valueCount[0] + valueCount[1]
		if valueCount[1] > total * 0.8: return 1

		if valueCount[0] > valueCount[1]: return 2
		return 0


if __name__ == '__main__':

	try:
		(FindGreenDot()).main()
	except KeyboardInterrupt:
		print(" - interrupted")
