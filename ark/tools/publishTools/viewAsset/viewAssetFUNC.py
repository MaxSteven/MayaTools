'''
Author: Carlo Cherisier
Date: 09.26.14
Script: viewAssetFUNC
'''
import arkInit
arkInit.init()

import translators
translator = translators.getCurrent()

import sys, os
sys.path.append( 'c:/ie/ark/tools/dataDecoder')
import dataDecoder

sys.path.append( 'c:/ie/ark/tools/animationLibrary')
import animationLibraryFUNC as ALF

class guiFunc(object):
	'''
	Functions for GUI
	'''
	def __init__( self):
		## Class Variables
		self.namespace_List = []
		self.deptName_List = []
		self.assetVersion_List = []
		self.assetType_List = []
		self.import_Dict = {}
		self.layerDict= {}
	#
	def getGuiInformation( self):
		'''
		Purpose:
			To check if the GUI was opened in the scene already
			if so look at the variables stored within the scene
			if not use data stored within data file
		'''
		## Check if GUI has been opened
		result = translator.executeNativeCommand( 'print viewAssets')

		if result == 'undefined':
			## Run Maxscript
			translator.executeNativeCommand( 'viewAssets = 1')

			result = self.useDataFile()
			if result == False:
				result = self.useSceneData()

		else:
			result = self.useSceneData()

		if result != False:
			self.prepareSceneInformation()

		else:
			return False
	#
	def useDataFile( self):
		'''
		Save namespaces into the scene
		'''
		projName = translator.getData( 'smart_projName')
		deptName = translator.getData( 'smart_deptName')
		assetName = translator.getData( 'smart_assetName')

		if projName != '' or deptName != '' or assetName != '':
			## Grab information
			self.import_Dict= dataDecoder.get_sceneAssetData( projName, deptName, assetName)

		else:
			return False
	#
	def useSceneData( self):
		'''
		Check Scene for newly import Assets
		'''
		## Grab namespace list
		sceneData = translator.getData( 'namespace_List')

		if sceneData == '':
			return False

		## Turn string into list
		namespace_List = [x for x in sceneData.split(',')]

		for each in namespace_List:
			if translator.namespaceExists( each):
				## Grab namespace list
				assetInfo = translator.getData( each)

				self.import_Dict[ each] = assetInfo
	#
	def prepareSceneInformation( self):
		'''
		Prepare infomation for View Asset GUI
		'''
		if 'publish' in self.import_Dict.keys():
			del self.import_Dict[ 'publish']

		for key in sorted( self.import_Dict.keys()):
			## Construct namespace list
			self.namespace_List.append( key)

			## Construct dept list
			self.deptName_List.append( self.import_Dict[key].split('**')[1])

			## Construct Asset Version list
			self.assetVersion_List.append( self.import_Dict[key].split('**')[4])

			## Construct Asset Type list
			self.assetType_List.append( self.import_Dict[key].split('**')[3])
	#
	def setLayerDict( self, key, projName, deptName, assetName):
		## Set path to data file
		dataFile= 'r:/{0}/Data/{1}/{2}.data'.format( projName, deptName, assetName)
		# print dataFile, 1

		## Save namespaces
		self.layerDict[ key]= ( dataDecoder.get_publishAssets( dataFile, 'layerList'))
	#
	def selectAssets( self, namespace):
		'''
		Select Asset in scene
		'''
		translator.searchSceneForObjects( namespace, findAndSelect= True)
	#
	def selectMultipleAssets( self, namespace_List):
		'''
		Select Multiple Assets in scene
		'''
		## Function Variables
		selectedList = []

		## Clear Selection
		translator.clearSelection()

		for each in namespace_List:
			## Select namespace asset
			translator.searchSceneForObjects( each, findAndSelect= True)

			## Grab object names
			selectedList.extend( translator.getSelectedObjectName())

		## Clear Selection
		translator.clearSelection()

		## Select all objects
		translator.selectObject( *selectedList, add= True)
	#
	def checkAssetForUpdates( self, selected_List):
		'''
		Check if selected Assets have updates in scene
		'''
		## Function Variables
		asset_Dict = {}
		sceneData_Dict = {}
		holder = {}
		declinedAssets = []

		for namespace in selected_List:
			## Grab information from  asset dictionary
			projName = self.import_Dict[ namespace].split('**')[0]
			deptName = self.import_Dict[ namespace].split('**')[1]
			assetName = self.import_Dict[ namespace].split('**')[2]
			assetType = self.import_Dict[ namespace].split('**')[3]
			version = self.import_Dict[ namespace].split('**')[4]
			versionNum = version

			## Construct Path
			assetPublishFolder = 'r:/{0}/Project_Assets/{1}/Published/{2}'.format( projName, assetName, deptName)

			## Grab folder list
			folder_List = os.listdir( assetPublishFolder)

			## Find newest folder
			for folder in folder_List:
				if versionNum < folder:
					versionNum = folder

			if versionNum <= version:
				continue

			## Construct Path
			path = assetPublishFolder+ '/'+ versionNum
			fileList = os.listdir( path)

			if any( assetType in each for each in fileList):
				newFile= [ each for each in fileList if assetType in each][0]
				## Construct Path
				asset_filePath = path+ '/'+ newFile

				if os.path.exists( asset_filePath):
					## Add path to list
					asset_Dict[ namespace] = asset_filePath

					## Store Asset Data
					sceneData_Dict[ namespace] = '{0}**{1}**{2}**{3}**{4}'.format( projName, deptName, assetName, assetType, versionNum )

					## Store Change
					holder[ namespace] = versionNum

					## Set Layer Dictionary
					self.setLayerDict( namespace, projName, deptName, assetName)
			else:
				## Inform User
				message = '{0}:{1} does not exist for version {2}'.format( assetName, assetType, versionNum)
				declinedAssets.append( message)

		if asset_Dict != {}:
			## Update Asset
			self.update_Asset( asset_Dict, sceneData_Dict)

		return holder, declinedAssets
	#
	def deleteAssets( self, namespace_List):
		'''
		Delete Asset(s) in scene
		'''
		## Clear Selection
		translator.clearSelection()

		for namespace in namespace_List:
			if translator.getProgram() == 'Max':
				## Select namespace asset
				translator.searchSceneForObjects( namespace, findAndSelect= True)

				## Delete selected Assets
				translator.deleteObject( useSelected= True)

			if translator.getProgram() == 'Maya':
				## Grab reference nodes in scene
				referenceNodes = translator.getReferenceNodes()

				for ref in referenceNodes:
					if namespace in ref:
						## Remove reference file from scene
						translator.removeReference( refNode= ref)
	#
	def changeAssetType( self, namespace_List, newAssetType):
		'''
		Change selected Asset Type
		'''
		## Function Variables
		assetPublishPath = {}
		sceneData_Dict = {}
		holder = {}
		declinedAssets = {}

		for each in namespace_List:
			## Grab information from  asset dictionary
			projName = self.import_Dict[ each].split('**')[0]
			deptName = self.import_Dict[ each].split('**')[1]
			assetName = self.import_Dict[ each].split('**')[2]
			# assetType = self.import_Dict[ each].split('**')[3]
			version = self.import_Dict[ each].split('**')[4]

			## Construct Path
			assetPublishFolder = 'r:/{0}/Project_Assets/{1}/Published/{2}/{3}'.format( projName, assetName, deptName, version)

			## Grab files from folder
			file_List = os.listdir( assetPublishFolder)

			## Check file list to see if new asset type exists
			result= [ x for x in file_List if newAssetType in x]

			if result !=[]:
				fileName = result[0]
				## Construct Path
				asset_filePath =  assetPublishFolder+ '/'+ fileName

				if os.path.exists( asset_filePath):
					## Add path to list
					assetPublishPath[ each] = asset_filePath

					## Store Asset Data
					sceneData_Dict[ each] = '{0}**{1}**{2}**{3}**{4}'.format( projName, deptName, assetName, newAssetType, version )

					## Store Change
					holder[ each] = newAssetType

					## Set Layer Dictionary
					self.setLayerDict( each, projName, deptName, assetName)

			else:
				if assetName not in declinedAssets.keys():
					message = '{0}:{1} does not exist for version {2}'.format( assetName, newAssetType, version)
					declinedAssets[ assetName] = message


		if assetPublishPath != {}:
			## Update Asset
			self.update_Asset( assetPublishPath, sceneData_Dict)

		return holder, declinedAssets
	#
	def update_Asset( self, assetPublishPath, sceneData_Dict):
		'''
		Purpose
			Update selected asset with it's new published version
		'''
		## Load Animation Manager
		animLibrary= ALF.guiFUNC()

		for namespace in assetPublishPath.keys():
			if translator.getProgram() == 'Maya':
				## Grab reference nodes in scene
				referenceNodes = translator.getReferenceNodes()

				for each in referenceNodes:
					if namespace in each:
						## Change file to new published file
						translator.setReferenceNodeFile( refNode= each, filePath= assetPublishPath[namespace])

			if translator.getProgram() == 'Max':
				## Set Save Animation Folder Path
				animLibrary.animFolder= os.path.split( assetPublishPath[namespace])[0]

				## Select Rig Controllers
				animLibrary.selectAnimationCtrls( namespace)

				## Save animation
				animFile = animLibrary.saveAnimation( namespace, 'Update')

				## Grab asset type
				assetType= self.import_Dict[ namespace].split('**')[3]

				if assetType != 'Rig':
					## Select namespace asset
					translator.searchSceneForObjects( namespace, findAndSelect= True)

					## Delete selected Assets
					translator.deleteObject( useSelected= True)

					## Import Asset with namespace
					translator.importFile( filePath= assetPublishPath[namespace], namespace= namespace, smartTool=1)

					## Layer Fixes
					if len(self.layerDict.keys()) != 0:
						for layerName in self.layerDict[ namespace]:
							## Delete Layer
							translator.deleteLayerByName( namespace)

							## Change LayerName
							translator.changeLayerName( oldName= layerName, newName= namespace+'__'+ layerName, replace= True)

				if assetType == 'Rig':
					## Select namespace asset
					translator.searchSceneForObjects( namespace, findAndSelect= True)

					## Delete selected Assets
					translator.deleteObject( useSelected= True)

					## Import Asset with namespace
					translator.importFile( filePath= assetPublishPath[namespace], namespace= namespace, smartTool=1)

				## Load Animation
				animLibrary.loadAnimation( namespace= namespace, animationName= 'Update', filePath= animFile, modular=True)

				## Delete Animation File
				animLibrary.deleteAnimationFile( animFile, modular=True)

			## Clear selection
			translator.clearSelection()

			## Store information
			translator.setData( namespace, sceneData_Dict[namespace])
	#
	def updateInstances( self, namespace):
		'''
		This will update all instances of object with instances
		'''
		func='''
		selected_List= getCurrentSelection()
		'''
		translator.executeNativeCommand( func)
	#
