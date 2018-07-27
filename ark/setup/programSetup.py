
# Standard modules
import shutil
import os
import time
# import glob
import sys
from distutils import dir_util
# from fnmatch import fnmatch
import subprocess
import json
import psutil
import traceback
# import zipfile
# import ConfigParser

# windows has no pwd module and won't use it
try:
	import pwd
except ImportError:
	pass


# Our modules
import arkInit
arkInit.init()
import killJobProcesses
import cOS
import settingsManager
globalSettings = settingsManager.globalSettings()

setupConfigFile = os.path.join(
	globalSettings.SYSTEM_ROOT,
	'config/computerSettings.json'
)

computerSettings = {}
if os.path.isfile(setupConfigFile):
	with open(setupConfigFile) as f:
		contents = f.read()

	computerSettings = json.loads(contents)
	print 'Loaded computer settings from ' + setupConfigFile

else:
	databaseConfig = settingsManager.databaseSettings(
		'programs',
		globalSettings.UNIQUE_NAME)
	computerSettings = databaseConfig.settings
	print 'Loaded computer settings from database'

# Helpers
##################################################
def installProgram(cmd, label, version='1.0'):
	if computerSettings.get(label) == version:
		print '\n' + label + ': already installed'
		return True

	print '\n' + label + ': installing'
	print cmd
	out, err = cOS.getCommandOutput(cmd)
	if out or not err:
		print label + ': success'
		computerSettings[label] = version
	else:
		print label + ': ERROR'
		print err
		raise Exception(err)

# Main functionality
##################################################
def installWindowsPrograms():

	# Quicktime
	installProgram('msiexec /i "R:\\Assets\\Software\\Quicktime\\QuickTime.msi" /passive DESKTOP_SHORTCUTS=NO',
					'Quicktime',
					'1.0')
	installProgram('msiexec /i "R:\\Assets\\Software\\Quicktime\\AppleApplicationSupport.msi" /passive',
					'Apple Application Support',
					'1.0')

	# Python
	installProgram('msiexec /i "R:\\Assets\\Software\\Python\\python-2.7.11.amd64.msi" /passive',
					'Python',
					'2.7.11.x64')

	# EZ Setup
	pythonEXE = 'c:/Python27/python.exe '
	installProgram(pythonEXE + globalSettings.RAMBURGLAR + '/Assets/Software/Python/install_ez_setup.py',
					'EZ Setup',
					'1.0')

	# pip
	installProgram(pythonEXE + globalSettings.RAMBURGLAR + '/Assets/Software/Python/install_pip.py',
					'PIP',
					'1.0')

	# Avid Codecs
	installProgram(globalSettings.RAMBURGLAR + '/Assets/Software/Codecs/AvidCodecsLESetup.exe /S /v/qn',
					'Avid Codecs',
					'1.0')

	# cOS.removeFile(cOS.getUserHome() + 'AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/hubShortcut.vbs.lnk')
	# cOS.removeFile(cOS.getUserHome() + 'AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/sheep.lnk')
	# cOS.copy(globalSettings.ARK_ROOT + 'ark/tools/hub/hubShortcut.lnk', cOS.getUserHome() + 'AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/hubShortcut.lnk')
	# cOS.copy(globalSettings.ARK_ROOT + 'ark/tools/hub/hubShortcut.lnk', cOS.getUserHome() + 'Desktop/hubShortcut.lnk')
	os.system('rmdir /s /q  ' + cOS.getUserHome().replace('/', '\\') + 'Desktop\\hubShortcut')
	# os.system('mklink ' + cOS.getUserHome().replace('/', '\\') + 'Desktop\\hubShortcut ' + \
	# 				globalSettings.ARK_ROOT.replace('/', '\\') + 'ark\\tools\\hub\\hub.vbs')
	cOS.createShortcut(cOS.getUserHome().replace('/', '\\') + 'Desktop\\hubShortcut.lnk',
				target=globalSettings.ARK_ROOT.replace('/', '\\') + 'ark\\tools\\hub\\hub.vbs')
	os.system('powercfg.exe -h off')

	addCaretakerToHosts()


def installLinuxPrograms():
	# cOS.copy('%s/Assets/Software/Chrome/google-chrome.repo' % globalSettings.RAMBURGLAR, '/etc/yum.repos.d/')
	# installProgram('yum install -y google-chrome-stable',
	# 	'Google Chrome',
	# 	'57.0')

	addCaretakerToHosts()

	xprintidleCmd = ['yes | cp -rf %s/Assets/Software/xprintidle /usr/' % globalSettings.RAMBURGLAR,
			'mv -f /usr/xprintidle/scrnsaver.h /usr/include/X11/extensions/',
			'rm -f /usr/lib64/libXss.so',
			'ln -s /usr/lib64/libXss.so.1.0.0 /usr/lib64/libXss.so',
			'cd /usr/xprintidle/',
			'python /usr/xprintidle/setup.py install',
			'python /usr/xprintidle/setup.py build'
			]
	installProgram((' && ').join(xprintidleCmd),
		'xprintidle',
		'1.0')

	# cOS.copy(globalSettings.ARK_ROOT + 'ark/tools/hub/hubShortcut',
	# 			'/home/' + cOS.getOSUsername() + '/Desktop/hubShortcut')

	cOS.removeFile('/home/' + cOS.getOSUsername() + '/Desktop/hubShortcut')
	cOS.copy(globalSettings.ARK_ROOT + '/ark/tools/hub/hubShortcut',
					'/home/' + cOS.getOSUsername() + '/Desktop/hubShortcut')
	os.system('chmod +x /home/' + cOS.getOSUsername() + '/Desktop/hubShortcut')
	os.system('sed -i -e "s/\\r$//" ' + globalSettings.ARK_ROOT + '/ark/tools/hub/hubLinux')
	os.system('sed -i -e "s/\\r$//" /home/' + cOS.getOSUsername() + '/Desktop/hubShortcut')

def addCaretakerToHosts():
	try:
		with open(globalSettings.HOSTS, 'ab+') as f:
			lines = f.readlines()
			caretakerHost = globalSettings.CARETAKER_LOCAL + ' caretaker\n'
			wikiHost = globalSettings.CARETAKER_WIKI + ' caretaker/wiki\n'

			if caretakerHost not in lines:
				f.write('\n' + caretakerHost)

			if wikiHost not in lines:
				f.write('\n' + wikiHost)

	except Exception as err:
		print 'Could not write to hosts file:', globalSettings.HOSTS
		print err


def installAdditionalTools():
	# if cOS.isWindows():
	# 	sheepShortcut = globalSettings.USER_ROOT + 'Desktop/sheep.lnk'
	# 	shutil.copyfile(globalSettings.SHEPHERD_ROOT + '../bin/sheep.lnk', sheepShortcut)
	# 	sheepShortcut = globalSettings.USER_ROOT + 'Desktop/sheep.desktop'
	# 	shutil.copyfile(globalSettings.SHEPHERD_ROOT + '../bin/sheep.desktop', sheepShortcut)
	# 	os.system('chmod +x ' + sheepShortcut)

	if cOS.isLinux():
		# install xterm
		installProgram('yum install -y xterm',
			'xterm',
			'1.0')

		# install slack app
		try:
			installProgram('yum install -y /ramburglar/Assets/Software/Slack/slack-2.2.1-0.1.fc21.x86_64.rpm',
				'slack',
				'1.1')
		except:
			print 'Error installing Slack'

		# install shutter
		try:
			installProgram('yum install -y shutter',
				'shutter',
				'1.0')

		except:
			print 'Error installing Shutter'

	else:
		pass

def environmentSetup():
	drives = [
		'RAMBURGLAR',
		'RAIDCHARLES',
		'FOOTAGE',
		]
	for drive in drives:
		cOS.setEnvironmentVariable(drive.lower(), globalSettings.get(drive))

	if cOS.isLinux():
		# add this user to sudoers file so they can run updateLinux as root
		try:
			sudoersFile = '/etc/sudoers'
			username = cOS.getOSUsername()
			permissions = [
					'%s ALL=(root) NOPASSWD: /ie/ark/tools/hub/hubLinux' % username,
					'%s ALL=(root) NOPASSWD: /ie/ark/tools/hub/hubShortcut' % username,
					'%s ALL=(root) NOPASSWD: /home/%s/Desktop/hubShortcut' % (username, username),
					]
			existingPermissions = []
			lines = []
			with open(sudoersFile) as config:
				for line in config:
					for permission in permissions:
						if permission in line:
							existingPermissions.append(permission)
					lines.append(line)

			newPermissions = [permission for permission in permissions if permission not in existingPermissions]

			if newPermissions:
				for permission in newPermissions:
					lines.append(permission + '\n')

				with open(sudoersFile, 'w') as config:
					for line in lines:
						config.write(line)
				print '/etc/sudoers updated successfully'
			else:
				print '/etc/sudoers already set correctly'

		except Exception as err:
			print 'Error updating /etc/sudoers'
			print err

