# launchScript "C:/ie/ark/tools/animationManager/animationManagerGui.py"

import lx
import os

import arkInit
arkInit.init()

import translators
translator = translators.getCurrent()
# from translators import QtGui

# import knobs
import baseWidget


options = {
	'title': 'Animation Manager',
	'width': 460,
	'height': 240,
	# 'x': 100,
	# 'y': 100,
	# 'margin': '0 0 0 0',
	'knobs': [
		{
			'name': 'heading',
			'dataType': 'heading',
			'value': 'Animation Manager'
		},
		{
			'name': 'Save file',
			'dataType': 'saveFile',
			'value': 'c:/temp/save.json',
			'label': 'Pick a file',
			'directory': 'C:/temp/',
			'extension': 'json (*.json)'
		},
		{
			'name': 'Save Selected',
			'dataType': 'pythonButton',
			'callback': 'saveSelected',
		},
		{
			'name': 'Load for Selected',
			'dataType': 'pythonButton',
			'callback': 'load',
		},
	]
}

class AnimationManager(baseWidget.BaseWidget):

	def saveSelected(self):
		print 'saveSelected:', self.knobs['Save file'].getValue()
		lx.eval('@"%s/animationManager.py" save %s' % \
			(os.path.dirname(__file__), self.knobs['Save file'].getValue()))

	def load(self):
		print 'load:', self.knobs['Save file'].getValue()
		lx.eval('@"%s/animationManager.py" load %s' % \
			(os.path.dirname(__file__), self.knobs['Save file'].getValue()))


def main():
	translator.launch(AnimationManager, options=options)


if __name__ == '__main__':
	main()
