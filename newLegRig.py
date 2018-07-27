import maya.cmds as mc
import maya.OpenMaya as OpenMaya

def legRig(fkOnly = False, ikOnly = False):
    selection = mc.ls(sl=True)[0]
    legJoints = mc.listRelatives(selection, allDescendents=True)
    legJoints.append(selection)

    if fkOnly:
        fkLeg(legJoints)
        return

    elif ikOnly:
        ikLeg(legJoints)
        return

    else:
        fkDuplicateJoints = mc.duplicate(selection, renameChildren = True)
        fkJoints = []
        for joint in fkDuplicateJoints:
            fkJoint = mc.rename(joint, joint.replace('_JNT1', '_FK_JNT'))
            fkJoints.append(fkJoints)
        fkJoints = fkLeg(fkJoints)

        ikDuplicateJoints = mc.duplicate(selection, renameChildren = True)
        ikJoints = []
        for joint in ikDuplicateJoints:
            ikJoint = mc.rename(joint, joint.replace('_JNT1', '_IK_JNT'))
            ikJoints.append(ikJoints)
        ikJoints = ikLeg(ikJoints)

    mainControl = mc.circle(nr = (0, 1, 0), c = (0,0,0), r = 3, n = selection + "_CTL")[0]
    mc.addAttr(mainControl, ln = "ik_fk_blend", attributeType = "float", minValue = 0.00, maxValue = 1.00, keyable = True)
    reverseNode = mc.shadingNode("reverse", asUtility = True, n = selection.rpartition("_")[0]+"_REV")
    mc.connectAttr(mainControl+".ik_fk_blend", reverseNode+".input.inputX")
    # for joint in :
    #     blendColor = mc.shadingNode("blendColors", asUtility = True, n = joint.rpartition("_")[0]+"_BLC")

    #     mc.connectAttr(joint.replace('_JNT', '_IK_JNT')+'.rotate', blendColor + '.color1' )
    #     mc.connectAttr(joint.replace('_JNT', '_FK_JNT')+'.rotate', blendColor + '.color2' )
    #     mc.connectAttr(mainControl + '.ik_fk_blend', blendColor + '.blender')

    #     mc.connectAttr(blendColor + '.output', joint + '.rotate')

    for joint in self.fkJoints:
        mc.connectAttr(reverseNode + '.outputX', joint + '.visibility')

    mc.connectAttr(mainControl + '.ik_fk_blend', self.ikControlObject + '.visibility')
    mc.connectAttr(mainControl + '.ik_fk_blend', self.poleVectorControl + '.visibility')

    ikControlPos = mc.xform(self.ikControlObject, query = True, worldSpace = True, rp = True)
    self.mainControlPos = [pos + 1 for pos in ikControlPos]
    mc.xform(mainControl, worldSpace=True, translation=self.mainControlPos)





def fkLeg(legJoints=None):
    # FK leg rig stuff
    for joint in legJoints:
        if 'ankle' in joint.lower():
            print 'ankle joint found'
            ankleJoint = str(joint)
        elif 'toe' in joint.lower():
            print 'toe joint found'
            toeJoint = str(joint)
        elif 'ball' in joint.lower():
            print 'ball joint found'
            ballJoint = str(joint)
        elif 'knee' in joint.lower() or 'shin' in joint.lower():
            print 'knee joint found'
            shinJoint = str(joint)
        elif 'thigh' in joint.lower() or 'upleg' in joint.lower():
            print 'thigh joint found'
            upLegJoint = str(joint)
        else:
            pass

    parent = None
    for joint in [upLegJoint, shinJoint, ankleJoint, ballJoint]:
        if mc.listRelatives(joint, children=True):
            controlObject = mc.circle(nr=(0,1,0), c=(0, 0, 0), r=10, n=joint.replace('_JNT', '_CTL'))[0]
            controlGroup = mc.group(controlObject, n=joint.replace('_JNT', 'CTL_GRP'))
            mc.parent(controlGroup, joint)
            mc.makeIdentity(controlGroup, t=True, r=True, s=True)
            mc.parent(controlGroup, world=True)
            mc.parentConstraint(controlObject, joint, mo=True)
            if mc.listRelatives(joint, parent=True):
                jointParent = mc.listRelatives(joint, parent=True)[0]
                controlGroupParent = jointParent.replace('_JNT', '_CTL')
                if parent:
                    mc.parent(controlGroup, controlGroupParent)
                parent = controlGroupParent

