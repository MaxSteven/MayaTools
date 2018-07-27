# Name: Publish Assets
# Author: Grant Miller
# Date: 12/01/2017

import os

import arkInit
arkInit.init()

import settingsManager
globalSettings = settingsManager.globalSettings()

import translators
translator = translators.getCurrent()
currentApp = os.environ.get('ARK_CURRENT_APP')
from translators import QtGui

import cOS

from caretaker import Caretaker
caretaker = Caretaker()

import baseWidget
import arkUtil

import json
import arkMath
import translators
import pymel.core as pymel
import maya.mel as mel

translator = translators.getCurrent()

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


def exportMaterial(material, filename):
	# fix: crappy check, should create an attribute on substance
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

	with open(filename, 'w') as f:
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

		return materialDictionary['material']

	else:
		mel.eval('nodeEdCreateNodeCommand "' + matInfo['type'] + '";')
		materialNode = translator.getNodeByName(pymel.ls(sl=True)[0])
		materialNode.setName(matInfo['name'])
		materialNode.setProperties(matInfo['properties'])

		createdNodes = {}
		for sourceProperty, inputInfo in matInfo['inputs'].iteritems():
			# if we already created the node, just re-use it
			if inputInfo['name'] in createdNodes:
				translator.connectProperty(
					createdNodes[inputInfo['name']],
					inputInfo['targetProperty'],
					materialNode,
					sourceProperty)

			# otherwise make a new node and connect it
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

		return materialNode

# Process Alembic
# fix: this should be somewhere common
def processAlembic(filepath, frameRange, fps=24):
	command = (os.environ.get('ARK_PYTHON') +
			' ' + globalSettings.HOUDINI_PROCESS_ALEMBIC +
			' -o ' + filepath +
			' -fr ' + frameRange +
			' -fps ' + fps +
			' -farm false')

	(out, err) = cOS.getCommandOutput(command)
	print 'process alembic output:', out
	print 'process alembic errors:', err

	if err:
		return err
	else:
		return True


