#-----------------------------------------------------------------------------
# ieself.Sql.py
# By Grant Miller (blented@gmail.com)
# v 1.0
# Created On: 11/01/2011
# Modified On: 11/01/2011
# tested using Nuke X 6.3v2 & 3dsMax 2012 & Caretaker 2.0
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Required Files:
# os, sys, socket, urllib2
# globalSettings.py
# ieCommon.py
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Description:
# Manages functions for connecting to Caretaker via Python
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Revision History:
#
# v 1.00 Initial version
#
#-----------------------------------------------------------------------------

import os
# import sys
import re
# import json
import socket
import urllib2

import arkInit
arkInit.init()
import settingsManager
import database
globalSettings = settingsManager.globalSettings()

import arkUtil
# import ieSql
# import re
# import ieOS
import cOS

# GLOBALS
#-----------------------------------------------------------------------------
ct = None

class Caretaker(object):
	pass














# 	# sampleDirectoryStructure = globalSettings.WORKSPACE_FOLDERS
# 	localIP = False
# 	rootDrive = 'R:/'
# 	userInfo = False
# 	entityNames = {}
# 	schema = False

# 	def __init__(self):
# 		localIP = socket.gethostbyname(socket.gethostname())
# 		self.sql = ieSql.SqlConnection(keepTrying=False)
# 		self.database = database.Database(globalSettings.DATABASE)

# 		self.sql.query('SELECT user FROM session WHERE ip="%s" LIMIT 1' % localIP)
# 		session = self.sql.fetchOne()

# 		if session:
# 			self.sql.query('SELECT * FROM user WHERE id="%s" LIMIT 1' % session['user'])
# 			self.userInfo = self.sql.fetchOne()

# 		if self.userInfo:
# 			print 'Currently logged in as: %s' % self.userInfo['name']

# 		# We get the entity names manually to avoid having a bunch of checks all over the place
# #        self.sql.query('SELECT id,name FROM entity')
# #        result = self.sql.fetchAll()
# #        for row in result:
# #			self.entityNames[row['id']] = row['name']
# #        self.entityNames = ieCommon.dictToAndFrom(self.entityNames)
# #
# #		# Then immediatly read the rest of the info about the entities and fields so we have all that data
# #        self.schema_read(True)
# #        self.fieldNames = self.getEntityNames('field','name')
# #        self.projectNames = ieCommon.dictToAndFrom(self.getEntityNames('project','name'))
# #		# fix: needs to be getting this from the sql class, don't really know where that class fits in
# #		# this bit adds the connection tables in as 'entities' so we can use standard ct->find commands with them
# #        self.sql.query("SHOW tables FROM iebase")
# #        result = self.sql.fetchAll()
# #        connectionTables = {}
# #        tableOffset = 99999
# #        for row in result:
# #            tableName = row.items()[0][1]
# #            if tableName.find('connection') != -1:
# #                connectionTables[tableOffset] = tableName
# #                connectionTables[tableName] = tableOffset
# #                tableOffset += 1
# #
# #		self.entityNames = appendDict(self.entityNames,connectionTables)
# #
# #		self.dataTypes = self.getListOptions('field','data_type',True)
# #		self.pageTypes = self.getListOptions('caretaker_page','page_type',True)
# #		for type,val in self.sqlTypes:
# #			self.sqlTypes[self.dataTypes[type]] = val

# 	def create(self,entity_type,data,returnFields=['id'],generateScriptCalls=True):
# 		if 'dict' not in arkUtil.varType(data):
# 			data = {}
# 		data['edit_entity'] = entity_type
# 		data['editFields'] = ct.getEditFields(data)
# 		response = urllib2.urlopen('http://' + globalSettings.DATABASE_HOST + '/_edit.php',arkUtil.postString(data))
# 		print response.read()

# 	def modify(self,entity_type,entity_id,data,generateScriptCalls=True):
# 		if 'dict' not in arkUtil.varType(data):
# 			data = {}
# 		data['edit_entity'] = entity_type
# 		data['edit_entityIDs'] = str(entity_id)
# 		data['editFields'] = ct.getEditFields(data)
# 		urllib2.urlopen('http://' + globalSettings.DATABASE_HOST + '/_edit.php',arkUtil.postString(data))
# 		#print response.read()

# 	def remove(self,entity_type,entity_id,generateScriptCalls=True):
# 		data = {}
# 		data['edit_entity'] = entity_type
# 		data['removeIDs'] = entity_id
# 		response = urllib2.urlopen('http://' + globalSettings.DATABASE_HOST + '/_edit.php',arkUtil.postString(data))
# 		print response.read()

