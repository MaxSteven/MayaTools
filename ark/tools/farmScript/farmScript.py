import arkInit
arkInit.init()

import arkUtil

import os
import cOS
import deadline

currentApp =  os.environ.get('ARK_CURRENT_APP')

import translators
translator = translators.getCurrent()

import baseWidget

import arkFTrack
pm = arkFTrack.getPM()

import settingsManager
globalSettings = settingsManager.globalSettings()

class FarmScript(baseWidget.BaseWidget):
	defaultOptions = {
			'title': 'Script-O-Farm',
			'width': 600,
			'height': 500,

			'knobs': [
				{
					'name': 'Input Files',
					'dataType': 'Text',
					'multiline': True,
				},
				{
					'name': 'Python Script',
					'dataType': 'openFile',
					'value': 'S:/custom/scripts/Jobs/testMayaJob.py',
				},
				{
					'name': 'Submit to Farm',
					'dataType': 'PythonButton',
					'callback': 'submitToFarm'
				}
			]
		}

	def init(self):
		pass

	def postShow(self):
		pass

	def submitToFarm(self):
		files = [f.strip() for f in self.getKnob('Input Files').getValue().split('\n') if f]

		pythonScript = self.getKnob('Python Script').getValue()

		if not pythonScript.endswith('.py') or not os.path.isfile(pythonScript):
			self.showMessage('Please select a valid python script!')
			return

		ext = None
		executable = None
		limitGroups = None

		if currentApp == 'maya':
			ext = ('.ma', '.mb')
			executable = globalSettings.MAYA_PYTHON_EXE
			limitGroups = 'maya-license'
			print 'you are using maya with extension(s) {} and executable {}'.format(ext, executable)
		elif currentApp == 'houdini':
			ext = ('.hip')
			executable = globalSettings.HYTHON_EXE
			limitGroups = 'hbatch-license'
			print 'you are using houdini with extension(s) {} and executable {}'.format(ext, executable)
		elif currentApp == 'nuke':
			ext = ('.nk')
			executable = globalSettings.NUKE_PYTHON_EXE
			limitGroups = 'nuke-license'
			print 'you are using nuke with extension(s) {} and executable {}'.format(ext, executable)
		else:
			self.showMessage('"{}" is not supported by this application'.format(currentApp))
			return

		for f in files:
			f = cOS.normalizePath(f)
			if self.isValidFile(f, ext):
				self.sendToFarm(f, executable, pythonScript, limitGroups)
				print f, 'is a valid file!'
			else:
				print f, 'is not a valid file!'

	def isValidFile(slef, file, ext):
		return os.path.isfile(file) and file.endswith(ext)

	def sendToFarm(self, filePath, executable, pythonScript, limitGroups):
		self.arkDeadline = deadline.arkDeadline.ArkDeadline()
		pathInfo = cOS.getPathInfo(filePath)
		name = pathInfo['name']

		jobInfo = {
			'Name': name,
			'BatchName': name,
			'Plugin': 'CommandLine',
			'priority': 70,
			'LimitGroups': limitGroups,
			'Group': 'good-software',
			'MachineLimit': 0,
		}

		pluginInfo = {
			'SceneFile': pythonScript,
			'Executable': executable,
			'Shell': 'default',
			'ShellExecute': False,
			'SingleFramesOnly': True
		}

		submittedInfo = self.arkDeadline.submitJob(jobInfo, pluginInfo)
		jobID = submittedInfo.get('_id')

		self.arkDeadline.updateJobData(jobID, {
			'Props.PlugInfo.Arguments': pythonScript + ' ' + filePath
		})

def gui():
	return FarmScript()

def launch(docked=False):
	translator.launch(FarmScript, docked=docked)

if __name__=='__main__':
	launch()
