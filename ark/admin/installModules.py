# Python script to install or reinstall local modules from published tools
# Used in batch file install.bat at R:/Assets/Tools/install/install.bat
# Duplicate of this installModules.py, that is not reliant on everything
# at R:/Assets/Tools/install/installModules.py

# Standard modules
import argparse
import shutil
import sys
import os

# Our modules
import arkInit
arkInit.init()
# sys.path append etc upa dir
import cOS
import settingsManager
globalSettings = settingsManager.globalSettings()

parser = argparse.ArgumentParser(description='Install/reinstall from published tools')
parser.add_argument('--local', help='Local directory to reinstall to')
parser.add_argument('--master', help='Master directory.')
parser.add_argument('--confirm', action='store_true' , help='Wait for confirmation.')

modules = [
			'ark',
			'arkMath',
			'arkUtil',
			'cOS',
			'daemon',
			'database',
			'logmont',
			'settingsManager',
			'shepherd',
			'translators',
			'tryout',
			'weaver']

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
	if not args.local:
		args.local = globalSettings.ARK_ROOT
	if not args.master:
		args.master = '%sAssets/Tools/install/ie' % globalSettings.SHARED_ROOT

	local = cOS.normalizeDir(args.local)
	master = cOS.normalizeDir(args.master)

	# If a worker/render computer, with no --confirm flag
	if (globalSettings.COMPUTER_TYPE != 'developer') and (not args.confirm):
		reply = True
	# If a worker/render computer with a --confirm flag
	# Always ask confirmation for developer computer
	else:
		reply = False
		reply = confirm('\nPreparing to sync modules %s from master %s to local %s.\n' % (modules, master, local) +'Continue?')

	if not reply:
		sys.exit('\nCancelling restore, exiting.')
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

if __name__ == '__main__':
	main(sys.argv)
