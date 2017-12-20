import  maya.cmds as mc

objGrps = mc.group(empty=True)
ctlGrps = mc.group(empty=True)
for obj in mc.ls(sl=True):
    objGrp = mc.group(n = obj.rpartition('_')[0] + '_GRP', empty=True)
    mc.parent(objGrp, obj)
    mc.makeIdentity(objGrp, t=True, s=True, r=True)
    mc.parent(objGrp, world = True)
    mc.parent(obj, objGrp)
    mc.parent(objGrp, objGrps)
    position = mc.xform(obj, query=True, worldSpace=True, translation=True)
    ctl = mc.sphere(n = obj.replace('_JNT', '_CTL'), radius = .1)[0]
    mc.xform(ctl, worldSpace=True, translation=position)
    mc.makeIdentity(ctl, apply=True, t = 1, r = 1, s = 1)
    ctlGrp = mc.group(ctl, n = ctl.replace('_CTL', 'ctl_GRP'))
    mc.parent(ctlGrp, obj)
    mc.makeIdentity(ctlGrp,)
    mc.parent(ctlGrp, world=True)
    mc.parent(ctlGrp, ctlGrps)
    mc.connectAttr(ctl + '.translate', obj + '.translate')

