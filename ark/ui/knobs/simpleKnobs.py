from knob import Knob
from translators import QtGui, QtCore
import arkMath

class Text(Knob):
	def setValue(self, value, emit=True):
		if str(value) != self.value:
			self.value = str(value)
			self.updateWidgetValue()
			if emit:
				self.emit('changed', self.value)
		else:
			return

	def updateWidgetValue(self):
		if self.widget:
			if 'multiline' in self.options:
				self.widget.setPlainText(self.value)
			else:
				self.widget.setText(self.value)

	def setValueFromWidget(self):
		if 'multiline' in self.options:
			self.value = str(self.widget.toPlainText())
		else:
			self.value = str(self.widget.text())

	def setToDefaultValue(self):
		self.value = ''

	def isDefault(self):
		return self.value == ''

	def createWidget(self):
		if 'multiline' in self.options:
			value = str(self.getValue()).replace('\n','<br>')
			self.widget = QtGui.QTextEdit(value)

			# defaults to accepting rich text
			if 'acceptRichText' not in self.options:
				self.widget.setAcceptRichText(False)

		else:
			super(Text, self).createWidget()

		if 'readOnly' in self.options:
				self.widget.setReadOnly(self.options.get('readOnly'))
		self.widget.cursorPositionChanged.connect(self.onKeyReleased)

	def onKeyReleased(self):
		self.emit('keyReleased')

class Vec3(Knob):
	defaultValue = arkMath.Vec(float(0), float(0), float(0))

	def createWidget(self):
		self.widget = QtGui.QWidget()

		hBox = QtGui.QHBoxLayout()
		hBox.setContentsMargins(0, 0, 0, 0)
		hBox.setSpacing(5)
		self.vecx = QtGui.QLineEdit()
		self.vecy = QtGui.QLineEdit()
		self.vecz = QtGui.QLineEdit()
		hBox.addWidget(self.vecx)
		hBox.addWidget(self.vecy)
		hBox.addWidget(self.vecz)
		hBox.setAlignment(QtCore.Qt.AlignTop)
		self.widget.setLayout(hBox)
		self.vecx.editingFinished.connect(self.widgetEdited)
		self.vecy.editingFinished.connect(self.widgetEdited)
		self.vecz.editingFinished.connect(self.widgetEdited)

	def widgetEdited(self):
		self.setValueFromWidget()
		self.value = arkMath.Vec(float(self.value[0]),float(self.value[1]),float(self.value[2]))
		self.emit('changed', self.value)

	def updateWidgetValue(self):
		if not self.widget:
			return
		self.vecx.setText(str(self.value.x))
		self.vecy.setText(str(self.value.y))
		self.vecz.setText(str(self.value.z))

	def setValueFromWidget(self):
		self.setValue([self.vecx.text(), self.vecy.text(), self.vecz.text()], emit=False)

	def setValue(self, value, emit=True):
		try:
			value = arkMath.Vec(float(value[0]), float(value[1]), float(value[2]))
			if self.value != value:
				self.value = value
				self.updateWidgetValue()
				if emit:
						self.emit('changed', self.value)
			else:
				return
		except:
			self.setToDefaultValue()

class Heading(Knob):
	useFullRow = True
	showLabel = False

	def createWidget(self):
		self.widget = QtGui.QLabel(str(self.value))
		self.widget.setObjectName('heading')

class Label(Knob):
	useFullRow = True
	showLabel = False

	def createWidget(self):
		self.widget = QtGui.QLabel(str(self.value))

class VariableCheckbox(Knob):
	defaultValue = {}
	labels = []

	def init(self):
		self.labels = self.options['labels']
		for label in self.labels:
			self.defaultValue[label] = False
		self.value = self.defaultValue

	def createWidget(self):
		self.widget = QtGui.QWidget()
		hBox = QtGui.QHBoxLayout()
		hBox.setContentsMargins(0, 0, 0, 0)
		hBox.setSpacing(5)
		for label in self.labels:
			checkBox = QtGui.QCheckBox(label)
			checkBox.setChecked(self.value.get(label))
			checkBox.stateChanged.connect(self.widgetEdited)
			hBox.addWidget(checkBox)
		hBox.setAlignment(QtCore.Qt.AlignTop)
		self.widget.setLayout(hBox)

	def widgetEdited(self):
		self.setValueFromWidget()
		self.emit('changed', None)

	def setValue(self, value, emit=True):
		checkBoxes = self.widget.findChildren(QtGui.QCheckBox)
		for checkBox in checkBoxes:
			self.value[checkBox.text()] = checkBox.isChecked()
		self.updateWidgetValue()

		if emit:
			self.emit('changed', self.value)

	def setValueFromWidget(self):
		self.setValue(None, emit=False)

	def updateWidgetValue(self):
		if not self.widget:
			return
		checkBoxes = self.widget.findChildren(QtGui.QCheckBox)
		for checkBox in checkBoxes:
			checkBox.setChecked(self.value[checkBox.text()])
		# self.widget.setChecked(self.value)

