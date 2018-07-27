
import os
# import collections
# import json
# import requests
# import urllib
# launchScript "C:/ie/ark/tools/sidebar/sidebarGui.py"

import arkInit
arkInit.init()

import translators
translator = translators.getCurrent()
# from translators import QtGui
# from translators import QtCore

import baseWidget

import publish


class Sidebar(baseWidget.BaseWidget):

	def new(self):
		publish.main(parent=self, mode='new')

	def open(self):
		publish.main(parent=self, mode='open')

	def publish(self):
		publish.main(parent=self, mode='publish')

	def publishMulti(self):
		publish.main(parent=self, mode='publishMulti')


def main():
	options = {
		'title': 'Sidebar',
		'width': 160,
		'height': 200,
		# 'x': 100,
		# 'y': 100,
		# 'margin': '0 0 0 0',
		'knobs': [
			{
				'name': 'New',
				'dataType': 'pythonButton',
				'callback': 'new',
			},
			{
				'name': 'Open',
				'dataType': 'pythonButton',
				'callback': 'open',
			},
			{
				'name': 'Publish',
				'dataType': 'pythonButton',
				'callback': 'publish',
			},
		]
	}
	if os.environ.get('ARK_CURRENT_APP') is None:
		options['knobs'].append({
				'name': 'Publish Multi',
				'dataType': 'pythonButton',
				'callback': 'publishMulti',
			})

	translator.launch(Sidebar, options=options)




if __name__ == '__main__':
	main()
