import os

import arkInit
arkInit.init()

# import ieOS
import cOS
import settingsManager
globalSettings = settingsManager.globalSettings()
import translators
translator = translators.getCurrent()
from keyCommands import Command

from translators import QtGui, QtCore


class ShotManager(QtGui.QDialog):

	def __init__(self, parent=None, **kwargs):
		super(ShotManager, self).__init__(parent)
		# translator.setArgs(kwargs)

		self.ext = None

		# parameterize stuff like this
		height = 500
		panelWidth = 200
		padding = 10

		# setTimeout example
		# from threading import Timer
		# def example(arg1,arg2):
		#     print arg1
		#     print arg2

		# r = Timer(1.0, example, ('arg1','arg2'))
		# r.start()

		form = QtGui.QFormLayout()
		form.setLabelAlignment(QtCore.Qt.AlignLeft)
		form.setVerticalSpacing(padding)

		hBox = QtGui.QHBoxLayout()

		self.projectSelector = QtGui.QListWidget()
		self.projectSelector.itemDoubleClicked.connect(self.exploreProject)
		self.projectSelector.currentItemChanged.connect(self.projectProgress)
		hBox.addWidget(self.projectSelector)

		self.shotSelector = QtGui.QListWidget()
		self.shotSelector.itemDoubleClicked.connect(self.exploreShot)
		self.shotSelector.currentItemChanged.connect(self.shotProgress)
		hBox.addWidget(self.shotSelector)

		self.deptSelector = QtGui.QListWidget()
		self.deptSelector.itemDoubleClicked.connect(self.exploreDept)
		self.deptSelector.currentItemChanged.connect(self.deptProgress)
		hBox.addWidget(self.deptSelector)

		self.versionSelector = QtGui.QListWidget()
		self.versionSelector.itemDoubleClicked.connect(self.fileDoubleClicked)
		self.versionSelector.currentItemChanged.connect(self.versionProgress)
		hBox.addWidget(self.versionSelector)

		form.addRow(hBox)

		self.setLayout(form)
		self.setDefaults()

		self.prevSelector = {self.projectSelector: self.projectSelector, self.shotSelector: self.projectSelector, self.deptSelector: self.shotSelector, self.versionSelector: self.deptSelector}
		self.nextSelector = {self.projectSelector: self.shotSelector, self.shotSelector: self.deptSelector, self.deptSelector: self.versionSelector, self.versionSelector: self.versionSelector}

		self.commands = {}
		self.keyCodes = {}
		for enum in dir(QtCore.Qt):
			if 'Key_' in enum:
				self.keyCodes[int(getattr(QtCore.Qt,enum))] = enum.replace('Key_','').lower()

		newCommand = Command('progress', self.progress, 'right')
		self.commands[newCommand.shortcut] = newCommand
		newCommand = Command('regress', self.regress, 'left')
		self.commands[newCommand.shortcut] = newCommand

		newCommand = Command('submit', self.submit, 'enter')
		self.commands[newCommand.shortcut] = newCommand
		newCommand = Command('submit', self.submit, 'return')
		self.commands[newCommand.shortcut] = newCommand


		self.setWindowTitle('Shot Manager')
		self.name = 'ShotManager'
		self.show()
		self.resize(panelWidth * 4, height)

	def progress(self):
		newWidget = self.nextSelector[self.focusWidget()]
		newWidget.setFocus()
		newWidget.setCurrentItem(newWidget.currentItem())

	def regress(self):
		newWidget = self.prevSelector[self.focusWidget()]
		newWidget.setFocus()
		newWidget.setCurrentItem(newWidget.currentItem())

	def resizeEvent(self, event=None):
		height = event.size().height() - 20
		self.versionSelector.resize(self.versionSelector.width(), height)
		self.deptSelector.resize(self.deptSelector.width(), height)
		self.shotSelector.resize(self.shotSelector.width(), height)
		self.projectSelector.resize(self.projectSelector.width(), height)

	def setDefaults(self):
		if not globalSettings.ARK_CURRENT_APP:
			for name in os.listdir('r:/'):
				if os.path.isdir(os.path.join('r:/', name)):
					self.projectSelector.addItem(name)
			self.projectSelector.sortItems()
			self.projectSelector.setFocus()

		else:
			self.getSubDirs('r:/', self.projectSelector)
			self.projectSelector.sortItems()
			try:
				currFile = translator.getFilename().replace('\\', '/')
				print 'Current File: ', currFile
				self.ext = cOS.getExtension(currFile)
				parts = currFile.split('/')
				print 'Ext: ', self.ext
				print 'Parts: ', parts
				self.projectSelector.setCurrentItem(self.projectSelector.findItems(parts[1], QtCore.Qt.MatchFlag.MatchFixedString)[0])
				self.getSubDirs('/'.join(parts[:3]) + '/', self.shotSelector)
				self.shotSelector.setCurrentItem(self.shotSelector.findItems(parts[3], QtCore.Qt.MatchFlag.MatchFixedString)[0])
				self.getSubDirs('/'.join(parts[:4]) + '/', self.deptSelector)
				self.deptSelector.setCurrentItem(self.deptSelector.findItems(parts[4], QtCore.Qt.MatchFlag.MatchFixedString)[0])
				self.getSubDirs('/'.join(parts[:5]) + '/', self.versionSelector)
				self.versionSelector.setCurrentItem(self.versionSelector.findItems(parts[5], QtCore.Qt.MatchFlag.MatchFixedString)[0])
				self.shotSelector.setFocus()
			except:
				pass

	def projectProgress(self, item):

		if item:

			self.shotSelector.clear()
			self.deptSelector.clear()
			self.versionSelector.clear()

			currDirWorkspaces = 'r:/' + item.text() + '/Workspaces/'
			currDirPA = 'r:/' + item.text() + '/Project_Assets/'

			self.getSubDirs(currDirWorkspaces, self.shotSelector)
			self.getSubDirs(currDirPA, self.shotSelector)

			self.shotSelector.sortItems()

	def shotProgress(self, item):


		if item:
			deptItem = None
			if (self.deptSelector.currentItem()):
				deptItem = self.deptSelector.currentItem().text()

			self.deptSelector.clear()
			self.versionSelector.clear()

			currDirWorkspaces = 'r:/' + self.projectSelector.currentItem().text() + '/Workspaces/' + item.text() + '/'
			currDirPA = 'r:/' + self.projectSelector.currentItem().text() + '/Project_Assets/' + item.text() + '/'

			self.getSubDirs(currDirWorkspaces, self.deptSelector)
			self.getSubDirs(currDirPA, self.deptSelector)

			self.deptSelector.sortItems()

			if (deptItem):
				self.deptSelector.setCurrentItem(self.deptSelector.findItems(deptItem, QtCore.Qt.MatchFlag.MatchFixedString)[0])
				self.deptProgress(self.deptSelector.currentItem())

	def deptProgress(self, item):

		if item:

			self.versionSelector.clear()

			currDirWorkspaces = 'r:/' + self.projectSelector.currentItem().text() + '/Workspaces/' + self.shotSelector.currentItem().text() + '/' + item.text() + '/'
			currDirPA = 'r:/' + self.projectSelector.currentItem().text() + '/Project_Assets/' + self.shotSelector.currentItem().text() + '/' + item.text() + '/'

			self.getFiles(currDirWorkspaces, self.versionSelector)
			self.getFiles(currDirPA, self.versionSelector)
			self.versionSelector.setCurrentItem(self.versionSelector.item(0))

	def exploreProject(self, item):

		filePath = 'r:/' + item.text()

		os.system('explorer ' + filePath.replace('/', '\\'))

	def exploreShot(self, item):

		filePath = 'r:/' + self.projectSelector.currentItem().text() + '/Workspaces/' + item.text() + '/'
		if not os.path.isdir(filePath):
			filePath = 'r:/' + self.projectSelector.currentItem().text() + '/Project_Assets/' + item.text() + '/'

		os.system('explorer ' + filePath.replace('/', '\\'))

	def exploreDept(self, item):

		filePath = 'r:/' + self.projectSelector.currentItem().text() + '/Workspaces/' + self.shotSelector.currentItem().text() + '/' + item.text() + '/'
		if not os.path.isdir(filePath):
			filePath = 'r:/' + self.projectSelector.currentItem().text() + '/Project_Assets/' + self.shotSelector.currentItem().text() + '/' + item.text() + '/'

		os.system('explorer ' + filePath.replace('/', '\\'))

	def versionProgress(self):
		pass

	def getSubDirs(self, directory, selector):
		if (os.path.isdir(directory)):
			for name in os.listdir(directory):
				if os.path.isdir(directory + name):
					selector.addItem(name)

	def getFiles(self, directory, selector):

		files = {}
		times = []
		if (os.path.isdir(directory)):
			for name in os.listdir(directory):
				if os.path.isfile(directory + name) and (not self.ext or self.ext == cOS.getExtension(name)):
					files[os.path.getmtime(directory + name)] = name
					times.append(os.path.getmtime(directory + name))
		times = list(reversed(sorted(times)))
		for i in times:
			selector.addItem(files[i])


	def fileDoubleClicked(self, item):

		filePath = 'r:/' + self.projectSelector.currentItem().text() + '/Workspaces/' + self.shotSelector.currentItem().text() + '/' + self.deptSelector.currentItem().text() + '/' + item.text()
		if not os.path.isfile(filePath):
			filePath = 'r:/' + self.projectSelector.currentItem().text() + '/Project_Assets/' + self.shotSelector.currentItem().text() + '/' + self.deptSelector.currentItem().text() + '/' + item.text()


		self.openFile(filePath)

	def keyPressEvent(self, e):
		if e.key() not in self.keyCodes:
			return

		shortcut = self.keyCodes[e.key()]

		if shortcut in self.commands:
			self.commands[shortcut].execute()

	def submit(self):

		if self.projectSelector.currentItem() and self.shotSelector.currentItem() and self.deptSelector.currentItem() and self.versionSelector.currentItem():
			filePath = 'r:/' + self.projectSelector.currentItem().text() + '/Workspaces/' + self.shotSelector.currentItem().text() + '/' + self.deptSelector.currentItem().text() + '/' + self.versionSelector.currentItem().text()
			if not os.path.isfile(filePath):
				filePath = 'r:/' + self.projectSelector.currentItem().text() + '/Project_Assets/' + self.shotSelector.currentItem().text() + '/' + self.deptSelector.currentItem().text() + '/' + self.versionSelector.currentItem().text()

		self.openFile(filePath)

	def openFile(self, filePath):

		if not globalSettings.ARK_CURRENT_APP:
			os.system('explorer ' + filePath.replace('/', '\\'))
		elif translator.isFileDirty():

			msg = QtGui.QMessageBox()
			msg.setWindowTitle('Do you want to save?')
			msg.setText('Selecting \'No\' will delete all unsaved changes.')

			msg.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel)
			msg.setDefaultButton(QtGui.QMessageBox.Cancel)

			res = msg.exec_()

			if res == QtGui.QMessageBox.Yes:
				translator.saveFile()
				translator.openFile(filePath)
			elif res == QtGui.QMessageBox.No:
				translator.openFile(filePath)
		else:
			translator.openFile(filePath)

def launch(parent=None, *args, **kwargs):
	print globalSettings.ARK_CURRENT_APP
	translator.launch(ShotManager, parent, *args, **kwargs)

if __name__ == '__main__':
	launch()
