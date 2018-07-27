
import os

import arkInit
arkInit.init()

import settingsManager
globalSettings = settingsManager.globalSettings()
import translators

translator = translators.getCurrent()

import baseWidget
import cOS

import arkFTrack
pm = arkFTrack.getPM()

validPlateExtensions = [
	'dpx',
	'exr',
	'tif',
	'tiff',
	'jpg',
	'jpeg',
]


options = {
	'title': 'Shot Importer',
	'width': 600,
	'height': 1000,
	'x': 100,
	'y': 100,
	'knobs': [
		{
			'name': 'heading',
			'dataType': 'heading',
			'value': 'Shot Importer'
		},
		{
			'name': 'Projects',
			'dataType': 'searchList',
			'selectionMode': 'single'
		},
		{
			'name': 'Sequences',
			'dataType': 'searchList',
			'selectionMode': 'single'
		},
		# {
		# 	'name': 'Shots From Directory',
		# 	'dataType': 'Directory',
		# 	'value': globalSettings.SHARED_ROOT,
		# },
		{
			'name': 'Allow shot pasting',
			'dataType': 'checkbox'
		},
		{
			'name': 'Shots List',
			'dataType': 'listBox',
			'selectionMode': 'multi'
		},
		{
			'name': 'Shots Text',
			'dataType': 'text',
			'multiline': True
		},
		{
			'name':'Get Conversions',
			'dataType': 'PythonButton',
			'callback': 'getConversions'
		},
		{
			'name': 'Conversions',
			'dataType': 'listBox',
			'selectionMode': 'multi',
		},
		{
			'name': 'Sort Shots',
			'dataType': 'checkbox',
			'value': False,
		},
		{
			'name': 'Import Final Render',
			'dataType': 'checkbox',
			'value': True,
		},
		{
			'name': 'Import Offline',
			'dataType': 'checkbox',
			'value': True,
		},
		{
			'name': 'Import A Plate',
			'dataType': 'radio',
			'options': ['full res','proxy','none'],
			'value': 'full res',
		},
		{
			'name': 'Import Other Plates',
			'dataType': 'radio',
			'options': ['full res','proxy','none'],
			'value': 'none',
		},
		{
			'name': 'Import Shots',
			'dataType': 'PythonButton',
			'callback': 'importShots',
		},
		# 		{
		# 	'name': 'Import Latest CG',
		# 	'dataType': 'PythonButton',
		# 	'callback': 'importLatestCG',
		# },
	]
}

def getLatestConversion(shotName, sequenceRoot, conversionType):
	shot = pm.getByField('Shot', 'name', shotName, multiple=False)
	shotName = pm.getRenderShotName(shot)

	conversionRoot = cOS.ensureEndingSlash(cOS.normalizeAndJoin(
		sequenceRoot,
		conversionType
	))
	conversionNames = os.listdir(conversionRoot)
	conversionNames.sort()
	latestVersion = -999
	latestConversion = None
	for conversionName in conversionNames:
		version = cOS.getVersion(conversionName)
		if shotName in conversionName and version > latestVersion:
			latestConversion = conversionName
			latestVersion = version

	if latestConversion:
		if os.path.isdir(os.path.join(conversionRoot, latestConversion)):
			files = cOS.getFiles(os.path.join(conversionRoot, latestConversion), depth = 1)
			files = cOS.collapseFiles(files)
			if len(files) > 0:
				files = files[0].rpartition(' ')[0]
				return files
			else:
				return None
		else:
			return os.path.join(conversionRoot, latestConversion)

def getShotPlates(shotName, sequenceRoot):
	platesRoot = cOS.normalizeAndJoin(
		sequenceRoot,
		shotName,
		'Plates/')
	if not os.path.isdir(platesRoot):
		platesRoot = platesRoot.replace('/Plates/','/plates/')
		if not os.path.isdir(platesRoot):
			print 'No plate folder found'
			return []
	rawFiles = cOS.collectAllFiles(platesRoot)
	rawFiles = [f['path'] for f in rawFiles]
	sequences = cOS.collapseFiles(rawFiles)
	plates = []
	for s in sequences:
		s = s.split(' ')[0]
		extension = cOS.getExtension(s)
		if extension in validPlateExtensions:
			plates.append(s.split(' ')[0])
	return plates


