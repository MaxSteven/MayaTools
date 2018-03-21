import maya.cmds as mc

def handRig():
	handRootJoint = mc.ls(sl=True)[0]
	allFingers = [obj for obj in mc.listRelatives(handRootJoint, allDescendents=True) if mc.listRelatives(obj, children=True) != None]
	for finger in allFingers:
		setupFKControl(finger)


def setupFKControl(obj, circleSize = .5):
	control = mc.circle(n = obj.replace('JNT', 'CTL'), nr=(0, 0, 1), c=(0, 0, 0), r = circleSize)[0]
	controlGroup = mc.group(control, n = obj.replace('JNT', 'GRP'))
	mc.parent(controlGroup, obj)
	mc.makeIdentity(controlGroup, t = 1, r = 1, s = 1)
	mc.parent(controlGroup, world=True)
	objParent = mc.listRelatives(obj, parent=True)
	mc.parent(controlGroup, objParent)
	mc.parent(obj, control)

handRig()


