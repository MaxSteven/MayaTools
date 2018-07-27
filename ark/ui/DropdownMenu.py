'''
[ ] - add clicks to key commands, rename
[M] - folder-based dropdown from commands
[M] - arbitraty python execution in program scope
'''

import sys

import arkInit
arkInit.init()

import settingsManager
globalSettings = settingsManager.globalSettings()
import arkUtil
import translators
translator = translators.getCurrent()

from translators import QtGui
import traceback

# app = QtGui.QApplication(sys.argv)

dropdownMenu = False

class DropDownDialog(QtGui.QMenu):

	def __init__(self, parent=None, **kwargs):
		super(DropDownDialog, self).__init__(parent)
		self.initUI()

	def initUI(self):

		self.actions = {'_commands': [], '_menu': self}
		self.namespace = globals()

	# def launch(self):
	# 	print "Launching"
	# 	self.move(QtGui.QCursor.pos().x(), QtGui.QCursor.pos().y())
	# 	global app
	# 	app.exec_()
	# 	# self.show()


	def addCommand(self, name, imports, python=None, shortcut=None):
		try:
			path = name.split('/')
			fileDict = self.findSubdict(self.actions, path)
			fileDict['_commands'].append(path[-1])

			if imports:
				imports = arkUtil.ensureArray(imports)

				for i in imports:
					parentDir = '/'.join(i.split('/')[:-1])
					parentDir = globalSettings.ARK_ROOT + 'ark/' + parentDir
					sys.path.append(parentDir)
					name = i.split('/')[-1].split('.')[0]

					if not python:
						python = name + '.main()'

					self.namespace[name] = __import__(name)

			func = lambda: self.executePython(python)
			action = fileDict['_menu'].addAction(self.tr(path[-1]), func)

			if shortcut and translator.options.get('hasKeyCommands'):
				action.setShortcut(QtGui.QKeySequence(self.tr(shortcut)))
		except Exception as err:
			print 'ERROR:', name, imports
			print err
			print traceback.format_exc()

	def findSubdict(self, dictionary, path):
		if len(path) > 1:
			if path[0] not in dictionary.keys():
				dictionary[path[0]] = {}
				dictionary[path[0]]['_commands'] = []
				dictionary[path[0]]['_menu'] = QtGui.QMenu(path[0])
				dictionary['_menu'].addMenu(dictionary[path[0]]['_menu'])
			return self.findSubdict(dictionary[path[0]], path[1:])
		return dictionary

	def executePython(self, python):
		try:
			exec python in self.namespace
		except:
			self.showtraceback()

	def showtraceback(self):
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

def launch(*args, **kwargs):
	global dropdownMenu
	dialogMenu = translator.launch(DropDownDialog, *args, **kwargs)
	return dialogMenu

def gui(*args, **kwargs):
	global dropdownMenu
	# fix: this is so hax
	dropdownMenu = translator.launch(DropDownDialog, *args, **kwargs)
	dropdownMenu.hide()
	return dropdownMenu

def showMenu():
	global dropdownMenu
	if not dropdownMenu:
		raise Exception('Please call gui() first')
	dropdownMenu.move(QtGui.QCursor.pos().x(), QtGui.QCursor.pos().y())
	dropdownMenu.show()

if __name__ == '__main__':
	launch()

