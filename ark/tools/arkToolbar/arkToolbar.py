# Name: Ark Toolbar
# Author: Shobhit Khinvasara
# Date: 04/03/2017
import sys

import arkInit
arkInit.init()

import settingsManager
globalSettings = settingsManager.globalSettings()


import os
import json
import cOS
import re
import shutil
currentApp =  os.environ.get('ARK_CURRENT_APP')

from translators import QtGui
toolSettings = {}

toolsConfigFile = os.path.join(
	globalSettings.USER_ROOT,
	'config/tools.json'
)

if os.path.isfile(toolsConfigFile):
	with open(toolsConfigFile) as f:
		contents = f.read()

	toolSettings = json.loads(contents)
else:
	try:
		# temporary fallback until caretaker gone
		from caretaker import Caretaker
		caretaker = Caretaker()
		databaseToolSettings = settingsManager.databaseSettings(
			'arkToolbar_favoriteTools_%s' % currentApp,
			caretaker.getUserInfo().get('username'))
		toolSettings = databaseToolSettings.getAll().get('settings')
	except:
		print 'Could not get username, are you logged in to hub?'
	cOS.makeDir(os.path.dirname(toolsConfigFile))
	with open(toolsConfigFile, 'w') as outfile:
		json.dump(toolSettings, outfile)


from translators import QtCore

import arkFTrack
pm = arkFTrack.getPM()
import translators
translator = translators.getCurrent()

import traceback

import baseWidget
import arkUtil

MAX_FAVORITES = 10

class QCloseMessageBox(QtGui.QMessageBox):
	stateChanged  = QtCore.Signal()

	def closeEvent(self, event):
		self.stateChanged.emit()

