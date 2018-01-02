def follicle(*args, **kwargs):
	sels = list(args)
	if not args: sels = cmds.ls(sl=1)
	if len(sels) == 1:
		sels = sels[0]
		name = kwargs.get('name', sels.split('.')[0:1][0])
		shape = cmds.listRelatives(sels.split('.')[0:1][0], s=1)[0]
	elif len(sels) == 2:
		name = kwargs.get('name', sels[0])
		shape = cmds.listRelatives(sels[-1], s=1)[0]
		sels = sels[0]
	follicleShape = cmds.createNode('follicle')
	follicleShapeParents = cmds.listRelatives(follicleShape, p=1)
	follicle = cmds.rename(follicleShapeParents[0], name+'_Follicle')
	follicleShape = cmds.listRelatives(follicle, s=1)[0]
	cmds.connectAttr(follicleShape+'.outTranslate', follicle+'.translate', f=1)
	cmds.connectAttr(follicleShape+'.outRotate', follicle+'.rotate', f=1)
	ws = cmds.xform(sels, q=1, t=1, ws=1)
	#if shape is a nurbs:
	if cmds.nodeType(shape) == 'nurbsSurface':
		cpos = cmds.createNode('closestPointOnSurface')
		cmds.setAttr (cpos + ".inPositionX", ws[0])
		cmds.setAttr (cpos + ".inPositionY", ws[1])
		cmds.setAttr (cpos + ".inPositionZ", ws[2])
		cmds.connectAttr(shape + ".worldSpace", cpos + ".inputSurface", f=1)
		# get the result U and V value
		Ucpos = cmds.getAttr(cpos + '.parameterU')
		Utotal = cmds.getAttr(shape+'.minMaxRangeU')[0]
		U = abs((Ucpos-Utotal[0])/(Utotal[1]-Utotal[0]))
		Vcpos = cmds.getAttr(cpos + '.parameterV')
		Vtotal = cmds.getAttr(shape+'.minMaxRangeV')[0]
		V = abs((Vcpos-Vtotal[0])/(Vtotal[1]-Vtotal[0]))
		# plug the U and V value into follicleShape's U and V attrs
		cmds.setAttr(follicleShape + ".parameterU", U)
		cmds.setAttr(follicleShape + ".parameterV", V)
		# connect the meshShape's worldMatrix and worldMesh to the follicleShape
		cmds.connectAttr(shape + ".worldMatrix", follicleShape + ".inputWorldMatrix", f=1)
		cmds.connectAttr(shape + ".worldSpace", follicleShape + ".inputSurface", f=1)
		cmds.delete(cpos)
	#if shape is a poly:
	if cmds.nodeType(shape) == 'mesh':
		cpom = cmds.createNode('closestPointOnMesh')
		cmds.setAttr (cpom + ".inPositionX", ws[0])
		cmds.setAttr (cpom + ".inPositionY", ws[1])
		cmds.setAttr (cpom + ".inPositionZ", ws[2])
		cmds.connectAttr(shape + ".outMesh", cpom + ".inMesh", f=1)
		# get the result U and V value
		U = cmds.getAttr(cpom + '.parameterU')
		V = cmds.getAttr(cpom + '.parameterV')
		# plug the U and V value into follicleShape's U and V attrs
		cmds.setAttr(follicleShape + ".parameterU", U)
		cmds.setAttr(follicleShape + ".parameterV", V)
		# connect the meshShape's worldMatrix and worldMesh to the follicleShape
		cmds.connectAttr(shape + ".worldMatrix[0]", follicleShape + ".inputWorldMatrix", f=1)
		cmds.connectAttr(shape + ".worldMesh[0]", follicleShape + ".inputMesh", f=1)
	return follicle

follicle()