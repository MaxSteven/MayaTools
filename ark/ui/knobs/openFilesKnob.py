
import re

from simpleKnobs import Text
from translators import QtGui
from translators import QtCore
from translators import QtSignal

import knobs

class DropButton(QtGui.QPushButton):

	fileDropped = QtSignal(list)

	def __init__(self, text, parent=None):
		super(DropButton, self).__init__(text, parent)
		self.setAcceptDrops(True)

	def dragEnterEvent(self, event):
		if event.mimeData().hasUrls:
			event.accept()
		else:
			event.ignore()

	def dropEvent(self, event):
		if event.mimeData().hasUrls:
			event.setDropAction(QtCore.Qt.CopyAction)
			event.accept()
			links = []
			for url in event.mimeData().urls():
				links.append(str(url.toLocalFile()))
			self.fileDropped.emit(links)
		else:
			event.ignore()

	def updateWidget(self):
		pass

class FileBrowser(knobs.OpenFile):

	defaultValue = []

	def createWidget(self):
		self.widget = DropButton(self.options['buttonText'])
		self.widget.setMaximumWidth(len(self.options['buttonText']) * 10)
		self.widget.clicked.connect(self.browseFile)
		self.widget.fileDropped.connect(self.collectDrops)

	def browseFile(self):
		filenames = QtGui.QFileDialog.getOpenFileNames(
			self.widget,
			self.options['label'],
			self.options['directory'],
			self.options['extension'])
		self.setValue([str(f) for f in filenames[0]])
		if 'callback' in self.options:
			method = self.getParentMethod(self.options['callback'])
			method()

	def collectDrops(self, links):
		self.setValue(links)
		if 'callback' in self.options:
			method = self.getParentMethod(self.options['callback'])
			method()

	def setValue(self, value):
		if value is None:
			return self.setToDefaultValue()

		self.value = []
		for path in value:
			self.value.append(re.sub(r'[\\/]+', '/', path))

	def updateWidget(self):
		pass

class OpenFiles(Text):

	showLabel = False
	useFullRow = True

	defaultOptions = {
		'label': 'Select file(s)',
		'directory': '',
		'extension': 'Any file (*.*)'
	}

	def createWidget(self):
		self.widget = QtGui.QWidget()
		self.layout = QtGui.QGridLayout()
		self.layout.setContentsMargins(0,0,0,0)
		self.row = 0

		options = {
			'buttonText': 'Drag and drop file(s), click to browse',
			'callback': 'addFiles'
		}
		self.browseKnob = FileBrowser('browse', options=options)
		self.browseKnob.parent = self
		self.layout.addWidget(self.browseKnob.createWidget(), self.row, 0, 1, 2)
		self.browseKnob.widget.setObjectName('dropButton')
		self.row += 1

		# add sequence support when we need it
		# options = {'options': ['collapse sequences', 'show all']}
		# self.modeKnob = knobs.Radio('file mode', 'collapse sequences', options)
		# self.layout.addWidget(self.modeKnob.createWidget(), self.row, 0, 1, 2)
		# self.row += 1

		options = {
			'headings': ['Files'],
		}
		self.fileList = knobs.Table('Files', None, options)
		# span 3 rows for buttons below
		self.layout.addWidget(self.fileList.createWidget(), self.row, 0, 1, 3)
		self.fileList.widget.doubleClicked.connect(self.removeRow)
		self.row += 1

		options = {
			'callback': 'removeSelected',
		}
		knob = knobs.PythonButton('Remove Selected', options=options)
		knob.parent = self
		self.layout.addWidget(knob.createWidget(), self.row, 0)

		options = {
			'callback': 'removeUnselected',
		}
		knob = knobs.PythonButton('Remove Unselected', options=options)
		knob.parent = self
		self.layout.addWidget(knob.createWidget(), self.row, 1)

		options = {
			'callback': 'removeAll',
		}
		knob = knobs.PythonButton('Remove All', options=options)
		knob.parent = self
		self.layout.addWidget(knob.createWidget(), self.row, 2)
		self.row += 1

		self.widget.setLayout(self.layout)
		self.widget.setStyleSheet("#dropButton { margin-bottom: 16px; padding: 32px; background: #3a3a3a; border: 2px dashed #999; font-size: 16px}")

	def addFiles(self, files=None):
		if not files:
			files = self.browseKnob.getValue()

		existingFiles = set([row[0] for row in self.fileList.getValue()])
		# items expects an array of arrays
		# also remove dupes
		files = [[f] for f in files if f not in existingFiles]
		sortedFiles = files + self.fileList.getValue()
		sortedFiles.sort()
		self.fileList.removeAll()
		self.fileList.addItems(sortedFiles)

	def removeRow(self, modelIndex):
		self.fileList.removeRow(modelIndex.row())

	def removeSelected(self):
		self.fileList.removeSelected()

	def removeUnselected(self):
		self.fileList.removeUnselected()

	def removeAll(self):
		self.browseKnob.setValue(None)
		self.fileList.removeAll()

	def getValue(self):
		return [f[0] for f in self.fileList.getValue()]

	def updateWidget(self):
		pass

	def widgetEdited(self):
		pass