def installFonts():
	print 'Installing Fonts'
	globalFontDirectory = globalSettings.RAMBURGLAR + '/Assets/Fonts/Standard'
	allFonts =os.listdir(globalFontDirectory)
	localFontDirectory = ''
	if cOS.isLinux():
		localFontDirectory = globalSettings.SYSTEM_ROOT + 'usr/share/fonts'
	else:
		localFontDirectory = globalSettings.SYSTEM_ROOT + 'Windows/Fonts'

	for font in allFonts:
		if not os.path.isfile(os.path.join(localFontDirectory, font)):
			cOS.copy(os.path.join(globalFontDirectory, font), os.path.join(localFontDirectory, font))

def installNuke():
	if os.path.isfile(globalSettings.NUKE_EXE):
		print 'Nuke already installed'
	elif cOS.isWindows():
		installProgram('"%s/Assets/Software/Nuke/Nuke10.0v4-win-x86-release-64.exe"  /verysilent /MERGETASKS="!desktopicon"' % globalSettings.RAMBURGLAR,
			'Nuke',
			'10.0v4')
	elif cOS.isLinux():
		local = '/usr/Nuke10.0v4'
		print 'Making local dir', local
		try:
			os.makedirs(local)
		except Exception as err:
			if os.path.isdir(local):
				cOS.emptyDir(local)
			else:
				raise
		try:
			remote = '%s/Assets/Software/Nuke/Nuke10.0v4-linux-x86-release-64-installer' % globalSettings.RAMBURGLAR
			print 'Copying installer from', remote
			shutil.copy2(remote, local + '/Nuke10.0v4-linux-x86-release-64-installer')
		except Exception as err:
			raise err
		print 'Unzipping in', local
		installProgram('unzip /usr/Nuke10.0v4/Nuke10.0v4-linux-x86-release-64-installer -d %s' % local,
			'Nuke',
			'10.0v4')
	else:
		raise Exception ('Cannot install Nuke on OS:', sys.platform)

	# Set common variables depending on platform
	# Set up additional license files for Windows
	licenseServer = globalSettings.LICENSE_SERVER
	if cOS.isWindows():

		if os.path.exists('N:/nuke'):
			globalSettings.NUKE_TEMP_DIR = 'N:/nuke'

		# Set windows vars to use for common setup
		nukeOFXDir = 'C:/Program Files/Common Files/OFX/Plugins/'
		try:
			cOS.makeDirs('C:/ProgramData/The Foundry/FLEXlm')
			cOS.makeDirs('C:/ProgramData/The Foundry/RLM')

			cOS.emptyDir('C:/ProgramData/The Foundry/RLM')
			cOS.emptyDir('C:/ProgramData/The Foundry/FLEXlm')
			cOS.emptyDir('C:/Program Files/The Foundry/FLEXlm')
			cOS.emptyDir('C:/Program Files/The Foundry/RLM')
		# 	try:
		# 		shutil.copy2('%s/Assets/Software/TheFoundry/FlexLM/foundry_client.lic' % globalSettings.RAMBURGLAR,'C:/ProgramData/The Foundry/FLEXlm')
		# 		shutil.copy2('%s/Assets/Software/TheFoundry/RLM/foundry_client.lic' % globalSettings.RAMBURGLAR,'C:/ProgramData/The Foundry/RLM')
		# 	except Exception as err:
		# 		raise err
		# 		pass
		# 	print 'Nuke license installed: ie-license'
		except:
			print 'Could not copy Foundry License'
			# raise
	elif cOS.isLinux():
		# Set linux vars to use in common setup
		nukeOFXDir = '/usr/OFX/Plugins'
		# symlink nuke to bin so it's easy to run
		os.system('ln -sf /usr/Nuke10.0v4/Nuke10.0 /usr/bin/nuke')

		if os.path.exists('/mnt/NVME/nuke'):
			globalSettings.NUKE_TEMP_DIR = '/mnt/NVME/nuke'
			cOS.emptyDir(globalSettings.NUKE_TEMP_DIR)

	# Common
	# License environment variables
	print 'Setting Nuke Environment Variables'
	cOS.setEnvironmentVariable('RLM_LICENSE', '5053@%s' % licenseServer)
	cOS.setEnvironmentVariable('peregrinel_LICENSE', '2020@%s' % licenseServer)
	cOS.setEnvironmentVariable('foundry_LICENSE', '4101@%s' % licenseServer)
	# Used for loading Nuke Plugins
	cOS.setEnvironmentVariable('NUKE_PATH', globalSettings.NUKE_TOOLS_ROOT)
	# Disable crash reporting
	cOS.setEnvironmentVariable('NUKE_CRASH_HANDLING', 0)

	# OFX Plugins
	if computerSettings.get('Nuke OFX Plugins') != '1.1':
		print '\nNuke plugins: Installing'
		try:
			cOS.makeDirs(nukeOFXDir)
			dir_util.copy_tree('%s/Assets/Tools/Nuke/plugins/' % globalSettings.RAMBURGLAR,
									nukeOFXDir)
			print 'Nuke plugins: success'
			computerSettings['Nuke OFX Plugins'] = '1.0'
		except Exception as err:
			print 'Nuke plugins: ERROR'
			print err
	else:
		print 'Nuke plugins: already installed'

	cOS.setEnvironmentVariable('NUKE_USE_FAST_ALLOCATOR', '1')
	cOS.setEnvironmentVariable('RLM_LICENSE', '5053@%s' % licenseServer)

	print 'Installing Sapphire client license'
	print 'Sapphire license server set to:', globalSettings.LICENSE_SERVER
	cOS.setEnvironmentVariable('RVL_SERVER', globalSettings.LICENSE_SERVER)

	if cOS.isWindows():
		try:
			cOS.makeDirs('C:/Program Files/GenArts/SapphireOFX/')
			open('C:/Program Files/GenArts/SapphireOFX/s_config.text', 'w').close()
			installProgram('"%s/Assets/Software/Sapphire/RVLFloatLicenseSoftware-2.2-windows-installer.exe" --clientOrServer client --mode unattended --acceptEULA 1' % globalSettings.RAMBURGLAR,
				'SapphireLicense',
				'2.2')

		except Exception as err:
			print 'Error installing Sapphire license:', err

	print 'Setting up Optical Flares environment variables'
	cOS.setEnvironmentVariable('OPTICAL_FLARES_LICENSE_PATH', globalSettings.USER_ROOT)
	cOS.setEnvironmentVariable('OPTICAL_FLARES_VERBOSE_CONSOLE', 1)
	cOS.setEnvironmentVariable('OPTICAL_FLARES_PATH', '%s/Assets/Software/Optical_Flares/' % globalSettings.RAMBURGLAR)
	cOS.setEnvironmentVariable('OPTICAL_FLARES_PRESET_PATH', '%s/Assets/Software/Optical_Flares/Textures-And-Presets' % globalSettings.RAMBURGLAR)

def installMocha():
	if cOS.isLinux():
		installProgram('rpm -Uvh --replacepkgs --nodeps  %s/Assets/Software/Mocha/mochapro-4.1.3-10962.x86_64.rpm' % globalSettings.RAMBURGLAR,
			'Mocha',
			'4.1.2')
		cOS.makeDirs('/etc/opt/isl/licences/')
		shutil.copyfile('%s/Assets/Software/Mocha/client.lic' % globalSettings.RAMBURGLAR,
			'/etc/opt/isl/licences/client.lic')

		# remove the default cache directory as user cannot access it
		cOS.removeDir('/tmp/MoTemp')

		configDir = globalSettings.USER_ROOT + '.config/Imagineer Systems Ltd/'
		configFile = os.path.join(configDir, 'mocha Pro 4.conf')
		cOS.makeDir(configDir)

		# try to cache on NVME
		cacheDir = '/mnt/NVME/mochaCache'
		cOS.makeDir('/mnt/NVME/mochaCache')

		# fall back to user folder
		if not os.path.isdir(cacheDir):
			cacheDir = '/home/ingenuity/temp/mochaCache'
			cOS.makeDirs(cacheDir)

		writeLines = []
		try:
			if os.path.isfile(configFile):
				with open(configFile) as config:
					for line in config:
						writeLine = line
						if 'FileCacheFolder' in line:
							writeLine = 'FileCacheFolder=' + cacheDir + '\n'
							print 'Mocha cache dir:', cacheDir
						writeLines.append(writeLine)
			with open(configFile, 'w') as config:
				for writeLine in writeLines:
					config.write(writeLine)
		except Exception as err:
			print 'Could not write to config file:', configFile
			print err

	elif cOS.isWindows():
		try:
			if os.path.isfile(globalSettings.MOCHA_EXE):
				print 'Mocha already installed'
			else:
				installProgram('msiexec /i "%s/Assets\Software\Mocha\mochapro-4.1.2-9658.x64.msi" /passive' % globalSettings.RAMBURGLAR,
					'Mocha',
					'4.1.2')

			cOS.makeDirs('C:/ProgramData/Imagineer Systems Ltd/Licensing/')
			shutil.copyfile('%s/Assets/Software/Mocha/client.lic' % globalSettings.RAMBURGLAR,
				'C:/ProgramData/Imagineer Systems Ltd/Licensing/')
		except Exception as e:
			print e

