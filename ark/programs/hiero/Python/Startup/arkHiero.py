# This example shows how you can add custom keyboard shortcuts to Hiero.
# If you wish for this code to be run on startup, copy it to your <HIERO_PATH>/Startup directory.

import os
import sys

os.environ['ARK_CURRENT_APP'] = 'hiero'
os.environ['ARK_NS'] = 'True'

print 'Running arkHiero.py'

import hiero.ui
import hiero.core

arkRoot = os.environ.get('ARK_ROOT')
print 'arkInit path:', arkRoot + 'ark/setup/'
sys.path.append(arkRoot + 'ark/setup/')

import arkInit
arkInit.init()

import settingsManager
globalSettings = settingsManager.globalSettings()

import translators
translator = translators.getCurrent()

from translators import QtGui



# hiero.core.addPluginPath('C:/Python26/Lib/site-packages')

#-----------------------------------------------------------------------------
# __init__.py
# By Grant Miller (blented@gmail.com)
# v 1.0
# Created On: 08/10/2012
# Modified On: 08/10/2012
# tested using Nuke X 6.3v4 & 3dsMax 2012
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Required Files:
#
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Description:
# Sets up system paths for Ingenuity Engine tools
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Revision History:
#
# v 1.00 Initial version
#
#-----------------------------------------------------------------------------

# Ingenuity Plugin Paths
#-----------------------------------------------------------------------------
pluginPaths = [
	globalSettings.ARK_ROOT + 'Lib',
	globalSettings.HIERO_TOOLS_ROOT + 'Python/tools'
]

for path in pluginPaths:
	hiero.core.addPluginPath(path)
	hiero.core.find_plugins.loadPluginsFromFolder(path)

# import ieRenameShots
import hieroUtils
import importComps
import shotImporter
# import customTranscode
# customTranscode.setup()

def findAndSetShortcut(search, shortcut):
	item = hiero.ui.findMenuAction(search)
	if item:
		item.setShortcut(QtGui.QKeySequence(shortcut))


def addIEMenuItem(name, function, shortcut=None):
	global arkMenu
	renameAction = QtGui.QAction(name, arkMenu)
	renameAction.triggered.connect(function)
	if shortcut:
		renameAction.setShortcut(shortcut)
	arkMenu.addAction(renameAction)




mainMenu = hiero.ui.menuBar()
# Ingenuity menu entry
arkMenu = mainMenu.addMenu('Ingenuity')

# addIEMenuItem('Rename Shots', ieRenameShots.showDialog, 'Ctrl+Shift+R')
# addIEMenuItem('Test', hieroUtils.test, 'ctrl+shift+t')
addIEMenuItem('Import Comps', importComps.launch)
addIEMenuItem('Shot Importer', shotImporter.launch, 'ctrl+alt+i')
addIEMenuItem('Fix Multi-Shots', hieroUtils.fixMultiShots)
addIEMenuItem('Create Caretaker Shots', hieroUtils.createCaretakerShots)
addIEMenuItem('Export CDL for Visible Track Items', hieroUtils.exportCDLPerShot, 'ctrl+shift+l')
addIEMenuItem('Export LUT for Visible Track Items', hieroUtils.exportLUTFromEDL, 'ctrl+shift+u')

findAndSetShortcut('Show Metadata', 'Alt+M')
findAndSetShortcut('foundry.project.importSequence', 'Alt+I')
findAndSetShortcut('foundry.project.openInSpreadsheet', 'S')
