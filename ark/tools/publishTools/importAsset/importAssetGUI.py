'''
Author: Carlo Cherisier
Date: 09.10.14
Script: importAssetGUI

python.execute("
import sys;
sys.path.append('c:/ie/ark/tools/publishTools');
import publishTools; reload( publishTools); publishTools.importAsset();
")
'''
from PySide import QtGui

import arkInit
arkInit.init()

import translators
translator = translators.getCurrent()
runMaxScript= translator.executeNativeCommand

import sys
sys.path.append( 'c:/ie/ark/tools/publishTools')
import shared_Elements

import importAssetFUNC as guiFunc
reload( guiFunc)

class GUI( QtGui.QDialog):
	##Class Variables
	projName= None
	deptName= None
	mode01= False
	mode02= False
	mode03= False

	def __init__(self, parent=None):
		super(GUI, self).__init__(parent)

		## GUI Functions Class
		self.guiFunc= guiFunc.guiFunc()

		## Setup GUI
		self.create_Window()
		shared_Elements.populate_Projects( self.project_Widget)
		shared_Elements.populate_Deparments( self.department_Widget, 1)
		self.setup_Connections()
		self.show()

		## Store last guiPath
		projName = translator.getData( 'importProject')

		if projName != None:
			deptName = translator.getData( 'importDepartment')

			## Set GUI Elements
			shared_Elements.select_guiItem( self.project_Widget, projName)
			shared_Elements.select_guiItem( self.department_Widget, deptName)

#------------------- WINDOW CREATION----------------------------------#
	def create_Window( self):
		'''
		Purpose:
			Contains window elements
		'''
		## Window Title
		self.setWindowTitle( 'Import Publish Asset')

		## Window Settings
		self.setFixedWidth( 920)

		## Set GUI Layouts
		self.guiLayout= QtGui.QVBoxLayout()
		self.guiLayout.addStretch(1)
		self.setLayout( self.guiLayout)

		## Make Second Layout for GUI
		hLayout = QtGui.QHBoxLayout()
		self.guiLayout.addLayout( hLayout)
		#--------------------------------#

		## Project Section
		groupBox, self.project_Widget= shared_Elements.make_listWidget( 'Project List')
		hLayout.addWidget( groupBox)
		#--------------------------------#

		## Department Section
		groupBox, self.department_Widget= shared_Elements.make_listWidget( 'Departments', 110)
		hLayout.addWidget( groupBox)
		#--------------------------------#

		## Asset Name Section
		groupBox, self.assetName_Widget= shared_Elements.make_listWidget( 'Published Assets', 150)
		hLayout.addWidget( groupBox)
		#--------------------------------#

		## Transfer Section
		groupBox = QtGui.QGroupBox( 'Transfer')
		hLayout.addWidget( groupBox)
		groupBox.setAlignment( 4)
		groupBox.setFixedWidth( 100)

		## Create layout for group
		box = QtGui.QVBoxLayout()
		groupBox.setLayout( box)

		## Asset Type Section
		self.importType_Combo= QtGui.QComboBox()
		self.importType_Combo.addItems( ['hiRez', 'lowRez', 'bBox', 'vRayProxy', 'maxWell Poxy', 'alembic', 'rig'])
		self.importType_Combo.setFixedHeight( 40)

		# Space
		space01= QtGui.QSpacerItem( 10, 50)
		space02= QtGui.QSpacerItem( 10, 30)

		## Transfer Button
		self.transferAsset_Button= QtGui.QPushButton('Transfer >>')
		self.transferAsset_Button.setFixedHeight( 60)
		self.transferAsset_Button.setEnabled( 0)

		box.addItem( space01)
		box.addWidget( self.importType_Combo)
		box.addItem( space02)
		box.addWidget( self.transferAsset_Button)
		#--------------------------------#

		## Import Section
		groupBox, self.import_Widget, returnLayout= shared_Elements.make_listWidget( 'Published Assets', 200, returnLayout= True)
		hLayout.addWidget( groupBox)

		## Remove and Import Buttons
		self.removeAsset_Button= QtGui.QPushButton('Remove Selected Asset(s)')
		self.importAsset_Button= QtGui.QPushButton('Import Asset(s)')

		returnLayout.addWidget( self.removeAsset_Button)
		returnLayout.addWidget( self.importAsset_Button)
		#--------------------------------#

		## Adding Extra Gui Functions
		self.assetName_Widget.setSelectionMode( QtGui.QAbstractItemView.ExtendedSelection)
		self.import_Widget.setSelectionMode( QtGui.QAbstractItemView.ExtendedSelection)


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
		self.assetName_Widget.itemDoubleClicked.connect( self.transferAsset_clicked)

		## Transfer Section
		self.transferAsset_Button.clicked.connect( self.transferAsset_clicked)

		## Import List
		self.import_Widget.itemDoubleClicked.connect( self.removeAsset_clicked)

		## Import + Remove Button
		self.removeAsset_Button.clicked.connect( self.removeAsset_clicked)
		self.importAsset_Button.clicked.connect( self.importAsset_clicked)


