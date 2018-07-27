# Name: Animation Publisher
# Author: Shobhit Khinvasara

import arkInit
arkInit.init()

import translators
translator = translators.getCurrent()

import baseWidget

class AnimationPublisher(baseWidget.BaseWidget):
	defaultOptions = {
		'title': 'Animation Publisher',

		'knobs': [
			{
				'name':'Animation directory',
				'dataType': 'directory'
			},
			{
				'name': 'Animation Sequence Name',
				'dataType': 'text'
			},
			{
				'name': 'Frame Range',
				'dataType': 'FrameRange'
			},
			{
				'name': 'Export FBX',
				'dataType': 'checkbox',
				'value': True
			},
			{
				'name': 'Publish Animation',
				'dataType': 'PythonButton',
				'callback': 'publishAnimation'
			}
		]
	}

	def init(self):
		pass

	def postShow(self):
		pass

	def publishAnimation(self):
		animationOptions = {
			'AnimDir': self.getKnob('Animation directory').getValue(),
			'AnimName': self.getKnob('Animation Sequence Name').getValue(),
			'FrameRange': self.getKnob('Frame Range').getValue(),
			'Export': self.getKnob('Export FBX').getValue()
		}
		# get/set animation publishing options
		translator.exportAnimation(options=animationOptions)


def gui():
	return AnimationPublisher()

def launch(docked=False):
	translator.launch(AnimationPublisher, docked=docked)

if __name__=='__main__':
	launch()
