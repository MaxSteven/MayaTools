# Max_Animation

import MaxPlus
import re

class Max_AnimationManager( object):

	def __init__(self, translator):
		self.translator = translator

	def getTime( self):
		'''
		Purpose:
			Grab start and end frame
		'''
		func = '''
			print animationrange.start
			'''
		## Run Maxscript
		startTime = int( self.translator.executeNativeCommand( func)[:-1])

		func = '''
			print animationrange.end
			'''
		## Run Maxscript
		endTime = int( self.translator.executeNativeCommand( func)[:-1])

		return( startTime, endTime)

	def replaceSelectObjectsName( self, oldName, newName):
		## Grab selected nodes
		## And remove namespace to fix namespace issues
		selected_List= list( MaxPlus.SelectionManager.Nodes)

		for each in selected_List:
			name = each.GetName()
			replacedName= name.replace( oldName, newName)
			each.SetName( replacedName)

	def saveAssetAnimation( self, filePath):
		func = '''
		currentSel = getCurrentSelection()
		timeStart = animationrange.start
		timeEnd = animationrange.end
		userAttr = #()
		userVal = #()

		LoadSaveAnimation.saveAnimation "{0}" (getCurrentSelection()) userAttr userVal animatedTracks:true
		'''.format( filePath)
		self.translator.executeNativeCommand( func)

	def loadAssetAnimation( self, filePath):
		## Function variables
		controllerList=[]

		## Read through file and grab CTRLs in file
		with open( filePath, 'r') as dataFile:
			for line in dataFile:
				result = re.findall( r'(?!<Node name="|<Controller name=")(ns\w+)(?:"|[ ])', line )
				if( result):
					if( result[0] not in controllerList):
						controllerList.append( result[0])

		## Make empty list in Maxscript
		self.translator.executeNativeCommand( 'ctrl_List= #()')

		## Select CTRLs from saved animation file
		for each in controllerList:
			func = '''
			append ctrl_List ${0}
			'''.format( each)
			self.translator.executeNativeCommand( func)

		## Select controllers
		self.translator.executeNativeCommand( 'select ctrl_List')

		## Load animation onto selected asset
		func = '''
		userAttr = #()
		userVal = #()

		LoadSaveAnimation.loadAnimation "{0}" (getCurrentSelection()) relative:false insert:false
		'''.format( filePath)
		self.translator.executeNativeCommand( func)