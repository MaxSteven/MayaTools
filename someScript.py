import maya.cmds as mc

selection = mc.ls(sl=True)
for obj in selection:
    child = mc.listRelatives(obj, children=True)[0]
    grandparent = mc.listRelatives(obj, parent=True)[0]
    mc.parent(child, grandparent)
    mc.group(grandparent, n = grandparent.replace('Offset_GRP', 'Constraint_GRP'))
    mc.delete(obj)
