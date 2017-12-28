# Skin Manager
# currently only works if vertex order is same

import maya.cmds as mc
import json

from PySide2 import QtCore, QtNetwork
from PySide2 import QtWidgets
from PySide2 import QtGui

for name in dir(QtWidgets):
	obj = getattr(QtWidgets, name)
	if inspect.isclass(obj):
		setattr(QtGui, name, obj)

from PySide2.QtCore import Signal as QtSignal
from PySide2.QtCore import Slot as QtSlot
from PySide2.QtCore import QEvent

class skinManager(QtGui.QDialog):
	def __init__(self, parent=None):
		super(skinManager, self).__init__(parent)

		self.setWindowTitle("Skin Manager")
		self.setLayout(QtGui.QVBoxLayout())
		self.layout().setContentsMargins(5,5,5,5)
		self.layout().setSpacing(5)

		# skin cluster layout
		skinClusterLayout = QtGui.QHBoxLayout()
		skinClusterLabel = QtGui.QLabel("Skin Cluster:")
		skinClusterLayout.addWidget(skinClusterLabel)
		self.skinCLusterName = QtGui.QLineEdit()
		skinClusterLayout.addWidget(self.skinCLusterName)
		self.skinClusterButton = QtGui.QPushButton("<<")
		self.skinClusterButton.clicked.connect(self.getSkinCluster)
		skinClusterLayout.addWidget(self.skinClusterButton)
		self.layout().addLayout(skinClusterLayout)

		# file path layout
		filepathLayout = QtGui.QHBoxLayout()
		filepathLabel = QtGui.QLabel("Skin data file:")
		filepathLayout.addWidget(filepathLabel)
		self.filepathName = QtGui.QLineEdit()
		filepathLayout.addWidget(self.filepathName)
		self.filepathButton = QtGui.QPushButton("..")
		self.filepathButton.clicked.connect(self.getFilepath)
		filepathLayout.addWidget(self.filepathButton)
		self.layout().addLayout(filepathLayout)

		# button layout
		buttonLayout = QtGui.QHBoxLayout()
		self.saveButton = QtGui.QPushButton("Save to")
		self.saveButton.clicked.connect(self.saveSkin)
		buttonLayout.addWidget(self.saveButton)

		self.loadButton = QtGui.QPushButton("Load from")
		self.loadButton.clicked.connect(self.loadSkin)
		buttonLayout.addWidget(self.loadButton)
		

		self.layout().addLayout(buttonLayout)

	def getSkinCluster(self):
		self.vertices = mc.filterExpand(expand=True, selectionMask=31)
		if not self.vertices or len(self.vertices) < 1:
			self.showError('No Vertices selected')
			return

		selectedObject = self.vertices[0].split('.')[0]
		skinCluster = mc.connectionInfo(selectedObject + '.inMesh', sourceFromDestination=True).split('.')[0]
		self.skinCLusterName.setText(skinCluster)

	def getFilepath(self):
		self.fileDialog = QtGui.QFileDialog(self)
		self.fileDialog.setFileMode(QtGui.QFileDialog.AnyFile)
		if self.fileDialog.exec_():
			file = self.fileDialog.selectedFiles()[0]
			self.filepathName.setText(file)

	def saveSkin(self):
		skinCluster = self.skinCLusterName.text()
		filepath = self.filepathName.text()
		vertices = mc.filterExpand(expand=True, selectionMask=31)

		if not vertices or len(vertices) < 1:
			self.showError('No Vertices selected')
			return
		
		skinJsonInfo = {
						'components': {},
						'joints': []
						}


		f = open(filepath, "w")
		mc.setAttr(skinCluster + '.envelope', 0.0)

		for vertex in vertices:
			weights = []
			joints = []

			joints = mc.skinPercent(skinCluster, vertex, query=True, transform=None)
			weights = mc.skinPercent(skinCluster, vertex, query=True, value=True)

			# pruneAndNormalize(weights, prunePlaces)

			worldPosition = mc.pointPosition(vertex, world=True)
			localPosition = mc.pointPosition(vertex, local=True)

			vertexInfo = {
							vertex: {
									'positionW': worldPosition,
									'positionL': localPosition,
									'influences': {}
						}
			}

			influenceInfo = {}
			i = 0
			for joint in joints:
				influenceInfo.update({joint: weights[i]})
				i += 1

			vertexInfo[vertex]['influences'] = influenceInfo
			skinJsonInfo['components'].update(vertexInfo)

		skinJsonInfo['joints'] = joints

		json.dump(skinJsonInfo, f, indent=2)
		f.close()

		mc.setAttr(skinCluster + '.envelope', 1.0)

	def loadSkin(self):
		skinCluster = self.skinCLusterName.text()
		filepath = self.filepathName.text()
		vertices = mc.filterExpand(expand=True, selectionMask=31)

		if not vertices or len(vertices) < 1:
			self.showError('No Vertices selected')
			return
		
		f = open(filepath, "r")
		mc.setAttr(skinCluster + '.envelope', 0.0)

		data = json.load(f)

		numOfJoints = len(data[u'joints'])

		for vertex in vertices:
			joints = mc.skinPercent(skinCluster, vertex, query=True, transform=None)
			if len(joints) != numOfJoints:
				print "Invalid joints in selected vertices"
				break

			vertexInfluenceInfo = data['components'][vertex]['influences']
			transformValues = []
			for key, value in vertexInfluenceInfo.iteritems():
				transformValues.append((key, value))

			mc.skinPercent(skinCluster, vertex, transformValue = transformValues)
			mc.skinPercent(skinCluster, vertex, normalize=True)

		f.close()

		mc.setAttr(skinCluster + '.envelope', 1.0)

		pass

	def showError(self, message):
		errorMessage = QtGui.QErrorMessage(self)
		errorMessage.showMessage(message)


skinDialog = skinManager()
skinDialog.show()






