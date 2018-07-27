# Python script to install or reinstall local modules from published tools
# Used in batch file install.bat at R:/Assets/Tools/install/install.bat
# Duplicate of this ark/admin/installModules.py, that is not reliant on everything

# Standard modules
import argparse
import shutil
import sys
import os
import re

parser = argparse.ArgumentParser(description='Install/reinstall from published tools')
parser.add_argument('--local', help='Local directory to reinstall to')
parser.add_argument('--master', help='Master directory.')
parser.add_argument('--confirm', action='store_true' , help='Wait for confirmation.')

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
			'weaver'
		]

# Helper function to ask a yes/no question and waits for confirmation
# Waits for user to reply 'y' or 'n'
# Inputs: question - prompt for user
# Outputs: boolean - True if user replies yes, False if user replies No
# raw_input used for Python 2 and input for Python 3
def confirm(question):
 	version = sys.version_info[0]
	prompt = question + ' (y/n): '
	reply = None
	while True:
		try:
			if version is 2:
				reply = raw_input(prompt)
			if version is 3:
				reply = input(prompt)
		except KeyboardInterrupt:
			sys.exit('\n\nCtrl-C, safely exiting.')
		reply = reply.lower().strip()
		if reply in ['y', 'yes']:
			return True
		elif reply in ['n', 'no']:
			return False
		else:
			print '\nPlease enter \'y\' or \'n\''

def main(argv):
	args = parser.parse_args()
	# Note: these do not use globalSettings.SHARED_ROOT because this must run independent
	# of our libraries
	if not args.local:
		if isWindows():
			args.local = 'c:/ie'
		elif isLinux():
			args.local = '/var/ie'
		elif isMac():
			args.local = '/Library/ie'
	if not args.master:
		if isWindows():
			args.master = 'r:/Assets/Tools/install/ie'
		elif isLinux():
			args.master = '/ramburglar/Assets/Tools/install/ie'
		elif isMac():
			args.master = '/Volumes/rambuglar_work/Assets/Tools/install/ie'

	local = normalizeDir(args.local)
	master = normalizeDir(args.master)
	# If this is called, assume first install.
	# Always ask for confirmation
	reply = False
	reply = confirm('\nPreparing to sync modules %s from master %s to local %s.\n' % (modules, master, local) +'Continue?')

	if not reply:
		sys.exit('\nCancelling install, exiting.')
	else:
		for module in modules:
			localModule = local + module
			masterModule = master + module
			# All default modules should be published, but double check
			if (not os.path.isdir(masterModule)):
				raise Exception('Master module %s could not be found. Publish first\n' % (masterModule))

			# Delete local module folder if already exists
			if os.path.isdir(localModule):
				print 'Removing old module %s from %s' % (module, localModule)
				try:
					shutil.rmtree(localModule)
				except Exception as err:
					# If error is "not exists", don't raise, just return
					print 'Error removing %s: %s' % (localModule, err)
					if not os.path.exists(localModule):
						raise err

			print 'Copying module %s from %s to %s\n' % (module, masterModule, localModule)
			try:
				shutil.copytree(masterModule, localModule)
			except Exception:
				raise
		print '\nInstall completed.\n'

# Tiny cOS
##################################################
##################################################
# DO NOT MODIFY, STRAIGHT DUPLICATE of select helpers from cOS.py
##################################################
##################################################
def ensureEndingSlash(path):
	'''
	Ensures that the path has a trailing '/'
	'''

	path = unixPath(path)
	if path[-1] != '/':
		path += '/'
	return path

def normalizeDir(path):
	'''
	Dirs always use forward slashses and have a trailing slash.
	'''
	# lower case drive leters
	if path[1] == ':':
		path = path[0].lower() + path[1:]

	# ensureEndingSlash already makes sure
	# the path is a unixPath
	return ensureEndingSlash(path)

def unixPath(path):
	'''
	Changes backslashes to forward slashes and
	removes successive slashes, ex \\ or \/
	'''
	# lower case drive leters
	if not path:
		return ''
	if len(path) > 1 and path[1] == ':':
		path = path[0].lower() + path[1:]

	# bit hacky, but basically we want to keep
	# :// for http:// type urls
	# so we split on that, replace the slashes in the parts
	# then join it all back together
	parts = path.split('://')
	replaced = [re.sub(r'[\\/]+', '/', p) for p in parts]
	return '://'.join(replaced)

# OS
##################################################
def isWindows():
	'''
	Returns whether or not the machine running the command is Windows.
	'''
	return sys.platform.startswith('win')

def isLinux():
	'''
	Returns whether or not the machine running the command is Windows.
	'''
	return sys.platform.startswith('linux')

def isMac():
	'''
	Returns whether or not the machine running the command is Windows.
	'''
	return sys.platform.startswith('darwin')

if __name__ == '__main__':
	main(sys.argv)
