# Name: Shot Builder
# Author: Shobhit Khinvasara
# Date: 01/20/2017

import arkInit
arkInit.init()

import os
currentApp =  os.environ.get('ARK_CURRENT_APP')

import cOS

import re
import translators
translator = translators.getCurrent()

import arkFTrack
pm = arkFTrack.getPM()

import baseWidget
import knobs

class ShotBuilder(baseWidget.BaseWidget):
	defaultOptions = {
			'title': 'Shot Builder',
			'width': 1100,
			'height': 800,

		'knobs': [
			{
				'name': 'Shot Root',
				'dataType': 'directory',
			},
			{
				'name': 'File Types',
				'dataType': 'list',
				'options': ['All', 'Single Image', 'Image Sequence', 'Alembic'],
				'value': 'All'
			},
			{
				'name': 'Ignore',
				'dataType': 'text',
			},
			{
				'name': 'Latest Versions Only',
				'dataType': 'checkbox',
				'value': True
			},
			{
				'name': 'Parse Alembic Frame Range',
				'dataType': 'checkbox',
				'value': False
			},
			{
				'name': 'Files',
				'dataType': 'listBox',
				'selectionMode': 'multi'
			},
			{
				'name': 'Refresh',
				'dataType': 'PythonButton',
				'callback': 'postShow'
			}
		]
	}

	allImportMethods = {
			'Single Image':
					{
						'maya': ['materialEditor', 'imagePlane', 'referencePlane'],
						'nuke': ['Read Node'],
						'houdini': ['materialEditor', 'imagePlane', 'referencePlane'],
						'default': ['None']
					},
			'Image Sequence':
					{
						'maya': ['materialEditor', 'imagePlane', 'referencePlane'],
						'nuke': ['Read Node'],
						'houdini': ['materialEditor', 'imagePlane', 'referencePlane'],
						'default': ['None']

					},
			'Alembic':
					{
						'maya': ['Geometry', 'Camera', 'VRay Proxy'],
						'nuke': ['Geometry', 'Camera', 'VRay Proxy'],
						'houdini': ['Geometry', 'Camera', 'VRay Proxy'],
						'default': ['None']
					},
		}

	def init(self):
		self.currentShot = pm.getShot()

		self.fileList = []
		importMethodOptions = {}

		defaultImportOptions = {'All': {}}


		# Logic for procedurally populated default list
		tempDict = {}
		newDict = {}
		for filekey in self.allImportMethods.keys():
			for softkey in self.allImportMethods[filekey].keys():
				if softkey not in newDict.keys():
					newDict.update({softkey: []})
				for item in self.allImportMethods[filekey][softkey]:
					if item not in newDict[softkey]:
						newDict[softkey].append(item)

				tempDict.update(newDict)

		defaultImportOptions['All'] = tempDict
		# Logic end.

		self.allImportMethods.update(defaultImportOptions)

		importMethodOptions['options'] = {}
		if currentApp != None:
			importMethodOptions['options'] = self.allImportMethods['All'][currentApp]

		else:
			importMethodOptions['options'] = self.allImportMethods['All']['default']

		self.importMethodKnob = knobs.List('Import Method', options=importMethodOptions)
		self.addKnob(self.importMethodKnob)

		cameraListOptions = {'selectionMode': 'single'}
		self.listOfCameras = knobs.ListBox('List of Cameras', options=cameraListOptions)
		self.addKnob(self.listOfCameras)

		self.inContextKnob = False
		if currentApp == 'houdini':
			self.inContextKnob = knobs.Checkbox('In Context')
			self.addKnob(self.inContextKnob)

		self.scaleKnob = knobs.Float('Scale', options={'value': 1.0})
		self.addKnob(self.scaleKnob)

		self.importButton = knobs.PythonButton('Import', options={'callback': 'importSelected'})
		self.addKnob(self.importButton)

		self.imgSeqRegex = re.compile('[0-9]+-[0-9]+$')
		self.alembRegex = re.compile('.+\.[aA][bB][cC]$')

	def postShow(self):
		assetRoot = pm.getPath(self.currentShot, checkPath=translator.getFilename())

		if not assetRoot:
			self.showError('Invalid Asset Root!')

		self.getKnob('Shot Root').setValue(assetRoot, emit=False)
		# set useful defaults for specific programs
		if translator.program == 'nuke':
			self.getKnob('Ignore').setValue('Proxy')
			self.getKnob('File Types').setValue('Image Sequence')

		self.createFileList()
		self.populateFileList()
		self.hideKnob('List of Cameras')
		self.hideKnob('Scale')
		self.getKnob('Shot Root').on('changed', self.createFileList)
		self.getKnob('Shot Root').on('changed', self.populateFileList)
		self.getKnob('File Types').on('changed', self.populateFileList)
		self.getKnob('Parse Alembic Frame Range').on('changed', self.populateFileList)
		self.getKnob('Ignore').on('changed', self.populateFileList)
		self.getKnob('Latest Versions Only').on('changed', self.populateFileList)
		self.getKnob('Files').on('doubleClicked', self.importSelected)
		self.importMethodKnob.on('changed', self.listCameraOptions)

	def populateFileList(self, *args):
		reduceFileList = self.reduceFileList()
		self.importMethodOptionChange()

		self.getKnob('Files').clear()
		self.getKnob('Files').addItems(reduceFileList)

	def importMethodOptionChange(self):
		fileType = self.getKnob('File Types').getValue()
		self.importMethodKnob.clear()
		if currentApp:
			self.importMethodKnob.addItems(self.allImportMethods[fileType][currentApp])
		else:
			self.importMethodKnob.addItems(self.allImportMethods[fileType]['default'])

		self.listCameraOptions()

	def reduceFileList(self):
		fileList = self.fileList
		fileType = self.getKnob('File Types').getValue()
		latestVersionsOnly = self.getKnob('Latest Versions Only').getValue()
		ignore = self.getKnob('Ignore').getValue().strip()

		newFileList = []

		if fileType == 'Single Image':
			for f in fileList:
				if not self.imgSeqRegex.search(f) and \
					not self.alembRegex.search(f) and \
					(not ignore or ignore.lower() not in f.lower()):
					newFileList.append(f)

		elif fileType == 'Image Sequence':
			for f in fileList:
				if self.imgSeqRegex.search(f) and \
					(not ignore or ignore.lower() not in f.lower()):
					newFileList.append(f)


		elif fileType == 'Alembic':
			for f in fileList:
				if self.alembRegex.match(f) and \
					(not ignore or ignore.lower() not in f.lower()):
					newFileList.append(f)

		else:
			newFileList = fileList

		if latestVersionsOnly:
			items = {}
			for f in newFileList:

				# strip version
				baseName = re.sub('_[vV][0-9]+', '', f)
				baseName = re.sub('/[vV][0-9]+/', '/', baseName)

				# strip frame length
				baseName = re.sub('[0-9]+-[0-9]+', '', baseName)
				if self.getKnob('Parse Alembic Frame Range').getValue() and f.endswith('.abc'):
					if len(f.split('_')) > 1:
						frames = f.split('_')[1]
						if len(frames.split('-')) > 1:
							
							f = re.sub(frames, '', f)
							f = f + '       ' + frames

				# strip spaces and lowercase
				baseName = baseName.replace(' ','')
				baseName = baseName.lower()

				versionNumber = cOS.getVersion(f)

				if baseName not in items or versionNumber > items[baseName]['latest']:
					items[baseName] = {
						'latest': versionNumber,
						'file': f
					}

			# collapse the list back down
			newFileList = [i['file'] for i in items.values()]
			newFileList.sort()

		self.reducedFileList = newFileList

		formattedFileList = []
		# format the names nicely
		for f in newFileList:
			f = re.sub('\.%.+? ', '       ', f)
			f = f.replace('/', '    /    ')
			formattedFileList.append(f)

		return formattedFileList

	def createFileList(self, *args):
		self.folderPath = cOS.normalizePath(self.getKnob('Shot Root').getValue())
		self.fileList = []
		fileList = []
		try:
			allFiles = cOS.getFiles(self.folderPath,
				fileIncludes=['*.jpg', '*.png', '*.tif', '*.tga', '*.exr', '*.abc', '*.dpx'],
				folderExcludes=['.*'],
				fileExcludes=['.*'],
				filesOnly=True)

			if currentApp == 'houdini':
				for f in allFiles:
					fileList.append(f.replace(self.folderPath, ''))

			else:
				for f in allFiles:
					if '_unprocessed.' not in f:
						fileList.append(f.replace(self.folderPath, ''))
		except:
			return

		fileList = [f for f in fileList if ('.preview' not in f.lower())]

		self.fileList = cOS.collapseFiles(fileList)

	def listCameraOptions(self, *args):
		if self.importMethodKnob.getValue() == 'imagePlane':
			self.showKnob('List of Cameras')
			cameraList = translator.getNodesByType('camera')
			cameraNames = [n.name() for n in cameraList]
			self.listOfCameras.addItems(cameraNames)
		else:
			self.listOfCameras.clear()
			self.hideKnob('List of Cameras')

		if self.importMethodKnob.getValue() == 'VRay Proxy':
			self.showKnob('Scale')

		else:
			self.hideKnob('Scale')

	def importSelected(self):
		importMethod = self.getKnob('Import Method').getValue()

		# importAlembicMethod = self.getKnob('Import Alembic \nMethod').getValue()

		# get the index-based selection from the file list
		selection = self.getKnob('Files').getSelectedIndexes()

		# look up the real file name in the reduced file list
		# this is because the filenames in the actual files widget
		# have "pretty" formatting
		selectedFiles = [self.reducedFileList[i] for i in selection]

		importOptions = {}
		importImageMethods = []
		for filekey in self.allImportMethods.keys():
			for softkey in self.allImportMethods[filekey].keys():
				if filekey in ['Single Image', 'Image Sequence']:
					importImageMethods.extend(self.allImportMethods[filekey][softkey])

		importImageMethods = list(set(importImageMethods))

		inContextValue = False
		if self.inContextKnob:
			inContextValue = self.inContextKnob.getValue()

		scale = self.scaleKnob.getValue()

		for f in selectedFiles:
			filepath = self.folderPath + f.split(' ')[0]
			if importMethod in importImageMethods:
				if importMethod == 'imagePlane':
					importOptions['Camera'] = self.getKnob('List of Cameras').getValue()
				if self.imgSeqRegex.search(f):
					translator.importImageSequence(filepath, importMethod, importOptions)

				elif self.alembRegex.match(f):
					self.showError('Invalid file type!')

				else:
					translator.importImage(filepath, importMethod, importOptions)

			else:
				if self.alembRegex.match(f):
					if importMethod == 'Geometry':
						translator.importAlembicGeometry(filepath, inContext=inContextValue)
					elif importMethod == 'Camera':
						translator.importAlembicCamera(filepath)
					else:
						translator.createRenderProxy(filepath, renderOptions = {'scale': scale,
																				'particleWidthMultiplier': 1.0,
																				'hairWidthMultiplier': 1.0,
																				'previewFaces': 5000,
																				'geoToLoad': 'Preview'})
				else:
					self.showError('Invalid file type')

def gui():
	return ShotBuilder()

def launch(docked=False):
	translator.launch(ShotBuilder, docked=docked)

if __name__=='__main__':
	launch()