class PublishManager(baseWidget.BaseWidget):
	defaultOptions = {
			'title': 'Publish Asset',
			'width': 600,
			'height': 300,

		'knobs':
		[
			{
				'name': 'Folder',
				'dataType': 'directory',
			},
			{
				'name': 'Asset Name',
				'dataType': 'text',
				'value': 'tacos',
			},
			{
				'name': 'Publish As',
				'dataType': 'List',
			},
			{
				'name': 'Frame Range',
				'dataType': 'FrameRange',
			},
			{
				'name': 'Animation',
				'dataType': 'Checkbox',
			},
			{
				'name': 'Process Locally',
				'dataType': 'Checkbox',
				'value': True,
			},
			{
				'name': 'Publish',
				'dataType': 'PythonButton',
				'callback': 'publishAsset',
			},
			{
				'name': 'Import',
				'dataType': 'PythonButton',
				'callback': 'importAsset',
			},
		]
	}

	def postShow(self):
		self.taskInfo = caretaker.getTaskInfo()
		if not self.taskInfo.projectInfo:
			return self.showError('Invalid Project!')

		publishDir = self.taskInfo.assetRoot + 'Publish'
		self.getKnob('Folder').setValue(publishDir)

		# default frame range
		frameRange = translator.getAnimationRange()
		self.getKnob('Frame Range').setValue(
			str(frameRange['startFrame']) + '-' + str(frameRange['endFrame']))

		# set publish as
		if not translator.getOption('exportTypes'):
			self.hideKnob('Publish As')
		else:
			self.showKnob('Publish As')
			self.getKnob('Publish As').addItems(translator.getOption('exportTypes'))

	def publishAsset(self):
		# asset info
		assetFolder = self.getKnob('Folder').getValue()
		cOS.makeDirs(assetFolder)
		assetName = arkUtil.makeWebSafe(self.getKnob('Asset Name').getValue())

		assetFilename = assetFolder + assetName + '.asset'
		alembicFilename = assetFolder + assetName + '.abc'
		publishType = self.getKnob('Publish As').getValue()

		assetInfo = {
			'alembicPath': alembicFilename,
			'materials': {},
			'type': publishType.lower(),
		}

		exportNodes = translator.getSelectedNodes()

		children = translator.getChildNodes(exportNodes)
		print '\n\n\nchildren:', children
		allNodes = exportNodes + children

		materials = {}

		# collect materials
		for node in allNodes:
			print 'node:', node
			print 'node:', node.name()
			# only meshes
			if node.getType() != 'geometry':
				print 'skipping:', node.name(), node.getType()
				continue

			parent = node.getParent()
			try:
				material = parent.getMaterial()
				materialName = material.name()

				if not materialName.startswith(assetName):
					materialName = assetName + '_' + material.name()

				if materialName in materials:
					print 'Skipping:', materialName, 'already collected'
					continue

				material.setName(materialName)

				materials[materialName] = material
			except:
				material = None
				materialName = 'NoMaterial'

			if not node.hasProperty('materialName'):
				node.addProperty('materialName')

			if ':' in materialName:
				materialName = materialName.split(':')[-1]

			if materialName == 'lambert1':
				materialName = 'NoMaterial'

			# set materialName property on node
			# this gets dumped out to Houdini
			node.setProperty('materialName', materialName)

		# set material names to be asset_material
		# then export all materials used on objects
		for materialName, material in materials.iteritems():
			materialFilename = assetFolder + materialName + '.material'
			exportMaterial(material, materialFilename)

			assetInfo['materials'][materialName] = materialFilename

		# single frame if animation isn't checked
		frameRange = self.getKnob('Frame Range').getValue()
		if not self.getKnob('Animation').getValue():
			frameRange = frameRange.split('-')[0].strip()

		# export alembic
		translator.exportAlembic(
			alembicFilename,
			frameRange,
			{
				# fix: completely wrong should be nodes not names
				'objects': [obj.name() for obj in exportNodes],
			})

		# write asset info to file
		with open(assetFilename, 'w') as f:
			f.write(json.dumps(assetInfo,
				sort_keys=True,
				indent=4,
				separators=(', ', ': ')).replace('    ','\t'))

		# process the alembic if we're in Maya
		if currentApp != 'houdini' and publishType == 'Geometry':
			if self.getKnob('Process Locally').getValue():
				print '\nprocessing alembic, chill..'

				unprocessedFilename = alembicFilename.replace('.abc','_unprocessed.abc')
				cOS.removeFile(unprocessedFilename)

				result = processAlembic(alembicFilename,
					frameRange,
					str(translator.getFPS()))

				if not result:
					# cOS.removeFile(assetFilename)
					return self.showError(result)
				if not os.path.exists(unprocessedFilename):
					# cOS.removeFile(assetFilename)
					return self.showError('Unprocessed file not found, local processing likely failed')
			else:
				self.deadlineProcessAlembic()


	def importAsset(self):
		filename = QtGui.QFileDialog.getOpenFileName(
			self,
			'Select asset',
			self.getKnob('Folder').getValue(),
			'*.asset')

		if not filename or len(filename) < 1:
			return self.error('No file selected')
		filename = filename[0]

		assetInfo = None
		try:
			with open(filename) as f:
				assetInfo = json.load(f)
		except Exception as err:
			return self.showError('Failed to load asset:', err)

		if assetInfo['type'] == 'geometry':

			allMaterials = translator.getNodesByType('material')
			# make a dictionary of materials
			existingMaterials = {}
			for material in allMaterials:
				existingMaterials[material.name()] = material

			# import all the materials
			materials = assetInfo['materials']
			print '\n\nImporting materials'

			importedMaterials = {}
			for materialName, materialFilename in materials.iteritems():
				# use the existing material if it's there
				if materialName in existingMaterials:
					print '\nUsed existing material:', materialName
					importedMaterials[materialName] = existingMaterials[materialName]
				# otherwise import it
				else:
					print '\nImported:', materialName
					importedMaterials[materialName] = importMaterial(materialFilename)

			# import the alembic
			print '\n\nImporting alembic'
			proxy = translator.createRenderProxy(assetInfo['alembicPath'])

			# material assignment
			proxyMaterial = proxy.getMaterial()
			materialNames = proxyMaterial.getProperty('shaderNames')
			print '\n\nAssigning shaders:'
			print '\n'.join(materialNames)

			for i, materialName in enumerate(materialNames):
				if materialName not in importedMaterials:
					print 'Could not find:', materialName, 'skipping'
					continue

				outputs = importedMaterials[materialName].getOutputsByProperty('outColor')
				alreadyConnected = False
				for output in outputs:
					if output.name() == proxyMaterial.name():
						alreadyConnected = True

				# if the property is already connected
				# maya will throw an error
				if alreadyConnected:
					continue

				translator.connectProperty(
					importedMaterials[materialName],
					'outColor',
					proxyMaterial,
					'shaders[' + str(i) + ']')

		proxy.addProperty('source')
		proxy.setProperty('source', filename)

		return proxy





def gui():
	return PublishManager()

def launch(docked=False):
	translator.launch(PublishManager, docked=docked)

if __name__=='__main__':
	launch()
