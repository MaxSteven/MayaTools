# Standard Modules
# import re
# import time

# Our Modules
import arkInit
arkInit.init()
# import cOS
import settingsManager
globalSettings = settingsManager.globalSettings()
# import pathManager
import HoudiniJob

class HoudiniMantra(HoudiniJob.HoudiniJob):

	defaultSubmitInfo = [
		{
			'job': {
				'Plugin': 'Houdini',
				'OverrideTaskExtraInfoNames': False, #?
			},
			'plugin': {
				'Build': '64bit',
				'GPUsPerTask': 0,
				'IgnoreInputs': 0,
				'OpenCLUseGPU': 0,
				'OutputDriver': '/obj/ropnet1/mantra1',
				'SelectGPUDevices': '',
				'Version': '16.0',
			}
		},
		{
			'job': {
				'Plugin': 'Mantra',
				'IsFrameDependent': True,
				'OverrideTaskExtraInfoNames': False, #?
			},
			'plugin': {
				'Threads': 1,
				'Version': '16.0',
			}
		},
	]

	def getPluginInfo(self, jobData, index=0):
		pluginInfo = super(self.__class__, self).getPluginInfo(jobData, index)
		if index == 0:
			pluginInfo.update({
				'SceneFile': jobData.get('file'),
			})
		return pluginInfo

	def getJobInfo(self, jobData, index=0):
		jobInfo = super(self.__class__, self).getJobInfo(jobData, index)
		if index == 0:
			jobInfo.update({
				'Name': jobInfo['Name'] + '-' + jobInfo.get('node')
			})
		elif index == 1:
			jobInfo.update({
				'Name': jobInfo['Name'] + '-Mantra Job'
			})
		return jobInfo

	def jobFromPrevious(self, result={}, index=0):
		jobInfo = {}
		if '_id' in result:
			jobInfo['JobDependency0'] = result['_id']
		if index == 0:
			jobInfo.pop('OutputFilename0', None)
		return jobInfo
