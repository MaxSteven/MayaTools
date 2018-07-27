
import arkInit
arkInit.init()

import caretaker
ct = caretaker.Caretaker()

import os


import translators
translator = translators.getCurrent()
from translators import QtCore, QtGui
import baseWidget


def main():
	options = {
	'title': 'test',
	'knobs': [{
		'name': 'Take a Screenshot',
		'dataType': 'TakeScreenShot'
	}]
	}
	translator.launch(baseWidget.BaseWidget, None, options=options)

if __name__=='__main__':
	main()