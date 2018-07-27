import os
import re

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

def deleteIFDFiles():
	arkDeadline = deadline.arkDeadline.ArkDeadline()
	sheepName = cOS.getComputerName()
	currentJobID = arkDeadline.getSheepInfo(sheepName)[u'JobId']
	currentJob = arkDeadline.getJob(currentJobID)

	jobProperties = currentJob[u'Props']
	submittedJobID = jobProperties.get(u'ExDic')[u'jobID']
	submittedJob = arkDeadline.getJob(submittedJobID)
	ifdFile = submittedJob[u'Props'][u'PlugInfo'][u'SceneFile']

	ifdRegex = r'(.*)\.([0-9]*)\.ifd(\.sc)?'
	ifdMatch = re.match(ifdRegex, ifdFile)
	if ifdMatch:
		prefix = ifdMatch.group(1)
		padding = len(ifdMatch.group(2))

		frames = submittedJob[u'Props'][u'Frames']
		frameSplit = frames.split('-')

		if not len(frameSplit):
			raise Exception('Could not parse frame list')

		elif len(frameSplit) == 1:
			frameSplit = frameSplit[0].split(',')
			for frame in frameSplit:
				path = getFilename(prefix, int(frame), padding)
				try:
					if os.path.isfile(path):
						os.remove(path)
					else:
						print 'unable to delete ', path
				except Exception as err:
					print err
			return

		elif len(frameSplit) == 2:
			startFrame = int(frameSplit[0])
			endFrame = int(frameSplit[1])

		for f in range(startFrame, endFrame + 1):
			path = getFilename(prefix, f, padding)
			print 'deleting', path
			try:
				if os.path.isfile(path):
					os.remove(path)
				else:
					print 'unable to delete ', path
			except Exception as err:
				print err

	else:
		raise Exception('Could not match ifd file')

def __main__(*args):
	deleteIFDFiles()

if __name__ == '__main__':
	__main__()
