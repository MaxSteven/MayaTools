import json
import arkMath
import translators
import pymel.core as pymel
import maya.mel as mel

translator = translators.getCurrent()

matFile = 'c:/trash/mat.material'

# Export
##################################################

materialTypes = {
	'vrayalsurface': 'VRayAlSurface',
	'vraymtl': 'VRayMtl',
	'vrayalsurface': 'VRayAlSurface',
	'vraymtlsided': 'VRayMtl2Sided',
	'vraycarpaintmtl': 'VRayCarPaintMtl',
	'vraymtl': 'VRayMtl',
}
inputTypes = {
	'file': 'file',
	'placedtexture': 'place2dTexture',
}

allNodes = materialTypes.copy()
allNodes.update(inputTypes)


def serializeNode(node=None, serializeConnections=True):

	nodeType = node.getType()
	if nodeType not in allNodes:
		print 'Node type not supported:', nodeType
		return None

	nodeInfo = {
		'name': node.getSafeName(),
		'type': allNodes[nodeType],
		'properties': {},
		'isSubstance': False,
	}

	supportedAttributeTypes = [bool, str, list, tuple, int, float, arkMath.Vec]
	props = node.getPropertyNames()
	for propName in props:
		if '.' in propName:
			print 'Skipping:', propName
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
			print 'connection:', connection
			inputNode = connection['target']
			inputName = connection['sourceProperty']

			if not inputNode:
				continue

			inputType = inputNode.getType()
			if inputType not in inputTypes:
				print 'Input type not supported:', inputType
				continue

			if inputType == 'file':
				print inputName, ':', inputNode.getProperty('fileTextureName')
				print 'props:', inputNode.getPropertyNames()
				inputSeralized = serializeNode(inputNode,
					serializeConnections=False)
				print '\nserialized', inputSeralized
				# get the place2D node and serialize that
				placementInfo = inputNode.getInputConnectionByProperty('coverage')
				placementSeralized = serializeNode(placementInfo['target'],
					serializeConnections=False)
				print '\nplacementSeralized', placementSeralized
				additionalInfo = {
						'targetProperty': connection['targetProperty'],
						'placementSettings': placementSeralized,
					}
				inputSeralized.update(additionalInfo)
				nodeInfo['inputs'][inputName] = inputSeralized

	return nodeInfo




def exportMaterial(material=None):
	# fix: remove this eventually
	if not material:
		selection = translator.getSelectedNode()
		material = selection.getMaterial()

	# crappy check, should create an attribute on substance
	# material that flags it as substance
	nodeType = material.getType()
	if nodeType == 'vraymtl' and \
		material.getInputByProperty('refractionIOR') and \
		'remapior' in material.getInputByProperty('refractionIOR').name().lower():
		print '\n\nExporting:', material.name(), 'as a substance material'
		materialInfo = serializeNode(material, serializeConnections=False)
		materialInfo.update({
			'isSubstance': True,
			'maps': {
				'diffuse': None,
				'ao_rough_metal_ior': None,
				'normal': None,
			},
		})

		# diffuse and ao_rough_metal_ior both use calcDiffuse node
		calcDiffuse = material.getInputByProperty('diffuseColor')
		if calcDiffuse:
			# find diffuse
			diffuseNode = calcDiffuse.getInputByProperty('input1')
			if diffuseNode:
				materialInfo['maps']['diffuse'] = diffuseNode.getProperty('fileTextureName')

			# find aoRough
			invertMetalNode = calcDiffuse.getInputByProperty('input2')
			if invertMetalNode:
				aoNode = invertMetalNode.getInputByProperty('inputX')
				if aoNode:
					materialInfo['maps']['ao_rough_metal_ior'] = aoNode.getProperty('fileTextureName')

		# normal map
		normalNode = material.getInputByProperty('bumpMapR')
		if normalNode:
			materialInfo['maps']['normal'] = normalNode.getProperty('fileTextureName')

	else:
		materialInfo = serializeNode(material)

	with open(matFile, 'w') as f:
		f.write(json.dumps(materialInfo,
			sort_keys=True,
			indent=4,
			separators=(', ', ': ')).replace('    ','\t'))



# Import
##################################################

def importMaterial(matFile):
	matInfo = {}
	with open(matFile) as f:
		matInfo = json.load(f)

	if matInfo['isSubstance']:
		maps = matInfo['maps'].values()
		materialDictionary = translator.createMaterialFromImages(maps, matInfo['name'])
		print 'Created substance material:', materialDictionary
	else:
		mel.eval('nodeEdCreateNodeCommand "' + matInfo['type'] + '";')
		materialNode = translator.getNodeByName(pymel.ls(sl=True)[0])
		print '\n\n\n\n\nmaterialNode.name:', materialNode.name()
		materialNode.setName(matInfo['name'])
		materialNode.setProperties(matInfo['properties'])

		createdNodes = {}
		for sourceProperty, inputInfo in matInfo['inputs'].iteritems():
			# print sourceProperty, '>', inputInfo['name']

			# if we already connected the node, just re-use it
			if inputInfo['name'] in createdNodes:
				translator.connectProperty(
					createdNodes[inputInfo['name']],
					inputInfo['targetProperty'],
					materialNode,
					sourceProperty)
			elif inputInfo['type'] == 'file':
				mel.eval('optionVar -sv create2dTextureType "texture";')
				mel.eval('nodeEdCreateNodeCommand "file";')
				fileNode = translator.getSelectedNode()
				fileNode.setName(inputInfo['name'])
				mel.eval('vray addAttributesFromGroup "{}" "vray_file_gamma" 1;'.format(fileNode.name()))
				fileNode.setProperties(inputInfo['properties'])
				uvNode = fileNode.getInputByProperty('coverage')
				uvNode.setProperties(inputInfo['placementSettings']['properties'])
				uvNode.setName(inputInfo['placementSettings']['name'])
				translator.connectProperty(fileNode, inputInfo['targetProperty'], materialNode, sourceProperty)
				createdNodes[inputInfo['name']] = fileNode

node = translator.getSelectedNode()

# print node.getInputConnections()
# print node.getOutputConnections()
# print node.getInputConnectionByProperty('coverage')
# print node.getOutputsbyProperty('outColor')
# print node.getInputConnectionByProperty('coverage')['target']
# print node.getOutputsbyProperty('outColor')['targets']

# print getInputConnections(node)
# exportMaterial()
importMaterial(matFile)
