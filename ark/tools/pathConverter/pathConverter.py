
import arkInit
arkInit.init()

import translators
translator = translators.getCurrent()

import baseWidget

import pathManager

class PathConverter(baseWidget.BaseWidget):
	defaultOptions = {
		'title': 'PathConverter',
		'width': 600,
		'height': 200,
		'x': 100,
		'y': 100,
		'knobs': [
			{
				'name': 'Path',
				'dataType': 'text',
				'value': ''
			},
			{
				'name': 'Results',
				'dataType': 'ListBox',
				'options': []
			}
		]
	}

	def init(self):
		self.oldValue = ''

	def postShow(self):
		self.getKnob('Path').on('keyReleased', self.convertPath)

	def convertPath(self):
		if not self.oldValue == self.getKnob('Path').getValue():
			self.getKnob('Results').clear()
			possiblePaths = pathManager.translatePathSearch(self.getKnob('Path').getValue())
			if possiblePaths:
				self.getKnob('Results').addItems(possiblePaths)
			self.oldValue = self.getKnob('Path').getValue()

def gui():
	return PathConverter()

def launch(docked=False):
	translator.launch(PathConverter, docked=docked)

if __name__ == '__main__':
	launch()