#------------------- GUI FUNCTIONS----------------------------------#
	def resetGUI( self, mode=''):
		'''
		Reset Open Button
		'''
		if mode== 0:
			##Clear Widgets
			self.assetName_Widget.clear()


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

			## Populate published Asset Widget
			self.guiFunc.populate_publishedAssets( self.assetName_Widget, self.projName, self.deptName)
	#
	def updateDepartment( self):
		'''
		Connect Widget Signals to functions
		'''
		if len(self.project_Widget.selectedItems())== 0:
			return

		## Grab Widget Info
		selected= str(self.department_Widget.currentItem().text())

		if selected== 'Rig':
			self.importType_Combo.setCurrentIndex( 6)

		if self.deptName== 'Rig' and selected!= 'Rig':
			self.importType_Combo.setCurrentIndex( 0)

		self.deptName= selected

		## Clear List
		self.assetName_Widget.clear()

		## Populate published Asset Widget
		self.guiFunc.populate_publishedAssets( self.assetName_Widget, self.projName, self.deptName)
	#
	def updateAssetName( self):
		'''
		Enable publishAsset_Button
		'''
		self.transferAsset_Button.setEnabled( 1)
	#
	def transferAsset_clicked( self):
		'''
		Purpose:
			Transfer selected assets to import list widget
		'''
		## Grab Import Type
		assetType= str( self.importType_Combo.currentText())

		temp_List= self.assetName_Widget.selectedItems()

		for each in temp_List:
			assetName= each.text()
			result, message= self.guiFunc.assetTypeExists( self.projName, self.deptName, assetName, assetType)

			if result == 1:
				## Construct Item Name
				item= '{0}**{1}**{2}**{3}'.format( self.projName, self.deptName, assetName, assetType)

				## Add item to list widget
				self.import_Widget.addItem( item)
			if result == 2:
				QtGui.QMessageBox.warning( None, "Warning {0} was not transferred to Import list".format( assetName), message)
			if result == 3:
				QtGui.QMessageBox.warning( None, "Warning {0} was not transferred to Import list".format( assetName), message)
	#
	def removeAsset_clicked( self):
		'''
		Remove Selected Assets
		'''
		## Grab item list that need to be removed
		remove_List= self.import_Widget.selectedItems()

		## Conver Qt List to String List
		remove_List= [ str(i.text()) for i in remove_List]

		## Grab full item list
		item_List=[]
		for i in range( self.import_Widget.count()):
			name= str( self.import_Widget.item( i).text())
			item_List.append( name)

		## Clear List
		self.import_Widget.clear()

		## Remove Item From List
		for each in remove_List:
			item_List.remove( each)

		## Add back to List Widget
		for each in item_List:
			self.import_Widget.addItem( each)
	#
	def importAsset_clicked( self):
		'''
		Import Assets From List
		'''
		for i in range( self.import_Widget.count()):
			name= str( self.import_Widget.item( i).text())
			print name
			## Grab assetName and assetPath
			self.guiFunc.getAssetPath( name)

			## Set namespace for asset
			self.guiFunc.set_namespace()

			if translator.getProgram() == 'Maya':
				if name.split( '**')[-1] == 'vRayProxy':
					self.guiFunc.importVrayProxy()

				elif name.split( '**')[-1] == 'alembic':
					pass
				else:
					## Import Asset into Scene and provide namespace
					self.guiFunc.importAsset()

			if translator.getProgram() == 'Max':
				## Import Asset into Scene and provide namespace
				self.guiFunc.importAsset()

		## Clear list
		self.import_Widget.clear()
		self.close()

		self.guiFunc.finalize_importAsset()

		## Store last guiPath
		translator.setData( 'importProject', self.projName)
		translator.setData( 'importDepartment', self.deptName)


def main():
	'''
	Show Window
	'''
	translator.launch( GUI, None)



if __name__ == '__main__':
	main()

