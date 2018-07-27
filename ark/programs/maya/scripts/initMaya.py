import maya.OpenMaya as api
import maya.cmds as mc
import maya.mel as mel
import os
import functools

import sys
import xml.dom.minidom as xml

import maya.utils
import pymel.core as pymel

import arkInit
arkInit.init()

import settingsManager
globalSettings = settingsManager.globalSettings()
arkRoot = globalSettings.ARK_ROOT
import pathManager
import cOS

import translators
translator = translators.getCurrent()

import arkToolbar

import arkFTrack
pm = arkFTrack.getPM()

if pm.hasCurrentTask():
	import ftrackTask

	# import ftrack_connect.util
	# import ftrack_connect.asset_version_scanner
	# import ftrack_connect.config

	# from ftrack_connect_maya.connector import Connector
	# from ftrack_connect_maya.connector.mayacon import DockedWidget
	# from ftrack_connect.ui.widget.asset_manager import FtrackAssetManagerDialog
	# from ftrack_connect.ui.widget.import_asset import FtrackImportAssetDialog
	# from ftrack_connect_maya.ui.info import FtrackMayaInfoDialog
	# from ftrack_connect_maya.ui.publisher import PublishAssetDialog
	# from ftrack_connect_maya.ui.tasks import FtrackTasksDialog

	# connector = Connector()
	# dialogs = []
	# created_dialogs = dict()

app = None

def init():

	print 'globalSettings.ARK_ROOT + ark/tools/ ' + globalSettings.ARK_ROOT + 'ark/tools/'
	print 'globalSettings.MAYA_SCRIPT_ROOT ' + globalSettings.MAYA_SCRIPT_ROOT
	sys.path.append(globalSettings.ARK_ROOT + 'ark/tools/')

	try:
		pymel.commandPort(name=':7002', sourceType='python')
		pymel.commandPort(name=':10000', sourceType='mel')
	except:
		print 'Port init failed, nbd'
		pass

	api.MSceneMessage.addCallback(api.MSceneMessage.kMayaInitialized, enableDirMapping)
	api.MSceneMessage.addCallback(api.MSceneMessage.kMayaInitialized, loadRenderer)
	api.MSceneMessage.addCallback(api.MSceneMessage.kMayaInitialized, loadPlugin)


	# arkToolbar should only load in interactive mode
	if not mel.eval('about -batch'):
		api.MSceneMessage.addCallback(api.MSceneMessage.kMayaInitialized, initMayaSession)
		mc.scriptJob(event = ["SceneOpened", "initMaya.setupMayaAndFtrack();"], protected=True)
		mc.scriptJob(event = ["SceneOpened", "initMaya.loadHoudiniEngine();"], protected=True)
		# api.MSceneMessage.addCallback(api.MSceneMessage.kAfterOpen, setupMayaAndFtrack)
		# api.MSceneMessage.addCallback(api.MSceneMessage.kAfterNew, setupMaya)

		# atexit module doesn't work well with Maya, so need to explicitly clean up time log
		api.MSceneMessage.addCallback(api.MSceneMessage.kMayaExiting, ftrackClose)

	else:
		maya.utils.executeDeferred('import initMaya;initMaya.loadOrnatrix();')

	# api.MSceneMessage.addCallback(api.MSceneMessage.kAfterOpen, relocalize)

	# RUN THIS AUTOMATICALLY AT START. CALLBACK RUNS BEFORE ANY REFERENCE IS LOADED.
	# link: http://download.autodesk.com/us/maya/2011help/index.html?url=./files/File_referencing_Edit_reference_paths_in_the_Reference_Editor.htm,topicNumber=d0e136218
	# api.MSceneMessage.addCheckFileCallback(api.MSceneMessage.kBeforeLoadReferenceCheck, relocalizeReference)

	print 'Ingenuity Maya initialized'

