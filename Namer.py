# Control Namer and Painter
import inspect

import json
import maya.cmds as mc
import os

import collections

from PySide import QtCore
from PySide import QtGui
try:
	from qtpy import QtWidgets

	for name in dir(QtWidgets):
		obj = getattr(QtWidgets, name)
		if inspect.isclass(obj):
			setattr(QtGui, name, obj)

except:
	pass

class Namer(QtGui.QDialog):

	enterPressed = QtCore.Signal(QtCore.QEvent)

	def __init__(self, parent=None):
		super(Namer, self).__init__(parent=parent)

		self.setWindowTitle('Namer')
		# self.resize(500, 300)
		# if not os.path.isfile(os.environ.get('MAYA_APP_DIR') + '/2017/prefs/controlNamePrefs.json'):
		# 	messageBox = QtGui.QMessageBox()
		# 	messageBox.setText('This program is runnning for the first time. Have fun!')
		# 	self.nameWidgets = None

		# else:
		# 	self.buildWidgets()

		mainLayout = QtGui.QVBoxLayout()

		self.setLayout(mainLayout)

		self.nameWidgets = collections.deque()
		# read from json list and populate self.nameWidgets

		self.namingLayout = QtGui.QHBoxLayout()
		mainLayout.addLayout(self.namingLayout)

		# self.addNameWidgets()

		leftNameButtonsLayout = QtGui.QVBoxLayout()
		self.namingLayout.addLayout(leftNameButtonsLayout)

		self.leftAddButton = QtGui.QPushButton('+')
		leftNameButtonsLayout.addWidget(self.leftAddButton)
		self.leftAddButton.setObjectName('leftAdd')
		self.leftAddButton.clicked.connect(self.addNameWidget)

		self.leftRemoveButton = QtGui.QPushButton('-')
		leftNameButtonsLayout.addWidget(self.leftRemoveButton)
		self.leftRemoveButton.setObjectName('leftRemove')
		self.leftRemoveButton.clicked.connect(self.removeNameWidget)

		self.nameWidgetsLayout = QtGui.QHBoxLayout()
		self.namingLayout.addLayout(self.nameWidgetsLayout)

		rightNameButtonsLayout = QtGui.QVBoxLayout()
		self.namingLayout.addLayout(rightNameButtonsLayout)

		self.rightAddButton = QtGui.QPushButton('+')
		self.rightAddButton.setObjectName('rightAdd')
		rightNameButtonsLayout.addWidget(self.rightAddButton)
		self.rightAddButton.clicked.connect(self.addNameWidget)

		self.rightRemoveButton = QtGui.QPushButton('-')
		rightNameButtonsLayout.addWidget(self.rightRemoveButton)
		self.rightRemoveButton.setObjectName('rightRemove')
		self.rightRemoveButton.clicked.connect(self.removeNameWidget)

		finalNameLayout = QtGui.QHBoxLayout()
		mainLayout.addLayout(finalNameLayout)

		# self.saveLayoutButton = QtGui.QPushButton('Save Layout')
		# finalNameLayout.addWidget(self.saveLayoutButton)
		# self.saveLayoutButton.clicked.connect(self.saveNameLayout)

		finalNameLayout.addWidget(QtGui.QLabel('Increment After:'))
		self.incrementAfter = QtGui.QLineEdit()
		self.incrementAfter.setValidator(QtGui.QIntValidator())
		finalNameLayout.addWidget(self.incrementAfter)

 		finalNameLayout.addWidget(QtGui.QLabel('Separator'))
		self.separator = QtGui.QLineEdit('_')
		finalNameLayout.addWidget(self.separator)

		self.setNamesButton = QtGui.QPushButton('Set Names')
		self.setNamesButton.clicked.connect(self.nameSelected)
		finalNameLayout.addWidget(self.setNamesButton)

	def keyPressEvent(self, event):
		if event.key() in [QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter]:
			event.ignore()
			return

		super(Namer, self).keyPressEvent(event)

	def showError(self, message):
		errorMessage = QtGui.QErrorMessage(self)
		errorMessage.showMessage(message)

	def buildWidget(self):
		# with open('C:/Tools/trashTest/controlNamePrefs.json', 'r+') as f:
		# 	dictionary = json.load(f)

		# for option in dictionary['AllOptions']:
		# 	pass		self.leftAddButton.setObjectName('left')

		# create VLayout
		nameWidget = NameOptionsWidget(parent=self)

		return nameWidget

		# add blank widget if self.nameWidgets in empty
		# get dictionaries from json file and add widgets


	def addNameWidget(self):
		if len(self.nameWidgets) == 0:
			pass

		widget = self.buildWidget()
		if self.sender().objectName() == 'leftAdd':
			self.nameWidgets.appendleft(widget)
			self.nameWidgetsLayout.insertWidget(0, widget)

		else:
			self.nameWidgets.append(widget)
			self.nameWidgetsLayout.insertWidget(-1, widget)


		# add nameWidget to the right or left of current widget
		# and make a dictionary item containing values
		# connect dictionary item to final name text field
		# append dictionary to self.nameWidgets

	def removeNameWidget(self):
		if self.sender().objectName() == 'leftRemove':
			try:
				obj = self.nameWidgets.popleft()
				print obj.getValue()
			except IndexError:
				pass

		else:
			try:
				obj = self.nameWidgets.pop()
			except IndexError:
				pass


		obj.deleteLater()
		# delete widget from current layout from the right or left
		# pop from the dictionary list
		# if len(current list) == 0:
			# add blank widget

	# def saveNameLayout(self):
	# 	# write current layout to json file in a listed dictionary format
	# 	# stored in Maya dirs
	# 	pass

	def nameSelected(self):
		selection = mc.ls(sl=True)
		separator = self.separator.text()
		nameList = []
		incrementPartition = int(self.incrementAfter.text()) - 1
		if incrementPartition > len(self.nameWidgets):
			self.showError('Partiton location more than number of partitions')
			return

		for widget in self.nameWidgets:
			nameList.append(widget.getValue())

		counter = 1
		for obj in selection:
			finalName = ''
			i = 0
			for name in nameList:
				finalName += name
				if i == incrementPartition:
					finalName += str(counter)
				if i != len(nameList) - 1:
					finalName += separator
				i += 1
			print finalName
			mc.rename(obj, finalName)
			counter += 1

