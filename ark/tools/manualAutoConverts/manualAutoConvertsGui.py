# python
# launchScript "C:\ie\ark\tools\publish\publishMultiGui.py"

import os
import datetime
import subprocess

import arkInit
arkInit.init()

import translators
translator = translators.getCurrent()

import baseWidget
import copyWrapper
import cOS

import settingsManager
globalSettings = settingsManager.globalSettings()

from database import Database
database = Database()
database.connect()

from caretaker import Caretaker
caretaker = Caretaker()

from shotConverter import convertVersion

class ManualAutoConvertsGui(baseWidget.BaseWidget):

	projectRoot = False

	def findVersions(self):
		versionText = str(self.getKnob('versions').widget.toPlainText())
		self.versions = []
		for line in versionText.split('\n'):
			line = line.strip()
			parts = line.split('\t')
			if len(parts) < 2:
				print 'Invalid line:', line
				continue

			shot = parts[0]
			version = parts[-1]
			if 'v' in version.lower():
				version = cOS.getVersion(version)
			else:
				version = int(version)
			self.versions.append({'shot': shot, 'version': version})
			print 'shot:', shot, 'version:', version

		if not len(self.versions):
			self.error('No assets')
			return False

		shotParts = self.versions[0]['shot'].split('_')
		if not len(shotParts):
			self.error('Invalid shot name, no project code')
			return False

		folderSelection = self.getKnob('Project').getValue()
		project = caretaker.getEntityFromField('project','folderName', folderSelection)
		if not project:
			self.error('Invalid shot name, no project code')
			return False

		sequenceInfo = caretaker.getSequenceFromShot(shot)
		if not sequenceInfo:
			self.error('No sequence found for shot')
			return False

		self.sequence = sequenceInfo['name']

		self.projectRoot = globalSettings.SHARED_ROOT + project['folderName']
		self.versionRoot = '{0}/Final_Renders/{1}/'.format(self.projectRoot, self.sequence)
		self.exrRoot = '{0}/Final_Renders/{1}/EXR_Linear/'.format(self.projectRoot, self.sequence)

		if not os.path.isdir(self.versionRoot):
			self.error('Could not find version root:', self.versionRoot)

		self.conversions = database\
			.find('autoConversion')\
			.where('project','is',project['_id'])\
			.execute()

		self.conversions = dict([(c['name'], c) for c in self.conversions])

		self.getKnob('Version Type').clear().addItems(self.conversions)

		self.setOutputDirectory()

	def postShow(self):
		self.getKnob('Version Type').on('changed', self.setOutputDirectory)
		self.getKnob('Output Type').on('changed', self.setOutputDirectory)

		projects = caretaker.getProjects()
		projects = [project['folderName'] for project in projects if 'archive' in project and not project['archive']]
		projects.sort()
		self.getKnob('Project').addItems(projects)

	def setOutputDirectory(self, *args):
		if not self.projectRoot:
			return False

		today = datetime.date.today()
		versionType = self.getKnob('Version Type').getValue()
		outputType = self.getKnob('Output Type').getValue()
		if outputType == 'Temp':
			dateString = '{0:04d}_{1:02d}_{2:02d}'.format(today.year, today.month, today.day)
			exportRoot = '{0}/{1}/{3}'.format(
				globalSettings.TEMP, self.sequence, versionType, dateString)

		elif outputType == 'Deliverables':
			dateString = '{0:04d}_{1:02d}_{2:02d}'.format(today.year, today.month, today.day)
			exportRoot = '{0}/{4}/{1}/{3}'.format(
				self.projectRoot, self.sequence, versionType, dateString, outputType)

		elif outputType == 'Postings':
			dateString = '{0:04d}_{1:02d}_{2:02d}'.format(today.year, today.month, today.day)
			exportRoot = '{0}/{4}/{1}/{3}'.format(
				self.projectRoot, self.sequence, versionType, dateString, outputType)

		self.getKnob('Output Directory').setValue(exportRoot)

	def error(self, *error):
		print 'Error:', ' '.join(error)

	def convertVersion(self, shot, version):
		exrPath = self.exrRoot + shot
		print 'exrPath:', exrPath
		versionInfo = database\
			.findOne('version')\
			.where('path', 'contains', exrPath)\
			.where('name','is','EXR_Linear')\
			.where('number', 'is', version)\
			.execute()

		if not versionInfo:
			return False

		print 'Version:', versionInfo['path']

		conversionType = self.getKnob('Version Type').getValue()
		conversionInfo = self.conversions[conversionType]

		return convertVersion.convertVersion(versionInfo,
					conversionInfo)

	def onComplete(self):
		print 'Job complete!'

	def collectFiles(self):
		self.scanForShots()

		versionType = self.getKnob('Version Type').getValue()
		outputDirectory = cOS.normalizeDir(self.getKnob('Output Directory').getValue())
		result = cOS.makeDirs(outputDirectory)
		if type(result) is Exception:
			self.error('Could not make output directory:', outputDirectory)
			return False

		totalVersions = len(self.versions)
		progressKnob = self.getKnob('Progress')

		searchRoot = self.versionRoot + versionType + '/'


		results = []

		def collectVersion(shot, version):
			print 'Looking for:', shot, version
			path = False
			files = os.listdir(searchRoot)
			for f in files:
				if shot.lower() == f.lower().rpartition('_')[0]:
					fileVersion = cOS.getVersion(f)
					if fileVersion == version:
						path = f

			if path:
				src = searchRoot + path
				dest = outputDirectory + path
				print 'Found, copy:', src, '>', dest
				if os.path.isdir(src):
					src = cOS.normalizeDir(src)
					directoryFiles = os.listdir(src)
					validFiles = [f for f in directoryFiles if f[0] != '.' and os.path.isfile(src + '/' + f)]
					if len(validFiles):
						copyWrapper.copyTree(src, dest)
						if os.path.isdir(dest):
							return True
				else:
					copyWrapper.copy(src, dest)
					if os.path.isfile(dest):
						return True

			return False

		for i, versionInfo in enumerate(self.versions):
			progressKnob.setValue(float(i) / totalVersions)
			shot = versionInfo['shot']
			version = versionInfo['version']

			# try to collect the file
			collectResult = collectVersion(shot, version)
			convertResult = False

			# if we didn't collect it, the convert it
			if not collectResult:
				convertResult = self.convertVersion(shot, version)
				# then try to collect it again
				collectResult = collectVersion(shot, version)

			print convertResult
			print collectResult

			# store results
			if convertResult and collectResult:
				results.append([shot, 'Copied and Converted'])

			elif collectResult:
				results.append([shot, 'Copied'])

			elif not convertResult:
				results.append([shot, 'Unable to Convert'])

			else :
				print 'Did not find, trying to convert'
				results.append([shot, 'Not Found'])

		progressKnob.setValue(1)

		resultsOptions = {
			'title': 'Results',
			'width': 800,
			'height': 600,
			'knobs':[
				{
					'name': 'versions',
					'dataType': 'Table',
					'headings': ['Shot', 'Status'],
					'items': results,
				},
				{
					'name': 'Close',
					'dataType': 'PythonButton',
					'callback': 'closeWindow',
				},
			]
		}

		translator.launch(baseWidget.BaseWidget, None, options=resultsOptions, newWindow=True)

	def viewFiles(self):
		outputDirectory = self.getKnob('Output Directory').getValue()
		if cOS.isWindows():
			subprocess.call('explorer ' + outputDirectory.replace('/','\\'))
		elif cOS.isLinux():
			subprocess.call('nautilus ' + outputDirectory)

	def scanForShots(self):
		folderName = self.getKnob('Project').getValue()
		caretaker.createShotsForFolder(folderName)

	def scanForVersions(self):
		folderName = self.getKnob('Project').getValue()
		caretaker.createVersionsForFolder(folderName)

	def scanForAllShots(self):
		caretaker.createAllShots()

