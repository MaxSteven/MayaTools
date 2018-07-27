import os

import arkInit
arkInit.init()
import cOS

import deadline

import settingsManager
globalSettings = settingsManager.globalSettings()

import translators
translator = translators.getCurrent()

def getFilename(prefix, frame, padding):
	num = str(frame)
	return prefix + '.' +  '0' * (padding - len(num)) + num + '.ifd.sc'

def deleteWedgeSceneFiles():
	print 'Deleting wedge scene files'
	arkDeadline = deadline.arkDeadline.ArkDeadline()
	sheepName = cOS.getComputerName()
	currentJobID = arkDeadline.getSheepInfo(sheepName)[u'JobId']
	currentJob = arkDeadline.getJob(currentJobID)

	jobProperties = currentJob[u'Props']
	extraDict = jobProperties.get(u'ExDic')
	hipFolder = extraDict['wedgedFolder']
	wedgeNodePath = extraDict['wedgeNodePath']

	for hFile in os.listdir(hipFolder):
		if os.path.isfile(hFile) and \
			wedgeNodePath in hFile:
			print 'Removing hFile:', hFile
			os.remove(hFile)

def __main__(*args):
	deleteWedgeSceneFiles()

if __name__ == '__main__':
	__main__()
