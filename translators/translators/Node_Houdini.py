import Node_Base

# Vendor modules
import hou

# Our modules
import arkMath
import arkUtil

class Node_Houdini(Node_Base.Node_Base):

	typeRemap = {
		'cam': 'camera'
	}

	# Basics
	##################################################
	def name(self, fullpath = False):
		if fullpath:
			return self.nativeNode().path()

		return self.nativeNode().name()

	def setName(self, name):
		name = self.getSafeName(name)
		self.nativeNode().setName(name, unique_name=True)
		return self

	def getType(self):
		# .type() returns a NodeType object, get name()
		nodeType = self.nativeNode().type().name()

		if nodeType in self.typeRemap.keys():
			return self.typeRemap[nodeType]

		# trash any non alphabet characters
		return arkUtil.replaceAll(
			nodeType.lower(),
			'[^a-z]', '')

	# Return absolute path of node in network, starting with '/' root
	# path cannot be lowered, as Houdini paths are case sensitive
	def getPath(self):
		return self.nativeNode().path()

	def createNode(self, nodeType):
		newNode = self.nativeNode().createNode(nodeType)
		return self.translator.ensureNode(newNode)


	# Properties
	##################################################
	def getPropertyNames(self):
		# Parameters in Houdin, returned as a tuple
		nativeNode = self.nativeNode()
		parms = nativeNode.parms()
		names = []
		for parm in parms:
			names.append(parm.name())
		return names

	def getProperty(self, prop):
		if not self.hasProperty(prop):
			raise Exception('Node %s does not have property %s to get' % (self.name(), prop))
		nativeNode = self.nativeNode()
		raw = nativeNode.evalParm(prop)
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

		# float
		if floatString == raw:
			return float(raw)
		# int
		elif intString == raw:
			return int(raw)
		# everything else (for now)
		else:
			return raw

	# def setProperty(self, prop, value):
	# 	nativeNode = self.nativeNode()
	# 	parmDict = {
	# 		prop : value,
	# 	}
	# 	nativeNode.setParms(parmDict)
	# 	return self

	def setProperty(self, prop, value):
		self.nativeNode().parm(prop).set(value)
		return self

	def hasProperty(self, prop):
		nativeNode = self.nativeNode()
		if nativeNode.parm(prop):
			return True
		else:
			return False

