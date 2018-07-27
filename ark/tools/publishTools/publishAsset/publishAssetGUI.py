'''
Author: Carlo Cherisier
Date: 09.5.14
Script: publishAssetGUI

python.execute("
import sys;
sys.path.append('c:/ie/ark/tools');
import publishTools; reload( publishTools); publishTools.publishAsset();
")
'''
from PySide import QtGui

import arkInit
arkInit.init()

import translators
translator = translators.getCurrent()

import sys, os
mainFolder = os.path.dirname(os.path.dirname(__file__))
sys.path.append( mainFolder)
sys.path.append( 'c:/ie/ark/tools/dataDecoder')
import dataDecoder, shared_Elements
reload( shared_Elements)

import publishAssetFUNC as guiFunc
reload( guiFunc)
import re

class GUI( QtGui.QDialog):
	##Class Variables
	projName = None
	deptName = None
	assetName = None
	projectPath = None

	def __init__(self, parent=None):
		super(GUI, self).__init__(parent)
		## Setup GUI
		self.create_Window()
		shared_Elements.populate_Projects( self.project_Widget)
		shared_Elements.populate_Deparments( self.department_Widget, 1)
		self.setup_Connections()

		## GUI Functions Class
		self.guiFunc= guiFunc.guiFunc()

		##Retrieve Global Variables
		guiInfo = shared_Elements.get_dataForGUI()

		if guiInfo != None:
			projName = guiInfo[1].capitalize()
			deptName = guiInfo[2].capitalize()
			assetName = guiInfo[3].capitalize()

		else:
			projName = dataDecoder.get_smartData( 'projName').capitalize()
			deptName = dataDecoder.get_smartData( 'deptName').capitalize()
			assetName = dataDecoder.get_smartData( 'assetName').capitalize()

		## Check scene asset publish in order to save Asset List selection
		## because user forget to select obejcts in the scene
		result = translator.getData( 'publishAsset')

		if result != '':
			assetName = result

		## Set GUI Elements
		shared_Elements.select_guiItem( self.project_Widget, projName)
		shared_Elements.select_guiItem( self.department_Widget, deptName)
		result = shared_Elements.select_guiItem( self.assetName_Widget, assetName)

		if result != False:
			## Set Asset Path
			shared_Elements.create_guiPath( projName, deptName, assetName)

			## Populate Asset Versions
			self.updateAssetName()

