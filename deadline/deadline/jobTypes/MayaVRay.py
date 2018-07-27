# Standard Modules
# import re

# Our Modules
import MayaJob
import arkInit
arkInit.init()
import cOS
# import time
import settingsManager
globalSettings = settingsManager.globalSettings()
import translators
translator = translators.getCurrent()

class MayaVRay(MayaJob.MayaJob):

	defaultSubmitInfo = [
		{
			'job': {
				'Plugin': 'MayaBatch',
				'Pool': 'all',
				'SecondaryPool': '',
				'PostTaskScript': 'S:/custom/scripts/Tasks/checkTaskOutputVray.py',
				'LimitGroups': 'maya-license',
			},
			'plugin': {
				'Animation': 1,
				'Build': '64bit',
				'CountRenderableCameras': 0,
				'IgnoreError211': 0,
				'Renderer': 'vrayExport',
				'UseLocalAssetCaching': 0,
				'Version': translator.getSoftwareVersion(),
				'StrictErrorChecking': False
			}
		},
		{
			'job': {
				'Plugin': 'Vray',
				'Pool': 'all',
				'SecondaryPool': '',
				'PostJobScript': 'S:/custom/scripts/Jobs/postVrayJob.py',
				'LimitGroups': 'vray-license',
			},
			'plugin': {
				'Height': 0,
				'SeparateFilesPerFrame': 1,
				'Threads': 0,
				'Width': 0,
			}
		},
		{
			'job': {
				'Plugin': 'DraftPlugin',
			},
			'plugin': {
				# uses default draft plugin info
			}
		},
	]

	def getPluginInfo(self, jobData, index=0):
		pathInfo = cOS.getPathInfo(jobData['output'])
		try:
			# try to use output filename as job name, it's more descriptive
			pathInfo['name'] = cOS.getSequenceBaseName(pathInfo['basename'], matchNumbersOnly=False)
		except:
			pass

		pluginInfo = super(self.__class__, self).getPluginInfo(jobData, index)
		if index == 0:
			pluginInfo.update({
				'OutputFilePath': pathInfo['dirname'],
				'OutputFilePrefix': pathInfo['name'],
				'ProjectPath': '/'.join(jobData.get('output').split('/')[:3]),
				'VRayExportFile': pathInfo['dirname'] + pathInfo['name'] + '.vrscene',
				'Camera': jobData['node'],
				'SceneFile': jobData.get('file'),
				'ImageWidth': jobData.get('width'),
				'ImageHeight': jobData.get('height'),
			})
		elif index == 1:
			pluginInfo.update({
				'InputFilename': pathInfo['dirname'] + pathInfo['name'] + \
					'_' + ('0' * cOS.getPadding(jobData['output'])) + '.vrscene'
			})
		elif index == 2:
			pluginInfo = self.getDraftPluginInfo(jobData)

		return pluginInfo

	def jobFromPrevious(self, result={}, index=0):
		jobInfo = {}
		if index == 1:
			if '_id' in result:
				jobInfo.update({
					'JobDependencies': result['_id'],
					'IsFrameDependent': True
				})
		elif index == 2:
			if '_id' in result:
				jobInfo.update({
					'JobDependencies': result['_id'],
				})
		return jobInfo

	def getJobInfo(self, jobData, index=0):
		jobInfo = super(self.__class__, self).getJobInfo(jobData, index)

		if index == 2:
			jobInfo = self.getDraftJobInfo(jobData)

		return jobInfo

	# def postSubmit(self, result):
		# possible bug in deadline, strict error checking can't be set with initial submission
		# self.arkDeadline.updateJobData(result['_id'], {'Props.PlugInfo.StrictErrorChecking':'False'})
