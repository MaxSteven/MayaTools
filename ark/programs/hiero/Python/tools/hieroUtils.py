import os

import re
import json

import hiero.core

import cOS

import arkUtil
from database import Database

import settingsManager
globalSettings = settingsManager.globalSettings()

def getActiveProject():
	return hiero.core.projects()[-1]

def getProjectRoot():
	activeProject = getActiveProject()
	if activeProject:
		return cOS.normalizeDir(activeProject.projectRoot())

def getWorkspacesRoot():
	projectRoot = getProjectRoot()
	if projectRoot:
		return projectRoot + 'WORKSPACES/'

def fixMultiShots():
	workspacesRoot = getWorkspacesRoot()

	multiBases = []
	lastShot = ''
	allShots = os.listdir(workspacesRoot)
	allShots.sort()
	for shot in allShots:
		shotBase = shot[:-1]
		if shotBase == lastShot and re.match('[A-Za-z]',shot[-1]):
			multiBases.append(shotBase)
		else:
			lastShot = shotBase

	for shot in allShots:
		shotBase = shot[:-1]
		if shotBase in multiBases:
			commonRoot = workspacesRoot + shotBase + '/'
			if not os.path.isdir(commonRoot):
				os.mkdir(commonRoot)
			cOS.copyTree(workspacesRoot + shot, commonRoot, True)
			print shot + ' copied to: ' + commonRoot

def test():
	print 'Selection Info'

	activeView = hiero.ui.activeView()
	# if you're not in the TimelineBin you can't have a selection
	if not activeView:
		return

	itemSelection = activeView.selection()
	print dir(itemSelection[0])
	print itemSelection[0].parentTrack()
	print itemSelection[0].parentTrack().name()

def createCaretakerShots():
	projectRoot = getProjectRoot()
	if not projectRoot:
		return False

	# caretaker has no function named createShotsFromDirectory...
	raise Exception('This should never happen?')
	# caretaker.createShotsFromDirectory(projectRoot)

def exportCDLPerShot():
	itemSuffix = '_CDLEffect'
	database = Database()
	database = database.connect()

	sequence = hiero.ui.activeSequence()
	projectPath = sequence.project().path()
	folderName = projectPath.split('/')[1]
	print 'Project Folder:', folderName
	project = database.findOne('project').where('folderName','is',folderName).execute()
	if not project:
		return

	print 'Project found:', project
	tracks = sequence.videoTracks()
	for track in tracks:
		if not track.isEnabled():
			print 'Skipping disabled track:', track.name()
			continue
		print 'Exporting CDLs for:', track.name()
		for item in track.items():
			if itemSuffix in item.name():
				print 'Removing CDL:', item.name()
				track.removeItem(item)

		for item in track.items():
			# get the edl comment string
			if 'foundry.edl.editString' not in item.metadata():
				print item.name(), ' - No metadata'
				continue
			comment = item.metadata()['foundry.edl.editString']
			asc_sop = re.search('ASC_SOP \(([\-0-9\.]+) ([\-0-9\.]+) ([\-0-9\.]+)\)\(([\-0-9\.]+) ([\-0-9\.]+) ([\-0-9\.]+)\)\(([\-0-9\.]+) ([\-0-9\.]+) ([\-0-9\.]+)\)', comment)
			# pull out the CDL params
			asc_sat = re.search('ASC_SAT ([\-0-9\.]+)', comment)

			# bail if the params aren't found
			if not asc_sop or not asc_sat:
				continue

			# convert the params to float values
			asc_sop = [float(param) for param in asc_sop.groups()]
			asc_sat = float(asc_sat.groups()[0])

			# create a CDL track effect and apply it to the track item
			effect = track.createEffect('OCIOCDLTransform', trackItem=item)
			node = effect.node()
			cdl = {
				'slope': (asc_sop[0],asc_sop[1],asc_sop[2]),
				'offset': (asc_sop[3],asc_sop[4],asc_sop[5]),
				'power': (asc_sop[6],asc_sop[7],asc_sop[8]),
				'saturation': asc_sat,
			}

			node['slope'].setValue(cdl['slope'])
			node['offset'].setValue(cdl['offset'])
			node['power'].setValue(cdl['power'])
			node['saturation'].setValue(cdl['saturation'])
			effect.setName(arkUtil.getAlphaNumericOnly(item.name()) + itemSuffix)

			data = {
				'startFrame': item.sourceIn(),
				'endFrame': item.sourceOut(),
				'cdl': json.dumps(cdl)
			}

			result = database\
				.update('shot')\
				.where('name','is',item.name())\
				.set(data)\
				.execute()

			if not result['modified']:
				print item.name(), ' - Shot not found, please add shots first'
			else:
				print item.name(), ' - Success!'

