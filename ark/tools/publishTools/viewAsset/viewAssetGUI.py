'''
Author: Carlo Cherisier
Date: 09.10.14
Script: viewAssetGUI

python.execute("
import sys;
sys.path.append('c:/ie/ark/tools');
import viewAsset; reload( viewAsset); viewAsset.main();
")
'''
from PySide import QtGui

import arkInit
arkInit.init()

import translators
translator = translators.getCurrent()

import viewAssetFUNC as guiFunc
reload( guiFunc)


class GUI( QtGui.QDialog):
	def __init__(self, parent=None):
		super(GUI, self).__init__(parent)

		## GUI Functions Class
		self.guiFunc= guiFunc.guiFunc()
		self.guiFunc.getGuiInformation()

		## Setup GUI
		self.create_Window()
		self.populate_Widgets()
		self.setup_Connections()


#------------------- WINDOW CREATION----------------------------------#
	def create_Window( self):
		'''
		Here is where the window
		is created
		'''
		## Window Title
		self.setWindowTitle( 'Views In Scene Asset')

		## Window Settings
		self.resize( 600, 300)

		## Set GUI Layouts
		self.mainlayout= QtGui.QHBoxLayout()
		#--------------------------------#

		## Table Section
		vBox_layout01= QtGui.QVBoxLayout()
		qTable= QtGui.QTableWidget()
		qTable.setSelectionBehavior( QtGui.QAbstractItemView.SelectRows)
		qTable.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
		qTable.setSelectionMode( QtGui.QAbstractItemView.ExtendedSelection)
		qTable.verticalHeader().hide()
		qTable.setColumnCount(4)
		vBox_layout01.addWidget( qTable)

		label_List= ['Namespace', 'Department', 'Version', 'Asset Type']
		qTable.setHorizontalHeaderLabels( label_List)
		self.viewTable= qTable
		#--------------------------------#

		## Button Section
		hBox_layout01 = QtGui.QHBoxLayout()
		b1= QtGui.QPushButton('Select Assets')
		b2= QtGui.QPushButton('Update Assets')
		b3= QtGui.QPushButton('Delete Assets')
		hBox_layout01.addWidget( b1)
		hBox_layout01.addWidget( b2)
		hBox_layout01.addWidget( b3)

		self.selectAssets_Button= b1
		self.updateAssets_Button= b2
		self.deleteAssets_Button= b3
		#--------------------------------#

		## Asset Type Button Section
		vBox_layout02 = QtGui.QVBoxLayout()
		label= QtGui.QLabel('Change Selected Asset To:')
		b1= QtGui.QPushButton('Bounding Box')
		b2= QtGui.QPushButton('Low Res')
		b3= QtGui.QPushButton('Hi Res')
		b4= QtGui.QPushButton('Vray Proxy')
		b5= QtGui.QPushButton('Maxwell Proxy')
		b6= QtGui.QPushButton('Alembic')
		vBox_layout02.addWidget( label)
		vBox_layout02.addWidget( b1)
		vBox_layout02.addWidget( b2)
		vBox_layout02.addWidget( b3)
		vBox_layout02.addWidget( b4)
		vBox_layout02.addWidget( b5)
		vBox_layout02.addWidget( b6)
		#--------------------------------#

		self.bBox_Button= b1
		self.lowRez_Button= b2
		self.hiRez_Button= b3
		self.vRay_Button= b4
		self.maxWell_Button= b5
		self.alembic_Button= b6

		## Finalize Layout
		vBox_layout01.addLayout( hBox_layout01)
		self.mainlayout.addLayout( vBox_layout01)
		self.mainlayout.addLayout( vBox_layout02)
		self.setLayout( self.mainlayout)

		## Show Gui
		self.show()
	#
	def setup_Connections( self):
		'''
		Contains all Connections to GUI elements
		'''
		## QTable
		self.viewTable.itemDoubleClicked.connect( self.viewTable_itemClicked)

		## Select Button
		self.selectAssets_Button.clicked.connect( self.selectAssets_clicked)

		## Update Button
		self.updateAssets_Button.clicked.connect( self.updateAssets_clicked)

		## Delete Button
		self.deleteAssets_Button.clicked.connect( self.deleteAssets_clicked)

		## Open Latest Button
		self.bBox_Button.clicked.connect( lambda: self.changeAssetType_clicked('bBox'))
		self.lowRez_Button.clicked.connect( lambda: self.changeAssetType_clicked('lowRez'))
		self.hiRez_Button.clicked.connect( lambda: self.changeAssetType_clicked('hiRez'))
		self.vRay_Button.clicked.connect( lambda: self.changeAssetType_clicked('vRayProxy'))
		self.maxWell_Button.clicked.connect( lambda: self.changeAssetType_clicked('maxWell'))
		self.alembic_Button.clicked.connect( lambda: self.changeAssetType_clicked('alembic'))


