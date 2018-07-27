import copy

from knob import Knob
from translators import QtGui
from translators import QtCore
from translators import QtSignal
from translators import QEvent

import arkUtil

class List(Knob):

	defaultOptions = {
		'options': []
		}

	def init(self):
		# ensure all options are strings
		self.listItems = []
		if self.options['options']:
			self.listItems = [str(o) for o in self.options['options']]
		super(List, self).init()

	def createWidget(self):
		self.widget = QtGui.QComboBox()
		for i, option in enumerate(self.listItems):
			self.widget.addItem(option, i)

		self.widget.currentIndexChanged.connect(self.widgetEdited)

	def setValueFromWidget(self):
		self.setValue(self.widget.currentText(), emit=False)

	def addItem(self, item):
		hadOptions = len(self.listItems)
		self.listItems.append(item)
		if not hadOptions:
			self.setValue(self.listItems[0], emit=False)
		if self.widget:
			self.widget.addItem(item)
		return self

	def setValue(self, value, emit=True):
		if value and self.value != value:
			if value in self.listItems:
				self.value = value
				self.updateWidgetValue()
				if emit:
					self.emit('changed', self.value)
			else:
				raise Exception('Value not in options.')
		else:
			return

	def addItems(self, items):
		for item in items:
			self.addItem(item)

		return self

	def clear(self):
		self.widget.clear()
		self.listItems = []
		self.value = ''
		return self

	def updateWidgetValue(self):
		if not self.widget:
			return

		if self.value in self.listItems:
			self.widget.setCurrentIndex(self.listItems.index(self.value))

	def getSelectedIndex(self):
		return self.widget.currentRow()

	# returns list of all items
	def items(self):
		return self.listItems

###This class simply allows us to have a signal emitted from the QWidget
class QChangingWidget(QtGui.QWidget):
	stateChanged  = QtSignal()

class Radio(List):

	def isDefault(self):
		return self.getValue() != self.listItems[0]

	def createWidget(self):
		self.qButtons = []

		self.widget = QChangingWidget()
		hbox = QtGui.QHBoxLayout()

		# this stops the buttons from floating away from each other
		hbox.setSizeConstraint(QtGui.QLayout.SetFixedSize)
		hbox.setContentsMargins(0,0,0,0)
		for item in self.listItems:
			box = QtGui.QRadioButton(str(item))
			box.clicked.connect(self.widgetEdited)
			box.clicked.connect(self.widget.stateChanged)
			hbox.addWidget(box)
			self.qButtons.append(box)

		self.widget.setLayout(hbox)

	def setValueFromWidget(self):
		for i, b in enumerate(self.qButtons):
			if b.isChecked():
				self.setValue(self.listItems[i], emit=False)

	def updateWidgetValue(self):
		if not self.widget or not self.value:
			return

		if self.value in self.listItems:
			self.qButtons[self.listItems.index(self.value)].setChecked(True)

	def setValue(self, value, emit=True):
		if value and self.value != value:
			if value in self.listItems:
				self.value = value
				self.updateWidgetValue()
				if emit:
					self.emit('changed', self.value)
			else:
				raise Exception('Value not in options.')
		else:
			return

	def getSelectedIndex(self):
		return self.listItems.index(self.value)

