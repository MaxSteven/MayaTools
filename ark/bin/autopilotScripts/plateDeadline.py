import os
import cOS
from datetime import datetime, timedelta

import settingsManager
globalSettings = settingsManager.globalSettings()

rootDir = globalSettings.RAMBURGLAR
lineBreak = '-------------------------------------\n'
now = datetime.now()
weeks = 2

def main():

	for root, dirs, files in os.walk(rootDir):
		for f in files:
			if f.endswith('.nk~'):
				print cOS.join(root, f)

		# for dir in dirs:
		# 	print subdir, dir
		# for f in files:
		# 	print f

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
