'''
Author: Carlo Cherisier
Date: 09.2.14
Script: smartSave

python.execute("
import sys;
sys.path.append('c:/ie/ark/tools/smartTools/');
import smartSave; reload(smartSave); smartSave.main();
")

'''
from PySide import QtGui, QtCore
from PySide.QtCore import Qt

import arkInit
arkInit.init()

import translators
translator = translators.getCurrent()

import smartTools_Elements
reload( smartTools_Elements)

import sys, re, os.path, shutil
sys.path.append( 'c:/ie/ark/tools/dataDecoder')
import dataDecoder

from functools import partial

class GUI( QtGui.QDialog):
	'''
	Purpose:
		Contains window elements
	'''
	def __init__(self, parent=None):
		super( GUI, self).__init__(parent)

		##Class Variables
		self.projName= None
		self.deptName= None
		self.assetName= None
		self.assetVersion= None
		self.saveLine_Elements=[]
		self.saveLocation= 'local'
		self.saveMode_newFile= 0

		## Setup GUI
		self.create_Window()
		smartTools_Elements.populate_localDrive( self.locaDrive_Combo)
		smartTools_Elements.populate_Projects( self.project_Widget)
		smartTools_Elements.populate_Deparments( self.department_Widget, 2)
		self.setup_Connections()

		##Retrieve Global Variables
		guiInfo= smartTools_Elements.get_dataForGUI()
		if guiInfo!= None:
			localDrive= guiInfo[0]
			projName= guiInfo[1]
			deptName= guiInfo[2]
			assetName= guiInfo[3]

		else:
			localDrive= dataDecoder.get_smartData( 'localDrive')
			projName= dataDecoder.get_smartData( 'projName')
			deptName= dataDecoder.get_smartData( 'deptName')
			assetName= dataDecoder.get_smartData( 'assetName')

		if localDrive != None:
			## Set GUI Elements
			smartTools_Elements.select_guiItem( self.locaDrive_Combo, localDrive, mode= 'localDrive')
			smartTools_Elements.select_guiItem( self.project_Widget, projName)
			smartTools_Elements.select_guiItem( self.department_Widget, deptName)
			smartTools_Elements.select_guiItem( self.assetName_Widget, assetName)

			## Set Asset Path
			# print projName, deptName, assetName
			smartTools_Elements.create_guiPath( projName, deptName, assetName)

