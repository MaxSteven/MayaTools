# Standard modules
# import sys
import json
import os
# from datetime import date
import re

# Vendor modules
import hou
import toolutils
import pyqt_houdini
from qt import QtGui

from PIL import Image

# Our modules
import Translator
import arkInit
arkInit.init()

import Node_Houdini
import SerialNode_Houdini
import pathManager
import cOS
import arkUtil
import settingsManager
globalSettings = settingsManager.globalSettings()

class Houdini(Translator.Translator):
	nodeClass = Node_Houdini.Node_Houdini
	serialNodeClass = SerialNode_Houdini.SerialNode_Houdini
	fileExtension = 'hip'
	program = 'houdini'
	environmentFormatString = '$%s'

	def __init__(self):
		super(Houdini, self).__init__()
		self.setOptions(
			canUse=True,
			canPublishShots=True,
			renderNodeType=[
				'ropgeometry',
				'ropalembic',
				'filecache',
				'ifd',
				'geometry',
				'alembic',
				'vrayrenderer',
				'ropvrayproxy',
				'wedge'
			],
			renderNodeCategory = 'rop',
			vRayRenderPresets=None,
			cameraType='camera',
			exportTypes=['Geometry', 'Camera'],
			hasFrames=True,
			hasPasses=False,
			hasDeep=True,
			hasKeyCommands=False,
			closeOnSubmit=False,
			singleArkInit=True,
			hasChunks=False,
			jobTypes=[
				'Houdini_Mantra',
				'Houdini_Cache',
				'Houdini_VRay',
				'Houdini_Cache_VRayMesh',
				'Houdini_Cache_Wedge',
				'Houdini_Cache_Alembic',
			],
			alembicImportOptions=['Alembic Archive', 'Alembic Geometry'],
			displayOptions=['Shaded', 'Wireframe on Shaded', 'Textured'],
			appHandlesSubmit=False,
			renderPresetOrder=['Progressive', 'Fast', 'Decent', 'Full', 'Final (Existing)'])

		# used in preSubmit and postSubmit to repath $HIP to full path
		self.nodeReplaceList= {}

	# Basics
	##################################################
	# Inherited

	# Data Storage
	##################################################
	def getSceneData(self, key=None):
		rawData = hou.node('/obj').userData('label')
		# if no sceneData yet, create empty dict
		if not rawData:
			hou.node('/obj').setUserData('label', '')
			return {}
		try:
			data = arkUtil.parseJSON(rawData, ignoreErrors=True)
		except Exception as err:
			raise err
		if not key:
			return data
		else:
			return data.get(key)

	def setSceneData(self, key, val=None):
		data = self.getSceneData()
		if val is None:
			if isinstance(key, dict):
				data = key
			else:
				data[key] = key
		else:
			data[key] = val
		obj = hou.node('/obj')
		obj.setUserData('label', json.dumps(data))

	def removeSceneData(self, key):
		data = self.getSceneData()
		if key in data:
			del data[key]
		self.setSceneData(data)

	# Files
	##################################################
	def getFilename(self):
		'''
		Get the current open filename
		'''
		path = hou.hipFile.path()
		# For compatibility with Shepherd Submit
		if 'untitled' in path:
			path = ''
		return pathManager.translatePath(path)

	def saveFile(self, filename=None, force=False):
		'''
		Save the current open file, optionally specifying
		a name to save the file as
		'''
		if not filename:
			filename = self.getFilename()
		hou.hipFile.save(filename)

	def openFile(self, filename, force=False):
		'''
		Open the specified filename
		'''
		hou.hipFile.load(filename, suppress_save_prompt=force, ignore_load_warnings=force)

	def newFile(self, force=False):
		'''
		Open new file. Force=True continues without saving current open file
		'''
		hou.hipFile.clear(suppress_save_prompt=force)

	def exit(self, force=False):
		'''
		Exit the program
		'''
		hou.exit(suppress_save_prompt=force)

	def checkSaveState(self, useHash=False):
		return hou.hipFile.hasUnsavedChanges()

	# Nodes
	##################################################
	def getAllNodes(self, recurse=False):
		# Get list of all node types
		allNodes = list(hou.node('/').allSubChildren())
		return self.ensureNodes(allNodes)

	def getNodeByName(self, name):
		allNodes = self.getAllNodes()
		validNodes = []
		for node in allNodes:
			if (name.lower() == node.name().lower()):
				validNodes.append(node)
		# Naming in Houdini is unique
		# TODO: this might not necessarily be true, in different directories
		# Ex: maybe no two of pCone1 in /obj, but pCone1 can contain a pCone1 node
		if len(validNodes) > 1:
			raise Exception('More than one node with matching name found')
		# None found
		if not validNodes:
			return None
		return self.ensureNode(validNodes[0])

	# Bit of a hack. You can't determine if a node is a RopNode simply by type,
	# as type varies. If category is 'rop', assume you are looking for render nodes
	# and use Class instead for comparison
	def getNodesByCategory(self, nodeCategory):
		if nodeCategory.lower() == 'rop':
			# hax for vray nodes which aren't hou.ropNode class
			nodes = self.getNodesByClass(hou.RopNode) + \
				self.getNodesByType('vrayrenderer') + \
				self.getNodesByType('ropvrayproxy') + \
				self.getNodesByType('filecache')

			nodes = [n for n in nodes if not n.nativeNode().isInsideLockedHDA()]

			return nodes

		allNodes = self.getAllNodes()
		validNodes = [n for n in allNodes if n.getCategory().lower() == nodeCategory.lower()]

		return self.ensureNodes(validNodes)

	def getNodeByPath(self, path):
		node = hou.node(str(path))
		if not node:
			print 'Node at path %s not found' % path
			return None

		return self.ensureNode(node)

	def getSoftwareVersion(self):
		return '.'.join([str(ver) for ver in hou.applicationVersion()])

	# Deselect all nodes and select this one
	def selectNode(self, node):
		node = self.ensureNative(node)
		node.setSelected(on=True, clear_all_selected=True)

	# Repeating selectNode call, but can't call
	# clear selection before adding each node
	def selectNodes(self, nodes):
		self.clearSelection()
		nodes = self.ensureNatives(nodes)
		for node in nodes:
			node.setSelected(on=True, clear_all_selected=False)

	def deselectNodes(self, nodes):
		nodes = self.ensureNatives(nodes)
		for node in nodes:
			node.setSelected(on=False, clear_all_selected=False)

	def getSelectedNodes(self, recurse=False):
		selected = list(hou.selectedNodes())
		return self.ensureNodes(selected)

	# if ignoreErrors=True, pass any nodes that error on delete
	# will error on delete if already deleted (hou.ObjectWasDeleted)
	def removeNodes(self, nodes, ignoreErrors=True):
		nodes = self.ensureNatives(nodes)
		if ignoreErrors:
			for node in nodes:
				try:
					node.destroy()
				except:
					pass
		else:
			for node in nodes:
				node.destroy()

	def localizeNodes(self, nodes=[]):
		return True

		excludeNodeChannels = {
			'ropgeometry': 'sopoutput', 					# cache bgeo
			'ropalembic': 'filename', 						# cache alembic
			'geometry': 'sopoutput', 						# cache wedge
			'vrayrenderer': 'SettingsOutput_img_file', 		# vray render
			'ropvrayproxy': 'filepath', 					# cache Vray Proxy
			'ifd': 'vm_picture' 							# mantra render
		}
		localizeRoot = os.environ.get('ARK_CACHE')
		if not localizeRoot:
			return False

		# get all roots for current OS
		for root in pathManager.getAllDriveRoots():
			root = root.strip('/')
			root = root.strip('\\')
			if not len(nodes):

				# get all the nodes which contain root in any of their channels
				nodeList = hou.hscript('opfind ' + root)[0].split('\n')
				nodeList += hou.hscript('opfind ' + root.upper())[0].split('\n')
				nodePaths = [node.strip() for node in nodeList]

			else:
				nodePaths = [node.name(fullpath=True) for node in nodes]

			for fileNode in nodePaths:
				if fileNode == '':
					continue

				# get all the nodes which contain root in any of their channels
				if hou.node(fileNode).isInsideLockedHDA():
					continue

				# get all channels of nodes which contain the root
				channelStrings = hou.hscript('chls -a ' + fileNode)[0].split(' ')[1:]
				channels = [channel.strip() for channel in channelStrings]

				# if channel is in the exclude list, remove them from localization
				if self.getNodeByPath(fileNode).getType() in excludeNodeChannels.keys():
					badChannel = excludeNodeChannels[self.getNodeByPath(fileNode).getType()]
					print 'not localizing channel: ' + badChannel + ' from node: ' + str(fileNode)
					channels.remove(badChannel)

				# get values from every channel of that node
				for channel in channels:
					# some evals are breaky that's why in try block
					try:
						if not hou.node(fileNode).parm(channel).isDisabled():
							# This is just a test to weed out non-string parms
							path = hou.node(fileNode).parm(channel).unexpandedString()
							path = hou.node(fileNode).parm(channel).eval()
						else:
							path = None

					except:
						path = None

					# if the root exists in path then localize it
					if root in str(path) or root.upper() in str(path):
						path = cOS.normalizeFramePadding(path)
						newPath = self.localizeFiles(path, localizeRoot)
						if newPath:
							newPath = cOS.normalizeFramePadding(newPath)

							# exception case for %d
							if '.%d.' in newPath:
								newPath = newPath.replace('%d', '$F')

							# this will work for both:
							# files with frame padding and without frame padding
							# as files with padding shall be replaced and
							# no operation will happen on files without any frame padding
							else:
								padding = cOS.getPadding(newPath)
								newPath = newPath.replace('%0' + str(padding) + 'd', '$F' + str(padding))

							hou.node(fileNode).parm(channel).set(newPath)
		return True

	def delocalizeNodes(self, nodes=[]):
		excludeNodeChannels = {
			'ropgeometry': 'sopoutput', 					# cache bgeo
			'ropalembic': 'filename', 						# cache alembic
			'geometry': 'sopoutput', 						# cache wedge
			'vrayrenderer': 'SettingsOutput_img_file', 		# vray render
			'ropvrayproxy': 'filepath', 					# cache vray proxy
			'ifd': 'vm_picture' 							# mantra render
		}

		localizeRoot = os.environ.get('ARK_CACHE')
		if not localizeRoot:
			return False

		if not len(nodes):

			# get all the nodes which contain localCache path in any of their channels
			nodeList = hou.hscript('opfind ' + localizeRoot.lower()[:-1])[0].split('\n')
			nodeList += hou.hscript('opfind ' + localizeRoot.upper()[:-1])[0].split('\n')
			nodePaths = [node.strip() for node in nodeList]

		else:
			nodePaths = [node.name(fullpath=True) for node in nodes]

		for fileNode in nodePaths:
			if fileNode == '':
				continue

			# don't touch node if inside locked HDA
			if hou.node(fileNode).isInsideLockedHDA():
				continue

			# get all channels of nodes which contain the localCache
			channelStrings = hou.hscript('chls -a ' + fileNode)[0].split(' ')[1:]
			channels = [channel.strip() for channel in channelStrings]

			# if channel is in the exclude list, remove them from localization
			if self.getNodeByPath(fileNode).getType() in excludeNodeChannels.keys():
				badChannel = excludeNodeChannels[self.getNodeByPath(fileNode).getType()]
				channels.remove(badChannel)

			# get values from every channel of that node
			for channel in channels:
				# some evals are breaky that's why in try block
				try:
					if not hou.node(fileNode).parm(channel).isDisabled():
						# This is just a test to weed out non-string parms
						path = hou.node(fileNode).parm(channel).unexpandedString()
						path = hou.node(fileNode).parm(channel).eval()
					else:
						path = None

				except:
					path = None

				if not path:
					continue

				# if the path contains any of the linux roots in it, globalize it
				roots = pathManager.getAllDriveRoots(osName = 'linux')
				for root in roots:
					if root[:-1] in path or root[:-1].upper() in path:
						newPath = pathManager.globalizePath(path)

						newPath = cOS.normalizeFramePadding(newPath)

						if '%d' in newPath:
							newPath = newPath.replace('%d', '$F')

						else:
							padding = cOS.getPadding(newPath)
							newPath = newPath.replace('%0' + str(padding) + 'd', '$F' + str(padding))

						hou.node(fileNode).parm(channel).set(newPath)

		return True

	def relocalizeNodes(self, nodes=[]):
		return True

		excludeNodeChannels = {
			'ropgeometry': 'sopoutput', 					# cache bgeo
			'ropalembic': 'filename', 						# cache alembic
			'geometry': 'sopoutput', 						# cache wedge
			'vrayrenderer': 'SettingsOutput_img_file', 		# vray render
			'ropvrayproxy': 'filepath', 					# cache Vray Proxy
			'ifd': 'vm_picture' 							# mantra render
		}
		localizeRoot = os.environ.get('ARK_CACHE')
		if not localizeRoot:
			return False

		nodePaths = []
		# get all roots for both OSes
		allRoots = pathManager.getAllDriveRoots(osName='linux') + pathManager.getAllDriveRoots(osName='windows')
		for root in allRoots:
			if not len(nodes):
				root = root.strip('/')
				root = root.strip('\\')
				nodeList = hou.hscript('opfind ' + root)[0].split('\n')
				nodeList += hou.hscript('opfind ' + root.upper())[0].split('\n')
				nodePaths += [node.strip() for node in nodeList]

			else:
				nodePaths = [node.name(fullpath=True) for node in nodes]

		for fileNode in nodePaths:
			if fileNode == '':
				continue


			if hou.node(fileNode).isInsideLockedHDA():
				continue

			# get all the nodes which contain root in any of their channels
			channelStrings = hou.hscript('chls -a ' + fileNode)[0].split(' ')[1:]
			channels = [channel.strip() for channel in channelStrings]

			# if channel is in the exclude list, remove them from localization
			if self.getNodeByPath(fileNode).getType() in excludeNodeChannels.keys():
				badChannel = excludeNodeChannels[self.getNodeByPath(fileNode).getType()]
				channels.remove(badChannel)

			# get values from every channel of that node
			for channel in channels:
				# some evals are breaky that's why in try block
				try:
					if not hou.node(fileNode).parm(channel).isDisabled():
						# This is just a test to weed out non-string parms
						path = hou.node(fileNode).parm(channel).unexpandedString()
						path = hou.node(fileNode).parm(channel).eval()
					else:
						path = None

				except:
					path = None

				if not path:
					continue

				# if the path contains any of the roots in it, relocalize it based on current localCache
 				roots = pathManager.getAllDriveRoots(osName = 'windows') + pathManager.getAllDriveRoots(osName = 'linux')
				for root in roots:
					if root[:-1] in path or root[:-1].upper() in path:
						newPath = pathManager.localizePath(path)

						if cOS.isValidSequence(newPath):
							newPath = cOS.getFirstFileFromFrameRangeText(newPath)

						if not newPath or not os.path.isfile(str(newPath)):
							newPath = pathManager.globalizePath(path)

						newPath = cOS.normalizeFramePadding(newPath)

						if '%d' in newPath:
							newPath = newPath.replace('%d', '$F')

						else:
							padding = cOS.getPadding(newPath)
							newPath = newPath.replace('%0' + str(padding) + 'd', '$F' + str(padding))

						hou.node(fileNode).parm(channel).set(newPath)

		return True

	# TODO: implement as Reference Copy in Houdini
	# Unclear where this call is in hou docs
	def createInstance(self, node):
		raise Exception('Not implemented yet')

	# TODO: implement createPrimitive
	def createPrimitive(self, primitiveType):
		raise Exception('Not implemented')

	# Rendering
	##################################################
	def getRenderProperty(self, prop):
		'''
		Get a variety of render properties:
		- width: render width
		- height: render height
		'''
		# Use render node  if it exists
		if self.getRenderNode():
			renderNode = self.ensureNode(self.getRenderNode())
		else:
			renderNode = None

		if renderNode:
			propName = False
			if renderNode.hasProperty('camera'):
				propName = 'camera'
			elif renderNode.hasProperty('render_camera'):
				propName = 'render_camera'

			if propName:
				cam = self.ensureNative(renderNode).parm(propName).eval()
				camera = self.getNodeByPath(str(cam))
				if not camera:
					raise Exception('Node {} not found'.format(str(cam)))

				if prop == 'width':
					return camera.getProperty('resx')
					# return hou.node(camera).parm('resx').eval()
				elif prop == 'height':
					return camera.getProperty('resy')
					# return hou.node(camera).parm('resy').eval()
				elif prop == 'nearPlane':
					return camera.getProperty('near')
				elif prop == 'farPlane':
					return camera.getProperty('far')
				else:
					raise Exception('Property not implemented: ' + prop)
			# if no camera, a cache, so no width/height/nearPlane/farPlane
			else:
				if prop in ['width','height','nearPlane','farPlane']:
					return None
				else:
					raise Exception('Property not implemented: ' + prop)
		else:
			print ('RenderNode not set. Cannot fetch property' + prop)
			return None

	def getRenderProperties(self):
		renderProperties = super(Houdini, self).getRenderProperties()
		# render node path must be absolute
		# If render node set already
		if self.getRenderNode():
			renderProperties['node'] = self.getRenderNode().getPath()
			print 'Using render node:', renderProperties['node']
		else:
			print 'Render node not set.\n'

		return renderProperties

	def setRenderProperty(self, prop, val):
		'''
		Set a variety of render properties:
		- width: render width
		- height: render height
		'''
		try:
			renderNode = self.ensureNode(self.getRenderNode())
		except:
			renderNode = None
		if renderNode:
			if renderNode.hasProperty('camera'):
				camera = self.ensureNative(renderNode).parm('camera').eval()
				camera = self.getNodeByPath(str(camera))
				val = arkUtil.ensureNumber(val)
				if prop == 'width':
					camera.setProperty('resx', val)
				elif prop == 'height':
					camera.setProperty('resy', val)
				else:
					raise Exception('Property not implemented: ' + prop)
			else:
				raise Exception('RenderNode has no camera (may be Cache file), nothing to set.')
		else:
			raise Exception('No RenderNode set. Cannot set property ' + prop)

	def replaceHIP(self, path):
		hipPath = cOS.getDirName(self.getFilename())
		return path.replace('$HIP', hipPath)


	def replaceHIPEnvs(self, path):
		if not path:
			return
		pathInfo = cOS.getPathInfo(path)
		hou.hscript('setenv HIP = ' + pathInfo['dirname'])
		hou.hscript('setenv HIPNAME = ' + pathInfo['name'].split('.')[0])
		hou.hscript('setenv HIPFILE = ' + path)

	def getOutputFilename(self, path, jobData):
		def normalizePath(path):
			newPath = cOS.normalizeFramePadding(path)
			newPath = pathManager.translatePath(newPath)
			return newPath

		if jobData['jobType'] == 'Houdini_Cache':
			ropNode = self.getNodeByPath(jobData['node'])
			try:
				if ropNode.getType() == 'ropgeometry':
					path = ropNode.getProperty('sopoutput')

				elif ropNode.getType() == 'filecache':
					path = ropNode.getProperty('file')

				return normalizePath(path)
			except:
				return False

		elif jobData['jobType'] == 'Houdini_Cache_Alembic':
			ropNode = self.getNodeByPath(jobData['node'])
			try:
				path = ropNode.getProperty('filename')
				return normalizePath(path)
			except:
				return False

		elif jobData['jobType'] == 'Houdini_Cache_VRayMesh':
			ropNode = self.getNodeByPath(jobData['node'])
			try:
				path = ropNode.getProperty('filepath')
				return normalizePath(path)
			except:
				return False
		elif jobData['jobType'] == 'Houdini_Cache_Wedge':
			# get the wedge node
			wedgeNode = self.getNodeByPath(jobData['node'])
			if wedgeNode.getType() != 'wedge':
				print 'Wedge node not selected.'
				return False
			exportNode = self.getNodeByPath(wedgeNode.getProperty('driver'))
			if not exportNode:
				print 'Export node could not be found'
				return False

			# get the channel we're varying and ensure it exists, along w/ it's parm
			channel = wedgeNode.getProperty('chan1')
			channelNodePath = '/'.join(channel.split('/')[:-1])
			channelNode = self.getNodeByPath(channelNodePath)
			if not channelNode:
				print 'The node specified in channel does not exist:', channelNodePath
				return False
			propName = channel.split('/')[-1]
			propertyExists = channelNode.hasProperty(propName)
			if not propertyExists:
				print 'The parameter for the specified channel node does not exist:', channelNodePath
				return False

			# get the output path from the export node
			# path = exportNode.getProperty('sopoutput')
			path = exportNode.nativeNode().parm('sopoutput').unexpandedString()
			return normalizePath(path)
		else:
			path = arkUtil.removeTrailingSlash(path)
			path = path + ('/renders/v%04d/' % jobData['version']) + \
						jobData['name'] + '.%04d.exr'
			return pathManager.translatePath(path)

	def setOutputFilename(self, filename, jobData):
		padding = cOS.getPadding(filename)
		filename = filename.replace('%0' + str(padding) + 'd','$F' + str(padding))

		ropNode = self.getNodeByPath(jobData['node'])

		if jobData['jobType'] == 'Houdini_Cache':
			if ropNode.getType() == 'ropgeometry':
				ropNode.setProperty('sopoutput', filename)
			elif ropNode.getType() == 'filecache':
				ropNode.setProperty('file', filename)

		elif jobData['jobType'] == 'Houdini_Cache_Alembic':
			ropNode.setProperty('filename', filename)

		elif jobData['jobType'] == 'Houdini_Mantra':
			ropNode.setProperty('vm_picture', filename)
			# IFD generation
			ropNode.setProperty('soho_outputmode', True)
			if ropNode.hasProperty('vm_inlinestorage'):
				ropNode.setProperty('vm_inlinestorage', True)
			ropNode.setProperty('soho_diskfile', filename.replace('.$F4.exr','.$F4.ifd.sc'))

			if jobData.get('deep'):
				ropNode.setProperty('vm_picture', filename)
				ropNode.setProperty('vm_deepresolver', 'camera')
				deepFilename = filename.replace('.$F4.exr','_deep.$F4.exr')
				ropNode.setProperty('vm_dcmfilename', deepFilename)

	def getRenderRange(self):
		# Use render node
		renderNode = self.getRenderNode()
		if renderNode:
			renderNode = self.ensureNode(self.getRenderNode())

		if renderNode:
			# wedge "frames" are the number of individual wedges to run
			# the actual frame range of the cache is stored in options as
			# additional json data
			if renderNode.getType() == 'wedge':
				return {
					'startFrame': 0,
					'endFrame': int(renderNode.getProperty('steps1')) - 1,
				}
			else:
				return {
					'startFrame': int(renderNode.getProperty('f1')),
					'endFrame': int(renderNode.getProperty('f2')),
				}
		else:
			print ('RenderNode not set. Cannot get Render Range')
			return None

	def setRenderRange(self, start, end):
		# Use render node
		try:
			renderNode = self.ensureNode(self.getRenderNode())
		except:
			renderNode = None
		if renderNode:
			# Clear out channels for f1, f2 (by default reference playback range)
			self.ensureNative(renderNode).parm('f1').deleteAllKeyframes()
			self.ensureNative(renderNode).parm('f2').deleteAllKeyframes()
			# Make sure renderNode set to render Frame Range
			renderNode.setProperty('trange', True)
			# Set start/end
			start = arkUtil.ensureNumber(start)
			end = arkUtil.ensureNumber(end)
			renderNode.setProperty('f1', start)
			renderNode.setProperty('f2', end)
		else:
			raise Exception('RenderNode not set. Cannot set Render Range')

	def preSubmit(self, jobData):
		hou.setSessionModuleSource('')
		hipPath = os.path.dirname(hou.hipFile.path())
		hipPath = re.sub(r'[\\/]+', '/', hipPath)

		for node in hou.node('/').allSubChildren():
			for parm in node.parms():
				try:
					val = str(parm.unexpandedString())
					if '$HIP' in val:
						print 'replacing $HIP:', val
						parm.set(val.replace('$HIP', hipPath))
						self.nodeReplaceList[node]= hipPath
				except:
					pass

		renderNode = self.getRenderNode()

		if jobData['jobType'] == 'Houdini_Mantra':
			renderNode.setProperty('vm_verbose', 3)
			renderNode.setProperty('vm_alfprogress', True)
			renderNode.setProperty('vm_cacheratio', .75)
			renderNode.setProperty('declare_all_shops', 2)
		# wedge jobs get cache start and end
		elif jobData['jobType'] == 'Houdini_Cache_Wedge':
			wedgeNode = self.getNodeByPath(jobData['node'])
			cacheNode = self.getNodeByPath(wedgeNode.getProperty('driver'))
			options = {
				'startFrame': cacheNode.getProperty('f1'),
				'endFrame': cacheNode.getProperty('f2'),
				'propStart': wedgeNode.getProperty('range1x'),
				'propEnd': wedgeNode.getProperty('range1y'),
				'steps': wedgeNode.getProperty('steps1'),
				'wedge': wedgeNode.getProperty('prefix') + '_' + \
					wedgeNode.getProperty('name1') + '_%.6f'
			}
			jobData['options'] = json.dumps(options)

		super(Houdini, self).preSubmit(jobData)
		return jobData

	def createPlayblast(self, playblastOptions):
		self.setAnimationFrame(playblastOptions['endTime'])
		currentCam = None
		width, height = playblastOptions['size']
		if playblastOptions['camera']:
			currentCam = self.getCamFromView()
			self.setCamView(self.getNodeByName(playblastOptions['camera']))

		desktop = hou.ui.curDesktop().name()

		if playblastOptions['background']:
			outputPath = playblastOptions['inPath'] + '.$F4.jpg'
		else:
			outputPath = playblastOptions['inPath'] + '.$F4.png'

		cOS.makeDir(outputPath.rpartition('/')[0])

		playblastOptions['fps'] = self.getFPS()

		playblastCommand = [
				'viewwrite',
				'-f', str(playblastOptions['startTime']) + ' ' + str(playblastOptions['endTime']),
				'-i 1',
				'-g 2.2',
				'-c',
				'-r ' + str(width) + ' ' + str(height),
				'-q 3',
				'-b ""',
				'-v "*"',
				'-m 1 1 0.500000',
				desktop +'.' + self.getPanel('SceneViewer')[0] + '.world.persp1',
				"'%s'" % outputPath
				]
		# viewwrite -a '' -o 1 0.000000 -f $RFSTART $RFEND -i 1 -g 2.2 -r 1920 1080 -c -q 3 -b '0'  -v '*' -m 1 1 0.500000 Technical.panetab2.world.persp1 'C:/temp/path/Test.$F4.png'

		playblastCommand = ' '.join(playblastCommand)
		print playblastCommand
		try:
			hou.hscript(playblastCommand)
		except:
			return False

		playblastOptions['inPath'] = outputPath.replace('$F4', '%04d')
		result = super(Houdini, self).createPlayblast(playblastOptions)
		return result

	# TODO: copied from Houdini_Old.py, verify works
	def postSubmit(self, jobData):
		for node, hipPath in self.nodeReplaceList.items():
			for parm in node.parms():
				try:
					val = str(parm.unexpandedString())
					if hipPath in val:
						print 'replacing {}:'.format( hipPath), val
						parm.set(val.replace(hipPath, '$HIP'))
				except:
					pass

	def setRenderable(self, nodes, value=True):
		nodes = self.ensureNodes(nodes)
		# not all nodeTypes have setRenderFlag function
		for node in nodes:
			try:
				self.ensureNative(node).setRenderFlag(value)
			except:
				continue

	def connectProperty(self, fromNode, fromNodeProperty, toNode, toNodeProperty):
		outIndex = fromNode.nativeNode().outputIndex(fromNodeProperty)
		inIndex = toNode.nativeNode().inputIndex(toNodeProperty)
		toNode.nativeNode().setInput(inIndex, fromNode.nativeNode(), outIndex)

	# Animation
	##################################################
	def getFPS(self):
		return hou.fps()

	def setFPS(self, fps):
		fps = arkUtil.ensureNumber(fps)
		hou.setFps(fps)

	def getAnimationRange(self):
		playbackRange = hou.playbar.playbackRange()
		start = playbackRange[0]
		end = playbackRange[1]
		return {
			'startFrame': int(start),
			'endFrame': int(end),
		}

	def setAnimationRange(self, start, end):
		start = arkUtil.ensureNumber(start)
		end = arkUtil.ensureNumber(end)
		hou.playbar.setPlaybackRange(start, end)

	def getAnimationFrame(self):
		return hou.frame()

	def setAnimationFrame(self, frame):
		hou.setFrame(arkUtil.ensureNumber(frame))

	# TODO: implement load/removeAnimation
	def loadAnimation(self, nodes, animation):
		raise Exception('Not implemented')

	def removeAnimation(self, nodes, frame):
		raise Exception('Not implemented')

	def setCamView(self, camNode, frame=None):
		viewer = toolutils.sceneViewer()
		current = viewer.curViewport()
		if not camNode:
			return

		current.setCamera(camNode.nativeNode())
		if frame != None:
			self.setAnimationFrame(frame)


	def getCamFromView(self):
		viewer = toolutils.sceneViewer()
		current = viewer.curViewport()
		if not current.camera():
			return

		return self.getNodeByName(current.camera().name())

	# Visibility
	##################################################

	# Isolate nodes not really a thing in Houdini
	def isolateNodes(self, nodes):
		raise Exception('Not Implemented')

	# Isolate nodes not really a thing in Houdini
	def unisolateNodes(self, nodes):
		raise Exception('Not Implemented')

	def showNodes(self, nodes):
		nodes = self.ensureNatives(nodes)
		for node in nodes:
			try:
				node.setDisplayFlag(True)
			except:
				continue

	def hideNodes(self, nodes):
		nodes = self.ensureNatives(nodes)
		for node in nodes:
			try:
				node.setDisplayFlag(False)
			except:
				continue

	# Toggling visibility in viewport (displayFlag)
	def getHiddenNodes(self):
		allNodes = self.getAllNodes()
		allNodes = self.ensureNatives(allNodes)
		hidden = []
		for node in allNodes:
			if not node.isDisplayFlagSet():
				hidden.append(node)
		return self.ensureNodes(hidden)

	def getVisibleNodes(self):
		allNodes = self.getAllnodes()
		allNodes = self.ensureNatives(allNodes)
		visible = []
		for node in allNodes:
			if node.isDisplayFlagSet():
				visible.append(node)
		return self.ensureNodes(visible)

	# Locks
	##################################################
	def setNodeTransformLock(self, objectName=None, useSelected=False, value=True):
		# Lock translation, rotation, scale
		transformList = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']
		if useSelected:
			allNodes = self.getSelectedNodes()
			for node in allNodes:
				for item in transformList:
					if node.hasProperty(item):
						parm = self.ensureNative(node).parm(item)
						parm.lock(value)
					else:
						continue
		else:
			objectName = self.getNodeByName(objectName)
			for item in transformList:
				if objectName.hasProperty(item):
					parm = self.ensureNative(objectName).parm(item)
					parm.lock(value)
				else:
					continue

	def setNodeSelectionLock(self, objectName=None, useSelected=False, value=True):
		if useSelected:
			selected = self.getSelectedNodes()
			for node in selected:
				if (node.getCategory() == 'object'):
					self.ensureNative(node).setSelectableInViewport(not value)
				else:
					continue
		elif objectName:
			objectName = self.getNodeByName(objectName)
			if (objectName.getCategory() == 'object'):
				self.ensureNative(objectName).setSelectableInViewport(not value)
			else:
				pass
		else:
			raise Exception('Invalid arguments')

	# IO
	##################################################
	# Returns list of new nodes
	# TODO: options for type of import method
	def importAlembicGeometry(self, filename, method='Alembic Geometry', inContext=False):
		if not filename.endswith('.abc'):
			raise Exception ('Filename not Alembic .abc file')
		name = cOS.getPathInfo(filename)['name']
		pre = self.getAllNodes()
		obj = hou.node('/obj')
		if method == 'Alembic Archive':
			alembic = obj.createNode('alembicarchive')
			alembic.setName(name+'alembicArchive')
			alembic.setParms({'fileName': filename})
			alembic.parm('buildHierarchy').pressButton()

		elif method == 'Alembic Geometry':
			if not inContext:
				node = obj.createNode('geo')
				node.setName(name + '_geo')
				hou.Node.destroy(node.allSubChildren()[0])
			else:
				networkPanel = self.getPanel('NetworkEditor')[0]
				node = hou.ui.findPaneTab(networkPanel).pwd()

			alembic = node.createNode('alembic')
			alembic.setName(name+'_alembic')
			alembic.setParms({'fileName': filename})
			alembic.parm('reload').pressButton()
		else:
			raise Exception ('Invalid import method')

		post = self.getAllNodes()
		return self.newNodes(pre, post)

	# # Returns list of new nodes
	def importAlembicCamera(self, filename):
		diff = self.importAlembicGeometry(filename, method='Alembic Archive')
		# Check if camera node created
		hasCamera = False
		# Evaluate alembicArchive node to see if camera was imported
		children = self.ensureNative(diff[0]).allSubChildren()
		for child in children:
			if child.type().name().lower() == 'cam':
				hasCamera = True
		# Verify camera node
		if not hasCamera:
			raise Exception ('Camera not imported')
		return diff

	def importFBXGeometry(self, filename):
		if not filename.endswith('.fbx'):
			raise Exception ('Filename not FBX .fbx file')
		pre = self.getAllNodes()
		hou.hipFile.importFBX(filename, merge_into_scene=True)
		post = self.getAllNodes()
		return self.newNodes(pre, post)

	def importFBXCamera(self, filename):
		diff = self.importFBXGeometry(filename)
		hasCamera = False
		children = self.ensureNative(diff[0]).allSubChildren()
		for child in children:
			if child.type().name().lower() == 'cam':
				hasCamera = True
		if not hasCamera:
			raise Exception ('Camera not imported')
		return diff

	def importOBJGeometry(self, filename):
		if not filename.endswith('.obj'):
			raise Exception ('Filename not OBJ .obj file')
		pre = self.getAllNodes()
		# Make geo node
		obj = hou.node('/obj')
		geo = obj.createNode('geo')
		children = geo.children()
		# Get containing file node and set file path
		fileNode = None
		for child in children:
			if child.type().name() == 'file':
				fileNode = child
		if not fileNode:
			raise Exception ('file node not found')
		fileNode.setParms({'file':filename})
		post = self.getAllNodes()
		return self.newNodes(pre, post)

	# Supports 3 methods of import: materialEditor, imagePlane, referencePlane
	# imagePlane created for new cam by default
	def importImage(self, filename, method=None, importOptions=None):
		normalized = arkUtil.removeTrailingSlash(cOS.normalizePath(filename))
		name = cOS.getPathInfo(filename)['name']

		if method == 'materialEditor':
			# raise Exception('importImage for materialEditor not implemented yet')
			matnetNode = hou.node('/obj/material')
			if not matnetNode:
				matnetNode = hou.node('/obj').createNode('matnet')
				matnetNode.setName('material')

			texture = matnetNode.createNode('texture')
			texture.setName(name)
			texture.setParms({'map': normalized})

		elif method == 'imagePlane':
			if importOptions.get('Camera'):
				cam = self.getNodeByName(importOptions['Camera']).nativeNode()
				cam.setParms({'vm_bgenable': 1, 'stdswitcher31': 2, 'vm_background': filename})

		elif method == 'referencePlane':
			# works for Houdini 16 only
			im = Image.open('filename')
			width, height = im.size
			geomNode = hou.node('/obj').createNode('geo')
			geomNode.setName(name+'_reference')
			grid = geomNode.createNode('grid')
			grid.setName(name + '_grid')
			gridNode = grid.allSubChildren()[0]
			gridNode.setParms({'orient': 0, 'rows': 2, 'columns': 2, 'sizex': width / 100, 'sizey': height / 100})
			gridNode.setName(name)
			transform = grid.createNode('transform')
			transform.setName(name+'_transform')
			uvShader = grid.createNode('uvquickshade2')
			uvShader.setName(name+'_uvShader')
			uvShader.setFirstInput(transform)
			uvShader.setParms('texture', filename)

		else:
			raise Exception('importImage method not supported')

	# Supports 3 methods of import for imageSequences
	# Uses cOS getFrameRange to find all images in matching sequence
	# Requires filename in format '../image.%04d.png' etc,
	# with %04d or other type of specification included in strings
	def importImageSequence(self, filename, method=None, importOptions=None):
		# Generate sequence information
		normalized = arkUtil.removeTrailingSlash(cOS.normalizePath(filename))
		# Get name without sequence or extension
		info = cOS.getFrameRange(normalized)
		base = info['base'].rsplit('.', 1)[0]
		ext = info['extension']
		path = base + '.$F.' + ext
		self.importImage(path, method, importOptions)

	def createRenderProxy(self,
						filepath,
						renderOptions = {'scale': 1.0,
										'particleWidthMultiplier': 1.0,
										'hairWidthMultiplier': 1.0,
										'previewFaces': 5000,
										'geoToLoad': 'Preview'},
						renderEngine = 'Vray'):
		pass

	def createMaterialFromImages(self, texFile, matName = ''):
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

		if self.getNodeByName(matName+'_material'):
			vrayMaterial = self.getNodeByName(matName+'_material')

		else:
			if not hou.node('/obj/mats'):
				hou.node('/obj').createNode('matnet', node_name='mats')
			matsNode = hou.node('/obj/mats')

			hou.hda.installFile(globalSettings.ARK_ROOT + '/ark/programs/houdini/otls/ingenuity_substanceMaterial_0_1.hda')
			substanceNode = self.ensureNode(matsNode.createNode('substanceMaterial', node_name=matName + '_substanceShader'))

			substanceNode.setProperty('diffuse', diffuseFilePath)
			substanceNode.setProperty('ao_rough_metal_ior', metalFilePath)
			substanceNode.setProperty('normal_height', normalFilePath)

			vrayMaterial = substanceNode.name(fullpath=True)

		matDict = {
				'material' : vrayMaterial + '/material'
		}

		return matDict

	def createDisplacementFromMap(self, normalNode, matName = ''):
		pass

	def exportAlembic(self, filepath, frameRange, exportOptions=None):
		normalized = arkUtil.removeTrailingSlash(cOS.normalizePath(filepath))
		frameRanges = []
		if '-' in frameRange:
			frameRanges.extend(frameRange.split('-'))

		else:
			frameRanges.extend([frameRange, frameRange])

		if exportOptions['objects'] == []:
			raise Exception('No objects selected!')

		if len(exportOptions['objects']) > 1:
			raise Exception('Please select one object from sop')

		obj = exportOptions['objects'][0]
		node = self.getNodeByPath(obj).nativeNode()
		parent = node.parent()
		ropNode = parent.createNode('rop_alembic')

		ropNode.setParms({
			'trange': 1,
			'f1': frameRanges[0],
			'f2': frameRanges[1],
			'filename': normalized,
			'partition_mode': 1,
			'partition_attribute': 'materialName'
			})
		ropNode.setFirstInput(node)
		ropNode.render()
		hou.Node.destroy(ropNode)


	def addCommand2(self, toolbar, tool):
		if tool.get('software') is None or 'houdini' in tool.get('software'):
			toolbar.currentTools[tool.get('name').lower()] = tool

	# UI
	########################################

	def getPanel(self, panelName):
		panels = []
		for p in hou.ui.paneTabs():
			if panelName in str(p.type()):
				panels.append(p.name())
		return panels

	# PySide
	########################################


	# OLD getQTApp function!
	########################################
	# TODO: Copied over from Houdini_Old.py, verify works/up to date
	# def getQTApp(self):
	# 	app = QtGui.QApplication.instance()
	# 	if not app:
	# 		print 'No app instance found, creating'
	# 		app = QtGui.QApplication
	# 		pyqt_houdini.exec_(app)
	# 	return app

	########################################


	def getQTApp(self):
		app = hou.qt.mainWindow()
		return app
		# if not app:
		# 	print 'No app instance found, creating'
		# 	app = QtGui.QApplication
		# 	pyqt_houdini.exec_(app)
		# return app




	# def launch(self, Dialog, qApplication=None, *args, **kwargs):
	# 	app = self.getQTApp()
	# 	dialog = Dialog(app.activeWindow(), *args, **kwargs)
	# 	return dialog

	def launch(self, Dialog, parent=None, newWindow=None, docked = False, *args, **kwargs):
		# if parent is not None:

		# partially working, only takes effect after restarting Houdini
		if docked:
			# dialog = Dialog(QtGui.QApplication.activeWindow(), *args, **kwargs)
			# with open(globalSettings.HOUDINI_TOOLS_ROOT+'houdini16.0/toolbar/arkDockable.pypanel') as ppFile:
			# 	lines = ppFile.readlines()

			# lineText = ''.join(lines)

			# currentString = re.findall('name="[a-zA-Z]+"', lineText)[0]
			# currentTool = currentString.split('"')[1]

			# name = dialog.name.replace(' ', '')

			# name = name.replace('_', '')

			# moduleName = name.replace(name[0], name[0].lower(), 1)

			# if currentTool != moduleName:
			# 	with open(globalSettings.HOUDINI_TOOLS_ROOT+'houdini16.0/toolbar/arkDockable.pypanel', 'w') as ppFile:
			# 		for line in lines:
			# 			ppFile.write(line.replace(currentTool, moduleName))

			# os.system('chown -R ' + cOS.getOSUsername() + '/home/' + + cOS.getOSUsername() +)
			# cOS.copy(globalSettings.HOUDINI_TOOLS_ROOT+'houdini16.0/toolbar/arkDockable.pypanel',
			# 		globalSettings.USER_ROOT + 'houdini16.0/python_panels/default.pypanel')
			return

		# ex = Dialog(parent=hou.qt.mainWindow(), *args, **kwargs)
		# x = hou.qt.createWindow()
		# try:
		# 	x.setWindowTitle(' '.join(ex.name.split('_')))
		# except AttributeError:
		# 	pass
		# layout = QtGui.QVBoxLayout()
		# layout.addWidget(ex)
		# x.setLayout(layout)
		# x.show()

		# return ex

		houdiniApp = self.getQTApp()
		undocked = Dialog(parent= houdiniApp, *args, **kwargs)
		undocked.show()
		undocked.raise_()

		return undocked

	# Application specific
	########################################
	# Helper to ensureNative, as many of calls used in Translator
	# are called at the Node level in Houdini
	# To avoid having to wrap calls in the Node_Houdini.py level
	# ensureNode/ensureNodes handles if node is already a nodeClass object
	def ensureNative(self, node):
		node = self.ensureNode(node)
		nativeNode = node.nativeNode()
		return nativeNode

	def ensureNatives(self, nodes):
		nodes = self.ensureNodes(nodes)
		nativeNodes = [node.nativeNode() for node in nodes]
		return nativeNodes

	# Really only applicable to Houdini
	# If called by accident for a different program, just use type
	def getNodesByClass(self, nodeClass):
		allNodes = self.getAllNodes()
		allNodes = self.ensureNatives(allNodes)
		validNodes = [n for n in allNodes if isinstance(n, nodeClass)]
		return self.ensureNodes(validNodes)


# if __name__ == '__main__':
# 	getOutputFilename()

