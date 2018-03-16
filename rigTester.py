import maya.cmds as mc
from PySide2 import QtGui, QtCore, QtWidgets
import maya.OpenMaya as OpenMaya
import maya.OpenMayaUI as mui
from PIL import ImageGrab

import json

import time

import shiboken2

import inspect
import os

class ScreenCapture(QtWidgets.QWidget):
	def __init__(self):
		super(ScreenCapture, self).__init__()
		img = ImageGrab.grab
		self.screenDimensions = None
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
		QtWidgets.QApplication.restoreOverrideCursor()
		self.screenDimensions = {'A': [x1, y1], 'B': [x2, y2]}
		print 'screenCaptured', self.screenDimensions
		rigTester = RigTester(screenDimensions = self.screenDimensions)

	def getScreenCapDimensions(self):
		return self.screenDimensions

# class RigTester(QtWidgets.QMainWindow):
class RigTester(QtWidgets.QDialog):

	viewAdded = QtCore.Signal()
	pathUpdated = QtCore.Signal()

	def __init__(self, parent = None, screenDimensions = None):
		super(RigTester, self).__init__(parent = getMainWindow())
		self.screenDimensions = screenDimensions
		self.testList = []
		self.setWindowTitle('Rig Tester')
		self.setLayout(QtWidgets.QHBoxLayout())
		self.rigTestListWidget = QtWidgets.QListWidget()
		self.layout().setContentsMargins(5,5,5,5)
		self.layout().setSpacing(5)
		self.layout().addWidget(self.rigTestListWidget)
		self.path = None

		# self.statusBar()

		# saveAction = QtWidgets.QAction('Save', self)
		# saveAction.setShortcut("Ctrl+S")
		# saveAction.setStatusTip('&Save the test')
		# saveAction.triggered.connect(self.saveTest)

		# self.mainMenu = self.menuBar()
		# fileMenu = self.mainMenu.addMenu('&File')

		# saveAction = QtWidgets.QAction('Save', self)
		# saveAction.setShortcut("Ctrl+S")
		# saveAction.setStatusTip('Save the test')
		# saveAction.triggered.connect(self.saveTest)
		# fileMenu.addAction(saveAction)

		# loadAction = QtWidgets.QAction('Load', self)
		# loadAction.setShortcut("Ctrl+O")
		# loadAction.setStatusTip('load the test')
		# loadAction.triggered.connect(self.loadTest)
		# fileMenu.addAction(loadAction)

		# quitAction = QtWidgets.QAction('Quit', self)
		# quitAction.setShortcut("Ctrl+Q")
		# quitAction.setStatusTip('Quit')
		# quitAction.triggered.connect(self.quit)
		# fileMenu.addAction(quitAction)

		buttonsLayout = QtWidgets.QVBoxLayout()
		self.layout().addLayout(buttonsLayout)

		self.addRigTestButton = QtWidgets.QPushButton('Add new view')
		self.addRigTestButton.clicked.connect(self.addView)
		buttonsLayout.addWidget(self.addRigTestButton)

		self.setRigTestPathButton = QtWidgets.QPushButton('Set path')
		self.setRigTestPathButton.clicked.connect(self.setPathUI)
		buttonsLayout.addWidget(self.setRigTestPathButton)

		self.removeRigTestButton = QtWidgets.QPushButton('Remove view')
		self.removeRigTestButton.clicked.connect(self.removeView)
		buttonsLayout.addWidget(self.removeRigTestButton)

		self.generateTestButton = QtWidgets.QPushButton('Generate Test')
		self.generateTestButton.clicked.connect(self.generateTest)
		buttonsLayout.addWidget(self.generateTestButton)

		self.saveTestButton = QtWidgets.QPushButton('Save Test')
		self.saveTestButton.clicked.connect(self.saveTest)
		buttonsLayout.addWidget(self.saveTestButton)

		self.loadTestButton = QtWidgets.QPushButton('Load Test')
		self.loadTestButton.clicked.connect(self.loadTest)
		buttonsLayout.addWidget(self.loadTestButton)

		self.viewAdded.connect(self.addViewToList)
		self.pathUpdated.connect(self.setPath)

		self.show()
	
	def addViewToList(self):	
		testDict = self.view.getTest()
		self.testList.append(testDict)
		self.rigTestListWidget.addItem(testDict['name'])
		self.view.close()
	
	def addView(self):
		self.view = ViewManager(parent = self)

	def removeView(self):
		selectedTest = self.rigTestListWidget.selectedItems()
		for item in selectedItems:
			for test in self.testList:
				if item == test['name']:
					self.testList.remove(test)
					self.rigTestListWidget.takeItem(self.rigTestListWidget.row(item))

	def setPathUI(self):
		self.pathUI = SetPath(parent = self)

	def setPath(self):
		self.path = self.pathUI.getPath()
		self.pathUI.close()

	def generateTest(self):
		view = mui.M3dView.active3dView()
		cam = OpenMaya.MDagPath()
		view.getCamera(cam)
		camName = cam.partialPathName()
		cam = mc.listRelatives(camName, parent=True)[0]

		self.hide()

		time.sleep(2)

		currentViewPosition = mc.xform(cam, query = True, worldSpace = True, translation=True)
		currentViewOrientation = mc.xform(cam, query = True, worldSpace = True, rotation = True)

		for view in self.testList:
			mc.xform(cam, worldSpace = True, translation = view['viewPosition'])
			mc.xform(cam, worldSpace = True, rotation = view['viewOrientation'])
			previousValues = []
			for test in view['data']:
				obj = test['obj']
				attr = test['attr']
				val = mc.getAttr(obj + '.' + attr)
				valDict = {
							'obj': obj,
							'attr': attr,
							'value': val
						}
				previousValues.append(valDict)

			for test in view['data']:
				obj = test['obj']
				attr = test['attr']
				val = test['value']
				mc.setAttr(obj + '.' + attr, float(val))
				mc.refresh()
				
			# time.sleep(1)
			self.takeScreenshot(view['name'])
			# time.sleep(1)
			for val in previousValues:
				obj = val['obj']
				attr = val['attr']
				val = val['value']
				mc.setAttr(obj + '.' + attr, float(val))
				print 'value restored'
		self.show()
		mc.xform(cam, worldSpace = True, translation = currentViewPosition)
		mc.xform(cam, worldSpace = True, rotation = currentViewOrientation)

	def loadTest(self):
		filepath, garbage = QtWidgets.QFileDialog.getOpenFileName(parent = self)
		f = open(filepath, 'r')

		self.testList = json.load(f)
		f.close()

	def saveTest(self):
		filepath, garbage = QtWidgets.QFileDialog.getSaveFileName(parent = self)
		# print type(filepath)
		f = open(filepath, 'w')

		json.dump(self.testList, f, indent = 4)
		f.close()

	def takeScreenshot(self, name):
		if not self.path:
			print "Path not set"
			return

		point1 = self.screenDimensions['A']
		point2 = self.screenDimensions['B']
		img = ImageGrab.grab(bbox=(point1[0], point1[1], point2[0], point2[1]))
		img.save(self.path + '/ ' + name + '.png')

	def quit(self):
		self.close()


