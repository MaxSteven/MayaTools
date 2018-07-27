
import arkInit
arkInit.init()

import caretaker
ct = caretaker.getCaretaker()

import os


import translators
translator = translators.getCurrent()
import baseWidget

class CreateShotsGUI(baseWidget.BaseWidget):
	'''
	Purpose:
		Contains logic for all Basic GUI Elements
	'''

	def postShow(self):
		self.getKnob('Drive').editBox.textChanged.connect(self.repopulateList)

	def createShots(self):
		drive = self.getKnob('Drive').getValue()
		folderName = self.getKnob('Directories').widget.selectedItems()[0]
		folderName = folderName.text()

		ct.createShotsFromDirectory(os.path.join(drive, folderName))
		print('shots are being created!')

	def repopulateList(self):
		print('repopulating')
		drive = self.getKnob('Drive').getValue()
		directories = filter(lambda name: (name[0] != '.' and os.path.isdir('r:/' + name + '/Workspaces')), os.listdir(drive))
		directories.sort(key=lambda v: v.upper())
		self.getKnob('Directories').clear()
		self.getKnob('Directories').addItems(directories)





def main():

	directories = os.listdir('r:/')
	directories = filter(lambda name: (name[0] != '.' and os.path.isdir('r:/' + name + '/Workspaces')), directories)
	directories.sort(key=lambda v: v.upper())

	print('directory of dumy project')
	print('is it even here', os.path.isdir('r:/dummy_project/Workspaces'))

	options = {
		'title': 'Create Shots From Directory',
		'width': 250,
		'knobs': [
			{
				'name': 'heading',
				'dataType': 'heading',
				'value': 'Create Shots'
			},
			{
				'name': 'Drive',
				'dataType': 'directory',
				'value': 'r:/',
			},
			{
				'name': 'Directories',
				'dataType': 'listBox',
				'value': directories,
				# 'selectionMode': 'multi'
			},
			{
				'name': 'Create Shots',
				'dataType': 'pythonButton',
				'callback': 'createShots'
			}]

	}
	translator.launch(CreateShotsGUI, None, options=options)



if __name__ == '__main__':
	main()
