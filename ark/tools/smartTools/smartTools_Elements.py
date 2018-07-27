'''
Author: Carlo Cherisier
Date: 10.02.14
Script: shared_Elements
'''
from PySide import QtGui
import os.path, re

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
#
def make_notesWidget( widgetName, setWidth=200, returnLayout= False):
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

	##Create Line and TextField
	qLine= QtGui.QLineEdit()
	qText= QtGui.QTextEdit()

	try:
		## Set User Name
		qLine.setText( ct.userInfo['name'])
	except:
		pass

	##Disable use
	qLine.setEnabled( 0)

	## Main Layout
	box.addWidget( qLine)
	box.addWidget( qText)

	if returnLayout:
		return groupBox, qLine, qText, box
	else:
		return groupBox, qLine, qText

#------------------- POPULATE GUI ELEMENTS----------------------------------#
def populate_localDrive( widgetName):
	##Grab drives
	temp_List= re.findall(r"[A-Z]+:.*$",os.popen("mountvol /").read(),re.MULTILINE)

	drive_List=[]
	for each in temp_List:
		try:
			os.path.getsize( each)

			each= each.replace( '\\', '/')
			drive_List.append( each)

		except WindowsError:
			pass
	## Add Drive to widget
	widgetName.addItems( drive_List)
#
def populate_Projects( widgetName):
	'''
	Purpose:
		Populate Widget with all current projects
	'''
	## Grab folder list
	tempList= os.listdir( 'r:/')
	#print( tempList)

	## Folder to remove
	removeList=[ 'Assets', 'Users', 'Website', 'zz_trash', 'Reels', 'Template Project', '_Project_Template', 'Production_Manager', 'Promotional_Material']

	for each in removeList:
		if each in tempList:
			tempList.remove( each)

	projectList=[]
	for each in tempList:
		holder= 1
		## Join item to folder path
		projectPath=  'r:/'+ each

		## Add anything that is a folder
		if not os.path.isdir( projectPath):
			holder= 0

		## Remove hidden folders
		if '.' in each or '_DO' in each or 'root' in each:
			holder= 0

		## Remove matching folders
		if holder:
			projectList.append( each)

	## Add project to widget
 	widgetName.addItems( sorted( projectList))
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
	widgetName.addItems( sorted( folderList))
#
def populate_assetVersion( widgetName, assetName, localDrive):
	'''
	Purpose:
		Populate Asset Version Table
	'''
	## Function variables
	globalList = []
	localList = []
	fileList = []

	## Construct local path
	local_filePath= global_filePath.lower().replace( 'r:/', localDrive+ 'ie/projects/')

	## Check if file exist
	if not os.path.exists( global_filePath) and not os.path.exists( local_filePath):
		print 'NO global or local!!'
		return

	## Grab global files
	if os.path.exists( global_filePath):
		globalList= os.listdir( global_filePath)

	## Grab local files
	if os.path.exists( local_filePath):
		localList= os.listdir( local_filePath)

	## Store all global files
	for each in globalList:
		fileList.append( '{0}*Global'.format( each))

	## Store All Global files
	for each in localList:
		tempString= ' '.join( globalList)

		if not bool( re.findall( each, tempString)) and each[-2:] in translator.fileExtension:
			fileList.append( '{0}*Local'.format( each))

	## Reset Table
	widgetName.setRowCount(0)

	## Sort list
	fileList= sortList_descend( fileList)
	tempList = list( fileList)

	## Only grab correct file types for that program
	for item in tempList:
		if item.split( '*')[0].split('.')[-1] != translator.fileExtension:
			fileList.remove( item)

	if len( fileList) == 0:
		return

	## Set number of rows available in Table
	widgetName.setRowCount( len(fileList))

	for rowNum, each in enumerate(fileList, start= 0):
		## Convert to QItem
		## Grab file name and location
		qeachItem = QtGui.QTableWidgetItem( each.split('*')[0])
		qlocation = QtGui.QTableWidgetItem( each.split('*')[1])

		##Add file name to Table at column 0
		widgetName.setItem(rowNum, 0, qeachItem)

		##Add file name to Table at column 0
		widgetName.setItem(rowNum, 1, qlocation)

	##Resize columns
	widgetName.resizeColumnsToContents()


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
	if mode== 'localDrive':
		for i in range( widget.count()):
			##Convert item to str
			localDrive= str( widget.itemText(i))

			if localDrive== itemName :
				widget.setCurrentIndex( i)
	else:
		for i in range( widget.count() ):
			##Convert item to str
			qItem= widget.item( i)
			projName= str( qItem.text() )

			if projName== itemName:
				#print( projName, itemName)
				widget.setCurrentItem( qItem)
#
def get_dataForGUI():
	'''
	Purpose:
		Get scene data stored in file
	'''
	## Retrieve variables inside Application to use for Smart Save Tool
	localDrive= translator.getData( 'smart_localDrive')

	projName = translator.getData( 'smart_projName')
	if projName == '' or projName== None:
		return None

	deptName = translator.getData( 'smart_deptName')
	assetName = translator.getData( 'smart_assetName')
	fileName = translator.getData( 'smart_fileName')

	# print localDrive, projName, deptName, assetName, fileName
	return localDrive, projName, deptName, assetName, fileName

#------------------- ORGANIZATION----------------------------------#
def sortList_descend( key=[]):
	'''
	Rearrange list to descending values
	'''
	##Loop throught list
	for i in range( 1, len(key)):
		for j in range( i):
			## Make sure 'v' (version) is in item name
			check01 = key[i].split('.')[0].split('_')[-2].lower()
			check02 = key[j].split('.')[0].split('_')[-2].lower()

			if 'v' not in check01 or 'v' not in check02:
				continue

			# print key[i], key[j]

			##Grab number value
			num_i= int( key[i].split('.')[0].split('_')[-2].lower().split('v')[-1])
			num_j= int( key[j].split('.')[0].split('_')[-2].lower().split('v')[-1])

			##Compare numbers
			if num_i> num_j:
				hold= key[j]

				key[j]= key[i]
				key[i]= hold
	return key
#
def naturalSort( strings):
	'''
	Sort strings the way humans are said to expect
	'''
	#
	def sorted_nicely(strings):
		'''
		Sort strings the way humans are said to expect
		'''
		newList= sorted(strings, key=natural_sort_key)
		#print( newList)

		return newList
	#
	def natural_sort_key(key):
		import re
		return [int(t) if t.isdigit() else t for t in re.split(r'(\d+)', key)]
	#
	return sorted_nicely( strings)
