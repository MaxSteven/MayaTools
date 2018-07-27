
import arkInit
arkInit.init()

import translators
translator = translators.getCurrent()

import baseWidget


options = {
	'title': 'Publish',
	'width': 460,
	'height': 640,
	# 'x': 100,
	# 'y': 100,
	# 'margin': '0 0 0 0',
	'knobs': [
		{
			'name': 'heading',
			'dataType': 'heading',
			'value': 'Publish Files'
		},
		{
			'name': 'files',
			'dataType': 'openFiles',
			'value': '',
			'directory': '',
		},
		{
			'name': 'Next',
			'dataType': 'pythonButton',
			'callback': 'submit',
		},
	]
}






def gui(parent=None):
	return baseWidget.BaseWidget(parent=parent, options=options)

def main():
	translator.launch(baseWidget.BaseWidget, options=options)


if __name__ == '__main__':
	main()
