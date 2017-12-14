import  maya.cmds as mc

# only supports verticies
selection = mc.filterExpand(expand=True, selectionMask = 31)
positionX = 0
positionY = 0
positionZ = 0
for obj in selection:
    position = mc.xform(obj, q=True, worldSpace=True, translation=True)
    positionX += position[0]
    positionY += position[1]
    positionZ += position[2]

averageX = positionX/len(selection)
averageY = positionY/len(selection)
averageZ = positionZ/len(selection)

loc = mc.spaceLocator(p = (averageX, averageY, averageZ))
mc.xform(loc, cp=True)
