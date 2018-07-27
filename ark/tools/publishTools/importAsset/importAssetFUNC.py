'''
Author: Carlo Cherisier
Date: 09.10.14
Script: importAssetFUNC
'''
import sys, os
sys.path.append( 'c:/ie/ark/tools/dataDecoder')
import dataDecoder

import translators
translator = translators.getCurrent()


class guiFunc(object):
	'''
	Functions for GUI
	'''
	def __init__( self):
		## Class Variables
		self.hiRez= []
		self.lowRez= False
		self.assetName= 'Test'
		self.asset_folderPath= 'Test'
		self.asset_departmentPath=''
		self.publish_folderPath= ''
		self.publishVersion=''

		self.import_assetName=''
		self.import_deptName=''
		self.import_assetType=''
		self.import_version=''
		self.poxyMode=''

		self.holder_Dict={}
	#
	def populate_publishedAssets( self, widgetName, projName, deptName):
		'''
		Grab All Published Assets
		'''
		## Construct filePath
		data_folderPath= 'r:/{0}/Data/{1}'.format( projName, deptName)

		## Check if file exist
		check= os.path.exists( data_folderPath)

		if check == False:
			return

		## Grab Asset List
		asset_List= os.listdir( data_folderPath)

		## Remove . from items
		asset_List = [ each.split('.')[0].capitalize() for each in asset_List]

		## Add assets to widget
		widgetName.addItems( sorted( asset_List))
	#
	def assetTypeExists( self, projName, deptName, assetName, assetType):
		'''
		Purpose:
			Check if Asset Type exists
		'''
		dataPath= 'r:/{0}/Data/{1}/{2}.data'.format( projName, deptName, assetName)

		result01 = dataDecoder.get_publishAssets( dataPath, assetType)
		result02 = dataDecoder.get_publishAssets( dataPath, 'program')

		if result01 != None:
			if assetType in ['hiRez', 'lowRez', 'bBox']:
				if result02 == translator.getProgram():
					return 1, None
				else:
					return 3, '{0} {1} has not yet been published for {2}.'.format( assetType, assetName, translator.getProgram())
			else:
				return 1, None
		else:
			return 2,'{0} has not yet been published for {1}.'.format( assetType, assetName)
	#
	def getAssetPath( self, key):
		'''
		Grab import asset path
		'''
		## Grab information from item
		projName, deptName, self.import_assetName, assetType= key.split( '**')
		# print projName, deptName, self.import_assetName, assetType, 0

		## Data To Save
		self.import_projName= projName
		self.import_deptName= deptName
		self.import_assetType= assetType

		## Set path to data file
		dataFile= 'r:/{0}/Data/{1}/{2}.data'.format( projName, deptName, self.import_assetName)
		# print dataFile, 1

		## Grab Asset Path
		self.asset_importPath= dataDecoder.get_publishAssets( dataFile, assetType)
		# print self.asset_importPath, 2

		if assetType == 'lowRez' and self.asset_importPath== None:
			## Set asset type to bBox
			self.import_assetType= 'bBox'

			## Grab Asset Path
			self.asset_importPath = dataDecoder.get_publishAssets( dataFile, 'bBox')

		## Save namespaces
		self.import_version = dataDecoder.get_publishAssets( dataFile, 'version')

		## Save namespaces
		self.layerList = dataDecoder.get_publishAssets( dataFile, 'layerList')
	#
	def set_namespace( self):
		'''
		Set Asset Name
		'''
		## Set namespace count
		count= 1

		## Return namespace
		self.namespace= self.checkNamespace( count)

		self.holder_Dict[ self.namespace]= '{0}**{1}**{2}**{3}**{4}'.format( self.import_projName, self.import_deptName, self.import_assetName, self.import_assetType, self.import_version )
	#
	def checkNamespace( self, count=0):
		'''
		Check if namespace is already in use
		if not use namespace
		if so increase number
		'''
		## Check if namespace exist
		name= '{0}{1:03}'.format( self.import_assetName, count)
		result= translator.namespaceExists( name)

		if result:
			count+=1
			namespace= self.checkNamespace( count)
			return namespace
		else:
			## Set Namespace
			namespace= '{0}{1:03}'.format( self.import_assetName, count)
			return namespace
	#
	def importAsset( self):
		'''
		Import asset into scene
		'''
		if translator.getProgram() == 'Max':
			## Import Latest Published File
			translator.importFile( self.asset_importPath, self.namespace, smartTool=1)

			if len(self.layerList) != 0:
				for each in self.layerList:
					## Change LayerName
					translator.changeLayerName( oldName= each, newName= self.namespace+'__'+ each, replace= True)

		if translator.getProgram() == 'Maya':
			translator.referenceFile( self.asset_importPath, self.namespace)

		## Key Asset
		self.keyAsset()

		## Clear Selection
		translator.clearSelection()
	#
	def importVrayProxy( self):
		'''
		Purpose:
			Import vRay Proxy
		'''
		translator.assetManager.importvRayProxy( self.asset_importPath, self.namespace, self.import_assetName)
	#
	def keyAsset( self):
		'''
		Purpose:
			Sets a key on assetRoot or on Rig Controls
		'''
		result = translator.objectExists( self.namespace+'__Scene')

		if result == True:
			## Select Rig Ctrls
			result = translator.searchSceneForObjects( self.namespace, findAndSelect= True, searchFilter='_CTRL_')

			## Set Key on Select Objects
			translator.keySelectedObjects()

		else:
			if translator.fileExtension == 'max':
				translator.selectObject( self.namespace + '__assetRoot')

			else:
				translator.selectObject( self.namespace + ':assetRoot')
			## Set Key on Select Objects
			translator.keySelectedObjects()
	#
	def finalize_importAsset( self):
		'''
		Save namespaces into the scene
		'''
		for each in self.holder_Dict.keys():
			## Store all namespaces in the scene
			self.store_sceneData( key='namespace_List', value= each)

		for each in self.holder_Dict.keys():
			## Store all Asset Data
			self.store_sceneData( each, self.holder_Dict[each], onlyUnique=True)
	#
	def store_sceneData( self, key=None, value= None, duplicates=False, onlyUnique= False):
		'''
		Save namespaces into the scene
		'''
		## Grab namespace list
		sceneData = translator.getData( key)

		## Create List to hold data
		data_List=[]

		if sceneData== '' or onlyUnique== True:
			## Add asset path to list
			data_List.append( value)
		else:
			## Turn string into list
			data_List= [x for x in sceneData.split(',')]

			if duplicates== False:
				## Prevent any duplicates
				if value not in data_List:
					data_List.append( value)

			else:
				## Add namespace to list
				data_List.append( value)

		## Make data into string
		sceneData= ','.join( data_List)

		## Store information
		translator.setData( key, sceneData)
