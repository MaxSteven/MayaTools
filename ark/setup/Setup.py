import os
import shutil
import sys
import re
from distutils import dir_util

import cOS_tiny

# matching python packages
packageRe = re.compile(r'^([a-zA-Z0-9-.]+)')

# usage: Setup.py [--noPrograms] [--deadlineOnly] [--useComputerName]

# Main setup class
class Setup(object):

	def __init__(self, options={}):
		self.options = options

	def setup(self):
		'''
		Main ark Installation
		'''
		print '\nArk Installation'

		# Verify root for Linux
		if cOS_tiny.isLinux():
			try:
				testFile = '/usr/ark_permissionTestFile'
				open(testFile,'w+')
				os.remove(testFile)
			except:
				raise Exception('Please run install with sudo access on Linux')

		self.getPythonPaths()
		self.getArkRoot()
		self.copyArkInit()

		self.installPip()
		self.installEZSetup()
		self.setEnvironmentVariables()
		self.setTempFolder()
		self.scheduleRemountDrives()

		self.installPythonPackages()
		self.ensureComputerName()
		self.makeConfig()
		self.cleanFiles()

		# don't install software if computer is in nyc
		if not os.getenv('IE_LOCATION') == 'NY':
			self.programSetup()
		else:
			print 'Computer is NY, skipping program installation'

		self.ftrackSetup()

		self.startScheduledTask()

		print '\n\nArk Installation complete!'
		print '\nNice work! (like you did anything..)'

	def getPythonPaths(self):
		# get the system python directory
		if cOS_tiny.isWindows():
			self.arkPython = cOS_tiny.normalizeDir(sys.exec_prefix)
			# get the site packages within that
			self.arkPythonLib = self.arkPython + 'lib/site-packages/'
			self.arkPython += 'python.exe'
		elif cOS_tiny.isMac() or cOS_tiny.isLinux():
			self.arkPython = cOS_tiny.normalizeDir(sys.exec_prefix)
			# get the site packages within that
			self.arkPythonLib = self.arkPython + 'lib/python2.7/site-packages/'
			self.arkPython += 'bin/python'

	def getArkRoot(self):
		# arkRoot is hardcoded because symlinks dont behave the same in Linux as in Windows
		# and the root will now be the same across both Linux and Windows
		self.arkRoot = ''
		if cOS_tiny.isWindows():
			self.arkRoot = 'c:/ie'
		elif cOS_tiny.isLinux():
			self.arkRoot = '/ie'
		self.arkRoot = cOS_tiny.normalizeDir(self.arkRoot)

		print 'ARK_ROOT:', self.arkRoot

	def copyArkInit(self):
		print 'Copying Ark Init'
		arkInitPath = self.arkRoot + 'ark/setup/arkInit'
		installPath = self.arkPythonLib + 'arkInit'

		try:
			shutil.rmtree(installPath)
		except:
			if os.path.isdir(installPath):
				raise Exception('Failed to remove: ' + installPath)

		print '\nCopying: {0} to {1}'.format(
			arkInitPath, installPath)
		shutil.copytree(arkInitPath, installPath)

	def installPip(self):
		# Check if pip already installed
		out, err = cOS_tiny.getCommandOutputParsed(['pip', '--version'])

		if out and \
			'pip ' in out.lower() and \
			' from ' in out.lower() and \
			not err:
			print '\npip: already installed.'
			return
		pipPath = self.arkRoot + 'ark/setup/install_pip.pyc'
		out, err = cOS_tiny.getCommandOutputParsed(['python', pipPath])

		if err:
			print '\nerror:\n', err
		else:
			print '\nout:\n', out
			# adding pip path to PATH
			if cOS_tiny.isWindows():
				os.environ['PATH'] += os.pathsep + 'C:/Python27/Scripts'
			print '\nPip installed.\n'

	def installEZSetup(self):
		# Check if easy_install already installed
		out, err = cOS_tiny.getCommandOutputParsed(['easy_install', '--version'])
		if out and 'setuptools ' in out.lower() and not err:
			print '\neasy_install: already installed.\n'
			return
		EZpath = self.arkRoot + 'ark/setup/install_ez_setup.pyc'

		out, err = cOS_tiny.getCommandOutputParsed(['python', EZpath])
		if err:
			print '\nerror:\n', err
		else:
			print '\nout:\n', out

	def setEnvironmentVariables(self):
		sys.path.append(self.arkRoot)

		pythonPathEnv = [
			'%s' % self.arkRoot,
			'%sark/setup/sitePackages/2.7' % self.arkRoot,
			'%sark/setup' % self.arkRoot,
			'%sark/lib' % self.arkRoot,
			'%sark/ui' % self.arkRoot,
			'%sark/tools' % self.arkRoot,
			'%sark/admin' % self.arkRoot,
			'%sark/programs' % self.arkRoot,
			'%ssettingsManager' % self.arkRoot,
			'%scoren/autoBackup' % self.arkRoot,
			'%sarkFTrack/Lib/site-packages' % self.arkRoot,
			'%sftrack-connect/source' % self.arkRoot,
			'%sftrack-connect-nuke/source' % self.arkRoot,
			'%sftrack-connect-foundry/source' % self.arkRoot,
			'%sftrack-connect-maya/source' % self.arkRoot,
			'%sftrack-connect-houdini/source' % self.arkRoot,
			]

		# fix: should eventually move to user's home directory
		if cOS_tiny.isLinux():
			usernames = os.listdir('/home')
			# fix: shouldn't just default to first user, but works currently
			self.osUser = usernames[0]
			self.userRoot = '/home/' + self.osUser + '/'
			self.configDir = cOS_tiny.normalizeDir(
				self.userRoot + 'config/')
			cOS_tiny.makeDirs(self.configDir)
			self.ramburglar = '/ramburglar/'
		elif cOS_tiny.isMac():
			# fix: need osuser
			self.osUser = 'taco'
			self.userRoot = cOS_tiny.normalizeDir(os.path.expanduser('~'))

		# if cOS_tiny.isWindows():
		else:
			if not os.environ.get('HOME'):
				cOS_tiny.setEnvironmentVariable('HOME', 'C:\\Users\\' + cOS_tiny.getOSUsername())
			self.configDir = cOS_tiny.ensureEndingSlash(os.environ['HOME']) + 'config/'
			self.ramburglar = 'R:/'


		# set up ark's environment variables
		env = {
			'ROOT': '/ramburglar/',
			'ARK_ROOT': cOS_tiny.normalizeDir(self.arkRoot),
			'ARK_CONFIG': cOS_tiny.normalizeDir(self.configDir),
			'ARK_PYTHON': cOS_tiny.unixPath(self.arkPython),
			'ARK_PYTHONLIB': cOS_tiny.normalizeDir(self.arkPythonLib),
			'PYTHONPATH': os.pathsep.join(pythonPathEnv),
			'FTRACK_SERVER': 'https://ingenuity-studios.ftrackapp.com',
			'MAYA_DISABLE_CIP': 1,
			'MAYA_DISABLE_CLIC_IPM': 1,
			'MAYA_DISABLE_CER': 1,
			'MAYA_PRESET_PATH': cOS_tiny.normalizeDir('{}Assets/Tools/Maya/presets/'.format(self.ramburglar))
		}

		# update with ftrack variables
		env.update({
			'FTRACK_CONNECT_NUKE': cOS_tiny.normalizeDir('%sftrack-connect-nuke' % self.arkRoot),
			'FTRACK_CONNECT_MAYA': cOS_tiny.normalizeDir('%sftrack-connect-maya' % self.arkRoot),
			'FTRACK_CONNECT_HOUDINI': cOS_tiny.normalizeDir('%sftrack-connect-houdini' % self.arkRoot),
			'NUKE_USE_FNASSETAPI': 1,
		})

		ftrackEventPlugins = [
			cOS_tiny.normalizeDir('%sarkFTrack/plugin/hook' % self.arkRoot),
			cOS_tiny.normalizeDir('%sresource/hook' % env['FTRACK_CONNECT_NUKE']),
			cOS_tiny.normalizeDir('%sresource/hook' % env['FTRACK_CONNECT_MAYA']),
			cOS_tiny.normalizeDir('%sresource/hook' % env['FTRACK_CONNECT_HOUDINI']),
		]

		env.update({
			'FTRACK_CONNECT_NUKE_PLUGINS_PATH': cOS_tiny.normalizeDir('%sresource' % env['FTRACK_CONNECT_NUKE']),
			'FTRACK_CONNECT_MAYA_PLUGINS_PATH': cOS_tiny.normalizeDir('%sresource' % env['FTRACK_CONNECT_MAYA']),
			'FTRACK_CONNECT_HOUDINI_PLUGINS_PATH': cOS_tiny.normalizeDir('%sresource' % env['FTRACK_CONNECT_HOUDINI']),
			'FTRACK_EVENT_PLUGIN_PATH': (';' if cOS_tiny.isWindows() else ':').join(ftrackEventPlugins)
		})

		for k,v in env.iteritems():
			print k + ':', v
			cOS_tiny.setEnvironmentVariable(k, v)

		if cOS_tiny.isLinux():
			os.system('chown -R %s:%s %s' % (self.osUser, self.osUser, env['ARK_CONFIG']))

	def setTempFolder(self):
		if 'ARK_TEMP' in os.environ:
			tempFolder = os.environ.get('ARK_TEMP')
		elif cOS_tiny.isWindows():
			tempFolder = 'c:/temp/'
		elif cOS_tiny.isMac() or cOS_tiny.isLinux():
			tempFolder = self.userRoot + 'temp/'

		# ensure the temp directory exists
		cOS_tiny.makeDirs(tempFolder)
		if cOS_tiny.isLinux():
			os.system('chown -R %s:%s %s' % (self.osUser, self.osUser, tempFolder))

	def scheduleRemountDrives(self):
		if cOS_tiny.isWindows():
			# make sure drives are mounted
			if os.getenv('IE_LOCATION') == 'NY':
				out, err = cOS_tiny.getCommandOutput('%sark/admin/mountDrives_windows_ny.bat' % self.arkRoot)
			else:
				out, err = cOS_tiny.getCommandOutput('%sark/admin/mountDrives_windows.bat' % self.arkRoot)
			if err:
				print 'Error mounting drives:', err

			# remove hub from startup folder (might have been added in previous attempt)
			oldHubShortcuts = cOS_tiny.getFiles('C:/Users/' + cOS_tiny.getOSUsername() + '/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup', fileIncludes=['hub','sheep'])
			for shortcut in oldHubShortcuts:
				print 'removing startup hub:', shortcut
				cOS_tiny.removeFile(shortcut)

			# delete hub scheduled task (might have been added in previous attempt)
			if not os.system('schtasks /query /tn Hub >NUL 2>&1'):
				print 'removing hub scheduled task'
				os.system('schtasks /delete /tn Hub /f')

			# change registry settings to share network drives between user and administrator
			if os.system('reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" /v EnableLinkedConnections >NUL 2>&1'):
				print 'adding linked connections key'
				os.system('reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" /v EnableLinkedConnections /d 1 /t REG_DWORD')

			# on startup, unmount drives, wait a bit, mount drives, then run webservice
			if os.system('schtasks /query /tn RemountDrives >NUL 2>&1'):
				if os.getenv('IE_LOCATION') == 'NY':
					print 'adding remount drives task ny'
					os.system('schtasks /create /XML /ie/ark/setup/RemountDrives_ny.xml /tn RemountDrives')
				else:
					print 'adding remount drives task'
					os.system('schtasks /create /XML /ie/ark/setup/RemountDrives.xml /tn RemountDrives')

	def installPythonPackages(self):
		# modified from below
		def installPackage(cmd, label, alreadyInstalled=False):
			if alreadyInstalled:
				print '\n' + label + ': already installed'
				return

			print '\n' + label + ': installing'

			out, err = cOS_tiny.getCommandOutputParsed(cmd.split(' '))
			if out:
				print label + ': success'
			else:
				print label + ': ERROR'
				print err
				raise Exception(err)

		# get the packages we've already installed
		out, err = cOS_tiny.getCommandOutputParsed(['pip', 'list'])

		# If no pip packages install, out will be "True"
		if out is True:
			out = ''
		installedPackages = out.split('\n')
		# get the name, drop the version
		installedPackages = [name.split(' ')[0] for name in installedPackages]

		print '\nInstalled packages:'
		print '\n'.join(installedPackages)

		if cOS_tiny.isWindows():
			# PIP can do some
			pipPackages = [
				# '--upgrade pip',
				'appdirs',
				'arrow',
				'backports.ssl-match-hostname',
				'boto',
				'commentjson',
				'clique',
				'django==1.11',
				'expects',
				'Image',
				'fileseq',
				'futures',
				'mysql-connector-repackaged',
				'pyseq',
				'PySide>=1.2.4',
				'pyparsing',
				'pypiwin32',
				'QtPy',
				'requests>=2.18.4',
				'riffle',
				'sphinx',
				'socketIO-client',
				'tinys3',
				# Ftrack packages
				'ftrack-python-api',
				'ftrack-python-legacy-api',
				'ftrack-action-handler',
			]

			for packageName in pipPackages:
				installPackage('pip install ' + packageName,
					packageName,
					re.match(packageRe, packageName.lower()).group(0) in installedPackages)

			# easy_install can do some more
			easy_installPackages = [
				'psutil==1.2.1',
				'autopy',
			]
			for packageName in easy_installPackages:
				installPackage('easy_install ' + packageName,
					packageName,
					re.match(packageRe, packageName.lower()).group(0) in installedPackages)

			# fucking nothing can do numpy :\
			numpyInstallDir = os.environ.get('ARK_PYTHONLIB') + 'numpy'
			if os.path.isdir(numpyInstallDir):
				print '\nnumpy: already installed'
			else:
				print '\nnumpy: installing'
				try:
					dir_util.copy_tree(
						'R:/Assets/Software/Python/2.7/64bit/numpy',
						numpyInstallDir)
					print 'numpy: success'
				except Exception as err:
					print 'numpy: ERROR'
					print err
					raise err

			# install OpenEXR straight from the .whl file
			installPackage('pip install R:/Assets/Software/Python/OpenEXR-1.2.0-cp27-none-win_amd64.whl',
					'OpenEXR',
					'openexr' in installedPackages)

			# install OpenImageIO straight from the .whl file
			installPackage('pip install R:/Assets/Software/Python/OpenImageIO-1.6.18-cp27-cp27m-win_amd64.whl',
					'OpenImageIO',
					'openimageio' in installedPackages)

			installPackage(('pip install %sftrack-connect' % self.arkRoot).replace('/','\\'),
				'ftrack-connect',
				'ftrack-connect' in installedPackages)

			# fix: PyQT4 requires binaries which sucks
			# pyQTInstallDir = os.environ.get('ARK_PYTHONLIB') + 'PyQt4'
			# installPackage('R:/Assets/Software/Python/2.7/PyQT4/PyQt4-4.10.4-gpl-Py2.7-Qt4.8.6-x64.exe /S',
			# 				'PyQt4',
			# 				os.path.isdir(pyQTInstallDir))

		elif cOS_tiny.isLinux() or cOS_tiny.isMac():
			# Yum can do some
			import yum
			yb = yum.YumBase()
			inst = yb.rpmdb.returnPackages()
			yumInstalled = [x.name for x in inst]

			yumPackages = [
				'cmake',
				'wine',
				'qt-devel',
				'python-devel',
				'libXtst-devel',
				'PyQt4',
				'gcc',
				'libpng',
				'libpng12',
				'libpng-devel',
				'python-pyside',
				'python-OpenImageIO',
			]
			# Note: for autopy to install, it needs both libpng and libpng-devl
			# to not be a derp

			for packageName in yumPackages:
				# Run with -y to override asking for user confirmation
				try:
					installPackage('yum -y install ' + packageName,
						packageName,
						packageName in yumInstalled)
				except Exception as err:
					print err
					print 'Error installing:', packageName

			# PIP can do some
			pipPackages = [
				# '--upgrade pip',
				'appdirs',
				'arrow',
				'autopy',
				'boto',
				'clique',
				'commentjson',
				'expects',
				'fileseq',
				'futures',
				'Image',
				'mysql-connector-repackaged',
				'numpy',
				'pillow',
				'pyseq',
				'pyside',
				'requests>=2.18.4',
				'riffle',
				'sphinx',
				'socketIO_client',
				'tinys3',
				# Ftrack packages
				'ftrack-python-api',
				'ftrack-python-legacy-api',
				'ftrack-action-handler',
			]

			for packageName in pipPackages:
				installPackage('pip install ' + packageName,
					packageName,
					re.match(packageRe, packageName.lower()).group(0) in installedPackages)

			# easy_install can do some more
			easy_installPackages = [
				'psutil',
			]
			for packageName in easy_installPackages:
				installPackage('easy_install ' + packageName,
					packageName,
					packageName in installedPackages)

			# temporarily set path environment variable so it's able to install ftrack connect
			os.environ['PATH'] = '/usr/lib64/python2.7/site-packages/PySide/:' + os.environ['PATH']
			installPackage(('pip install %sftrack-connect' % self.arkRoot),
				'ftrack-connect',
				'ftrack-connect' in installedPackages)

	def ensureComputerName(self):
		'''
		Generate a unique name for this computer
		ex: IE202_nksvknlDKNDSNKLf2kn90
		'''
		# bail if we've already made a name
		if os.environ.get('ARK_COMPUTER_NAME') and\
			not '--useComputerName' in self.options:
			return

		import cOS
		import arkUtil
		if cOS.isWindows():
			newName = os.environ.get('COMPUTERNAME')
		elif cOS.isLinux() or cOS.isMac():
			newName = os.environ.get('HOSTNAME')
		if not '--useComputerName' in self.options:
			newName = newName + '_' + arkUtil.randomHash()
		# if useComputerName, computer name better be unique already
		cOS.setEnvironmentVariable('ARK_COMPUTER_NAME', newName)
		print 'ARK_COMPUTER_NAME:', newName

	def makeConfig(self):
		import cOS
		cOS.makeDirs(self.configDir)
		for f in ['cookies.dat', 'key.user.dat']:
			if not os.path.isfile(self.configDir + f):
				try:
					cOS.copy(os.environ["ARK_ROOT"] + 'config/'+ f, self.configDir + f)

				except:
					pass

		cOS.removeDir(os.environ["ARK_ROOT"] + 'config/')

	def cleanFiles(self):
		'''
		Remove old files that shouldn't be there, only on farm nodes
		'''
		if cOS_tiny.isWindows() and 'RENDER' in os.getenv('COMPUTERNAME'):
			# number of versions to keep
			keepLatestVersions = 3

			import arkUtil
			installVersions =  cOS_tiny.getFiles(path='C:/',
				folderIncludes=['ie_v*'],
				fileExcludes=['*'],
				folderExcludes=['*'],
				includeAfterExclude=True
			)
			installVersions = arkUtil.sort(installVersions)
			oldVersions = installVersions[:-min(keepLatestVersions, len(installVersions))]

			print 'Cleaning up old tools versions...'
			for oldVersion in oldVersions:
				try:
					cOS_tiny.removeDir(oldVersion)
				except:
					print 'Error removing {}'.format(oldVersion)

	def ftrackSetup(self):
		if cOS_tiny.isWindows():
			# start ftrack at startup
			shutil.copy('%sarkFTrack/install/ftrackConnect_windowsHidden.vbs' % os.environ["ARK_ROOT"],
				'C:/Users/' + cOS_tiny.getOSUsername() + '/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup')

			cOS_tiny.removeFile('C:/Users/' + cOS_tiny.getOSUsername() + '/Desktop/ftrackConnect.lnk')
			# Desktop shortcut
			cOS_tiny.createShortcut(
				'C:/Users/' + cOS_tiny.getOSUsername() + '/Desktop/ftrackConnect.lnk',
				target='%sarkFTrack/install/ftrackConnect_windowsHidden.vbs' % os.environ["ARK_ROOT"])
		elif cOS_tiny.isLinux():
			# Ftrack Connect should start on login
			cOS_tiny.makeDir('%s.config/autostart/' % self.userRoot)
			cOS_tiny.copy('/ie/arkFTrack/install/ftrackConnect.desktop', '%s.config/autostart/ftrackConnect.desktop' % self.userRoot)
			os.system('chmod +x %s.config/autostart/ftrackConnect.desktop' % self.userRoot)
			os.system('chmod +x %sarkFTrack/install/ftrackConnect' % self.arkRoot)

	def programSetup(self):
		'''
		Install all the software in the world
		'''
		if '--noPrograms' in self.options:
			return

		import programSetup
		programSetup.setup(deadlineOnly=('--deadlineOnly' in self.options))

	def startScheduledTask(self):
		if cOS_tiny.isWindows():
			try:
				os.system('C:/ie/ark/setup/deadlineWebservice_windowsHidden.vbs')
			except Exception as err:
				print 'Could not start webservice', err


def main():
	arkSetup = Setup(sys.argv)
	arkSetup.setup()


if __name__ == '__main__':
	main()
