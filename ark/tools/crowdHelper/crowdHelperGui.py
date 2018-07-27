
import os

import arkInit
arkInit.init()

import translators
translator = translators.getCurrent()
from translators import QtGui

import knobs
import baseWidget

import crowdHelper


options = {
	'title': 'Crowd Helper',
	'width': 460,
	'height': 640,
	# 'x': 100,
	# 'y': 100,
	# 'margin': '0 0 0 0',
	'knobs': [
		{
			'name': 'heading',
			'dataType': 'heading',
			'value': 'Crowd Helper'
		},
	]
}

peopleRoot = 'Q:/Assets/MODELS/MODELS_V2/Humans/Crowd_People_Modo/Crowd_Rigged/'


class CrowdHelper(baseWidget.BaseWidget):

	def init(self):
		# people picker
		self.personList = knobs.ListBox('Existing People')
		self.addKnob(self.personList)

		# people picker
		self.newName = knobs.Text('New Name')
		# refresh
		options = {
			'callback': 'postShow',
		}
		knob = knobs.PythonButton('Refresh List', options=options)
		self.addKnob(knob)

		# new name
		self.addKnob(self.newName)

		# duplicate
		options = {
			'callback': 'duplicate',
		}
		knob = knobs.PythonButton('Duplicate Person', options=options)
		self.addKnob(knob)

		# openFolder
		options = {
			'callback': 'openFolder',
		}
		knob = knobs.PythonButton('Open Folder', options=options)
		self.addKnob(knob)

	def postShow(self):
		self.personList.clear()
		self.existingPeople = os.listdir(peopleRoot)
		self.existingPeople.sort()
		self.personList.addItems(self.existingPeople)
		self.personList.widget.clicked.connect(self.setPerson)

	def setPerson(self):
		self.newName.widget.setText(self.personList.widget.currentItem().text())

	def showError(self, text):
		errorMessage = QtGui.QMessageBox(self)
		errorMessage.setText(text)
		errorMessage.resize(300, 300)
		errorMessage.setWindowTitle('Error')
		errorMessage.exec_()

	def duplicate(self):
		newName = self.newName.widget.text().strip()
		if not newName:
			return self.showError('Enter a name')

		if newName in self.existingPeople:
			return self.showError('Name already exists')

		basePerson = self.personList.widget.currentItem().text()
		crowdHelper.duplicatePerson(peopleRoot, basePerson, newName)

	def openFolder(self):
		folderPath = peopleRoot + self.newName.widget.text().strip()
		os.system('explorer ' + folderPath.replace('/','\\'))



def gui(parent=None):
	return baseWidget.BaseWidget(parent=parent, options=options)

def main():
	translator.launch(CrowdHelper, options=options)


if __name__ == '__main__':
	main()
