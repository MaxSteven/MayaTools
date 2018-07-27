
# Standard modules
# import sys
import json
import os
# import time
import pymel.core as pymel
import maya.cmds as mc
from maya import OpenMayaUI as OpenMayaUI
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from maya.app.general.mayaMixin import MayaQDockWidget
import maya.mel as mel
mayaVersion = mc.about(version=True)
if int(mayaVersion) > 2016:
	from shiboken2 import wrapInstance, getCppPointer
else:
	from shiboken import wrapInstance, getCppPointer

# Our modules
import Translator
# import PySide.QtCore as QtCore

from qt import QtGui
from qt import QtCore

import arkInit
arkInit.init()

import Node_Maya
import SerialNode_Maya
import cOS
import pathManager
import arkUtil
import settingsManager
globalSettings = settingsManager.globalSettings()

class Maya(Translator.Translator):

	nodeClass = Node_Maya.Node_Maya
	fileExtension = 'mb'
	program = 'maya'
	serialNodeClass = SerialNode_Maya.SerialNode_Maya
	frameRates = {'film': 24, 'game': 15, 'pal': 25, 'ntsc': 30, 'show': 48, 'palf': 50, 'ntscf': 60}
	environmentFormatString = '${%s}'

	def __init__(self):
		super(Maya, self).__init__()
		self.setOptions(
			canUse=True,
			canPublishShots=True,
			renderNodeType=['camera'],
			cameraType='camera',
			hasCameras=True,
			hasFrames=True,
			hasPasses=True,
			canPreview=True,
			jobTypes=['Maya_VRayStandalone'],
			imageImportMethods = ['camera backplate', 'texture', 'texture on a plane w/ correct aspect'],
			exportTypes=['Geometry', 'Camera'],
			hasKeyCommands=True,
			hasChunks=False,
			closeOnSubmit=False,
			displayOptions=['Shaded', 'Wireframe on Shaded', 'Textured'],
			defaultCameras=['perspShape', 'frontShape', 'topShape', 'sideShape'],
			vRayRenderPresets={
				'Final (Existing)': {},
				'Full': {
					'samplerType': 1,
					'minShadeRate': 16,
					'dmcMinSubdivs': 4,
					'dmcMaxSubdivs': 16,
					'dmcThreshold': .004,
					'primaryEngine': 2,
					'secondaryEngine': 0,
					'cam_mbOn': 1,
					'cam_mbCameraMotionBlur': 1
				},
				'Decent': {
						'samplerType': 1,
						'minShadeRate': 8,
						'dmcMinSubdivs': 1,
						'dmcMaxSubdivs': 8,
						'dmcThreshold': .008,
						'cam_mbOn': 1,
						'cam_mbCameraMotionBlur': 1
					},
				'Fast': {
					'samplerType': 1,
					'minShadeRate': 4,
					'dmcMinSubdivs': 1,
					'dmcMaxSubdivs': 4,
					'dmcThreshold': .012,
					'giOn': 0,
					'cam_mbOn': 0,
					'cam_mbCameraMotionBlur': 0
				},
				'Progressive':{
					'samplerType': 3,
					'minShadeRate': 12,
					'dmcMinSubdivs': 1,
					'dmcMaxSubdivs': 100,
					'dmcThreshold': 1,
					'progressiveThreshold': 0.004,
					'progressiveBundleSize': 32,
					'imageFormatStr': 'exr (multichannel)'
				}
			},
			renderPresetOrder=['Progressive', 'Fast', 'Decent', 'Full', 'Final (Existing)']
		)

		# made dialog into a class variable
		# so that value is retained in scope
		self.ex = None
	# Basics
	##################################################
	# Inherited

	# Data Storage
	##################################################
	def getSceneData(self, key=None):
		rawData = pymel.fileInfo.get('label')
		# If key 'label' does not exist yet, create empty key-value pair
		if not rawData:
			pymel.fileInfo['label'] = ''
			return None
		# Maya automatically escapes json quotation marks, restore unescaped string
		rawData = rawData.decode('string_escape')
		data = None
		try:
			data = arkUtil.parseJSON(rawData)
		except Exception as err:
			raise err
		if not key:
			return data
		else:
			return data.get(key)

	def getSafeObjectName(self, name):
		if ':' in name:
			return name.replace('-','_')

		return arkUtil.safeFilename(name).replace('-','_')

	def setSceneData(self, key, val=None):
		data = self.getSceneData()
		if not data:
			data = {}
		if val is None:
			if isinstance(key, dict):
				data = key
			else:
				data[key] = key
		else:
			data[key] = val
		pymel.fileInfo['label'] = json.dumps(data)

	def removeSceneData(self, key):
		data = self.getSceneData()
		if key in data:
			del data[key]
		self.setSceneData(data)

	def getFileHash(self):
		hashDict = {}

		geoNodes = pymel.ls(geometry=True)
		# print 'geoNodes:', len(geoNodes)

		lightNodes = pymel.ls(lights=True)
		# print 'lightNodes:', len(lightNodes)

		camNodes = pymel.ls(cameras=True)
		# print 'camNodes:', len(camNodes)

		texNodes = pymel.ls(textures=True)
		# print 'texNodes:', len(texNodes)

		matNodes = pymel.ls(materials=True)
		# print 'matNodes:', len(matNodes)

		imagePlaneNodes = pymel.ls(type='imagePlane')
		# print 'imagePlane:', len(imgPlaneNodes)

		transformNodes = pymel.ls(transforms=True)
		# print 'transformNodes:', len(transformNodes)

		renderNodes = pymel.ls(objectsOnly=True)
		renderNodes = [n for n in renderNodes if 'vray' in n.nodeType().lower()]
		# print renderNodes
		# print 'renderNodes:', len(renderNodes)

		def hashParams(params, hashDict):
			for attr in params:
				paramName = str(node) + '.' + str(attr)
				if not hashDict.get(paramName):
					try:
						hashDict[paramName] = str(pymel.getAttr(paramName, sl=True))
					except:
						pass

			return hashDict

		paramCount = 0
		for node in geoNodes:
			geoParams = pymel.listAttr(node, keyable=True, shortNames=True, unlocked=True)
			paramCount += len(geoParams)

			# continue

			hashDict.update(hashParams(geoParams, hashDict))

		# print 'geoParams', paramCount

		paramCount = 0
		for node in lightNodes:
			lightParams = pymel.listAttr(node, shortNames=True, unlocked=True)
			paramCount += len(lightParams)

			# continue

			hashDict.update(hashParams(lightParams, hashDict))

		# print 'lightParams', paramCount

		paramCount = 0
		for node in camNodes:
			camParams = pymel.listAttr(node, shortNames=True, unlocked=True)
			paramCount += len(camParams)

			# continue


			hashDict.update(hashParams(camParams, hashDict))

		# print 'camParams', paramCount

		paramCount = 0
		for node in texNodes:
			texParams = pymel.listAttr(node, shortNames=True, unlocked=True)
			paramCount += len(texParams)

			# continue

			hashDict.update(hashParams(texParams, hashDict))

		# print 'texParams', paramCount

		paramCount = 0
		matParams = []
		for node in matNodes:
			matParams = pymel.listAttr(node, shortNames=True, unlocked=True)
			paramCount += len(matParams)

			# continue


			hashDict.update(hashParams(matParams, hashDict))

		# print 'matParams', paramCount

		imagePlaneParams = []
		for node in imagePlaneNodes:
			imagePlaneParams = pymel.listAttr(node, shortNames=True, unlocked=True)
			paramCount += len(imagePlaneParams)

			# continue

			hashDict.update(hashParams(imagePlaneParams, hashDict))

		paramCount = 0
		for node in renderNodes:

			renderParams = pymel.listAttr(node, shortNames=True, unlocked=True)
			paramCount += len(renderParams)

			# continue

			hashDict.update(hashParams(renderParams, hashDict))

		# print 'renderParams', paramCount

		paramCount = 0
		for node in transformNodes:
			transformParams = pymel.listAttr(node, cfo=True, keyable=True, shortNames=True, unlocked=True)
			transformParams = [attr for attr in transformParams if attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz','sx', 'sy', 'sz', 'visibility']]
			paramCount += len(transformParams)

			# continue

			hashDict.update(hashParams(transformParams, hashDict))

		# print 'transformParams', paramCount

		return hash(frozenset(hashDict.items()))

	# Files
	##################################################
	def getFilename(self):
		'''
		Get the current open filename
		'''
		path = str(pymel.sceneName())
		if path == 'untitled':
			path = ''

		return pathManager.translatePath(path)

	def saveFile(self, filename=None, force=False):
		'''
		Save the current open file, optionally specifying
		a name to save the file as
		'''
		if not filename:
			filename = self.getFilename()
		pymel.saveAs(filename)

	def openFile(self, filename, force=False):
		'''
		Open the specified filename
		'''
		pymel.openFile(filename, force=force)

	def newFile(self, force=False):
		'''
		Open new file. Force=True continues without saving current open file
		'''
		pymel.newFile(force=force)

	def exit(self, force=False):
		'''
		Exit the program
		'''
		pymel.cmds.quit(force=force)


	def checkSaveState(self, useHash=False):
		if not useHash:
			return mc.file(q=True, modified=True)

		# if self.fileHash:
		# 	newFileHash = self.getFileHash()
		# 	if newFileHash != self.fileHash:
		# 		self.fileHash = newFileHash
		# 		return True
		# 	return False
		# else:
		# 	self.fileHash = self.getFileHash()
		# 	return mc.file(q=True, modified=True)
		# else:
		# 	return mc.file(q=True, modified=True)
	# Nodes
	##################################################
	def getAllNodes(self, recurse=False):
		# Get list of all node types
		return self.ensureNodes(pymel.ls())

	def getChildNodes(self, parentNode):
		parentNode = self.ensureNodes(parentNode)

		children = []
		for node in parentNode:
			newChildren = pymel.listRelatives(node.nativeNode(),
				allDescendents=True,
				shapes=True)
			children += [self.getNodeByPath(n) for n in newChildren]

		return children

	def getNodeByName(self, name):
		name = self.getSafeObjectName(name)
		node = pymel.ls(name)
		if not node:
			return None
		if len(node) > 1:
			# Note: this should not happen with Maya (unique naming)
			raise Exception('More than one node with matching name found')
		node = node[0]
		if not node:
			return None
		return self.ensureNode(node)

	def getNodeByPath(self, name):
		# getNodeByName breaks when the name contains pipes, this should be used instead
		node = pymel.ls(name)
		if not node:
			return None
		if len(node) > 1:
			# Note: this should not happen with Maya (unique naming)
			raise Exception('More than one node with matching name found')
		node = node[0]
		if not node:
			return None
		return self.ensureNode(node)

	def getNodesByType(self, nodeType, recurse=False):
		allNodes = self.getAllNodes()
		validNodes = []
		nodeType = nodeType.lower()
		for node in allNodes:

			# special case for materials
			if nodeType == 'material':
				shadingGroups = self.getNodesByType('shadingEngine')
				materials = []
				for shadingGroup in shadingGroups:
					surfaceShader = shadingGroup.getInputByProperty('surfaceShader')
					if surfaceShader:
						materials.append(surfaceShader)

				return materials

			elif nodeType == node.getType():
				validNodes.append(node)

		return self.ensureNodes(validNodes)

		# node types are always upper cased
		# ex: read > Read
		# nodeType = nodeType[0].upper() + nodeType[1:]
		# return self.ensureNodes(nuke.allNodes(nodeType))

	def selectNode(self, node):
		self.clearSelection()
		node = self.ensureNode(node)
		pymel.select(node.name(), add=True)

	# Repeating selectNode call, but can't call
	# clear selection before adding each node
	def selectNodes(self, nodes):
		self.clearSelection()
		nodes = self.ensureNodes(nodes)
		# Maya nodes do not have a 'selected' attribute, modify active selection list instead
		for node in nodes:
			pymel.select(node.name(), add=True)

	def deselectNodes(self, nodes):
		nodes = self.ensureNodes(nodes)
		for node in nodes:
			pymel.select(node.name(), deselect=True)

	def getSelectedNodes(self, recurse=False):
		return self.ensureNodes(pymel.ls(selection=True))

	# ignoreErrors flag to deal with Maya deleting multiple
	# nodes in one go. Ex: if you delete Transform node, shape goes with it
	# with ignoreErrors=False, Maya will error when trying to delete
	# the already deleted node
	def removeNodes(self, nodes, ignoreErrors=True):
		nodes = self.ensureNodes(nodes)
		if ignoreErrors:
			for node in nodes:
				try:
					pymel.delete(node.nativeNode())
				except:
					pass
		else:
			for node in nodes:
				pymel.delete(node.nativeNode())

	def localizeNodes(self, nodes=[]):
		return True

		localizeRoot = os.environ.get('ARK_CACHE')
		if not localizeRoot:
			return False

		if not len(nodes):
			nodes = self.getAllNodes(recurse=True)
		fileNodesTypeDict = {
			'file': 'fileTextureName',
			'alembicnode':'abc_File',
			'vraylightiesshape': 'iesFile',
			'vrayscene': 'FilePath',
			'vraymesh': 'fileName2',
			'vrayvolumegrid': 'inFile',
			'imageplane': 'imageName',
		}

		for obj in nodes:
			if obj.getType() in fileNodesTypeDict.keys():
				objType = obj.getType()
				path = obj.getProperty(fileNodesTypeDict[objType])
				newPath = self.localizeFiles(path, localizeRoot)
				if newPath:
					# set path with padding only if these image types
					if obj.getType() in ['imageplane', 'vraymesh', 'vrayscene']:
						newPath = cOS.normalizeFramePadding(newPath)

					pymel.setAttr(obj.name(fullpath=True) + '.' + fileNodesTypeDict[objType], newPath, type = 'string')

					# if file reset uvTilingMode to UDIM
					if obj.getType() == 'file':
						obj.setProperty('uvTilingMode', 3)

			if mc.referenceQuery(obj.name(fullpath=True), isNodeReferenced=True):
				refObject = mc.referenceQuery(obj.name(fullpath=True), referenceNode=True)
				refNode = pymel.FileReference(refObject)
				path = refNode.path
				newPath = self.localizeFiles(path, localizeRoot)
				if newPath:
					refNode.replace(newPath)

		return True

	def delocalizeNodes(self, nodes=[]):
		localizeRoot = os.environ.get('ARK_CACHE')
		if not localizeRoot:
			return False

		if not len(nodes):
			nodes = self.getAllNodes(recurse=True)

		fileNodesTypeDict = {
			'file': 'fileTextureName',
			'alembicnode':'abc_File',
			'vraylightiesshape': 'iesFile',
			'vrayscene': 'FilePath',
			'vraymesh': 'fileName2',
			'vrayvolumegrid': 'inFile',
			'imageplane': 'imageName',
		}
		for obj in nodes:
			if obj.getType() in fileNodesTypeDict.keys():
				objType = obj.getType()
				path = obj.getProperty(fileNodesTypeDict[objType])

				if cOS.isValidSequence(path):
					path = cOS.getFirstFileFromFrameRangeText(path)

				newPath = pathManager.globalizePath(path)

				# set path with padding only if these image types
				if obj.getType() in ['imageplane', 'vraymesh', 'vrayscene']:
					newPath = cOS.normalizeFramePadding(newPath)

				pymel.setAttr(obj.name(fullpath=True) + '.' + fileNodesTypeDict[objType], newPath, type = 'string')

				# if file reset uvTilingMode to UDIM
				if obj.getType() == 'file':
					obj.setProperty('uvTilingMode', 3)

			if mc.referenceQuery(obj.name(fullpath=True), isNodeReferenced=True):
				refObject = mc.referenceQuery(obj.name(fullpath=True), referenceNode=True)
				refNode = pymel.FileReference(refObject)
				path = refNode.path
				newPath = pathManager.globalizePath(path)
				refNode.replaceWith(newPath)

		return True

	def relocalizeNodes(self, nodes=[]):
		return True

		localizeRoot = os.environ.get('ARK_CACHE')
		if not localizeRoot:
			return False

		if not len(nodes):
			nodes = self.getAllNodes(recurse=True)

		fileNodesTypeDict = {
			'file': 'fileTextureName',
			'alembicnode':'abc_File',
			'vraylightiesshape': 'iesFile',
			'vrayscene': 'FilePath',
			'vraymesh': 'fileName2',
			'vrayvolumegrid': 'inFile',
			'imageplane': 'imageName',
		}
		for obj in nodes:
			if obj.getType() in fileNodesTypeDict.keys():
				objType = obj.getType()
				path = obj.getProperty(fileNodesTypeDict[objType])

				newPath = pathManager.localizePath(path)

				if cOS.isValidSequence(newPath):
					newPath = cOS.getFirstFileFromFrameRangeText(newPath)

				if not newPath or not os.path.isfile(str(newPath)):
					newPath = pathManager.globalizePath(path)

				# set path with padding only if these image types
				if obj.getType() in ['imageplane', 'vraymesh', 'vrayscene']:
					newPath = cOS.normalizeFramePadding(newPath)

				pymel.setAttr(obj.name(fullpath=True) + '.' + fileNodesTypeDict[objType], newPath, type='string')

				# if file reset uvTilingMode to UDIM
				if obj.getType() == 'file':
					obj.setProperty('uvTilingMode', 3)

		return True

	# Can only createInstances on mesh/transform objects in Maya
	# Return None otherwise
	def createInstance(self, node):
		node = self.ensureNode(node)
		# store the selection
		originalSelection = self.getSelectedNodes()
		# clear the selection so the clone
		# isn't auto-connected
		self.clearSelection()

		# clone
		try:
			clone = pymel.instance(node.nativeNode())[0]
		except Exception as err:
			print 'Error: ' + err.message
			self.selectNodes(originalSelection)
			return None

		# restore the selection
		self.selectNodes(originalSelection)
		return self.ensureNode(clone)

	# TODO: implement createPrimitive
	def createPrimitive(self, primitiveType):
		raise Exception('Not implemented')

	def applyNodePreset(self, node, preset):
		originalSelection = self.getSelectedNodes()
		self.selectNode(node)
		# node needs to be selected to apply preset
		mel.eval('applyPresetToNode "{}" "" "" "{}" 1'.format(
			node.name(),
			preset
		))
		# restore original selection
		self.selectNodes(originalSelection)

	# Rendering
	##################################################
	def getRenderProperty(self, prop):
		'''
		Get a variety of render properties:
		- width: render width
		- height: render height
		'''
		# Maya does not have render node, so get width/height using attributes
		if prop == 'width':
			return pymel.getAttr('defaultResolution.width')
		elif prop == 'height':
			return pymel.getAttr('defaultResolution.height')
		elif prop == 'nearPlane':
			return self.getOption('renderNode').getProperty('nearClipPlane')
		elif prop == 'farPlane':
			return self.getOption('renderNode').getProperty('farClipPlane')
		else:
			raise Exception('Property not implemented: ' + prop)

	def setRenderProperty(self, prop, val):
		'''
		Set a variety of render properties:
		- width: render width
		- height: render height
		'''
		# Maya does not have render node, so set width/height using attributes
		if prop == 'width':
			pymel.setAttr('defaultResolution.width', val)
		elif prop == 'height':
			pymel.setAttr('defaultResolution.height', val)
		else:
			raise Exception('Property not implemented: ' + prop)

	# Camera object will be stored as jobData['node'] in ShepherdSubmit
	def getOutputFilename(self, path, jobData):
		filename = arkUtil.removeTrailingSlash(path) + \
			('/renders/v%03d/' % jobData['version']) + \
			jobData['name'] + '_' + jobData['node'] + '.%04d.exr'

		# fix Maya's referencing which puts ':' in the filename.  Maxwell replaces these w/ '_'
		filename = filename[:2] + filename[2:].replace(':','_')
		return pathManager.translatePath(filename)

	# Camera object will be stored as jobData['node'] in ShepherdSubmit
	def setOutputFilename(self, filename, jobData):
		filename = pathManager.translatePath(filename)
		pymel.setAttr(
			'defaultRenderGlobals.imageFilePrefix',
			jobData['name'] + '_' + jobData['node'],
			type='string')

	def getRenderRange(self):
		start = pymel.getAttr('defaultRenderGlobals.startFrame')
		end = pymel.getAttr('defaultRenderGlobals.endFrame')
		return {
			'startFrame': int(start),
			'endFrame': int(end),
		}

	def setRenderRange(self, start, end):
		pymel.setAttr('defaultRenderGlobals.startFrame', start)
		pymel.setAttr('defaultRenderGlobals.endFrame', end)

	def preSubmit(self, jobData):
		if not os.path.isfile(jobData['previewPath']):
			raise Exception('Preview Render doesnt exist')

		if pymel.getAttr('vraySettings.samplerType') == 3:
			raise Exception('Cannot submit to the farm with progressive sampling')

		lightSelects = self.getNodesByType('vrayrenderelementset')

		for n in lightSelects:
			name = n.getProperty('vray_name_lightselect')
			defaultPrefix = 'lightselect'
			newPrefix = 'l_'

			if name.startswith(defaultPrefix):
				name = name[len(defaultPrefix):]

			if not name.startswith(newPrefix):
				name = newPrefix + name

			n.setProperty('vray_name_lightselect', name)


		# get all the render layers
		layers = self.getNodesByType('renderLayer')
		# get ones that are additional and non-referenced
		# ex: 'ref:whatever' is fine, as is 'defaultRenderLayer'
		# but 'shadowPass' isn't
		additionalLayers = [l for l in layers
			if ':' not in l.name() and
			'defaultRenderLayer' not in l.name()]

		if len(additionalLayers) > 0:
			raise Exception('Scene has render layers, please remove before submitting')

		try:
			pymel.setAttr('vraySettings.fileNamePrefix', jobData['name'] + '_' + jobData['node'], type='string')
			pymel.setAttr('vraySettings.abortOnMissingAsset', True)

			# fix: if Maxwell once we add vray
			# tell Maxwell to output MXI's
			# pymel.setAttr('maxwellRenderOptions.writeMXI', 1)
			# set output to exr
			# pymel.setAttr('defaultRenderGlobals.imageFormat', 31)
		except Exception as err:
			raise err
			# raise Exception('VRay renderer not found.')
			# print 'Maxwell renderer not found.'
			# pass

		if arkUtil.makeWebSafe(jobData['node']) != jobData['node']:
			raise Exception('Camera name has invalid characters, alpha numeric + underscore only: ' +
				jobData['node'])

		# If VRayStandalone job, presubmit for Vrayscene
		if jobData['jobType'] == 'Maya_VRayStandalone':
			# Set only jobData camera to renderable
			cameras = self.getNodesByType('camera')
			for camera in cameras:
				camera.setProperty('renderable', 0)
			renderCamera = self.getNodeByName(jobData['node'])
			renderCamera.setProperty('renderable', 1)

			pymel.setAttr('vraySettings.vrscene_render_on', 0)
			pymel.setAttr('vraySettings.vrscene_on', 1)
			pymel.setAttr('vraySettings.animType', 0)
			pymel.setAttr('vraySettings.misc_separateFiles', 0)
			pymel.setAttr('vraySettings.misc_eachFrameInFile', 1)
			try:
				pymel.setAttr(jobData['node'] + '.vrayCameraPhysicalUseMoBlur',
								pymel.getAttr('vraySettings.cam_mbOn'))
			except:
				pass
			# vrsceneFile = jobData['sourceFile']
			# arkUtil.replaceAll(vrsceneFile, '.mb', '_' + jobData['name'] + '.vrscene')
			vrsceneFile = globalSettings.TEMP + 'render.vrscene'
			pymel.setAttr('vraySettings.vrscene_filename', vrsceneFile, type='string')
			# jobData['sourceFile'] = vrsceneFile
			jobData['program'] = 'vray'
			# 'Render' .vrscene to temp location (.vrscene at same filepath as sourceFile)
			# pymel.vrend()

		# save the file
		return super(Maya, self).preSubmit(jobData)

	def postSubmit(self, jobData):
		pymel.setAttr('vraySettings.vrscene_render_on', 1)
		pymel.setAttr('vraySettings.vrscene_on', 0)
		return True

	def setRenderable(self, nodes, value=True):
		nodes = self.ensureNodes(nodes)
		for node in nodes:
			node.setProperty('primaryVisibility', value)

	def getDescendants(self, nodes, immediateOnly=False):
		descendents = []
		for node in nodes:
			if immediateOnly:
				descendents.extend(pymel.listRelatives(node.name(), children=True))
			else:
				descendents.extend(pymel.listRelatives(node.name(), allDescendents=True))

		return self.ensureNodes(descendents)

	def createPlayblast(self, playblastOptions):
		currentCam = None
		if playblastOptions['camera']:
			currentCam = self.getCamFromView()
			self.setCamView(self.getNodeByName(playblastOptions['camera']))

		# turn off pan/zoom to avoid showing extra stuff
		panZoomEnabled = self.getCamFromView().getChildren()[0].getProperty('panZoomEnabled')
		if panZoomEnabled:
			self.getCamFromView().getChildren()[0].setProperty('panZoomEnabled', False)

		outputPath = playblastOptions['inPath']

		panel = self.getPanel('Persp View')
		cOS.makeDir(outputPath.rpartition('/')[0])

		currentState = mc.modelEditor(panel, query=True, imagePlane=True)

		audioFile = None
		if playblastOptions['sound']:
			playblastOptions['sound'] = False
			audioNodes = mc.ls(type='audio')
			if audioNodes:
				audio = mc.getAttr(audioNodes[0] + '.filename')
				if os.path.isfile(audio):
					audioFile = audio
					print audioFile
					playblastOptions['sound'] = True

		playblastOptions['audioFile'] = audioFile

		playblastOptions['fps'] = self.getFPS()

		# turn on diplay gradient for Maya's default alpha to work
		if not playblastOptions['background']:
			pymel.displayPref(dgr=True)
			mc.modelEditor(panel, edit=True, imagePlane=False)

		# turn off display gradient for flat or imageplane bg
		else:
			pymel.displayPref(dgr=False)
			mc.modelEditor(panel, edit=True, imagePlane=True)

		try:
			pymel.playblast(format=playblastOptions['format'],
						widthHeight=playblastOptions['size'],
						fp=4,
						compression='png',
						viewer=False,
						percent=100,
						quality=100,
						startTime=playblastOptions['startTime'],
						endTime=playblastOptions['endTime'],
						filename=outputPath
						)

		except:
			return False

		playblastOptions['inPath'] = outputPath + '.%04d.png'
		result = super(Maya, self).createPlayblast(playblastOptions)

		# set cam settings back to original, in reverse order
		if panZoomEnabled:
			self.getCamFromView().getChildren()[0].setProperty('panZoomEnabled', True)

		if currentCam:
			self.setCamView(currentCam)

		pymel.displayPref(dgr=False)
		mc.modelEditor(panel, edit=True, imagePlane=currentState)
		return result

	def renderTurntable(self, referenceFile):

		pass

		# import maya.standalone
		# maya.standalone.initialize()
		# import maya.cmds as cmds

		# turntableFile = 'R:/Test_Project/Workspaces/maya/3D/turntable_test_v0010.mb'

		# if cOS.isfile(turntableFile):
		# 	cmds.file(turntableFile, open=True, force=True)
		# 	cmds.file(referenceFile, reference=True, groupReference=True, force=True)

		# 	objGroup = cmds.group(name='turntable_objects')
		# 	cmds.makeIdentity(objGroup, a=True, s=True, t=True, r=True)
		# 	cmds.xform(objGroup, centerPivots=True)

		# 	bboxGroup = cmds.exactWorldBoundingBox(objGroup)
		# 	bboxBounding = cmds.exactWorldBoundingBox('boundingBox')

		# 	def toLength(bbox):
		# 	    return [abs(bbox[0] - bbox[3]), abs(bbox[1] - bbox[4]), abs(bbox[2] - bbox[5])]

		# 	def scalingFactor(bbox1, bbox2):
		# 	    return max(max(bbox1[0] / bbox2[0], bbox1[1] / bbox2[1]), bbox1[2] / bbox2[2])

		# 	bboxGroupLength = toLength(bboxGroup)
		# 	bboxBoundingLength = toLength(bboxBounding)

		# 	factor = scalingFactor(bboxGroupLength, bboxBoundingLength)

		# 	cmds.xform('turntable_scale', scale=[factor,factor,factor])

		# 	cmds.move(0, (-.5 * bboxGroupLength[1]), 0, objGroup + '.scalePivot', objGroup + '.rotatePivot', relative=True)
		# 	cmds.move(0, 0.025 * factor, 0, objGroup, rpr=True)

		# 	cmds.parent(objGroup, 'turntable_rotate')

		# 	cmds.file(save=True)
		# else:
		# 	print 'Can\'t locate the turntable file!'


	def addToRenderSet(slef, setName, elementName):
		mel.eval('sets -edit -forceElement %s %s' % (setName, elementName))

	def addRenderElement(self, elementName):
		mel.eval('vrayAddRenderElement {}'.format(elementName))
		return self.ensureNode(pymel.ls(sl=True)[0])

	def removeRenderElement(self, elementName):
		mel.eval('vrayRemoveRenderElement {}'.format(elementName))

	def createShadingNode(self, nodeName):
		mc.shadingNode(nodeName, asUtility = True)
		return self.ensureNode(pymel.ls(sl=True)[0])

	def connectProperty(self, fromNode, fromNodeProperty, toNode, toNodeProperty):
		mc.connectAttr('{}.{}'.format(fromNode.name(), fromNodeProperty), '{}.{}'.format(toNode.name(), toNodeProperty))

	# Animation
	##################################################
	def getFPS(self):
		# Maya only returns currentTime frame as a string
		time = pymel.currentUnit(query=True, time=True)
		if time in self.frameRates:
			return self.frameRates[time]
		else:
			raise Exception('Framerate/FPS not supported: ' + time)

	def setFPS(self, fps):
		unitName = None
		for name, frameRate in self.frameRates:
			if self.frameRate == fps:
				unitName = name
		if unitName:
			pymel.currentUnit(time=unitName)
		else:
			raise Exception('Framerate/FPS not supported: ' + fps)

	def getAnimationRange(self):
		start = pymel.playbackOptions(query=True, animationStartTime=True)
		end = pymel.playbackOptions(query=True, animationEndTime=True)
		return {
			'startFrame': int(start),
			'endFrame': int(end),
		}

	def setAnimationRange(self, start, end):
		pymel.playbackOptions(animationStartTime=start)
		pymel.playbackOptions(animationEndTime=end)

	def getAnimationFrame(self):
		return pymel.currentTime()

	def setAnimationFrame(self, frame):
		pymel.currentTime(frame, update=True)

	# TODO: implement load/removeAnimation
	def loadAnimation(self, nodes, animation):
		raise Exception('Not implemented')

	def removeAnimation(self, nodes, frame):
		raise Exception('Not implemented')

	def setCamView(self, camName, frame=None):
		pymel.lookThru(camName.name())
		if frame != None:
			pymel.currentTime(frame, update=True)

	def getCamFromView(self):
		return self.getNodeByName(pymel.lookThru(q=True))

	# Visibility
	##################################################
	def isolateNodes(self, nodes):
		nodes = self.ensureNodes(nodes)
		# Query current modeling view
		view = pymel.paneLayout('viewPanes', query=True, pane1=True)
		self.selectNodes(nodes)
		# Turn on isolate selection mode
		pymel.isolateSelect(view, state=True)
		pymel.isolateSelect(view, addSelected=True)

	def unisolateNodes(self, nodes):
		nodes = self.ensureNodes(nodes)
		# Query current modelng view
		view = pymel.paneLayout('viewPanes', query=True, pane1=True)
		self.selectNodes(nodes)
		# Remove selected and turn off isolation mode
		pymel.isolateSelect(view, removeSelected=True)
		pymel.isolateSelect(view, state=False)

	def showNodes(self, nodes):
		for node in nodes:
			pymel.showHidden(node)

	def hideNodes(self, nodes):
		for node in nodes:
			pymel.hide(node)

	def getHiddenNodes(self):
		return pymel.ls(invisible=True)

	def getVisibleNodes(self):
		return pymel.ls(visible=True)

	# Locks
	##################################################
	def setNodeTransformLock( self, objectName=None, useSelected=False, value=True):
		# Lock translation, rotation, scale
		transformList = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']

		if useSelected:
			objectList = self.getSelectedNodes()
			for each in objectList:
				for item in transformList:
					each.setProperty(item, lock=value)
		else:
			objectName = self.getNodeByName(objectName)
			for item in transformList:
				objectName.setProperty(item, lock=value)

	def getSoftwareVersion(self):
		return mc.about(version=True)

	def setNodeSelectionLock( self, objectName=None, useSelected=False, value=True):
		# Order matters for Enabled -> DisplayType -> DisplayType -> Enabled,
		# so split into True/False
		if useSelected:
			objectList = self.getSelectedNodes()
			for each in objectList:
				if value:
					each.setProperty('overrideEnabled', 1)
					each.setProperty('overrideDisplayType', 2)
				else:
					each.setProperty('overrideDisplayType', 0)
					each.setProperty('overrideEnabled', 0)
		elif objectName:
			objectName= self.getNodeByName(objectName)
			if value:
				objectName.setProperty('overrideEnabled', 1)
				objectName.setProperty('overrideDisplayType', 2)
			else:
				objectName.setProperty('overrideDisplayType', 0)
				objectName.setProperty('overrideEnabled', 0)
		else:
			raise Exception('Invalid arguments')

	# IO
	##################################################
	# Returns list of new nodes
	# TODO: options for type of import method
	def importAlembicGeometry(self, filepath, method=None, inContext=False):
		if cOS.getExtension(filepath) != 'abc':
			raise Exception ('Filename not Alembic .abc file')
		pre = self.getAllNodes()
		pymel.AbcImport(filepath)
		post = self.getAllNodes()
		objName = self.getSafeObjectName(cOS.getPathInfo(filepath)['name'])

		nodes = self.newNodes(pre, post)
		importGroup = pymel.group(em=True, n=objName)
		for node in nodes:
			if not pymel.listRelatives(node.name(), parent=True):
				pymel.parent(node.name(), importGroup)

		return self.getNodeByName(importGroup)

	# Returns list of new nodes
	def importAlembicCamera(self, filepath, method=None):
		groupNode = self.importAlembicGeometry(filepath)
		# Check if camera node created
		hasCamera = False
		children = pymel.listRelatives(groupNode.name(), allDescendents = True)
		children = self.ensureNodes(children)
		for item in children:
			if item.getType() == 'camera':
				hasCamera = True
		# Verify camera node
		if not hasCamera:
			print 'No Camera found!'
		return groupNode

	def importFBXGeometry(self, filename):
		if not filename.endswith('.fbx'):
			raise Exception ('Filename not FBX .fbx file')
		pre = self.getAllNodes()
		pymel.importFile(filename)
		post = self.getAllNodes()
		return self.newNodes(pre, post)

	def importFBXCamera(self, filename):
		diff = self.importFBXGeometry(filename)
		hasCamera = False
		for item in diff:
			if item.getType() == 'camera':
				hasCamera=True
		if not hasCamera:
			raise Exception ('Camera not imported')
		return diff

	def importOBJGeometry(self, filename):
		if not filename.endswith('.obj'):
			raise Exception ('Filename not OBJ .obj file')
		pre = self.getAllNodes()
		pymel.importFile(filename)
		post = self.getAllNodes()
		return self.newNodes(pre, post)

	# Supports 3 methods of import: materialEditor, imagePlane, referencePlane
	# imagePlane created for frontShape orthographic view by default
	def importImage(self, filename, method=None, importOptions=None):
		normalized = cOS.normalizePath(filename)
		objName = self.getSafeObjectName(cOS.getPathInfo(normalized)['name']) + '_file'


		if method == 'materialEditor':
			# Create file node
			mel.eval('nodeEdCreateNodeCommand "file";')
			imageFileNode = pymel.rename(pymel.ls(sl=True)[0], self.getSafeObjectName(objName))
			pymel.setAttr(imageFileNode + '.fileTextureName', filename)

		elif method == 'imagePlane':
			# ensure image planes are turned on for the viewports
			for i in range(0, 50):
				try:
					mel.eval('modelEditor -e -imagePlane true modelPane%d;' % i)
				except:
					pass

			if 'Camera' in importOptions and importOptions['Camera']:
				imageFileNode = pymel.imagePlane(camera=importOptions['Camera'], fileName=filename, maintainRatio=True, name=objName)[1]

			else:
				print 'No Camera specified for Image plane.'
				return

		elif method == 'referencePlane':
			planeNodes = pymel.polyPlane(axis=(0.0, 0.0, 1.0), height=1, width=1, \
				name= objName+'_plane', \
				subdivisionsX=1, subdivisionsY=1, createUVs=1)
			try:
				transform = filter(lambda item: item.nodeType() == 'transform', planeNodes)
			except:
				raise Exception ('polyPlane did not create a transform node')
			# Create shader
			transform = transform[0]
			shader = pymel.shadingNode('VRayMtl', asShader=True, name=objName + '_vrayMtl')
			shaderSet = pymel.sets(renderable=True, noSurfaceShader=True, empty=True, name=objName + '_VRayMtl4SG')
			pymel.connectAttr(shader + '.outColor', shaderSet+'.surfaceShader')

			mel.eval('nodeEdCreateNodeCommand "file";')
			imageFileNode = pymel.rename(pymel.ls(sl=True)[0], self.getSafeObjectName(objName))
			pymel.setAttr(imageFileNode + '.fileTextureName', filename)

			texture = pymel.shadingNode('file', asTexture=True)
			pymel.rename(texture, objName+'_file')
			texture.setAttr('fileTextureName', filename)

			# Resize plane to match dimensions
			width = texture.getAttr('outSizeX')
			height = texture.getAttr('outSizeY')
			transform.setAttr('scaleX', width/100)
			transform.setAttr('scaleY', height/100)

			# Apply shader to plane
			pymel.connectAttr('%s.outColor' %texture, '%s.color' %shader)
			pymel.sets(shaderSet, edit=True, forceElement=transform)
			pymel.select(planeNodes[0])
		else:
			raise Exception ('importImage method not supported')

		return self.ensureNode(imageFileNode)

	# Gets frame: 1001 of imageSequence
	def importImageSequence(self, filename, method=None, importOptions=None):
		# Generate sequence information
		normalized = cOS.getFirstFileFromFrameRangeText(filename)
		if normalized == False:
			return

		objName = self.getSafeObjectName(cOS.getPathInfo(normalized)['name']).split('.')[0] + '_file'

		if method == 'materialEditor':
			mel.eval('optionVar -sv create2dTextureType "texture";')
			mel.eval('nodeEdCreateNodeCommand "file";')
			imageFileNode = pymel.rename(pymel.ls(sl=True)[0], objName)
			pymel.setAttr(imageFileNode + '.useFrameExtension', 1)
			pymel.setAttr(imageFileNode + '.fileTextureName', normalized)

		elif method == 'imagePlane':
			# ensure image planes are turned on for the viewports
			for i in range(0, 50):
				try:
					mel.eval('modelEditor -e -imagePlane true modelPane%d;' % i)
				except:
					pass

			if 'Camera' in importOptions and importOptions['Camera']:
				imageFileNode = pymel.imagePlane(camera=importOptions['Camera'], maintainRatio=True, name=objName)[1]
				pymel.setAttr(imageFileNode + '.imageName', normalized)
				pymel.setAttr(imageFileNode + '.useFrameExtension', 1)

			else:
				print 'No Camera specified for Image plane.'
				return

		elif method == 'referencePlane':
			planeNodes = pymel.polyPlane(axis=(0.0, 0.0, 1.0), height=1, width=1, \
				name= objName+'_plane', \
				subdivisionsX=1, subdivisionsY=1, createUVs=1)
			try:
				transform = filter(lambda item: item.nodeType() == 'transform', planeNodes)
			except:
				raise Exception ('polyPlane did not create a transform node')

			# Create shader
			transform = transform[0]
			shader = pymel.shadingNode('VRayMtl', asShader=True, name=objName + '_vrayMtl')
			shaderSet = pymel.sets(renderable=True, noSurfaceShader=True, empty=True, name=objName + '_VRayMtl4SG')
			pymel.connectAttr(shader + '.outColor', shaderSet+'.surfaceShader')

			mel.eval('nodeEdCreateNodeCommand "file";')
			imageFileNode = pymel.rename(pymel.ls(sl=True)[0], self.getSafeObjectName(objName))
			pymel.setAttr(imageFileNode + '.useFrameExtension', 1)
			pymel.setAttr(imageFileNode + '.fileTextureName', normalized)

			pymel.connectAttr('%s.outColor' %imageFileNode, '%s.color' %shader)
			pymel.sets(shaderSet, edit=True, forceElement=transform)
			pymel.select(planeNodes[0])

		else:
			raise Exception ('importImage method not supported')

		return self.ensureNode(imageFileNode)

	def createRenderProxy(self,
		filepath,
		renderOptions={
			'scale': 1.0,
			'particleWidthMultiplier': 1.0,
			'hairWidthMultiplier': 1.0,
			'previewFaces': 5000,
			'geoToLoad': 'Preview'
		},
		renderEngine='Vray'):

		geomTypeDict = {
			'Preview': 2,
			'Bounding Box': 1,
			'GPU Mesh': 4
		}
		shaders = []

		for shadingEngine in self.getNodesByType('shadingEngine'):
			if pymel.attributeQuery('surfaceShader', node=shadingEngine.name(), exists=True):
				shader =  pymel.connectionInfo(shadingEngine.name()+'.surfaceShader', sfd=True).split('.')[0]
				if shader and shader not in shaders:
					shaders.append(shader)

		fileStuff = cOS.getPathInfo(filepath)
		nodeName = self.getSafeObjectName(fileStuff['name'])

		# allows multiple import of same name
		nodeName = self.getAvailableNodeName(nodeName)

		if renderEngine.lower() == 'vray':

			mel.eval('vrayCreateProxy -node "{}"  -dir "{}" -existing -createProxyNode -animStart 0 -animLength 0'.format(nodeName, filepath))
			scale = renderOptions['scale']

			proxy = self.getNodeByName(nodeName)

			nodeShape = pymel.listRelatives(nodeName, children=True, shapes=True)[0]
			vrayMesh =  pymel.connectionInfo(nodeShape + '.inMesh', sfd=True).split('.')[0]
			vrayMeshMtlSG = pymel.connectionInfo(nodeShape + '.instObjGroups[0]', dfs=True)[0].split('.')[0]
			vrayMeshMtl =  pymel.connectionInfo(vrayMeshMtlSG + '.surfaceShader', sfd=True).split('.')[0]

			# User Settings
			pymel.setAttr(vrayMesh + '.geomType', geomTypeDict[renderOptions['geoToLoad']])
			pymel.setAttr(vrayMesh + '.hairWidthMultiplier', renderOptions['hairWidthMultiplier'])
			pymel.setAttr(vrayMesh + '.particleWidthMultiplier', renderOptions['particleWidthMultiplier'])
			pymel.setAttr(vrayMesh + '.numPreviewFaces', renderOptions['previewFaces'])
			pymel.setAttr(nodeName + '.scale', scale, scale, scale)

			# Standard default settings
			pymel.setAttr(vrayMesh + '.computeBBox', 1)
			pymel.setAttr(vrayMesh + '.computeNormals', 0)
			pymel.setAttr(vrayMesh + '.animType', 1)
			pymel.setAttr(vrayMesh + '.useAlembicOffset', 1)
			pymel.setAttr(vrayMesh + '.subdivLevel', 0)

			# shader re-connection
			shaderNames = pymel.getAttr(vrayMeshMtl + '.shaderNames')
			for i, shader in enumerate(shaderNames):
				if shader in shaders:
					pymel.connectAttr(shader + '.outColor',
						vrayMeshMtl + '.shaders[' + str(i) + ']')

			return proxy

	def createMaterialFromImages(self, texFile, matName=''):
		for f in texFile:
			fPathInfo = cOS.getPathInfo(f)
			if len(fPathInfo['name'].split('.')) >= 2:
				if fPathInfo['name'].split('.')[1] == 'ao_rough_metal_ior':
					metalFilePath = f
				elif fPathInfo['name'].split('.')[1] == 'diffuse':
					diffuseFilePath = f
				elif fPathInfo['name'].split('.')[1] == 'normal_height':
					normalFilePath = f

		if matName == '':
			matName = cOS.getPathInfo(texFile[0])['name'].split('.')[0]

		matName = self.getSafeObjectName(matName)

		if pymel.objExists(matName+'_material'):
			vrayMaterial = pymel.ls(matName + '_material')[0]
			normalFile = pymel.ls(matName + '_normal')[0]

		else:
			mel.eval('optionVar -sv create2dTextureType "texture";')
			mel.eval('nodeEdCreateNodeCommand "file";')
			metalFile = pymel.rename(pymel.ls(sl=True)[0], matName+'_ao_rough_metal_ior')
			mel.eval('vray addAttributesFromGroup "{}" "vray_file_gamma" 1;'.format(metalFile))
			pymel.setAttr(metalFile + '.fileTextureName', metalFilePath)
			pymel.setAttr(metalFile + '.uvTilingMode', 3)
			pymel.setAttr(metalFile + '.colorSpace', 'Raw')
			pymel.setAttr(metalFile + '.vrayFileColorSpace', 0)

			mel.eval('optionVar -sv create2dTextureType "texture";')
			mel.eval('nodeEdCreateNodeCommand "file";')
			diffuseFile = pymel.rename(pymel.ls(sl=True)[0], matName+'_diffuse')
			mel.eval('vray addAttributesFromGroup "{}" "vray_file_gamma" 1;'.format(diffuseFile))
			pymel.setAttr(diffuseFile+'.fileTextureName', diffuseFilePath)
			pymel.setAttr(diffuseFile+'.uvTilingMode', 3)
			pymel.setAttr(diffuseFile+'.vrayFileColorSpace', 2)

			mel.eval('optionVar -sv create2dTextureType "texture";')
			mel.eval('nodeEdCreateNodeCommand "file";')
			normalFile = pymel.rename(pymel.ls(sl=True)[0], matName+'_normal')
			mel.eval('vray addAttributesFromGroup "{}" "vray_file_gamma" 1;'.format(normalFile))
			pymel.setAttr(normalFile+'.fileTextureName',normalFilePath)
			pymel.setAttr(normalFile+'.uvTilingMode', 3)
			pymel.setAttr(normalFile+'.colorSpace', 'Raw')
			pymel.setAttr(normalFile+'.vrayFileColorSpace', 0)

			iorMultiDiv = pymel.shadingNode('multiplyDivide', asUtility=True, name=matName+'_calcTrueIOR')
			pymel.setAttr(iorMultiDiv+'.input1', (1,1,1))
			pymel.setAttr(iorMultiDiv+'.operation', 2)

			remapIorMultiDiv = pymel.shadingNode('multiplyDivide', asUtility=True, name=matName+'_remapIOR')
			pymel.setAttr(remapIorMultiDiv+'.input2', (100,100,100))

			diffuseMultiDiv = pymel.shadingNode('multiplyDivide', asUtility=True, name=matName+'_calDiffuse')

			reflectMultiDiv = pymel.shadingNode('multiplyDivide', asUtility=True, name=matName+'_calReflection')

			dieElectricMultiDiv = pymel.shadingNode('multiplyDivide', asUtility=True, name=matName+'_calcDielectricReflection')

			maxNonMetalVrayUserScalar = pymel.shadingNode('VRayUserScalar', asUtility=True, name=matName+'_maxNonMetallicReflection')
			pymel.setAttr(maxNonMetalVrayUserScalar+'.defaultValue', 0.1)

			invertMetalRev = pymel.shadingNode('reverse', asUtility=True, name=matName+'_invertMetal')

			invertRoughRev = pymel.shadingNode('reverse', asUtility=True, name=matName+'_invertRoughness')

			invertGreenRev = pymel.shadingNode('reverse', asUtility=True, name=matName+'_invertGreenNormal')

			blendReflection = pymel.shadingNode('blendColors', asUtility=True, name=matName+'_blendReflections')

			mel.eval('nodeEdCreateNodeCommand "VRayMtl";')
			vrayMaterial = pymel.rename(pymel.ls(sl=True)[0], matName+'_material')

			pymel.setAttr(vrayMaterial + '.bumpMapType', 1)
			pymel.setAttr(vrayMaterial + '.brdfType', 3)

			# ao_rough_metal
			pymel.connectAttr(metalFile + '.outAlpha', iorMultiDiv + '.input2X', force=True)
			pymel.connectAttr(metalFile + '.outAlpha', iorMultiDiv + '.input2Y', force=True )
			pymel.connectAttr(metalFile + '.outAlpha', iorMultiDiv +'.input2Z', force=True)

			pymel.connectAttr(metalFile + '.outColorB', invertMetalRev + '.inputX', force=True)
			pymel.connectAttr(metalFile + '.outColorB', invertMetalRev + '.inputY', force=True)
			pymel.connectAttr(metalFile + '.outColorB', invertMetalRev + '.inputZ', force=True)

			pymel.connectAttr(metalFile + '.outColorB', reflectMultiDiv + '.input2X', force=True)
			pymel.connectAttr(metalFile + '.outColorB', reflectMultiDiv + '.input2Y', force=True)
			pymel.connectAttr(metalFile + '.outColorB', reflectMultiDiv + '.input2Z', force=True)

			pymel.connectAttr(metalFile + '.outColorG', invertRoughRev + '.inputX', force=True)
			pymel.connectAttr(metalFile + '.outColorG', invertRoughRev + '.inputY', force=True)
			pymel.connectAttr(metalFile + '.outColorG', invertRoughRev + '.inputZ', force=True)

			pymel.connectAttr(metalFile + '.outColorB', blendReflection + '.blender', force=True)

			# diffuse
			pymel.connectAttr(diffuseFile + '.outColor', reflectMultiDiv + '.input1', force=True)
			pymel.connectAttr(diffuseFile + '.outColor', diffuseMultiDiv + '.input1', force=True)

			pymel.connectAttr(diffuseFile + '.outAlpha', vrayMaterial + '.opacityMapR', force=True)
			pymel.connectAttr(diffuseFile + '.outAlpha', vrayMaterial + '.opacityMapG', force=True)
			pymel.connectAttr(diffuseFile + '.outAlpha', vrayMaterial + '.opacityMapB', force=True)

			# normal
			pymel.connectAttr(normalFile + '.outColorR', vrayMaterial + '.bumpMapR', force=True)
			pymel.connectAttr(normalFile + '.outColorB', vrayMaterial + '.bumpMapB', force=True)
			pymel.connectAttr(normalFile + '.outColorG', invertGreenRev + '.inputX', force=True)

			# diffuseMultiDiv
			pymel.connectAttr(invertMetalRev + '.output', diffuseMultiDiv + '.input2', force=True)
			pymel.connectAttr(diffuseMultiDiv + '.output', vrayMaterial + '.color', force=True)

			# iorMultiDiv
			pymel.connectAttr(iorMultiDiv + '.outputX', remapIorMultiDiv + '.input1X', force=True)
			pymel.connectAttr(iorMultiDiv + '.outputX', remapIorMultiDiv + '.input1Y', force=True)
			pymel.connectAttr(iorMultiDiv + '.outputX', remapIorMultiDiv + '.input1Z', force=True)

			# remapIOR
			pymel.connectAttr(remapIorMultiDiv + '.outputX', vrayMaterial + '.refractionIOR', force=True)

			# reflectMultiDiv
			pymel.connectAttr(reflectMultiDiv + '.output', blendReflection + '.color1', force=True)

			# invertRoughRev
			pymel.connectAttr(invertRoughRev + '.output', dieElectricMultiDiv + '.input1', force=True)
			pymel.connectAttr(invertRoughRev + '.outputX', vrayMaterial + '.reflectionGlossiness', force=True)

			# dieElectricMultiDiv
			pymel.connectAttr(maxNonMetalVrayUserScalar + '.defaultValue', dieElectricMultiDiv + '.input2X', force=True)
			pymel.connectAttr(maxNonMetalVrayUserScalar + '.defaultValue', dieElectricMultiDiv + '.input2Y', force=True)
			pymel.connectAttr(maxNonMetalVrayUserScalar + '.defaultValue', dieElectricMultiDiv + '.input2Z', force=True)

			pymel.connectAttr(dieElectricMultiDiv + '.output', blendReflection+'.color2', force=True)

			# blendReflection
			pymel.connectAttr(blendReflection + '.output', vrayMaterial + '.reflectionColor')

			# invertGreenRev
			pymel.connectAttr(invertGreenRev + '.outputX', vrayMaterial + '.bumpMapG', force=True)

			# vrayMaterial
			pymel.setAttr(vrayMaterial + '.bumpMapType', 1)


		matDict = {
				'material': self.ensureNode(vrayMaterial),
				'displacement': self.ensureNode(normalFile)
				}

		return matDict

	def createDisplacementFromMap(self, normalNode, matName=''):
		normalFile = normalNode.name()
		matName = self.getSafeObjectName(matName)
		if pymel.objExists(matName + '_displacement'):
			vrayDisplacement = pymel.ls(matName + '_displacement')[0]

		else:
			# remapHeight
			heightRemap = pymel.shadingNode('remapValue', asUtility=True, name=matName + '_remapHeight')
			pymel.setAttr(heightRemap + '.outputMin', -.5)
			pymel.setAttr(heightRemap + '.outputMax', .5)

			# dMapVrayUserColor
			dMapVrayUserColor = pymel.shadingNode('VRayUserColor', asUtility=True, name=matName + '_displacementMap')

			# vrayDisplacement
			vrayDisplacement = pymel.shadingNode('VRayDisplacement', asUtility=True, name=matName + '_displacement')

			pymel.connectAttr(normalFile + '.outAlpha', heightRemap + '.inputValue', force=True)

			pymel.connectAttr(heightRemap + '.outValue', dMapVrayUserColor + '.colorR', force=True)
			pymel.connectAttr(heightRemap +'.outValue', dMapVrayUserColor + '.colorG', force=True)
			pymel.connectAttr(heightRemap + '.outValue', dMapVrayUserColor + '.colorB', force=True)

			pymel.connectAttr(dMapVrayUserColor + '.outColor', vrayDisplacement + '.displacement')

			mel.eval('vray addAttributesFromGroup "{}" "vray_displacement" 1;'.format(vrayDisplacement))

			pymel.setAttr(vrayDisplacement + '.vrayDisplacementAmount', 1.0)
			pymel.setAttr(vrayDisplacement + '.vrayDisplacementKeepContinuity', 1)
			pymel.setAttr(vrayDisplacement + '.vrayDisplacementUseBounds', 1)
			pymel.setAttr(vrayDisplacement + '.vrayDisplacementCacheNormals', 1)
			pymel.setAttr(vrayDisplacement + '.vrayDisplacementMaxValue', (0.5, 0.5, 0.5), type='double3')
			pymel.setAttr(vrayDisplacement + '.vrayDisplacementMinValue', (-0.5, -0.5, -0.5), type='double3')

		return self.ensureNode(vrayDisplacement)

	def exportAlembic(self, filepath, frameRange, exportOptions=None):
		frameRanges = []
		if '-' in frameRange:
			frameRanges.extend([frame.strip() for frame in frameRange.split('-')])
		else:
			frameRanges.extend([frameRange, frameRange])

		commandString = '-frameRange ' + frameRanges[0] + ' ' + frameRanges[1]


		if exportOptions:
			if exportOptions.get('noNormals'):
				commandString += ' -noNormals'

			if exportOptions.get('writeCreases'):
				commandString += ' -writeCreases'

			commandString += ' -uvWrite -dataFormat ogawa'

		objectList = []
		if not exportOptions or 'objects' not in exportOptions:
			for ob in self.getNodesByType('geometry'):
				objectList.append(pymel.listRelatives(ob.name(), parent=True)[0])

		else:
			for ob in exportOptions['objects']:
				commandString += ' -root ' + ob
			objectList = exportOptions['objects']

		for ob in objectList:
			children = pymel.listRelatives(ob, allDescendents=True, shapes=True)
			for child in children:
				# if object not shape/mesh type bail
				if pymel.objectType(child) != 'mesh':
					continue

				parent = pymel.listRelatives(child, parent=True)[0]
				parent = self.getNodeByPath(parent)
				try:
					materialName = parent.getMaterial().name()
					if materialName == 'lambert1':
						materialName = 'NoMaterial'
				except:
					materialName = 'NoMaterial'

				if not pymel.attributeQuery('materialName', node=child, exists=True):
					pymel.addAttr(child, ln="materialName", dt="string", keyable=False)

				if ':' in materialName:
					materialName = materialName.split(':')[-1]
				pymel.setAttr(child + '.materialName', materialName)

		commandString += ' -attr materialName -file ' + filepath

		print commandString
		pymel.AbcExport(j=commandString)

	def exportAnimation(self, options=None):
		self.saveFile()
		if not options:
			print 'No Options'
			return
		frameRangeText = options['FrameRange']
		frameRange = [int(frame) for frame in frameRangeText.split('-')]
		frameRangeTuple = (frameRange[0], frameRange[1])
		animDir = cOS.normalizeDir(options['AnimDir'])
		path = animDir + options['AnimName'] + '_' + frameRangeText + '.fbx'
		if not len(mc.ls(sl=True)):
			print 'No selection made'
			return

		selection = mc.ls(sl=True)[0]
		rFile = mc.referenceQuery(selection, filename=True)
		namespace = mc.referenceQuery(selection, namespace=True).replace(':', '')
		mc.file(rFile, importReference = True)
		mc.select(selection, hi=True)
		objectsToDelete = mc.ls(sl=True)
		for obj in objectsToDelete:
			try:
				mc.rename(obj, obj.replace(namespace + ':', ''))
			except:
				pass

		selection = selection.replace(namespace + ':', '')
		mc.select(selection, hi=True)
		objectsToDelete = mc.ls(sl=True)
		mc.select([obj for obj in mc.ls(type='joint') if 'Bind' in obj])
		joints = mc.ls(sl=True)
		if frameRangeTuple[0] != frameRangeTuple[-1]:
			mc.bakeResults(joints, simulation=True, t = frameRangeTuple,
					sampleBy = 1, disableImplicitControl=True,
					preserveOutsideKeys=True, sparseAnimCurveBake=False,
					removeBakedAttributeFromLayer=False, removeBakedAnimFromLayer=False,
					bakeOnOverrideLayer=False, minimizeRotation=True, controlPoints=False,
					shape=True
					)
		mc.select(joints, d=True)
		mc.select([obj for obj in mc.ls(type='transform') if 'lowPoly' in obj])
		rootJointParent = next(joint for joint in joints if 'Ground' in joint)
		selectionChildren = mc.listRelatives(selection, children=True)
		for child in selectionChildren:
			if child not in ['Deformation', 'GEO']:
				mc.delete(child)
		mc.select(rootJointParent, hi=True)
		siblings = [child for child in mc.listRelatives('Deformation', children=True) if 'Ground' not in child]
		mc.delete(siblings)
		allJoints = mc.ls(sl=True)
		uselessJoints = [joint for joint in allJoints if 'End' in joint]
		for joint in uselessJoints:
			allJoints.remove(joint)
			mc.delete(joint)

		for joint in allJoints:
			for attr in ['scaleX', 'scaleY', 'scaleZ', 'visibility']:
				object = mc.listConnections(joint + '.' + attr, source=True)
				print 'deleting', object
				mc.delete(object)

		mc.xform('Deformation', scale = (.01, .01, .01))
		mc.select(selection)
		mc.refresh()

		if options['Export']:
			mel.eval('file -force -options "groups=1;ptgroups=1;materials=1;smoothing=1;normals=1" -typ "FBX export" -pr -es "' + path + '"')

	def getVrayRenderSettings(self):
		renderSettings = {}
		for attr in pymel.listAttr('vraySettings', unlocked=True):
			if pymel.getAttr('vraySettings.' + str(attr), sl=True):
				renderSettings[str(attr)] = pymel.getAttr('vraySettings.' + str(attr), sl=True)

		return renderSettings

	def setVrayRenderSettings(self, renderSettings):
		for k, v in renderSettings.iteritems():
			# in try block because if an attr is locked or connect,
			# we should just ignore it
			try:
				pymel.setAttr('vraySettings.' + k, v)
			except:
				pass

	def previewRender(self, renderOptions):
		# turn off denoiserChannel cuz it fucks w/ the name
		renderElements = self.getNodesByType('vrayrenderelement')
		for renderElements in renderElements:
			if renderElements.getProperty('vrayClassType') == 'denoiserChannel':
				renderElements.setProperty('enabled', False)

		currentTime = pymel.currentTime(query = True)
		pymel.currentTime(renderOptions['frame'])

		currentRenderSettings = self.getVrayRenderSettings()
		self.setVrayRenderSettings(renderOptions['renderSettings'])
		try:
			pymel.vrend(camera=renderOptions['renderNode'])
			pymel.vray('vfbControl', '-saveImage', renderOptions['output'])
		except:
			print 'Preview render failed, please check your scene.'

		pymel.currentTime(currentTime)
		self.setVrayRenderSettings(currentRenderSettings)

		# turn denoiserChannel back on
		renderElements = self.getNodesByType('vrayrenderelement')
		for renderElements in renderElements:
			if renderElements.getProperty('vrayClassType') == 'denoiserChannel':
				renderElements.setProperty('enabled', True)

	def changeColorspace(self, node=None):
		pass
		# if not node:
		# 	return
		# if cOS.getExtension(mc.getAttr(node+'.fileTextureName')) in ['exr', 'hdri', 'hdr']:
		# 	try:
		# 		mc.setAttr(node + '.vrayFileColorSpace', 0)
		# 		mc.setAttr(node + '.colorSpace', 'scene-linear Rec 709/sRGB', type='string')

		# 	except:
		# 		print 'colorspace for ' + node + ' not set automatically.'
		# 		pass

		# else:
		# 	try:
		# 		mc.setAttr(node + '.vrayFileColorSpace', 2)
		# 		mc.setAttr(node + '.colorSpace', 'sRGB', type='string')

		# 	except:
		# 		print 'colorspace for ' + node + ' not set automatically.'
		# 		pass
	# Materials
	##################################################
	def getMaterialByName(self, materialName):
		'''
		Get material from hypershade
		'''
		# whatever pymel equivalent is
		# add to base translator w/ the comment block
		# specific to Maya because Nuke and Houdini handle
		# materials differently
		return self.getNodeByName(materialName)
		### material = pymel.getMaterialByName(materialName)
		### return self.ensureNode(material)

	def addCommand2(self, toolbar, tool):
		if tool.get('software') is None or 'maya' in tool.get('software'):
			toolbar.currentTools[tool.get('name').lower()] = tool

	# UI
	########################################
	def getPanel(self, panelName):
		return mc.getPanel(withLabel = panelName)

	def getQTApp(self):
		ptr = OpenMayaUI.MQtUtil.mainWindow()
		mainWin = wrapInstance(long(ptr), QtGui.QWidget)
		return mainWin

	# PySide
	########################################
	# Uses default getQTApp from Translator.py

	# TODO: Copied over from old Maya.py, verify works and up to date
	def launch(self, Dialog, parent=None, newWindow=None, docked=False, *args, **kwargs):
		if docked:
			# get the title of the new dialog
			newName = arkUtil.makeWebSafe(Dialog.defaultOptions.get('title', ''))

			if int(mayaVersion) > 2016:
				self.ex = Dialog()
				# print 'Launching docked arktoolbar!'
				dialogName = Dialog.__name__
				try:
					mc.deleteUI(dialogName)
				except RuntimeError:
					pass

				dockControl = mc.workspaceControl(dialogName,
								dockToMainWindow=["right", 0],
								initialWidth=60,
								minimumWidth=True,
								widthProperty="preferred",
								label=self.ex.name
					)

				dockObject = OpenMayaUI.MQtUtil.findControl(dockControl)
				dockWidget = wrapInstance(long(dockObject), QtGui.QWidget)
				dockPtr = getCppPointer(dockWidget)[0]
				dockWidget.setAttribute(QtCore.Qt.WA_DeleteOnClose)

				widgetPtr = getCppPointer(self.ex)[0]
				mc.evalDeferred(lambda *args: mc.workspaceControl(dockControl, edit=True, restore=True))
				OpenMayaUI.MQtUtil.addWidgetToMayaLayout(widgetPtr, dockPtr)

			else:
				if self.ex:
					self.ex.deleteInstances(newName)

				# # so that multiple arktoolbars are not loaded
				class arkDialog(MayaQWidgetDockableMixin, Dialog):
					def __init__(self, node=None, *args, **kwargs):
						super(arkDialog, self).__init__(parent=parent)

					# deletes everything with the name newName
					def deleteInstances(self, newName):
						mayaMainWindowPtr = OpenMayaUI.MQtUtil.mainWindow()
						mayaMainWindow = wrapInstance(long(mayaMainWindowPtr), QtGui.QMainWindow) # Important that it's QMainWindow, and not QWidget/QDialog

						for obj in mayaMainWindow.children():
							if type(obj) == MayaQDockWidget:
								if obj.widget().objectName() == newName: # Compare object names
									# If they share the same name then remove it
									mayaMainWindow.removeDockWidget(obj) # This will remove from right-click menu, but won't actually delete it! ( still under mainWindow.children() )
									# Delete it for good
									obj.setParent(None)
									obj.deleteLater()

				self.ex = arkDialog()
				self.ex.setDockableParameters(dockable=True, area='right', floating=False)

		else:
			if os.getenv('ARKTOOLBAR_UNDOCKED'):
				undocked = Dialog(parent= None, *args, **kwargs)
			else:
				mayaApp = self.getQTApp()
				undocked = Dialog(parent= mayaApp, *args, **kwargs)
			undocked.show()
			undocked.raise_()
			return undocked

	# Application specific
	########################################
