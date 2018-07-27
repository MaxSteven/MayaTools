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

from caretaker import Caretaker
caretaker = Caretaker()

import baseWidget

import settingsManager
globalSettings = settingsManager.globalSettings()


class PlayblastToolLegacy(baseWidget.BaseWidget):
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
				},
				{
					'name': 'Open Playblast Folder',
					'dataType': 'PythonButton',
					'callback': 'openPlayblastFolder'
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
				}
			]
		}

	def postShow(self):
		self.taskInfo = caretaker.getTaskInfo()
		self.outputPath = self.taskInfo.assetRoot + 'playblast'

		if not self.taskInfo.projectInfo:
			self.showError('Invalid Project!')

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

		if self.taskInfo.projectInfo:
			# Coz for some reason directly querying width and height don't work in Houdini
			width = self.taskInfo.projectInfo['formatWidth']
			height = self.taskInfo.projectInfo['formatHeight']

			self.getKnob('Output path').setValue(self.outputPath)
			self.getKnob('Playblast Resolution').setValue({'width': width, 'height': height}, emit=False)

	def openPlayblastFolder(self):
		filepath, filename = self.getFileName()
		cOS.openFileBrowser(filepath)

	def openPlayblast(self):
		filepath, filename = self.getFileName()
		if not os.path.exists(filepath):
			self.showError('Playblast does not exist')
			return

		subprocess.Popen(filepath, shell=True)

	def getFileName(self):
		outputPath = self.getKnob('Output path').getValue()
		name = self.getKnob('Name').getValue()
		outputPath = outputPath + self.taskInfo.shotNumber + '_' + name + '.mov'
		filename = self.taskInfo.shotNumber + '_' + name

		return outputPath, filename

	def playblast(self):
		playblastOptions = {}
		cOS.makeDir(self.outputPath)
		playblastOptions['format'] = 'image'

		frameRanges = self.getKnob('Frame Range').getValue().split('-')
		playblastOptions['startTime'] = int(frameRanges[0])
		playblastOptions['endTime'] = int(frameRanges[1])
		playblastOptions['camera'] = None
		if self.getKnob('Camera').getValue() != 'Current View':
			playblastOptions['camera'] = self.getKnob('Camera').getValue()

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

		translator.createPlayblast(playblastOptions)
		self.openPlayblast()

def gui():
	return PlayblastToolLegacy()

def launch(docked=False):
	translator.launch(PlayblastToolLegacy, docked=docked)

if __name__=='__main__':
	launch()
