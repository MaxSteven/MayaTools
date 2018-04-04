import sys
from PyQt4 import QtGui, QtCore

class MyWidget(QtGui.QWidget):
	def __init__(self):
		super(MyWidget, self).__init__()
		self.screen = QtGui.QDesktopWidget()
		screen_width = self.screen.screenGeometry().width()
		screen_height = self.screen.screenGeometry().height()
		self.pixmap = QtGui.QPixmap()
		self.setGeometry(0, 0, screen_width, screen_height)
		self.setWindowTitle(' ')
		self.begin = QtCore.QPoint()
		self.end = QtCore.QPoint()
		self.setWindowOpacity(0.3)
		QtGui.QApplication.setOverrideCursor(
			QtGui.QCursor(QtCore.Qt.CrossCursor)
		)
		self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
		print('Capture the screen...')

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
		y2 = max(self.begin.y(), self.end.y()) - y1
		

		screenShotPixmap = QtGui.QPixmap()
		img = screenShotPixmap.grabWindow(QtGui.QApplication.desktop().winId(), x = x1, y = y1, width = x2, height = y2)
		img.save('C:/rigTestFolder/testing.png')
		self.close()
		# img = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)

		# cv2.imshow('Captured Image', img)
		# cv2.waitKey(0)
		# cv2.destroyAllWindows()
if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	window = MyWidget()
	window.show()
	sys.exit(app.exec_())