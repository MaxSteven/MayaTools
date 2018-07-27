
# Standard modules
import os
import re
import datetime
import traceback
import math

# Our modules
import arkInit
arkInit.init()
import cOS
import arkUtil
import pathManager
import settingsManager
globalSettings = settingsManager.globalSettings()
import translators
translator = translators.getCurrent()
import deadline
import arkFTrack
pm = arkFTrack.getPM()

class DeadlineJob(object):

	defaultSubmitInfo = []

	timeout = False
	# minimum size a file must be to be 'valid'
	minFileSize = 5
	# 10,000 lines in the buffer
	outputBufferLength = 10000
	sceneJobs = ['MayaVRay']
	compJobs = ['NukeComp']
	fxJobs = []

	extraInfo = {
		'toolsVersion': 'ExtraInfo0',
		'username': 'ExtraInfo1',
		'name': 'ExtraInfo2',
		'taskID': 'ExtraInfo3',
		'shotID': 'ExtraInfo4',
		'version': 'ExtraInfo5',
	}

	def __init__(self):
		self.arkDeadline = deadline.arkDeadline.ArkDeadline()

	# Submission
	##################################################
	def submit(self, data):
		data['file'] = pathManager.translatePath(data['sourceFile'], 'windows')
		data['output'] = pathManager.translatePath(data['output'], 'windows')

		result = {}
		results = []

		# for every job in job
		# (job may consist of multiple dependent jobs)
		for index in range(self.numberOfJobs()):
			jobInfo = self.getJobInfo(data, index)
			jobInfo.update(self.jobFromPrevious(result, index))
			cOS.makeDirs(jobInfo['OutputDirectory0'])

			pluginInfo = self.getPluginInfo(data, index)
			pluginInfo.update(self.pluginFromPrevious(result, index))

			result = self.arkDeadline.submitJob(jobInfo, pluginInfo)
			if isinstance(result, str) and result.startswith('Error'):
				return False

			self.postSubmit(result)
			results.append(result)
			print 'Raw submit result:', result

		return results

	def preSubmit(self, jobData, translator):
		pass

	def postSubmit(self, result):
		pass

	def changeJob(self):
		translator.setOptions(renderNode=None)

	def sortFrameRange(self, frameRange, chunkSize):
		frameSequences = frameRange.split(',')
		parsedSequences = []

		for frameSequence in frameSequences:
			framesParsed = arkUtil.parseFrameRange(frameSequence)
			start = framesParsed[0]
			end = framesParsed[-1]
			if (chunkSize == 1):
				length = end - start + 1
				if length == 1:
					parsedSequences.append('{}-{}'.format(start, end))
				frames = ''
				step = length
				while step > 1:
					step = int(.5 * step)
					frames += "%d-%dx%d, " % (start, end, step)
				parsedSequences.append(frames)
			else:
				# make list of all chunks
				framesParsed = ['{}-{}'.format(s, min(s + chunkSize - 1, end)) for s in range(start, end + 1, chunkSize)]
				framesOrdered = [framesParsed[0]]

				step = len(framesParsed) - 1

				while step >= 1:
					# step through list but only if element is not already in orderedlist
					nextStep = [n for n in framesParsed[::step] if not n in framesOrdered]
					framesOrdered.extend(nextStep)
					step = int(.5 * step)

				# check that all frames are included
				if not len(framesParsed) == len(framesOrdered):
					print len(framesParsed), len(framesOrdered)
					print sorted(framesOrdered)
					raise Exception('Did not parse frame range correctly.')

				parsedSequences.append(','.join(framesOrdered))

		return ','.join(parsedSequences)

	# returns dictionary of job info for deadline
	# use index to get plugin info for chain of dependent jobs
	def getJobInfo(self, jobData, index=0):
		pathInfo = cOS.getPathInfo(jobData['output'])

		# Get chunk size if it exists, otherwise set chunk size to one
		chunkSize = jobData.get('chunkSize', 1) if jobData.get('chunkSize', 1) else 1

		jobInfo = {
			'Name': jobData['name'],
			'BatchName': jobData['name'],
			'UserName': 'ie',
			'Frames': self.sortFrameRange(jobData['frameRange'], chunkSize),
			'ChunkSize': chunkSize,
			'MachineLimit': jobData.get('sheepLimit', 0),
			'Priority': jobData.get('priority', 50),
			'OutputFilename0': self.deadlinePadding(pathInfo.get('basename')),
			'OutputDirectory0': pathInfo.get('dirname'),
			'Group': 'good-software',
			'EnableAutoTimeout': True,
		}
		jobInfo.update(self.getExtraJobInfo())
		if index in range(len(self.defaultSubmitInfo)):
			jobInfo.update(self.defaultSubmitInfo[index]['job'])

		return jobInfo

	# try to submit user info and tools version along with job
	def getExtraJobInfo(self):
		extraJobInfo = dict()
		try:
			userInfo = pm.getUser()
			extraJobInfo.update({
				self.extraInfo['name']: pm.getName(),
				self.extraInfo['username']: userInfo.get('username'),
				self.extraInfo['taskID']: pm.getTaskID(),
				self.extraInfo['shotID']: pm.getShotID(),
				self.extraInfo['version']: cOS.getVersion(translator.getFilename())
			})
		except:
			pass

		try:
			import updateModules
			extraJobInfo.update({
				self.extraInfo['toolsVersion']: updateModules.getLatestDirectory(remote=False)
			})
		except:
			pass

		return extraJobInfo

	# returns dictionary of plugin info for deadline
	# use index to get plugin info for chain of dependent jobs
	def getPluginInfo(self, jobData, index=0):
		return self.defaultSubmitInfo[index]['plugin']

	# get additional job info from result of submitting previous job
	def jobFromPrevious(self, result={}, index=0):
		return {}

	# get additional plugin info from result of submitting previous job
	def pluginFromPrevious(self, result={}, index=0):
		return {}

	def numberOfJobs(self):
		return len(self.defaultSubmitInfo)

	# Draft
	##################################################
	# returns job info for basic h264 draft job
	def getDraftJobInfo(self, jobData):
		pathInfo = cOS.getPathInfo(jobData['output'])
		try:
			pathInfo['name'] = cOS.getSequenceBaseName(pathInfo['basename'], matchNumbersOnly=False)
		except:
			pass

		jobInfo = self.getJobInfo(jobData, index=-1)

		# for draft, use original frame range!
		jobInfo['Frames'] = jobData['frameRange']

		if not pm.getTask():
			return None

		# houdini draft jobs should include render node in job name and output file
		if jobData.get('program') == 'houdini' and jobData.get('node'):
			jobInfo['Name'] = jobInfo['Name'] + ' - ' + jobData.get('node')
			pathInfo['name'] = pathInfo['name'] + '_' + jobData.get('node').split('/')[-1]

		jobInfo.update({
			'Plugin': 'DraftPlugin',
			'ChunkSize': 1000000,
			'OutputFilename0': self.getDraftName(jobData),
			'OutputDirectory0': self.getDraftFolder(jobData),
			'Name': jobInfo['Name'] + ' - h264',
		})

		if pm.getTask().get('project') and pm.getInfo(pm.getTask()['project'], 'autoQuicktime'):
			jobInfo['PostTaskScript'] = 'S:/custom/scripts/Jobs/uploadToFtrack.py'

		return jobInfo

	# returns plugin info for basic h264 draft job
	def getDraftPluginInfo(self, jobData):
		frames = arkUtil.parseFrameRange(jobData['frameRange'])
		draftFolder = self.getDraftFolder(jobData)
		pathInfo = cOS.getPathInfo(jobData['output'])
		try:
			pathInfo['name'] = cOS.getSequenceBaseName(pathInfo['basename'], matchNumbersOnly=False)
		except:
			pass

		annotationsString = jobData.get('annotationsString', 'None')

		return {
			'ScriptArg0': 'resolution="1"',
			'ScriptArg1': 'codec="h264"',
			'ScriptArg10': 'frameRate="24"',
			'ScriptArg11': 'quickType="createMovie"',
			'ScriptArg12': 'isDistributed="False"',
			'ScriptArg2': 'colorSpaceIn="Identity"',
			'ScriptArg3': 'colorSpaceOut="Draft sRGB"',
			'ScriptArg4': 'annotationsString="{}"'.format(annotationsString),
			'ScriptArg5': 'annotationsImageString="None"',
			'ScriptArg6': 'annotationsResWidthString="None"',
			'ScriptArg7': 'annotationsResWidthString="None"',
			'ScriptArg8': 'annotationsFramePaddingSize="None"',
			'ScriptArg9': 'quality="70"',
			'ScriptArg13': 'frameList={}-{}'.format(str(frames[0]), str(frames[-1])),
			'ScriptArg14': 'startFrame=' + str(frames[0]),
			'ScriptArg15': 'endFrame=' + str(frames[-1]),
			'ScriptArg16': 'outFolder="' + draftFolder + '"' ,
			'ScriptArg17': 'outFile="' + draftFolder + '/' + pathInfo['name'] + '.mov"',
			'ScriptArg18': 'inFile="' + pathInfo.get('dirname') + self.deadlinePadding(pathInfo.get('basename')) + '"',
			'scriptFile': 'S:/events/DraftEventPlugin/DraftQuickSubmission/QuickDraft.py',
		}

	def getDraftName(self, jobData):
		task = pm.getTask()
		passname = None

		if jobData.get('program') in ('maya', 'vray'):
			# parse pass name fom job name
			passname = jobData.get('name', '').split('_')[-1]

		elif jobData.get('program') == 'houdini':
			# include render node name
			passname = jobData.get('node', '').split('/')[-1]

		return pm.getDailiesFile(task, filename=translator.getFilename(), passname=passname)

	# returns <project>/Dailies/<currentDate>
	# creates folder if doesn't exist
	def getDraftFolder(self, jobData):
		draftFolder = pm.getDailiesPath(pm.getTask(), checkPath=translator.getFilename())
		cOS.makeDirs(pathManager.translatePath(draftFolder + '/'))
		return draftFolder

	# Helpers
	##################################################
	# replaces .%04d. with .####.
	def deadlinePadding(self, path):
		padding = cOS.getPadding(path)
		digitsPadding = re.compile('\.%\d+d')
		path = cOS.normalizeFramePadding(path)
		return re.sub(digitsPadding, '.' + ('#' * padding), path)

	def getOutputPaths(self):
		outputPath = cOS.unixPath(self.jobInfo['output'])
		# translate the path for the current OS
		outputPath = pathManager.translatePath(outputPath)

		outputPaths = []

		if 'frameRange' in self.jobInfo and self.jobInfo['frameRange']:
			if '%' not in outputPath:
				raise Exception('Output path missing % for frame padding')
			frames = arkUtil.parseFrameRange(self.jobInfo['frameRange'])
			outputPaths = [outputPath.strip() % frame for frame in frames]
		else:
			outputPaths = [outputPath.strip()]


		# begin silly hax to fix Renders vs renders folders cuz Linux vs Windows = :(
		dirName = cOS.getDirName(outputPaths[0])
		# if dir name exists as is just return
		if os.path.isdir(dirName):
			return outputPaths

		# if lowercase renders folder exists, replace it in output paths and return
		lowercaseRenderDir = dirName.replace('/Renders/','/renders/')
		if os.path.isdir(lowercaseRenderDir):
			print 'upper to lower:', outputPaths[0].replace(dirName, lowercaseRenderDir)
			return [p.replace(dirName, lowercaseRenderDir) for p in outputPaths]

		# if uppercase renders folder exists, replace it in output paths and return
		capitalRenderDir = dirName.replace('/renders/','/Renders/')
		if os.path.isdir(capitalRenderDir):
			print 'lower to upper:', outputPaths[0].replace(dirName, lowercaseRenderDir)
			return [p.replace(dirName, capitalRenderDir) for p in outputPaths]

		# if no folder exists, use the lowercase one and return output paths
		return [p.replace(dirName, lowercaseRenderDir) for p in outputPaths]


	# New methods, please keep clean
	renderNodeTypes = []
	jobDataFields=[
			'farPlane',
			'fps',
			'frameRange',
			'height',
			'jobType',
			'name',
			'nearPlane',
			'node',
			'output',
			'previewPath',
			'priority',
			'program',
			'sourceFile',
			'version',
			'width',
			'chunkSize'
		]

	def connectJobSignals(self, shepherd):
		pass

	def isValidClippingPlanes(self, shepherd):
		far = shepherd.jobData.get('farPlane')
		near = shepherd.jobData.get('nearPlane')
		if far and near:
			# checks magnitude of far and near values
			farMag = int(math.floor(math.log10(far)))
			nearMag = int(math.floor(math.log10(near)))

			return (farMag - nearMag) < 7
		return True

	def isValidFrameRange(self, shepherd):
		frameRangeText = shepherd.getKnob('frame range').getValue()
		frameRange = arkUtil.parseFrameRange(frameRangeText)
		return (len(frameRange) > 0)

	def isValidTask(self, shepherd):
		return pm.hasCurrentTask()

	def isValidRenderNode(self, shepherd):
		pass

	# Get frame range start and end from string frameRange
	# "1, 2, 3" --> {start: 1, end: 3}
	# "1" --> {start: 1, end: 1}
	def getFrameRange(self):
		if self.jobInfo.get('frameRange'):
			frames = arkUtil.parseFrameRange(self.jobInfo['frameRange'])
			return {
				'startFrame': int(frames[0]),
				'endFrame': int(frames[-1])}
		else:
			self.error('Error: job does not have a frameRange. getFrameRange should not have been called')
			return None

	def getJobData(self, shepherd):
		jobData = {}
		jobData['frameRange'] = shepherd.getKnob('frame range').getValue().strip()
		jobData['jobType'] = shepherd.getKnob('job type').getValue()
		jobData['priority'] = str(int(shepherd.getKnob('priority').getValue())).strip()
		jobData['sourceFile'] = shepherd.getSourceFile()
		jobData['version'] = shepherd.getVersion()
		jobData['output'] = shepherd.getKnob('output path').getValue()
		return jobData

	# UI
	def getKnobs(self, shepherd):
		knobs = [
			{
				'name': 'frame range',
				'dataType': 'text'
			},
			{
				'name': 'priority',
				'dataType': 'int',
				'value': 50
			},
			{
				'name': 'Suspend Old Versions',
				'dataType': 'checkbox',
				'value': True
			},
			{
				'name': 'output path',
				'dataType': 'text',
				'readOnly': True
			},
			{
				'name': 'Refresh',
				'dataType': 'PythonButton',
				'callback': 'refresh'
			},
			{
				'name': 'Submit',
				'dataType': 'PythonButton',
				'callback': 'submit'
			}
		]
		return knobs

	def getRenderNodesKnob(self, shepherd):
		pass

	def getRenderNodes(self):
		renderNodes = []
		for renderNodeType in self.renderNodeTypes:
			renderNodes += translator.getNodesByType(renderNodeType, recurse=True)
		return renderNodes

	def getOutputPath(self, shepherd):
		pass

	def refresh(self,shepherd):
		shepherd.updateRenderNodes()

	def validateJob(self, shepherd):
		currentJobFields = arkUtil.sort(shepherd.getJobData().keys())
		if set(self.jobDataFields) != set(currentJobFields):
			raise ValueError('Missing job fields')
		nonEmptyJobs = [value for value in shepherd.getJobData().values() if value == '']
		if len(nonEmptyJobs) != 0:
			raise ValueError('Job fields are incomplete check for missing entries')


if __name__ == '__main__':
	pass
