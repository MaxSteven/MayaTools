
# Standard modules
##################################################
import os
import re

# import sys
# import datetime
import shutil
import threading
import subprocess
# import sys
# import time
import pyseq
import json
# import glob
import math

# Application modules
##################################################
import nuke

# Our modules
##################################################
import arkInit
arkInit.init()
import arkUtil
import cOS
import pathManager
import baseWidget
# from hub import hub

try:
	from database import Database
	database = Database()
	if not database.getTime():
		nuke.message('Please make sure you are logged in Hub!')
		# to fix
		# import hub
		# hub.main()
		# import arkInit
		# os.system('python C:/ie/ark/tools/hub/hub.py')
		# raw_input()
		# sys.exit()

	else:
		from caretaker import Caretaker
		caretaker = Caretaker()
except:
	# caretaker is probably down
	nuke.message('Could not connect to caretaker! Final render might not work correctly.')

try:
	import deadline
	arkDeadline = deadline.arkDeadline.ArkDeadline()
except Exception as err:
	# network issues, webservice not running, etc
	print err
	nuke.message('Could not connect to Deadline: {}'.format(err))

import arkFTrack
pm = arkFTrack.getPM()

try:
	currentTask = pm.getTask()
	print 'Task:', currentTask['name']
	currentShot = pm.getShot()
	print 'Shot:', currentShot['name']
	currentProject = currentShot.get('project')
	print 'Project:', currentProject['full_name']
	if len(currentShot.get('ancestors')):
		currentSequence = currentShot['ancestors'][0]
		print 'Sequence:', currentSequence['name']
except:
	print 'File not opened through ftrack.'

import settingsManager
globalSettings = settingsManager.globalSettings()

import backdrop
import superRender
import translators
translator = translators.getCurrent()

# Mocha Stuff
##################################################
import TrackerToSplineWarp
import RotopaintToSplineWarp_v2
import freezeSplineWarp_v2

# fix: shouldn't have to do these like this
def rotoToWarpSpline():
	RotopaintToSplineWarp_v2.Roto_to_WarpSpline_v2()

def freezeWarp():
	freezeSplineWarp_v2.freezeWarp_v2()

def trackerToSplineWarp():
	TrackerToSplineWarp.main()

# Toolsets
##################################################
globalSettings.LOCAL_TOOLSETS = nuke.pluginPath()[0] + '/ToolSets'

# Node Functions
##################################################
def splitChannels():
	'''
	Split out all channels associated with selected node
	'''
	selectedNodes = nuke.selectedNodes()
	if len(selectedNodes) == 0:
		nuke.message('Please select one or more read nodes to split out')
		return False

	hSpace = 200
	for readNode in selectedNodes:
		if readNode.Class() != 'Read':
			continue
		xPos = readNode.xpos()
		yPos = readNode.ypos() + 200
		channels = []
		allChannels = readNode.channels()
		for c in allChannels:
			channels.append(c.split('.')[0])
		channels = list(set(channels))
		for c in channels:
			xPos += hSpace
			shuffle = nuke.nodes.Shuffle()
			shuffle.setXYpos(xPos,yPos)
			shuffle.setInput(0,readNode)
			shuffle['in'].setValue(c)
			shuffle.setName(c)

def bypassNukeX():
	knobs = ''
	for i in nuke.selectedNode().knobs():
		knobs = knobs + ' ' + i
	p = nuke.Panel('Bypass NukeX')
	p.addEnumerationPulldown('Knobs', knobs)
	p.addSingleLineInput('Value', '')
	p.show()
	if p.value('Value'):
		nuke.selectedNode()[p.value('Knobs')]\
			.setValue(float(p.value('Value')))

def bakeCameraKnob(oldCam, newCam, knob):
	if oldCam[knob].isAnimated() and not (oldCam[knob].animation(0).constant()):
		newCam[knob].setAnimated()
	return oldCam[knob]

def bakeCamera(bakeCam=None):
	if not bakeCam and len(nuke.selectedNodes()) > 0:
		bakeCam = nuke.selectedNode()
	else:
		nuke.message('No camera selected')
		return

	if not bakeCam.Class() in ['Camera2', 'Camera']:
		nuke.message('No camera selected')
		return

	firstFrame = int(nuke.numvalue('root.first_frame'))
	lastFrame = int(nuke.numvalue('root.last_frame'))
	step = 1
	frameRange = str(nuke.FrameRange(firstFrame, lastFrame, step))
	r = nuke.getInput('Enter Frame Range:', frameRange)

	camMatrix = bakeCam['world_matrix']

	newCam = nuke.nodes.Camera2()
	newCam.setInput(0, None)
	newCam['rotate'].setAnimated()
	newCam['translate'].setAnimated()

	knobNames = [
		'focal',
		'haperture',
		'vaperture',
		'near',
		'far',
		'focal_point',
		'fstop',
	]

	# knobs from old camera that have animation should be baked
	bakeKnobs = dict((knob, bakeCameraKnob(bakeCam, newCam, knob)) for knob in knobNames )

	newCam['win_translate'].setValue(bakeCam['win_translate'].value())
	newCam['win_scale'].setValue(bakeCam['win_scale'].value())

	for t in nuke.FrameRange(r):
		blankMatrix = nuke.math.Matrix4()
		for y in range(camMatrix.height()):
			for z in range(camMatrix.width()):
				blankMatrix[z+(y*camMatrix.width())] = camMatrix.getValueAt(t, (y+(z*camMatrix.width())))

		rotM = nuke.math.Matrix4(blankMatrix)
		rotM.rotationOnly()
		rot = rotM.rotationsZXY()

		newCam['rotate'].setValueAt(math.degrees(rot[0]), t, 0)
		newCam['rotate'].setValueAt(math.degrees(rot[1]), t, 1)
		newCam['rotate'].setValueAt(math.degrees(rot[2]), t, 2)
		newCam['translate'].setValueAt(camMatrix.getValueAt(t, 3), t, 0)
		newCam['translate'].setValueAt(camMatrix.getValueAt(t, 7), t, 1)
		newCam['translate'].setValueAt(camMatrix.getValueAt(t, 11), t, 2)

		for knobName, oldKnob in bakeKnobs.iteritems():
			if oldKnob:
				newCam[knobName].setValueAt(oldKnob.getValueAt(t), t)

	newCam['name'].setValue(bakeCam['name'].getValue() + '_baked')
	setXPos(newCam, getXPos(bakeCam) + 40)
	setYPos(newCam, getYPos(bakeCam))

	return newCam

# CDL
##################################################
def applyShotColor():
	# get the current shot
	taskInfo = caretaker.getTaskInfo()
	shot = taskInfo.shotNumber

	# find the shot
	shotData = database.findOne('shot')\
		.where('name','is',shot).execute()
	if not len(shotData):
		return nuke.message('Shot not found: ' + shot)

	node = nuke.createNode('applyShotColor')
	updateShotColor(node)
	#node['name'].setValue('CDL_Values')
	#node['name'].setValue('VIEWER_INPUT')
	node['label'].setValue(shotData['name'])

def updateShotColor(node=None):
	if not node:
		node = nuke.thisNode()

	if not node or node.Class() != 'applyShotColor':
		return nuke.message('Invalid node')

	# get the current shot
	taskInfo = caretaker.getTaskInfo()
	shot = taskInfo.shotNumber

	# find the shot
	shotData = database.findOne('shot')\
		.where('name','is',shot).execute()
	if not len(shotData):
		nuke.message('Shot not found: ' + shot)

	# parse the cdl values
	try:
		cdl = json.loads(shotData['cdl'])
	except Exception as err:
		nuke.message('Error loading cdl: ' + shotData['cdl'] + ' ' + err)

	# update them for the given node
	node['currentShot'].setValue(shotData['name'])
	node['slope'].setValue(cdl['slope'])
	node['offset'].setValue(cdl['offset'])
	node['power'].setValue(cdl['power'])
	node['saturation'].setValue(cdl['saturation'])

# Placement
##################################################
def moveNodesUp():
	'''
	Select all nodes above the currently selected node
	'''
	curYPos = nuke.selectedNode()['ypos'].getValue()
	# nuke.selectedNode()['selected'].setValue(False)
	for n in nuke.allNodes():
		if n['ypos'].getValue() < (curYPos - 40):
			# n['selected'].setValue(True)
			n['ypos'].setValue(n['ypos'].getValue() - 40)

def moveNodesDown():
	'''
	Select all nodes below the currently selected node
	'''
	curYPos = nuke.selectedNode()['ypos'].getValue()
	# nuke.selectedNode()['selected'].setValue(False)
	for n in nuke.allNodes():
		if n['ypos'].getValue() > (curYPos + 40):
			# n['selected'].setValue(True)
			n['ypos'].setValue(n['ypos'].getValue() + 40)

def moveNodesLeft():
	'''
	Select all nodes to the left of the currently selected node
	'''
	curXPos = nuke.selectedNode()['xpos'].getValue()
	# nuke.selectedNode()['selected'].setValue(False)
	for n in nuke.allNodes():
		if n['xpos'].getValue() < (curXPos - 80):
			# n['selected'].setValue(True)
			n['xpos'].setValue(n['xpos'].getValue() - 80)

def moveNodesRight():
	'''
	Select all nodes to the right of the currently selected node
	'''
	curXPos = nuke.selectedNode()['xpos'].getValue()
	# nuke.selectedNode()['selected'].setValue(False)
	for n in nuke.allNodes():
		if n['xpos'].getValue() > (curXPos + 80):
			# n['selected'].setValue(True)
			n['xpos'].setValue(n['xpos'].getValue() + 80)

