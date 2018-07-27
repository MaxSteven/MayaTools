# Python script to update local modules using folder sync with published tools
# Used in batch file update.bat at C:/ark/update.bat

# Standard modules
import argparse
import os
import zipfile
import shutil
# Our modules
import arkInit
arkInit.init()
import arkUtil
import cOS
import settingsManager
globalSettings = settingsManager.globalSettings()

parser = argparse.ArgumentParser(description='Update modules using folderSync')
parser.add_argument('--local', help='Local directory to sync modules to. Default C:/ie')
parser.add_argument('--master', help='Master directory to sync modules from. Default R:/Assets/Tools/install/ie')
parser.add_argument('--force', action='store_true' , help='Skip confirmation.')
parser.add_argument('--quiet', action='store_true' , help='(optional) Reduce output. Default verbose.')
parser.add_argument('--noSetup', action='store_true' , help='Run setup after copying modules')

modules = [
			'ark',
			'arkMath',
			'arkUtil',
			'cOS',
			'database',
			'logmont',
			'settingsManager',
			'shepherd',
			'translators',
			'tryout',
			'weaver']

defaultMasterLocation = '%s/Assets/Tools/install/' % globalSettings.RAMBURGLAR
defaultLocalLocation = globalSettings.SYSTEM_ROOT

def getLatestDirectory(remote=True):
	if remote:
		versionsPath = defaultMasterLocation
	else:
		versionsPath = globalSettings.SYSTEM_ROOT
	installVersions =  cOS.getFiles(path=versionsPath,
		folderIncludes=['ie_v*'],
		fileExcludes=['*'],
		folderExcludes=['*'],
		includeAfterExclude=True
		)
	installVersions = arkUtil.sort(installVersions)
	if installVersions:
		return installVersions[-1]
	else:
		return False

def getLocalFromLatestDirectory():
	local = defaultLocalLocation
	latestDirectory = getLatestDirectory()
	if not latestDirectory:
		return False

	masterBaseName = latestDirectory.split('/')[-1]
	local += masterBaseName
	return local

def needsUpdate():
	localDirectory = getLocalFromLatestDirectory()
	if localDirectory:
		return globalSettings.COMPUTER_TYPE != 'developer' and \
			not os.path.isdir(cOS.normalizeDir(localDirectory))

	return False

def updateModules(local=getLocalFromLatestDirectory(), master=getLatestDirectory()):
	if os.path.isdir(globalSettings.ARK_ROOT + '/ark/.git'):
		return False

	if not master:
		print 'Could not get latest remote directory, will try again later'
		return False

	if not os.path.isfile(cOS.normalizeDir(master) + 'completed.dat'):
		print 'Incomplete release, will try again later'
		return False

	local = cOS.normalizeDir(local)
	master = cOS.normalizeDir(master)
	localZip = cOS.normalizeDir(local)[:-1] + '.zip'
	# copy zip to temp folder bc permissions
	localZip = localZip.replace('ie_v', 'temp/ie_v')
	cOS.makeDir(os.path.dirname(localZip))
	masterZip = cOS.normalizeDir(master)[:-1] + '.zip'

	if os.path.isfile(masterZip):
		print 'Copying {} to {}'.format(masterZip, localZip)
		shutil.copyfile(masterZip, localZip)
		print 'Unpacking {} to {}'.format(localZip, local)
		with zipfile.ZipFile(localZip,'r') as z:
			z.extractall(local)
		cOS.removeFile(localZip)
	else:
		cOS.copyTree(master, local)

	if cOS.isWindows():
		# Have to replace / with \\ in windows because / is considered a switch chracter
		print cOS.getCommandOutput('rmdir /s /q %sie' % (globalSettings.SYSTEM_ROOT.replace('/', '\\')))
		# mklink link target
		print cOS.getCommandOutput('mklink /d %sie %s' % (globalSettings.SYSTEM_ROOT.replace('/', '\\'), local.replace('/', '\\')))
	elif cOS.isLinux():
		cOS.getCommandOutput('rm -rf %sie' % (globalSettings.SYSTEM_ROOT))
		# ln target link
		cOS.getCommandOutput('ln -s %s %sie' %(local, globalSettings.SYSTEM_ROOT))
	print '\nUpdate modules completed.\n'
	return True

if __name__ == '__main__':
	args = parser.parse_args()

	if args.local and not args.master:
		args.master = os.path.join(
			defaultMasterLocation,
			args.local.split('/')[-1]
		)
	elif args.master and not args.local:
		args.local = os.path.join(
			defaultLocalLocation,
			args.master.split('/')[-1]
		)
	elif not args.master and not args.local:
		args.local = getLocalFromLatestDirectory()
		args.master = getLatestDirectory()

	if not args.force:
		print 'Copy {} to {}?'.format(args.master, args.local)
		confirm = raw_input('Continue? (y/n)')
		if not confirm == 'y':
			print 'Update canceled.'
			exit()

	updateModules(local=args.local, master=args.master)

	if not args.noSetup:
		print 'Running setup...'
		setupCommand = 'python %sark/setup/Setup.pyc' % (globalSettings.ARK_ROOT)
		print cOS.getCommandOutput(setupCommand)

	print 'Update done.'
