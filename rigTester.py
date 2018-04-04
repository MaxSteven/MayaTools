import maya.cmds as mc
from PySide2 import QtGui, QtCore, QtWidgets
import maya.OpenMaya as OpenMaya
import maya.OpenMayaUI as mui

import json

import time

import shiboken2

import inspect
import os

class ScreenCapture(QtWidgets.QWidget):
	def __init__(self):
		super(ScreenCapture, self).__init__()
		self.screen = QtWidgets.QDesktopWidget()
		screen_width = self.screen.screenGeometry().width()
		screen_height = self.screen.screenGeometry().height()
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
		x2 = max(self.begin.x(), self.end.x()) - x1
		y2 = max(self.begin.x(), self.end.x()) - y1
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
		self.viewList = []
		self.setWindowTitle('Rig Tester')
		self.setLayout(QtWidgets.QHBoxLayout())
		self.rigViewListWidget = QtWidgets.QListWidget()
		self.layout().setContentsMargins(5,5,5,5)
		self.layout().setSpacing(5)
		self.layout().addWidget(self.rigViewListWidget)
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

		self.addRigViewButton = QtWidgets.QPushButton('Add new view')
		self.addRigViewButton.clicked.connect(self.addView)
		buttonsLayout.addWidget(self.addRigViewButton)

		self.setRigViewPathButton = QtWidgets.QPushButton('Set path')
		self.setRigViewPathButton.clicked.connect(self.setPathUI)
		buttonsLayout.addWidget(self.setRigViewPathButton)

		self.removeRigViewButton = QtWidgets.QPushButton('Remove view')
		self.removeRigViewButton.clicked.connect(self.removeView)
		buttonsLayout.addWidget(self.removeRigViewButton)

		self.generateViewButton = QtWidgets.QPushButton('Generate View')
		self.generateViewButton.clicked.connect(self.generateView)
		buttonsLayout.addWidget(self.generateViewButton)

		self.saveViewButton = QtWidgets.QPushButton('Save View')
		self.saveViewButton.clicked.connect(self.saveView)
		buttonsLayout.addWidget(self.saveViewButton)

		self.loadViewButton = QtWidgets.QPushButton('Load View')
		self.loadViewButton.clicked.connect(self.loadView)
		buttonsLayout.addWidget(self.loadViewButton)

		self.viewAdded.connect(self.getViewFromVM)
		self.pathUpdated.connect(self.setPath)

		self.show()

	def addViewToList(self):
		self.rigViewListWidget.clear()
		for view in self.viewList:
			self.rigViewListWidget.addItem(view['name'])

	def getViewFromVM(self):	
		viewDict = self.view.getView()
		self.viewList.append(viewDict)
		self.addViewToList()
		self.view.close()
	
	def addView(self):
		self.view = ViewManager(parent = self)

	def removeView(self):
		selectedViews = self.rigViewListWidget.selectedItems()
		for item in selectedViews:
			for View in self.viewList:
				if item.text() == View['name']:
					self.viewList.remove(View)
					self.rigViewListWidget.takeItem(self.rigViewListWidget.row(item))

	def setPathUI(self):
		self.pathUI = SetPath(parent = self)

	def setPath(self):
		self.path = self.pathUI.getPath()
		self.pathUI.close()

	def generateView(self):
		view = mui.M3dView.active3dView()
		cam = OpenMaya.MDagPath()
		view.getCamera(cam)
		camName = cam.partialPathName()
		cam = mc.listRelatives(camName, parent=True)[0]

		self.hide()

		time.sleep(2)

		currentViewPosition = mc.xform(cam, query = True, worldSpace = True, translation=True)
		currentViewOrientation = mc.xform(cam, query = True, worldSpace = True, rotation = True)

		for view in self.viewList:
			mc.xform(cam, worldSpace = True, translation = view['viewPosition'])
			mc.xform(cam, worldSpace = True, rotation = view['viewOrientation'])
			previousValues = []
			for View in view['data']:
				obj = View['obj']
				attr = View['attr']
				val = mc.getAttr(obj + '.' + attr)
				valDict = {
							'obj': obj,
							'attr': attr,
							'value': val
						}
				previousValues.append(valDict)

			for View in view['data']:
				obj = View['obj']
				attr = View['attr']
				val = View['value']
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

	def loadView(self):
		filepath, garbage = QtWidgets.QFileDialog.getOpenFileName(parent = self)
		f = open(filepath, 'r')

		self.viewList = json.load(f)
		self.addViewToList()
		f.close()

	def saveView(self):
		filepath, garbage = QtWidgets.QFileDialog.getSaveFileName(parent = self)
		# print type(filepath)
		f = open(filepath, 'w')

		json.dump(self.viewList, f, indent = 4)
		f.close()

	def takeScreenshot(self, name):
		if not self.path:
			print "Path not set"
			return

		point1 = self.screenDimensions['A']
		point2 = self.screenDimensions['B']
		screenShotPixmap = QtGui.QPixmap()
		img = screenShotPixmap.grabWindow(QtWidgets.QApplication.desktop().winId(), x = point1[0], y = point1[1], width = point2[0], height = point2[0])
		# img = ImageGrab.grab(bbox=(point1[0], point1[1], point2[0], point2[1]))
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
		
		ViewLayout = QtWidgets.QHBoxLayout()
		self.layout().addLayout(ViewLayout)

		objectNameLayout = QtWidgets.QHBoxLayout()
		objectNameLayout.addWidget(QtWidgets.QLabel('Object:'))
		self.objectNameText = QtWidgets.QLineEdit()
		self.objectNameText.returnPressed.connect(self.getKeyableAttributesFromObject)
		objectNameLayout.addWidget(self.objectNameText)
		self.getObjectButton = QtWidgets.QPushButton('<<')
		self.getObjectButton.clicked.connect(self.getObjectFromSelection)
		objectNameLayout.addWidget(self.getObjectButton)
		ViewLayout.addLayout(objectNameLayout)

		attributeListLayout = QtWidgets.QHBoxLayout()
		attributeListLayout.addWidget(QtWidgets.QLabel('Attribute:'))
		self.attributeList = QtWidgets.QComboBox()
		attributeListLayout.addWidget(self.attributeList)
		ViewLayout.addLayout(attributeListLayout)

		valueLayout = QtWidgets.QHBoxLayout()
		valueLayout.addWidget(QtWidgets.QLabel('Object:'))
		self.valueText = QtWidgets.QLineEdit()
		valueLayout.addWidget(self.valueText)
		self.getObjectButton = QtWidgets.QPushButton('<<')
		self.getObjectButton.clicked.connect(self.getValueFromAttribute)
		valueLayout.addWidget(self.getObjectButton)
		ViewLayout.addLayout(valueLayout)

		addRemoveButtonsLayout = QtWidgets.QHBoxLayout()
		self.layout().addLayout(addRemoveButtonsLayout)

		self.addAttrTestButton = QtWidgets.QPushButton('+')
		addRemoveButtonsLayout.addWidget(self.addAttrTestButton)
		self.addAttrTestButton.clicked.connect(self.addAttrTest)

		self.removeAttrTestButton = QtWidgets.QPushButton('-')
		addRemoveButtonsLayout.addWidget(self.removeAttrTestButton)
		self.removeAttrTestButton.clicked.connect(self.removeAttrTest)

		self.attrTestTable = QtWidgets.QTableWidget(3, 3)
		self.attrTestTable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
		self.attrTestTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
		self.layout().addWidget(self.attrTestTable)
		
		self.setTestButton = QtWidgets.QPushButton('Add/Modify')
		self.setTestButton.clicked.connect(self.setTest)
		self.layout().addWidget(self.setTestButton)

		self.show()

	def addAttrTest(self):
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
		self.attrTestTable.setRowCount(len(self.viewJson['data']))
		row = len(self.viewJson['data']) - 1
		columnIndex = 0
		for key in ['obj', 'attr', 'value']:
			item = QtWidgets.QTableWidgetItem(str(objJson[key]))
			self.attrTestTable.setItem(row, columnIndex, item)
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

	def getView(self):
		return self.viewJson

	def removeAttrTest(self):
		row = self.attrTestTable.currentRow()
		columnIndex = 0
		selectedDataJson = {}
		for key in ['obj', 'attr','value']:
			if self.attrTestTable.item(row, columnIndex).text() == '':
				continue

			selectedDataJson.update({key: self.attrTestTable.item(row, columnIndex).text()})
			columnIndex += 1

		if selectedDataJson in self.viewJson['data']:
			self.viewJson['data'].remove(selectedDataJson)
		self.attrTestTable.removeRow(row)

	def getObjectFromSelection(self):
		self.obj = mc.ls(sl=True)[0]
		self.objectNameText.setText(self.obj)
		self.getKeyableAttributesFromObject()

	def getKeyableAttributesFromObject(self):
		obj = self.objectNameText.text()
		attributes = mc.listAttr(obj, keyable = True, unlocked = True)
		self.attributeList.clear()
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
