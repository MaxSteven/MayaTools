'''
Author: Carlo Cherisier
Date: 08.25.14
Script: smartOpen

python.execute("
import sys;
sys.path.append('c:/ie/ark/tools/smartTools');
import smartOpen; reload(smartOpen); smartOpen.main();
")
'''
import arkInit
arkInit.init()

import translators
translator = translators.getCurrent()

from translators import QtGui, QtCore

import smartTools_Elements
reload( smartTools_Elements)

import sys, os, os.path, shutil
sys.path.append( 'c:/ie/ark/tools/dataDecoder')
import dataDecoder


class UpdateList( QtGui.QDialog):
	def __init__(self, parent= None, *args):
		super( UpdateList, self).__init__(parent)
		namespaceList = args

		sys.path.append('c:/ie/ark/tools/publishTools/viewAsset');
		import viewAssetFUNC
		reload( viewAssetFUNC)
		self.viewAssetFUNC = viewAssetFUNC.guiFunc()
		self.viewAssetFUNC.getGuiInformation()

		## Setup GUI
		self.create_Window()
		self.setup_Connections()

		## Add to List
		self.updateAssetList.addItems( namespaceList)
	#
	def create_Window( self):
		'''
		Purpose:
			Contains window elements
		'''
		## Window Title
		self.setWindowTitle( 'Update Assets')

		## Window Settings
		#self.setMinimumSize( 1000, 200)
		if translator.getProgram() == 'Maya':
			self.resize( 250, 300)
		else:
			self.resize( 150, 300)

		## Set GUI Layouts
		self.guiLayout= QtGui.QHBoxLayout()
		self.setLayout( self.guiLayout)

		## Asset Update Section
		groupBox, self.updateAssetList = smartTools_Elements.make_listWidget( 'Asset To Update List', 100)
		self.updateAssetList.setSelectionMode( QtGui.QAbstractItemView.ExtendedSelection)
		self.guiLayout.addWidget( groupBox)
		#--------------------------------#

		## Button Section
		boxLayout = QtGui.QVBoxLayout()
		qButton01 = QtGui.QLabel( 'Update')
		qButton01 = QtGui.QPushButton('All')
		qButton02 = QtGui.QPushButton('Selected')
		qButton03 = QtGui.QPushButton('Cancel')
		boxLayout.addWidget( qButton01)
		boxLayout.addWidget( qButton02)
		boxLayout.addWidget( qButton03)

		self.guiLayout.addLayout( boxLayout)

		self.updateAllButton = qButton01
		self.updateSelectedButton = qButton02
		self.cancelButton = qButton03

		## Show Gui
		self.show()


	#------------------- GUI FUNCTIONS----------------------------------#
	def setup_Connections( self):
		'''
		Purpose:
			Connect all GUI Elements to desired functions
		'''
		##Project
		self.updateAllButton.clicked.connect( self.updateAll)
		self.updateSelectedButton.clicked.connect( self.updateSelected)
		self.cancelButton.clicked.connect( self.cancelAll)

	#------------------- GUI SIGNALS----------------------------------#
	def updateAll( self):
		namespaceList= []
		for i in range( self.updateAssetList.count()):
			name= str( self.updateAssetList.item( i).text())
			namespaceList.append( name)

		self.viewAssetFUNC.checkAssetForUpdates( namespaceList)
		self.close()
	#
	def updateSelected( self):
		assetList = self.updateAssetList.selectedItems()

		namespaceList = [each.text() for each in assetList]
		self.viewAssetFUNC.checkAssetForUpdates( namespaceList)
	#
	def cancelAll( self):
		self.close()
	#
	def completedMessage( self):
		QtGui.QMessageBox.warning( None, 'Updated!', 'Assets have been updated!')


