# python

# Grant Miller
# blented@gmail.com
# www.ievfx.com

import os
import sys
import shutil
import re
import ast

'''
Proper Usage:
python archiveScript.py <list of workspaces> <archive directory> <replace list>

ex:
python archiveScript.py "['Q:/Qoros/Workspaces/0050/comp', 'Q:/Qoros/Workspaces/0060/comp']" "E:/archive/Qoros" "['Q:/Qoros','F:/Qoros']"
'''


failList = []

def getVersion(filename):
	match = re.findall('[vV]([0-9]+)', filename)
	if (match):
		return int(match[-1])
	return 0

def normalizePath(path):
	return re.sub(r'[\\/]+', '/', path)

def normalizeDir(path):
	path = normalizePath(path)
	if path[-1] != '/':
		path = path + '/'
	return path

def makeDirs(path):
	dirName = os.path.dirname(path)
	try:
		os.makedirs(dirName)
	except Exception as err:
		return err

def getArchivePath(path, archiveRoot):
	ogRoot = path.split('/')[0] + '/'
	return path.replace(ogRoot, archiveRoot)

def archiveFile(filePath, archiveRoot):
	global failList
	# remove quotes
	filePath = filePath.replace('"','')
	dest = getArchivePath(filePath, archiveRoot)
	makeDirs(dest)
	try:
		shutil.copyfile(filePath, dest)
	except Exception as err:
		print 'FAILED:', filePath
		failList.append(filePath)
		print err

def archiveFrames(filePath, firstFrame, lastFrame, archiveRoot):
	if '#' in filePath:
		initPos = i = filePath.index('#')
		while filePath[i] == '#':
			i += 1
		padding = i - initPos
		filePath = filePath.replace('#' * padding, '%0' + str(padding) + 'd')

	if '%' not in filePath:
		print 'FAILED: No frame padding in:', filePath
		return
	for frame in xrange(int(firstFrame), int(lastFrame) + 1):
		archiveFile(filePath % frame, archiveRoot)

def archiveScript(source, archiveRoot):
	fileNodes = ['DeepRead', 'Read', 'Camera2', 'ReadGeo2','Write']

	beginNodeRegex = re.compile('^([A-Za-z]+) \{$')
	endNodeRegex = re.compile('^}$')
	fileRegex = re.compile('file (.+)')
	firstRegex = re.compile('first ([0-9]+)$')
	lastRegex = re.compile('last ([0-9]+)$')
	rootRegex = re.compile('Root {$')
	compFirstFrameRegex = re.compile('first_frame ([0-9]+)$')
	compLastFrameRegex = re.compile('last_frame ([0-9]+)$')

	dest = source.replace('.nk','.archive.nk')
	dest = getArchivePath(dest, archiveRoot)

	makeDirs(dest)
	shutil.copyfile(source, dest)
	with open(source) as script:
		with open(dest, 'w') as archiveScript:
			inFileNode = False
			inRoot = False
			filePath = None
			firstFrame = 1
			lastFrame = None
			nodeType = None
			compFirstFrame = 1
			compLastFrame = None

			for line in script:
				# substitute paths in the line
				it = iter(replaceList)
				for k,v in zip(it, it):
					line = line.replace(k, v)

				# figure out if we're in a read node
				rootNodeMatch = re.search(rootRegex, line)
				beginNodeMatch = re.search(beginNodeRegex, line)
				if rootNodeMatch:
					inRoot = True
				elif beginNodeMatch:
					inRoot = False
					nodeType = beginNodeMatch.groups()[0]
					inFileNode = nodeType in fileNodes
					filePath = None
					firstFrame = 1
					lastFrame = None

				# if we're in the root node store the first and last frames
				if inRoot:
					compFirstFrameMatch = re.search(compFirstFrameRegex, line)
					compLastFrameMatch = re.search(compLastFrameRegex, line)
					if compFirstFrameMatch:
						compFirstFrame = int(compFirstFrameMatch.groups()[0])
					if compLastFrameMatch:
						compLastFrame = int(compLastFrameMatch.groups()[0])
				# if we're in a read node try to get some info
				elif inFileNode:
					fileMatch = re.search(fileRegex, line)
					firstMatch = re.search(firstRegex, line)
					lastMatch = re.search(lastRegex, line)
					if fileMatch:
						filePath = fileMatch.groups()[0]
						line.replace(filePath, getArchivePath(filePath, archiveRoot))
					if firstMatch:
						firstFrame = int(firstMatch.groups()[0])
					if lastMatch:
						lastFrame = int(lastMatch.groups()[0])

				# if we come to the end of the node and we've been in a file node
				# then check if we have enough info and try to archive it
				if re.search(endNodeRegex, line) and inFileNode and filePath:
					# write nodes don't specify a frame range so we use the comp's
					if nodeType == 'Write':
						firstFrame = compFirstFrame
						lastFrame = compLastFrame

					if lastFrame is not None and '#' in filePath or '%' in filePath:
						print '\n%d-%d  %s' % (firstFrame, lastFrame, filePath)
						archiveFrames(filePath, firstFrame, lastFrame, archiveRoot)
					else:
						print '\n', filePath
						archiveFile(filePath, archiveRoot)

				archiveScript.write(line)

def archiveScripts(compFolders, archiveRoot, replaceList=None):
	global failList

	# normalize the archive root and ensure it exists
	archiveRoot = normalizeDir(archiveRoot)
	makeDirs(archiveRoot)

	for folder in compFolders:
		# loop through the comp folders to get the latest comps (by version number)
		folder = normalizeDir(folder)
		filesInFolder = [f for f in os.listdir(folder) if '~' not in f]

		# store the version numbers along with their list index
		versionNumbers = [(getVersion(f), i) for i, f in enumerate(filesInFolder)]
		if not len(versionNumbers):
			continue

		# get the file matching the highest version number
		latestFile = folder + filesInFolder[max(versionNumbers)[1]]

		print '\n\nArchiving: ', latestFile
		print '=' * 50, '\n'
		archiveScript(latestFile, archiveRoot)

	print '\n\nFailed Files:'
	for f in failList:
		print f

if __name__ == '__main__':
	compFolders = sys.argv[1]
	arc = sys.argv[2]
	replaceList = sys.argv[3]
	compFolders = ast.literal_eval(compFolders)
	replaceList = ast.literal_eval(replaceList)

	archiveScripts(compFolders, arc, replaceList)
