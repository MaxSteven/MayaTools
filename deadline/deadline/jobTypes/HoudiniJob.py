import DeadlineJob
import translators
translator = translators.getCurrent()

class HoudiniJob(DeadlineJob.DeadlineJob):

	def connectJobSignals(self, shepherd):
		shepherd.getKnob('rop').on('clicked', shepherd.updateFrameRange)
		shepherd.getKnob('rop').on('clicked', shepherd.updateOutputPath)

	def isValidRenderNode(self, shepherd):
		renderNodePath = shepherd.getKnob('rop').getValue()
		renderNode = translator.getNodeByPath(renderNodePath)
		return (renderNode != None)

	def getFrameRange(self, shepherd=None):
		frameRange = super(HoudiniJob, self).getFrameRange(shepherd=shepherd)
		if frameRange:
			return frameRange

		nodePath = shepherd.getKnob('rop').getValue()
		renderNode = translator.getNodeByPath(nodePath)
		if renderNode != None:
			return '-'.join([str(int(renderNode.getProperty('f1'))), str(int(renderNode.getProperty('f2')))])
		else:
			return 'Node no longer exists'

	# Override
	def getJobData(self, shepherd):
		jobData = super(HoudiniJob, self).getJobData(shepherd)

		nodePath = shepherd.getKnob('rop').getValue()
		renderNode = translator.getNodeByPath(nodePath)

		if shepherd.getKnob('rop').getValue() != '' and renderNode != None:
			translator.setRenderNode(renderNode)
			jobData.update(translator.getRenderProperties())
			del jobData['startFrame']
			del jobData['endFrame']

		jobData['previewPath'] = None
		jobData['chunkSize'] = None

		return jobData

	# Override
	def getKnobs(self, shepherd):
		knobs = super(HoudiniJob, self).getKnobs(shepherd)
		knobs[0:0] = [
				{
					'name': 'rop',
					'dataType': 'searchList',
					'options': self.getRenderNodes()
				}
			]
		return knobs

	def getRenderNodesKnob(self, shepherd):
		return shepherd.getKnob('rop')

	# Override
	def getRenderNodes(self):
		renderNodes = super(HoudiniJob, self).getRenderNodes()
		return [renderNode.getPath() for renderNode in renderNodes if not renderNode.nativeNode().isInsideLockedHDA()]
