import maya.cmds as mc
import json

viewJson = {
		'name':'',
		'viewPostition': [],
		'viewOrientation': [],
		'data':[]
}
objJson = {
	'obj': '',
	'attr': '',
	'value': ''
}

viewList = []
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import maya.OpenMayaUI as OpenMayaUI

view = OpenMayaUI.M3dView.active3dView()
cam = OpenMaya.MDagPath()
view.getCamera(cam)
camName = cam.partialPathName()
cam = mc.listRelatives(camName, parent=True)[0]

cameraPos = mc.xform(cam, query = True, translation = True, worldSpace = True)
cameraOrient = mc.xform(cam, query = True, rotation = True, worldSpace = True)

viewJson['viewPosition'] = cameraPos
viewJson['viewOrientation'] = cameraOrient

obj = mc.ls(sl=True)[0]
attr = 'translateX'
value = 0

objJson['obj'] = obj
objJson['attr'] = attr
objJson['value'] = value

viewJson['data'].append(objJson)

viewList.append(viewJson)

filepath = "C:\\trash\\test.json"
f = open(filepath, 'w')

json.dump(viewList, f, indent = 4)
f.close()