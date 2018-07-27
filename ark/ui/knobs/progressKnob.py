
# from knob import Knob
from simpleKnobs import Float
from translators import QtGui

class Progress(Float):
	showLabel = False
	useFullRow = True

	def createWidget(self):
		self.widget = QtGui.QProgressBar()
		self.widget.setMaximum(100)

	def updateWidgetValue(self):
		if self.widget:
			self.widget.setValue(self.value * 100)

	def setMaximum(self, maximum):
		self.widget.setMaximum(maximum)

	def getValue(self):
		return self.widget.value()

	def reset(self):
		self.widget.reset()

	def increment(self, value=1):
		self.widget.setValue(self.widget.value() + value)
