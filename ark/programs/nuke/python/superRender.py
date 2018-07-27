# Application modules
##################################################
# import nuke

# Our modules
##################################################
import arkInit
arkInit.init()

import arkUtil

from translators import QtCore

import os

import translators
translator = translators.getCurrent()

import settingsManager
globalSettings = settingsManager.globalSettings()

import baseWidget

import cOS

# independant function to run Super Render
def superRender(frameRange=None, numThreads=None, writeNodeName=None, outputFile=None):
	processes = []
	writeNode = None

	# Saves file just in case
	translator.saveFile(force=True)

	if not numThreads:
		numThreads = cOS.numberOfProcesses()

	if not frameRange:
		frameRange = translator.getAnimationRange()

	frameRangeChunks = arkUtil.splitFrameRangeByChunk(frameRange, numThreads)
	if writeNodeName:
		writeNode = translator.getNodeByName(writeNodeName)
	else:
		writeNode = translator.getSelectedNodes()[0]
		if not writeNode:
			raise Exception('Write node not selected: ' + writeNode.name())
		elif writeNode.getType() != 'finalrender':
			raise Exception('Selected node not write node: ' + writeNode.name())

		writeNodeName = writeNode.name()

	if not writeNode:
		raise Exception('Could not find write node')

	if not outputFile:
		outputFile = writeNode.getProperty('file')
		cOS.makeDirs(cOS.getPathInfo(outputFile)['dirname'])

	else:
		writeNode.setProperty('file', outputFile)

	# create Command line function to run nuke render
	for i in range(numThreads):
		frameRangeChunk = frameRangeChunks[i]
		frameRangeString = '%s-%s' % (frameRangeChunk['startFrame'], frameRangeChunk['endFrame'])
		args = [
			'"' + globalSettings.NUKE_EXE + '"',
			'-X', writeNodeName,
			'-V', '1',
			'-F', frameRangeString,
			translator.getFilename()
		]
		args = ' '.join([str(arg) for arg in args])
		# print args
		processes.append(cOS.startSubprocess(args))

	return processes, outputFile

# super Render UI
class SuperRender(baseWidget.BaseWidget):
	defaultOptions = {
			'title': 'Super Render',

			'knobs':[
				{
					'name': 'Number Of Processes',
					'dataType': 'Int',
					'value': 4
				},
				{
					'name': 'Progress',
					'dataType':'progress',
				},
				{
					'name': 'Render',
					'dataType':'PythonButton',
					'callback': 'render'
				}
			]
		}

	def init(self):
		# QTimer to check progress of render and update progressBar
		self.timer = QtCore.QTimer()
		self.timer.setInterval(8000)
		self.timer.timeout.connect(self.qtimerCallback)
		self.processes = []

	def render(self):
		numThreads = self.getKnob('Number Of Processes').getValue()
		self.processes, self.outputPath = superRender(numThreads=numThreads)
		frameRange = translator.getAnimationRange()
		self.numFrames = frameRange['endFrame'] - frameRange['startFrame'] + 1
		self.timer.start()

	def qtimerCallback(self):
		progress = 0

		# check number of files rendered
		files = os.listdir(cOS.getPathInfo(self.outputPath)['dirname'])

		# check progress based on number of files vs number of frames
		progress = len(files) / float(self.numFrames)

		# set progress to progressBar
		self.getKnob('Progress').setValue(progress)

		# if progress is done then wait for processes to end
		# and once its done, stop the timer and close the UI
		if progress >= 1:
			for p in self.processes:
				p.wait()

			self.timer.stop()
			self.close()

def gui():
	return SuperRender()

def main():
	translator.launch(SuperRender)

if __name__=='__main__':
	main()
