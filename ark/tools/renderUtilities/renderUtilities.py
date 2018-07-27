import arkInit
import arkMath
arkInit.init()

import os
currentApp =  os.environ.get('ARK_CURRENT_APP')

import translators
translator = translators.getCurrent()

from translators import QtGui
import settingsManager
globalSettings = settingsManager.globalSettings()

import baseWidget

class RenderUtilities(baseWidget.BaseWidget):
	defaultOptions = {
	'title': 'Render Utilities',
	'width': 300,
	'height': 400,

	'knobs': [
		{
			'name': 'Apply Material Override',
			'dataType': 'checkbox',
			'value': False
		},
		{
			'name': 'color',
			'dataType': 'vec3',
			'value': arkMath.Vec(float(0.2), float(0.2), float(0.2))
		},
		{
			'name': 'Color Picker',
			'dataType': 'pythonButton',
			'callback': 'launchColorEditor'
		},
		{
			'name': 'reflectivity',
			'dataType': 'float'
		},
		{
			'name': 'ior',
			'dataType': 'float'
		},
		{
			'name': 'glossiness',
			'dataType': 'float'
		},
		{
			'name': 'Add Render Elements:',
			'dataType': 'label',
			'value': 'Add Render Elements'
		},
		{
			'name': 'Standard Elements',
			'dataType': 'pythonButton',
			'callback': 'setPresets'
		},
		{
			'name': 'Light Select',
			'dataType': 'pythonButton',
			'callback': 'createLightSelect'
		},
		{
			'name': 'Selection Matte',
			'dataType': 'pythonButton',
			'callback': 'selectionMatte'
		},
		{
			'name': 'Layers Mattes',
			'dataType': 'pythonButton',
			'callback': 'layersMattes'
		},
		{
			'name': 'Scene Materials',
			'dataType': 'pythonButton',
			'callback': 'sceneMaterials'
		},
		{
			'name': 'Selected Materials',
			'dataType': 'pythonButton',
			'callback': 'selectedMaterials'
		},
		{
			'name': 'Remove Render Elements:',
			'dataType': 'label',
			'value': 'Remove Render Elements'
		},
		{
			'name': 'Remove Unused Mattes',
			'dataType': 'pythonButton',
			'callback': 'removeUnusedMattes'
		},
		{
			'name': 'Remove Mattes',
			'dataType': 'pythonButton',
			'callback': 'removeAllMattes'
		},
		{
			'name': 'Remove All',
			'dataType': 'pythonButton',
			'callback': 'clearPresets'
		},
	]
	}

	def init(self):
		# check for existing matte render elements when opened (necessary for unique ids)
		existingIDs = set()
		elementNodes = translator.getNodesByProperty('vray_redid_multimatte')
		if len(elementNodes) == 0:
			self.currID = 1
		else:
			for elementNode in elementNodes:
				existingIDs.add(elementNode.getProperty('vray_redid_multimatte'))
			self.currID = sorted(existingIDs)[-1] + 1

	def postShow(self):
		self.getKnob('color').on('changed', self.overrideMaterials)
		self.getKnob('reflectivity').on('changed', self.overrideMaterials)
		self.getKnob('ior').on('changed', self.overrideMaterials)
		self.getKnob('glossiness').on('changed', self.overrideMaterials)
		translator.getNodeByName('vraySettings').setProperty('postTranslatePython', '')
		self.getKnob('Apply Material Override').on('changed', self.checkBoxChanged)

	def checkBoxChanged(self, value):
		if value:
			self.overrideMaterials()
		else:
			self.clearOverrides()

	def overrideMaterials(self, *args):
		color = self.getKnob('color').getValue()
		reflect = self.getKnob('reflectivity').getValue()
		ior = self.getKnob('ior').getValue()
		glossiness = self.getKnob('glossiness').getValue()
		if self.getKnob('Apply Material Override').value:
			overrideCommand = [
				'from vray.utils import *',
				'vRayMtl = create(\"BRDFVRayMtl\", \"_overrideMtl\")',
				'vRayMtl.set(\"diffuse\", AColor(%s, %s, %s, 1.0))' % (color.x, color.y, color.z),
				'vRayMtl.set(\"reflect\", AColor(%s, %s, %s, 1.0))' % (reflect, reflect, reflect),
				'vRayMtl.set(\"fresnel\", True)',
				'vRayMtl.set(\"fresnel_ior\", %s)' % (ior),
				'vRayMtl.set(\"refract_ior\", %s)' % (ior),
				'vRayMtl.set(\"reflect_glossiness\", %s)' % (glossiness),
				'vRayMtl.set(\"refract_glossiness\", %s)' % (glossiness),
				'vRayMtl.set(\"brdf_type\", 4)',
				'nodes = findByType("Node")',
				'for node in nodes:',
				'	node.set(\"material\", vRayMtl)'
			]
			translator.getNodeByName('vraySettings').setProperty('postTranslatePython', '\n'.join(overrideCommand))

	def clearOverrides(self):
		translator.getNodeByName('vraySettings').setProperty('postTranslatePython', '')

	def launchColorEditor(self):
		selectedColor = QtGui.QColorDialog.getColor()
		color = []
		color.append(selectedColor.redF())
		color.append(selectedColor.greenF())
		color.append(selectedColor.blueF())
		self.getKnob('color').setValue(color)

	def renderPassElementExists(self, elementName):
		element = translator.getNodeByName(elementName)
		# return not not element
		return element is not None

	def getMatteID(self, matteName):
		elementNode = translator.getNodeByName('vrayRE_Multi_Matte_' + matteName)
		return elementNode.getProperty('vray_redid_multimatte')

	# adds matte layer, names render element and matte filename, assigns id to red channel, increments currid and returns id
	def addMatte(self, matteName):
		if self.renderPassElementExists('vrayRE_Multi_Matte_' + matteName):
			return self.showError('Render element named {} already exists. No render element added.'.format(str(matteName)))
		prefix = 'vrayRE_Multi_Matte_'
		matteNode = translator.addRenderElement('MultiMatteElement')
		matteNode = matteNode.setName(prefix + matteName)
		if not hasattr(self, 'currID'):
			self.currID = 1
		matteNameSuffix = matteNode.name()[len(prefix):]
		matteNode.setProperty('vray_redid_multimatte', self.currID)
		matteNode.setProperty('vray_greenon_multimatte', False)
		matteNode.setProperty('vray_blueon_multimatte', False)
		self.currID += 1
		# match filename to suffix of render element
		matteNode.setProperty('vray_name_multimatte', 'm_' + matteNameSuffix)
		return self.currID - 1

	# sets the vray object id (adds attribute if it doesn't exist)
	def setObjectID(self, obj, objectID):
		if not obj.hasProperty('vrayObjectID'):
			obj.addVrayProperty('vray_objectID')
		obj.setProperty('vrayObjectID', objectID)

	def removeObjectID(self, obj):
		if obj.hasProperty('vrayObjectID'):
			obj.removeVrayProperty('vray_objectID')

	# adds mattes to selection
	def selectionMatte(self):
		selectedObjects = translator.getSelectedNodes()
		if len(selectedObjects) == 0:
			return self.showError('No objects selected; no render element added.')
		matteName = QtGui.QInputDialog().getText(self, self.tr('Selection Matte'), self.tr('Enter selection matte name:'))
		if matteName[1] and matteName[0]:
			matteID = self.addMatte(matteName[0])
			for obj in selectedObjects:
				self.setObjectID(obj, matteID)

	# adds a matte to each layer in scene (named after layer name)
	# will ignore masterLayer
	def layersMattes(self):
		layerNodes = translator.getNodesByType('renderLayer')
		for ln in layerNodes:
			# ignore default layer
			if not 'defaultRenderLayer' == ln.name():
				if not self.renderPassElementExists('vrayRE_Multi_Matte_' + ln.name()):
					matteID = self.addMatte(ln.name())
				else:
					matteID = self.getMatteID(ln.name())
				outputNodes = ln.getOutputs()
				for objName in outputNodes:
					if not 'defaultRenderingList' == objName:
						objNode = translator.getNodeByName(objName)
						self.setObjectID(objNode, matteID)

	# adds a matte to each material in scene (named after material name)
	def sceneMaterials(self):
		usedMaterials = self.materialsInUse()
		materialNodes = translator.getNodesByType('shadingEngine')
		for materialNode in materialNodes:
			inputNodes = materialNode.getInputs()
			if len(inputNodes) > 0:
				materialName = inputNodes[0].name()
				if materialName in usedMaterials:
					# get matte id of existing element, or create new element
					if not self.renderPassElementExists('vrayRE_Multi_Matte_' + materialName):
						matteID = self.addMatte(materialName)
					else:
						matteID = self.getMatteID(materialName)
					for objName in inputNodes:
						objNode = translator.getNodeByName(objName)
						# geometry objects
						if objNode.getType() == 'transform':
							self.setObjectID(objNode, matteID)

	# adds a matte to selected material (named after material name)
	def selectedMaterials(self):
		selectedNodes = translator.getSelectedNodes()
		for obj in selectedNodes:
			material = obj.getMaterial()
			# throws error if no material or no shader
			if self.renderPassElementExists('vrayRE_Multi_Matte_' + material.name()):
				matteID = self.getMatteID(material.name())
			else:
				matteID = self.addMatte(material.name())
			outputNodes = material.getOutputs()
			for objName in outputNodes:
				if translator.getNodeByName(objName).getType() == 'shadingengine':
					inputObjects = translator.getNodeByName(objName).getInputs()
					for obj in inputObjects:
						objNode = translator.getNodeByName(obj)
						if objNode.getType() == 'transform':
							# geometry objects
							self.setObjectID(objNode, matteID)

	def materialsInUse(self):
		usedMaterials = set()
		existingObjects = translator.getNodesByType('transform')
		for obj in existingObjects:
			try:
				usedMaterials.add(obj.getMaterial().name())
			except Exception:
				# object does not have material
				pass
		return usedMaterials

	def removeUnusedMattes(self):
		# get object ids currently in use
		existingIDs = set()
		existingObjects = translator.getNodesByType('transform')
		for obj in existingObjects:
			if obj.hasProperty('vrayObjectID'):
				existingIDs.add(obj.getProperty('vrayObjectID'))

		# delete any matte with an unused id
		existingMattes = translator.getNodesByProperty('vray_redid_multimatte')
		toRemove = []
		for matte in existingMattes:
			if not matte.getProperty('vray_redid_multimatte') in existingIDs:
				toRemove.append(matte)
				objNodes = translator.getNodesByProperty('vrayObjectID')
				for obj in objNodes:
					if not obj.getProperty('vrayObjectID') in existingIDs:
						obj.removeVrayProperty('vray_objectID')
		translator.removeNodes(toRemove)

	def clearObjectIDs(self):
		objNodes = translator.getNodesByProperty('vrayObjectID')
		for obj in objNodes:
			self.removeObjectID(obj)
		self.currID = 1

	def removeAllMattes(self):
		toRemove = translator.getNodesByProperty('vray_redid_multimatte')
		translator.removeNodes(toRemove)
		self.clearObjectIDs()

	def setPresets(self):
		if not self.renderPassElementExists('vrayRE_Diffuse'):
			translator.addRenderElement('diffuseChannel')
		if not self.renderPassElementExists('vrayRE_Normals'):
			translator.addRenderElement('normalsChannel')
		if not self.renderPassElementExists('vrayRE_Reflection'):
			translator.addRenderElement('reflectChannel')
		if not self.renderPassElementExists('vrayRE_Reflection_Filter'):
			translator.addRenderElement('reflectionFilterChannel')
		if not self.renderPassElementExists('vrayRE_Refraction'):
			translator.addRenderElement('refractChannel')
		if not self.renderPassElementExists('vrayRE_Refraction_Filter'):
			translator.addRenderElement('refractionFilterChannel')
		if not self.renderPassElementExists('vrayRE_SSS'):
			translator.addRenderElement('FastSSS2Channel')
		if not self.renderPassElementExists('vrayRE_Specular'):
			translator.addRenderElement('specularChannel')
		if not self.renderPassElementExists('vrayRE_Self_Illumination'):
			translator.addRenderElement('selfIllumChannel')
		if not self.renderPassElementExists('vrayRE_Atmospheric_Effects'):
			translator.addRenderElement('atmosphereChannel')

		if not self.renderPassElementExists('vrayRE_Worldspace_Position'):
			self.createXyzWPP()
		if not self.renderPassElementExists('vrayRE_Z_depth'):
			self.createZDepth()

		if not self.renderPassElementExists('cryptomatteChannel_node_name'):
			self.createCryptomatte()

		globalPresets = '{}/presets/attrPresets/'.format(globalSettings.MAYA_NETWORK_ROOT)

		# apply defaultRenderGlobals preset
		defaultRenderGlobalsNode = translator.getNodeByName('defaultRenderGlobals')
		translator.applyNodePreset(defaultRenderGlobalsNode, '{}renderGlobals/IngenuityStandard.mel'.format(globalPresets))

		# apply vraySettings preset
		vraySettingsNode = translator.getNodeByName('vraySettings')
		translator.applyNodePreset(vraySettingsNode, '{}VRaySettingsNode/IngenuityStandard.mel'.format(globalPresets))

		return

	def clearPresets(self):
		for preset in translator.getNodesByType('VRayRenderElement'):
			translator.removeRenderElement(preset.name())
		for renderSet in translator.getNodesByType('vrayrenderelementset'):
			translator.removeRenderElement(renderSet.name())
		self.clearObjectIDs()

	def createCryptomatte(self):
		cryptoMattes = ['node_name', 'material_name', 'node_name_hierarchy']
		for idx, name in enumerate(cryptoMattes):
			crypto = translator.addRenderElement('cryptomatteChannel')
			crypto.setName('cryptomatteChannel_' + name)
			crypto.setProperty('vray_idtype_cryptomatte', idx)
			crypto.setProperty('vray_name_cryptomatte', 'cryptomatte_' + name)

	def createXyzWPP(self):
		ppp = translator.addRenderElement('ExtraTexElement')

		pppWorld = ppp.setName('vrayRE_Worldspace_Position')
		pppWorld.setProperty('vray_explicit_name_extratex', 'vrayRE_Worldspace_Position')
		pppWorld.setProperty('vray_affectmattes_extratex', 0)

		samplerInfoPPP = translator.createShadingNode('samplerInfo')

		translator.connectProperty(samplerInfoPPP, 'pointWorldX', pppWorld, 'vray_texture_extratexR')
		translator.connectProperty(samplerInfoPPP, 'pointWorldY', pppWorld, 'vray_texture_extratexG')
		translator.connectProperty(samplerInfoPPP, 'pointWorldZ', pppWorld, 'vray_texture_extratexB')

	def createZDepth(self):
		zDepth = translator.addRenderElement('zdepthChannel')
		zDepth.setProperty('vray_depthClamp', 0)

	def createLightSelect(self):
		selectedObjects = translator.getSelectedNodes()
		print selectedObjects
		if len(selectedObjects) == 0:
			return self.showError('No lights selected; no render element added.')

		lightSelectItems  = ['dome',
							'key',
							'fill',
							'left',
							'right',
							'middle',
							'top',
							'bottom',
							'back',
							'front',
							'accent_one',
							'accent_two',
							'accent_three',
							'sun',
							'headlights',
							'streetlights']
		lightSelectName = QtGui.QInputDialog().getItem(self, self.tr('Light select'), self.tr('Select Light Select pass name:'), lightSelectItems, editable=False)
		if lightSelectName[0] and lightSelectName[1]:
			lightSelectName = lightSelectName[0]
		print lightSelectName
		if self.renderPassElementExists('vrayRE_Light_Select_' + lightSelectName):
			return self.showError('Render element named {} already exists. No render element added.'.format(str(lightSelectName)))
		prefix = 'vrayRE_Light_Select_'
		lightSelectNode = translator.addRenderElement('LightSelectElement')
		lightSelectNode = lightSelectNode.setName(prefix + lightSelectName)
		lightSelectNode.setProperty('vray_name_lightselect', 'l_' + lightSelectName)
		for node in selectedObjects:
			translator.addToRenderSet(prefix + lightSelectName, node.name())


def gui():
	return RenderUtilities()

def launch(docked=False):
	translator.launch(RenderUtilities, docked=docked)

if __name__ == '__main__':
	launch()