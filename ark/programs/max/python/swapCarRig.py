'''
Author: Carlo Cherisier
Date: 09.26.14
Script: swapCarRig

python.execute("
import sys;
sys.path.append('c:/ie/ark/programs/max/python');
import swapCarRig; reload( swapCarRig); swapCarRig.saveAnimation();
")
'''
import os
import re

import arkInit
arkInit.init()

import translators
translator = translators.getCurrent()

import cOS

def saveAnimation():
	'''
	Purpose:
		Save animation on Car rig
		Delte car rig out of scene
		Import new car rig
		and load animation back on
	'''
	rigList=[]

	## Select all objects with name...
	translator.searchSceneForObjects( 'CTRL_', findAndSelect= True)

	## Grab selected nodes
	rigList.extend( translator.getSelectedObjectName())

	## Select all objects with name...
	translator.searchSceneForObjects( 'CON_', findAndSelect= True)

	## Grab selected nodes
	rigList.extend( translator.getSelectedObjectName())

	## Select all objects with name...
	translator.searchSceneForObjects( 'Link_', findAndSelect= True)

	## Grab selected nodes
	rigList.extend( translator.getSelectedObjectName())

	if rigList == []:
		return

	for each in rigList:
		translator.selectObject( each, add= True)

	if not os.path.exists( 'c:/testAnimation'):
		## Make Folder
		os.makedirs( 'c:/testAnimation')

	shotName= translator.getFilename()

	shotNumber = shotName.split( '\\')[-1].split( '_')[-3]

	animFile= 'c:/testAnimation/Car_Animation_{}.xaf'.format( shotNumber)

	## Save Animation
	translator.animationManager.saveAssetAnimation( animFile)


def loadAnimation():
	## Class Varaiable
	controllerList=[]

	## Construct path to car
	root = 'R:/Final_Girls/Project_Assets/nissan_altima/Rig/'
	latestVersion = 0
	latestFile = ''
	for f in os.listdir(root):
		version = cOS.getVersion(f)
		if version > latestVersion:
			latestFile = f
			latestVersion = version

	carPath= root + latestFile

	## Import Car
	func='''
	mergeMAXFile "{0}"
	'''.format( carPath)
	translator.executeNativeCommand ( func)

	# translator.importFile( carPath, smartTool=1)

	shotName= translator.getFilename()
	shotNumber = shotName.split( '\\')[-1].split( '_')[-3]

	animFile= 'c:/testAnimation/Car_Animation_{}.xaf'.format( shotNumber)
	print animFile

	# return
	## Clear Selection
	translator.clearSelection()

	## Read through file and grab CTRLs in file
	with open( animFile, 'r') as dataFile:
		for count, line in enumerate( dataFile):
			result = re.findall( r'(?!<Node name="|<Controller name=")(?=CON_|CTRL_|Link_)(\w+)(?="|[ ]\\)', line )
			if result:
				if result[0] not in controllerList:
					print result[0]
					controllerList.append( result[0])

	# print controllerList
	## Select controllers from rig
	for each in controllerList:
		translator.selectObject( each, add= True)

	## Load Animation onto controls from file
	## Load animation onto selected asset
	func = '''
	print selectObjects
	userAttr = #()
	userVal = #()

	LoadSaveAnimation.loadAnimation "{0}" (getCurrentSelection()) relative:false insert:false
	'''.format( animFile)
	translator.executeNativeCommand( func)


	## Delete file
	os.remove( animFile)