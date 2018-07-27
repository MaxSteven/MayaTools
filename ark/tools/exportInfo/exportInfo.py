
import datetime
import re

import arkInit
arkInit.init()

import translators
translator = translators.getCurrent()
# from translators import QtCore
# from translators import QtSignal

import baseWidget
import cOS

import settingsManager
globalSettings = settingsManager.globalSettings()

from database import Database
database = Database()
database.connect()

class ExportInfoGui(baseWidget.BaseWidget):


	def postShow(self):
		now = datetime.datetime.now()
		baseID = 'IG' + str(now.year) + str(now.month) + str(now.day) + 'A'
		self.getKnob('submission id').setValue(baseID)


	def viewInfo(self):
		now = datetime.datetime.now()
		submissionID = 'IG' + str(now.year) + '%02d' % now.month + '%02d' % now.day + 'A'
		noteVendor = 'INGENUITY'
		submissionDate = '%02d' % now.month + '/' + '%02d' % now.day + '/' + str(now.year)
		directory = self.getKnob('folder').getValue()

		allFiles = cOS.collectAllFiles(directory)
		# get just 'path' from the pathInfo dict that allFiles returns
		allFiles = [f['path'] for f in allFiles]
		fileList = cOS.collapseFiles(allFiles)

		formatted = 'Submission ID,' + 'Note Vendor,' + 'Submission Date,' +'VFX Number,' +'Slate,' + 'Submission Format,' +'Frame Count,' + 'Submission Notes\n'

		for f in fileList:
			submissionFormatOurs = False
			if f.endswith('.mov'):
				submissionFormat = 'QT'
				vfxNumber = re.search(r'(\b[0-9a-zA-Z_]*)(_v\d+)(_RV)?(.mov)',f).group(1)
				slateInfo = re.search(r'((\b[0-9a-zA-Z_]*)(.mov))',f).group(1)
				frameCount = ''
				submissionFormatOurs = True
			elif cOS.isFrameRangeText(f):
				parts = f.split(' ')
				fullPath = parts[0]
				frameCount = parts[1]
				# use https://regex101.com/ to find out about group numbering with test string r:/Blackish_s03/Final_Renders/BLA_308/EXR_Linear/BLA_308_018_020_v0008/BLA_308_018_020_v0008.%04.exr 1000-1048
				submissionFormat = re.search(r'(\.([a-zA-Z]{1,3}))$',fullPath).group(2)
				vfxNumber = re.search(r'(\/(((\b[0-9a-zA-Z_]*)(_v\d{4}\/))))',fullPath).group(4)
				versionNumber = re.search(r'(\/(((\b[0-9a-zA-Z_]*)((_v\d{4})(\/)))))',fullPath).group(6)
				slateInfo = vfxNumber + versionNumber + '.' + frameCount + '.' + submissionFormat
				submissionFormatOurs = True

			if submissionFormatOurs:
				formatted += submissionID + ',' + noteVendor + ',' + submissionDate+ ',' + vfxNumber + ',' + slateInfo + ',' + submissionFormat.upper() + ',' + frameCount + '\n'

		self.getKnob('Info').setValue(formatted)




options = {
	'title': 'Export Info',
	'width': 1280,
	'height': 780,
	# 'x': 100,
	# 'y': 100,
	'knobs':[
		{
			'name': 'heading',
			'dataType': 'heading',
			'value': 'Export Info',
		},
		{
			'name': 'submission id',
			'dataType': 'text',
		},
		{
			'name': 'folder',
			'dataType': 'Directory',
			'value': 'R:/',
		},
		{
			'name': 'Info',
			'dataType': 'text',
			'multiline': True,
		},
		{
			'name': 'Get Info',
			'dataType': 'PythonButton',
			'callback': 'viewInfo',
		},
	]
}




def main():
	translator.launch(ExportInfoGui, None, options=options)

if __name__ == '__main__':
	main()
