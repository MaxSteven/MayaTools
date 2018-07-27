import os

import arkInit
arkInit.init()

import cOS

import settingsManager
globalSettings = settingsManager.globalSettings()

import translators
translator = translators.getCurrent()

import baseWidget

from operator import itemgetter
from itertools import groupby

options = {
	'title': 'Chunk Sequence',
	'width': 460,
	'height': 200,
	'knobs': [
		{
			'name': 'folder',
			'dataType': 'directory',
			'value': globalSettings.RAMBURGLAR,
		},
		{
			'name': 'existing files',
			'dataType': 'listBox',
			'options': [],
		},
		{
			'name': 'shot prefix',
			'dataType': 'text'
		},
		{
			'name': 'starting number',
			'dataType': 'int'
		},
		{
			'name': 'shot number increment',
			'dataType': 'int'
		},
		{
			'name': 'Split Sequence',
			'dataType': 'pythonButton',
			'callback' : 'chunkExistingFilenames'
		}
	]
}


class ChunkSequence(baseWidget.BaseWidget):

	allFiles = []
	chunkedFiles = []

	def postShow(self):
		self.getKnob('folder').on('changed', self.updateFiles)

	def updateFiles(self, *args):
		self.allFiles = []
		self.allFiles = cOS.getFiles(self.getKnob('folder').getValue(),
				fileIncludes=['*.jpg', '*.png', '*.tif', '*.tga', '*.exr', '*.abc', '*.dpx'],
				folderExcludes=['.*'],
				fileExcludes=['.*'],
				filesOnly=True)
		self.allFiles.sort()

		self.chunkedFiles = []
		for k, g in groupby(enumerate(self.allFiles), lambda (i,x):i - int(cOS.getFrameNumber(x))):
			self.chunkedFiles.append(map(itemgetter(1), g))

		self.getKnob('existing files').clear()
		self.getKnob('existing files').addItems(self.allFiles)

	def chunkExistingFilenames(self):
		folderRoot =  cOS.upADir(self.getKnob('folder').getValue())
		shotPrefix = self.getKnob('shot prefix').getValue()
		startingNumber = self.getKnob('starting number').getValue()
		shotIncrement = self.getKnob('shot number increment').getValue()
		if startingNumber >= 0 and shotIncrement > 0 and shotPrefix != '':
			for chunk in self.chunkedFiles:
				shotFolder = '%s%s_%04d' % (folderRoot, shotPrefix, startingNumber)
				if os.path.isdir(shotFolder):
					self.showError('Direcotry already exists')
					return
				else:
					os.mkdir(shotFolder)
					for imageFile in chunk:
						cOS.copy(imageFile, shotFolder)
					startingNumber += shotIncrement
		else:
			self.showError('Shot Prefix cannot be empty, \
				Starting Number must be 0 or greater, \
				and Shot Number Increment must be greater than 0')

def gui():
	return ChunkSequence(options=options)

def launch():
	translator.launch(ChunkSequence, options=options)

if __name__ == '__main__':
	launch()

