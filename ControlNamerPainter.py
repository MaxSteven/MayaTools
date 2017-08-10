# Control Namer and Painter
import inspect
import maya.cmds as mc
import os
try:
	from PySide2 import QtCore, QtNetwork
	from PySide2 import QtWidgets
	from PySide2 import QtGui

	for name in dir(QtWidgets):
		obj = getattr(QtWidgets, name)
		if inspect.isclass(obj):
			setattr(QtGui, name, obj)

except:
	from PySide import QtGui
	from PySide import QtCore

class ControlNamerPainter(QtGui.QDialog):
	def __init__(self, parent=None):
		super(ControlNamerPainter, self).__init__(parent=parent)

		mainLayout = QtGui.QVBoxLayout()

		self.setLayout(mainLayout)

		self.nameWidgets = []
		# read from json list and populate self.nameWidgets

		namingLayout = QtGui.QHBoxLayout()
		mainLayout.addLayout(namingLayout)

		self.addNameWidgets()
		# self.blankWidget = QtGui.QWidget()
		# namingLayout.addWidget(self.blankWidget)

		self.addButton = QtGui.QPushButton('+')
		nameButtonsLayout.addWidget(self.addButton)
		self.addButton.clicked.connect(self.addNameWidget)

		self.removeButton = QtGui.QPushButton('-')
		nameButtonsLayout.addWidget(self.removeButton)
		self.removeButton.clicked.connect(self.removeNameWidget)

		self.saveLayoutButton = QtGui.QPushButton('-')
		nameButtonsLayout.addWidget(self.saveLayoutButton)
		self.saveLayoutButton.clicked.connect(self.saveLayoutWidget)

		nameButtonsLayout = QtGui.QVBoxLayout()
		namingLayout.addLayout(nameButtonsLayout)

		finalNameLayout = QtGui.QHBoxLayout()
		mainLayout.addLayout(finalNameLayout)

		self.finalNameText = QtGui.QLineEdit('_')
		finalNameLayout.addWidget(self.finalNameText)

		self.setNamesButton = QtGui.QPushButton()
		finalNameLayout.addWidget(self.setNamesButton)

		self.show()

	def addNameWidgets(self):
		# add blank widget if self.nameWidgets in empty
		# get dictionaries from json file and add widgets
		pass


	def addNameWidget(self):
		# if len of self.nameWidgets == 0
			# delete blank widget

		# add nameWidget to the right of current widget
		# and make a dictionary item containing values
		# connect dictionary item to final name text field
		# append dictionary to self.nameWidgets
		pass

	def removeNameWidget(self):
		# delete widget from current layout
		# pop from the dictionary list
		# if len(current list) == 0:
			# add blank widget
		pass

	def saveNameLayout(self):
		# write current layout to json file in a listed dictionary format 
		# stored in Maya dirs
		pass

	def nameSelected(self):
		pass 


test = ControlNamerPainter()
