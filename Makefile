
result.txt: \
		res01.txt \
		res02.txt \
		res03.txt \
		res04.txt \
		res05.txt \
		res06.txt \
		res07.txt \
		res08.txt \
		res09.txt \
		res10.txt
	cat res* > final.txt
	rm -f res*.txt

res01.txt:
	./findgreendot.py sample/afternoon-light-1.avi > res01.txt

res02.txt:
	./findgreendot.py sample/afternoon-none.avi > res02.txt

res03.txt:
	./findgreendot.py sample/dark-blink.avi > res03.txt

res04.txt:
	./findgreendot.py sample/dark-light-1.avi > res04.txt

res05.txt:
	./findgreendot.py sample/dark-light-2.avi > res05.txt

res06.txt:
	./findgreendot.py sample/morning-blink-1.avi > res06.txt

res07.txt:
	./findgreendot.py sample/morning-blink-2.avi > res07.txt

res08.txt:
	./findgreendot.py sample/morning-blink-3.avi > res08.txt

res09.txt:
	./findgreendot.py sample/morning-none-1.avi > res09.txt

res10.txt:
	./findgreendot.py sample/morning-none-2.avi > res10.txt