def alignNodes():
	'''
	Intelligently align nodes horizontally or vertically.
	'''
	# could optimize this whole thing, but it works so who cares
	nodes = nuke.selectedNodes()
	numNodes = len(nodes)
	if numNodes < 1:
		return False

	connectionIn = None
	connectionOut = None
	# inNode = nodes[0]
	# outNode = nodes[0]
	for n in nodes:
		if n.input(0) != None and n.input(0) not in nodes:
			connectionIn = n.input(0)
			# inNode = n
		if len(n.dependent(nuke.INPUTS)) > 0 and n.dependent(nuke.INPUTS)[0] not in nodes:
			 connectionOut = n.dependent(nuke.INPUTS)[0]
			 # outNode = n

	if connectionIn != None:
		inXpos = getXPos(connectionIn)
		inYpos = getYPos(connectionIn)
	if connectionOut != None:
		outXpos = getXPos(connectionOut)
		outYpos = getYPos(connectionOut)

	if numNodes == 1:
		xSame = True
		ySame = True
	if connectionOut != None and connectionIn != None:
		if inXpos == outXpos:
			for n in nodes:
				setXPos(n,inXpos)
			return True
		if inYpos == outYpos:
			for n in nodes:
				setYPos(n,inYpos)
			return True
	if nodes[0].input(0) != None:
		inXPos = getXPos(nodes[0].input(0))
		inYPos = getYPos(nodes[0].input(0))
		xDif = abs(getXPos(nodes[0]) - inXPos)
		yDif = abs(getYPos(nodes[0]) - inYPos)
		if xDif != 0 and yDif != 0:
			xSame = False
			ySame = False
		if (xDif < yDif):
			setXPos(nodes[0],inXPos)
		else:
			setYPos(nodes[0],inYPos)
	if (xSame or ySame) and len(nodes[0].dependent(nuke.INPUTS)) > 0:
		dependentNode = nodes[0].dependent(nuke.INPUTS)[0]
		inXPos = getXPos(dependentNode)
		inYPos = getYPos(dependentNode)
		xDif = abs(getXPos(nodes[0]) - inXPos)
		yDif = abs(getYPos(nodes[0]) - inYPos)
		if (xDif < yDif and xDif != 0):
			setXPos(nodes[0],inXPos)
		else:
			setYPos(nodes[0],inYPos)
	return True

	if connectionOut != None or connectionIn != None:
		xSame = ySame = True
		firstXpos = getXPos(nodes[0])
		firstYpos = getYPos(nodes[0])
		for i in range(1,len(nodes)):
			if getXPos(nodes[i]) != firstXpos:
				xSame = False
			if getYPos(nodes[i]) != firstYpos:
				ySame = False

	if xSame:
		if connectionIn != None:
			setPos = inXpos
		else:
			setPos = outXpos
		for n in nodes:
			setXPos(n,setPos)
		return True
	if ySame:
		if connectionIn != None:
			setPos = inYpos
		else:
			setPos = outYpos
		for n in nodes:
			setYPos(n,setPos)
		return True

	xPositions = [getXPos(n) for n in nodes]
	yPositions = [getYPos(n) for n in nodes]
	xSpan = ySpan = 0
	for p1 in xPositions:
		for p2 in xPositions:
			dist = abs(p1-p2)
			if dist > xSpan:
				xSpan = dist
	for p1 in yPositions:
		for p2 in yPositions:
			dist = abs(p1-p2)
			if dist > ySpan:
				ySpan = dist

	xCenter=yCenter=False
	if (xSpan < ySpan):
		xCenter = sum(xPositions) / len(xPositions)
	else:
		yCenter = sum(yPositions) / len(yPositions)
	for n in nodes:
		if (xCenter):
			setXPos(n,xCenter)
		else:
			setYPos(n,yCenter)

def scaleNodes( xScale, yScale=None ):
	def getSideNodes( bd ):
		'''return a given backdrop node's "side nodes" (left, right, top and bottom most nodes) as a dictionary including the nodes and the respective DAG coordinates'''
		origSel = nuke.selectedNodes()
		[ n.setSelected( False ) for n in origSel ]

		bd.selectNodes()
		backdropNodes = nuke.selectedNodes()
		[ n.setSelected( False ) for n in backdropNodes ]  #DESELECT BACKDROP NODES
		[ n.setSelected( True ) for n in origSel ]  #RESTORE ORIGINAL SELECTION
		if not backdropNodes:
			return []

		leftNode = rightNode = bottomNode = topNode= backdropNodes[0] # START WITH RANDOM NODE
		for n in backdropNodes:
			if n.xpos() < leftNode.xpos():
				leftNode = n
			if n.xpos() > rightNode.xpos():
				rightNode = n
			if n.ypos() < topNode.ypos():
				topNode = n
			if n.ypos() > bottomNode.ypos():
				bottomNode = n

		return dict( left=[leftNode, nuke.math.Vector2( leftNode.xpos(), leftNode.ypos()) ], right=[rightNode, nuke.math.Vector2( rightNode.xpos(), rightNode.ypos()) ], top=[topNode, nuke.math.Vector2( topNode.xpos(), topNode.ypos()) ], bottom=[bottomNode, nuke.math.Vector2( bottomNode.xpos(), bottomNode.ypos()) ])

   # MAKE THINGS BACKWARDS COMPATIBLE
	yScale = yScale or xScale

   # COLLECT SIDE NODES AND COORDINATES FOR BACKDROPS
	backdrops = {}
	for bd in nuke.allNodes( 'BackdropNode' ):
		backdrops[bd] = getSideNodes( bd )

	# MOVE NODES FROM CENTRE OUTWARD
	nodes = [ n for n in nuke.selectedNodes() if n.Class() != 'BackdropNode' ]
	amount = len( nodes )
	if amount == 0:
		return

	allX = 0
	allY = 0
	for n in nodes:
		allX += n.xpos()
		allY += n.ypos()

	centreX = allX / amount
	centreY = allY / amount

	for n in nodes:
		n.setXpos( int( centreX + ( n.xpos() - centreX ) * xScale ) )
		n.setYpos( int( centreY + ( n.ypos() - centreY ) * yScale ) )

	#ADJUST BACKDROP NODES
	for bd,bdSides in backdrops.iteritems():
		if 'left' not in bdSides:
			continue
		leftDelta = bdSides['left'][0].xpos() - bdSides['left'][1].x
		topDelta = bdSides['top'][0].ypos() - bdSides['top'][1].y
		rightDelta = bdSides['right'][0].xpos() - bdSides['right'][1].x
		bottomDelta = bdSides['bottom'][0].ypos() - bdSides['bottom'][1].y


		bd.setXpos( int( bd.xpos() + leftDelta ) )
		bd.setYpos( int( bd.ypos() + topDelta ) )

		bd['bdwidth'].setValue( int( bd['bdwidth'].value() - leftDelta + rightDelta ) )
		bd['bdheight'].setValue( int( bd['bdheight'].value() - topDelta + bottomDelta ) )


# Utility
##################################################
def collectDependencies(node):
	def getDeps(node, deps):
		try:
			dependentNodes = nuke.dependencies(node)
			if not len(dependentNodes):
				return

			deps += dependentNodes
			for n in dependentNodes:
				getDeps(n, deps)
		except Exception as err:
			print 'Error getting dependencies:'
			if hasattr(node, 'name'):
				print node.name()
			else:
				print node
			print err
			return

	deps = []
	getDeps(node, deps)
	return deps

def getXPos(node):
	xPos = node['xpos'].getValue()
	return int(xPos + node.screenWidth() * .5)

def getYPos(node):
	yPos = node['ypos'].getValue()
	return int(yPos + node.screenHeight() * .5)

def setXPos(node, xPos):
	node['xpos'].setValue(int(xPos - node.screenWidth() * .5))

def setYPos(node, yPos):
	node['ypos'].setValue(int(yPos - node.screenHeight() * .5))

def getPlatesNode():
	# get all the valid plate nodes
	plateNodes = [n for n in nuke.allNodes() if n.Class() == 'Read' and '/Plates/' in n['file'].getValue()]

	# dumbly return the first one for now
	if len(plateNodes):
		return plateNodes[0]
	return False

def normalizeFrameRange():
	frameRange = translator.getAnimationRange()
	hasSlate = translator.getSceneData('hasSlateOffset')

	# if we have a slate and don't start at 0 or don't and don't start at 1 then time offset accordingly
	if (hasSlate and frameRange['startFrame'] != 0) or (not hasSlate and frameRange['startFrame'] != 1):
		nuke.createNode('TimeOffset','time_offset ' + str(-frameRange['startFrame'] + 1))

	# if we have a slate we start at zero
	if hasSlate:
		nuke.root().knob('first_frame').setValue(0)
		nuke.root().knob('last_frame').setValue(frameRange['endFrame'] - frameRange['startFrame'])
	# otherwise we don't need to offset for the slate so we start at 1
	else:
		nuke.root().knob('first_frame').setValue(1)
		nuke.root().knob('last_frame').setValue(frameRange['endFrame'] - frameRange['startFrame'] + 1)

def clearAnimation():
	for node in nuke.selectedNodes():
		for knob in node.knobs():
			node[knob].clearAnimated()

def getEndNode(node):
	if node.inputs() > 0:
		return getEndNode(node.input(0))
	return node

def setBoundingBoxB():
	'''
	Set bounding box to "B" in selected merge nodes
	'''
	for n in nuke.selectedNodes():
		if n.Class() == 'Merge2':
			n['bbox'].setValue('B')

def mirrorNodes():
	'''
	Mirror nodes horizontally or vertically
	'''

	nodes = nuke.selectedNodes()
	if len( nodes ) < 2:
		return False

	positions = [float(n.xpos() + n.screenWidth() * .5) for n in nodes ]
	axis = sum(positions) / len(positions)
	for n in nodes:
		n.setXpos(int( n.xpos() - 2*(n.xpos() + n.screenWidth()*.5 - axis)))

def setTextNames():
	for n in nuke.selectedNodes():
		if n.Class() == 'Text':
			n.setName(re.sub('[^a-zA-Z0-9_]','','t' + n['message'].getText().replace(' ','_'))[:12])

def disablePostage():
	'''Turn Off Postage Stamp'''
	for n in nuke.selectedNodes():
		try:
			n['postage_stamp'].setValue(False)
		except:
			pass

def cornerpin_clearFromAnimation():
	x = nuke.selectedNode()
	if x == 'CornerPin2D':
		x['from1'].clearAnimated()
		x['from2'].clearAnimated()
		x['from3'].clearAnimated()
		x['from4'].clearAnimated()

