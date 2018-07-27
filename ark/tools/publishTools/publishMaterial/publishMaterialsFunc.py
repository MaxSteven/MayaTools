'''
Author: Carlo Cherisier
Date: 09.30.14
Script: publishMaterialsFunc
'''
import os

import translators
translator = translators.getCurrent()

class guiFunc(object):
	'''
	Functions for GUI
	'''
	## Class Variables
	projName=''
	deptName=''
	assetName=''
	#
	def __init__( self):
		pass
		# self.getFileInfo()
	#
	def getFileInfo( self):
		'''
		Purpose:
			Grab the Project, Department, and Asset Name of the file
			If Department = Model/ Rig then publish material to Published/Materials folder
		'''
		projName= translator.getData( 'smart_projName')
		deptName= translator.getData( 'smart_deptName')
		assetName= translator.getData( 'smart_assetName')

		if projName!= '' or deptName!= '' or assetName!= '':
			if deptName == 'Model' or deptName == 'Rig':
				## Grab information
				self.publishFolder= 'r:/{0}/Project_Assets/{1}/Published/Material'
	#
	def createPublishedFolder( self):
		'''
		Purpose:
			Create publish version folder for Material
			If Department Folder doesn't exist make version folder 001
			If Department folder exist but contins no files make version folder 001
			Create Main Folder for Asset
		'''
		startOver=0
		if not os.path.exists( self.publishFolder):
			startOver= 1

		else:
			if len( os.listdir( self.publishFolder))== 0:
				startOver= 1

		if startOver:
			## Set publish version
			self.publishVersion= 'v001'

			## Construct folder path
			self.publishPath='{0}/v001'.format( self.publishFolder)

			if not os.path.exists( self.publishPath):
				## Make Folder
				os.makedirs( self.publishPath)

		else:
			## Grab files
			file_List= os.listdir( self.publishFolder)

			holder= 1
			for each in file_List:
				if 'v0' in each or 'v1' in each or 'v2' in each:
					## Grab version number
					version= int( each.split( 'v')[-1])
					if version>= holder:
						holder= version+1

			## Set publish version
			self.publishVersion= 'v{0:03}'.format( holder)

			## Construct folder path
			self.publishPath='{0}/{1}'.format( self.publishFolder, self.publishVersion)

			if not os.path.exists( self.publishPath):
				## Make Folder
				os.makedirs( self.publishPath)
	#
	def saveMultiSubMaterial( self, projName, assetName):
		'''
		Purpose:
			Save out Multi Sub material on select objects
		'''
		## Check if anything is selected
		result= translator.isObjectSelected()

		if result == False:
			return 2

		## Set Publish Folder
		self.publishFolder= 'r:/{0}/Project_Assets/{1}/Published/Material'.format( projName, assetName)

		## Create folder for published materials
		self.createPublishedFolder()

		## Prepare Materials for export
		translator.assetManager.prepareMaterials()

		if result == 'undefined':
			return 3

		## Save published materials
		translator.assetManager.exportMaterials( folderPath= self.publishPath, fileName= assetName)
	#
	def loadMultiSubMaterial( self, projName, assetName):
		'''
		Purpose:
			Load published Multi Sub Materials onto selected objects
		'''
		## Check if anything is selected
		result= translator.isObjectSelected()

		if result == False:
			return 2

		## Set Publish Folder
		publishFolder= 'r:/{0}/Project_Assets/{1}/Published/Material'.format( projName, assetName)

		## Grab newest folder from published materials
		newestFolder= sorted(os.listdir( publishFolder))[-1]

		## Construct asset material path
		folderPath= '{0}/{1}'.format( publishFolder, newestFolder)

		## Load Asset's material
		translator.assetManager.importMaterials( folderPath= folderPath, fileName= assetName)
