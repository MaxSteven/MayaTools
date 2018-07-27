'''
Author: Carlo Cherisier
Date: 09.26.14
Script: animationLibrary

python.execute("
import sys;
sys.path.append('c:/ie/ark/tools/animationLibrary');
import animationLibraryGUI; reload(animationLibraryGUI); animationLibraryGUI.main();
")
'''
from PySide import QtGui

import arkInit
arkInit.init()

import re
import animationLibraryFUNC as guiFUNC
reload( guiFUNC)

import translators
translator = translators.getCurrent()


class GUI( QtGui.QDialog):
	## Class variables
	storeName = ''

	def __init__(self, parent=None):
		super(GUI, self).__init__(parent)

		## GUI logictions Class
		self.guiFunc = guiFUNC.guiFUNC()
		self.guiFunc.getGuiInformation()

		## Setup GUI
		self.create_Window()
		self.addExtra()
		self.populate_Widgets()
		self.setup_Connections()
		self.show()

#------------------- WINDOW CREATION----------------------------------#
	def create_Window( self):
		'''
		Purpose:
			Contains all GUI widgets
		'''
		## Window Title
		self.setWindowTitle( 'Animation Copy Paste')

		## Window Settings
		self.resize( 450, 300)

		#### Set GUI Layouts
		self.mainlayout = QtGui.QHBoxLayout()
		self.setLayout( self.mainlayout)

		#### Scene Assets List
		groupBox = QtGui.QGroupBox( 'Scene Assets')
		box = QtGui.QVBoxLayout()
		list01 = QtGui.QListWidget()
		groupBox.setLayout( box)
		groupBox.setFixedWidth( 150)
		groupBox.setAlignment( 4)
		box.addWidget( list01)
		self.mainlayout.addWidget( groupBox)

		#### Save Animation
		formLayout  = QtGui.QFormLayout()
		self.mainlayout.addLayout( formLayout)

		label = QtGui.QLabel('Save Name')
		line01 = QtGui.QLineEdit()
		line01.setEnabled( 0)

		button01 = QtGui.QPushButton('Save Animation')
		button01.setEnabled( 0)

		check01 = QtGui.QCheckBox ('Edit Time')

		spin01 = QtGui.QSpinBox()
		spin02 = QtGui.QSpinBox()
		spin01.setFixedWidth( 50)
		spin02.setFixedWidth( 50)
		spin01.setEnabled( 0)
		spin02.setEnabled( 0)

		formLayout.addRow( label)
		formLayout.addRow( line01)
		formLayout.addRow( check01)
		formLayout.addRow( '   In', spin01)
		formLayout.addRow( '   Out', spin02)
		formLayout.addRow( button01)

		#### Saved Animations
		vert_Lay = QtGui.QVBoxLayout()
		groupBox = QtGui.QGroupBox( '')
		box = QtGui.QVBoxLayout()

		label = QtGui.QLabel('Animation Library For:')

		list02 = QtGui.QListWidget()

		button02 = QtGui.QPushButton('Load Animation')
		button03 = QtGui.QPushButton('Delete Select Animation')

		groupBox.setLayout( box)
		groupBox.setAlignment( 4)
		groupBox.setFixedWidth( 200)

		button02.setEnabled( 0)
		button03.setEnabled( 0)

		box.addWidget( label)
		box.addWidget( list02)
		box.addWidget( button02)
		box.addWidget( button03)

		vert_Lay.addWidget( groupBox)
		self.mainlayout.addLayout( vert_Lay)

		## Set Variables
		self.sceneNamespaceList = list01
		self.animLibraryList = list02

		self.assetLabel = label

		self.saveAnimNameLine = line01

		self.saveAnimButton = button01
		self.loadAnimButton = button02
		self.deleteAnimButton = button03

		self.startTime = spin01
		self.endTime = spin02

		self.editTimeCheckBox = check01


#------------------- GUI CONNECTIONS----------------------------------#
	def setup_Connections( self):
		'''
		Purpose:
			Provide all signal connections for GUI window
		'''
		## Asset Name Section
		self.sceneNamespaceList.itemClicked.connect( self.sceneNamespaceList_hasChanged)

		## Name Animation Line
		self.saveAnimNameLine.textChanged.connect( self.saveAnimNameLine_hasChanged)

		## Save Animation
		self.saveAnimButton.clicked.connect( self.saveAnimButton_clicked)

		## Load Animation
		self.loadAnimButton.clicked.connect( self.loadAnimButton_clicked)

		## Edit Time
		self.editTimeCheckBox.stateChanged.connect( self.editTime_clicked)

		## Animation Library
		self.animLibraryList.itemClicked.connect( self.animLibraryList_hasChanged)

		## Delete Saved Animation
		self.deleteAnimButton.clicked.connect( self.deleteAnimButton_clicked)


