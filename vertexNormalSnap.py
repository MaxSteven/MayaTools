import maya.cmds as mc
import maya.mel as mel

vertex = mc.filterExpand(expand=True, selectionMask=31)[0]
print vertex
joint = mc.ls(sl=True)[1]


mel.eval('doCreatePointOnPolyConstraintArgList 2 {   "0" ,"0" ,"0" ,"1" ,"" ,"1" ,"0" ,"0" ,"0" ,"0" };')
constraint= mc.listRelatives(joint, children=True)[0]
mc.delete(constraint)
mc.makeIdentity(joint, t=True, r=True, s=True, n=False)