def transformFromTracker():
	if 'translate' and 'rotate' and 'scale' in nuke.selectedNode().knobs():
		x = nuke.selectedNode().name()
		px = nuke.selectedNode().xpos()
		py = nuke.selectedNode().ypos()

		b = nuke.nodes.Transform(name = x + '_link')
		b['translate'].setExpression('parent.' + str(x) + '.translate*(transMix*globalMix)')
		b['invert_matrix'].setExpression('Stabilize')
		b['rotate'].setExpression('parent.' + str(x) + '.rotate*(rotMix*globalMix)')
		b['scale'].setExpression('(1-((scaleMix*globalMix)*(1-parent.'+str(x)+'.scale)))')
		b['center'].setExpression('parent.'+str(x)+'.center')
		b.setXYpos( px, py+50 )
		b.knob('tile_color').setValue( 1442840575L )
		b['label'].setValue('[if {[value invert_matrix]==true} {return "Stabilize"} {return "Matchmove"}]')

		stab = nuke.Boolean_Knob ("Stabilize","Stabilize")
		b.addKnob(stab)
		transMix = nuke.Double_Knob ("transMix","transMix")
		b.addKnob(transMix)
		transMix.setValue(1)
		globalMix = nuke.Double_Knob ("globalMix","globalMix")
		b.addKnob(globalMix)
		globalMix.setValue(1)
		scaleMix = nuke.Double_Knob ("scaleMix","scaleMix")
		b.addKnob(scaleMix)
		scaleMix.setValue(1)
		rotMix = nuke.Double_Knob ("rotMix","rotMix")
		b.addKnob(rotMix)
		rotMix.setValue(1)
	else:
		nuke.message('Not a Tracker!')

def setReadProxy():
	nuke.root()['proxy_type'].setValue('scale')
	nuke.root()['proxy_scale'].setValue(.5)
	for n in nuke.selectedNodes():
		if n.Class() == 'Read':
			filename = n['file'].getValue()
			pathInfo = cOS.getPathInfo(filename)
			# proxy plates are always jpgs
			proxyFilename = pathInfo['dirname'] + 'Proxy/' + pathInfo['basename'].replace(pathInfo['extension'],'jpg')
			n['proxy'].setValue(proxyFilename)

def r3dTimecode():
	selNode = nuke.selectedNode()
	textNode = nuke.createNode('Text')
	textNode.knob('message').setValue("[python nuke.toNode('" + selNode.name() + "').metadata('r3d/absolute_time_code')]")
	textNode.knob('size').setValue(200)
	textNode.knob('translate').setValue((1480,-1000))
	textNode.knob('label').setValue('R3d Timecode')

def frameRepairAll():
	viewers = translator.getNodesByType('viewer')
	if len(viewers) == 0:
		raise Exception('Scene is missing a viewer node.')
	else:
		viewer = viewers[0]

	selectedNodes = translator.getSelectedNodes()
	for n in selectedNodes:
		translator.selectNode(n)
		if n.getType() == 'read':
			error = {'start': None, 'end': None}
			first = n.getProperty('first')
			last = n.getProperty('last')
			for f in range(first, last + 1):
				viewer.setProperty('frame', f)
				if n.nativeNode().treeHasError():
					if not error['start']:
						error['start'] = f
					error['end'] = f
				else:
					if error['start'] and error['end']:
						if error['start'] == first:
							nuke.message('{}: Can\'t repair frames at start, skipping.'.format(n.name()))
						else:
							repairNode = translator.ensureNode(nuke.createNode('FrameRepair'))
							repairNode.setProperty('badFrame', error['start'])
							repairNode.setProperty('EndFrame', error['end'])
							repairNode.setProperty('RangeCheck', not error['start'] == error['end'])
					error['start'] = None
					error['end'] = None

			if error['start'] and error['end']:
				nuke.message('{}: Can\'t repair frames at end, skipping.'.format(n.name()))
		else:
			nuke.message('Non-read node selected, skipping.')

def pngFromMov():
	ffmpeg = globalSettings.FFMPEG_EXE
	node = translator.getSelectedNode()

	if node.getType() == 'read':
		filePath = node.getProperty('file')
		filePath = translator.nonEnvironmentPath(filePath)

		if os.path.isfile(filePath):
			rootDir, fileName = os.path.split(filePath)
			projName = os.path.splitext(fileName)[0]
			imgFolder = cOS.join(rootDir, projName)
			pngPath = cOS.join(imgFolder, projName) + '_%04d.png'

			if not cOS.makeDir(imgFolder):
				nuke.message("Failed to create directory for PNG sequence")
				return

			os.system(ffmpeg + ' -i ' + filePath + ' ' + pngPath)

			node.setProperty('file', pngPath)
		else:
		 	nuke.message("Read points to a directory that does not exist")
	else:
		return nuke.message("Select a Read Node")


# Faded Rotopaint (not totally working)
##################################################
def fadedRotopaint():
	node = nuke.createNode('RotoPaint')
	fadeTab = nuke.Tab_Knob('Faded Paint')
	node.addKnob(fadeTab)
	uk = nuke.nuke.Boolean_Knob('Enable', 'Enable',True)
	node.addKnob(uk)
	uk = nuke.nuke.Int_Knob('duration', 'Duration')
	node.addKnob(uk)
	node['duration'].setValue(10)
	uk = nuke.nuke.Int_Knob('fadeoff', 'FadeOff')
	node.addKnob(uk)
	node['fadeoff'].setValue(5)
	uk = nuke.nuke.PyScript_Knob('apply', 'Apply to selection','arkNuke._fadedRotopaint(nuke.thisKnob())')
	node.addKnob(uk)
	node['knobChanged'].setValue('arkNuke._fadedRotopaint()')

def _fadedRotopaint():
	node = nuke.thisNode()
	knob = nuke.thisKnob()
	shps = nuke.thisNode()['curves'].getSelected()
	frame = nuke.frame()
	duration = int(node['duration'].value())
	fadeoff = int(node['fadeoff'].value())

	for shp in shps:
		if 'Layer object' in str(shp) or 'Faded' in shp.name:
			continue
		attrs = shp.getAttributes()
		opacityCurve = attrs.getCurve(attrs.kOpacityAttribute)
		opacityCurve.reset()
		opacityCurve.addKey(frame-duration-fadeoff-5, 0)
		opacityCurve.addKey(frame-duration-fadeoff, 0)
		opacityCurve.addKey(frame-duration, 1)
		opacityCurve.addKey(frame+duration, 1)
		opacityCurve.addKey(frame+duration+fadeoff, 0)
		opacityCurve.addKey(frame+duration+fadeoff+5, 0)
		keyCount = opacityCurve.getNumberOfKeys()
		for i in range(keyCount):
			opacityCurve.getKey(i).ra = 1
			opacityCurve.getKey(i).la = 1
			opacityCurve.getKey(i).lslope = 0
			opacityCurve.getKey(i).rslope = 0
		shp.getAttributes().set('ltt',4)
		shp.getAttributes().set('ltn',frame-duration-fadeoff)
		shp.getAttributes().set('ltm',frame+duration+fadeoff)
		shp.name = 'Faded ' + shp.name + '{{fade ' +\
			str(fadeoff) + '}}{{duration ' + str(duration) +\
			'}}{{at ' + str(nuke.frame()) + '}}'
		nuke.thisNode()['curves'].changed()

	if knob.name() == 'curves':
		if node['Enable'].value() == True:
			pass
			# faded()
		else:
			shps = node['curves'].getSelected()
			for shp in shps:
				if 'Layer object' in str(shp) or 'Not Faded' in shp.name:
					continue
				shp.name = 'Not Faded ' + shp.name
				nuke.thisNode()['curves'].changed()

# Tools
##################################################
def getOutputs(node):
	'''
	Return a dictionary of the nodes and pipes that are connected to node
	'''
	depDict = {}
	dependencies = node.dependent(nuke.INPUTS | nuke.HIDDEN_INPUTS)
	for d in dependencies:
		depDict[d] = []
		for i in range(d.inputs()):
			if d.input(i) == node:
				depDict[d].append(i)
	return depDict

def fixOverlappingNodes(minSpacing=20,
	xThreshold=50):
	allNodes = nuke.allNodes()
	allNodes.sort(key=lambda n: n.ypos())

	offset = 0
	for i, node in enumerate(allNodes):
		nodeY = node.ypos() + node.screenHeight()
		offset = 0
		for lowerNode in allNodes[i+1:]:
			lowerY = lowerNode.ypos()
			yDiff = lowerY - nodeY
			if yDiff < minSpacing:
				offset = minSpacing - yDiff

		if offset != 0:
			for lowerNode in allNodes[i+1:]:
				lowerNode.setYpos(lowerNode.ypos() + offset)

		for output in getOutputs(node).keys():
			if output.ypos() < node.ypos():
				output.setYpos(node.ypos() + node.screenHeight() + offset)

def isNativeGizmo(gizmo):
	'''
	Check if gizmo is in default install path
	'''
	plugDir = cOS.normalizeAndJoin(os.path.dirname(nuke.env['ExecutablePath']), 'plugins')
	return gizmo.filename().startswith(plugDir)

def bakeGizmos(group=nuke.Root()):
	# recursively burrows into gizmos converting them
	# in to groups if they are not nuke standard gizmos
	with group:
		for n in nuke.allNodes():
			n.setSelected(False)
		for node in nuke.allNodes():
			if isinstance(node, nuke.Gizmo) and not isNativeGizmo(node):
				with node:
					outputs = getOutputs(node)
					group = node.makeGroup()
					# Reconnect inputs and outputs if any
					if outputs:
						for n, pipes in outputs.items():
							for i in pipes:
								n.setInput(i, group)
					for i in range(node.inputs()):
						group.setInput(i, node.input(i))
					# set node position and name
					group.setXYpos(node.xpos(), node.ypos())
					name = node.name()
					nuke.delete(node)
					group.setName(name)
					node = group

			if node.Class() == 'Group':
				bakeGizmos(node)

