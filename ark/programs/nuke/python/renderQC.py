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
# import arkNuke
# import nukeUtil

import cOS

from nukeScript import NukeScript

# fix: this and ImageConverter should share a common baseclass
class RenderQC(NukeScript):

	args = False
	options = {}
	# pretty good default, 90% of our work..
	fps = 23.976

	def qcFrames(self, curveTest, testFrames):
		# check each frame and fail on black frames
		for f in testFrames:
			intensity = curveTest['intensitydata'].getValueAt(f)
			allColors = intensity[0] + intensity[1] + intensity[2] + intensity[3]
			if allColors < 0.001:
				print 'RenderQC: FAIL, frame %d is black!' % f
				print 'RenderQC: intensities:', intensity
				return False
			else:
				print 'RenderQC: frame %d passed:' % f, intensity
		return True

	def execute(self):
		print 'RenderQC: QCing Output'

		readNode = nuke.nodes.Read()

		filepath = self.getOption('file')
		if '%' in filepath:
			filepath = cOS.getFrameRangeText(filepath)
		readNode['file'].fromUserText(filepath)

		curveTest = nuke.nodes.CurveTool()
		curveTest.setInput(0, readNode)
		curveTest['name'].setValue('curveTest')
		curveTest['ROI'].setValue([0,0,readNode.width(), readNode.height()])

		startFrame = int(readNode['first'].getValue())
		endFrame = int(readNode['last'].getValue())
		duration = endFrame - startFrame

		# based on the output path, find the shot and project
		# use the destinationFile to build path info

		# fix: should be checking FPS
		# destinationFile = self.getOption('destinationFile', filepath)

		# pathInfo = caretaker.getPathInfo(destinationFile)
		# if not pathInfo.projectInfo:
		# 	print 'RenderQC: Could not get path info for:', destinationFile
		# 	return False

		# fps = round(float(pathInfo.projectInfo['fps']), 3)

		# test duration
		conversionDuration = self.getOption('conversionDuration')
		if not conversionDuration:
			print 'RenderQC: Conversion duration not found in options!'
			return False

		if duration != int(conversionDuration):
			print 'RenderQC: fail, wrong duration'
			print 'RenderQC: file duration:', duration
			print 'RenderQC: expected duration:', conversionDuration
			return False

		# metadata = readNode.metadata()
		# if not metadata:
		# 	print 'RenderQC: fail, no metadata'
		# 	return False
		# if not arkNuke.validMeta(readNode):
		# 	print 'RenderQC: fail, no timecode'
		# 	return False
		# if 'input/frame_rate' not in metadata or \
		# 	round(metadata['input/frame_rate'], 3) != fps:
		# 	print 'RenderQC: fail, wrong fps'
		# 	print 'RenderQC: metadata fps:', round(metadata['input/frame_rate'], 3)
		# 	print 'RenderQC: expected fps:', fps
		# 	return False

		testFrames = range(startFrame, endFrame + 1)

		# compute the average intensity for the given frame range
		curveTest = nuke.toNode('curveTest')
		print 'RenderQC: running curve test:', startFrame, endFrame

		nuke.execute('curveTest', int(startFrame), int(endFrame))

		print 'RenderQC: testing black frames'
		qcPass = self.qcFrames(curveTest, testFrames)
		if not qcPass and 'decoder' in readNode.knobs():
			# the mov32 decoder gets the gamma on DNxHD's and Rec709's correct
			# the mov64 decoder can decode ProRes
			# it's all the worst
			print 'RenderQC: Retrying with mov32 decoder'
			readNode['decoder'].setValue('mov32')
			print 'RenderQC: re-running curve test:', startFrame, endFrame
			nuke.execute('curveTest', int(startFrame), int(endFrame))
			qcPass = self.qcFrames(curveTest, testFrames)

		if not qcPass:
			return False

		print 'QC Pass! YAY!!'
		return True


if __name__ == '__main__':
	renderQC = RenderQC()
	renderQC.parseArgs(sys.argv)
	renderQC.execute()


# "C:/Program Files/Nuke9.0v8/Nuke9.0.exe" -V 2 -t C:/ie/ark/programs/nuke/python/renderQC.py -options "{'conversionDuration': 62, 'file': 'R:/Modern_Family_s07/Final_Renders/MF_704/ProRes42HQ_Alexa/MF_704_16_0050_v007.mov'}"
