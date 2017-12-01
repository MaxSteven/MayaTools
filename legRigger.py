import maya.cmds as mc
from maya import OpenMaya

class IkFkBlending():
	def __init__(self):
		self.blendedJoints = []
		self.fkJoints = []
		self.jointNames = []
		self.ikJoints = []
		self.ikControls = []
		self.fkControls = []
		self.fkControlGroups = []

		joints = mc.ls(sl = True)
		self.side = joints[0].split('_')[0]
		joints.extend(mc.listRelatives(joints[0], allDescendents = True))

		for joint in joints:
			if 'Heel' in joint:
				joints.remove(joint)
				# mc.parent(joint, worldSpace = True)
				break

		for joint in joints:
			if 'Heel' not in joint and 'Toe' not in joint:
				self.blendedJoints.append(joint)

		for joint in joints:
			self.jointNames.append(joint.rpartition("_")[0])

		ikJointRoot = mc.duplicate(joints[0], n = self.jointNames[0]+"_IK_JNT", renameChildren = True)[0]
		self.ikJoints.append(ikJointRoot)
		ikJointDecendants = mc.listRelatives(ikJointRoot, allDescendents = True)
		for joint in ikJointDecendants:
			ikJoint = mc.rename(joint, joint.rpartition('_')[0] +"_IK_JNT")
			self.ikJoints.append(ikJoint)

		fkJointRoot = mc.duplicate(joints[0], n = self.jointNames[0]+"_FK_JNT", renameChildren = True)[0]
		fkJointDecendants = mc.listRelatives(fkJointRoot, allDescendents = True)
		self.fkJoints.append(fkJointRoot)
		for joint in fkJointDecendants:
			fkJoint = mc.rename(joint, joint.rpartition('_')[0] +"_FK_JNT")
			if 'Heel' not in fkJoint and 'Toe' not in fkJoint:
				print fkJoint
				self.fkJoints.append(fkJoint)

			else:
				print fkJoint

		self.createFKControl()
		self.createIKControl()

		self.blend()

		self.mainGroup = mc.group(self.fkJoints[0], self.ikJoints[0], self.blendedJoints[0], n = self.jointNames[0] + "_GRP")

	def createFKControl(self):
		for joint in self.fkJoints:
			control = self.generateFKControl()
			controlName = joint.rpartition("_")[0] + "_CTL"
			FKControlObject = mc.rename(control, controlName)
			self.fkControls.append(FKControlObject)
			FKControlObjectShapes = mc.listRelatives(FKControlObject, children = True)
			mc.parent(FKControlObject, joint, relative = True)
			mc.makeIdentity(FKControlObject)
			mc.parent(FKControlObject, world = True)
			for shape in FKControlObjectShapes:
				mc.parent(shape, joint, relative = True, shape = True)

			mc.delete(FKControlObject)

		# for joint in self.fkJoints:
		# 	controlObject = self.generateFKControl()
		# 	controlName = joint.rpartition("_")[0] + "_CTL"
		# 	FKControlObject = mc.rename(controlObject, controlName)
		# 	self.fkControls.append(FKControlObject)
		# 	mc.xform(FKControlObject, worldSpace=True, translation=mc.xform(joint, query = True, worldSpace = True, translation = True))
		# 	groupName = mc.group(FKControlObject, n = joint.rpartition("_")[0] + "_GRP")
		# 	mc.parent(groupName, joint)
		# 	mc.makeIdentity(groupName, apply=True, t=1, r=1, s=1, n=0)
		# 	mc.parent(groupName, world = True)
		# 	mc.orientConstraint(FKControlObject, joint)
		# 	self.fkControlGroups.append(groupName)
		# mc.parent(self.fkControlGroups[2], self.fkControls[1])
		# mc.parent(self.fkControlGroups[1], self.fkControls[0])

	def generateFKControl(self):
		groupName = mc.group(empty = True, n = "fkControl")
		normalAxes = [(1,0,0), (0,1,0), (0,0,1)]
		for normalAxis in normalAxes:
			circleTransform = mc.circle(nr = normalAxis, c=(0, 0, 0), r = 5)[0]
			circle = mc.listRelatives(circleTransform, children = True)[0]
			mc.setAttr(circle+".overrideEnabled", 1)
			mc.setAttr(circle+".overrideColor", 13)
			mc.parent(circle, groupName, relative = True, shape = True)
			mc.delete(circleTransform)
		return groupName

	def createIKControl(self):
		joint1Pos = mc.xform(self.ikJoints[0], q = True, ws = True, t = True)
		joint2Pos = mc.xform(self.ikJoints[1], q = True, ws = True, t = True)
		joint3Pos = mc.xform(self.ikJoints[2], q = True, ws = True, t = True)

		startV = OpenMaya.MVector(joint1Pos[0] ,joint1Pos[1],joint1Pos[2])
		midV = OpenMaya.MVector(joint2Pos[0] ,joint2Pos[1],joint2Pos[2])
		endV = OpenMaya.MVector(joint3Pos[0] ,joint3Pos[1],joint3Pos[2])

		for joint in self.ikJoints:
			if 'Heel' in joint:
				heelJoint = joint
				self.ikJoints.remove(joint)
				break

		for joint in self.ikJoints:
			if 'Ankle' in joint:
				ankleJoint = joint
			elif 'Toe' in joint:
				toeJoint = joint
			elif 'Ball' in joint:
				ballJoint = joint
			elif 'Knee' in joint or 'Shin' in joint:
				shinJoint = joint

		startEnd = endV - startV
		startMid = midV - startV

		dotP = startMid * startEnd

		proj = float(dotP) / float(startEnd.length())

		startEndN = startEnd.normal()

		projV = startEndN * proj

		arrowV = startMid - projV

		arrowV*= 10

		finalV = arrowV + midV

		self.poleVectorControl = mc.spaceLocator(n = shinJoint.rpartition('_')[0] + "_PV_CTL", p = (finalV.x , finalV.y ,finalV.z))[0]

		mc.makeIdentity(self.poleVectorControl, apply=True, t=1, r=1, s=1, n=0)

		kneeIkHandle = mc.ikHandle(sj = self.ikJoints[0], ee = ankleJoint, sol = "ikRPsolver")[0]

		self.ikControlObject = mc.circle(nr = (0, 0, 1), c = (0,0,0), r = 10, name = self.jointNames[2]+"_IK_CTL")[0]

		mc.xform(self.ikControlObject, worldSpace=True, translation=mc.xform(self.ikJoints[2], query = True, worldSpace = True, translation = True))

		mc.makeIdentity(self.ikControlObject, apply=True, t=1, r=1, s=1, n=0)

		mc.parent(kneeIkHandle, self.ikControlObject)

		mc.poleVectorConstraint(self.poleVectorControl, kneeIkHandle)

		mc.xform(self.poleVectorControl, centerPivots=True)

		ballIkHandle = mc.ikHandle(sj = ankleJoint, ee = ballJoint, sol = "ikSCsolver")[0]
		toeIkHandle = mc.ikHandle(sj = ballJoint, ee = toeJoint, sol = "ikSCsolver")[0]

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
		HeelOffsetGroup = mc.group(empty=True, n = self.side + '_HeelOffset_GRP')
		HeelGroup = mc.group(empty=True, n = self.side + '_Heel_GRP')
		mc.parent(HeelOffsetGroup, proxyHeel1Joint)
		mc.xform(HeelOffsetGroup, rotation = [0,0,0], translation = [0,0,0], a = True)
		mc.parent(HeelGroup, HeelOffsetGroup)
		mc.xform(HeelGroup, rotation = [0,0,0], translation = [0,0,0], a = True)
		mc.parent(HeelOffsetGroup, world=True)

		ToeOffsetGroup = mc.group(empty=True, n = self.side + '_ToeOffset_GRP')
		ToeGroup = mc.group(empty=True, n = self.side + '_Toe_GRP')
		mc.parent(ToeOffsetGroup, proxyToeJoint)
		mc.xform(ToeOffsetGroup, rotation = [0,0,0], translation = [0,0,0], a = True)
		mc.parent(ToeGroup, ToeOffsetGroup)
		mc.xform(ToeGroup, rotation = [0,0,0], translation = [0,0,0], a = True)
		mc.parent(ToeOffsetGroup, world=True)

		BallOffsetGroup = mc.group(empty=True, n = self.side + '_BallOffset_GRP')
		BallGroup = mc.group(empty=True, n = self.side + '_Ball_GRP')
		mc.parent(BallOffsetGroup, proxyBallJoint)
		mc.xform(BallOffsetGroup, rotation = [0,0,0], translation = [0,0,0], a = True)
		mc.parent(BallGroup, BallOffsetGroup)
		mc.xform(BallGroup, rotation = [0,0,0], translation = [0,0,0], a = True)
		mc.parent(BallOffsetGroup, world=True)

		mc.parent(ToeOffsetGroup, HeelGroup)
		mc.parent(BallOffsetGroup, ToeGroup)

		ToeTapOffsetGroup = mc.duplicate(BallOffsetGroup, n = self.side + '_ToeTapOffset_GRP', renameChildren = True)[0]
		ToeTapGroup = mc.rename(mc.listRelatives(ToeTapOffsetGroup, children=True)[0], self.side + '_ToeTap_GRP')

		mc.parent(ToeTapOffsetGroup, world=True)
		mc.xform(ToeTapOffsetGroup, rotation=[0,0,0], a=True)
		mc.parent(ToeTapOffsetGroup, HeelGroup)

		mc.delete(proxyHeel1Joint)
		mc.delete(proxyHeel2Joint)

		mc.parent(kneeIkHandle, BallGroup)
		mc.parent(ballIkHandle, BallGroup)
		mc.parent(toeIkHandle, ToeTapGroup)

		mc.addAttr(self.ikControlObject, longName='HeelRoll', attributeType='float', defaultValue=0, keyable=True)
		mc.connectAttr(self.ikControlObject + '.HeelRoll', HeelGroup + '.rotateX')
		mc.addAttr(self.ikControlObject, longName='BallRoll', attributeType='float', defaultValue=0, keyable=True)
		mc.connectAttr(self.ikControlObject + '.BallRoll', BallGroup + '.rotateX')
		mc.addAttr(self.ikControlObject, longName='ToeRoll', attributeType='float', defaultValue=0, keyable=True)
		mc.connectAttr(self.ikControlObject + '.ToeRoll', ToeGroup + '.rotateX')
		mc.addAttr(self.ikControlObject, longName='HeelPivot', attributeType='float', defaultValue=0, keyable=True)
		mc.connectAttr(self.ikControlObject + '.HeelPivot', HeelGroup + '.rotateY')
		mc.addAttr(self.ikControlObject, longName='BallPivot', attributeType='float', defaultValue=0, keyable=True)
		mc.connectAttr(self.ikControlObject + '.BallPivot', BallGroup + '.rotateY')
		mc.addAttr(self.ikControlObject, longName='ToePivot', attributeType='float', defaultValue=0, keyable=True)
		mc.connectAttr(self.ikControlObject + '.ToePivot', ToeGroup + '.rotateY' )
		mc.addAttr(self.ikControlObject, longName='ToeTap', attributeType='float', defaultValue=0, keyable=True)
		mc.connectAttr(self.ikControlObject + '.ToeTap', ToeTapGroup + '.rotateX')

		mc.parent(HeelOffsetGroup, self.ikControlObject)

	def blend(self):
		mainControl = mc.circle(nr = (0, 1, 0), c = (0,0,0), r = 3, n = self.jointNames[0] + "_CTL")[0]
		mc.addAttr(mainControl, ln = "ik_fk_blend", attributeType = "float", minValue = 0.00, maxValue = 1.00, keyable = True)
		reverseNode = mc.shadingNode("reverse", asUtility = True, n = self.blendedJoints[0].rpartition("_")[0]+"_REV")
		mc.connectAttr(mainControl+".ik_fk_blend", reverseNode+".input.inputX")
		for joint in self.blendedJoints:
			blendColor = mc.shadingNode("blendColors", asUtility = True, n = joint.rpartition("_")[0]+"_BLC")

			mc.connectAttr(joint.replace('_JNT', '_IK_JNT')+'.rotate', blendColor + '.color1' )
			mc.connectAttr(joint.replace('_JNT', '_FK_JNT')+'.rotate', blendColor + '.color2' )
			mc.connectAttr(mainControl + '.ik_fk_blend', blendColor + '.blender')

			mc.connectAttr(blendColor + '.output', joint + '.rotate')

		for joint in self.fkJoints:
			mc.connectAttr(reverseNode + '.outputX', joint + '.visibility')

		mc.connectAttr(mainControl + '.ik_fk_blend', self.ikControlObject + '.visibility')
		mc.connectAttr(mainControl + '.ik_fk_blend', self.poleVectorControl + '.visibility')

		ikControlPos = mc.xform(self.ikControlObject, query = True, worldSpace = True, rp = True)
		self.mainControlPos = [pos + 10 for pos in ikControlPos]
		mc.xform(mainControl, worldSpace=True, translation=self.mainControlPos)

object = IkFkBlending()