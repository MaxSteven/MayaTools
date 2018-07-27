
import os

import arkInit
arkInit.init()

# import ieOS
import cOS
import settingsManager
globalSettings = settingsManager.globalSettings()
import translators

translator = translators.getCurrent()

# from keyCommands import Command

from translators import QtGui, QtCore

class ImportComps(QtGui.QDialog):

	currentSearchRoot = False

	def __init__(self, parent=None, **kwargs):
		super(ImportComps, self).__init__(parent)

		form = QtGui.QFormLayout()
		form.setLabelAlignment(QtCore.Qt.AlignLeft)
		form.setVerticalSpacing(10)

		# search directory
		self.searchDir = QtGui.QLineEdit()
		self.searchDir.setReadOnly(True)

		browseButton = QtGui.QPushButton('...')
		browseButton.pressed.connect(self.getSearchDirectory)
		browseButton.setMaximumWidth(30)

		browseHBox = QtGui.QHBoxLayout()
		browseHBox.addWidget(self.searchDir)
		browseHBox.addWidget(browseButton)
		form.addRow('Search Directory:', browseHBox)

		self.compRoot = QtGui.QLineEdit()
		self.compRoot.setText('/Comp/')
		form.addRow('Comp Root:', self.compRoot)

		self.compList = QtGui.QListWidget()
		self.compList.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
		self.compList.setMinimumHeight(780)
		form.addRow(self.compList)

		importComps = QtGui.QPushButton('Import Selected Comps')
		importComps.pressed.connect(self.importComps)
		form.addRow(importComps)

		self.setLayout(form)

		self.setGeometry(300, 300, 300, 900)
		self.setWindowTitle('Import Comps')

		self.show()

	def getSearchDirectory(self):
		searchDir = QtGui.QFileDialog.getExistingDirectory(self, 'Search Root')
		if searchDir:
			self.searchDir.setText(searchDir)

		self.updateCompList()

	def updateCompList(self):
		self.compList.clear()

		searchDir = self.searchDir.text()
		compRoot = self.compRoot.text()
		if not searchDir or not os.path.isdir(searchDir):
			self.compList.addItem('< Invalid Directory >')
			# QtGui.QMessageBox.warning( None, 'Error', 'Invalid Search Directory')
			return False

		self.currentSearchRoot = cOS.normalizeDir(searchDir)

		# get the root shot folders and sort them
		folders = os.listdir(self.currentSearchRoot)
		folders.sort()

		for directory in folders:
			if directory[0] != '.' and os.path.isdir(self.currentSearchRoot + directory + compRoot):
				self.compList.addItem(directory)

	def importComps(self):
		if not self.currentSearchRoot:
			QtGui.QMessageBox.warning( None, 'Error', 'Invalid Search Directory')
			return False

		compRoot = self.compRoot.text()
		# import hiero.core

		comps = []
		# no items iterator on list widgets, super lame
		for i in xrange(self.compList.count()):

			# bail if the item isn't selected
			listItem = self.compList.item(i)
			if not listItem.isSelected():
				continue

			# build a path to the comp directory and get the files there
			directory = listItem.text()
			compFolder = self.currentSearchRoot + directory + compRoot
			try:
				files = os.listdir(compFolder)
			except:
				continue

			# find the latest comp
			maxVersion = -1
			latestComp = None
			for f in files:
				version = cOS.getVersion(f)
				if version > maxVersion and '~' not in f and '.autosave' not in f:
					maxVersion = version
					latestComp = f

			if latestComp:
				comps.append(compFolder + latestComp)

		self.createSequence(comps)

	def createSequence(self, comps):
		import hiero.core

		clips = []
		currentProject = hiero.core.projects()[-1]
		clipsBin = currentProject.clipsBin()
		sequence = hiero.core.Sequence('CompSequence')
		clipsBin.addItem(hiero.core.BinItem(sequence))
		track = hiero.core.VideoTrack('Comps')

		currentTime = 0

		for compFile in comps:
			try:
				# create and import the clip
				clipSource = hiero.core.MediaSource(compFile)
				clip = hiero.core.Clip(clipSource)
				clipsBin.addItem(hiero.core.BinItem(clip))
				clips.append(clip)

				# turns '/some/path/170_240_v001_ghm.nk' to '170_240'
				clipName = '_'.join(compFile.split('/')[-1].split('.')[0].split('_')[:-2])

				# create the track item
				trackItem = track.createTrackItem(clipName)
				trackItem.setSource(clip)
				trackItem.setTimelineIn(currentTime)
				currentTime += trackItem.sourceDuration()
				trackItem.setTimelineOut(currentTime - 1)
				track.addItem(trackItem)
			except Exception as err:
				print '\nFAILED:', compFile, err

		sequence.addTrack(track)
		sequence.openInTimeline()


def launch(parent=None, *args, **kwargs):
	translator.launch(ImportComps, parent, *args, **kwargs)

if __name__ == '__main__':
	launch()
