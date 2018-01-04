import maya.cmds as mc

selection = mc.ls(sl=True)
newObject = selection[0]
newSelectionShape = mc.listRelatives(newObject, children=True)[0]
oldObject = selection[1]
oldObjectChildren = mc.listRelatives(oldObject, children=True)
for shape in oldObjectChildren:
    if 'Orig' in shape:
        origShape = shape
        break

mc.setAttr(origShape + '.intermediateObject', 0)

mc.transferAttributes(newSelectionShape, origShape, transferPositions=True, transferNormals=True, transferUVs=False, transferColors=False, sampleSpace=4, searchMethod=3, flipUVs=0, colorBorders=1);

mc.delete(origShape, constructionHistory=True)

mc.setAttr(origShape + '.intermediateObject', 1)