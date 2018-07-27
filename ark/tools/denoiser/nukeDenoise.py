import sys
# import os
# import glob
# import re
# import json
import time

import arkInit
arkInit.init()
# import ieOS
# import cOS

# import arkUtil
import settingsManager
globalSettings = settingsManager.globalSettings()

import nuke
import arkNuke
# import pathManager

from nukeScript import NukeScript

class nukeDenoise(NukeScript):

	args = False
	options = {}

	def __init__(self):
		print 'Denoise: __init__'

	def denoisePlates(self):
		print 'Denoise: denoisePlates'

		# get the list of input objects
		plate = self.getOption('plate')

		readNode = nuke.createNode('Read')
		readNode['file'].fromUserText(plate)

		arkNuke.checkScript(force=True)

		# denoise = nuke.createNode('OFXcom.absoft.neatvideo4_v4')
		denoise = nuke.createNode('Blur')

		output = plate.replace('Plates/','Assets/auto_denoised/')
		write = nuke.createNode('Write')
		write['file'].fromUserText(output)
		write['colorspace'].fromScript(readNode['colorspace'].toScript())

		# add a click file to the click folder
		# so the parent program knows to click the buttons
		f = open(globalSettings.TEMP + 'denoise_clicks/click', 'w+')
		f.close()

		# print 'saving:', globalSettings.TEMP + 'denoise.nk'
		# nuke.scriptSave(globalSettings.TEMP + 'denoise.nk')

		# denoise['Prepare_Profile...'].execute()
		# wait for clicks
		time.sleep(6)

		nuke.execute(write.name(),
			int(readNode['first'].getValue()),
			int(readNode['last'].getValue()))

# if __name__ == '__main__':
print 'trying to run'
nukeDenoise = nukeDenoise()
nukeDenoise.parseArgs(sys.argv)
nukeDenoise.denoisePlates()

