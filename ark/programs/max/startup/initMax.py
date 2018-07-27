
import os
os.environ['ARK_CURRENT_APP'] = 'max'

import sys
sys.path.append('C:/Python27/Lib/site-packages/')
import arkInit
arkInit.init()

import maxMenuInit

def main():
	print 'Python Max Init'
	maxMenuInit.initMenu()


def launchMenu():
	maxMenuInit.launchMenu()

if __name__ == '__main__':
	main()
