#!/usr/bin/env python

import struct
import sys
import json

import arkInit
arkInit.init()

import cOS

# On Windows, the default I/O mode is O_TEXT. Set this to O_BINARY
# to avoid unwanted modifications of the input/output streams.
if sys.platform == "win32":
	import os, msvcrt
	msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
	msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

# Thread that reads messages from the webapp.
def read_thread_func():
	while 1:
		# Read the message length (first 4 bytes).
		text_length_bytes = sys.stdin.read(4)

		if len(text_length_bytes) == 0:
			sys.exit(0)

		# Unpack message length as 4 byte integer.
		text_length = struct.unpack('i', text_length_bytes)[0]

		# Read the text (JSON object) of the message.
		text = json.loads(sys.stdin.read(text_length).decode('utf-8'))['text']
		return text

def Main():

	string = read_thread_func()

	with open('C:/testfile.txt', 'w') as f:
		 f.write(string)

	if string:
		cOS.startSubprocess(string)
		# subprocess.call(string)


if __name__ == '__main__':
	Main()
