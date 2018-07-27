
import collections
import copy
import os
import time
import json

import cOS

import arkUtil

import arkInit
arkInit.init()

import settingsManager
globalSettings = settingsManager.globalSettings()


import knobs

import translators
translator = translators.getCurrent()
currentApp = os.environ.get('ARK_CURRENT_APP')

from translators import QtGui
from translators import QtCore
from translators import Events
from translators import QtSignal
from translators import QEvent

# To Support dockable windows
class BaseWidget(QtGui.QDialog):

	# Creating custom own signal to capture baseWidget events
	keyPressed = QtSignal(QEvent)

	defaultOptions = {
		'title': 'Ingenuity',
		'width': None,
		'height': None,
		'x': None,
		'y': None,
		'margin': '16 16 16 16',
		'spacing': 16,
		'minimize': False,
		'maximize': False,
		'icon': globalSettings.ARK_ROOT + '/ark/ui/icons/ark.png',
		'align': None,
		'alwaysOnTop': False,
		'borderless': False,
		'clickToMove': False,
	}

	def __init__(self, parent=None, options={}, *args, **kwargs):

		super(BaseWidget, self).__init__(parent)

		self.align = {
			'top': QtCore.Qt.AlignTop
		}
		self.events = Events()
		self.knobRows = {}
		self.knobs = collections.OrderedDict()

		self.setDefaultOptions(options)

		# general window setup
		self.name = arkUtil.makeWebSafe(self.options['title'])

		self.settingsRootDir = cOS.ensureEndingSlash(os.environ.get('ARK_CONFIG'))
		self.settingsFile = self.settingsRootDir + self.name + '.json'

		# for making windows Maya Dockable
		self.title = self.options['title']
		self.setWindowTitle(self.title)
		self.setWindowFlags(QtCore.Qt.Window)
		self.setObjectName(self.name)

		if self.options['width'] and self.options['height']:
			self.resize(self.options['width'], self.options['height'])
		if self.options['x'] and self.options['y']:
			self.move(self.options['x'], self.options['y'])

		styleSheet = open(globalSettings.ARK_ROOT + 'ark/ui/css/arkStyle.css').read()
		styleSheet = styleSheet.replace('$uiRoot', globalSettings.ARK_ROOT + 'ark/ui')
		self.setStyleSheet(styleSheet)

		icon = QtGui.QIcon(self.options['icon'])
		self.setWindowIcon(icon)

		if not self.options['minimize']:
			self.setWindowFlags(self.windowFlags() &
				~QtCore.Qt.WindowMinimizeButtonHint)
		if not self.options['maximize']:
			self.setWindowFlags(self.windowFlags() &
				~QtCore.Qt.WindowMaximizeButtonHint)

		if 'knobs' in self.options:
			for option in self.options['knobs']:
				dataType = option['dataType'][0].upper() + option['dataType'][1:]
				knobClass = getattr(knobs, dataType)
				knob = knobClass(option['name'], None, option)
				self.addKnob(knob)

		# for Maya only
		self._dockName = self._dockWidget = None
		self.keyPressed.connect(self.onKey)


		# self.knobHolder = QtGui.QGridLayout()
		# This will replace showKnobs ultimately
		# self.createGUI()

		self.init()
		self.showKnobs()

		self.postShow()

	def addKnobFromDict(self, knobDict, row=-1, replace=False):
		# Checks if knob exists prior to adding
		if knobDict['name'] in self.knobs:
			raise Exception('Duplicate knob name: ' +knobDict['name'])

		# Generates knob
		dataType = knobDict['dataType'][0].upper() + knobDict['dataType'][1:]
		knobClass = getattr(knobs, dataType)
		knob = knobClass(knobDict['name'], None, knobDict)
		# knob.setParent(self)

		# Adds knob to widget's dictionary
		# self.knobs[knob.name] = knob
		# Adds knob to GUI
		self.addKnobToGUI(knob, row, replace)

	def takeWidgets(self, row, column):
		widgets = []
		for i in range(self.knobHolder.count()-1, 0, -1):
			widgetInfo = self.knobHolder.getItemPosition(i)
			if ((widgetInfo[0] <= row and widgetInfo[0] + widgetInfo[2] - 1 >= row) or (widgetInfo[1] <= column and widgetInfo[1] + widgetInfo[4] - 1 >= column)):
				widgets.append(self.knobHolder.takeAt(i).widget())
		return widgets



	def shiftRow(self, rowBefore, rowAfter):
		return


	def addKnobToGUI(self, knob, row, replace):

		self.addKnob(knob)

		if row == -1:
			row = self.knobHolder.rowCount()

		if replace:
			if row != -1:
				widgets = self.takeWidgets(row, -1)
				for key in self.knobRows.keys():
					if widgets[0] in self.knobRows[key]:
						self.removeKnob(key)
						break
		else:
			if row != -1:
				widgetLists = {}
				for i in range(self.knobHolder.rowCount()-1, row-1, -1):
					widgetLists[i] = self.takeWidgets(i, -1)

				for i in range(row, self.knobHolder.rowCount(), 1):
					col = 0
					for widget in reversed(widgetLists[i]):
						self.knobHolder.addWidget(widget, i+1, col)
						col +=1


		if knob.visible and knob.getWidget() == None:
			knob.createWidget()
			knob.updateWidgetValue()
			widget = knob.getWidget()

			for subWidget in knob.getWidgets():
				subWidget.installEventFilter(self)

			knob.setKnobToWidget()

			if knob.showLabel:
				label = self.formatLabel(knob.name)
			else:
				label = ''
			labelWidget = QtGui.QLabel(label)
			if knob.useFullRow:
				if knob.showLabel:
					self.knobHolder.addWidget(labelWidget, row, 0, 1, 2)
					self.knobRows[knob.name] = [labelWidget, widget]
				else:
					self.knobRows[knob.name] = [widget]

				self.knobHolder.addWidget(knob.getWidget(), row, 0, 1, 2)

			else:
				labelWidget.setAlignment(QtCore.Qt.AlignRight)
				self.knobHolder.addWidget(labelWidget, row, 0)
				self.knobHolder.addWidget(widget, row, 1)
				self.knobRows[knob.name] = [labelWidget, widget]

	def createGUI(self):
		self.knobHolder = QtGui.QGridLayout()
		if self.options['align']:
			self.knobHolder.setAlignment(self.align.get(self.options['align']))

		if 'knobs' in self.options:
			for option in self.options['knobs']:
				self.addKnobFromDict(option)

		self.setLayout(self.knobHolder)
		self.layout = self.knobHolder

		margins = [int(x) for x in self.options['margin'].split(' ')]
		self.knobHolder.setContentsMargins(margins[0], margins[1], margins[2], margins[3])
		self.knobHolder.setSpacing(int(self.options['spacing']))

	def init(self):
		pass

	def postShow(self):
		pass

	def setDefaultOptions(self, options):
		# start with base widget's default options
		# this has stuff like x and y, default title, etc
		# always deepcopy so you're not using the class variable
		defaultOptions = copy.deepcopy(BaseWidget.defaultOptions)

		# then get this widget's default options
		# usually default knobs, new title, whatever
		# always deepcopy so you're not using the class variable
		defaultOptions.update(copy.deepcopy(self.defaultOptions))

		# then get the passed in options
		defaultOptions.update(options)

		# finally set all that to options
		self.options = defaultOptions


	def showKnobs(self):
		if not self.knobs:
			return

		self.knobHolder = QtGui.QGridLayout()
		if self.options['align']:
			self.knobHolder.setAlignment(self.align.get(self.options['align']))
		row = 0

			# if self.knobs:

		for knob in self.knobs.values():

			if knob.visible:
				knob.createWidget()
				knob.updateWidgetValue()
				widget = knob.getWidget()

				for subWidget in knob.getWidgets():
					subWidget.installEventFilter(self)

				knob.setKnobToWidget()

				if knob.showLabel:
					label = self.formatLabel(knob.name)
				else:
					label = ''
				labelWidget = QtGui.QLabel(label)
				if knob.useFullRow:
					if knob.showLabel:
						self.knobHolder.addWidget(labelWidget, row, 0, 1, 2)
						self.knobRows[knob.name] = [labelWidget, widget]
						row += 1
					else:
						self.knobRows[knob.name] = [widget]

					self.knobHolder.addWidget(knob.getWidget(), row, 0, 1, 2)

				else:
					labelWidget.setAlignment(QtCore.Qt.AlignRight)
					self.knobHolder.addWidget(labelWidget, row, 0)
					self.knobHolder.addWidget(widget, row, 1)
					self.knobRows[knob.name] = [labelWidget, widget]
				row += 1

		self.setLayout(self.knobHolder)
		self.layout = self.knobHolder

		margins = [int(x) for x in self.options['margin'].split(' ')]
		self.knobHolder.setContentsMargins(margins[0], margins[1], margins[2], margins[3])
		self.knobHolder.setSpacing(int(self.options['spacing']))

	def showKnob(self, knobName):
		for knob in self.knobRows[knobName]:
			knob.show()

	def hideKnob(self, knobName):
		for knob in self.knobRows[knobName]:
			knob.hide()

	def addKnobToLayout(self, knob, row=None):
		# self.addKnob(knob)

		self.addKnob(knob)

		if row == None:
			row = self.knobHolder.count()

		if knob.visible and knob.getWidget() == None:
				knob.createWidget()
				knob.updateWidgetValue()
				widget = knob.getWidget()

				for subWidget in knob.getWidgets():
					subWidget.installEventFilter(self)

				knob.setKnobToWidget()

				if knob.showLabel:
					label = self.formatLabel(knob.name)
				else:
					label = ''
				labelWidget = QtGui.QLabel(label)
				if knob.useFullRow:
					if knob.showLabel:
						self.knobHolder.addWidget(labelWidget, row, 0, 1, 2)
						self.knobRows[knob.name] = [labelWidget, widget]
					else:
						self.knobRows[knob.name] = [widget]

					self.knobHolder.addWidget(knob.getWidget(), row, 0, 1, 2)

				else:
					labelWidget.setAlignment(QtCore.Qt.AlignRight)
					self.knobHolder.addWidget(labelWidget, row, 0)
					self.knobHolder.addWidget(widget, row, 1)
					self.knobRows[knob.name] = [labelWidget, widget]

	def addKnob(self, knob):
		knob.setParent(self)

		if knob.name in self.knobs:
			raise Exception('Duplicate knob name: ' + knob.name)
		self.knobs[knob.name] = knob

	def getKnob(self, knobName):
		if knobName not in self.knobs:
			raise Exception('Knob not found: ' + knobName)
		return self.knobs[knobName]

	def allKnobs(self):
		return self.knobs.values()

	def setKnobs(self, knobDict):
		self.knobs = knobDict

	def removeKnob(self, knobName):
		if knobName in self.knobs:
			for knob in self.knobRows[knobName]:
				knob.setParent(None)
			del self.knobs[knobName]
			del self.knobRows[knobName]

	def formatLabel(self, label):
		if not label:
			return ''
		return label.title() + ':'

	def showError(self, *error):
		text = 'Error: ' + ' '.join([str(e) for e in error])
		QtGui.QMessageBox.critical(
			self,
			'Error',
			text,
			QtGui.QMessageBox.Ok)

	def showMessage(self, msg):
		QtGui.QMessageBox.information(
			self,
			'Information',
			msg,
			QtGui.QMessageBox.Ok)

	def log(self, *args):
		text = ' '.join([str(arg) for arg in args])
		t = time.strftime('%Y/%m/%d %H:%M:%S') + ': '
		print '%s %s' % (t, text)

	# Save and Load
	##################################################
	def saveToFile(self):
		data = self.toScript()
		try:
			with open(self.settingsFile, 'w') as fp:
				json.dump(data, fp)
		except:
			print 'could not save user settings'

	def loadFromFile(self):
		data = {}
		try:
			with open(self.settingsFile, 'r') as fp:
				data = json.load(fp)
			self.loadKnobData(data['knobs'])
		except:
			print 'could not load saved user settings'

	def toScript(self):
		saveData = {}
		saveData['class'] = self.__class__.__name__
		saveData['knobs'] = self.getKnobData()
		return saveData

	def getKnobData(self):
		knobData = {}
		for name, knob in self.knobs.iteritems():
			knobData[name] = knob.toScript(string = False)
		return knobData

	def loadKnobData(self, knobData):
		for name, value in knobData.iteritems():
			# we don't load the name knob because init has already taken care of that and ensured it's unique
			if name in self.knobs and name != 'name':
				self.knobs[name].fromScript(value)

	def closeEvent(self, event):
		self.events.emit('closed')
		event.accept()

	def submit(self, data=None):
		if data is None:
			data = {}
			for knob in self.allKnobs():
				data[knob.name] = knob.getValue()

		self.submitted.emit(data)

	def closeWindow(self):
		self.close()

# Tabbing out of any knob will trigger widgetEdited of that knob
	def eventFilter(self, obj, event):
		if event.type() == QtCore.QEvent.FocusOut:
			obj.knob.widgetEdited()

		return QtCore.QObject.eventFilter(self, obj, event)

# To make sure pressing enter does not activate the pushButton
# We reimplement keyPressEvent
	def keyPressEvent(self, event):
		self.keyPressed.emit(event)

# using Events class for emitting event for enter pressed
	def enterPressed(self):
		self.events.emit('enterPressed')

# Now we filter out enterPressed event by baseWidget to not do anything
	def onKey(self, event):
		if event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter:
			self.enterPressed()
			event.ignore()

	def getDesktop(self):
		qtApp = translator.getQTApp()
		return qtApp.desktop()

	def getCurrentMonitor(self):
		desktop = self.getDesktop()
		pos = self.pos()
		print 'pos:', pos.x(), pos.y()

		for i in range(desktop.numScreens()):
			screen = desktop.screenGeometry(i)
			if pos.x() >= screen.left() and pos.x() < screen.right():
				print 'monitor:', i
				return i

		return 0
