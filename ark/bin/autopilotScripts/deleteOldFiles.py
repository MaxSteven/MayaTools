import os
import cOS
from datetime import datetime, timedelta

import settingsManager
globalSettings = settingsManager.globalSettings()

rootDir = globalSettings.TRASH_ROOT
lineBreak = '-------------------------------------\n'
now = datetime.now()
weeks = 2

def main():

	for subdir, dirs, files in os.walk(rootDir):
		for f in files:
			path = cOS.join(subdir, f)

			try:
				if olderThan(path):
					print 'DELETING:\t', path
					os.remove(path)
				print lineBreak
			except OSError as ex:
				print(ex)

	deleteEmptyDirs()

def olderThan(path):
	modTime = int(os.path.getmtime(path))
	print 'CURR PATH:\t', path
	print 'MOD TIME:\t', datetime.fromtimestamp(modTime)

	howOld = now - timedelta(weeks = weeks)
	pathTime = datetime.fromtimestamp(modTime)

	return pathTime < howOld

# bottom up search for empty dirs older than the globally set number of weeks
def deleteEmptyDirs():
	 for dirpath, subdir, files in os.walk(rootDir, topdown=False):
		if dirpath == rootDir:
			break
		try:
			if olderThan(dirpath):
				print 'DELETING:\t', dirpath
				os.rmdir(dirpath)
			print lineBreak
		except OSError as ex:
			print(ex)

if __name__ == '__main__':
	main()
