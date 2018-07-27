from knob import Knob
from translators import QtGui
from translators import QtCore
import os


class PythonButton(Knob):
	defaultOptions = {
		'callback': 'None',
		'width': None,
		'height': None,
	}

	showLabel = False
	useFullRow = True

	def createWidget(self):
		self.widget = QtGui.QPushButton()
		self.widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.widget.customContextMenuRequested.connect(self.rightClicked)
		self.widget.setAutoDefault(False)

		if self.options['callback'] != 'None':
			method = self.getParentMethod(self.options['callback'])
			self.widget.clicked.connect(method)
		self.setIcon(self.options.get('iconPath'))
		self.widget.clicked.connect(self.buttonClicked)

	def buttonClicked(self):
		self.emit('clicked')

	def setIcon(self, iconPath):
		self.widget.setIcon(QtGui.QIcon())
		self.widget.setText(None)
		buttonImage = None
		if iconPath != None and os.path.isfile(iconPath):
			buttonImage = QtGui.QPixmap(iconPath)
			self.widget.setIcon(QtGui.QIcon(buttonImage))

		else:
			self.widget.setText(str(self.name))

		if self.options['width'] and self.options['height']:
			self.widget.setFixedSize(self.options['width'], self.options['height'])
			if buttonImage:
				iconSize = min(self.options['width'], self.options['height'])
				self.widget.setIconSize(QtCore.QSize(iconSize, iconSize))

	def rightClicked(self):
		self.emit('rightClicked')

	def updateWidgetValue(self):
		pass