def installPureRef():
	if cOS.isWindows():
		installProgram('"%s\Assets\Software\PureRef\PureRef-1.9.2_x64.exe" /S' % globalSettings.RAMBURGLAR,
			'PureRef',
			'1.9.2')
	elif cOS.isLinux():
		installProgram('rpm -Uvh --replacepkgs "\Assets\Software\PureRef\PureRef-1.9.2_x64.rpm"' % globalSettings.RAMBURGLAR,
			'PureRef',
			'1.9.2')

def installDJV():
	if cOS.isWindows():
		installProgram('"%s\Assets\Software\DJV\djv-1.1.0-Windows-64.exe" /S' % globalSettings.RAMBURGLAR,
			'DJV',
			'1.1.0')
	elif cOS.isLinux():
		print 'DJV not currently working for Linux :('
		# cOS.copyTree('%s/Assets/Software/DJV/djv-1.1.0-Linux-64/usr' % globalSettings.RAMBURGLAR,
		# 	'/usr')
		# os.system('ln -s /usr/local/djv-1.1.0-Linux-64/bin/djv_view /usr/bin/djv_view')

def installHiero():
	print '\n\nInstalling Hiero'
	cOS.setEnvironmentVariable('HIERO_PLUGIN_PATH', globalSettings.HIERO_TOOLS_ROOT)

def installCinema4D():
	print '\n\nInstalling Cinema4D'
	if cOS.isWindows():
		label = 'Cinema4D'
		version = 'R19'
		if computerSettings.get(label) == version:
			print '\n' + label + ': already installed'
			return True

		try:
			print '\n' + label + ': installing'
			cOS.copyTree('%s/Assets/Software/Maxon/Node Install/' % globalSettings.RAMBURGLAR, 'C:/Program Files/')
			print label + ': success'
			computerSettings[label] = version
		except Exception as err:
			print 'Error installing Cinema4D'
			print err

	elif cOS.isLinux():
		print 'No Cinema4D for Linux :('

def installNeatVideo():
	print '\n\nInstalling Neat Video'
	if cOS.isWindows():
		installProgram('%s\Assets\Software\NeatVideo_Grain\NeatOFXSetup64.exe /VERYSILENT /NORESTART' % globalSettings.RAMBURGLAR,
			'NeatVideo',
			'v4')
		installProgram('REG IMPORT %s\Assets\Software\NeatVideo_Grain\site_license.reg' % globalSettings.RAMBURGLAR,
			'NeatVideo License',
			'v4')

	elif cOS.isLinux():
		print 'No neat video for Linux :('


def installSubstance():
	# Check if Substance is already installed (?)
	print '\n\nInstalling Substance Painter'
	installProgram('"%s/Assets/Software/Substance/Substance_Painter-2018.1.0-2128-msvc14-x64-standard-full.exe" /SILENT' % globalSettings.RAMBURGLAR,
		'SubstancePainter',
		'2018.1.0')
	print '\n\nInstalling Bitmap 2 Material'
	installProgram('"%s/Assets/Software/Substance/bitmap2material_3_1_3_build_18040_trial.exe" /S' % globalSettings.RAMBURGLAR,
		'BitmapMaterial',
		'3.1.3')
	print '\n\nInstalling Substance Houdini'
	installProgram('"%s/Assets/Software/Substance/SubstanceHoudini.exe" /S' % globalSettings.RAMBURGLAR,
		'SubstanceHoudini',
		'1.0')
	print '\n\nInstalling Substance Designer'
	installProgram('"%s/Assets/Software/Substance/Substance_Designer-2018.1.0-1039-msvc14-x64-standard-full.exe" /SILENT' % globalSettings.RAMBURGLAR,
		'SubstanceDesigner',
		'2018.1.0')
	print '\n\nInstalling Substance Player'
	installProgram('"%s/Assets/Software/Substance/Substance_Player-2018.1.0-1039-msvc14-x64-standard-full.exe" /SILENT' % globalSettings.RAMBURGLAR,
		'SubstancePlayer',
		'2018.1.0')

def installFFMPEG():
	version = '4.0.1'
	label = 'FFMPEG'
	if cOS.isWindows():

		if computerSettings.get(label) == version:
			print '\n' + label + ': already installed'

		else:
			print '\nInstalling FFMPEG'
			cOS.removeDir('c:/ffmpeg')
			cOS.makeDirs('c:/ffmpeg')
			cOS.copyTree('%s/Assets/Software/ffmpeg/4.0.1' % globalSettings.RAMBURGLAR, 'C:/ffmpeg')

			print label + ': success'
			computerSettings[label] = version

	elif cOS.isLinux():
		os.system('rpm --import https://www.elrepo.org/RPM-GPG-KEY-elrepo.org')
		os.system('rpm -Uvh --replacepkgs http://li.nux.ro/download/nux/dextop/el7/x86_64/nux-dextop-release-0-5.el7.nux.noarch.rpm')

		installProgram('yum -y install ffmpeg',
			'FFMPEG',
			'3.1.4')

def installShortcuts():
	if cOS.isLinux():
		print 'Installing Linux Shortcuts'
		iconRoot = globalSettings.ARK_ROOT + 'ark/ui/shortcuts/linux/'
		icons = os.listdir(iconRoot)
		appDir = '/usr/share/applications/'
		for filename in icons:
			try:
				os.remove('{}Desktop/{}'.format(globalSettings.USER_ROOT, filename))
			except:
				pass

			try:
				# copies to application directory to add to start menu
				# print 'copying:', iconRoot + filename, '> ', appDir
				shutil.copy2(iconRoot + filename, appDir)

				# copies to desktop
				# print 'copying:', iconRoot + filename, '> %sDesktop/' % username
				shutil.copy2(iconRoot + filename, '%sDesktop/' % globalSettings.USER_ROOT)
				shortcutPath = '{}Desktop/{}'.format(globalSettings.USER_ROOT, filename)
				userID = pwd.getpwnam(globalSettings.OS_USERNAME).pw_uid
				os.chown(shortcutPath, userID, userID)
				os.chmod(shortcutPath, 0o775)
			except:
				pass

def setKeybindings():
	if cOS.isLinux():
		print 'Setting Linux Keybindings'
		userID = pwd.getpwnam(os.environ['USER']).pw_uid
		subprocess.Popen(['gsettings', 'reset-recursively', 'org.gnome.desktop.wm.keybindings'],
			preexec_fn = (lambda: os.setuid(userID)))

		# reads keybindings.json
		with open('keybindings.json') as data_file:
			data = json.load(data_file)
			keybindings = data['keybindings']
			customKeybindings = data['customKeybindings']
		# userid needs to be non-root to set keybindings without dconf error
		for action in keybindings:
			subprocess.Popen(['gsettings', 'set', 'org.gnome.desktop.wm.keybindings', action, keybindings[action]],
				preexec_fn = (lambda: os.setuid(userID)))
		customPaths = []
		customKeybindingsPath = 'org.gnome.settings-daemon.plugins.media-keys'
		mediaKeysPath = '/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/'

		for idx, custom in enumerate(customKeybindings):
			customPaths.append('{}custom{}/'.format(mediaKeysPath, idx))

		subprocess.Popen(['gsettings', 'set', customKeybindingsPath, 'custom-keybindings',
			str(customPaths)], preexec_fn = (lambda: os.setuid(userID)))

		for idx, custom in enumerate(customKeybindings):
			gnomeKeybindingPath = '{}.custom-keybinding:{}custom{}/'.format(customKeybindingsPath, mediaKeysPath, idx)
			for label in ['name', 'command', 'binding']:
				subprocess.Popen(['gsettings', 'set', gnomeKeybindingPath,
					label, custom[label]], preexec_fn = (lambda: os.setuid(userID)))

