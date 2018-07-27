# Standard modules
# import os
# import time
# import re

# Our modules
import arkInit
arkInit.init()

import database

database = database.Database()
database.connect()

import cOS
import arkUtil

import database

database = database.Database()
database.connect()

# import pathManager
import re
import settingsManager
globalSettings = settingsManager.globalSettings()


# drives
ramburglar = cOS.ensureEndingSlash(globalSettings.RAMBURGLAR)
assetRoot = cOS.ensureEndingSlash(globalSettings.ASSET_ROOT)

# path templates
_sourcePathDir = ramburglar + '{project}/Workspaces/{sequence}/{shot}/{asset}/'

_renderPathAbsoluteShort = ramburglar + '{project}/Workspaces/{sequence}/{shot}/R|renders/{versionName}/'
_renderPathAbsolute = _renderPathAbsoluteShort + '{versionNumber}/'

_publishPathAbsoluteShort = ramburglar + '{project}/Workspaces/{sequence}/{shot}/P|publish/{versionName}/'
_publishPathAbsolute = _publishPathAbsoluteShort + '{versionNumber}/'

_assetPathRelative = '{assetChunk}/{assetID}/{versionID}/'
_assetPathAbsolute = assetRoot + _assetPathRelative

# filename template
_filename = '{versionName}_{versionPadding}_{initials}.{extension}'


# Path/dict utilities
##################################################

def isAbsolutePath(filepath):
	if cOS.isLinux():
		drives = [v['linux'] for k,v in globalSettings.PATHS.iteritems()]
		drives.append('/')
	elif cOS.isWindows():
		drives = [v['windows'] for k,v in globalSettings.PATHS.iteritems()]
		drives.append('c:/')
	return any([filepath.find(drive) == 0 for drive in drives])

def isAbsoluteData(data):
	return 'absolutePath' in data and data['absolutePath']

def isAssetPath(filepath):
	return not re.match(globalSettings.ASSET_ROOT, filepath) == None

def isPublishPath(filepath):
	return arkUtil.matchesText(_publishPathAbsoluteShort, filepath)

def isRenderPath(filepath):
	return arkUtil.matchesText(_renderPathAbsoluteShort, filepath)

def getPublishDataFromPath(path):
	data = arkUtil.parse(_publishPathAbsolute, path)
	if not data:
		data = arkUtil.parse(_publishPathAbsoluteShort, path)
		data['versionNumber'] = ''
	return data

def getRenderDataFromPath(path):
	data = arkUtil.parse(_renderPathAbsolute, path)
	if not data:
		data = arkUtil.parse(_renderPathAbsoluteShort, path)
		data['versionNumber'] = ''
	return data

# builds dictionary from path
def getDataFromPath(path, absolutePath = True):
	data = None
	if absolutePath:
		# new asset path
		if isAssetPath(path):
			data = arkUtil.parse(_assetPathAbsolute, path)
		# old asset path
		else:
			if isPublishPath(path):
				data = getPublishDataFromPath(path)
			elif isRenderPath(path):
				data = getRenderDataFromPath(path)
	else:
		# use relative paths only for new asset path
		data = arkUtil.parse(_assetPathRelative, path)
	return data

# builds path from dictionary
def getPathFromData(assetData):
	if assetData['absolutePath']:
		# assetdata should know whether it's a render or publish
		if arkUtil.matchesData(_renderPathAbsolute, assetData):
			template = _renderPathAbsolute
		elif arkUtil.matchesData(_renderPathAbsolute, assetData):
			template = _renderPathAbsolute

		elif arkUtil.matchesData(_publishPathAbsoluteShort, assetData):
			template = _publishPathAbsoluteShort
		elif arkUtil.matchesData(_publishPathAbsoluteShort, assetData):
			template = _publishPathAbsoluteShort

		elif arkUtil.matchesData(_assetPathAbsolute, assetData):
			template = _assetPathAbsolute
		else:
			return None
	else:
		template = _assetPathRelative
		if not 'assetChunk' in assetData:
			assetData['assetChunk'] = assetData['assetID'][:5]
	return arkUtil.expand(template, assetData)


# Database operations
##################################################

# find versions where asset is assetID and field is fieldValue
# ex: getLatestVersionByField(, 'sourceFile', True)
def getLatestVersionByField(assetID, field, fieldValue):
	return database\
		.find('version')\
		.where('asset','is',assetID)\
		.where(field,'is',fieldValue)\
		.execute()

# find asset
# find project where id is asset.project and users contains current user
# return True if project found, otherwise False
# untested lol
def getAssetAccess(assetID, userID):
	asset = database\
		.find('asset')\
		.where('_id','is',assetID)\
		.execute()
	if len(asset) == 0:
		return False
	project = database\
		.find('project')\
		.where('_id','is',asset[0]['project'])\
		.where('users','contains',userID)\
		.execute()
	if len(project) == 0:
		return False
	return project[0]['users']


def main():
	pass

if __name__ == '__main__':
	main()




# thumbnail
# $assetRoot\59555\59555c57ab3e387968da5478\59654ffbb3f2cb025c2fcda3\file.jpg
# path: file.jpg

# exr sequence
# $assetRoot\59555\59555c57ab3e387968da5478\59654ffbb3f2cb025c2fcda3\file.%04d.exr
# path: file.%04d.exr

# alembic
# $assetRoot\59555\59555c57ab3e387968da5478\59654ffbb3f2cb025c2fcda3\file.abc
# path: file.abc

# quicktime
# $assetRoot\59555\59555c57ab3e387968da5478\59654ffbb3f2cb025c2fcda3\file.mov
# path: file.mov


# R:\Caretaker\Assets\<asset_id_chunk>/<asset_id>/<version_id>/<version.path>



# Existing Paths


# Final_Renders (comp renders)
# r:/project/final_renders/sequence/exr_linar/shot/shot.%04d.exr

# Auto Converts
# r:/project/final_renders/sequence/postingType (ProRes444)/shot/shot.%04d.exr

# CG Renders
# r:/project/workspaces/sequence/shot/renders/v001/name.%04d.exr

# Plates (footage from IO)
# r:/project/workspaces/sequence/shot/plates/v001/plate_colorspace.%04d.exr

# Publishes
# r:/project/workspaces/sequence/shot/publish/name/name_v001.%04d.exr




