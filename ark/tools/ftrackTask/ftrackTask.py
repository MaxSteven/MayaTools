import arkInit
arkInit.init()

import os

currentApp =  os.environ.get('ARK_CURRENT_APP')

import translators
translator = translators.getCurrent()

import settingsManager
globalSettings = settingsManager.globalSettings()

import baseWidget
import arkFTrack
pm = arkFTrack.getPM()

class FtrackTask(baseWidget.BaseWidget):
	startTime = False

	defaultOptions = {
			'title': 'Ftrack Task',
			'align': 'top',
			'margin': '8 8 8 8',
			'spacing': 8,

			'knobs' : [
				{
					'name': 'Log Time',
					'dataType': 'FtrackTimer',
				},
				{
					'name': 'Web View',
					'dataType': 'FtrackWebView'
				}
			]
		}


def gui():
	if os.getenv('ARK_CURRENT_APP') == 'houdini':
		# task view panel crashes houdini now
		return None

	return FtrackTask()

def launch(*args):
	return translator.launch(FtrackTask, docked=True)


if __name__=='__main__':
	launch()



