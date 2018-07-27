
from translators import Translator
from translators import QtGui#, QtCore

import caretaker
ct = caretaker.getCaretaker()

import MaxPlus
import settingsManager
globalSettings = settingsManager.globalSettings()
# import ieOS
import cOS
# import ieCommon
import arkUtil
from datetime import date
# from Settings import Settings

from Max_AnimationManager import Max_AnimationManager
from Max_AssetManager import Max_AssetManager
from Max_CameraManager import Max_CameraManager

class Max(Translator):

	# canUse = True
	# hasCameras = True
	# hasFrames = True
	# hasPasses = True
	# closeOnSubmit = False

	keys = {"passNames" : 1000}

	def __init__(self):
		super(Max, self).__init__()
		self.settings.append(canUse=True,
			node= 'camera',
			hasFrames=True,
			hasPasses=True,
			hasDeep=True,
			hasKeyCommands=False,
			closeOnSubmit=False,
			singleArkInit=True)

		self.fileExtension = 'max'
		self.animationManager = Max_AnimationManager(self)
		self.assetManager = Max_AssetManager(self)
		self.cameraManager = Max_CameraManager(self)

	def getProgram( self):
		return( 'Max')

	# Publish API Tools
	########################################
	def setFileExtension(self):
		'''
		Set Intials with file extension
		'''
		if not ct.userInfo or 'initials' not in ct.userInfo:
			return( '.max')

		fileExtension = '{0}.max'.format( ct.userInfo['initials'])

		return( fileExtension)

	# Nodes
	########################################

	SuperIdTypes = {
		MaxPlus.SuperClassIds.Osm : MaxPlus.Modifier,
		MaxPlus.SuperClassIds.Wsm : MaxPlus.Modifier,
		MaxPlus.SuperClassIds.Helper : MaxPlus.HelperObject,
		MaxPlus.SuperClassIds.GeomObject : MaxPlus.GeomObject,
		MaxPlus.SuperClassIds.Light : MaxPlus.LightObject,
		MaxPlus.SuperClassIds.Texmap : MaxPlus.Texmap,
		MaxPlus.SuperClassIds.Material : MaxPlus.Mtl,
		MaxPlus.SuperClassIds.Atmospheric : MaxPlus.Atmospheric,
		MaxPlus.SuperClassIds.SoundObj : MaxPlus.SoundObj,
		MaxPlus.SuperClassIds.Renderer : MaxPlus.Renderer,
		MaxPlus.SuperClassIds.Camera : MaxPlus.CameraObject
	}

	def getNodesByType(self, nodeType):
		nodeType = nodeType.lower()
		nodes = []
		for n in self.getSceneNodes():
			baseObject = n.GetBaseObject()
			cast = self.castObject(baseObject)
			if cast:
				if nodeType in str(type(cast)).lower():
					nodes.append(n.Name)
		return nodes

	def getSceneNodes(self):
		allNodes = []
		def getNodes(allNodes, nodes):
			allNodes += nodes
			for node in nodes:
				children = list(node.Children)
				if len(children):
					getNodes(allNodes, children)

		getNodes(allNodes, list(MaxPlus.Core.GetRootNode().Children))
		return allNodes

	def castObject(self, o):
		if not o: return None
		sid = o.GetSuperClassID()
		if not sid in self.SuperIdTypes: return None
		return self.SuperIdTypes[sid]._CastFrom(o)


	# Data Storage
	########################################
	def stringToInteger( self, thisString= ''):
		number=0
		for each in thisString:
			number+= int( ord( each))
		return( number)

	def setData(self, key= '', val=None):
		data = {}

		# lets you either pass a complete dictionary
		if val is None and isinstance(key, dict):
			data = key
		# or pass key, val
		else:
			data[key] = val

		for key in data.keys():
			## Convert key into an integer
			number= self.stringToInteger(key)

			## Maxscript function
			func = 'setAppData rootnode {0} "{1}"'.format( number, data[key])
			print 'setAppData', number

			self.executeNativeCommand( func)

	def getData(self, key=None):
		if key!= '' or key!= None:
			## Convert String to number
			number= self.stringToInteger( key)

			## Maxscript function
			func = 'print (getAppData rootnode {0})'.format( number)

			value = self.executeNativeCommand( func)
			# print( value, number, key)

			if (value != 'undefined'):
				return( value)
		return('')

	def removeData(self, key):
		self.executeNativeCommand("deleteAppData rootnode %s" % (self.keys[key]))

	# # File Info
	#####################################

	def getFilename(self):
		return MaxPlus.FileManager.GetFileNameAndPath()

	def saveFile(self, filePath=None):
		if filePath!= None:
			##Create MaxScript function
			func = 'saveMaxFile "{0}" useFileUnit:true quiet:true'.format( filePath)

			## Run Maxscript
			self.executeNativeCommand(func)
			return

		return MaxPlus.FileManager.Save()

	def openFile(self, filePath, smartTool= False):
		if smartTool == True:
			## Open without prompt
			func = 'actionMan.executeAction 0 "16" '
			self.executeNativeCommand(func)

		else:
			MaxPlus.FileManager.Open( filePath)

	def isFileDirty(self):
		return MaxPlus.FileManager.IsSaveRequired()

	def saveIncrementWithInitials(self):
		if not ct.userInfo or 'initials' not in ct.userInfo:
			self.executeNativeCommand('print "You need to log into Caretaker for this to work!!')
			return

		# newScript = self.getFilename()[:-6] + ct.userInfo['initials'] + '.max'
		newScript = self.getFilename()
		newScript = cOS.incrementVersion( self.getFilename())

		MaxPlus.FileManager.Save(newScript)

	def getFileInfo(self):
		#fix: this needs more file info
		fileInfo = {}

		fileName = self.getFilename()
		if fileName:
			fileParts = fileName.replace('\\', '/').split('/')
			if len(fileParts) > 3 and fileParts[2].upper() == 'WORKSPACES':
				fileInfo['shotName'] = fileParts[3]
			elif len(fileParts) > 3:
				fileInfo['shotName'] = fileParts[2] + '-' + fileParts[3]
			fileInfo['version'] = cOS.getVersion(fileName)

			fileInfo['version'] = arkUtil.pad(int(fileInfo['version']), 3)
			fileInfo['jobName'] = fileParts[1]

			fileInfo['jobRoot'] = globalSettings.SHARED_ROOT + fileInfo['jobName'] + '/'
			today = date.today()

			fileInfo['postingRoot'] = fileInfo['jobRoot'] + 'POSTINGS/' + str(today.year) + '_' + arkUtil.pad(today.month, 2) + '_' + arkUtil.pad(today.day, 2) + '/'

		return fileInfo

	# # Event Listening
	#####################################

	def addCallbacks(self, action, eventName, callback):
		pass
		# if action == 'load':
		# 	MaxPlus.Core.EvalMAXScript("callbacks.addScript #filePostOpen python.execute(self.fireEvent( " + eventName + "))")
		# 	self.onAppEvent(eventName, callback)
		# elif action == 'save':
		# 	MaxPlus.Core.EvalMAXScript("callbacks.addScript #filePreSave python.execute(self.fireEvent( " + eventName + "))")
		# 	self.onAppEvent(eventName, callback)

	# # Rendering
	#####################################

	def getDefaultJobName(self):
		return MaxPlus.FileManager.GetFileName().split('/')[-1][:-4]

	def getRenderProperties(self, camera):
		renderProperties = {
				'width': MaxPlus.RenderSettings.GetWidth(),
				'height': MaxPlus.RenderSettings.GetHeight(),
				# fix:  no maxplus function to get start and end frame from render settings.
				'frameRange' : self.executeNativeCommand('print (ieMaxGetRenderFrameRange())'),
				'startFrame': self.executeNativeCommand('print animationrange.start.frame'),
				'endFrame': self.executeNativeCommand('print animationrange.end.frame'),
				'program': 'max'
			}

		if 'maxwell' in self.executeNativeCommand('print renderers.current').lower():
			renderProperties['shadingLevel'] = self.executeNativeCommand('print renderers.current.gsSamplingLevel')
			renderProperties['shading_level'] = renderProperties['shadingLevel']
			renderProperties['jobType'] = 'Max_Maxwell'

		elif 'v_ray' in self.executeNativeCommand('print renderers.current').lower():
			renderProperties['shadingLevel'] = self.executeNativeCommand('print renderers.current.dmc_earlyTermination_threshold')
			renderProperties['shading_level'] = renderProperties['shadingLevel']
			renderProperties['jobType'] = 'Max_Vray'

		else:
			print 'Not Maxwell of VRay?  Is this amateur hour?'
		return renderProperties


	def getOutputFilename(self, outputRoot, jobData):
		outputFile = outputRoot + ('/renders/v%03d/' % jobData['version']) + \
			jobData['name'] + '_' + jobData['cameraName'] + '.%04d.exr'
		# fix: should make a generic "safe filename" function to wrap this in

		path = outputFile[:2] + outputFile[2:].replace(':','_')
		return path

	def setOutputFilename(self, outputFile, jobData):
		currentRenderer = self.executeNativeCommand('print renderers.current').lower()
		if 'maxwell' in currentRenderer:
			print outputFile, 111
			self.executeNativeCommand('renderers.current.gsMXSOutputPath = "' + outputFile.replace('%04d.exr','mxs') + '"')
			self.executeNativeCommand('renderers.current.gsMXIOutputPath = "' + outputFile.replace('%04d.exr','mxi') + '"')
			self.executeNativeCommand('renderers.current.gsOverrideImagePath = "' + outputFile + '"')

		elif 'v_ray' in currentRenderer:
			if jobData['deep']:
				print 'Submitting deep'
				self.executeNativeCommand('renderers.current.output_rawFileName = "' + outputFile.replace('%04d.exr','.exr') + '"')
				self.executeNativeCommand('renderers.current.output_rawExrDeep = true')
			else:
				print 'Submitting normal, not deep'
				self.executeNativeCommand('renderers.current.output_rawFileName = "' + outputFile.replace('%04d.exr','.exr') + '"')
				self.executeNativeCommand('renderers.current.output_rawExrDeep = false')

	# # Pre's
	######################################

	def preRender(self):
		pass

	def preSubmit(self, jobData):
		self.executeNativeCommand('ieMaxPreSubmit()')
		self.saveFile()

	def postSubmit(self, jobData):
		self.executeNativeCommand('ieMaxPostSubmit()')

	def executeNativeCommand(self, command):
		# keep escapes
		command = command.replace('\\','\\\\').replace('"','\\"')
		MaxPlus.Core.EvalMAXScript('ieMaxExecuteCommand "%s"' % command)
		with open(globalSettings.MAX_TOOLS_ROOT + 'temp/maxResult.txt') as f:
			result = f.read()
		print 'maxscript result:', result
		return result

	# # PySide
	######################################

	def getQTApp(self):
		return QtGui.QApplication.instance()

	def launch(self, Dialog, qApplication=None, *args, **kwargs):
		app = self.getQTApp()
		ex = Dialog(None, *args, **kwargs)
		ex.show()
		app.exec_()




	########################################
	# Weaver Functions
	########################################

	# Object Creation
	########################################
	def boxCreate(self, name= 'Box'):
		box = MaxPlus.Factory.CreateGeomObject(MaxPlus.ClassIds.Box)
		MaxPlus.Factory.CreateNode(box)
		return box

	def arealightCreate(self, name= 'areaLight'):
		return MaxPlus.Factory.CreateLightObject(MaxPlus.ClassIds.AreaLight)

	def cameraCreate(self, name= 'camera'):
		pass

	# Property Settings
	########################################
	def setProperty(self, obj, key, value):
		pass

	def setWidth(self, obj, value, entity):
		obj.ParameterBlock.Width.Value = value

	def setHeight(self, obj, value, entity):
		obj.ParameterBlock.Height.Value = value

	def setLength(self, obj, value, entity):
		obj.ParameterBlock.Length.Value = value

	def arealight_setWidth(self, obj, value, entity):
		obj.ParameterBlock.Width.Value = value

	def arealight_setHeight(self, obj, value, entity):
		obj.ParameterBlock.Height.Value = value

	def setFocallength(self, obj, value, entity):
		obj.ParameterBlock.Lens.Value = value

	def setShutterangle(self, obj, value, entity):
		pass

	def setFstop(self, obj, value, entity):
		pass

	def setFocusdistance(self, obj, value, entity):
		obj.ParameterBlock.FocalDepth.Value = value

	def setVisibility(self, obj, value, entity):
		obj.ParameterBlock.IsHidden.Value = value

	def setChildren(self, obj, value, entity):
		pass


	# Transform Properties
	########################################
	def transform(self, obj, transform):
		# These functions exist
		# obj.Move(<something>)
		# obj.Rotate(<something else>)
		# obj.Scale(<something different from the first two>)
		pass

	# Instancing
	########################################
	def instanceObject(self, original):
		return MaxPlus.Factory.CreateNode(original)

	# Importing / Export
	########################################
	def importFile(self, filePath, namespace=None, smartTool=0):
		if smartTool:
			##Create MaxScript function
			func= 'mergeMAXFile "{0}" #select #neverReparent #useSceneMtlDups #deleteOldDups quiet:true'.format( filePath)
			self.executeNativeCommand(func)
			self.executeNativeCommand( 'CompleteRedraw()')

			## Give import objects a namespace
			if namespace != None:
				if 'Rig' in filePath:
					## Run Maxscript
					self.executeNativeCommand('select $Scene/.../*')

				## Grab selected nodes
				selected_List= list( MaxPlus.SelectionManager.Nodes)
				for each in selected_List:
					name= each.GetName()
					each.SetName( '{0}__{1}'.format( namespace, name))

		else:
			MaxPlus.FileManager.Import(filePath)

	def importAlembic(self, filePath):
		pass

	def exportAlembic(self, filePath, startTime, endTime):
		## Create set export arguments
		jobString= 'filename={0};'.format( filePath)
		jobString+= 'in={0};out={1};step=1;substep=1;'.format( startTime, endTime)
		jobString+= 'normals=true; uvs=true;materialids=true;bindpose=true;'
		jobString+= 'exportselected=true;flattenhierarchy=false;automaticinstancing=true;transformCache=false;'

		## Export alembic file
		func = 'ExocortexAlembic.createExportJobs("{0}")'.format( jobString)
		self.executeNativeCommand( func)

	def exportOBJ( self, filePath):
		func = '''
			exportClass_List = exporterPlugin.classes
			exportFile "{0}" #noPrompt selectedOnly:on using:exportClass_List[ 15]
			'''.format( filePath)
		## Run Maxscript
		self.executeNativeCommand( func)

	def exportSelectObjects( self, filePath, objectName=None, cleanExport=False):
		if cleanExport == True:
			func = '''
				thisDummy= dummy()
				objectName= getnodebyname "{0}"
				thisDummy.transform = objectName.transform
				objectName.transform= matrix3 1
				'''.format( objectName)
			self.executeNativeCommand( func)

		func = 'saveNodes $ "{0}"'.format( filePath)
		self.executeNativeCommand( func)

		if cleanExport == True:
			func = '''
			objectName.transform= thisDummy.transform
			delete thisDummy
			'''
			self.executeNativeCommand( func)

	## Selection
	def selectObject( self, *objectName, **kwargs):
		if 'add' in kwargs and kwargs['add']== True:
			for each in objectName:
				func= '''
				selectObjects= getCurrentSelection()
				objectName = getnodebyname "{0}"

				if objectName != undefined then
					(
						append selectObjects objectName
					)
				select selectObjects
				'''.format( each)
				self.executeNativeCommand( func)

		else:
			for each in objectName:
				func= '''
				objectName = getnodebyname "{0}"
				if objectName != undefined then
					(
						select objectName
					)
				isvalidNode objectName
				'''.format( each)
				result = self.executeNativeCommand( func)

			if result== 'false':
				return False

			else:
				return True

	def getSelectedObjectName( self,):
		## Grab selected nodes
		tempList= MaxPlus.SelectionManager.GetNodes()

		selectObjects=[]
		for each in tempList:
			selectObjects.append( each.GetName())

		return selectObjects

	def setObjectName( self, newName, oldName= None):
		func= '''
		objectName = getCurrentSelection()[1]
		if objectName != undefined then
			(
				objectName.name = "{0}"
			)
		'''.format( newName)
		self.executeNativeCommand( func)

	def clearSelection( self):
		self.executeNativeCommand( 'deselect $*')

	def selectObjectAndChildren( self, objectName):
		func = '''
		select ${0}/.../*
		'''.format( objectName)
		self.executeNativeCommand( func)

	def namespaceExists( self, namespace):
		func = '''
		namespaceObjects = for obj in $*{0}* collect obj
		isvalidNode namespaceObjects[1]
		'''.format( namespace)

		## Run Maxscript
		result = self.executeNativeCommand( func)

		if result== 'true':
			return True
		else:
			return False

	def objectExists( self, objectName):
		func = '''
		objectName = getnodebyname "{0}"
		isvalidNode objectName
		'''.format( objectName)

		## Run Maxscript
		result= self.executeNativeCommand( func)

		if result== 'true':
			return True
		else:
			return False

	def searchSceneForObjects( self, objectName, findAndSelect=False, searchFilter=None, addToSelection=False):
		## Collect all objects with name
		func = '''
		searchObjects = for obj in $*{0}* collect obj
		isvalidNode searchObjects[1]
		'''.format( objectName)
		result = self.executeNativeCommand( func)
		# print result

		if result == 'undefined':
			return False

		if searchFilter != None:
			func = '''
			filterList = #()
			for obj in searchObjects do
			(
				if (findString obj.name "{0}") != undefined then
				(
					--Add control to list
					append filterList obj
				)
			searchObjects = filterList
			isvalidNode filterList[1]
			)
			'''.format( searchFilter)
			result = self.executeNativeCommand( func)

			if result == 'undefined':
				return False

		if findAndSelect == True:
			## Select objects
			self.executeNativeCommand( 'select searchObjects')

		if addToSelection == True:
			func= '''
			-- Grab selected objects
			selectObject= getCurrentSelection()

			-- Add objects to list
			append addObjects selectObject

			-- Select object list
			select addObjects
			'''

		else:
			func= '''
			addObjects = #()
			'''
		self.executeNativeCommand( func)

		return True

	def isObjectSelected( self):
		check= self.executeNativeCommand( 'print $')

		if check== 'undefined':
			return False

		else:
			return True

	def getObjectByType( self, objectName):
		## Get Object Type
		func='''
		objectName = getnodebyname "{0}"
		result = SuperclassOf objectName
		print result
		'''.format( objectName)
		result= self.executeNativeCommand( func)

		return result

	def deleteObject( self, objectName=None, useSelected=False):
		if useSelected == True:
			func = '''
			selectObjects = getCurrentSelection()
			delete selectObjects
			'''
		else:
			func = '''
			objectName = getnodebyname "{0}"
			delete objectName
			'''.format( objectName)

		self.executeNativeCommand( func)

	def setObjectTransformLock( self, objectName=None, useSelected=False, value=True):
		if value== True:
			result= 'all'
		else:
			result= 'none'

		if objectName:
			func = '''
			objectName = getnodebyname "{0}"
			setTransformLockFlags objectName #{1}
			'''.format( objectName, result)

		if useSelected:
			func = '''
			selectObjects = getCurrentSelection()
			setTransformLockFlags selectObjects #{0}
			'''.format( result)

		self.executeNativeCommand( func)

	def setObjectSelectionLock( self, objectName=None, useSelected=False, value=True):
		if value== True:
			result01= 'false'
			result02= 'true'
		else:
			result01= 'true'
			result02= 'false'

		if objectName:
			func = '''
			objectName = getnodebyname "{0}"
			objectName.showFrozenInGray = {1}
			objectName.isFrozen = {2}
			'''.format( objectName, result01, result02)

		if useSelected:
			func = '''
			selectObjects = getCurrentSelection()
			selectObjects.showFrozenInGray = {0}
			selectObjects.isFrozen = {1}
			'''.format( result01, result02)

		self.executeNativeCommand( func)

	def setObjectDisplayLayer( self, objectName= None, useSelected= False, value= True):
		if value== True:
			result= 'true'
		else:
			result= 'false'

		if objectName:
			func = '''
			objectName = getnodebyname "{0}"
			objectName.displayByLayer = {1}
			'''.format( objectName, result)

		if useSelected:
			func = '''
			selectObjects= getCurrentSelection()
			selectObjects.displayByLayer= {0}
			'''.format( result)

		self.executeNativeCommand( func)

	def setParentObject( self, parentName, childName):
		func = '''
		parentObject = getnodebyname "{0}"
		childObject = getnodebyname "{1}"
		childObject.parent= parentObject
		'''.format( parentName, childName)
		self.executeNativeCommand( func)

	def matchPosition( self, parentName, childName):
		func = '''
		parentObject = getnodebyname "{0}"
		childObject = getnodebyname "{1}"
		parentPosition= parentObject.pos
		childObject.pos= parentPosition
		'''.format( parentName, childName)
		self.executeNativeCommand( func)

	def matchRotation( self, parentName, childName):
		func = '''
		parentObject = getnodebyname "{0}"
		childObject = getnodebyname "{1}"
		originPos= childObject.pos
		parentPosition= parentObject.rotation
		childObject.rotation= parentPosition
		childObject.pos= originPos
		'''.format( parentName, childName)
		self.executeNativeCommand( func)

	def matchMatrix( self, parentName, childName):
		func = '''
		parentObject = getnodebyname "{0}"
		childObject = getnodebyname "{1}"
		childObject.transform= parentObject.transform
		'''.format( parentName, childName)
		self.executeNativeCommand( func)

	def getMatrix( self, objectName, namespace=None):
		func='''
		objectName = getnodebyname "{0}"
		storedTransform{1} = objectName.transform
		'''.format( objectName, namespace)
		self.executeNativeCommand( func)

		## Store dummy name
		name= 'storedTransform{0}'.format( namespace)
		return name

	def setMatrix( self, objectName, storedTransform):
		func='''
		objectName = getnodebyname "{0}"
		objectName.transform = {1}
		'''.format( objectName, storedTransform)
		self.executeNativeCommand( func)


	def setRenderable( self, objectName= None, useSelected= False, value= None):
		if value== True:
			result= 'true'
		else:
			result= 'false'

		if useSelected == False:
			func='''
			objectName = getnodebyname "{0}"
			objectName.renderable= {1}
			'''.format( objectName, result)

		else:
			func='''
			selectObject = getCurrentSelection()
			selectObject.renderable= {0}
			'''.format( result)

		self.executeNativeCommand( func)

	def keySelectedObjects( self):
		func= '''
		objList = getCurrentSelection()

		with animate on
		(
			for obj in objList do
			(
				addNewKey obj[3] animationRange.start
			)
		)
		'''
		self.executeNativeCommand( func)


