import os

import arkInit
arkInit.init()

import settingsManager
globalSettings = settingsManager.globalSettings()

import arkFTrack
pm = arkFTrack.getPM()

import translators
translator = translators.getCurrent()

import arkUtil
import deadline
ad = deadline.arkDeadline.ArkDeadline()

import baseWidget
import cOS
from deadline import jobTypes
# import submit
from translators import QtGui
import updateModules

currentApp =  os.environ.get('ARK_CURRENT_APP')

class DeadlineSubmit(baseWidget.BaseWidget):
	currentJob = None

	defaultOptions = {
		'title': 'Deadline Submit',
		'width': 700,
		'align': 'top'
	}

	sortedJobDataFields = [
			'jobType',
			'program',
			'sourceFile',
			'version',
			'name',
			'node',
			'frameRange',
			'fps',
			'width',
			'height',
			'nearPlane',
			'farPlane',
			'priority',
			'previewPath',
			'output'
		]

	def init(self):
		self.currentTask = pm.getTask()

		self.jobData = {}
		self.updateShots()
		# Given the way our nasewidget works self.knobholder does not exist if there
		# are no knobs in the default options

		try:
			self.knobHolder
		except AttributeError:
			self.createGUI()

	def postShow(self):
		jobTypes = arkUtil.sort(translator.getOption('jobTypes'))
		jobListDict = {
			'name': 'job type',
			'dataType': 'list',
			'options': jobTypes
		}
		self.addKnobFromDict(jobListDict)
		self.getKnob('job type').on('changed', self.changeJob)
		self.changeJob()

	# temporary hack for deadline transition
	# deadline jobs named differently
	def deadlineJobType(self, shepherdJobType):
		shepherdToDeadline = {
			'Maya_VRayStandalone': 'MayaVRay',
			'Nuke_Comp': 'NukeComp',
			'Houdini_Mantra': 'HoudiniMantra',
		}
		if shepherdJobType in shepherdToDeadline.keys():
			return shepherdToDeadline.get(shepherdJobType)
		else:
			return shepherdJobType

	def changeJob(self, *args):
		for knob in self.allKnobs():
			if knob.name != 'job type':
				self.removeKnob(knob.name)
		jobType = self.deadlineJobType(self.getKnob('job type').getValue())
		jobClass = getattr(jobTypes, jobType)
		self.currentJob = jobClass()
		knobs = self.currentJob.getKnobs(self)
		for knob in knobs:
			self.addKnobFromDict(knob)
		self.currentJob.changeJob()
		self.currentJob.connectJobSignals(self)

	def isValidClippingPlanes(self):
		return self.currentJob.isValidClippingPlanes(self)

	def isValidFrameRange(self):
		return self.currentJob.isValidFrameRange(self)

	def validateJob(self):
		return self.currentJob.validateJob(self)

	def isValidTask(self):
		return self.currentJob.isValidTask(self)

	def isValidRenderNode(self):
		return self.currentJob.isValidRenderNode(self)

	def refresh(self):
		self.currentJob.refresh(self)

	# Should avoid doing thins for Nuke takes time and is unnecessary
	def updateShots(self):
		folders = cOS.getFiles(self.getWorkspaceRoot(),
						folderExcludes=['.*'],
						fileExcludes=['*'],
						depth=1,
						fullPath=True)
		# dictionary to store sequence for every shot
		self.shotSequence = {}
		shots = []
		for folder in folders:
			folderSections = folder.split('/')
			if len(folderSections) == 5:
				# dict {shotName : sequenceName}
				self.shotSequence[folderSections[-1]] = folderSections[-2]
				shots.append(folderSections[-1])

		self.shots = arkUtil.sort(shots)

	def getJobData(self):
		return self.jobData

	def getShots(self):
		return self.shots

	def getShotSequence(self, shotName):
		return self.shotSequence.get(shotName)

	def getSourceFile(self):
		return translator.getFilename()

	def getVersion(self):
		return cOS.getVersion(self.getSourceFile())

	def getWorkspaceRoot(self):
		project = self.currentTask.get('project')
		if not project:
			return None
		else:
			return cOS.normalizeAndJoin(pm.getPath(project), 'Workspaces/')

	def updateFrameRange(self):
		frameRange = self.currentJob.getFrameRange(self)
		self.getKnob('frame range').setValue(frameRange)

	def updateJobData(self):
		updatedJobData = self.currentJob.getJobData(self)
		self.jobData = updatedJobData

	def updateOutputPath(self, *args):
		outputPath = self.currentJob.getOutputPath(self)
		self.getKnob('output path').setValue(outputPath)

	def updatePassName(self):
		passName = self.currentJob.getPassName(self)
		self.getKnob('pass name').setValue(passName)

	def updateRenderNodes(self):
		if not self.currentJob.getRenderNodesKnob(self):
			return
		renderNodesKnob = self.currentJob.getRenderNodesKnob(self)
		updatedRenderNodes = self.currentJob.getRenderNodes()
		renderNodesKnob.clear()
		renderNodesKnob.addItems(updatedRenderNodes)

	# webservice needs to be running to use the deadline api, start it if not running
	def submit(self):
		sceneError = self.checkSceneError()
		if sceneError:
			return self.showError(sceneError)

		if self.checkToolsVersion():
			return self.showError('Did not submit job.')

		confirm = QtGui.QMessageBox(self)
		confirm.setText('<h2 style="color: #e7e7e7">' +
			'Job Settings</h2>')

		jobDataText = '<table>'
		for field in self.sortedJobDataFields:
			jobDataText += '''
				<tr>
					<td style="color: #e7e7e7; padding:2px 8px; vertical-align: top; text-align: right">%s:</td>
					<td style="padding:2px 8px; vertical-align: top; white-space: nowrap">%s</td>
				</tr>''' % (field, self.jobData.get(field))

		jobDataText += '</table>'

		confirm.setInformativeText(jobDataText)

		confirm.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
		confirm.setDefaultButton(QtGui.QMessageBox.No)

		confirm.resize(1000, 1000)
		confirm.setWindowTitle('Job settings')

		confirmed = confirm.exec_()

		if confirmed == QtGui.QMessageBox.Yes:
			try:
				self.jobData = translator.preSubmit(self.jobData)
			except Exception as err:
				return self.showError(str(err))

			if not translator.getOption('appHandlesSubmit'):

				data = self.jobData
				data['jobType'] = self.deadlineJobType(data['jobType'])
				print 'Submitting job:', data

				jobDataError = self.checkJobDataError(data)
				if jobDataError:
					return self.showError(jobDataError)

				job = jobTypes.getJobClass(data['jobType'])
				if not job:
					print 'No job class found:', data['jobType']
					return self.showError('ERROR: No job class found')

				result = job.submit(data)
				print 'Submit result:', result

				popup = QtGui.QMessageBox(self)
				updateStatus = False
				if result and type(result) == list and len(result):
					result = 'Submitted successfully!'
					if self.currentTask:
						result += ' Set task "{}" status to "Rendering on Farm"?'.format(self.currentTask['name'])
						popup.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
						updateStatus = True

					if self.getKnob('Suspend Old Versions').getValue():
						self.suspendPreviousVersions()

				else:
					result = 'Failed to submit job: ' + str(result)

				popup.setText(str(result))
				response = popup.exec_()

				if updateStatus and response == QtGui.QMessageBox.Yes:
					status = pm.getByField('Status', 'name', 'Rendering on Farm')
					pm.update(self.currentTask, 'status_id', status['id'])

			if translator.getOption('closeOnSubmit'):
				self.close()

		translator.postSubmit(self.jobData)

	def suspendPreviousVersions(self):
		task = pm.getTask()
		activeJobs = ad.getJobsActive()
		version = self.jobData.get('version')

		if version:
			for job in activeJobs:
				if job['Props']['Ex3'] == task['id'] and int(job['Props']['Ex5']) < version:
					ad.suspendJob(job['_id'])
					print 'Suspending job', job['_id']

	def checkToolsVersion(self):
		if updateModules.needsUpdate():
			confirm = QtGui.QMessageBox(self)

			confirm.setText('You are not submitting with the latest tools version! ' +
				'This may cause slow render times, job errors, or worse. Submit anyway?')

			confirm.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
			confirm.setDefaultButton(QtGui.QMessageBox.No)
			confirm.setWindowTitle('Tools version warning')
			response = confirm.exec_()
			return not response == QtGui.QMessageBox.Yes
		else:
			return False

	# returns error string, or false if no error
	def checkJobDataError(self, data):
		if not data['sourceFile']:
			print 'No sourceFile:', data
			return 'ERROR: No sourceFile'

		if not data['jobType']:
			print 'No jobType:', data
			return 'ERROR: No jobType'

		return False

	# returns error string, or false if no error
	def checkSceneError(self):
		try:
			self.updateJobData()
		except Exception as err:
			return err

		if not self.isValidTask():
			return 'Invalid Task'

		if not self.isValidClippingPlanes():
			# just a warning
			self.showError('Your camera clipping ranges are set too far apart. Set the near clip to .1 or even 1 if ' + \
					'you\'re not rendering a macro scene, and set the far clip as near to the end of the scene as you can.')

		if not self.isValidRenderNode():
			return 'The selected render node could not be found'

		if not self.isValidFrameRange():
			return 'Invalid frame range.  Ex: "1-100" or "52, 64-90"'

		try:
			self.validateJob()
		except ValueError as err:
			return err

		try:
			translator.setOutputFilename(self.jobData['output'], self.jobData)
		except Exception as err:
			return err

		return False


def launch(docked=False):
	translator.launch(DeadlineSubmit, docked=docked)

if __name__ == '__main__':
	launch()

