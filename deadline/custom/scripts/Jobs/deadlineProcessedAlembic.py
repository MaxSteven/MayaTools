import os
import sys
sys.path.append(os.environ.get('ARK_PYTHONLIB'))

import math

import deadline

import arkInit
arkInit.init()
import cOS

os.environ['ARK_CURRENT_APP'] = 'houdini_cl'

import settingsManager
globalSettings = settingsManager.globalSettings()
sys.path.append(globalSettings.HOUDINI_TOOLS_ROOT + 'houdini16.0/python')

import translators
translator = translators.getCurrent()

import hou

def renderProcessedAlembic():
	arkDeadline = deadline.arkDeadline.ArkDeadline()
	sheepName = cOS.getComputerName()
	currentJobID = arkDeadline.getSheepInfo(sheepName)[u'JobId']
	currentJob = arkDeadline.getJob(currentJobID)

	jobProperties = currentJob[u'Props']
	extraDict = jobProperties.get(u'ExDic')
	filepath = extraDict.get(u'abc_in')
	frames = str(extraDict.get(u'abc_frames')).split('-')
	startFrame = int(frames[0])
	endFrame = int(frames[-1])

	if not extraDict.get(u'abc_fps'):
		fps = 24
	else:
		fps = int(math.ceil(int(extraDict.get(u'abc_fps'))))

	outputPath = extraDict.get(u'abc_out')

	hou.hipFile.load(globalSettings.HOUDINI_PROCESS_ALEMBIC_FILE, ignore_load_warnings=True)


	hou.node('/obj/process_alembic/import_alembic').parm('fileName').set(filepath)
	hou.node('/obj/process_alembic/rop_alembic1').parm('partition_attribute').set('materialName')

	hou.node('/obj/process_alembic/rop_alembic1').parm('filename').set(outputPath)
	hou.node('/obj/process_alembic/rop_alembic1').parm('f1').set(startFrame)
	hou.node('/obj/process_alembic/rop_alembic1').parm('f2').set(endFrame)
	translator.setFPS(fps)
	hou.node('/obj/process_alembic/rop_alembic1').render()
	print 'Alembic Rendered Successfully!'

def main():
	renderProcessedAlembic()

if __name__ == '__main__':
	main()
