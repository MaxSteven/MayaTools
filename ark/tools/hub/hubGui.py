import arkInit
arkInit.init()

import cOS

import settingsManager
globalSettings = settingsManager.globalSettings()

import translators
translator = translators.getCurrent()

# from translators import QtGui

import baseWidget

class HubGui(baseWidget.BaseWidget):
	defaultOptions = {
		'title': 'HubGui',
		'knobs':[
			{
				'name': 'Update',
				'dataType': 'PythonButton',
				'callback': 'updatePressed'
			},
			{
				'name': 'Logout',
				'dataType': 'PythonButton',
				'callback': 'logoutPressed'
			}
		]
	}

	def caretakerPressed(self):
		self.events.emit('caretakerPressed')

	def updatePressed(self):
		self.events.emit('updatePressed')

	def logoutPressed(self):
		self.events.emit('logoutPressed')

def gui():
	return HubGui()

