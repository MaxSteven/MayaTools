
# Standard modules
import os
import time
import re
import json
import traceback

# Our modules
import arkInit
arkInit.init()

import database

database = database.Database()
database.connect()

import cOS
import arkUtil
import socket

import pathManager
import settingsManager
globalSettings = settingsManager.globalSettings()

from TaskInfo import TaskInfo
from PathInfo import PathInfo

class Caretaker(object):

	assetTypes = None

	def __init__(self):
		self.userInfo = False

	def getTaskInfo(self):
		return TaskInfo(self)

	def getPathInfo(self, path):
		return PathInfo(self, path)

	def getIP(self):
		s = socket.socket(
			socket.AF_INET,
			socket.SOCK_DGRAM)
		s.connect((
				globalSettings.DATABASE_ROOT,
				int(globalSettings.DATABASE_PORT)
			))
		# fix: hardcoded ipv6 prefix currently
		ip = s.getsockname()[0]
		s.close()
		return ip

	def getUserInfo(self):
		# cache user info, use that if we have it
		if self.userInfo:
			return self.userInfo

		userInfoCache = globalSettings.ARK_CONFIG + 'userInfo.json'

		if database.checkHealth():
			userInfo = database\
				.findOne('user')\
				.where('token','is', database.key)\
				.execute()
			if not userInfo or not len(userInfo):
				raise Exception('Please log in to hub and restart the application.  Could not find user for token: ' + database.key)

			# cache user info to file in case the server goes down
			with open(userInfoCache, 'w') as f:
				json.dump(userInfo, f)
		else:
			# can't connect to database
			try:
				print 'Could not connect to server, loading cached user info...'
				with open(userInfoCache, 'r') as f:
					userInfo = json.load(f)
			except Exception as err:
				traceback.print_exc(err)
				raise Exception('Failed loading cached user info.')

		self.userInfo = userInfo
		return self.userInfo

	def getEntityFromField(self, entityType, field, val, entities=None):
		# optionally provide entities
		if entities:
			for entity in entities:
				if entity[field] == val:
					return entity
			return None

		# otherwise use database to find
		else:
			return database\
				.findOne(entityType)\
				.where(field,'is',val)\
				.execute()

	def getProjects(self, includeArchived=False):
		query = database.find('project').sort('folderName')
		if not includeArchived:
			query = query.where('archive','is not',True)
		return query.execute()

	def getProjectRootFromFolder(self, folderName):
		return globalSettings.SHARED_ROOT + folderName + '/'

	def getProjectFromPath(self, path):
		'''
		Input: path with a project folder
		Output: a dict with the project's basic information
		'''

		try:
			path = pathManager.removeSharedRoot(path)
		except:
			print 'Path does not start with shared root:', globalSettings.SHARED_ROOT
			path = ''
		parts = path.split('/')
		if len(parts) < 1:
			return None

		folderName = parts[0]

		query = database\
			.find('project')\
			.where('folderName', 'is', folderName)\
			.execute()
		try:
			response = query[0]
			return response
		except:
			return None

	def getProjectFromFolder(self, folderName):
		'''
		Input: folderName, the name (not path) of the project folder
		Output: a dict with the project's basic information
		'''
		query = database\
			.find('project')\
			.where('folderName', 'is', folderName)\
			.execute()
		try:
			response = query[0]
			return response
		except:
			return None

	def getShotFromName(self, shotName, project=None):
		'''
		Input: shotName: either the unique caretaker shotname (project abbreviation + shot name)
							or the shotname in a project folder
				project (optional): the caretaker id of the project that the shot belongs to
		Output: a dict with the shot's basic information
		'''
		if project:
			query = database\
				.find('shot')\
				.where('project', 'is', project)\
				.where('name', 'is', shotName)\
				.execute()
			try:
				allShots = query[0]
				return allShots
			except:
				return None
		else:
			query = database\
				.find('shot')\
				.where('name', 'is', shotName)\
				.execute()
			try:
				shot = query[0]
				return shot
			except:
				return None

	def getShotFromPath(self, path):
		shotName = self.getShotNameFromPath(path)
		return self.getShotFromName(shotName)

	def getShotNameFromPath(self, path):
		# mandates sequence shot
		# works for workspaces and final renders
		try:
			path = pathManager.removeSharedRoot(path)
		except:
			print 'Path does not start with shared root:', globalSettings.SHARED_ROOT
			path = ''
		parts = path.split('.')[0].split('/')

		if len(parts) < 4:
			return ''
		else:
			return parts[3]

	def getSequenceFromShot(self, shotName):
		shot = database.findOne('shot')\
				.where('name','is', shotName)\
				.execute()

		if not shot:
			print 'No shot found'
			return None

		# find the sequence by ID if it's set
		if 'sequence' in shot and shot['sequence']:
			sequence = database.findOne('sequence')\
				.where('_id','is',shot['sequence'])\
				.execute()

		# fix: this entire section is hax
		# shouldn't have shots without a sequence ever
		# otherwise try to find it or create it
		else:
			print 'Shot does not have a sequence'
			# grab TRO_208 from TRO_208_03_010
			potentialSequenceName = '_'.join(shot['name'].split('_')[:2])
			print 'Looking for sequence:', potentialSequenceName
			sequence = database.findOne('sequence')\
				.where('name','is',potentialSequenceName)\
				.execute()
			# if we couldn't find a sequence, make one
			if not sequence:
				print 'Sequence not found, creating:', potentialSequenceName
				sequence = database.create('sequence',
					{
						'project': shot['project'],
						'name': potentialSequenceName,
					}).execute()

			print 'Setting sequence on shot'
			database.update('shot')\
				.where('_id','is',shot['_id'])\
				.set('sequence', sequence['_id'])\
				.execute()

		if sequence:
			return sequence
		else:
			print 'No sequence found for shot:', shotName
			return None


	def getSequenceFromPath(self, path):
		# mandates sequence shot
		# works for workspaces and final renders
		try:
			path = pathManager.removeSharedRoot(path)
		except:
			print 'Path does not start with shared root:', globalSettings.SHARED_ROOT
			path = ''
		parts = path.split('/')

		if len(parts) < 3:
			return ''
		else:
			return parts[2]

	def getShotInfo(self, shot):
		'''
		Input: shot: the id of the shot that we want more info about
		Output: a dict with full information of the shot, including project and sequence info
		'''
		shotQuery = database\
			.find('shot')\
			.where('_id', 'is', shot)\
			.options('getLinks', True)\
			.execute()
		try:
			shotInfo = shotQuery[0]
			return shotInfo
		except:
			return None

	def getAssetsFromShot(self, shot, assetType=None):
		'''
		Input: shot: the id of the shot that we want the assets of
				assetType(optional): The id of an assetType
		Output: a list of dicts with Asset info for all the assets (of type assetType
				if assetType is specified) linked to the shot
		'''
		query = database\
			.find('asset')\
			.where('shot','is',shot)
		if assetType:
			query = query.where('type','is', assetType)
		response = query.execute()
		try:
			assets = response
			if assets:
				return assets
			return None
		except:
			return None

	def getAssetFromPath(self, assetPath):
		'''
		Input: assetPath: simply a path
		Output: a dict with information about the asset that has its path at assetPath
		'''
		version = database\
			.findOne('version')\
			.where('path', 'is', assetPath)\
			.execute()
		if not version:
			return None

		print 'version:', version['path']
		return database.findOne('asset')\
								.where('_id', 'is', version['asset'])\
								.execute()

	def getAssetFromName(self, name):
		'''
		Input: name: the name of the asset
		output: a dict with information about the asset
		'''
		query = database\
			.find('asset')\
			.where('name', 'is', name)\
			.execute()
		try:
			response = query[0]
			return response
		except:
			return None

	def getAssetVersions(self, asset):
		'''
		Input: an Asset ID
		Output: a list of all the versions linked to this asset
		'''
		versions = database\
			.find('version')\
			.where('asset', 'is', asset)\
			.execute()

		if len(versions):
			return versions
		else:
			return None

	def getVersionPadding(self, projectInfo):
		versionPadding = 4
		if projectInfo and 'versionPadding' in projectInfo:
			versionPadding = projectInfo['versionPadding']
		return versionPadding

	def getVersionString(self, projectInfo, versionNumber):
		versionPadding = self.getVersionPadding(projectInfo)
		return arkUtil.pad(versionNumber, versionPadding)

	def getFramePadding(self, projectInfo):
		framePadding = 4
		if projectInfo and 'framePadding' in projectInfo:
			framePadding = projectInfo['framePadding']
		return framePadding

	def getFramePaddingString(self, projectInfo):
		framePadding = self.getFramePadding(projectInfo)
		return '%0' + str(framePadding) + 'd'

	def getAssetTypes(self, forceUpdate=False):
		if self.assetTypes and not forceUpdate:
			return self.assetTypes

		self.assetTypes = database.find('assetType').fetch()
		return self.assetTypes

	def getAssetTypeFromAsset(self, assetInfo):
		def find():
			return self.getEntityFromField(
				'assetType',
				'_id',
				assetInfo['type'],
				self.assetTypes)

		if self.assetTypes:
			assetType = find()
			if assetType:
				return assetType

		self.getAssetTypes(forceUpdate=True)
		return find()

	def getAssetTypeFromName(self, assetTypeName):
		'''
		Input: the name of an assumed assetType
		Output: a dict with the information about this assetType, or None if the assetType does not exist
		'''
		def find():
			return self.getEntityFromField(
				'assetType',
				'name',
				assetTypeName,
				self.assetTypes)

		if self.assetTypes:
			assetType = find()
			if assetType:
				return assetType

		self.getAssetTypes(forceUpdate=True)
		return find()

	def buildAssetPath(self, assetInfo, versionInfo, projectInfo, sequenceInfo, shotInfo):
		# fix: this is super hacks
		# "R:/Blackish_s03/Final_Renders/BLA_302/EXR_Linear/BLA_302_003_030_v002/BLA_302_003_030_v002.1000.exr"
		# assetType = self.getAssetTypeFromAsset(assetInfo)

		# if assetType == 'compRender':
			versionString = self.getVersionString(
				projectInfo, versionInfo['number'])
			framePaddingString = self.getFramePaddingString(projectInfo)

			return '{0}{1}/Final_Renders/{2}/EXR_Linear/{3}_v{4}/{3}_v{4}.{5}.exr'.format(
				globalSettings.SHARED_ROOT,
				projectInfo['folderName'],
				sequenceInfo['name'],
				shotInfo['name'],
				versionString,
				framePaddingString)

	def addCompVersion(self,
		projectInfo,
		assetName,
		versionNumber,
		shotName,
		sequenceInfo,
		checkComp=True):
		# fix: this doesn't go here
		def getFrameRangeFromNukeScript(path):
			with open(path) as f:
				startFrame = False
				endFrame = False
				for line in f:
					matches = re.findall(r'first_frame ([0-9]+)$', line)
					if len(matches):
						startFrame = int(matches[0])
					matches = re.findall(r'last_frame ([0-9]+)$', line)
					if len(matches):
						endFrame = int(matches[0])

					if startFrame and endFrame:
						break

			if startFrame and endFrame:
				return {
					'startFrame': startFrame,
					'endFrame': endFrame,
					'duration': endFrame - startFrame + 1,
				}

		# bail if no project
		if not projectInfo or not projectInfo['_id']:
			print 'Invalid project:', projectInfo
			raise Exception('Invalid project: ' + str(projectInfo))

		# bail if no shot
		# (tools should run createAllShots for project first)
		shotInfo = self.getShotFromName(shotName, projectInfo['_id'])
		if not shotInfo:
			print 'Shot not found:', shotName
			raise Exception('Shot not found: ' + shotName)

		# if the asset doesn't exist, create it
		assetInfo = database.findOne('asset')\
			.where('shot','is', shotInfo['_id'])\
			.where('type','is', 'comp')\
			.execute()

		if not assetInfo:
			assetData = {
				'name': shotInfo['name'],
				'type': 'comp',
				'project': projectInfo['_id'],
				'shot': shotInfo['_id']
			}
			assetInfo = database.create('asset', assetData).execute()
			if assetInfo and len(assetInfo):
				assetInfo = assetInfo[0]

			# time.sleep(.5)
				print 'Created asset for:', shotInfo['name']
			else:
				print 'Error creating asset:', assetInfo

		# start building the version info
		versionInfo = {
				'name': 'EXR_Linear',
				'type': 'exr',
				'number': versionNumber,
				'extension':  'exr',
				'status':  'complete',
				'sequence':  True,
				'asset': assetInfo['_id'],
			}

		versionInfo['path'] = self.buildAssetPath(
				assetInfo,
				versionInfo,
				projectInfo,
				sequenceInfo,
				shotInfo)
		versionInfo['sourceFile'] = versionInfo['path']

		if checkComp:
			frameRange = cOS.getFrameRange(versionInfo['path'])
			# fix: hax for pre-project-version padding
			if not frameRange:
				versionInfo['path'] = versionInfo['path'].replace('_v0','_v')
			frameRange = cOS.getFrameRange(versionInfo['path'])

			if not frameRange:
				print 'Could not get frame range for: ' + versionInfo['path']
				raise Exception('Could not get frame range for: ' + versionInfo['path'])

			# fix: hax, just lobbing the version off to get the shot number
			# basically only works for final_renders
			compRoot = globalSettings.SHARED_ROOT + projectInfo['folderName'] + \
				'/Workspaces/' + sequenceInfo['name'] + '/' + shotName + '/Comp/'

			compPath = cOS.getHighestVersionFilePath(compRoot, extension='nk')
			if not compPath:
				print 'Error finding latest comp:', compRoot
				raise Exception('Error finding latest comp:' + compRoot)

			nukeFrameRange = getFrameRangeFromNukeScript(compPath)
			frameRange = cOS.getFrameRange(versionInfo['path'])

			if not frameRange:
				print 'Error getting frame range:', versionInfo['path']
				raise Exception('Error getting frame range: ' + versionInfo['path'])
			if not nukeFrameRange:
				print 'Error getting nuke frame range:', compPath
				raise Exception('Error getting nuke frame range: ' + compPath)

			if not frameRange['complete']:
				print 'EXRs not complete:', versionInfo['path']
				raise Exception('EXRs not complete: ' + versionInfo['path'])
			if frameRange['duration'] < nukeFrameRange['duration']:
				print 'Mismatched frame range'
				print 'Shot range:',frameRange['min'], frameRange['max']
				print 'Comp range:',nukeFrameRange['startFrame'], nukeFrameRange['endFrame']
				raise Exception('Mismatched frame range: ' + compPath)

			versionInfo.update({
					'startFrame': frameRange['min'],
					'endFrame': frameRange['max'],
					'sourceFile': compPath,
				})

		print 'Version:', versionInfo['path']
		existingVersion = database.findOne('version')\
			.where('asset', 'is', assetInfo['_id'])\
			.where('path', 'is', versionInfo['path'])\
			.execute()

		if existingVersion:
			print 'updating version'
			database\
				.update('version')\
				.where('_id','is',existingVersion['_id'])\
				.set(versionInfo)\
				.execute()

			return database.\
				findOne('version')\
				.where('_id','is',existingVersion['_id'])\
				.execute()
		else:
			print 'adding version'
			return database.create('version', versionInfo).execute()[0]

	# creates or updates the field of an entity with matching data
	def createOrUpdateEntityByField(self, entityType, fields, data):
		query = database\
			.findOne(entityType)
		fields = arkUtil.ensureArray(fields)

		for field in fields:
			if field not in data:
				raise Exception('Data must contain search field: ' + field)
			query = query.where(field,'is',data[field])\

		entity = query.fetch()

		if not entity:
			entity = database.create(entityType, data).execute()
			if not len(entity):
				raise Exception('Error creating entity: ' + entityType)
			entity = entity[0]
		else:
			result = database\
				.update(entityType)\
				.where('_id','is',entity['_id'])\
				.set(data)\
				.limit(1)\
				.execute()
			if not result or result['modified'] != 1:
				print result
				raise Exception('Error updating entity: ' + entityType)

		return entity

	def createShotsForFolder(self, folderName):
		# bail if we can't find the project
		matchingProject = database.find('project').where('folderName','is',folderName).execute()
		if not len(matchingProject):
			print 'No project found for:', folderName
			return None

		project = matchingProject[0]
		print '\n\nScanning:', project['folderName']

		# bail if workspaces doesn't exist
		projectRoot = globalSettings.SHARED_ROOT + folderName + '/Workspaces/'
		if not os.path.isdir(projectRoot):
			print 'No workspaces for:', folderName
			return None

		# find all the project's sequences
		projectSequences = database.find('sequence').where('project','is',project['_id']).execute()
		if len(projectSequences):
			sequences = dict((s['name'],s) for s in projectSequences)
		else:
			sequences = {}

		# get the shots for the project as well
		projectShots = database.find('shot').where('project','is',project['_id']).execute()
		shots=[]
		if projectShots:
			shots = [s['name'] for s in projectShots]

		# loop through the sequences
		sequenceDirs = os.listdir(projectRoot)
		sequenceDirs.sort()
		for sequenceName in sequenceDirs:
			if not os.path.isdir(projectRoot + sequenceName) or \
				sequenceName[0] == '.' or \
				'*' in sequenceName:
				continue

			# create the sequence if it's missing
			if sequenceName not in sequences:
				result = database.create('sequence',
							{
								'name': sequenceName,
								'project': project['_id']
							}).execute()
				sequences[sequenceName] = result[0]
				print 'Added sequence:', sequenceName

			# get the sequence info and root
			sequenceInfo = sequences[sequenceName]
			sequenceRoot = projectRoot + sequenceName + '/'

			# loop through the sequence's shot folders
			shotFolders = os.listdir(sequenceRoot)
			shotFolders.sort()
			for shotName in shotFolders:
				if not os.path.isdir(sequenceRoot + shotName) or \
					shotName[0] == '.' or \
					'*' in shotName:
					continue

				if shotName not in shots:
					result = database.create('shot',
								{
									'name': shotName,
									'project': project['_id'],
									'sequence': sequenceInfo['_id'],
								}).execute()
					print 'Added shot:', shotName

		print 'Scan complete'


	def createVersionsForFolder(self, folderName, existingVersions=False):
		results = database.find('project').where('folderName','is',folderName).execute()

		if not results:
			print 'No project found for:', folderName
			return

		project = results[0]
		searchRoot = globalSettings.SHARED_ROOT + folderName + '/Final_Renders/'

		if not os.path.isdir(searchRoot):
			print 'Not a project:', folderName
			return

		print '\n\nScanning:', folderName

		if not existingVersions:
			existingVersions = database\
					.find('version')\
					.execute()
			print 'Existing versions:', len(existingVersions)

		versionPaths = [v['path'].lower() for v in existingVersions]

		sequences = os.listdir(searchRoot)
		sequences.sort()
		for sequence in sequences:
			exrRoot = searchRoot + sequence + '/EXR_Linear/'
			if not os.path.isdir(exrRoot):
				# print 'Not a sequence:', sequence
				continue

			# get the version folders for that root
			versionFolders = os.listdir(exrRoot)
			versionFolders.sort()

			# collect missing versions
			missingVersions = []
			for versionName in versionFolders:
				found = False
				for path in versionPaths:
					if versionName.lower() in path:
						found = True

				if not found:
					missingVersions.append(versionName)

			missingVersions.sort()
			if not len(missingVersions):
				continue

			print '\n\n\nTrying to add versions:'
			print '\n  '.join(missingVersions)
			print '\n'

			for versionName in missingVersions:
				shotName = '_'.join(versionName.split('_')[:-1])
				versionNumber = cOS.getVersion(versionName)

				try:
					print '\n', shotName, 'v%04d' % versionNumber
					self.addCompVersion(
						projectInfo=project,
						assetName=shotName,
						versionNumber=versionNumber,
						shotName=shotName,
						sequenceInfo={'name': sequence})
				except Exception as err:
					print 'Error adding:', shotName, versionNumber
					print err

		print 'Scan complete'

