
import json

import arkInit
arkInit.init()

import translators
translator = translators.getCurrent()
# from translators import QtGui
from translators import QtCore

import baseWidget




options = {
	'title': 'Select Assets',
	'width': 460,
	'height': 736,
	# 'x': 100,
	# 'y': 100,
	'margin': '0 0 0 0',
	'knobs': [
		{
			'name': 'web',
			'dataType': 'web',
			'url': '127.0.0.1:2020/publish/selectProgram',
		},
	]
}


class AppHelper(QtCore.QObject):

	def __init__(self, parent=None):
		super(AppHelper, self).__init__(parent)

	@QtCore.Slot(str)
	def log(self, text):
		print text

	@QtCore.Slot()
	def back(self):
		self.parent().parent().back()

	@QtCore.Slot(str)
	def submit(self, data):
		self.parent().submit(json.loads(data))


class WebGui(baseWidget.BaseWidget):

	def postShow(self):
		self.appHelper = AppHelper(self)
		self.getKnob('web').addJavascriptObject('appHelper', self.appHelper)




def gui():
	return WebGui(options=options)

def main():
	translator.launch(WebGui, options=options)


if __name__ == '__main__':
	main()