# Maintenance Job for checking software versions

import _winreg
import os
import sys
import itertools
import json
import socket
import traceback

try:
	import updateModules
except:
	sys.exit('could not update, no update modules found')

try:
	import cOS
	import arkInit
	arkInit.init()
except:
	sys.exit('could not update, no arkinit found')

try:
	from deadline import arkDeadline
	ad = arkDeadline.ArkDeadline()
	# checks that this function exists, otherwise update
	print ad.removeSheepFromLimitGroup
except:
	print 'no deadline'
	updateModules.updateModules()
	print 'updated'
	os.system(cOS.normalizePath(r'c:\ie\ark\setup\Setup.pyc'))
	from deadline import arkDeadline
	ad = arkDeadline.ArkDeadline()

try:
	import arkFTrack
	pm = arkFTrack.getPM()
except:
	print 'no ftrack'

sheepName = socket.gethostname()
plugins = ['hbatch', 'vray', 'nuke', 'maya', 'mantra']

extraInfo = {
	'toolsVersion': 'Ex0',
	'username': 'Ex1',
	'name': 'Ex2',
	'errorString': 'Ex3'
}


argsFile = 'S:/config/defaultInstall.json'
with open(argsFile) as f:
	standardSoftwares = json.load(f)
softwareList = standardSoftwares


def checkSoftwareVersions():
	programDict = {}

	# get all the software and versions installed in Maya
	localMachineReg = _winreg.ConnectRegistry(None, _winreg.HKEY_LOCAL_MACHINE)
	programKey = _winreg.OpenKey(localMachineReg, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall', 0, _winreg.KEY_READ)
	for i in itertools.count():
		try:
			subname = _winreg.EnumKey(programKey, i)
		except:
			break

		subkey = _winreg.OpenKey(programKey, subname, 0, _winreg.KEY_READ)

		# Some outputs don't get type cast and its safe to assume they won't be checked when checking software versions
		try:
			name, regtype = _winreg.QueryValueEx(subkey, "DisplayName")
			name = str(name)
		except:
			continue

		try:
			version, regtype = _winreg.QueryValueEx(subkey, "DisplayVersion")
			version = str(version)
		except:
			version = ''

		programDict.update({name:version})
		_winreg.CloseKey(subkey)

	missingSoftwares = []
	wrongVersions = {}
	for key, val in softwareList.iteritems():
		if key not in programDict.keys():
			missingSoftwares.append(key)
		elif val['version'] != str(programDict[key]):
			if '.' in val['version'] and '.' in programDict[key]:
				localVersion = programDict[key].split('.')
				configVersion = val['version'].split('.')
				localVersion = localVersion[0] + '.' + ''.join(localVersion[1:])
				configVersion = configVersion[0] + '.' + ''.join(configVersion[1:])
				if float(localVersion) < float(configVersion):
					wrongVersions.update({key: programDict[key]})
			else:
				wrongVersions.update({key: programDict[key]})

	if len(missingSoftwares) == 0 and len(wrongVersions) == 0:
		return None

	else:
		return missingSoftwares, wrongVersions

def main():
	if updateModules.needsUpdate():
		updateModules.updateModules()
		os.system(cOS.normalizePath(r'c:\ie\ark\setup\Setup.pyc'))
	else:
		print 'tools version up to date'

	try:
		# will only work on artist boxes, where config file exists
		import ftrack_connect.ui.config
		config = ftrack_connect.ui.config.read_json_config()['accounts'][0]

		pm.getSession(api_user=config['api_user'], api_key=config['api_key'])

		userInfo = {
			'name': pm.getName(),
			'username': pm.getUsername()
		}
		print 'user: ' + userInfo['name'] + ' (' + userInfo['username'] + ')'
	except:
		print 'no user info'
		userInfo = {'name': 'none', 'username': 'none'}

	try:
		ad.updateSheepSettings(sheepName, {
			extraInfo['username']: userInfo['username'],
			extraInfo['name']: userInfo['name'],
		})

		ad.updateSheepSettings(sheepName, {extraInfo['toolsVersion']: updateModules.getLatestDirectory(remote=False)})
	except:
		print 'could not update sheep settings'
		pass

	try:
		# add sheep to good software if latest version, otherwise remove from good software
		groups = ad.getSheepSettings(sheepName)
		print groups
		if isinstance(groups, list):
			groups = groups[0]
		groups = groups[u'Grps']
		if updateModules.needsUpdate():
			if u'good-software' in groups:
				groups.remove(u'good-software')
				print ad.setSheepGroups(sheepName, groups)
		else:
			if not u'good-software' in groups:
				groups.append(u'good-software')
				print ad.setSheepGroups(sheepName, groups)
	except:
		print traceback.format_exc()
		print 'could not get sheep settings for: ', sheepName
		# os.system(cOS.normalizePath(r'c:\ie\ark\setup\Setup.pyc'))
		sys.exit('could not get sheep settings for: ' + sheepName)


	# Adds sheep to group based on software result
	result = checkSoftwareVersions()
	if not result:
		print 'Up to Date'
		for data in softwareList.values():
			for t in data['tags']:
				ad.addSheepToLimitGroup(t + '-license', sheepName, blackList=False)

	else:
		missingSoftwares = result[0]
		wrongVersions = result[1]

		for program, data in softwareList.iteritems():
			if program in missingSoftwares or program in wrongVersions.keys():
				for t in data['tags']:
					ad.removeSheepFromLimitGroup(t + '-license', sheepName, blackList=False)
					if t == 'vray':
						ad.removeSheepFromLimitGroup('maya-license', sheepName, blackList=False)
			else:
				for t in data['tags']:
					ad.addSheepToLimitGroup(t + '-license', sheepName, blackList=False)

		errString = ''
		if len(missingSoftwares) > 0:
			errString += 'software missing: ' + ', '.join(missingSoftwares)

		if len(wrongVersions) > 0:
			if errString != '':
				errString += ' and'
			errString += ' wrong versions: ' + str(wrongVersions)

		ad.updateSheepSettings(sheepName, {extraInfo['errorString']: errString})
		sys.exit(errString)


if __name__ == '__main__':
	main()