class Checkbox(Knob):
	defaultValue = False

	def setValue(self, value, emit=True):
		self.value = value
		self.updateWidgetValue()

		if emit:
			self.emit('changed', self.value)

	def setToDefaultValue(self):
		self.value = self.defaultValue

	def isDefault(self):
		return not self.value

	def widgetEdited(self):
		self.setValueFromWidget()
		self.emit('changed', self.value)

	def createWidget(self):
		self.widget = QtGui.QCheckBox()
		self.widget.setChecked(self.value)
		self.widget.stateChanged.connect(self.widgetEdited)

	def setValueFromWidget(self):
		self.setValue(self.widget.isChecked(), emit=False)

	def updateWidgetValue(self):
		if not self.widget:
			return
		self.widget.setChecked(self.value)

class Float(Knob):

	defaultValue = 0.0

	def setValue(self, value, emit=True):
		try:
			if float(value) != self.value:
				self.value = float(value)
				self.updateWidgetValue()
				if emit:
					self.emit('changed', self.value)
			else:
				return

		except:
			self.setToDefaultValue()


class Int(Knob):
	defaultValue = 0

	def setValue(self, value, emit=True):
		try:
			if int(value) != self.value:
				self.value = int(value)
				self.updateWidgetValue()
				if emit:
					self.emit('changed', self.value)

			else:
				return
		except:
			self.setToDefaultValue()


class FrameRange(Knob):
	def getValue(self):
		value = super(FrameRange, self).getValue()
		return value.replace(' ','')

	def setValue(self, value, emit=True):
		if value != self.value:
			self.value = value
			self.updateWidgetValue()
			if emit:
				self.emit('changed', self.value)

		else:
			return

class Resolution(Knob):

	defaultValue={'width': 0, 'height': 0}

	def init(self):
		self.setToDefaultValue()
		super(Resolution, self).init()

	def createWidget(self):
		self.widget = QtGui.QWidget()
		hBox = QtGui.QHBoxLayout()
		hBox.setContentsMargins(0, 0, 0, 0)
		hBox.setSpacing(5)

		self.widthKnob = QtGui.QLineEdit()
		hBox.addWidget(self.widthKnob)
		self.heightKnob = QtGui.QLineEdit()
		hBox.addWidget(self.heightKnob)
		self.widthKnob.editingFinished.connect(self.widgetEdited)
		self.heightKnob.editingFinished.connect(self.widgetEdited)

		self.widget.setLayout(hBox)

	def setValue(self, value, emit=True):
		if (value['width'] != self.value['width']) or \
			(value['height'] != self.value['height']):

			self.value = value
			self.updateWidgetValue()
			if emit:
				self.emit('changed', self.value)
		else:
			return

	def setWidth(self, value):
		currentHeight = self.value['height']
		self.setValue({'width': value, 'height': currentHeight})

	def setHeight(self, value):
		currentWidth = self.value['width']
		self.setValue({'width': currentWidth, 'height': value})

	def getWidth(self):
		return self.value['width']

	def getHeight(self):
		return self.value['height']

	def updateWidgetValue(self):
		if not self.widget or not self.value:
			return
		self.widthKnob.setText(str(self.value['width']))
		self.heightKnob.setText(str(self.value['height']))

	def setValueFromWidget(self):
		try:
			width = int(self.widthKnob.text())
			height = int(self.heightKnob.text())
			self.setValue({'width': width, 'height': height}, emit=False)

		except ValueError:
			self.setToDefaultValue()


class Hidden(Knob):
	def createWidget(self):
		pass
