'''
Author: Carlo Cherisier
Date: 10.28.14
Script: objectMatcher

import sys
sys.path.append( 'C:/ie/ark/tools/objectAlign')
import objectAlign
reload( objectAlign)
objectAlign.main()
'''
from PySide import QtGui

import arkInit
arkInit.init()

import translators
translator = translators.getCurrent()

import maya.cmds as cmds
import weakref

class Callback(object):
	def __init__(self, func, *args, **kwargs):
		self.func = func
		self.args = args
		self.kwargs = kwargs
	def __call__(self, *args):
		return self.func( *self.args, **self.kwargs )

class GUI( QtGui.QDialog):
	'''
	Match one object transform to another
	'''
	objID_Dict = weakref.WeakValueDictionary()
	activeList = None

	def __init__(self, parent=None):
		super(GUI, self).__init__(parent)
		# w = self.window()

		## Store Instance
		self.set_objID_Dict( self )

		## Close instance if it exist
		if len( self.objID_Dict) >= 2:
			idNum = self.objID_Dict.keys()[0]

			inst = self.get_objFromID_Dict( idNum)
			inst.close()

			del self.objID_Dict[ idNum]

		##Class Variables
		self.parent = ''
		self.posSkipList = ['x', 'y', 'z']
		self.rotSkipList = ['x', 'y', 'z']
		self.posToggle = 1
		self.rotToggle = 1

		## Setup GUI
		self.create_Window()
		self.setup_Connections()
		self.addElements()


	def set_objID_Dict( self, obj):
		idNum = id(obj)
		self.objID_Dict[idNum] = obj


	def get_objFromID_Dict( self, idNum):
		return self.objID_Dict[idNum]

#------------------- WINDOW CREATION----------------------------------#
	def create_Window( self):
		'''
		Purpose:
			Create UI
		'''
		## Window Title
		self.setWindowTitle( 'Object Aligner')

		## Window Settings
		#self.setMinimumSize( 1000, 200)
		self.setFixedSize ( 300, 150)

		## Set GUI Layouts
		self.guiLayout= QtGui.QVBoxLayout()
		self.setLayout( self.guiLayout)

		#### Local Drive Section ####
		formlay = QtGui.QFormLayout()
		self.guiLayout.addLayout( formlay)

		## Add To Layout
		box = QtGui.QHBoxLayout()
		qLine01 = QtGui.QLineEdit()
		qLine01.setEnabled( 0)
		qButton01 = QtGui.QPushButton('Update')
		box.addWidget( qLine01)
		box.addWidget( qButton01)
		formlay.addRow( 'Parent', box)

		## Add To Layout
		label = QtGui.QLabel ( 'Select Children')
		formlay.addRow( '', label)

		## Add To Layout
		box = QtGui.QHBoxLayout()
		check01 = QtGui.QCheckBox('X')
		check02 = QtGui.QCheckBox('Y')
		check03 = QtGui.QCheckBox('Z')
		qButton03 = QtGui.QPushButton('Toggle Checkboxes')
		box.addWidget( check01)
		box.addWidget( check02)
		box.addWidget( check03)
		box.addWidget( qButton03)
		formlay.addRow( 'Position', box)

		## Add To Layout
		box = QtGui.QHBoxLayout()
		check05 = QtGui.QCheckBox('Y')
		check04 = QtGui.QCheckBox('X')
		check06 = QtGui.QCheckBox('Z')
		qButton04 = QtGui.QPushButton('Toggle Checkboxes')
		box.addWidget( check04)
		box.addWidget( check05)
		box.addWidget( check06)
		box.addWidget( qButton04)
		formlay.addRow( 'Rotation', box)

		## Constraint Button
		self.makeConstraint = QtGui.QPushButton('Align Selection To Parent')
		self.guiLayout.addWidget( self.makeConstraint)

		self.parentLine = qLine01
		self.parentButton = qButton01

		self.posXCheckbox = check01
		self.posYCheckbox = check02
		self.posZCheckbox = check03
		self.posButton = qButton03

		self.rotXCheckbox = check04
		self.rotYCheckbox = check05
		self.rotZCheckbox = check06
		self.rotButton = qButton04

		## Show Gui
		self.show()

