
import arkInit
arkInit.init()

import arkUtil

class Node_Base(object):

	def __init__(self, nativeNode, translator):
		self._nativeNode = nativeNode
		self.translator = translator

	# Basics
	##################################################
	def name(self, fullpath = False):
		return ''

	def setName(self, name):
		return self

	def getType(self):
		return ''

	# Applicable to path-based node programs such as Houdini
	# Defaults to getName()
	def getPath(self):
		return self.name()

	def createNode(self, nodeType):
		print 'creating:', nodeType
		return None

	def hide(self):
		return self.translator.hideNodes([self])

	def show(self):
		return self.translator.showNodes([self])

	def remove(self, ignoreErrors=True):
		return self.translator.removeNodes([self], ignoreErrors)

	# Properties
	##################################################
	def getPropertyNames(self):
		return []

	def getProperties(self):
		# generic implementation should work for most apps
		propertyNames = self.getPropertyNames()
		data = {}
		for prop in propertyNames:
			propVal = self.getProperty(prop)
			if propVal:
				data[prop] = propVal
		return data

	def getProperty(self, prop):
		return None

	def setProperty(self, prop, value):
		return self

	def setProperties(self, properties, ignoreErrors=True):
		for k,v in properties.iteritems():
			if ignoreErrors:
				try:
					self.setProperty(k,v)
				except:
					pass
			else:
				self.setProperty(k,v)

		return self

	def hasProperty(self, prop):
		return prop in self.getProperties()

	def addProperty(self, prop, type='string'):
		return None

	def propertyType(self, prop):
		return 'string'

	def addVrayProperty(self, prop):
		pass

	def removeVrayProperty(self, prop):
		pass

	# Transform
	##################################################
	# Object or World space transformations. Default worldspace (object=False)
	def getTransformMatrix(self, object=False):
		return []

	def setTransformMatrix(self, transform, object=False):
		return self

	def getPosition(self, object=False):
		return []

	def setPosition(self, x, y, z, object=False):
		return self

	def getRotation(self, object=False):
		return []

	def setRotation(self, x, y, z, object=False):
		return self

	def getScale(self):
		return []

	def setScale(self, scale):
		return self

	# Hierarchy
	##################################################
	def getParent(self):
		return None

	def setParent(self, node):
		return True

	def getChildren(self):
		return []

	def getSubChildren(self):
		return []

	# Animation
	##################################################
	def setKey(self, prop, value, frame):
		return True

	def removeKey(self, prop, frame):
		return True

	def removeAllKeys(self, prop):
		return True

	def getKeys(self, prop):
		return True

	# Expressions
	##################################################
	def getExpression(self, prop):
		return True

	def setExpression(self, prop, expression):
		return True

	def removeExpression(self, prop):
		return True

	# UI
	##################################################
	def getUIPosition(self):
		return {'x': 0, 'y': 0}

	def setUIPosition(self, position):
		return self

	# getNumInputs/getNumOutputs typically don't need to be
	# modified from Translator.py
	def getNumInputs(self):
		return len(self.getInputs())

	def getNumOutputs(self):
		return len(self.getOutputs())

	def getInputs(self):
		return None

	# getInput/getOutput typically don't need to be
	# modified, unless program has faster way of doing this
	# If no inputName specified, return first input
	def getInput(self, inputVal=None):
		inputs = self.getInputs()
		if isinstance(inputVal, str):
			for node in inputs:
				if node.name().lower() == inputVal.lower():
					return self.translator.ensureNode(node)
		elif isinstance(inputVal, int):
			return self.translator.ensureNode(inputs[inputVal])
		else:
			return self.translator.ensureNode(inputs[0])

	def setInput(self, node, inputName=None):
		return True

	def getOutputs(self):
		return None

	def getOutput(self, outputName=None):
		outputs = self.getOutputs()
		if outputName:
			for output in outputs:
				if output.name().lower() == 'outputName':
					return self.translator.ensureNode(output)
		else:
			return self.translator.ensureNode(outputs[0])

	def getInputConnections(self):
		return []

	# getInputConnectionByProperty typically doesn't need to be
	# modified, unless program has faster way of doing this
	def getInputConnectionByProperty(self, portName):
		inputConnections = self.getInputConnections()
		for info in inputConnections:
			if info['sourceProperty'].lower() == portName.lower():
				return info

	# getOutputConnectionsByProperty typically doesn't need to be
	# modified, unless program has faster way of doing this
	def getOutputConnectionsByProperty(self, portName):
		outputConnections = self.getOutputConnections()
		for info in outputConnections:
			if info['sourceProperty'].lower() == portName.lower():
				return info

	# getInputByProperty typically doesn't need to be
	# modified, unless program has faster way of doing this
	def getInputByProperty(self, portName):
		inputConnections = self.getInputConnections()
		for info in inputConnections:
			if info['sourceProperty'].lower() == portName.lower():
				return info['target']

	# getOutputsbyProperty typically doesn't need to be
	# modified, unless program has faster way of doing this
	def getOutputsByProperty(self, portName):
		outputConnections = self.getOutputConnections()
		for info in outputConnections:
			if info['sourceProperty'].lower() == portName.lower():
				return info['targets']

	# Materials
	##################################################
	def getMaterial(self):
		return None

	def setMaterial(self, material):
		print 'material: ' + str(material)
		return self

	def setDisplacement(self, displacementMap):
		print 'displacementMap: ' + str(displacementMap)
		pass

	# Helpers
	##################################################
	def getSafeName(self, name=None):
		if not name:
			name = self.name()

		return arkUtil.makeWebSafe(name)

	def nativeNode(self):
		return self._nativeNode
