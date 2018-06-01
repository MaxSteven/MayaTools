import maya.cmds as mc

selection = mc.ls(sl=True)
parentConstraints = []
scaleConstraints = []
for obj in selection:
	if 'Bind' in obj and 'End' not in obj:
		try:
			parentConstraints.append(mc.parentConstraint(obj.replace('Bind', 'Rig'), obj, mo=True)[0])
			scaleConstraints.append(mc.scaleConstraint(obj.replace('Bind', 'Rig'), obj, mo=True)[0])

		except:
			print obj, 'No Constraint'

mc.select(parentConstraints)
mc.select(scaleConstraints, add=True)



