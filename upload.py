#!/usr/bin/env python3

import sys
sys.dont_write_bytecode = True
import os
import glob
import time
import urllib.request


class Upload:

	def main(self):

		self.dataDir = sys.argv[1]
		self.apiKey = sys.argv[2]

		last = ""
		idleReported = False

		while True:

			self.file = None
			pattern = self.dataDir + "/*.txt"
			for self.file in glob.glob(pattern): break

			if self.file is None:
				
				time.sleep(1)
				
				if idleReported: continue
				idleReported = True

				print("(idle)")
				continue

			if self.file == last: 
				print("internal error: proc same file again")
				quit(1)

			last = self.file
			idleReported = False

			self.procFile()


	def procFile(self):

		stamp = os.path.basename(self.file)
		stamp = stamp.replace(".txt","")

		with open(self.file) as f: 
			value = f.read().strip()

		url = "https://api.thingspeak.com/update.json"
		url += "?api_key=" + self.apiKey
		url += "&created_at=" + stamp
		url += "&status=" + value

		print("request: " + stamp)

		attempt = 0
		while True:
			attempt += 1

			try:
				response = urllib.request.urlopen(url)
				data = response.read().decode("utf-8").strip()

			except urllib.error.HTTPError as e:
				if e.getcode() == 400:
					print("fatal error: " + str(e))
					quit(1)

			except Exception as e:
				print("Attempt " + str(attempt) + " failed: " + str(e))
				time.sleep(1)
				continue

			if data[0] == "0": 
				print("fatal error: update failed")
				quit(1)

			break

		os.unlink(self.file)
		time.sleep(15)


if __name__ == '__main__':

	try:
		(Upload()).main()
	except KeyboardInterrupt:
		print(" - interrupted")