def blendCameras():
	'''
	Connect two different camera animations
	into one camera that has the ability to
	transition between both cameras
	'''
	# Grab Nodes
	nodes = translator.getSelectedNodes()

	if (len(nodes) != 2 or
		not nodes[0].getType() == 'camera' or
		not nodes[1].getType() == 'camera'):
		nuke.message('Must select two camera nodes')
		return False

	if (nodes[0].getProperty('useMatrix') or nodes[1].getProperty('useMatrix')):
		nuke.message('Camera transforms must be specified by translation, rotation, and scale values, not by matrix.')
		return False

	# Deselect all nodes
	nuke.selectAll()
	nuke.invertSelection()

	# Create new camera node
	cam = nuke.createNode('Camera')
	cam.setName('Blend_camera')

	# Create user knob for blending between cameras
	cam.addKnob(nuke.nuke.Double_Knob('blend','Blend'))
	cam['blend'].setValue( 0)

	cam.addKnob(nuke.nuke.String_Knob('camera0','Camera0'))
	cam['camera0'].setValue(nodes[0].name())
	cam.addKnob(nuke.nuke.String_Knob('camera1','Camera1'))
	cam['camera1'].setValue(nodes[1].name())

	cam['translate'].setExpression('[knob camera1].translate*blend.0+[knob camera0].translate*(1-blend.0)')
	# rotate needs mod to interpolate the smallest angle of the two rotations
	cam['rotate'].setExpression('((([knob camera1].rotate - [knob camera0].rotate) + 180) % 360 - 180) * blend.0 + [knob camera0].rotate')
	cam['scaling'].setExpression('[knob camera1].scaling*blend.0+[knob camera0].scaling*(1-blend.0)')
	cam['uniform_scale'].setExpression('[knob camera1].uniform_scale*blend.0+[knob camera0].uniform_scale*(1-blend.0)')

	knobs = ['focal', 'haperture', 'vaperture', 'near', 'far', 'focal_point', 'fstop']
	for knob in knobs:
		expression = '[knob camera1].{0}*blend.0+[knob camera0].{0}*(1-blend.0)'.format(knob)
		cam.knob(knob).setExpression(expression)

def cameraFromEXR(readNode=None):
	'''
	Create a camera from EXR
	'''
	if readNode == None:
		readNode = nuke.selectedNode()
	if not(readNode.Class() == 'Read' and cOS.getExtension(readNode['file'].getValue()) == 'exr' and readNode.metadata('exr/cameraFocalLength') != None):
		nuke.message('Please select an exr read node with embedded camera data')
		return False
	cam = nuke.nodes.Camera2()
	setXPos(cam,getXPos(readNode)-200)
	setYPos(cam,getYPos(readNode))
	cam['useMatrix'].setValue(True)
	m = cam['matrix']
	m.isAnimated(True)
	cam['near'].setValue(.1)
	cam['far'].setValue(100000)

	startFrame = int(readNode['first'].getValue())
	endFrame = int(readNode['last'].getValue())
	if (endFrame - startFrame) < 1:
		animRange = range(0,1)
	else:
		animRange = range(startFrame,endFrame)
	for t in animRange:
		cam['focal'].setValueAt(readNode.metadata('exr/cameraFocalLength',t),t)
		cam['haperture'].setValueAt(readNode.metadata('exr/cameraAperture',t),t)
		cam['vaperture'].setValueAt( float(readNode.metadata('input/height',t))/float(readNode.metadata('input/width',t)) * float(readNode.metadata('exr/cameraAperture',t)),t)
		# cam['near'].setValueAt(readNode.metadata('exr/cameraNearClip',t),t)
		# cam['far'].setValueAt(readNode.metadata('exr/cameraFarClip',t),t)
		cam['focal_point'].setValueAt(readNode.metadata('exr/cameraTargetDistance',t),t)
		cam['fstop'].setValueAt(readNode.metadata('exr/cameraFNumber',t),t)

		camMatrix = nuke.math.Matrix4()
		matrixList = readNode.metadata('exr/cameraTransform',t)
		for i in range(0,16):
			camMatrix[i] = matrixList[i]

		transposedMatrix = nuke.math.Matrix4(camMatrix)
		transposedMatrix.transpose()
		swapMatrix = nuke.math.Matrix4(transposedMatrix)

		transposedMatrix[0] = swapMatrix[0]
		transposedMatrix[1] = -swapMatrix[2]
		transposedMatrix[2] = swapMatrix[1]
		transposedMatrix[3] = swapMatrix[3]*10

		transposedMatrix[4] = swapMatrix[8]
		transposedMatrix[5] = -swapMatrix[10]
		transposedMatrix[6] = swapMatrix[9]
		transposedMatrix[7] = swapMatrix[11]*10

		transposedMatrix[8] = -swapMatrix[4]
		transposedMatrix[9] = swapMatrix[6]
		transposedMatrix[10] = -swapMatrix[5]
		transposedMatrix[11] = -swapMatrix[7]*10

		transposedMatrix[12] = swapMatrix[12]
		transposedMatrix[13] = swapMatrix[13]
		transposedMatrix[14] = swapMatrix[14]
		transposedMatrix[15] = swapMatrix[15]

		m.setKeyAt(t)
		for i in range(0,16):
			m.setValue(transposedMatrix[i],i,t)

	return cam

def incrementAndSave():
	script = translator.getFilename()

	newScript = cOS.incrementVersion(script, initials=pm.getInitials())
	if not newScript:
		nuke.scriptSave()

	nuke.scriptSaveAs(newScript)

def createBackdrop():
	backdrop.launch()

def runSuperRender():
	superRender.main()

def createRedMasks():
	node = nuke.selectedNode()
	group = nuke.createNode(
		'Group',
		'name RedMasks tile_color 1',
		False)
	table = nuke.Table_Knob('name', 'label')
	group.addKnob(table)
	booleanCheckBox = None
	chanList = []
	for channel in node.channels():
		if channel.lower().startswith('m_'):
			if channel.endswith('.red'):
				mlist = nuke.Boolean_Knob(channel, booleanCheckBox)
				mlist.setFlag(nuke.STARTLINE)
				chanList.append(channel)
				group.addKnob(mlist)

	group.begin()
	nuke.createNode('Input', '', False)
	nuke.createNode(
		'Expression',
		' channel3 rgba expr3 ' + 'masks',
		False)
	nuke.createNode('Output', '', False)
	group.end()

def maskWithRedChannel():
	'''
	Mask Red Mask in color nodes with knob maskChannelInput
	'''
	panel = nuke.Panel('Select Red Masks')
	node = nuke.selectedNode()
	chanList = []

	if 'maskChannelInput' in node.knobs():
		for i in node.channels():
			if i.startswith('M_'):
				if i.endswith('.red'):
					chanList.append(i)
		panel.addEnumerationPulldown(
			'Red Mask:',
			str(chanList).replace("'", "").replace(", ","\n").strip("[]"))
		panel.show()
		enumVal = panel.value('Red Mask:')
		if enumVal is not None:
			node['maskChannelInput'].setValue(enumVal)
	else:
		nuke.message('Can only operate on nodes with maskChannelInput knob')

def frameholdCurrent():
	frameHold = nuke.createNode('frameholdCurrent')
	frameHold.knob('first_frameNode').setValue(nuke.frame())

def frameholdPro():
	p = nuke.Panel('Frame Hold Pro')
	p.addEnumerationPulldown('Do', 'Play Stop')
	p.addEnumerationPulldown('Where', 'After Before At')
	p.addSingleLineInput('Frame', '')
	p.show()
	do = p.value('Do')
	where = p.value('Where')
	frame = p.value('Frame')
	node = nuke.createNode("FrameHold")['first_frame']
	if where == 'After':
		where = '>'
		if do == 'Play':
			node.setExpression('frame'+where+frame+' ? frame :'+frame)
		else:
			node.setExpression('frame'+where+frame+' ? '+frame+' : frame')
	elif where == 'Before':
		where = '<'
		if do == 'Play':
			node.setExpression('frame'+where+frame+' ? frame :'+frame)
		else:
			node.setExpression('frame'+where+frame+' ? '+frame+' : frame')
	elif where == 'at':
		where = '>'
		if do == 'Stop':
			node.setExpression('frame'+where+frame+' ? frame :'+frame)
		else:
			node.setExpression('frame'+where+frame+' ? '+frame+' : frame')

def autoCrop():
	'''
	Use Nukes autocrop on selected nodes
	'''
	import nukescripts
	nodes = nuke.selectedNodes()
	for node in nodes:
		nukescripts.autocrop()

def fixMetadata():
	fps = nuke.root()['fps'].getValue()
	if not nuke.thisNode().metadata() or 'input/timecode' not in nuke.thisNode().metadata():
		return ''

	source = nuke.thisNode().metadata()['input/timecode']

	(hours, minutes, seconds, frames) = [int(param) for param in source.split(':')]

	totalFrames = hours * 60 * 60 * fps + minutes * 60 * fps + seconds * fps + frames

	hours = int(totalFrames / 60.0 / 60 / fps)
	totalFrames -= hours * 60 * 60 * fps
	minutes = int(totalFrames / 60.0 / fps)
	totalFrames -= minutes * 60 * fps
	seconds = int(float(totalFrames) / fps)
	totalFrames -= seconds * fps
	fps = round(totalFrames)

	return '%02d:%02d:%02d:%02d' % (hours, minutes, seconds, fps)

def timer():
	#shotFPS = nuke.root()['fps'].getValue()
	hours = nuke.thisNode()['hours'].getValue()
	minutes = nuke.thisNode()['minutes'].getValue()
	seconds = nuke.thisNode()['seconds'].getValue()
	frames = nuke.thisNode()['frames'].getValue()
	offset = nuke.thisNode()['startframe'].getValue()
	timeBase = nuke.thisNode()['timeBase'].getValue()
	#determine if time sub-seconds is 24 or 60
	if timeBase == 1:
		shotFPS = 60.0
	else:
		shotFPS = 24.0

	# totalFrames = (hours * 60 * 60 * shotFPS + minutes * 60 * shotFPS + seconds * shotFPS + frames) - offset

	#determine if counting up or down
	countDirection=nuke.thisNode()['countDirection'].getValue()
	if countDirection == 1:
		totalFrames = (hours * 60 * 60 * shotFPS + minutes * 60 * shotFPS + seconds * shotFPS + frames) - offset
		totalFrames += nuke.frame()
	else:
		totalFrames = (hours * 60 * 60 * shotFPS + minutes * 60 * shotFPS + seconds * shotFPS + frames) + offset
		totalFrames -= nuke.frame()

	hours = int(totalFrames / 60.0 / 60 / shotFPS)
	totalFrames -= hours * 60 * 60 * shotFPS
	minutes = int(totalFrames / 60.0 / shotFPS)
	totalFrames -= minutes * 60 * shotFPS
	seconds = int(float(totalFrames) / shotFPS)
	totalFrames -= seconds * shotFPS
	frames = round((totalFrames*shotFPS) / shotFPS)

	if totalFrames < 0:
		hours = 60 - hours
		minutes = 60 - minutes
		seconds = 60 - seconds
		frames = shotFPS - frames

	return '%02d:%02d:%02d:%02d' % (hours, minutes, seconds, frames)

