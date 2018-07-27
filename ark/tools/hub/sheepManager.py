import os
import psutil
import time

import arkInit
arkInit.init()

import settingsManager
globalSettings = settingsManager.globalSettings()

import translators
translator = translators.getCurrent()

# from translators import QtGui
from translators import QtCore

import idleTime
import baseWidget
import cOS
# import killJobProcesses
from threading import Lock
import updateModules

from caretaker import Caretaker
caretaker = Caretaker()

# The process will be killed by the kernel; this signal cannot be ignored. USE AS LAST RESORT
SIGKILL = 9
# The process is requested to stop running; it should try to exit cleanly
SIGTERM = 15
# sheep restarted every 2 hours IN SECONDS
maxUpTime = 2 * 60 * 60

# Used to prevent timers synchronizing and calling restartSheep at the same time
mutex = Lock()

class SheepManager(baseWidget.BaseWidget):

	# standard sheep UI, knobs etc.
	defaultOptions = {
		'title': 'Sheep Manager',

		'knobs': [
			{
				'name': 'Programs',
				'dataType':'Heading',
				'value': 'Programs'
			},
			{
				'name': 'Program List',
				'dataType': 'ListBox',
				'selectionMode': 'multi'
			},
			{
				'name': 'Delay(mins)',
				'dataType': 'Float',
				'value': 1.0
			},
			{
				'name': 'Set Delay',
				'dataType': 'PythonButton',
				'callback':'setDelay',
			},
			{
				'name': 'Launch Sheep',
				'dataType': 'PythonButton',
			},
			{
				'name': 'Stop Sheep',
				'dataType': 'PythonButton',
			}
		]
	}

	sheepLaunchSignal = QtCore.Signal()
	sheepStopSignal = QtCore.Signal()
	updateModulesSignal = QtCore.Signal()

	def init(self, parent=None):
		if cOS.isWindows():
			cOS.getCommandOutput('%sark/admin/mountDrives_windows.bat' % globalSettings.ARK_ROOT)

		# data from db
		self.sheep = False

		# flag to store process status, True: process running, False: process ended,stopped
		self.idling = False

		# cmd process that launched last sheep
		self.process = False

		# actual python process
		self.sheepProcess = False

		# Checks the idle status of the computer
		self.idleTimer = QtCore.QTimer()

		# Checks the sheep status of the computer
		self.sheepTimer = QtCore.QTimer()

		# get current hub launch time
		self.launchTime = time.time()

		if globalSettings.IS_NODE:
			self.timeout = globalSettings.NODE_IDLE_TIMEOUT
		else:
			self.timeout = globalSettings.SHEEP_IDLE_TIMEOUT

		self.timerCount = 1
		self.restartCount = 1

		self.sheepName = self.getUserComputerName()

	def postShow(self):
		# Only way to pass arguments for callbacks
		self.getKnob('Launch Sheep').widget.clicked.connect(lambda x=True: self.launchSheep(reset=x, saveSettings=x))
		self.getKnob('Stop Sheep').widget.clicked.connect(lambda x=True: self.stopSheep(deleteSettings=x))
		# stores program list based on global settings
		programList = [program['tag'] for program in globalSettings.PROGRAMS]
		self.getKnob('Program List').addItems(programList)

		self.idleTimer = QtCore.QTimer()
		self.sheepTimer = QtCore.QTimer()

		delayPath = globalSettings.ARK_CONFIG + '/hubDelay.dat'
		if os.path.isfile(delayPath):
			with open(delayPath, 'r') as f:
				try:
					# get hubDelay value from file
					self.nextSheepTime = float(f.read())
					self.nextSheepTime = int(self.nextSheepTime)
				except:
					print 'no delayMinutes settings found'
					self.nextSheepTime = 0

		else:
			self.nextSheepTime = 0

		self.idleTimer.start(60 * 1000)
		self.idleTimer.setInterval(60 * 1000)
		self.idleTimer.timeout.connect(self.checkIdle)

		self.sheepTimer.start(30*60*1000)
		# try to run sheep every 30 minutes
		self.sheepTimer.setInterval(30*60*1000)

		self.sheepTimer.timeout.connect(self.checkSheep)

	def checkIdle(self):
		self.idling = idleTime.getIdleTime() > self.timeout

	def checkSheep(self):
		# Check sheep runs every 30 seconds after delay has passed in SECONDS
		if time.time() < self.nextSheepTime:
			return

		# sheep process running, get info from db
		print time.asctime(), 'sheep?'
		print 'Sheep:', self.sheepName
		self.sheep = caretaker.getEntityFromField('sheep', 'name', self.sheepName)
		print 'result:', self.sheep

		# Theoretically prevents the freezing of the GUI
		QtCore.QCoreApplication.processEvents()

		if self.sheep:
			sheep = self.sheep
			print 'status:', sheep['status']
			if updateModules.needsUpdate():
				print 'Hub needs update...'
				if sheep['status'] == 'working':
					self.lazyRestart()
				else:
					# sheep idle, offline or no sheep
					self.stopSheep()
					try:
						self.updateModules()
						# hub will restart sheep manager etc
					except IOError as err:
						print err
						self.launchSheep()
			else:
				if sheep['status'] == 'working' or sheep['status'] == 'idle':
					if self.launchTime + maxUpTime < time.time():
						print 'sheep has existed for too long, restarting sheep...'
						self.restartSheep()
				else:
					# user idle, status offline
					if self.idling:
						print 'user idle, restarting sheep...'
						self.restartSheep()
					elif not self.idleTimer.isActive():
						print 'Starting idleTimer'
						self.idleTimer.start()
		else:
			print 'no sheep found for name ' + self.sheepName
			self.restartSheep()

	# kills sheep process if no sheep
	# returns sheep process, or False
	def checkSheepProcess(self):
		return

		# for proc in psutil.process_iter():
		# 	if self.getSheepPath() in cOS.getCmdline(proc):
		# 		self.sheepProcess = proc
		# 		return self.sheepProcess
		# self.sheepProcess = False
		# return self.sheepProcess

	def killSheepProcess(self):
		if not self.sheepProcess:
			return
		try:
			print 'killing sheep process'
			for p in self.sheepProcess.get_children(recursive=True):
				p.kill()
			self.sheepProcess.kill()
		except psutil._error.NoSuchProcess:
			print 'could not kill sheep, no such process'
		self.sheepProcess = False

	# stop all sheep + child processes immediately
	def stopSheep(self, deleteSettings=False):
		return
		# self.sheepStopSignal.emit()
		# self.sheep = False
		# self.process = False

		# # get actual sheep python process
		# self.checkSheepProcess()
		# # make sure process is killed
		# self.killSheepProcess()

		# # Removes sheep setting file created for the sheep so when restarting it is able to maintain
		# # the initial selections
		# if deleteSettings:
		# 	cOS.removeFile(globalSettings.ARK_CONFIG + 'sheepSettings.dat')

		# self.idleTimer.start()

	def updateModules(self):
		print 'updating modules...'
		self.updateModulesSignal.emit()

	def lazyRestart(self):
		return

		# if self.sheep and self.sheep['status'] == 'working':
		# 	# lazy restart working sheep
		# 	try:
		# 		self.sheep['lazyRestart'] = True
		# 		caretaker.createOrUpdateEntityByField('sheep',
		# 					'lazyRestart',
		# 					{'_id': self.sheep.sheepInfo['_id'], 'lazyRestart': True})
		# 		print 'Lazy restarted at ' + time.strftime("%c") + '\n'
		# 		return True
		# 	except AttributeError:
		# 		# if sheep hasn't registered (network issue?), getting its id will fail
		# 		print 'Lazy restart failed'
		# 		return False
		# return False

	def restartSheep(self):
		return

		# if self.sheep and self.sheep['status'] == 'working':
		# 	if self.lazyRestart():
		# 		return

		# # immediately restart idle/offline sheep
		# self.stopSheep()
		# self.launchSheep(reset=False)
		# print 'Restarted at ' + time.strftime("%c") + '\n'

	def launchSheep(self, reset=False, saveSettings=False):
		return

		# print 'launch sheep'

		# if self.checkSheepProcess():
		# 	print 'Sheep already working'
		# 	return

		# self.idling = False
		# self.sheepLaunchSignal.emit()
		# self.launchTime = time.time()

		# self.programList = self.getProgramList()
		# if saveSettings:
		# 	with open(globalSettings.ARK_CONFIG + 'sheepSettings.dat', 'w') as f:
		# 		f.write((',').join(self.programList))

		# self.process = cOS.startSubprocess(self.getSheepCommand(), env=None, shell=True)

		# # stop timer till process is running
		# self.idleTimer.stop()

	def getProgramList(self):
		programList = self.getKnob('Program List').getValue()
		if not programList:
			if globalSettings.COMPUTER_TYPE == 'transcode':
				programList = ['convert']
			else:
				# set default program list as complete program list if no programs mentioned
				self.programList = [program['tag'] for program in globalSettings.PROGRAMS]
		return programList

	def getSheepPath(self):
		sheepPath = globalSettings.SHEPHERD_ROOT + 'sheep.pyc'
		if not os.path.isfile(sheepPath):
			sheepPath = globalSettings.SHEPHERD_ROOT + 'sheep.py'
		return sheepPath

	def getSheepCommand(self):
		sheepPath = self.getSheepPath()
		try:
			with open(globalSettings.ARK_CONFIG + 'sheepSettings.dat') as f:
				sheepArgs = f.readline().strip()
			sheepCommand =  'python %s --skipInstall 1 --computerName %s --tags %s' % \
				(sheepPath, self.sheepName, sheepArgs)
		except IOError:
			sheepCommand =  'python %s --skipInstall 1 --computerName %s --tags %s' % \
				(sheepPath, self.sheepName, (',').join(self.programList))

		if cOS.isWindows():
			commandString = 'start cmd /c "%s"' % (sheepCommand)
		elif cOS.isLinux():
			commandString = 'xterm -e %s' % (sheepCommand)
		return commandString

	def getUserComputerName(self):
		user = 'none'
		try:
			if globalSettings.COMPUTER_TYPE == 'render':
				user = 'sheep'
			elif globalSettings.COMPUTER_TYPE == 'transcode':
				user = 'TC'
			else:
				userInfo = caretaker.getUserInfo()
				if userInfo:
					user = userInfo.get('username')
				else:
					# no user found
					if globalSettings.COMPUTER_TYPE == 'developer':
						user = 'dev'
		except Exception as err:
			print err

		userComputerName = user + '_' + os.environ.get('ARK_COMPUTER_NAME')

		if self.options.get('nameSuffix'):
			userComputerName += '_' + str(self.sheep.options['nameSuffix'])
		return userComputerName

	# sets delay in MINUTES based on value in delayMinutes text box
	def setDelay(self):
		delayMinutes = self.getKnob('Delay(mins)').getValue()
		delayMinutes = max(delayMinutes, 1)

		#  In case people use an arbitrary infinite delayMinutes, max is 12 hours
		if delayMinutes > 720:
			delayMinutes = 720

		with open(globalSettings.ARK_CONFIG + '/hubDelay.dat', 'w') as f:
			# next sheep time is current time + delay time in SECONDS
			self.nextSheepTime = delayMinutes * 60 + time.time()
			f.write(str(self.nextSheepTime))

def gui():
	return SheepManager()

def launch():
	translator.launch(SheepManager)

if __name__=='__main__':
	launch()
