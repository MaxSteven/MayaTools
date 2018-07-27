'''
Author: Carlo Cherisier
Date: 09.05.14
Script: publishAssetFUNC
'''
import translators
translator = translators.getCurrent()

import caretaker
ct = caretaker.getCaretaker()

import sys, os
sys.path.append( 'c:/ie/ark/tools/dataDecoder')
import dataDecoder
reload( dataDecoder)

class guiFunc(object):
	'''
	Functions for GUI
	'''
	def __init__( self):
		## Class Variables
		self.hiRezList = []
		self.hiRezDict = {}
		self.lowRez = False
		self.assetName = 'Test'
		self.publishFolderPath = 'Test'
		self.departmentFolder = ''
		self.publishFolderPath = ''
		self.publishVersion = ''
		self.geoCheck = [ 'NURBS', 'GeometryClass', 'mesh']
		self.layerList= []
		self.skipDevFile = True

		## Grab layer List
		self.layerList = translator.getNewLayers()

		if len( self.layerList) == 1:
			if '0' in self.layerList:
				translator.createLayer( 'geoLayer')

				translator.moveLayerObjects( source= '0', dest= 'geoLayer')

				self.layerList.append( 'geoLayer')
				self.layerList.remove( '0')

#------------------- CREATING FOLDERS----------------------------------#
	def createAssetFolder( self, projName, newAssetName):
		'''
		Create new Asset Folders
		'''
		subFolderList = ['Model', 'Digi Matte', 'FX', 'Rig', 'Lighting', 'Materials', 'Reference', 'Texture', 'Published']

		newAssetFolder = 'r:/{0}/Project_Assets/{1}'.format( projName, newAssetName)

		##Check if folder exists
		check = os.path.exists( newAssetFolder)

		if check== True:
			return

		else:
			## Make Asset Folder
			os.makedirs( newAssetFolder)

			for each in subFolderList:
				## Join Sub Folder to Main Asset Folder
				subFolder = os.path.join( newAssetFolder, each)

				## Make Asset Sub Folder
				os.makedirs( subFolder)
	#
	def startNewPublishFolder( self, deptName):
		'''
		Purpose:
			Check if Published Asset should start at Version 001
		'''
		## Function Variables
		startOver = 0
		result = translator.getData( 'smart_deptName')
		deptList = [ 'Anim Scene', 'Lighting Scene', 'FX Scene']
		## Construct folder path
		folderPath = '{0}/{1}'.format( self.publishFolderPath, deptName.split(' ')[0])

		if result in deptList:
			startOver = 1

		if not os.path.exists( self.departmentFolder):
			startOver = 2

		if len( os.listdir( self.departmentFolder)) == 0:
			startOver = 2

		if not os.path.exists( folderPath):
			os.makedirs( folderPath)
			startOver = 1

		return startOver, folderPath
	#
	def createPublishFolder( self, deptName):
		'''
		Purpose:
			Create publish version folder for asset
			If Department Folder doesn't exist make version folder 001
			If Department folder exist but contins no files make version folder 001
			Create Main Folder for Asset
		'''
		## Check Asset Publish Folder
		startOver, folderPath = self.startNewPublishFolder( deptName)

		if startOver != 0:
			## Set publish version
			if startOver == 2:
				self.publishVersion = 'v001'
				self.skipDevFile = False

			else:
				tempList = os.listdir( folderPath)
				if tempList != []:
					size = int(sorted(tempList)[-1][1:])+1

				else:
					size = 1
				self.publishVersion = 'v{0:03}'.format( size)

			## Construct folder path
			folderPath = '{0}/{1}'.format( folderPath, self.publishVersion)

		else:
			if '_' in translator.getFilename():
				self.publishVersion = translator.getFilename().split( '_')[-2]

			else:
				self.publishVersion = 'v001'
				self.skipDevFile = False

			## Construct folder path
			folderPath = '{0}/{1}'.format( folderPath, self.publishVersion)

		if not os.path.exists( folderPath):
			## Make Folder
			os.makedirs( folderPath)

		else:
			## Remove files publish folder
			for each in os.listdir( folderPath):
				os.remove( folderPath + '/' + each)

		self.publishFolderPath = folderPath

