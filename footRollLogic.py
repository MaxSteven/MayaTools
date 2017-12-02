import maya.cmds as mc

side = mc.ls(sl=True)[0].split('_')[0]

for joint in mc.ls(sl=True):
	if 'Heel' in joint:
		heelJoint = joint
	elif 'Ankle' in joint:
		ankleJoint = joint
	elif 'Toe' in joint:
		toeJoint = joint
	elif 'Ball' in joint:
		ballJoint = joint

mc.select(clear=True)

proxyHeel1Joint = mc.joint(p=mc.xform(heelJoint, query=True, worldSpace=True, translation=True))
mc.select(clear=True)
proxyHeel2Joint = mc.joint(p=mc.xform(heelJoint, query=True, worldSpace=True, translation=True))
mc.select(clear=True)
proxyBallJoint = mc.joint(p=mc.xform(ballJoint, query=True, worldSpace=True, translation=True))
mc.select(clear=True)
proxyToeJoint = mc.joint(p=mc.xform(toeJoint, query=True, worldSpace=True, translation=True))
mc.select(clear=True)
proxyAnkle1Joint = mc.joint(p=mc.xform(ankleJoint, query=True, worldSpace=True, translation=True))
mc.select(clear=True)
proxyAnkle2Joint = mc.joint(p=mc.xform(ankleJoint, query=True, worldSpace=True, translation=True))
mc.select(clear=True)
mc.parent(proxyToeJoint, proxyHeel1Joint)
mc.parent(proxyBallJoint, proxyHeel2Joint)
mc.parent(proxyAnkle1Joint, proxyToeJoint)
mc.parent(proxyAnkle2Joint, proxyBallJoint)

# orient proxy joint chains
mc.joint(proxyHeel1Joint, edit = True, orientJoint='zyx', sao='yup', children=True)
mc.joint(proxyHeel2Joint, edit = True, orientJoint='zyx', sao='yup', children=True)

# placing groups
HeelOffsetGroup = mc.group(empty=True, n = side + '_HeelOffset_GRP')
HeelGroup = mc.group(empty=True, n = side + '_Heel_GRP')
mc.parent(HeelOffsetGroup, proxyHeel1Joint)
mc.xform(HeelOffsetGroup, rotation = [0,0,0], translation = [0,0,0], a = True)
mc.parent(HeelGroup, HeelOffsetGroup)
mc.xform(HeelGroup, rotation = [0,0,0], translation = [0,0,0], a = True)
mc.parent(HeelOffsetGroup, world=True)

ToeOffsetGroup = mc.group(empty=True, n = side + '_ToeOffset_GRP')
ToeGroup = mc.group(empty=True, n = side + '_Toe_GRP')
mc.parent(ToeOffsetGroup, proxyToeJoint)
mc.xform(ToeOffsetGroup, rotation = [0,0,0], translation = [0,0,0], a = True)
mc.parent(ToeGroup, ToeOffsetGroup)
mc.xform(ToeGroup, rotation = [0,0,0], translation = [0,0,0], a = True)
mc.parent(ToeOffsetGroup, world=True)

BallOffsetGroup = mc.group(empty=True, n = side + '_BallOffset_GRP')
BallGroup = mc.group(empty=True, n = side + '_Ball_GRP')
mc.parent(BallOffsetGroup, proxyBallJoint)
mc.xform(BallOffsetGroup, rotation = [0,0,0], translation = [0,0,0], a = True)
mc.parent(BallGroup, BallOffsetGroup)
mc.xform(BallGroup, rotation = [0,0,0], translation = [0,0,0], a = True)
mc.parent(BallOffsetGroup, world=True)

mc.parent(ToeOffsetGroup, HeelGroup)
mc.parent(BallOffsetGroup, ToeGroup)

ToeTapOffsetGroup = mc.duplicate(BallOffsetGroup, n = side + '_ToeTapOffset_GRP', renameChildren = True)[0]
ToeTapGroup = mc.rename(mc.listRelatives(ToeTapOffsetGroup, children=True)[0], side + '_ToeTap_GRP')

mc.parent(ToeTapOffsetGroup, world=True)
mc.xform(ToeTapOffsetGroup, rotation=[0,0,0], a=True)
mc.parent(ToeTapOffsetGroup, HeelGroup)

mc.delete(proxyHeel1Joint)
mc.delete(proxyHeel2Joint)

# parent ik handle