class GUI( QtGui.QDialog):

	def __init__(self, parent=None):
		super(GUI, self).__init__(parent)

		##Class Variables
		self.projName = None
		self.deptName = None
		self.assetName = None
		self.fileName = None

		## Setup GUI
		self.create_Window()
		smartTools_Elements.populate_localDrive( self.locaDrive_Combo)
		smartTools_Elements.populate_Projects( self.project_Widget)
		smartTools_Elements.populate_Deparments( self.department_Widget, 2)
		self.setup_Connections()

		##Retrieve Global Variables
		guiInfo = smartTools_Elements.get_dataForGUI()

		if guiInfo!= None:
			localDrive = guiInfo[0]
			projName = guiInfo[1]
			deptName = guiInfo[2]
			assetName = guiInfo[3]

		else:
			localDrive= dataDecoder.get_smartData( 'localDrive')
			projName= dataDecoder.get_smartData( 'projName')
			deptName= dataDecoder.get_smartData( 'deptName')
			assetName= dataDecoder.get_smartData( 'assetName')

		if projName != None:
			## Set GUI Elements
			smartTools_Elements.select_guiItem( self.locaDrive_Combo, localDrive, mode= 'localDrive')
			smartTools_Elements.select_guiItem( self.project_Widget, projName)
			smartTools_Elements.select_guiItem( self.department_Widget, deptName)
			smartTools_Elements.select_guiItem( self.assetName_Widget, assetName)

			## Set Asset Path
			smartTools_Elements.create_guiPath( projName, deptName, assetName)

			## Populate Asset Versions
			self.updateAssetName()

			## Select newest file
			self.assetVersion_Widget.setCurrentCell( 0, 0)
			self.assetVersion_Widget.setFocus()

			## Location
			fileName= str(self.assetVersion_Widget.item( 0, 0).text())
			location= str(self.assetVersion_Widget.item( 0, 1).text())

			## Grab Asset Version number
			version = 'v'+ fileName.split( '_v')[-1].split( '_')[0]

			## Asset Notes
			result = dataDecoder.get_assetNotes( location, self.projName, self.deptName, self.assetName, version, localDrive)

			if result!= None:
				## Set Asset Notes
				self.userName_Widget.setText( result[0])
				self.assetNotes_Widget.setText( result[1])

#------------------- WINDOW CREATION----------------------------------#
	def create_Window( self):
		'''
		Purpose:
			Contains window elements
		'''
		## Window Title
		self.setWindowTitle( 'Smart Open')

		## Window Settings
		#self.setMinimumSize( 1000, 200)
		if translator.getProgram() == 'Maya':
			self.setFixedWidth( 1150)
		else:
			self.setFixedWidth( 1050)

		## Set GUI Layouts
		self.guiLayout= QtGui.QVBoxLayout()
		self.setLayout( self.guiLayout)

		#### Local Drive Section ####
		formlay= QtGui.QFormLayout()
		self.locaDrive_Combo= QtGui.QComboBox()
		self.locaDrive_Combo.setFixedWidth( 50)

		## Add To Layout
		formlay.addRow( 'Select Local Drive', self.locaDrive_Combo)
		self.guiLayout.addLayout( formlay)
		#--------------------------------#

		## Make Second Layout for GUI
		hLayout = QtGui.QHBoxLayout()
		self.guiLayout.addLayout( hLayout)
		#--------------------------------#

		## Project Section
		groupBox, self.project_Widget= smartTools_Elements.make_listWidget( 'Project List')
		hLayout.addWidget( groupBox)
		#--------------------------------#

		## Department Section
		groupBox, self.department_Widget= smartTools_Elements.make_listWidget( 'Departments', 110)
		hLayout.addWidget( groupBox)
		#--------------------------------#

		## Asset Name Section
		groupBox, self.assetName_Widget= smartTools_Elements.make_listWidget( 'Asset Name', 150)
		hLayout.addWidget( groupBox)
		#--------------------------------#

		## Asset Version and Open File Section
		groupBox, self.assetVersion_Widget, returnLayout= smartTools_Elements.make_tableWidget( 'Asset Versions', returnLayout= True)
		hLayout.addWidget( groupBox)

		## Create Open button
		horizontal_lay = QtGui.QHBoxLayout()
		qButton01= QtGui.QPushButton('Open File')
		qButton02= QtGui.QPushButton('Latest File')

		## Disable use
		qButton01.setEnabled( 0)
		qButton02.setEnabled( 0)
		qButton01.setFixedHeight( 40)
		qButton02.setFixedHeight( 40)

		## Save layout
		horizontal_lay.addWidget( qButton01)
		horizontal_lay.addWidget( qButton02)

		returnLayout.addLayout( horizontal_lay)
		self.open_Button= qButton01
		self.openLatest_Button= qButton02
		#--------------------------------#

		## User Info and Comment Section
		groupBox, self.userName_Widget, self.assetNotes_Widget= smartTools_Elements.make_notesWidget( 'Asset Notes')
		hLayout.addWidget( groupBox)
		self.assetNotes_Widget.setEnabled( 0)
		#--------------------------------#

		## Show Gui
		self.show()