#------------------- PUBLISHING ASSET FUNCTIONS----------------------------------#
	#
	def checkForRig( self):
		'''
		Purpose:
			Check if Scene node exists
			If not cancel Publish
		'''
		result = translator.objectExists( 'Scene')
		return result
	#
	def grabObjects( self):
		'''
		Purpose:
			Delete bBox and assetRoot if they are already in the scene
			Grab Selected Assets
			Save hiRez objects and lowRez objects
		'''
		## Check if bBox and assetRoot are in the scene
		## If so delete it
		result = translator.objectExists( 'bBox')
		if result == True:
			translator.deleteObject( 'bBox')

		result = translator.objectExists( 'assetRoot')
		if result == True:
			translator.deleteObject( 'assetRoot')

		## Check if anything is selected
		if not translator.isObjectSelected():
			return False

		## Lock objects transforms and make unselected
		translator.setObjectTransformLock( useSelected= True, value=True)
		translator.setObjectSelectionLock( useSelected= True, value=True)

		## Grab selected nodes
		self.hiRezList = translator.getSelectedObjectName()

		i=0
		for num in range( len( self.hiRezList)):
			num-= i
			if '__' in self.hiRezList[num]:
				newName= self.hiRezList[num].split( '__')[1]
				translator.setObjectName( newName= newName, oldName= self.hiRezList[num])
				self.hiRezList[num] = newName

			if translator.getObjectByType( self.hiRezList[num]) == 'nurbsCurve':
				self.hiRezList.pop( num)
				i+=1

		i= 0
		## Check if objects selected are in layerList
		if len( self.layerList) != 0:
			for num in range( len( self.hiRezList)):
				if num == len( self.layerList):
					break

				num-= i
				result = translator.isObjectInLayer( self.layerList[num], *self.hiRezList)

				if result == False:
					## Remove unuse layed from layer list
					self.layerList.pop( num)
					i+=1
				else:
					if '__' in self.layerList[num]:
						## Remove namespace from layer name
						newLayerName= self.layerList[num].split( '__')[-1]
						self.layerList[num]= newLayerName
						translator.changeLayerName( oldName= self.layerList[num], newName= newLayerName, replace= True)

		## Low rez list
		lowList = [' low rez', 'low res', 'lowrez', 'lowres']

		for low in lowList:
			if any( low.lower() in x.lower() for x in self.hiRezList):
				## Grab lowRez name
				result= [ x for x in self.hiRezList if low.lower() in x.lower() ][0]

				self.hiRezList.remove( result)
				self.lowRez = True
				self.lowRezName= result

		for each in self.hiRezList:
			## Grab object properties
			properties= translator.assetManager.getAssetProperties( each)

			## Change renderSubdivision (Maxs Turbosmooth.renderIterations)
			## to subdivision (Max's Turbosmooth.iterations)
			value= properties[ 'subdivision']
			properties[ 'subdivision']= 1
			properties[ 'renderSubdivision']= value

			## Grab object parent
			self.hiRezDict[ each] = properties[ 'parent']

			## Set object properties
			translator.assetManager.setAssetProperties( each, properties)
	#
	def select_hiRezObjects( self, returnNameList= False):
		'''
		Select all hiRez objects
		and return names as jobString
		'''
		## Clear Selection
		translator.clearSelection()

		## Select objects
		translator.selectObject( *self.hiRezList, add= True)

		return self.hiRezList
	#
	def makeBoundingBox( self):
		'''
		Make Bounding Box and Locator for select Objects
		'''
		## Select hiRez
		self.select_hiRezObjects()

		## Make bounding Box
		translator.assetManager.makeBoundingBox()

		## Clear Selection
		translator.clearSelection()
	#
	def createLocator( self):
		'''
		Create asset locator
		'''
		## Make Asset Root Locator
		translator.assetManager.makeAssetRoot()

		## Clear Selection
		translator.clearSelection()
	#
	def setLocaterToAssetParent( self):
		'''
		Make Locator the root for
		lowRez geo
		hiRez geo
		and boundingBox
		'''
		## Place Objects in layer
		objectList= ['assetRoot', 'bBox']

		if translator.layerExists( '0'):
			translator.placeObjectsInLayer( '0', *objectList)

		## Parent Bounding box to assetRoot Node
		translator.setParentObject( parentName= 'assetRoot', childName= 'bBox')

		if self.lowRez== True:
			## Parent lowRez to assetRoot Node
			translator.setParentObject( parentName= 'assetRoot', childName= self.lowRezName)

			## Place lowRez in layer
			if translator.layerExists( '0'):
				translator.placeObjectsInLayer( '0', *[self.lowRezName])

		for each in self.hiRezList:
			## Parent object to assetRoot Node
			translator.setParentObject( parentName= 'assetRoot', childName= each)

		## Clear Selection
		translator.clearSelection()


