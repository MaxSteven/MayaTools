import maya.cmds as mc

selectedObjects = mc.ls(sl = True)
blenderAttr = 'UpperBody_CTL.FkRibbonSpine'
reverseNode = mc.shadingNode('reverse', asUtility=True, n = 'Spine_REV')
mc.connectAttr(blenderAttr, reverseNode + '.input.inputX')
for obj in selectedObjects:
	IKObject = obj.replace('Rig_', 'IKRig_')
	FKObject = obj.replace('Rig_', 'FKRig_')

	parentConstraint = mc.parentConstraint(IKObject, obj, mo=True)[0]
	parentConstraint = mc.parentConstraint(FKObject, obj, mo=True)[0]

	mc.connectAttr(blenderAttr, parentConstraint + '.' + IKObject + 'W0')
	mc.connectAttr(reverseNode + '.outputX', parentConstraint + '.' + FKObject + 'W1')

	mc.connectAttr(reverseNode + '.outputX', FKObject + '.visibility')
