import os
import re

def getFilename(prefix, frame, padding):
	num = str(frame)
	return prefix + '0' * (padding - len(num)) + num + '.vrscene'

def deleteSceneFiles(deadlinePlugin):
	vrayFile = deadlinePlugin.GetPluginInfoEntry('InputFilename')
	vrayRegex = r'(.*_)(0*).vrscene'
	vrayMatch = re.match(vrayRegex, vrayFile)
	if vrayMatch:
		prefix = vrayMatch.group(1)
		padding = len(vrayMatch.group(2))

		framesList = deadlinePlugin.GetJob().FramesList
		frameChunks = framesList.split(',')
		for frames in frameChunks:
			frameSplit = frames.split('-')
			if not len(frameSplit):
				raise Exception('Could not parse frame list')
			elif len(frameSplit) == 1:
				startFrame = int(frameSplit[0])
				endFrame = startFrame
			elif len(frameSplit) == 2:
				startFrame = int(frameSplit[0])
				endFrame = int(frameSplit[1])
			for f in range(startFrame, endFrame + 1):
				path = getFilename(prefix, f, padding)
				print 'deleting', path
				try:
					if os.path.isfile(path):
						os.unlink(path)
				except Exception as err:
					print err
	else:
		raise Exception('Could not match vray file')

def __main__(*args):
	deadlinePlugin = args[0]
	deleteSceneFiles(deadlinePlugin)

