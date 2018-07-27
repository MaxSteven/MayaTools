'''
Author: Carlo Cherisier
Date: 09.26.14
Script: animationLibraryFUNC
'''
import sys, os
sys.path.append( 'c:/ie/ark/tools/dataDecoder')
import dataDecoder

import translators
translator = translators.getCurrent()

class guiFUNC(object):
	'''
	Functions for GUI
	'''
	## Class Variables
	projName=''
	deptName=''
	assetName=''
	namespace_List= []
	publishFolder=''
	publishDict={}
	animFolder=''

	def __init__( self):
		self.projName= translator.getData( 'smart_projName')
		self.deptName= translator.getData( 'smart_deptName')
		self.assetName= translator.getData( 'smart_assetName')
	#
	def grabTime( self):
		'''
		Purpose:
			Grab start and end frame
		'''
		startTime, endTime= translator.animationManager.getTime()

		return( startTime, endTime)
	#
	def getGuiInformation( self):
		'''
		Purpose:
			To check if the GUI was opened in the scene already
			if so look at the variables stored within the scene
			if not use data stored within data file
		'''
		## Check if GUI has been opened
		result= translator.executeNativeCommand( 'print publishAnimationGUI')

		if result== 'undefined':
			func='''
			publishAnimationGUI= 1
			'''
			## Run Script
			translator.executeNativeCommand( func)
			self.useDataFile()

		else:
			self.useSceneData()
	#
	def useDataFile( self):
		'''
		Save namespaces into the scene
		'''
		if self.projName!= '' or self.deptName!= '' or self.assetName!= '':
			## Grab information
			result= dataDecoder.get_sceneAssetData( self.projName, self.deptName, self.assetName)

			if result!= None:
				self.namespace_List= result.keys()

				## Grab namespace list
				sceneData= translator.getData( 'namespace_List')

				## Turn into string
				tempList= [x for x in sceneData.split(',')]

				## Add any namespace for newly added assets
				for each in tempList:
					if each not in self.namespace_List:
						self.namespace_List.append( each)
	#
	def useSceneData( self):
		'''
		Check Scene for newly import Assets
		'''
		print 'Using a sceneData'
		## Grab namespace list
		sceneData= translator.getData( 'namespace_List')

		if sceneData!= '':
			## Turn string into list
			self.namespace_List= [x for x in sceneData.split(',')]
	#
	def createAnimationFolder( self, namespace):
		'''
		Purpose:
			Create Folder to store Animation Curves
		'''
		self.animFolder = 'r:/{0}/Data/Animation_Library/{1}'.format( self.projName, namespace)

		if not os.path.exists( self.animFolder):
			## Make Folder
			os.makedirs( self.animFolder)
	#
	def searchAnimationLibrary( self, namespace):
		'''
		Purpose:
			Check for saved animation files
		'''
		animLibraryPath= 'r:/{0}/Data/Animation_Library/{1}'.format( self.projName, namespace[:-3])

		if not os.path.exists(animLibraryPath):
			return False

		## Grab files
		fileList = os.listdir( animLibraryPath)

		return fileList
	#
	def selectAnimationCtrls( self, namespace):
		'''
		Select Asset in scene
		'''
		## Check if Asset is a Rig
		if translator.getProgram() == 'Max':
			name = '{0}__Scene'.format( namespace)

		if translator.getProgram() == 'Maya':
			name = '{0}:Scene'.format( namespace)

		result = translator.objectExists( name)

		if result == True:
			## Select Rig Ctrls
			result= translator.searchSceneForObjects( namespace, findAndSelect= True, searchFilter='_CTRL_')
			return result

		## Check if Asset is a Model
		if translator.getProgram() == 'Max':
			name = '{0}__assetRoot'.format( namespace)

		if translator.getProgram() == 'Maya':
			name = '{0}:assetRoot'.format( namespace)

		result = translator.objectExists( name)

		if result == True:
			## Select Ctrl
			translator.selectObject( name)
			return result
	#
	def saveAnimation( self, namespace, animationName):
		'''
		Purpose:
			Save animation on Ctrls
		'''
		if translator.getProgram() == 'Max':
			## Remove namespace from selected objects
			translator.animationManager.replaceSelectObjectsName( namespace, 'ns')

			animFile = '{0}/{1}.xaf'.format( self.animFolder, animationName)

			## Save Animation
			translator.animationManager.saveAssetAnimation( animFile)

			## Return namespace back to objects
			translator.animationManager.replaceSelectObjectsName( 'ns', namespace)

		if translator.getProgram() == 'Maya':
			animFile = '{0}/{1}.atom'.format( self.animFolder, animationName)

			## Save Animation
			translator.animationManager.saveAssetAnimation( animFile)

		## Clear Selection
		translator.clearSelection()

		return animFile
	#
	def loadAnimation( self, namespace, animationName=None, filePath= None, modular= False):
		'''
		Purpose:
			Load animation onto selected Asset
		'''
		if modular == False:
			## Construct animation file path
			animFile= 'r:/{0}/Data/Animation_Library/{1}/{2}'.format( self.projName, namespace[:-3], animationName)

		else:
			animFile = filePath

		if not os.path.exists( animFile):
			return

		if translator.getProgram() == 'Max':
			## Remove namespace from selected objects to avoid namespace issues
			translator.animationManager.replaceSelectObjectsName( namespace, 'ns')

			## Load Animation onto controls from file
			translator.animationManager.loadAssetAnimation( animFile)

			## Return namespace back to objects
			translator.animationManager.replaceSelectObjectsName( 'ns', namespace)

		if translator.getProgram() == 'Maya':
			## Load Animation onto controls from file
			translator.animationManager.loadAssetAnimation( animFile, namespace)

		## Clear Selection
		translator.clearSelection()
	#
	def deleteAnimationFile( self, fileName, modular=False):
		'''
		Purpose:
			Delete Saved Animation File
		'''
		if modular == False:
			animFile= '{0}/{1}.xaf'.format( self.animFolder, fileName)
		else:
			animFile = fileName

		## Delete Anim File
		os.remove( animFile)