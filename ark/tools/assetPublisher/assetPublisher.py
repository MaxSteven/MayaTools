'''

Asset Publisher

Publishes:
	materials
	lights
	geometry

'''
import json
import os
import cOS
import traceback
import arkUtil
import deadline

import translators
translator = translators.getCurrent()
currentApp = os.environ.get('ARK_CURRENT_APP')

import baseWidget

class AssetPublisher(baseWidget.BaseWidget):
	defaultOptions = {
			'title': 'Asset Manager',
			'width': 600,
			'height': 200,

		'knobs': [
			{
				'name': 'Asset Name',
				'dataType': 'text',
				'value': 'ball'
			},
			{
				'name': 'Export Location',
				'dataType': 'Directory',
				'value': 'C:\Users\IE\Desktop\materialsPub',
				'buttonText': '...'
			},
			{
				'name': 'Asset Type',
				'dataType': 'list',
				'options': ['Geometry Asset','Lighting Setup','Just Materials']
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
				'name': 'Export Lights with Asset',
				'dataType': 'Checkbox',
				'value': False
			},
			{
				'name': 'Export',
				'dataType': 'PythonButton',
				'callback':'export'
			},
			{
				'name': 'Import File',
				'dataType': 'OpenFile',
				'value': 'C:\Users\IE\Desktop\materialsPub\\ball.asset',
				'buttonText': '...',
				'extension': '*.asset'
			},
			{
				'name': 'Import',
				'dataType': 'PythonButton',
				'callback':'load'
			}
		]
	}

	def init(self):
		pass

	def postShow(self):
		# Get selected nodes
		self.selections = translator.getSelectedNodes()

		# Process frame range
		frameRange = translator.getAnimationRange()

		# Set up frame range knob and set 'export with lights' to hide itself when not applicable
		self.getKnob('Frame Range').setValue(str(frameRange['startFrame']) + '-' + str(frameRange['endFrame']))
		self.getKnob('Asset Type').on('changed', self.hideExportWithLights)

	# Hides 'export with lights' when not exporting geometry asset
	def hideExportWithLights(self, *args):
		if self.getKnob('Asset Type').getValue() == 'Geometry Asset':
			self.showKnob('Export Lights with Asset')
		else:
			self.hideKnob('Export Lights with Asset')

	# Process alembic on the farm.
	# Currently this uses a beta version of the deadline scripts
	def deadlineProcessAlembic(self, filepath, frameRange, fps=24):

		self.arkDeadline = deadline.arkDeadline.ArkDeadline()
		pathInfo = cOS.getPathInfo(filepath)
		name = pathInfo['name']

		# Add job info
		jobInfo = {
			'Name': name,
			'BatchName': name,
			'Plugin': 'CommandLine',
			'priority': 70,
			'LimitGroups': 'hbatch-license',
			'Group': 'good-software',
			'MachineLimit': 0,
			'ExtraInfoKeyValue0': 'abc_in=' + filepath,
			'ExtraInfoKeyValue1': 'abc_out=' + filepath.replace('.abc', '_processed.abc'),
			'ExtraInfoKeyValue2': 'abc_frames=' + str(frameRange),
			'ExtraInfoKeyValue3': 'abc_fps=' + str(fps),
		}

		# Submit job using beta script
		pluginInfo = {
			'SceneFile': globalSettings.DEADLINE + '/custom/scripts/Jobs/deadlineProcessedAlembic.py',
			'Executable': globalSettings.HYTHON_EXE,
			'Shell': 'default',
			'ShellExecute': False,
			'SingleFramesOnly': True
		}
		
		submittedInfo = self.arkDeadline.submitJob(jobInfo, pluginInfo)
		jobID = submittedInfo.get('_id')

		self.arkDeadline.updateJobData(jobID, {
			'Props.PlugInfo.Arguments': '{}/jobs/{}/deadlineProcessedAlembic.py'.format(globalSettings.DEADLINE, jobID)
		})

	# Export asset
	def export(self):

		# Double check selections
		self.selections = translator.getSelectedNodes()

		# Error check
		if self.selections == []:
			self.showError('Please select at least one item to export')
			return

		exDir = self.getKnob('Export Location').getValue()
		if not self.getKnob('Process Locally').getValue() and exDir.startswith(globalSettings.SYSTEM_ROOT):
			self.showError('Cannot export to C drive on the farm. Please choose a shared drive')
			return

		# Make sure asset name is websafe
		assetName = arkUtil.makeWebSafe(self.getKnob('Asset Name').getValue())

		# Set up file names
		alembicFilename = self.getKnob('Export Location').getValue() + assetName + '.abc'
		assetFilename = self.getKnob('Export Location').getValue() + assetName + '.asset'

		assetType = 'geometry'
		if self.getKnob('Asset Type').getValue() == 'Lighting Setup':
			assetType = 'lighting'
		if self.getKnob('Asset Type').getValue() == 'Just Materials':
			assetType = 'materials'

		# Set up asset info
		assetInfo = {
			'alembicPath': alembicFilename,
			'materials': {},
			'lights':{},
			'lightTransforms':{},
			'type': assetType,
		}

		# Get all nodes under the selection
		exportNodes = translator.getSelectedNodes()

		children = None 

		# Depending on the current app, use houdini or maya commands
		if currentApp == 'houdini':
			childHolder = []
			for selectedNode in exportNodes:
				childHolder = childHolder + translator.ensureNodes(selectedNode.getOutputs())
			children = childHolder
		else:
			children = translator.getChildNodes(exportNodes)

		allNodes = exportNodes + children
		materials = {}
		lights = {}

		#####
		# For all nodes in the selection, write dictionaries for lights and materials
		#####

		for node in allNodes:

			###################### ONLY EXPORTING LIGHTS ##########################

			if assetType == 'lighting' and node.getType() in translator.serialNodeClass.lightTypes:

				assetInfo['alembicPath'] = ''

				light = node
				lightName = light.name()

				if not lightName.startswith(assetName):
					lightName = assetName + '_' + lightName

				if lightName in lights:
					continue

				light.setName(lightName)
				lights[lightName] = light
				
			############################################################################

			####################### ONLY EXPORTING MATERIALS ##########################

			if assetType == 'materials' and node.getType() in translator.serialNodeClass.materialTypes:

				assetInfo['alembicPath'] = ''

				# Get the material
				try:
					material = node
					materialName = material.name()

					if not materialName.startswith(assetName):
						materialName = assetName + '_' + materialName

					if materialName in materials:
						continue

					material.setName(materialName)
					materials[materialName] = material

				except:
					material = None
					materialName = 'NoMaterial'

			###########################################################################

			########################## STANDARD EXPORT ################################

			if assetType == 'geometry':

				# If exporting lights with this geometry,
				# set lights names and add them to the dictionary
				if self.getKnob('Export Lights with Asset').getValue():
					if node.getType() in translator.serialNodeClass.lightTypes:
						light = node
						lightName = light.name()

						if not lightName.startswith(assetName):
							lightName = assetName + '_' + lightName

						if lightName in lights:
							continue

						light.setName(lightName)
						lights[lightName] = light

				# Rename objects to include asset name
				if node.getType() in translator.serialNodeClass.objectTypes:
					if not node.name().startswith(assetName):
						node.setName(assetName + '_' + node.name())

				# Find nodes with assigned materials
				if node.getType() in translator.serialNodeClass.geometryTypes:
					parent = node.getParent()
					materialName = None

					# Get the material
					try:
						material = parent.getMaterial()
						materialName = material.name()

						if not materialName.startswith(assetName):
							materialName = assetName + '_' + materialName

						if materialName in materials:
							continue

						material.setName(materialName)
						materials[materialName] = material

					except:
						material = None
						materialName = 'NoMaterial'

					# Assign material property
					if not node.hasProperty('materialName'):
						node.addProperty('materialName')

					if ':' in materialName:
						materialName = materialName.split(':')[-1]

					if materialName == 'lambert1':
						materialName = 'NoMaterial'

					node.setProperty('materialName', materialName)

			####################################################################

		####
		# Now that dictionaries have been writen, write asset files
		####

		######################## WRITING JUST LIGHTS #############################

		# If this asset is supposed to be a lighting setup
		if assetType == 'lighting':
			for lightName, light in lights.iteritems():

				lightFileName = self.getKnob('Export Location').getValue() + lightName + '.light'
				serialNode = translator.getSerialNode(light)
				serialized = serialNode.serialize()
				pos = light.getParent().getPosition()
				with open(lightFileName, 'w') as f:
					f.write(json.dumps(serialized,
						sort_keys=True,
						indent=4,
						separators=(', ', ': ')).replace('    ','\t'))

				assetInfo['lightTransforms'][lightName] = pos
				assetInfo['lights'][lightName] = lightFileName

			# Write asset file
			with open(assetFilename, 'w') as f:
				f.write(json.dumps(assetInfo,
					sort_keys=True,
					indent=4,
					separators=(', ', ': ')).replace('    ','\t'))
		
		###########################################################################

		######################## WRITING JUST MATERIALS ###########################

		if assetType == 'materials':
			for materialName, material in materials.iteritems():

				materialFilename = self.getKnob('Export Location').getValue() + materialName + '.material'
				serialNode = translator.getSerialNode(material)
				with open(materialFilename, 'w') as f:
					f.write(json.dumps(serialNode.serialize(),
						sort_keys=True,
						indent=4,
						separators=(', ', ': ')).replace('    ','\t'))

				assetInfo['materials'][materialName] = materialFilename

			# Write asset file
			with open(assetFilename, 'w') as f:
				f.write(json.dumps(assetInfo,
					sort_keys=True,
					indent=4,
					separators=(', ', ': ')).replace('    ','\t'))

		##########################################################################

		######################## WRITE STANDARD ASSET FILE #######################

		if assetType == 'geometry':

			# If this asset should include lights, like a lamp, add light dictionary
			if self.getKnob('Export Lights with Asset').getValue():
				# Creat light files
				for lightName, light in lights.iteritems():

					lightFileName = self.getKnob('Export Location').getValue() + lightName + '.light'
					serialNode = translator.getSerialNode(light)
					serialized = serialNode.serialize()
					pos = light.getParent().getPosition()
					with open(lightFileName, 'w') as f:
						f.write(json.dumps(serialized,
							sort_keys=True,
							indent=4,
							separators=(', ', ': ')).replace('    ','\t'))

					assetInfo['lightTransforms'][lightName] = pos
					assetInfo['lights'][lightName] = lightFileName

			# Create material files
			for materialName, material in materials.iteritems():

				materialFilename = self.getKnob('Export Location').getValue() + materialName + '.material'
				serialNode = translator.getSerialNode(material)
				with open(materialFilename, 'w') as f:
					f.write(json.dumps(serialNode.serialize(),
						sort_keys=True,
						indent=4,
						separators=(', ', ': ')).replace('    ','\t'))

				assetInfo['materials'][materialName] = materialFilename

			# Process frame range
			frameRange = self.getKnob('Frame Range').getValue()
			if not self.getKnob('Animation').getValue():
				frameRange = frameRange.split('-')[0].strip()

			# Export alembic, using appropriate commands for current app
			if currentApp == 'houdini':
				translator.exportAlembic(
					alembicFilename,
					frameRange,
					{
						'objects': [obj.getPath() for obj in exportNodes],
					})
			else:
				translator.exportAlembic(
					alembicFilename,
					frameRange,
					{
						'objects': [obj.name() for obj in exportNodes],
					})

			# Write asset file
			with open(assetFilename, 'w') as f:
				f.write(json.dumps(assetInfo,
					sort_keys=True,
					indent=4,
					separators=(', ', ': ')).replace('    ','\t'))

			# Process alembic
			# ASK GRANT ABOUT WHAT TO DO WHEN THE CURRENT APP -IS- HOUDINI
			if currentApp != 'houdini':

				# Process locally
				if self.getKnob('Process Locally').getValue():
					print '\nprocessing alembic, chill..'

					unprocessedFilename = alembicFilename.replace('.abc','_unprocessed.abc')
					cOS.removeFile(unprocessedFilename)

					result = translator.processAlembic(alembicFilename,
						frameRange,
						str(translator.getFPS()))

					# SHOULD HAPPEN AUTOMATICALLY
					if not result:
						# cOS.removeFile(assetFilename)
						return self.showError(result)
					if not os.path.exists(unprocessedFilename):
						# cOS.removeFile(assetFilename)
						return self.showError('Unprocessed file not found, local processing likely failed')

				# Process on the farm
				else:
					self.deadlineProcessAlembic(alembicFilename, frameRange, str(translator.getFPS()))

	# Load an asset files
	def load(self):

		# Open asset file
		filename = self.getKnob('Import File').getValue()
		if not filename or len(filename) < 1:
			return self.error('No file selected')
		extension = cOS.getExtension(filename)
		assetInfo = None

		try:
			with open(filename) as f:

				# Load asset info
				assetInfo = json.load(f)

				###################### LOAD JUST LIGHTS #######################

				if assetInfo['type'] == 'lighting':

					# Add lights
					lights = assetInfo['lights']
					importedLights = {}
					# Filter asset for new materials to import
					for lightName, lightFileName in lights.iteritems():
						serialNode = translator.getSerialNodeFromFile(lightFileName)
						actualNode = serialNode.getDeserialized()
						importedLights[lightName] = actualNode
						nodePos = assetInfo['lightTransforms'][lightName]
						actualNode.getParent().setPosition(nodePos[0],nodePos[1],nodePos[2])

				################################################################

				#################### LOAD JUST MATERIALS #######################

				if assetInfo['type'] == 'materials':

					# Get expisting materials
					allMaterials = translator.getNodesByType('material')
					existingMaterials = {}
					for material in allMaterials:
						existingMaterials[material.name()] = material

					materials = assetInfo['materials']
					importedMaterials = {}

					# Filter asset for new materials to import
					for materialName, materialFilename in materials.iteritems():
						if materialName in existingMaterials:
							importedMaterials[materialName] = existingMaterials[materialName]
						else:
							serialNode = translator.getSerialNodeFromFile(materialFilename)
							actualNode = translator.getNodeByName(materialName)
							importedMaterials[materialName] = actualNode

				################################################################

				#################### LOAD REGULAR ASSET ########################

				if assetInfo['type'] == 'geometry':

					# Get all materials present in file
					allMaterials = translator.getNodesByType('material')
					existingMaterials = {}
					for material in allMaterials:
						existingMaterials[material.name()] = material

					materials = assetInfo['materials']
					importedMaterials = {}

					# Filter asset for new materials to import
					for materialName, materialFilename in materials.iteritems():

						if materialName in existingMaterials:
							importedMaterials[materialName] = existingMaterials[materialName]
						else:
							serialNode = translator.getSerialNodeFromFile(materialFilename)
							actualNode = translator.getNodeByName(materialName)
							importedMaterials[materialName] = actualNode

					# Import alembic as proxy
					# First look for processed alembic, then look for unprocessed
					proxy = None
					try:
						proxy = translator.createRenderProxy(assetInfo['alembicPath'].replace('.abc', '_processed.abc'), {'scale': 1.0,
												'particleWidthMultiplier': 1.0,
												'hairWidthMultiplier': 1.0,
												'previewFaces': 5000,'geoToLoad':'Preview'})
					except:
						self.showError("ERROR: Could not find processed alembic, defaulting to unprocessed")
						proxy = translator.createRenderProxy(assetInfo['alembicPath'], {'scale': 1.0,
												'particleWidthMultiplier': 1.0,
												'hairWidthMultiplier': 1.0,
												'previewFaces': 5000,'geoToLoad':'Preview'})
					proxyMaterial = proxy.getMaterial()
					materialNames = proxyMaterial.getProperty('shaderNames')

					# Connect any materials that need to be connected
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
					
					# Get lights dictionary
					lights = assetInfo['lights']
					importedLights = {}

					# Import lights
					for lightName, lightFileName in lights.iteritems():
						serialNode = translator.getSerialNodeFromFile(lightFileName)
						actualNode = serialNode.getDeserialized()
						importedLights[lightName] = actualNode
						nodePos = assetInfo['lightTransforms'][lightName]
						actualNode.getParent().setPosition(nodePos[0],nodePos[1],nodePos[2])

		except Exception as err:
			return self.showError('Failed to load asset:', err)

def gui():
	return AssetPublisher()

def launch(docked=False):
	translator.launch(AssetPublisher, docked=docked)

if __name__=='__main__':
	launch()
