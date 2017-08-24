# Control Namer and Painter
import inspect
import sys
import json
# import maya.cmds as mc
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

		# if not os.path.isfile(os.environ.get('MAYA_APP_DIR') + '/2017/prefs/controlNamePrefs.json'):
		# 	messageBox = QtGui.QMessageBox()
		# 	messageBox.setText('This program is runnning for the first time. Have fun!')
		# 	self.nameWidgets = None

		# else:
		# 	self.buildWidgets()
		
		mainLayout = QtGui.QVBoxLayout()
		

		self.setLayout(mainLayout)

		self.nameWidgets = []
		# read from json list and populate self.nameWidgets

		namingLayout = QtGui.QHBoxLayout()
		mainLayout.addLayout(namingLayout)

		# self.addNameWidgets()

		leftNameButtonsLayout = QtGui.QVBoxLayout()
		namingLayout.addLayout(leftNameButtonsLayout)

		self.leftAddButton = QtGui.QPushButton('+')
		leftNameButtonsLayout.addWidget(self.leftAddButton)
		self.leftAddButton.clicked.connect(self.addNameWidget)

		self.leftRemoveButton = QtGui.QPushButton('-')
		leftNameButtonsLayout.addWidget(self.leftRemoveButton)
		self.leftRemoveButton.clicked.connect(self.removeNameWidget)

		rightNameButtonsLayout = QtGui.QVBoxLayout()
		namingLayout.addLayout(rightNameButtonsLayout)

		self.rightAddButton = QtGui.QPushButton('+')
		rightNameButtonsLayout.addWidget(self.rightAddButton)
		self.rightAddButton.clicked.connect(self.addNameWidget)

		self.rightRemoveButton = QtGui.QPushButton('-')
		rightNameButtonsLayout.addWidget(self.rightRemoveButton)
		self.rightRemoveButton.clicked.connect(self.removeNameWidget)

		finalNameLayout = QtGui.QHBoxLayout()
		mainLayout.addLayout(finalNameLayout)

		self.saveLayoutButton = QtGui.QPushButton('Save Layout')
		finalNameLayout.addWidget(self.saveLayoutButton)
		self.saveLayoutButton.clicked.connect(self.saveNameLayout)

		self.finalNameText = QtGui.QLineEdit('_')
		finalNameLayout.addWidget(self.finalNameText)

		self.setNamesButton = QtGui.QPushButton('Set Names')
		finalNameLayout.addWidget(self.setNamesButton)

		self.show()

	def buildWidgets(self):
		pass
		# with open('C:/Tools/trashTest/controlNamePrefs.json', 'r+') as f:
		# 	dictionary = json.load(f)

		# for option in dictionary['AllOptions']:
		# 	pass


		# add blank widget if self.nameWidgets in empty
		# get dictionaries from json file and add widgets


	def addNameWidget(self):
		if len(self.nameWidgets) == 0:
			pass

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


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    main_window = ControlNamerPainter()
    sys.exit(app.exec_())
