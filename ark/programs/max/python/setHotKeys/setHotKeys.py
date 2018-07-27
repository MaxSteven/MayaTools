'''
Author: Carlo Cherisier
Date: 10.01.14
Script: setHotKeys

python.execute("import sys;
sys.path.append('c:/ie/ark/programs/max/python/setHotKeys');
import setHotKeys; reload(setHotKeys); setHotKeys.loadUpdateHotKeys();
")
'''
import arkInit
arkInit.init()

import translators
translator = translators.getCurrent()

import re

def getHotKeyFile():
	'''
	Purpose:
		Grab hotkey file path
	'''
	func='''
	actionMan.getKeyboardFile()
	'''
	## Run Maxscript
	hotkeyPath= translator.executeNativeCommand( func)

	## Fix file path
	hotkeyPath= hotkeyPath.replace( '\\', '/')

	return hotkeyPath
#
def searchAndChange( value, numberCombo, accKey, actionID):
	'''
	Purpose:
		Search value for matching string characters
		If not found create new string
	'''
	if len(value.split( '    '))<=1:
		return value, True

	## Grab need characters
	cleanLine= value.split( '    ')[-1]

	# print re.findall( '<shortcut.+', holder[1]), hotKeyList[i]
	searchValue= '<shortcut fVirt="{0}" accleleratorKey="{1}".+'.format(numberCombo, accKey,)
	check= bool( re.findall( searchValue, cleanLine))

	if check == True:
		value= '    <shortcut fVirt="{0}" accleleratorKey="{1}" actionID="{2}`smartTools" actionTableID="647394" />'.format( numberCombo, accKey, actionID)
		return value, False
	else:
		return value, True
#
def createNewKey( numberCombo, accKey, actionID):
	'''
	Purpose:
		Create new hotkey for Hotkey file
	'''
	## Create new string
	value= '    <shortcut fVirt="{0}" accleleratorKey="{1}" actionID="{2}`File" actionTableID="647394" />'.format( numberCombo, accKey, actionID)

	return( value)
#
def set_saveKey():
	'''
	Purpose:
		Create hotkey for smartSave Tool
		Hotkey: Alt + Shift + S
	'''
	modifier= 15
	keyBoard= 83

	## Grab hotkey file path
	hotkeyPath= getHotKeyFile()

	func='''
		macroScript smartSave
			category:"smartTools"
			tooltip:""
			autoUndoEnabled:false
		(
		python.execute("import sys; sys.path.append('c:/ie/ark/tools/smartTools'); import smartSave; smartSave.main();")
		)
		'''
		## Run Maxscript
	translator.executeNativeCommand( func)

	with open( hotkeyPath) as readFile:
		## Grab lines
		hotKeyList= readFile.readlines()

	notHere=1
	with open( hotkeyPath, 'wt') as writeFile:
		for i in range( len(hotKeyList)):
			## Search and replace file for matching hotkey
			hotKeyList[i], check= searchAndChange( hotKeyList[i], modifier, keyBoard, 'smartSave')

			if check:
				notHere=0

		## Add hotkey to list
		if notHere:
			hotKeyList.append( createNewKey( modifier, keyBoard, 'smartSave'))

		## Add new hotkeys back to file
		for each in hotKeyList:
			each= each.replace( '\n', '')

			if '<shortcut' in each:
				writeFile.write( '{0}\n'.format( each))
			else:
				writeFile.write( each+ '\n')