def readFromWrite():
	'''
	Use pyseq to help create Read node from selected Write node
	'''

	node = nuke.selectedNode()
	if node.Class() == 'Write' or 'file' in node.knobs():
		if 'colorspace' in node.knobs():
			colorspace = node['colorspace'].toScript()
		else:
			colorspace = 'linear'

		filePath = node['file'].value()
		# get the real path, not the [getenv ramburglar] path
		filePath = translator.nonEnvironmentPath(filePath)
		dirName = os.path.dirname(filePath)
		renderlist = []
		if os.path.exists(dirName):
			for i in os.listdir(dirName):
				renderlist.append(i)
			getSeq = pyseq.get_sequences(renderlist)
			for i in getSeq:
				fullPath = [ dirName + '/' + i.format('%h%p%t') , i.format('%s'), i.format('%e')]
				if fullPath[0] == filePath:
					readNode = nuke.createNode('Read', 'file ' + fullPath[0] + ' first ' + fullPath[1] + ' last ' + fullPath[2]  + ' origfirst ' + fullPath[1] + ' origlast ' + fullPath[2] )
					readNode['colorspace'].fromScript(colorspace)
					readNode.knob('localizationPolicy').setValue('off')
		else:
			nuke.message("Directory Write points to does not exist")
	else:
		return nuke.message("Select a Write Node")

def sendToMocha():
	readNode = nuke.selectedNode()
	if readNode.Class() != 'Read':
		return nuke.message('Select a read node...')

	filePath = readNode['file'].getValue()
	# get the real path, not the [getenv ramburglar] path
	filePath = translator.nonEnvironmentPath(filePath)
	# mocha on linux doesn't listen to % paths,
	# so we find the first frame and stick that in
	if '%' in filePath:
		filePath = filePath % readNode['first'].getValue()

	if cOS.isWindows():
		mochaCommand = '"' + globalSettings.MOCHA_EXE + '" ' + filePath
	elif cOS.isLinux():
		mochaCommand = [
			globalSettings.MOCHA_EXE,
			filePath
		]

	subprocess.Popen(mochaCommand)

# Checks
##################################################
def checkSlateOffset():
	animRange = translator.getAnimationRange()
	if animRange['startFrame'] == 999:
		nuke.root().knob('last_frame')\
			.setValue(nuke.root().knob('last_frame')
				.getValue() - 1)
		nuke.root().knob('first_frame')\
			.setValue(nuke.root().knob('first_frame')
				.getValue() + 1)
		translator.setSceneData('hasSlateOffset', True)
	elif animRange['startFrame'] == 1000:
		translator.setSceneData('hasSlateOffset', True)

	slateOffset = translator.getSceneData('hasSlateOffset')
	if slateOffset:
		return

	nuke.root().knob('last_frame')\
		.setValue(nuke.root().knob('last_frame')
			.getValue() + 1)
	nuke.root().knob('first_frame')\
		.setValue(nuke.root().knob('first_frame')
			.getValue() - 1)

	translator.setSceneData('hasSlateOffset', True)

def checkFileNode(node):
	# print 'checking:', node['file'].getValue()
	cleanPath = cOS.unixPath(node['file'].getValue())
	# get the real path, not the [getenv ramburglar] path
	cleanPath = translator.nonEnvironmentPath(cleanPath)

	cleanPath = cleanPath.replace('####','%04d')
	cleanPath = pathManager.translatePath(cleanPath)
	# cleanPath = cOS.findCaseInsensitiveFilename(cleanPath)

	# stuff to do with cache nodes

	# if '%' in cleanPath and 'first' in node.knobs():
	# 	firstFrame = node['first'].getValue()
	# 	if not os.path.isfile(cleanPath % firstFrame):
	# 		print 'not found'
	# 		labelPath = node['label'].getValue()
	# 		if labelPath and '%' in labelPath:
	# 			cleanPath = labelPath
	# 		node['label'].setValue('')
	# else:
	# 	if not os.path.isfile(cleanPath):
	# 		print 'not found'
	# 		cleanPath = node['label'].getValue()
	# 		node['label'].setValue('')

	node['file'].setValue(cleanPath)

	# originalFile = node['file'].getText()
	#FIX: we just swap %v with left eye for now, need to properly check eventually
	# originalFile = originalFile.replace('%v','l')
	# if (originalFile[0] == 'R'):
	# 	baseFile = 'Q' + originalFile[1:]
	# 	if (firstFrame == lastFrame or originalFile.find('%') == -1):
	# 		if os.path.isfile(originalFile):
	# 			return True
	# 		else:
	# 			node['file'].setValue(baseFile)
	# 	else:
	# 		for f in range(firstFrame,lastFrame+1):
	# 			if (not os.path.isfile(originalFile % f)):
	# 				node['file'].setValue(baseFile)

def checkRootKnobs():
	root = nuke.root()
	root['onScriptLoad'].setValue('arkNuke.scriptLoad()')
	root['onScriptSave'].setValue('arkNuke.scriptSave()')
	root['onScriptClose'].setValue('arkNuke.scriptClose()')

def checkScript(force=False):
	if os.environ.get('ARK_CURRENT_APP') == 'nuke_cl' and not force:
		return True

	print 'arkNuke.checkScript'

	root = nuke.root()
	checkRootKnobs()

	# only add the timeline_write_node if it doesn't exist
	if 'timeline_write_node' not in root.knobs():
		studioKnob = nuke.Tab_Knob('studio', 'Studio')
		root.addKnob(studioKnob)
		timelineKnob = nuke.String_Knob('timeline_write_node')
		root.addKnob(timelineKnob)

	timelineNodeValue = root['timeline_write_node'].getValue()
	if timelineNodeValue:
		nodeExists = nuke.exists(timelineNodeValue)

	# if the write node isn't already set,
	# try to find the final renders node and fill it in
	if not timelineNodeValue or not nodeExists:
		finalRenderNodes = nuke.allNodes('finalRender')
		if len(finalRenderNodes):
			root['timeline_write_node'].setValue(finalRenderNodes[0].name())
		else:
			for node in nuke.allNodes('Write'):
				if 'final_renders' in node['file'].getValue().lower():
					root['timeline_write_node'].setValue(node.name())

	# fileNodes = translator.getCacheableNodes()
	# fix: hax, this should run through translators
	fileNodeTypes = [
			'Read',
			'ReadGeo2',
			'Camera2',
			'WriteGeo',
			'Write',
			'finalRender',
		]
	fileNodes = []
	for nodeType in fileNodeTypes:
		fileNodes += nuke.allNodes(nodeType)

	for node in fileNodes:
		try:
			checkFileNode(node)
		except:
			print 'failed in checkFileNode'

	viewers = nuke.allNodes('Viewer')
	for node in viewers:
		node['channels'].setValue('rgba')

	# bail if we're in the autoConversion script
	# fix: hax, but hax below as well, remove both
	if 'formats.nk' in nuke.root()['name'].getValue():
		return

	# try to auto-fix colorspaces
	colorspaces = {
		'linear': 'linear',
		'srgb': 'sRGB',
		'rec709': 'rec709',
		'cineon': 'Cineon',
		'redlog': 'REDLog',
		'alexa': 'AlexaV3LogC',
		'slog1': 'SLog1',
		'slog2': 'SLog2',
		'slog3': 'SLog3',
		'clog': 'CLog',
		'panalog': 'Panalog',
	}

	# search for colorspaces key in file value
	# if found set colorspace accordingly
	for readNode in nuke.allNodes('Read'):
		# only set colorspace once
		# if int(readNode['gl_color'].getValue()) == 16711935:
		# 	continue
		filename = readNode['file'].getValue().lower()

		# skip jpgs
		if '.jpg' in filename or '.jpeg' in filename:
			continue

		matched = False
		for match, colorspace in colorspaces.iteritems():
			if match in filename:
				readNode['colorspace'].setValue(colorspace)
				matched = True
				break
		# slog is handled as a special case
		if not matched and 'slog' in filename:
			readNode['colorspace'].setValue('SLog')
		# readNode['gl_color'].setValue(16711935)

	# check write nodes
	writeNodes = nuke.allNodes('Write')
	# the write node inside a finalRender node already has this set
	for writeNode in writeNodes:
		writeNode['beforeRender'].setValue(
			'arkNuke.beforeRender()')

	writeNodes += nuke.allNodes('finalRender', nuke.root())

	# set filepaths of precomp nodes

	# In order to render optical flares on the farm, we are no longer
	# Versioning up precomp nodes.
	# preCompNodes = nuke.allNodes('IE_PreComp', nuke.root())
	# for preComp in preCompNodes:
		# preComp['file'].setValue(getPrecompOutput(preComp))

	# writeNodes += preCompNodes

	if nuke.env['gui']:

		try:
			nuke.root()['fps'].setValue(pm.getInfo(currentProject, 'fps'))
		except:
			print 'Could not find a project'
			return False

		filename = translator.getFilename()
		if filename:
			versionString = pm.getInfo(currentTask, 'versionString')
			for writeNode in writeNodes:
				filename = writeNode['file'].getValue()
				versionedFilename = re.sub(r'[vV][0-9]+', versionString, filename)

				# translate the path for the current OS
				versionedFilename = pathManager.translatePath(versionedFilename)
				versionedFilename = cOS.findCaseInsensitiveFilename(versionedFilename)

				writeNode['file'].setValue(versionedFilename)

			setSlateInfo()

