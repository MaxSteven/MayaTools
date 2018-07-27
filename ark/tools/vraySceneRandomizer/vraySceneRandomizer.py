# Name: Vray Scene Randomizer
# Author: Shobhit Khinvasara
# Date: 04/03/2017

import random

import arkInit
arkInit.init()

import settingsManager
globalSettings = settingsManager.globalSettings()

import translators
translator = translators.getCurrent()

import cOS
from caretaker import Caretaker
caretaker = Caretaker()

import translators
translator = translators.getCurrent()

import baseWidget

class VraySceneRandomizer(baseWidget.BaseWidget):
	defaultOptions = {
			'title': 'VRay Scene Randomizer',
			'width': 500,
			'height': 800,

			'knobs': [
				{
					'name': 'Browse',
					'dataType': 'directory'
				},
				{
					'name': 'VRay Scene List',
					'dataType': 'listBox',
					'selectionMode': 'multi',
				},
				{
					'name': 'Randomize on Selected',
					'dataType': 'PythonButton',
					'callback': 'randomizeSelected',
				},
				{
					'name': 'Randomize Range',
					'dataType': 'FrameRange',
					'value': '0-50'
				},
				{
					'name': 'Randomize animation offset',
					'dataType': 'PythonButton',
					'callback': 'randomizeAnim',
				},

			]
	}

	def init(self):
		self.vrayNodes = []

	def postShow(self):
		self.getKnob('Browse').on('changed', self.populateList)

	def populateList(self, *args):
		self.folderPath = self.getKnob('Browse').getValue()
		self.files = cOS.getFiles(self.folderPath, fileIncludes=['*.vrscene'], depth=0, filesOnly=True, fullPath=False)
		if not self.files:
			self.showError('No files found!')
			return

		self.getKnob('VRay Scene List').addItems(self.files)

	def getVrayNodesFromSelected(self):
		descendants = translator.getDescendants(translator.getSelectedNodes())
		for dec in descendants:
			if dec.getType() == 'vrayscene':
				self.vrayNodes.append(dec)

		if not self.vrayNodes:
			self.showError('No objects selected!')
			return

	def randomizeSelected(self):
		print 'randomizeSelected'

		if not self.vrayNodes:
			self.getVrayNodesFromSelected()

		self.selectedFiles = self.getKnob('VRay Scene List').getValue()
		if not self.selectedFiles:
			self.showError('No VRay Scenes selected!')
			return

		paths = []
		for f in self.selectedFiles:
			paths.append(self.folderPath + f)

		for node in self.vrayNodes:
			node.setProperty('FilePath', random.choice(paths))

	def randomizeAnim(self):
		if not self.vrayNodes:
			self.getVrayNodesFromSelected()

		minMax = self.getKnob('Randomize Range').getValue().split('-')

		try:
			minVal = int(minMax[0])
			maxVal = int(minMax[1])
		except:
			self.showError('Invalid Frame Range')
			return

		for node in self.vrayNodes:
			node.setProperty('animOffset', random.randint(minVal, maxVal))

def gui():
	return VraySceneRandomizer()

def launch(*args):
	translator.launch(VraySceneRandomizer)

if __name__=='__main__':
	launch()