# initialize ftrack info about the task, including ui dialogs
def ftrackOpen(*args):
	# global created_dialogs
	# global dialogs

	if pm.hasCurrentTask():
		currentEntity = pm.getTask()

		# dialogs = [
		# 	(FtrackImportAssetDialog, 'Import asset'),
		# 	(
		# 		functools.partial(PublishAssetDialog, currentEntity=currentEntity),
		# 		'Publish asset'
		# 	),
		# 	'divider',
		# 	(FtrackAssetManagerDialog, 'Asset manager'),
		# 	'divider',
		# 	(FtrackMayaInfoDialog, 'Info'),
		# 	(FtrackTasksDialog, 'Tasks')
		# ]
		# mc.evalDeferred("initMaya.loadAndInit()")

		# if not Connector.batch():
		# 	mc.scriptJob(e=["SceneOpened", "initMaya.scan_for_new_assets()"], permanent=True)
		# 	mc.scriptJob(e=["SceneOpened", "initMaya.refAssetManager()"], permanent=True)
			# temporarily disabled until people start setting frame range in ftrack
			# mc.evalDeferred("initMaya.framerateInit()")
			# mc.evalDeferred("initMaya.Connector.setTimeLine()")

		# ftrack_connect.config.configure_logging(
		# 	'ftrack_connect_maya', level='WARNING'
		# )

		ftrackTask.launch()
		pm.startTimerPrompt()

def ftrackClose(*args):
	try:
		if pm.hasCurrentTask():
			pm.stopTimer(context=pm.getTask())
	except:
		pass

def setVRayAsRenderer(*args):
	pymel.setAttr('defaultRenderGlobals.currentRenderer', 'vray', type='string')

def relocalize(*args):
	print 'Relocalizing File nodes!'
	result = translator.relocalizeNodes()
	if not result:
		print 'relocalizing failed!'

def enableDirMapping(*args):
	print 'Enabling DIR mapping.'
	mc.dirmap(en=True)

	# for Windows
	if cOS.isWindows():
		replaceOSName = 'linux'

	# for Linux
	if cOS.isLinux():
		replaceOSName = 'windows'

	for drive in globalSettings.DRIVES:
		fromPath  = globalSettings.PATHS[drive][replaceOSName][:-1]
		toPath = getattr(globalSettings, drive.upper())
		mc.dirmap(m = [fromPath, toPath])
		mc.dirmap(m = [fromPath.upper(), toPath])

def setupMayaAndFtrack(*args):
	print 'Setting VRay as renderer.'
	pymel.setAttr('defaultRenderGlobals.currentRenderer', 'vray', type='string')
	arkToolbar.launch()

	if pm.hasCurrentTask():
		ftrackOpen()

def callColorspace(node):
	translator.changeColorspace(node)

def setColorspaceScriptJob(node, clientData):
	if node.hasFn(api.MFn.kDagNode):
		name = api.MFnDagNode(node).fullPathName()
	else:
		name = api.MFnDependencyNode(node).name()

	if mc.objectType(name) == 'file':
		mel.eval('vray addAttributesFromGroup ' + name + ' "vray_file_gamma" 1')
		mc.scriptJob(attributeChange = [name + '.fileTextureName',
			'import arkInit;arkInit.init();import initMaya;initMaya.callColorspace(\"{0}\")'.format(name)], runOnce=False)

def loadOrnatrix():
	if not pymel.pluginInfo('Ornatrix', query=True, loaded=True):
		pymel.loadPlugin('Ornatrix')
		pymel.pluginInfo('Ornatrix', edit=True, autoload=True)
		print 'Loading plugin Ornatrix'

def loadPlugin(*args):
	# Load plugins
	if not pymel.pluginInfo('AbcImport', query=True, loaded=True):
		pymel.loadPlugin('AbcImport')
		pymel.pluginInfo('AbcImport', edit=True, autoload=True)
		print 'Loading plugin AbcImport'

def loadHoudiniEngine():
	if not pymel.pluginInfo('houdiniEngine', query=True, loaded=True):
		# Run this to avoid crashing Maya as soon as Houdini Engine plugin loads:
		# https://www.sidefx.com/forum/topic/51658/
		mel.eval('optionVar -iv "houdiniEngineSessionType" 2 -iv "houdiniEngineSessionPipeCustom" 0;')
		pymel.loadPlugin('houdiniEngine')
		pymel.pluginInfo('houdiniEngine', edit=True, autoload=True)
		print 'Loading plugin houdiniEngine'

# Callback
def loadRenderer(*args):
	# Set Vray renderer
	if not pymel.pluginInfo('vrayformaya', query=True, loaded=True):
		pymel.loadPlugin('vrayformaya')
		pymel.pluginInfo('vrayformaya', edit=True, autoload=True)
		print 'Loading plugin vrayformaya'
	print 'Setting vray as current renderer'

