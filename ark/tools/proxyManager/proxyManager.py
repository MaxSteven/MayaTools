# Name: Proxy Manager
# Author: Shobhit Khinvasara
# Date: 01/20/2017

import os

import arkInit
arkInit.init()

from translators import QtGui
import cOS

import translators
translator = translators.getCurrent()
currentApp = os.environ.get('ARK_CURRENT_APP')

from caretaker import Caretaker
caretaker = Caretaker()

import baseWidget
import knobs

class ProxyManager(baseWidget.BaseWidget):
	defaultOptions = {
			'title': 'Proxy Manager',
			'width': 700,
			'height': 1000,

			'knobs' : [
				{
					'name': 'Target Folder',
					'dataType': 'directory',
				},
				{
					'name': 'Scale',
					'dataType': 'float',
					'value':'1.0'
				},
			]
		}
	def init(self):
		self.taskInfo = caretaker.getTaskInfo()
		self.folderPath = self.taskInfo.assetRoot + 'Publish'

		if not self.taskInfo.projectInfo:
			self.showError('Invalid Project!')

		self.getKnob('Target Folder').setValue(self.folderPath)
		self.exportOptions = {}

		if currentApp == 'maya':
			parWidthMultKnob = knobs.Float('Particle Width Multiplier', '1.0')
			self.addKnob(parWidthMultKnob)

			hairWidthMultKnob = knobs.Float('Hair Width Multiplier', '1.0')
			self.addKnob(hairWidthMultKnob)

			previewFacesKnob = knobs.Int('Preview Faces', '5000')
			self.addKnob(previewFacesKnob)

			geoLoadListOptions = {'options': ['Bounding Box', 'Preview', 'GPU Mesh']}
			self.geoToLoadKnob = knobs.List('Geometry To Load', 'Preview', options=geoLoadListOptions)
			self.addKnob(self.geoToLoadKnob)

			self.renderOptions = {
				'scale': 1.0,
				'particleWidthMultiplier': 1.0,
				'hairWidthMultiplier': 1.0,
				'previewFaces': 5000,
				'geoToLoad': 2
			}

		if currentApp in ('nuke', 'nuke_cl'):

			geoLoadListOptions = {'options': ['Bounding Box', 'Proxy']}
			self.geoToLoadKnob = knobs.List('Geometry To Load', 'Proxy', options=geoLoadListOptions)
			self.addKnob(self.geoToLoadKnob)

			self.renderOptions = {
				'scale': 1.0,
				'geoToLoad': 'Proxy'
				}

		else:
			self.renderOptions = {}

		filesOptions = {'selectionMode': 'multi'}
		self.filesKnob = knobs.ListBox('Assets', options=filesOptions)
		self.addKnob(self.filesKnob)

		options = {'options':['As Vray Proxy', 'As Alembic'], 'value': 'As Vray Proxy'}
		importType = knobs.Radio('Import Type', options = options)
		self.addKnob(importType)

		importOptions = {'callback': 'importLatestFile'}
		importLatestButton = knobs.PythonButton('Import Latest Version', options=importOptions)
		self.addKnob(importLatestButton)

		importOptions = {'callback': 'importSelectedFile'}
		importSelectedButton = knobs.PythonButton('Import Specific Version', options=importOptions)
		self.addKnob(importSelectedButton)

		self.filesList = []

	def importLatestFile(self):
		for f in self.getKnob('Assets').getValue():
			files = cOS.getFiles(self.folderPath+'/'+f, fileExcludes = ['unprocessed'])
			if files:
				files.sort()
				self.filepath = files[-1]
				self.importFile()
			else:
				self.showError('No Files found in: ' + f)

	def importSelectedFile(self):
		for f in self.getKnob('Assets').getValue():
			self.filepath = QtGui.QFileDialog.getOpenFileName(self, self.options['title'], self.folderPath + '/' + f)[0]
			if self.filepath:
				self.importFile()

	def postShow(self):
		self.populateFileList()
		self.getKnob('Target Folder').on('changed', self.changed)

	def changed(self, path):
		self.folderPath = path
		self.getKnob('Assets').clear()
		self.populateFileList()

	def populateFileList(self):
		try:
			fileList = []
			for f in os.listdir(self.folderPath):
				if os.path.isdir(self.folderPath + '/' + f):
					fileList.append(f.replace(self.folderPath, ''))

			self.getKnob('Assets').addItems(fileList)
		except:
			pass

	def importFile(self):
		self.renderOptions['scale'] = float(self.getKnob('Scale').getValue())

		if currentApp == 'maya':
			self.renderOptions['particleWidthMultiplier'] = float(self.getKnob('Particle Width Multiplier').getValue())
			self.renderOptions['hairWidthMultiplier'] = float(self.getKnob('Hair Width Multiplier').getValue())
			self.renderOptions['previewFaces'] = int(self.getKnob('Preview Faces').getValue())
			self.renderOptions['geoToLoad'] = str(self.geoToLoadKnob.widget.currentText())

		elif currentApp in ('nuke', 'nuke_cl'):
			self.renderOptions['geoToLoad'] = str(self.geoToLoadKnob.widget.currentText())

		if self.getKnob('Import Type').getValue() == 'As Vray Proxy':
			translator.createRenderProxy(self.filepath, self.renderOptions)

		else:
			translator.importAlembicGeometry(self.filepath)

def gui():
	return ProxyManager()

def launch(docked=False):
	translator.launch(ProxyManager, docked=docked)

if __name__=='__main__':
	launch()
