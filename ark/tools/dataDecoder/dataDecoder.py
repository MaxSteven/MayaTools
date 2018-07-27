'''
Author: Carlo Cherisier
Title: dataParser
Creation: 08.28.14
'''
import os, os.path

import json
from pprint import pprint

import arkInit
arkInit.init()

import translators
translator = translators.getCurrent()

#------------------- SET GUI ELEMENTS FOR OPEN/SAVE----------------------------------#
def store_smartData( drive=None, projName=None, deptName=None, assetName=None, fileName=None):
	'''
	Make Data file for GUI Elements
	'''
	## Function Variables
	project_dataFile = 'C:/ie/data/smartData_{}.data'.format( translator.getProgram())
	main_Dict = {}

	if drive:
		main_Dict[ 'localDrive']= drive

	if projName:
		main_Dict[ 'projName']= projName

	if deptName:
		main_Dict[ 'deptName']= deptName

	if assetName:
		main_Dict[ 'assetName']= assetName

	if fileName:
		main_Dict[ 'fileName']= fileName

	## Check if file exist
	check = os.path.exists( project_dataFile)

	if check == False:
		try:
			## Make Data folder
			os.makedirs( os.path.split(project_dataFile)[0] )
		except WindowsError:
			pass

		with open( project_dataFile, 'wt') as dataFile:
			store = json.dumps( main_Dict, sort_keys=True, indent=4, separators=(',', ': '))
			dataFile.write(store)
	else:
		## Grab store information on data file
		with open( project_dataFile) as dataFile:
			saved_Dict = json.load( dataFile)
		# pprint(saved_Dict)

		## Update old dictionary with new data
		saved_Dict.update( main_Dict)
		# pprint(saved_Dict)

		## Write out changes to data file
		with open( project_dataFile, 'wt') as dataFile:
			store = json.dumps( saved_Dict, sort_keys=True, indent=4, separators=(',', ': '))
			dataFile.write(store)
#
def get_smartData( key= None):
	'''
	Get information for GUI
	'''
	## Function Variables
	project_dataFile= 'C:/ie/data/smartData_{}.data'.format( translator.getProgram())

	## Check if file exist
	check= os.path.exists( project_dataFile)

	if check:
		## Grab store information on data file
		with open( project_dataFile) as dataFile:
			saved_Dict = json.load( dataFile)
		#pprint( saved_Dict)

		if key in saved_Dict.keys():
			return saved_Dict[key]


#------------------- GUI STORE/ GET ASSET NOTES FOR OPEN/ SAVE----------------------------------#
def store_assetNotes( userName, assetNotes, projName, deptName, assetName, version, saveLocation, localDrive):
	'''
	Store Asset Notes
	'''
	if saveLocation == 'local':
		## Store notes Locally
		notes_dataFile= '{0}ie/projects/{1}/Data/Notes/{2}/{3}_{4}.data'.format( localDrive, projName, deptName, assetName, translator.getProgram())
	else:
		## Store notes Globally
		notes_dataFile= 'r:/{0}/Data/Notes/{1}/{2}_{3}.data'.format( projName, deptName, assetName, translator.getProgram())

	## Check if file exist
	check= os.path.exists( notes_dataFile)

	if check == False:
		try:
			## Make Data folder
			os.makedirs( os.path.split(notes_dataFile)[0] )
		except WindowsError:
			pass

		## Create and store information on data file
		main_Dict={}

		## Store data in dictionary
		main_Dict[ version] = userName+ '**'+ assetNotes

		with open( notes_dataFile, 'wt') as dataFile:
			store = json.dumps( main_Dict, sort_keys=True, indent=4, separators=(',', ': '))
			dataFile.write(store)
	else:
		## Grab store information on data file
		with open( notes_dataFile) as dataFile:
			main_Dict = json.load( dataFile)
		# pprint(main_Dict)

		## Update old dictionary with new data
		main_Dict[ version] = userName+ '**'+ assetNotes

		## Write out changes to data file
		with open( notes_dataFile, 'wt') as dataFile:
			store = json.dumps( main_Dict, sort_keys=True, indent=4, separators=(',', ': '))
			dataFile.write(store)
