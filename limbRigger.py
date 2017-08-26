import maya.cmds as mc
from maya import OpenMaya

import os
import inspect
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

class IkFkBlender(QtGui.QDialog):
	def __init__(self, parent=None):

		super(IkFkBlender, self).__init__(parent=parent)
		self.blendedJoints = []
		self.fkJoints = []
		self.jointNames = []
		self.ikJoints = []
		self.ikControls = []
		self.fkControls = []
		self.fkControlGroups = []

		mainLayout = QtGui.QVBoxLayout()
		self.setLayout(mainLayout)

		i = 0
		self.jointText = []
		self.jointButtons = []
		for i in range(3):
			jointLayout = QtGui.QHBoxLayout()

			jointLabel = QtGui.QLabel(str(i))
			jointLayout.addWidget(jointLabel)

			jointText = QtGui.QLineEdit()
			jointLayout.addWidget(jointText)
			self.jointText.append(jointText)

			jointButton = QtGui.QPushButton('<<')
			jointButton.setObjectName(str(i))
			jointButton.clicked.connect(self.addSelectedToText)
			jointLayout.addWidget(jointButton)
			self.jointButtons.append(jointButton)

			mainLayout.addLayout(jointLayout)

		controlLayout = QtGui.QHBoxLayout()
		mainLayout.addLayout(controlLayout)
		controlLabel = QtGui.QLabel('Control Size')
		controlLayout.addWidget(controlLabel)
		self.controlSizeSlider = QtGui.QSlider()
		self.controlSizeSlider.setOrientation(QtCore.Qt.Horizontal)
		controlLayout.addWidget(self.controlSizeSlider)

		self.rigButton = QtGui.QPushButton('Rig')
		self.rigButton.clicked.connect(self.rigLimb)
		mainLayout.addWidget(self.rigButton)

		self.show()

	def addSelectedToText(self):
		buttonClicked = int(self.sender().objectName())
		objectSelected = mc.ls(sl=True)[0]
		self.jointText[buttonClicked].setText(objectSelected)

	def rigLimb(self):
		self.jointNames = [text.text() for text in self.jointText]
		print self.jointNames



tool = IkFkBlender()
