# Standard Modules
import os
import re
from functools import partial
# import time

# Our Modules
import arkInit
arkInit.init()
import cOS
import arkUtil
import settingsManager
globalSettings = settingsManager.globalSettings()
import pathManager
import DeadlineJob

import arkFTrack
pm = arkFTrack.getPM()

import translators
translator = translators.getCurrent()

class MayaJob(DeadlineJob.DeadlineJob):
	renderNodeTypes = ['camera']
	resolutionDict = {
						'100%': 1,
						'75%': .75,
						'50%': .5,
						'25%': .25,
						'12.5%': .125,
						'6.25%': .0625,
					}

	# Override
	def getKnobs(self, shepherd):
		knobs = super(MayaJob, self).getKnobs(self)
		frameRange = translator.getAnimationRange()
		knobs[0:0] = [
				{
					'name': 'shot',
					'dataType': 'text',
				},
				{
					'name': 'Pass name',
					'dataType': 'dynamicList',
					'options': self.getPassesForScene(shepherd)
				},
				{
					'name': 'Camera',
					'dataType': 'searchList',
					'options': self.getRenderNodes()
				}
			]
		knobs[-5:-5] = [
				{
					'name': 'Chunk Size',
					'dataType': 'Int',
					'value': 1
				},
				{
					'name': 'Preview Resolution',
					'dataType': 'list',
					'options': ['6.25%', '12.5%', '25%', '50%', '75%', '100%']
				},
				{
					'name': 'Preview Frame',
					'dataType': 'Int',
					'value': (frameRange['startFrame'] + frameRange['endFrame']) * .5
				},
				{
					'name': 'Preview Render Options',
					'dataType': 'list',
					'options': translator.getOption('renderPresetOrder')
				},
				{
					'name': 'Max. Preview Time',
					'dataType': 'Int',
					'value': 10
				},
				{
					'name': 'Preview Render',
					'dataType': 'PythonButton'
				}
			]

		# Could have better efficiency
		for knob in knobs:
			if knob.get('name') == 'frame range':
				frameRange = translator.getAnimationRange()
				knob['value'] = str(frameRange.get('startFrame')) + '-' + str(frameRange.get('endFrame'))
			elif knob.get('name') == 'shot':
				knob['value'] = pm.getShot()['name']
		return knobs

	# Override
	def getRenderNodes(self):
		renderNodes = super(MayaJob, self).getRenderNodes()
		renderNodes = [renderNode.getPath() for renderNode in renderNodes]
		nodesToRemove = translator.getOption('defaultCameras')
		for node in nodesToRemove:
			if node in renderNodes:
				renderNodes.remove(node)
		return renderNodes

	def getRenderNodesKnob(self, shepherd):
		return shepherd.getKnob('Camera')

	def getPassesForScene(self, shepherd):
		if shepherd.getSourceFile() == '':
			return shepherd.showError('Save your file before submitting')

		# shotRoot/renders/
		shotRenders = cOS.normalizeAndJoin(pm.getPath(pm.getShot()), 'renders')

		if not os.path.isdir(shotRenders):
			print 'shot render directory {} does not exist'.format(shotRenders)
			return []

		taskName = pm.getTask()['name']
		idx = len(taskName) + 1

		passNames = os.listdir(shotRenders)
		versionRe = re.compile('[vV]([0-9]+)')

		# filter on passes for this task
		# ignore version folders
		passNames = [name[idx:] for name in passNames if not versionRe.match(name) if name.startswith(taskName + '_')]

		return passNames

	def isValidRenderNode(self, shepherd):
		renderNodePath = shepherd.getKnob('Camera').getValue()
		renderNode = translator.getNodeByPath(renderNodePath)
		return (renderNode != None)

	# Override
	def refresh(self, shepherd):
		super(MayaJob, self).refresh(shepherd)
		shepherd.updateShots()
		shepherd.getKnob('shot').clear()
		shepherd.getKnob('shot').addItems(shepherd.getShots())
		shepherd.getKnob('Pass name').clear()
		shepherd.getKnob('Pass name').addItems(self.getPassesForScene(shepherd))
		frameRange = translator.getAnimationRange()
		shepherd.getKnob('frame range').setValue(str(frameRange.get('startFrame')) + '-' + str(frameRange.get('endFrame')))

	def getFrameRange(self, shepherd=None):
		frameRange = super(MayaJob, self).getFrameRange()
		if frameRange:
			return frameRange

		frameRangeText = shepherd.getKnob('frame range').getValue()
		frames = arkUtil.parseFrameRange(frameRangeText)
		return {'startFrame': int(frames[0]), 'endFrame': int(frames[-1])}

	def connectJobSignals(self, shepherd):
		shepherd.getKnob('shot').on('clicked', shepherd.updateOutputPath)
		shepherd.getKnob('Pass name').on('clicked', shepherd.updateOutputPath)
		shepherd.getKnob('Camera').on('clicked', shepherd.updateOutputPath)
		shepherd.hideKnob('Max. Preview Time')
		shepherd.getKnob('Preview Render').on('clicked', partial(self.previewRender, shepherd))
		shepherd.getKnob('Preview Render Options').on('changed', partial(self.hideMaxPreviewKnob, shepherd))

	def hideMaxPreviewKnob(self, shepherd, *args):
		if shepherd.getKnob('Preview Render Options').getValue() == 'Progressive':
			shepherd.showKnob('Max. Preview Time')

		else:
			shepherd.hideKnob('Max. Preview Time')

	def getJobData(self, shepherd):
		jobData = super(MayaJob, self).getJobData(shepherd)

		renderNode = translator.getNodeByName(shepherd.getKnob('Camera').getValue())
		frame = shepherd.getKnob('Preview Frame').getValue()
		jobData.update({
			'program': 'maya',
			'fps': 24,
			'name': self.getJobName(shepherd),
			'node': translator.setRenderNode(renderNode).name(),
			'previewPath': shepherd.getKnob('output path').getValue().replace('%04d', str(frame) + '.preview'),
			'height': translator.getRenderProperty('height'),
			'width': translator.getRenderProperty('width'),
			'farPlane': translator.getRenderProperty('farPlane'),
			'nearPlane': translator.getRenderProperty('nearPlane'),
			'chunkSize': shepherd.getKnob('Chunk Size').getValue(),
		})
		return jobData

	def getJobName(self, shepherd):
		shotName = shepherd.getKnob('shot').getValue()
		passName = shepherd.getKnob('Pass name').getValue()
		if shotName != 'None' and shotName != '':
			return '%s_%s' % (shotName, passName)
		else:
			return passName

	def getOutputPath(self, shepherd):
		filePath = shepherd.getSourceFile()
		if filePath == '':
			print 'File must be saved!'
			return None

		self.currentTask = pm.getTask()

		version = cOS.getVersion(filePath)

		passName = shepherd.getKnob('Pass name').getValue()
		if not passName:
			print 'No passname!'
			return None

		outputDir = pm.getRenderPath(
			self.currentTask,
			passName,
			version
		)

		outputFile = pm.getRenderName(
			self.currentTask,
			passName,
			4,
			'exr'
		)

		self.outputDir = outputDir

		return cOS.normalizeAndJoin(outputDir, outputFile)

	def previewRender(self, shepherd, *args):

		if shepherd.getKnob('Camera').getValue():
			shepherd.getKnob('Preview Render').widget.setEnabled(False)
			jobData = self.getJobData(shepherd)

			cOS.makeDirs(cOS.ensureEndingSlash(self.outputDir))

			frame = shepherd.getKnob('Preview Frame').getValue()
			renderOptions = {
				'frame': frame,
				'renderNode': jobData['node']
			}
			self.renderSettings = {}
			previewRenderOption = shepherd.getKnob('Preview Render Options').getValue()
			if previewRenderOption == 'Progressive':
				maxRenderTime = shepherd.getKnob('Max. Preview Time').getValue() / 60.0
				self.renderSettings['progressiveMaxTime'] = maxRenderTime
			self.renderSettings.update(translator.getOption('vRayRenderPresets')[previewRenderOption])
			resolution = {
				'width': int(jobData['width'] * self.resolutionDict[shepherd.getKnob('Preview Resolution').getValue()]),
				'height': int(jobData['height'] * self.resolutionDict[shepherd.getKnob('Preview Resolution').getValue()]),
			}
			self.renderSettings.update(resolution)

			renderOptions['renderSettings'] = self.renderSettings
			renderOptions['output'] = shepherd.getKnob('output path').getValue().replace('%04d', str(frame) + '.preview')
			translator.previewRender(renderOptions)
			shepherd.getKnob('Preview Render').widget.setEnabled(True)

		else:
			shepherd.showError("Please Select a Camera to Preview")
