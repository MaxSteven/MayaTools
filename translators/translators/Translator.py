import os
import sys
# import time
import re

from qt import QtGui
from qt import QtCore

import Events
import Node_Base

import arkInit
arkInit.init()

# import arkMath
import arkUtil
import pathManager
import cOS
import SerialNode_Base
import TranslatorIO

import settingsManager
globalSettings = settingsManager.globalSettings()

class Translator(object):

	nodeClass = Node_Base.Node_Base
	serialNodeClass = SerialNode_Base.SerialNode_Base
	fileExtension = 'none'
	program = 'translator'
	environmentFormatString = '%s'

	def __init__(self):
		self.eventListener = Events.Events()
		self.options = {}
		self.setOptions(
			canUse=False,
			hasFrames=False,
			hasPasses=False,
			canPreview=False,
			canPublishShots=True,
			hasCameras = False,
			hasKeyCommands=False,
			vRayRenderPresets=None,
			hasDeep=False,
			defaultCameras=[],
			closeOnSubmit=True,
			jobTypes=['Render'],
			alembicImportOptions = [],
			displayOptions=[],
			appHandlesSubmit=False,
			hasChunks=False,
			defaultChunkSize=1,
			hasSubdivision=False,
			hasSceneAssembly=False,
			renderNode=None)

	# Basics
	##################################################
	def setOption(self, key, val):
		'''
		Set the options for the current translator
		'''
		self.options[key] = val

	def setOptions(self, **kwargs):
		'''
		Set the options for the current translator
		'''
		for k,v in kwargs.iteritems():
			self.options[k] = v
		# self.options.set(**kwargs)

	def getOption(self, key):
		if not key in self.options:
			return None
		return self.options.get(key)

	def getOptions(self):
		return self.options

	def getProgram(self):
		'''
		Get the current application
		'''
		return self.program

	def getSafeObjectName(self, name):
		return arkUtil.safeFilename(name)

	def executeNativeCommand(self, command):
		eval(command, locals={'self': self})

	def getSoftwareVersion(self):
		return ''

	# Data Storage
	##################################################
	def getSceneData(self, key=None):
		if not hasattr(self, 'sceneData'):
			self.sceneData = {}

		if key:
			return self.sceneData.get(key)
		else:
			return self.sceneData

	def setSceneData(self, key, val):
		if not hasattr(self, 'sceneData'):
			self.sceneData = {}
		self.sceneData[key] = val

	def removeSceneData(self, key):
		data = self.getSceneData()
		if key in data:
			del data[key]
		self.setSceneData(data)

	def getFileHash(self):
		return {}

	# Files
	##################################################
	def getFilename(self):
		'''
		Get the current open filename
		'''
		return ''

	def setFilename(self, filename):
		return True

	def saveFile(self, filename=None, force=False):
		'''
		Save the current open file, optionally specifying
		a name to save the file as
		'''
		return True

	def openFile(self, filename, force=False):
		'''
		Open the specified filename
		'''
		return True

	def newFile(self, force=False):
		'''
		Get the current open filename
		'''
		return None

	def closeFile(self, force=False):
		'''
		Close the current open filename
		'''
		self.newFile(force=force)

	def exit(self, force=False):
		'''
		Exit the program
		'''
		return None

	def getEnvironmentPath(self, path):
		# print 'Maya path:', pathManager.getEnvironmentPath('${%s}', path)
		# print 'Houdini path:', pathManager.getEnvironmentPath('$%s', path)
		# print 'Nuke path:', pathManager.getEnvironmentPath('[getenv %s]', path)
		return pathManager.getEnvironmentPath(self.environmentFormatString, path)

	def nonEnvironmentPath(self, path):
		# print 'Maya path:', pathManager.nonEnvironmentPath('${%s}', path)
		# print 'Houdini path:', pathManager.nonEnvironmentPath('$%s', path)
		# print 'Nuke path:', pathManager.nonEnvironmentPath('[getenv %s]', path)
		return pathManager.nonEnvironmentPath(self.environmentFormatString, path)

	def checkSaveState(self, useHash=True):
		return True

	def replaceFilePaths(self):
		return True

	# Nodes
	##################################################
	def getAllNodes(self, recurse=False):
		return []

	def getChildNodes(self, parentNode):
		return []

	def getNodeByName(self, name):
		return []

	def getAvailableNodeName(self, name):
		while self.getNodeByName(name):
			nameRegex = re.compile('[0-9]+$')
			try:
				suffixPadding = len(nameRegex.findall(name)[0])
				suffix = int(nameRegex.findall(name)[0]) + 1
				name = nameRegex.sub(str(suffix).zfill(suffixPadding), name)
			except:
				name = name + '1'

		return name

	def getNodesByNames(self, names):
		nodes = []
		for name in names:
			node = self.getNodeByName(name)
			if node:
				nodes.append(node)
		return nodes

	def getNodesByType(self, nodeType, recurse=False):
		# default implementation is slow but
		# should always work
		# indivial apps may have better tools
		allNodes = self.getAllNodes()
		validNodes = [n for n in allNodes if n.getType().lower() == nodeType.lower()]
		return self.ensureNodes(validNodes)

	# Really only applicable to Houdini
	# If called by accident for a different program, just use type
	def getNodesByCategory(self, nodeCategory):
		return self.getNodesByType(nodeCategory)

	def getNodesByProperty(self, prop, value=None):
		allNodes = self.getAllNodes()
		validNodes = []
		for node in allNodes:
			if not node.hasProperty(prop):
				continue
			if value is None or node.getProperty(prop) == value:
				validNodes.append(node)

		return validNodes

	# Based on path (Houdini) or hierarchy. Paths should be unique
	# Defaults to getNodeByName()
	def getNodeByPath(self, path):
		return self.getNodeByName(path)

	def selectNode(self, node):
		return True

	def selectNodes(self, nodes):
		return True

	def deselectNodes(self, nodes):
		return True

	def selectNodesByNames(self, names):
		nodes = self.getNodesByNames(names)
		self.selectNodes(nodes)

	def getSelectedNodes(self, recurse=False):
		return []

	def getSelectedNode(self):
		'''
		Return the first selected node or error
		'''
		selectedNodes = self.getSelectedNodes()
		if len(selectedNodes) > 0:
			return selectedNodes[0]
		raise Exception('No node selected')

	def clearSelection(self):
		allNodes = self.getAllNodes()
		self.deselectNodes(allNodes)

	def removeNodes(self, nodes, ignoreErrors=True):
		return True

	def createInstance(self, node):
		return True

	def createPrimitive(self, primitiveType):
		return None

	def applyNodePreset(self, node, preset):
		raise Exception('Not implemented')

	# Rendering
	##################################################
	def getRenderNode(self):
		renderNode = self.getOption('renderNode')
		if renderNode is None:
			# print 'Translator: render node not set'
			return None
		return renderNode

	def setRenderNode(self, node):
		node = self.ensureNode(node)
		self.setOptions(renderNode=node)
		return node

	def getRenderProperties(self):
		frameRange = self.getRenderRange()
		animationRange = self.getAnimationRange()

		# If program has render node
		if self.getRenderNode():
			return {
				'program': self.getProgram(),
				'node': self.getRenderNode().name(),
				'startFrame': frameRange['startFrame'],
				'endFrame': frameRange['endFrame'],
				'fps': self.getFPS(),
				'width': self.getRenderProperty('width'),
				'height': self.getRenderProperty('height'),
				'nearPlane': self.getRenderProperty('nearPlane'),
				'farPlane': self.getRenderProperty('farPlane'),
			}
		# If no renderNode, can't do much
		else:
			return {
				'program': self.getProgram(),
				'node': None,
				'startFrame': animationRange['startFrame'],
				'endFrame': animationRange['endFrame'],
				'fps': self.getFPS(),
				# hard coded, will never actually render without a renderNode
				'width': self.getRenderProperty('width') or 1920,
				'height': self.getRenderProperty('height') or 1080,
				'nearPlane': 0.1,
				'farPlane': 10000,
			}

	def getRenderProperty(self, prop):
		'''
		Get a variety of render properties:
		- width: render width
		- height: render height
		'''
		return None

	def setRenderProperty(self, prop, val):
		return True

	def getOutputFilename(self, path=None, jobData=None):
		return None

	def setOutputFilename(self, filename, jobData=None):
		return True

	def getRenderRange(self):
		# expected to be integers
		return {
			'startFrame': int(1001),
			'endFrame': int(1100),
		}

	def setRenderRange(self, start, end):
		return None

	def preSubmit(self, jobData):
		if self.checkSaveState():
			self.saveFile(force=True)
		return jobData

	def postSubmit(self, jobData):
		return True

	def setRenderable(self, nodes, value=True):
		return True

	def createPlayblast(self, playblastOptions):
		'''
		playblastOptions expects:
			inPath
			outputPath
			fps
			startTime
			endTime
			sound
			audioFile
			copyToDir 		dailies folder
			text 			burn in
		'''
		# convert png image sequence into h264
		pathInfo = cOS.getPathInfo(playblastOptions['outputPath'])
		cOS.makeDirs(pathInfo['dirname'])

		fps = 24

		if playblastOptions['fps']:
			print 'hit this for fps'
			fps = playblastOptions['fps']

		ffmpegCommand = [
			globalSettings.FFMPEG_EXE,
			'-r', '%s' % str(fps),
			'-start_number', '%s' % playblastOptions['startTime'],
			'-i', playblastOptions['inPath'],
		]

		if playblastOptions['sound'] and playblastOptions['audioFile']:
			ffmpegCommand.extend([
				'-ss', str(playblastOptions['startTime'] / fps),
				'-t', str((playblastOptions['endTime'] - playblastOptions['startTime']) / fps),
				'-i', playblastOptions['audioFile'],
				'-c:a aac',
			])

		if playblastOptions.get('text'):
			ffmpegCommand.append("-vf \"{}\"".format(playblastOptions['text']))

		ffmpegCommand.extend([
			'-y',
			'-c:v libx264',
			'-preset slower',
			'-profile:v high',

			# https://apple.stackexchange.com/questions/166553/why-wont-video-from-ffmpeg-show-in-quicktime-imovie-or-quick-preview
			'-pix_fmt yuv420p',
			'-g', '1',
			'-keyint_min', '1',
			'-bf', '16',
			'-b_strategy', '2',
			'-coder', '1',
			'-refs', '6',
			'-flags', '+loop',
			'-crf 20',
			'-b:v 15M',
			'-threads 0',
			'-maxrate 30M',
			'-bufsize 60M',
			'-qdiff', '4',
			'%s' % playblastOptions['outputPath'],
		])

		ffmpegCommand = ' '.join(ffmpegCommand)
		print ffmpegCommand

		# startSubprocess doesn't work because Maya doesn't recognize psutil
		out, err = cOS.getCommandOutput(ffmpegCommand)
		if not out:
			print 'ffmpegCommand Errored:', err
			return False

		# directory of playblast
		playblastDir = playblastOptions['inPath'].rpartition('/')[0]

		# copy png from temp folder to playblast location
		cOS.makeDirs(cOS.ensureEndingSlash(playblastOptions['outputPath'].rpartition('.')[0]))
		cOS.copyTree(playblastDir, playblastOptions['outputPath'].rpartition('.')[0])
		cOS.removeDir(playblastDir)
		path = cOS.normalizeDir(playblastOptions['outputPath'])
		playblastFile = path.split('/')[-2]

		# copy to dailies folder
		if playblastOptions.get('copyToDir'):
			cOS.makeDirs(playblastOptions['copyToDir'])
			playblastPath = cOS.normalizeAndJoin(
				playblastOptions['copyToDir'],
				playblastOptions.get('copyToFile', playblastFile)
			)
			cOS.copy(playblastOptions['outputPath'], playblastPath)
			return playblastPath

		else:
			return None

	def addRenderElement(self, elementName):
		return None

	def removeRenderElement(self, elementName):
		return None

	def createShadingNode(self, nodeName):
		return True

	def connectProperty(self, fromNode, fromNodeProperty, toNode, toNodeProperty):
		return True

	# Cannot go to cOS as it heavily relies on pathManager
	def localizeFiles(self, path, localizeRoot):
		path = self.nonEnvironmentPath(path)
		assetPath = pathManager.translatePath(path)
		newPath = None
		if cOS.isValidSequence(path):
			pathInfo = cOS.getPathInfo(assetPath)
			extension = pathInfo['extension']
			seqDir = pathInfo['dirname']
			seqName = '.'.join(pathInfo['name'].split('.')[:-1])
			files = cOS.getFiles(seqDir, fileIncludes = [seqName + '*.' + extension], depth=0, filesOnly=True)
			pathRoot = cOS.getPathInfo(pathManager.translatePath(seqDir))['root']
			if pathRoot.lower() in pathManager.getAllDriveRoots():
				cOS.makeDirs(localizeRoot + cOS.removeStartingSlash(pathManager.translatePath(seqDir, osName='linux')))
				for f in files:
					newPath = localizeRoot + cOS.removeStartingSlash(pathManager.translatePath(f, osName='linux'))
					print 'copying source:	' + f + ' ==> destination:	' + newPath
					if not os.path.isfile(newPath):
						try:
							cOS.copy(f, newPath)

						except Exception as err:
							print 'Couldn\'t copy over path:' + f
							print 'Error: ', err
							return f
		else:
			pathRoot = cOS.getPathInfo(pathManager.translatePath(path))['root']
			if pathRoot.lower() in pathManager.getAllDriveRoots():
				newPath = cOS.removeStartingSlash(pathManager.translatePath(path, osName='linux'))
				newPath = localizeRoot + newPath
				cOS.makeDirs(newPath)
				print 'copying source:	' + assetPath + ' ==> destination:	' + newPath
				if not os.path.isfile(newPath):
					try:
						cOS.copy(assetPath, newPath)

					except Exception as err:
						print 'Couldn\'t copy over path:' + assetPath
						print 'Error: ', err
						return assetPath

		return newPath

	# Animation
	##################################################
	def getFPS(self):
		return None

	def setFPS(self, fps):
		return True

	def getAnimationRange(self):
		# expected to be integers
		return {
			'startFrame': int(1001),
			'endFrame': int(1100),
		}

	def setAnimationRange(self, start, end):
		return True

	def getAnimationFrame(self):
		return None

	def setAnimationFrame(self, frame):
		return True

	def loadAnimation(self, nodes, animation):
		return True

	def removeAnimation(self, nodes, frame):
		return True

	def setCamView(self, camName):
		return True

	def getCamview(self):
		return True

	def localizeNodes(self, nodes=None):
		localizeRoot = os.environ.get('ARK_CACHE')
		if not localizeRoot:
			return False
		return True

	def delocalizeNodes(self, nodes=None):
		localizeRoot = os.environ.get('ARK_CACHE')
		if not localizeRoot:
			return False
		return True

	def relocalizeNodes(self, nodes=None):
		localizeRoot = os.environ.get('ARK_CACHE')
		if not localizeRoot:
			return False
		return True

	# Visibility
	##################################################
	def isolateNodes(self, nodes):
		return True

	def unisolateNodes(self, nodes):
		return True

	def showNodes(self, nodes):
		return True

	def hideNodes(self, nodes):
		return True

	def getHiddenNodes(self):
		return []

	def getVisibleNodes(self):
		return []

	# Locks
	##################################################
	def setNodeTransformLock( self, objectName=None, useSelected=False, value=True):
		pass

	def setNodeSelectionLock( self, objectName=None, useSelected=False, value=True):
		pass

	# IO
	##################################################
	def processAlembic(self, filepath, frameRange, fps=24):
		return TranslatorIO.processAlembic(filepath, frameRange, fps)

	def importAlembicGeometry(self, filename, method=None):
		print 'filename: ' + filename
		return True

	def importAlembicCamera(self, filename, method=None):
		print 'filename: ' + filename
		return True

	def importFBXGeometry(self, filename):
		return True

	def importFBXCamera(self, filename):
		return True

	def importOBJGeometry(self, filename):
		return True

	def importImage(self, filename, method=None, importOptions = None):
		print 'filename:', filename
		print 'method:', method
		print 'importOptions:', importOptions
		return True

	def importImageSequence(self, filename, method=None, importOptions = None):
		normalized = cOS.getFirstFileFromFrameRangeText(filename)

		print 'filename:', normalized
		print 'method:', method
		print 'importOptions:', importOptions
		return True

	def createRenderProxy(self,
						filepath,
						renderOptions = {'scale': 1.0,
										'particleWidthMultiplier': 1.0,
										'hairWidthMultiplier': 1.0,
										'previewFaces': 5000,
										'geoToLoad': 2},
						renderEngine = 'Vray'):
		print 'filepath:', filepath
		print 'renderOptions:',renderOptions
		print 'renderEngine', renderEngine
		return True


	def createMaterialFromImages(self, texFile, matName = ''):
		for f in texFile:
			fPathInfo = cOS.getPathInfo(f)
			if fPathInfo['name'].split('.')[1] == 'ao_rough_metal_ior':
				metalFile = f
			elif fPathInfo['name'].split('.')[1] == 'diffuse':
				diffuseFile = f
			elif fPathInfo['name'].split('.')[1] == 'normal_height':
				normalFile = f

		if not matName:
			matName = cOS.getPathInfo(texFile[0])['name'].split('.')[0]

		print matName
		print metalFile
		print diffuseFile
		print normalFile
		matDict = {
				'material': matName,
				'displacement': str(matName) + '\n' + str(normalFile)
				}
		return matDict


	def createDisplacementFromMap(self, normalNode, matName = ''):
		print 'normalNode: ' + normalNode
		print 'matName: ' + matName
		return True

	def exportAlembic(self, filepath, frameRange, camera=None, exportOptions=None):
		print 'filepath: ', filepath
		print 'frameRange: ', frameRange
		print 'camera: ', camera
		print 'exportOptions: ', exportOptions
		return True

	# Materials
	##################################################
	def getMaterialByName(self, materialName):
		print 'materialName: ' + materialName
		pass

	def setMaterialByName(self, nodes, materialName):
		nodes = self.ensureNodes(nodes)
		material = self.getMaterialByName(materialName)
		for node in nodes:
			node.setMaterial(material)

	def convertToTiledEXR(self, textureFiles, convertOptions = {'32bit': False, 'compression': 'pxr24', 'convertToLinear': False}):
		for filename in textureFiles:
			parts = filename.split('.')
			newFilename = '.'.join(parts[:-3]) + '_tiled.' + parts[-3] + '.' + parts[-2] + '.exr'

			if convertOptions['32bit']:
				bit = '-32Bit'
			else:
				bit = ''

			if convertOptions['convertToLinear']:
				convertToLinear = 'on'
			else:
				convertToLinear = 'off'

			command = r'"C:/Program Files/Chaos Group/V-Ray/Maya 2018 for x64/bin/img2tiledexr.exe" {0} {1} {2} -compression {3} -linear {4}'.format(
				filename, newFilename, bit, convertOptions['compression'], convertToLinear)
			print command
			os.system(command)

		return True

	def addCommand2(self, toolbar, tool):
		if tool.get('software') is not None and 'standalone' in tool.get('software'):
			toolbar.currentTools[tool.get('name').lower()] = tool

	# Serialization
	########################################
	def getSerialNode(self, node):
		return self.serialNodeClass(self, nativeNode=node)

	def getSerialNodeFromFile(self, filepath):
		print filepath
		return self.serialNodeClass(self, filepath=filepath)

	# UI
	########################################

	def getPanel(self, panelName):
		pass

	# PySide
	########################################
	def getQTApp(self):
		app = QtGui.QApplication.instance()
		if not app:
			print 'creating app instance'
			app = QtGui.QApplication(sys.argv)
		return app

	def launch(
		self,
		Dialog,
		qApplication=None,
		parent=None,
		newWindow=None,
		docked = True,
		*args,
		**kwargs):
		print 'launching:', Dialog
		if parent is not None:
			newWindow = True

		if not qApplication:
			qApplication = self.getQTApp()

		# window flags
		def setWindowFlags(dialog):
			flags = QtCore.Qt.Dialog
			if dialog.options.get('alwaysOnTop'):
				flags |= QtCore.Qt.WindowStaysOnTopHint
			if dialog.options.get('borderless'):
				flags |= QtCore.Qt.FramelessWindowHint
			if newWindow:
				flags |= QtCore.Qt.Window

			dialog.setWindowFlags(flags)

		if parent:
			dialog = Dialog(parent, *args, **kwargs)
			setWindowFlags(dialog)
			dialog.show()
		elif hasattr(qApplication, '_mainApp'):
			dialog = Dialog(qApplication._mainApp, *args, **kwargs)
			setWindowFlags(dialog)
			dialog.show()
		elif qApplication and qApplication.activeWindow() is not None:
			dialog = Dialog(qApplication.activeWindow(), *args, **kwargs)
			setWindowFlags(dialog)
			dialog.show()
		else:
			dialog = Dialog(None, *args, **kwargs)
			setWindowFlags(dialog)
			dialog.show()
			qApplication._mainApp = dialog
			sys.exit(qApplication.exec_())

		return dialog

	def messageBox(
			self,
			text,
			title='Message',
			icon=None,
			buttons=None,
			defaultButton=None,
			parent=None,
			staysOnTop=True,
			modal=False,
			deleteOnClose=True,
			offset=False,
			callback = None):
		# default values
		parent = parent or self.getQTApp()
		flags = QtCore.Qt.Dialog | QtCore.Qt.MSWindowsFixedSizeDialogHint
		if staysOnTop:
			flags = flags | QtCore.Qt.WindowStaysOnTopHint

		icon = icon or QtGui.QMessageBox.NoIcon
		buttons = buttons or QtGui.QMessageBox.NoButton

		dialog = QtGui.QMessageBox(
			icon,
			title,
			text,
			buttons=buttons,
			parent=parent,
			flags=flags)


		if deleteOnClose:
			dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
		if defaultButton:
			dialog.setDefaultButton(defaultButton)

		if offset:
			# move to not-quite-center so it doesn't cover up default dialogs
			fg = dialog.frameGeometry()
			cp = QtGui.QDesktopWidget().availableGeometry().center()
			fg.moveCenter(cp)
			dialog.move(fg.topLeft() + QtCore.QPoint(0,100))

		if callback:
			dialog.buttonClicked.connect(callback)

		if modal:
			dialog.exec_()

		else:
			dialog.setWindowModality(QtCore.Qt.NonModal)
			dialog.show()
			dialog.raise_()

	# Events (typically no need to modify)
	##################################################
	def emit(self, eventName, *args, **kwargs):
		'''
		Emit an event with other applications using this
		translator can listen to
		'''
		self.eventListener.emit(
			eventName,
			*args,
			**kwargs)

	def on(self, eventName, callback, **kwargs):
		'''
		Listen to an event, calling the specified callback
		when the event is emitted
		'''
		self.eventListener.on(
			eventName,
			callback,
			**kwargs)

	def once(self, eventName, callback, **kwargs):
		'''
		Listen to an event, calling the specified callback
		when the event is emitted
		'''
		self.eventListener.once(
			eventName,
			callback,
			**kwargs)

	def off(self, eventName=None, callback=None):
		'''
		Remove a callback from a certain event,
		or remove all callbacks if a specific callback
		is not supplied
		'''
		self.eventListener.off(
			eventName,
			callback)

	# Helpers (typically no need to modify)
	########################################
	def ensureNode(self, node):
		if not node:
			return None
		if isinstance(node, self.nodeClass):
			return node
		wrapped = self.nodeClass(node, self)
		return wrapped

	def ensureNodes(self, nodes):
		nodes = arkUtil.ensureArray(nodes)
		return [self.ensureNode(node) for node in nodes]

	# Converts list of nodes to list of node names
	def nodeToNameList(self, nodes):
		return [n.name() for n in nodes]

	# Converts list of nodes to list of node types
	def nodeToTypeList(self, nodes):
		return [n.getType() for n in nodes]

	# Compares two lists and gets list of new nodes after an operation
	# pre - stored list of nodes before operation
	# post - list of nodes after operation
	# returns diff - list of differences
	def newNodes(self, pre, post):
		preNames = self.nodeToNameList(pre)
		# postNames = self.nodeToNameList(post)
		diff = []
		# return list(set(postNames) - set(preNames))
		for node in post:
			if node.name() not in preNames:
				diff.append(self.ensureNode(node))
		return diff

def main():
	translator = Translator()
	# print translator.getEnvironmentPath('r:/some/path/alembic.abc')
	print translator.getAllRoots()
	print translator.getAllRoots(osName='linux')
	# translators.createPlayblast(playblastOptions)

	# translator.localizeFiles('/ramburglar/Test_Project/Workspaces/houdini_alembic/cache/pieces/v002/pieces.%04d.abc', '/home/ie/linux_cache/')
	# translator.localizeFiles('/ramburglar/Aeroplane/Project_Assets/crash/fx/geo/center_secondary_debris_v0045/center_secondary_debris_v0045.$F.bgeo.sc', '/home/ie/linux_cache/')
	# print translator.getEnvironmentPath('q:/some/path/alembic.abc')
	# print translator.getEnvironmentPath('f:/some/path/alembic.abc')

	# print translator.nonEnvironmentPath('[getenv footage]/some/path/alembic.abc')
	# print translator.nonEnvironmentPath('${footage}/some/path/alembic.abc')
	# print translator.nonEnvironmentPath('$footage/some/path/alembic.abc')

if __name__ == '__main__':
	main()