def setSlateInfo():
	if not nuke.env['gui']:
		return

	taskInfo = pm.getInfo(currentTask)
	if not taskInfo.get('version') == None:
		allSlateNodes = nuke.allNodes('ieSlate') + nuke.allNodes('finalRender')
		for slate in allSlateNodes:
			slate['shot'].setValue(currentShot.get('name'))
			slate['version'].setValue(taskInfo.get('versionString')[1:])
			slate['artist'].setValue(pm.getName())
			slate['project'].setValue(currentProject.get('full_name'))

			# if 'burnIn' in slate.knobs():
			# 	slate['burnIn'].setValue(False)

def validMetadata(node):
	# only valid if hours or minutes are greater than 0
	try:
		timecodeParts = node.metadata()['input/timecode'].split(':')
		if int(timecodeParts[0]) > 0 or int(timecodeParts[1]) > 0:
			return True
		return False
	except:
		return False
	return True

# Ftrack
##################################################
def ftrackLoad():
	pass
	# eventually we'll read in the frame start and end, once people actually set the frame range in ftrack
	# if os.getenv('FS'):
	# 	nuke.root()['first_frame'].setValue(float(os.getenv('FS')))
	# if os.getenv('FE'):
	# 	nuke.root()['last_frame'].setValue(float(os.getenv('FE')))

# Events
##################################################
def scriptLoad():
	checkScript()
	replaceFilePaths()
	result = translator.relocalizeNodes()
	if not result:
		print 'relocalizing failed!'

	loadReadGeoSelection()
	if os.getenv('ARK_CURRENT_APP') == 'nuke':
		ftrackLoad()

def replaceFilePaths():
	nodesToIgnore = [
		'ofxcomabsoftneatvideov'
	]
	nodes = translator.getAllNodes()
	for node in nodes:
		if not node.getType() in nodesToIgnore:
			for knob in node.nativeNode().knobs():
				# check if knob value is a string or not to reduce computations
				if isinstance(node.nativeNode().knob(knob).getValue(), basestring):
					path = node.nativeNode().knob(knob).getValue()

					newPath = translator.nonEnvironmentPath(path)
					newPath = pathManager.translatePath(newPath)
					if newPath != path and not node.nativeNode().knob(knob).getFlag(nuke.READ_ONLY):
						node.nativeNode().knob(knob).setValue(newPath)

def scriptSave():
	saveReadGeoSelection()


	# Linux is case sensitive, Windows isn't
	# this fixes r:/project/FINAL_RENDERS/ from not
	# writing to r:/Project/Final_Renders/ and instead
	# making two folders and messing everything up
	filename = translator.getFilename()
	nuke.root()['name'].setValue(cOS.findCaseInsensitiveFilename(filename))

	if not nuke.env['gui']:
		return

	checkScript()
	threading.Timer(10.0, localScriptBackup).start()

	name = nuke.root().name()
	if not re.search('_[vV][0-9]+',name):
		raise Exception,'No version number found in the script name.\nShould be "filename_v0001_abc.nk"'
	else:
		print 'Version Saved'

def scriptClose():
	print 'ark.scriptClose'
	try:
		if pm.hasCurrentTask():
			pm.stopTimer(context=currentTask)
	except:
		pass
	saveReadGeoSelection()
	checkScript()
	localScriptBackup()

def loadReadGeoSelection():
	for node in nuke.allNodes('ReadGeo2'):
		if 'ark_selection' in node.knobs():
			try:
				items = json.loads(node['ark_selection'].getValue())
				node['scene_view'].setSelectedItems(items)
			except:
				print 'Error loading items for:', node.name()

def saveReadGeoSelection():
	for node in nuke.allNodes('ReadGeo2'):
		if 'scene_view' not in node.knobs():
			continue
		if 'ark_selection' not in node.knobs():
			tab = nuke.Tab_Knob('ingenuity', 'Ingenuity')
			selectionKnob = nuke.String_Knob('ark_selection','Selection')
			node.addKnob(tab)
			node.addKnob(selectionKnob)
		node['ark_selection'].setValue(json.dumps(node['scene_view'].getSelectedItems()))

def checkNodes():
	if nuke.thisNode().Class() == 'Root':
		checkRootKnobs()
	elif nuke.thisNode().Class() == 'Write':
		nuke.thisNode()['beforeRender']\
			.setValue('arkNuke.beforeRender()')

def beforeRender(node=None):
	'''
	Performs misc options before launching a render
	Turn off postage stamps, builds directory if one
	does not exist
	'''

	if not node:
		node = nuke.thisNode()

	node['postage_stamp'].setValue(0)
	nuke.root()['proxy'].setValue(0)

	# we only perform this check if we're in gui mode
	# as it crashes Hiero
	if nuke.env['gui']:
		# don't check for slate since it's built in to gizmo now
		# if 'ieSlate' not in [n.Class() for n in nuke.allNodes()]:
		# 	raise Exception('No slate found, please add IE Slate before rendering!')
		# setSlateInfo()
		# setWritePath(node)
		checkScript()

	filename = node['file'].getValue()
	# get the real path, not the [getenv ramburglar] path
	filename = translator.nonEnvironmentPath(filename)
	makeWriteDir(filename)

	# Linux is case sensitive, Windows isn't
	# this fixes r:/project/FINAL_RENDERS/ from not
	# writing to r:/Project/Final_Renders/ and instead
	# making two folders and messing everything up
	filename = cOS.findCaseInsensitiveFilename(filename)
	node['file'].setValue(filename)

	if 'final_renders' in filename.lower() and \
		'exr_linear' in filename.lower():
		node['afterRender'].setValue(
			'arkNuke.afterFinalRender()')
		if not validMetadata(node):
			raise Exception('Invalid metadata, please connect ' +
				'the metadata input and ensure it\'s correct')

	for node in nuke.allNodes('Read'):
		if 'decoder' in node.knobs():
			data = translator.getSceneData('codec')

			if data == 'mov64':
				node['decoder'].setValue('mov64')
			else:
				node['decoder'].setValue('mov32')

	# remove any extra files that we don't need
	# first we build a list of valid files
	# taskInfo = pm.getTaskInfo()
	# validFiles = []
	# if '%04d' in filename or '%06d' in filename:
	# 	for frame in range(taskInfo['startFrame'], taskInfo['endFrame']):
	# 		validFiles.append(filename % frame)

	# if nuke.env['gui']:
	#	pathInfo = cOS.getPathInfo(filename)
	# 	# then we build a glob of the actual files there matching the framebase
	# 	fileGlob = pathInfo['dirname'] + pathInfo['filebase'] + '*'
	# 	for filename in glob.glob(fileGlob):
	# 		filename = filename.replace('\\','/')
	# 		if filename not in validFiles:
	# 			try:
	# 				os.remove(filename)
	# 				print 'Removed ' + filename
	# 			except:
	# 				print 'Could not remove: ' + filename

def afterFinalRender(node=None):
	if not node:
		node = nuke.thisNode()

	# bail if we're inside NS or Hiero
	# fix: need to fire this before close if we're in Nuke Studio
	database = Database()
	database.connect()
	if not database:
		return nuke.message('the Database can\'t be contacted! Let somebody know about this.')

	# fix: this is hax but not bad, not really a better solution
	# should check against shepherd jobs root from settings and see if that's in path
	if nuke.root()['name'].getValue().lower().find('temp/jobs') != -1 or \
		globalSettings.IS_NODE:
		print 'afterFinalRender skipped for Shepherd jobs and nodes'
		return True

	versionPath = node['file'].getValue()
	# get the real path, not the [getenv ramburglar] path
	versionPath = translator.nonEnvironmentPath(versionPath)
	# versions always use windows paths
	versionPath = pathManager.translatePath(versionPath, 'windows')

	filePath = translator.getFilename()

	if 'exr_linear' not in versionPath.lower():
		print 'Not a Final Render, bailing'
		return

	try:
		print 'Submitting draft job to deadline'
		deadlineJob = deadline.jobTypes.NukeComp()
		frameRange = translator.getAnimationRange()
		jobData = {
			'output': versionPath,
			'name': cOS.getPathInfo(translator.getFilename())['name'],
			'frameRange': '{}-{}'.format(frameRange['startFrame'], frameRange['endFrame'])
		}
		jobInfo = deadlineJob.getDraftJobInfo(jobData)
		pluginInfo = deadlineJob.getDraftPluginInfo(jobData)
		print arkDeadline.submitJob(jobInfo, pluginInfo)
	except:
		print 'Could not submit Draft job, no Quicktime will be created'

	# these have to be before the path is translated from the native shared root
	project = caretaker.getProjectFromPath(filePath)
	shotName = caretaker.getShotNameFromPath(filePath)

	# translate the file path to windows after getting the project
	filePath = pathManager.translatePath(filePath, 'windows')
	if not project:
		return nuke.message('Project not found: ' + filePath)

	shot = caretaker.getEntityFromField('shot','name',shotName)
	if not shot:
		raise Exception('No shot exists for this comp!', filePath.split('/')[-3], filePath.split('/')[1])

	# create comp asset if not present
	assetData = {
		'project': project['_id'],
		'name': shot['name'] + '_comp',
		'type': 'comp',
		'shot': shot['_id'],
		'status': 'working',
	}
	print 'assetData:', assetData
	asset = caretaker.createOrUpdateEntityByField(
		'asset',
		['shot','type'],
		assetData)

	print 'asset is', asset

	# create render version if not present
	versionNumber = cOS.getVersion(versionPath)
	print 'version number is', versionNumber
	animationRange = translator.getAnimationRange()
	renderVersionData = {
		'name': 'EXR_Linear',
		'type': 'exr',
		'asset': asset['_id'],
		'number': versionNumber,
		'startFrame': animationRange['startFrame'],
		'endFrame': animationRange['endFrame'],
		'path': versionPath,
		'sequence': True,
		'status': 'complete',
	}
	print 'renderVersionData:', renderVersionData
	caretaker.createOrUpdateEntityByField(
		'version',
		'path',
		renderVersionData)

	# create source file version if not present
	sourceVersionData = renderVersionData
	extension = cOS.getExtension(filePath)
	sourceVersionData.update({
		'name': extension,
		'type': extension,
		'number': versionNumber,
		'sequence': False,
		'path': pathManager.translatePath(filePath, 'windows'),
		'sourceFile': True,
		'status': 'working',
	})
	print 'sourceVersionData:', sourceVersionData
	caretaker.createOrUpdateEntityByField(
		'version',
		'path',
		sourceVersionData)


