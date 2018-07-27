# Name: Publish Manager
# Author: Shobhit Khinvasara
# Date: 02/06/2017

import os

import arkInit
arkInit.init()

import settingsManager
globalSettings = settingsManager.globalSettings()

from translators import QtGui

import translators
translator = translators.getCurrent()
currentApp = os.environ.get('ARK_CURRENT_APP')

import deadline

import cOS

import arkFTrack
pm = arkFTrack.getPM()

import baseWidget

class PublishManager(baseWidget.BaseWidget):
	defaultOptions = {
			'title': 'Publish Manager',
			'width': 400,
			'height': 600,

		'knobs': [
			{
				'name': 'Shot',
				'dataType': 'searchList',
				'hasNone': True
			},
			{
				'name': 'Assets',
				'dataType': 'dynamicList',
				'selectionMode': 'single'
			},
			{
				'name': 'Version',
				'dataType': 'Int',
				'value': 1,
			},
			{
				'name': 'Frame Range',
				'dataType': 'FrameRange',
			},
			{
				'name': 'Publish Type',
				'dataType': 'Radio',
				'options': ['All', 'Selected'],
				'value': 'Selected'
			},
			{
				'name': 'Write Creases',
				'dataType': 'Checkbox',
			},
			{
				'name': 'No Normals',
				'dataType': 'Checkbox'
			},
			{
				'name': 'Animation',
				'dataType': 'Checkbox'
			},
			{
				'name': 'Export As',
				'dataType': 'List',
			},
			{
				'name': 'Publish Output Path',
				'dataType': 'text'
			},
			{
				'name': 'Refresh',
				'dataType': 'PythonButton',
				'callback':'refresh'
			},
			{
				'name': 'Publish',
				'dataType': 'PythonButton',
				'callback':'publish'
			}
		]
	}

	def init(self):
		filename = translator.getFilename()
		self.assetRoot = pm.getPath(pm.getTask()['parent'], checkPath=filename)
		if not self.assetRoot:
			self.showError('Invalid Task!')

		self.projectRoot = pm.getPath(pm.getTask()['project'])

		self.folderPath = cOS.normalizeAndJoin(self.assetRoot, 'Publish')
		self.assets = []

	def refresh(self):
		self.getKnob('Assets').clear()
		self.getKnob('Export As').clear()
		self.getKnob('Shot').clear()
		self.postShow()

	def postShow(self):
		if not translator.getOption('exportTypes'):
			self.hideKnob('Export As')
		else:
			self.showKnob('Export As')
			self.getKnob('Export As').addItems(translator.getOption('exportTypes'))
		selectedNodes =  translator.getSelectedNodes()
		if selectedNodes:
			self.getKnob('Publish Type').setValue('Selected', emit=False)
		else:
			self.getKnob('Publish Type').setValue('All', emit=False)

		openFile = translator.getFilename()
		self.version = cOS.getVersion(openFile)
		if self.version == 0:
			self.version = 1
		self.getKnob('Version').setValue(self.version, emit=False)

		frameRange = translator.getAnimationRange()
		self.getKnob('Frame Range').setValue(str(frameRange['startFrame']) + '-' + str(frameRange['endFrame']))

		if not self.projectRoot:
			self.workspaceRoot = None
		else:
			self.workspaceRoot = cOS.normalizeAndJoin(self.projectRoot, 'Workspaces/')
		folders = cOS.getFiles(self.workspaceRoot,
						folderExcludes=['.*'],
						fileExcludes=['*'],
						depth=1,
						fullPath=True)

		# dictionary to store sequence for every shot
		self.shotSequence = {}
		shots = []
		for folder in folders:
			folderSections = folder.split('/')
			if len(folderSections) == 5:

				# dict {shotName : sequenceName}
				self.shotSequence[folderSections[-1]] = folderSections[-2]
				shots.append(folderSections[-1])

		shots.sort()
		self.getKnob('Shot').addItems(shots)
		self.items = []
		self.updateAssets()
		self.setPublishValues()

		self.assets = cOS.getFiles(self.folderPath,
								fileExcludes=['*'],
								folderExcludes=['.*'],
								depth=0,
								fullPath=False
							)
		self.getKnob('Shot').on('clicked', self.updateAssets)
		self.getKnob('Assets').on('itemAdded', self.storeAssets)
		self.getKnob('Assets').on('clicked', self.setPublishValues)
		self.getKnob('Frame Range').on('changed', self.setPublishValues)
		self.getKnob('Animation'). on('changed', self.setPublishValues)

		self.getKnob('Assets').on('doubleClicked', self.openFolder)

		if currentApp in ['nuke', 'houdini']:
			self.hideKnob('Write Creases')
			self.hideKnob('No Normals')
			if currentApp == 'houdini':
				self.getKnob('Publish Type').setValue('Selected', emit=False)
				self.hideKnob('Publish Type')

	def storeAssets(self, item):
		self.items.append(item)

	def updateAssets(self, value=None):
		shotName = self.getKnob('Shot').getValue()
		self.items = []
		if shotName == 'None' or shotName is '':
			self.folderPath = cOS.normalizeAndJoin(self.assetRoot, 'Publish/')

		# Path generated from shotSequence dict
		else:
			self.folderPath = cOS.normalizeAndJoin(
								self.workspaceRoot,
								self.shotSequence[shotName],
								shotName,
								'Publish/'
							)

		self.assets = cOS.getFiles(self.folderPath,
								fileExcludes=['*'],
								folderExcludes=['.*'],
								depth=0,
								fullPath=False
							)
		self.getKnob('Assets').clear()
		self.getKnob('Assets').addItems(self.assets, emit=False)
		self.getKnob('Assets').addItems(self.items, emit=False)
		self.getKnob('Publish Output Path').clear()

	def openFolder(self, value=None):
		self.setPublishValues()
		try:
			if os.path.isdir(self.folderPath):
				os.startfile(self.folderPath)
		except:
			return

	def setPublishValues(self, value=None):
		self.version = self.getKnob('Version').getValue()

		if self.getKnob('Animation').getValue():
			frameRange = self.getKnob('Frame Range').getValue()
			self.frameRange = frameRange.replace(' ', '')
		else:
			frameRange = self.getKnob('Frame Range').getValue().split('-')[0]
			self.frameRange = frameRange + '-' + frameRange

		self.assetFolderName = None
		if self.getKnob('Assets').getValue():
			self.assetFolderName = self.getKnob('Assets').getValue()

		if not self.assetFolderName:
			self.getKnob('Publish Output Path').clear()
			return

		self.publishPath = self.folderPath + self.assetFolderName + '/'
		name = self.assetFolderName + '_' + self.frameRange
		filename = cOS.createVersionedFilename(name, self.version, 4, 'abc')
		self.getKnob('Publish Output Path').setValue(self.publishPath + filename)

	def confirmOverwrite(self):
		if os.path.isfile(self.filepath):
			overwrite = QtGui.QMessageBox()
			overwrite.setText('File already exists. Overwrite?')
			overwrite.setWindowTitle('Overwrite')
			overwrite.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
			overwrite.setDefaultButton(QtGui.QMessageBox.No)
			msg = overwrite.exec_()
			if msg == QtGui.QMessageBox.Yes:
				return True
			else:
				return False
		else:
			return True

	def publish(self):
		exportOptions = {}
		if not os.path.isdir(self.publishPath):
			cOS.makeDirs(self.publishPath)

		if not os.path.isdir(self.publishPath):
			cOS.makeDirs(self.publishPath)
			self.assets.append(self.assetFolderName)

		self.setPublishValues()
		if not self.assetFolderName:
			return
		name = self.assetFolderName + '_' + self.frameRange
		filename = cOS.createVersionedFilename(name, self.version, 4, 'abc')
		self.filepath = (self.publishPath + filename)

		if not self.confirmOverwrite():
			return

		if self.getKnob('Publish Type').getValue() == 'Selected':
			if translator.getSelectedNodes():
				if currentApp == 'houdini':
					objects = [ob.nativeNode().path() for ob in translator.getSelectedNodes()]
				else:
					objects = [ob.name(fullpath=True) for ob in translator.getSelectedNodes()]
				exportOptions.update({
					'objects': objects
				})
			else:
				self.showError('Nothing selected!')
				return

		exportOptions.update({
					'noNormals': self.getKnob('No Normals').getValue(),
					'writeCreases': self.getKnob('Write Creases').getValue()
			})

		translator.exportAlembic(self.filepath, self.frameRange, exportOptions)

		if currentApp != 'houdini' and \
			self.getKnob('Export As').getValue() == 'Geometry':
			self.deadlineProcessAlembic()
			print 'Publish successful!: Path:', self.filepath

	def deadlineProcessAlembic(self):
		self.arkDeadline = deadline.arkDeadline.ArkDeadline()
		pathInfo = cOS.getPathInfo(self.filepath)
		name = pathInfo['name']

		jobInfo = {
			'Name': name,
			'BatchName': name,
			'Plugin': 'CommandLine',
			'priority': 70,
			'LimitGroups': 'hbatch-license',
			'Group': 'good-software',
			'MachineLimit': 0,
			'ExtraInfoKeyValue0': 'abc_in=' + self.filepath,
			'ExtraInfoKeyValue1': 'abc_out=' + self.filepath.replace('.abc', '_processed.abc'),
			'ExtraInfoKeyValue2': 'abc_frames=' + str(self.frameRange),
			'ExtraInfoKeyValue3': 'abc_fps=' + str(translator.getFPS()),
		}

		pluginInfo = {
			'SceneFile': globalSettings.DEADLINE + '/custom/scripts/Jobs/deadlineProcessedAlembic.py',
			'Executable': globalSettings.HYTHON_EXE,
			'Shell': 'default',
			'ShellExecute': False,
			'SingleFramesOnly': True
		}

		submittedInfo = self.arkDeadline.submitJob(jobInfo, pluginInfo)
		jobID = submittedInfo.get('_id')

		self.arkDeadline.updateJobData(jobID, {
			'Props.PlugInfo.Arguments': '{}/jobs/{}/deadlineProcessedAlembic.py'.format(globalSettings.DEADLINE, jobID)
		})

def gui():
	return PublishManager()

def launch(docked=False):
	translator.launch(PublishManager, docked=docked)

if __name__=='__main__':
	launch()
