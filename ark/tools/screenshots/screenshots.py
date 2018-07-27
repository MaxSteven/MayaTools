import os
from PIL import ImageGrab
from knob import Knob

import arkInit
arkInit.init()

import translators
translator = translators.getCurrent()
from translators import QtCore, QtGui
import baseWidget


class ScreenShotSelector (QtGui.QLabel):
	def __init__(self, parentQWidget=None):
		super(ScreenShotSelector, self).__init__(parentQWidget)

	def takeScreenshot(self):
		im = ImageGrab.grab()
		im.save('tmp.jpg')
		pixMap = QtGui.QPixmap('tmp.jpg')
		self.setPixmap(pixMap)
		self.setFixedWidth(pixMap.width())
		self.setFixedHeight(pixMap.height())

	def mousePressEvent(self, eventQMouseEvent):
		self.originQPoint = eventQMouseEvent.pos()
		self.currentQRubberBand = QtGui.QRubberBand(QtGui.QRubberBand.Rectangle, self)
		self.currentQRubberBand.setGeometry(QtCore.QRect(self.originQPoint, QtCore.QSize()))
		self.currentQRubberBand.show()

	def mouseMoveEvent(self, eventQMouseEvent):
		self.currentQRubberBand.setGeometry(QtCore.QRect(self.originQPoint, eventQMouseEvent.pos()).normalized())

	def mouseReleaseEvent(self, eventQMouseEvent):
		self.currentQRubberBand.hide()
		currentQRect = self.currentQRubberBand.geometry()
		self.currentQRubberBand.deleteLater()
		cropQPixmap = self.pixmap().copy(currentQRect)
		cropQPixmap.save('output.jpg')
		os.remove('tmp.jpg')
		self.close()


class ScreenShotKnob(PythonButton):

	def display(self):
		super(ScreenShotKnob, self).display()
		execPython = lambda: self.executePython('self.takeScreenShot()')
		self.widget.clicked.connect.execPython
		return self.widget

	def takeScreenShot(self):
		if not self.hasFired:
			self.screenShotPopup.takeScreenshot()
			self.screenShotPopup.show()
			self.hasFired = True
		else:
			self.hide()
			self.screenShotPopup = ScreenShotSelector()
			self.screenShotPopup.takeScreenshot()
			self.show()
			self.screenShotPopup.show()


def main():
	options = {
		'title': 'Take Screen shot',
		'knobs': [
		{
			'name': 'Take a shot',
			'dataType': 'pythonButton',
			'callback': 'takeScreenShot'
		}
		]
	}
	translator.launch(ScreenShotButton, None, options=options)

if __name__ == '__main__':
	main()
