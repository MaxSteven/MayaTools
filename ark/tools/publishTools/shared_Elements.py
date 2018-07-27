'''
Author: Carlo Cherisier
Date: 10.02.14
Script: shared_Elements
'''
from PySide import QtGui
import os.path

import arkInit
arkInit.init()

import translators
translator = translators.getCurrent()

import caretaker
ct = caretaker.getCaretaker()

## Class Variables
global global_filePath
global_filePath=''
global local_filePath
local_filePath=''

def make_listWidget( widgetName, setWidth=200, returnLayout= False):
	'''
	Purpose:
		Create QGroup with a list widget
	'''
	## Create Group Layout
	groupBox = QtGui.QGroupBox( widgetName)
	groupBox.setAlignment( 4)
	groupBox.setFixedWidth( setWidth)

	## Create layout for group
	box = QtGui.QVBoxLayout()
	groupBox.setLayout( box)

	##Create List Widget
	widgetVar = QtGui.QListWidget()

	## Main Layout
	box.addWidget( widgetVar)
	groupBox.setFixedWidth( setWidth)

	if returnLayout:
		return groupBox, widgetVar, box
	else:
		return groupBox, widgetVar
#
def make_tableWidget( widgetName, setWidth= 350, returnLayout= False):
	'''
	Purpose:
		Create QGroup with a table widget inside
	'''
	## Create Group Layout
	groupBox = QtGui.QGroupBox( widgetName)
	groupBox.setAlignment( 4)
	groupBox.setFixedWidth( setWidth)

	## Create layout for group
	box = QtGui.QVBoxLayout()
	groupBox.setLayout( box)

	## Create Table
	qTable= QtGui.QTableWidget()
	qTable.setSelectionBehavior( QtGui.QAbstractItemView.SelectRows)
	qTable.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
	qTable.verticalHeader().hide()
	qTable.setColumnCount(2)

	label_List= ['File Name', 'Location']
	qTable.setHorizontalHeaderLabels( label_List)

	## Main Layout
	box.addWidget( qTable)

	if returnLayout:
		return groupBox, qTable, box
	else:
		return groupBox, qTable


#------------------- POPULATE GUI ELEMENTS----------------------------------#
def populate_Projects( widgetName):
	'''
	Purpose:
		Populate Widget with all current projects
	'''
	##  Function Variables
	folderList=[]

	## Grab folder list
	tempList= os.listdir( 'r:/')
	#print( tempList)

	## Folder to remove
	removeList=[ 'Assets', 'Users', 'Website', 'zz_trash', 'Reels', 'Template Project', '_Project_Template', 'Production_Manager', 'Promotional_Material']

	for each in removeList:
		if each in tempList:
			tempList.remove( each)

	for each in tempList:
		holder= 1
		## Join item to folder path
		projectPath=  'r:/'+ each

		## Add anything that is a folder
		if not os.path.isdir( projectPath):
			holder= 0

		## Remove hidden folders
		if '.' in each or '_DO' in each or 'root' in each:
			holder = 0

		## Remove matching folders
		if holder == True:
			folderList.append( each)

	## Add project to widget
 	widgetName.addItems( sorted( [ each.capitalize() for each in folderList]))
#
def populate_Deparments( widgetName, mode):
	'''
	Purpose:
		Popualte Department widget
	'''
	dept_List01=[ 'Model', 'Rig', 'Lighting Asset', 'FX Asset']
	dept_List02=[ 'Anim Scene', 'Lighting Scene', 'FX Scene']

	if mode== 1:
		## Add department to widget
 		widgetName.addItems( dept_List01)

 	elif mode== 2:
		## Add department to widget
 		widgetName.addItems( dept_List01)
 		widgetName.addItems( dept_List02)
#
def populate_assetName( widgetName):
	'''
	Purpose:
		Popualte Asset Name widget
	'''
	## Check if file exist
	if not os.path.exists( global_filePath) :
		return

	## Grab file list
	folderList= os.listdir( global_filePath)

	## Add folder to list
	widgetName.addItems( sorted( [ each.capitalize() for each in folderList]))


#------------------- HANDING GUI ELEMENTS----------------------------------#
def create_guiPath( projName= None, deptName= None, assetName= None, fileName= None, mode= None):
	'''
	Purpose:
		Use GUI widget results to create path to assets' folders and files
	'''
	department_Dict={ 'Model':['Project_Assets','Model'],
				'Lighting Asset':['Project_Assets', 'Lighting'],
				'FX Asset':['Project_Assets', 'FX'],
				'Rig':['Project_Assets', 'Rig'],
				'Anim Scene':['Workspaces', 'Anim'],
				'Lighting Scene':['Workspaces', 'Lighting' ],
				'FX Scene':['Workspaces', 'FX'],
				'Testing Folder':['Project_Assets', 'Testing'],
				}
	if projName!= '' and projName!= None:
		path= 'r:/'+ projName

		if mode== 'camera':
			path= path + '/Workspaces'

	if deptName!= ''and deptName!= None:
		path= path+ '/'+ department_Dict[deptName][0]

	if assetName!= '' and assetName!= None:
		path= path+ '/'+ assetName
		path= path+ '/'+ department_Dict[deptName][1]

	if fileName!='' and fileName!= None:
		path= path+ '/'+ fileName

	if projName!= '' and projName!= None:
		## Fix Path '\' issue
		global global_filePath
		global_filePath= path
	return path
#
def select_guiItem( widget, itemName='', mode= None):
	'''
	Purpose:
		Select item in widget
	'''
	found = False
	if mode== 'localDrive':
		## Store widget items in combo
		nameList = [ widget.item(i) for i in range( widget.count())]

		## Find itemName in list
		result= [ each for each in nameList if itemName in each.text()]

		if result != []:
			widget.setItemText( result[0])
			found = True

	else:
		## Store widget items in list
		nameList = [ widget.item(i) for i in range( widget.count())]

		## Find itemName in list
		result= [ each for each in nameList if itemName in each.text()]

		if result != []:
			widget.setCurrentItem( result[0])
			found = True

	if found == False:
		return False
#
def get_dataForGUI():
	'''
	Purpose:
		Get scene data stored in file
	'''
	## Retrieve variables inside Application to use for Smart Save Tool
	localDrive= translator.getData( 'smart_localDrive')

	projName= translator.getData( 'smart_projName')
	if projName== '' or projName== None:
		return None

	deptName= translator.getData( 'smart_deptName')
	assetName= translator.getData( 'smart_assetName')
	fileName= translator.getData( 'smart_fileName')

	# print localDrive, projName, deptName, assetName, fileName
	return localDrive, projName, deptName, assetName, fileName

