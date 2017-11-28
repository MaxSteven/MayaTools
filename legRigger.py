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
		joints.extend(mc.listRelatives(joints[0], allDescendents = True))

		for joint in joints:
			if 'Heel' in joint:
				joints.remove(joint)
				mc.parent(joint, worldSpace = True)
				break

		for joint in joints:
			self.blendedJoints.append(joint)

		for joint in joints:
			self.jointNames.append(joint.rpartition("_")[0])

		ikJointRoot = mc.duplicate(joints[0], n = jointNames[0]+"_IK_JNT", renameChildren = True)[0]
		ikJointDecendants = mc.listRelatives(ikJointRoot, allDescendents = True)
		self.ikJoints.append(ikJointRoot)
		for joint in ikJointDecendants:
			ikJoint = mc.rename(joint, joint.rpartition('_')[0] +"_IK_JNT")
			self.ikJoints.append(ikJoint)

		fkJointRoot = mc.duplicate(joints[0], n = jointNames[0]+"_FK_JNT", renameChildren = True)[0]
		fkJointDecendants = mc.listRelatives(fkJointRoot, allDescendents = True)
		self.fkJoints.append(fkJointRoot)
		for joint in fkJointDecendants:
			fkJoint = mc.rename(joint, joint.rpartition('_')[0] +"_FK_JNT")
			self.fkJoints.append(fkJoint)

		self.createFKControl()
		# self.createIKControl()

		# self.blend()

		# self.mainGroup = mc.group(self.fkJoints[0], self.ikJoints[0], self.blendedJoints[0], n = joint1+"_GRP")

	def createFKControl(self):
		for joint in self.fkJoints:
			if 'Heel' not in joint and 'Toe' not in joint:
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


	def generateFKControl(self):
		circle1 = mc.listRelatives(mc.circle( nr=(1, 0, 0), c=(0, 0, 0), r =5)[0], children = True)[0]
		mc.setAttr(circle1+".overrideEnabled", 1)
		mc.setAttr(circle1+".overrideColor", 13)
		circle2 = mc.listRelatives(mc.circle( nr=(0, 1, 0), c=(0, 0, 0), r = 5)[0], children = True)[0]
		mc.setAttr(circle2+".overrideEnabled", 1)
		mc.setAttr(circle2+".overrideColor", 13)
		circle3 = mc.listRelatives(mc.circle( nr=(0, 0, 1), c=(0, 0, 0), r = 5)[0], children = True)[0]
		mc.setAttr(circle3+".overrideEnabled", 1)
		mc.setAttr(circle3+".overrideColor", 13)
		groupName = mc.group(empty = True, n = "fkControl")
		mc.parent(circle1, groupName, relative = True, shape = True)
		mc.parent(circle2, groupName, relative = True, shape = True)
		mc.parent(circle3, groupName, relative = True, shape = True)
		return groupName

	def createIKControl(self):
		joint1Pos = mc.xform(self.ikJoints[0], q = True, ws = True, t = True)
		joint2Pos = mc.xform(self.ikJoints[1], q = True, ws = True, t = True)
		joint3Pos = mc.xform(self.ikJoints[2], q = True, ws = True, t = True)

		startV = OpenMaya.MVector(joint1Pos[0] ,joint1Pos[1],joint1Pos[2])
		midV = OpenMaya.MVector(joint2Pos[0] ,joint2Pos[1],joint2Pos[2])
		endV = OpenMaya.MVector(joint3Pos[0] ,joint3Pos[1],joint3Pos[2])

		startEnd = endV - startV
		startMid = midV - startV

		dotP = startMid * startEnd

		proj = float(dotP) / float(startEnd.length())

		startEndN = startEnd.normal()

		projV = startEndN * proj

		arrowV = startMid - projV

		arrowV*= 10

		finalV = arrowV + midV

		poleVectorControl = mc.spaceLocator(n = self.jointNames[1] + "_PV_CTL")[0]

		mc.xform(poleVectorControl , ws =1 , t= (finalV.x , finalV.y ,finalV.z))
		mc.makeIdentity(poleVectorControl, apply=True, t=1, r=1, s=1, n=0)

		kneeIkHandle = mc.ikHandle(sj = self.ikJoints[0], ee = self.ikJoints[2], sol = "ikRPsolver")[0]

		ikControlObject = mc.circle(nr = (0, 0, 1), c = (0,0,0), r = 10, name = self.jointNames[2]+"_IK_CTL")[0]

		mc.xform(ikControlObject, worldSpace=True, translation=mc.xform(self.ikJoints[2], query = True, worldSpace = True, translation = True))

		mc.makeIdentity(ikControlObject, apply=True, t=1, r=1, s=1, n=0)

		mc.parent(kneeIkHandle, ikControlObject)

		poleVector = mc.poleVectorConstraint(poleVectorControl, kneeIkHandle)

		self.ikControls.append(ikControlObject)
		self.ikControls.append(poleVectorControl)

		ballIkHandle = mc.ikHandle(sj = self.ikJoints[2], ee = self.ikJoints[3], sol = "ikSCsolver")[0]
		toeIkHandle = mc.ikHandle(sj = self.ikJoints[3], ee = self.ikJoints[4], sol = "ikSCsolver")[0]

		proxyHeelJoint = mc.joint()

		

	def blend(self):
		self.blendColor1 = mc.shadingNode("blendColors", asUtility = True, n = self.blendedJoints[0].rpartition("_")[0]+"_BLC")
		self.blendColor2 = mc.shadingNode("blendColors", asUtility = True, n = self.blendedJoints[1].rpartition("_")[0]+"_BLC")

		self.mainControl = mc.circle(nr = (0, 1, 0), c = (0,0,0), r = 3)[0]

		mc.addAttr(self.mainControl, ln = "ik_fk_blend", attributeType = "float", minValue = 0.00, maxValue = 1.00, keyable = True)

		mc.connectAttr(self.ikJoints[0]+".rotateX", self.blendColor1+".color1.color1R")
		mc.connectAttr(self.ikJoints[0]+".rotateY", self.blendColor1+".color1.color1G")
		mc.connectAttr(self.ikJoints[0]+".rotateZ", self.blendColor1+".color1.color1B")

		mc.connectAttr(self.fkJoints[0]+".rotateX", self.blendColor1+".color2.color2R")
		mc.connectAttr(self.fkJoints[0]+".rotateY", self.blendColor1+".color2.color2G")
		mc.connectAttr(self.fkJoints[0]+".rotateZ", self.blendColor1+".color2.color2B")

		mc.connectAttr(self.mainControl+".ik_fk_blend", self.blendColor1+".blender")

		mc.connectAttr(self.ikJoints[1]+".rotateX", self.blendColor2+".color1.color1R")
		mc.connectAttr(self.ikJoints[1]+".rotateY", self.blendColor2+".color1.color1G")
		mc.connectAttr(self.ikJoints[1]+".rotateZ", self.blendColor2+".color1.color1B")

		mc.connectAttr(self.fkJoints[1]+".rotateX", self.blendColor2+".color2.color2R")
		mc.connectAttr(self.fkJoints[1]+".rotateY", self.blendColor2+".color2.color2G")
		mc.connectAttr(self.fkJoints[1]+".rotateZ", self.blendColor2+".color2.color2B")

		mc.connectAttr(self.mainControl+".ik_fk_blend", self.blendColor2+".blender")

		mc.connectAttr(self.blendColor1+".outputR", self.blendedJoints[0]+".rotateX")
		mc.connectAttr(self.blendColor1+".outputG", self.blendedJoints[0]+".rotateY")
		mc.connectAttr(self.blendColor1+".outputB", self.blendedJoints[0]+".rotateZ")

		mc.connectAttr(self.blendColor2+".outputR", self.blendedJoints[1]+".rotateX")
		mc.connectAttr(self.blendColor2+".outputG", self.blendedJoints[1]+".rotateY")
		mc.connectAttr(self.blendColor2+".outputB", self.blendedJoints[1]+".rotateZ")

		self.reverseNode1 = mc.shadingNode("reverse", asUtility = True, n = self.blendedJoints[0].rpartition("_")[0]+"_REV")

		mc.connectAttr(self.mainControl+".ik_fk_blend", self.reverseNode1+".input.inputX")

		mc.connectAttr(self.reverseNode1+".outputX", self.fkControls[0]+".visibility")
		mc.connectAttr(self.reverseNode1+".outputX", self.fkControls[1]+".visibility")
		mc.connectAttr(self.reverseNode1+".outputX", self.fkControls[2]+".visibility")

		mc.connectAttr(self.mainControl+".ik_fk_blend", self.ikControls[0]+".visibility")
		mc.connectAttr(self.mainControl+".ik_fk_blend", self.ikControls[1]+".visibility")
		ikControlPos = mc.xform(self.ikControls[0], query = True, worldSpace = True, rp = True)
		self.mainControlPos = [pos + 10 for pos in ikControlPos]
		mc.xform(self.mainControl, worldSpace=True, translation=self.mainControlPos)

object = IkFkBlending()