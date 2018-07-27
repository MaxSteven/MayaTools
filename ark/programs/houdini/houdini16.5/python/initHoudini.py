
import os
import sys
import tempfile
import functools

import arkInit
arkInit.init()

import cOS

import settingsManager

globalSettings = settingsManager.globalSettings()
sys.path.append(globalSettings.ARK_ROOT + 'ark/ui')

import translators
translator = translators.getCurrent()
import hou

if os.environ.get('ARK_CURRENT_APP') == 'houdini':
	import houdiniMenuInit

	import arkFTrack
	pm = arkFTrack.getPM()

	import arkToolbar
	arkToolbar.launch()

	from ftrack_connect.ui.widget.import_asset import FtrackImportAssetDialog
	from ftrack_connect.ui.widget.asset_manager import FtrackAssetManagerDialog

	from ftrack_connect_houdini.connector import Connector
	from ftrack_connect_houdini.ui.info import FtrackHoudiniInfoDialog
	from ftrack_connect_houdini.ui.publisher import PublishAssetDialog
	from ftrack_connect_houdini.ui.tasks import FtrackTasksDialog

	if os.getenv('FTRACK_TASKID'):
		connector = Connector()
		connector.registerAssets()

# for ftrack directory structure
fxdirname = 'FX'
outdirname = 'out'

# ftrack stuff
createdDialogs = {}


def init(initFtrack=False):
	replaceFilePaths()

	result = translator.relocalizeNodes()
	if not result:
		print 'relocalizing failed!'
	hou.appendSessionModuleSource('hou.hscript("autosave on")')
	# hou.setUpdateMode(hou.updateMode.AutoUpdate)

	# note: makeDropdown and launchMenu never called
	# Ingenuity shelf is initiated automatically by ark.shelf
	# Houdini searches HOUDINI PATH/toolbar/ for any .shelf files
	# houdiniMenuInit.initMenu() and .launchMenu() are called from that xml file

	if os.environ.get('ARK_CURRENT_APP') == 'houdini' and initFtrack:
		ftrackSetup()

# code to replace file paths in houdini node attributes
# fix: capitalization of folders
def replaceFilePaths():
	# depends on which
	if cOS.isWindows():
		osName = 'windows'

	if cOS.isLinux():
		osName = 'linux'

	# for each drive entry in PATHS
	for drive, paths in globalSettings.PATHS.iteritems():
		osPath = paths[osName]
		# for each OS in that drive entry
		for replaceOS, replacePath in paths.iteritems():
			# replace if the OS isn't the current os
			if replaceOS != osName:
				# only replace from the beginning of the path
				# keeps /some/drive/footage/whatever/ from getting replaced
				if hou.hscript('opfind ' + replacePath[:-1]) != ('', '') or \
					hou.hscript('opfind ' + replacePath.upper()[:-1])  != ('', ''):
						hou.hscript('opchange ' + replacePath.upper()[:-1] + ' ' + osPath[:-1])
						hou.hscript('opchange ' + replacePath[:-1] + ' ' + osPath[:-1])


def makeDropdown():
	houdiniMenuInit.initMenu()

def launchMenu():
	houdiniMenuInit.launchMenu()

def ftrackSetup():
	print 'ftrack setup'

	if pm and pm.hasCurrentTask():
		# program opened through ftrack

		coolprint('Starting ftrack integration', 5, 5)

		# Set up ftrack environment
		setHouVars(pm.getTask())
		pm.startTimerPrompt()

		coolprint('ftrack integration successful', 5, 5)
	else:
		print 'File not opened through ftrack'

def coolprint(msg, leading, trailing):
	print('{}{}{}'.format('+'*leading, msg, '+'*trailing))

def setHouVars(task):
	"""Set the following custom houdini variables to be used with custom OTLs
	$SHOTPATH -- The path to where the houdini project lives
	$SHOTNAME -- Name of the shot
	$TASKNAME -- The current task
	"""

	shot = task['parent']
	commands = []

	# $SHOTPATH
	SHOTPATH = mkvar('SHOTPATH', pm.getPath(shot, checkPath=translator.getFilename()))
	commands.append(SHOTPATH)

	# $SHOTNAME
	SHOTNAME = mkvar('SHOTNAME', shot['name'])
	commands.append(SHOTNAME)

	# $TASK
	TASKNAME = mkvar('TASKNAME', task['name'])
	commands.append(TASKNAME)

	# Set all the vars
	for cmd in commands:
		print cmd
		hou.hscript(cmd)

# currently not used
def setFrameRangeData():
	start_frame = float(os.getenv('FS'))
	end_frame = float(os.getenv('FE'))
	shot = pm.getShot()
	fps = shot.get('fps')
	if 'handles' in shot.keys():
		handles = float(shot.get('handles'))
	else:
		handles = 0.0

	# add handles to start and end frame
	hsf = (start_frame - 1) - handles
	hef = end_frame + handles

	coolprint('Setting Frame Rate to {} fps'.format(fps), 10, 0)
	hou.setFps(fps)
	hou.setFrame(start_frame)

	try:
		if start_frame != end_frame:
			hou.hscript("tset {0} {1}".format((hsf) / fps,
						hef / fps))
			coolprint('Setting timeline: {} to {}'.format(start_frame, end_frame), 10, 0)
			hou.playbar.setPlaybackRange(start_frame, end_frame)
	except IndexError:
		pass