# Caching
##################################################
def cacheRead(node=0, firstFrame=0, lastFrame=0):
	if not node:
		node = nuke.selectedNode()
	if node:
		if (not firstFrame):
			firstFrame = int(node.knob('first').getValue())
		if (not lastFrame):
			lastFrame = int(node.knob('last').getValue())
		originalFile = node['file'].getText()
		# get the real path, not the [getenv ramburglar] path
		originalFile = translator.nonEnvironmentPath(originalFile)

		#fix: need better # matching code
		originalFile = originalFile.replace('####','%04d')
		if (originalFile[0].lower() == 'q'):
			newFile = 'R' + originalFile[1:]
			makeWriteDir(newFile)
			if (cOS.getExtension(originalFile) == 'r3d'):
				originalDir = cOS.getDirName(originalFile)
				newDir = 'R' + originalDir[1:]
				for f in os.listdir(originalDir):
					if cOS.getExtension(f) == 'r3d':
						shutil.copyfile(originalDir + f,newDir + f)
			elif (firstFrame == lastFrame or originalFile.find('%') == -1):
				shutil.copyfile(originalFile,newFile)
			else:
				for f in range(firstFrame,lastFrame+1):
					shutil.copyfile(originalFile % f,newFile % f)
			node['file'].setValue(newFile)
	else:
		nuke.message('No node was specified.  Please select the node you wish to cache')

def cacheScript():
	# nuke.toNode('preferences').knob('autoLocalCachePath').setValue(globalSettings.SHARED_ROOT)

	readNodes = nuke.allNodes('Read')
	for r in readNodes:
		cacheRead(r,int(r.knob('first').getValue()),int(r.knob('last').getValue()))


# Deadline
##################################################
def farmSubmit(node=None):
	'''Submit the selected write node to the render farm, deadline'''
	checkScript()
	if node:
		nodes = arkUtil.ensureArray(node)
	else:
		nodes = nuke.selectedNodes()

	import deadlineSubmit
	for node in nodes:
		filename = node['file'].getValue()
		# get the real path, not the [getenv ramburglar] path
		filename = translator.nonEnvironmentPath(filename)

		makeWriteDir(filename)

		# Linux is case sensitive, Windows isn't
		# this fixes r:/project/FINAL_RENDERS/ from not
		# writing to r:/Project/Final_Renders/ and instead
		# making two folders and messing everything up
		filename = cOS.findCaseInsensitiveFilename(filename)

		if 'final_renders' in filename.lower() and not validMetadata(node):
			raise Exception('Invalid metadata, please connect the metadata input')

		translator.setRenderNode(node)
		deadlineSubmit.launch()

# IO
##################################################
def localScriptBackup():
	try:
		originalFilename = nuke.root()['name'].getValue()
		newFilename = globalSettings.TEMP + \
			'NukeBackup' + originalFilename[2:]
		makeWriteDir(newFilename)
		if os.path.isfile(originalFilename):
			shutil.copyfile(originalFilename,newFilename)
	except Exception as err:
		print 'Local backup failed:', err

def makeWriteDir(writeDir):
	if (writeDir):
		writeDir = '/'.join(writeDir.split('/')[:-1]) + '/'
		if (writeDir.find('%v') == -1):
			writeDir = os.path.dirname(writeDir)
			if not os.path.isdir(writeDir):
				os.makedirs(writeDir)
		else:
			writeDirLeft = writeDir.replace('%v','L')
			writeDirRight = writeDir.replace('%v','R')
			if not os.path.isdir(writeDirLeft):
				os.makedirs(writeDirLeft)
			if not os.path.isdir(writeDirRight):
				os.makedirs(writeDirRight)

def ieSlate(connected = True):
	'''
	Typical IE generated slate
	'''
	checkSlateOffset()
	# normalizeFrameRange()
	slate = nuke.nodes.ieSlate()
	if connected and len(nuke.selectedNodes()):
		selectedNode = nuke.selectedNode()
		slate.setInput(0, selectedNode)
		xStart = getXPos(selectedNode)
		yStart = getYPos(selectedNode)
		setXPos(slate, xStart)
		setYPos(slate, yStart + 100)

	setSlateInfo()
	slate.setSelected(True)

	return slate

def writeFinal():
	'''Write files to HD_Renders folder of the current job'''
	endNode = nuke.selectedNode()
	checkSlateOffset()

	filename = translator.getFilename()
	version = cOS.getVersion(filename)

	output = pm.getFinalRenderPath(
		currentTask,
		version,
		format='EXR_Linear',
		ext='exr'
	)
	finalRenderNode = nuke.nodes.finalRender(name='finalRender', file=output)

	if len(nuke.selectedNodes()):
		setXPos(finalRenderNode, getXPos(endNode))
		setYPos(finalRenderNode, getYPos(endNode) + 100)

	dotNodes = [n for n in nuke.allNodes() if n.Class() == 'Dot' and 'metadot' in n.name()]
	if not len(dotNodes):
		dotNode = nuke.nodes.Dot()
		setXPos(dotNode, getXPos(finalRenderNode) + 200)
		setYPos(dotNode, getYPos(finalRenderNode))
		dotNode['hide_input'].setValue(True)
		platesNode = getPlatesNode()
		if platesNode:
			dotNode.setInput(0, platesNode)
	else:
		dotNode = dotNodes[0]

	finalRenderNode.setInput(0, endNode)
	finalRenderNode.setInput(1, dotNode)

	setSlateInfo()

	nuke.show(finalRenderNode)
	return finalRenderNode

def writePlates():
	'''Create jpgs for smaller image size and ease of use'''
	plater = nuke.createNode('Write','file_type jpg _jpeg_quality 1')

	reader = None
	line = []

	# Get write node inputs
	for i in range(plater.inputs()):
		line.append(plater.input(i))

	# Search write node connections and look for a node that is reading in plates
	while len(line) > 0:
		toPop = line[0]
		if toPop != None and toPop.Class() == 'Read':
			if 'Plates' in toPop['file'].value():
				reader = toPop
				break
		else:
			if toPop != None:
				for i in range(toPop.inputs()):
					if toPop.input(i) != None:
						line.append(toPop.input(i))
				line.remove(toPop)

	# If we couldn't find a plate reader, error out
	if reader == None:
		nuke.message('ERROR: Could not find read node for plates')
		nuke.delete(plater)
		return

	# Otherwise, use the plate reader to determine the output path
	else:
		path = reader['file'].value()
		sequence = path.split('/')[-1]
		path = cOS.getDirName(path)
		path = path[:-1] + '_forCG/'
		baseName = sequence.split('.')[0]
		sequence = sequence.replace(baseName, baseName + '_forCG')
		sequence = cOS.removeExtension(sequence) + '.jpg'
		path = path + sequence
		plater['file'].setValue(path)

def writePreComp():
	cropNode = nuke.createNode('Crop')
	cropNode['box'].setExpression('input.width', 2 )
	cropNode['box'].setExpression('input.height', 3 )

	preCompRenderNode = nuke.createNode('IE_PreComp')
	preCompRenderNode['name'].setValue('precomp')
	preCompRenderNode['passName'].setValue('denoised')

	preCompRenderNode.setInput(0, cropNode)

	output = getPrecompOutput(preCompRenderNode)
	with preCompRenderNode:
		nuke.toNode('write')['file'].setValue(output)

	return preCompRenderNode

def writeMattes():
	endNode = nuke.selectedNode()
	fps = translator.getFPS()

	metaDataNode = nuke.nodes.ModifyMetaData()
	metaDataNode.setInput(0, endNode)
	metaDataNode['metadata'].fromScript('set input/frame_rate ' + str(fps))

	shuffleNode = nuke.nodes.Shuffle()

	shuffleNode.setInput(0, metaDataNode)
	shuffleNode['red'].setValue('alpha')
	shuffleNode['blue'].setValue('alpha')
	shuffleNode['green'].setValue('alpha')
	shuffleNode['alpha'].setValue('alpha')

	output = pm.getMatteOutput(
		currentTask,
		cOS.getVersion(translator.getFilename()),
		passName='alpha',
		ext='dpx'
	)
	matteRenderNode = nuke.nodes.Write(name='MatteRender', file=output, colorspace='sRGB')
	matteRenderNode.setInput(0,shuffleNode)

def getPrecompOutput(writeNode):
	passName = writeNode['passName'].getValue()
	passName = arkUtil.makeWebSafe(passName)
	if passName == '':
		writeNode['passName'].setValue('precomp')
		passName = 'precomp'

	fileType = writeNode['file_type'].value()

	versionNumber = cOS.getVersion(translator.getFilename())

	output = pm.getPrecompOutput(
		currentTask,
		passName,
		versionNumber,
		fileType
	)
	return output

def writePreCompRender(precompGizmo, writeNode):
	nuke.root()['proxy'].setValue(False)

	output = getPrecompOutput(writeNode)
	with precompGizmo:
		nuke.toNode('write')['file'].setValue(output)

	nuke.execute(precompGizmo.name(),
		int(nuke.root()['first_frame'].getValue()),
		int(nuke.root()['last_frame'].getValue()))

def readFromWritePrecomp(precompGizmo, writeNode):
	with nuke.root():
		readNode = nuke.createNode('Read')
		readNode['file'].setValue(writeNode['file'].getValue())
		readNode['first'].setValue(int(nuke.root()['first_frame'].getValue()))
		readNode['last'].setValue(int(nuke.root()['last_frame'].getValue()))
		if writeNode.knob('colorspace'):
			readNode['colorspace'].fromScript(writeNode['colorspace'].toScript())
		readNode['last'].setValue(int(nuke.root()['last_frame'].getValue()))
		readNode['xpos'].setValue(precompGizmo.xpos())
		readNode['ypos'].setValue(precompGizmo.ypos() + 200)

