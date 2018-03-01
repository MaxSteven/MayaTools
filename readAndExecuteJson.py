import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import maya.OpenMayaUI as OpenMayaUI

view = OpenMayaUI.M3dView.active3dView()
cam = OpenMaya.MDagPath()
view.getCamera(cam)
camName = cam.partialPathName()
cam = mc.listRelatives(camName, parent=True)[0]

filepath = "C:\\trash\\test.json"
f = open(filepath, 'r')

viewList = json.load(viewList, f, indent = 4)
f.close()

for view in viewList:
	mc.xform(cam, worldSpace = True, translation = view['viewPosition'])
	mc.xform(cam, worldSpace = True, rotation = view['viewOrientation'])

	for test in view['data']:
		
	