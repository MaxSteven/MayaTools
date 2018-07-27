
import json

import arkMath

class SerialNode_Base(object):

	materialTypes = {}
	lightTypes = {}
	inputTypes = {}
	deserialized = None

	def __init__(self, translator, nativeNode=None, filepath=None):
		self._translator = translator

		if nativeNode:
			self._nativeNode = nativeNode

		if filepath:
			self.deserialized = self.deserialize(filepath)

		self.allTypes = {}

	def __str__(self):
		return self._nativeNode.__str__()

	def makeNode(self, inputNode):
		return self.__class__(self._translator, inputNode)

	def getDeserialized(self):
		return self.deserialized

	def getNativeNode(self):
		return self._nativeNode

	def isValidInputType(self, nodeType):
		return nodeType in self.inputTypes

	def isValidNodeType(self, nodeType):
		return nodeType in self.allTypes.keys()

	def getNodeType(self, nodeType):
		return self.allTypes.get(nodeType)

	def readSerialized(self, filepath):
		'''
		helper for deserialize
		'''
		nodeInfo = {}
		with open(filepath) as f:
			nodeInfo = json.load(f)

		return nodeInfo

	def constructNode(self, nodeInfo):
		'''
		override in subclass
		'''
		return None

	def deserialize(self, filepath):
		nodeInfo = self.readSerialized(filepath)

		# deserialize this node
		node = self.constructNode(nodeInfo)

		# deserialize inputs
		inputNodes = {}
		for sourceProperty, inputInfo in nodeInfo['inputs'].iteritems():
			targetProperty = inputInfo.get('targetProperty')
			if not targetProperty:
				raise Exception('Input {} has no targetProperty'.format(inputInfo))

			# recursive call
			inputNode = self.constructNode(inputInfo)

			# connect nodes
			self._translator.connectProperty(inputNode, targetProperty, node, sourceProperty)

		return node

	def serialize(self, serializeConnections=True, connection=None):
		'''
		subclass should call this method then do whatever program-specific info they need
		'''
		print 'self._translator',self._translator
		print 'self._nativeNode',self._nativeNode

		node = self._nativeNode
		print node

		nodeType = node.getType()
		if not self.isValidNodeType(nodeType):
			print 'Node type not supported:', nodeType
			print 'Valid node types are ', self.allTypes.keys()
			return None

		nodeInfo = {
			'name': node.getSafeName(),
			'type': self.getNodeType(nodeType),
			'properties': {},
			'isSubstance': False,
		}

		supportedAttributeTypes = [bool, str, list, tuple, int, float, arkMath.Vec]
		props = node.getPropertyNames()
		for propName in props:
			if '.' in propName:
				print 'Skipping:', propName
				continue

			if propName == 'boundingBox':
				print 'Cannot serialize bounding box',
				continue

			val = node.getProperty(propName)

			if type(val) in supportedAttributeTypes:
				nodeInfo['properties'][propName] = val
			else:
				print 'Invalid type:', type(val), 'skipping:', propName, val

		if serializeConnections:
			nodeInfo['inputs'] = {}
			inputConnections = node.getInputConnections()
			for connection in inputConnections:
				#print 'connection:', connection
				inputNode = connection['target']
				inputName = connection['sourceProperty']

				if not inputNode:
					continue

				inputType = inputNode.getType()
				if not self.isValidInputType(inputType):
					print 'Input type not supported:', inputType
					continue

				inputSerialNode = self.makeNode(inputNode)
				inputSeralized = inputSerialNode.serialize(connection=connection)
				nodeInfo['inputs'][inputName] = inputSeralized

		return nodeInfo
