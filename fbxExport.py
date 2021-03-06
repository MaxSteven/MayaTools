import maya.cmds as mc

def exportAnimation(options=None):
	if not options:
		return
	path = options['AnimDir'] + '/' + options['AnimName'] + '.fbx'
	frameRangeText = options['FrameRange']
	frameRange = [int(frame) for frame in frameRangeText.split('-')]
	frameRangeTuple = (frameRange[0], frameRange[1])
	if not len(mc.ls(sl=True)):
		return

	selection = mc.ls(sl=True)[0]
	rFile = mc.referenceQuery(selection, filename=True)
	namespace = mc.referenceQuery(selection, namespace=True).replace(':', '')
	mc.file(rFile, importReference = True)
	mc.select(selection, hi=True)
	objectsToDelete = mc.ls(sl=True)
	for obj in objectsToDelete:
		try:
			mc.rename(obj, obj.replace(namespace + ':', ''))
		except:
			pass

	selection = selection.replace(namespace + ':', '')
	mc.select(selection, hi=True)
	objectsToDelete = mc.ls(sl=True)
	mc.select([obj for obj in mc.ls(type='joint') if 'Bind' in obj])
	joints = mc.ls(sl=True)
	if frameRangeTuple[0] != frameRangeTuple[1]:
		mc.bakeResults(joints, simulation=True, t = frameRangeTuple,
				sampleBy = 1, disableImplicitControl=True,
				preserveOutsideKeys=True, sparseAnimCurveBake=False,
				removeBakedAttributeFromLayer=False, removeBakedAnimFromLayer=False,
				bakeOnOverrideLayer=False, minimizeRotation=True, controlPoints=False,
				shape=True
				)
	mc.select(joints, d=True)
	mc.select([obj for obj in mc.ls(type='transform') if 'lowPoly' in obj])
	lowPolyParent = mc.ls(sl=True)[0]
	print lowPolyParent
	rootJointParent = next(joint for joint in joints if 'Ground' in joint)
	print rootJointParent
	selectionChildren = mc.listRelatives(selection, children=True)
	for child in selectionChildren:
		if child not in ['Deformation', 'GEO']:
			mc.delete(child)
	mc.select(rootJointParent, hi=True)
	siblings = [child for child in mc.listRelatives('Deformation', children=True) if 'Ground' not in child]
	print siblings
	mc.delete(siblings)
	allJoints = mc.ls(sl=True)
	uselessJoints = [joint for joint in allJoints if 'End' in joint]
	for joint in uselessJoints:
		allJoints.remove(joint)
		mc.delete(joint)
	print allJoints
	for joint in allJoints:
		for attr in ['scaleX', 'scaleY', 'scaleZ', 'visibility']:
			object = mc.listConnections(joint + '.' + attr, source=True)
			print 'deleting', object
			mc.delete(object)

	mc.xform('Deformation', scale = (.01, .01, .01))
	try:

		mel.eval('file -force -options "v=0;" -typ "FBX export" -pr -es "' + path + '";')
		print 'FBX export successful'
	except:
		print "Export failed!"

exportAnimation(options = {'AnimDir': 'Q:/Assets/models_v003/humans/crowd_anim/Publish/', 'AnimName': 'crowd_female_tPose_v0002_1001-1001', 'FrameRange':'1001-1001'})
