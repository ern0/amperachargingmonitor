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


	def procImage(self,fnam,way = "hard"):

		source = Image.open(self.mkTmpImgPath(fnam))
		(self.width,self.height) = source.size
		self.pixels = source.load()

		target = Image.new(
			"RGB",
			(self.width * 2 + 1, self.height),
			"black"
		)
		self.result = target.load()

		# copy source and draw separator

		if self.debugMode:
			for y in range(0,self.height):
				self.result[self.width,y] = (0,255,0)
				for x in range(0,self.width):
					self.result[x + self.width + 1, y] = self.pixels[x,y]

		# perform the job

		found = -1
		if way == "hard": found = self.procImageTheHardWay()
		else: found = self.procImageTheEasyWay()

		# save image for debugging purposes

		if self.debugMode:
			target.save("/tmp/image.png","PNG")

		return found


	def procImageTheHardWay(self):

		self.hardSetEnums()
		self.hardFindEdges()
		self.hardFillGaps()
		self.hardCollectSpots()
		self.hardCalcBoundingRects()
		self.hardFindMatchingSpots()
		self.hardDrawBoundingBoxes()

		return self.found


	def hardSetEnums(self):

		self.CHANGE_SMALL = 0
		self.CHANGE_LIGHTER = 1
		self.CHANGE_DARKER = 2
		self.CHANGE_FILL = 3
		self.FILL_OFF = -1


	def hardFindEdges(self):

		# create placeholder 3x3 matrix

		mx = [
			[ (0,0,0), (0,0,0), (0,0,0) ],
			[ (0,0,0), (0,0,0), (0,0,0) ],
			[ (0,0,0), (0,0,0), (0,0,0) ]
		]

		# foreach image-pixel

		for y in range(1,self.height - 1):
			for x in range(1,self.width - 1):

				# copy 3x3 region (known issue: not used now)

				mx[0][0] = self.pixels[x - 1, y - 1]
				mx[0][1] = self.pixels[x    , y - 1]
				mx[0][2] = self.pixels[x + 1, y - 1]

				mx[1][0] = self.pixels[x - 1, y]
				mx[1][1] = self.pixels[x    , y]
				mx[1][2] = self.pixels[x + 1, y]

				mx[2][0] = self.pixels[x - 1, y + 1]
				mx[2][1] = self.pixels[x    , y + 1]
				mx[2][2] = self.pixels[x + 1, y + 1]

				# calc sobel-ish difference

				diff = mx[1][2][1] - mx[1][0][1]

				# filter for only green

				if mx[1][1][0] > mx[1][1][1]: diff = 0
				if mx[1][1][2] > mx[1][1][1]: diff = 0

				# mark difference types (lighten, darken, unchanged) with color codes

				if diff > 0:

					if abs(diff) > self.SOBEL_DIFF_LIGHTER:
						self.result[x,y] = (1,255,self.CHANGE_LIGHTER)
					else:
						self.result[x,y] = (0,0,self.CHANGE_SMALL)

				else:

					if abs(diff) > self.SOBEL_DIFF_DARKER:
						self.result[x,y] = (255,1,self.CHANGE_DARKER)
					else:
						self.result[x,y] = (0,0,self.CHANGE_SMALL)


	def hardFillGaps(self):

		for y in range(1,self.height - 1):
			fill = self.FILL_OFF
			for x in range(1,self.width - 1):
				pix = self.result[x,y]

				if fill == self.FILL_OFF and pix[2] == self.CHANGE_LIGHTER:
					fill = x + 1

				if fill != self.FILL_OFF and pix[2] == self.CHANGE_DARKER:
					if x - fill < 15:
						for gap in range(fill,x): self.result[gap,y] = (255,255,self.CHANGE_FILL)
					fill = self.FILL_OFF


	def hardCollectSpots(self):

		# neighbour offset x,y pairs for later use

		xyOffsets = [
			(-1,-2), ( 0,-2), (+1,-2),
			( 0,-1), ( 0,-1), (+1,-1),
			(-1,0)
		]

		# spotMap[ tupleof(x,y) ] = spot ID
		self.spotMap = {}

		# initial spot ID
		nextSpotId = 1

		for y in range(2,self.height - 2):
			for x in range(2,self.width - 2):
				if self.result[x,y][2] == self.CHANGE_SMALL: continue

				# add current diff-pixel to an existing spot, or create a new one

				neighbourSpots = {}  # neighbourSpots[ spotId ] = dummy

				# collect neigbour spot IDs

				for xyOffset in xyOffsets:
					xy = ( x + xyOffset[0], y + xyOffset[1] )

					if xy not in self.spotMap: continue
					spotId = self.spotMap[xy]
					neighbourSpots[spotId] = None

				# if there is no neighbour, register new spot

				if len(neighbourSpots) == 0:
					self.spotMap[x,y] = nextSpotId
					nextSpotId += 1

				# else make union for all spots touched as neighbour

				else:
					# pick a random neighbour's ID
					for unionId in neighbourSpots: break

					# change all neighbours' ID in spotMap to union ID
					for obsoleteSpotId in neighbourSpots:
						for xy in self.spotMap:
							if self.spotMap[xy] != obsoleteSpotId: continue
							self.spotMap[xy] = unionId

					# set current diff-pixel ID to union ID
					self.spotMap[x,y] = unionId


	def hardCalcBoundingRects(self):

		self.spotTops = {}
		self.spotBottoms = {}
		self.spotLefts = {}
		self.spotRights = {}
		self.spotPixels = {}

		for spotCoords in self.spotMap:
			spotId = self.spotMap[spotCoords]

			if spotId not in self.spotPixels:
				self.spotTops[spotId] = spotCoords[1]
				self.spotBottoms[spotId] = spotCoords[1]
				self.spotLefts[spotId] = spotCoords[0]
				self.spotRights[spotId] = spotCoords[0]
				self.spotPixels[spotId] = 0

			if spotCoords[1] < self.spotTops[spotId]: self.spotTops[spotId] = spotCoords[1]
			if spotCoords[1] > self.spotBottoms[spotId]: self.spotBottoms[spotId] = spotCoords[1]
			if spotCoords[0] < self.spotLefts[spotId]: self.spotLefts[spotId] = spotCoords[0]
			if spotCoords[0] > self.spotRights[spotId]: self.spotRights[spotId] = spotCoords[0]

			self.spotPixels[spotId] += 1

			# TODO: find spot to attach this spot


	def hardFindMatchingSpots(self):

		self.found = 0
		self.match = {}
		for spotId in self.spotPixels:

			# calculate bounding rectangle width and height
			# we used horizontal sobel, so width is corrected

			w = self.spotRights[spotId] - self.spotLefts[spotId] + 1
			h = self.spotBottoms[spotId] - self.spotTops[spotId] + 1
			correctedW = w - 1

			self.match[spotId] = True

			# pre-calculate some values for debugging

			fillRatio = self.spotPixels[spotId] / (w * h)
			if correctedW == 0 or h == 0:
				ratio = None
				printableRatio = "n.a."
			else:
				ratio = max(correctedW,h) / min(correctedW,h)
				printableRatio = str(round(ratio * 100) / 100) + ":1"

			# print some info when debugging

			if self.debugMode: print(
				"TL:",
				str(self.spotLefts[spotId]) + ";" +
				str(self.spotTops[spotId]),
				"dim:",
				str(w) + "x" + str(h),
				"(" +	str(correctedW) + "x" + str(h) + ")",
				"ratio:",
				printableRatio,
				"filled:",
				str(self.spotPixels[spotId]) + "/" + str(w * h),
				str(round(fillRatio * 10000) / 100) + "%",
				end = " -"
			)

			# drop small ones (using corrected width for size)

			if correctedW < self.MIN_SIZE_PX or h < self.MIN_SIZE_PX:
				if self.debugMode: print(" small_size",end="")
				self.match[spotId] = False

			# drop ones with weak fill ratio, e.g. diagonal lines
			# (using uncorrected width for fill ratio)

			if fillRatio < self.MIN_FILL_RATIO:
				if self.debugMode: print(" fill_ratio",end="")
				self.match[spotId] = False

			# drop ones with only few pixels filled

			if self.spotPixels[spotId] < self.MIN_FILL_PIX:
				if self.debugMode: print(" fill_number",end="")
				self.match[spotId] = False

			# drop non-square-ish shapes

			if ratio is not None:
				if ratio < self.MIN_SQUARE_RATIO:
					if self.debugMode: print(" not_square",end="")
					self.match[spotId] = False

			# checkpoint, report if no matching failed

			if self.match[spotId]:
				self.found += 1
				if self.debugMode: print(" PASSED.")
			else:
				if self.debugMode: print()


	def hardDrawBoundingBoxes(self):

			if not self.debugMode: return

			for spotId in self.spotPixels:

				for y in range(self.spotTops[spotId] - 1,self.spotBottoms[spotId] + 2):
					for x in range(self.spotLefts[spotId] - 1,self.spotRights[spotId] + 2):
						if self.result[x,y][2] != self.CHANGE_SMALL: continue

						extra = False
						if y < self.spotTops[spotId]: extra = True
						if y > self.spotBottoms[spotId]: extra = True
						if x < self.spotLefts[spotId]: extra = True
						if x > self.spotRights[spotId]: extra = True

						if self.match[spotId]:
							if extra: self.result[x,y] = (192,192,255)
							else: self.result[x,y] = (0,0,255)

						else:
							if extra: self.result[x,y] = (127,127,127)
							else: self.result[x,y] = (63,63,63)


	def procFrames(self,fnam,specifiedFrame = None):

		frameCount = self.countNumberOfFrames(fnam)

		if specifiedFrame is None:
			frameRange = range(0,frameCount)
			self.debugMode = False
		else:
			frameRange = [ specifiedFrame, ]
			self.debugMode = True

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