#------------------- WINDOW CREATION----------------------------------#
	def create_Window( self):
		'''
		Purpose:
			Contains window elements
		'''
		## Window Title
		self.setWindowTitle( 'Publish Asset')

		## Window Settings
		self.setFixedWidth( 750)

		## Set GUI Layouts
		self.guiLayout= QtGui.QVBoxLayout()
		self.guiLayout.addStretch(1)
		self.setLayout( self.guiLayout)

		## Make Second Layout for GUI
		hLayout = QtGui.QHBoxLayout()
		self.guiLayout.addLayout( hLayout)
		#--------------------------------#

		## Project Section
		groupBox, self.project_Widget = shared_Elements.make_listWidget( 'Project List', 200)
		hLayout.addWidget( groupBox)
		#--------------------------------#

		## Department Section
		groupBox, self.department_Widget = shared_Elements.make_listWidget( 'Departments', 110)
		hLayout.addWidget( groupBox)
		#--------------------------------#

		## Asset Name Section
		groupBox, self.assetName_Widget, returnLayout= shared_Elements.make_listWidget( 'Asset Name', 150, returnLayout= True)
		hLayout.addWidget( groupBox)

		## Add Asset Section
		horizontal_lay = QtGui.QHBoxLayout()
		label= QtGui.QLabel('Add Asset')
		self.newAsset_Line = QtGui.QLineEdit()
		self.newAsset_Line.setEnabled( 0)

		self.addNewAsset_Button = QtGui.QPushButton('Add Asset')
		self.addNewAsset_Button.setEnabled( 0)

		horizontal_lay.addWidget( label)
		horizontal_lay.addWidget( self.newAsset_Line)

		returnLayout.addLayout( horizontal_lay)
		returnLayout.addWidget( self.addNewAsset_Button)
		#--------------------------------#

		## Publish Section
		pub_Lay = QtGui.QVBoxLayout()
		hLayout.addLayout( pub_Lay)

		label = QtGui.QLabel('Select Objects and press button')

		if translator.fileExtension == 'max':
			self.nativeFile_CheckBox = QtGui.QCheckBox ('Publish Max File')

		elif translator.fileExtension == 'ma':
			self.nativeFile_CheckBox = QtGui.QCheckBox ('Publish Maya File')

		else:
			self.nativeFile_CheckBox = QtGui.QCheckBox ('Publish Native File')

		self.rigFile_CheckBox = QtGui.QCheckBox ('Publish Rig File')
		self.alembicFile_CheckBox = QtGui.QCheckBox ('Publish Alembic File')
		self.vrayFile_CheckBox = QtGui.QCheckBox ('Publish Vray Poxy')
		self.objFile_CheckBox = QtGui.QCheckBox ('Publish OBJ File')
		self.rigFile_CheckBox.setEnabled( 0)
		# self.vrayFile_CheckBox.setEnabled( 0)
		# self.alembicFile_CheckBox.setEnabled( 0)
		# self.objFile_CheckBox.setEnabled( 0)

		## Button Section
		self.publishAsset_Button = QtGui.QPushButton('Publish Asset')
		self.publishAsset_Button.setFixedHeight( 80)
		self.publishAsset_Button.setEnabled( 0)

		self.nativeFile_CheckBox.setChecked( 1)
		# self.alembicFile_CheckBox.setChecked( 1)
		# self.objFile_CheckBox.setChecked( 1)

		pub_Lay.addWidget( label)
		pub_Lay.addWidget( self.nativeFile_CheckBox)
		pub_Lay.addWidget( self.rigFile_CheckBox)
		pub_Lay.addWidget( self.alembicFile_CheckBox)
		pub_Lay.addWidget( self.vrayFile_CheckBox)
		pub_Lay.addWidget( self.objFile_CheckBox)
		pub_Lay.addWidget( self.publishAsset_Button)
		#--------------------------------#

		## Show Gui
		self.show()


#------------------- GUI CONNECTIONS----------------------------------#
	def setup_Connections( self):
		'''
		Contains all Connections to GUI elements
		'''
		##Project
		self.project_Widget.currentItemChanged.connect( self.updateProject)

		## Department
		self.department_Widget.currentItemChanged.connect( self.updateDepartment)

		##Asset Name
		self.assetName_Widget.itemSelectionChanged.connect( self.updateAssetName)

		## New Asset Button
		self.newAsset_Line.textChanged.connect( self.updateNewAssetLine)
		self.addNewAsset_Button.clicked.connect( self.addNewAssetClicked)

		## Checkbox
		if translator.fileExtension == 'max':
			self.nativeFile_CheckBox.stateChanged.connect( lambda: self.updateCheckbox('mode01'))
		self.rigFile_CheckBox.stateChanged.connect( lambda: self.updateCheckbox('mode02'))

		## Publish Button
		self.publishAsset_Button.clicked.connect( self.publishAssetClicked)


#------------------- GUI FUNCTIONS----------------------------------#
	def resetGUI( self, mode=''):
		'''
		Reset Open Button
		'''
		if mode == 0:
			##Clear Widgets
			self.assetName_Widget.clear()
			self.publishAsset_Button.setEnabled( 0)

		self.newAsset_Line.clear()
		self.addNewAsset_Button.setEnabled( 0)


