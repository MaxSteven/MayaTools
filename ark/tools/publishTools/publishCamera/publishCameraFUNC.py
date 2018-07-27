'''
Author: Carlo Cherisier
Date: 09.5.14
Script: publishCameraFUNC
'''
import sys, os
sys.path.append( 'c:/ie/ark/tools/dataDecoder')
import dataDecoder

import translators
translator = translators.getCurrent()
translator.executeNativeCommand= translator.executeNativeCommand

class guiFUNC(object):
	'''
	Functions for GUI
	'''
	## Class Variables
	startTime=0
	endTime=0
	assetName= 'Test'
	cameraType=''
	cameraSettings={}

	publish_folderPath= ''
	publishVersion=''

	def checkCamera( self):
		'''
		Check if Camera is a vRay Cam
		'''
		## Delete Old Camera
		result = translator.objectExists( 'newCamera')

		if result:
			translator.deleteObject( 'newCamera')

		## Check if camera is selected
		if translator.isObjectSelected():
			return False

		## Get Start and End Frame
		self.startTime, self.endTime= translator.animationManager.getTime()

		## Grab camera name
		self.originalCamera= translator.getSelectedObjectName()[0]

		## Camera camera type
		properties= translator.assetManager.getAssetProperties( objectName= self.originalCamera)

		if properties['camera']== 'VRayPhysicalCamera':
			self.cameraType= 'vRay'
			return 1

		else:
			self.cameraType= 'nativeCamera'
			return 2
	#
	def createPublishFolder( self, projName, assetName):
		'''
		Create Main Folder for Asset
		'''
		publishFolder= 'r:/{0}/Workspaces/{1}/Published/Camera'.format( projName, assetName)

		size= 0

		if os.path.exists( publishFolder):
			## Grab files
			file_List= os.listdir( publishFolder)

			## Grab list size
			size= len( file_List)

		if size== 0:
			## Set publish version
			self.publishVersion= 'v001'

			## Construct folder path
			self.publish_folderPath='{0}/v001'.format( publishFolder)

			try:
				## Make Folder
				os.makedirs( self.publish_folderPath)
			except WindowsError:
				print 'WindowsError'
				pass
		else:
			holder= 0
			for each in file_List:
				if 'v0' in each or 'v1' in each or 'v2' in each:
					## Grab version number
					version= int( each.split( 'v')[-1].split( '_')[0])
					if version>= holder:
						holder= version+1

			## Set publish version
			self.publishVersion= 'v{0:03}'.format( holder)

			## Construct folder path
			self.publish_folderPath='{0}/{1}'.format( publishFolder, self.publishVersion)

			if not os.path.exists( self.publish_folderPath):
				## Make Folder
				os.makedirs( self.publish_folderPath)

		return( self.publishVersion)


#------------------- PUBLISHING ASSET FUNCTIONS----------------------------------#
	def publishVRayCamera( self):
		'''
		Grab and Store VRay Camera information
		'''
		## Create max camera to export
		newCamera= 'publishCam__{0}'.format( self.publishVersion)

		## Create export camera
		translator.cameraManager.createVRayExportCamera( newCamera)

		## Get Native camera attributes
		self.cameraSettings= translator.cameraManager.getVRayCameraSettings( self.originalCamera)

		## Transfer Original Camera Setting to New Camera
		translator.cameraManager.transferCameraSettings( newCamera, self.cameraSettings)

		## Transfer animation
		translator.cameraManager.copyCameraAnimation( self.originalCamera, self.newCamera, self.startTime, self.endTime)

		## Lock camera transform and selection
		translator.setObjectTransformLock( newCamera, value=True)
		translator.setObjectSelectionLock( newCamera, value=True)
	#
	def publishNativeCamera( self):
		'''
		Grab and Store VRay Camera information
		'''
		## Create max camera to export
		newCamera= 'publishCam__{0}'.format( self.publishVersion)

		## Create export camera
		translator.cameraManager.createNativeExportCamera( newCamera)

		## Get Native camera attributes
		self.cameraSettings= translator.cameraManager.getNativeCameraSettings( self.originalCamera)

		## Transfer Original Camera Setting to New Camera
		translator.cameraManager.transferCameraSettings( newCamera, self.cameraSettings)

		## Transfer animation
		translator.cameraManager.copyCameraAnimation( self.originalCamera, self.newCamera, self.startTime, self.endTime)

		## Lock camera transform and selection
		translator.setObjectTransformLock( newCamera, value=True)
		translator.setObjectSelectionLock( newCamera, value=True)

