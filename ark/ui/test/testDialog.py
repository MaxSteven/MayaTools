
import os
# import collections

import arkInit
arkInit.init()

import translators
translator = translators.getCurrent()

import baseWidget
import knobs

class Test(baseWidget.BaseWidget):

	def init(self):

		knob = knobs.Text('description', 'Have a lovely day')
		self.addKnob(knob)

		knob = knobs.Text('paragraph', 'super\nawesome\nrad', {'multiline': True})
		self.addKnob(knob)

		knob = knobs.Checkbox('checkbox', True)
		self.addKnob(knob)

		knob = knobs.Vec3('vec3')
		self.addKnob(knob)

		options = {'options': ['sweet', 'awesome', 'rad']}
		knob = knobs.Radio('radio', 'awesome', options)
		# print 'TestDialog: Value is ' + knob.value
		self.addKnob(knob)

		options = {'options': ['yes', 'no', 'maybe']}
		knob = knobs.List('list', 'maybe', options)
		self.addKnob(knob)

		options = {
			'label': 'Save a file',
			'directory': 'C:/temp/',
			'extension': 'Whatever(*.*)'
		}
		knob = knobs.SaveFile('Output Filename', 'c:/thoughts.txt', options)
		self.addKnob(knob)

		options = {
			'selectionMode': 'multi',
			'options': ['Xe', 'Ya', 'Zf'],
		}
		knob = knobs.ListBox('Crazy List', options=options)
		self.addKnob(knob)
		self.getKnob('Crazy List').setValue('Y')

		options = {
			'headings': ['root','filename','extension'],
			'items': [['A', 'B', 'C'], ['D', 'E', 'F']]
		}
		data = self.getData()
		knob = knobs.Table('Files', data, options)
		self.addKnob(knob)

		options = {
			'label': 'Output Directory',
			'directory': 'C:/temp/'
		}
		knob = knobs.Directory('Output Directory', 'c:/temp', options)
		# self.addKnob(knob)

		# options = {
		# 	'url': 'http://google.com',
		# }
		# knob = knobs.Web('web', options=options)
		# self.addKnob(knob)

		# options = {
		# }
		# knob = knobs.OpenFiles('publish files', options=options)
		# self.addKnob(knob)

		knob = knobs.TakeScreenShot('Test')
		self.addKnob(knob)

		options = {
			'callback': 'submit', 'iconPath': 'C:/ie/ark/ui/icons/hub.png'
		}
		knob = knobs.PythonButton('Submit', options=options)
		self.addKnob(knob)

	def postShow(self):
		self.getKnob('name').on('changed', self.nameChanged)
		self.getKnob('number').on('changed', self.numberChanged)
		self.getKnob('Crazy Number').on('changed', self.floatChanged)
		self.getKnob('Crazy List').on('changed', self.listBoxChanged)
		self.getKnob('checkbox').on('changed', self.checkBoxChanged)
		self.getKnob('how awesome').on('changed', self.radioChanged)
		self.getKnob('list').on('changed', self.listChanged)
		self.getKnob('DList').on('clicked', self.dynamicListChanged)
		self.getKnob('DList').on('doubleClicked', self.removeItem)
		self.events.on('enterPressed', self.enterWasPressed)
		self.getKnob('Resolution').on('changed', self.resolutionChanged)
		self.getKnob('asset').on('changed', self.test)

	def resolutionChanged(self, *args):
		print self.getKnob('Resolution').getWidth()
		print self.getKnob('Resolution').getHeight()
	def enterWasPressed(self):
		print 'Wassaaa..'

	def removeItem(self):
		# print 'listItems: ', self.getKnob('DList').listItems
		self.getKnob('DList').removeItem(self.getKnob('DList').getValue())

	def listBoxChanged(self):
		print 'listBoxChanged'
		print self.getKnob('Crazy List').getValue()

	def nameChanged(self, *args):
		print 'nameChanged'
		print self.getKnob('name').getValue()

	def numberChanged(self, *args):
		print 'numberChanged'
		print self.getKnob('number').getValue()

	def floatChanged(self, *args):
		print 'floatChanged'
		print self.getKnob('Crazy Number').getValue()

	def checkBoxChanged(self, *args):
		print 'checkBoxChanged'

	def radioChanged(self, *args):
		print 'radioChanged'
		print self.getKnob('how awesome').getValue()

	def listChanged(self, *args):
		print 'listChanged'
		self.getKnob('list').getValue()

	def dynamicListChanged(self, *args):
		print 'dynamicListChanged'
		print self.getKnob('DList').getValue()

	def test(self):
		print 'yay'

	def getData(self):
		data = []
		for f in os.listdir('c:/temp'):
			filename, ext = os.path.splitext(f)
			data.append(['c:/temp', filename, ext])
		return data

	def submit(self):
		print '\nSubmit:\n'
		for knob in self.allKnobs():
			print knob.name + ':', knob.getValue()

		self.getKnob('Resolution').setValue([1080,240])

def main():
	options = {
		'title': 'Test Dialog',
		# 'width': 600,
		# 'height': 400,
		'x': 100,
		'y': 100,
		'knobs': [
			{
				'name': 'heading',
				'dataType': 'heading',
				'value': 'Amazing test form'
			},
			{
				'name': 'name',
				'dataType': 'text',
				'value': 'Robin Hood'
			},
			{
				'name': 'number',
				'dataType': 'int',
				'value': 23
			},
			{
				'name': 'Vec',
				'dataType': 'vec3'
			},
			{
				'name': 'Crazy Number',
				'dataType': 'float',
				'value': 23.4
			},
			{
				'name': 'awesome',
				'dataType': 'checkbox',
				'value': False,
			},
			{
				'name': 'how awesome',
				'dataType': 'radio',
				'value': 'super',
				'options': ['pretty','mostly','super']
			},
			{
				'name': 'awesome level',
				'dataType': 'list',
				'value': '4',
				'options': [1,2,3,4,5]
			},
			{
				'name': 'DList',
				'dataType': 'DynamicList',
				'selectionMode': 'single',
				'options': ['Ab', 'Bv', 'Cx']
			},
			{
				'name': 'asset',
				'dataType': 'AssetPicker',
			},
			{
				'name': 'Resolution',
				'dataType': 'Resolution',
				'value': {
					'width': 960,
					'height': 540,
				}
			},
			# {
			# 	'name': 'input',
			# 	'dataType': 'openFile',
			# 	'value': 'c:/sup.txt',
			# 	'label': 'Pick a file',
			# 	'directory': 'C:/temp/',
			# 	'extension': 'whatever (*.*)'
			# },
		]
	}
	translator.launch(Test, None, options=options)


if __name__ == '__main__':
	main()
