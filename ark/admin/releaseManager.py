import arkInit
arkInit.init()

import cOS

import arkGit
import arkUtil

import settingsManager
globalSettings = settingsManager.globalSettings()

import translators
translator = translators.getCurrent()

import baseWidget
import moduleTools

# GUI
##################################################
options = {
	'title': 'Release Manager',
	'width': 460,
	'height': 200,
	'knobs': [
		{
			'name': 'publish location',
			'dataType': 'directory',
		},
		{
			'name': 'release version',
			'dataType': 'text'
		},
		{
			'name': 'release notes',
			'dataType': 'text',
			'multiline': True
		},
		{
			'name': 'Publish',
			'dataType': 'pythonButton',
			'callback': 'publishTools'
		}
	]
}

defaultModules = globalSettings.DEFAULT_MODULES
toolsFilter = globalSettings.TOOLS_FILTER

class ReleaseManager(baseWidget.BaseWidget):

	def postShow(self):
		versionsPath = '%sAssets/Tools/install/' % globalSettings.SHARED_ROOT
		installVersions =  cOS.getFiles(path=versionsPath,
				folderIncludes=['ie_v*'],
				fileExcludes=['*'],
				folderExcludes=['*'],
				includeAfterExclude=True
				)
		if installVersions:
			installVersions = arkUtil.sort(installVersions)
			versionElements = installVersions[-1].split('/')[-1].split('_')[-1].split('.')
			versionElements[-1] = str((int(versionElements[-1]) + 1))
			self.getKnob('release version').setValue('.'.join(versionElements))
		else:
			self.getKnob('release version').setValue('v1.0.0')

		publishLocation = '%sAssets/Tools/install/' % (globalSettings.SHARED_ROOT)
		self.getKnob('publish location').setValue(publishLocation)

	def publishTools(self):
		if self.getKnob('release version').getValue() is '' or self.getKnob('release notes').getValue() is '':
			return self.showError('Release Version and Release Notes must not be blank.')
		print 'Tagging branches'
		for module in defaultModules:
			arkGit.tag(self.getKnob('release version').getValue(),  '"' + self.getKnob('release notes').getValue() + '"',  arkInit.arkRoot + module)
			arkGit.pushTags(arkInit.arkRoot + module)
		print 'Branches tagged succesfully'

		print 'defaultModules:', defaultModules
		print 'toolsFilter:', toolsFilter
		quiet = False
		publishLocation = '%sie_%s' % (self.getKnob('publish location').getValue(), self.getKnob('release version').getValue())
		result = moduleTools.publishTools(publishLocation, defaultModules, quiet, **toolsFilter)
		try:
			open(publishLocation + '/completed.dat', 'w').close()
		except IOError:
			result = False

		if result:
			self.closeWindow()

def gui():
	return ReleaseManager(options=options)

def launch():
	translator.launch(ReleaseManager, options=options)

if __name__ == '__main__':
	launch()