# checks for nodes which contain file attributes
# and replaces them after the file is opened
def setFilenodePaths(clientData=None):
	# return
	nodeDict = {
			'file': 'fileTextureName',
			'AlembicNode':'abc_File',
			'VRayLightIESShape': 'iesFile',
			'VRayScene': 'FilePath',
			'VRayMesh': 'fileName2',
			'VRayVolumeGrid': 'inFile',
			'imagePlane': 'imageName',
	}
	allObjects = pymel.ls(allPaths=True)

	for obj in allObjects:
		if pymel.objectType(obj) in nodeDict.keys():
			objType = pymel.objectType(obj)
			path = pymel.getAttr(obj + '.' + nodeDict[objType])

			newPath = translator.nonEnvironmentPath(path)

			# coz translatePathSearch returns a list
			# newPath = pathManager.translatePathSearch(newPath)[0]

		# FOR ENV VARIABLE PATHS, JUST IN CASE
			# if pymel.objectType(obj) in ['VRayVolumeGrid']:
			# 	newPath = translator.nonEnvironmentPath(path)
			# 	newPath = pathManager.translatePath(newPath)
			# 	print newPath
			# else:
			# 	newPath = translator.getEnvironmentPath(path)

			if newPath != path:
				try:
					pymel.setAttr(obj + '.' + nodeDict[objType], newPath)

				except:
					pass

# replace file paths on reference objects:
# done after file opens and before reference loads
def relocalizeReference(retCode=None, fileObject=None, clientData=None):
	print 'Relocalizing References'
	newPath = None

	path = fileObject.rawFullName()
	newPath = pathManager.localizePath(path)
	if not os.path.isfile(newPath):
		newPath = pathManager.globalizePath(path)

	fileObject.setRawFullName(newPath)
	api.MScriptUtil.setBool(retCode, True)


def initMayaSession(*args):
	print 'Initializing Maya ui'
	# create Ark Shelf
	if pymel.shelfLayout('Ingenuity', exists=True):
		pymel.deleteUI('Ingenuity')

	# Add ArkToolbar to Windows menu
	gMainWindowmenu = pymel.melGlobals['gMainWindowMenu']
	mel.eval('WindowMenu("%s")' % gMainWindowmenu)
	print mc.menuItem(label="Ark Toolbar", parent=gMainWindowmenu, command='import arkToolbar;arkToolbar.launch()')

	# get the top level shelf
	gShelfTopLevel = pymel.melGlobals['gShelfTopLevel']
	pymel.melGlobals.initVar('string', 'arkShelf')
	pymel.melGlobals['arkShelf'] = pymel.shelfLayout('Ingenuity', cellHeight=33, cellWidth=33, parent=gShelfTopLevel)

	xmlPath = globalSettings.MAYA_TOOLS_ROOT + 'ui/ingenuity.xml'
	iconsPath = globalSettings.MAYA_TOOLS_ROOT + 'ui/icons/'

	xmlMenuDoc = xml.parse(xmlPath)

	for shelfItem in xmlMenuDoc.getElementsByTagName('shelfItem') :
		annotation = shelfItem.attributes['ann'].value
		cmd = shelfItem.attributes['cmds'].value
		iconFile = shelfItem.attributes['icon'].value
		iconPath = os.path.join(iconsPath, iconFile)
		pymel.shelfButton(command=cmd, annotation=annotation, image=iconPath)

	print 'Ingenuity Maya ui initialized'

# Ftrack
############################################
# def open_dialog(dialog_class):
# 	'''Open *dialog_class* and create if not already existing.'''
# 	dialog_name = dialog_class

# 	if dialog_name not in created_dialogs:
# 		created_dialogs[dialog_name] = DockedWidget(dialog_class(connector=connector))

# 	created_dialogs[dialog_name].show()

# def loadAndInit():
# 	'''Load and Init the maya plugin, build the widgets and set the menu'''
# 	# Load the ftrack maya plugin
# 	mc.loadPlugin('ftrackMayaPlugin.py', quiet=True)
# 	# Create new maya connector and register the assets
# 	connector.registerAssets()