#------------------- GUI FUNCTIONS----------------------------------#
	def setup_Connections( self):
		'''
		Purpose:
			Connect all GUI Elements to desired functions
		'''
		##Project
		self.project_Widget.itemSelectionChanged.connect( self.updateProject)

		## Department
		self.department_Widget.itemSelectionChanged.connect( self.updateDepartment)

		##Asset Name
		self.assetName_Widget.itemSelectionChanged.connect( self.updateAssetName)
		self.assetName_Widget.itemDoubleClicked.connect( self.openLatest_clicked)

		## Asset Version
		self.assetVersion_Widget.itemSelectionChanged.connect( self.assetVersion_itemClicked)
		self.assetVersion_Widget.itemDoubleClicked.connect( self.openButton_clicked)

		## Open Button
		self.open_Button.clicked.connect( self.openButton_clicked)

		## Open Latest Button
		self.openLatest_Button.clicked.connect( self.openLatest_clicked)
	#
	def resetGUI( self, mode=''):
		'''
		Reset Open Button
		'''
		## Turn Off Button
		self.open_Button.setEnabled( 0)

		if mode== 0:
			##Clear Widgets
			self.assetName_Widget.clear()
			self.assetVersion_Widget.setRowCount(0)
			self.openLatest_Button.setEnabled( 0)

			self.assetName= None
			self.assetVersion= None

		if mode== 1:
			##Clear Widgets
			self.assetVersion_Widget.setRowCount(0)
			self.openLatest_Button.setEnabled( 1)

			self.fileName= None

		## Clear Notes Widget
		self.assetNotes_Widget.clear()