def writePreCompRenderRange(precompGizmo, writeNode):
	nuke.root()['proxy'].setValue(False)

	startFrame = int(nuke.root()['first_frame'].getValue())
	endFrame = int(nuke.root()['last_frame'].getValue())

	frameRange = nuke.getInput('Frame Range', '%s-%s' % (startFrame, endFrame))
	if frameRange:
		frames = arkUtil.parseFrameRange(frameRange)

	output = getPrecompOutput(writeNode)
	with precompGizmo:
		nuke.toNode('write')['file'].setValue(output)

	nuke.execute(precompGizmo.name(),
		frames[0],
		frames[-1])

def flipbook(writeNode):
	from nukescripts import flipbooking

	flipbooker = flipbooking.gFlipbookFactory.getApplication('Default')
	startFrame = nuke.root()['first_frame'].getValue() + 1
	endFrame = nuke.root()['last_frame'].getValue() - 1
	flipbooker.runFromNode(writeNode,
		nuke.FrameRanges('%d-%d' % (startFrame, endFrame)),
		'main',
		{})

def writeKeyedPlates():
	endNode = nuke.selectedNode()

	plateFile = cOS.normalizeAndJoin(
		pm.getPath(currentShot),
		'Assets',
		'plates_keyed',
		'shot_{}.%04d.png'.format(currentShot.get('name'))
	)

	renderNode = nuke.nodes.Write(name='KeyedPlates', colorspace='sRGB', channels='rgba')
	renderNode['file'].fromUserText(plateFile)
	renderNode.setInput(0,endNode)

def exportCamera():
	camNode = nuke.selectedNode()
	if camNode:
		if camNode.Class() == 'StereoControls':
			camName = camNode.input(0).name().replace('left','right')
			camNode = camNode.node('cam_rightEye')
		else:
			camName = camNode.name()
		if camNode.Class()[:6] == 'Camera':
			frameRange = translator.getAnimationRange()
			tempFile = open(globalSettings.TEMP + 'camera.txt','w')
			if tempFile:
				tempFile.write('%s\n' % camName)
				for f in range(frameRange['startFrame'],frameRange['endFrame']+1):
					camMatrix = camNode['world_matrix'].valueAt(f)
					fov = camNode['focal'].valueAt(f)
					hap = camNode['haperture'].valueAt(f)
					#dump out frame number and 0-12 of the camMatrix
					tempFile.write('%d ' % f + (" ".join(('%f' % camMatrix[n]) for n in range(12))) + ' %f %f\n' % (fov,hap))
				tempFile.close()
			else:
				nuke.message('Could not create a temp camera file')
		else:
			nuke.message('Selected node was not a camera or stereo controls')
	else:
		nuke.message('Please select the camera you wish to export')

def exportTracker():
	trackNode = nuke.selectedNode()
	if trackNode:
		trackName = trackNode.name()
		frameRange = translator.getAnimationRange()
		width = translator.getRenderProperty('width')
		height = translator.getRenderProperty('height')
		if trackNode.Class() == 'Tracker4':
			tempFile = open(globalSettings.TEMP + 'tracker.txt','w')
			if tempFile:
				tempFile.write('%s\n' % trackName)
				tempFile.write('%s %s\n' % (width, height))

				tracks = trackNode['tracks']
				trackSelection = trackNode['selected_tracks'].getText().split(',')
				if len(trackSelection) != 1 or trackSelection[0] == '':
					nuke.message('Please select the tracker you wish to export')
					return False
				else:
					trackSelection = int(trackSelection[0])
				nCols = 31
				xCol = 2
				yCol = 3
				for f in range(frameRange['startFrame'],frameRange['endFrame']+1):
					x = tracks.getValueAt(f, trackSelection*nCols+xCol)
					y = tracks.getValueAt(f, trackSelection*nCols+yCol)
					# dump out frame and float track data
					tempFile.write('%d %f %f\n' % (f, x, y))
				tempFile.close()
				nuke.message('Selected tracker exported successfully')
			else:
				nuke.message('Could not create a temp track file')
		elif trackNode.Class()[:7] == 'Tracker':
			if tempFile:
				tempFile.write('%s\n' % trackName)
				tempFile.write('%s %s\n' % (width, height))
				for f in range(frameRange['startFrame'],frameRange['endFrame']+1):
					trackData = trackNode['track1'].valueAt(f)
					# dump out frame and float track data
					tempFile.write('%d %f %f\n' % (f,trackData[0],trackData[1]))
				tempFile.close()
				nuke.message('Selected tracker exported successfully')
			else:
				nuke.message('Could not create a temp track file')
		else:
			nuke.message('Selected node was not a Tracker')
	else:
		nuke.message('Please select the Tracker you wish to export')


# Trackers
##################################################
def trackNextFrame():
	t = nuke.selectedNode()
	if t.Class() != 'Tracker3':
		return False
	for i in range(0,t.getNumKnobs()):
			if t.knob(i).label() == ' @#-1|> ':
					t.knob(i).execute()

def trackPreviousFrame():
	t = nuke.selectedNode()
	if t.Class() != 'Tracker3':
		return False
	for i in range(0,t.getNumKnobs()):
			if t.knob(i).label() == ' @#-1<| ':
					t.knob(i).execute()

def grabTrackerFrame():
	t = nuke.selectedNode()
	if t.Class() != 'Tracker3':
		return False
	for i in range(0,t.getNumKnobs()):
		if t.knob(i).label() == ' grab ':
			t.knob(i).execute()

# Toolsets
##################################################
def createNetworkToolset():
	if not nuke.env['gui']:
		return

	class NetworkToolsetDialog(baseWidget.BaseWidget):
		defaultOptions = {
			'name': 'Create Network Toolset',

			'knobs':[
				{
					'name': 'Toolset Folder',
					'dataType': 'List',
				},
				{
					'name': 'Toolset Name',
					'dataType': 'Text'
				},
				{
					'name': 'Create',
					'dataType': 'PythonButton',
					'callback': 'createNetworkToolset'
				}
			]
		}

		def postShow(self):
			self.allDirectories = ['root']
			self.allDirectories = collectDirectoryChoices(globalSettings.NETWORK_TOOLSETS, self.allDirectories)

			self.getKnob('Toolset Folder').addItems(self.allDirectories)
			self.getKnob('Toolset Folder').on('changed', self.selectToolsetFolder)

		def selectToolsetFolder(self, *args):
			folderName = self.getKnob('Toolset Folder').getValue()
			if folderName == 'root':
				self.getKnob('Toolset Name').setValue('')
			else:
				self.getKnob('Toolset Name').setValue(folderName + '/')

		def createNetworkToolset(self):
			# change file path
			def archiveFile(filepath, subDir):
				filepath = cOS.normalizePath(filepath)
				if globalSettings.RAIDCHARLES in filepath:
					return None

				pathRoot = pathManager.getRoot(filepath)
				toolsetRoot = globalSettings.NETWORK_TOOLSETS.replace('Toolsets', 'Toolset_assets')
				newRoot = toolsetRoot + subDir + '/'
				newFilepath = filepath.replace(pathRoot, newRoot)

				cOS.makeDirs(newFilepath)
				if '%' in newFilepath:
					cOS.copyFileSequence(filepath, newFilepath, echo=True)

				else:
					cOS.copy(filepath, newFilepath)

				return newFilepath

			if len(nuke.selectedNodes()) > 0:
				subDir = self.getKnob('Toolset Name').getValue()
				savePath = globalSettings.NETWORK_TOOLSETS + subDir + '.nk'
				saveDir = os.path.dirname(savePath)
				for node in nuke.selectedNodes():
					if node.Class() == 'Group':
						for n in node.nodes():
							if 'file' in n.knobs():
								filepath = n['file'].getValue()
								filepath = cOS.normalizeFramePadding(filepath)

								# change filepath
								if filepath:
									newFilepath = archiveFile(filepath, subDir)
									if newFilepath:
										n['file'].setValue(newFilepath)

					elif 'file' in node.knobs():
						filepath = node['file'].getValue()
						filepath = cOS.normalizeFramePadding(filepath)

						# change filepath
						if filepath:
							newFilepath = archiveFile(filepath, subDir)
							node['file'].setValue(newFilepath)

				if not os.path.isdir(saveDir):
					os.makedirs(saveDir)
				nuke.nodeCopy(savePath)
				print 'New Toolset saved to: ' + savePath
				refreshToolsets()
			else:
				nuke.message('Please select the node(s) you wish to use to create a Toolset.')

			self.close()


	NetworkToolsetDialog().show()

def addToolsetItems(searchDir, toolsetMenu):
	# adds network toolset and refresh Network toolset
	toolsetMenu.addCommand('Refresh Toolsets','arkNuke.refreshToolsets()')
	toolsetMenu.addCommand('Create Network Toolset','arkNuke.createNetworkToolset()')
	toolsetMenu.addSeparator()
	for treeInfo in os.walk(searchDir):
		(dirPath, dirNames, files) = treeInfo
		dirNames = sorted(dirNames)
		if dirPath:
			subDirs = dirPath.replace(searchDir,'').split(os.sep)[0:]

		activeMenu = toolsetMenu
		try:
			if subDirs and len(subDirs) > 0:
				for d in subDirs:
					dirMenu = activeMenu.menu(d)
					if dirMenu == None:
						activeMenu = activeMenu.addMenu(d)
					else:
						activeMenu = dirMenu
			files = sorted(files)
			if files:
				for f in files:
					activeMenu.addCommand(f[:-3], command='nuke.loadToolset("' + dirPath.replace('\\', '/') + '/' + f + '")')
		except AttributeError:
			pass

def refreshToolsets():
	'''Reload toolsets'''
	toolsetMenu = nuke.menu('Nodes').menu('Network Toolsets')

	toolsetMenu.clearMenu()
	addToolsetItems(globalSettings.NETWORK_TOOLSETS, toolsetMenu)

def collectDirectoryChoices(startingPath, allDirectories=[]):
	for i in os.walk(startingPath):
		directories = i[0].replace(startingPath,'').split(os.sep)[0:]
		joined = '/'.join(directories)
		if not (joined in allDirectories):
			allDirectories.append(joined)
	return allDirectories
