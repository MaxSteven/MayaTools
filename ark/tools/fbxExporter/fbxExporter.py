import os
import arkInit
arkInit.init()

import cOS
import traceback
import subprocess

import translators
translator = translators.getCurrent()
import baseWidget

import settingsManager
globalSettings = settingsManager.globalSettings()

class FbxExporter(baseWidget.BaseWidget):
	defaultOptions = {
			'title': 'FBX Exporter',
			'width': 600,
			'height': 200,

		'knobs': [
			{
				'name': 'Animation Directory',
				'dataType': 'Directory',
				'extension': '*.mb'
			},
			{
				'name': 'Animation Files',
				'dataType': 'SearchList',
				'selectionMode': 'multi',
			},
			{
				'name': 'Crowd',
				'dataType': 'checkbox',
				'value': True
			},
			{
				'name': 'Export Directory',
				'dataType': 'Directory'
			},
			{
				'name': 'Export Animation',
				'dataType': 'PythonButton',
				'callback': 'exportFBXAnimation'
			}
		]
	}

	def init(self):
		pass

	def postShow(self):
		self.getKnob('Animation Directory').on('changed', self.populateAnimFiles)

	def populateAnimFiles(self, *args):
		self.animDir = self.getKnob('Animation Directory').getValue()
		animFiles = cOS.getFiles(self.animDir, fileIncludes=['.mb'], filesOnly=True, fullPath=False, depth=0)
		self.getKnob('Animation Files').addItems(animFiles)

	def exportFBXAnimation(self):
		exportDir = self.getKnob('Export Directory').getValue()
		exportDir = cOS.normalizeDir(exportDir)
		crowdExport = self.getKnob('Crowd').getValue()
		animFiles = self.getKnob('Animation Files').getValue()
		print animFiles
		for animFile in animFiles:
			args = [globalSettings.MAYA_BATCH_EXE]
			args.extend(['-file', self.animDir + animFile])
			args.extend(['-command', 'python ("import fbxExporter;fbxExporter.prepAndExportFBX(crowdExport = ' + str(crowdExport) + ', exportDir = \'' + exportDir + '\');")'])
			# args = [mayabatchExe, fileArg, command]
			# print args
			process = cOS.startSubprocess(args)
			out, err = cOS.waitOnProcess(process)
			if 'Error' not in out and not err:
				print 'Export Success!'
			else:
				print err
				pass


def gui(self):
	return FbxExporter()

def launch(docked=False):
	translator.launch(FbxExporter, docked=docked)