# Currently Only Handles String, Float and Int
	def addProperty(self, prop, attrType='string'):
		nativeNode = self.nativeNode()
		if self.hasProperty(prop):
			raise Exception('Property already exists')

		attrGroup = nativeNode.parmTemplateGroup()
		if attrType == 'int':
			userParam = hou.IntParmTemplate(prop, prop, 1)

		elif attrType == 'float':
			userParam = hou.FloatParmTemplate(prop, prop, 1)

		if attrType == 'string':
			userParam = hou.StringParmTemplate(prop, prop, 1)

		attrGroup.append(userParam)
		nativeNode.setParmTemplateGroup(attrGroup)

	def propertyType(self, prop):
		if not self.hasProperty(prop):
			return None
		attr = self.nativeNode().parm(prop).parmTemplate().dataType()
		return arkUtil.varType(attr)

	# Transform
	##################################################
	# Object or World space transformations. Default worldspace (object=False)
	def getTransformMatrix(self, object=False):
		if self.getCategory() != 'object':
			raise Exception('Cannot get TransformMatrix on NodeType', self.getCategory())
		nativeNode = self.nativeNode()
		# object space transform matrix
		if object:
			matrix = nativeNode.localTransform()
		# world space transform matrix
		else:
			matrix = nativeNode.worldTransform()
		# convert hou.Matrix4 type into something arkMath can parse
		matrix = list(matrix.asTuple())
		return arkMath.Mat44(matrix)

	def setTransformMatrix(self, transform, object=False):
		if self.getCategory() != 'object':
			raise Exception('Cannot set TransformMatrix on NodeType', self.getCategory())
		# transform could be list or matrix
		matrix = arkMath.ensureMatrix(transform)
		matList = matrix.getList()
		houMat = hou.Matrix4(matList)
		nativeNode = self.nativeNode()
		# Local space
		if object:
			raise Exception('Not implemented yet')
		# World space
		else:
			nativeNode.setWorldTransform(houMat)

	# Assumes Transform Matrix created with default order 'srt' (scale, rotate, translation)
	def getPosition(self, object=False):
		matrix = self.getTransformMatrix(object)
		houMat = hou.Matrix4(matrix.getList())
		houVec = houMat.extractTranslates()
		x = houVec[0]
		y = houVec[1]
		z = houVec[2]
		return arkMath.Vec(x, y, z)

	def setPosition(self, x, y=None, z=None, object=False):
		vec = arkMath.ensureVector(x, y, z)
		translate = (vec.x, vec.y, vec.z)
		# Get existing transform matrix for rotation, scale
		scale = self.getScale()
		scale = (scale.x, scale.y, scale.z)
		rot = self.getRotation()
		rot = (rot.x, rot.y, rot.z)
		# Parse values for buildTransform
		values = {
			'translate': translate,
			'rotate': rot,
			'scale': scale,
		}
		matrix = hou.hmath.buildTransform(values)
		matrix = list(matrix.asTuple())
		matrix = arkMath.ensureMatrix(matrix)
		if object:
			raise Exception('Not implemented yet')
		else:
			self.setTransformMatrix(matrix, object)

	# Assumes Transform Matrix created with default order 'srt' (scale, rotate, translation)
	def getRotation(self, object=False):
		matrix = self.getTransformMatrix(object)
		houMat = hou.Matrix4(matrix.getList())
		houVec = houMat.extractRotates()
		x = houVec[0]
		y = houVec[1]
		z = houVec[2]
		return arkMath.Vec(x, y, z)

	# Assumes Transform Matrix created with default order 'srt' (scale, rotate, translation)
	def setRotation(self, x, y=None, z=None, object=False):
		vec = arkMath.ensureVector(x, y, z)
		rot = (vec.x, vec.y, vec.z)
		# Get existing transform matrix for translate, sacle
		scale = self.getScale()
		scale = (scale.x, scale.y, scale.z)
		translate = self.getPosition()
		translate = (translate.x, translate.y, translate.z)
		# Parse values for buildTransform
		values = {
			'translate': translate,
			'rotate': rot,
			'scale': scale,
		}
		matrix = hou.hmath.buildTransform(values)
		matrix = list(matrix.asTuple())
		matrix = arkMath.ensureMatrix(matrix)
		if object:
			raise Exception('Not implemented yet')
		else:
			self.setTransformMatrix(matrix, object)

	# Assumes Transform Matrix created with default order 'srt' (scale, rotate, translation)
	def getScale(self):
		matrix = self.getTransformMatrix(object)
		houMat = hou.Matrix4(matrix.getList())
		houVec = houMat.extractScales()
		x = houVec[0]
		y = houVec[1]
		z = houVec[2]
		return arkMath.Vec(x, y, z)

	# Assumes Transform Matrix created with default order 'srt' (scale, rotate, translation)
	def setScale(self, x, y=None, z=None):
		vec = arkMath.ensureVector(x, y, z)
		scale = (vec.x, vec.y, vec.z)
		# Get existing transform matrix for translate, rotate
		rot = self.getRotation()
		rot = (rot.x, rot.y, rot.z)
		translate = self.getPosition()
		translate = (translate.x, translate.y, translate.z)
		# Parse values for buildTransform
		values = {
			'translate': translate,
			'rotate': rot,
			'scale': scale,
		}
		matrix = hou.hmath.buildTransform(values)
		matrix = list(matrix.asTuple())
		matrix = arkMath.ensureMatrix(matrix)
		if object:
			raise Exception('Not implemented yet')
		else:
			self.setTransformMatrix(matrix, object)

	# Hierarchy
	##################################################

	def getParent(self):
		return self.translator.ensureNodes(self.getInputs())

	def setParent(self, node):
		self.setInput(node)

	def getChildren(self):
		return self.translator.ensureNodes(self.getOutputs())

	def getSubChildren(self):
		nodes = self.nativeNode().allSubChildren()
		return self.translator.ensureNodes(nodes)

	# Animation
	##################################################
	def setKey(self, prop, value, frame):
		raise Exception('Not yet implemented')

	def removeKey(self, prop, frame):
		raise Exception('Not yet implemented')

	def removeAllKeys(self, prop):
		self.nativeNode().parm(prop).deleteAllKeyframes()
		return self

	def getKeys(self, prop):
		raise Exception('Not yet implemented')

	# Expressions
	##################################################
	def getExpression(self, prop):
		if not self.hasProperty(prop):
			raise Exception('Node does not have property: ' + prop)
		nativeNode = self.nativeNode()
		parm = nativeNode.parm(prop)
		try:
			expression = parm.expression()
		except:
			raise Exception('Property does not have expression: ' + prop)
		return expression

	def setExpression(self, prop, expression):
		if not self.hasProperty(prop):
			raise Exception('Node does not have property: ' + prop)
		nativeNode = self.nativeNode()
		parm = nativeNode.parm(prop)
		parm.setExpression(expression)

	# Remove expression and rever to defaults
	def removeExpression(self, prop):
		nativeNode = self.nativeNode()
		parm = nativeNode.parm(prop)
		parm.revertToDefaults()

	# UI
	##################################################
	def getUIPosition(self):
		nativeNode = self.nativeNode()
		xPos = nativeNode.position()[0]
		yPos = nativeNode.position()[1]

		return {'x': xPos, 'y': yPos}

	def setUIPosition(self, x=None, y=None):
		nativeNode = self.nativeNode()
		if not x:
			x = self.getUIPosition['x']
		if not y:
			y = self.getUIPosition['y']
		nativeNode.setPosition(hou.Vector2(x, y))
		return self

	def getInputs(self):
		nativeNode = self.nativeNode()
		inputs = nativeNode.inputs()
		inputs = self.translator.ensureNodes(inputs)
		return list(inputs)

	# If inputName specified, search for corresponding index
	# Else, set first input
	def setInput(self, node, inputName=None, inputNumber=0):
		# Get index from inputName
		inputs = self.getInputs()

		if inputName:
			for i, item in enumerate(inputs):
				if item.name() == inputName:
					inputNumber = i

		nativeNode = self.nativeNode()
		nativeNode.setInput(inputNumber, node.nativeNode())

		return self

	def getOutputs(self):
		nativeNode = self.nativeNode()
		outputs = nativeNode.outputs()
		outputs = self.translator.ensureNodes(outputs)
		return list(outputs)

	# Materials
	##################################################
	# TODO: getmaterial, setMaterial
	def getMaterial(self):
		if self.getType() == 'material':
			return self.getProperty('shop_materialpath1')

		if self.getType() == 'geo':
			return self.getProperty('shop_materialpath')

		outputs = self.nativeNode().outputs()
		for out in outputs:
			if out.type().name() == 'material':
				return self.translator.ensureNode(out).getProperty('shop_materialpath1')

	def setMaterial(self, material):
		if self.getType() == 'material':
			self.setProperty('shop_materialpath1', material)
			return self

		if self.getType() == 'geo':
			self.setProperty('shop_materialpath', material)
			return self

		path = self.nativeNode().path()
		parentPath = path.rpartition('/')[0]

		matNode = self.translator.ensureNode(hou.node(parentPath).createNode('material'))
		matNode.setProperty('shop_materialpath1', material)

		outputs = self.nativeNode().outputs()

		connections = self.nativeNode().outputConnections()
		inIndexes = []

		for con in connections:
			outIndex = con.outputIndex()
			inIndexes.append(con.inputIndex())

		matNode.nativeNode().setInput(0, self.nativeNode(), outIndex)
		i = 0
		for out in outputs:
			out.setInput(inIndexes[i], None)
			out.setInput(inIndexes[i], matNode.nativeNode(), 0)
			i += 1

		return self.translator.ensureNode(matNode)

	def setDisplacement(self, displacementMap):
		raise Exception('Not implemented yet')
		pass

	# Application specific
	##################################################

	# Get NodeType's category, such as 'sop', 'dop', 'object'
	def getCategory(self):
		nativeNode = self.nativeNode()
		return nativeNode.type().category().name().lower()