def mkvar(var_name, value):
	"""Quick way to generate an hscript command for setting vars"""
	cmd = 'set -g {}={}'.format(var_name, value)
	return cmd

# currently not used
def mkdirs(kw):
	# Bongo Format:
	#
	# workspace = jobs/showname/Workspaces/showcode_seqname/showcode_seqname_ARBITRARY_shotnum/
	# fxdir = workspace/fx
	# taskdir = workspace/fx/taskcode_v####.hip
	# cachedir = workspace/fx/out/geo
	# abcdir = workspace/fx/out/abc
	# flipdir = workspace/fx/out/flipbook
	# ifddir = workspace/renders/fx/ifds/taskcode/v####/taskcode_ropnode_v####.$F4.ifd.sc
	# rendersdir = workspace/renders/fx/taskcode/v####/taskcode_ropnode_v####.$F4.exr

	workspace = kw['workspace']
	taskname = kw['taskname']

	fxdir = os.path.join(workspace, fxdirname).replace('\\','/')

	taskdir = os.path.join(workspace, fxdirname, taskname).replace('\\','/')

	cachedir = os.path.join(workspace, fxdirname, outdirname, 'geo').replace('\\','/')

	abcdir = os.path.join(workspace, fxdirname, outdirname, 'abc').replace('\\','/')

	flipdir = os.path.join(workspace, fxdirname, outdirname, 'flipbook').replace('\\','/')

	rendersdir = os.path.join(workspace, 'renders', fxdirname, taskname).replace('\\','/')

	ifddir = os.path.join(rendersdir, 'ifds', taskname).replace('\\','/')

	chkdirs = [
		workspace,
		fxdir,
		taskdir,
		cachedir,
		abcdir,
		flipdir,
		rendersdir,
		ifddir
	]

	# Check if the shot workspace dir exists
	if os.path.exists(workspace):
		for d in chkdirs:
			if not os.path.exists(d):
				print('Directory {} does not exist. Creating...'.format(d))
				os.makedirs(d)
				print('Made directory at {}'.format(d))
	# Throw error that the shot needs to be created by a supe or something
	else:
		 hou.ui.displayMessage('Shot directory does not exist. Talk to a lead',
								buttons=('OK'),
								severity=hou.severityType.Error)

	# If no hipfile with matching taskname exists, set the session to be it
	matches = False
	search = 'fx.{}_v'
	for f in os.listdir(taskdir):
		if search in f:
			matches = True
	if not matches:
		hou.hipFile.setName(os.path.join(taskdir, '{}_v0001.hip'.format(taskname)).replace('\\','/'))

	coolprint('Shot info', 10, 10)
	coolprint('Show is: {}'.format(kw['showname']),10,0)
	coolprint('Sequence is: {}'.format(kw['seqname']), 10,0)
	coolprint('Shot is: {}'.format(kw['shotname']), 10,0)
	coolprint('Task is: {}'.format(kw['taskname']), 10,0)
	coolprint('', 100, 0)

# Ftrack
################################################

def writePypanel(panel_id):
	""" Write temporary xml file for pypanel """
	xml = """<?xml version="1.0" encoding="UTF-8"?>
<pythonPanelDocument>
  <interface name="{0}" label="{0}" icon="MISC_python" help_url="">
	<script><![CDATA[

import __main__

def createInterface():

	info_view = __main__.showDialog('{0}')

	return info_view]]></script>
	<help><![CDATA[]]></help>
  </interface>
</pythonPanelDocument>"""

	xml = xml.format(panel_id)

	path = os.path.join(tempfile.gettempdir(), '%s.pypanel' % panel_id)
	if os.path.exists(path):
		pass
	else:
		f = open(path, 'w')
		f.write(xml)
		f.close()
	return path


def FtrackDialogs(panel_id):
	""" Generate Dialog and create pypanel instance """

	pan_path = writePypanel(panel_id)
	hou.pypanel.installFile(pan_path)

	ftrack_id = 'Ftrack_ID'
	panel_interface = None

	try:
		for interface, value in hou.pypanel.interfaces().items():
			if interface == panel_id:
				panel_interface = value
				break
	except hou.OperationFailed:
		print 'Something Wrong with Python Panel'

	main_tab = hou.ui.curDesktop().findPaneTab(ftrack_id)

	if main_tab:
		panel = main_tab.pane().createTab(hou.paneTabType.PythonPanel)
		panel.showToolbar(False)
		panel.setActiveInterface(panel_interface)
	else:
		if panel_interface:
			hou.hscript("pane -S -m pythonpanel -o -n %s" % ftrack_id)
			panel = hou.ui.curDesktop().findPaneTab(ftrack_id)
			panel.showToolbar(False)
			panel.setActiveInterface(panel_interface)

def showDialog(name):
	""" Show Dialog """
	currentEntity = pm.getTask()

	if 'info' in name:
		dialogClass = FtrackHoudiniInfoDialog
	elif 'task' in name:
		dialogClass = FtrackTasksDialog
	elif 'import' in name:
		dialogClass = FtrackImportAssetDialog
	elif 'Manager' in name:
		dialogClass = FtrackAssetManagerDialog
	else:
		dialogClass = functools.partial(PublishAssetDialog, currentEntity=currentEntity)

	if dialogClass in createdDialogs:
		dialog = createdDialogs[dialogClass]
	else:
		dialog = dialogClass(connector=connector)
		createdDialogs[dialogClass] = dialog

	return dialog
