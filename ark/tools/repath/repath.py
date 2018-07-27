'''
Author: Carlo Cherisier
Date: 10.13.14
Script: repath
'''
import arkInit
arkInit.init()

import translators
translator = translators.getCurrent()
from keyCommands import Command

from translators import QtGui

class Repath(QtGui.QDialog):
	'''
	This will be the code for all the Import QtGui elements
	'''

	def __init__(self, parent = None, **kwargs):
		super(Repath, self).__init__(parent)
		self.setModal(True)

		translator.setArgs(kwargs)

		# fix: houdini needs this or it won't show the dialog, figure out why
		self.commands = {}
		newCommand = Command('repath', self.repath, 'return')
		self.commands[newCommand.shortcut] = newCommand

		## Setup GUI
		self.createWindow()
		self.setupConnections()
		self.show()

#------------------- WINDOW CREATION----------------------------------#
	def createWindow(self):
		'''
		Contains window elements
		'''
		# Window Title
		self.setWindowTitle('Repath')

		# Window Settings
		self.setFixedWidth(150)

		## Set GUI Layouts
		self.guiLayout = QtGui.QVBoxLayout()
		self.guiLayout.addStretch(1)
		self.setLayout(self.guiLayout)

		# Line Edit
		formLayout = QtGui.QFormLayout()
		self.sourcePath = QtGui.QLineEdit()
		self.destinationPath = QtGui.QLineEdit()

		## Set Line Values
		self.sourcePath.setText('Q:')
		self.destinationPath.setText('R:')

		## Button
		self.executeButton = QtGui.QPushButton('Execute')

		## Add To Layout
		formLayout.addRow('Change', self.sourcePath)
		formLayout.addRow('To', self.destinationPath)
		formLayout.addRow('', self.executeButton)
		self.guiLayout.addLayout(formLayout)

#------------------- GUI FUNCTIONS----------------------------------#
	def setupConnections(self):
		'''
		Connect all GUI Elements to desired functions
		'''
		#Project
		self.executeButton.clicked.connect(self.repath)

#------------------- GUI SIGNALS----------------------------------#
	def repath(self):
		'''
		Repath file textures from destination to source
		'''
		self.close()

		# Grab source path
		destinationPath = str(self.destinationPath.text()).lower()

		# Grab destination path
		sourcePath = str(self.sourcePath.text()).lower()

		# Repath all
		translator.repath(sourcePath, destinationPath)

		QtGui.QMessageBox.about(
			None,
			'All Files Repathed',
			'All Files have been repathed from {0} to {1}'.format(destinationPath, sourcePath))



def main(parent=None, *args, **kwargs):
	'''
	Show Window
	'''
	return translator.launch(Repath, parent, *args, **kwargs)

if __name__ == '__main__':
	main()
