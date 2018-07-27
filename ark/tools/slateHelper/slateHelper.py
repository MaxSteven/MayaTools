import sys
# import os
# import glob
# import re
# import json
# import time

import arkInit
arkInit.init()
# import ieOS
# import cOS

# import arkUtil
import settingsManager
globalSettings = settingsManager.globalSettings()
import nuke
import arkNuke
# import nukeUtil

import caretaker
ct = caretaker.getCaretaker()

import cOS

from nukeScript import NukeScript

# fix: this and ImageConverter should share a common baseclass
class SlateHelper(NukeScript):

	args = False
	options = {}
	# pretty good default, 90% of our work..
	fps = 23.976

	def __init__(self):
		print 'SlateHelper: __init__'

	def execute(self):
		print 'SlateHelper: Creating output'

		nuke.scriptOpen(globalSettings.ARK_ROOT + 'ark/tools/slateHelper/slateHelper.nk')

		inputNode = nuke.toNode('input')
		plateNode = nuke.toNode('plate')

		filepath = self.getOption('input')
		if '%' in filepath:
			filepath = cOS.getFrameRangeText(filepath)
		inputNode['file'].fromUserText(filepath)

		# add slate and end card frames
		startFrame = int(inputNode['first'].getValue()) - 1
		endFrame = int(inputNode['last'].getValue()) + 1
		duration = endFrame - startFrame



		# based on the output path, find the shot and project
		# use the destinationFile to build path info
		destinationFile = self.getOption('destinationFile', filepath)
		pathInfo = ct.getPathInfo(destinationFile)
		if not pathInfo:
			print 'SlateHelper: Could not get path info for:', filepath
			return False

		fps = round(float(pathInfo['projectInfo']['fps']), 3)

		# test duration
		conversionDuration = self.getOption('conversionDuration')
		if not conversionDuration:
			print 'SlateHelper: Conversion duration not found in options!'
			return False

		if duration != int(conversionDuration):
			print 'SlateHelper: fail, wrong duration'
			print 'SlateHelper: file duration:', duration
			print 'SlateHelper: expected duration:', conversionDuration
			return False

		# metadata = inputNode.metadata()
		# if not metadata:
		# 	print 'SlateHelper: fail, no metadata'
		# 	return False
		# if not arkNuke.validMeta(readNode):
		# 	print 'SlateHelper: fail, no timecode'
		# 	return False
		# if 'input/frame_rate' not in metadata or \
		# 	round(metadata['input/frame_rate'], 3) != fps:
		# 	print 'SlateHelper: fail, wrong fps'
		# 	print 'SlateHelper: metadata fps:', round(metadata['input/frame_rate'], 3)
		# 	print 'SlateHelper: expected fps:', fps
		# 	return False

		testFrames = range(startFrame, endFrame + 1)

		# compute the average intensity for the given frame range
		curveTest = nuke.toNode('curveTest')
		print 'SlateHelper: running curve test:', startFrame, endFrame

		nuke.execute('curveTest', int(startFrame), int(endFrame))

		print 'SlateHelper: testing black frames'
		qcPass = self.qcFrames(curveTest, testFrames)
		if not qcPass and 'decoder' in readNode.knobs():
			# the mov32 decoder gets the gamma on DNxHD's and Rec709's correct
			# the mov64 decoder can decode ProRes
			# it's all the worst
			print 'SlateHelper: Retrying with mov32 decoder'
			readNode['decoder'].setValue('mov32')
			print 'SlateHelper: re-running curve test:', startFrame, endFrame
			nuke.execute('curveTest', int(startFrame), int(endFrame))
			qcPass = self.qcFrames(curveTest, testFrames)

		if qcPass:
			return False

		print 'QC Pass! YAY!!'

		return True


if __name__ == '__main__':
	SlateHelper = SlateHelper()
	SlateHelper.parseArgs(sys.argv)
	SlateHelper.execute()


# "C:/Program Files/Nuke9.0v8/Nuke9.0.exe" -V 2 -t C:/ie/ark/programs/nuke/python/SlateHelper.py -options "{'conversionDuration': 62, 'file': 'R:/Modern_Family_s07/Final_Renders/MF_704/ProRes42HQ_Alexa/MF_704_16_0050_v007.mov'}"
