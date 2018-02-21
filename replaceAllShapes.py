import maya.cmds as mc



selection = mc.ls(sl=True)
for ob in selection:
	newObject = ob
	newSelectionShape = mc.listRelatives(newObject, children=True)[0]
	oldObject = ob.replace('_Group64227', '')
	if not mc.objExists(oldObject):
		continue

	oldObjectChildren = mc.listRelatives(oldObject, children=True)
	origShape = None
	for shape in oldObjectChildren:
	    if 'Orig' in shape:
	        origShape = shape
	        break

	if origShape:
		mc.setAttr(origShape + '.intermediateObject', 0)

		mc.transferAttributes(newSelectionShape, origShape, transferPositions=True, transferNormals=True, transferUVs=False, transferColors=False, sampleSpace=4, searchMethod=3, flipUVs=0, colorBorders=1)

		mc.delete(origShape, constructionHistory=True)

		mc.setAttr(origShape + '.intermediateObject', 1)

	elif len(oldObjectChildren) == 1:
		origShape = oldObjectChildren[0]

		mc.transferAttributes(newSelectionShape, origShape, transferPositions=True, transferNormals=True, transferUVs=False, transferColors=False, sampleSpace=4, searchMethod=3, flipUVs=0, colorBorders=1)

		mc.delete(origShape, constructionHistory=True)
