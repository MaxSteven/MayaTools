'''
Author: Carlo Cherisier
Date: 09.26.14
Script: createShots
'''
from PySide import QtGui

import arkInit
arkInit.init()

import caretaker
ct = caretaker.getCaretaker()

import os

import translators
translator = translators.getCurrent()


class GUI( QtGui.QDialog):
	'''
	Purpose:
		Contains logic for all Basic GUI Elements
	'''
	def __init__(self, parent=None):
		super(GUI, self).__init__(parent)
		self.create_Window()
		self.setup_Connections()
		self.populate_Widgets()

#------------------- WINDOW CREATION----------------------------------#
	def create_Window( self):
		'''
		Here is where the window
		is created
		'''
		## Window Title
		self.setWindowTitle( 'Create Shots From Directory')

		## Window Settings
		self.setFixedWidth( 250)

		## Set GUI Layouts
		self.mainlayout= QtGui.QVBoxLayout()
		vert_lay = QtGui.QVBoxLayout()

		## Create Combo
		self.driveCombo= QtGui.QComboBox()
		self.driveCombo.addItem( 'r:/')
		vert_lay.addWidget( self.driveCombo)

		## Create List
		self.projectWidget = QtGui.QListWidget()
		vert_lay.addWidget( self.projectWidget)

		## Create Button
		self.createShotButton= QtGui.QPushButton('Create Shots')
		self.createShotButton.setEnabled( 0)
		vert_lay.addWidget( self.createShotButton)

		## Finalize Layout
		self.mainlayout.addLayout( vert_lay)
		self.setLayout( self.mainlayout)

		## Show Gui
		self.show()

#------------------- GUI CONNECTIONS----------------------------------#
	def setup_Connections( self):
		'''
		Purpose:
			Provide all signal connections for GUI window
		'''
		## Select All Section
		self.driveCombo.currentIndexChanged .connect( self.populate_Widgets)

		## Asset Name Section
		self.projectWidget.itemSelectionChanged.connect( self.projectWidget_hasChanged)

		## Alembic Section
		self.createShotButton.clicked.connect( self.createShot_clicked)

#------------------- ADD GUI ElEMENTS----------------------------------#
	def populate_Widgets( self):
		'''
		Purpose:
			Populate List Widget with projects from selected drive
		'''
		## Grab drive
		drive= str( self.driveCombo.currentText())

		folderList= os.listdir( drive)

		## Folder to remove
		removeList=[ 'Assets', 'Users', 'Website', '_DO NOT DELETE THIS OR MATT WILL KILL YOU', 'root', '_Project_Template', 'Production_Manager', 'Promotional_Material', 'Test_Project']

		## Remove folders from list
		for each in removeList:
			if each in folderList:
				folderList.remove( each)

		## Remove files
		projectList=[]
		for each in folderList:
			holder= 1
			## Join item to folder path
			filePath= os.path.join( drive, each)

			## Add anything that is a folder
			if not os.path.isdir( filePath):
				holder= 0

			## Remove hidden folders
			if '.' in each:
				holder= 0

			## Remove matching folders
			if holder:
				projectList.append( each)
		## Sort List
		projectList.sort()

		for each in projectList:
			## Add project folder to list
			self.projectWidget.addItem( each)
	#
	def projectWidget_hasChanged( self):
		'''
		Purpose:
			Turn on or off Button
		'''
		if len(self.projectWidget.selectedItems())== 0:
			self.createShotButton.setEnabled( 0)

		else:
			self.createShotButton.setEnabled( 1)
	#
	def createShot_clicked( self):
		'''
		Purpose:
			Create Shot From Directory
		'''
		## Grab drive
		drive= str( self.driveCombo.currentText())

		## Grab selected project
		folderName= self.projectWidget.selectedItems()[0]
		folderName= folderName.text()

		# call sweet caretaker command
		ct.createShotsFromDirectory( drive+folderName)

		QtGui.QMessageBox.about( None, 'Shot are being created ', 'Shots are being created from Caretaker!!')

def main():
	'''
	Show Window
	'''
	translator.launch( GUI, None)



if __name__ == '__main__':
	main()
