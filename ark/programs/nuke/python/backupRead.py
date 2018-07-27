import nuke
import sys

import arkInit
arkInit.init()

import cOS
import arkUtil
import shutil

def getArchivePath(path, archive):
	ogRoot = path.split('/')[0] + '/'
	return path.replace(ogRoot, archive)

def copyReadFiles(nukeScriptFile, archive):

	print 'Archive:', archive
	print 'File', nukeScriptFile

	nuke.scriptOpen(nukeScriptFile)
	validReadNodes = ['Read','DeepRead']

	for node in nuke.allNodes():
		if node.Class() in validReadNodes:
			readPath = node['file'].getValue()
			readPath = cOS.normalizePath(readPath)
			startFrame = node['first'].getValue()
			endFrame = node['last'].getValue()

			if '#' in readPath:
				initPos = i = readPath.index('#')
				while readPath[i] == '#':
					i += 1
				padding = i - initPos
				failed = False

				print 'Copy:', readPath
				for frame in xrange(int(startFrame), int(endFrame) + 1):
					fileToCopy = readPath.replace('#'*padding, arkUtil.pad(frame, padding))
					dest = getArchivePath(fileToCopy, archive)

					print fileToCopy, ' > ', dest
					cOS.makeDirs(dest)
					try:
						shutil.copyfile(fileToCopy, dest)
					except Exception as err:
						print err
						failed = True

				if failed:
					print '\n\nFAILED:', readPath
				node['file'].setValue(getArchivePath(readPath, archive))
			elif '%' in readPath:
				initPos = readPath.index('%')
				padding = int(readPath[initPos + 2])
				failed = False

				print 'Copy:', readPath
				for frame in xrange(int(startFrame), int(endFrame) + 1):
					fileToCopy = readPath.replace('%0' + str(padding) + 'd', arkUtil.pad(frame, padding))

					dest = getArchivePath(fileToCopy, archive)
					print fileToCopy, ' > ', dest

					cOS.makeDirs(dest)
					try:
						shutil.copyfile(fileToCopy, dest)
					except Exception as err:
						print err
						failed = True

				if failed:
					print '\n\nFAILED:', readPath
				node['file'].setValue(getArchivePath(readPath, archive))
			else:
				fileToCopy = readPath
				print 'Copy:', fileToCopy
				dest = getArchivePath(readPath, archive)

				cOS.makeDirs(dest)
				try:
					shutil.copyfile(fileToCopy, dest)
				except:
					print '\n\nFAILED:', fileToCopy
				node['file'].setValue(dest)

	savePath = getArchivePath(nukeScriptFile, archive)
	cOS.makeDirs(savePath)
	nuke.scriptSaveAs(savePath)
	nuke.scriptClose()

if __name__ == '__main__':
	copyReadFiles(sys.argv[1], sys.argv[2])
