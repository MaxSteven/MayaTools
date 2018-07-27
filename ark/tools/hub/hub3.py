# Name: Hub
# Author: Shobhit Khinvasara
# Date: 04/07/2017
# import os
# import fnmatch

# import sys

# import psutil

import arkInit
arkInit.init()

import arkUtil
# import cOS

import settingsManager
globalSettings = settingsManager.globalSettings()

import translators
translator = translators.getCurrent()

from translators import QtGui
from translators import QtCore

import baseWidget

# import hubGui

# import caretakerGui

# import updateModules

# import arkToolbar

# import mouseControl

# from caretaker import Caretaker
# caretaker = Caretaker()

# from translators import Events




class Hub(baseWidget.BaseWidget):
	defaultOptions = {
		'title': 'Hub',
		'minimize': True,
		'alwaysOnTop': True,
		'borderless': True,
		'clickToMove': True,
		'knobs': [
			{
				'name': 'Next Monitor',
				'dataType': 'pythonButton',
				'callback': 'nextMonitor'
			},
		]
	}

	# def init(self):
	# 	# kill previously running hubs
	# 	self.currentProcessId = os.getpid()
	# 	hubCount = 0
	# 	print 'killing hubs...'
	# 	for proc in psutil.process_iter():

	# 		if len(cOS.getCmdline(proc)) > 1 \
	# 			and ('Hub' in cOS.getCmdline(proc)[0] \
	# 				or ('python' in cOS.getCmdline(proc)[0] and 'hub.py' in cOS.getCmdline(proc)[1])) \
	# 			and proc.pid != self.currentProcessId:
	# 			for p in proc.get_children(recursive=True):
	# 				p.kill()
	# 			proc.kill()
	# 			hubCount += 1

	# 	print 'Hubs killed:', hubCount

	# 	try:
	# 		self.title = self.options['title'] + ' ' + updateModules.getLatestDirectory(remote=False).split('/')[-1]
	# 		self.setWindowTitle(self.title)
	# 	except Exception:
	# 		pass

	def init(self):
		self.currentMonitor = 1
		self.side = 'left'
		self.moving = False
		self.y = 0

	def postShow(self):
		# enable mouseMoveEvent
		self.setMouseTracking(True)
		qtApp = translator.getQTApp()
		desktop = qtApp.desktop()
		print 'availableGeometry', desktop.availableGeometry()
		print 'numScreens', desktop.numScreens()
		print 'primaryScreen', desktop.primaryScreen()
		for i in range(desktop.numScreens()):
			print 'screen:', i, desktop.screenGeometry(i)
		self.updatePosition(force=True)

	# availableGeometry PySide.QtCore.QRect(0, 0, 1920, 1160)
	# numScreens 4
	# primaryScreen 3
	# screen: 0 PySide.QtCore.QRect(3840, 0, 1280, 720)
	# screen: 1 PySide.QtCore.QRect(1920, 0, 1920, 1200)
	# screen: 2 PySide.QtCore.QRect(-1920, 0, 1920, 1200)
	# screen: 3 PySide.QtCore.QRect(0, 0, 1920, 1200)

	def nextMonitor(self):
		desktop = self.getDesktop()

		self.currentMonitor += 1
		# wrap to monitor count
		self.currentMonitor = self.currentMonitor % desktop.numScreens()
		self.updatePosition(force=True)

	def updatePosition(self, force=False):
		if not (self.moving or force):
			return

		desktop = self.getDesktop()

		# if we're forcing then
		if not force:
			self.currentMonitor = self.getCurrentMonitor()

		area = desktop.screenGeometry(self.currentMonitor)

		actualY = arkUtil.clamp(self.y, 0, area.bottom() - self.height())
		if self.side == 'left':
			self.move(area.left(), actualY)
		else:
			self.move(area.right() - self.width(), actualY)

	def mousePressEvent(self, event):
		print 'mousePressEvent', event.button()
		if event.button() == QtCore.Qt.MouseButton.RightButton:
			self.moving = True
		else:
			self.moving = False

	def mouseReleaseEvent(self, event):
		print 'mouseReleaseEvent'
		self.moving = False

	def mouseMoveEvent(self, event):
		pos = QtGui.QCursor.pos()
		# print 'x: %d, y: %d' % (pos.x(), pos.y())
		self.y = pos.y()
		self.updatePosition()

	# 	self.mainLayout = QtGui.QHBoxLayout()

	# 	self.setLayout(self.mainLayout)

	# 	self.sidebarWidget = hubGui.gui()
	# 	self.sidebarWidget.events.on('updatePressed', lambda: self.updatePressed(silent=False))
	# 	self.sidebarWidget.events.on('logoutPressed', self.logoutPressed)
	# 	self.mainLayout.addWidget(self.sidebarWidget)

	# 	self.caretakerWidget = caretakerGui.gui()
	# 	self.mainLayout.addWidget(self.caretakerWidget)

	# 	self.toolbarWidget = arkToolbar.gui()
	# 	self.mainLayout.addWidget(self.toolbarWidget)

	# 	self.show()

	# def updatePressed(self, silent=True):
	# 	silent = silent or globalSettings.IS_NODE
	# 	latestArkpath = '%s%s/' % (globalSettings.SYSTEM_ROOT, getLatestArkVersion())
	# 	if os.path.isdir(latestArkpath):
	# 		if silent:
	# 			print 'Most recent tools already installed :)'
	# 			return
	# 		return self.showMessage('Most recent tools already installed :)')
	# 	if not updateModules.updateModules():
	# 		if silent:
	# 			raise IOError('Could not update, continuing on currently installed version')
	# 		return self.showError('Could not update, continuing on currently installed version')
	# 	setupCommand = 'python %sark/setup/Setup.pyc' % (globalSettings.ARK_ROOT)
	# 	print cOS.getCommandOutput(setupCommand)
	# 	if not silent:
	# 		self.showMessage("Update complete :) \n Press OK to restart Hub")

	# 	sys.exit()

	# def logoutPressed(self):
	# 	try:
	# 		cOS.removeFile(globalSettings.ARK_CONFIG + 'cookies.dat')
	# 		cOS.removeFile(globalSettings.ARK_CONFIG + 'key.user.dat')
	# 	except OSError as err:
	# 		print 'error removing cookies: '
	# 		print err
	# 	self.caretakerWidget.getKnob('web').widget.load('http://{}/login'.format(globalSettings.DATABASE_ROOT))
	# 	self.caretakerWidget.getKnob('web').cookieJar.setAllCookies([])

	# def closeEvent(self, event):
	# 	if globalSettings.COMPUTER_TYPE != 'developer':
	# 		self.showError('Please do not close hub, it runs sheep and all sorts of other commands :)')
	# 		event.ignore()


def main():
	'''
	Show Window
	'''
	translator.launch(Hub, None)


if __name__ == '__main__':
	main()