class ListBox(List):

	# Adding Default SelectionMode
	defaultOptions = {
		'selectionMode': 'single',
		'options': []
		}

	def init(self):

		# Since now selection mode is determing the behaviour of the knob,
		# it's better to assign it as a class variable
		self.selectionMode = self.options['selectionMode']

		# and needs to be done in init because init runs setValue
		super(ListBox, self).init()

	def createWidget(self):
		self.widget = QtGui.QListWidget()

		if self.selectionMode == 'multi':
			self.widget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)

		# Raise exception if selectionMode is something else
		elif self.selectionMode != 'single':
			raise Exception('Invalid Selection mode')

		# addItems sets appends items to self.items
		# so we copy it, then clear it, then call self.addItems
		# hacky but better than the other options
		items = self.listItems
		self.listItems = []
		self.addItems(items)
		self.listItems = []

		self.widget.itemClicked.connect(self.widgetEdited)
		self.widget.itemDoubleClicked.connect(self.doubleClicked)

	def addItem(self, item=None):
		self.addItems([item])
		self.listItems.append(item)

	def widgetEdited(self):
		# Since now value can be a list or a string, this checks whether widget value either
		# exists in the list or is equal to the string or not.
		items = []

		if self.widget.count() == 0:
			return

		if not self.widget.selectedItems():
			self.setValue(None)

		for item in self.widget.selectedItems():
			items.append(item.text())

		if (self.selectionMode == 'multi' and self.value != items) or \
			(self.selectionMode == 'single' and self.value != self.widget.currentItem().text()):

			self.setValueFromWidget()
			self.emit('changed', self.getValue())

	def doubleClicked(self):
		self.emit('doubleClicked')

	def getValue(self):
		# check if widget exists and items exist in widget
		if self.widget and self.widget.item(0):
			self.setValueFromWidget()

		if self.value is None:
			return self.defaultValue

		return self.value

	def addItems(self, items = []):
		if items != []:
			items = arkUtil.ensureArray(items)
			self.widget.addItems(items)
			self.listItems.extend(items)
			# if value not mentioned then set default value as first value
			if not self.value:

				# if mode is single then set value as string
				if self.selectionMode == 'single':
					self.setValue(self.widget.item(0).text(), emit=False)


	def setValue(self, value, emit=True):
		# If value sent is a list but selection mode is string, then raise Exception
		if self.selectionMode == 'single' and isinstance(value, list):
			raise Exception('Invalid Value')

		if value and value != self.value:
			self.value = value
			self.updateWidgetValue()

		elif not value and self.selectionMode == 'multi':
			self.value = None

		if emit:
			self.emit('changed', self.value)

	def setValueFromWidget(self):
		if self.widget.currentItem():
		# if selection mode is multi then send item list
			if self.selectionMode == 'multi':
				itemList = []
				for item in self.widget.selectedItems():
					itemList.append(item.text())
				self.setValue(itemList, emit=False)

			# else send text of selected Item
			else:
				self.setValue(self.widget.currentItem().text(), emit=False)

	def clear(self):
		self.listItems = []
		self.widget.clear()
		self.value = ''
		return self

	def clearSelection(self):
		self.widget.clearSelection()
		self.value = ''

	def setIndex(self, index):
		self.widget.setCurrentRow(index)

	def updateWidgetValue(self):
		if not self.widget:
			return

		# if self.value in self.listItems
		if self.value in self.listItems:
			# if selectionMode is single then then select sel.value in list
			if self.selectionMode == 'single':
				valueItem = self.widget.findItems(self.value, QtCore.Qt.MatchExactly)[0]
				valueItem.setSelected(True)

			# else select every item in self.value
			else:
				for v in self.value:
					valueItem = self.widget.findItems(v, QtCore.Qt.MatchExactly)[0]
					valueItem.setSelected(True)

	def getSelectedIndexes(self):
		return [i.row() for i in self.widget.selectedIndexes()]

	def removeItem(self, itemText):
		self.widget.takeItem(self.listItems.index(itemText))
		if itemText in self.value or itemText == self.value:
			self.setValueFromWidget()

		self.listItems.remove(itemText)