# 	# Check if maya is in batch mode
# 	if mc.about(batch=True):
# 		return

# 	gMainWindow = mel.eval('$temp1=$gMainWindow')
# 	if mc.menu('ftrack', exists=True):
# 		mc.deleteUI('ftrack')

# 	ftrackMenu = mc.menu(
# 		'ftrack',
# 		parent=gMainWindow,
# 		tearOff=True,
# 		label='ftrack'
# 	)

# 	# Register and hook the dialog in ftrack menu
# 	for item in dialogs:
# 		if item == 'divider':
# 			mc.menuItem(divider=True)
# 			continue

# 		dialog_class, label = item

# 		mc.menuItem(
# 			parent=ftrackMenu,
# 			label=label,
# 			command=(
# 				lambda x, dialog_class=dialog_class: open_dialog(dialog_class)
# 			)
# 		)

# def handle_scan_result(result, scanned_ftrack_nodes):
# 	'''Handle scan *result*.'''
# 	message = []
# 	for partial_result, ftrack_node in zip(result, scanned_ftrack_nodes):
# 		if partial_result is None:
# 			# The version was not found on the server, probably because it has
# 			# been deleted.
# 			continue

# 		scanned = partial_result.get('scanned')
# 		latest = partial_result.get('latest')
# 		if scanned['version'] != latest['version']:
# 			message.append(
# 				'{0} can be updated from v{1} to v{2}'.format(
# 					ftrack_node, scanned['version'], latest['version']
# 				)
# 			)

# 	if message:
# 		confirm = mc.confirmDialog(
# 			title='Scan result',
# 			message='\n'.join(message),
# 			button=['Open AssetManager', 'Close'],
# 			defaultButton='Close',
# 			cancelButton='Close',
# 			dismissString='Close'
# 		)

# 		if confirm != 'Close':
# 			global assetManagerDialog
# 			assetManagerDialog = FtrackAssetManagerDialog(connector=connector)
# 			assetManagerDialog.show()


# def scan_for_new_assets():
# 	'''Check whether there is any new asset.'''
# 	nodes_in_scene = mc.ls(type='ftrackAssetNode')

# 	check_items = []
# 	scanned_ftrack_nodes = []
# 	for ftrack_node in nodes_in_scene:
# 		if not mc.referenceQuery(ftrack_node, isNodeReferenced=True):
# 			asset_version_id = mc.getAttr('{0}.assetId'.format(ftrack_node))
# 			if asset_version_id is None:
# 				mc.warning(
# 					'FTrack node "{0}" does not contain data!'.format(ftrack_node)
# 				)
# 				continue

# 			component_name = mc.getAttr(ftrack_node + '.assetTake')
# 			check_items.append({
# 				'asset_version_id': asset_version_id,
# 				'component_name': component_name
# 			})
# 			scanned_ftrack_nodes.append(ftrack_node)

# 	if scanned_ftrack_nodes:
# 		import ftrack_api
# 		session = ftrack_api.Session(
# 			auto_connect_event_hub=False,
# 			plugin_paths=None
# 		)
# 		scanner = ftrack_connect.asset_version_scanner.Scanner(
# 			session=session,
# 			result_handler=(
# 				lambda result: ftrack_connect.util.invoke_in_main_thread(
# 					handle_scan_result,
# 					result,
# 					scanned_ftrack_nodes
# 				)
# 			)
# 		)
# 		scanner.scan(check_items)


# def refAssetManager():
# 	'''Refresh asset manager'''
# 	from ftrack_connect.connector import panelcom
# 	panelComInstance = panelcom.PanelComInstance.instance()
# 	panelComInstance.refreshListeners()


# def framerateInit():
# 	'''Set the initial framerate with the values set on the shot'''
# 	shot = pm.getShot()
# 	fps = str(round(shot.get('fps')))

# 	mapping = {
# 		'15': 'game',
# 		'24': 'film',
# 		'25': 'pal',
# 		'30': 'ntsc',
# 		'48': 'show',
# 		'50': 'palf',
# 		'60': 'ntscf',
# 	}

# 	fpsType = mapping.get(fps, 'pal')
# 	mc.warning('Setting current unit to {0}'.format(fps))
# 	mc.currentUnit(time=fpsType)




