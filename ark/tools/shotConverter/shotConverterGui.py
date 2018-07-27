# python
# launchScript "C:\ie\ark\tools\publish\publishMultiGui.py"


import arkInit
arkInit.init()

import translators
translator = translators.getCurrent()

import baseWidget
import cOS

import settingsManager
globalSettings = settingsManager.globalSettings()

from database import Database
database = Database()
database.connect()

from caretaker import Caretaker
caretaker = Caretaker()

from shotConverter import convertVersion


options = {
	'title': 'Shot Converter',
	'width': 800,
	'height': 250,

	'knobs':[
		{
			'name': 'heading',
			'dataType': 'heading',
			'value': 'Shot Converter',
		},
		{
			'name': 'EXR Folder',
			'dataType': 'Directory',
			'value': globalSettings.SHARED_ROOT,
		},
		{
			'name': 'Conversion Type',
			'dataType': 'List',
			'options': ['-- Please enter an EXR first --'],
			'value': '-- Please enter an EXR first --',
		},
		{
			'name': 'Run Conversion',
			'dataType': 'PythonButton',
			'callback': 'runConversion',
		},
	]
}

class ShotConverterGui(baseWidget.BaseWidget):

	projectRoot = False

	def postShow(self):
		# fix: hacks to use event system here, don't have a better solution though
		self.getKnob('EXR Folder').on('changed', self.updateConversions)

		self.version = None

	def findVersion(self):
		folderPath = self.getKnob('EXR Folder').getValue()
		folderPath = cOS.unixPath(folderPath)
		parts = folderPath.split('/')
		if len(parts) < 5:
			return self.error('Invalid path, copy the whole path to the EXRs:', folderPath)

		folder = parts[5]
		versionNumber = cOS.getVersion(folderPath)
		print 'folder:', folder
		print 'versionNumber:', versionNumber

		self.version = database\
			.findOne('version')\
			.where('path','contains',folder)\
			.where('name','is','EXR_Linear')\
			.where('number','is', versionNumber)\
			.execute()

		if not self.version:
			return self.error('Could not find version:', self.version)

		print 'version:', self.version['name']

		self.asset = database\
			.findOne('asset')\
			.where('_id','is',self.version['asset'])\
			.options('getLinks',['project','shot'])\
			.execute()
		self.sequence = caretaker.getSequenceFromPath(self.version['path'])
		if not self.sequence:
			return self.error('Could not find sequence:', self.sequence)

		print 'version path:', self.version['path']

	def findConversions(self):
		print 'findConversions'
		self.conversions = database\
			.find('autoConversion')\
			.where('project','is',self.asset['project']['_id'])\
			.execute()

		self.conversions = dict((c['name'], c) for c in self.conversions)
		self.getKnob('Conversion Type').clear().addItems(self.conversions.keys())

	def updateConversions(self, path):
		print 'updateConversions:', path
		# bail if empty dir
		if self.getKnob('EXR Folder').getValue() == '':
			return

		self.findVersion()
		if not self.version:
			# self.error('Could not find version')
			return

		self.findConversions()

	def error(self, *error):
		text = 'Error: ' + ' '.join([str(e) for e in error])
		self.showError(text)

	def runConversion(self):
		print 'runConversion'

		conversionType = self.getKnob('Conversion Type').getValue()
		conversionInfo = self.conversions[conversionType]

		return convertVersion.convertVersion(self.version,
			conversionInfo)

	def onComplete(self):
		print 'Job complete!'

def main():
	translator.launch(ShotConverterGui, None, options=options)

if __name__ == '__main__':
	main()
