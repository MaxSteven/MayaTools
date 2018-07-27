import copy
import arkUtil.arkUtil

from translators import Events

from translators import QtGui

class Knob(Events):
	application = None
	visible = True
	showLabel = True
	useFullRow = False
	defaultOptions = {}
	defaultValue = ''

	def __init__(self, name, value=None, options={}):
		super(Knob, self).__init__()
		self.node = None
		self.widget = None
		self.parent = None
		self.name = name
		self.options = options
		self.setDefaultOptions()
		self.value = value

		self.init()

	def init(self):
		if 'value' in self.options:
			self.setValue(self.options['value'], emit=False)
		elif self.value is None:
			self.setToDefaultValue()

	def setDefaultOptions(self):
		for k,v in self.defaultOptions.iteritems():
			if k not in self.options:
				self.options[k] = v

	def getValue(self):
		if self.widget:
			self.setValueFromWidget()

		if self.value is None:
			return self.defaultValue

		return self.value

	def setValue(self, value, emit=True):
		if value is None:
			self.setToDefaultValue()

		elif value != self.value:
			self.value = value
			self.updateWidgetValue()
			if emit:
				self.emit('changed', self.value)

		else:
			return

	def fromScript(self, value):
		return self.setValue(value, emit=False)

	def toScript(self, string=True):
		if string:
			return str(self.getValue())
		else:
			return self.getValue()

	def setToDefaultValue(self):
		self.value = copy.copy(self.defaultValue)
		self.updateWidgetValue()

	def isDefault(self):
		return self.value is None

	def createWidget(self):
		self.widget = QtGui.QLineEdit(str(self.value))

	def updateWidgetValue(self):
		'''
		updates the widget when setValue is called
		'''
		if not self.widget:
			return

		self.widget.setText(str(self.value))

	def setValueFromWidget(self):
		'''
		updates self.value from the widget
		'''
		self.setValue(self.widget.text(), emit=False)

	def widgetEdited(self):
		'''
		triggered when the user enters text and focuses out
		'''
		ogValue = self.value
		self.setValueFromWidget()
		if self.value != ogValue:
			self.emit('changed', self.value)

	def setParent(self, parent=None):
		self.parent = parent

	def executePython(self, code):
		context = {
			'self': self.parent,
			'knob': self,
		}
		result = arkUtil.executePython(code, context)
		print result
		return result

	def getParentMethod(self, methodName):
		if not hasattr(self.parent, methodName):
			raise Exception('Callback not found for: ' + str(self.name))
		return getattr(self.parent, methodName)

	def getWidget(self):
		return self.widget

	def getWidgets(self):
		return [self.widget]

	def setKnobToWidget(self):
		for widget in self.getWidgets():
			widget.knob = self

	def clear(self):
		self.widget.clear()
		self.value = ''
		return self