def ikLeg(legJoints=None):

    for joint in legJoints:
        if 'ankle' in joint.lower():
            print 'ankle joint found'
            ankleJoint = str(joint)
        elif 'toe' in joint.lower():
            print 'toe joint found'
            toeJoint = str(joint)
        elif 'ball' in joint.lower():
            print 'ball joint found'
            ballJoint = str(joint)
        elif 'knee' in joint.lower() or 'shin' in joint.lower():
            print 'knee joint found'
            shinJoint = str(joint)
        elif 'thigh' in joint.lower() or 'upleg' in joint.lower():
            print 'thigh joint found'
            upLegJoint = str(joint)
        else:
            pass

    upLegJointPos = mc.xform(upLegJoint, q = True, ws = True, t = True)
    kneeJointPos = mc.xform(shinJoint, q = True, ws = True, t = True)
    ankleJointPos = mc.xform(ankleJoint, q = True, ws = True, t = True)

    startV = OpenMaya.MVector(upLegJointPos[0] ,upLegJointPos[1],upLegJointPos[2])
    midV = OpenMaya.MVector(kneeJointPos[0] ,kneeJointPos[1],kneeJointPos[2])
    endV = OpenMaya.MVector(ankleJointPos[0] ,ankleJointPos[1],ankleJointPos[2])

    for joint in legJoints:
        if 'heel' in joint.lower():
            heelJoint = joint
            legJoints.remove(joint)
            break

    startEnd = endV - startV
    startMid = midV - startV

    dotP = startMid * startEnd

    proj = float(dotP) / float(startEnd.length())

    startEndN = startEnd.normal()

    projV = startEndN * proj

    arrowV = startMid - projV

    arrowV*= 10

    finalV = arrowV + midV

    poleVectorControl = mc.spaceLocator(n = shinJoint.rpartition('_')[0] + "_PV_CTL", p = (finalV.x , finalV.y ,finalV.z))[0]
    mc.group(poleVectorControl, n = poleVectorControl.replace("_CTL", "_GRP"))

    mc.makeIdentity(poleVectorControl, apply=True, t=1, r=1, s=1, n=0)

    kneeIkHandle = mc.ikHandle(sj = upLegJoint, ee = ankleJoint, sol = "ikRPsolver")[0]

    ikControl = mc.circle(nr = (0, 0, 1), c = (0,0,0), r = 10, name = upLegJoint.rpartition('_')[0] + "_IK_CTL")[0]

    mc.xform(ikControl, worldSpace=True, translation=mc.xform(legJoints[2], query = True, worldSpace = True, translation = True))

    mc.makeIdentity(ikControl, apply=True, t=1, r=1, s=1, n=0)

    mc.parent(kneeIkHandle, ikControl)

    mc.poleVectorConstraint(poleVectorControl, kneeIkHandle)

    mc.xform(poleVectorControl, centerPivots=True)

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
    HeelOffsetGroup = mc.group(empty=True, n = 'HeelOffset_GRP')
    HeelGroup = mc.group(empty=True, n = 'Heel_GRP')
    mc.parent(HeelOffsetGroup, proxyHeel1Joint)
    mc.xform(HeelOffsetGroup, rotation = [0,0,0], translation = [0,0,0], a = True)
    mc.parent(HeelGroup, HeelOffsetGroup)
    mc.xform(HeelGroup, rotation = [0,0,0], translation = [0,0,0], a = True)
    mc.parent(HeelOffsetGroup, world=True)

    ToeOffsetGroup = mc.group(empty=True, n = 'ToeOffset_GRP')
    ToeGroup = mc.group(empty=True, n = 'Toe_GRP')
    mc.parent(ToeOffsetGroup, proxyToeJoint)
    mc.xform(ToeOffsetGroup, rotation = [0,0,0], translation = [0,0,0], a = True)
    mc.parent(ToeGroup, ToeOffsetGroup)
    mc.xform(ToeGroup, rotation = [0,0,0], translation = [0,0,0], a = True)
    mc.parent(ToeOffsetGroup, world=True)

    BallOffsetGroup = mc.group(empty=True, n = 'BallOffset_GRP')
    BallGroup = mc.group(empty=True, n = 'Ball_GRP')
    mc.parent(BallOffsetGroup, proxyBallJoint)
    mc.xform(BallOffsetGroup, rotation = [0,0,0], translation = [0,0,0], a = True)
    mc.parent(BallGroup, BallOffsetGroup)
    mc.xform(BallGroup, rotation = [0,0,0], translation = [0,0,0], a = True)
    mc.parent(BallOffsetGroup, world=True)

    mc.parent(ToeOffsetGroup, HeelGroup)
    mc.parent(BallOffsetGroup, ToeGroup)

    ToeTapOffsetGroup = mc.duplicate(BallOffsetGroup, n = 'ToeTapOffset_GRP', renameChildren = True)[0]
    ToeTapGroup = mc.rename(mc.listRelatives(ToeTapOffsetGroup, children=True)[0], 'ToeTap_GRP')

    mc.parent(ToeTapOffsetGroup, world=True)
    mc.xform(ToeTapOffsetGroup, rotation=[0,0,0], a=True)
    mc.parent(ToeTapOffsetGroup, HeelGroup)

    mc.delete(proxyHeel1Joint)
    mc.delete(proxyHeel2Joint)

    mc.parent(kneeIkHandle, BallGroup)
    mc.parent(ballIkHandle, BallGroup)
    mc.parent(toeIkHandle, ToeTapGroup)

    mc.addAttr(ikControl, longName='HeelRoll', attributeType='float', defaultValue=0, keyable=True)
    mc.connectAttr(ikControl + '.HeelRoll', HeelGroup + '.rotateX')
    mc.addAttr(ikControl, longName='BallRoll', attributeType='float', defaultValue=0, keyable=True)
    mc.connectAttr(ikControl + '.BallRoll', BallGroup + '.rotateX')
    mc.addAttr(ikControl, longName='ToeRoll', attributeType='float', defaultValue=0, keyable=True)
    mc.connectAttr(ikControl + '.ToeRoll', ToeGroup + '.rotateX')
    mc.addAttr(ikControl, longName='HeelPivot', attributeType='float', defaultValue=0, keyable=True)
    mc.connectAttr(ikControl + '.HeelPivot', HeelGroup + '.rotateY')
    mc.addAttr(ikControl, longName='BallPivot', attributeType='float', defaultValue=0, keyable=True)
    mc.connectAttr(ikControl + '.BallPivot', BallGroup + '.rotateY')
    mc.addAttr(ikControl, longName='ToePivot', attributeType='float', defaultValue=0, keyable=True)
    mc.connectAttr(ikControl + '.ToePivot', ToeGroup + '.rotateY' )
    mc.addAttr(ikControl, longName='ToeTap', attributeType='float', defaultValue=0, keyable=True)
    mc.connectAttr(ikControl + '.ToeTap', ToeTapGroup + '.rotateX')

    mc.connectAttr(ikControl + '.BallPivot', ToeTapGroup + '.rotateY')

    mc.parent(HeelOffsetGroup, ikControl)

    # return

legRig(fkOnly=True)

#legRig(ikOnly=True)

