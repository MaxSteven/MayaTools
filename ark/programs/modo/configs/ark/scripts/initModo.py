#python
import sys
import os

def init(commandLine=False):
	if commandLine:
		os.environ['ARK_CURRENT_APP'] = 'modo_cl'
	else:
		os.environ['ARK_CURRENT_APP'] = 'modo'

	sys.path.insert(0, 'C:/Python27/Lib/site-packages/')

	import arkInit
	arkInit.init()

if __name__ == '__main__':
	init()