# "C:/Program Files/Nuke9.0v6/Nuke9.0.exe" -V 2 -t C:/ie/ark/programs/nuke/python/nukeDenoise.py -options "{'outputColorspace': 'sRGB', 'codec': 'h264_low', 'inColorspace': 'AlexaV3LogC', 'output': 'C:/Trash/formats/test.mov', 'inputs': [{'file': 'c:/Trash/sequence/sequence.%04d.jpg'}], 'resize': .5, 'resizeType': 'width', 'fps': 23.976, 'handles': 5, 'startFrame': 1001, 'slateArtist': 'Tom Brady', 'slateJob': 'Patriots', 'slateVersion': '2015', 'slateShot': 'Superbowl', 'slateNotes': 'Good job', 'slateBurnIn': true, 'slateMaskOpacity': 0.5}"
# "C:/Program Files/Nuke9.0v6/Nuke9.0.exe" -V 2 -t C:/ie/ark/programs/nuke/python/nukeDenoise.py -options "{'outputColorspace': 'sRGB', 'codec': 'h264_low', 'inColorspace': 'AlexaV3LogC', 'output': 'C:/Trash/formats/test.mov', 'inputs': [{'file': 'c:/Trash/sequence/sequence.%04d.jpg'}, {'file': 'c:/Trash/sequence/sequence2.%04d.jpg'}, {'file': 'c:/Trash/sequence/sequence.%04d.jpg'}, {'file': 'c:/Trash/sequence/sequence2.%04d.jpg'}], 'reformat': {'value': '.5', 'resizeType': 'width'}, 'fps': 23.976, 'handles': 5, 'startFrame': 1001, 'slateBurnIn': true, 'slateVersion': '027', 'slateArtist': 'Tom Brady'}"
# "C:/Program Files/Nuke9.0v6/Nuke9.0.exe" -V 2 -t C:/ie/ark/programs/nuke/python/nukeDenoise.py -options "{'outputColorspace': 'sRGB', 'codec': 'jpg_75', 'inColorspace': 'AlexaV3LogC', 'output': 'C:/Trash/formats/seq/test.%04d.jpg', 'inputs': [{'file': 'c:/Trash/sequence/sequence.%04d2.jpg'}], 'reformat': {'value': '.5', 'resizeType': 'width'}, 'fps': 23.976, 'handles': 5, 'startFrame': 1001, 'slateArtist': 'Tom Brady', 'slateJob': 'Patriots', 'slateVersion': '2015', 'slateShot': 'Superbowl', 'slateNotes': 'Good job', 'slateBurnIn': true, 'slateMaskOpacity': 0.5}"
# "C:/Program Files/Nuke9.0v6/Nuke9.0.exe" -V 2 -t C:/ie/ark/programs/nuke/python/nukeDenoise.py -options "{'slate': false, 'outputColorspace': 'linear', 'codec': 'exr_16bit_piz', 'inColorspace': 'sRGB', 'output': 'C:/Trash/formats/exr/test.%04d.exr', 'inputs': [{'file': 'c:/Trash/sequence/sequence2.%04d.jpg'}], 'reformat': {'value': '.5', 'resizeType': 'width'}, 'fps': 23.976, 'handles': 5, 'startFrame': 1001, 'slateArtist': 'Tom Brady', 'slateJob': 'Patriots', 'slateVersion': '2015', 'slateShot': 'Superbowl', 'slateNotes': 'Good job', 'slateBurnIn': true, 'slateMaskOpacity': 0.5}"
# "C:/Program Files/Nuke9.0v6/Nuke9.0.exe" -V 2 -t C:/ie/ark/programs/nuke/python/nukeDenoise.py -options "{'outputColorspace': 'AlexaV3LogC', 'codec': 'prores_422HQ', 'inColorspace': 'sRGB', 'output': 'C:/Trash/formats/prores_422HQ.mov', 'inputs': [{'file': 'c:/Trash/sequence/sequence2.%04d.jpg'}], 'fps': 23.976, 'handles': 0, 'startFrame': 1001, 'slateArtist': 'Tom Brady', 'slateJob': 'Patriots', 'slateVersion': '2015', 'slateShot': 'Superbowl', 'slateNotes': 'Good job', 'slateBurnIn': true, 'slateMaskOpacity': 0.5}"
# "C:/Program Files/Nuke9.0v6/Nuke9.0.exe" -V 2 -t C:/ie/ark/programs/nuke/python/nukeDenoise.py -options "{'outputColorspace': 'AlexaV3LogC', 'codec': 'prores_444', 'inColorspace': 'sRGB', 'output': 'C:/Trash/formats/prores_444.mov', 'inputs': [{'file': 'c:/Trash/sequence/sequence2.%04d.jpg'}], 'fps': 23.976, 'handles': 0, 'startFrame': 1001, 'slateArtist': 'Tom Brady', 'slateJob': 'Patriots', 'slateVersion': '2015', 'slateShot': 'Superbowl', 'slateNotes': 'Good job', 'slateBurnIn': true, 'slateMaskOpacity': 0.5}"
# "C:/Program Files/Nuke9.0v6/Nuke9.0.exe" -V 2 -t C:/ie/ark/programs/nuke/python/nukeDenoise.py -options "{'outputColorspace': 'AlexaV3LogC', 'codec': 'prores_444', 'inColorspace': 'AlexaV3LogC', 'output': 'C:/Trash/formats/prores_444_realFootage.mov', 'inputs': [{'file': 'r:/Agent_X_s01/Workspaces/AGX_104/AGX104_001_020/Plates/v001/AGX104_001_020_A_alexaLog.%04d.dpx'}], 'fps': 23.976, 'handles': 0, 'startFrame': 1001, 'slateArtist': 'Tom Brady', 'slateJob': 'Patriots', 'slateVersion': '2015', 'slateShot': 'Superbowl', 'slateNotes': 'Good job', 'slateMaskOpacity': 0.5}"
# "C:/Program Files/Nuke9.0v6/Nuke9.0.exe" -V 2 -t C:/ie/ark/programs/nuke/python/nukeDenoise.py -options "{'slate': false, 'outputColorspace': 'AlexaV3LogC', 'codec': 'prores_444', 'inColorspace': 'AlexaV3LogC', 'output': 'C:/Trash/formats/prores_444_realFootage_noSlate.mov', 'inputs': [{'file': 'r:/Agent_X_s01/Workspaces/AGX_104/AGX104_001_020/Plates/v001/AGX104_001_020_A_alexaLog.%04d.dpx'}], 'fps': 23.976, 'handles': 0, 'startFrame': 1001, 'slateArtist': 'Tom Brady', 'slateJob': 'Patriots', 'slateVersion': '2015', 'slateShot': 'Superbowl', 'slateNotes': 'Good job', 'slateMaskOpacity': 0.5}"
# "C:/Program Files/Nuke9.0v6/Nuke9.0.exe" -V 2 -t C:/ie/ark/programs/nuke/python/nukeDenoise.py -options "{'outputColorspace': 'AlexaV3LogC', 'codec': 'prores_444', 'inColorspace': 'AlexaV3LogC', 'output': 'C:/Trash/formats/prores_444_blackish_noSlate.mov', 'inputs': [{'file': 'R:/Black-ish_s01/Workspaces/BLA_108_03_040/Plates/BLA_108_03_040_Left_Alexa.%04d.dpx'}], 'fps': 23.976, 'handles': 0, 'startFrame': 1001, 'slateArtist': 'Tom Brady', 'slateJob': 'Patriots', 'slateVersion': '2015', 'slateShot': 'Superbowl', 'slateNotes': 'Good job', 'slateMaskOpacity': 0.5}"
# "C:/Program Files/Nuke9.0v6/Nuke9.0.exe" -V 2 -t C:/ie/ark/programs/nuke/python/nukeDenoise.py -options "{'outputColorspace': 'AlexaV3LogC', 'codec': 'prores_444', 'inColorspace': 'AlexaV3LogC', 'output': 'C:/Trash/formats/prores_444_blackish_noSlate.mov', 'inputs': [{'file': 'R:/Black-ish_s01/Workspaces/BLA_108_03_040/Plates/BLA_108_03_040_Left_Alexa.%04d.dpx'}], 'fps': 23.976, 'handles': 0, 'startFrame': 1001, 'slateArtist': 'Tom Brady', 'slateJob': 'Patriots', 'slateVersion': '2015', 'slateShot': 'Superbowl', 'slateNotes': 'Good job', 'slateMaskOpacity': 0.5, 'slateBurnIn': true}"
# "C:/Program Files/Nuke9.0v6/Nuke9.0.exe" -V 2 -t C:/ie/ark/programs/nuke/python/nukeDenoise.py -options "{'outputColorspace': 'AlexaV3LogC', 'codec': 'prores_444', 'inColorspace': 'sRGB', 'output': 'C:/Trash/formats/prores_444.mov', 'inputs': [{'file': 'c:/Trash/sequence/sequence2.%04d.jpg'}], 'fps': 23.976, 'handles': 0, 'startFrame': 1001, 'slateArtist': 'Tom Brady', 'slateJob': 'Patriots', 'slateVersion': '2015', 'slateShot': 'Superbowl', 'slateNotes': 'Good job', 'slateBurnIn': true, 'slateMaskOpacity': 0.5}"