#------------------- ADD GUI ElEMENTS----------------------------------#
	def addExtra( self):
		'''
		Purpose:
			Grab start and end range of animation scene
		'''
		## Grab time
		timeFrame = self.guiFunc.grabTime()

		## Set min and max values
		self.startTime.setMinimum( timeFrame[0])
		self.endTime.setMaximum( timeFrame[1])

		## Set Value
		self.startTime.setValue( timeFrame[0])
		self.endTime.setValue( timeFrame[1])
	#
	def populate_Widgets( self):
		'''
		Purpose:
			Popuplate Asset Widget with
		Popuplate Name space layout with namespaces in scene
		'''
		for each in sorted(self.guiFunc.namespace_List):
			## Check if asset is still in the scene
			if translator.namespaceExists( each) == True:
				## Add items
				self.sceneNamespaceList.addItem( each)

#------------------- GUI SIGNALS----------------------------------#
	def sceneNamespaceList_hasChanged( self):
		'''
		Purpose:
			Turn on or off Save Animation Name
		'''
		if len(self.sceneNamespaceList.selectedItems())== 0:
			self.saveAnimNameLine.setEnabled( 0)
			self.saveAnimButton.setEnabled( 0)
			self.animLibraryList.setEnabled( 0)

		else:
			## Grab selected asset
			namespace= str(self.sceneNamespaceList.selectedItems()[0].text())

			if self.storeName != namespace[:-3]:
				self.storeName = namespace[:-3]

				self.animLibraryList.clear()
				self.saveAnimNameLine.setEnabled( 1)
				self.animLibraryList.setEnabled( 1)

				## Check if asset has saved animation files
				animFiles = self.guiFunc.searchAnimationLibrary( namespace)

				if animFiles != False:
					for each in animFiles:
						## Add to list
						self.animLibraryList.addItem( each)
	#
	def animLibraryList_hasChanged( self):
		'''
		Purpose:
			Turn on or off Delete Animation button
		'''
		if len(self.animLibraryList.selectedItems()) == 0:
			self.deleteAnimButton.setEnabled( 0)
			self.loadAnimButton.setEnabled( 0)

		else:
			self.deleteAnimButton.setEnabled( 1)
			self.loadAnimButton.setEnabled( 1)
	#
	def saveAnimNameLine_hasChanged( self):
		'''
		Purpose:
			Turn on or off Save Animation Button
			If name has been given
		'''
		data = self.saveAnimNameLine.text()

		## Check if notes are left
		check = bool( re.findall( '[\100-\177]+', data))

		if check == True:
			self.saveAnimButton.setEnabled( 1)

		else:
			self.saveAnimButton.setEnabled( 0)
	#
	def editTime_clicked( self):
		'''
		Purpose:
			Enable or disable edit time range
		'''
		if self.editTimeCheckBox.isChecked():
			self.startTime.setEnabled( 1)
			self.endTime.setEnabled( 1)

		else:
			self.startTime.setEnabled( 0)
			self.endTime.setEnabled( 0)
	#
	def saveAnimButton_clicked( self):
		'''
		Purpose:
			Saved animation for selected Assets
		'''
		if len(self.sceneNamespaceList.selectedItems()) == 0:
			return

		## Close window
		self.close()

		## Grab selected project
		namespace = str( self.sceneNamespaceList.selectedItems()[0].text())

		## Grab New Asset Name
		animationName = str(self.saveAnimNameLine.text())

		## Prepare asset to save Animation
		result = self.guiFunc.selectAnimationCtrls( namespace)
		print result, animationName, namespace

		if result == True:
			## Create asset animation folder
			self.guiFunc.createAnimationFolder( namespace[:-3])

			## Save Animation
			self.guiFunc.saveAnimation( namespace, animationName)

			## Updated Animation Library Widget
			self.sceneNamespaceList_hasChanged()
	#
	def loadAnimButton_clicked( self):
		'''
		Puropse:
			Load saved animation onto selected asset
		'''
		if len(self.animLibraryList.selectedItems()) == 0 and len(self.sceneNamespaceList.selectedItems()) == 0:
			return

		## Grab selected asset
		namespace = str( self.sceneNamespaceList.selectedItems()[0].text())

		## Grab selected animation
		savedAnimation = str( self.animLibraryList.selectedItems()[0].text())

		## Message to user
		text = 'Are you sure you want to load {0} onto {1}?'.format( savedAnimation, namespace)

		result = QtGui.QMessageBox.question(self, 'Message', text,
			QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)

		if result != QtGui.QMessageBox.Yes:
			return

		## Prepare asset to save Animation
		result = self.guiFunc.selectAnimationCtrls( namespace)

		if result == True:
			## Delete Animation
			self.guiFunc.loadAnimation( namespace, savedAnimation)
	#
	def deleteAnimButton_clicked( self):
		'''
		Puropse:
			Delete Saved Animation File
		'''
		if len(self.animLibraryList.selectedItems()) == 0:
			return
		## Grab selected project
		savedAnimation = str( self.animLibraryList.selectedItems()[0].text())

		text = 'Are you sure you want to delete {0}?'.format( savedAnimation)

		result = QtGui.QMessageBox.question(self, 'Message', text,
			QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)

		if result == QtGui.QMessageBox.Yes:
			## Delete Animation
			self.guiFunc.deleteAnimationFile( savedAnimation)


def main():
	'''
	Show Window
	'''
	translator.launch( GUI, None)



if __name__ == '__main__':
	main()