#
def set_incrementalSaveKey():
	'''
	Purpose:
		Create hotkey for smartSave Tool
		Hotkey: Ctrl + Shift + S
	'''
	modifier= 23
	keyBoard= 83

	## Grab hotkey file path
	hotkeyPath= getHotKeyFile()

	func='''
		macroScript incrementalSave
			category:"smartTools"
			tooltip:""
			autoUndoEnabled:false
		(
		python.execute("import translators; translator = translators.getCurrent(); translator.saveIncrementWithInitials();")
		)
		'''
		## Run Maxscript
	translator.executeNativeCommand( func)

	with open( hotkeyPath) as readFile:
		## Grab lines
		hotKeyList= readFile.readlines()

	notHere=1
	with open( hotkeyPath, 'wt') as writeFile:
		for i in range( len(hotKeyList)):
			## Search and replace file for matching hotkey
			hotKeyList[i], check= searchAndChange( hotKeyList[i], modifier, keyBoard, 'incrementalSave')

			if check:
				notHere=0

		## Add hotkey to list
		if notHere:
			hotKeyList.append( createNewKey( modifier, keyBoard, 'incrementalSave'))

		## Add new hotkeys back to file
		for each in hotKeyList:
			each= each.replace( '\n', '')

			if '<shortcut' in each:
				writeFile.write( '{0}\n'.format( each))
			else:
				writeFile.write( each+ '\n')
#
def set_openKey():
	'''
	Purpose:
		Create hotkey for smartSave Tool
		Hotkey: Ctrl + O
	'''
	modifier= 11
	keyBoard= 79

	## Grab hotkey file path
	hotkeyPath= getHotKeyFile()
	func='''
		macroScript smartOpen
			category:"smartTools"
			tooltip:""
			autoUndoEnabled:false
		(
		python.execute("import sys; sys.path.append('c:/ie/ark/tools/smartTools'); import smartOpen; smartOpen.main();")
		)
		'''
		## Run Maxscript
	translator.executeNativeCommand( func)

	with open( hotkeyPath) as readFile:
		## Grab lines
		hotKeyList= readFile.readlines()

	notHere=1
	with open( hotkeyPath, 'wt') as writeFile:
		for i in range( len(hotKeyList)):
			## Search and replace file for matching hotkey
			hotKeyList[i], check= searchAndChange( hotKeyList[i], modifier, keyBoard, 'smartOpen')

			if check:
				notHere=0

		## Add hotkey to list
		if notHere:
			hotKeyList.append( createNewKey( modifier, keyBoard, 'smartOpen'))

		## Add new hotkeys back to file
		for each in hotKeyList:
			each= each.replace( '\n', '')

			if '<shortcut' in each:
				writeFile.write( '{0}\n'.format( each))
			else:
				writeFile.write( each+ '\n')
#
def set_importAssetKey():
	'''
	Purpose:
		Create hotkey for importAsset Tool
		Hotkey: Ctrl + I
	'''
	modifier= 11
	keyBoard= 73

	## Grab hotkey file path
	hotkeyPath= getHotKeyFile()

	func='''
		macroScript importAsset
			category:"smartTools"
			tooltip:""
			autoUndoEnabled:true
		(
		python.execute("import sys; sys.path.append('c:/ie/ark/tools/publishTools');  import importAsset; importAsset.main()")
		)
		'''
		## Run Maxscript
	translator.executeNativeCommand( func)


	with open( hotkeyPath) as readFile:
		## Grab lines
		hotKeyList= readFile.readlines()

	notHere=1
	with open( hotkeyPath, 'wt') as writeFile:
		for i in range( len(hotKeyList)):
			## Search and replace file for matching hotkey
			hotKeyList[i], check= searchAndChange( hotKeyList[i], modifier, keyBoard, 'importAsset')

			if check:
				notHere=0

		## Add hotkey to list
		if notHere:
			hotKeyList.append( createNewKey( modifier, keyBoard, 'importAsset'))

		## Add new hotkeys back to file
		for each in hotKeyList:
			each= each.replace( '\n', '')

			if '<shortcut' in each:
				writeFile.write( '{0}\n'.format( each))
			else:
				writeFile.write( each+ '\n')
