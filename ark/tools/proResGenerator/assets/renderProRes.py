import sys
# import os
# import glob
import re
# import json
# import time

import arkInit
arkInit.init()
# import ieOS
import cOS

# import arkUtil
import settingsManager
globalSettings = settingsManager.globalSettings()
import translators
translator = translators.getCurrent()
import nuke
import arkNuke
import pathManager

from nukeScript import NukeScript

class proResRenderer(NukeScript):
	
	def render(self):

		# Dictionary for setting color space
		colorspaceDictionary = {
			'linear' : 1,
			'sRGB' : 2,
			'rec709' : 3,
			'Cineon' : 4,
			'Gamma1.8' : 5,
			'Gamme2.2' : 6,
			'Gamma2.4' : 7,
			'Panalog' : 8,
			'REDLog' : 9,
			'ViperLog' : 10,
			'AlexaV3LogC' : 11,
			'PLogLin' : 12,
			'SLog' : 13,
			'Slog1' : 14,
			'SLog2' : 15,
			'SLog3' : 16,
			'CLog' : 17,
			'Protune' : 18,
			'REDSpace' : 19
		}

		# Hold onto our shot info
		movFile = self.getOption('movFile')
		folderPath = self.getOption('directory')
		colorSpace = self.getOption('colorSpace')
		proResType = self.getOption('proResType')
		exportDir = self.getOption('exportDir')
		channels = self.getOption('channels')
		fps = self.getOption('fps')

		# Find out which pro-res script to load
		proResOptions = ['Apple ProRes 442','Apple ProRes 442 HQ','Apple ProRes 442 LT','Apple ProRes 442 Proxy','Apple ProRes 4444']

		if proResType not in proResOptions:
			print 'ERROR: Invalid Codec Given'
			return

		if proResType == 'Apple ProRes 442':
			nuke.scriptOpen(os.path.join(globalSettings.SYSTEM_ROOT, 'ie/ark/tools/proResGenerator/assets/proresGenBase_v0001_bpg.nk'))
			translator.setSceneData('codec', 'mov64')
			nuke.scriptSave(os.path.join(globalSettings.SYSTEM_ROOT, 'ie/ark/tools/proResGenerator/assets/proresGenBase_v0001_bpg.nk'))

		elif proResType == 'Apple ProRes 442 HQ':
			nuke.scriptOpen(os.path.join(globalSettings.SYSTEM_ROOT, 'ie/ark/tools/proResGenerator/assets/proresGenHQ_v0001_bpg.nk'))
			translator.setSceneData('codec', 'mov64')
			nuke.scriptSave(os.path.join(globalSettings.SYSTEM_ROOT, 'ie/ark/tools/proResGenerator/assets/proresGenHQ_v0001_bpg.nk'))

		elif proResType == 'Apple ProRes 442 LT':
			nuke.scriptOpen(os.path.join(globalSettings.SYSTEM_ROOT, 'ie/ark/tools/proResGenerator/assets/proresGenLT_v0001_bpg.nk'))
			translator.setSceneData('codec', 'mov64')
			nuke.scriptSave(os.path.join(globalSettings.SYSTEM_ROOT, 'ie/ark/tools/proResGenerator/assets/proresGenLT_v0001_bpg.nk'))

		elif proResType == 'Apple ProRes 442 Proxy':
			nuke.scriptOpen(os.path.join(globalSettings.SYSTEM_ROOT, 'ie/ark/tools/proResGenerator/assets/proresGenProxy_v0001_bpg.nk'))
			translator.setSceneData('codec', 'mov64')
			nuke.scriptSave(os.path.join(globalSettings.SYSTEM_ROOT, 'ie/ark/tools/proResGenerator/assets/proresGenProxy_v0001_bpg.nk'))

		elif proResType == 'Apple ProRes 4444':
			nuke.scriptOpen(os.path.join(globalSettings.SYSTEM_ROOT, 'ie/ark/tools/proResGenerator/assets/proresGenFour_v0001_bpg.nk'))
			translator.setSceneData('codec', 'mov64')
			nuke.scriptSave(os.path.join(globalSettings.SYSTEM_ROOT, 'ie/ark/tools/proResGenerator/assets/proresGenFour_v0001_bpg.nk'))

		if folderPath != '' and movFile != '':
			print 'ERROR: Cannot import both and mov and a squence'
			return

		if folderPath != '':
			# Get folder contents
			files = os.listdir(folderPath)
			files.sort()

			firstfile = files[0]
			lastfile = files[-1]

			if not cOS.isValidSequence(firstfile):
				print 'ERROR: This is not a valid sequence'
				return
			
			firstframe = int(cOS.getFrameNumber(firstfile))
			lastframe = int(cOS.getFrameNumber(lastfile))

			filename = cOS.getSequenceBaseName(firstfile)
			extension = cOS.getExtension(firstfile)

			padding = cOS.getPadding(firstfile)
			padding = '%0' + str(padding) + 'd'

			if extension != 'jpg' and extension != 'png' and extension != 'dpx':
				print 'ERROR: Please submit a png or dpx sequence'
				return

			# Get nuke nodes
			writer = nuke.toNode( 'Write1' )
			reader = nuke.toNode( 'Read1' )

			reader['file'].fromUserText(folderPath + filename + '.' + padding + '.' + extension + ' ' + str(firstframe) + '-' + str(lastframe))

			nuke.Root()['first_frame'].setValue(firstframe)
			nuke.Root()['last_frame'].setValue(lastframe)

			outputPath = exportDir + filename + '.mov'
			writer['file'].fromUserText(outputPath)
			writer['colorspace'].setValue(colorspaceDictionary[colorSpace])
			writer['channels'].setValue(channels)

			nuke.execute( 'Write1' , firstframe, lastframe, 1)

		if movFile != '':

			extension = cOS.getExtension(movFile)
			dirName = cOS.getDirName(movFile)
			baseName = movFile.replace(dirName, '')
			underlying = baseName.replace('.' + extension, '')

			files = os.listdir(exportDir)
			files.sort()

			for file in files:
				if file == baseName:
					underlying = underlying + '1'

			if extension != 'mov':
				print 'ERROR: Please provide an mov file'
				return

			# Get nuke nodes
			writer = nuke.toNode( 'Write1' )
			reader = nuke.toNode( 'Read1' )

			reader['file'].fromUserText(movFile)

			firstframe = reader['origfirst'].getValue()
			lastframe = reader['origlast'].getValue()
			nuke.Root()['first_frame'].setValue(firstframe)
			nuke.Root()['last_frame'].setValue(lastframe)
			nuke.Root()['fps'].setValue(float(fps))
			writer['mov64_fps'].setValue(float(fps))

			outputPath = exportDir + underlying + '.' + extension
			writer['file'].fromUserText(outputPath)

			if self.getOption('useAudio') == 'True':
				writer['mov64_audiofile'].fromUserText(movFile)
			writer['colorspace'].setValue(colorspaceDictionary[colorSpace])
			writer['channels'].setValue(channels)

			nuke.execute( 'Write1' , int(firstframe), int(lastframe), 1)

if __name__ == '__main__':
	slateGenerator = proResRenderer()
	slateGenerator.parseArgs(sys.argv)
	slateGenerator.render()