import maya.cmds as mc

srf = 'M_neckRibbon_SRF'

increment = 0
selection = mc.ls(sl=True)
lenSelection = len(selection)
division = 1 / lenSelection
for jnt in selection:
	i = 0

	p = mc.xform(jnt, q = True, t = True, ws = True)
	cPos = mc.createNode('closestPointOnSurface')

	mc.setAttr(cPos + '.inPositionX', p[0])
	mc.setAttr(cPos + '.inPositionY', p[1])
	mc.setAttr(cPos + '.inPositionZ', p[2])
	srfShape = mc.listRelatives(srf, children=True)[0]
	mc.connectAttr(srfShape + '.worldSpace', cPos + '.inputSurface')

	u = mc.getAttr(cPos + '.parameterU')
	v = mc.getAttr(cPos + '.parameterV')

	mc.delete(cPos)

#	fol = mc.rename(fol, 'M_neckIKRibbon' + str(increment + 1) + '_FOLShape')
	fol = mc.createNode('follicle')

	folParent = mc.listRelatives(fol, parent=True)[0]
	folParent = mc.rename(folParent, 'M_neckIKRibbon' + str(i + 1) + '_FOL')
	fol = mc.listRelatives(folParent, children=True)[0]

	mc.connectAttr(srf + '.worldMatrix[0]', fol + '.inputWorldMatrix')
	mc.connectAttr(srf + '.local', fol + '.inputSurface')

	mc.connectAttr(fol + '.outTranslate', folParent + '.translate')
	mc.connectAttr(fol + '.outRotate', folParent + '.rotate')

	mc.setAttr(fol + ".parameterV", v)
	mc.setAttr(fol + ".parameterU", u)

	i += 1
	increment += division

	mc.parent(jnt, folParent)