options = {
	'title': 'Manual Auto Converts',
	'width': 1200,
	'height': 768,
	'knobs':[
		{
			'name': 'heading',
			'dataType': 'heading',
			'value': 'Manual AutoConverts',
		},
		{
			'name': 'Project',
			'dataType': 'List',
			'options': [],
		},
		# scanning buttons
		{
			'name': 'Scan Shots for All Projects',
			'dataType': 'PythonButton',
			'callback': 'scanForAllShots',
		},
		{
			'name': 'Scan for Shots',
			'dataType': 'PythonButton',
			'callback': 'scanForShots',
		},
		{
			'name': 'Scan for Versions',
			'dataType': 'PythonButton',
			'callback': 'scanForVersions',
		},

		# versions
		{
			'name': 'versions',
			'dataType': 'Text',
			'multiline': True,
		},
		{
			'name': 'Find Versions',
			'dataType': 'PythonButton',
			'callback': 'findVersions',
		},
		{
			'name': 'Version Type',
			'dataType': 'List',
			'options': ['-- Please Find Versions first --'],
			'value': '-- Please Find Versions first --',
		},
		{
			'name': 'Output Type',
			'dataType': 'Radio',
			'options': ['Temp','Deliverables','Postings'],
			'value': 'Temp',
		},
		{
			'name': 'Output Directory',
			'dataType': 'Directory',
			'value': globalSettings.SHARED_ROOT,
		},
		{
			'name': 'Progress',
			'dataType': 'progress',
		},
		{
			'name': 'Collect Files',
			'dataType': 'PythonButton',
			'callback': 'collectFiles',
		},
		{
			'name': 'View Files',
			'dataType': 'PythonButton',
			'callback': 'viewFiles',
		},
	]
}


def main():
	translator.launch(ManualAutoConvertsGui, None, options=options)

if __name__ == '__main__':
	main()
