# Name: Playblast tool
# Author: Shobhit Khinvasara
# Date: 04/28/2017

import arkInit
arkInit.init()

import arkUtil

import os

import subprocess

currentApp =  os.environ.get('ARK_CURRENT_APP')

import cOS

import translators
translator = translators.getCurrent()

import baseWidget

import arkFTrack
pm = arkFTrack.getPM()

import settingsManager
globalSettings = settingsManager.globalSettings()

if currentApp == 'maya':
	import maya.cmds as cmds

from deadline import jobTypes

class PlayblastTool(baseWidget.BaseWidget):
	defaultOptions = {
			'title': 'Playblast Tool',
			'width': 600,
			'height': 200,

			'knobs': [
				{
					'name': 'Output path',
					'dataType': 'Directory',
				},
				{
					'name': 'Name',
					'dataType': 'Text',
				},
				{
					'name': 'Playblast Resolution',
					'dataType': 'Resolution',
				},
				{
					'name': 'Maintain Aspect Ratio',
					'dataType': 'checkbox',
					'value': True
				},
				{
					'name': 'Frame Range',
					'dataType': 'FrameRange',
				},
				{
					'name': 'Camera',
					'dataType': 'list',
					'options': ['Current View']
				},
				{
					'name': 'Show Background',
					'dataType': 'Checkbox',
					'value': True
				},
				{
					'name': 'Save PNG Sequence',
					'dataType': 'checkbox'
				},
				{
					'name': 'Enable Audio',
					'dataType': 'checkbox'
				},
				{
					'name': 'Open Playblast Folder',
					'dataType': 'PythonButton',
					'callback': 'openPlayblastFolder'
				},
				{
					'name': 'Open PNG Folder',
					'dataType': 'PythonButton',
					'callback': 'openPngFolder'
				},
				{
					'name': 'Open playbast',
					'dataType': 'PythonButton',
					'callback': 'openPlayblast'
				},
				{
					'name': 'Playblast',
					'dataType': 'PythonButton',
					'callback': 'playblast'
				},
				# {
				# 	'name': 'Render Turntable',
				# 	'dataType': 'PythonButton',
				# 	'callback': 'turntable'
				# }
			]
		}

	def init(self):
		self.currentTask = pm.getTask()
		self.currentShot = pm.getShot()
		self.currentProject = self.currentTask['project']

	def postShow(self):
		projectInfo = pm.getInfo(self.currentProject)
		self.outputPath = os.path.join(
			pm.getPath(self.currentShot),
			'playblast'
		)

		nodeType = translator.getOption('cameraType')
		nodes = translator.getNodesByType(nodeType)

		# remove default cams from camera options
		if translator.getOption('defaultCameras'):
			for cam in translator.getOption('defaultCameras'):
				for node in nodes:
					if cam == node.name():
						nodes.remove(node)

		self.getKnob('Camera').addItems([cam.name() for cam in nodes])

		frameRange = translator.getAnimationRange()
		self.getKnob('Frame Range').setValue(str(frameRange['startFrame']) + '-' + str(frameRange['endFrame']))

		# Defaults name to filename minus shotname
		shotName = self.currentShot['name'] + '_'
		basename = os.path.basename(translator.getFilename()).rsplit('.', 1)[0]
		newDefaultName = basename.replace(shotName, '', 1)

		self.getKnob('Name').setValue(newDefaultName)

		# get resolution from render settings
		renderSettings = translator.getRenderProperties()
		width = renderSettings['width']
		height = renderSettings['height']
		self.getKnob('Playblast Resolution').setValue({'width': width, 'height': height}, emit=False)

		self.getKnob('Output path').setValue(self.outputPath)

		self.originalResolution = self.getKnob('Playblast Resolution').getValue()
		self.previousResolution =  self.originalResolution

		# change resolution based on selected camera if houdini
		if currentApp == 'houdini':
			self.getKnob('Camera').on('changed', self.changeResolution)

		self.getKnob('Playblast Resolution').on('changed', self.maintainAspectRatio)
		self.getKnob('Maintain Aspect Ratio').on('changed', self.changeAspectRatio)

	def changeResolution(self, *args):
		cam = self.getKnob('Camera').getValue()
		camNode = translator.getNodeByName(cam)

		if camNode:
			width = camNode.getProperties()['resx']
			height = camNode.getProperties()['resy']

			self.getKnob('Playblast Resolution').setValue({'width': width, 'height': height})

	def maintainAspectRatio(self, *args):
		currentResolution = self.getKnob('Playblast Resolution').getValue()
		if self.getKnob('Maintain Aspect Ratio').getValue():
			if self.previousResolution['width'] != currentResolution['width']:
				newHeight = int(currentResolution['width'] * self.originalResolution['height'] / self.originalResolution['width'])
				self.getKnob('Playblast Resolution').setValue({'width': currentResolution['width'], 'height': newHeight}, emit=False)
				self.previousResolution = currentResolution
			elif self.previousResolution['height'] != currentResolution['height']:
				newWidth = int(currentResolution['height'] * self.originalResolution['width'] / self.originalResolution['height'])
				self.getKnob('Playblast Resolution').setValue({'width': newWidth, 'height': currentResolution['height']}, emit=False)
				self.previousResolution = currentResolution
		else:
			self.previousResolution = currentResolution

	def changeAspectRatio(self, *args):
		if self.getKnob('Maintain Aspect Ratio').getValue():
			self.originalResolution = self.getKnob('Playblast Resolution').getValue()

	def openPlayblastFolder(self):
		filepath, filename = self.getFileName()
		cOS.openFileBrowser(filepath)

	def openPngFolder(self):
		filepath, filename = self.getFileName()
		pngPath = cOS.join(self.getKnob('Output path').getValue(), filename)

		if os.path.isdir(pngPath):
			cOS.openFileBrowser(pngPath)
		else:
			self.openPlayblastFolder()

	def deletePngFolder(self):
		filepath, filename = self.getFileName()
		pngPath = cOS.join(self.getKnob('Output path').getValue(), filename)

		if os.path.isdir(pngPath):
			cOS.removeDir(pngPath)
		else:
			print 'Unable to find PNG folder'

	def turntable(self):
		if cmds.currentUnit( query=True, linear=True ) != 'cm':
			self.showMessage('Please make sure your units are in "cm"!')
			return

		fullPath = cmds.file(q=True, expandName=True)

		filePath = os.path.splitext(fullPath)[0] + '_turntableReference.mb'
		referenceFile = cmds.file(filePath, exportSelected=True, type='mayaBinary')
		referencePathName = os.path.splitext(referenceFile)[0].rstrip('_turntableReference')
		newTurntableFile = referencePathName + '_turntable.mb'

		params = [
				'mayapy',
				globalSettings.ARK_ROOT + 'ark/tools/turntable/turntable.py',
				referenceFile,
				newTurntableFile
				]

		result = cOS.getCommandOutput(params, shell=False)

		if result[0]:
			job = jobTypes.MayaVRay()

			name, nameExt = os.path.split(newTurntableFile)
			name = os.path.splitext(nameExt)[0]
			nameExt = name + '.%04d.exr'
			output = cOS.join(os.path.splitext(newTurntableFile)[0], nameExt)

			bbox = cmds.exactWorldBoundingBox()
			sizeVals = [abs(bbox[0] - bbox[3]), abs(bbox[1] - bbox[4]), abs(bbox[2] - bbox[5])]
			sizeValsM = ['{0:.3f}'.format(size * 0.01) for size in sizeVals]

			x, y, z = sizeValsM
			units = 'm'
			annotationsString = '{"SouthCenter": {"text": "SIZE (X,Y,Z): ' + x +' x ' + y + ' x ' + z + units + '", "colorR": 0, "type": "", "colorG": 0, "colorB": 0}}'

			jobData = {
					'node': 'turntable_camShape',
					'program': 'vray',
					'farPlane': 10000.0,
					'name': name,
					'chunkSize': None,
					'sourceFile': newTurntableFile,
					'height': 1080,
					'priority': '50',
					'width': 1920,
					'version': 5,
					'frameRange': '1001-1003',
					'fps': 24,
					'output': output,
					'jobType': 'MayaVRay',
					'nearPlane': 0.1,
					'annotationsString': annotationsString
					}

			job.submit(jobData)

		else:
			print result[1]

	def openPlayblast(self, playblastFile=None):
		if not playblastFile:
			playblastFile = self.getFileName()[0]

		if not os.path.exists(playblastFile):
			self.showError('Playblast does not exist')
			return

		subprocess.Popen(playblastFile, shell=True)

	def getFileName(self):
		name = self.getKnob('Name').getValue()
		filename = '{}_{}'.format(self.currentShot['name'], name)

		outputPath = os.path.join(
			self.getKnob('Output path').getValue(),
			filename + '.mov'
		)

		return outputPath, filename

	def playblast(self):
		playblastOptions = {}
		cOS.makeDir(self.outputPath)
		playblastOptions['format'] = 'image'

		frameRanges = self.getKnob('Frame Range').getValue().split('-')
		playblastOptions['startTime'] = int(frameRanges[0])
		playblastOptions['endTime'] = int(frameRanges[1])
		playblastOptions['camera'] = None
		cameraName = self.getKnob('Camera').getValue()
		if cameraName != 'Current View':
			playblastOptions['camera'] = cameraName
			if currentApp == 'maya':
				# so that burn in says camera1, not cameraShape1
				cameraName = translator.getNodeByName(playblastOptions['camera']).getParent().name()
		else:
			if currentApp == 'maya':
				cameraName = translator.getCamFromView().name()

		resolution = self.getKnob('Playblast Resolution').getValue()

		# making sure it's divisible by 4 after res percent is applied
		width = (int(resolution['width'] * .25) * 4)
		height = (int(resolution['height'] * .25) * 4)
		playblastOptions['size'] = [width, height]

		playblastOptions['background'] = self.getKnob('Show Background').getValue()

		outputPath, filename = self.getFileName()

		playblastOptions['outputPath'] = outputPath
		playblastOptions['filename'] = filename

		playblastOptions['inPath'] = globalSettings.TEMP + arkUtil.randomHash() + '/' + playblastOptions['filename']

		playblastOptions['sound'] = self.getKnob('Enable Audio').getValue()

		task = pm.getTask()
		playblastOptions['copyToDir'] = pm.getDailiesPath(task, checkPath=translator.getFilename())
		playblastOptions['copyToFile'] = pm.getDailiesFile(task, filename=translator.getFilename())

		# get burn in info
		focalLength = ''
		if currentApp == 'maya':
			focalLength = translator.getNodeByName(cameraName).getChildren()[0].getProperty('focalLength')
		elif currentApp == 'houdini' and cameraName != 'Current View':
			focalLength = translator.getNodeByName(cameraName).getProperty('focal')

		sourceFile = translator.getFilename().rsplit('/', 1)[-1]
		playblastOptions['text'] = self.getBurnInText(
			filename, self.currentShot['name'], cameraName, playblastOptions['startTime'], focalLength
		)

		playblastFile = translator.createPlayblast(playblastOptions)
		if playblastFile:
			task = pm.get('Task', pm.getTaskID())
			userID = pm.getUser()['id']
			asset = pm.getAsset(task)
			version = cOS.getVersion(playblastFile)
			versionData = {
						'user_id': userID,
						'version': version,
						'task_id': task['id']
						}
			print 'Uploading playblast version {} on asset "{}"" for task "{}":'.format(versionData['version'], asset['name'], task['name'])
			pm.uploadFile(asset, playblastFile, versionData = versionData, overwrite = True)
			if not self.getKnob('Save PNG Sequence').getValue():
				print 'delete the PNG Sequence'
				self.deletePngFolder()
			self.openPlayblast(playblastFile)
			return

		return self.showError('Playblast failed!')

	def getBurnInText(self, filename, shotName, camera, fstart, focalLength):
		'''
		gets passed to ffmpeg
		'''
		padding = 30
		fontFile = r'C\\:/Windows/Fonts/arial.ttf'
		texts = [
			# top left
			(filename, 'x={padding}:y={padding}'.format(padding=padding)),
			# top right
			(shotName, 'x=(w-text_w)-{padding}:y={padding}'.format(padding=padding)),
			# bottom left
			('\'%{{eif\:n+{}\:d}}\''.format(fstart), 'x={padding}:y=(h-text_h)-{padding}'.format(padding=padding)),
			# bottom middle
			(camera, 'x=(w-text_w)/2:y=(h-text_h)-{padding}'.format(padding=padding)),
			# bottom right
			(focalLength, 'x=(w-text_w)-{padding}:y=(h-text_h)-{padding}'.format(padding=padding))
		]

		drawText = 'drawtext=fontfile={font}:text={text}:fontsize=24:fontcolor=white:{pos}'
		drawTexts = [drawText.format(font=fontFile, text=text[0], pos=text[1]) for text in texts]

		return ', '.join(drawTexts)


def gui():
	return PlayblastTool()

def launch(docked=False):
	if not pm.hasCurrentTask():
		print 'Scene not opened through ftrack!'

	else:
		translator.launch(PlayblastTool, docked=docked)

if __name__=='__main__':
	launch()
