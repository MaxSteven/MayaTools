
# import Entities
import sys
import time
# import shutil

from qt import QtGui
from qt import QtCore

import Events
from Settings import Settings

# weaver
# import Entities
# import collections

import arkInit
arkInit.init()

import arkUtil
import copyWrapper
import cOS
import caretaker
ct = caretaker.getCaretaker()

import settingsManager
globalSettings = settingsManager.globalSettings()

class Translator(object):
	# canUse = False
	# hasCameras = False
	# hasFrames = False
	# hasPasses = False
	# hasKeyCommands = False
	# singleArkInit = True

	def __init__(self):
		self.entities = {}
		self.nodes = {}
		self.objects = {}
		self.instanceNum = {}
		self.instancedNodes = {}
		self.materials = {}
		self.fileExtension = ''
		self.program = ''
		self.eventListener = Events.Events()
		self.settings = Settings(canUse=False,
			node='',
			hasFrames=False,
			hasPasses=False,
			hasKeyCommands=False,
			hasDeep=False,
			closeOnSubmit=True,
			singleArkInit=True,
			jobTypes=['Render'],
			appHandlesSubmit=False,
			hasSubdivision=False,
			hasSceneAssembly=False)

	# Tools
	########################################

	# WEAVER
	########################################
	def translateScene(self, weaver):
		# self.startTime = self.lastTime = time.clock()

		# scene = weaver.currentScene
		# allNodes = weaver.allNodes()

		# # objects are unhidden as they're displayed
		# self.hideAllObjects()

		# # Create all the unique entities first
		# # ex// primitives, models, materials, etc
		# # also store the instances as we go
		# self.instances = []
		# self.createdEntityIDs = []
		# self.usedEntityIDs = []
		# for entity in scene.entities:
		# 	print 'Entity:', entity
		# 	self.translateEntity(entity)

		# self.printTime('Create Entities')

		# # handles creation of entities we need but havent created yet
		# # ex// place nodes create only instances, not the original objects
		# entitiesToCreate = []
		# for entityID in self.usedEntityIDs:
		# 	if entityID not in self.createdEntityIDs:
		# 		matchingNode = weaver.getNodeByEntityID(entityID)
		# 		if matchingNode:
		# 			entitiesToCreate += matchingNode[0].eval().entities

		# # creates the remaining entities taht weren't already directly created
		# # by the scene but are needed by instances in the scene
		# # assumes (correctly for now) that those entities need to be hidden
		# for entity in entitiesToCreate:
		# 	entity.isHidden = True
		# 	self.translateEntity(entity)

		# # go through all the instances and eitehr create a new one or update existing
		# for entity in self.instances:
		# 	objects = self.getInstance(entity)
		# 	self.setTransform(objects, entity)
		# 	self.setMaterial(objects, entity)

		# self.printTime('Create Instances')
		# self.cleanScene(scene, allNodes)
		# self.printTime('Clean Scene')
		# self.postTranslate()
		# self.printTime('End Translate', self.startTime)

		# self.deleteEverything()

		# Get scene and all of the nodes from Weaver
		scene = weaver.currentScene
		allNodes = weaver.allNodes()
		for node in allNodes:
			node.imported = False

		# Get entities from current scene
		sceneEntities = scene.entities
		self.entities = collections.defaultdict(list)

		# Print Entities and IDs -- remove eventually
		# Add all of the entities to a dictionary mapping entityIDs to instances
		for e in sceneEntities:
			print 'Entity:', e
			print 'ID:', e.entityID
			print 'Properties:', e.properties
			print 'Help:', dir(e)
			print 'Is Instance:', e.isInstance
			print 'Transform:', e.transform
			self.entities[e.entityID].append(e)

		entityObjects = []
		instanceObjects = []
		for entityID in self.entities:
			orig = self.entities[entityID][0]
			instantiatedObject = self.instantiateOriginalEntity(orig)
			orig.objects.append(instantiatedObject)
			entityObjects.append((orig, instantiatedObject))
			if len(self.entities[entityID]) > 1:
				for instanceEntity in self.entities[entityID]:
					instantiatedInstance = self.instanceObject(instantiatedObject)
					instanceEntity.objects.append(instantiatedInstance)
					instanceObjects.append((instanceEntity, instantiatedInstance))

		for entity, obj in entityObjects:
			self.applyProperties(obj, entity)
			self.transformObject(obj, entity)
		for entity, obj in instanceObjects:
			self.transformObject(obj, entity)

		# Instantiate all original entities, and apply properties
		# for entityID in self.entities:
		# 	orig = self.entities[entityID][0]
		# 	# if orig.properties['type'] == 'import':
		# 	# 	continue

		# 	instantiatedObject = self.instantiateOriginalEntity(orig)
		# 	orig.objects.append(instantiatedObject)
		# 	self.applyProperties(instantiatedObject, orig)
		# 	self.transformObject(instantiatedObject, orig)
		# 	if len(self.entities[entityID]) > 1:
		# 		for instanceEntity in self.entities[entityID][1:]:
		# 			instantiatedInstance = self.instanceObject(instantiatedObject)
		# 			instanceEntity.objects.append(instantiatedInstance)
		# 			self.transformObject(instantiatedInstance, instanceEntity)


	def instantiateOriginalEntity(self, entity):
		print 'Entity Type:', entity.properties['type']
		if entity.properties['type'] == 'alembic':
			print 'Entity Name:', entity.properties['name']
			return entity.properties['name']

		# Check for function called <type>Create
		typedInstantiationFunction = '{0}Create'.format(entity.properties['type'])
		print 'Typed Instantiation Function:', typedInstantiationFunction

		# If function exists, use it, otherwise createPrimitive
		if hasattr(self, typedInstantiationFunction):
			return getattr(self, typedInstantiationFunction)(entity.properties['name'])
		else:
			return self.createPrimitive(entity.properties['type'], entity.properties['name'])

	def applyProperties(self, obj, entity):
		for k, v in entity.properties['attributes'].iteritems():
			if k == 'name':
				continue
			# Check for function called <type>_set<propertyName>
			typedPropertySetFunction = '{0}_set{1}'.format(entity.properties['type'], k.title())
			untypedPropertySetFunction = typedPropertySetFunction.split('_')[1]
			print 'Untyped Property Function:', untypedPropertySetFunction

			# Cascade through functions from most specific to least specific
			if hasattr(self, typedPropertySetFunction):
				getattr(self, typedPropertySetFunction)(obj, v, entity)
			elif hasattr(self, untypedPropertySetFunction):
				getattr(self, untypedPropertySetFunction)(obj, v, entity)
			else:
				self.setProperty(obj, k, v)

	def performAction(self, entity):
		getattr(self, entity.action)(entity)

	def transformObject(self, obj, entity):
		transform = entity.transform

		typedTransform = 'transform{0}'.format(entity.properties['type'].title())
		if hasattr(self, typedTransform):
			getattr(self, typedTransform)(obj, transform)
		else:
			self.transform(obj, transform)

	def translateEntity(self, entity):
		# keep track of each entity id we use so we can create
		# any we didn't via the graph
		# ex// place nodes create only instances, not original objects
		if entity.entityID not in self.usedEntityIDs:
			self.usedEntityIDs.append(entity.entityID)

		# instances are handled in a separate pass
		if entity.isInstance:
			# self.instances.append(entity.entityID)
			self.instances.append(entity)
		elif entity not in self.createdEntityIDs:
			# add the entityID to the created list and set its instance num to 0
			self.createdEntityIDs.append(entity.entityID)
			self.instanceNum[entity.entityID] = 0

			# translate various entity types
			if isinstance(entity, Entities.Primitive):
				self.translatePrimitive(entity)

			# hide the objects if it should be hidden
			if entity.isHidden:
				objects = self.getObjects(entity)
				if objects:
					self.hideObjects(objects)

	def translatePrimitive(self, entity):
		primitive = None

		# if the primitive has already been created
		# just retrieve it from the objects dict
		if entity.entityID in self.entities.keys():
			primitive = self.getObjects(entity)

		# otherwise we'll need to create it
		# the creation itself is handled by the
		# application specific translators
		if not primitive:
			primitive = self.createPrimitive(entity)
			self.objects[entity.entityID] = primitive

		# if we've found or created the primitive
		# set its properties
		if primitive:
			self.setAttributes(primitive, entity)
			self.setTransform(primitive, entity)
			self.setMaterial(primitive, entity)
			self.showObjects(primitive)
			self.entities[entity.entityID] = entity
		return primitive

	def cleanScene(self, scene, allNodes):
		# collect all the entity IDs for the entire graph
		graphEntityIDs = []
		for n in allNodes:
			# reset the seed number so randoms are consistent
			n.resetRandom()
			if hasattr(n, 'entityID'):
				graphEntityIDs.append(n.entityID)

		# get all the active entities displayed in the current scene
		# ex// primitives, geometry, materials, etc
		self.sceneEntityIDs = []
		for entity in scene.entities:
			if hasattr(entity, 'entityID'):
				self.sceneEntityIDs.append(entity.entityID)

		# hide objects that are no longer in the scene but still in the graph
		# remove objects that are no longer in the node graph
		for entityID in graphEntityIDs:
			# hide the entity if it exists in the graph but not in the current scene
			if entityID in self.entities and entityID not in self.sceneEntityIDs:
				objects = self.getObjects(self.entities[entityID])
				self.hideObjects(objects)

		# delete scene entities and their instances
		# when they ar eno longer in the graph (node has been deleted)
		for entityID, entity in self.entities.items():
			if entityID not in graphEntityIDs:
				objects = self.getObjects(entity)
				print 'Objects:', objects
				objects += self.getInstancedObjects(entity)
				self.deleteObjects(objects)
				del self.entities[entityID] #May need to remove this

		# delete instances that are no longer needed
		# we only do this for the entities in the current scene
		# other entities will remain hidden
		for entityID, entity in self.entities.items():
			if entityID in self.instancedNodes:
				instanceObjects = []
				#collect and delete the unused instance objects
				usedInstances = self.instanceNum[entity.entityID]
				i = usedInstances
				while len(self.instancedNodes[entityID]) > usedInstances:
					instanceObjects += self.instancedNodes[entityID][i]
					del self.instancedNodes[entityID][i] #May need to remove this

				self.deleteObjects(instanceObjects)

	# OBJECTS
	########################################
	def getObjects(self, entity):
		objects = None
		if isinstance(entity, Entities.Primitive):
			objects = self.getPrimitiveObjects(entity)

		return self.checkObjects(objects)

	def checkObjects(self, objects):
		return objects

	# Weaver
	##############################

	def setScene(self, scene):
		print 'Translator set scene'
		self.scene = scene

	def exportOBJ( self, filePath):
		func = '''
			exportClass_List = exporterPlugin.classes
			exportFile "{0}" #noPrompt selectedOnly:on using:exportClass_List[ 15]
			'''.format( filePath)
		## Run Maxscript
		self.executeNativeCommand( func)

	def exportSelectObjects( self, filePath, objectName=None, cleanExport=None):
		if cleanExport == True:
			func = '''
				objectName= getnodebyname "{0}"
				objectPosition= objectName.pos
				objectName.pos= [0, 0, 0]
				'''.format( objectName)
			self.translator.executeNativeCommand( func)

		func = 'saveNodes $ "{0}"'.format( filePath)
		self.translator.executeNativeCommand( func)

		if cleanExport == True:
			func = 'objectName.pos= [objectPosition[1], objectPosition[2], objectPosition[3]]'
			self.translator.executeNativeCommand( func)

	## Selection
	def selectObject( self, *objectName, **kwargs):
		pass

	def getSelectedObjectName( self,):
		pass

	def getObjectByType( self, objectName= None):
		pass

	def clearSelection( self):
		pass

	def isObjectSelected( self):
		pass

	def selectObjectAndChildren( self, objectName):
		pass

	def namespaceExists( self, namespace):
		pass

	def objectExists( self, objectName):
		pass

	def searchSceneForObjects( self, objectName, findAndSelect=False, searchFilter=None, addToSelection=False):
		pass

	def setObjectTransformLock( self, objectName=None, useSelected=False, value=True):
		pass

	def setObjectSelectionLock( self, objectName=None, useSelected=False, value=True):
		pass

	def setObjectDisplayLayer( self, objectName= None, useSelected= False, value= True):
		pass

	def setParentObject( self, parentName, childName):
		pass

	def matchPosition( self, parentName, childName):
		pass

	def matchRotation( self, parentName, childName):
		pass

	def matchMatrix( self, parentName, childName):
		pass

	def storeMatrix( self, objectName):
		pass

	def deleteObject( self, objectName, useSelected=False):
		pass

	def setRenderable( self, objectName= None, useSelected= False, value= None):
		pass

	def deleteEverything(self):
		pass

	def repath( self, sourcePath, destinationPath):
		pass

	def createLayer( self, layerName):
		pass

	def placeObjectsInLayer( self, layerName, *objectList):
		pass

	def changeLayerName( self, oldName, newName, replace= False):
		pass

	def getNewLayers( self):
		pass

	def deleteLayerByName( self, *layerList):
		pass

	def isObjectInLayer( self, layerName, *objectList):
		pass

	def loadPlugin( self, pluginName):
		pass

	def unloadPlugin( self, pluginName):
		pass
