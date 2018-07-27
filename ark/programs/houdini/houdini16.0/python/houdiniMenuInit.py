import os
os.environ['ARK_CURRENT_APP'] = 'houdini'

import sys
sys.path.append('C:/Python27/Lib/site-packages/')

import hou

import arkInit
arkInit.init()

from translators import QtGui
import DropdownMenu
import pyqt_houdini

dialog = None

def initMenu():
	global dialog
	global app
	if not dialog:
		app = QtGui.QApplication.instance()
		if app is None:
			app = QtGui.QApplication(['houdini'])

		menu = DropdownMenu.gui()

		menu.addCommand(name='Studio/IFD Submitter',
			python='import IFDSubmitter;IFDSubmitter.launch()',
			imports='IFDSubmitter')

		menu.addCommand(name='Studio/Shot Builder',
			imports='shotBuilder',
			python='import shotBuilder;shotBuilder.launch()')

		menu.addCommand(name='Studio/Publish Manager',
			imports='publishManager',
			python='import publishManager;publishManager.launch()')

		menu.addCommand(name='Studio/Playblast Tool',
			imports='ark/tools/playblastTool/playblastTool.py',
			python='import playblastTool; playblastTool.launch()')

		# menu.addCommand(name='AutoSave/Start',
		# 	imports='ark/programs/houdini/houdini13.0/python/autoSave/autoSave.py',
		# 	python='import autoSave; autoSave.run()')

		# menu.addCommand(name='AutoSave/End',
		# 	imports='ark/tools/autoSave/autoSave.py',
		# 	python='import autoSave; autoSave.stop()')

		# menu.addCommand(name='Refresh',
		# 	imports='programs/houdini/houdini13.0/python/houdiniMenuInit.py',
		# 	python='import houdiniMenuInit; houdiniMenuInit.launchMenu()')

		# menu.addCommand(name='Utilities/Repath',
		# 	imports='ark/tools/repath/repath.py',
		# 	python='repath.main()')

	pyqt_houdini.exec_(app, dialog)


def launchMenu():
	if( dialog== None):
		initMenu()

	# global dialog
	DropdownMenu.showMenu()