#
def get_assetNotes( location, projName, deptName, assetName, version, localDrive=None):
	'''
	Get data for Asset Notes
	'''
	if location== 'Local':
		## Store notes Locally
		notes_dataFile= '{0}ie/projects/{1}/Data/Notes/{2}/{3}_{4}.data'.format( localDrive, projName, deptName, assetName, translator.getProgram())
	else:
		## Store notes Globally
		notes_dataFile= 'r:/{0}/Data/Notes/{1}/{2}_{3}.data'.format( projName, deptName, assetName, translator.getProgram())

	## Check if file exist
	check= os.path.exists( notes_dataFile)

	if check:
		## Grab store information on data file
		with open( notes_dataFile) as dataFile:
			saved_Dict = json.load( dataFile)
		# pprint( saved_Dict)

		if version in saved_Dict.keys():
			return saved_Dict[version].split( '**')


#------------------- SAVE PUBLISHED ASSETS----------------------------------#
def store_publishedAssets( projName, deptName, assetName, version, lowRezPath, hiRezPath, rigPath, devPath, bBoxPath, abcPath, vrayPath, objPath, layerList, program):
	'''
	Purpose:
		Store information about Published Asset
	'''
	## Construct filePath
	published_dataFile= 'r:/{0}/Data/{1}/{2}.data'.format( projName, deptName, assetName)

	## Check if file exist
	check = os.path.exists( published_dataFile)

	if check == False:

		try:
			## Make Data folder
			os.makedirs( os.path.split(published_dataFile)[0] )
		except WindowsError:
			pass

		## Create and store information on data file
		data_Dict= {}

		data_Dict[ str(version) ]={ 'hiRez':hiRezPath, 'lowRez': lowRezPath, 'rig':rigPath, 'dev':devPath, 'bBox':bBoxPath, 'alembic':abcPath, 'vRayProxy':vrayPath, 'obj':objPath, 'version':version, 'layerList': layerList, 'program': program}

		with open( published_dataFile, 'wt') as dataFile:
			store = json.dumps( data_Dict, sort_keys=True, indent=4, separators=(',', ': '))
			dataFile.write(store)
	else:
		## Grab store information on data file
		with open( published_dataFile) as dataFile:
			saved_Dict = json.load( dataFile)
		# pprint(saved_Dict)

		saved_Dict[ str(version) ]={ 'hiRez':hiRezPath, 'lowRez': lowRezPath, 'rig':rigPath, 'dev':devPath, 'bBox':bBoxPath, 'alembic':abcPath, 'vRayProxy':vrayPath, 'obj':objPath, 'version':version, 'layerList': layerList, 'program': program}

		## Write out changes to data file
		with open( published_dataFile, 'wt') as dataFile:
			store = json.dumps( saved_Dict, sort_keys=True, indent=4, separators=(',', ': '))
			dataFile.write(store)


#------------------- FIND PUBLISHED ASSETS FOR IMPORT---------------------------------#
def get_publishAssets( published_dataFile, key=None):
	'''
	Grab published asset path so it can be used to Import Asset into scene
	'''
	## Grab store information on data file
	with open( published_dataFile) as dataFile:
		saved_Dict = json.load( dataFile)
	# pprint(saved_Dict)

	newestVersion= sorted( saved_Dict.keys())[-1]
	#print( newestVersion)

	## If key isn't in list return none
	if key not in saved_Dict[newestVersion].keys():
		return

	value= saved_Dict[newestVersion][ key]

	if key== 'alembic' and value== None:
		return

	return value


#------------------- SAVE IMPORTED ASSETS----------------------------------#
def store_sceneAssetData( projName, deptName, assetName, fileVersion, value_Dict):
	'''
	Save Imported Assets to data file when File is saved using Smart Save Tool
	'''
	## Construct filePath
	published_dataFile= 'r:/{0}/Data/{1}/{2}.data'.format( projName, deptName, assetName)

	## Check if file exist
	check= os.path.exists( published_dataFile)

	if not check:

		try:
			## Make Data folder
			os.makedirs( os.path.split(published_dataFile)[0] )
		except WindowsError:
			pass

		## Create and store information on data file
		data_Dict= {}

		data_Dict[ str(fileVersion) ]= value_Dict

		with open( published_dataFile, 'wt') as dataFile:
			store = json.dumps( data_Dict, sort_keys=True, indent=4, separators=(',', ': '))
			dataFile.write(store)
	else:
		## Grab store information on data file
		with open( published_dataFile) as dataFile:
			saved_Dict = json.load( dataFile)
		# pprint(saved_Dict)

		## Update old dictionary with new data
		saved_Dict[ str(fileVersion) ]= value_Dict
		# pprint(saved_Dict)

		## Write out changes to data file
		with open( published_dataFile, 'wt') as dataFile:
			store = json.dumps( saved_Dict, sort_keys=True, indent=4, separators=(',', ': '))
			dataFile.write(store)

	return published_dataFile


