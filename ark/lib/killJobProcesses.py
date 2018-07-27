import arkInit
arkInit.init()

import settingsManager
globalSettings = settingsManager.globalSettings()

import cOS
import os

def killJobProcesses(nodesOnly=True):
	'''
	Kills all other processes currently on
	the render node.
	'''
	if not nodesOnly or not globalSettings.IS_NODE:
		executableNames = [program['executableName'] for program in globalSettings.PROGRAMS if program['killOnArtistWorkstation']]
	else:
		executableNames = [program['executableName'] for program in globalSettings.PROGRAMS]
	# this does much better
	print 'Killing processes:'
	for name in executableNames:
		if cOS.isWindows():
			command = 'taskkill /F /FI "imagename eq %s*"' % name
		elif cOS.isLinux():
			command = 'killall -r %s -KILL' % name

		print command
		os.system(command)
