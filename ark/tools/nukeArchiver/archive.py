
import os
import json
import shutil
import sys
import traceback

sys.path.append(os.environ.get('ARK_PYTHONLIB'))


import arkInit
arkInit.init()

import cOS
import pathManager

import settingsManager
globalSettings = settingsManager.globalSettings()

import nukePython
nukePython.init()

import nuke
import arkNuke

import translators
translator = translators.getCurrent()


def stringSubstitute(baseString, values):
	for k, v in values.iteritems():
		key = '{' + k + '}'
		if key in baseString:
			baseString = baseString.replace(key, v)

	return baseString

def removeEmptyBackdrops():
	nonBackdropNodes = [n for n in nuke.allNodes() if n.Class() != 'BackdropNode']
	xPositions = [n.xpos() for n in nonBackdropNodes]
	yPositions = [n.ypos() for n in nonBackdropNodes]
	for node in nuke.allNodes('BackdropNode'):
		containsNodes = False
		left = node.xpos()
		right = left + node['bdwidth'].getValue()
		top = node.ypos()
		bottom = top + node['bdheight'].getValue()
		for x, y in zip(xPositions, yPositions):
			if x >= left and x <= right and y >= top and y <= bottom:
				containsNodes = True
				continue
		if containsNodes:
			continue
		nuke.delete(node)

def cleanUpComp():
	finalRenderNodes = nuke.allNodes('finalRender')
	# finalRenderNodes = [n for n in nuke.allNodes('Dot') if n['label'].getValue() == ' Final Output']
	# finalRenderNodes = [n for n in nuke.allNodes('Group') if 'newRender' in n.knobs()]
	if not len(finalRenderNodes):
		print 'No final render node found'
		return False

	finalRenderNode = finalRenderNodes[0]

	dependencies = arkNuke.collectDependencies(finalRenderNode)
	dependencies.append(finalRenderNode)
	keepers = [n.name() for n in dependencies]
	keepClasses = ['BackdropNode', 'Viewer']

	for node in nuke.allNodes():
		if node.name() not in keepers and node.Class() not in keepClasses:
			nuke.delete(node)

	removeEmptyBackdrops()

def replaceFinalRenderNodes():
	# finalRenderNodes = nuke.allNodes('finalRender')
	finalRenderNodes = [n for n in nuke.allNodes('Group') if 'newRender' in n.knobs()]
	for node in finalRenderNodes:
		xPos = arkNuke.getXPos(node)
		yPos = arkNuke.getYPos(node)
		read = nuke.nodes.Read()
		read['file'].setValue(node['file'].getValue())
		read['first'].setValue(nuke.root().firstFrame())
		read['last'].setValue(nuke.root().lastFrame())
		read['colorspace'].fromScript('linear')
		arkNuke.setXPos(read, xPos - 200)
		arkNuke.setYPos(read, yPos)
		read['label'].setValue(' Final Render')
		read['note_font_size'].setValue(20)
		mainInput = node.input(0)
		if node.inputs() > 1:
			metaDot = node.input(1)
			if metaDot.Class() == 'Dot':
				nuke.delete(metaDot)
		nuke.delete(node)
		dot = nuke.nodes.Dot()
		arkNuke.setXPos(dot, xPos)
		arkNuke.setYPos(dot, yPos)
		dot.setInput(0, mainInput)
		dot['label'].setValue(' Final Output')
		dot['note_font_size'].setValue(100)