#Delete old version
	# Temp
	########################################
	def deleteEverything(self):
		sceneNode = self.getSceneNodes()

	def repath( self, sourcePath, destinationPath):
		'''
		Change all paths from sourcePath to destinationPath
		'''

		func = '''
		textures = getClassInstances Bitmaptexture
		for tex in textures do
		(
			filePath = toLower tex.filename
			if filePath != undefined then
			(
				filePath = substituteString filePath "\\\\" "/"
				print filePath

				if findString filePath "q:/assets" == undefined then
				(
					tex.filename = substituteString tex.filename "{0}" "{1}"
					tex.filename = substituteString tex.filename "{2}" "{3}"
				)
			)
		)

		textures = getClassInstances VRayHDRI
		for tex in textures do
		(
			filePath = toLower tex.HDRIMapName
			if filePath != undefined then
			(
				filePath = substituteString filePath "\\\\" "/"
				print filePath

				if findString filePath "q:/assets" == undefined then
				(
					tex.HDRIMapName = substituteString tex.HDRIMapName "{0}" "{1}"
					tex.HDRIMapName = substituteString tex.HDRIMapName "{2}" "{3}"
				)
			)
		)
		'''.format( sourcePath, destinationPath, sourcePath.upper(), destinationPath.upper())
		self.executeNativeCommand( func)

	def createLayer( self, layerName):
		func='''
		LayerManager.newLayerFromName "{0}"
		'''.format( layerName)
		self.executeNativeCommand( func)

	def placeObjectsInLayer( self, layerName, *objectList):
		func='''
		thisLayer= LayerManager.getLayerFromName "{0}"
		'''.format( layerName)
		result= self.executeNativeCommand( func)

		if result == 'undefined':
			return False

		for each in objectList:
			func='''
			objectName = getnodebyname "{0}"
			thisLayer.addNode objectName
			'''.format( each)
			result= self.executeNativeCommand( func)

	def changeLayerName( self, oldName, newName, replace= False):
		if replace == False:
			func='''
			found= false
			for i = 0 to layerManager.count-1 do
			(
				thisLayer = layerManager.getLayer i
				layerName = thisLayer.name
				if findString layerName "{0}" != undefined then
				(
					thisLayer.setname = "{1}"
					found = true
				)
			)
			print found
			'''.format( oldName, newName)

		else:
			func='''
				found= false
				for i = 0 to layerManager.count-1 do
				(
					thisLayer = layerManager.getLayer i
					layerName = thisLayer.name
					if findString layerName "{0}" != undefined then
					(
						if findString layerName "__" == undefined then
						(
							result = substituteString layerName "{0}" "{1}"
							thisLayer.setname result
							found = true
						)
					)
				)
				print found
				'''.format( oldName, newName)
			result = self.executeNativeCommand( func)

		if result == 'true':
			return True

		else:
			return False

	def getNewLayers( self):
		## Function variable
		layerList=[]

		func='''
		layerManager.count
		'''
		layerSize = int( self.executeNativeCommand( func))

		for i in range( layerSize):
			func='''
			found= false
			thisLayer = layerManager.getLayer {0}
			layerName = thisLayer.name
			layer = ILayerManager.getLayerObject {0}
			layerNodes = refs.dependents layer

			if	layerNodes.count > 2 then
			(
				found = layerName
			)

			print found
			'''.format( i)
			result = self.executeNativeCommand( func)

			if result != 'false':
				layerList.append( result)

		return layerList

	def layerExists( self, layerName):
		func='''
		found= false
		for i = 0 to layerManager.count-1 do
			(
				print i
				thisLayer = layerManager.getLayer i
				layerName = thisLayer.name
				if layerName =="{0}" then
				(
					found= true
				)
			)
		print found
		'''.format( layerName)
		result = self.executeNativeCommand( func)

		if result == 'true':
			return True
		return False

	def moveLayerObjects( self, source, dest):
		func='''
		sourceLayer= LayerManager.getLayerFromName "{0}"
		'''.format( source)
		result= self.executeNativeCommand( func)

		if result == 'undefined':
			return False

		func='''
		destLayer= LayerManager.getLayerFromName "{0}"
		'''.format( dest)
		result= self.executeNativeCommand( func)

		if result == 'undefined':
			return False

		## Grab objects from '0' Layer and place
		func='''
		layer = ILayerManager.getLayerObject "{0}"
		layerNodes = refs.dependents layer

		for obj in layerNodes do
		(
			result = SuperclassOf obj

			if result != 'ReferenceTarget' then
			(
				print obj
				destLayer.addNode obj
			)
		)
		'''.format( source)
		self.executeNativeCommand( func)

	def deleteLayerByName( self, *layerList):
		for each in layerList:
			func='''
			layerList= #()
			for i = 0 to layerManager.count-1 do
			(
				thisLayer = layerManager.getLayer i
				layerName = thisLayer.name
				if findString layerName "{0}" != undefined then
				(
					append layerList layerName
				)
			)

			for item in layerList do
			(
				LayerManager.deleteLayerByName item
			)
			'''.format( each)
			self.executeNativeCommand( func)

	def isObjectInLayer( self, layerName, *objectList):
		for each in objectList:
			func='''
			found= false

			objectName = getnodebyname "{0}"

			layer = ILayerManager.getLayerObject "{1}"
			layerNodes = refs.dependents layer

			for obj in layerNodes do
			(
				if obj == objectName then
				(
					found= true
				)
			)
			print found
			'''.format( each, layerName)
			result = self.executeNativeCommand( func)

			if result == 'true':
				return True
		return False

	def loadPlugin( self, pluginName):
		pass

	def unloadPlugin( self, pluginName):
		pass