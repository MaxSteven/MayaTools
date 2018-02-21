import maya.cmds as mc
from PySide2 import QtGui, QtCore, QtWidgets

import inspect
import os

class RigTester(QtWidgets.QDialog):
	def __init__(self, parent = None):
		super(RigTester, self).__init__(parent=parent)
		screenCap = ScreenCapture()
		self.screenCapArea = screenCap.getScreenCapDimensions()

		super(RigTester, self).__init__(parent=parent)

		self.setLayout(QtWidgets.QHBoxLayout())
		self.rigTestList = QtWidgets.QListWidget()
		self.layout().setContentsMargins(5,5,5,5)
		self.layout().setSpacing(5)
		self.layout().addWidget(self.rigTestList)

		buttonsLayout = QtWidgets.QVBoxLayout()
		self.layout().addLayout(buttonsLayout)

		self.addRigTestButton = QtWidgets.QPushButton('Add new view')
		self.addRigTestButton.clicked.connect(self.addRigTest)
		buttonsLayout.addWidget(self.addRigTestButton)

		self.setRigTestPathText = QtWidgets.QLineEdit():
		self.layout().addWidget(self.setRigTestPathText)

		self.setRigTestPathButton = QtWidgets.QPushButton('Set path')
		self.setRigTestPathButton.clicked.connect(self.setRigTestPath)
		buttonsLayout.addWidget(self.setRigTestPathButton)

		self.removeRigTestButton = QtWidgets.QPushButton('Remove view')
		self.removeRigTestButton.clicked.connect(self.removeRigTest)
		buttonsLayout.addWidget(self.removeRigTestButton)

		self.generateTestButton = QtWidgets.QPushButton('Generate Test')
		self.generateTestButton.clicked.connect(self.generateTest)
		buttonsLayout.addWidget(self.generateTestButton)

		self.saveTestButton = QtWidgets.QPushButton('Remove view')
		self.saveTestButton.clicked.connect(self.saveTest)
		buttonsLayout.addWidget(self.saveTestButton)

		self.loadTestButton = QtWidgets.QPushButton('Remove view')
		self.loadTestButton.clicked.connect(self.loadTest)
		buttonsLayout.addWidget(self.loadTestButton)

	def addView(self):
		pass

	def removeView(self):
		pass

	def setPath(self):
		pass

	def generateTest(self):
		pass

	def loadTest(self):
		pass

	def saveTest(self):
		pass

class ScreenCapture():
	def __init__(self, parent = None):
		super(ScreenCapture, self).__init__(parent=parent)
		img = ImageGrab.grab
		size = img().size
		screen_width = size[0]
		screen_height = size[1]
		self.setGeometry(0, 0, screen_width, screen_height)
		self.setWindowTitle(' ')
		self.begin = QtCore.QPoint()
		self.end = QtCore.QPoint()
		self.setWindowOpacity(0.3)
		QtWidgets.QApplication.setOverrideCursor(
			QtGui.QCursor(QtCore.Qt.CrossCursor)
		)
		self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
		print('Capture the screen...')
		self.show()

	def paintEvent(self, event):
		qp = QtGui.QPainter(self)
		qp.setPen(QtGui.QPen(QtGui.QColor('black'), 3))
		qp.setBrush(QtGui.QColor(128, 128, 255, 128))
		qp.drawRect(QtCore.QRect(self.begin, self.end))

	def mousePressEvent(self, event):
		self.begin = event.pos()
		self.end = self.begin
		self.update()

	def mouseMoveEvent(self, event):
		self.end = event.pos()
		self.update()

	def mouseReleaseEvent(self, event):
		self.close()

		x1 = min(self.begin.x(), self.end.x())
		y1 = min(self.begin.y(), self.end.y())
		x2 = max(self.begin.x(), self.end.x())
		y2 = max(self.begin.y(), self.end.y())
		self.screenDimensions = {'A': [x1, y1], 'B': [x2, y2]}

	def getScreenCapDimensions(self):
		return self.screenDimensions

class AddView():
	def __init__(self, parent = None):
		super(AddView, self).__init__(parent=parent)

		self.viewDictionary = []

		


	def setName(self, name):
		pass

	def getView(self):
		pass

	def getObjectFromSelection(self):
		pass

	def getKeyableAttributesFromObject(self, object):
		pass

	def setValueForAttribute(self, attribute, value):
		pass

class SetPath():
	def __init__(self, parent = None):
		super(SetPath, self).__init__(parent=parent)

	def getPath(self):
		return self.path

	def setPath(self, path):
		self.path = path