def installModo():
	cOS.setEnvironmentVariable('NEXUS_USER', globalSettings.MODO_TOOLS_ROOT)

	# disable window flashing stealing focus
	# so autosave in MODO doesn't ruin your week
	os.system('REG ADD "HKEY_CURRENT_USER\Control Panel\Desktop" /v ForegroundFlashCount /d 0 /t REG_DWORD /f')
	os.system('REG ADD "HKEY_CURRENT_USER\Control Panel\Desktop" /v ForegroundLockTimeout /d 90000000 /t REG_DWORD /f')

	# copy distutils because Modo doesn't ship w/ it
	print 'Copying distutils'
	cOS.copyTree('C:/Python27/Lib/distutils','C:/Python27/Lib/site-packages/distutils')

	# install MODO
	if os.path.isfile(globalSettings.MODO_EXE):
		print 'MODO already installed'
	else:
		installProgram('"%s/Assets/Software/Modo/MODO_10.1v2_win_b0.exe" /S /ALL /F /V' % globalSettings.RAMBURGLAR,
			'Modo',
			'10.1v2b0')

def installMax_Node():
	# 3dsMax Plugins
	pluginsRoot = '%s/Assets/Tools/Max/plugins/' % globalSettings.RAMBURGLAR
	plugins = {
		# 'Phoenix': 'Phoenix/2.2.24973',
		# 'VRay': 'VRay/3.15.01.25159',
		# 'Fume': 'Fume/3.5.5',
		# 'Maxwell': 'Maxwell/3.0.35',
		# 'Ornatrix': 'Ornatrix/3.3.0.2.0',
		# 'Forest Pack': 'Forest Pack/5.0.0',
		# 'Realflow': 'Realflow/1.0.0',
	}

	for plugin, folder in plugins.iteritems():
		pluginRootDir = pluginsRoot + folder + '/root'
		try:
			dir_util.copy_tree(pluginRootDir,
								globalSettings.MAX_ROOT)
			print '%s: root files copied' % plugin
		except Exception as err:
			print '%s: ERROR' % plugin
			print err

def installMax():
	if os.path.isfile(globalSettings.MAX_EXE):
		print '3dsMax already installed'
	else:
		print '3dsMax not installed, please install manually :\\'
		return False

	cOS.setEnvironmentVariable('ADSKFLEX_LICENSE_FILE', 'ie-license')

	# install Max from the deployment if the folder doesn't already exist
	# shouldInstall = os.path.isfile(trackingFile)
	# skipInstall = os.path.isfile(globalSettings.MAX_EXE)
	# installProgram('R:/Assets/Software/3dsMax/Deployments/max2016_ingenuity.lnk',
	# 				'3dsMax 2016',
	# 				'2016')


	# install Forest Pack
	installProgram('%s/Assets/Software/ForestPack/ForestPackPro500b.exe /S' % globalSettings.RAMBURGLAR,
					'Forest Pack',
					'5.0.0')

	# install Alembic plugin
	if computerSettings.get('Max Alembic Plugin') != '1.0':
		try:
			cOS.copyTree('%s/Assets/Software/Crate/install/Windows7/Max2016/' % globalSettings.RAMBURGLAR,
				'C:/Program Files/Autodesk/3ds Max 2016/')
			print 'Alembic installed successfully'
			computerSettings['Max Alembic Plugin'] = '1.0'
		except Exception as err:
			print 'Error installing Alembic:', err

	# try:
	# 	os.remove(globalSettings.USER_ROOT + 'AppData/Local/Autodesk/3dsMax/2016 - 64bit/ENU/Plugin.UserSettings.ini')
	# except:
	# 	pass

	# for now we always do the node install, even on workstations
	# if globalSettings.IS_NODE:
# 	installMax_Node()

	# set up the plugin.ini to include ieNodePlugins
	# copy the scripts, icons, and plugin.ini
	try:
		cOS.makeDirs(globalSettings.MAX_ROOT + 'Scripts/Startup/')
		cOS.makeDirs(globalSettings.MAX_ROOT + 'UI_ln/IconsDark/')
		cOS.makeDirs(globalSettings.MAX_ROOT + 'UI_ln/Icons/')
		print 'Max folder success'
	except Exception as err:
		print 'Max folder: ERROR'
		print err

	try:
		shutil.copyfile(globalSettings.MAX_TOOLS_ROOT + 'ieScripts.ms', globalSettings.MAX_ROOT + 'Scripts/Startup/')
		cOS.copyTree(globalSettings.MAX_TOOLS_ROOT + 'ui/icons', globalSettings.MAX_ROOT + 'UI_ln/Icons/')
		cOS.copyTree(globalSettings.MAX_TOOLS_ROOT + 'ui/icons', globalSettings.MAX_ROOT + 'UI_ln/IconsDark/')
		print 'Max icons and scripts: success'
	except Exception as err:
		print 'Max icons and scripts: ERROR'
		print err

	# add IE_Network_Plugins to the include file
	# filePath = globalSettings.MAX_ROOT + 'en-US/plugin.ini'
	# config.read(filePath)

	# if 'Include' not in config.sections():
	# 	config.add_section('Include')
	# maxRoot = globalSettings.MAX_TOOLS_ROOT
	# # '/3ds Max 2014/' -> '2014'
	# version = globalSettings.MAX_ROOT[-5:-1]
	# if globalSettings.IS_NODE:
	# 	# ieNodePlugins includes ieCommon
	# 	config.set('Include', 'IE_Node_Plugins', maxRoot + 'config/ieNodePlugins_' + version + '.ini')
	# else:
	# 	config.set('Include', 'IE_Network_Plugins', maxRoot + 'config/ieCommon_' + version + '.ini')
	# 	# ensure VRay isn't set, should be pulled from ieCommon
	# 	config.remove_option('Directories', 'V-Ray main plug-ins')
	# 	config.remove_option('Directories', 'V-Ray additional plug-ins')

	# with open(filePath, 'wb') as configFile:
	# 	# config.write(configFile)
	# 	for section in config.sections():
	# 		configFile.write('\r\n[' + section + ']\r\n')
	# 		for option in config.options(section):
	# 			configFile.write(option + '=' + config.get(section, option) + '\r\n')

	# # copy the maxstart scene
	# if os.path.isdir(os.environ['USERPROFILE'] + '/Documents/3dsMax/scenes/') and \
	# 	not globalSettings.IS_NODE:
	# 	shutil.copyfile(globalSettings.MAX_TOOLS_ROOT + 'scenes/maxstart.max',
	# 				os.environ['USERPROFILE'] + '/Documents/3dsMax/scenes/')



# 	# # set up the symbolic link for PointHelperPro
# 	# try:
# 	# 	osUsername = os.environ.get('username')
# 	# 	os.mkdir('c:/users/' + osUsername + '/appdata/Local/Autodesk/3dsMax/2012 - 64bit/enu/plugcfg/PointHelperPro/')
# 	# 	os.system('mklink "c:/users/' + osUsername + '/appdata/Local/Autodesk/3dsMax/2012 - 64bit/enu/plugcfg/PointHelperPro/Meshes.max" "Q:/ASSETS/TOOLS/Max/plugins/PointHelperPro/IE_Point_Meshes.max"')
# 	# 	print 'PointHelperPro symbolic link set up successfully'
# 	# except Exception as err:
# 	# 	print e
# 	# 	print 'Could not set up PointHelperPro symbolic link'

def installZBrushPlugin():
	pluginSixtyFour = 	"C:\Program Files (x86)\Pixologic\ZBrush 4R8\ZStartup\ZPlugs64\\"

	if os.path.isdir(pluginSixtyFour):
		zscFile = globalSettings.SHARED_ROOT + '\Assets\Software\ZBrush\PLYformat_4R8.zsc'
		pluginFolder = globalSettings.SHARED_ROOT + 'Assets\Software\ZBrush\PLYformatData'
		installProgram('xcopy \"%s\" \"%s\"' % (zscFile, pluginSixtyFour),
						'ZBrush PLY PLugin 64-bit zsc',
						'1.1')
		installProgram('xcopy /s /q /i \"%s\" \"%s\"' % (pluginFolder, pluginSixtyFour + 'PLYformatData'),
						'ZBrush PLY Plugin 64-bit folder',
						'1.1')