# 	def getEditFields(self,data):
# 		if 'dict' in arkUtil.varType(data):
# 			return ','.join(str(x) for x in data.keys())


# 	def getProjects(self, includeArchived=False):
# 		query = self.database.find('project')
# 		if not includeArchived:
# 			query = query.where('archive','is not',True)

# 		projects = query.execute()
# 		return projects

# 	def getEntityFromField(self, entityType, field, value):
# 		entity = self.database.find(entityType).where(field,'is', value).execute()
# 		if len(entity):
# 			return entity[0]
# 		else:
# 			print 'Could not find {0} where {1} = {2}'.format(entity, field, value)
# 			return False

# 	def getShotFromName(self, shotName):
# 		shotInfo = self.database.find('shot').where('name','is',shotName).execute()
# 		if len(shotInfo):
# 			return shotInfo[0]
# 		else:
# 			print 'Could not find a shot for:', shotName
# 			return False

# 	def getPathInfo(self, filepath):
# 		filepath = cOS.unixPath(filepath)
# 		pathInfo = cOS.getPathInfo(filepath)

# 		projectFolder = filepath.split('/')[1]
# 		projectInfo = self.database.find('project').where('folderName','is',projectFolder).execute()
# 		if not projectInfo or not len(projectInfo):
# 			print 'Could not find a project for:', projectFolder
# 			return False
# 		else:
# 			pathInfo['projectInfo'] = projectInfo[0]

# 		projectInfo = projectInfo[0]
# 		projectCode = projectInfo['code']

# 		# remove versions from the filepath
# 		modifiedPath = re.sub(r'_[vV][0-9]+', '', filepath)

# 		matches = re.findall(r'(' + projectCode + '_[a-zA-Z0-9]+_[a-zA-Z0-9_]+)', modifiedPath)
# 		if not len(matches):
# 			print 'primary shot format failed, trying secondary'
# 			matches = re.findall(r'(' + projectCode + '[a-zA-Z0-9]+_[a-zA-Z0-9_]+)', modifiedPath)
# 		if not len(matches):
# 			print 'Could not parse a shot for:', projectCode, filepath
# 			print 'Maybe the shot name doesn\'t start with the project code?'
# 			# return False
# 		else:
# 			shotName = matches[0]
# 			pathInfo['shotInfo'] = self.getShotFromName(shotName)

# 		pathInfo['version'] = cOS.getVersion(filepath)
# 		return pathInfo

# 	def pathInfo(self, filepath):
# 		"""Returns a dictionary of database information for a given filepath"""

# 		pathInfo = cOS.getPathInfo(filepath)

# 		pathInfo['version'] = 0
# 		pathInfo['department'] = ''
# 		pathInfo['entity_info'] = False
# 		pathInfo['entity_type'] = False

# 		filepath = filepath.replace('\\','/')
# 		fileParts = filepath.split('/')
# 		pathInfo['filepath'] = filepath

# 		if len(fileParts) > 2:
# 			if fileParts[2].lower() == 'workspaces':
# 				pathInfo['entity_type'] = 'shot'
# 			elif fileParts[2].lower() == 'global_assets' or fileParts[2].lower() == 'project_assets':
# 				pathInfo['entity_type'] = 'asset'

# 		if len(fileParts) > 3:
# 			pathInfo['entity_name'] = fileParts[3]

# 		if len(fileParts) > 3:
# 			self.sql.query('SELECT * FROM project WHERE folder_name="%s" LIMIT 1' % fileParts[1])
# 			pathInfo['project_info'] = self.sql.fetchOne()
# 			if (pathInfo['project_info'] and pathInfo['entity_type']):
# 				self.sql.query('SELECT * FROM %s WHERE name="%s" AND project="%s" LIMIT 1' % (pathInfo['entity_type'],fileParts[3],pathInfo['project_info']['id']))
# 				pathInfo['entity_info'] = self.sql.fetchOne()

# 		pathInfo['version'] = cOS.getVersion(filepath)

