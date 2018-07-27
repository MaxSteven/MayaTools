import arkInit
arkInit.init()

import cOS

import settingsManager
globalSettings = settingsManager.globalSettings()

import translators
translator = translators.getCurrent()
from translators import QtCore, QtGui

from math import trunc

import baseWidget

# GUI
##################################################
options = {
	'title': 'Wacom Settings',
	'width': 460,
	'height': 200,
	'knobs': [
		{
			'name': 'touch enabled',
			'dataType': 'checkbox',
			'callback' : 'switchTouch'
		},
		{
			'name': 'forced proportions',
			'dataType': 'checkbox',
			'callback': 'forcedProportions'
		},
		{
			'name': 'map proportions',
			'dataType': 'list',
			'options': ['Top', 'Bottom'],
			'value': 'Top'
		},
		{
			'name': 'Save',
			'dataType': 'pythonButton',
			'callback': 'save'
		}
	]
}

class WacomSettings(baseWidget.BaseWidget):
	def init(self):
		print globalSettings.USER_ROOT
		if cOS.isWindows():
			return self.showError("Use Windows Wacom Settings")

		self.devices = {}
		self.dimensions = []
		self.scale = None
		self.heightDifference = None
		output = cOS.getCommandOutput('xsetwacom --list devices')
		self.parse(output[0])
		if 'stylus' not in self.devices.keys():
			return self.showError('No tablet detected')


	def parse(self, input):
		unFilteredDevices = input.splitlines()
		for unfilteredDevice in unFilteredDevices:
			name = unfilteredDevice.strip().rsplit('\t', 1)
			id = name[0].rsplit(None, 1)[-1]
			type = name[1].rsplit(None, 1)[-1]
			self.devices[type] = id

	def postShow(self):
		if 'stylus' not in self.devices.keys():
			self.close()
			return False
		self.getKnob('forced proportions').on('changed', self.forcedProportions)
		self.getKnob('touch enabled').on('changed', self.switchTouch)
		self.getKnob('map proportions').on('changed', self.mapProportions)
		self.resetArea()
		getAreaCommand = [
				'xsetwacom get',
				self.devices['stylus'],
				'area']
		self.dimensions = cOS.getCommandOutput(' '.join(getAreaCommand))[0].strip().split()
		self.forcedProportions()
		self.switchTouch()
		self.calculateDisplayFactors()

	def switchTouch(self, *args):
		if 'touch' in self.devices.keys():
			commandPrefix = 'xsetwacom set ' + self.devices['touch'] + ' Touch '
			if self.getKnob('touch enabled').getValue():
				cOS.getCommandOutput(commandPrefix + 'on')
			else:
				cOS.getCommandOutput(commandPrefix + 'off')

	def forcedProportions(self, *args):
		isForcedProportions = self.getKnob('forced proportions').getValue()
		if isForcedProportions:
			self.showKnob('map proportions')
			self.mapProportions()
		else:
			self.hideKnob('map proportions')
			self.resetArea()

	def mapProportions(self, *args):
		orientation = self.getKnob('map proportions').getValue()
		print self.heightDifference
		if orientation == 'Top':
			for device in self.devices:
				if device != 'pad':
					cOS.getCommandOutput(self.topProportionCommand(device))
		else:
			for device in self.devices:
				if device != 'pad':
					cOS.getCommandOutput(self.bottomProportionCommand(device))

	def resetArea(self):
		for key in self.devices:
			if key != 'pad':
				cOS.getCommandOutput(self.resetAreaCommand(key))

	def resetAreaCommand(self, device):
		return 'xsetwacom set ' + self.devices[device] + ' ResetArea'

	def topProportionCommand(self, device):
		command = [
				'xsetwacom set',
				self.devices[device],
				'Area 0 0',
				self.dimensions[2],
				str(int(self.dimensions[3]) - self.heightDifference)
				]
		return ' '.join(command)
	def bottomProportionCommand(self,device):
		command = [
				'xsetwacom set',
				self.devices[device],
				'Area 0',
				str(self.heightDifference),
				self.dimensions[2],
				self.dimensions[3]
				]
		return ' '.join(command)

	def calculateDisplayFactors(self):
		rec = QtCore.QRect()
		wholeRec = QtCore.QRect()
		for i in range(QtGui.QApplication.desktop().screenCount()):
			rec = QtGui.QApplication.desktop().screenGeometry(i)
			wholeRec = wholeRec.united(rec)
		self.scale =  float(self.dimensions[2]) / float(wholeRec.width())
		self.heightDifference = trunc(float(self.dimensions[3]) -
									  (float(wholeRec.height()) * self.scale))

	def save(self):
		if 'stylus' not in self.devices.keys():
			self.showError('No tablet detected')
			return

		with open(globalSettings.USER_ROOT + 'startup', 'w') as target:
			target.write('#!/bin/bash\n\n')
			target.write(self.currentAreaCommand())
			if 'touch' in self.devices.keys():
				commandPrefix = 'xsetwacom set ' + self.devices['touch'] + ' Touch '
				if self.getKnob('touch enabled').getValue():
					target.write(commandPrefix + 'on\n')
				else:
					target.write(commandPrefix + 'off\n')
			target.write('\n')
			target.write('python %s/ark/startup.py\n' % globalSettings.ARK_ROOT)

	def currentAreaCommand(self):
		getAreaCommand = [
				'xsetwacom get',
				self.devices['stylus'],
				'area']
		currentArea = cOS.getCommandOutput(' '.join(getAreaCommand))[0]
		print currentArea
		result = ''
		for device in self.devices:
			if device != 'pad':
				setAreaCommand = [
						'xsetwacom set',
						self.devices[device],
						currentArea + '\n'
						]
				result += ' '.join(setAreaCommand)
		return result

	def closeEvent(self, event):
		if 'stylus' in self.devices.keys():
			self.save()
		super(WacomSettings, self).closeEvent(event)

def gui():
	return WacomSettings(options=options)

def launch():
	translator.launch(WacomSettings, options=options)

if __name__ == '__main__':
	launch()

