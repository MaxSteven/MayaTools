# python.executeFile("C:/ie/ark/programs/max/python/arkMax.py")

import MaxPlus
import arkInit
arkInit.init()
import settingsManager
globalSettings = settingsManager.globalSettings()

import translators
translator = translators.getCurrent()

# from translators import QtGui
# from shiboken import wrapInstance

def getSceneNodes():
	# MaxPlus.Core.GetRootNode().Children doesn't return a list
	return list(MaxPlus.Core.GetRootNode().Children)
	# return [node.GetBaseObject() for node in MaxPlus.Core.GetRootNode().Children]

def getSelectedNodes():
	# MaxPlus.SelectionManager.Nodes doesn't return a list
	return list(MaxPlus.SelectionManager.Nodes)

# fix: DOES NOT WORK
SuperIdTypes = {
	MaxPlus.SuperClassIds.Osm : MaxPlus.Modifier,
	MaxPlus.SuperClassIds.Wsm : MaxPlus.Modifier,
	MaxPlus.SuperClassIds.Helper : MaxPlus.HelperObject,
	MaxPlus.SuperClassIds.GeomObject : MaxPlus.GeomObject,
	MaxPlus.SuperClassIds.Light : MaxPlus.LightObject,
	MaxPlus.SuperClassIds.Texmap : MaxPlus.Texmap,
	MaxPlus.SuperClassIds.Material : MaxPlus.Mtl,
	MaxPlus.SuperClassIds.Atmospheric : MaxPlus.Atmospheric,
	MaxPlus.SuperClassIds.SoundObj : MaxPlus.SoundObj,
	MaxPlus.SuperClassIds.Renderer : MaxPlus.Renderer,
	MaxPlus.SuperClassIds.Camera : MaxPlus.CameraObject
}

def descendants(node):
	for c in node.Children:
		yield c
		for d in descendants(c):
			yield d

def allNodes():
	return descendants(MaxPlus.Core.GetRootNode())

def castObject(o):
	if not o: return None
	sid = o.GetSuperClassID()
	# print "SID: " + str(sid)
	if not sid in SuperIdTypes: return None
	return SuperIdTypes[sid]._CastFrom(o)

def getSceneNodesByType(nodeType):
	nodes = []
	for n in getSceneNodes():
		baseObject = n.GetBaseObject()
		cast = castObject(baseObject)
		if cast:
			print "Type: " + str(type(cast))
			if nodeType in str(type(cast)).lower():
				nodes.append(n)
	return nodes

def getNodeNames(nodes):
	if not hasattr(nodes, '__iter__'):
		nodes = [nodes]
	return [node.Name for node in nodes]

def addModifier(nodes):
	for node in nodes:
		mod = MaxPlus.Factory.CreateObjectModifier(MaxPlus.ClassIds.Noisemodifier)

		print '\nNoise parameters:'
		for param in  mod.ParameterBlock:
			print param.Name

		mod.ParameterBlock.seed.Value = 86753
		mod.ParameterBlock.strength.Value = MaxPlus.Point3(100, 100, 100)
		node.AddModifier(mod)

# # File Info
#####################################

def getFileName():
	return MaxPlus.FileManager.GetFileName()

def saveFile():
	return MaxPlus.FileManager.Save()

# # Event Listening
#####################################

def addCallbacks(action, eventName, callback):
	if action == 'load':
		MaxPlus.Core.EvalMAXScript("callbacks.addScript #filePostOpen self.fireEvent( " + eventName + ")")
		# self.onAppEvent(eventName, callback)
	elif action == 'save':
		MaxPlus.Core.EvalMAXScript("callbacks.addScript #filePreSave self.fireEvent( " + eventName + ")")
		# self.onAppEvent(eventName, callback)

# # Rendering
#####################################

def getRenderProperties():
	return {
		'width': MaxPlus.RenderSettings.GetWidth(),
		'height': MaxPlus.RenderSettings.GetHeight(),
		'startFrame': MaxPlus.RenderSettings.GetStart() / 160,
		'endFrame': MaxPlus.RenderSettings.GetEnd() / 160,
		'shadingLevel': translator.executeNativeCommand('print renderers.current.gsSamplingLevel'),
		# fix: should remove when we get Coren
		'shading_level': translator.executeNativeCommand('print renderers.current.gsSamplingLevel'),
		'program': 'max',
		'jobType': 'Max_Maxwell'
	}

def getOutputFilename(outputPath, jobData):
	outputFile = outputPath + ('/renders/v%03d/' % jobData['version']) + \
		jobData['name'] + '_' + jobData['cameraName'] + '.exr'
	return outputFile[:2] + outputFile[2:].replace(':','_')

def setOutputFilename(outputFile, jobData):
	# Fix:  _<Camera>
	MaxPlus.RenderSettings.SetOutputFilename(jobData['name'] + '_<Camera>')

# # Pre's
######################################

def preRender():
	pass

def preSubmit(jobData):
	saveFile()

# # PySide
######################################

def getQTApp():
	pass


def main():
	print '\nScene nodes:'
	# print getNodeNames(getSceneNodes())

	print '\nSelected nodes:'
	# print getNodeNames(getSelectedNodes())

	print '\nCameras:'
	# print getNodeNames(getSceneNodesByType('camera'))
	print getSceneNodesByType('geo')

	print '\nFilename:'
	print getFileName()

	print '\nSave Success:'
	print saveFile()

	print "\nRender Properties: "
	print getRenderProperties()
	# print 'started'
	# MaxPlus.Core.EvalMAXScript('sleep 2;print BOOBS')
	# print 'finished'


	# notes


	# ieMax
	# fn ieMaxExecuteCommand(command)
	# (
	# 	f = openFile (MAX_TOOLS_ROOT + "temp/maxResult.txt", "w")
	# 	result = execute command
	# 	format result to:f
	# 	close f
	# )
	result = translator.executeNativeCommand('print "boobs"')
	print result


	# print '\n'.join(dir(MaxPlus.RenderSettings.GetProduction()))
	# print 'result:', result
	# print result.GetStr(True)

	selectedNodes = getSelectedNodes()
	addModifier(selectedNodes)

if __name__ == '__main__':
	main()