def prepAndExportFBX(crowdExport = True, exportDir = True):
	import maya.cmds as mc
	import pymel.core as pymel
	import os
	import maya.mel as mel

	# Change this to desired frame range before you run it
	startframe = int(mc.playbackOptions(query=True, minTime=True))
	endframe = int(mc.playbackOptions(query=True, maxTime=True))

	frameRange = (startframe, endframe)

	namespaces = mc.namespaceInfo(listOnlyNamespaces=True)
	if crowdExport:
		for namespace in namespaces:
			if mc.objExists(namespace + ':body_lowPoly'):
				selection = mc.ls(namespace + ':body_lowPoly')[0]
				break
	else:
		for namespace in namespaces:
			if mc.objExists(namespace + ':body'):
				selection = mc.ls(namespace + ':body')[0]
				break

	isReference=True
	while isReference==True:
		referenceNode = mc.referenceQuery(selection, rfn = True, tr=True)
		referenceFile = mc.referenceQuery(referenceNode, filename=True)
		namespace = mc.referenceQuery(selection, namespace=True).replace(':', '')
		mc.file(referenceFile, importReference = True)
		isReference = mc.referenceQuery(selection, isNodeReferenced = True)

	geoGroup = mc.listRelatives(selection, parent=True)[0]
	geoObjects = [obj for obj in mc.listRelatives(geoGroup, allDescendents = True) if mc.objectType(obj)== 'mesh']
	geoTransforms = [mc.listRelatives(obj, parent=True)[0] for obj in geoObjects]
	bindJoints = []
	for obj in geoTransforms:
		joints = mc.skinCluster(obj, query=True, weightedInfluence = True)
		bindJoints.extend(joints)

	print namespace
	mc.select(namespace + ':Human_rig', hi = True)
	allObjects = mc.ls(sl=True)
	newAllObjects = []
	for obj in allObjects:
		try:
			newObj = mc.rename(obj, obj.replace(namespace + ':', ''))
			newAllObjects.append(newObj)
		except:
			pass

	geo = selection.replace(namespace + ':', '')
	mc.select('GroundBindRoot_JNT', hi = True)
	allBindNodes = mc.ls(sl=True)
	bakedNodes = []
	for obj in allBindNodes:
		if 'Constraint' not in mc.objectType(obj):
			print obj
			bakedNodes.append(obj)

	mc.bakeResults(bakedNodes, simulation=True, t = frameRange,
				sampleBy = 1, disableImplicitControl=True,
				preserveOutsideKeys=True, sparseAnimCurveBake=False,
				removeBakedAttributeFromLayer=False, removeBakedAnimFromLayer=False,
				bakeOnOverrideLayer=False, minimizeRotation=True, controlPoints=False,
				shape=True
				)
	scaleConnectedObjects = ['R_ArmRig_JNT', 'R_ForearmRig_JNT',
							 'L_ArmRig_JNT', 'L_ForearmRig_JNT',
							 'L_upLegRig_JNT', 'L_ShinRig_JNT', 'L_AnkleRig_JNT', 'L_FootBaseRig_JNT', 'L_BallRig_JNT',
							 'R_upLegRig_JNT', 'R_ShinRig_JNT', 'R_AnkleRig_JNT', 'R_FootBaseRig_JNT', 'R_BallRig_JNT']
	for obj in scaleConnectedObjects:
		try:
			mc.disconnectAttr(obj + '.scale', obj.replace('Rig', 'Bind') + '.scale')
		except:
			print obj
			pass

	mc.delete('World_CTL')

	mc.delete('DO_NOT_TOUCH')

	for obj in mc.listRelatives('Deformation', children=True):
		if obj != 'GroundBindRoot_JNT':
			mc.delete(obj)

	newBindJoints = []

	geoObjects = [obj for obj in mc.listRelatives('GEO', allDescendents = True) if mc.objectType(obj)== 'mesh']
	geoTransforms = [mc.listRelatives(obj, parent=True)[0] for obj in geoObjects]
	for obj in geoTransforms:
		joints = mc.skinCluster(obj, query=True, weightedInfluence = True)
		newBindJoints.extend(joints)

	nonBindNodes = []
	for obj in allBindNodes:
		if mc.objExists(obj) == True and obj not in newBindJoints:
			if not mc.listRelatives(obj, children = True):
				mc.delete(obj)

			else:
				nonBindNodes.append(obj)

	nonBindJointExceptions = ['R_ObjectHoldBind_JNT', 'R_ObjectHoldEndBind_JNT', 'L_ObjectHoldBind_JNT', 'L_ObjectHoldEndBind_JNT']

	# Deleting non-bind nodes
	for obj in nonBindNodes:
		if not mc.listRelatives(obj, children = True) and obj not in nonBindJointExceptions:
			print obj
			mc.delete(obj)

	mc.setAttr('Deformation.scaleX', 0.01)
	mc.setAttr('Deformation.scaleY', 0.01)
	mc.setAttr('Deformation.scaleZ', 0.01)

	# keying blendshapes
	blendshapeNode = namespace + ':all_lowPoly_BSH'
	for attr in mc.listAttr(blendshapeNode, keyable=True):
		try:
			mc.setKeyframe(blendshapeNode + '.' + attr)
		except:
			pass

	# Only for crowd export
	if crowdExport:
		mc.delete('body')
		mc.delete('nails')

	mc.select('Human_rig')
	currentFilename = mc.file(query=True, sn=True, shn=True)
	fbxFilename = currentFilename.rpartition('_')[0] + '_' + str(startframe) + '-' + str(endframe) + '.fbx'

	mel.eval('FBXExportCameras -v false;')
	mel.eval('FBXExportLights -v false;')
	mel.eval('FBXExportInAscii -v false;')
	mel.eval('FBXExportInAscii -q;')
	exportDir = cOS.normalizeDir(exportDir)
	fbxPath = exportDir + fbxFilename
	mel.eval('FBXExport -f "' + fbxPath + '" -s;')
	print 'Saving FBX:', fbxPath

if __name__=='__main__':
	launch()


