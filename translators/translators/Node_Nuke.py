
import Node_Base

import arkMath
import arkUtil

import nuke

class Node_Nuke(Node_Base.Node_Base):

	# Basics
	##################################################
	def name(self, fullpath = False):
		return self.nativeNode().name()

	def setName(self, name):
		name = self.getSafeName(name)
		self.nativeNode().setName(name)
		return self

	def getType(self):
		nativeNode = self.nativeNode()
		nodeType = nativeNode.Class()
		# trash any non alphabet characters
		# this gets around nuke's dumb node names
		# like Camera2 or ReadGeo2
		return arkUtil.replaceAll(
			nodeType.lower(),
			'[^a-z]', '')

	# Properties
	##################################################
	def getPropertyNames(self):
		nativeNode = self.nativeNode()
		return nativeNode.knobs().keys()

	def getProperty(self, prop):
		if not self.hasProperty(prop):
			raise Exception('Node %s does not have property %s to get' % (self.name(), prop))
		nativeNode = self.nativeNode()
		# fix: this doesn't work with animated properties
		# figure out how we want to handle that
		raw = nativeNode[prop].toScript()
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

		# special case for default(sRGB) etc
		if prop == 'colorspace':
			parts = raw.split('(')
			if len(parts) > 1:
				raw = parts[1][:-1]

		# float
		if floatString == raw:
			return float(raw)
		# int
		elif intString == raw:
			return int(raw)
		# bool
		elif raw.lower() in ['true', 'false']:
			return bool(raw.lower() == 'true')
		# everything else (for now)
		else:
			return raw

	def setProperty(self, prop, value):
		nativeNode = self.nativeNode()
		nativeNode[prop].fromScript(str(value))
		return self

	def hasProperty(self, prop):
		return prop in self.nativeNode().knobs()

	def getChannels(self):
		nativeNode = self.nativeNode()
		return nativeNode.channels()

# Currently Only Handles String, Float and Int
	def addProperty(self, prop, attrType='string'):
		nativeNode = self.nativeNode()
		if self.hasProperty(prop):
			raise Exception('Property already exists')

		if attrType == 'int':
			userKnob = nuke.Int_Knob(prop, prop)

		elif attrType == 'float':
			userKnob = nuke.Double_Knob(prop, prop)

		if attrType == 'string':
			userKnob = nuke.String_Knob(prop, prop)

		nativeNode.addKnob(userKnob)

	def propertyType(self, prop):
		if not self.hasProperty(prop):
			return None

		knob = self.nativeNode()[prop]
		return arkUtil.varType(knob)

	# Transform
	##################################################
	# Object or World space transformations. Default worldspace (object=False)
	# fix: implement world or object space
	def getTransformMatrix(self, object=False):
		if self.propertyType('world_matrix') != 'IArray_Knob':
			raise Exception('Invalid property: world_matrix')

		nativeNode = self.nativeNode()
		return arkMath.Mat44(nativeNode['world_matrix'].getValue())

	def setTransformMatrix(self, transform, object=False):
		if self.propertyType('world_matrix') != 'IArray_Knob':
			raise Exception('Invalid property: world_matrix')

		transform = arkMath.ensureMatrix(transform)
		self.setProperty('world_matrix', transform.mat)

	def getPosition(self, object=False):
		if self.propertyType('translate') != 'XYZ_Knob':
			raise Exception('Invalid property: translate')

		nativeNode = self.nativeNode()
		return arkMath.Vec(nativeNode['translate'].getValue())

	def setPosition(self, x, y=None, z=None, object=False):
		if self.propertyType('translate') != 'XYZ_Knob':
			raise Exception('Invalid property: translate')

		vec = arkMath.ensureVector(x, y, z)
		self.setProperty('translate', [vec.x, vec.y, vec.z])

	def getRotation(self, object=False):
		nativeNode = self.nativeNode()
		return arkMath.Vec(nativeNode['rotate'].getValue())

	def setRotation(self, x, y=None, z=None, object=False):
		if self.propertyType('rotate') != 'XYZ_Knob':
			raise Exception('Invalid property: rotate')

		vec = arkMath.ensureVector(x, y, z)
		self.setProperty('rotate', [vec.x, vec.y, vec.z])

	def getScale(self):
		nativeNode = self.nativeNode()
		return arkMath.Vec(nativeNode['scaling'].getValue())

	def setScale(self, x, y=None, z=None):
		if self.propertyType('scaling') != 'XYZ_Knob':
			raise Exception('Invalid property: scaling')

		vec = arkMath.ensureVector(x, y, z)
		self.setProperty('scaling', [vec.x, vec.y, vec.z])

	# Hierarchy
	##################################################
	def getParent(self):
		self.getInput()

	def setParent(self, node):
		self.setInput(node)

	def getChildren(self):
		nativeNode = self.nativeNode()
		return self.translator.ensureNodes(nativeNode.dependent())

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
	def getExpression(self, prop, expression):
		nativeNode = self.nativeNode()
		value = nativeNode[prop].toScript()
		# expressions start with braces or brackets
		# (tcl or python)
		if value[0] == '{' or value[0] == '[':
			return value

		return None

	def setExpression(self, prop, expression):
		nativeNode = self.nativeNode()
		nativeNode[prop].setExpression(expression)

	def removeExpression(self, prop):
		nativeNode = self.nativeNode()
		nativeNode[prop].clearAnimated()

	# UI
	##################################################
	def getUIPosition(self):
		nativeNode = self.nativeNode()
		xPos = nativeNode['xpos'].getValue()
		xPos = int(xPos + nativeNode.screenWidth() * .5)

		yPos = nativeNode['ypos'].getValue()
		yPos = int(yPos + nativeNode.screenWidth() * .5)

		return {'x': xPos, 'y': yPos}

	def setUIPosition(self, x=None, y=None):
		nativeNode = self.nativeNode()
		if x is not None:
			x = int(x - nativeNode.screenWidth() * .5)
			nativeNode['xpos'].setValue(x)
		if y is not None:
			y = int(y - nativeNode.screenHeight() * .5)
			nativeNode['ypos'].setValue(y)
		return self

	def getInputs(self):
		nativeNode = self.nativeNode()
		numInputs = nativeNode.inputs()
		nodes = []
		for i in range(0, numInputs):
			nodes.append(nativeNode.input(i))
		return nodes

	def setInput(self, node, inputName=None, inputNumber=0):
		nativeNode = self.nativeNode()
		inputs = self.getInputs()
		if inputName:
			for i, item in enumerate(inputs):
				if item.name() == inputName:
					inputNumber = i
		nativeNode.setInput(inputNumber, node.nativeNode())

	# TODO: getOutputs to return list of outputs
	# Can nuke.Node do this? Just maxOutputs
	def getOutputs(self):
		raise Exception('Not implemented yet')

	# Materials
	##################################################
	def getMaterial(self):
		return None

	def setMaterial(self, material):
		return True

	def setDisplacement(self, displacementMap):
		pass

	# Application specific
	##################################################
	def width(self):
		return self.nativeNode().width()

	def height(self):
		return self.nativeNode().height()