class ViewManager(QtWidgets.QDialog):
	def __init__(self, parent = None):
		super(ViewManager, self).__init__(parent=parent)
		self.viewJson = {
			'name':'',
			'viewPostition': [],
			'viewOrientation': [],
			'data':[]
		}
		self.parent = parent
		self.setLayout(QtWidgets.QVBoxLayout())
		self.viewDictionaryList = []
		self.setWindowTitle('View Manager')
		self.layout().setContentsMargins(5,5,5,5)
		self.layout().setSpacing(5)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		sizePolicy.setHeightForWidth(True)
		self.setSizePolicy(sizePolicy)
		
		nameLayout = QtWidgets.QHBoxLayout()
		self.layout().addLayout(nameLayout)

		nameLayout.addWidget(QtWidgets.QLabel('Name:'))
		self.nameText = QtWidgets.QLineEdit()
		nameLayout.addWidget(self.nameText)
		
		testLayout = QtWidgets.QHBoxLayout()
		self.layout().addLayout(testLayout)

		objectNameLayout = QtWidgets.QHBoxLayout()
		objectNameLayout.addWidget(QtWidgets.QLabel('Object:'))
		self.objectNameText = QtWidgets.QLineEdit()
		self.objectNameText.returnPressed.connect(self.getKeyableAttributesFromObject)
		objectNameLayout.addWidget(self.objectNameText)
		self.getObjectButton = QtWidgets.QPushButton('<<')
		self.getObjectButton.clicked.connect(self.getObjectFromSelection)
		objectNameLayout.addWidget(self.getObjectButton)
		testLayout.addLayout(objectNameLayout)

		attributeListLayout = QtWidgets.QHBoxLayout()
		attributeListLayout.addWidget(QtWidgets.QLabel('Attribute:'))
		self.attributeList = QtWidgets.QComboBox()
		attributeListLayout.addWidget(self.attributeList)
		testLayout.addLayout(attributeListLayout)

		valueLayout = QtWidgets.QHBoxLayout()
		valueLayout.addWidget(QtWidgets.QLabel('Object:'))
		self.valueText = QtWidgets.QLineEdit()
		valueLayout.addWidget(self.valueText)
		self.getObjectButton = QtWidgets.QPushButton('<<')
		self.getObjectButton.clicked.connect(self.getValueFromAttribute)
		valueLayout.addWidget(self.getObjectButton)
		testLayout.addLayout(valueLayout)

		addRemoveButtonsLayout = QtWidgets.QHBoxLayout()
		self.layout().addLayout(addRemoveButtonsLayout)

		self.addViewButton = QtWidgets.QPushButton('+')
		addRemoveButtonsLayout.addWidget(self.addViewButton)
		self.addViewButton.clicked.connect(self.addView)

		self.removeViewButton = QtWidgets.QPushButton('-')
		addRemoveButtonsLayout.addWidget(self.removeViewButton)
		self.removeViewButton.clicked.connect(self.removeView)

		self.testTable = QtWidgets.QTableWidget(3, 3)
		self.testTable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
		self.testTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
		self.layout().addWidget(self.testTable)
		
		self.setTestButton = QtWidgets.QPushButton('Add/Modify')
		self.setTestButton.clicked.connect(self.setTest)
		self.layout().addWidget(self.setTestButton)

		self.show()

	def addView(self):
		objJson = {
			'obj': '',
			'attr': '',
			'value': ''
		}
		if not self.objectNameText.text() \
			or not self.attributeList.currentText() \
			or not self.valueText.text():
			return

		objJson['obj'] = self.objectNameText.text()
		objJson['attr'] = self.attributeList.currentText()
		objJson['value'] = self.valueText.text()

		self.viewJson['data'].append(objJson)
		# add to table
		self.testTable.setRowCount(len(self.viewJson['data']))
		row = len(self.viewJson['data']) - 1
		columnIndex = 0
		for key in ['obj', 'attr', 'value']:
			item = QtWidgets.QTableWidgetItem(str(objJson[key]))
			self.testTable.setItem(row, columnIndex, item)
			columnIndex += 1

	def setTest(self):
		view = mui.M3dView.active3dView()
		cam = OpenMaya.MDagPath()
		view.getCamera(cam)
		camName = cam.partialPathName()
		cam = mc.listRelatives(camName, parent=True)[0]
		name = self.nameText.text()

		cameraPos = mc.xform(cam, query = True, translation = True, worldSpace = True)
		cameraOrient = mc.xform(cam, query = True, rotation = True, worldSpace = True)

		self.viewJson['name'] = name
		self.viewJson['viewPosition'] = cameraPos
		self.viewJson['viewOrientation'] = cameraOrient
		if self.parent:
			self.parent.viewAdded.emit()

	def getTest(self):
		return self.viewJson

	def removeView(self):
		row = self.testTable.currentRow()
		columnIndex = 0
		selectedDataJson = {}
		for key in ['obj', 'attr','value']:
			if self.testTable.item(row, columnIndex).text() == '':
				continue

			selectedDataJson.update({key: self.testTable.item(row, columnIndex).text()})
			columnIndex += 1

		if selectedDataJson in self.viewJson['data']:
			self.viewJson['data'].remove(selectedDataJson)
		self.testTable.removeRow(row)

	def getObjectFromSelection(self):
		self.obj = mc.ls(sl=True)[0]
		self.objectNameText.setText(self.obj)
		self.getKeyableAttributesFromObject()

	def getKeyableAttributesFromObject(self):
		obj = self.objectNameText.text()
		attributes = mc.listAttr(obj, keyable = True, unlocked = True)
		self.attributeList.addItems(attributes)

	def getValueFromAttribute(self):
		attr = self.attributeList.currentText()
		value = mc.getAttr(self.obj + '.' + attr)
		self.valueText.setText(value)

