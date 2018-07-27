from knobs import Knob
from translators import QtGui, QtCore
from translators import Events
import cOS

class OpenFile(Knob):

	defaultOptions = {
		'label': 'Select a file',
		'directory': '',
		'extension': 'Any file (*.*)',
		'buttonText': '...'
	}
	def __init__(self, name, value=None, options={}):
		Events.__init__(self)
		super(OpenFile, self).__init__(name, value, options)

	def setValue(self, value, emit=True):
		if value and value != self.value:
			try:
				self.value = cOS.normalizePath(value)
				self.updateWidgetValue()
				if emit:
					self.emit('changed', self.value)
			except:
				self.value = ''
		else:
			return

	def createWidget(self):
		self.widget = QtGui.QWidget()
		hbox = QtGui.QHBoxLayout()

		self.editBox = QtGui.QLineEdit(str(self.value))
		hbox.addWidget(self.editBox)
		self.browseButton = QtGui.QPushButton(self.options['buttonText'])
		self.browseButton.setObjectName('inline')
		self.browseButton.setAutoDefault(False)
		self.browseButton.setMaximumWidth(len(self.options['buttonText']) * 10)
		hbox.addWidget(self.browseButton)
		hbox.setAlignment(QtCore.Qt.AlignTop)
		hbox.setContentsMargins(0,0,0,0)
		self.widget.setLayout(hbox)
		self.browseButton.clicked.connect(self.browseFile)

	def setValueFromWidget(self):
		self.setValue(self.editBox.text(), emit = False)

	def browseFile(self):
		filename = QtGui.QFileDialog.getOpenFileName(
			self.widget,
			self.options['label'],
			self.options['directory'],
			self.options['extension'])
		if filename[0]:
			self.editBox.setText(filename[0])
			self.widgetEdited()

	def getWidgets(self):
		return [self.editBox, self.browseButton]

	def updateWidgetValue(self):
		if not self.widget:
			return

		self.editBox.setText(self.value)


class SaveFile(OpenFile):
	def browseFile(self):
		filename = QtGui.QFileDialog.getSaveFileName(
			self.widget,
			self.options['label'],
			self.options['directory'],
			self.options['extension'])
		if filename[0]:
			self.editBox.setText(filename[0])
			self.widgetEdited()

class Directory(OpenFile):
	def browseFile(self):
		directory = QtGui.QFileDialog.getExistingDirectory(
			self.widget,
			self.options['label'],
			self.getValue())
		if directory:
			self.editBox.setText(directory)
			self.widgetEdited()

	def setValue(self, value, emit=True):
		if value and value != self.value:
			try:
				self.value = cOS.normalizeDir(value)
				self.updateWidgetValue()
				if emit:
					self.emit('changed', self.value)
			except:
				self.value = ''
		else:
			return


