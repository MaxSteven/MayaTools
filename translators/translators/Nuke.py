
# Standard modules
# import os
import nuke
import os
# import glob
import json

# from datetime import date

# Our modules
import Translator
from qt import QtGui
from qt import QtCore

import arkInit
arkInit.init()

import Node_Nuke
import cOS
import pathManager
import arkUtil
import settingsManager
globalSettings = settingsManager.globalSettings()


class Nuke(Translator.Translator):

	nodeClass = Node_Nuke.Node_Nuke
	fileExtension = 'nk'
	program = 'nuke'
	environmentFormatString = '[getenv %s]'

	def __init__(self):
		super(Nuke, self).__init__()
		self.setOptions(
			canUse=True,
			canPublishShots=False,
			hasCameras=True,
			hasFrames=True,
			hasPasses=False,
			canPreview=False,
			exportTypes=['Geometry', 'Camera', 'Image Sequence'],
			vRayRenderPresets=None,
			jobTypes=['Nuke_Comp'],
			imageImportMethods=['read node','camera projection'],
			fileNodeTypesList = ['read', 'write', 'deepread', 'camera', 'readgeo'],
			hasChunks=True,
			defaultChunkSize=5,
			hasKeyCommands=True,
			closeOnSubmit=True)

	# Basics
	##################################################

	# Data Storage
	##################################################
	def getSceneData(self, key=None):
		rawData = nuke.root()['label'].getValue()
		data = arkUtil.parseJSON(rawData, ignoreErrors=True)
		# if we failed just make an empty dictionary
		if type(data) != dict:
			data = {}

		# fix: remove in 6 months
		# temp hax for slate offset from old style
		if 'hasSlateOffset' not in data:
			data['hasSlateOffset'] = 'slate offset' in rawData

		if key:
			return data.get(key)
		else:
			return data

	def setSceneData(self, key, val=None):
		data = self.getSceneData()
		if val is None:
			if isinstance(key, dict):
				data = key
			else:
				data[key] = key
		else:
			data[key] = val

		nuke.root()['label'].setValue(json.dumps(data))

	# Files
	##################################################
	def getFilename(self):
		'''
		Get the current open filename
		'''
		path = cOS.unixPath(nuke.root()['name'].getValue())
		if path:
			return pathManager.translatePath(path)
		return

	# sets filename without saving
	def setFilename(self, filename):
		nuke.root()['name'].setValue(filename)

	def saveFile(self, filename=None, force=False):
		'''
		Save the current open file, optionally specifying
		a name to save the file as
		'''
		if not filename:
			filename = self.getFilename()
		nuke.scriptSaveAs(filename, force)

	def openFile(self, filename, force=False):
		'''
		Open the specified filename
		'''
		# fix: not using force correctly
		nuke.scriptOpen(filename)

	def newFile(self, force=False):
		'''
		Open new file
		'''
		# fix: not using force correctly (if open file, continue w/o saving?)
		nuke.scriptClose()

	def exit(self, force=False):
		'''
		Exit the program
		'''
		# fix: not using force correctly
		nuke.executeInMainThread(nuke.scriptExit)

	def checkSaveState(self, useHash=False):
		return nuke.root().modified()

	# Nodes
	##################################################
	def getAllNodes(self, recurse=False):
		return self.ensureNodes(nuke.allNodes(recurseGroups=recurse))

	def getNodeByName(self, name):
		node = nuke.toNode(name)
		if not node:
			return None
		return self.ensureNode(node)

	def getSoftwareVersion(self):
		return nuke.NUKE_VERSION_STRING

	def getNodesByType(self, nodeType, recurse=False):
		allNodes = self.getAllNodes(recurse=recurse)
		validNodes = []
		for node in allNodes:
			if nodeType.lower() == node.getType():
				validNodes.append(node)

		return self.ensureNodes(validNodes)

		# node types are always upper cased
		# ex: read > Read
		# nodeType = nodeType[0].upper() + nodeType[1:]
		# return self.ensureNodes(nuke.allNodes(nodeType))

	def selectNode(self, node):
		self.clearSelection()
		node = self.ensureNode(node)
		node.setProperty('selected', True)

	# Repeats functionality of selectNode,
	# But can't clearSelection before adding each node
	def selectNodes(self, nodes):
		self.clearSelection()
		nodes = self.ensureNodes(nodes)
		for node in nodes:
			node.setProperty('selected', True)

	def deselectNodes(self, nodes):
		nodes = self.ensureNodes(nodes)
		for node in nodes:
			node.setProperty('selected', False)

	def getSelectedNodes(self, recurse=False):
		return self.ensureNodes(nuke.selectedNodes())

	def removeNodes(self, nodes):
		nodes = self.ensureNodes(nodes)
		for node in nodes:
			nuke.delete(node.nativeNode())

	def createInstance(self, node):
		node = self.ensureNode(node)

		# store the selection
		originalSelection = self.getSelectedNodes()
		# clear the selection so the clone
		# isn't auto-connected
		self.clearSelection()

		# clone
		clone = nuke.clone(node.nativeNode(), inpanel=False)
		clone.hideControlPanel()

		# restore the selection
		self.selectNodes(originalSelection)
		return self.ensureNode(clone)

	def createPrimitive(self, primitiveType):
		raise Exception('Not implemented')

	def localizeNodes(self, nodes=[]):
		return True

		localizeRoot = os.environ.get('ARK_CACHE')
		if not localizeRoot:
			return False

		if not len(nodes):
			nodes = self.getAllNodes(recurse=True)

		fileNodeTypesList = self.getOption('fileNodeTypesList')

		for obj in nodes:
			if obj.getType() in fileNodeTypesList:
				if not obj or not obj.hasProperty('file'):
					continue

				try:
					path = nuke.toNode(obj.name()).knob('file').getValue()
				except:
					path = None

				if not path:
					continue

				newPath = self.localizeFiles(path, localizeRoot)
				if not newPath:
					continue

				newPath = cOS.normalizeFramePadding(newPath)
				obj.setProperty('file', newPath)

		return True

	def delocalizeNodes(self, nodes=[]):
		localizeRoot = os.environ.get('ARK_CACHE')
		if not localizeRoot:
			return False

		if not len(nodes):
			nodes = self.getAllNodes(recurse=True)

		fileNodeTypesList = self.getOption('fileNodeTypesList')

		for obj in nodes:
			if obj.getType() in fileNodeTypesList:
				if not obj or not obj.hasProperty('file'):
					continue

				try:
					path = nuke.toNode(obj.name()).knob('file').getValue()
				except:
					path = None

				newPath = pathManager.globalizePath(path)

				newPath = cOS.normalizeFramePadding(newPath)
				obj.setProperty('file', newPath)

		return True

	def relocalizeNodes(self, nodes=[]):
		return True

		localizeRoot = os.environ.get('ARK_CACHE')
		if not localizeRoot:
			return False

		if not len(nodes):
			nodes = self.getAllNodes(recurse=True)

		fileNodeTypesList = self.getOption('fileNodeTypesList')

		for obj in nodes:
			if obj.getType() in fileNodeTypesList:
				if not obj or not obj.hasProperty('file'):
					continue

				try:
					path = nuke.toNode(obj.name()).knob('file').getValue()
				except:
					path = None

				newPath = pathManager.localizePath(path)

				if cOS.isValidSequence(newPath):
					newPath = cOS.getFirstFileFromFrameRangeText(newPath)

				if not newPath or not os.path.isfile(str(newPath)):
					newPath = pathManager.globalizePath(path)

				newPath = cOS.normalizeFramePadding(newPath)
				obj.setProperty('file', newPath)
				obj.nativeNode().knob('reload').execute()

		return True
	# Rendering
	##################################################
	def getRenderProperty(self, prop):
		try:
			renderNode = self.getRenderNode()
		except:
			renderNode = None

		# without a renderNode we can't get much
		if renderNode:
			if prop == 'width':
				return renderNode.width()
			elif prop == 'height':
				return renderNode.height()
		else:
			if prop == 'width':
				return nuke.root().width()
			elif prop == 'height':
				return nuke.root().height()

	def setRenderProperty(self, prop, val):
		renderNode = self.getRenderNode()
		renderNode.setProperty(prop, val)

	def getOutputFilename(self, path=None, jobData=None):
		renderNode = self.getRenderNode()
		path = cOS.unixPath(renderNode.getProperty('file'))
		return pathManager.translatePath(path)

	def setOutputFilename(self, filename, jobData=None):
		filename = cOS.unixPath(filename)
		renderNode = self.getRenderNode()
		renderNode.setProperty('file', filename)

	def getRenderRange(self):
		return self.getAnimationRange()

	def setRenderRange(self, start, end):
		self.setAnimationRange(start, end)

	def preSubmit(self, jobData):

		# disable proxy before save, then set it back after
		rootNode = nuke.root()
		proxyOn = rootNode['proxy'].value()
		rootNode['proxy'].setValue(False)

		# Optical flares now are precomped
		if len(nuke.allNodes('OpticalFlares')):

			import arkNuke

			with nuke.root():

				# Deselect all nodes
				if nuke.selectedNodes():
					for i in nuke.selectedNodes():
						i['selected'].setValue(False)

				# Get all enabled flares
				for item in nuke.allNodes():
					if item.Class() == 'OpticalFlares':
						if not item['disable'].getValue():

							# Create precomp nodes and render them
							item['selected'].setValue(True)
							precomp = arkNuke.writePreComp()
							item['selected'].setValue(False)

							precomp['passName'].setValue(item.name())
							precomp['render'].execute()
							precomp['reading'].setValue(True)

							# Disable the flare
							item['disable'].setValue(True)

			# Save temp file to submit. This file will have its flares
			# deleted so that it can be rendered on the farm
			tempFile = os.path.join('r:/_trash/OpFlares/', jobData['sourceFile'].split('/')[-1])
			nuke.scriptSave(tempFile)

			# Call subprocess to delete flares
			file = globalSettings.NUKE_EXE
			script = os.path.join(globalSettings.DEADLINE, 'custom\scripts\Jobs\handleFlares.py')
			options = {'tempFile': str(tempFile)}
			process = cOS.startSubprocess([file, '-V', '2', '-t', script, '-options', str(options)])
			cOS.waitOnProcess(process)

			# Update job data
			jobData['sourceFile'] = tempFile

		super(Nuke, self).preSubmit(jobData)

		rootNode['proxy'].setValue(proxyOn)
		return jobData

	def postSubmit(self, jobData):
		# If the submitted file has an optical flares back up, delete it
		if os.path.exists(os.path.join('r:/_trash/OpFlares/', jobData['sourceFile'].split('/')[-1])):
			os.remove(os.path.join('r:/_trash/OpFlares/', jobData['sourceFile'].split('/')[-1]))

	def setRenderable(self, nodes, value=True):
		nodes = self.ensureNodes(nodes)
		for node in nodes:
			node.setProperty('disable', not value)

	def createPlayblast(self, playblastOptions):
		# from nukescripts import flip, flipbooking

		# self.selectNode(playblastOptions['camera'])
		# node = nuke.selectedNode()
		# flipbooker = flipbooking.gFlipbookFactory.getApplication('Default')
		# flipbooker.run()
		pass

	# Animation
	##################################################
	def getFPS(self):
		return nuke.root()['fps'].getValue()

	def setFPS(self, fps):
		nuke.root()['fps'].setValue(fps)

	def getAnimationRange(self):
		start = nuke.root()['first_frame'].getValue()
		end = nuke.root()['last_frame'].getValue()
		return {
			'startFrame': int(start),
			'endFrame': int(end),
		}

	def setAnimationRange(self, start, end):
		nuke.root()['first_frame'].setValue(start)
		nuke.root()['last_frame'].setValue(end)

	def getAnimationFrame(self):
		return nuke.frame()

	def setAnimationFrame(self, frame):
		nuke.frame(frame)

	def loadAnimation(self, nodes, animation):
		raise Exception('Not implemented')

	def removeAnimation(self, nodes, frame):
		raise Exception('Not implemented')

	# Visibility (not really valid in Nuke)
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
		return self.getAllNodes()

	# IO
	##################################################
	def importAlembicGeometry(self, filename, method=None, inContext=False):
		geoNode = nuke.nodes.ReadGeo2()
		geoNode['file'].fromUserText(filename)
		# if the control panel isn't shown the info
		# won't be properly updated
		geoNode.showControlPanel()
		geoNode.hideControlPanel()
		nuke.zoom(1, (geoNode.xpos(), geoNode.ypos()))
		geoNode.setSelected(True)
		return self.ensureNode(geoNode)

	def importAlembicCamera(self, filename, method=None):
		cameraNode = nuke.nodes.Camera2(
			read_from_file=True,
			file=filename)
		# if the control panel isn't shown the info
		# won't be properly updated
		cameraNode.showControlPanel()
		cameraNode.hideControlPanel()
		nuke.zoom(1, (cameraNode.xpos(), cameraNode.ypos()))
		cameraNode.setSelected(True)
		return self.ensureNode(cameraNode)

	def importFBXGeometry(self, filename):
		return self.importAlembicGeometry(filename)

	def importFBXCamera(self, filename):
		return self.importAlembicCamera(filename)

	def importOBJGeometry(self, filename):
		return self.importFBXGeometry(filename)

	def importImage(self, filename, method=None, importOptions=None):
		readNode = nuke.nodes.Read()
		readNode['auto_alpha'].setValue(1)
		readNode['file'].fromUserText(filename)
		readNode.setSelected(True)
		nuke.zoom(1, (readNode.xpos(), readNode.ypos()))
		return self.ensureNode(readNode)

	def importImageSequence(self, filename, method=None,importOptions=None):
		if not cOS.isFrameRangeText(filename):
			filename = cOS.getFrameRangeText(filename)
		return self.importImage(filename)

	def createRenderProxy(self,
						filepath,
						renderOptions={'scale': 1.0,
										'particleWidthMultiplier': 1.0,
										'hairWidthMultiplier': 1.0,
										'previewFaces': 5000,
										'geoToLoad': 'Proxy'},
						renderEngine='Vray'):
		filepath = cOS.normalizePath(filepath)
		if renderEngine.lower() == 'vray':
			nodeName = filepath.split('.')[0]
			filepath = (r'{}'.format(filepath))

			vrayNode = nuke.nodes.VRayProxy()
			vrayNode['name'].setValue(nodeName)
			vrayNode['file'].setValue(filepath)
			vrayNode['uniform_scale'].setValue(renderOptions['scale'])
			vrayNode['preview_type'].setValue(renderOptions['geoToLoad'])
			vrayNode.setSelected(True)
			nuke.zoom(1, (vrayNode.xpos(), vrayNode.ypos()))
			vrayNode['anim_type'].setValue(1)

	def createMaterialFromImages(self, texFile, matName = ''):
		pass

	def createDisplacementFromMap(self, normalNode, matName = ''):
		pass

	def exportAlembic(self, filepath, frameRange, exportOptions=None):
		print 'Nuke!'

	def addCommand2(self, toolbar, tool):
		if tool.get('software') is None or 'nuke' in tool.get('software'):
			toolbar.currentTools[tool.get('name').lower()] = tool

	# UI
	########################################

	# def getPanel(self, panelName):
	# 	return nuke.getPaneFor(panelName)

	# PySide
	########################################
	def getQTApp(self):

		# This checks that the widget in Nuke's UI is part of the
		# Foundry::UI::DockMainWindow, which should comply to the same results as in
		# the Maya.py logic for this function

		for window in QtGui.qApp.topLevelWidgets():
			if window.inherits('QMainWindow') and window.metaObject().className() == 'Foundry::UI::DockMainWindow':
				return window
		else:
			raise RuntimeError('Could not find DockMainWindow instance')


	def launch(
		self,
		Dialog,
		qApplication=None,
		parent=None,
		newWindow=None,
		docked=False,
		*args,
		**kwargs):

		if parent is not None:
			newWindow = True

		dialog = None

		if parent:
			print 'have parent'
			dialog = Dialog(parent, *args, **kwargs)
			if newWindow:
				dialog.setWindowFlags(QtCore.Qt.Window)
			dialog.show()
		else:
			print 'using activeWindow'

			if docked:
				import nukescripts
				# name = Ark Toolbar
				name = Dialog.defaultOptions.get('title') or Dialog.__name__
				name = name.replace(' ', '')
				name = name.replace('_', '')
				# name = ArkToolbar

				moduleName = (Dialog.__module__).split('.')[0]
				# moduleName = arkToolbar

				dialogString = '__import__("' + moduleName + '").' + name
				# dialogString = '__import__("arkToolbar").ArkToolbar'

				pane = nuke.getPaneFor('DAG.1')
				nukescripts.panels.registerWidgetAsPanel(dialogString,
								name,
								'uk.co.thefoundry.' + name + '.1',
								create=True).addToPane(pane)
			else:

				# dialog = Dialog(QtGui.QApplication.activeWindow(), *args, **kwargs)
				# if newWindow:
				# 	dialog.setWindowFlags(QtCore.Qt.Window)

				# dialog.show()

				nukeApp = self.getQTApp()
				undocked = Dialog(parent=nukeApp, *args, **kwargs)
				undocked.show()
				undocked.raise_()

				return undocked




		return dialog


	# # Nodes
	# ########################################
	# def getSelectedNodes(self):
	# 	return nuke.selectedNodes()

	# def getNodesByType(self, nodeType):
	# 	return nuke.allNodes(nodeType)

	# # fix: hax, should wrap nodeTypes and set nodeWrapper.cacheable
	# def getCacheableNodes(self):
	# 	cacheableTypes = ['Read','ReadGeo2','Camera2']
	# 	cacheableNodes = []
	# 	for nodeType in cacheableTypes:
	# 		cacheableNodes += self.getNodesByType(nodeType)
	# 	return cacheableNodes

	# def cacheNode(self, node):
	# 	ogPath = node['file'].getValue()
	# 	ogPath = cOS.unixPath(ogPath)

	# 	if globalSettings.TEMP in ogPath:
	# 		ogPath = node['label'].getValue()

	# 	framePaddingLocation = ogPath.find('%')
	# 	# if there's no % sign (frame padding) look for a #
	# 	if framePaddingLocation == -1:
	# 		framePaddingLocation = ogPath.find('#')

	# 	if framePaddingLocation == -1:
	# 		allFiles = [ogPath]
	# 	else:
	# 		globPath = ogPath[:framePaddingLocation] + '*'
	# 		allFiles = list(glob.iglob(globPath))

	# 	self.cache(allFiles)

	# 	node['label'].setValue(ogPath)
	# 	node['file'].setValue(self.getCachePath(ogPath))

	# def uncacheNode(self, node):
	# 	ogPath = node['label'].getValue()
	# 	if ogPath:
	# 		node['file'].setValue(ogPath)
	# 		node['label'].setValue('')

	# # File Info
	# ########################################

	# def getFileInfo(self):
	# 	fileInfo = {}
	# 	scriptFile = nuke.root()['name'].getValue()

	# 	fileInfo['baseName'] = scriptFile.split('/')[-1].split('.')[0]
	# 	format = nuke.root().format()
	# 	fileInfo['pixelAspect'] = format.pixelAspect()
	# 	fileInfo['width'] = format.width()
	# 	fileInfo['height'] = format.height()
	# 	fileInfo['fps'] = str(int(nuke.root().knob('fps').getValue()))
	# 	fileInfo['isStereo'] = False
	# 	fileInfo['version'] = None

	# 	#info from Caretaker
	# 	fileInfo['pathInfo'] = ct.pathInfo(scriptFile)
	# 	fileInfo['userInfo'] = ct.userInfo
	# 	if 'project_info' in fileInfo['pathInfo'] and fileInfo['pathInfo']['project_info'] and fileInfo['pathInfo']['project_info']['short_name']:
	# 		fileInfo['short_name'] = fileInfo['pathInfo']['project_info']['short_name']

	# 	if (scriptFile):
	# 		fileParts = (scriptFile).split("/")
	# 		if (len(fileParts) > 3 and fileParts[2].upper() == 'WORKSPACES'):
	# 			fileInfo['shotName'] = fileParts[3]
	# 		elif len(fileParts) > 3:
	# 			fileInfo['shotName'] = fileParts[2] + '-' + fileParts[3]
	# 		fileInfo['version'] = cOS.getVersion(scriptFile)

	# 		# ensure 3 digit padding on all versions
	# 		fileInfo['version'] = arkUtil.pad(int(fileInfo['version']), 3)
	# 		fileInfo['jobName'] = fileParts[1]
	# # fix: pull this from caretaker
	# #      if (self.jobName.upper() in self.jobPrefixes):
	# #        self.jobPrefix = self.jobPrefixes[self.jobName.upper()]

	# 		fileInfo['jobRoot'] = globalSettings.SHARED_ROOT + fileInfo['jobName'] + '/'
	# 		today = date.today()
	# 		fileInfo['postingRoot'] = fileInfo['jobRoot'] + 'POSTINGS/' + str(today.year) + '_' + arkUtil.pad(today.month, 2) + '_' + arkUtil.pad(today.day, 2) + '/'
	# 	else:
	# 		nuke.message("Please save your script before using IE's tools")

	# 	fileInfo['startFrame'] = int(nuke.root().knob('first_frame').getValue())
	# 	fileInfo['endFrame'] = int(nuke.root().knob('last_frame').getValue())
	# 	fileInfo['frameCount'] = fileInfo['endFrame'] - fileInfo['startFrame']

	# 	return fileInfo

	# def isFileDirty(self):
	# 	return nuke.modified()

	# def saveIncrementWithInitials(self):
	# 	if not ct.userInfo or 'initials' not in ct.userInfo:
	# 		return

	# 	newScript = nuke.toNode('root').name()[:-6] + ct.userInfo['initials'] + '.nk'
	# 	newScript = cOS.incrementVersion(newScript)

	# 	nuke.scriptSaveAs(newScript)

	# # Rendering
	# ########################################
	# def getDefaultJobName(self):
	# 	filename = self.args['node']['file'].getValue()
	# 	pathInfo = cOS.getPathInfo(filename)
	# 	jobName = pathInfo['basename'].split('.')[0]
	# 	version = cOS.getVersion(jobName)
	# 	if not version:
	# 		jobName += '_v%03d' % cOS.getVersion(self.getFilename())
	# 	return jobName

	# def getRenderProperties(self, camera=None):
	# 	shotInfo = ShotInfo.ShotInfo()

	# 	return {
	# 		'width': shotInfo.width,
	# 		'height': shotInfo.height,
	# 		'startFrame': shotInfo.startFrame,
	# 		'endFrame': shotInfo.endFrame,
	# 		'program': 'nk',
	# 		'jobType': 'Nuke_Comp',
	# 		'node': self.args['node'].name(),
	# 	}

	# def getOutputFilename(self, outputPath, jobData):
	# 	# fix: should ensure name is file-safe
	# 	return self.args['node']['file'].getValue()

	# # Pre's
	# ########################################
	# def preSubmit(self, jobData):
	# 	# disable proxy before save, then set it back after
	# 	rootNode = nuke.root()
	# 	proxyOn = rootNode['proxy'].value()
	# 	rootNode['proxy'].setValue(False)
	# 	super(Nuke, self).preSubmit(jobData)
	# 	rootNode['proxy'].setValue(proxyOn)



	# # PySide
	# ########################################
	# def getQTApp(self):
	# 	app = QtGui.QApplication.instance()
	# 	if not app:
	# 		print 'No app instance found, creating'
	# 		app = QtGui.QApplication(sys.argv)
	# 	return app

	# # def launch(self, Dialog, *args, **kwargs):
	# 	# return super(Nuke, self).launch(Dialog, *args, **kwargs)
	# 	# return ex
	# 	# ex = Dialog(QtGui.QApplication.activeWindow(), *args, **kwargs)
	# 	# ex.show()
	# 	# return ex

	# def launch(self, Dialog, parent=None, newWindow=None, *args, **kwargs):
	# 	if parent is not None:
	# 		newWindow = True

	# 	if parent:
	# 		print 'have parent'
	# 		ex = Dialog(parent, *args, **kwargs)
	# 		if newWindow:
	# 			ex.setWindowFlags(QtCore.Qt.Window)
	# 		ex.show()
	# 	else:
	# 		print 'using activeWindow'
	# 		ex = Dialog(QtGui.QApplication.activeWindow(), *args, **kwargs)
	# 		if newWindow:
	# 			ex.setWindowFlags(QtCore.Qt.Window)
	# 		ex.show()

	# 	return ex
