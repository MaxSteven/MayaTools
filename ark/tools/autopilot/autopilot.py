import os
import time
import datetime
import cOS

import arkInit
arkInit.init()

import translators
translator = translators.getCurrent()

import baseWidget

import settingsManager
globalSettings = settingsManager.globalSettings()

from multiprocessing import Process

class AutoPilot(baseWidget.BaseWidget):

	subProcess = None

	defaultOptions = {
			'title': 'AutoPilot Manager',
			'width': 500,
			'height': 600,

		'knobs': [
			{
				'name': 'heading',
				'dataType': 'heading',
				'value': 'AutoPilot Manager'

			},
			{
				'name': 'Scripts Source',
				'dataType': 'directory',
				'value' : globalSettings.DEFAULT_AUTOPILOT_DIR
			},
			{
				'name': 'Files',
				'dataType': 'listBox',
				'selectionMode': 'multi'
			},
			{
				'name': 'Run',
				'dataType': 'PythonButton',
				'callback': 'runAuto'
			},
			{
				'name': 'Stop',
				'dataType': 'PythonButton',
				'callback': 'stopAuto'
			}
		]
	}


	def init(self):
		pass

	def postShow(self):
		self.createFileList()

		self.getKnob('Scripts Source').on('changed', self.createFileList)

	def createFileList(self, *args):
		self.folderPath = cOS.normalizePath(self.getKnob('Scripts Source').getValue())
		self.fileList = []
		fileList = []
		try:
			allFiles = cOS.getFiles(self.folderPath,
				fileIncludes=['*.py'],
				folderExcludes=['.*'],
				fileExcludes=['.*'],
				filesOnly=True)

			for f in allFiles:
				fileList.append(f.replace(self.folderPath, ''))

		except:
			return

		self.fileList = cOS.collapseFiles(fileList)
		self.getKnob('Files').clear()
		self.getKnob('Files').addItems(self.fileList)

	def runAuto(self):
		directory = cOS.normalizePath(self.getKnob('Scripts Source').getValue())
		scripts = self.getKnob('Files').getValue()
		self.subProcess = Process(target=autoPilot, kwargs={'directory' : directory, 'scripts' : scripts})
		self.subProcess.start()
		if self.subProcess.is_alive():
			print '\n\n\nSuccessfully started AutoPilot process\n'
		else:
			print '\n\n\nUnable to start AutoPilot process\n'

	def stopAuto(self):
		if self.subProcess:
			self.subProcess.terminate()
			self.subProcess.join()
			if not self.subProcess.is_alive():
				print '\nTerminated:\t ' + str(datetime.datetime.now())
				self.subProcess = None
		else:
			print '\nNo AutoPilot process was found'

def autoPilot(directory, scripts):
	print '\n\n\n===========* RUNNING AUTO PILOT *===========\n'
	print 'Script Source:\t ' + directory
	print 'Initialized:\t ' + str(datetime.datetime.now())

	while True:

		if scripts:
			runPythonFiles(scripts, directory)
		else:
			for root, dirs, filenames in os.walk(directory):
				runPythonFiles(filenames, root)

		print 'Last run:\t {} \n'.format(datetime.datetime.now())
		time.sleep(2)

def runPythonFiles(scripts, root):
	for script in scripts:
		if script.endswith('.py'):
			pythonPath = cOS.join(root, script)
			cOS.runPython(pythonPath)

def main():
	translator.launch(AutoPilot, docked=False)

if __name__ == '__main__':
	main()