def installMaya():

	def installRPMPackage(cmd, label):
		print '\n' + label + ': installing'
		out, err = cOS.getCommandOutput(cmd, shell=True)
		if out:
			print label + ': success'
		else:
			if 'already installed' in err:
				print label + ': already installed'
			else:
				print err
				raise

	def installYumPackage(cmd, label):
		print '\n' + label + ': installing'
		out, err = cOS.getCommandOutput(cmd, shell=True)
		if out:
			if 'nothing to do' in out:
				print label + ': already installed'
			else:
				print label + ': success'
		else:
			print label + ': ERROR'
			print err
			raise


	if os.path.isfile(globalSettings.MAYA_EXE) and computerSettings.get('Maya') == '2016.05':
		print 'Maya already installed'

	elif cOS.isWindows():
		if globalSettings.IS_NODE:
			try:
				cOS.emptyDir(globalSettings.MAYA_ROOT, waitTime=30)
				print 'Maya emptyFolder: success'
			except Exception as err:
				print 'Maya emptyFolder: ERROR', err

			try:
				print 'Installing Maya 2016.05'
				cOS.makeDirs(globalSettings.MAYA_ROOT)
				cOS.copyTree('%s/Assets/Software/Maya/2016/installed_2016.05/Maya2016' % globalSettings.RAMBURGLAR,
							globalSettings.MAYA_ROOT)
				computerSettings['Maya'] = '2016.05'
				print 'Maya: success'
			except Exception as err:
				raise err

	elif cOS.isLinux():
		yumPackages = [
			'mesa-libGLw',
			'csh',
			'libXp',
			'libXp-devel',
			'gamin',
			'audiofile',
			'audiofile-devel',
			'e2fsprogs-libs',
			'tcsh',
			'xorg-x11-fonts-ISO8859-1-100dpi',
			'xorg-x11-fonts-ISO8859-1-75dpi',
			'liberation-mono-fonts',
			'liberation-fonts-common',
			'liberation-sans-fonts',
			'liberation-serif-fonts',
			'compat-libtiff3',
			'glx-utils',
		]
		print '\nMaya: installing'
		# Install Maya dependencies
		for packageName in yumPackages:
			# Run with -y to override asking for user confirmation
			installYumPackage('yum -y install ' + packageName,
				packageName)

		# Install RPM Maya packages
		# Note: While Maya recommends you install all RPM at once
		# It seems like if you install at once, adlm packages do not install 100%
		rpmPackages = [
			'%s/Assets/Software/Maya/2016/setup_linux/Autodesk_Maya_2016_EN_Linux_64bit/Maya2016_64-2016.0-1312.x86_64.rpm' % globalSettings.RAMBURGLAR,
			'%s/Assets/Software/Maya/2016/setup_linux/Autodesk_Maya_2016_EN_Linux_64bit/adlmapps11-11.0.15-0.x86_64.rpm' % globalSettings.RAMBURGLAR,
			'%s/Assets/Software/Maya/2016/setup_linux/Autodesk_Maya_2016_EN_Linux_64bit/adlmflexnetclient-11.0.15-0.x86_64.rpm' % globalSettings.RAMBURGLAR,
		]
		try:
			for packagePath in rpmPackages:
				packageName = packagePath[len(globalSettings.SHARED_ROOT):].split('/')[-1]
				installRPMPackage('rpm -Uvh --replacepkgs ' + packagePath, packageName)
			os.system('chown -R ' + cOS.getOSUsername() + ' /home/' + cOS.getOSUsername() + '/maya/')
			print 'Maya: success'
			computerSettings['Maya'] = '2016.05'
		except Exception as err:
			print 'Maya: ERROR'
			raise err

	else:
		print 'Cannot install Maya on OS:', sys.platform


	# If Linux, always copy overwrite License files
	if cOS.isLinux():
		try:
			licenseRoot = '%s/Assets/Software/Autodesk/License_Linux/' % globalSettings.RAMBURGLAR
			installProgram('cp %sLicense.env %sbin/License.env' % (licenseRoot, globalSettings.MAYA_ROOT),
							'Maya License.env',
							'1.0')
		except Exception as err:
			print 'ERROR copying Maya License.env'
			raise err
		try:
			installProgram('cp %smaya.lic /var/flexlm/maya.lic' % (licenseRoot),
							'Maya maya.lic',
							'1.0')
		except Exception as err:
			print 'ERROR copying Maya maya.lic'
			raise err
		try:
			installProgram('cp %sMayaConfig.pit /var/opt/Autodesk/Adlm/Maya2016/MayaConfig.pit' % (licenseRoot),
							'Maya MayaConfig.pit',
							'1.0')
		except Exception as err:
			print 'ERROR copying Maya MayaConfig.pit'
			raise err

	# If Linux set license paths
	if cOS.isLinux():
		if not os.path.isfile(globalSettings.SYSTEM_ROOT + 'etc/ld.so.conf.d/maya-linux.conf'):
			cOS.copy(globalSettings.RAMBURGLAR +'/Assets/Software/Maya/2016/setup_linux/maya-linux.conf',
					globalSettings.SYSTEM_ROOT + 'etc/ld.so.conf.d/')

		os.system('ldconfig')
		installProgram(
			'/usr/autodesk/maya2016/bin/adlmreg -i N 657H1 657H1 2016.0.0.F 123-12345678 /var/opt/Autodesk/Adlm/Maya2016/MayaConfig.pit',
			'MayaConfig',
			'1.0')

		os.system('chown -R ' + cOS.getOSUsername() + ' /home/' + cOS.getOSUsername() + '/maya')

	# always install this stuff, it's quick and changes frequently
	if cOS.isWindows():
		scriptsPath = globalSettings.USER_ROOT + 'Documents/maya/2016/scripts/'
		cOS.makeDirs(scriptsPath)

		# mayaMixin bug fix.
		try:
			cOS.copy(globalSettings.RAMBURGLAR + '/Assets/Software/Maya/2016/mayaMixin.py',
					'C:/Program Files/Autodesk/Maya2016/Python/lib/site-packages/maya/app/general/mayaMixin.py')
		except Exception as err:
			print 'Maya mixin not replaced.'

	elif cOS.isLinux():
		scriptsPath = globalSettings.USER_ROOT + 'maya/2016/scripts/'
		cOS.makeDirs(scriptsPath)

		# mayaMixin bug fix.
		try:
			cOS.copy(globalSettings.RAMBURGLAR + '/Assets/Software/Maya/2016/mayaMixin.py',
					'/usr/autodesk/maya/lib/python2.7/site-packages/maya/app/general/mayaMixin.py')
		except:
			print 'Maya mixin not replaced.'

	else:
		raise Exception('Cannot install userSetup on OS:', sys.platform)

	try:
		shutil.copyfile(globalSettings.MAYA_TOOLS_ROOT + 'install/userSetup.py',
					scriptsPath + 'userSetup.py')
		if cOS.isLinux():
			mayaRootPath = '/root/maya/2016/scripts/'
			cOS.makeDirs(mayaRootPath)
			shutil.copyfile(globalSettings.MAYA_TOOLS_ROOT + 'install/userSetup.py', mayaRootPath + 'userSetup.py')
		print 'Maya userSetup: success'
	except Exception as err:
		print 'Maya userSetup: ERROR'

	# Bonus Tools
	if cOS.isWindows():
		bonusTools = globalSettings.RAMBURGLAR + '\Assets\Software\Maya\MayaBonusTools-2014-2017-win64.msi'
		installProgram('msiexec /i \"%s\" /passive' % (bonusTools),
						'Maya Bonus Tools',
						'1.0')
	elif cOS.isLinux():
		bonusTools = globalSettings.SHARED_ROOT + 'Assets/Software/Maya/MayaBonusTools-2014-2017-linux.sh'
		installProgram( 'echo y | %s' % (bonusTools),
						'Maya Bonus Tools',
						'1.0')

	# install Ornatrix!
	if cOS.isWindows():
		ornatrix = globalSettings.RAMBURGLAR + '\Assets\Software\Ornatrix\win64__343420342032313532.msi'
		installProgram('msiexec /i \"%s\" /passive' % (ornatrix),
						'Ornatrix',
						'1.0')

	# remove senddmp.exe from Maya folder
	if cOS.isWindows():
		if computerSettings.get('error_report_removed') != '1.0':
			if os.path.isfile('C:/Program Files/Autodesk/Maya2016/bin/senddmp.exe'):
				# in case folder does not exist
				try:
					cOS.makeDirs('C:/temp')
					cOS.copy('C:/Program Files/Autodesk/Maya2016/bin/senddmp.exe', 'C:/temp/senddmp.exe')
					os.system('del "C:\\Program Files\\Autodesk\\Maya2016\\bin\\senddmp.exe"')
					computerSettings['error_report_removed'] = '1.0'
					print 'senddmp Dumped!'

				except IOError:
					print 'senddmp.exe not removed!'
					pass