class ArkToolbar(baseWidget.BaseWidget):
	defaultOptions = {
			'title': 'Ark Toolbar',
			'align': 'top',

			'knobs' : [
				{
					'name': 'tools',
					'width': 30,
					'height': 30,
					'dataType': 'PythonButton',
					'iconPath': '%sark/ui/icons/ark.png' % globalSettings.ARK_ROOT,
					'callback': 'launchSearchTools'
				},
			]
		}

	standardKnobs = {}
	favoriteKnobs = {}
	currentTools = {}
	commands = {}
	namespace = globals()
	toolsDialog = False
	favoritesDialog = False

	def launchSearchTools(self):
		undocked = os.getenv('ARKTOOLBAR_UNDOCKED')
		if self.favoritesDialog:
			self.favoritesDialog.close()
		if self.toolsDialog is False:
			self.toolsDialog = ArkToolbar.SearchTools(parentInstance=self, parent=(None if undocked else translator.getQTApp()))
		try:
			self.toolsDialog.show()
		except:
			self.diatoolsDialoglog =  ArkToolbar.SearchTools(parentInstance=self, parent=(None if undocked else translator.getQTApp()))
			self.toolsDialog.show()

	def launchFavoritesTools(self, callerKnob):
		if self.favoritesDialog:
			self.favoritesDialog.close()
		undocked = os.getenv('ARKTOOLBAR_UNDOCKED')
		self.favoritesDialog = ArkToolbar.FavoriteTools(parentInstance=self, callerKnob=callerKnob, parent=(None if undocked else translator.getQTApp()))
		self.favoritesDialog.show()
		try:
			self.toolsDialog.hide()
		except:
			pass

	def init(self):
		if toolSettings and toolSettings.get('favorites') == None:
			toolSettings['favorites'] = {}

		self.currentTools = {}
		self.setupTools()
		self.timer = QtCore.QTimer(parent=self)
		self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
		self.msgBox = None
		self.activeMsgBox = False

	def postShow(self):
		standardTools = sorted((tool for tool in self.currentTools.values() if tool.get('order')), key=lambda tool: tool.get('order'))
		for tool in standardTools:
			options = {
				'name': tool.get('name'),
				'dataType': 'PythonButton',
				'width': 30,
				'height': 30,
				'iconPath': '%sark%s' % (globalSettings.ARK_ROOT, tool.get('iconPath')),
			}
			self.addKnobFromDict(options)
			self.standardKnobs[tool.get('name')] = self.getKnob(tool.get('name'))

		if not toolSettings:
			return

		favorites = toolSettings.get('favorites')
		for i in range(1, MAX_FAVORITES + 1):
			iconPath = None
			if favorites.get(str(i)) != None:
				# try to get icon path
				try:
					iconPath =  '%sark%s' % (globalSettings.ARK_ROOT,
						self.currentTools.get(favorites.get(str(i)).lower()).get('iconPath'))
				except:
					pass
			options = {
				'name': '%i' % (i),
				'dataType': 'PythonButton',
				'width': 30,
				'height': 30,
				'iconPath': iconPath
			}
			self.addKnobFromDict(options)
			self.favoriteKnobs['%i' % (i)] = self.getKnob('%i' % (i))


		for knobName in self.standardKnobs.keys():

			knob = self.standardKnobs.get(knobName)
			knob.widget.clicked.connect(lambda python=self.commands.get(knobName.lower()): self.executePython(python))

		for knobName in self.favoriteKnobs.keys():
			knob = self.favoriteKnobs.get(knobName)
			if self.commands.get(toolSettings.get('favorites').get(knobName)) != None:
				knob.widget.clicked.connect(lambda python=self.commands.get(toolSettings.get('favorites').get(knobName).lower()): self.executePython(python))
			knob.on('rightClicked', lambda callerKnob=knobName: self.launchFavoritesTools(callerKnob))

		# 15min in miliseconds for nuke
		if currentApp == 'nuke':
			self.timer.start(15*60*1000)
			self.timer.setInterval(15*60*1000)

		# 10min in miliseconds for others
		elif currentApp != None:
			self.timer.start(10*60*1000)
			self.timer.setInterval(10*60*1000)

		self.timer.timeout.connect(self.autoSave)

	# A/B/backup/C_d_v0001_xy.0005.nk
	def getHighestBackup(self, root, filename, extension):
		backups = set()
		p = re.compile(filename + '\.(\d{4})\.' + extension)
		for f in cOS.getFolderContents(root, includeFiles=True, includeFolders=False):
			m = p.search(f)
			if m:
				backups.add(int(m.group(1)))
		if len(backups) > 0:
			return sorted(backups)[-1]
		else:
			return 0

	def autoSave(self):
		# A/B/C_d_v0001_xy.nk
		self.filename = translator.getFilename()
		if not self.filename:
			return

		if currentApp == 'nuke':
			# backup 'recent files' list on disk
			shutil.copyfile(globalSettings.USER_ROOT + '.nuke/recent_files', globalSettings.USER_ROOT + '.nuke/.recent_files')
			# backup 'recent files' menu
			import nuke
			recentMenu = nuke.menu('Nuke').findItem('File').findItem('Open Recent Comp')
			recentItems = recentMenu.items()

			pathInfo = cOS.getPathInfo(self.filename)
			writeDir = '{}backup/'.format(pathInfo['dirname'])
			if not os.path.isdir(writeDir):
				os.makedirs(writeDir)
			backup = self.getHighestBackup(writeDir, pathInfo['name'], 'nk') + 1
			self.newFilename = '{}{}.{}.{}'.format(writeDir, pathInfo['name'], '{0:04d}'.format(backup), pathInfo['extension'])
			translator.saveFile(self.newFilename)
			translator.setFilename(self.filename)

			# restore 'recent files' list on disk
			shutil.copyfile(globalSettings.USER_ROOT + '.nuke/.recent_files', globalSettings.USER_ROOT + '.nuke/recent_files')
			os.remove(globalSettings.USER_ROOT + '.nuke/.recent_files')
			# restore 'recent files' menu
			recentMenu.clearMenu()
			for idx, recent in enumerate(recentItems, 1):
				recentMenu.addCommand(re.sub('/', '\/', recent.name()), 'nuke.scriptOpen({})'.format(recent.name()), "#+{}".format(str(idx)))

		else:
			pathInfo = cOS.getPathInfo(self.filename)
			self.newFilename = cOS.getHighestVersionFilePath(pathInfo['dirname'],
																	pathInfo['name'],
																	pathInfo['extension'])

			self.newFilename = cOS.incrementVersion(self.newFilename, initials=pm.getInitials())

			if not self.activeMsgBox and translator.checkSaveState(useHash=False):
				# File dialog text based on the file open in Software
				if not self.filename:
					msgBoxText = 'Save?'

				else:
					msgBoxText =  'Version Up to this: \n' + self.newFilename

				undocked = os.getenv('ARKTOOLBAR_UNDOCKED')
				self.msgBox = QCloseMessageBox(parent=(None if undocked else translator.getQTApp()))
				self.msgBox.setWindowTitle('Version Up?')
				self.msgBox.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
				self.msgBox.setText(msgBoxText)
				self.msgBox.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
				self.msgBox.setWindowModality(QtCore.Qt.NonModal)
				self.msgBox.buttonClicked.connect(self.saveFileClearBox)
				self.msgBox.stateChanged.connect(self.stateChangedEvent)
				self.msgBox.setAttribute(QtCore.Qt.WA_DeleteOnClose)
				self.msgBox.show()

				self.activeMsgBox = True

	def stateChangedEvent(self):
		self.activeMsgBox = False

	def saveFileClearBox(self, button):
		if button.text() in ['OK', '&OK']:
			self.saveFile()
		self.activeMsgBox = False

	def saveFile(self):
		if not self.filename:
			fileDialog = QtGui.QFileDialog()
			fileDialog.setModal(True)
			fileDialog.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
			customFileName = fileDialog.getSaveFileName(self, 'Save as..', None)[0]
			if not customFileName:
				return

			self.newFilename = customFileName

		translator.saveFile(self.newFilename)

	def setupTools(self):
		settings = settingsManager.getSettings('tools')
		tools = settings.get('tools')
		for tool in tools:
			translator.addCommand2(self, tool)
		for tool in self.currentTools.values():
			if not tool.get('imports') is None:
				imports = arkUtil.ensureArray(tool.get('imports'))

				for i in imports:
					parentDir = '/'.join(i.split('/')[:-1])
					parentDir = globalSettings.ARK_ROOT + 'ark/' + parentDir
					sys.path.append(parentDir)
					name = i.split('/')[-1].split('.')[0]

					self.namespace[name] = __import__(name)
			if tool.get('python') is None or tool.get('python') is '':
				raise Exception("Python option must exist and cannot be an empty string")
			self.commands[tool.get('name').lower()] = tool.get('python')


	def runTool(self):
		selectedTool = self.commands.get(self.getKnob('tools').getValue().lower())
		self.executePython(selectedTool)

	def showTraceback(self):
		try:
			type, value, tb = sys.exc_info()
			sys.last_type = type
			sys.last_value = value
			sys.last_traceback = tb
			tblist = traceback.extract_tb(tb)
			del tblist[:1]
			list = traceback.format_list(tblist)
			if list:
				list.insert(0, 'Traceback (most recent call last):\n')
			list[len(list):] = traceback.format_exception_only(type, value)
		finally:
			tblist = tb = None

		print ''.join(list)

	def executePython(self, python):
		try:
			exec python in self.namespace
		except:
			self.showTraceback()

	class SearchTools(baseWidget.BaseWidget):
		defaultOptions = {
			'title': 'Tool Search',
			'align': 'top',

			'knobs' : [
				{
					'name': 'tools',
					'dataType': 'searchList',
				},
			]
		}


		def __init__(self, parent, parentInstance, options={}, *args, **kwargs):
			self.parentInstance = parentInstance
			super(ArkToolbar.SearchTools, self).__init__(parent, options={}, *args, **kwargs)

		def postShow(self):
			self.getKnob('tools').on('doubleClicked', self.runTool)
			# Because postShow gets called multiple times
			tools = [tool.get('name') for tool in self.parentInstance.currentTools.values()]
			tools.sort()
			self.getKnob('tools').addItems(tools)

		def runTool(self):
			selectedTool = self.parentInstance.commands.get(self.getKnob('tools').getValue().lower())
			self.parentInstance.executePython(selectedTool)
			self.hide()

	class FavoriteTools(baseWidget.BaseWidget):
		defaultOptions = {
			'title': 'Favorite Search',
			'align': 'top',

			'knobs' : [
				{
					'name': 'tools',
					'dataType': 'searchList',
					'hasNone': True,
				},
			]
		}


		def __init__(self, parent, parentInstance, callerKnob, options={}, *args, **kwargs):
			self.callerKnob = callerKnob
			self.parentInstance = parentInstance
			super(ArkToolbar.FavoriteTools, self).__init__(parent, options={}, *args, **kwargs)

		def postShow(self):
			self.getKnob('tools').on('doubleClicked', self.addFavoriteTool)
			# Because postShow gets called multiple times
			tools = [tool.get('name') for tool in self.parentInstance.currentTools.values()]
			tools.sort()
			self.getKnob('tools').addItems(tools)

		def addFavoriteTool(self):
			selectedTool = self.getKnob('tools').getValue().lower()
			favorites = toolSettings.get('favorites')

			if favorites == None:
				favorites= {}
			if selectedTool == 'none':
				favorites[self.callerKnob] = None
			else:
				favorites[self.callerKnob] = selectedTool
			toolSettings['favorites'] = favorites
			self.saveFavoriteTools()

			try:
				self.parentInstance.getKnob(self.callerKnob).widget.clicked.disconnect()
				self.parentInstance.getKnob(self.callerKnob).widget.setText(self.parentInstance.getKnob(self.callerKnob).name)
			except:
				pass

			iconPath = None
			if selectedTool != 'none':
				self.parentInstance.getKnob(self.callerKnob).widget.clicked.connect(lambda python=self.parentInstance.commands.get(selectedTool): self.parentInstance.executePython(python))
				iconPath = '%sark%s' % (globalSettings.ARK_ROOT, self.parentInstance.currentTools.get(selectedTool).get('iconPath'))

			self.parentInstance.getKnob(self.callerKnob).setIcon(iconPath)

			self.close()

		def saveFavoriteTools(self):
			cOS.makeDir(os.path.dirname(toolsConfigFile))

			with open(toolsConfigFile, 'w') as outfile:
				json.dump(toolSettings, outfile)

			print 'Tool settings saved to {}'.format(toolsConfigFile)

def gui():
	return ArkToolbar()

def launch(*args):
	translator.launch(ArkToolbar, docked=(currentApp !='maya' or not os.getenv('ARKTOOLBAR_UNDOCKED')))

if __name__=='__main__':
	launch()



