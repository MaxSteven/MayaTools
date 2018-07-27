# Name: Hub
# Author: Shobhit Khinvasara
# Date: 04/07/2017
import os
import fnmatch

import sys

import psutil

import arkInit
arkInit.init()

import cOS

import settingsManager
globalSettings = settingsManager.globalSettings()

import translators
translator = translators.getCurrent()

from translators import QtGui

import baseWidget

import hubGui

import caretakerGui

import updateModules

import arkToolbar

from caretaker import Caretaker
caretaker = Caretaker()

# from translators import Events

class Hub(baseWidget.BaseWidget):
	defaultOptions = {
		'title': 'Hub',
		'minimize': True,
	}

	def init(self):
		# kill previously running hubs
		self.currentProcessId = os.getpid()
		hubCount = 0
		print 'killing hubs...'
		for proc in psutil.process_iter():

			if len(cOS.getCmdline(proc)) > 1 \
				and ('Hub' in cOS.getCmdline(proc)[0] \
					or ('python' in cOS.getCmdline(proc)[0] and 'hub.py' in cOS.getCmdline(proc)[1])) \
				and proc.pid != self.currentProcessId:
				for p in proc.get_children(recursive=True):
					p.kill()
				proc.kill()
				hubCount += 1

		print 'Hubs killed:', hubCount

		try:
			self.title = self.options['title'] + ' ' + updateModules.getLatestDirectory(remote=False).split('/')[-1]
			self.setWindowTitle(self.title)
		except Exception:
			pass

	def postShow(self):
		self.mainLayout = QtGui.QHBoxLayout()

		self.setLayout(self.mainLayout)

		self.sidebarWidget = hubGui.gui()
		self.sidebarWidget.events.on('updatePressed', lambda: self.updatePressed(silent=False))
		self.sidebarWidget.events.on('logoutPressed', self.logoutPressed)
		self.mainLayout.addWidget(self.sidebarWidget)

		self.caretakerWidget = caretakerGui.gui()
		self.mainLayout.addWidget(self.caretakerWidget)

		self.toolbarWidget = arkToolbar.gui()
		self.mainLayout.addWidget(self.toolbarWidget)

		self.show()

	def updatePressed(self, silent=True):
		silent = silent or globalSettings.IS_NODE
		latestArkpath = '%s%s/' % (globalSettings.SYSTEM_ROOT, getLatestArkVersion())
		if os.path.isdir(latestArkpath):
			if silent:
				print 'Most recent tools already installed :)'
				return
			return self.showMessage('Most recent tools already installed :)')
		if not updateModules.updateModules():
			if silent:
				raise IOError('Could not update, continuing on currently installed version')
			return self.showError('Could not update, continuing on currently installed version')
		setupCommand = 'python %sark/setup/Setup.pyc' % (globalSettings.ARK_ROOT)
		print cOS.getCommandOutput(setupCommand)
		if not silent:
			self.showMessage("Update complete :) \n Press OK to restart Hub")

		sys.exit()

	def logoutPressed(self):
		try:
			cOS.removeFile(globalSettings.ARK_CONFIG + 'cookies.dat')
			cOS.removeFile(globalSettings.ARK_CONFIG + 'key.user.dat')
		except OSError as err:
			print 'error removing cookies: '
			print err
		self.caretakerWidget.getKnob('web').widget.load('http://{}/login'.format(globalSettings.DATABASE_ROOT))
		self.caretakerWidget.getKnob('web').cookieJar.setAllCookies([])

	def closeEvent(self, event):
		if globalSettings.COMPUTER_TYPE != 'developer':
			self.showError('Please do not close hub, it runs sheep and all sorts of other commands :)')
			event.ignore()

def getLatestArkVersion():
	result =[]
	for filename in os.listdir(globalSettings.SHARED_ROOT + '/Assets/Tools/install'):
		if fnmatch.fnmatch(filename, 'ie_v*'):
			result.append(filename)
	result.sort()
	return result[-1]

def main():
	'''
	Show Window
	'''
	translator.launch(Hub, None)


if __name__ == '__main__':
    main()
