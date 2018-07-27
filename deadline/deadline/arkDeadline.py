import collections

import sys
import os
import time

import Deadline.DeadlineConnect as Connect
import socket
import urllib2
import pathManager
deadlineIP = str(socket.gethostbyname(socket.gethostname()))

''' wrapper around Deadline for general render management functions '''
class ArkDeadline(object):

	def __init__(self, ip=deadlineIP, port=8082):
		try:
			self.connection = Connect.DeadlineCon(ip, port)
			connectString = self.connection.Repository.GetDatabaseConnectionString()
		except urllib2.URLError as err:
			self.ensureWebserviceRunning()
			self.connection = Connect.DeadlineCon(ip, port)

	def ensureWebserviceRunning(self):
		if sys.platform.startswith('win'):
			try:
				# this will exit if webservice already running
				os.system('C:/ie/ark/setup/deadlineWebservice_windowsHidden.vbs')
			except Exception as err:
				print 'Could not start webservice', err

		elif sys.platform.startswith('linux'):
			try:
				os.system('systemctl start deadlineWeb.service')

			except Exception as err:
				print 'Could not start webservice', err

		# for race conditions
		time.sleep(3)

	# Job
	################################################
	# returns dictionary of job information based on job id
	def getJob(self, jobID):
		return self.connection.Jobs.GetJob(jobID)

	def getJobsActive(self, username=None):
		# only jobs that are rendering, queued, or pending
		jobs = self.connection.Jobs.GetJobsInState('Active')

		if not username:
			return jobs

		jobs.sort(key=lambda x: x['Props']['Pri'], reverse=True)

		result = []
		for idx, job in enumerate(jobs):
			if job['Props']['Ex1'] == username:
				job['order'] = idx
				result.append(job)
		return result

	def getJobs(self, username=None):
		jobs = self.connection.Jobs.GetJobs()
		if username:
			return [job for job in jobs if job['Props']['Ex1'] == username]
		else:
			return jobs

	# jobs have too much info in deadline, only get what's useful
	def getJobInfo(self, job):
		statusMap = {
			'1': 'rendering',
			'2': 'suspended',
			'3': 'completed',
			'4': 'failed',
			'5': 'queued', # ?
			'6': 'pending',
		}
		jobInfo = {
			'id': job['_id'],
			'name': job['Props']['Name'],
			'plugin': job['Plug'],
			'frames': job['Props']['Frames'],
			'outDir': job['OutDir'][0] if len(job['OutDir']) else '',
			'status': statusMap[str(job['Stat'])],
			'suspended': job['SuspendedChunks'],
			'rendering': job['RenderingChunks'],
			'completed': job['CompletedChunks'],
			'pending': job['PendingChunks'],
			'failed': job['FailedChunks'],
			'queued': job['QueuedChunks'],
		}
		jobInfo['total'] = (
			jobInfo['suspended'] +
			jobInfo['rendering'] +
			jobInfo['completed'] +
			jobInfo['pending'] +
			jobInfo['failed'] +
			jobInfo['queued']
		)
		# deadline treats queued as rendering
		if job['Stat'] == 1 and not job['RenderingChunks']:
			jobInfo['status'] = 'queued'

		if job.get('order'):
			jobInfo['order'] = job['order']

		return jobInfo

	# returns dictionary of job information based on job name
	def getJobByName(self, name):
		pass

	def submitJob(self, jobInfo, pluginInfo):
		# submit scene file as 'auxiliary file' to get it copied to the repo
		if pluginInfo.get('SceneFile'):
			pluginInfo['SceneFile'] = pathManager.translatePath(pluginInfo['SceneFile'])
		aux = pluginInfo.pop('SceneFile', [])
		return self.connection.Jobs.SubmitJob(jobInfo, pluginInfo, aux)

	# updates job in database with all data in updateData (nested dictionary, keys can use dot notation)
	def updateJobData(self, jobID, updateData):
		job = self.getJob(jobID)
		newJob = self.update(job, updateData)
		return self.connection.Jobs.SaveJob(newJob)

	def suspendJob(self, jobID):
		return self.connection.Jobs.SuspendJob(jobID)

	# Sheep
	################################################
	def getSheepInfo(self, sheepName):
		return self.connection.Slaves.GetSlaveInfo(sheepName)

	def getSheepSettings(self, sheepName):
		settings = self.connection.Slaves.GetSlaveSettings(sheepName)
		if len(settings):
			return settings[0]
		else:
			raise Exception('Could not get sheep settings')

	def setSheepGroups(self, sheepName, groupNames):
		return self.connection.Slaves.SetGroupsForSlave(sheepName, groupNames)

	def updateSheepSettings(self, sheepName, settings):
		sheepSettings = self.getSheepSettings(sheepName)
		sheepSettings = self.update(sheepSettings, settings)
		return self.connection.Slaves.SaveSlaveSettings(sheepSettings)

	# Limit Groups
	################################################
	# returns dictionary of limit group information based on limit name
	def getLimitGroup(self, name):
		return self.connection.LimitGroups.GetLimitGroup(name)

	# adds sheep to limit group blacklist (or whitelist)
	# limitName can be a string or a list of limit names
	# sheepName can be a string or a list of sheep names
	def addSheepToLimitGroup(self, limitName, sheepName, blackList=True):
		if isinstance(limitName, list):
			limits = limitName
		else:
			limits = [limitName]

		if isinstance(sheepName, list):
			sheeps = sheepName
		else:
			sheeps = [sheepName]

		success = True
		for limit in limits:
			limitGroup = self.getLimitGroup(limit)
			limitGroup['Props']['Slaves'].extend([s for s in sheeps if not s in limitGroup['Props']['Slaves']])
			limitGroup['Props']['White'] = not blackList
			success = success and self.connection.LimitGroups.SaveLimitGroup(limitGroup) == 'Success'
		return success

	# removes sheep from limit group blacklist (or whitelist)
	# limitName can be a string or a list of limit names
	# sheepName can be a string or a list of sheep names
	def removeSheepFromLimitGroup(self, limitName, sheepName, blackList=True):
		if isinstance(limitName, list):
			limits = limitName
		else:
			limits = [limitName]

		if isinstance(sheepName, list):
			sheeps = sheepName
		else:
			sheeps = [sheepName]

		success = True
		for limit in limits:
			limitGroup = self.getLimitGroup(limit)
			limitGroup['Props']['Slaves'] = [s for s in limitGroup['Props']['Slaves'] if not s in sheeps]
			limitGroup['Props']['White'] = not blackList
			success = success and self.connection.LimitGroups.SaveLimitGroup(limitGroup) == 'Success'
		return success

	# helpers
	################################################
	# recursively merge nested dictionaries
	# can accept keys with dot notation
	def update(self, d, u, dotNotation=True):
		for k, v in u.iteritems():
			if dotNotation and '.' in k:
				kSplit = k.split('.')
				d[kSplit[0]] = self.update(d.get(kSplit[0], {}), {'.'.join(kSplit[1:]): v})
			else:
				if isinstance(v, collections.Mapping) and isinstance(d.get(k, {}), collections.Mapping):
					d[k] = self.update(d.get(k, {}), v)
				else:
					d[k] = v

		return d

