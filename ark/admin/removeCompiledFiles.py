
# Standard modules
import os

# Our modules
import arkInit
arkInit.init()

import moduleTools

def main():
	options = moduleTools.loadModuleOptions()
	for module in options:
		files = moduleTools.getModuleFiles(
			module['path'],
			fileIncludes=['*.pyc'])

		for filename in files:
			print 'remove pyc:', filename
			try:
				os.remove(filename)
			except Exception as err:
				print err

if __name__ == '__main__':
	main()