#------------------- EXPORTING FILES----------------------------------#
	def exportNativeFile( self):
		'''
		Export Max File for Camera
		'''
		translator.selectObject( self.newCamera)

		## Make file path
		fileName = '{0}/{1}_Camera.{2}'.format( self.publish_folderPath, self.cameraType, translator.fileExtension)

		## Export Camera
		translator.exportSelectObjects( fileName)

		return fileName
	#
	def exportAlembicFile( self):
		'''
		Export Alembic File for Camera
		'''
		## Construct camera name
		alembicCamera= 'alembicCamera__{0}'.format( self.publishVersion)

		## Create Alembic camera to export
		translator.cameraManager.createNativeExportCamera( alembicCamera)

		## Transfer camera animation
		translator.cameraManager.copyCameraAnimation( self.originalCamera, alembicCamera, self.startTime, self.endTime)

		if self.cameraType== 'vRay':
			## Set Native camera with vRay camera settings
			translator.cameraManager.tranferVRayToNativeCameraSetting( alembicCamera, self.cameraSettings)

		else:
			## Transfer Original Camera Setting to New Camera
			translator.cameraManager.transferCameraSettings( alembicCamera, self.cameraSettings)

		## Make file path
		fileName = '{0}/{1}_Camera.abc'.format( self.publish_folderPath, self.cameraType)

		## Select Alembic Camera
		translator.selectObject( alembicCamera)

		## Export Camera
		translator.cameraManager.exportAlembicCamera( fileName, self.startTime, self.endTime)

		## Delete Camera
		translator.deleteObject( alembicCamera)

		return fileName
	#
	def exportFbxFile( self):
		'''
		Export FBX for Camera
		'''
		## Construct camera name
		fbxCamera = 'fbxCamera__{0}'.format( self.publishVersion)

		## Create FBX camera to export
		translator.cameraManager.createNativeExportCamera( fbxCamera)

		## Transfer animation
		translator.cameraManager.copyCameraAnimation( self.originalCamera, fbxCamera, self.startTime, self.endTime)

		if self.cameraType== 'vRay':
			## Set Native camera with vRay camera settings
			translator.cameraManager.tranferVRayToNativeCameraSetting( fbxCamera, self.cameraSettings)

		## Make file path
		fileName = '{0}/{1}_Camera.fbx'.format( self.publish_folderPath, self.cameraType)

		## Select FBX Camera
		translator.selectObject( 'fbxCamera')

		## Export FBX Camera
		translator.cameraManager.exportFBXCamera( fileName)

		return fileName
	#
	def exportCamera( self, mode, projName, shotName):
		'''
		Export Camera
		'''
		## Create Path to store camera files
		self.createPublishFolder( projName, shotName)

		if mode== 1:
			self.publishVRayCamera()

		elif mode== 2:
			self.publishNativeCamera()

		## Export out Camera
		maxPath = self.exportNativeFile()
		abcPath = self.exportAlembicFile()
		fbxPath = self.exportFbxFile()

		## Store Camera Data
		dataDecoder.store_cameraData( projName, shotName, self.publishVersion, self.cameraSettings, maxPath, abcPath, fbxPath)

		print self.publishVersion
	#
	def deleteCamera( self, name):
		'''
		Delete Orginal Camera
		'''
		translator.deleteObject( name)