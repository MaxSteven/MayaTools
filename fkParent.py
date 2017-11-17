import maya.cmds as cmds

def FKParent():
    selectedObjects = cmds.ls(selection =  True)
    if len(selectedObjects) != 2:
        print "Wrong number of objects selected"
        return
    control = selectedObjects[0]
    joint = selectedObjects[1]
    cmds.parent(control, joint, relative = True)
    cmds.makeIdentity(control)
    cmds.parent(control, world = True)
    shapeOfSelectedObject = cmds.listRelatives(control, shapes = True)
    cmds.parent(shapeOfSelectedObject, control, relative = True, shape = True)
    print "Success"

FKParent()