import os
import sys

arkRoot = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + '/../../')

print 'arkRoot:', arkRoot

sys.path.append(arkRoot)

import arkInit
arkInit.init()

import cOS

import translators
translator = translators.getCurrent()

import arkUtil

import baseWidget

class SetComputerSettings(baseWidget.BaseWidget):
	defaultOptions = {
			'title': 'Set Computer Settings',

			'knobs': [
			{
				'name': 'User Name',
				'dataType': 'Text',
				'value': cOS.getOSUsername()
			},
			{
				'name': 'Computer Name',
				'dataType': 'Text',
				'value': cOS.getComputerName()
			},
			{
				'name': 'Local Cache Folder',
				'dataType': 'Directory'
			},
			{
				'name': 'Set Computer Settings',
				'dataType': 'PythonButton',
				'callback': 'setComputerSettings'
			}
		]
	}

	def setComputerSettings(self):
		userName = arkUtil.makeWebSafe(self.getKnob('User Name').getValue())
		computerName = arkUtil.makeWebSafe(self.getKnob('Computer Name').getValue())
		cacheDir = self.getKnob('Local Cache Folder').getValue()
		newName = userName + '_' + computerName
		if newName == '_':
			self.showError('Name not Set!')
			return

		if cacheDir == '':
			self.showError('Cache Dir not Set!')
			return

		cOS.setEnvironmentVariable('ARK_COMPUTER_NAME', newName)
		cOS.setComputerName(newName)
		cOS.setEnvironmentVariable('ARK_CACHE', cacheDir)
		if cOS.isLinux():
			os.system('chown -R ' + cOS.getOSUsername() + ' ' + cacheDir)

def gui():
	return SetComputerSettings()

def launch():
	translator.launch(SetComputerSettings)

if __name__=='__main__':
	launch()
