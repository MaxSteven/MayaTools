
# http://stackoverflow.com/questions/15686501/qt-qtablewidget-column-resizing

from knob import Knob
from translators import QtGui#, QtCore
import arkUtil

class Table(Knob):
	useFullRow = True
	defaultOptions = {
		'showLineNumbers': False,
		'showGrid': True,
		'selectionStyle': 'row',
		'columnResizeMode': 'contents',
		'selectionMode': 'single',
	}
	defaultValue = []

	def init(self):
		self.items = []
		super(Table, self).init()

		if 'items' in self.options and self.options['items']:
			for item in self.options['items']:
				if len(item) != len(self.options['headings']):
					raise Exception('Invalid item:', str(item))
				self.items.append(item)

	def createWidget(self):
		self.widget = QtGui.QTableWidget()
		self.columns = len(self.options['headings'])
		try:
			self.widget.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
		except AttributeError:
			self.widget.horizontalHeader().setSectionResizeMode(QtGui.QHeaderView.Stretch)
		self.widget.setColumnCount(len(self.options['headings']))
		self.widget.setHorizontalHeaderLabels(self.options['headings'])
		self.widget.verticalHeader().setVisible(self.options['showLineNumbers'])
		self.widget.setShowGrid(self.options['showGrid'])
		self.widget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)

		if self.options['selectionStyle'] == 'row':
			self.widget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
		elif self.options['selectionStyle'] == 'column':
			self.widget.setSelectionBehavior(QtGui.QAbstractItemView.SelectColumns)
		elif self.options['selectionStyle'] == 'item':
			self.widget.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)

		if self.options['selectionMode'] == 'single':
			self.widget.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
		elif self.options['selectionMode'] == 'multi':
			self.widget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)

		self.updateRowCount()
		self.rows = self.widget.rowCount()

		# addItems sets appends items to self.items
		# so we copy it, then clear it, then call self.addItems
		# hacky but better than the other options
		items = self.items
		self.items = []
		self.addItems(items)

		self.widget.cellClicked.connect(self.widgetEdited)

	def updateWidgetValue(self):
		pass

	def updateRowCount(self):
		self.widget.setRowCount(len(self.items))

	def addItems(self, items=None):
		if not items:
			return

		self.items += items
		self.updateRowCount()

		for r, row in enumerate(self.items):
			for c, column in enumerate(row):
				item = QtGui.QTableWidgetItem(str(self.items[r][c]))
				self.widget.setItem(r,c, item)

		if len(self.options['headings']) == 1:
			self.widget.horizontalHeader().setStretchLastSection(True)
		else:
			self.widget.resizeColumnsToContents()

	def removeRow(self, row):
		self.widget.removeRow(row)
		self.items.pop(row)
		self.updateRowCount()

	def removeSelected(self):
		selection = self.widget.selectedIndexes()
 		selection = [i.row() for i in selection]

 		# row will be listed for each column that's selected
 		# make it unique so we're not removing it three times
 		selection = arkUtil.makeArrayUnique(selection)
 		selection.sort()
 		selection.reverse()

 		for row in selection:
 			self.removeRow(row)

	def removeUnselected(self):
		rowCount = len(self.items)
		selection = self.widget.selectedIndexes()
		selection = set([i.row() for i in selection])
		unselected = [i for i in range(rowCount) if i not in selection]
		unselected.sort()
		unselected.reverse()

		for row in unselected:
			self.removeRow(row)

		self.updateRowCount()

	def clear(self):
		self.widget.clear()
		self.items = []
		self.updateRowCount()

	def addItem(self, items=None):
		self.addItems([items])

	def setValueFromWidget(self):
		items = []
		if self.widget.selectedItems():
			for item in self.widget.selectedItems():
				items.append(item.text())

			self.setValue(items, emit=False)

		else:
			self.setToDefaultValue()

	def setValue(self, value=[], emit=True):
		# print 'value', value
		if value and self.value != value:
			self.value = value
			self.updateWidgetValue()
			if emit:
				self.emit('changed', self.value)

		else:
			return

