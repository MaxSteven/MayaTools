import os
import hou
import sys

if hou.applicationName() in ['hbatch', 'hython']:
	os.environ['ARK_CURRENT_APP'] = 'houdini_cl'
else:
	os.environ['ARK_CURRENT_APP'] = 'houdini'

# necessary for importing the ftrack widgets
sys.path.append("C:/Python27/Lib/site-packages")

import arkInit
arkInit.init()

import settingsManager
globalSettings = settingsManager.globalSettings()

version = hou.applicationVersion()
versionString = 'houdini{}.{}'.format(version[0], version[1])
sys.path.append(globalSettings.HOUDINI_TOOLS_ROOT + versionString + '/python')

try:
	import urllib3
	urllib3.disable_warnings()
	import ftrack
	from ftrack_connect_houdini.connector import Connector
except:
	print 'Ftrack not installed'

try:
	ftrack.setup()
except:
	pass

# wrappers around initHoudini functions, called from MainMenuCommon.xml and initHoudini
def FtrackDialogs(panel_id):
	import initHoudini
	return initHoudini.FtrackDialogs(panel_id)

def showDialog(name):
	import initHoudini
	return initHoudini.showDialog(name)

print 'Completed pythonrc'