class DynamicList(ListBox):

	defaultOptions = {
		'selectionMode': 'single',
		'options': [],
		'height': 150
		}

	def createWidget(self):
		self.widget = QtGui.QWidget()
		vBox = QtGui.QVBoxLayout()
		vBox.setContentsMargins(0, 0, 0, 0)
		vBox.setSpacing(5)
		self.addItemText = QtGui.QLineEdit()
		self.itemList = QtGui.QListWidget()

		if (self.options['selectionMode'] == 'multi'):
			self.itemList.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)

		elif self.selectionMode != 'single':
			raise Exception('Invalid Selection mode')

		self.addItemText.returnPressed.connect(self.addItem)

		# emit clicked when item is added and auto-selected in Dynamic List
		self.addItemText.returnPressed.connect(self.clicked)

		self.itemList.itemClicked.connect(self.clicked)
		self.itemList.itemDoubleClicked.connect(self.doubleClicked)

		vBox.addWidget(self.addItemText)
		vBox.addWidget(self.itemList)

		# addItems sets appends items to self.items
		# so we copy it, then clear it, then call self.addItems
		# hacky but better than the other options
		items = self.listItems
		self.listItems = []
		self.addItems(items)

		self.widget.setLayout(vBox)
		self.widget.setMinimumHeight(self.options['height'])

	def addItems(self, items, emit=True):
		items = copy.copy(items)
		for item in items:
			self.addItem(item, emit=emit)

	def getValue(self):
		# check if widget exists and items exist in itemList
		if self.widget and self.itemList.item(0):
			self.setValueFromWidget()

		if self.value is None:
			return self.defaultValue

		return self.value

	def addItem(self, item=None, emit=True):
		if not item:
			item = self.addItemText.text()
			self.addItemText.clear()

		if not item:
			return

		self.itemList.addItem(item)
		self.listItems.append(item)

		items = self.itemList.selectedItems()
		for i in items:
			i.setSelected(False)

		if items:
			items[-1].setSelected(True)
		self.setValueFromWidget()

		if emit:
			self.emit('itemAdded', item)

	def widgetEdited(self):
		# Since now value can be a list or a string, this checks whether widget value either
		# exists in the list or is equal to the string or not.
		items = []
		for item in self.itemList.selectedItems():
			items.append(item.text())

		if (self.selectionMode == 'multi' and self.value != items) or \
			(self.selectionMode == 'single' and self.value != self.itemList.currentItem().text()):

			self.setValueFromWidget()
			self.emit('changed')

	def clicked(self):
		self.emit('clicked')

	def doubleClicked(self):
		self.emit('doubleClicked')

	def setValueFromWidget(self):
		if self.itemList.currentItem():
			if self.selectionMode == 'multi':
				itemList = []
				for item in self.itemList.selectedItems():
					itemList.append(item.text())
				self.setValue(itemList, emit=False)

			else:
				self.setValue(self.itemList.currentItem().text(), emit=False)

	def updateWidgetValue(self):
		if not self.widget:
			return

		if self.value in self.listItems:
			if self.selectionMode == 'single':
				self.setIndex(self.listItems.index(self.value))
			else:
				if isinstance(self.value, list):
					for v in self.value:
						valueItem = self.itemList.findItems(v, QtCore.Qt.MatchExactly)[0]
						valueItem.setSelected(True)

				else:
					valueItem = self.itemList.findItems(self.value, QtCore.Qt.MatchExactly)[0]
					valueItem.setSelected(True)

	def setIndex(self, index):
		self.itemList.setCurrentRow(index)

	def clear(self):
		self.itemList.clear()
		self.value = ''
		self.listItems = []
		return self

	def getSelectedIndexes(self):
		return [i.row() for i in self.itemList.selectedIndexes()]

	def removeItem(self, itemText):
		self.itemList.takeItem(self.listItems.index(itemText))
		if itemText in self.value or itemText == self.value:
			self.setValueFromWidget()

		self.listItems.remove(itemText)

	def getItems(self):
		return self.listItems