def archiveShot(shotName,
	bundle,
	shotRoot,
	archiveRoot,
	shotFolderConvention,
	imageConvention,
	assetConvention):

	print '\nShot:', shotName
	for folder in os.listdir(shotRoot):
		if 'comp' != folder.lower():
			continue

		# get the latest comp
		compRoot = shotRoot + folder + '/'
		latestComp = cOS.getHighestVersionFilePath(compRoot, extension='.nk')
		pathInfo = cOS.getPathInfo(latestComp)
		compDir = pathInfo['dirname']
		relativeRoot = '[file dirname [value root.name]]/'

		if not latestComp:
			return 'No comp found'

		print 'Archiving:', latestComp

		errors = []
		try:
			# build the archive shot root
			compPathInfo = cOS.getPathInfo(latestComp)
			info = {
				'bundle': bundle,
				'shot': shotName,
			}
			archiveShotRoot = stringSubstitute(shotFolderConvention, info)
			archiveShotRoot = cOS.normalizeDir(archiveRoot + archiveShotRoot)
			cOS.makeDirs(archiveShotRoot)

			# open the file
			translator.openFile(latestComp)

			# translate paths to the current OS
			for node in translator.getAllNodes(recurse=True):
				node = node.nativeNode()
				if 'file' in node.knobs():
					filepath = node['file'].getValue()
					filepath = pathManager.translatePath(filepath)
					node['file'].setValue(filepath)

			# remove unused nodes
			cleanUpComp()

			# bake all the gizmos to groups
			arkNuke.bakeGizmos()

			# remove final render nodes, replacing them w/ read nodes
			# that point to the renders
			replaceFinalRenderNodes()

			# build the string to archive
			imageBaseString = archiveShotRoot + imageConvention
			singleImageBaseString = imageBaseString.replace('{padding}.','')

			# archive images
			imageNodes = ['deepread', 'read', 'write']
			for nodeType in imageNodes:
				nodes = translator.getNodesByType(nodeType, recurse=True)
				for node in nodes:
					source = node.getProperty('file')
					# replace relative roots with the real comp dir
					source = source.replace(relativeRoot, compDir)
					# non-environment path
					source = translator.nonEnvironmentPath(source)
					# deep reads don't have colorspace
					# so "default" to linear
					try:
						colorspace = node.getProperty('colorspace')
						if colorspace == 'default':
							if 'srgb' in source.lower():
								colorspace = 'sRGB'
							else:
								colorspace = 'linear'
					except Exception as err:
						print 'Error getting colorspace:', err
						colorspace = 'linear'

					info = {
						'shot': shotName,
						'bundle': bundle,
						'resolution': '%dx%d' % (int(node.width()), int(node.height())),
						'colorspace': colorspace,
					}
					frameRangeInfo = cOS.getFrameRange(source)

					# handle image sequences
					if frameRangeInfo:
						firstFrame = frameRangeInfo['path'] % frameRangeInfo['min']
						pathInfo = cOS.getPathInfo(firstFrame)
						basename = frameRangeInfo['baseUnpadded'].replace(pathInfo['dirname'], '')

						# ending in . or _ results in an undesireable basename
						if basename.endswith('.') or basename.endswith('_'):
							basename = basename[:-1]

						# add more info for stringSubstitute
						info.update({
							'extension': pathInfo['extension'],
							'basename': basename,
							'padding': frameRangeInfo['paddingString'],
						})
						destination = stringSubstitute(imageBaseString, info)
						source = frameRangeInfo['paddedPath']
						print source, '  >  ', destination
						cOS.makeDirs(destination)
						cOS.copyFileSequence(source, destination, frameRangeInfo, echo=True)

						archivePath = destination.replace(archiveShotRoot, relativeRoot)
						node.setProperty('file', archivePath)

					# if it's not a sequence maybe it's a single image?
					else:
						if '%' in source or '#' in source or '$F' in source:
							errors.append('Could not get frame range for: ' + source)
							continue

						pathInfo = cOS.getPathInfo(source)
						basename = pathInfo['filebase'].replace(pathInfo['dirname'], '')

						# add more info for stringSubstitute
						info.update({
							'extension': pathInfo['extension'],
							'basename': basename,
						})
						destination = stringSubstitute(singleImageBaseString, info)
						print source, '  >  ', destination
						cOS.makeDirs(destination)
						try:
							shutil.copyfile(source, destination)
						except Exception as err:
							print 'Error copying:', err

						archivePath = destination.replace(archiveShotRoot, relativeRoot)

						node.setProperty('file', archivePath)


			# archive 3d nodes
			assetBaseString = archiveShotRoot + assetConvention
			assetNodes = ['camera', 'readgeo']
			for nodeType in assetNodes:
				nodes = translator.getNodesByType(nodeType, recurse=True)
				for node in nodes:
					if not node.hasProperty('file`'):
						continue

					source = node.getProperty('file')

					pathInfo = cOS.getPathInfo(source)
					basename = pathInfo['filebase'].replace(pathInfo['dirname'], '')

					# add more info for stringSubstitute
					info = {
						'shot': shotName,
						'bundle': bundle,
						'extension': pathInfo['extension'],
						'basename': basename,
					}
					destination = stringSubstitute(assetBaseString, info)
					print source, '  >  ', destination
					cOS.makeDirs(destination)
					try:
						shutil.copyfile(source, destination)
					except Exception as err:
						print 'Error copying:', err

					archivePath = destination.replace(archiveShotRoot, relativeRoot)
					node.setProperty('file', archivePath)

			# save the script
			archiveCompPath = archiveShotRoot + compPathInfo['basename']
			print 'comp saved:', archiveCompPath + '\n'
			translator.saveFile(archiveCompPath, force=True)

		except Exception as err:
			print err
			print traceback.format_exc()

			print err
			sys.exit()

	if len(errors):
		return '\n'.join(errors)
	else:
		return 'Success!'

def main():
	settingsPath = globalSettings.TEMP + 'archiverData.json'
	with open(settingsPath) as settingsFile:
		settings = json.load(settingsFile)

	print settings
	results = archiveShot(shotName=settings['shot'],
		bundle=settings['bundle'],
		shotRoot=settings['shotRoot'],
		archiveRoot=settings['archiveRoot'],
		shotFolderConvention=settings['shotFolderConvention'],
		imageConvention=settings['imageConvention'],
		assetConvention=settings['assetConvention'])

	settingsPath = globalSettings.TEMP + 'archiverResults.json'
	with open(settingsPath, 'w') as output:
		settings = json.dump(results, output)


if __name__ == '__main__':
	main()

# R:/Geostorm/Workspaces/Movie/LTC_0184_0210/comp/ltc_0184_0210_comp_v2023_djc.nk
