
import SerialNode_Base

class SerialNode_Houdini(SerialNode_Base.SerialNode_Base):

	objectTypes = {
		'geo': 'Transform',
	}
	geometryTypes = {
		'sphere': 'Geometry',
		'circle': 'Geometry',
		'tube': 'Geometry',
	}
	materialTypes = {
		'texture': 'texture',
		'vraymtl': 'VRayNodeBRDFVrayMtl',
		'vrayalsurface': 'VRayNodeBRDFAlSurface',
		'vraymtlsided': 'VRayNodeMtl2Sided',
		'vraycarpaintmtl': 'VRayNodeBRDFCarPaint',
	}
	lightTypes = {
		'vraylightrectshape': 'VRayLightRectShape',
		'vraylightsphereshape': 'VRayLightSphereShape',
		'vraylightdomeshape': 'VRayLightDomeShape',
		'vraylightiesshape': 'VRayLightIESShape',
	}
	inputTypes = {
		'file': 'file',
		'placedtexture': 'place2dTexture',
	}

	def __init__(self, translator, nativeNode=None, filepath=None):
		super(self.__class__, self).__init__(translator, nativeNode=nativeNode, filepath=filepath)
		self.allTypes.update(self.materialTypes)
		self.allTypes.update(self.lightTypes)
		self.allTypes.update(self.inputTypes)
		self.allTypes.update(self.geometryTypes)
		self.allTypes.update(self.objectTypes)

	def __str__(self):
		return self._nativeNode.__str__()

	def serialize(self, serializeConnections=True, connection=None):

		nodeInfo = super(self.__class__, self).serialize()

		# if self.getNativeNode().getType() == 'file' and connection:
		# 	placementInfo = self.getNativeNode().getInputConnectionByProperty('coverage')
		# 	placementSeralized = self.makeNode(placementInfo['target']).serialize(serializeConnections=False)
		# 	nodeInfo.update({
		# 			'placementSettings': placementSeralized,
		# 			'targetProperty': connection['targetProperty'],
		# 		})

		return nodeInfo


	def constructNode(self, nodeInfo):
		print nodeInfo

		# if nodeInfo['isSubstance']:
		# 	maps = nodeInfo['maps'].values()
		# 	materialDictionary = self._translator.createMaterialFromImages(maps, nodeInfo['name'])
		# 	return materialDictionary

		# else:
		# 	nodeType = nodeInfo.get('type')

		# 	if nodeType in self.materialTypes.values():
		# 		nodeName = mel.eval('hyperShadePanelCreate "shader" {}'.format(nodeType))

		# 	elif nodeType in self.inputTypes.values():
		# 		nodeName = mel.eval('hyperShadePanelCreate "2dTexture" {}'.format(nodeType))

		# 	elif nodeType in self.lightTypes.values():
		# 		nodeName = mel.eval('hyperShadePanelCreate "light" {}'.format(nodeType))

		# 	node = self._translator.getNodeByName(nodeName)

		# 	# set name
		# 	node.setName(nodeInfo['name'])

		# 	# set properties
		# 	node.setProperties(nodeInfo['properties'])

		# 	return node
