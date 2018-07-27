
import arkInit
arkInit.init()
import arkUtil

import cOS

import settingsManager
globalSettings = settingsManager.globalSettings()

import translators
translator = translators.getCurrent()

import baseWidget
import updateModules

options = {
	'title': 'Update Manager',
	'width': 460,
	'height': 200,
	'knobs': [
		{
			'name': 'versions',
			'dataType': 'searchList'
		},
		{
			'name': 'Install Selected Version',
			'dataType': 'pythonButton',
			'callback': 'updateTools'
		}
	]
}

class UpdateManager(baseWidget.BaseWidget):

	def postShow(self):
		versionsPath = '%sAssets/Tools/install/' % globalSettings.SHARED_ROOT
		installVersions =  cOS.getFiles(path=versionsPath,
			folderIncludes=['ie_*'],
			fileExcludes=['*'],
			folderExcludes=['*'],
			includeAfterExclude=True
			)
		installVersions = arkUtil.sort(installVersions)
		self.getKnob('versions').addItems(installVersions)

	def updateTools(self):
		local = globalSettings.SYSTEM_ROOT + self.getKnob('versions').getValue().split('/')[-1] + '/'
		master = self.getKnob('versions').getValue()
		if not updateModules.updateModules(local, master):
			return self.showError('Incomplete release, please try after some time')
		setupCommand = 'python %sark/setup/Setup.pyc' % (globalSettings.ARK_ROOT)
		print cOS.getCommandOutput(setupCommand)
		self.showMessage('Update complete')


def gui():
	return UpdateManager(options=options)

def launch():
	translator.launch(UpdateManager, options=options)

if __name__ == '__main__':
	launch()
