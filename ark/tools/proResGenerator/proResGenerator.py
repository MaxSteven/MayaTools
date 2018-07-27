import os

import arkInit
arkInit.init()

import settingsManager
globalSettings = settingsManager.globalSettings()

import translators
translator = translators.getCurrent()
frameRange = translator.getAnimationRange()

currentApp = os.environ.get('ARK_CURRENT_APP')

import cOS
import os
import baseWidget
import shepherd
import subprocess

class ProResGenerator(baseWidget.BaseWidget):

	defaultOptions = {
			'title': 'Sequence to ProRes Converter',
			'width': 600,
			'height': 100,

			'knobs': [
				{
					'name': 'Import Type',
					'dataType': 'list',
					'options': ['Sequence', 'Mov File']
				},
				{
					'name': 'Sequence Folder',
					'dataType': 'Directory',
					'buttonText': '...'
				},
				{
					'name': 'Mov Clip',
					'dataType': 'openFile',
					'buttonText': '...',
					'extension': '*.mov'
				},
				{
					'name': 'Use Mov for Audio',
					'dataType': 'checkbox',
					'value': True
				},
				{
					'name': 'FPS',
					'dataType': 'float',
					'value': 23.976
				},
				{
					'name': 'Pro-Res Type',
					'dataType': 'list',
					'options': [
						'Apple ProRes 442',
						'Apple ProRes 442 HQ',
						'Apple ProRes 442 LT',
						'Apple ProRes 442 Proxy',
						'Apple ProRes 4444'
					]
				},
				{
					'name': 'Channels',
					'dataType': 'list',
					'options': [
						'rgb',
						'rgba'
					]
				},
				{
					'name': 'Colorspace',
					'dataType': 'list',
					'value': 'sRGB',
					'options': [
						'linear',
						'sRGB',
						'rec709',
						'Cineon',
						'Gamma1.8',
						'Gamme2.2',
						'Gamma2.4',
						'Panalog',
						'REDLog',
						'ViperLog',
						'AlexaV3LogC',
						'PLogLin',
						'SLog',
						'Slog1',
						'SLog2',
						'SLog3',
						'CLog',
						'Protune',
						'REDSpace'
					]
				},
				{
					'name': 'Export Location',
					'dataType': 'Directory'
				},
				{
					'name': 'Generate Pro-Res',
					'dataType': 'PythonButton',
					'callback': 'submit'
				}
			]
	}

	def postShow(self):
		self.hideKnob('Mov Clip')
		self.hideKnob('Use Mov for Audio')
		self.hideKnob('FPS')
		self.getKnob('Import Type').on('changed', self.switchImport)

	def switchImport(self, *args):
		value = self.getKnob('Import Type').getValue()
		if value == 'Sequence':
			self.hideKnob('Mov Clip')
			self.hideKnob('Use Mov for Audio')
			self.hideKnob('FPS')
			self.showKnob('Sequence Folder')

		else:
			self.showKnob('Mov Clip')
			self.showKnob('FPS')
			self.showKnob('Use Mov for Audio')
			self.hideKnob('Sequence Folder')

	def submit(self):

		# Collect some initial shot info
		movFile = self.getKnob('Mov Clip').getValue()
		folderPath = self.getKnob('Sequence Folder').getValue()
		colorSpace = self.getKnob('Colorspace').getValue()
		proResType = self.getKnob('Pro-Res Type').getValue()
		exportDir = self.getKnob('Export Location').getValue()
		channels = self.getKnob('Channels').getValue()
		useAudio = self.getKnob('Use Mov for Audio').getValue()
		fps = self.getKnob('FPS').getValue()

		if folderPath == None or exportDir == None:
			self.showError('Please specify a shot folder and an export folder')
			return

		value = self.getKnob('Import Type').getValue()
		if value == 'Sequence':
			movFile = ''

		else:
			forlderPath = ''

		# Call up nuke!
		file = globalSettings.NUKE_EXE
		script = os.path.join(globalSettings.SYSTEM_ROOT, 'ie/ark/tools/proResGenerator/assets/renderProRes.py')
		options = {'movFile': str(movFile), 'useAudio': str(useAudio), 'fps': str(fps), 'directory': str(folderPath), 'channels': str(channels), 'colorSpace': str(colorSpace), 'proResType': str(proResType), 'exportDir': str(exportDir)}
		subprocess.call([file, '-V 2', '-t', script, '-options', str(options)])

def gui():
	return ProResGenerator()

def launch():
	translator.launch(ProResGenerator)

if __name__=='__main__':
	launch()