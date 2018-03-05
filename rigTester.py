import maya.cmds as mc
from PySide2 import QtGui, QtCore, QtWidgets
import maya.OpenMaya as OpenMaya
import maya.OpenMayaUI as mui
from PIL import ImageGrab

import shiboken2

import inspect
import os

class RigTester(QtWidgets.QDialog):
	def __init__(self, parent = None, screenDimensions = None):
		super(RigTester, self).__init__(parent = getMainWindow())
		self.screenDimensions = screenDimensions
		self.setWindowTitle('Rig Tester')
		self.setLayout(QtWidgets.QHBoxLayout())
		self.rigTestList = QtWidgets.QListWidget()
		self.layout().setContentsMargins(5,5,5,5)
		self.layout().setSpacing(5)
		self.layout().addWidget(self.rigTestList)

		buttonsLayout = QtWidgets.QVBoxLayout()
		self.layout().addLayout(buttonsLayout)

		self.addRigTestButton = QtWidgets.QPushButton('Add new view')
		self.addRigTestButton.clicked.connect(self.addView)
		buttonsLayout.addWidget(self.addRigTestButton)

		self.setRigTestPathButton = QtWidgets.QPushButton('Set path')
		self.setRigTestPathButton.clicked.connect(self.setPath)
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

		self.show()
		
	def addView(self):
		view = ViewManager(parent = self)

	def removeView(self):
		pass

	def setPath(self):
		pathUI = SetPath(parent = self)
		self.path = pathUI.getPath()

	def generateTest(self):
		view = OpenMayaUI.M3dView.active3dView()
		cam = OpenMaya.MDagPath()
		view.getCamera(cam)
		camName = cam.partialPathName()
		cam = mc.listRelatives(camName, parent=True)[0]

		filepath = "C:\\trash\\test.json"
		f = open(filepath, 'r')

		viewList = json.load(viewList, f, indent = 4)
		f.close()

		currentViewPosition = mc.xform(cam, query = True, worldSpace = True, translation=True)
		currentViewOrientation = mc.xfomr(cam, query = True, worldSpace = True, rotation = True)

		for view in viewList:
			mc.xform(cam, worldSpace = True, translation = view['viewPosition'])
			mc.xform(cam, worldSpace = True, rotation = view['viewOrientation'])
			previousValues = []
			for test in view['data']:
				obj = test['obj']
				attr = test['attr']
				val = mc.getAttr(obj + '.' + attr)
				valDict = {
							'obj': obj,
							'attr':attr,
							'val':val
						}
				previousValues.append(valDict)

			for test in view['data']:
				obj = test['obj']
				attr = test['attr']
				val = test['val']
				mc.setAttr(obj + '.' + attr, val)
				print 'screencap captured!'

			for val in previousValues:
				obj = val['obj']
				attr = val['attr']
				val = val['val']
				mc.setAttr(obj + '.' + attr, val)
				print 'value restored'

		mc.xform(cam, worldSpace = True, translation = currentViewPosition)
		mc.xform(cam, worldSpace = True, rotation = currentViewOrientation)

	def loadTest(self):
		pass

	def saveTest(self):
		pass

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
		
		self.screenDimensions = {'A': [x1, y1], 'B': [x2, y2]}
		print 'screenCaptured', self.screenDimensions
		rigTester = RigTester(screenDimensions = self.screenDimensions)

	def getScreenCapDimensions(self):
		return self.screenDimensions

class ViewManager(QtWidgets.QDialog):
	def __init__(self, parent = None):
		super(ViewManager, self).__init__(parent=parent)
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

		self.removeViewButton = QtWidgets.QPushButton('+')
		addRemoveButtonsLayout.addWidget(self.removeViewButton)
		self.removeViewButton.clicked.connect(self.removeTest)

		self.testTable = QtWidgets.QTableWidget(3, 3)
		self.testTable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
		self.layout().addWidget(self.testTable)
		
		self.addTestButton = QtWidgets.QPushButton('Add/Modify')
		self.addTestButton.clicked.connect(self.addTest)
		self.layout().addWidget(self.addTestButton)

		self.show()

	def setName(self, name):
		pass

	def getView(self):
		pass

	def addView(self):
		pass

	def addTest(self):
		viewJson = {
			'name':'',
			'viewPostition': [],
			'viewOrientation': [],
			'data':[]
		}
		objJson = {
			'obj': '',
			'attr': '',
			'value': ''
		}
		view = OpenMayaUI.M3dView.active3dView()
		cam = OpenMaya.MDagPath()
		view.getCamera(cam)
		camName = cam.partialPathName()
		cam = mc.listRelatives(camName, parent=True)[0]

		cameraPos = mc.xform(cam, query = True, translation = True, worldSpace = True)
		cameraOrient = mc.xform(cam, query = True, rotation = True, worldSpace = True)

		viewJson['viewPosition'] = cameraPos
		viewJson['viewOrientation'] = cameraOrient

		obj = mc.ls(sl=True)[0]
		attr = 'translateX'
		value = 0

		objJson['obj'] = obj
		objJson['attr'] = attr
		objJson['value'] = value

		viewJson['data'].append(objJson)

		viewList.append(viewJson)

		filepath = "C:\\trash\\test.json"
		f = open(filepath, 'w')

		json.dump(viewList, f, indent = 4)
		f.close()

	def removeTest(self):
		pass

	def getObjectFromSelection(self):
		self.obj = mc.ls(sl=True)[0]
		self.objectNameText.setText(self.obj)
		self.getKeyableAttributesFromObject()

	def getKeyableAttributesFromObject(self):
		attributes = mc.listAttr(obj, keyable = True, unlocked = True)
		self.attributeList.addItems(attributes)

	def getValueFromAttribute(self):
		attr = self.attributeList.currentText()
		value = mc.getAttr(self.obj + '.' + attr)
		self.valueText.setText(value)


class SetPath(QtWidgets.QDialog):
	def __init__(self, parent = None):
		super(SetPath, self).__init__(parent=parent)

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
		dirpath = QtGui.QFileDialog.getExistingDirectory(self, 'Save Directory') 
		self.pathText.setText(dirpath)

	def getPath(self):
		self.path = self.pathText.getText()
		return self.path

	def setPath(self, path):
		self.path = path

# class Viewer(QtGui.QDialog):
def getMainWindow():
	ptr = mui.MQtUtil.mainWindow()
	mainWin = shiboken2.wrapInstance(long(ptr), QtWidgets.QWidget)
	return mainWin

screenCap = ScreenCapture()
