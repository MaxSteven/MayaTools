
# Standard modules
##################################################

# Our modules
##################################################
import arkInit
arkInit.init()
import cOS

import settingsManager
globalSettings = settingsManager.globalSettings()

import translators
translator = translators.getCurrent()

class PathInfo(object):
	'''
	Gets task information from the translator
	and caretaker
	'''

	def __init__(self, caretaker, path):
		self.version = cOS.getVersion(path)

		# info from Caretaker
		self.sequence = caretaker.getSequenceFromPath(path)
		self.projectInfo = caretaker.getProjectFromPath(path)
		self.shotNumber = caretaker.getShotNameFromPath(path)

	def __str__(self):
		printString = 'Version: ' + self.version
		printString += '\nSequence: ' + self.sequence
		printString += '\nProject Info: '+ self.projectInfo
		printString += '\nshotNumber: ' + self.shotNumber

		return printString