#------------------- SHOW IMPORTED ASSETS IN SCENE----------------------------------#
def get_sceneAssetData( projName, deptName, assetName):
	'''
	Show current asset files in the scene when using the View Asset Tool
	'''
	## Construct filePath
	published_dataFile= 'r:/{0}/Data/{1}/{2}.data'.format( projName, deptName, assetName)

	## Check if file exist
	check= os.path.exists( published_dataFile)

	if not check:
		return

	## Grab store information on data file
	with open( published_dataFile) as dataFile:
		saved_Dict = json.load( dataFile)
	# pprint(saved_Dict)

	## Grab most recent key
	key= sorted( saved_Dict.keys())[-1]

	return saved_Dict[ key]


#------------------- SAVE IMPORTED ASSETS----------------------------------#
def store_cameraData( projName, assetName, version, value_Dict, maxPath, abcPath, fbxPath):
	'''
	Save Camera information to data file when using Publish Camera Tool
	'''
	main_Dict={}

	value_Dict[' maxPath']= maxPath
	value_Dict[' abcPath']= abcPath
	value_Dict[' fbxPath']= fbxPath

	main_Dict[ str(version)]= value_Dict

	## Construct filePath
	published_dataFile= 'r:/{0}/Data/Cameras/{1}.data'.format( projName, assetName)

	## Check if file exist
	check= os.path.exists( published_dataFile)

	if not check:

		try:
			## Make Data folder
			os.makedirs( os.path.split(published_dataFile)[0] )
		except WindowsError:
			pass

		with open( published_dataFile, 'wt') as dataFile:
			store = json.dumps( main_Dict, sort_keys=True, indent=4, separators=(',', ': '))
			dataFile.write(store)
	else:
		## Grab store information on data file
		with open( published_dataFile) as dataFile:
			saved_Dict = json.load( dataFile)
		# pprint(saved_Dict)

		## Update old dictionary with new data
		saved_Dict.update( main_Dict)
		pprint(saved_Dict)

		## Write out changes to data file
		with open( published_dataFile, 'wt') as dataFile:
			store = json.dumps( saved_Dict, sort_keys=True, indent=4, separators=(',', ': '))
			dataFile.write(store)


#------------------- STORE AND GET DATA----------------------------------#
def storeParserData( path, fileVersion, value_Dict):
	'''
	Save Imported Assets to data file when File is saved using Smart Save Tool
	'''
	## Check if file exist
	if not os.path.exists( path):

		try:
			## Make Data folder
			os.makedirs( os.path.split(path)[0] )
		except WindowsError:
			pass

		## Create and store information on data file
		data_Dict= {}

		data_Dict[ str(fileVersion) ]= value_Dict

		with open( path, 'wt') as dataFile:
			store = json.dumps( data_Dict, sort_keys=True, indent=4, separators=(',', ': '))
			dataFile.write(store)
	else:
		## Grab store information on data file
		with open( path) as dataFile:
			saved_Dict = json.load( dataFile)
		# pprint(saved_Dict)

		## Update old dictionary with new data
		saved_Dict[ str(fileVersion) ]= value_Dict
		pprint(saved_Dict)

		## Write out changes to data file
		with open( path, 'wt') as dataFile:
			store = json.dumps( saved_Dict, sort_keys=True, indent=4, separators=(',', ': '))
			dataFile.write(store)

	return path

def getParserData( path):
	'''
	Show current asset files in the scene when using the View Asset Tool
	'''
	## Check if file exist
	check= os.path.exists( path)

	if not check:
		return

	## Grab store information on data file
	with open( path) as dataFile:
		saved_Dict = json.load( dataFile)
	#pprint(saved_Dict)

	## Grab most recent key
	key= sorted( saved_Dict.keys())[-1]

	return saved_Dict[ key]


