import Node_Base

# Vendor modules
import pymel.core as pymel
# import maya.mel as mel
import maya.cmds as mc

# Our modules
import arkMath
import arkUtil

class Node_Maya(Node_Base.Node_Base):

	typeRemap = {
		'mesh': 'geometry'
	}

	def __init__(self, nativeNode, translator):
		try:
			# Passing a PyMel node and using an in-built function exists
			if not nativeNode.exists():
				raise Exception('Node doesn\'t exist')
		except:
			raise Exception ('Not a PyMel Node!')

		self._nativeNode = nativeNode
		self.translator = translator

	def __str__(self):
		return 'Node_Maya(' + self.name() + ')'

	# Basics
	##################################################
	def name(self, fullpath=False):
		if fullpath:
			return str(self.nativeNode().longName())

		return str(self.nativeNode().name())

	def setName(self, name):
		name = self.getSafeName(name)
		self.nativeNode().rename(name)
		return self

	def getType(self):
		nodeType = self.nativeNode().nodeType()

		if nodeType in self.typeRemap.keys():
			return self.typeRemap[nodeType]

		# trash any non alphabet characters
		return arkUtil.replaceAll(
			nodeType.lower(),
			'[^a-z]', '')

	# Properties
	##################################################
	def getPropertyNames(self):
		# Attributes in Maya, returned as List
		nativeNode = self.nativeNode()
		return pymel.listAttr(nativeNode)

	def getProperty(self, prop):
		if not self.hasProperty(prop):
			raise Exception('Node %s does not have property %s to get' % (self.name(), prop))
		nativeNode = self.nativeNode()
		try:
			raw = nativeNode.getAttr(prop)
		except:
			return

		# try to handle variable type conversions

		# have to try catch the conversions as they fail
		# with an error otherwise
		try:
			floatString = str(float(raw))
		except:
			floatString = None
		try:
			intString = str(int(raw))
		except:
			intString = None

		# handle list, tupple, etc inputs as vec
		try:
			raw[:0]
		except TypeError:
			# not a list
			pass
		# try to make it a vec
		else:
			try:
				vec = arkMath.Vec(raw)
			except:
				vec = None

		# handle strings /w commas as vecs
		try:
			if ',' in raw:
				vec = arkMath.Vec(raw)
			else:
				vec = None
		except:
			vec = None

		# float
		if vec:
			return vec
		elif raw is not None and floatString == raw:
			return float(raw)
		# int
		elif raw is not None and intString == raw:
			return int(raw)
		elif isinstance(raw, unicode):
			return str(raw)
		# everything else (for now)
		else:
			return raw

	def setProperty(self, prop, value):
		nativeNode = self.nativeNode()
		nativeNode.setAttr(prop, value)
		return self

	def hasProperty(self, prop):
		propList = self.getPropertyNames()
		return prop in propList

