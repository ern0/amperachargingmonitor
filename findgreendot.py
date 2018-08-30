#!/usr/bin/env python3

import sys
sys.dont_write_bytecode = True
import os

from PIL import Image


class FindGreenDot:


	# image parameters

	SOBEL_DIFF_LIGHTER = 170
	SOBEL_DIFF_DARKER = 150
	
	# spot parameters

	MIN_SIZE_PX = 2
	MIN_FILL_RATIO = 0.6
	MIN_FILL_PIX = 5
	MIN_SQUARE_RATIO = 0.7


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

		CHANGE_SMALL = 0
		CHANGE_LIGHTER = 1
		CHANGE_DARKER = 2
		CHANGE_FILL = 3
		FILL_OFF = -1

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
					mx[1][2][1] - mx[1][0][1]
				)

				# filter for only green

				if mx[1][1][0] > mx[1][1][1]: diff = 0
				if mx[1][1][2] > mx[1][1][1]: diff = 0

				# mark difference types (lighten, darken, unchanged) with color codes

				if diff > 0:

					if abs(diff) > self.SOBEL_DIFF_LIGHTER:
						result[x,y] = (1,255,CHANGE_LIGHTER)
					else:
						result[x,y] = (0,0,CHANGE_SMALL)

				else:

					if abs(diff) > self.SOBEL_DIFF_DARKER:
						result[x,y] = (255,1,CHANGE_DARKER)
					else:
						result[x,y] = (0,0,CHANGE_SMALL)

		# fill gaps

		for y in range(1,height - 1):
			fill = FILL_OFF
			for x in range(1,width - 1):
				pix = result[x,y]

				if fill == FILL_OFF and pix[2] == CHANGE_LIGHTER:
					fill = x + 1

				if fill != FILL_OFF and pix[2] == CHANGE_DARKER:
					if x - fill < 15:
						for gap in range(fill,x): result[gap,y] = (255,255,CHANGE_FILL)
					fill = FILL_OFF

		# collect spots

		spotMap = {}
		spotNumero = 1
		for y in range(2,height - 2):
			for x in range(2,width - 2):
				if result[x,y][2] == CHANGE_SMALL: continue

				# neighbours: top 3 and left 1

				neighbourSpots = {}
				if (x - 1, y - 1) in spotMap: neighbourSpots[ spotMap[x - 1, y - 1] ] = None
				if (x, y - 1) in spotMap: neighbourSpots[ spotMap[x, y - 1] ] = None
				if (x + 1, y - 1) in spotMap: neighbourSpots[ spotMap[x + 1, y - 1] ] = None
				if (x - 1, y) in spotMap: neighbourSpots[ spotMap[x - 1, y] ] = None
				
				# if there is no neighbour, register new spot

				if len(neighbourSpots) == 0:
					spotMap[x,y] = spotNumero
					spotNumero += 1

				# if there are homogenous neighbours, 
				# add actual pixel to this spot

				elif len(neighbourSpots) == 1:
					for onlyNeighbourNo in neighbourSpots: break
					spotMap[x,y] = onlyNeighbourNo

				# if there're heterogeneous neigbours, pick first, 
				# then add actual and all other neighbours to this spot

				else:
					for firstNeighbourNo in neighbourSpots: break
					spotMap[x,y] = firstNeighbourNo
					if (x - 1, y - 1) in spotMap: spotMap[x - 1, y - 1] = firstNeighbourNo
					if (x   , y - 1) in spotMap: spotMap[x, y - 1] = firstNeighbourNo
					if (x + 1, y - 1) in spotMap: spotMap[x + 1, y - 1] = firstNeighbourNo
					if (x - 1, y) in spotMap: spotMap[x - 1, y] = firstNeighbourNo

		# get bounding rectangles of collected spots

		spotTops = {}
		spotBottoms = {}
		spotLefts = {}
		spotRights = {}
		spotPixels = {}
		for spotCoords in spotMap:
			spotId = spotMap[spotCoords]

			if spotId not in spotPixels:
				spotTops[spotId] = spotCoords[1]
				spotBottoms[spotId] = spotCoords[1]
				spotLefts[spotId] = spotCoords[0]
				spotRights[spotId] = spotCoords[0]
				spotPixels[spotId] = 0

			if spotCoords[1] < spotTops[spotId]: spotTops[spotId] = spotCoords[1]
			if spotCoords[1] > spotBottoms[spotId]: spotBottoms[spotId] = spotCoords[1]
			if spotCoords[0] < spotLefts[spotId]: spotLefts[spotId] = spotCoords[0]
			if spotCoords[0] > spotRights[spotId]: spotRights[spotId] = spotCoords[0]
			spotPixels[spotId] += 1

		# draw bounding boxes

		if self.saveImage: 
			for spotCoords in spotMap:
				spotId = spotMap[spotCoords]
				for y in range(spotTops[spotId],spotBottoms[spotId] + 1):
					for x in range(spotLefts[spotId],spotRights[spotId] + 1):
						if result[x,y][2] == CHANGE_SMALL:
							result[x,y] = (127,127,255)

		# find spots which matches our criterias

		found = 0
		for spotId in spotPixels:

			# calculate bounding rectangle width and height
			# we used horizontal sobel, so width is corrected

			w = spotRights[spotId] - spotLefts[spotId] + 1
			h = spotBottoms[spotId] - spotTops[spotId] + 1
			correctedW = w - 1

			# pre-calculate some values for debugging

			fillRatio = spotPixels[spotId] / (w * h)
			if correctedW == 0 or h == 0:
				printableRatio = "n.a."
			else:
				ratio = max(correctedW,h) / min(correctedW,h)
				printableRatio = str(round(ratio * 100) / 100) + ":1"

			# print some info when debugging

			if self.saveImage: print(
				"TL:",
				str(spotLefts[spotId]) + ";" +
				str(spotTops[spotId]),
				"dim:",
				str(w) + "x" + str(h),
				"(" +	str(correctedW) + "x" + str(h) + ")",
				"ratio:",
				printableRatio,
				"filled:",
				str(spotPixels[spotId]) + "/" + str(w * h),
				str(round(fillRatio * 10000) / 100) + "%",
				end = " - "
			)
			
			# drop small ones (using corrected width for size)

			if correctedW < self.MIN_SIZE_PX or h < self.MIN_SIZE_PX: 
				if self.saveImage: print("small size")
				continue

			# drop ones with weak fill ratio, e.g. diagonal lines
			# (using uncorrected width for fill ratio)

			if fillRatio < self.MIN_FILL_RATIO: 
				if self.saveImage: print("fill ratio")
				continue

			# drop ones with only few pixels filled

			if spotPixels[spotId] < self.MIN_FILL_PIX: 
				if self.saveImage: print("fill number")
				continue

			# drop non-square-ish shapes

			if ratio < self.MIN_SQUARE_RATIO: 
				if self.saveImage: print("not square")
				continue

			# checkpoint, all the criteria checks passed

			if self.saveImage: print("PASSED")
			found += 1

		# save image for debugging purposes

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