# 		if len(fileParts) > 5:
# 			# fix: this is outdated per our new folder structure and should be more generic
# 			departmentNames = self.getEntityNames('department','name')
# 			if (fileParts[4] == '3DSMAX'):
# 				if (fileParts[-2] == '3DSMAX'):
# 					pathInfo['department'] = departmentNames['Light and Shade']
# 				elif (fileParts[-2] == 'CAM'):
# 					pathInfo['department'] = departmentNames['Match Move']
# 				elif (fileParts[-2] == '3D'):
# 					pathInfo['department'] = departmentNames['3D']
# 				elif (fileParts[-2] == 'Rig'):
# 					pathInfo['department'] = departmentNames['Rig']
# 				elif (fileParts[-2] == 'Animation'):
# 					pathInfo['department'] = departmentNames['Animation']
# 				elif (fileParts[-2] == 'FX'):
# 					pathInfo['department'] = departmentNames['FX']
# 				elif (fileParts[-2] == 'Dynamics'):
# 					pathInfo['department'] = departmentNames['Dynamics']
# 			elif (fileParts[4] == 'NUKE'):
# 				if (fileParts[-1].find('key') != -1 or fileParts[-1].find('roto') != -1):
# 					pathInfo['department'] = departmentNames['Key Roto']
# 				elif (fileParts[-1].find('matte') != -1):
# 					pathInfo['department'] = departmentNames['Matte Painting']
# 				else:
# 					pathInfo['department'] = departmentNames['Comp']


# 			pathInfo['department'] = departmentNames['Comp']

# 		if len(fileParts) > 2:
# 			pathInfo['project_root'] = self.rootDrive + fileParts[1] + '/'
# 		if len(fileParts) > 3:
# 			pathInfo['entity_root'] = pathInfo['project_root'] + fileParts[2] + '/' + fileParts[3] + '/'

# 		return pathInfo

# 	def connectionString(self,link_etype,link):
# 		return ",%s:%s," % (link_etype,link)

# 	def getEntityNames(self,entity_type,name_field):
# 		self.sql.query('SELECT id,%s FROM %s' % (name_field,entity_type))
# 		nameResult = self.sql.fetchAll()
# 		if nameResult:
# 			names = {}
# 			for row in nameResult:
# 				names[row[name_field]] = row['id']
# 			return names
# 			# return arkUtil.dictToAndFrom(names)
# 		return False

# 	def createShotsFromDirectory(self, directory):
# 		folderName = directory.replace('\\','/').split('/')[1]
# 		print 'Project root: ' + folderName
# 		self.sql.query('SELECT id FROM project WHERE folder_name="%s" LIMIT 1' % folderName)
# 		projectInfo = self.sql.fetchOne()
# 		if not projectInfo:
# 			self.sql.query('SELECT folder_name FROM project')
# 			projectInfo = self.sql.fetchAll()
# 			print projectInfo
# 			return False

# 		self.sql.query('SELECT name FROM shot WHERE project="%s"' % projectInfo['id'])
# 		result = self.sql.fetchAll()
# 		existingShots = []
# 		if result:
# 			for shot in result:
# 				existingShots.append(shot['name'])

# 		workspacesDirectory = os.path.join(directory, 'WORKSPACES')
# 		print 'Workspaces root: ' + workspacesDirectory
# 		#This line takes care of the shots immediately living in the Workspaces directory
# 		folders = [d for d in os.listdir(workspacesDirectory) if os.path.isdir(os.path.join(workspacesDirectory, d, 'Plates'))]
# 		paths = [os.path.join(workspacesDirectory, name) for name in folders]

# 		# This loop goes through each directory, checking whether it is potentially a sequence folder with shots inside
# 		subdirectories = filter(lambda f: os.path.isdir(os.path.join(workspacesDirectory, f)), os.listdir(workspacesDirectory))
# 		for subd in subdirectories:
# 			subpath = os.path.join(workspacesDirectory, subd)
# 			sequences =  [d for d in os.listdir(subpath) if os.path.isdir(os.path.join(subpath, d, 'Plates'))]
# 			sequencePaths = [os.path.join(subpath, name) for name in sequences]
# 			folders += sequences
# 			paths += sequencePaths

# 		folders.sort()
# 		shotInfo = {
# 			'project':projectInfo['id'],
# 			'description':'AUTO CREATED'
# 		}

# 		for folder in folders:
# 			if folder not in existingShots:
# 				print 'Creating: ' + folder
# 				shotInfo['name'] = folder
# 				self.create('shot',shotInfo)

















		# for path in paths:
		# 	cOS.copyTree(self.sampleDirectoryStructure, path)

	# def createMissingFiles(self, shotRoot):
	# 	sampleFiles = os.listdir(sampleDirectoryStructure):