#------------------- GUI SIGNALS----------------------------------#
	def updateProject( self):
		'''
		Connect Widget Signals to functions
		'''
		## Reset GUI
		self.resetGUI( 0)

		## Grab Widget Info
		self.projName = self.project_Widget.currentItem().text()

		if bool( self.department_Widget.currentItem()):
			self.updateDepartment()
	#
	def updateDepartment( self):
		'''
		Connect Widget Signals to functions
		'''
		if len(self.project_Widget.selectedItems())== 0:
			return
		## Reset GUI
		self.resetGUI( 0)

		## Grab Widget Info
		self.deptName= str(self.department_Widget.currentItem().text())

		if self.deptName== 'Rig':
			self.rigFile_CheckBox.setEnabled( 1)
			self.rigFile_CheckBox.setChecked( 1)

			self.nativeFile_CheckBox.setEnabled( 0)

		else:
			self.rigFile_CheckBox.setEnabled( 0)
			self.rigFile_CheckBox.setChecked( 0)

			self.nativeFile_CheckBox.setEnabled( 1)

		## Save Asset Path
		self.projectPath = shared_Elements.create_guiPath( self.projName, self.deptName)

		## Populate widget
		shared_Elements.populate_assetName( self.assetName_Widget)

		## Enable New Asset Line
		self.newAsset_Line.setEnabled( 1)
	#
	def updateAssetName( self):
		'''
		Enable publishAsset_Button
		'''
		self.publishAsset_Button.setEnabled( 1)
	#
	def updateNewAssetLine( self):
		'''
		Enable addNewAsset_Button
		'''
		data= self.newAsset_Line.text()

		## Check if notes are left
		check= bool( re.findall( '[\100-\177]+', data))

		if check:
			self.addNewAsset_Button.setEnabled( 1)
		else:
			self.addNewAsset_Button.setEnabled( 0)
	#
	def addNewAssetClicked( self):
		'''
		Add New Asset Folder to Selected Project
		'''
		## Grab New Asset Name
		newAssetName= str(self.newAsset_Line.text()).capitalize()

		## Grab Asset List
		nameList=[ str( self.assetName_Widget.item(i).text()) for i in range( self.assetName_Widget.count())]

		if newAssetName in nameList:
			text= 'There Asset already exists! Create new name!'
			QtGui.QMessageBox.warning (self, 'Warning', text)
			return

		## Reset GUI
		self.resetGUI( 0)

		## Create Asset Folder
		self.guiFunc.createAssetFolder( self.projName, newAssetName)

		## Save Asset Path
		self.projectPath = shared_Elements.create_guiPath( self.projName, self.deptName)

		## Add New Asset To Asset List
		shared_Elements.populate_assetName( self.assetName_Widget)

		## Select New Asset From List
		shared_Elements.select_guiItem( self.assetName_Widget, newAssetName)

		## Store Asset Name
		translator.setData( 'publishAsset', newAssetName)
	#
	def updateCheckbox( self, mode):
		if mode == 'mode01':
			if self.nativeFile_CheckBox.isChecked()== True:
				self.vrayFile_CheckBox.setEnabled( 1)
				self.alembicFile_CheckBox.setEnabled( 1)
				self.objFile_CheckBox.setEnabled( 1)
			else:
				self.vrayFile_CheckBox.setEnabled( 0)
				self.alembicFile_CheckBox.setEnabled( 0)
				self.objFile_CheckBox.setEnabled( 0)

		if mode== 'mode02':
			if self.rigFile_CheckBox.isChecked()== True:
				self.vrayFile_CheckBox.setEnabled( 1)
				self.alembicFile_CheckBox.setEnabled( 1)
				self.objFile_CheckBox.setEnabled( 1)
			else:
				self.vrayFile_CheckBox.setEnabled( 0)
				self.alembicFile_CheckBox.setEnabled( 0)
				self.objFile_CheckBox.setEnabled( 0)
	#
	def prepExport( self):
		'''
		Purpose:
			Create bounding box, assetRoot for hiRez export
		'''
		# Make bounding box for hiRez
		self.guiFunc.makeBoundingBox()

		## Make locator for Asset
		self.guiFunc.createLocator()

		## Parent Objects to Locator
		self.guiFunc.setLocaterToAssetParent()
	#
	def publishAssetClicked( self):
		'''
		Publish Selected Objects
		'''
		self.close()

		## Function variables
		lowRezPath= ''
		hiRezPath= ''
		devPath=''
		bBoxPath= ''
		abcPath= ''
		objPath= ''
		rigPath= ''
		vrayPath= ''
		mode01= self.nativeFile_CheckBox.isChecked()
		mode02= self.rigFile_CheckBox.isChecked()
		mode03= self.alembicFile_CheckBox.isChecked()
		mode04= self.vrayFile_CheckBox.isChecked()
		mode05= self.objFile_CheckBox.isChecked()

		if not mode01 and not mode02 and not mode03 and not mode04 and not mode05:
			return

		## Grab Asset Name
		self.assetName= str( self.assetName_Widget.currentItem().text())

		## Store GUI Elements for guiFunc
		self.guiFunc.assetName= self.assetName
		self.guiFunc.publishFolderPath= '{0}/{1}/Published'.format( self.projectPath, self.assetName)
		self.guiFunc.departmentFolder= '{0}/{1}/{2}'.format( self.projectPath, self.assetName, self.deptName.split(' ')[0])

		## Prepare asset to be published
		if mode01 == True:
			check= self.guiFunc.grabObjects()

			if check == False:
				## Message to user
				text= 'Nothing is selected. In order to use script select objects!'
				QtGui.QMessageBox.warning (self, 'Warning', text)
				return

		## Create folder location for Published Asset files
		self.guiFunc.createPublishFolder( self.deptName)

		## Export lowRez, hiRez, BoundingBox, development file
		if mode01 == True:
			self.prepExport()
			bBoxPath = self.guiFunc.exportBoundingBox()
			lowRezPath = self.guiFunc.exportLowRezFile()
			hiRezPath = self.guiFunc.exportHiRezFile()
			devPath = self.guiFunc.exportDevelopmentFile( self.deptName)

		## Export Rig File
		if mode02 == True:
			if self.guiFunc.checkForRig() == True:
				devPath= self.guiFunc.exportDevelopmentFile( self.deptName)
				rigPath= self.guiFunc.exportRigFile()
				# print rigPath

			if rigPath == False or rigPath == '':
				QtGui.QMessageBox.warning( None, "Warning Asset Was Not Published", 'There is no "Scene" object in this file. Either create one of fix the name')
				return

		## Export Alembic File
		if mode03 == True:
			abcPath = self.guiFunc.exportAlembicFile( self.deptName)

		## Export vRay Proxy
		if mode04 == True:
			if mode01 == False:
				check = self.guiFunc.grabObjects()

				if check == False:
					return

			if translator.fileExtension == 'max':
				abcPath = self.guiFunc.exportAlembicFile( self.deptName)
				vrayPath = self.guiFunc.exportVrayFile( self.deptName, abcPath)

			if translator.fileExtension == 'ma':
				vrayPath = self.guiFunc.exportVrayFile( self.deptName)

		## Export OBJ File
		if mode05 == True:
			objPath = self.guiFunc.exportObjFile( self.deptName)

		self.guiFunc.cleanFile()

		# Store Asset data
		self.guiFunc.storeAssetData( self.projName, self.deptName, self.assetName, lowRezPath, hiRezPath, rigPath, devPath, bBoxPath, abcPath, vrayPath, objPath)

		## Store Asset Name
		translator.setData( 'publishAsset', self.assetName)

		## Inform User
		QtGui.QMessageBox.about( None, 'Asset Published', ' {0} {1} has been published!'.format( self.assetName, self.guiFunc.publishVersion))


def main():
	'''
	Show Window
	'''
	translator.launch(GUI, None)


if __name__ == '__main__':
	main()

