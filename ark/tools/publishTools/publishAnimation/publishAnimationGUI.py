'''
Author: Carlo Cherisier
Date: 09.10.14
Script: publishAnimationGUI

python.execute("
import sys;
sys.path.append('c:/ie/ark/tools');
import publishTools; reload( publishTools); publishTools.publishAnimation();
")
'''
from PySide import QtGui

import arkInit
arkInit.init()

import translators
translator = translators.getCurrent()

import sys
sys.path.append( 'c:/ie/ark/tools/publishTools')
import shared_Elements

import publishAnimationFunc as guiFUNC

class GUI( QtGui.QDialog):
	'''
	Purpose:
		Contains logic for all Basic GUI Elements
	'''
	def __init__(self, parent=None):
		super(GUI, self).__init__(parent)

		## GUI Functions Class
		self.guiFunc= guiFUNC.guiFUNC()
		self.guiFunc.get_guiInformation()

		## Setup GUI
		self.create_Window()
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
		self.setWindowTitle( 'Publish Animation')

		## Window Settings
		self.setFixedWidth( 350)

		## Set GUI Layouts
		self.guiLayout= QtGui.QVBoxLayout()
		self.guiLayout.addStretch(1)
		self.setLayout( self.guiLayout)

		## Make Second Layout for GUI
		hLayout = QtGui.QHBoxLayout()
		self.guiLayout.addLayout( hLayout)
		#--------------------------------#

		## Asset Name Section
		groupBox, self.assetName_Widget= shared_Elements.make_listWidget( 'Published Assets', 150)
		hLayout.addWidget( groupBox)
		#--------------------------------#

		## Publish Section
		gridLayout= QtGui.QGridLayout()
		gridLayout.setSpacing( 2)
		hLayout.addLayout( gridLayout)

		## Create Checkbox
		check01= QtGui.QCheckBox ('Select All')
		check02= QtGui.QCheckBox ('Publish Alembic File')

		iterCheck= QtGui.QCheckBox ('Set Iterations')
		iterCheck.setEnabled( 0)

		spinBox= QtGui.QSpinBox()
		spinBox.setMinimum( 1)
		spinBox.setMaximum( 5)
		spinBox.setEnabled( 0)

		qButton= QtGui.QPushButton('Publish Animation')
		qButton.setFixedHeight( 60)
		qButton.setEnabled( 0)

		## Add to Grid
		gridLayout.addWidget( check01, 0, 0)
		gridLayout.addWidget( check02, 1, 0)
		gridLayout.addWidget( iterCheck, 2, 0)
		gridLayout.addWidget( spinBox, 2, 1)
		gridLayout.addWidget( qButton, 3, 0)
		#--------------------------------#

		self.allAssets_CheckBox= check01
		self.abcFile_CheckBox= check02
		self.iterations_CheckBox= iterCheck
		self.iterations_SpinBox= spinBox
		self.publishAnimation_Button= qButton

		## Adding Extra Gui Functions
		self.assetName_Widget.setSelectionMode( QtGui.QAbstractItemView.ExtendedSelection)


#------------------- GUI CONNECTIONS----------------------------------#
	def setup_Connections( self):
		'''
		Purpose:
			Provide all signal connections for GUI window
		'''
		## Asset Name Section
		self.assetName_Widget.itemSelectionChanged.connect( self.assetName_hasChanged)

		## Select All Section
		self.allAssets_CheckBox.clicked.connect( self.allAssets_clicked)

		## Alembic Section
		self.abcFile_CheckBox.clicked.connect( self.abc_clicked)

		## Iterations Section
		self.iterations_CheckBox.clicked.connect( self.iterations_clicked)

		## Publish Animation Section
		self.publishAnimation_Button.clicked.connect( self.publishAnimation_clicked)


#------------------- ADD GUI ElEMENTS----------------------------------#
	def populate_Widgets( self):
		'''
		Purpose:
			Popuplate Asset Widget with
		Popuplate Name space layout with namespaces in scene
		'''
		for each in self.guiFunc.namespace_List:
			## Check if asset is still in the scene
			if( translator.namespaceExists( each)):
				## Add items
				self.assetName_Widget.addItem( each)


#------------------- GUI SIGNALS----------------------------------#
	def assetName_hasChanged( self):
		'''
		Enable publishAsset_Button
		'''
		if( len(self.assetName_Widget.selectedItems())== 0):
			self.publishAnimation_Button.setEnabled( 0)

		else:
			self.publishAnimation_Button.setEnabled( 1)
			self.allAssets_CheckBox.setChecked( 0)
	#
	def allAssets_clicked( self):
		'''
		Purpose:
			Select all items in List and turn on publish button
		'''
		if( self.allAssets_CheckBox.isChecked()):
			self.publishAnimation_Button.setEnabled( 1)

			## Select all items in list
			for i in range( self.assetName_Widget.count()):
				self.assetName_Widget.item( i).setSelected( 1)
	#
	def abc_clicked( self):
		'''
		Purpose:
			Turn on or off iteration Checkbox
		'''
		if( self.abcFile_CheckBox.isChecked()):
			self.iterations_CheckBox.setEnabled( 1)
		else:
			self.iterations_CheckBox.setEnabled( 0)
			self.iterations_CheckBox.setChecked( 0)
			self.iterations_SpinBox.setEnabled( 0)
	#
	def iterations_clicked( self):
		'''
		Purpose:
			Turn on or off iteration spinBox
		'''
		if( self.iterations_CheckBox.isChecked()):
			self.iterations_SpinBox.setEnabled( 1)
		else:
			self.iterations_SpinBox.setEnabled( 0)
	#
	def publishAnimation_clicked( self):
		'''
		Enable publishAsset_Button
		'''
		if( len(self.assetName_Widget.selectedItems())== 0):
			return

		self.close()

		## Create Publish Animation Curve Folder
		self.guiFunc.create_publishFolder()

		## Grab selected Rigs
		assetList=[]
		tempList= self.sceneAssetList.selectedItems()

		## Convert Qitem to string
		for each in tempList:
			assetList.append( str(each.text()))

		if( self.allAssets_CheckBox.isChecked()):
			## Grab full item list
			assetList=[]
			for i in range( self.assetName_Widget.count()):
				assetList.append( str( self.assetName_Widget.item( i).text()))

		for each in assetList:
			## Save out animation
			result= self.guiFunc.prepAssets( each)

			if( self.abcFile_CheckBox.isChecked() and result):

				if( self.iterations_CheckBox.isChecked()):
					iterationValue= int( self.iterations_SpinBox.value())
					## Save out alembic file
					self.guiFunc.saveAlembic( each, iterationValue)

				else:
					## Save out alembic file
					self.guiFunc.saveAlembic( each)

			## Store Data
			self.guiFunc.store_publishData()




def main():
	'''
	Show Window
	'''
	translator.launch( GUI, None)



if __name__ == '__main__':
	main()
