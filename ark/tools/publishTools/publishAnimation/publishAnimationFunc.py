'''
Author: Carlo Cherisier
Date: 09.10.14
Script: publishAnimationFunc
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

	def __init__( self):
		self.projName= translator.getData( 'smart_projName')
		self.deptName= translator.getData( 'smart_deptName')
		self.assetName= translator.getData( 'smart_assetName')
	#
	def get_guiInformation( self):
		'''
		Purpose:
			To check if the GUI was opened in the scene already
			if so look at the variables stored within the scene
			if not use data stored within data file
		'''
		func='print publishAnimationGUI'
		## Run Maxscript
		result= translator.executeNativeCommand( func)

		if result== 'undefined':
			func='''
			publishAnimationGUI= 1
			'''
			## Run Maxscript
			translator.executeNativeCommand( func)

			self.use_dataFile()

		else:
			self.use_sceneData()
	#
	def use_dataFile( self):
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

				tempList= [x for x in sceneData.split(',')]

				## Add any namespace for newly added assets
				for each in tempList:
					if each not in self.namespace_List:
						self.namespace_List.append( each)
	#
	def use_sceneData( self):
		'''
		Check Scene for newly import Assets
		'''
		## Grab namespace list
		sceneData= translator.getData( 'namespace_List')

		if sceneData!= '':
			## Turn string into list
			self.namespace_List= [x for x in sceneData.split(',')]
	#
	def create_publishFolder( self):
		'''
		Purpose:
			Create Folder to store Publish Animation Curves
		'''
		animFolder= 'r:/{0}/Workspaces/{1}/Published/savedAnimCurves'.format( self.projName, self.assetName)

		if not os.path.exists( animFolder):
			## Set publish version
			self.publishVersion= 'v001'

			## Construct folder path
			self.publishFolder='{0}/v001'.format( animFolder)

			## Make Folder
			os.makedirs( self.publishFolder)

		else:
			## Grab files
			folderList= os.listdir( animFolder)

			if len(folderList)== 0:
				## Set publish version
				self.publishVersion= 'v001'

				## Construct folder path
				self.publishFolder='{0}/v001'.format( animFolder)

				## Make Folder
				os.makedirs( self.publishFolder)

			holder= 1
			for each in folderList:
				if 'v0' in each or 'v1' in each or 'v2' in each:
					## Grab version number
					version= int( each.split( 'v')[-1])
					if version>= holder:
						holder= version+1

			## Set publish version
			self.publishVersion= 'v{0:03}'.format( holder)

			## Construct folder path
			self.publishFolder='{0}/{1}'.format( animFolder, self.publishVersion)

			if not os.path.exists( self.publishFolder):
				## Make Folder
				os.makedirs( self.publishFolder)
	#
	def prepAssets( self, namespace):
		'''
		Select Asset in scene
		'''
		## Check if Asset is a Rig
		name= '${0}__Scene'.format( namespace)
		check= translator.objectExists( name)

		if check:
			## Select Rig Ctrls
			result = translator.searchSceneForObjects( namespace, findAndSelect= True, searchFilter='_CTRL_')

			if result:
				## Publish Rig
				self.saveAnimation( namespace)
				return result

		## Check if Asset is a Model
		name= '${0}__assetRoot'.format( namespace)
		check= translator.objectExists( name)

		if check:
			## Select Model Geo
			result= translator.searchSceneForObjects( namespace, findAndSelect= True)

			if result:
				## Publish Rig
				self.saveAnimation( namespace)
			return result
	#
	def saveAnimation( self, namespace):
		'''
		Purpose:
			Save animation on Rig Ctrls
		'''
		animFile= '{0}/{1}__animation.xaf'.format( self.publishFolder, namespace[:-2])

		## Save object animation
		translator.animationManager.saveAssetAnimation( animFile)

		if 'namespaceList' in self.publishDict.keys():
			value= self.publishDict[ 'namespaceList']

			self.publishDict[ 'namespaceList']= namespace+ '**'+value
		else:
			self.publishDict[ 'namespaceList']= namespace

		if 'animPathList' in self.publishDict.keys():
			value= self.publishDict[ 'animPathList']

			self.publishDict[ 'animPathList']= animFile+ '**'+value
		else:
			self.publishDict[ 'animPathList']= animFile
	#
	def saveAlembic( self, namespace, iterationValue=None):
		'''
		Purpose:
			Save out animated geo
		'''
		## Select objects with namespace
		translator.searchSceneForObjects( objectName= namespace, findAndSelect= True)

		## Grab selected objects
		selectedObjects= translator.getSelectedObjectName()

		for each in selectedObjects:
			## Grab object properties
			properties= translator.assetManager.getAssetProperties( each)

			## Change subdivision (Maxs Turbosmooth.iterations) to renderSubdivision (Max's Turbosmooth.renderIterations)
			value= properties[ 'renderSubdivision']
			properties[ 'subdivision']= value

			## Set object properties
			translator.assetManager.setAssetProperties( each, properties)

		## Select Geo objects from rig
		for each in selectedObjects:
			## Check object type
			result= translator.getObjectType( objectName= each)

			if 'GeometryClass' in result or 'Polygon' in result:
				geoObjects= each

		## Clear Selection
		translator.clearSelection()

		## Select objects
		for each in geoObjects:
			translator.selectObject( each, add= True)

		## Make file path
		alembicFolder= 'r:/{0}/Workspaces/{1}/Published/Alembic/{2}'.format( self.projName, self.assetName, self.publishVersion)

		if not os.path.exists( alembicFolder):
			os.makedirs( alembicFolder)

		## Grab start and end frames
		startTime, endTime= translator.animationManager.getTime()

		alembicFile= '{0}/{1}_alembic.abc'.format( alembicFolder, namespace)

		## Export Alembic File
		translator.exportAlembic( alembicFile, startTime, endTime)

		if 'alembicPathList' in self.publishDict.keys():
			value= self.publishDict[ 'alembicPathList']

			self.publishDict[ 'alembicPathList']= alembicFile+ '**'+value
		else:
			self.publishDict[ 'alembicPathList']= alembicFile
	#
	def store_publishData( self):
		## Construct filePath
		dataPath= 'r:/{0}/Data/{1}/{2}_AnimCurves.data'.format( self.projName, self.deptName, self.assetName)

		if self.publishDict!={}:
			## Save Animation Path
			dataDecoder.storeParserData( dataPath, self.publishVersion, self.publishDict)
