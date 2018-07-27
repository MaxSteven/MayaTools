'''
Author: Carlo Cherisier
Date: 09.30.14
Script: publishMaterialsGUI

python.execute("
import sys;
sys.path.append('c:/ie/ark/tools');
import publishTools; reload( publishTools); publishTools.publishMaterials();
")
'''
from PySide import QtGui

import arkInit
arkInit.init()

import translators
translator = translators.getCurrent()

import shared_Elements
import publishMaterialsFunc as guiFunc

class GUI( QtGui.QDialog):
	'''
	Thiis will be the code for all the Import QtGui elements
	'''
	def __init__(self, parent=None):
		super(GUI, self).__init__(parent)

		## Setup GUI
		self.create_Window()
		shared_Elements.populate_Projects( self.project_Widget)
		shared_Elements.populate_Deparments( self.department_Widget, 1)
		self.setup_Connections()

		## GUI Functions Class
		self.guiFunc= guiFunc.guiFunc()

#------------------- WINDOW CREATION----------------------------------#
	def create_Window( self):
		'''
		Purpose:
			Function to contain all window elements
		'''
		## Window Title
		self.setWindowTitle( 'Publish Material')

		## Window Settings
		self.setFixedWidth( 650)

		## Set GUI Layouts
		self.guiLayout= QtGui.QVBoxLayout()
		self.guiLayout.addStretch(1)
		self.setLayout( self.guiLayout)

		## Make Second Layout for GUI
		hLayout = QtGui.QHBoxLayout()
		self.guiLayout.addLayout( hLayout)
		#--------------------------------#

		## Project Section
		groupBox, self.project_Widget= shared_Elements.make_listWidget( 'Project List', 200)
		hLayout.addWidget( groupBox)
		#--------------------------------#

		## Department Section
		groupBox, self.department_Widget= shared_Elements.make_listWidget( 'Departments', 110)
		hLayout.addWidget( groupBox)
		#--------------------------------#

		## Asset Name Section
		groupBox, self.assetName_Widget= shared_Elements.make_listWidget( 'Asset Name', 150)
		hLayout.addWidget( groupBox)
		#--------------------------------#

		## Publish Section
		pub_Lay = QtGui.QVBoxLayout()
		hLayout.addLayout( pub_Lay)
		label01= QtGui.QLabel('Select Objects and press button')

		self.activate_Button= QtGui.QPushButton('Publish Material')

		label02= QtGui.QLabel('')
		label02.setFixedHeight( 80)

		self.load_Button= QtGui.QPushButton('Load Material')
		self.activate_Button.setEnabled( 0)

		pub_Lay.addWidget( label01)
		pub_Lay.addWidget( self.activate_Button)
		pub_Lay.addWidget( self.load_Button)
		#--------------------------------#

		## Show Gui
		self.show()


#------------------- GUI CONNECTIONS----------------------------------#
	def setup_Connections( self):
		'''
		Contains all Connections to GUI elements
		'''
		##Project
		self.project_Widget.itemSelectionChanged.connect( self.project_hasChanged)

		## Department
		self.department_Widget.currentItemChanged.connect( self.department_hasChanged)

		##Asset Name
		self.assetName_Widget.itemSelectionChanged.connect( self.assetName_hasChanged)

		## Publish Button
		# if( guiMode=='Save'):
		self.activate_Button.clicked.connect( self.savePublishMaterials)
		self.load_Button.clicked.connect( self.loadPublishMaterials)

		# if( guiMode=='Load'):
		# 	self.activate_Button.clicked.connect( self.loadMaterials)

#------------------- GUI FUNCTIONS----------------------------------#
	def resetGUI( self, mode=''):
		'''
		Reset Open Button
		'''
		if( mode== 0):
			##Clear Widgets
			self.assetName_Widget.clear()
			self.activate_Button.setEnabled( 0)

#------------------- GUI SIGNALS----------------------------------#
	def project_hasChanged( self):
		'''
		Connect Widget Signals to functions
		'''
		## Reset GUI
		self.resetGUI( 0)

		## Grab Widget Info
		self.projName= self.project_Widget.currentItem().text()

		if( bool( self.department_Widget.currentItem()) ):
			self.deptName= str(self.department_Widget.currentItem().text())

			## Save Asset Path
			shared_Elements.create_guiPath( self.projName, self.deptName)

			## Populate widget
			shared_Elements.populate_assetName( self.assetName_Widget)
	#
	def department_hasChanged( self):
		'''
		Connect Widget Signals to functions
		'''
		if( len(self.project_Widget.selectedItems())== 0):
			return
		## Reset GUI
		self.resetGUI( 0)

		## Grab Widget Info
		self.deptName= str(self.department_Widget.currentItem().text())

		## Save Asset Path
		shared_Elements.create_guiPath( self.projName, self.deptName)

		## Populate widget
		shared_Elements.populate_assetName( self.assetName_Widget)
	#
	def assetName_hasChanged( self):
		'''
		Enable activate_Button
		'''
		self.activate_Button.setEnabled( 1)
	#
	def savePublishMaterials( self):
		'''
		Purpose:
			Save Materials on selected objects
		'''
		self.close()

		## Grab Asset Name
		self.assetName= str( self.assetName_Widget.currentItem().text())

		## Save Multi Sub Material
		result = self.guiFunc.saveMultiSubMaterial( self.projName, self.assetName)

		if result == 2:
			QtGui.QMessageBox.warning( None, "Warning Material was not Published", 'There are no objects selected!')

		if result == 3:
			QtGui.QMessageBox.warning( None, "Warning Material was not Published", 'There isn\'t a Multi Sub Material connected to the selected object!')

	#
	def loadPublishMaterials( self):
		'''
		Purpose:
			Load published materials on selected objects
		'''
		self.close()

		## Grab Asset Name
		self.assetName= str( self.assetName_Widget.currentItem().text())

		## Save Multi Sub Material
		result = self.guiFunc.loadMultiSubMaterial( self.projName, self.assetName)

		if result == 2:
			QtGui.QMessageBox.warning( None, "Warning Material was not Loaded", 'There are no objects selected!')

def main():
	'''
	Show Window
	'''
	translator.launch( GUI)



if __name__ == '__main__':
	main()

