# -- WRITING A JSON DICT -- 

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


# -- READING FROM A JSON DICT --
import maya.cmds as mc
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
	previousValues = []
	for test in view['data']:
		obj = test['obj']
		attr = test['attr']
		val = mc.getAttr(obj + '.' + attr)
		valDict = {
					'obj': obj,
					'attr':attr,
					'val':val
				}
		previousValues.append(valDict)

	for test in view['data']:
		obj = test['obj']
		attr = test['attr']
		val = test['val']
		mc.setAttr(obj + '.' + attr, val)
		print 'screencap captured!'

	for val in previousValues:
		obj = val['obj']
		attr = val['attr']
		val = val['val']
		mc.setAttr(obj + '.' + attr, val)
		print 'value restored'
