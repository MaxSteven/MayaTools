
import json
import urllib

import arkInit
arkInit.init()

import translators
translator = translators.getCurrent()
# from translators import QtGui
# from translators import QtCore

from steppedGui import SteppedGui

import publishGui
import baseWidget
import publishWebGui


class PublishSingle(SteppedGui):

	def init(self):
		# Step One
		self.steps.append({
			'class': baseWidget.BaseWidget,
			'options': publishGui.options,
			'callback': self.stepOne
			})

	def stepOne(self, data):
		# print data
		self.steps.append({
			'class': publishWebGui.WebGui,
			'options': publishWebGui.options,
			'callback': self.stepTwo
			})
		self.next()
		webWidget = self.getCurrentWidget()

		# build the url
		url = 'http://127.0.0.1:2020/publish/selectType?'
		data = {
			'files': json.dumps(data['files'])
		}
		url += urllib.urlencode(data)

		webWidget.getKnob('web').loadUrl(url)

	def stepTwo(self, data):
		print data


options = {
		'margin': '0 0 0 0',
		# 'x': 100,
		# 'y': 100,
	}

def main(parent=None, newWindow=False):
	translator.launch(PublishSingle,
		parent=parent,
		options=options,
		newWindow=newWindow)


if __name__ == '__main__':
	main()
