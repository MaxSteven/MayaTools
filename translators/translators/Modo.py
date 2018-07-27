
import os
# import sys
import shutil

import arkInit
arkInit.init()

from translators import Translator

import caretaker
ct = caretaker.getCaretaker()

import lx

import settingsManager
globalSettings = settingsManager.globalSettings()
import arkModo
import pathManager
import cOS
import arkUtil
from datetime import date


class Modo(Translator):

	def __init__(self):
		super(Modo, self).__init__()
		self.settings.append(canUse=True,
			node='camera',
			hasFrames=True,
			hasPasses=True,
			hasDeep=False,
			hasKeyCommands=False,
			closeOnSubmit=False,
			jobTypes=['Modo_VRay', 'Modo_Standard'],
			singleArkInit=True,
			hasChunks=False,
			appHandlesSubmit=False)

		self.fileExtension = 'lxo'
		self.program = 'Modo'
		self.data = {}

	# Data Storage
	########################################

	def setData(self, key, val=None):
		self.data[key] = val

		# data = {}
		# if val is None:
		# 	if isinstance(key, dict):
		# 		data = dict(key)
		# 	else:
		# 		data[key] = key
		# else:
		# 	data[key] = val

		# for key, val in data.iteritems():
		# 	obj = hou.node('/obj')
		# 	obj.setUserData(str(self.keyDict[key]), val)

	def getData(self, key=None):
		if key:
			if key in self.data:
				return self.data[key]
			return ''
		return self.data

	def removeData(self, key):
		if key in self.data:
			del self.data[key]

	# Nodes
	########################################
	def getNodesByType(self, nodeType):
		nodeCount = lx.eval1('query sceneservice {0}.N ?'.format(nodeType))
		lx.out('Found ' + str(nodeCount) + ' nodes of type {0}'.format(nodeCount))
		nodeNames = []
		for n in range(nodeCount):
			nodeName = lx.eval1('query sceneservice {0}.name ? {1}'.format(nodeType, n))
			nodeNames.append(nodeName)

		return nodeNames

	# File Info
	########################################
	def getFilename(self):
		fileName = lx.eval1('query sceneservice scene.file ? current')
		if not fileName:
			return None

		fileName = cOS.unixPath(fileName)
		return pathManager.translatePath(fileName)

	def saveFile(self, fileName=None):
		if not fileName:
			fileName = self.getFilename()
		lx.eval('scene.saveAs "{0}" export:true'.format(fileName))

	def openFile(self, fileName):
		lx.eval1('scene.open "{0}"'.format(fileName))

	def getFileInfo(self):
		# fix: should call super.getFileInfo then only fill what it needs
		fileInfo = {}

		fileName = self.getFilename()
		if not fileName:
			return

		fileInfo['baseName'] = fileName.split('/')[-1].split('.')[0]
		# fileInfo['width'] = hou.node('/obj/ipr_camera').parm('resx').eval()
		# fileInfo['height'] = hou.node('/obj/ipr_camera').parm('resy').eval()
		# fileInfo['deviceAspectRatio'] = float(fileInfo['width']) / float(fileInfo['height'])
		fileInfo['fps'] = lx.eval1('time.fpsCustom ?')
		fileInfo['isStereo'] = False
		fileInfo['version'] = cOS.getVersion(fileName)

		fileInfo['pathInfo'] = ct.pathInfo(fileName)
		fileInfo['userInfo'] = ct.userInfo

		if 'project_info' in fileInfo['pathInfo'] and fileInfo['pathInfo']['project_info'] and fileInfo['pathInfo']['project_info']['short_name']:
			fileInfo['short_name'] = fileInfo['pathInfo']['project_info']['short_name']

		if (fileName):
			fileParts = fileName.split('/')
			print('filename:', fileName)
			if (len(fileParts) > 3 and fileParts[2].upper() == 'WORKSPACES'):
				fileInfo['shotName'] = fileParts[3]
			elif len(fileParts) > 3:
				fileInfo['shotName'] = fileParts[2] + '-' + fileParts[3]
			fileInfo['version'] = cOS.getVersion(fileName)

			fileInfo['version'] = arkUtil.pad(int(fileInfo['version']), 3)
			fileInfo['jobName'] = fileParts[1]

			fileInfo['jobRoot'] = globalSettings.SHARED_ROOT + fileInfo['jobName'] + '/'
			today = date.today()

			fileInfo['postingRoot'] = fileInfo['jobRoot'] + 'POSTINGS/' + str(today.year) + '_' + arkUtil.pad(today.month, 2) + '_' + arkUtil.pad(today.day, 2) + '/'

		fileInfo['startFrame'] =  lx.eval1('time.range scene in:?') * fileInfo['fps']
		fileInfo['endFrame'] = lx.eval1('time.range scene out:?') * fileInfo['fps']
		fileInfo['frameCount'] = fileInfo['endFrame'] - fileInfo['startFrame']

		return fileInfo

	# Rendering
	########################################
	def getDefaultJobName(self):
		self.getFilename().split('/')[-1][:-4]

	def copyFileToFarm(self):
		self.saveFile()
		fileName = self.getFilename()

		# keep generating new filenames til we find one that's not un use
		uniqueJobID = arkUtil.randomHash(24)
		while os.path.isfile(globalSettings.SHEPHERD_REPOSITORY + 'jobs/' + uniqueJobID + '.lxo'):
		  uniqueJobID = arkUtil.randomHash(24)

		farmFile = globalSettings.SHEPHERD_REPOSITORY + 'jobs/' + uniqueJobID + '.lxo'
		farmFile = farmFile.replace('\\','/')
		print 'Copy: {0} To: {1}'.format(fileName, farmFile)
		shutil.copyfile(fileName, globalSettings.SHEPHERD_REPOSITORY + 'jobs/' + uniqueJobID + '.lxo')
		return farmFile

	def preSubmit(self, jobData):
		# no camera clipping
		# cameraItem = arkModo.getNodesByName(jobData['cameraName'])
		# if len(cameraItem):
		# 	try:
		# 		arkModo.setChannelValue(cameraItem[0].uniqueName(), 'clipping', 'false')
		# 	except:
		# 		print 'Couldn\'t set clipping plane'
		self.saveFile()

	def submitJob(self, jobData=None):
		if not jobData:
			jobData = self.jobData
		if not jobData:
			return False

		from shepherd import submit
		print 'about to submit'
		return submit.submitJob(jobData)

	def preRender(self):
		#  always export full paths, not relative ones
		lx.eval('pref.select defaults/sceneexport set')
		lx.eval('pref.value export.absPath true')

		renderItem = arkModo.getRenderItem()

		# always use animated noise
		arkModo.setChannelValue(renderItem, 'animNoise', 'true')
		# no render region
		arkModo.setChannelValue(renderItem, 'region', 'false')

	# def preSubmit(self, jobData):
	# 	super(Modo, self).preSubmit(jobData)

	def getRenderProperties(self, node):
		# fix: should get fileinfo, fill in, then get rest
		fileInfo = self.getFileInfo()
		if not fileInfo:
			return {'startFrame': 0, 'endFrame': 100}

		properties = {
				'width': lx.eval1('render.res axis:0 res:?'),
				'height': lx.eval1('render.res axis:1 res:?'),
				'startFrame':  fileInfo['startFrame'],
				'endFrame': fileInfo['endFrame'],
				'program': 'lxo',
				}
		return properties

	def getOutputFilename(self, outputRoot, jobData):
		outputFile = outputRoot + ('renders/v%03d/' % jobData['version']) + \
			jobData['name'] + '_' + jobData['cameraName'] + '.%04d.exr'
		# fix: should make a generic "safe filename" function to wrap this in
		path = outputFile[:2] + outputFile[2:].replace(':','_').replace(' ','_')
		return pathManager.translatePath(path)

	def setOutputFilename(self, outputFile, jobData):
		pass

	# Pre's
	########################################
	# def preRender(self):
	# 	pass

	# def preSubmit(self, jobData):
	# 	self.saveFile()

	# def postSubmit(self, jobData):
	# 	pass

	# def renderSetup(self, jobData):
	# 	pass

	# PySide
	########################################
	def launch(self, Dialog, qApplication=None, parent=None, newWindow=None, *args, **kwargs):
		# This is where the magic happens!
		# The lx module is persistent so you can store stuff there
		# and access it in commands.
		lx._widget = Dialog
		lx._widgetOptions = kwargs

		# widgetWrapper creates whatever widget is set via lx._widget above
		# note we're using launchScript which allows for runtime blessing
		lx.eval('launchWidget')

		try:
			return lx._widgetInstance
		except:
			return None
