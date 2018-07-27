import os

del os.environ['FTRACK_TASKID']
del os.environ['FTRACK_SHOTID']

import maya.standalone
maya.standalone.initialize()
import maya.cmds as cmds
from sys import argv

def run(turntableFile, referenceFile, newTurntableFile):
	cmds.file(turntableFile, open=True, force=True)
	cmds.file(referenceFile, reference=True, groupReference=True, force=True)

	objGroup = cmds.group(name='turntable_objects')
	cmds.makeIdentity(objGroup, a=True, s=True, t=True, r=True)
	cmds.xform(objGroup, centerPivots=True)

	bboxGroup = cmds.exactWorldBoundingBox(objGroup)
	bboxBounding = cmds.exactWorldBoundingBox('boundingBox')

	bboxGroupLength = toLength(bboxGroup)
	bboxBoundingLength = toLength(bboxBounding)

	factor = scalingFactor(bboxGroupLength, bboxBoundingLength)

	cmds.xform('turntable_scale', scale=[factor,factor,factor])

	cmds.move(
		0,
		(-.5 * bboxGroupLength[1]),
		0,
		objGroup + '.scalePivot',
		objGroup + '.rotatePivot',
		relative=True)
	cmds.move(
		0,
		0.025 * factor,
		0,
		objGroup,
		rpr=True)

	cmds.parent(objGroup, 'turntable_rotate')

	referencePathName = os.path.splitext(referenceFile)[0].rstrip('_turntableReference')

	newTurntableFile = referencePathName + '_turntable.mb'
	cmds.file(rename=newTurntableFile)
	cmds.file(type='mayaBinary', save=True, force=True)

	return newTurntableFile

def toLength(bbox):
	return [abs(bbox[0] - bbox[3]), abs(bbox[1] - bbox[4]), abs(bbox[2] - bbox[5])]

def scalingFactor(bbox1, bbox2):
	return max(max(bbox1[0] / bbox2[0], bbox1[1] / bbox2[1]), bbox1[2] / bbox2[2])

def main():
	turntableFile = 'R:/Test_Project/Workspaces/maya/3D/turntable_test_v0010.mb'
	referenceFile = argv[1]
	newTurntableFile = argv[2]

	run(turntableFile, referenceFile, newTurntableFile)

	maya.standalone.uninitialize()
	os._exit(0)

if __name__ == '__main__':
	main()