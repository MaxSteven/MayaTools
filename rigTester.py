import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PIL import ImageGrab


class SetScreencapAreaWidget(QtWidgets.QWidget):
	def __init__(self):
		super(SetScreencapAreaWidget, self).__init__()
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

		# img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
		# img.save('capture.png')
		# img.show()
		# img = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)

		# cv2.imshow('Captured Image', img)
		# cv2.waitKey(0)
		# cv2.destroyAllWindows()


class RigTester(QtWidgets.QDialog):
	def __init__(self, parent = None):
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


	def addRigTestButton(self):
		pass

	def setRigTestPathButton(self):
		pass

	def removeRigTest(self):
		pass

	def generateTest(self):
		pass

class AddView(QtWidgets.QDialog):
	def __init__(self, parent = parent):
		super(AddView, self).__init__(parent=parent)

		self.setLayout(QtWidgets.QGridLayout())

		self.layout().addWidget(QtWidget.QLabel('Name'), 0, 0)
		self.nameText = QtWidgets.QLineEdit()
		self.layout().addWidget(self.nameText, 0, 1)

		self.layout().addWidget(QtWidget.QLabel('Object'), 1, 0)
		self.objectText = QtWidgets.QLineEdit()
		self.layout().addWidget(self.objectText, 1, 1)

		self.layout().addWidget(QtWidget.QLabel('Attribute'), 2, 0)
		self.attributeText = QtWidgets.QLineEdit()
		self.layout().addWidget(self.attributeText, 2, 1)

		self.layout().addWidget(QtWidget.QLabel('Value'), 1, 0)
		self.valueText = QtWidgets.QLineEdit()
		self.layout().addWidget(self.valueText, 0, 1)




# if __name__ == '__main__':
# 	app = QtWidgets.QApplication(sys.argv)
# 	window = SetScreencapAreaWidget()
# 	window.show()
# 	app.aboutToQuit.connect(app.deleteLater)
# 	sys.exit(app.exec_())