if __name__ == '__main__':
	pass
	## testing (organize later)
	# ad = ArkDeadline()
	# print ad.removeSheepFromLimitGroup('mantra-license', 'Shobhit_Random')
	# print 'Shobhit_Random' not in ad.getLimitGroup('mantra-license')['Props']['Slaves']
	# print ad.addSheepToLimitGroup('mantra-license', 'Shobhit_Random')
	# print 'Shobhit_Random' in ad.getLimitGroup('mantra-license')['Props']['Slaves']
	# print ad.addSheepToLimitGroup('mantra-license', 'Shobhit_Random')
	# print 'Shobhit_Random' in ad.getLimitGroup('mantra-license')['Props']['Slaves']
	# print ad.removeSheepFromLimitGroup('mantra-license', 'Shobhit_Random')
	# print 'Shobhit_Random' not in ad.getLimitGroup('mantra-license')

	# ad = ArkDeadline()
	# print ad.updateJobData('59fa3cdf512acc2b20b483cd', {'Props':{'PlugInfo':{'StrictErrorChecking':'False'}}})
	# print ad.updateJobData('59fa3cdf512acc2b20b483cd', {'Props.PlugInfo.StrictErrorChecking':'False'})
	# print ad.getJob('59fa3cdf512acc2b20b483cd')['Props']['PlugInfo']['StrictErrorChecking']



	# test = {}
	# test = ad.update(test, {'a': {'b': 2}})
	# print test
	# test = ad.update(test, {'a': {'c': 3}})
	# print test
	# test = ad.update(test, {'a.d': 14, 'a.e': 15})
	# print test
	# test = ad.update(test, {'a': {'d': {}}})
	# print test
	# test = ad.update(test, {'a.d': {'e':145}})
	# print test
