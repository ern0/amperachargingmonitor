#!/usr/bin/env python3 -B

import os
import sys

class ReportLastFiles:

	def main(self):

		print(sys.argv[1])
		print(sys.argv[2])


if __name__ == '__main__':

	try:
		(ReportLastFiles()).main()
	except KeyboardInterrupt:
		print(" - interrupted")
