from knob import Knob
from translators import QtGui, QtCore, QtSignal, QEvent

###This class simply allows us to have a signal emitted from the QWidget
class QChangingWidget(QtGui.QWidget):
	stateChanged  = QtSignal()

class Notification(Knob):
	useFullRow = True
	showLabel = False

	def init(self):
		super(Notification, self).init()

		self.hideTop = QtCore.QPoint(0,-200)
		self.hideBottom = QtCore.QPoint(0,1000)
		self.displayBottom = QtCore.QPoint(0,800 - 150)
		self.beingDisplayed = False

	def createWidget(self):
		self.widget = QChangingWidget()

		self.row = 0
		if self.options['row'] != 'None':
			self.row = self.options['row']

		self.label = QtGui.QLabel(str(self.value))
		self.label.setFixedWidth(250)
		self.label.setFixedHeight(100)

		self.button = QtGui.QPushButton('x')
		self.button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.button.setAutoDefault(False)
		self.button.setFixedWidth(40)

		if self.options['callback'] != 'None':
			method = self.getParentMethod(self.options['callback'])
			self.button.clicked.connect(method)
		self.button.clicked.connect(self.buttonClicked)

		layout = QtGui.QVBoxLayout()
		layout.addWidget(self.button)
		layout.addWidget(self.label)

		self.widget.setLayout(layout)

		self.resetPosition()

	def openNotification(self, duration=300, value=None):
		self.beingDisplayed = True
		self.updateWidgetValue(value=value)

		self.showAnimation = QtCore.QPropertyAnimation(self.widget, b'pos')
		self.showAnimation.setStartValue(self.hideBottom)
		self.showAnimation.setEndValue(self.displayBottom)
		self.showAnimation.setDuration(duration)
		self.showAnimation.setEasingCurve(QtCore.QEasingCurve.OutExpo)
		self.showAnimation.finished.connect(self.wait)
		self.showAnimation.start()

	def wait(self, duration=4000):
		QtCore.QTimer.singleShot(duration,self.closeNotification)

	def isDisplayed(self):
		return self.beingDisplayed

	def moveUp(self):
		self.widget.move(self.widget.pos() - QtCore.QPoint(0, 150))

	def closeNotification(self, duration=300):
		self.closeAnimation = QtCore.QPropertyAnimation(self.widget, b'pos')
		self.closeAnimation.setStartValue(self.widget.pos())
		self.closeAnimation.setEndValue(self.widget.pos() + QtCore.QPoint(500, 0))
		self.closeAnimation.setDuration(duration)
		#self.closeAnimation.setEasingCurve(QtCore.QEasingCurve.OutExpo)
		self.closeAnimation.finished.connect(self.test)
		self.closeAnimation.start()

	def setRow(self, row):
		self.row = QtCore.QPropertyAnimation(self.widget, b'pos')

	def resetPosition(self):
		self.resetAnimation = QtCore.QPropertyAnimation(self.widget, b'pos')
		self.resetAnimation.setStartValue(self.hideBottom)
		self.resetAnimation.setEndValue(self.hideBottom)
		self.resetAnimation.setDuration(10)
		self.resetAnimation.start()

	def test(self):
		self.beingDisplayed = False
		self.emit('notfied', self.row)
		print 'Notified :)'

	def updateWidgetValue(self, value=None):
		if value is not None:
			self.label.setText(value)

	def buttonClicked(self):
		self.emit('clicked')

