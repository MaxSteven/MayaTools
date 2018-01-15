import maya.cmds as mc

selection = mc.ls(sl=True)
joint = selection[1]
control = selection[0]

control = mc.rename(control, joint.replace('_JNT', '_CTL'))
controlGroup = mc.group(control, n = control.replace('_CTL', '_GRP'))
mc.parent(controlGroup, joint)
mc.makeIdentity(controlGroup, t=1, r=1, s=1, apply=True)
mc.parent(controlGroup, world=True)
mc.parentConstraint(control, joint, mo=True)