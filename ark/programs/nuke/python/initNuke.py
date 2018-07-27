
# Standard modules
##################################################
import os
# import traceback

import nuke
import settingsManager
import cOS
import arkNuke

import arkToolbar
try:
	import arkFTrack
	pm = arkFTrack.getPM()
	import ftrackTask
except:
	print 'No ftrack'

globalSettings = settingsManager.globalSettings()

def init():
	# Menu commands
	##################################################
	# ToolSets
	# toolsetMenu = nuke.menu('Nodes').menu('ToolSets')

	# arkMenu
	# arkMenu = nuke.menu('Nodes').addCommand('Ark','initNuke.launchMenu()', icon='ark.png')
	# makeDropdown()

	# Optical Flares
	##################################################
	toolbar = nuke.toolbar('Nodes')
	toolbar.addMenu('VideoCopilot', icon='VideoCopilot.png')
	toolbar.addCommand( 'VideoCopilot/OpticalFlares', "nuke.createNode('OpticalFlares')", icon='OpticalFlares.png')


	#Node overrides
	##################################################
	nukeOriginalCreateNode = nuke.createNode
	def createNodeOverrides(node, knobs="", inpanel=True):
		if node == 'Text2':
			node = 'Text'
		return nukeOriginalCreateNode(node=node, knobs=knobs, inpanel=inpanel)
	nuke.createNode = createNodeOverrides

	# Peregrine / pgBokeh
	##################################################
	# nuke.load("pgBokeh")
	# toolbar = nuke.toolbar("Nodes")
	# toolbar.addCommand( "Peregrine/pgBokeh", "nuke.createNode('pgBokeh')", icon="pgBokeh.png")

	# Maxwell
	##################################################
	# import maxwell_utilities

	# nodesMenu = nuke.menu('Nodes')
	# maxwellMenu = nodesMenu.addMenu('Maxwell Utilities', 'maxwell_icon.png')
	# maxwellMenu.addCommand('MxiMixer', 'nuke.createNode("MxiMixer")', 'ctrl+m', 'maxwell_icon.png')
	# maxwellMenu.addCommand('MaxwellSimulens', 'nuke.createNode("MaxwellSimulens")', '', 'maxwell_icon.png')
	# maxwellMenu.addCommand('MxiMask', 'nuke.createNode("MxiMask")', '', 'maxwell_icon.png')
	# maxwellMenu.addCommand('MxiRender', 'nuke.createNode("MxiRender")', '', 'maxwell_icon.png')
	# maxwellMenu.addCommand('Reload All', 'maxwell_utilities.reloadAllReads()', '', 'maxwell_icon.png')
	# maxwellMenu.addCommand('Reload Selected', 'maxwell_utilities.reloadSelectedReads()', '', 'maxwell_icon.png')
	# maxwellMenu.addCommand('Color Adjustments', 'maxwell_utilities.mxihue()', '', 'maxwell_icon.png')

	# Add invisible commands so they can be run via tab
	####################################################################
	# arkMenu = nuke.menu('Nodes').addMenu('Don\'t Click Me.', icon='blank_icon.png')
	arkMenu = nuke.menu('Nodes').addMenu('Ingenuity', icon='ark.png')
	networkToolset = nuke.menu('Nodes').addMenu('Network Toolsets')

	# needs to be added here so that networkToolset is a menu object not a menu item object
	networkToolset.addCommand('Refresh Toolsets','arkNuke.refreshToolsets()')
	networkToolset.addCommand('Create Network Toolset','arkNuke.createNetworkToolset()')
	arkNuke.refreshToolsets()

	# Add favorites directories
	####################################################################
	if cOS.isWindows():
		projectsDir = 'r:/'
		assetsDir = 'q:/assets/'
		footageDir = 'f:/'
	elif cOS.isLinux():
		projectsDir = '/ramburglar/'
		assetsDir = '/raidcharles/Assets/'
		footageDir = '/footage/'

	nuke.addFavoriteDir('ramburglar_projects', projectsDir, nuke.IMAGE | nuke.SCRIPT | nuke.FONT, tooltip='Projects', icon='r_small.png')
	nuke.addFavoriteDir('raidcharles_assets', assetsDir, nuke.IMAGE | nuke.SCRIPT | nuke.FONT, tooltip='Assets', icon='q_small.png')
	nuke.addFavoriteDir('footage_io', footageDir, nuke.IMAGE | nuke.SCRIPT | nuke.FONT, tooltip='Footage', icon='f_small.png')

	arkToolbar.launch()

	if os.getenv('ARK_CURRENT_APP') == 'nuke' and pm.hasCurrentTask():
		ftrackTask.launch()
		pm.startTimerPrompt()

	def addCommand(
		name,
		python,
		shortcut=None):

		'''
		Wrapped so if we need to do other stuff
		when adding commands we can
		'''
		arkMenu.addCommand(name, python, shortcut)

	gizmoMenu = arkMenu.addMenu('Gizmos')
	gizmoDirectory = globalSettings.NUKE_TOOLS_ROOT + 'gizmos'
	files = os.listdir(gizmoDirectory)
	files.sort()
	for f in files:
		fileParts = f.split('.')
		if fileParts[-1] == 'gizmo':
			# raise Exception(fileParts[0])
			# print fileParts[0]
			# print 'nuke.createNode("' + fileParts[0] + '")'
			gizmoMenu.addCommand(fileParts[0], 'nuke.createNode("%s")' % fileParts[0])


	addCommand('3D/Fix FBX','arkNuke.fixFBX()')

	addCommand('Cache/Cache Manager','tools.cacheManager.cacheManagerGui.launch()','ctrl+alt+c')
	# addCommand('Cache/Cache Read','arkNuke.cacheRead()')
	# addCommand('Cache/Cache Script','arkNuke.cacheScript()')
	# addCommand('Cache/Set Read Proxy','arkNuke.setReadProxy()','Ctrl+Shift+Y')

	addCommand('Comp/From','nuke.createNode("Merge2","operation from")')
	addCommand('Comp/Stencil','nuke.createNode("Merge2","operation stencil")')
	addCommand('Comp/Overlay','nuke.createNode("Merge2","operation overlay")')
	addCommand('Comp/Mask','nuke.createNode("Merge2","operation mask")')
	addCommand('Comp/Split Channels','arkNuke.splitChannels()')
	addCommand('Comp/Red Masks','arkNuke.createRedMasks()')
	addCommand('Comp/Red Mask Channel','arkNuke.maskWithRedChannel()','ctrl+m')
	addCommand('Comp/Auto Crop','arkNuke.autoCrop()')
	addCommand('Comp/ApplyShotColor','arkNuke.applyShotColor()')
	addCommand('Comp/Shuffle Magic', 'import shuffleMultiLight;shuffleMultiLight.launch()', 'alt+w')

	addCommand('CG/Blend Cameras','arkNuke.blendCameras()')
	addCommand('CG/Camera from EXR','arkNuke.cameraFromEXR()')
	addCommand('CG/Export Camera','arkNuke.exportCamera()')
	addCommand('CG/Export Tracker','arkNuke.exportTracker()')
	addCommand('CG/Falloff Calc','nuke.createNode("FalloffCalc")')
	addCommand('CG/PositionToPoints','nuke.createNode("PositionToPoints")')
	addCommand('CG/ZDepth Calc','nuke.createNode("ZDepthCalc")')

	addCommand('KeyRoto/Bezier','nuke.createNode("Bezier")','shift+p')
	addCommand('KeyRoto/Faded RotoPaint','arkNuke.fadedRotopaint()','alt+shift+p')

	addCommand('Projects/HK3/HK 3D Posting','arkNuke.hk3dPosting()')

	addCommand('Render/Submit to Deadline','arkNuke.farmSubmit()', 'Ctrl+Shift+B')
	addCommand('Render/IE Slate','arkNuke.ieSlate()')
	addCommand('Render/Force Render','arkNuke.forceRender()')
	addCommand('Render/Read From Write','arkNuke.readFromWrite()','Alt+Shift+r')
	addCommand('Render/Write DPX','arkNuke.writeDPX()')
	addCommand('Render/Write Final Render','arkNuke.writeFinal()','Ctrl+Shift+F')
	addCommand('Render/Write Final Stereo','arkNuke.writeFinalStereo()')
	addCommand('Render/Write Plates','arkNuke.writePlates()')
	addCommand('Render/Write PreComp', 'arkNuke.writePreComp()')
	addCommand('Render/Write Mattes', 'arkNuke.writeMattes()')
	addCommand('Render/Write Posting','arkNuke.writePosting()')
	addCommand('Render/Write Keyed Plates','arkNuke.writeKeyedPlates()')
	addCommand('Render/Write PR','arkNuke.writePRPass()')
	addCommand('Render/Multiple Write','arkNuke.multiplewrite()')
	addCommand('Render/Render Movie','arkNuke.makeMovie()')
	addCommand('Render/IE Render', 'arkNuke.ieRender()')

	addCommand('Studio/Increment and Save', 'arkNuke.incrementAndSave()', 'Alt+Shift+s')
	# addCommand('Studio/Shot Manager', 'import shotManager;shotManager.launch()', 'Ctrl+Shift+O')
	addCommand('Studio/Shot Builder', 'import shotBuilder;shotBuilder.launch()', 'Ctrl+Shift+O')
	addCommand('Studio/Proxy Manager','import proxyManager;proxyManager.launch()')
	addCommand('Studio/Super Render','arkNuke.runSuperRender()')
	addCommand('Studio/Ftrack Task','import ftrackTask;ftrackTask.launch()')
	addCommand('Studio/Network Copy', 'import nukeNetworkCopyPaste;nukeNetworkCopyPaste.launch()', 'Ctrl+Alt+c')
	addCommand('Studio/Network Paste', 'import nukeNetworkCopyPaste;nukeNetworkCopyPaste.pasteContent()', 'Ctrl+Alt+v')
	# addCommand('Studio/Save Like A Pro','arkNuke.incrementAndSave()','Alt+Shift+s')

	# addCommand('Studio/Run Weaver','import weaver;weaver.launch()')
	# addCommand('Studio/Run Weaver','import nuke/python/util/tool;tool.launch()')

	addCommand('Tracking/Grab Tracker Frame','arkNuke.grabTrackerFrame()','ctrl+shift+r')
	addCommand('Tracking/Track Next Frame','arkNuke.trackNextFrame()','ctrl+shift+e')
	addCommand('Tracking/Track Previous Frame','arkNuke.trackPreviousFrame()','ctrl+shift+w')
	addCommand('Tracking/Transform From Tracker','arkNuke.transformFromTracker()','Ctrl+Shift+T')
	addCommand('RotoShapesToTrackers/Bake Roto to Tracker','import RotoShapes_to_trackers;RotoShapes_to_trackers.RotoShape_to_Trackers()','Ctrl+Shift+J')
	addCommand('Tracking/Mocha Clear Front Anim','arkNuke.cornerpin_clearFromAnimation()')
	addCommand('Tracking/PFBarrel','nuke.tcl("PFBarrel")')
	addCommand('Tracking/Send to Mocha', 'arkNuke.sendToMocha()', 'ctrl+shift+m')

	addCommand('Utility/Align Nodes','print "sup";arkNuke.alignNodes()','alt+q')
	addCommand('Utility/Check Script','arkNuke.checkScript()')
	addCommand('Utility/Mirror Nodes','arkNuke.mirrorNodes()','alt+m')
	addCommand('Utility/Normalize Frame Range','arkNuke.normalizeFrameRange()')
	addCommand('Utility/R3D Timecode','arkNuke.r3dTimecode()')
	addCommand('Utility/Select Up','arkNuke.moveNodesUp()','ctrl+alt+up')
	addCommand('Utility/Select Down','arkNuke.moveNodesDown()','ctrl+alt+down')
	addCommand('Utility/Select Left','arkNuke.moveNodesLeft()','ctrl+alt+left')
	addCommand('Utility/Select Right','arkNuke.moveNodesRight()','ctrl+alt+right')
	addCommand('Utility/Set Text Names','arkNuke.setTextNames()')
	addCommand('Utility/Set BBox to B','arkNuke.setBoundingBoxB()','ctrl+alt+b')
	addCommand('Utility/Postage Stamp Off','arkNuke.disablePostage()','ctrl+alt+p')
	addCommand('Utility/backdropPro','arkNuke.createBackdrop()','shift+b')
	addCommand('Utility/frameholdCurrent','arkNuke.frameholdCurrent()','shift+f')
	addCommand('Utility/frameholdPro','arkNuke.frameholdPro()')
	addCommand('Utility/Clear Animation','arkNuke.clearAnimation()')
	addCommand('Utility/Bypass NukeX','arkNuke.bypassNukeX()','alt+shift+b')
	addCommand('Utility/Unlock Knobs','arkNuke.unlockKnobs()')
	addCommand('Utility/Scale Up','arkNuke.scaleNodes(1.1)',']')
	addCommand('Utility/Scale Down','arkNuke.scaleNodes(.9)','[')
	addCommand('Utility/Bake Camera','arkNuke.bakeCamera()')
	addCommand('Utility/Bake Gizmos','arkNuke.bakeGizmos()')
	addCommand('Utility/Frame Repair All','arkNuke.frameRepairAll()')
	addCommand('Utility/Load Read Geo Selection','arkNuke.loadReadGeoSelection()', 'ctrl+shift+l')
	addCommand('Utility/PNG from MOV', 'arkNuke.pngFromMov()')


	# Mocha Stuff
	#-----------------------------------------------------------------------------
	addCommand('Warp/Rotopaint to SplineWarp', 'arkNuke.rotoToWarpSpline()', 'F8')
	addCommand('Warp/Freeze Warp', 'arkNuke.freezeWarp()','shift+F8')
	addCommand('Warp/Tracker to SplineWarp', 'arkNuke.trackerToSplineWarp()','ctrl+F8')

	addCommand("Projectionist/Create a projector from this camera", 'import projectionist;projectionist.create_projector_panel()')
	addCommand("Projectionist/Create projection alley from this camera", 'import projectionist;projectionist.create_projection_alley_panel()')
	addCommand("Projectionist/Convert this camera to nodal with dolly axis", 'import projectionist;projectionist.convert_to_dolly()')
	addCommand("Projectionist/Make this camera nodal at 0", 'import projectionist;projectionist.make_selected_cam_nodal()')


	# Sapphire Toolbar
	#-----------------------------------------------------------------------------
	items = toolbar.items()
	saph = toolbar.addMenu('Sapphire', icon='Sapphire.png')

	for item in items:
		error = False
		if 'Sapphire' in item.name():
			saphSub = saph.addMenu(item.name())
			for fun in toolbar.findItem(item.name()).items():
				try:
					saphSub.addCommand(fun.name(), fun.script())
				except:
					print 'Could not add:', fun
					error = True
			if error:
				break
			toolbar.removeItem(str(item.name()))