#------------------- EXPORTING FILES----------------------------------#
	def exportLowRezFile( self):
		'''
		Export Max File for lowRez
		'''
		## Select lowRez
		if self.lowRez== False:
			return None

		## Select lowRez and assetRoot
		translator.selectObject( self.lowRezName)

		## Add assetRoot to selection
		translator.selectObject( 'assetRoot', add= True)

		## Make file path
		fileName= '{0}/{1}_lowRez_{2}_{3}'.format( self.publishFolderPath, self.assetName, self.publishVersion, translator.setFileExtension())

		## Export lowRez
		translator.exportSelectObjects( fileName, 'assetRoot', cleanExport= True)

		## Clear Selection
		translator.clearSelection()

		return fileName
	#
	def exportHiRezFile( self):
		'''
		Export Max File for hiRez
		'''
		if translator.getProgram() == 'Maya':
			translator.setParentObject( parentName=None, childName= 'bBox')

		## Select hiRez
		self.select_hiRezObjects()

		## Add assetRoot to selection
		translator.selectObject( 'assetRoot', add= True)

		## Make Hi Rez file path
		fileName= '{0}/{1}_hiRez_{2}_{3}'.format( self.publishFolderPath, self.assetName, self.publishVersion, translator.setFileExtension())

		## Export lowRez
		translator.exportSelectObjects( fileName, 'assetRoot', cleanExport= True)

		if translator.getProgram() == 'Maya':
			translator.setParentObject( parentName= 'assetRoot', childName= 'bBox')

		## Clear Selection
		translator.clearSelection()

		return fileName
	#
	def exportBoundingBox( self):
		'''
		Export bounding Box
		'''
		## Make file path
		fileName= '{0}/{1}_bBox_{2}_{3}'.format( self.publishFolderPath, self.assetName, self.publishVersion, translator.setFileExtension())

		if translator.getProgram() == 'Maya':
			for each in self.hiRezList:
				translator.setParentObject( parentName=None, childName= each)

		## Select bounding box
		translator.selectObject( 'bBox')

		## Lock bounding box transform and selection
		translator.setObjectTransformLock( useSelected= True, value=True)
		translator.setObjectSelectionLock( useSelected= True, value=True)

		## Add assetRoot to selection
		translator.selectObject( 'assetRoot', add= True)

		## Export bounding box file
		translator.exportSelectObjects( fileName, 'assetRoot', cleanExport= True)

		if translator.getProgram() == 'Maya':
			for each in self.hiRezList:
				translator.setParentObject( parentName='assetRoot', childName= each)

		## Clear Selection
		translator.clearSelection()

		return fileName
	#
	def exportRigFile( self):
		'''
		Export Max File for Rig
		'''
		## Class Variable
		geoObjects=[]

		## Check if Rig has proper elements
		if not translator.objectExists( 'Scene'):
			return False

		## Select all rig objects
		translator.selectObjectAndChildren( 'Scene')

		## Grab selected objects
		selectedObjects= translator.getSelectedObjectName()

		## Select Geo objects from rig
		for each in selectedObjects:
			## Check object type
			result= translator.getObjectByType( objectName= each)

			if 'GeometryClass' in result or 'Polygon' in result:
				geoObjects= each

		## Clear Selection
		translator.clearSelection()

		## Select objects
		translator.selectObject( *geoObjects, add= True)

		## Lock Geo objects transforms and selection
		translator.setObjectTransformLock( useSelected= True, value=True)
		translator.setObjectSelectionLock( useSelected= True, value=True)

		## Turn on Geo objects display layer
		if translator.getProgram() == 'Max':
			translator.setObjectDisplayLayer( useSelected= True, value= True)

		## Select all rig objects
		translator.selectObjectAndChildren( 'Scene')

		## Make Rig file path
		fileName= '{0}/{1}_rig_{2}_{3}'.format( self.publishFolderPath, self.assetName, self.publishVersion, translator.setFileExtension())

		## Export bounding box file
		translator.exportSelectObjects( fileName)

		## Clear Selection
		translator.clearSelection()

		return fileName
	#
	def exportDevelopmentFile( self, deptName):
		'''
		Export Max File for Development
		'''
		## Make file path
		fileName= '{0}/{1}_{2}_{3}_{4}'.format( self.departmentFolder, self.assetName, deptName.split(' ')[0], self.publishVersion, translator.setFileExtension())

		if self.skipDevFile == True:
			return fileName

		## Clear Selection
		translator.clearSelection()

		## Export Rig file
		if deptName == 'Rig':
			translator.selectObjectAndChildren( 'Scene')

			## Unlock objects' transform and selection
			translator.setObjectTransformLock( useSelected= True, value= False)
			translator.setObjectSelectionLock( useSelected= True, value= False)

			## Export Rig file
			translator.exportSelectObjects( fileName)

		## Export Model file
		else:
			for each in self.hiRezList:
				## Parent object to assetRoot Node
				if translator.getProgram() == 'Max':
					translator.setParentObject( parentName='none', childName= each)

				if translator.getProgram() == 'Maya':
					translator.setParentObject( parentName=None, childName= each)

			## Select hiRez objects
			self.select_hiRezObjects()

			if self.lowRez:
				translator.selectObject( self.lowRezName, add= True)

			## Unlock objects' transform and selection
			translator.setObjectTransformLock( useSelected= True, value= False)
			translator.setObjectSelectionLock( useSelected= True, value= False)

			## Export development file
			translator.exportSelectObjects( fileName, 'assetRoot', cleanExport= True)

			for each in self.hiRezList:
				## Parent object to assetRoot Node
				if translator.getProgram() == 'Max':
					translator.setParentObject( parentName='assetRoot', childName= each)

				if translator.getProgram() == 'Maya':
					translator.setParentObject( parentName='assetRoot', childName= each)

		return fileName
		pass
	#
	def exportAlembicFile( self, deptName):
		'''
		Export Alembic for hiRez
		'''
		## Function List
		geoObjects = []

		## Make file path
		fileName= '{0}/{1}_alembic_{2}.abc'.format( self.publishFolderPath, self.assetName, self.publishVersion)

		## Get Start and End Frame
		startTime, endTime = translator.animationManager.getTime()

		if deptName == 'Rig':
			## Select all rig objects
			translator.selectObjectAndChildren( 'Scene')

			## Grab selected objects
			selectedObjects= translator.getSelectedObjectName()

			## Select Geo objects from rig
			for each in selectedObjects:
				## Check object type
				result= translator.getObjectByType( objectName= each)

				if result in self.geoCheck:
					geoObjects.append( each)

			## Clear Selection
			translator.clearSelection()

			## Select objects
			translator.selectObject( *geoObjects, add= True)

		else:
			## Select hiRez
			self.select_hiRezObjects()

		## Export Alembic File
		translator.exportAlembic( fileName, startTime, endTime)

		## Clear Selection
		translator.clearSelection()

		return fileName
	#
	def exportVrayFile( self, deptName, alembicFilePath=None):
		'''
		Export Vray Proxy for hiRez
		'''
		if translator.getProgram() == 'Max':
			## Make Hi Rez file path
			fileName = '{0}/{1}_vRayProxy_{2}_{3}'.format( self.publishFolderPath, self.assetName, self.publishVersion, translator.setFileExtension())

			## Check if bBox and assetRoot are in the scene
			## If so delete it
			result = translator.objectExists( 'vRayProxy')
			if result:
				translator.deleteObject( 'vRayProxy')

			## Create Vray Poxy
			vRayProxy = translator.assetManager.createvRayProxy( alembicFilePath)

			## Lock selection and transforms
			translator.setObjectTransformLock( vRayProxy, value= True)
			translator.setObjectSelectionLock( vRayProxy, value= True)

			## Clear Selection
			translator.clearSelection()

			## Match transform and rotation from assetRoot to vRay Poxy
			translator.matchMatrix( parentName= 'assetRoot', childName= vRayProxy)

			## Parent Vray Poxy to assetRoot
			translator.setParentObject( parentName= 'assetRoot', childName= vRayProxy)

			if self.lowRez:
				translator.selectObject( 'assetRoot', self.lowRezName, vRayProxy, add=True)
				translator.setRenderable( objectName= self.lowRezName, value=False)

				## Lock objects' transform and selection
				translator.setObjectTransformLock( self.lowRezName, value=True)
				translator.setObjectSelectionLock( self.lowRezName, value=True)

			else:
				translator.selectObject( 'assetRoot', 'bBox', vRayProxy, add=True)
				translator.setRenderable( objectName= 'bBox', value=False)

			## Export Rig file
			translator.exportSelectObjects( fileName)

			## Delete VRay Poxy
			translator.deleteObject( vRayProxy)

		if translator.getProgram() == 'Maya':
			## Make Hi Rez file path
			fileName = '{0}/{1}_vRayProxy_{2}_{3}.vrmesh'.format( self.publishFolderPath, self.assetName, self.publishVersion, ct.userInfo['initials'])

			## Select hiRez
			self.select_hiRezObjects()

			## Create Vray Proxy
			translator.assetManager.createvRayProxy( fileName)

		## Clear Selection
		translator.clearSelection()

		return fileName
	#
	def exportObjFile( self, deptName):
		'''
		Export .obj for hiRez
		'''
		## Function List
		geoObjects = []

		if deptName== 'Rig':
			## Select all rig objects
			translator.selectObjectAndChildren( 'Scene')

			## Grab selected objects
			selectedObjects= translator.getSelectedObjectName()

			## Select Geo objects from rig
			for each in selectedObjects:
				## Check object type
				result= translator.getObjectByType( objectName= each)

				if result in self.geoCheck:
					geoObjects.append( each)

			## Clear Selection
			translator.clearSelection()

			## Select objects
			translator.selectObject( *geoObjects, add= True)

		else:
			## Select hiRez
			self.select_hiRezObjects()

		## Make file path
		fileName = '{0}/{1}_obj_{2}.obj'.format( self.publishFolderPath, self.assetName, self.publishVersion)

		if translator.getProgram() == 'Maya':
			translator.loadPlugin( 'objExport')

		## Export OBJ file
		translator.exportOBJ( fileName)

		## Clear Selection
		translator.clearSelection()

		return fileName
	#
	def cleanFile( self):
		'''
		Purpose:
			Delete assetRoot and boundingBox out of scene so user has a clean file
		'''
		if self.lowRez == True:
			if translator.getProgram() == 'Max':
					translator.setParentObject( parentName= 'none', childName= self.lowRezName)

			else:
				translator.setParentObject( parentName= None, childName= self.lowRezName)

			translator.setObjectTransformLock( self.lowRezName, value= False)
			translator.setObjectSelectionLock( self.lowRezName, value= False)

		for each in self.hiRezList:
			## Unlock transforms, selection, and unparent
			if translator.getProgram() == 'Maya':
				translator.setParentObject( parentName= None, childName= each)

			translator.setObjectTransformLock( objectName= each, value= False)
			translator.setObjectSelectionLock( objectName= each, value= False)

		result = translator.objectExists( 'assetRoot')
		if result == True:
			## Delete assetRoot and boundindBox
			translator.deleteObject( 'bBox')
			translator.deleteObject( 'assetRoot')

		for key, value in self.hiRezDict.items():
			## Grab object properties
			properties = translator.assetManager.getAssetProperties( key)
			properties[ 'parent'] = value

			## Set object properties
			translator.assetManager.setAssetProperties( key, properties)

		## Clear Selection
		translator.clearSelection()
	#
	def storeAssetData( self, projName, deptName, assetName, lowRezPath, hiRezPath, rigPath, devPath, bBoxPath, abcPath, vrayPath, objPath):
		'''
		Purpose:
			Store Asset data in file
		'''
		# print( projName, deptName, assetName, lowRezPath, hiRezPath, devPath, bBoxPath, abcPath, objPath)

		## Grab program
		program = translator.getProgram()

		dataDecoder.store_publishedAssets( projName= projName, deptName= deptName.split(' ')[0], assetName= assetName, version= self.publishVersion, lowRezPath= lowRezPath, hiRezPath= hiRezPath, rigPath= rigPath, devPath= hiRezPath, bBoxPath= bBoxPath, abcPath= abcPath, vrayPath= vrayPath, objPath= objPath, layerList= self.layerList, program= program)