def installMaya2018():
	label = 'Maya2018'
	version = '2018.3'
	if computerSettings.get(label) == version:
		print '\n' + label + ': already installed'
		return True

	print '\n' + label + ': installing'

	try:
		cmd = '%s/Assets/Software/Maya/2018/dp/Maya18Win.lnk' % globalSettings.RAMBURGLAR
		print cmd
		subprocess.Popen(cmd, shell=True)

		# the command exits before the installation process is done, so check manually on the install process
		time.sleep(20)
		stillRunning = True
		while stillRunning:
			stillRunning = False
			time.sleep(10)
			for p in psutil.process_iter():
				try:
					if any(['Maya18' in c for c in p.cmdline]):
						# print p.cmdline
						stillRunning = True
				except:
					pass

		print label + ': success'
		computerSettings[label] = version

	except Exception as err:
		print label + ': ERROR'
		traceback.print_exc()
		raise Exception(err)

	# Need to figure out Maya Bonus Tools installation for 2018
	# if cOS.isWindows():
	# 	bonusTools = globalSettings.RAMBURGLAR + '/Assets/Software/Maya/2018/MayaBonusTools_2015_2018_win64.msi"'
	# 	installProgram('msiexec /i \"%s\" /passive' % (bonusTools),
	# 					'Maya Bonus Tools 2018',
	# 					'1.0')
	if cOS.isWindows():
		scriptsPath = os.path.join(globalSettings.USER_ROOT,'Documents/maya/2018/scripts/')
		cOS.makeDirs(scriptsPath)
		shutil.copyfile(os.path.join(globalSettings.MAYA_TOOLS_ROOT, 'install/userSetup.py'),
			os.path.join(scriptsPath, 'userSetup.py'))

def installVRay():

	# VRay for MODO
	# installDir = 'C:/Program Files/Chaos Group/V-Ray/MODO x64/'
	# trackingFile = globalSettings.MODO_ROOT + '/vray_3.35.01'
	# installPath = 'R:/Assets/Software/VRay/vray_beta_30101_modo_x64_SOFTWARE_LIC.exe'
	# installProgram(installPath + ' -gui=0 -configFile="' + \
	# 	globalSettings.THIRDPARTY + 'vray/modoConfig.xml" -quiet=1',
	# 					'VRay4MODO 30101',
	# 					os.path.isfile(trackingFile))
	# cOS.setEnvironmentVariable('VRAY_MODO_INSTALL_PATH', 'C:/Program Files/Chaos Group/V-Ray/MODO x64')
	# createTrackingFile(trackingFile)

	# fix: should be fine to set it to local path, but doesn't work on Linux
	# cOS.setEnvironmentVariable('VRAY_AUTH_CLIENT_FILE_PATH ', globalSettings.LICENSE)
	cOS.setEnvironmentVariable('VRAY_AUTH_CLIENT_FILE_PATH', globalSettings.VRAY_AUTH_CLIENT_FILE_PATH)

	# if cOS.isWindows():
	# 	# VRay for 3dsMax
	# 	installProgram('"%s/Assets/Software/VRay/vray_adv_33501_max2016_x64.exe" -configFile="%s/Assets/Software/VRay/config_max.xml" -ignoreErrors=1' % (globalSettings.RAMBURGLAR, globalSettings.RAMBURGLAR),
	# 					'VRay for 3dsMax',
	# 					'3.35.01')
	# else:
	# 	print 'No 3dsMax for anything but Windows, skipping VRay for 3dsMax'


	if cOS.isWindows():
		# VRay for Nuke
		installProgram('"%s/Assets/Software/VRay/nuke/37001_nuke10/windows/vray_adv_37001_nuke10_x64.exe" -configFile="%s/Assets/Software/VRay/config/config_nuke.xml" -ignoreErrors=1' % (globalSettings.RAMBURGLAR, globalSettings.RAMBURGLAR),
						'VRay for Nuke',
						'3.70.01')
		cOS.setEnvironmentVariable('VRAY_FOR_NUKE10_PLUGINS_x64',
			'C:/Program Files/Nuke10.0v4/plugins/vray')

	elif cOS.isLinux():
		#VRay for Nuke
		installProgram('"%s/Assets/Software/VRay/nuke/37001_nuke10/linux/vray_adv_37001_nuke10_linux_x64" -configFile="%s/Assets/Software/VRay/config/config_nuke_linux.xml" -ignoreErrors=1 -quiet=1 -gui=0' % (globalSettings.RAMBURGLAR, globalSettings.RAMBURGLAR),
						'VRay for Nuke',
						'3.70.01')
		cOS.setEnvironmentVariable('VRAY_FOR_NUKE10_PLUGINS_x64',
			'/usr/Nuke10.0v4/plugins/vray')

		os.system('chown -R ' + cOS.getOSUsername() + ' /usr/ChaosGroup')

	if cOS.isWindows():
		# VRay for Maya environment variables
		cOS.setEnvironmentVariable('VRAY_FOR_MAYA2018_MAIN_x64', 'C:/Program Files/Autodesk/Maya2018/vray')
		cOS.setEnvironmentVariable('VRAY_FOR_MAYA2018_PLUGINS_x64', 'C:/Program Files/Autodesk/Maya2018/vray/vrayplugins')
		cOS.setEnvironmentVariable('VRAY_OSL_PATH_MAYA2018_x64', 'C:/Program Files/Chaos Group/V-Ray/Maya 2018 for x64/opensl')
		cOS.setEnvironmentVariable('VRAY_TOOLS_MAYA2018_x64', 'C:/Program Files/Chaos Group/V-Ray/Maya 2018 for x64/bin')
		cOS.setEnvironmentVariable('MAYA_RENDER_DESC_PATH','C:/Program Files/Autodesk/Maya2018/vray/bin/rendererDesc')

		# VRay for Maya
		# installProgram('"%s/Assets/Software/VRay/maya/36004_Maya2016/windows/vray_adv_36004_maya2016_x64.exe" -configFile="%s/Assets/Software/VRay/config/config_maya.xml" -ignoreErrors=0' % (globalSettings.RAMBURGLAR, globalSettings.RAMBURGLAR),
		# 				'VRay for Maya',
		# 				'3.60.04')

		# VRay for Maya 2018
		installProgram('"%s/Assets/Software/VRay/maya/40302_Maya2018/windows/vray_adv_40302_maya2018_x64.exe" -configFile="%s/Assets/Software/VRay/config/config_maya_2018.xml" -ignoreErrors=0' % (globalSettings.RAMBURGLAR, globalSettings.RAMBURGLAR),
						'VRay for Maya2018',
						'4.03.02')
	elif cOS.isLinux():
		# VRay for Maya environment variables
		cOS.setEnvironmentVariable('VRAY_FOR_MAYA2018_MAIN_x64', '/usr/autodesk/maya2018/vray')
		cOS.setEnvironmentVariable('VRAY_FOR_MAYA2018_PLUGINS_x64', '/usr/autodesk/maya2018/vray/vrayplugins')
		cOS.setEnvironmentVariable('VRAY_OSL_PATH_MAYA2018_x64', '/usr/ChaosGroup/V-Ray/Maya2018-x64/opensl')
		cOS.setEnvironmentVariable('VRAY_TOOLS_MAYA2018_x64', '/usr/ChaosGroup/V-Ray/Maya2018-x64/bin')

		#VRay for Maya
		installProgram('"%s/Assets/Software/VRay/maya/40302_Maya2018/linux/vray_adv_40302_maya2018_linux_x64" -gui=0 -configFile="%s/Assets/Software/VRay/config/config_maya_linux.xml" -quiet=1 --ignoreErrors=0' % (globalSettings.RAMBURGLAR, globalSettings.RAMBURGLAR),
						'VRay for Maya',
						'4.03.02')

	else:
		print 'Cannot install VRay for Maya for ' + os.platform

	vrayForHoudiniVersion = False
	installDir = globalSettings.SYSTEM_ROOT + 'vray/houdini_16_5'
	if cOS.isWindows():
		vrayForHoudiniVersion = 'vfh-6e42f89'
		if computerSettings.get('vray_houdini') != vrayForHoudiniVersion:
			try:
				if os.path.isdir(installDir):
					os.system('rmdir "' + installDir + '" /s /q')

				sourceFolder = globalSettings.RAMBURGLAR + '/Assets/Software/VRay/houdini/' + vrayForHoudiniVersion
				os.system('xcopy /e /i /y /q "%s" "%s"' % (sourceFolder, installDir))
				computerSettings['vray_houdini'] = vrayForHoudiniVersion
			except Exception as err:
				print err
				print 'Houdini VRay not installed, please close houdini and try again'

	elif cOS.isLinux():
		vrayForHoudiniVersion = 'houdini_16_linux_qt5_vfh_dff1772'
		if computerSettings.get('vray_houdini') != vrayForHoudiniVersion:
			cOS.makeDir(globalSettings.SYSTEM_ROOT + 'usr/ChaosGroup/V-Ray/Houdini16.0-x64')
			cOS.copyTree(globalSettings.RAMBURGLAR + '/Assets/Software/VRay/' + vrayForHoudiniVersion + '/', globalSettings.SYSTEM_ROOT + 'usr/ChaosGroup/V-Ray/Houdini16.0-x64')
			computerSettings['vray_houdini'] = vrayForHoudiniVersion