#------------------- ADD GUI ElEMENTS----------------------------------#
	def populate_Widgets( self):
		'''
		Popuplate Name space layout with namespaces in scene
		'''
		## Reset Table
		self.viewTable.setRowCount(0)

		## Set number of rows available in Table
		self.viewTable.setRowCount( len(self.guiFunc.namespace_List))

		for rowNum, each in enumerate(self.guiFunc.namespace_List, start= 0):
			## Convert to QItem
			qeachItem = QtGui.QTableWidgetItem( each)

			##Add file name to Table at column 0
			self.viewTable.setItem(rowNum, 0, qeachItem)

		for rowNum, each in enumerate(self.guiFunc.deptName_List, start= 0):
			## Convert to QItem
			qeachItem = QtGui.QTableWidgetItem( each)

			##Add file name to Table at column 1
			self.viewTable.setItem(rowNum, 1, qeachItem)

		for rowNum, each in enumerate(self.guiFunc.assetVersion_List, start= 0):
			## Convert to QItem
			qeachItem = QtGui.QTableWidgetItem( each)

			##Add file name to Table at column 2
			self.viewTable.setItem(rowNum, 2, qeachItem)

		for rowNum, each in enumerate(self.guiFunc.assetType_List, start= 0):
			## Convert to QItem
			qeachItem = QtGui.QTableWidgetItem( each)

			##Add file name to Table at column 3
			self.viewTable.setItem(rowNum,3, qeachItem)

		self.viewTable.resizeColumnsToContents()
	#
	def get_selectedItems( self):
		'''
		Grab selected item name and row
		'''
		##Grab selected fileName
		temp_List= self.viewTable.selectionModel().selectedRows()

		row_List=[]
		for each in temp_List:
			row_List.append( each.row())

		holder_Dict={}
		for each in row_List:
			## Grab Widget Info
			namespace= str(self.viewTable.item( each, 0).text())

			## Store namespace and row number
			holder_Dict[ namespace] = each

		return holder_Dict


#------------------- GUI SIGNALS----------------------------------#
	def viewTable_itemClicked( self):
		'''
		Connect Widget Signals to functions
		'''
		##Grab selected fileName
		selectedRow= self.viewTable.selectionModel().selectedRows()[0].row()

		## Grab Widget Info
		namespace= str(self.viewTable.item( selectedRow, 0).text())

		self.guiFunc.selectAssets( namespace)
	#
	def selectAssets_clicked( self):
		'''
		Connect Widget Signals to functions
		'''
		## Grab selected items
		selected= self.get_selectedItems()

		if selected=={}:
			return

		self.guiFunc.selectMultipleAssets( selected.keys())
	#
	def updateAssets_clicked( self):
		'''
		Connect Widget Signals to functions
		'''
		holder= None

		## Grab selected items
		selected= self.get_selectedItems()

		if selected=={}:
			return

		## Check for new Published Assets
		holder, declinedAssets= self.guiFunc.checkAssetForUpdates( selected.keys())

		if holder!= {}:
			for each in holder.keys():
				## Convert version number into QItem
				qeachItem = QtGui.QTableWidgetItem( holder[each])

				## Update Asset Version number to QTable at column 2
				self.viewTable.setItem( selected[each], 2, qeachItem)

			if len( declinedAssets) > 0:
				message= '\n'.join( [each for each in declinedAssets])
				QtGui.QMessageBox.warning( self, "Warning Asset Not Updated", message)

		else:
			message= ', '.join( [each for each in selected.keys()])
			QtGui.QMessageBox.about( None, "Warning Asset Not Updated", message+ ' are up-to-date!')
	#
	def deleteAssets_clicked( self):
		'''
		Connect Widget Signals to functions
		'''
		## Grab selected items
		selected= self.get_selectedItems()

		if selected=={}:
			return

		## Delete asset from scene
 		self.guiFunc.deleteAssets( selected.keys())

 		## Remove asset from list
 		for each in selected.keys():
	 		self.guiFunc.namespace_List.remove( each)

	 	## Remove asset from widget table
	 	self.populate_Widgets()

 		message= ', '.join( [each for each in selected.keys()])+ ': Has/ Have been deleted'
 		QtGui.QMessageBox.about( None, "Assets Deleted from Scene", message)
	#
	def changeAssetType_clicked( self, assetType):
		'''
		Change selected Asset's asset Type
		'''
		## Grab selected items
		selected= self.get_selectedItems()

		if selected=={}:
			QtGui.QMessageBox.about( None, "Warning Asset Not Changed", 'Nothing is selected!')
			return

		if assetType== 'alembic' or assetType== 'maxWell':
			print 'Not ready!!'
			return

		else:
			print assetType
			holder, declinedAssets= self.guiFunc.changeAssetType( selected.keys(), assetType)

		if len( holder.keys()) != 0:
			for each in holder.keys():
				## Convert Asset Type into QItem
				qeachItem = QtGui.QTableWidgetItem( holder[each])

				## Update Asset Type in QTable at column 3
				self.viewTable.setItem( selected[each], 3, qeachItem)

			if len( declinedAssets) > 0:
				## Inform user of unchanged assets
				result= '\n'.join( [ x for x in declinedAssets.values()])
				QtGui.QMessageBox.warning( self, "Warning Asset Not Changed", result)


def main():
	'''
	Show Window
	'''
	translator.launch( GUI, None)



if __name__ == '__main__':
	main()