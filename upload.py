#!/usr/bin/env python3

import sys
sys.dont_write_bytecode = True
import os
import glob
import time
import urllib.request
import urllib.parse
import json


class Upload:

	def main(self):

		self.procDir = sys.argv[1]
		self.doneDir = sys.argv[2]
		self.apiKey = sys.argv[3]
		self.feedId = sys.argv[4]

		last = ""
		idleReported = False

		while True:

			self.file = None
			pattern = self.procDir + "/*.txt"
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

		fnam = os.path.basename(self.file)
		self.backup = self.doneDir + "/" + fnam
		stamp = fnam.replace(".txt","")

		pattern = '%Y-%m-%dT%H:%M:%S'
		epoch = int(time.mktime(time.strptime(stamp,pattern)))

		with open(self.file) as f: 
			value = f.read().strip()

		sys.stderr.write(fnam + "... ")
		sys.stderr.flush()

		attempt = 0
		while True:
			attempt += 1

			url = "http://iotplotter.com/api/v2/feed/" 
			url += self.feedId
					
			headers = { "api-key": self.apiKey }

			data = {
				"data": {
					"charging": [{
						"value": int(value)
						,"epoch": epoch
					}]
				}
			}
			data = json.dumps(data).encode("utf-8")

			try:
				req = urllib.request.Request(
					url
					,headers=headers
					,data=data
				)
				response = urllib.request.urlopen(req)

			except urllib.error.HTTPError as e:
				if e.getcode() == 400:
					print("fatal error: " + str(e))
					quit(1)

			except Exception as e:
				print("Attempt " + str(attempt) + " failed: " + str(e))
				time.sleep(1)
				continue

			if str(response.getcode()) != "200":
				print("fatal error: update failed")
				quit(1)

			break

		sys.stderr.write("done\n")
		sys.stderr.flush()

		os.rename(self.file,self.backup)
		time.sleep(1)


if __name__ == '__main__':

	try:
		(Upload()).main()
	except KeyboardInterrupt:
		print(" - interrupted")