class NameOptionsWidget(QtGui.QWidget):

	def __init__(self, parent=None):
		super(NameOptionsWidget, self).__init__()

		self.value = None

		widgetLayout = QtGui.QVBoxLayout()
		self.setLayout(widgetLayout)

		nameLayout = QtGui.QHBoxLayout()
		nameLayout.addWidget(QtGui.QLabel('Name'))
		self.nameText = QtGui.QLineEdit()
		nameLayout.addWidget(self.nameText)

		widgetLayout.addLayout(nameLayout)

		optionsLayout = QtGui.QVBoxLayout()
		optionsLayout.addWidget(QtGui.QLabel('Options'))

		self.optionsList = QtGui.QListWidget()
		optionsLayout.addWidget(self.optionsList)

		widgetLayout.addLayout(optionsLayout)
		self.optionsList.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)

		self.nameText.returnPressed.connect(self.addValue)

		self.optionsList.itemClicked.connect(self.setValue)
		self.optionsList.itemDoubleClicked.connect(self.removeValue)

	def addValue(self):
		value = self.nameText.text()
		self.optionsList.insertItem(0, value)
		self.nameText.clear()

	def setValue(self):
		self.value = self.optionsList.currentItem().text()

	def getValue(self):
		return self.value

	def removeValue(self):
		currentRow = self.optionsList.currentRow()
		self.optionsList.takeItem(currentRow)

# if __name__ == '__main__':
#     app = QtGui.QApplication(sys.argv)
#     main_window = Namer()
#     main_window.show()
#     sys.exit(app.exec_())

test = Namer()
test.show()