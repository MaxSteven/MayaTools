# import pathManager
import cOS
import arkUtil

import DeadlineJob
import translators
translator = translators.getCurrent()

class NukeJob(DeadlineJob.DeadlineJob):
	frameRange = translator.getAnimationRange()
	renderNodeTypes = ['write']

	# Override
	def getKnobs(self, shepherd):
		knobs = super(NukeJob, self).getKnobs(self)
		knobs[-4:-4] = [
				{
					'name': 'Chunk Size',
					'dataType': 'Int',
					'value': 5
				}
			]

		# Could have better efficiency
		for knob in knobs:
			if knob.get('name') == 'frame range':
				frameRange = translator.getAnimationRange()
				knob['value'] = str(frameRange.get('startFrame')) + '-' + str(frameRange.get('endFrame'))
		return knobs

	def connectJobSignals(self, shepherd):
		if not translator.getRenderNode():
			translator.setRenderNode(translator.getSelectedNode())
		shepherd.updateOutputPath()

	def getJobData(self, shepherd):
		jobData = super(NukeJob, self).getJobData(shepherd)
		filepath = shepherd.getSourceFile()
		pathInfo = cOS.getPathInfo(filepath)
		jobData['program'] = 'nuke'
		jobData['fps'] = 24
		jobData['name'] = pathInfo['name']
		try:
			jobData['node'] = translator.getRenderNode().name()
		except:
			raise Exception('No node selected!')
		jobData['previewPath'] = None
		jobData['chunkSize'] = shepherd.getKnob('Chunk Size').getValue()
		jobData['height'] = translator.getRenderProperty('height')
		jobData['width'] = translator.getRenderProperty('width')
		jobData['farPlane'] = None
		jobData['nearPlane'] = None

		return jobData

	def getOutputPath(self, shepherd):
		return translator.getOutputFilename()

	def isValidRenderNode(self, shepherd):
		renderNode = shepherd.getJobData()['node']
		return translator.getNodeByName(renderNode).getType() in ('write', 'finalrender', 'ieprecomp')

	def changeJob(self):
		pass
