# Initialization
import sys
import os
os.environ['ARK_CURRENT_APP'] = 'houdini'

sys.path.append('C:/Python27/Lib/site-packages/')

import arkInit
arkInit.init()

import settingsManager
globalSettings = settingsManager.globalSettings()

sys.path.append(globalSettings.HOUDINI_TOOLS_ROOT)
# End initialization

# Standard modules
from expects import *

# Our modules
import arkInit
arkInit.init()

import tryout
import cOS
import translators
translator = translators.getCurrent()

class test(tryout.TestSuite):
	title = 'test/test_houdini.py'
	timeout = 10

	# Setup
	##################################################
	def setUpClass(self):
		self.testRoot = cOS.getDirName(__file__)
		self.scriptPath = self.testRoot + 'test_v001.hip'
		self.scriptPathAlt = self.testRoot + 'test_v002.hip'
		self.assetsRoot = cOS.upADir(self.testRoot) + 'test_assets/'

	# Basics
	##################################################
	def basics(self):
		self.assertEqual(translator.program, 'houdini')
		self.assertEqual(translator.fileExtension, 'hip')

	def getSceneData(self):
		translator.setSceneData('things','awesome')
		data = translator.getSceneData('things')

		self.assertEqual(data, 'awesome')

	def setSceneData(self):
		translator.setSceneData('cool','yes')

		self.assertEqual(translator.program, 'houdini')
		self.assertEqual(translator.fileExtension, 'hip')

	def getFilename(self):
		try:
			translator.closeFile(force=True)
		except Exception as err:
			print 'closeFile in getFilename exception: ' + err.message
		filename = translator.getFilename()
		self.assertTrue('untitled.hip' in filename)

	def openFile(self):
		translator.openFile(self.scriptPath, force=True)
		filename = translator.getFilename()
		self.assertEqual(filename, self.scriptPath)
		allNodes = translator.getAllNodes()
		self.assertTrue(len(allNodes) > 3)

	def saveFile(self):
		translator.openFile(self.scriptPathAlt, force=True)
		newFilename = self.testRoot + 'test_v003.hip'
		translator.saveFile(newFilename)
		filename = translator.getFilename()

		self.assertEqual(filename, newFilename)
		self.assertTrue(os.path.isfile(newFilename))
		os.remove(newFilename)

	def getAllNodes(self):
		translator.openFile(self.scriptPath, force=True)
		nodes = translator.getAllNodes()

		print 'Nodes:'
		for node in nodes:
			print node.name()

		self.assertTrue(nodes[0].name() != '')
		allNodes = translator.getAllNodes()
		self.assertTrue(len(allNodes) > 3)

	def getNodesByName(self):
		translator.openFile(self.scriptPath, force=True)
		node = translator.getNodeByName('img')
		self.assertTrue('img' in node.name().lower())

	def getNodesByType(self):
		translator.openFile(self.scriptPath, force=True)
		nodes = translator.getNodesByType('img')

		print 'Img nodes:'
		for node in nodes:
			print node.name()

		self.assertTrue('img' in nodes[0].name().lower())

	def selectNodes(self):
		translator.openFile(self.scriptPath, force=True)
		node = translator.getNodeByName('obj')
		translator.selectNode(node)
		nodes = translator.getSelectedNodes()

		print 'Selected nodes:'
		for item in nodes:
			print item.name()

		self.assertEqual(len(nodes), 1)
		self.assertTrue('obj' in nodes[0].name().lower())

	# Not implemented in Houdini
	# def createInstance(self):
	# 	translator.openFile(self.scriptPath, force=True)

	# 	# Should not work with non mesh/transform node
	# 	nodeTime = translator.getNodeByName('time1')
	# 	instanceTime = translator.createInstance(nodeTime)
	# 	self.assertEqual(instanceTime, None)

	# 	# Should work with mesh/transform nodes
	# 	nodeCubeMesh = translator.getNodeByName('pCubeShape1')
	# 	instanceCubeMesh = translator.createInstance(nodeCubeMesh)
	# 	self.assertTrue('pcube' in instanceCubeMesh.name().lower())

	# 	nodeCubeMesh = translator.getNodeByName('pCube1')
	# 	instanceCubeMesh = translator.createInstance(nodeCubeMesh)
	# 	self.assertTrue('pcube' in instanceCubeMesh.name().lower())

	def removeNodes(self):
		translator.openFile(self.scriptPath, force=True)
		node = translator.getNodeByName('box1')
		translator.removeNodes(node)
		nodes = translator.getAllNodes()
		names = [n.name() for n in nodes]
		self.assertTrue('box1' not in names)

	def getRenderProperties(self):
		translator.openFile(self.scriptPath, force=True)

		# getRenderNode and setRenderNode
		translator.setRenderNode(translator.getNodeByName('mantra1'))
		self.assertEqual(translator.getRenderNode().name(), 'mantra1')

		# renderNode width height
		self.assertEqual(translator.getRenderProperty('width'), 1280)
		self.assertEqual(translator.getRenderProperty('height'), 720)

		# set renderProperty
		translator.setRenderProperty('width', 960)
		translator.setRenderProperty('height', 540)
		self.assertEqual(translator.getRenderProperty('width'), 960)
		self.assertEqual(translator.getRenderProperty('height'), 540)

		# set FPS
		translator.setFPS(23.976)

		# set/get render range
		translator.setRenderRange(1001, 1275)
		renderRange = translator.getRenderRange()
		self.assertEqual(renderRange['startFrame'], 1001)
		self.assertEqual(renderRange['endFrame'], 1275)

		# renderNode width height
		renderProps = translator.getRenderProperties()
		print 'Render properties:'
		print renderProps
		self.assertEqual(
				renderProps['program'],
				'houdini')
		self.assertEqual(
				renderProps['startFrame'],
				1001)
		self.assertEqual(
				renderProps['endFrame'],
				1275)
		self.assertEqual(
				renderProps['fps'],
				23.976)
		self.assertEqual(
				renderProps['width'],
				960)
		self.assertEqual(
				renderProps['height'],
				540)

	def getAndSetOutputFilename(self):
		translator.openFile(self.scriptPath, force=True)
		translator.setRenderNode(translator.getNodeByName('mantra1'))
		jobData = {
			'name': 'test',
			'version': 001,
			'cameraName': 'cam1',
			'renderNode': translator.getRenderNode().getPath(),
			'jobType': 'Houdini_Mantra',
			'deep': False,
		}

		translator.setOutputFilename('test', jobData)
		self.assertEqual(
			translator.getOutputFilename(self.testRoot, jobData),
			'c:/ie/translators/test/test_houdiniTranslator/renders/v001/test.%04d.exr')

	def animationProperties(self):
		translator.openFile(self.scriptPath, force=True)

		# set FPS
		translator.setFPS(23.976)

		self.assertEqual(
			translator.getFPS(),
			23.976)

		# getAnimationRange
		animRange = translator.getAnimationRange()
		self.assertEqual(
			animRange['startFrame'],
			1)
		self.assertEqual(
			animRange['endFrame'],
			240)

		# setAnimationRange
		translator.setAnimationRange(950, 1050)
		animRange = translator.getAnimationRange()
		self.assertEqual(
			animRange['startFrame'],
			950)
		self.assertEqual(
			animRange['endFrame'],
			1050)
		translator.setAnimationRange(1, 240)

		translator.setAnimationFrame(1010)
		self.assertEqual(
			translator.getAnimationFrame(),
			1010)

	def IO(self):
		translator.openFile(self.scriptPath)
		# alembic geometry
		# importAlembicGeometry returns list of new nodes created
		alembicGeoPath = self.assetsRoot + 'redCube.abc'
		print 'Importing ' + alembicGeoPath
		nodes = translator.importAlembicGeometry(alembicGeoPath)
		self.assertEqual(len(nodes), 4)
		names = translator.nodeToNameList(nodes)
		self.assertTrue('box' in names)
		box = translator.getNodeByName('box')
		translator.removeNodes(box)

		# alembic camera
		alembicCamPath = self.assetsRoot + 'camera_modo.abc'
		print 'Importing ' + alembicCamPath
		nodesCamera = translator.importAlembicCamera(alembicCamPath)
		types = translator.nodeToTypeList(nodesCamera)
		self.assertTrue('cam' in types)
		translator.removeNodes(nodesCamera)

		# fbx geometry
		FBXGeoPath = self.assetsRoot + 'cone.fbx'
		print 'Importing ' + FBXGeoPath
		nodesFBX = translator.importFBXGeometry(FBXGeoPath)
		namesFBX = translator.nodeToNameList(nodesFBX)
		self.assertTrue('cone_fbx' in namesFBX)
		cone = translator.getNodeByName('cone_fbx')
		translator.removeNodes(cone)

		# fbx camera
		FBXCamPath = self.assetsRoot + 'cameraFull.fbx'
		nodesFBXCamera = translator.importFBXCamera(FBXCamPath)
		types = translator.nodeToTypeList(nodesFBXCamera)
		self.assertTrue('cam' in types)
		translator.removeNodes(nodesFBXCamera)

		# obj geometry
		OBJGeoPath = self.assetsRoot + 'pipe.obj'
		print 'Importing ' + OBJGeoPath
		nodesOBJ = translator.importOBJGeometry(OBJGeoPath)
		namesOBJ = translator.nodeToNameList(nodesOBJ)
		self.assertTrue('geo1' in namesOBJ)
		pipe = translator.getNodeByName('geo1')
		children = list(translator.ensureNative(pipe).allSubChildren())
		children = translator.nodeToTypeList(translator.ensureNodes(children))
		self.assertTrue('file' in children)
		translator.removeNodes(pipe)

		# import image
		imagePath = self.assetsRoot + 'image.jpg'

		# image as imagePlane
		print 'Importing %s as imagePlane' % imagePath
		pre = translator.getAllNodes()
		translator.importImage(imagePath, 'imagePlane')
		post = translator.getAllNodes()
		nodes = translator.newNodes(pre, post)
		types = translator.nodeToTypeList(nodes)
		cam = nodes[0]
		self.assertTrue('cam' in types)
		children = list(translator.ensureNative(cam).allSubChildren())
		children = translator.nodeToTypeList(translator.ensureNodes(children))
		self.assertTrue('file' in children)
		translator.removeNodes(nodes)

		# image sequence
		sequencePath = self.assetsRoot + 'seq.%04d.png'

		# sequence as imagePlanes
		print 'Importing %s as imagePlanes' % sequencePath
		pre = translator.getAllNodes()
		translator.importImageSequence(sequencePath, 'imagePlane')
		post = translator.getAllNodes()
		nodes = translator.newNodes(pre, post)
		types = translator.nodeToTypeList(nodes)
		cam = nodes[0]
		self.assertTrue('cam' in types)
		children = list(translator.ensureNative(cam).allSubChildren())
		children = translator.nodeToTypeList(translator.ensureNodes(children))
		self.assertTrue('file' in children)
		translator.removeNodes(nodes)

def main():
	tryout.run(test)

if __name__ == '__main__':
	main()
