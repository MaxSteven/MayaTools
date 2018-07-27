
import baseWidget

class SteppedGui(baseWidget.BaseWidget):
	def __init__(self, parent=None, options={}, *args, **kwargs):
		self.step = 0
		if 'steps' in options:
			self.steps = options['steps']
		else:
			self.steps = []

		super(SteppedGui, self).__init__(parent, options, *args, **kwargs)

	def postShow(self):
		self.showStep()

	def addStep(self, stepInfo):
		self.steps.append(stepInfo)

	def showStep(self, step=None):
		if not len(self.steps):
			return

		if not step:
			step = self.step

		stepInfo = self.steps[step]
		stepInfo['widget'].show()

		# self.setGeometry(stepInfo['widget'].geometry())
		self.resize(stepInfo['widget'].geometry().width(),
					stepInfo['widget'].geometry().height())
		if stepInfo['widget'].x() != 0 and stepInfo['widget'].y() != 0:
			self.move(stepInfo['widget'].x(), stepInfo['widget'].y())

		self.layout.addWidget(self.steps[step]['widget'])

		stepInfo['widget'].submitted.connect(stepInfo['callback'])

	def closeStep(self, step=None):
		if not step:
			step = self.step
		self.steps[step]['widget'].hide()

	def next(self):
		self.closeStep()
		self.step += 1
		self.showStep()

	def back(self):
		self.closeStep()
		self.step -= 1
		self.showStep()

	def getCurrentWidget(self):
		if 'widget' in self.steps[self.step]:
			return self.steps[self.step]['widget']
		else:
			raise Exception('No widget found in current step')