#------------------- WINDOW CREATION----------------------------------#
	def create_Window( self):
		'''
		Purpose:
			Contains window elements
		'''
		## Window Title
		self.setWindowTitle( 'Smart Save')

		## Window Settings
		#self.setMinimumSize( 1000, 200)
		self.setFixedWidth( 1150)

		## Set GUI Layouts
		self.guiLayout= QtGui.QVBoxLayout()
		self.guiLayout.addStretch(1)
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
		groupBox, self.assetVersion_Widget, returnLayout= smartTools_Elements.make_tableWidget( 'Asset Versions', 410, returnLayout= True)
		hLayout.addWidget( groupBox)

		## Create Save Section
		gridLay = QtGui.QGridLayout()
		label= QtGui.QLabel('File Name')
		line01= QtGui.QLineEdit() ## Asset
		line02= QtGui.QLineEdit() ## Modifer
		line03= QtGui.QLineEdit() ## Department
		line04= QtGui.QLineEdit() ## Version
		line04.setReadOnly( 1)
		line05= QtGui.QLineEdit() ## Initials + Extension

		## Save Section Edits
		line01.setFixedWidth( 80)
		line02.setFixedWidth( 50)
		line03.setFixedWidth( 70)
		line04.setFixedWidth( 40)
		line05.setFixedWidth( 60)

		## Disable Line Edits except for option
		line01.setEnabled( 0)
		line02.setEnabled( 1)
		line03.setEnabled( 0)
		# line04.setEnabled( 0)
		line05.setEnabled( 0)

		## Set File Extension
		line05.setText( translator.setFileExtension())

		## Save layout
		gridLay.addWidget( label, 0, 1)
		gridLay.addWidget( line01, 0, 2)
		gridLay.addWidget( line02, 0, 3)
		gridLay.addWidget( line03, 0,4)
		gridLay.addWidget( line04, 0, 5)
		gridLay.addWidget( line05, 0, 6)

		returnLayout.addLayout( gridLay)
		self.saveLine_Elements= [line01, line02, line03, line04, line05]
		#--------------------------------#

		## User Info and Comment Section
		groupBox, self.userName_Widget, self.assetNotes_Widget, returnLayout= smartTools_Elements.make_notesWidget( 'Asset Notes', returnLayout= True)
		hLayout.addWidget( groupBox)

		## Create Save button
		button01= QtGui.QPushButton('Save File')
		button01.setFixedHeight( 40)
		returnLayout.addWidget( button01)

		## Save Radio Buttons
		horizontal_lay= QtGui.QHBoxLayout()
		button_group= QtGui.QButtonGroup( groupBox)

		##Create Buttons
		r0= QtGui.QRadioButton("Local")
		r0.setChecked( 1)
		r1= QtGui.QRadioButton("Global")
		# r2=QtGui.QRadioButton("Publish")

		##Add Buttons
		button_group.addButton(r0)
		button_group.addButton(r1)
		# button_group.addButton(r2)

		## Horizontal Layout
		horizontal_lay.addWidget(r0)
		horizontal_lay.addWidget(r1)
		# horizontal_lay.addWidget(r2)
		returnLayout.addLayout( horizontal_lay)

		self.save_Button= button01
		self.save_radioGrp= button_group
		#--------------------------------#

		##Enable Right clicking on Reference List
		self.saveLine_Elements[3].setContextMenuPolicy( Qt.CustomContextMenu)
		self.connect(self.saveLine_Elements[3], QtCore.SIGNAL('customContextMenuRequested(const QPoint&)'), self.show_saveLine_Popup)

		##Create Popup Menu
		self.versionLine_Popup = QtGui.QMenu( self)
		self.versionLine_Popup.addAction( 'Turn Edits On', partial( self.versionLine_toggle, 1))
		self.versionLine_Popup.addSeparator()
		self.versionLine_Popup.addAction( 'Turn Edits Off', partial( self.versionLine_toggle, 0))

		self.show()


#------------------- EXTRA----------------------------------#
	def show_saveLine_Popup( self, point):
		'''
		Purpose:
			Show popup menu on version number line widget
		'''
		##Show Popup Menu
		self.versionLine_Popup.exec_( self.saveLine_Elements[3].mapToGlobal(point) )

