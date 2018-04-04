# Name: Animation Publisher
# Author: Shobhit Khinvasara

import maya.cmds as mc
import maya
import pymel.core as pymel

import arkInit
arkInit.init()

import translators
translator = translators.getCurrent()

import baseWidget

class AnimationPublisher(baseWidget.BaseWidget):
	defaultOptions = {
		'title': 'Animation Publisher',

		'knobs': [
			{
				'name':'Animation directory',
				'dataType': 'directory'
			},
			{
				'name': 'Animation Sequence Name',
				'dataType': 'text'
			},
			{
				'name': 'Frame Range',
				'dataType': 'FrameRange'
			},
			{
				'name': 'Export FBX',
				'dataType': 'checkbox',
				'value': True
			},
			{
				'name': 'Publish Animation',
				'dataType': 'PythonButton',
				'callback': 'publishAnimation'
			}
		]
	}

	def init(self):
		pass

	def postShow(self):
		pass

	def publishAnimation(self):
		animationOptions = {
			'AnimDir': self.getKnob('Animation directory').getValue(),
			'AnimName': self.getKnob('Animation Sequence Name').getValue(),
			'FrameRange': self.getKnob('Frame Range').getValue(),
			'Export': self.getKnob('Export FBX').getValue()
		}
		# get/set animation publishing options
		exportAnimation(options=animationOptions)


def gui():
	return AnimationPublisher()

def launch(docked=False):
	translator.launch(AnimationPublisher, docked=docked)

def exportAnimation(options=None):
	if not options:
		return

	frameRangeText = options['FrameRange']
	animName = options['AnimName'] + '_' + frameRangeText
	path = options['AnimDir'] + '/' + animName + '.fbx'
	frameRange = [int(frame) for frame in frameRangeText.split('-')]
	frameRangeTuple = (frameRange[0], frameRange[1])
	if not len(mc.ls(sl=True)):
		return

	selection = mc.ls(sl=True)[0]
	namespace = selection.split(':')[0]
	for ref in pymel.listReferences(recursive=True):
		ref.importContents()

	mc.select(selection, hi=True)
	objectsToDelete = mc.ls(sl=True)
	mc.namespace(removeNamespace=namespace, mergeNamespaceWithRoot=True)

	# for obj in objectsToDelete:
	# 	try:
	# 		mc.rename(obj, obj.replace(namespace + ':', ''))
	# 	except:
	# 		pass
	selection = selection.replace(namespace + ':', '')
	mc.select([obj for obj in mc.ls(type='joint') if 'Bind' in obj])
	joints = mc.ls(sl=True)
	mc.bakeResults(joints, simulation=True, t = frameRangeTuple,
				sampleBy = 1, disableImplicitControl=True,
				preserveOutsideKeys=True, sparseAnimCurveBake=False,
				removeBakedAttributeFromLayer=False, removeBakedAnimFromLayer=False,
				bakeOnOverrideLayer=False, minimizeRotation=True, controlPoints=False,
				shape=True
				)

	for attr in mc.listAttr('bsh_all', keyable=True):
		mc.setKeyframe('bsh_all', attribute = attr, time = frameRangeTuple[0])

	mc.select(joints, d=True)
	mc.select([obj for obj in mc.ls(type='transform') if 'lowPoly' in obj])
	lowPolyParent = mc.ls(sl=True)[0]
	rootJointParent = next(joint for joint in joints if 'Ground' in joint)
	selectionChildren = mc.listRelatives(selection, children=True)
	for child in selectionChildren:
		if child not in ['Deformation', 'GEO']:
			mc.delete(child)
	mc.select(rootJointParent, hi=True)
	siblings = [child for child in mc.listRelatives('Deformation', children=True) if 'Ground' not in child]
	mc.delete(siblings)
	allJoints = mc.ls(sl=True)
	uselessJoints = [joint for joint in allJoints if 'End' in joint]
	for joint in uselessJoints:
		allJoints.remove(joint)
		mc.delete(joint)

	for joint in allJoints:
		for attr in ['scaleX', 'scaleY', 'scaleZ', 'visibility']:
			object = mc.listConnections(joint + '.' + attr, source=True)
			print 'deleting', object
			mc.delete(object)

	mc.xform('Deformation', scale = (.01, .01, .01))
	mc.select(selection)
	mc.refresh()

	if options['Export']:
		try:
			mel.eval('file -force -options "groups=1;ptgroups=1;materials=1;smoothing=1;normals=1" -typ "FBX export" -pr -es "' + path + '"')
			print 'FBX export successful', path
		except:
			print "Export failed!"

# exportAnimation(options = {'AnimDir': 'c:/Shobhit_Stuff/', 'AnimName': 'testingAgain_2', 'FrameRange':'1-30'})
launch()