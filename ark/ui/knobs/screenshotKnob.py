
import time
from knob import Knob

import arkInit
arkInit.init()

import translators
translator = translators.getCurrent()
from translators import QtCore, QtGui


#Calls to setValue() here will set the value of the filepath that the screenshot should be saved under

class TakeScreenShot(Knob):

	showLabel = False
	useFullRow = True

	def createWidget(self):
		self.widget = QtGui.QPushButton(str(self.name))
		self.widget.clicked.connect(self.takeScreenShot)
		self.value = 'c:/Screenshot.jpg'
		self.hasFired = False
		self.screenShotPopup = ScreenShotSelector()

	def takeScreenShot(self):
		self.parent.hide()
		time.sleep(0.2)
		if not self.hasFired:
			self.screenShotPopup.takeScreenshot(self.getValue())
			self.parent.show()
			self.screenShotPopup.show()
			self.hasFired = True
		else:
			self.screenShotPopup = ScreenShotSelector()
			self.screenShotPopup.takeScreenshot(self.getValue())
			self.parent.show()
			self.screenShotPopup.show()


class ScreenShotSelector (QtGui.QLabel):
	def __init__(self, parentQWidget=None):
		super(ScreenShotSelector, self).__init__(parentQWidget)
		self.setAlignment(QtCore.Qt.AlignCenter)
		self.setWindowTitle('Click and drag to select the area to save')

	def takeScreenshot(self, filePath):
		self.filePath = filePath
		imBuffer = QtCore.QBuffer()
		imBuffer.open(QtCore.QIODevice.ReadWrite)

		rec = QtCore.QRect()
		wholeRec = QtCore.QRect()

		for i in range(QtGui.QApplication.desktop().screenCount()):
			rec = QtGui.QApplication.desktop().screenGeometry(i)
			wholeRec = wholeRec.united(rec)

		im = QtGui.QPixmap.grabWindow(QtGui.QApplication.desktop().winId(),
															wholeRec.x(),
															wholeRec.y(),
															wholeRec.width(),
															wholeRec.height())
		self.setScaledContents(True)
		# self.setPixmap(im)
		self.setPixmap(im.scaled(wholeRec.width(), wholeRec.height(), QtCore.Qt.KeepAspectRatio))
		# self.setFixedWidth(im.width())
		# self.setFixedHeight(im.height())

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
		self.setPixmap(cropQPixmap)
		fileName = QtGui.QFileDialog.getSaveFileName(
			self,
			'Save Screenshot as',
			'c:/screenshot.jpg',
			'Images (*.png *.jpg *.bmp)')
		if fileName:
			cropQPixmap.save(fileName[0])
		self.close()

