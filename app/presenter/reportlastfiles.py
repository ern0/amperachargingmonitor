#!/usr/bin/env python3

import os
import sys
import serial
import time


class ReportLastFiles:

	def main(self):

		try:
			directory = sys.argv[1]
			device = sys.argv[2]
			delay = float(sys.argv[3])
			once = int(sys.argv[4])
		except IndexError:
			print("usage: \n reportlastfiles.py directory device delay once")
			quit()
		except ValueError:
			print("invalid value")
			quit()

		self.connectEarly(device)

		while True:
			self.collectLastResults(directory)
			self.fillUnusedSlots()
			self.lightLeds(delay)

			if once > 0: break

			time.sleep(66)

	
	def collectLastResults(self, directory):
		
		self.collectedItems = []

		allFiles = os.listdir(directory)
		lastFiles = sorted(allFiles)[-8:]
		#lastFiles = allFiles[-6:] ####
		
		for filename in lastFiles:
			with open(directory + "/" + filename) as f:
				value = f.read().strip()

			self.collectedItems.append(value)


	def fillUnusedSlots(self):

		self.paddedItems = []

		for i in range(0, 8 - len(self.collectedItems)):
			self.paddedItems.append("4")
		
		for value in self.collectedItems:
			self.paddedItems.append(value)


	def connectEarly(self, device):
		self.ser = serial.Serial(device, 9600)


	def lightLeds(self, delay):

		data = ":"
		for item in self.paddedItems:
			if item == "0": data += "008"
			if item == "1": data += "f00"
			if item == "2": data += "040"
			if item == "4": data += "101"
		data += ";"

		time.sleep(delay);

		self.ser.write(data.encode())


if __name__ == '__main__':

	try:
		(ReportLastFiles()).main()
	except KeyboardInterrupt:
		print(" - interrupted")
