
def init():
	import arkInit
	arkInit.init()

	import settingsManager
	globalSettings = settingsManager.globalSettings()

	# set environment to nuke_cl
	import os
	os.environ['ARK_CURRENT_APP'] = 'nuke_cl'

	# add nuke's python lib to the path
	import sys
	sys.path.append(globalSettings.NUKE_ROOT + 'lib/site-packages')

	# import nuke to set up the paths
	import nuke
