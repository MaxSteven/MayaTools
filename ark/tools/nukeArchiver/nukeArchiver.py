
import os
import json

import arkInit
arkInit.init()

import settingsManager
globalSettings = settingsManager.globalSettings()

import translators

translator = translators.getCurrent()

import baseWidget
import cOS
# import copyWrapper

from database import Database
database = Database()


options = {
	'title': 'Nuke Archiver',
	'width': 600,
	'height': 800,
	'x': 100,
	'y': 100,
	'knobs': [
		{
			'name': 'heading',
			'dataType': 'heading',
			'value': 'Nuke Archiver'
		},
		{
			'name': 'Archive Root',
			'dataType': 'directory',
			# 'value': os.environ.get('raidcharles') + '/',
			'value': os.environ.get('raidcharles') + '/Geostorm',
		},
		{
			'name': 'Bundle',
			'dataType': 'text',
			'value': 'test_v009',
		},
		{
			'name': 'Shot Folder Convention',
			'dataType': 'text',
			'value': '{bundle}/elements/{shot}/',
		},
		{
			'name': 'Image Naming Convention',
			'dataType': 'text',
			'value': '{basename}/{resolution}/{basename}.{colorspace}.{padding}.{extension}',
		},
		{
			'name': 'Asset Naming Convention',
			'dataType': 'text',
			'value': 'asset_{basename}/asset_{basename}.{extension}',
		},
		{
			'name': 'Shots Root',
			'dataType': 'directory',
			# 'value': globalSettings.SHARED_ROOT,
			'value': 'R:/Geostorm/Workspaces/Movie',
		},
		{
			'name': 'Shots',
			'dataType': 'text',
			'multiline': True,
			'value': 'ltc_0180_0080',
		},
		{
			'name':'Archive',
			'dataType': 'PythonButton',
			'callback': 'archive'
		},
		{
			'name':'Progress',
			'dataType': 'Progress',
		},
	]
}


class NukeArchiver(baseWidget.BaseWidget):

	def postShow(self):
		self.getKnob('Shots Root').on('changed', self.getShotsFromDirectory)
		self.getKnob('Shots').getWidget().setFocus()

	def getShotsFromDirectory(self, directory):
		folders = False
		try:
			folders = os.listdir(directory)
		except:
			return self.showError('Invalid directory:', directory)

		folders.sort()
		folders = [f for f in folders if os.path.isdir(directory + f)]
		self.getKnob('Shots').setValue('\n'.join(folders))

	def archive(self):
		root = self.getKnob('Shots Root').getValue()
		root = cOS.normalizeDir(root)
		# results = {}

		# go through each shot folder
		shots = self.getKnob('Shots').getValue()
		for shot in shots.split('\n'):
			shot = shot.strip()
			if len(shot) < 1:
				continue

			# get the comp folder
			shotRoot = root + shot + '/'
			archiveOptions = {
				'shot': shot,
				'bundle': self.getKnob('Bundle').getValue(),
				'shotRoot': shotRoot,
				'archiveRoot': self.getKnob('Archive Root').getValue(),
				'shotFolderConvention': self.getKnob('Shot Folder Convention').getValue(),
				'imageConvention': self.getKnob('Image Naming Convention').getValue(),
				'assetConvention': self.getKnob('Asset Naming Convention').getValue()
			}
			archiverRoot = cOS.getDirName(os.path.realpath(__file__))
			settingsPath = globalSettings.TEMP + 'archiverData.json'
			with open(settingsPath, 'w') as output:
				json.dump(archiveOptions, output)

			# we use Nuke's special version of python here
			# as it behaves nicely w/ command line stuff
			command = [
				globalSettings.NUKE_PYTHON_EXE,
				archiverRoot + 'archive.py'
			]
			process = cOS.startSubprocess(' '.join(command))
			out, err = cOS.waitOnProcess(process)

			# print 'out:\n', out
			if err:
				print '\nErrors:\n', err
			# results[shot] = out

	def showResults(self, results):
		resultsOptions = {
			'title': 'Results',
			'width': 800,
			'height': 600,
			'knobs': [
				{
					'name': 'versions',
					'dataType': 'Table',
					'headings': ['Shot', 'Status'],
					'items': results,
				},
				{
					'name': 'Close',
					'dataType': 'PythonButton',
					'callback': 'closeWindow',
				},
			]
		}

		translator.launch(baseWidget.BaseWidget, None, options=resultsOptions, newWindow=True)

def launch(parent=None, *args, **kwargs):
	translator.launch(NukeArchiver, parent, options=options, *args, **kwargs)

if __name__ == '__main__':
	launch()