class SetPath(QtWidgets.QDialog):
	def __init__(self, parent = None):
		super(SetPath, self).__init__(parent=parent)

		self.parent = parent

		self.setLayout(QtWidgets.QVBoxLayout())
		self.setWindowTitle('Set Path')
		self.layout().setContentsMargins(5,5,5,5)
		self.layout().setSpacing(5)

		pathLayout = QtWidgets.QHBoxLayout()
		self.layout().addLayout(pathLayout)

		pathLayout.addWidget(QtWidgets.QLabel('Directory:'))
		self.pathText = QtWidgets.QLineEdit()
		pathLayout.addWidget(self.pathText)
		self.getDirButton = QtWidgets.QPushButton('...')
		self.getDirButton.clicked.connect(self.openDirectory)
		pathLayout.addWidget(self.getDirButton)

		self.setPathButton = QtWidgets.QPushButton('Set Path')
		self.setPathButton.clicked.connect(self.setPath)
		self.layout().addWidget(self.setPathButton)

		self.show()

	def openDirectory(self):
		dirpath = QtWidgets.QFileDialog.getExistingDirectory(self, 'Save Directory') 
		self.pathText.setText(dirpath)

	def getPath(self):
		return self.path

	def setPath(self):
		self.path = self.pathText.text()
		self.parent.pathUpdated.emit()


# class Viewer(QtGui.QDialog):
def getMainWindow():
	ptr = mui.MQtUtil.mainWindow()
	mainWin = shiboken2.wrapInstance(long(ptr), QtWidgets.QWidget)
	return mainWin

screenCap = ScreenCapture()
