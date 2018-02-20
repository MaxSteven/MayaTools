import maya.cmds as mc
from PySide2 import QtGui, QtCore, QtWidgets

import inspect
import os

class RigTester(QtWidgets.QDialog):
	def __init__(self, parent = None):
		super(RigTester, self).__init__(parent=parent)
		screenCap = ScreenCapture()
		self.screenCapArea = screenCap.getScreenCapDimensions()

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

	def getScreenCapDimensions(self):
		return self.screenDimensions


class AddView():
	def __init__(self, parent = None):
		super(AddView, self).__init__(parent=parent)

		viewDictionary = []


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