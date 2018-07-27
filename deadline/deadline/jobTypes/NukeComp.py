# Standard Modules
# import re
# import time

# Our Modules
import arkInit
arkInit.init()
import arkUtil
import cOS
import settingsManager
globalSettings = settingsManager.globalSettings()
# import pathManager
import NukeJob

class NukeComp(NukeJob.NukeJob):

	defaultSubmitInfo = [
		{
			'job': {
				'Plugin': 'Nuke',
				'Pool': 'comp-pool',
				'SecondaryPool': 'none',
				'LimitGroups': 'nuke-license',
			},
			'plugin': {
				'BatchMode': True,
				'BatchModeIsMovie': False,
				'ContinueOnError': False,
				'EnforceRenderOrder': False,
				'GpuOverride': 0,
				'NukeX': False,
				'PerformanceProfiler': False,
				'RamUse': 0,
				'RenderMode': 'Use Scene Settings',
				'StackSize': 0,
				'Threads': 0,
				'UseGpu': False,
				'Version': 10.0,
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
		pluginInfo = super(self.__class__, self).getPluginInfo(jobData, index)

		if index == 0:
			pluginInfo.update({
				'SceneFile': jobData.get('file'),
				'WriteNode': jobData.get('node'),
			})
		elif index == 1:
			pluginInfo = self.getDraftPluginInfo(jobData)

		return pluginInfo

	def jobFromPrevious(self, result={}, index=0):
		jobInfo = {}
		if index == 1:
			if '_id' in result:
				jobInfo.update({
					'JobDependencies': result['_id'],
				})
		return jobInfo

	def getJobInfo(self, jobData, index=0):
		jobInfo = super(self.__class__, self).getJobInfo(jobData, index)
		if index == 1:
			jobInfo = self.getDraftJobInfo(jobData)

		return jobInfo