#
def set_publishAssetKey():
	'''
	Purpose:
		Create hotkey for publishAsset Tool
		Hotkey: Alt + P
	'''
	modifier= 19
	keyBoard= 80

	## Grab hotkey file path
	hotkeyPath= getHotKeyFile()

	func='''
		macroScript publishAsset
			category:"smartTools"
			tooltip:""
			autoUndoEnabled:true
		(
		python.execute("import sys; sys.path.append('c:/ie/ark/tools/publishTools'); import publishAsset; publishAsset.main()")
		)
		'''
		## Run Maxscript
	translator.executeNativeCommand( func)

	## Grab lines
	with open( hotkeyPath) as readFile:
		hotKeyList= readFile.readlines()

	notHere=1
	with open( hotkeyPath, 'wt') as writeFile:
		for i in range( len(hotKeyList)):
			## Search and replace file for matching hotkey
			hotKeyList[i], check= searchAndChange( hotKeyList[i], modifier, keyBoard, 'publishAsset')

			if check:
				notHere=0

		## Add hotkey to list
		if notHere:
			hotKeyList.append( createNewKey( modifier, keyBoard, 'publishAsset'))
			print hotKeyList[-1]
		## Add new hotkeys back to file
		for each in hotKeyList:
			each= each.replace( '\n', '')

			if '<shortcut' in each:
				writeFile.write( '{0}\n'.format( each))
			else:
				writeFile.write( each+ '\n')
#
def set_viewAssetKey():
	'''
	Purpose:
		Create hotkey for viewAsset Tool
		Hotkey: Alt + Shift + V
	'''
	modifier= 23
	keyBoard= 86

	## Grab hotkey file path
	hotkeyPath= getHotKeyFile()

	func='''
		macroScript viewAsset
			category:"smartTools"
			tooltip:""
			autoUndoEnabled:false
		(
		python.execute("import sys; sys.path.append('c:/ie/ark/tools/publishTools'); import viewAsset; viewAsset.main()")
		)
		'''
		## Run Maxscript
	translator.executeNativeCommand( func)

	## Grab lines
	with open( hotkeyPath) as readFile:
		hotKeyList= readFile.readlines()

	notHere=1
	with open( hotkeyPath, 'wt') as writeFile:
		for i in range( len(hotKeyList)):
			## Search and replace file for matching hotkey
			hotKeyList[i], check= searchAndChange( hotKeyList[i], modifier, keyBoard, 'viewAsset')

			if check:
				notHere=0

		## Add hotkey to list
		if notHere:
			hotKeyList.append( createNewKey( modifier, keyBoard, 'viewAsset'))

		## Add new hotkeys back to file
		for each in hotKeyList:
			each= each.replace( '\n', '')

			if '<shortcut' in each:
				writeFile.write( '{0}\n'.format( each))
			else:
				writeFile.write( each+ '\n')
#
def optimizeHotKeyFile():
	## Grab hotkey file path
	hotkeyPath= getHotKeyFile()

	## Grab lines
	with open( hotkeyPath) as readFile:
		hotKeyList= readFile.readlines()

	tempList=[]
	## Remove Duplicate lines
	with open( hotkeyPath, 'wt') as writeFile:
		## Add new hotkeys back to file
		for each in hotKeyList:
			each= each.replace( '\n', '')

			if '<shortcut' in each:
				if each not in tempList:
					writeFile.write( '{0}\n'.format( each))

					## Add line to list to avoid duplicates
					tempList.append( each)

			else:
				writeFile.write( each+ '\n')
#
def loadUpdateHotKeys():
	'''
	Purpose:
		Set and load new HotKeys
	'''
	## Set new keys
	set_openKey()
	set_saveKey()
	set_incrementalSaveKey()
	set_importAssetKey()
	set_publishAssetKey()
	set_viewAssetKey()

	## Optimize file
	optimizeHotKeyFile()

	func='''
	hotkeyPath= actionMan.getKeyboardFile()
	print hotkeyPath
	actionMan.loadKeyboardFile hotkeyPath
	print "HotKeys have been updated!!!"
	'''
	## Run Maxscript
	translator.executeNativeCommand( func)