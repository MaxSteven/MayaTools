# assume this is only run on render nodes
import os
import time
import sys
import subprocess
import updateModules
import psutil

import arkUtil
import cOS

import settingsManager
globalSettings = settingsManager.globalSettings()

from caretaker import Caretaker
caretaker = Caretaker()


sheepName = 'sheep_' + os.environ.get('ARK_COMPUTER_NAME')
process = False
waitClock = 0

# all time variables are IN SECONDS
# 30 seconds
sleepTime = 30

# wait 5 minutes for sheep to register itself or update modules
waitTime = 5 * 60

# sheep restarted every 2 hours
maxUpTime = 2 * 60 * 60


def run():
	global waitClock

	launchSheep()
	time.sleep(sleepTime)

	while True:
		print time.time(), 'Name:', sheepName
		sheep = caretaker.getEntityFromField('sheep', 'name', sheepName)
		print 'Sheep:', sheep

		if sheep:
			print 'Status:', sheep['status']

			if updateModules.needsUpdate():
				print 'Hub needs update...'
				if sheep['status'] == 'working':
					lazyRestart()
				else:
					stopSheep()
					print 'updating modules...'
					updateModules.updateModules()
					print 'update modules complete, exiting...'
					sys.exit()
			else:
				# no update needed
				if sheep['status'] == 'working' or sheep['status'] == 'idle':
					if launchTime + maxUpTime < time.time():
						print 'sheep has existed for too long, restarting sheep...'
						if sheep['status'] == 'working':
							lazyRestart()
						else:
							stopSheep()
							launchSheep()
					else:
						print 'sheep is fine'
				else:
					# status is offline
					if waitedTooLong():
						print 'sheep has been offline for too long, launching in ' + str(waitTime - waitClock)
						stopSheep()
						launchSheep()

		else:
			print 'could not find sheep with name ', sheepName
			if waitedTooLong():
				print 'still cannot find sheep, launching...'
				stopSheep()
				launchSheep()

		time.sleep(sleepTime)

def lazyRestart():
	print 'lazy restarting sheep...'
	caretaker.createOrUpdateEntityByField('sheep', 'name',
							{'name': sheepName, 'lazyRestart': True})
	print 'lazy restart done'

def waitedTooLong():
	global waitClock

	waitClock += sleepTime
	result = waitClock >= waitTime
	if result:
		waitClock = 0
	return result

def stopSheep():
	print 'killing all pythons...'
	pid = os.getpid()
	for proc in psutil.process_iter():
		pinfo = proc.as_dict(attrs=['pid', 'name'])
		if pinfo['name'] and 'python' in pinfo['name'] and pinfo['pid'] != pid:
			print 'killing: ', pinfo['name']
			proc.kill()
			print 'killed: ', pinfo['name']
	print 'killed all pythons'
	process = False

def launchSheep():
	global waitClock
	global process
	global launchTime

	sheepCmd = 'c:/ie/shepherd/shepherd/sheep.pyc'
	if globalSettings.COMPUTER_TYPE == 'developer':
		sheepCmd = 'c:/ie/shepherd/shepherd/sheep.py'

	print 'launching sheep...'
	waitClock = 0
	launchTime = time.time()
	process = subprocess.Popen([
		'c:/Python27/python.exe',
		sheepCmd,
		'--skipInstall',
		'1',
		'--computerName',
		sheepName
	], creationflags = subprocess.CREATE_NEW_CONSOLE)

	print 'process:', process


if __name__=='__main__':
	args = arkUtil.omitObjectKeys(cOS.getArgs(), '__file__')
	print args
	if 'computerName' in args:
		sheepName = args.get('computerName')

	run()
