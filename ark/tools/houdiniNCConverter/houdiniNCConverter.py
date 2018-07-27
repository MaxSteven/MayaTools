
# Steps
# - get location from user
# - export out your hip file as cmd file in a temp location
# 	- hou.hscript('cmd')
# - import the cmd file in fresh houdini scene
# - save file at location

import os
import cOS
import traceback
import subprocess

import translators
translator = translators.getCurrent()
import baseWidget

class NCConverter(baseWidget.BaseWidget):
	defaultOptions = {
			'title': 'Non-Commercial File Converter',
			'width': 600,
			'height': 200,

		'knobs': [
			{
				'name': 'Non-Commercial File',
				'dataType': 'OpenFile',
				'buttonText': '...',
				'extension': '*.hipnc'
			},
			{
				'name': 'Export Location',
				'dataType': 'Directory',
			},
			{
				'name': 'Export',
				'dataType': 'PythonButton',
				'callback':'export'
			},
		]
	}

	appVersion = ''

	def init(self):
		pass

	def postShow(self):
		if translator.getProgram() == 'houdini':
			import hou
			self.appVersion = hou.applicationVersionString()
			name = hou.hipFile.path()
			if cOS.getExtension(name) == 'hipnc':
				self.getKnob('Non-Commercial File').setValue(name)

	def export(self):
		ncFile = self.getKnob('Non-Commercial File').getValue()
		exportLoc = self.getKnob('Export Location').getValue()

		if ncFile == None or ncFile == '':
			self.showError("Please input a valid houdini file.")
			return

		if exportLoc == None or exportLoc == '':
			self.showError("Please input a valid export location.")
			return

		info = cOS.getPathInfo(ncFile)
		name = info['name']

		cmdFile =  'C:/temp/' + name + '.cmd'

		file = "C:\\Program Files\\Side Effects Software\\Houdini 16.5.323\\bin\\hython2.7.exe"
		if self.appVersion != '':
			file = "C:\\Program Files\\Side Effects Software\\Houdini " + self.appVersion + "\\bin\\hython2.7.exe"
		script = "C:\\ie\\ark\\tools\\houdiniNCConverter\\assets\\generateCmd.py"
		options = {
			'ncFile': str(ncFile),
			'cmdFile': str(cmdFile),
			'exportLoc': str(exportLoc)
		}
		subprocess.call([file, script, "-options", str(options)])
		return

def gui():
	return NCConverter()

def launch(docked=False):
	translator.launch(NCConverter, docked=docked)

if __name__=='__main__':
	launch()