def exportLUTFromEDL():
	itemSuffix = '_LUTEffect'
	database = Database()
	database = database.connect()

	# sequence info
	sequence = hiero.ui.activeSequence()
	if not sequence:
		raise Exception('Please open a sequence first')

	# find the project based on the sequence
	projectPath = sequence.project().path()
	folderName = projectPath.split('/')[1]
	print 'Project Folder:', folderName
	project = database.findOne('project').where('folderName','is',folderName).execute()
	if not project:
		raise Exception('No project found')

	lutRoot = '%s/%s/IO/Luts/%s/' % (
		globalSettings.RAMBURGLAR,
		project['folderName'],
		sequence.name())

	print 'lut folder:', lutRoot
	try:
		lutFiles = os.listdir(lutRoot)
	except Exception as err:
		print 'Could not find lut folder: ' + lutRoot
		raise err
		# raise Exception('Could not find lut folder: ' + lutRoot)

	# go through the video tracks in the sequence
	print 'Project found:', project
	tracks = sequence.videoTracks()
	for track in tracks:

		# skip disabled tracks
		if not track.isEnabled():
			print 'Skipping disabled track:', track.name()
			continue

		# remove existing luts
		print 'Exporting LUTs for:', track.name()
		for item in track.items():
			if itemSuffix in item.name():
				print 'Removing CDL:', item.name()
				track.removeItem(item)

		# export lut per track item
		for item in track.items():
			# get the edl comment string
			if 'foundry.edl.editString' not in item.metadata():
				print item.name(), ' - No metadata'
				continue

			comment = item.metadata()['foundry.edl.editString']
			# pull out the LUT params
			sourceFile = re.search('SOURCE FILE\:[\s]+([A-Z0-9_]+)', comment)
			clipName = re.search('CLIP NAME\:[\s]+([A-Z0-9_\-]+)', comment)

			# bail if the params aren't found
			if not sourceFile or not clipName or \
				not len(sourceFile.groups()) or not len(clipName.groups()):
				print 'Bad LUT info:', comment
				continue

			# # convert the params to float values
			sourceFile = sourceFile.groups()[0]
			clipName = clipName.groups()[0]

			lutPath = False
			for lut in lutFiles:
				if sourceFile in lut and clipName in lut:
					lutPath = lut

			if not lutPath:
				print item.name(), ' - No lut found', lutRoot + sourceFile, clipName
				continue

			# create a LUT track effect and apply it to the track item
			effect = track.createEffect('OCIOFileTransform', trackItem=item)
			node = effect.node()

			node['file'].setValue(lutRoot + lutPath)
			# set the working colorspace based on the source media
			lutWorkingSpace = item.sourceMediaColourTransform()
			node['working_space'].setValue(lutWorkingSpace)
			effect.setName(arkUtil.getAlphaNumericOnly(item.name()) + itemSuffix)

			# save that data in the database
			data = {
				'startFrame': item.sourceIn(),
				'endFrame': item.sourceOut(),
				'lut': lutRoot + lutPath,
				'lutWorkingSpace': lutWorkingSpace,
			}
			result = database\
				.update('shot')\
				.where('name','is',item.name())\
				.set(data)\
				.execute()

			if not result['modified']:
				print item.name(), ' - Shot not found, please add shots first'
			else:
				print item.name(), ' - Success!'
