
class Max_CameraManager( object):

	def __init__(self, translator):
		self.translator = translator

	def createVRayExportCamera( self, cameraName):
		func='''
		exportCamera= vrayPhysicalCamera()
		exportCamera.name= "{}"
		'''.format( cameraName)
		self.translator.executeNativeCommand( func)

	def createNativeExportCamera( self, cameraName):
		func='''
		exportCamera= FreeCamera()
		exportCamera.name= "{}"
		'''.format( cameraName)
		self.translator.executeNativeCommand( func)

	def getVRayCameraSettings( self, cameraName):
		cameraSettings={}

		## List of Maxwell camera attributes
		settingsList= [ 'type', 'targeted', 'film_width', 'focal_length', 'specify_fov', 'FOV', 'f_number', 'target_distance', 'vignetting', 'vignetting_amount', 'whiteBalance_preset', 'shutter_speed', 'shutter_angle', 'ISO', 'distortion_type', 'use_dof', 'use_moblur', 'clip_on', 'clip_near', 'clip_far', 'use_blades', 'blades_number', 'blades_rotation', 'anisotropy', 'optical_vignetting', 'bitmap_aperture_on']

		for each in settingsList:
			## Grab camera values
			func='''
			maxCamera= getnodebyname "{0}"
			print maxCamera.{0}
			'''.format( each)
			## Run Max Script
			value= self.translator.executeNativeCommand( func)

			## Store value
			cameraSettings[each]= value

			return cameraSettings

	def getNativeCameraSettings( self, cameraName):
		cameraSettings={}

		## List of Maxwell camera attributes
		settingsList= [ 'type', 'FOV','clipManually', 'nearclip', 'farclip', 'baseObject.Maxwell_Parameters.fStop', 'baseObject.Maxwell_Parameters.shutterSpeed', 'baseObject.Maxwell_Parameters.filmISO']

		for each in settingsList:
			## Grab camera values
			func='''
			maxCamera= getnodebyname "{0}"
			print maxCamera.{0}
			'''.format( each)
			## Run Max Script
			value= self.translator.executeNativeCommand( func)

			## Store value
			cameraSettings[each]= value

			return cameraSettings

	def transferCameraSetting( self, cameraName, cameraSettings):
		## Set new camera with proper setting
		for each in cameraSettings.keys():
			func='''
				maxCamera= getnodebyname "{0}"
				maxCamera.{1}= {2}
				'''.format( cameraName, each, cameraSettings[each])
		self.translator.executeNativeCommand( func)

	def copyCameraAnimation( self, sourceCamera, targetCamera, startTime, endTime):
		func='''
			sourceCamera= getnodebyname "{0}"
			targetCamera= getnodebyname "{1}"
			with animate on(
			for i={2} to {3} do(
				at time i
				(
					camTransform = orthogonalize sourceCamera.transform
					targetCamera.transform = camTransform)))
		'''.format( sourceCamera, targetCamera, startTime, endTime)
		self.translator.executeNativeCommand( func)

	def tranferVRayToMaxWellCameraSetting( self, cameraName, cameraSettings={}):
		func='''
		exportCamera= getnodebyname "{0}"
		exportCamera.type= #free
		exportCamera.fov= {1}
		exportCamera.clipManually= {2}
		exportCamera.nearclip= {3}
		exportCamera.farclip= {4}
		exportCamera.baseObject.Maxwell_Parameters.shutterSpeed= {5}
		exportCamera.baseObject.Maxwell_Parameters.filmISO = {6}
		exportCamera.baseObject.Maxwell_Parameters.fStop = {7}
		'''.format( cameraName, cameraSettings[ 'FOV'], cameraSettings[ 'clip_on'], cameraSettings[ 'clip_near'], cameraSettings[ 'clip_far'], cameraSettings[ 'shutter_speed'], cameraSettings[ 'ISO'], cameraSettings[ 'f_number'] )
		self.translator.executeNativeCommand( func)

	def exportAlembicCamera( self, filePath, startTime, endTime):
		## Create set export arguments
		jobString= 'filename={0};'.format( filePath)
		jobString+= 'in={0};out={1};step=1;substep=1;'.format( self.startTime, self.endTime)
		jobString+= 'exportselected=true;flattenhierarchy=false;automaticinstancing=true;transformCache=false;'

		## Export Camera
		func= '''
		ExocortexAlembic.createExportJobs("{0}")
		'''.format( jobString)
		self.translator.executeNativeCommand( func)

	def exportFBXCamera( self, filePath):
		func='''
		select fbxCamera
		FBXExporterSetParam "ASCII" true
		FBXExporterSetParam "Animation" true
		FBXExporterSetParam "AxisConversionMethod" #animation
		FBXExporterSetParam "SmoothingGroups" true
		FBXExporterSetParam "UpAxis" "Y"

		exportFile "{0}" #noPrompt selectedOnly:on using:FBXEXP
		delete fbxCamera
		'''.format( filePath)
		## Run Maxscript
		self.translator.executeNativeCommand( func)

