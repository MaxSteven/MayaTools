'''
Author: Carlo Cherisier
Date: 09.5.14
Script: publishCameraGUI

python.execute("
import sys;
sys.path.append('c:/ie/ark/tools');
import publishTools; reload( publishTools); publishTools.publishCamera();
")
'''
from PySide import QtGui

import arkInit
arkInit.init()

import translators
translator = translators.getCurrent()
runMaxScript= translator.executeNativeCommand

import shared_Elements

import sys
sys.path.append( 'c:/ie/ark/tools/dataDecoder')
import dataDecoder

import publishCameraFUNC as guiFUNC

class GUI( QtGui.QDialog):
	'''
	Thiis will be the code for all the Import QtGui elements
	'''
	## Class Variables
	projName= None
	assetName= None
	def __init__(self, parent=None):
		super(GUI, self).__init__(parent)

		## Setup GUI
		self.create_Window()
		shared_Elements.populate_Projects( self.project_Widget)
		self.setup_Connections()

		## GUI Functions Class
		self.guiFunc= guiFUNC.guiFUNC()

		## Retrieve Global Variables
		guiInfo= shared_Elements.get_dataForGUI()
		if( guiInfo!= None):
			projName= guiInfo[1]
			assetName= guiInfo[3]

		else:
			projName= dataDecoder.get_smartData( 'projName')
			assetName= dataDecoder.get_smartData( 'assetName')

		## Set GUI Elements
		shared_Elements.select_guiItem( self.project_Widget, projName)
		shared_Elements.select_guiItem( self.assetName_Widget, assetName)

#------------------- WINDOW CREATION----------------------------------#
	def create_Window( self):
		'''
		Purpose:
			Contains window elements
		'''
		## Window Title
		self.setWindowTitle( 'Publish Asset')

		## Window Settings
		self.setFixedWidth( 700)

		## Set GUI Layouts
		self.guiLayout= QtGui.QVBoxLayout()
		self.guiLayout.addStretch(1)
		self.setLayout( self.guiLayout)
		#--------------------------------#

		## Make Second Layout for GUI
		hLayout = QtGui.QHBoxLayout()
		self.guiLayout.addLayout( hLayout)
		#--------------------------------#

		## Project Section
		groupBox, self.project_Widget= shared_Elements.make_listWidget( 'Project List', 200)
		hLayout.addWidget( groupBox)
		#--------------------------------#

		## Asset Name Section
		groupBox, self.assetName_Widget= shared_Elements.make_listWidget( 'Asset Name', 200)
		hLayout.addWidget( groupBox)
		#--------------------------------#

		## Publish Section
		pub_Lay = QtGui.QVBoxLayout()
		hLayout.addLayout( pub_Lay)

		label= QtGui.QLabel('Select Camera and press button')
		self.publish_Button= QtGui.QPushButton('Publish Camera')
		self.publish_Button.setFixedHeight( 40)
		self.publish_Button.setEnabled( 0)
		pub_Lay.addWidget( label)
		pub_Lay.addWidget( self.publish_Button)

		## Show Gui
		self.show()

		## Adding Extra Gui Functions
		self.assetName_Widget.setSelectionMode( QtGui.QAbstractItemView.ExtendedSelection)


#------------------- GUI CONNECTIONS----------------------------------#
	def setup_Connections( self):
		'''
		Purpose:
			Connect all GUI Elements to desired functions
		'''
		## Project
		self.project_Widget.itemSelectionChanged.connect( self.project_hasChanged)

		## Shot Name
		self.assetName_Widget.itemSelectionChanged.connect( self.assetName_hasChanged)

		## Publish Button
		self.publish_Button.clicked.connect( self.publishAsset_clicked)


#------------------- GUI SIGNALS----------------------------------#
	def project_hasChanged( self):
		'''
		Connect Widget Signals to functions
		'''
		##Clear Widgets
		self.assetName_Widget.clear()
		self.publish_Button.setEnabled( 0)

		## Grab Widget Info
		self.projName= self.project_Widget.currentItem().text()

		## Save Asset Path
		shared_Elements.create_guiPath( self.projName, mode= 'camera')

		## Populate widget
		shared_Elements.populate_assetName( self.assetName_Widget)
	#
	def assetName_hasChanged( self):
		'''
		Enable publish_Button
		'''
		self.publish_Button.setEnabled( 1)
	#
	def publishAsset_clicked( self):
		'''
		Publish Selected Objects
		'''
		## Check if there is a camera is selected
		mode= self.guiFunc.check_Camera()

		if( mode== 0):
			return

		## Close Window
		self.close()

		## Grab selected items
		shot_List= self.assetName_Widget.selectedItems()

		for each in shot_List:
			shotName= each.text()

			## Export Camera
			self.guiFunc.export_Camera( mode, self.projName, shotName)

			if( shotName!= self.assetName):
				## Delete camera if it isn't the shot camera
				self.guiFunc.deleteCamera( 'newCamera')

		## Delete Original Camera
		self.guiFunc.deleteCamera( self.guiFunc.originalCamera)


def main():
	'''
	Show Window
	'''
	translator.launch( GUI, None)

if __name__ == '__main__':
	main()




