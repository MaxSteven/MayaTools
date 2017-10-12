import maya.cmds as mc
from maya import OpenMaya

import os
import inspect
try:
	from PySide2 import QtCore, QtNetwork
	from PySide2 import QtWidgets
	from PySide2 import QtGui

	for name in dir(QtWidgets):
		obj = getattr(QtWidgets, name)
		if inspect.isclass(obj):
			setattr(QtGui, name, obj)

except:
	from PySide import QtGui
	from PySide import QtCore

class IkFkBlender(QtGui.QDialog):
	def __init__(self, parent=None):

		super(IkFkBlender, self).__init__(parent=parent)
		self.blendedJoints = []
		self.fkJoints = []
		self.jointNames = []
		self.ikJoints = []
		self.ikControls = []
		self.fkControls = []
		self.fkControlGroups = []

		mainLayout = QtGui.QVBoxLayout()
		self.setLayout(mainLayout)

		i = 0
		self.jointText = []
		self.jointButtons = []
		for i in range(3):
			jointLayout = QtGui.QHBoxLayout()

			jointLabel = QtGui.QLabel(str(i))
			jointLayout.addWidget(jointLabel)

			jointText = QtGui.QLineEdit()
			jointLayout.addWidget(jointText)
			self.jointText.append(jointText)

			jointButton = QtGui.QPushButton('<<')
			jointButton.setObjectName(str(i))
			jointButton.clicked.connect(self.addSelectedToText)
			jointLayout.addWidget(jointButton)
			self.jointButtons.append(jointButton)

			mainLayout.addLayout(jointLayout)

		controlLayout = QtGui.QHBoxLayout()
		mainLayout.addLayout(controlLayout)
		controlLabel = QtGui.QLabel('Control Size')
		controlLayout.addWidget(controlLabel)
		self.controlSizeSlider = QtGui.QSlider()
		self.controlSizeSlider.setOrientation(QtCore.Qt.Horizontal)
		controlLayout.addWidget(self.controlSizeSlider)

		self.rigButton = QtGui.QPushButton('Rig')
		self.rigButton.clicked.connect(self.rigLimb)
		mainLayout.addWidget(self.rigButton)

		self.show()

	def addSelectedToText(self):
		buttonClicked = int(self.sender().objectName())
		objectSelected = mc.ls(sl=True)[0]
		self.jointText[buttonClicked].setText(objectSelected)

	def rigLimb(self):
		self.jointNames = [text.text() for text in self.jointText]
		
		ikJoint1 = mc.duplicate(self.jointNames[0], n=self.jointNames[0].replace('_JNT', '_IK_JNT'), renameChildren=True)[0]
		ikJoint2 = mc.rename(mc.listRelatives(ikJoint1, children=True)[0], self.jointNames[1].replace('_JNT', '_IK_JNT'))
		ikJoint3 = mc.rename(mc.listRelatives(ikJoint1, children=True)[0], self.jointNames[2].replace('_JNT', '_IK_JNT'))

		self.ikJoints = [ikJoint1, ikJoint2, ikJoint3]

		fkJoint1 = mc.duplicate(self.jointNames[0], n=self.jointNames[0].replace('_JNT', '_fk_JNT'), renameChildren=True)[0]
		fkJoint2 = mc.rename(mc.listRelatives(fkJoint1, children=True)[0], self.jointNames[1].replace('_JNT', '_fk_JNT'))
		fkJoint3 = mc.rename(mc.listRelatives(fkJoint1, children=True)[0], self.jointNames[2].replace('_JNT', '_fk_JNT'))

		self.fkJoints = [fkJoint1, fkJoint2, fkJoint3]

		self.createFKControl()

		self.createIKControl()

		mainGroup = mc.group(self.fkJoints[0], self.ikJoints[0], self.blendedJoints[0], n=joint1+"_GRP")


	def createFKControl(self):
		for joint in self.fkJoints:
			controlObject = self.generateFKControl()
			controlName = joint.rpartition("_")[0] + "_CTL"
			FKControlObject = mc.rename(controlObject, controlName)
			self.fkControls.append(FKControlObject)
			mc.setAttr(FKControlObject+'.translateX', mc.xform(joint, query=True, worldSpace=True, translation=True)[0])
			mc.setAttr(FKControlObject+'.translateY', mc.xform(joint, query=True, worldSpace=True, translation=True)[1])
			mc.setAttr(FKControlObject+'.translateZ', mc.xform(joint, query=True, worldSpace=True, translation=True)[2])
			FKControlObjectShape = mc.listRelatives(FKControlObject, children=True)
			groupName = mc.group(FKControlObject, n=joint.rpartition("_")[0] + "_GRP")   
			mc.parent(groupName, joint)
			mc.makeIdentity(groupName, apply=True, t=1, r=1, s=1, n=0)
			mc.parent(groupName, world=True)
			controlParent = mc.listRelatives(FKControlObject, parent=True)[0]
			mc.orientConstraint(FKControlObject, joint)
			self.fkControlGroups.append(groupName)
			#if controlParent != None:
		mc.parent(self.fkControlGroups[2], self.fkControls[1])
		mc.parent(self.fkControlGroups[1], self.fkControls[0])

	def generateFKControl(self):
		circle1 = mc.listRelatives(mc.circle( nr=(1, 0, 0), c=(0, 0, 0), r=1)[0], children=True)[0]
		mc.setAttr(circle1+".overrideEnabled", 1)
		mc.setAttr(circle1+".overrideColor", 13)
		circle2 = mc.listRelatives(mc.circle( nr=(0, 1, 0), c=(0, 0, 0), r=1)[0], children=True)[0]
		mc.setAttr(circle2+".overrideEnabled", 1)
		mc.setAttr(circle2+".overrideColor", 13)
		circle3 = mc.listRelatives(mc.circle( nr=(0, 0, 1), c=(0, 0, 0), r=1)[0], children=True)[0]
		mc.setAttr(circle3+".overrideEnabled", 1)
		mc.setAttr(circle3+".overrideColor", 13)
		groupName = mc.group(empty = True, n = "fkControl")
		mc.parent(circle1, groupName, relative=True, shape=True)
		mc.parent(circle2, groupName, relative=True, shape=True)
		mc.parent(circle3, groupName, relative=True, shape=True)
		return groupName

	def createIKControl(self):
		joint1Pos = mc.xform(self.ikJoints[0], q=True, ws=True, t=True)
		joint2Pos = mc.xform(self.ikJoints[1], q=True, ws=True, t=True)
		joint3Pos = mc.xform(self.ikJoints[2], q=True, ws=True, t=True)

		startV = OpenMaya.MVector(joint1Pos[0], joint1Pos[1], joint1Pos[2])
		midV = OpenMaya.MVector(joint2Pos[0], joint2Pos[1], joint2Pos[2])
		endV = OpenMaya.MVector(joint3Pos[0], joint3Pos[1], joint3Pos[2])

		startEnd = endV - startV
		startMid = midV - startV

		dotP = startMid * startEnd

		proj = float(dotP) / float(startEnd.length())

		startEndN = startEnd.normal()

		projV = startEndN * proj

		arrowV = startMid - projV

		arrowV*= 5
 
		finalV = arrowV + midV

		poleVectorControl = mc.spaceLocator(n=self.jointNames[1] + "_PV_CTL")[0]

		mc.xform(poleVectorControl , ws =1 , t= (finalV.x , finalV.y ,finalV.z))
		mc.makeIdentity(poleVectorControl, apply=True, t=1, r=1, s=1, n=0)

		ikHandle = mc.ikHandle(sj=self.ikJoints[0], ee=self.ikJoints[2], sol="ikRPsolver")[0]

		ikControlObject = mc.circle(nr=(0, 0, 1), c=(0,0,0), r=2, name=self.jointNames[2]+"_IK_CTL")[0]
		
		mc.setAttr(ikControlObject+'.translateX', mc.xform(self.ikJoints[2], query=True, worldSpace=True, translation=True)[0])
		mc.setAttr(ikControlObject+'.translateY', mc.xform(self.ikJoints[2], query=True, worldSpace=True, translation=True)[1])
		mc.setAttr(ikControlObject+'.translateZ', mc.xform(self.ikJoints[2], query=True, worldSpace=True, translation=True)[2])
		mc.makeIdentity(ikControlObject, apply=True, t=1, r=1, s=1, n=0)
		
		mc.parent(ikHandle, ikControlObject)

		poleVector = mc.poleVectorConstraint(poleVectorControl, ikHandle)

		mc.orientConstraint(ikControlObject, self.ikJoints[2], maintainOffset = True)

		self.ikControls.append(ikControlObject)
		self.ikControls.append(poleVectorControl)

	def blend(self):
		self.blendColor1 = mc.shadingNode("blendColors", asUtility=True, n=self.blendedJoints[0].rpartition("_")[0]+"_BLC")
		self.blendColor2 = mc.shadingNode("blendColors", asUtility=True, n=self.blendedJoints[1].rpartition("_")[0]+"_BLC")
		self.blendColor3 = mc.shadingNode("blendColors", asUtility=True, n=self.blendedJoints[2].rpartition("_")[0]+"_BLC")

		self.mainControl = mc.circle(nr=(0, 1, 0), c=(0,0,0), r=3)[0]
		pos = mc.xform(self.ikJoints[-1], query=True, ws=True, t=True)
		mc.xform(self.mainControl, t=[pos[0] + 3, pos[1] + 3, pos[2]])
		
		mc.addAttr(self.mainControl, ln="ik_fk_blend", attributeType="float", minValue=0.00, maxValue=1.00, keyable=True)

		mc.connectAttr(self.ikJoints[0]+".rotate", self.blendColor1+".color1")

		mc.connectAttr(self.fkJoints[0]+".rotate", self.blendColor1+".color2")

		mc.connectAttr(self.mainControl+".ik_fk_blend", self.blendColor1+".blender")

		mc.connectAttr(self.ikJoints[1]+".rotate", self.blendColor2+".color1")

		mc.connectAttr(self.fkJoints[1]+".rotate", self.blendColor2+".color2")

		mc.connectAttr(self.mainControl+".ik_fk_blend", self.blendColor2+".blender")

		mc.connectAttr(self.ikJoints[2]+".rotate", self.blendColor3+".color1")

		mc.connectAttr(self.fkJoints[2]+".rotate", self.blendColor3+".color2")

		mc.connectAttr(self.mainControl+".ik_fk_blend", self.blendColor3+".blender")

		mc.connectAttr(self.blendColor1+".output", self.blendedJoints[0]+".rotate")

		mc.connectAttr(self.blendColor2+".output", self.blendedJoints[1]+".rotate")

		mc.connectAttr(self.blendColor3+".output", self.blendedJoints[2]+".rotate")

		self.reverseNode1 = mc.shadingNode("reverse", asUtility=True, n=self.blendedJoints[0].rpartition("_")[0]+"_REV")
		
		mc.connectAttr(self.mainControl+".ik_fk_blend", self.reverseNode1+".input.inputX")

		for control in self.fkControls:
			mc.connectAttr(self.reverseNode1+".outputX", control+".visibility")

		for control in self.ikControls:
			mc.connectAttr(self.mainControl+".ik_fk_blend", control+".visibility")



tool = ikFkBlender()