#------------------- GUI CONNECTIONS----------------------------------#
	def setup_Connections( self):
		'''
		Contains all Connections to GUI elements
		'''
		## Parent Button
		self.parentButton.clicked.connect( self.updateParentName)

		## Pos and Rot Button
		self.posButton.clicked.connect( self.updatePosToggle)
		self.rotButton.clicked.connect( self.updateRotToggle)

		##Asset Name
		self.posXCheckbox.stateChanged.connect( lambda: self.updatePosCheckbox('x', self.posXCheckbox))
		self.posYCheckbox.stateChanged.connect( lambda: self.updatePosCheckbox('y', self.posYCheckbox))
		self.posZCheckbox.stateChanged.connect( lambda: self.updatePosCheckbox('z', self.posZCheckbox))
		self.rotXCheckbox.stateChanged.connect( lambda: self.updateRotCheckbox('x', self.rotXCheckbox))
		self.rotYCheckbox.stateChanged.connect( lambda: self.updateRotCheckbox('y', self.rotYCheckbox))
		self.rotZCheckbox.stateChanged.connect( lambda: self.updateRotCheckbox('z', self.rotZCheckbox))

		## Publish Button
		self.makeConstraint.clicked.connect( Callback(self.executeConstraint))
	#
	def addElements( self):

		if len( cmds.ls( sl=1)) > 2:
			self.parent = cmds.ls( sl=1)[0]
			self.parentLine.setText( self.parent)

			self.childrenList = cmds.ls( sl=1)[1:]
			temp= ' ,'.join( self.childrenList)
			self.childLine.setText( temp)

#------------------- GUI FUNCTIONS----------------------------------#
	def updateParentName( self):
		'''
		Purpose:
			Update parent item
		'''
		self.parent = cmds.ls( sl=1)[0]

		self.parentLine.setText( self.parent)
	#
	def updateChildrenNames( self):
		'''
		Purpose:
			Update parent item
		'''
		self.childrenList = cmds.ls( sl=1)

		temp= ' ,'.join( self.childrenList)
		self.childLine.setText( temp)
	#
	def updatePosToggle( self):
		if self.posXCheckbox.isChecked() and self.posYCheckbox.isChecked() and self.posZCheckbox.isChecked():
			self.posToggle = 0

		if self.posToggle == 1:
			self.posXCheckbox.setChecked( 1)
			self.posYCheckbox.setChecked( 1)
			self.posZCheckbox.setChecked( 1)



		else:
			self.posXCheckbox.setChecked( 0)
			self.posYCheckbox.setChecked( 0)
			self.posZCheckbox.setChecked( 0)

			self.posToggle = 1
	#
	def updateRotToggle( self):
		if self.rotXCheckbox.isChecked() and self.rotYCheckbox.isChecked() and self.rotZCheckbox.isChecked():
			self.rotToggle = 0

		if self.rotToggle == 1:
			self.rotXCheckbox.setChecked( 1)
			self.rotYCheckbox.setChecked( 1)
			self.rotZCheckbox.setChecked( 1)

			self.rotToggle = 0
		else:
			self.rotXCheckbox.setChecked( 0)
			self.rotYCheckbox.setChecked( 0)
			self.rotZCheckbox.setChecked( 0)

			self.rotToggle = 1
	#
	def updatePosCheckbox( self, value, checkBox):
		'''
		Purpose:
			Set axis for point constraint
		'''
		if checkBox.isChecked() == True:
			if value in self.posSkipList:
				self.posSkipList.remove( value)

		else:
			self.posSkipList.append( value)
	#
	def updateRotCheckbox( self, value, checkBox):
		'''
		Purpose:
			Set axis for orient constraint
		'''
		if checkBox.isChecked() == True:
			if value in self.rotSkipList:
				self.rotSkipList.remove( value)

		else:
			self.rotSkipList.append( value)
	#
	def executeConstraint( self):
		'''
		Purpose:
			Align selected objects to parent
		'''
		childrenList= cmds.ls( sl= 1)

		for each in childrenList:
			if each == self.parent:
				continue

			result= cmds.pointConstraint( self.parent, each, skip= self.posSkipList)
			cmds.delete( result)

			result= cmds.orientConstraint( self.parent, each, skip= self.rotSkipList)
			cmds.delete( result)



#------------------- CALL GUI----------------------------------#
def main():
	'''
	Show Window
	'''
	window = translator.launch( GUI, None)
	return window

if __name__ == '__main__':
	main()