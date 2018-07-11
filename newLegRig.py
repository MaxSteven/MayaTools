import maya.cmds as mc

def legRig(fkOnly = False, ikOnly = False):
	selection = mc.ls(sl=True)[0]
	# legJoints = mc.ls(mc.listRelatives(selection, children=True))

	if fkOnly:
		fkLeg(selection)
		return

	elif ikOnly:
		ikLeg(selection)
		return

	else:
		fkRootJoint = mc.duplicate(selection, renameChildren = True)[0]
		for joint in mc.listRelatives()





def fkLeg(legJointChain=None, fkControlObjects=None):
	# FK leg rig stuff

def ikLeg(legJointChain=None, ikControlObjects=None):
	# IK leg Stuff