#------------------- GUI FUNCTIONS----------------------------------#
	def versionLine_toggle( self, mode=1):
		'''
		Purpose:
			Turn on and off save version line edit
		'''
		if mode:
			self.saveLine_Elements[3].setReadOnly( False)
			# print 'ON', mode
		else:
			self.saveLine_Elements[3].setReadOnly( True)
			# print 'OFF', mode

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

		## Asset Version
		self.assetVersion_Widget.itemClicked.connect( self.assetVersion_itemClicked)

		## Asset Notes
		self.assetNotes_Widget.textChanged.connect( self.updateFileNote)

		## Save Button
		self.save_Button.clicked.connect( self.saveButton_clicked)
		self.save_radioGrp.buttonClicked.connect( self.save_groupButton_clicked)
		# self.saveLine_Elements[3].
	#
	def resetGUI( self, mode=''):
		'''
		Reset Open Button
		'''
		if mode== 0:
			##Clear Widgets
			self.assetName_Widget.clear()
			self.assetVersion_Widget.setRowCount(0)

			self.assetName= None
			self.assetVersion= None

		if mode== 1:
			##Clear Widgets
			self.assetVersion_Widget.setRowCount(0)
			self.assetVersion= None

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
		Purpose:
			Populate Asset Version list widget and set file name for saving
		Connect Widget Signals to functions
		'''
		## Function variable
		modifer=''

		if len(self.department_Widget.selectedItems())== 0 or  len(self.assetName_Widget.selectedItems())== 0:
			return
		## Reset GUI
		self.resetGUI( 1)

		self.assetName= str(self.assetName_Widget.currentItem().text())

		## Grab and Set Local Drive
		localDrive= str( self.locaDrive_Combo.currentText())

		## Save Asset Path
		smartTools_Elements.create_guiPath( self.projName, self.deptName, self.assetName)

		## Populate widget
		smartTools_Elements.populate_assetVersion( self.assetVersion_Widget, self.assetName, localDrive)

		## Version Up
		if self.assetVersion_Widget.rowCount()>0:
			versionNum= int(self.assetVersion_Widget.item( 0, 0).text().split( '_')[-2].split( 'v')[-1])
			versionNum+=1

			item= str(self.assetVersion_Widget.item( 0, 0).text()).split( self.assetName)[-1].split('_')[1]

			if not item in self.deptName:
				modifer = item

			else:
				modifer = ''

		else:
			versionNum=1

		## Construct Version
		versionNum= 'v{0:03}'.format( versionNum)

		self.saveLine_Elements[0].setText( self.assetName)
		self.saveLine_Elements[1].setText( modifer)
		self.saveLine_Elements[2].setText( self.deptName.split(' ')[0])
		self.saveLine_Elements[3].setText( versionNum)
	#
	def assetVersion_itemClicked( self):
		'''
		Connect Widget Signals to functions
		'''
		## Function Variables
		modifer= ''

		##Grab selected fileName
		selectedRow= self.assetVersion_Widget.selectionModel().selectedRows()[0].row()

		## Grab Widget Info
		fileName= str(self.assetVersion_Widget.item( selectedRow, 0).text())

		## Increase version number
		versionNum= int(fileName.split( '_')[-2].split( 'v')[-1])
		versionNum+=1
		versionNum= 'v%03d'%( versionNum)

		## Grab modifer if there is one
		item= str(fileName.split( self.assetName)[-1].split( '_')[0])


		if not item in self.deptName:
			modifer= item

		else:
			modifer=''

		self.saveLine_Elements[0].setText( self.assetName)
		self.saveLine_Elements[1].setText( modifer)
		self.saveLine_Elements[2].setText( self.deptName.split(' ')[0])
		self.saveLine_Elements[3].setText( versionNum)
	#
	def updateFileNote( self):
		'''
		Check if there are any notes,
		to unlock save in global mode
		'''
		notes= self.assetNotes_Widget.toPlainText()

		## Check if notes are left
		check= bool( re.findall( '[a-zA-Z]+|[0-9]+', notes))
		if check:
			self.save_Button.setEnabled( 1)
		else:
			self.save_Button.setEnabled( 0)
	#
	def save_groupButton_clicked( self):
		tempList= self.save_radioGrp.buttons()
		# print tempList

		for each in tempList:
			widgetName= str( each.text())

			if widgetName== 'Local' and each.isChecked() :
				self.save_Button.setEnabled( 1)

				## Set Save Mode
				self.saveLocation = 'local'

			if widgetName== 'Global' and each.isChecked() :
				self.save_Button.setEnabled( 1)

				## Set Save Mode
				self.saveLocation = 'global'

			if widgetName== 'Publish' and each.isChecked() :
				self.save_Button.setEnabled( 1)

				## Set Save Mode
				self.saveLocation = 'both'
	#
	def saveButton_clicked( self):
		'''
		Connect Widget Signals to functions
		'''
		## Close window
		self.close()

		##Create file Name
		fileName='_'.join( [str(each.text()) for each in self.saveLine_Elements])
		fileName= fileName.replace( '__', '_')

		## Grab Local Drive
		localDrive= str( self.locaDrive_Combo.currentText())

		## Store data on file
		dataDecoder.store_smartData( drive= localDrive)
		dataDecoder.store_smartData( projName= self.projName)
		dataDecoder.store_smartData( deptName= self.deptName)
		dataDecoder.store_smartData( assetName= self.assetName)
		dataDecoder.store_smartData( fileName= fileName)

		## Store data in scene
		translator.setData( 'smart_localDrive', localDrive)
		translator.setData( 'smart_projName', self.projName)
		translator.setData( 'smart_deptName', self.deptName)
		translator.setData( 'smart_assetName', self.assetName)
		translator.setData( 'smart_fileName', fileName)

		versionNum= fileName.split( '_v')[-1].split( '_')[0]
		translator.setData( 'smart_fileVersion', versionNum)

		## Save Asset Path
		global_filePath= smartTools_Elements.create_guiPath( self.projName, self.deptName, self.assetName, fileName)
		# print global_filePath

		## Construct local path
		local_filePath= global_filePath.replace( 'r:/', localDrive+ 'ie/projects/')
		# print local_filePath

		## Grab folder from path
		local_folderPath= os.path.split( local_filePath)[0]

		## Create folder if it doesn't exist
		if not os.path.exists( local_folderPath):
			os.makedirs( local_folderPath)

		## Save file Locally
		if self.saveLocation == 'local':
			## Save File
			translator.saveFile( local_filePath)

		## Save file locally and globally
		elif self.saveLocation == 'global':
			## Save File
			translator.saveFile( local_filePath)

			## Save file to the network
			self.copyToNetwork( local_filePath)

		elif self.saveLocation == 'both':
			## Save File
			translator.saveFile( local_filePath)

			## Save file to the network
			self.copyToNetwork( local_filePath)

		## Store the Drive the user has chosen
		dataDecoder.store_smartData( drive= localDrive)
		dataDecoder.store_smartData( projName= self.projName)
		dataDecoder.store_smartData( deptName= self.deptName)
		dataDecoder.store_smartData( assetName= self.assetName)
		dataDecoder.store_smartData( fileName= fileName)

		## Store data in scene
		translator.setData( 'smart_localDrive', localDrive)
		translator.setData( 'smart_projName', self.projName)
		translator.setData( 'smart_deptName', self.deptName)
		translator.setData( 'smart_assetName', self.assetName)
		translator.setData( 'smart_fileName', fileName)

		versionNum= 'v'+ fileName.split( '_v')[-1].split( '_')[0]
		translator.setData( 'smart_fileVersion', versionNum)

		## Store Scene Assets
		self.store_sceneData( self.projName, self.deptName, self.assetName, versionNum)

		## Store File Notse
		userName= str( self.userName_Widget.text())
		assetNotes= str(self.assetNotes_Widget.toPlainText())

		dataDecoder.store_assetNotes( userName, assetNotes, self.projName, self.deptName, self.assetName, versionNum, self.saveLocation, localDrive)


#------------------- EXTRA FUNCTIONS----------------------------------#
	def copyToNetwork( self, local_filePath):
		'''
		Purpose:
			To copy file from local to the r:/ network
		'''
		global_filePath= 'r:/'+'/'.join( local_filePath.split( '/')[3:])
		# print( global_filePath)

		## Grab folder from path
		global_folderPath= os.path.split( global_filePath)[0]

		if not os.path.exists( global_folderPath):
			## Make Folder Structure
			os.makedirs( global_folderPath)

		## Copy file from network to local drive
		shutil.copyfile( local_filePath, global_filePath)
	#
	def store_sceneData( self, projName, deptName, assetName, version):
		'''
		Purpose:
			Store namespaces of items in scene in data file
		'''
		## Function Variables
		assetInfo_Dict={}
		pubVersion_Dict={}

		## Grab namespace list
		sceneData= translator.getData( 'namespace_List')
		# print sceneData

		if sceneData== '':
			return

		## Turn string into list
		namespace_List= [x for x in sceneData.split(',')]

		for each in namespace_List:
			if translator.namespaceExists( each):
				## Grab namespace list
				assetInfo= translator.getData( each)

				assetInfo_Dict[ each]= assetInfo

				## Grab version number
				dept = assetInfo.split( '**')[1]
				asset = assetInfo.split( '**')[2]
				ver = assetInfo.split( '**')[4]

				## Store asset name with published version
				pubVersion_Dict[ each]=  asset+ '**'+ dept+ '**'+ ver

		assetInfo_Dict[ 'publish']= pubVersion_Dict

		## Store Information in Data File
		dataDecoder.store_sceneAssetData( projName, deptName, assetName, version, assetInfo_Dict)


def main():
	'''
	Show Window
	'''
	translator.launch( GUI, None)



if __name__ == '__main__':
	main()

