# Name: Localize tool
# Author: Shobhit Khinvasara
# Date: 08/08/2017

import os

import arkInit
arkInit.init()

# currentApp =  os.environ.get('ARK_CURRENT_APP')

import cOS
from translators import QtGui

import translators
translator = translators.getCurrent()

import baseWidget

import settingsManager
globalSettings = settingsManager.globalSettings()

class LocalizeTool(baseWidget.BaseWidget):
	defaultOptions = {
			'title': 'Localize Tool',

			'knobs': [
				{
					'name': 'Localize',
					'dataType' : 'Radio',
					'options': ['All', 'Selected']
				},
				{
					'name': 'Localize Nodes',
					'dataType': 'PythonButton',
					'callback': 'localizeNodes'
				},
				{
					'name': 'Open Cache Directory',
					'dataType': 'PythonButton',
					'callback': 'openCacheFolder'
			},
		]
	}

	def localizeNodes(self):
		nodes = []
		if self.getKnob('Localize').getValue() == 'Selected':
			nodes = translator.getSelectedNodes()
			if not len(nodes):
				return self.showError('No nodes selected')
		result = translator.localizeNodes(nodes=nodes)
		if not result:
			return self.showError('ARK_CACHE not set, set it with Set Computer-Name.')

		else:
			popup = QtGui.QMessageBox(self)
			popup.setText(str('Localized Node to ARK_CACHE successfully'))
			popup.exec_()

	def openCacheFolder(self):
		cOS.openFileBrowser(os.environ.get('ARK_CACHE'))

def gui():
	return LocalizeTool()

def launch(docked=False):
	translator.launch(LocalizeTool, docked=docked)

if __name__=='__main__':
	launch()
