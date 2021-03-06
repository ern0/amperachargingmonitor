#!/usr/bin/env python3

import sys
sys.dont_write_bytecode = True
import os

from PIL import Image


class FindGreenDot:

	# processing method

	WAY = "hard"

	# common parameters

	CROP_TOP = 50
	CROP_LEFT = 120
	CROP_BOTTOM = 90
	CROP_RIGHT = 50

	# easy way parameters

	GREEN_DIFF_SPLIT = 0.4
	SPOT_GREEN_LEVEL = 0.6
	RING_DARK_LEVEL = 0.3

	# hard way parameters

	SOBEL_DIFF_SPLIT = 0.6
	MIN_SIZE_PX = 2
	MIN_FILL_RATIO = 0.6
	MIN_FILL_PIX = 5
	MAX_SQUARE_RATIO = 1.5
	MAX_SQUARE_DIFF = 3


	def main(self):

		try: 
			fnam = sys.argv[1]
		except: 
			self.fatal(
				"filename must be specified \n"
				"  second arg is frame number (optional, ALL if not specified)"
			)
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


	def dumpParams(self):

		print("WAY = " + str(self.WAY))
		print()

		print("CROP_TOP = " + str(self.CROP_TOP))
		print("CROP_LEFT = " + str(self.CROP_LEFT))
		print("CROP_BOTTOM = " + str(self.CROP_BOTTOM))
		print("CROP_RIGHT = " + str(self.CROP_RIGHT))

		if self.WAY == "hard":
			print("SOBEL_DIFF_SPLIT = " + str(self.SOBEL_DIFF_SPLIT))
			print("MIN_SIZE_PX = " + str(self.MIN_SIZE_PX))
			print("MIN_FILL_RATIO = " + str(self.MIN_FILL_RATIO))
			print("MIN_FILL_PIX = " + str(self.MIN_FILL_PIX))
			print("MAX_SQUARE_RATIO = " + str(self.MAX_SQUARE_RATIO))
			print("MAX_SQUARE_DIFF = " + str(self.MAX_SQUARE_DIFF))

		if self.WAY == "easy":
			print("SPOT_GREEN_LEVEL = " + str(self.SPOT_GREEN_LEVEL))
			print("RING_DARK_LEVEL = " + str(self.RING_DARK_LEVEL))

		print()


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


	def procFrames(self,fnam,specifiedFrame = None):

		frameCount = self.countNumberOfFrames(fnam)

		if specifiedFrame is None:
			frameRange = range(0,frameCount)
			self.debugMode = False
		else:
			frameRange = [ specifiedFrame, ]
			self.debugMode = True

		self.valueCount = [0,0]
		for i in frameRange:

			self.extractFrame(fnam,i)
			found = self.procImage(fnam)
			if found > 0: value = 1
			else: value = 0

			self.valueCount[value] += 1

			sys.stderr.write(
				fnam
				+ ":"
				+ str.zfill(str(i),3)
				+ " "
			)

			for i in range(0,min(found,20)):
				sys.stderr.write("#")
			if found > 20: sys.stderr.write(".")

			sys.stderr.write(
				" "
				+ str(found)
				+ "\n"
			)

			sys.stderr.flush()

		sys.stderr.write(
			" dark="
			+ str(self.valueCount[0])
			+ " light="
			+ str(self.valueCount[1])
			+ "\n"
		)
		sys.stderr.flush()

		if self.valueCount[0] == 0: return 1
		if self.valueCount[1] == 0: return 0

		total = self.valueCount[0] + self.valueCount[1]
		if self.valueCount[1] > total * 0.8: return 1

		if self.valueCount[0] > self.valueCount[1]: return 2
		return 0


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
		(self.width,self.height) = source.size

		if (
			self.width - self.CROP_LEFT - self.CROP_RIGHT < 32
			or
			self.height - self.CROP_TOP - self.CROP_BOTTOM < 32
		):
			self.fatal(
				"image is too small: "
				+ str(self.width)
				+ " x "
				+ str(self.height)
			)

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

					outside = False
					if x < self.CROP_LEFT: outside = True
					elif x > self.width - self.CROP_RIGHT: outside = True
					elif y < self.CROP_TOP: outside = True
					elif y > self.height - self.CROP_BOTTOM: outside = True

					if outside:
						self.result[x + self.width + 1, y] = (
							int(self.pixels[x,y][0] / 2),
							int(self.pixels[x,y][1] / 2),
							int(self.pixels[x,y][2] / 2)
						)
						if int(x / 8) % 2 ^ int(y / 8) % 2:
							self.result[x,y] = (63,63,63)
						else:
							self.result[x,y] = (15,15,15)

					else: # inside
						self.result[x + self.width + 1, y] = self.pixels[x,y]

		# perform the job

		found = -1
		if self.WAY == "hard": found = self.procImageTheHardWay()
		else: found = self.procImageTheEasyWay()

		# save image for debugging purposes

		if self.debugMode:
			target.save("/tmp/image.png","PNG")

		return found


	def findLightnessValues(self):
		# notice: using full image, no crop applied

		occurrences = [0] * 256

		for y in range(1,self.height - 1):
			for x in range(1,self.width - 1):
				pix = self.pixels[x,y]

				g = pix[1]
				occurrences[g] += 1

		numberOfPixels = self.height * self.width

		bottomLimit = numberOfPixels * 0.01
		topLimit = numberOfPixels * 0.99

		bottomFound = None
		topFound = None

		counter = 0
		for lightness in range(0,256):

			if bottomFound is None and counter >= bottomLimit:
				bottomFound = lightness

			if topFound is None and counter >= topLimit:
				topFound = lightness
				break

			counter += occurrences[lightness]

		if bottomFound is None: bottomFound = 0
		if topFound is None: topFound = 255

		diff = topFound - bottomFound
		if diff < 50:	diff = 50

		self.sobelChangeLimit = int(bottomFound + ( diff * self.SOBEL_DIFF_SPLIT ))
		self.simpleChangeLimit = int(bottomFound + ( diff * self.GREEN_DIFF_SPLIT ))
		self.simpleGreenLimit = int(bottomFound + ( diff * self.SPOT_GREEN_LEVEL ))
		self.simpleDarkLimit = int(bottomFound + ( diff * self.RING_DARK_LEVEL ))

		if False:
			print(
				self.sobelChangeLimit
				,self.simpleChangeLimit
				,self.simpleGreenLimit
				,self.simpleDarkLimit
			)
			quit()

	def procImageTheHardWay(self):

		self.findLightnessValues()
		self.hardSetEnums()
		self.hardFindEdges()
		self.hardFillGaps()
		self.hardCollectSpots()
		self.hardCalcBoundingRects()
		self.hardUnionBoundingRects()
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

		for y in range(1 + self.CROP_TOP,self.height - 1 - self.CROP_BOTTOM):
			for x in range(1 + self.CROP_LEFT,self.width - 1 - self.CROP_RIGHT):

				# copy 3x3 region (known issue: not used in this version)

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

				if abs(diff) > self.sobelChangeLimit:
					if diff > 0:
						self.result[x,y] = (1,255,self.CHANGE_LIGHTER)
					else:
						self.result[x,y] = (255,1,self.CHANGE_DARKER)
				else:
					self.result[x,y] = (0,0,self.CHANGE_SMALL)


	def hardFillGaps(self):

		for y in range(1 + self.CROP_TOP,self.height - 1 - self.CROP_BOTTOM):
			fill = self.FILL_OFF
			for x in range(1 + self.CROP_LEFT,self.width - 1 - self.CROP_RIGHT):
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

		for y in range(2 + self.CROP_TOP,self.height - 2 - self.CROP_BOTTOM):
			for x in range(2 + self.CROP_LEFT,self.width - 2 - self.CROP_RIGHT):
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

		self.spotPixels = {}

		self.spotTops = {}
		self.spotBottoms = {}
		self.spotLefts = {}
		self.spotRights = {}

		for spotCoords in self.spotMap:
			spotId = self.spotMap[spotCoords]

			if spotId not in self.spotPixels:

				self.spotPixels[spotId] = 0

				self.spotTops[spotId] = spotCoords[1]
				self.spotBottoms[spotId] = spotCoords[1]
				self.spotLefts[spotId] = spotCoords[0]
				self.spotRights[spotId] = spotCoords[0]

			self.spotPixels[spotId] += 1

			if spotCoords[1] < self.spotTops[spotId]: self.spotTops[spotId] = spotCoords[1]
			if spotCoords[1] > self.spotBottoms[spotId]: self.spotBottoms[spotId] = spotCoords[1]
			if spotCoords[0] < self.spotLefts[spotId]: self.spotLefts[spotId] = spotCoords[0]
			if spotCoords[0] > self.spotRights[spotId]: self.spotRights[spotId] = spotCoords[0]


	def hardUnionBoundingRects(self):

		unions = {}
		membership = {}

		# find near or fully overlapping bounding boxes

		for id1 in self.spotPixels:
			for id2 in self.spotPixels:

				if id2 <= id1: continue
				# assert: id1 < id2

				uniteVert = False

				if (
					self.spotTops[id1]
					<= self.spotTops[id2] - 2 <=
					self.spotBottoms[id1]
				): uniteVert = True

				if (
					self.spotTops[id1]
					<= self.spotBottoms[id2] + 2 <=
					self.spotBottoms[id1]
				): uniteVert = True

				uniteHoriz = False

				if (
					self.spotLefts[id1]
					<= self.spotLefts[id2] - 2 <=
					self.spotRights[id1]
				): uniteHoriz = True

				if (
					self.spotLefts[id1]
					<= self.spotRights[id2] + 2 <=
					self.spotRights[id1]
				): uniteHoriz = True

				if not (uniteHoriz and uniteVert): continue

				# checkpoint: put id1 and id2 into union

				# head is id1 or its head
				if id1 in membership:
					headId = membership[id1]
				else:
					headId = id1

				# create head if new
				if headId not in unions:
					unions[headId] = {}

				# eliminate id2 as union head, if it was,
				# preserve members
				if id2 in unions:
					members = unions[id2]
					del unions[id2]

				# or just create a fake member list
				else:
					members = [ id2 ]

				# add id2 members to head
				for memberId in members:
					unions[headId][memberId] = None
					membership[memberId] = headId

		# make unions

		for headId in unions:
			for memberId in unions[headId]:

				self.spotTops[headId] = min(self.spotTops[headId],self.spotTops[memberId])
				self.spotBottoms[headId] = max(self.spotBottoms[headId],self.spotBottoms[memberId])
				self.spotLefts[headId] = min(self.spotLefts[headId],self.spotLefts[memberId])
				self.spotRights[headId] = max(self.spotRights[headId],self.spotRights[memberId])
				self.spotPixels[headId] += self.spotPixels[memberId]


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
				squareRatio = None
				printableRatio = "n.a."
			else:
				squareRatio = max(correctedW,h) / min(correctedW,h)
				printableRatio = str(round(squareRatio * 100) / 100) + ":1"

			squareDiff = max(correctedW,h) - min(correctedW,h)

			# print some info when debugging

			if self.debugMode: print(
				"#" + str(spotId),
				"TL:",
				str(self.spotLefts[spotId]) + ";" +
				str(self.spotTops[spotId]),
				"dim:",
				str(w) + "x" + str(h),
				"(" +	str(correctedW) + "x" + str(h) + ")",
				"ratio:",
				printableRatio,
				"diff:",
				squareDiff,
				"filled:",
				str(self.spotPixels[spotId]) + "/" + str(w * h),
				str(round(fillRatio * 10000) / 100) + "%",
				end = " -"
			)

			# drop small ones (using corrected width for size)

			if correctedW < self.MIN_SIZE_PX and h < self.MIN_SIZE_PX:
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

			isSquare = 0

			if squareRatio is not None:
				if squareRatio <= self.MAX_SQUARE_RATIO:
					isSquare += 1

			if squareDiff <= self.MAX_SQUARE_DIFF:
				isSquare += 1

			if isSquare == 0:
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
							if extra: self.result[x,y] = (127,127,255)
							else: self.result[x,y] = (63,63,127)

						else:
							if extra: self.result[x,y] = (127,127,127)
							else: self.result[x,y] = (63,63,63)


	def procImageTheEasyWay(self):

		self.findLightnessValues()
		self.easyCheckSpotAndRing()
		return self.easyCountMatches()


	def easyCheckSpotAndRing(self):

		# transform pixels to match flag

		for y in range(11 + self.CROP_TOP,self.height - 11 - self.CROP_BOTTOM):
			for x in range(11 + self.CROP_LEFT,self.width - 11 - self.CROP_RIGHT):

				# check center: is it green and light enough?

				g1 = self.easyBlurSpot(1,x,y)
				if g1 < self.simpleGreenLimit: continue

				r1 = self.easyBlurSpot(0,x,y)
				if g1 <= r1: continue

				b1 = self.easyBlurSpot(2,x,y)
				if g1 <= b1: continue

				# check ring: is it dark enough?

				r2 = self.easyBlurRing(0,x,y)
				g2 = self.easyBlurRing(1,x,y)
				b2 = self.easyBlurRing(2,x,y)

				if g2 > self.simpleDarkLimit: continue

				r = r1 - r2
				if r < 0: r = 0
				g = g1 - g2
				if g < 0: g = 0
				b = b1 - b2
				if b < 0: b = 0

				#print(g,self.simpleChangeLimit)
				if g < self.simpleChangeLimit: continue

				self.result[x,y] = (255,255,255)


	def easyBlurSpot(self,i,x,y):

		v = self.pixels[ x - 1, y - 1 ][i]
		v += self.pixels[ x    , y - 1 ][i] * 2
		v += self.pixels[ x + 1, y - 1 ][i]
		v += self.pixels[ x - 1, y ][i] * 2
		v += self.pixels[ x    , y ][i] * 4
		v += self.pixels[ x + 1, y ][i] * 2
		v += self.pixels[ x - 1, y + 1 ][i]
		v += self.pixels[ x    , y + 1 ][i] * 2
		v += self.pixels[ x + 1, y + 1 ][i]

		return int(v / 16)


	def easyBlurRing(self,i,x,y):

		v = 0

		for offset in (-5,+5):
			v += self.pixels[ x - 2, y + offset][i]
			v += self.pixels[ x - 1, y + offset][i]
			v += self.pixels[ x    , y + offset][i]
			v += self.pixels[ x + 1, y + offset][i]
			v += self.pixels[ x + 2, y + offset][i]

		for offset in (-4,+4):
			v += self.pixels[ x - 3, y + offset][i]
			v += self.pixels[ x - 2, y + offset][i]
			v += self.pixels[ x - 1, y + offset][i]
			v += self.pixels[ x    , y + offset][i]
			v += self.pixels[ x + 1, y + offset][i]
			v += self.pixels[ x + 2, y + offset][i]
			v += self.pixels[ x + 3, y + offset][i]

		for offset in (-3,+3):
			v += self.pixels[ x - 4, y - offset][i]
			v += self.pixels[ x - 3, y - offset][i]
			v += self.pixels[ x + 3, y - offset][i]
			v += self.pixels[ x + 4, y - offset][i]

		for offset in (-2,-1,0,+1,+2):
			v += self.pixels[ x - 5, y - offset][i]
			v += self.pixels[ x - 4, y - offset][i]
			v += self.pixels[ x + 4, y - offset][i]
			v += self.pixels[ x + 5, y - offset][i]

		return int(v / 52)


	def easyCountMatches(self):

		found = 0

		for y in range(11 + self.CROP_TOP,self.height - 11 - self.CROP_BOTTOM):
			for x in range(11 + self.CROP_LEFT,self.width - 11 - self.CROP_RIGHT):

				if self.result[x,y][1] != 255: continue
				found += 1

		return found


if __name__ == '__main__':

	try:
		(FindGreenDot()).main()
	except KeyboardInterrupt:
		print(" - interrupted")