class ShotImporter(baseWidget.BaseWidget):

	def init(self):
		self.projects = dict((project['name'], project['id']) for project in pm.getAll('Project'))

	def postShow(self):
		self.assignShotAttributesFlag = False
		self.getKnob('Projects').on('clicked', self.updateSequences)
		self.getKnob('Sequences').on('clicked', self.updateShotList)
		self.getKnob('Shots List').on('changed', self.getShots)
		self.getKnob('Shots Text').on('changed', self.getShots)
		self.getKnob('Allow shot pasting').on('changed', self.changeShotFormat)
		self.changeShotFormat()
		self.createProjectsList()
		self.shots = []
		self.shotNames = []
		self.sequenceObjects = []
		self.shotObjects = {}
		self.projectID = None
		self.project = None
		self.currentSeqObject = None

	def createProjectsList(self, *args):
		self.projectList = []

		try:
			for project in self.projects:
				self.projectList.append(project)
		except:
			return

		self.getKnob('Projects').clear()
		self.getKnob('Projects').addItems(self.projectList)

	def updateSequences(self, *args):
		self.getKnob('Shots List').clear()
		selectedProject = self.getKnob('Projects').getValue()
		self.projectID = self.projects.get(selectedProject)
		self.project = pm.get('Project', self.projectID)

		sequenceQuery = pm.getByField('Sequences', 'parent_id', self.project['id'], multiple=True)
		episodeQuery = pm.getByField('Episode', 'parent_id', self.project['id'], multiple=True)
		folderQuery = pm.getByField('Folder', 'parent_id', self.project['id'], multiple=True)

		self.sequenceObjects = []
		if sequenceQuery:
			self.sequenceObjects.extend(sequenceQuery.all())
		if folderQuery:
			self.sequenceObjects.extend(folderQuery.all())
		if episodeQuery:
			self.sequenceObjects.extend(episodeQuery.all())

		sequences = [sequence['name'] for sequence in self.sequenceObjects]

		sequencesList = []
		try:
			for sequence in sequences:
				sequencesList.append(sequence)
		except:
			return

		self.getKnob('Sequences').clear()
		self.getKnob('Sequences').addItems(sequencesList)

	def updateShotList(self, *args):
		currentSeq = self.getKnob('Sequences').getValue()
		self.currentSeqObject = None

		for seq in self.sequenceObjects:
			if seq['name'] == currentSeq:
				self.currentSeqObject = seq
				break

		self.shotObjects = {}
		if self.currentSeqObject:
			for obj in seq['descendants']:
				if obj.entity_type == 'Shot':
					self.shotObjects.update({obj['name'] : obj})
		else:
			print 'no shots found for this sequence'

		shots = list(self.shotObjects.keys())

		shotList = []
		try:
			for shot in shots:
				shotList.append(shot)
		except:
			return

		shotList.sort()
		self.getKnob('Shots List').clear()
		self.getKnob('Shots List').addItems(shotList)

		directory = pm.getPath(self.currentSeqObject)
		self.sequenceRoot = cOS.ensureEndingSlash(directory)
		self.conversionRoot = self.sequenceRoot.replace('Workspaces','Final_Renders')

	def changeShotFormat(self, *args):
		if self.getKnob('Allow shot pasting').getValue():
			self.hideKnob('Shots List')
			self.getKnob('Shots List').clearSelection()
			self.showKnob('Shots Text')

		else:
			self.hideKnob('Shots Text')
			self.showKnob('Shots List')

	# get Notes from a Shot and its descendants
	def getNotes(self, shot):
		notes = []

		if shot['object_type']['name'] == 'Shot':
			for note in shot['notes']:
				notes.append(note['content'])

			for task in shot['descendants']:
				for note in task['notes']:
					n = note['content'].encode('ascii', 'ignore').decode('ascii')
					notes.append('{} : {}'.format(task['name'], n))

		return notes

	# get Shotnames from shot Text
	def getShots(self, *args):
		# set flg as false so that if user changes shot directory,
		# then assignShotAttribtes should runs again\
		if not self.getKnob('Allow shot pasting').getValue():
			self.assignShotAttributesFlag = False
			self.shotNames = cOS.ensureArray(self.getKnob('Shots List').getValue())

		else:
			shotNameText = self.getKnob('Shots Text').getValue()
			self.shotNames = [name.strip() for name in shotNameText.split('\n') if name != '']

	# get conversion types available for shots if they exist
	def getConversions(self):
		# if assignShotAttributes has already run then no need to run it again.
		if not self.assignShotAttributesFlag:
			self.assignShotAttributes()

		conversionTypes = []
		if not len(self.shotNames):
			return self.showError('No Shots selected.')

		for shotName in self.shotNames:

			# make a dictionary w/ an empty array for each shot

			for f in os.listdir(self.conversionRoot):
				if os.path.isdir(os.path.join(self.conversionRoot, f)) and \
				f != 'EXR_Linear' and \
				f not in conversionTypes:
					conversionTypes.append(f)

		self.getKnob('Conversions').clear()
		self.getKnob('Conversions').addItems(conversionTypes)

	# Assign various shot attributes based on shotText
	def assignShotAttributes(self):
		if not len(self.shotNames):
			self.showError('No shots to import')
			self.getKnob('Conversions').clear()
			return

		# if no sequence was found throughout entire shotList
		if not self.sequenceRoot:
			self.showError('Could not find a sequence for any of the specified shots')
			self.getKnob('Conversions').clear()
			return

		# set flag as True so that it does not need to be run again.
		self.assignShotAttributesFlag = True

	def importShots(self):
		# if assignShotAttributes has already run then no need to run it again.
		if not self.assignShotAttributesFlag:
			self.assignShotAttributes()

		self.shotDictList = []
		self.shots = []
		self.getShots()

		if self.getKnob('Sort Shots').getValue():
			self.shotNames.sort()

		for shotName in self.shotNames:
			shotClips = self.getShotClips(shotName)
			if shotClips:
				self.shots.append(shotClips)
			shotObject = self.shotObjects[shotName]
			# if shotObject:
			# 	self.getNotes(shotObject)

		self.createSequence()

	# def importLatestCG(self):
	#	pass

	def getShotClips(self, shotName):
		shotClips = {}

		if self.getKnob('Import Final Render').getValue():
			latestVersion = getLatestConversion(shotName, self.conversionRoot, 'EXR_Linear')
			if latestVersion:
				shotClips['finalRender'] = [latestVersion]

		conversions = self.getKnob('Conversions').getValue()
		if len(conversions):
			shotClips['conversions'] = []
			for conversionType in conversions:
				latestConversion = getLatestConversion(shotName, self.conversionRoot, conversionType)
				if latestConversion:
					shotClips['conversions'].append(latestConversion)
				else:
					shotClips['conversions'].append(False)

		otherPlatesMode = self.getKnob('Import Other Plates').getValue()
		if otherPlatesMode != 'none':
			allPlates = getShotPlates(shotName, self.sequenceRoot)
			if otherPlatesMode == 'full res':
				otherPlates = [p for p in allPlates if '_a_' not in p.lower() and 'offline' not in p.lower() and 'proxy' not in p.lower()]
			else:
				otherPlates = [p for p in allPlates if '_a_' not in p.lower() and 'offline' not in p.lower() and 'proxy' in p.lower()]

			otherPlates.sort()

			# fix: cull v001 if v002 exists, etc
			shotClips['otherPlates'] = otherPlates

		aPlatesMode = self.getKnob('Import A Plate').getValue()
		if aPlatesMode != 'none':
			allPlates = getShotPlates(shotName, self.sequenceRoot)
			if aPlatesMode == 'full res':
				aPlates = [p for p in allPlates if '_a_' in p.lower() and 'proxy' not in p.lower()]
			else:
				aPlates = [p for p in allPlates if '_a_' in p.lower() and 'proxy' in p.lower()]

			aPlates.sort()
			if len(aPlates):
				# only use the latest A plate (highest version #)
				shotClips['aPlate'] = [aPlates[-1]]

		if self.getKnob('Import Offline').getValue():
			allPlates = getShotPlates(shotName, self.sequenceRoot)
			offlinePlates = [p for p in allPlates if 'offline' in p.lower()]
			offlinePlates.sort()

			if len(offlinePlates):
				# only use the latest offline (highest version #)
				shotClips['offline'] = [offlinePlates[-1]]

		return shotClips

	def createSequence(self):
		import hiero.core

		# setup
		currentProject = hiero.core.projects()[-1]
		self.clipsBin = currentProject.clipsBin()
		sequence = hiero.core.Sequence('ReviewSequence')
		sequenceBinItem = hiero.core.BinItem(sequence)
		self.clipsBin.addItem(sequenceBinItem)

		# create the tracks
		if self.getKnob('Import Offline').getValue():
			offlineTrack = hiero.core.VideoTrack('Offline')
			sequence.addTrack(offlineTrack)

		if self.getKnob('Import A Plate').getValue() != 'none':
			aTrack = hiero.core.VideoTrack('APlate')
			sequence.addTrack(aTrack)

		if self.getKnob('Import Other Plates').getValue() != 'none':
			numOtherPlateTracks = 0
			for shot in self.shots:
				if ('otherPlates' in shot and
					len(shot['otherPlates']) > numOtherPlateTracks):
					numOtherPlateTracks = len(shot['otherPlates'])
			otherPlateTracks = []
			for i in range(numOtherPlateTracks):
				track = hiero.core.VideoTrack('OtherPlates_%04d' % i)
				otherPlateTracks.append(track)
				sequence.addTrack(track)

		if self.getKnob('Conversions').getValue() != None:
			conversionNames = self.getKnob('Conversions').getValue()
			conversionTracks = []
			for conversion in conversionNames:
				track = hiero.core.VideoTrack(conversion)
				conversionTracks.append(track)
				sequence.addTrack(track)

		if self.getKnob('Import Final Render').getValue():
			finalRendersTrack = hiero.core.VideoTrack('FinalRender')
			sequence.addTrack(finalRendersTrack)

		# add the clips
		self.currentTime = 0
		self.maxDuration = 0

		def addTrack(clipPath, track):
			try:
				# create and import the clip
				clipSource = hiero.core.MediaSource(clipPath)
				clip = hiero.core.Clip(clipSource)
				self.clipsBin.addItem(hiero.core.BinItem(clip))
			except Exception as err:
				print 'faild to load:', clipPath, err
				return

			# turns '/some/path/170_240_v001.%04d.exr' to '170_240_v001'
			clipName = clipPath.split('/')[-1].split('.')[0]
			trackItem = track.createTrackItem(clipName)
			trackItem.setSource(clip)

			duration = trackItem.sourceDuration()
			if duration < 1:
				print 'clip had invalid duration:', clipPath
				return
			if duration > self.maxDuration:
				self.maxDuration = duration

			trackItem.setTimelineIn(self.currentTime)
			trackItem.setTimelineOut(self.currentTime + duration - 1)
			# add notes to the track item
			# tag = hiero.core.Tag('NAME GOES HERE')
			# tag.setNote('ACTUAL COMMENT GOES HERE')
			# trackItem.addTag(tag)
			track.addItem(trackItem)

			return trackItem

		for shot in self.shots:
			trackItems = []
			self.maxDuration = 0
			if 'offline' in shot:
				trackItems.append(addTrack(shot['offline'][0], offlineTrack))

			if 'aPlate' in shot:
				trackItems.append(addTrack(shot['aPlate'][0], aTrack))

			if 'otherPlates' in shot:
				for i, plate in enumerate(shot['otherPlates']):
					trackItems.append(addTrack(plate, otherPlateTracks[i]))

			if 'conversions' in shot:
				for i, plate in enumerate(shot['conversions']):
					if plate:
						trackItems.append(addTrack(plate, conversionTracks[i]))

			if 'finalRender' in shot:
				trackItems.append(addTrack(shot['finalRender'][0], finalRendersTrack))

			for trackItem in trackItems:
				if not trackItem:
					continue
				trackItemDuration = trackItem.sourceDuration()
				timeDiff = self.maxDuration - trackItemDuration

				if timeDiff > 0 and trackItemDuration > 0:
					newStartTime = self.currentTime + int(timeDiff * 0.5)

					# set end time first
					# end time must always be greater than start time
					# otherwise Hiero complains

					trackItem.setTimelineOut(newStartTime + trackItemDuration - 1)
					trackItem.setTimelineIn(newStartTime)

			self.currentTime += self.maxDuration

		hiero.ui.openInTimeline(sequenceBinItem)


def launch(parent=None, *args, **kwargs):
	translator.launch(ShotImporter, parent, options=options, *args, **kwargs)

if __name__ == '__main__':
	launch()