class AssetPicker(Knob):
	useFullRow = True
	isLayout = True
	defaultOptions = {
		'name': 'project\nshot\n\nasset\nversion',
		'options': []
	}
	def init(self):
		super(AssetPicker, self).init()
		from caretaker import Caretaker
		self.caretaker = Caretaker()
		from database import Database
		self.database = Database(keepTrying=False)

		self.database.connect()
		self.project = ''
		self.projectIDs = []
		self.shot = ''
		self.shotIDs = []
		self.asset = ''
		self.assetIDs = []
		self.version = ''
		self.versionIDs = []

	def createWidget(self):
		self.widget = QtGui.QWidget()

		vBox = QtGui.QGridLayout()
		vBox.setContentsMargins(0, 0, 0, 0)
		vBox.setSpacing(5)

		self.projectWidget = QtGui.QComboBox()
		self.shotWidget = QtGui.QComboBox()
		self.assetWidget = QtGui.QComboBox()
		self.versionWidget = QtGui.QComboBox()
		self.versionWidget.setEditable(True)
		self.versionWidget.setInsertPolicy(QtGui.QComboBox.InsertAtBottom)

		for idx, label in enumerate(['Project', 'Shot', 'Asset', 'Version Name']):
			labelWidget = QtGui.QLabel(label + ':')
			labelWidget.setFixedWidth(120)
			labelWidget.setAlignment(QtCore.Qt.AlignRight)
			vBox.addWidget(labelWidget, idx, 0)

		vBox.addWidget(self.projectWidget, 0, 1)
		vBox.addWidget(self.shotWidget, 1, 1)
		vBox.addWidget(self.assetWidget, 2, 1)
		vBox.addWidget(self.versionWidget, 3, 1)
		vBox.setAlignment(QtCore.Qt.AlignTop)
		self.widget.setLayout(vBox)

		self.projectWidget.currentIndexChanged.connect(self.fillShotWidget)
		self.shotWidget.currentIndexChanged.connect(self.fillAssetWidget)
		self.assetWidget.currentIndexChanged.connect(self.fillVersionWidget)

		# self.projectWidget.currentIndexChanged.connect(self.emitSignal)
		# self.shotWidget.currentIndexChanged.connect(self.emitSignal)
		# self.assetWidget.currentIndexChanged.connect(self.emitSignal)
		self.versionWidget.currentIndexChanged.connect(self.emitSignal)

		self.fillProjectWidget()

	def emitSignal(self):
		self.emit('changed')

	def hasProject(self):
		return len(self.projectIDs) > self.projectWidget.currentIndex() and self.projectWidget.currentIndex() >= 0

	def hasShot(self):
		return len(self.shotIDs) > self.shotWidget.currentIndex() and self.shotWidget.currentIndex() >= 0

	def hasAsset(self):
		return len(self.assetIDs) > self.assetWidget.currentIndex() and self.assetWidget.currentIndex() >= 0

	def hasVersion(self):
		return len(self.versionIDs) > self.versionWidget.currentIndex() and self.versionWidget.currentIndex() >= 0

	# gets all data from widgets
	def setValueFromWidget(self):
		self.project = self.projectWidget.currentText()
		if self.hasProject():
			self.projectID = self.projectIDs[self.projectWidget.currentIndex()]
			self.shot = self.shotWidget.currentText()
		if self.hasShot():
			self.shotID = self.shotIDs[self.shotWidget.currentIndex()]
			self.asset = self.assetWidget.currentText()
		if self.hasAsset():
			self.assetID = self.assetIDs[self.assetWidget.currentIndex()]
			self.version = self.versionWidget.currentText()
		if self.hasVersion():
			self.versionID = self.versionIDs[self.versionWidget.currentIndex()]

	def updateWidgetValue(self):
		pass

	def loadFromDatabase(self, widget, query):
		widget.clear()
		if not query:
			return []
		for i, option in enumerate(query):
			widget.addItem(option['name'], i)
		widget.setCurrentIndex(0)
		return [option['_id'] for i, option in enumerate(query)]

	def fillProjectWidget(self):
		self.projectWidget.clear()
		projectQuery = self.database.find('project')\
			.sort('name')\
			.execute()
		self.projectIDs = self.loadFromDatabase(self.projectWidget, projectQuery)
		self.projectWidget.currentIndexChanged.emit(0)

	def fillShotWidget(self):
		self.setValueFromWidget()
		if not self.hasProject():
			self.shotWidget.clear()
			return
		shotQuery = self.database.find('shot')\
			.where('project','is',self.projectID)\
			.sort('name')\
			.execute()
		self.shotIDs = self.loadFromDatabase(self.shotWidget, shotQuery)
		self.shotWidget.currentIndexChanged.emit(0)

	def fillAssetWidget(self):
		self.setValueFromWidget()
		if not self.hasShot():
			self.assetWidget.clear()
			return
		assetQuery = self.database.find('asset')\
			.where('project','is',self.projectID)\
			.where('shot','is',self.shotID)\
			.sort('name')\
			.execute()
		self.assetIDs = self.loadFromDatabase(self.assetWidget, assetQuery)
		self.assetWidget.currentIndexChanged.emit(0)

	def fillVersionWidget(self):
		self.setValueFromWidget()
		if not self.hasAsset():
			self.versionWidget.clear()
			return
		versionQuery = self.database.find('version')\
			.where('asset','is',self.assetID)\
			.where('project','is',self.projectID)\
			.where('shot','is',self.shotID)\
			.sort('name')\
			.execute()
		uniqueVersions = []
		for version in versionQuery:
			if not any(v['name'] == version['name'] for v in uniqueVersions):
				uniqueVersions.append({'name': version['name'], '_id': version['_id']})
		uniqueVersions.sort(key = lambda x: x['name'])
		self.versionIDs = self.loadFromDatabase(self.versionWidget, uniqueVersions)

	def fillFromPath(self, path):
		def _fillFromPath():
			nameFromPath = self.caretaker.getProjectFromPath(path)
			if not nameFromPath:
				return False
			fillID = self.projectWidget.findText(nameFromPath['name'])
			if fillID < 0:
				return False
			self.projectWidget.setCurrentIndex(fillID)

			nameFromPath = self.caretaker.getShotFromPath(path)
			if not nameFromPath:
				return False
			fillID = self.shotWidget.findText(nameFromPath['name'])
			if fillID < 0:
				return False
			self.shotWidget.setCurrentIndex(fillID)

			nameFromPath = self.caretaker.getAssetFromPath(path)
			if not nameFromPath:
				return False
			fillID = self.assetWidget.findText(nameFromPath['name'])
			if fillID < 0:
				return False
			self.assetWidget.setCurrentIndex(fillID)
			return True

		_fillFromPath()
		self.setValueFromWidget()

	def getProject(self):
		return self.project

	def getShot(self):
		return self.shot

	def getAsset(self):
		return self.asset

	def getVersion(self):
		return self.version
