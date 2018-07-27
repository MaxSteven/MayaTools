
# Standard modules
##################################################

# Our modules
##################################################
import arkInit
arkInit.init()
# import sys
import cOS

import settingsManager
globalSettings = settingsManager.globalSettings()

import translators
translator = translators.getCurrent()

class TaskInfo(object):
	'''
	Gets task information from the translator
	and caretaker
	'''

	def __init__(self, caretaker):
		self.filename = translator.getFilename()
		self.width = translator.getRenderProperty('width')
		self.height = translator.getRenderProperty('height')
		self.fps = translator.getFPS()
		self.version = cOS.getVersion(self.filename)

		# info from Caretaker
		self.sequence = caretaker.getSequenceFromPath(self.filename)

		self.shotNumber = caretaker.getShotNameFromPath(self.filename)

		self.startFrame = translator.getAnimationRange()['startFrame']
		self.endFrame = translator.getAnimationRange()['endFrame']

		self.projectInfo = caretaker.getProjectFromPath(self.filename)

		self.assetRoot = False
		if self.projectInfo:
			self.projectRoot = globalSettings.SHARED_ROOT + \
				self.projectInfo['folderName'] + '/'

			self.versionPadding = caretaker.getVersionPadding(
				self.projectInfo)
			self.versionString = caretaker.getVersionString(
				self.projectInfo, self.version)

			self.framePadding = caretaker.getFramePadding(
				self.projectInfo)
			self.framePaddingString = caretaker.getFramePaddingString(
				self.projectInfo)

			if 'workspaces' in self.filename.lower():
				self.assetRoot = self.projectRoot + 'Workspaces/' + self.sequence + '/' + self.shotNumber + '/'
			elif 'project_assets' in self.filename.lower():
				parts = self.filename.split('/')
				assetName = parts[3]
				self.assetRoot = self.projectRoot + 'Project_Assets/' + assetName + '/'

		if not self.assetRoot:
			pathInfo = cOS.getPathInfo(self.filename)
			self.assetRoot = pathInfo['dirname']


	def __str__(self):
		printString = 'Filename: ' + self.filename
		printString += '\nWidth: ' + str(self.width)
		printString += '\nHeight: ' + str(self.height)
		printString += '\nFPS: ' + str(self.fps)
		printString += '\nVersion: ' + str(self.version)
		printString += '\nSequence: ' + str(self.sequence)
		printString += '\nShot Number: ' + str(self.shotNumber)
		printString += '\nStart Frame: ' + str(self.startFrame)
		printString += '\nEnd Frame: ' + str(self.endFrame)
		printString += '\nProject Info: ' + str(self.projectInfo)
		printString += '\nProject Root: ' + self.projectRoot
		printString += '\nVersion Padding: ' + str(self.versionPadding)
		printString += '\nFrame Padding: ' + str(self.framePadding)
		printString += '\nAsset Root: ' + str(self.assetRoot)

		return printString


def main():
	import caretaker
	caretaker = caretaker.Caretaker()
	x = TaskInfo(caretaker)
	print x

if __name__ == '__main__':
	main()
