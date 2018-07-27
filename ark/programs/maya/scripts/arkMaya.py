import random

import arkInit
arkInit.init()

import maya.cmds as cmds
import maya.mel as mel

# fix: dropdown: doesn't work

def getShadingGroupFromShader(shader):
	if not cmds.objExists(shader):
		raise Exception('Shader does not exist: ' + shader)

	sgq = cmds.listConnections(shader, d=True, et=True, t='shadingEngine')
	if sgq:
		return sgq[0]

def assignRandomShaders():
	# get the current selection
	selection = cmds.ls(sl=True)
	selCount = len(selection)
	if selCount < 1:
		return False

	# get all the object nodes from the selection
	# list all the child nodes under the selection (walk the hierarchy)
	children = cmds.listRelatives(selection,
								allDescendents=False,
								noIntermediate=True,
								fullPath=True)
	# filter children into mesh/shape array
	nodes = cmds.ls(children, type=['mesh', 'shape'])
	nodeCount = len(nodes)

	print nodeCount

	# Get only the shaders from the current selection
	shaders = cmds.ls(selection, materials=True)
	shaderCount = len(shaders)

	# Apply random material to each node in the selection
	if shaderCount < 1 or nodeCount < 1:
		return False

	for n in nodes:
		# get a random shader
		index = random.randint(0, shaderCount-1)
		shader = shaders[index]

		# get the sahders shading engine node
		shaderSG = getShadingGroupFromShader(shader)

		# apply shader to node
		if shaderSG:
			cmds.sets(n, e=True, forceElement=shaderSG)
			print n, shaderSG
		else:
			print 'The provided shader didn\'t returned a shaderSG'

def addCameraFocusControl():
	#get the current selection
	selection = cmds.ls(sl=True)

	# Always use fullPath=True to avoid short name conflict errors
	nodes = cmds.listRelatives(selection, allDescendents=True,noIntermediate=True,fullPath=True) #list all the child nodes under the selection (walk the hierarchy)

	# Get a filtered list from the children
	cameras = cmds.ls(nodes, type="camera") #filter children into a curves array

	for cam in cameras:

		mel.eval('vray addAttributesFromGroup "' + cam + '" "vray_cameraPhysical" 1')
		cmds.setAttr(cam + '.vrayCameraPhysicalOn', True)

		# collect camera's transform
		camTM = cmds.listRelatives(cam, parent=True, fullPath=True)[0]

		# Collect the parent for each camera
		# The listRelatives command is used to get a list of nodes in a dag
		# hierarchy.  You can get child nodes, parent nodes, shape nodes, or all
		# nodes in a hierarchy.  Here we are getting the child nodes.
		parent = cmds.listRelatives(camTM, parent=True, type='transform')

		# create a locator to be used as the focus control
		focusCtrl = cmds.spaceLocator()[0]

		# enabled the cameras depth of field
		cmds.setAttr(cam + ".depthOfField", 1)
		#cmds.setAttr(cam + ".mxUseFocusDistance", 1) # MAXWELL SETTINGS

		# create distanceBetween utility
		distUtility = cmds.shadingNode( 'distanceBetween', asUtility=True)

		# Connect the distance utility node to override the focus property of the camera and vray camera
		cmds.connectAttr((distUtility + '.distance'), (cam + '.focusDistance'), f=True)
		cmds.setAttr(cam + '.vrayCameraPhysicalSpecifyFocus', True)
		cmds.connectAttr((distUtility + '.distance'), (cam + '.vrayCameraPhysicalFocusDistance'), f=True)

		#cmds.connectAttr( (distUtility + '.distance'), (cam + '.mxFocusDistance'), f=True ) # MAXWELL SETTINGS

		# set the the camera's Translation as argument 'one' of the distUtility
		cmds.connectAttr( (camTM + '.translate'), (distUtility + '.point1') , f=True)

		# set the the focusCtrl's Translation as argument 'two' of the distUtility
		cmds.connectAttr( (focusCtrl + '.translate'), (distUtility + '.point2') , f=True)

		# parent the focusCtrl to the same parent of the camera
		if parent != None:
			cmds.parent( focusCtrl, parent )

		# lastly rename the focusCtrl
		cmds.rename( focusCtrl, 'FocusCTRL_00' )
