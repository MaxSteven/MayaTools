import sys
import time

def getIdleTime():
	if sys.platform == 'win32':

		import ctypes

		class LastInputInfo(ctypes.Structure):
			_fields_ = [
				('cbSize', ctypes.c_uint),
				('dwTime', ctypes.c_int)
			]

		def getIdleDuration():
			lastInputInfo = LastInputInfo()
			lastInputInfo.cbSize = ctypes.sizeof(lastInputInfo)
			if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lastInputInfo)):
				millis = ctypes.windll.kernel32.GetTickCount() - lastInputInfo.dwTime
				return millis / 1000.0

			else:
				return 0

		while True:
			duration = getIdleDuration()
			time.sleep(1)
			return duration

	elif sys.platform == 'linux2':

		import xprintidle

		while True:
			duration = xprintidle.idle_time()/1000.0
			time.sleep(1)
			return duration

def main():
	time.sleep(10)
	print getIdleTime()

if __name__ == '__main__':
	main()

