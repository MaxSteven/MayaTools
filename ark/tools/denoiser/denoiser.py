
import os
import time
import json
import win32api
import win32con

import arkInit
arkInit.init()

import settingsManager
globalSettings = settingsManager.globalSettings()

import translators
# from translators import QtGui
from translators import QtCore

translator = translators.getCurrent()

import baseWidget
import cOS

options = {
	'title': 'Denoiser',
	'width': 1200,
	'height': 700,
	'x': 100,
	'y': 100,
	'knobs': [
		{
			'name': 'heading',
			'dataType': 'heading',
			'value': 'Denoiser'
		},
		{
			'name': 'Sequence Directory',
			'dataType': 'Directory',
			# 'value': globalSettings.SHARED_ROOT,
			'value': 'R:/Detour_s03/Workspaces/TD_303/',
		},
		{
			'name': 'Search',
			'dataType': 'Text',
			# 'value': 'B_Alexa',
			'value': 'v02',
		},
		{
			'name': 'Plate Extension',
			'dataType': 'Text',
			'value': '.dpx',
		},
		{
			'name': 'Find Plates',
			'dataType': 'PythonButton',
			'callback': 'findPlates',
		},
		{
			'name': 'Plates to Denoise',
			'dataType': 'Text',
			'multiline': True,
		},
		{
			'name': 'Denoise Plates',
			'dataType': 'PythonButton',
			'callback': 'denoise',
		},
		{
			'name': 'Progress',
			'dataType': 'progress'
		},
	]
}


def collectPlates(root, plateExtension='.dpx', searchTerm=''):
	root = cOS.normalizeDir(root)
	searchTerm = searchTerm.lower()

	shots = os.listdir(root)
	shots.sort()

	# find the valid plate folders
	allPlateFolders = []
	for shot in shots:
		platesRoot = root + shot + '/Plates/'
		try:
			plateFolders = os.listdir(platesRoot)
			if searchTerm:
				plateFolders = [p for p in plateFolders if searchTerm in p.lower()]

			fullPlateRoot = [platesRoot + p + '/' for p in plateFolders if os.path.isdir(platesRoot + p)]
			allPlateFolders += fullPlateRoot
		except:
			print 'Invalid directory:', platesRoot
			continue

	frameRangeTexts = []

	# generate frame range text for each plate
	for plateRoot in allPlateFolders:
		files = [f for f in os.listdir(plateRoot) if plateExtension in f]
		if not len(files):
			print 'No plates found:', plateRoot
			continue

		# try:
		frameRange = cOS.getFrameRange(plateRoot + files[0])
		frameRangeText = cOS.getFrameRangeText(frameRange['paddedPath'], frameRange)
		frameRangeTexts.append(frameRangeText)
		# except:
		# 	print 'Invalid frame sequence:', plateRoot

	return frameRangeTexts


def click(x, y):
	win32api.SetCursorPos((x, y))
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)

def reduceNoiseClicks():
	time.sleep(2)
	click(172, 165)
	time.sleep(1)
	click(1332, 787)
	time.sleep(1)
	click(2252, 1308)



class Denoiser(baseWidget.BaseWidget):

	def postShow(self):
		self.assignShotAttributesFlag = False
		self.getKnob('Search').getWidget().setFocus()
		self.shots = []

		# clicker clicks in the UI whenever it finds a click file
		self.timer = QtCore.QTimer()
		self.timer.setInterval(1000)
		self.timer.timeout.connect(self.clicker)
		self.timer.start()

		self.clickDir = globalSettings.TEMP + 'denoise_clicks/'
		cOS.makeDirs(self.clickDir)
		cOS.emptyDir(self.clickDir)

	def clicker(self):
		if len(os.listdir(self.clickDir)) > 0:
			print 'found click, clicking'
			cOS.emptyDir(self.clickDir)
			reduceNoiseClicks()
		else:
			print 'no clicks found'

	def findPlates(self, *args):
		root = self.getKnob('Sequence Directory').getValue()
		search = self.getKnob('Search').getValue()
		plateExtension = self.getKnob('Plate Extension').getValue()

		plates = collectPlates(root, plateExtension, search)

		self.getKnob('Plates to Denoise').setValue('\n'.join(plates))

	def denoise(self, *args):
		plates = self.getKnob('Plates to Denoise').getValue()
		plates = plates.split('\n')
		plates = [p for p in plates if len(p) > 4]

		denoiseScriptPath = globalSettings.ARK_ROOT + 'ark/tools/denoiser/nukeDenoise.py'

		denoiseOptions = {}
		plateCount = len(plates)

		for i, plate in enumerate(plates):

			denoiseOptions['plate'] = plate


			denoiseOptions['startupScript'] = denoiseScriptPath

			with open(globalSettings.TEMP + 'nukePythonStartup', 'w+') as f:
				f.write(json.dumps(denoiseOptions))

			# convertCommand = '"' + globalSettings.NUKE_EXE + '" ' + globalSettings.ARK_ROOT + 'ark/programs/nuke/empty.nk'
			convertCommand = '"' + globalSettings.NUKE_EXE + '"'
			# convertCommand = [globalSettings.NUKE_EXE]
			# process = cOS.startSubprocess(convertCommand)
			# print convertCommand
			os.system(convertCommand)

			# # helpers to wrap w/ self
			# def checkIn(out, err):
			# 	self.clicker()

			# cOS.waitOnProcess(process,
			# 	checkInFunc=checkIn,
			# 	checkInInterval=1)

			print 'Denoised:', plate
			self.getKnob('Progress').setValue(float(i) / plateCount)

def launch(parent=None, *args, **kwargs):
	translator.launch(Denoiser, parent, options=options, *args, **kwargs)


def main():
	plates = collectPlates('R:/Detour_s03/Workspaces/TD_303/', '.dpx', 'v02')
	print '\n\n'
	print '\n'.join(plates)
	print globalSettings.ARK_ROOT

if __name__ == '__main__':
	launch()
	# main()