# def installMaxwell():
# 	if computerSettings.get('Maxwell') == '3.0':
# 		print 'Maxwell: already installed'
# 		return

# 	maxwellInstallDir = 'C:/Program Files/Next Limit/Maxwell 3'
# 	# for now we always install Maxwell
# 	print 'Setting Maxwell 3 Environment Variables'
# 	cOS.setEnvironmentVariable('MAXWELL3_ROOT',
# 								maxwellInstallDir)
# 	cOS.setEnvironmentVariable('MAXWELL3_MATERIALS_DATABASE',
# 								maxwellInstallDir + '/materials database')
# 	try:
# 		cOS.emptyDir(maxwellInstallDir, waitTime=20)
# 		print 'Maxwell folder emptied'
# 	except Exception as err:
# 		print 'Error emptying Maxwell folder:', err
# 	try:
# 		print 'Installing Maxwell 3.0.1.1'
# 		cOS.makeDirs(maxwellInstallDir)
# 		dir_util.copy_tree('R:/Assets/Software/Maxwell/3/installed_3.0.1.1',
# 								maxwellInstallDir)
# 		print 'Maxwell install files copied to: ' + maxwellInstallDir
# 		computerSettings.set('Maxwell','3.0').save()
# 	except Exception as err:
# 		print 'Could not copy Maxwell install files to: ' + maxwellInstallDir
# 		raise err
# 	try:
# 		licenseDir = 'C:/ProgramData/Next Limit/Maxwell/licenses/'
# 		os.cOS.makedirs(licenseDir)
# 		cOS.emptyDir(licenseDir)
# 		shutil.copyfile('R:/Assets/Software/Maxwell/3/maxwell_license.lic', licenseDir)
# 		print 'Maxwell license files copied to: ' + licenseDir
# 	except Exception as err:
# 		print 'Could not copy Maxwell license files to: ' + licenseDir
# 		raise err


def installHoudini():
	if cOS.isWindows():

		installProgram('"%s/Assets/Software/Houdini/houdini-16.5.496-win64-vc14.exe" /S /AcceptEula=yes /LicenseServer=no /HoudiniServer=yes /EngineMaya=Yes' % globalSettings.RAMBURGLAR,
			'Houdini_beta',
			'16.5.496')

		# out, err = cOS.getCommandOutput('sesictrl -s')
		# if err:
		# 	raise err
		# if 'server caretaker' or 'server ' + globalSettings.LICENSE_SERVER not in out:
		installProgram(globalSettings.SYSTEM_ROOT + 'Windows/System32/hserver.exe -S ' + globalSettings.LICENSE_SERVER, 'Houdini_license', '1.0')

		cOS.setEnvironmentVariable('HOUDINI_OTLSCAN_PATH', globalSettings.HOUDINI_TOOLS_ROOT + 'otls;&')

		# Needed for Windows 10
		cOS.makeDir(globalSettings.USER_ROOT + '/houdini16.0')
		cOS.makeDir(globalSettings.USER_ROOT + '/houdini16.5')

	if cOS.isLinux():

		# installProgram('"%s/Assets/Software/Houdini/houdini-15.0.434-win64-vc11.exe" /S /AcceptEula=yes /LicenseServer=no /HoudiniServer=yes' % globalSettings.RAMBURGLAR,
		# 	'Houdini',
		# 	'15.0.434')

		if os.path.isdir(globalSettings.HOUDINI_ROOT):
			print 'Houdini already installed'
		else:
			os.system('%s/Assets/Software/Houdini/houdini-16.0.600-linux_x86_64_gcc4.8/houdini.install --auto-install --installEngineMaya --install-menus --accept-EULA' % globalSettings.RAMBURGLAR)
			computerSettings['Houdini'] = '16.0.600_qt5'

			os.system('%s/Assets/Software/Houdini/houdini-16.0.323-linux_x86_64_gcc4.8/houdini.install --auto-install --installEngineMaya --install-menus --accept-EULA' % globalSettings.RAMBURGLAR)
			computerSettings['Houdini'] = '16.5.323_qt5'

		# out, err = cOS.getCommandOutput('/usr/lib/sesi/sesictrl -s')
		# if err:
		# 	raise err
		try:
			installProgram(globalSettings.SYSTEM_ROOT + 'opt/hfs16.0/bin/hserver -S ' + globalSettings.LICENSE_SERVER, 'Houdini_license', '1.1')

		except Exception as err:
			print err

		cOS.setEnvironmentVariable('HOUDINI_OTLSCAN_PATH', globalSettings.HOUDINI_TOOLS_ROOT + 'otls:&')
		os.system('chown -R ' + cOS.getOSUsername() + ' /home/' + cOS.getOSUsername() + '/houdini16.0/')

		# installing arkToolbar
		cOS.makeDir(globalSettings.USER_ROOT + 'houdini16.0/python_panels/')

		os.system('chown -R ' + cOS.getOSUsername() + ' /home/' + cOS.getOSUsername() + '/houdini16.0')
		os.system('chown -R ' + cOS.getOSUsername() + ' /home/' + cOS.getOSUsername() + '/houdini16.0/python_panels')

	# installing arkToolbar
	cOS.makeDirs(globalSettings.USER_ROOT + 'houdini16.0/python_panels/')

	cOS.copy(globalSettings.HOUDINI_TOOLS_ROOT + 'houdini16.0/toolbar/default.pypanel', globalSettings.USER_ROOT + 'houdini16.0/python_panels/default.pypanel')
	cOS.copy(globalSettings.HOUDINI_TOOLS_ROOT + 'houdini16.0/toolbar/menu.pypanel', globalSettings.USER_ROOT + 'houdini16.0/python_panels/menu.pypanel')
	cOS.setEnvironmentVariable('HSITE', globalSettings.HOUDINI_TOOLS_ROOT)

	cOS.makeDirs(globalSettings.USER_ROOT + 'houdini16.5/python_panels/')
	cOS.copy(globalSettings.HOUDINI_TOOLS_ROOT + 'houdini16.5/toolbar/default.pypanel', globalSettings.USER_ROOT + 'houdini16.5/python_panels/default.pypanel')
	cOS.copy(globalSettings.HOUDINI_TOOLS_ROOT + 'houdini16.5/toolbar/menu.pypanel', globalSettings.USER_ROOT + 'houdini16.5/python_panels/menu.pypanel')

	# Needed for Windows 10
	cOS.setEnvironmentVariable('HOUDINI_USER_PREF_DIR', globalSettings.USER_ROOT + 'houdini16.0')

	if globalSettings.IS_NODE:
		cOS.setEnvironmentVariable('HOUDINI_SCRIPT_LICENSE', 'hbatch -R')

	cOS.copy(globalSettings.HOUDINI_TOOLS_ROOT + 'houdini16.0/houdini.env', globalSettings.USER_ROOT + 'houdini16.0/houdini.env')
	cOS.copy(globalSettings.HOUDINI_TOOLS_ROOT + 'houdini16.5/houdini.env', globalSettings.USER_ROOT + 'houdini16.5/houdini.env')

	cOS.makeDirs(globalSettings.USER_ROOT + 'houdini16.0/scripts/python/')
	cOS.makeDirs(globalSettings.USER_ROOT + 'houdini16.5/scripts/python/')
	cOS.copy(globalSettings.HOUDINI_TOOLS_ROOT + 'ftrack/pythonrc.py', globalSettings.USER_ROOT + 'houdini16.0/scripts/python/pythonrc.py')
	cOS.copy(globalSettings.HOUDINI_TOOLS_ROOT + 'ftrack/MainMenuCommon.xml', globalSettings.USER_ROOT + 'houdini16.0/MainMenuCommon.xml')
	cOS.copy(globalSettings.HOUDINI_TOOLS_ROOT + 'ftrack/pythonrc.py', globalSettings.USER_ROOT + 'houdini16.5/scripts/python/pythonrc.py')
	cOS.copy(globalSettings.HOUDINI_TOOLS_ROOT + 'ftrack/MainMenuCommon.xml', globalSettings.USER_ROOT + 'houdini16.5/MainMenuCommon.xml')

	# Enviornment var to make saving scenes on network drives faster + disable save thumb
	cOS.setEnvironmentVariable('HOUDINI_BUFFEREDSAVE', 1)
	cOS.setEnvironmentVariable('HOUDINI_DISABLE_SAVE_THUMB', 1)