# Currently Only Handles String, Float and Int
	def addProperty(self, prop, attrType='string'):
		nativeNode = self.nativeNode()
		if self.hasProperty(prop):
			raise Exception('Property already exists')

		pymel.addAttr(nativeNode, ln=prop, dt=attrType)

	def propertyType(self, prop):
		if not self.hasProperty(prop):
			return None

		attr = self.nativeNode().getProperty(prop)
		return arkUtil.varType(attr)

	def addVrayProperty(self, prop):
		mc.vray('addAttributesFromGroup', self.name(), prop, 1)

	def removeVrayProperty(self, prop):
		mc.vray('addAttributesFromGroup', self.name(), prop, 0)

	# Transform
	##################################################
	# Object or World space transformations. Default worldspace (object=False)
	def getTransformMatrix(self, object=False):
		if pymel.nodeType(self.name()) != 'transform':
			raise Exception('NodeType is not transform\n')
		nativeNode = self.nativeNode()
		matrix = pymel.xform(nativeNode, query=True, objectSpace=object, worldSpace=not object, matrix=True)
		print matrix
		return arkMath.Mat44(matrix)

	def setTransformMatrix(self, transform, object=False):
		# transform could be list or matrix
		matrix = arkMath.ensureMatrix(transform)
		matList = matrix.getList()
		if pymel.nodeType(self.name()) != 'transform':
			raise Exception('NodeType is not transform\n')
		nativeNode = self.nativeNode()
		pymel.xform(nativeNode, objectSpace=object, worldSpace=not object, matrix=matList)

	def getPosition(self, object=False):
		if pymel.nodeType(self.name()) != 'transform':
			raise Exception('NodeType is not transform\n')
		if object:
			space = 'object'
		else:
			space = 'world'
		nativeNode = self.nativeNode()
		translation = nativeNode.getTranslation(space=space)
		return arkMath.Vec(translation.x, translation.y, translation.z)

	def setPosition(self, x, y=None, z=None, object=False):
		if pymel.nodeType(self.name()) != 'transform':
			raise Exception('NodeType is not transform\n')
		if object:
			space = 'object'
		else:
			space = 'world'
		vec = arkMath.ensureVector(x, y, z)
		vec3 = [vec.x, vec.y, vec.z]
		nativeNode = self.nativeNode()
		nativeNode.setTranslation(vec3, space=space)

	def getRotation(self, object=False):
		if pymel.nodeType(self.name()) != 'transform':
			raise Exception('NodeType is not transform\n')
		if object:
			space = 'object'
		else:
			space = 'world'
		nativeNode = self.nativeNode()
		rotation = nativeNode.getRotation(space=space).asVector()
		return arkMath.Vec(rotation.x, rotation.y, rotation.z)

	def setRotation(self, x, y=None, z=None, object=False):
		if pymel.nodeType(self.name()) != 'transform':
			raise Exception('NodeType is not transform\n')
		if object:
			space = 'object'
		else:
			space = 'world'
		vec = arkMath.ensureVector(x, y, z)
		vec3 = [vec.x, vec.y, vec.z]
		nativeNode = self.nativeNode()
		nativeNode.setRotation(vec3, space=space)

	def getScale(self):
		if pymel.nodeType(self.name()) != 'transform':
			raise Exception('NodeType is not transform\n')
		nativeNode = self.nativeNode()
		scale = nativeNode.getScale()
		return arkMath.Vec(scale)

	def setScale(self, x, y=None, z=None):
		if pymel.nodeType(self.name()) != 'transform':
			raise Exception('NodeType is not transform\n')
		vec = arkMath.ensureVector(x, y, z)
		vec3 = [vec.x, vec.y, vec.z]
		nativeNode = self.nativeNode()
		nativeNode.setScale(vec3)

	# Hierarchy
	##################################################
	def getParent(self):
		nativeNode = self.nativeNode()
		parent = pymel.listRelatives(nativeNode, parent=True)
		if not len(parent):
			return None
		return self.translator.ensureNode(parent[0])

	def setParent(self, node):
		nativeNode = self.nativeNode()
		pymel.parent(nativeNode, node)

	def getChildren(self):
		nativeNode = self.nativeNode()
		return self.translator.ensureNodes(pymel.listRelatives(nativeNode, children=True))

	# Animation
	##################################################
	def setKey(self, prop, value, frame):
		raise Exception('Not yet implemented')

	def removeKey(self, prop, frame):
		raise Exception('Not yet implemented')

	def removeAllKeys(self, prop):
		raise Exception('Not yet implemented')

	def getKeys(self, prop):
		raise Exception('Not yet implemented')

	# Expressions
	##################################################
	# TODO: getExpression, removeExpression
	def getExpression(self, prop):
		if not self.hasProperty(prop):
			raise Exception('Node does not have property')
		# Expressions are strings
		# Parse expression from prop and expression
		raise Exception('Not implemented yet')

	def setExpression(self, prop, expression):
		if not self.hasProperty(prop):
			raise Exception('Node does not have property')
		nativeNode = self.nativeNode()
		string = '%s.%s = %s' % (nativeNode.name(), prop, expression)
		pymel.expression(string=string)

	def removeExpression(self, prop):
		# nativeNode = self.nativeNode()
		raise Exception('Not implemented yet')

	# UI
	##################################################
	# Note: Using getInput/getOutput inherited from base class

	def getInputs(self):
		nativeNode = self.nativeNode()
		connections = pymel.listConnections(nativeNode, destination=False, source=True)
		return connections

	def setInput(self, node, inputName):
		raise Exception('Not implemented yet')

	def getOutputs(self):
		nativeNode = self.nativeNode()
		connections = pymel.listConnections(nativeNode, destination=True, source=False)
		return connections

	def getInputConnections(self):
		connectionInfos = []
		connections = pymel.listConnections(self.name(),
			connections=True,
			destination=False,
			source=True)

		for connectionInfo in connections:
			sourceProperty = connectionInfo[0]
			sourceParts = sourceProperty.split('.')

			targetProperty = pymel.connectionInfo(sourceProperty, sourceFromDestination=True)
			targetParts = targetProperty.split('.')

			connectionInfos.append({
					'sourceProperty': str(sourceParts[1]),
					'target': self.translator.getNodeByName(targetParts[0]),
					'targetProperty': str(targetParts[1]),
				})

		return connectionInfos

	def getOutputConnections(self):
		connectionInfos = []
		connections = pymel.listConnections(self.name(),
			connections=True,
			destination=True,
			source=False)

		for connectionInfo in connections:
			sourceProperty = connectionInfo[0]
			sourceParts = sourceProperty.split('.')

			targets = pymel.connectionInfo(sourceProperty, destinationFromSource=True)
			targetNodes = [self.translator.getNodeByName(d.split('.')[0]) for d in targets]
			targetPorts = [str(d.split('.')[1]) for d in targets]

			connectionInfos.append({
					'sourceProperty': str(sourceParts[1]),
					'targets': targetNodes,
					'targetProperties': targetPorts,
				})

		return connectionInfos

	# Materials
	##################################################
	# TODO: getmaterial, setMaterial (if object, using .material or sets)
	def getMaterial(self):
		'''
		gets self's material
		'''
		# if self.getType() != 'geometry':
		# 	return

		child = pymel.listRelatives(self.name(), children=True, shapes=True)[0]
		if child:
			shaderNode = pymel.connectionInfo(child + '.instObjGroups[0]', dfs=True)
			if shaderNode:
				materialNode = shaderNode[0].split('.')[0]
				if materialNode:
					material = pymel.connectionInfo(materialNode + '.surfaceShader', sfd=True)
					return self.translator.getMaterialByName(material.split('.')[0])
				else:
					raise Exception('Material Not Found')
					return
			else:
				raise Exception('Shader Not Found')
				return
		else:
			raise Exception('Shape Not Found')
			return

		# raise Exception('Not implemented yet')

	def setMaterial(self, material):
		'''
		assigns material to self
		'''
		# if self.getType() != 'geometry':
		# 	return

		children = pymel.listRelatives(self.name(), allDescendents=True, shapes=True)
		if children:
			for c in children:
				materialNodePlug = pymel.connectionInfo(material.name()+'.outColor', dfs=True)[0]
				materialNode = materialNodePlug.split('.')[0]
				pymel.sets(materialNode, edit=True, forceElement=c)
				meshTransform = pymel.listRelatives(c, parent = True)[0]
				if pymel.attributeQuery('materialName', node = meshTransform, exists = True):
					pymel.setAttr(meshTransform+'.materialName', materialNode)

		else:
			return

	def setDisplacement(self, displacementMap):
		children = pymel.listRelatives(self.name(), allDescendents = True, shapes = True)
		if children:
			for c in children:
				meshTransform = pymel.listRelatives(c, parent = True)[0]
				pymel.sets(displacementMap.name(), edit=True, forceElement=meshTransform)

		# raise Exception('Not implemented yet')


	# Application specific
	##################################################
