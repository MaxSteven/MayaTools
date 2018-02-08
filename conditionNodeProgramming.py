import maya.cmds as mc

selection = mc.ls(sl=True)
for obj in selection:
    joint = obj.replace('_CTL', '_JNT')
    # print 'disconnecting ', obj, joint
    # try:
    #     mc.disconnectAttr(obj + '.translate', joint + '.translate')
    # except:
    #     print "couldn't disconnect", obj, joint
    #     pass
    objParent = mc.listRelatives(obj, parent=True)
    objGrandParent = mc.listRelatives(objParent, parent=True)

    mc.parent(objParent, joint)
    mc.makeIdentity(objParent, t=True, r=True, s=True)
    mc.parent(objParent, objGrandParent)
    print 'connecting ' obj, joint
    mc.connectAttr(obj + '.translate', joint + '.translate')
    mc.connectAttr(obj + '.rotate', joint + '.rotate')