#    def getListOptions(entity,fieldName,toAndFrom=False):
#        fieldInfo = self.schema_field_read(entity,fieldName)
#        if not fieldInfo:
#            return False
#        if self.isListType(fieldInfo['data_type']) or fieldName == 'data_type':
#            options = parseCommaString(fieldInfo['data'])
#            options = ieCommon.mergeDict({'0':''},options)
#            #unset(options[0])
#            if toAndFrom:
#                return ieCommon.dictToAndFrom(options)
#            return options
#        else:
#            self.logError("Field: fieldName is not a list type",'getListOptions')
#        return False
#
#    def schema_read(self,update=False):
#        if not self.schema or update:
#            self.schema = {}
#            # We get the fields manually to avoid extra checks all over as well
#            self.sql.query('SELECT * FROM field ORDER BY entity,name')
#            result = self.sql.fetchAll()
#            for field in result:
#                if field['entity'] in self.entityNames:
#                    entityName = self.entityNames[field['entity']]
#                else:
#                    entityName = 'non_entity'
#                if entityName not in self.schema:
#                    self.schema[entityName] = {}
#                self.schema[entityName][field['name']] = field
#        return self.schema
#
#    def schema_entity_read(self,entity_type):
#        # fix: total hack, get non_entity widgets
#        if entity_type != 'non_entity':
#            entityName = self.ensureName(entity_type,'entity')
#        else:
#            entityName = entity_type
#
#        if entityName in self.schema:
#            return self.schema[entityName]
#        elif not entityName:
#            self.logError("Entity: %s is not a valid entity name" % entity_type,'schema_entity_read')
#        return False
#
#    def schema_field_read(self,entity_type,fieldName):
#        # fix: total hack, get non_entity widgets
#        if entity_type != 'non_entity':
#            entityName = self.ensureName(entity_type,'entity')
#        else:
#            entityName = entity_type
#        if entityName in self.schema:
#            if fieldName in self.schema[entityName]:
#                return self.schema[entityName][fieldName]
#            else:
#                self.logError("Field: %s is not a valid field" % fieldName,'schema_field_read')
#        else:
#            self.logError("Entity: $entity_type is not a valid entity name",'schema_field_read')
#        return False

#

#updateData = {}
#updateData['status'] = 1
#updateData['updated_date'] = 'UNIX_TIMESTAMP()'
#ct.modify('shepherd_job',470,updateData)
#updateData = {}
#updateData['status'] = JOBSTATUS['complete']
#updateData['updated_date'] = 'UNIX_TIMESTAMP()'
#ct.modify('shepherd_job',jobRow['id'],updateData)
#pathInfo = ct.pathInfo('Q:\\HAPPY_ENDINGS_SEASON_02\\WORKSPACES\\201_001\\NUKE\\201_001_v02_dal.nk')
#for (k,v) in pathInfo.iteritems():
#    print "%s: %s" % (k,v)
#if (pathInfo['project'] and pathInfo['entity_info']):
#    noteData = {}
#    noteData['link'] = ct.connectionString(pathInfo['entity_type'],pathInfo['entity_info']['id'])
#    noteData['project'] = pathInfo['project']['id']
#    noteData['note'] = "testing this shit out"
#    noteData['department'] = ct.connectionString('department',pathInfo['department'])
#    ct.create('note',noteData)


def getCaretaker():
	global ct
	if not ct:
		ct = Caretaker()
	return ct


if __name__ == '__main__':
	ct = getCaretaker()
	# info = ct.getPathInfo('R:/Real_ONeals_s01/FINAL_RENDERS/TRO_105/EXR_Linear/TRO_105_04_010_v004/TRO_105_04_010_v004.%04d.exr')
	# info = ct.getPathInfo('r:/Real_ONeals_s01/Workspaces/TRO_105/TRO_105_04_010/Comp/TRO_105_04_010_v005_ghm.nk')
	# info = ct.getPathInfo('r:/Real_ONeals_s01/Workspaces/TRO_105/TRO_105_04_010/Plates/A_AlexaLog_v01/TRO_105_04_010_A_AlexaLog_v01.%04d.dpx')
	# info = ct.getPathInfo('R:/Modern_Family_s07/Final_Renders/MF_704/ProRes42HQ_Alexa/MF_704_16_0050_v007.mov')
	# info = ct.getPathInfo('r:/Agent_X_s01/Final_Renders/AGX_109/DNx36/AGX109_083_008_v003.mov')
	# info = ct.getProjects()
	# info = ct.getEntityFromField('project','folderName','Brooklyn_99_s03')
	# print json.dumps(info, sort_keys=True, indent=4)