def installDeadline(deadlineOnly=False):
	if cOS.isWindows():
		if os.path.isdir('s:'):
			if not os.path.isfile(r'C:\Program Files\Thinkbox\Deadline10\bin\deadlinecommand.exe'):
				cOS.copy(r'%s\Assets\Software\Deadline\Installation\10.0.15.5\Windows\DeadlineClient-10.0.15.5-windows-installer.exe' % globalSettings.RAMBURGLAR, globalSettings.TEMP)
				installProgram(('%sDeadlineClient-10.0.15.5-windows-installer.exe ' % globalSettings.TEMP) +\
					r'--mode unattended --connectiontype Repository --repositorydir \\deadlinedata\Repo --licenseserver 27008@172.16.0.53',
					'Deadline',
					'10.0.15.5')
				cOS.removeFile('%sDeadlineClient-10.0.15.5-windows-installer.exe ' % globalSettings.TEMP)

			if not deadlineOnly:
				username = cOS.getOSUsername()
				submissionTools = [('Maya', ' --enable-components Maya --destDir "C:/Users/{0}/Documents/maya/2016/scripts"'.format(username)),
					('Houdini', ' --enable-components Houdini16,Houdini16_5 --destDir16 "C:/Users/{0}/houdini16.0" --destDir16_5 "C:/Users/{0}/houdini16.5"'.format(username)),
					('Nuke', ' --destDir C:/Users/{0}/.nuke'.format(username)),
					('Hiero', '')]
				for submissionTool, flags in submissionTools:
					cmd = r's:/submission/%s/Installers/%s-submitter-windows-installer.exe --mode unattended --installdir "C:\Program Files\Thinkbox\Deadline10\bin"' % (submissionTool, submissionTool)
					cmd += flags
					installProgram(cmd, 'Deadline ' + submissionTool, '10.0.12.1')

			if not os.path.isdir('c:/Python27/Lib/site-packages/Deadline'):
				cOS.copyTree('s:/api/python/Deadline', 'c:/Python27/Lib/site-packages/Deadline')
		else:
			print 'Could not install deadline, please map S network drive first.'
	elif cOS.isLinux():

		# Why haven't we been doing this more often?
		import linuxSetup
		if computerSettings.get('MountDeadline') != '10.0.15.5':
			linuxSetup.network()
			computerSettings['MountDeadline'] = '10.0.15.5'

		installProgram((r'%s/Assets/Software/Deadline/Installation/10.0.15.5/Linux/DeadlineClient-10.0.15.5-linux-x64-installer.run ' % globalSettings.RAMBURGLAR) + \
					r'--mode unattended --connectiontype Repository --repositorydir /deadlinedata --licenseserver 27008@172.16.0.53',
					'Deadline',
					'10.0.15.5')

		# add Deadline Python package to local site-packages
		if computerSettings.get('DeadlinePythonAPI') != '10.0.6.3':
			print 'Deadline Python installing'
			cOS.copyTree('/deadlinedata/api/python/Deadline', '/usr/lib/python2.7/site-packages/Deadline')
			computerSettings['DeadlinePythonAPI'] = '10.0.6.3'

		# Enable Deadline Web Service
		if computerSettings.get('EnableWebService') != '10.0.6.3':
			print 'Enabling Deadline WebService on Startup'
			cOS.copy('/ie/deadline/admin/deadlineWeb.service', '/etc/systemd/system/deadlineWeb.service')
			os.system('systemctl enable deadlineWeb.service')
			os.system('systemctl start deadlineWeb.service')
			computerSettings['EnableWebService'] = '10.0.6.3'


		# For Nuke Submitter Install
		if computerSettings.get('NukeDeadlineInstall') != '10.0.6.3':
			print 'Deadline Nuke installing'
			cOS.copy('/deadlinedata/submission/Nuke/Client/DeadlineNukeClient.py', '/ie/ark/programs/nuke/DeadlineNukeClient.py')
			cOS.copy('/deadlinedata/submission/Nuke/Client/DeadlineNukeFrameServerClient.py', '/ie/ark/programs/nuke/DeadlineNukeFrameServerClient.py')
			cOS.copy('/deadlinedata/submission/Nuke/Client/DeadlineNukeVrayStandaloneClient.py', '/ie/ark/programs/nuke/DeadlineNukeVrayStandaloneClient.py')
			computerSettings['NukeDeadlineInstall'] = '10.0.6.3'

		# For Maya Submitter Install
		if computerSettings.get('MayaDeadlineInstall') != '10.0.6.3' and not globalSettings.IS_NODE:
			print 'Deadline Maya installing'
			cOS.copy('/deadlinedata/submission/Maya/Client/DeadlineMayaClient.mel',
					'/usr/autodesk/maya2016/scripts/startup/DeadlineMayaClient.mel')
			cOS.makeDirs('/home/' + cOS.getOSUsername() + '/maya/2016/scripts')
			cOS.copy('/deadlinedata/submission/Maya/Client/userSetup.mel',
					'/home/' + cOS.getOSUsername() + '/maya/2016/scripts/userSetup.mel')

			computerSettings['MayaDeadlineInstall'] = '10.0.6.3'


def installFusion():
	if cOS.isWindows():
		installProgram('msiexec /i "%s\\Assets\\Software\\Fusion\\Install Fusion v9.0.1.msi" /passive' % globalSettings.RAMBURGLAR,
			'Fusion',
			'9.0.1')
	elif cOS.isLinux():
		pass

def installResolve():
	if cOS.isWindows():
		# prompts user: okay to install driver
		installProgram('msiexec /i "%s\Assets\Software\Resolve\DaVinci Resolve Panels Installer v1.1.1.msi" /qn ALLUSERS="1" REBOOT="ReallySuppress"' % globalSettings.RAMBURGLAR,
			'Resolve Panels',
			'1.1.2')
		installProgram('msiexec /i "%s\Assets\Software\Resolve\ResolveInstaller.msi" /qn REBOOT="ReallySuppress" ALLUSERS="1"' % globalSettings.RAMBURGLAR,
			'Resolve',
			'1.1.2')
	elif cOS.isLinux():
		pass

def setupCacheDir():

	if cOS.isWindows():
		cacheDir = 'C:/cache/'

	elif cOS.isLinux():
		cacheDir = '/home/' + cOS.getOSUsername() + '/cache/'

	if computerSettings.get('Local Cache setup') == '1.0':
		print 'Local Cache already set.'
		return

	cOS.makeDirs(cacheDir)
	if cOS.isLinux():
		os.system('chown -R ' + cOS.getOSUsername() + ' ' + cacheDir)
	cOS.setEnvironmentVariable('ARK_CACHE', cacheDir)
	computerSettings['Local Cache setup'] = '1.0'

def saveComputerSettings():
	cOS.makeDir(os.path.dirname(setupConfigFile))

	with open(setupConfigFile, 'w') as outfile:
		json.dump(computerSettings, outfile)

	print 'Computer settings saved to {}'.format(setupConfigFile)

def setup(deadlineOnly=False):

	if deadlineOnly:
		installDeadline(deadlineOnly=deadlineOnly)
		return

	try:
		killJobProcesses.killJobProcesses()
	except Exception as err:
		print err

	environmentSetup()

	installAdditionalTools()

	installNuke()

	installMocha()

	installDJV()

	# installMaya()

	installMaya2018()

	installHoudini()

	installVRay()

	if not globalSettings.IS_NODE:
		installFusion()

	if not globalSettings.IS_NODE:
		installResolve()

	installHiero()

	installCinema4D()

	installNeatVideo()

	installFFMPEG()

	installShortcuts()

	installDeadline()

	# setKeybindings()

	if cOS.isWindows():
		installWindowsPrograms()
		if not globalSettings.IS_NODE:
			installSubstance()

	# installModo()

	# installMax()

	elif cOS.isLinux():
		installLinuxPrograms()

	installFonts()

	# installZBrushPlugin()

	setupCacheDir()

	# installMaxwell()

	# Copy startup link
	# if globalSettings.IS_NODE:
	# 	try:
	# 		source = arkInit.arkRoot + 'bin/nodeStartup.lnk'
	# 		startupDir = 'C:/Users/%s/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/' % globalSettings.OS_USERNAME
	# 		shutil.copy2(source, startupDir)
	# 		print 'Startup file copied to: ' + startupDir
	# 	except Exception as err:
	# 		print 'Could not copy startup file to: ' + startupDir
	# 		raise err

	saveComputerSettings()

if __name__ == '__main__':
	setup()