class SearchList(ListBox):

	defaultOptions = {
		'selectionMode': 'single',
		'options': [],
		'height': 150
		}


	def createWidget(self):
		class SearchTextBox(QtGui.QLineEdit):
			downKeyPressed = QtSignal(QEvent)

			def __init__(self, parent=None):
				super(SearchTextBox, self).__init__(parent)

			def keyPressEvent(self, event):
				if event.key() == QtCore.Qt.Key_Down:
					self.downKeyPressed.emit(event)

				super(SearchTextBox, self).keyPressEvent(event)

		self.widget = QtGui.QWidget()
		vBox = QtGui.QVBoxLayout()
		vBox.setContentsMargins(0, 0, 0, 0)
		vBox.setSpacing(5)
		self.searchItemText = SearchTextBox()
		self.itemList = QtGui.QListWidget()

		if (self.options['selectionMode'] == 'multi'):
			self.itemList.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)

		elif self.selectionMode != 'single':
			raise Exception('Invalid Selection mode')

		# emit clicked when item is added and auto-selected in Dynamic List
		self.searchItemText.cursorPositionChanged.connect(self.updateList)
		self.searchItemText.downKeyPressed.connect(self.downKeyPressed)

		self.itemList.itemClicked.connect(self.clicked)
		self.itemList.itemDoubleClicked.connect(self.doubleClicked)

		vBox.addWidget(self.searchItemText)
		vBox.addWidget(self.itemList)

		# addItems sets appends items to self.items
		# so we copy it, then clear it, then call self.addItems
		# hacky but better than the other options
		items = self.listItems
		self.listItems = []
		self.addItems(items)

		self.widget.setLayout(vBox)
		self.widget.setMinimumHeight(self.options['height'])
		self.updateList()

	def updateList(self):
		searchString = self.searchItemText.text().strip().lower()
		if searchString is '':
			filteredItems = self.listItems
		else:
			filteredItems = []
			for item in self.listItems:
				start = 0
				for i in range(0, len(searchString)):
					start = item.lower().find(searchString[i], start)
					if start == -1:
						break
					else:
						start += 1
				if start != -1:
					filteredItems.append(item)

		filteredItems = arkUtil.sort(filteredItems)
		self.itemList.clear()
		if self.options.get('hasNone'):
			self.itemList.addItem('None')
		self.itemList.addItems(filteredItems)

	def addItems(self, items, emit=True):
		items = copy.copy(items)
		for item in items:
			self.addItem(item, emit=emit)
		self.updateList

	def getValue(self):
		# check if widget exists and items exist in itemList
		if self.widget and self.itemList.item(0):
			self.setValueFromWidget()

		if self.value is None:
			return self.defaultValue

		return self.value

	def addItem(self, item=None, emit=True):
		if not item:
			return

		self.itemList.addItem(item)
		self.listItems.append(item)
		if emit:
			self.emit('itemAdded', item)
		self.updateList()

	def downKeyPressed(self, event):
		self.itemList.item(0).setSelected(True)
		self.itemList.setFocus()

	def widgetEdited(self):
		# Since now value can be a list or a string, this checks whether widget value either
		# exists in the list or is equal to the string or not.
		items = []

		if self.itemList.count() == 0:
			return

		if not self.itemList.selectedItems():
			self.setValue(None)

		for item in self.itemList.selectedItems():
			items.append(item.text())

		if (self.selectionMode == 'multi' and self.value != items) or \
			(self.selectionMode == 'single' and self.value != self.itemList.currentItem().text()):

			self.setValueFromWidget()
			self.emit('changed', self.getValue())

	def clicked(self):
		self.emit('clicked')

	def doubleClicked(self):
		self.emit('doubleClicked')

	def setValueFromWidget(self):
		if self.itemList.currentItem():
			if self.selectionMode == 'multi':
				itemList = []
				for item in self.itemList.selectedItems():
					itemList.append(item.text())
				self.setValue(itemList, emit=False)

			else:
				self.setValue(self.itemList.currentItem().text(), emit=False)

	def updateWidgetValue(self):
		if not self.widget:
			return

		# if self.value in self.listItems
		if self.value in self.listItems:
			# if selectionMode is single then then select sel.value in list
			if self.selectionMode == 'single':
				valueItem = self.itemList.findItems(self.value, QtCore.Qt.MatchExactly)[0]
				valueItem.setSelected(True)

			# else select every item in self.value
			else:
				for v in self.value:
					valueItem = self.itemList.findItems(v, QtCore.Qt.MatchExactly)[0]
					valueItem.setSelected(True)

	def setIndex(self, index):
		self.itemList.setCurrentRow(index)

	def clear(self):
		self.itemList.clear()
		if self.options.get('hasNone'):
			self.itemList.addItem('None')
		self.value = ''
		self.listItems = []
		return self

	def getSelectedIndexes(self):
		return [i.row() for i in self.itemList.selectedIndexes()]

	def removeItem(self, itemText):
		self.itemList.takeItem(self.listItems.index(itemText))
		if itemText in self.value or itemText == self.value:
			self.setValueFromWidget()

		self.listItems.remove(itemText)

	def getItems(self):
		return self.listItems