# WIP: will be much more elaborate and contain file checks, folder checks etc.
	def checkFilename(self, filename):
		filePathInfo = cOS.getPathInfo(filename)
		if len(filePathInfo['name'].split('_')) >= 3:
			return True
		else:
			return False

	def versionUpWithInitials(self, filepath):
		'''
		Takes in filepath and replaces initials and either adds a version or
		increments version according to the name
		'''
		if not filepath:
			return

		userInfo = self.getUserInfo()
		if not userInfo:
			return

		pathInfo = cOS.getPathInfo(filepath)

		# A/B/C_d_v0001_xy.nk
		if self.checkFilename(filepath):

			# oldUser = "xy.0001".split('.')[0] = xy
			oldUser = pathInfo['name'].split('_')[-1].split('.')[0]

			# "A/B/C_d_v0001_xy.nk".replace("_xy.", "_zz.")
			newFilepath = filepath.replace('_{}.'.format(oldUser), '_{}.'.format(userInfo['initials']))

			# "A/B/C_d_v0002_zz.nk"./
			newFilepath = cOS.incrementVersion(newFilepath)

		# if file doesn't belong to any shot
		else:
			extension = filepath.split('.')[-1]

			# if the file has versionInfo
			if cOS.getVersion(filepath):
				newFilepath = cOS.incrementVersion(filepath)

			else:
				newFilepath = filepath.split('.')[0] + '_v0001.' +  extension

		return newFilepath

	def createAllShots(self):
		root = globalSettings.SHARED_ROOT

		allProjects = os.listdir(root)
		allProjects.sort()
		for folderName in allProjects:
			self.createShotsForFolder(folderName)
			time.sleep(.5)

	def addVersions(self):
		root = globalSettings.SHARED_ROOT
		allProjects = os.listdir(root)

		existingVersions = database\
			.find('version')\
			.execute()
		print '\n\n\nExisting versions:', len(existingVersions)

		allProjects.sort()
		for folderName in allProjects:
			self.createVersionsForFolder(folderName, existingVersions)

def main():
	pass
	# caretaker = Caretaker()
	# print caretaker.getUserInfo()
	# caretaker.addVerions()
	# database = Database()
	# database.find('user').where('')
	# print caretaker.versionUpWithInitials('r:/Test_Project/Workspaces/publish/pathTest/cg/pathTest_v0011_ghm.mb')

if __name__ == '__main__':
	main()