#------------------- GUI SIGNALS----------------------------------#
	def updateProject( self):
		'''
		Connect Widget Signals to functions
		'''
		## Reset GUI
		self.resetGUI( 0)

		## Grab Widget Info
		self.projName= self.project_Widget.currentItem().text()

		if bool( self.department_Widget.currentItem()) :
			self.deptName= str(self.department_Widget.currentItem().text())

			## Save Asset Path
			smartTools_Elements.create_guiPath( self.projName, self.deptName)

			## Populate widget
			smartTools_Elements.populate_assetName( self.assetName_Widget)
	#
	def updateDepartment( self):
		'''
		Connect Widget Signals to functions
		'''
		if len(self.project_Widget.selectedItems())== 0:
			return

		## Grab Widget Info
		name= str(self.department_Widget.currentItem().text())

		## List
		list01=[ 'Rig', 'Model', 'Lighting Asset', 'FX Asset']
		list02=[ 'Anim Scene', 'Lighting Scene', 'FX Scene']

		if self.deptName in list01 and name in list01 :
			self.deptName= name
			self.updateAssetName()
			return
		elif self.deptName in list02 and name in list02:
			self.deptName= name
			self.updateAssetName()
			return

		## Reset GUI
		self.resetGUI( 0)
		self.deptName= name

		## Save Asset Path
		smartTools_Elements.create_guiPath( self.projName, self.deptName)

		## Populate widget
		smartTools_Elements.populate_assetName( self.assetName_Widget)
	#
	def updateAssetName( self):
		'''
		Connect Widget Signals to functions
		'''
		if len(self.department_Widget.selectedItems())== 0 or  len(self.assetName_Widget.selectedItems())== 0:
			return
		## Reset GUI
		self.resetGUI( 1)

		## Turn On Button
		self.openLatest_Button.setEnabled( 1)

		self.assetName= str(self.assetName_Widget.currentItem().text())

		## Grab and Set Local Drive
		localDrive= str( self.locaDrive_Combo.currentText())

		## Save Asset Path
		smartTools_Elements.create_guiPath( self.projName, self.deptName, self.assetName)

		## Populate widget
		smartTools_Elements.populate_assetVersion( self.assetVersion_Widget, self.assetName, localDrive)
	#
	def assetVersion_itemClicked( self):
		'''
		Connect Widget Signals to functions
		'''
		## Turn On Button
		self.open_Button.setEnabled( 1)

		## Clear Asset Notes Widget
		self.userName_Widget.clear()
		self.assetNotes_Widget.clear()

		##Grab selected fileName
		selectedRow= self.assetVersion_Widget.selectionModel().selectedRows()[0].row()

		## Grab Widget Info
		self.fileName= str(self.assetVersion_Widget.item( selectedRow, 0).text())

		## Location
		location= str(self.assetVersion_Widget.item( selectedRow, 1).text())

		## Grab Asset Version number
		version= 'v'+ self.fileName.split( '_v')[-1].split( '_')[0]

		## Grab Local Drive
		localDrive= str( self.locaDrive_Combo.currentText())

		## Asset Notes
		result= dataDecoder.get_assetNotes( location, self.projName, self.deptName, self.assetName, version, localDrive)

		if result!= None:
			## Set Asset Notes
			self.userName_Widget.setText( result[0])
			self.assetNotes_Widget.setText( result[1])
	#
	def openLatest_clicked( self):
		'''
		Purpose:
			Open newest file
		'''
		## Grab Widget Info
		self.fileName= str(self.assetVersion_Widget.item( 0, 0).text())

		self.openButton_clicked()
	#
	def openButton_clicked( self):
		'''
		Purpose:
			Opens file in scene and saves file in data
		'''
		## Close window
		self.close()

		## Grab Local Drive
		localDrive= str( self.locaDrive_Combo.currentText())

		## Store data on file
		dataDecoder.store_smartData( drive= localDrive)
		dataDecoder.store_smartData( projName= self.projName)
		dataDecoder.store_smartData( deptName= self.deptName)
		dataDecoder.store_smartData( assetName= self.assetName)
		dataDecoder.store_smartData( fileName= self.fileName)

		## Store data in scene
		translator.setData( 'smart_localDrive', localDrive)
		translator.setData( 'smart_projName', self.projName)
		translator.setData( 'smart_deptName', self.deptName)
		translator.setData( 'smart_assetName', self.assetName)
		translator.setData( 'smart_fileName', self.fileName)
		print 'Data has been set.'

		versionNum= 'v'+ self.fileName.split( '_v')[-1].split( '_')[0]
		translator.setData( 'smart_fileVersion', versionNum)

		## Save Asset Path
		global_filePath= smartTools_Elements.create_guiPath( self.projName, self.deptName, self.assetName, self.fileName)

		## Copy file and/ or folder to local directory
		local_filePath= self.create_LocalFolder( global_filePath, localDrive)

		## Open Selected File from Local Drive
		translator.openFile( local_filePath)

		dept_List =[ 'Anim Scene', 'Lighting Scene', 'FX Scene']
		if any( each in self.deptName for each in dept_List):
			return self.findNewPublishes( self.projName, self.deptName, self.assetName)
	#
	def findNewPublishes( self, projKey, deptKey, assetKey):
		'''
		Purpose:
			Check if assets in scene have new published version
		'''
		## Function Variables
		foundList = []

		## Grab scene info
		publishInfo_Dict = dataDecoder.get_sceneAssetData( projKey, deptKey, assetKey)['publish']

		for each in publishInfo_Dict.keys():
			## Grab version number and publish department
			assetName, deptName, currentVersion= publishInfo_Dict[ each].split( '**')

			## Path to publish folder
			publishFolder= 'r:/{0}/Project_Assets/{1}/Published/{2}'.format( projKey, assetName, deptName)

			## Grab folder in list
			folder = sorted( os.listdir( publishFolder))[-1]

			if folder> currentVersion:
				foundList.append( each)

		if foundList != []:
			global updateGUI
			updateGUI = UpdateList( None, *foundList)


#------------------- EXTRA FUNCTIONS----------------------------------#
	def create_LocalFolder( self, global_filePath, localDrive):
		'''
		Purpose:
			Create local folder structer and copy file to local drive
		'''
		local_filePath= global_filePath.replace( 'r:', '{0}ie/projects'.format( localDrive))
		local_folderPath= os.path.split( local_filePath)[0]

		## Check if folder exist
		if not os.path.exists( local_folderPath):
			## Make Folder Structure
			os.makedirs( local_folderPath)

		## Check if file exist
		if not os.path.exists( local_filePath):
			if os.path.exists( global_filePath):
				## Copy file from network to local drive
				shutil.copyfile( global_filePath, local_filePath)

		## Store Local
		return( local_filePath)

#------------------- CALL GUI----------------------------------#
def main():
	'''
	Show Window
	'''
	translator.launch( GUI, None)


if __name__ == '__main__':
    main()
