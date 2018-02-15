import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import maya.OpenMayaUI as OpenMayaUI

view = OpenMayaUI.M3dView.active3dView()
cam = OpenMaya.MDagPath()
view.getCamera(cam)
camPath = cam.fullPathName()
print camPath