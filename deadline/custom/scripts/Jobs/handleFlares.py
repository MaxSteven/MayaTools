import sys

import arkInit
arkInit.init()

import settingsManager
globalSettings = settingsManager.globalSettings()
import nuke

from nukeScript import NukeScript

class flareHandler(NukeScript):

	def interpretInstructions(self):
		nuke.scriptOpen(self.getOption('tempFile'))
		with nuke.root():
			for item in nuke.allNodes():
				if item.Class() == 'OpticalFlares':
					nuke.delete(item)
		nuke.scriptSave(self.getOption('tempFile'))
		nuke.scriptExit()

if __name__ == '__main__':
	flareHandler = flareHandler()
	flareHandler.parseArgs(sys.argv)
	flareHandler.interpretInstructions()