# Initialization
import sys
import os
os.environ['ARK_CURRENT_APP'] = 'maya'

sys.path.append('C:/Python27/Lib/site-packages/')

import arkInit
arkInit.init()

import settingsManager
globalSettings = settingsManager.globalSettings()

sys.path.append(globalSettings.MAYA_SCRIPT_ROOT)
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
	title = 'test/test_maya.py'
	timeout = 10

	# Setup
	##################################################
	def setUpClass(self):
		self.testRoot = cOS.getDirName(__file__)
		self.scriptPath = self.testRoot + 'test_v001.mb'
		# Alternative test file, to resolve race issues (trying to save/open same file)
		self.scriptPathAlt = self.testRoot + 'test_v002.mb'
		self.assetsRoot = cOS.upADir(self.testRoot) + 'test_assets/'

	# Basics
	##################################################
	def basics(self):
		self.assertEqual(translator.program, 'maya')
		self.assertEqual(translator.fileExtension, 'mb')

	def getSceneData(self):
		translator.setSceneData('things','awesome')
		data = translator.getSceneData('things')

		self.assertEqual(data, 'awesome')

	def setSceneData(self):
		translator.setSceneData('cool','yes')

		self.assertEqual(translator.program, 'maya')
		self.assertEqual(translator.fileExtension, 'mb')

	def getFilename(self):
		filename = translator.getFilename()
		print 'filename before is ' + filename
		try:
			translator.closeFile(force=True)
		except Exception as err:
			print 'closeFile in getFilename exception: ' + err.message
		filename = translator.getFilename()
		self.assertEqual(filename, '')

	def openFile(self):
		translator.openFile(self.scriptPath, force=True)
		filename = translator.getFilename()

		self.assertEqual(filename, self.scriptPath)
		allNodes = translator.getAllNodes()
		self.assertTrue(len(allNodes) > 3)

	def saveFile(self):
		translator.openFile(self.scriptPathAlt, force=True)
		newFilename = self.testRoot + 'test_v003.mb'
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
		node = translator.getNodeByName('time1')
		self.assertTrue('time' in node.name().lower())

	def getNodesByType(self):
		translator.openFile(self.scriptPath, force=True)
		nodes = translator.getNodesByType('time')

		print 'Time nodes:'
		for node in nodes:
			print node.name()

		self.assertTrue('time' in nodes[0].name().lower())

	def selectNodes(self):
		translator.openFile(self.scriptPath, force=True)
		node = translator.getNodeByName('lambert1')
		translator.selectNodes(node)
		nodes = translator.getSelectedNodes()

		print 'Selected nodes:'
		for node in nodes:
			print node.name()

		self.assertEqual(len(nodes), 1)
		self.assertTrue('lambert' in nodes[0].name().lower())

	def createInstance(self):
		translator.openFile(self.scriptPath, force=True)

		# Should not work with non mesh/transform node
		nodeTime = translator.getNodeByName('time1')
		instanceTime = translator.createInstance(nodeTime)
		self.assertEqual(instanceTime, None)

		# Should work with mesh/transform nodes
		nodeCubeMesh = translator.getNodeByName('pCubeShape1')
		instanceCubeMesh = translator.createInstance(nodeCubeMesh)
		self.assertTrue('pcube' in instanceCubeMesh.name().lower())

		nodeCubeMesh = translator.getNodeByName('pCube1')
		instanceCubeMesh = translator.createInstance(nodeCubeMesh)
		self.assertTrue('pcube' in instanceCubeMesh.name().lower())

	def removeNodes(self):
		translator.openFile(self.scriptPath, force=True)
		node = translator.getNodeByName('pCube1')
		translator.removeNodes(node)
		nodes = translator.getAllNodes()
		names = [n.name() for n in nodes]
		self.assertTrue('pCube1' not in names)

	def getRenderProperties(self):
		translator.openFile(self.scriptPath, force=True)

		# renderNode width height
		self.assertEqual(
			translator.getRenderProperty('width'),
			960)
		self.assertEqual(
			translator.getRenderProperty('height'),
			540)

		# renderNode width height
		renderProps = translator.getRenderProperties()
		print 'Render properties:'
		print renderProps
		self.assertEqual(
				renderProps['program'],
				'maya')
		self.assertEqual(
				renderProps['startFrame'],
				1001)
		self.assertEqual(
				renderProps['endFrame'],
				1275)
		self.assertEqual(
				renderProps['fps'],
				24)
		self.assertEqual(
				renderProps['width'],
				960)
		self.assertEqual(
				renderProps['height'],
				540)

	def getAndSetOutputFilename(self):
		translator.openFile(self.scriptPath, force=True)

		jobData = {
			'name': 'test',
			'version': 001,
			'cameraName': 'renderCam',

		}

		translator.setOutputFilename('test', jobData)
		self.assertEqual(
			translator.getOutputFilename(self.testRoot, jobData),
			'c:/ie/translators/test/test_mayaTranslator/renders/v001/test_renderCam.%04d.exr')

	def animationProperties(self):
		translator.openFile(self.scriptPath, force=True)

		# Maya only returns as 'film', 24 fps
		self.assertEqual(
			translator.getFPS(),
			24)

		# getAnimationRange
		animRange = translator.getAnimationRange()
		self.assertEqual(
			animRange['startFrame'],
			1001)
		self.assertEqual(
			animRange['endFrame'],
			1300)

		# setAnimationRange
		translator.setAnimationRange(950, 1050)
		animRange = translator.getAnimationRange()
		self.assertEqual(
			animRange['startFrame'],
			950)
		self.assertEqual(
			animRange['endFrame'],
			1050)
		translator.setAnimationRange(1001, 1300)

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
		self.assertEqual(len(nodes), 2)
		names = translator.nodeToNameList(nodes)
		self.assertTrue('box' in names)
		box = translator.getNodeByName('box')
		translator.removeNodes(box)

		# alembic camera
		alembicCamPath = self.assetsRoot + 'camera_modo.abc'
		print 'Importing ' + alembicCamPath
		nodesCamera = translator.importAlembicCamera(alembicCamPath)
		types = translator.nodeToTypeList(nodesCamera)
		self.assertTrue('camera' in types)
		translator.removeNodes(nodesCamera)

		# fbx geometry
		FBXGeoPath = self.assetsRoot + 'cone.fbx'
		print 'Importing ' + FBXGeoPath
		nodesFBX = translator.importFBXGeometry(FBXGeoPath)
		namesFBX = translator.nodeToNameList(nodesFBX)
		self.assertTrue('pCone1' in namesFBX)
		cone = translator.getNodeByName('pCone1')
		translator.removeNodes(cone)

		# fbx camera
		FBXCamPath = self.assetsRoot + 'cameraFull.fbx'
		nodesFBXCamera = translator.importFBXCamera(FBXCamPath)
		types = translator.nodeToTypeList(nodesFBXCamera)
		self.assertTrue('camera' in types)
		translator.removeNodes(nodesFBXCamera)

		# obj geometry
		OBJGeoPath = self.assetsRoot + 'pipe.obj'
		print 'Importing ' + OBJGeoPath
		nodesOBJ = translator.importOBJGeometry(OBJGeoPath)
		namesOBJ = translator.nodeToNameList(nodesOBJ)
		self.assertTrue('pPipe1' in namesOBJ)
		pipe = translator.getNodeByName('pPipe1')
		translator.removeNodes(pipe)

		# import image
		imagePath = self.assetsRoot + 'image.jpg'

		# image as materialEditor
		print 'Importing %s as materialEditor' % imagePath
		pre = translator.getAllNodes()
		translator.importImage(imagePath, 'materialEditor')
		post = translator.getAllNodes()
		nodes = translator.newNodes(pre, post)
		types = translator.nodeToTypeList(nodes)
		self.assertTrue('file' in types)
		self.assertTrue('placedtexture' in types)
		translator.removeNodes(nodes)

		# image as imagePlane
		print 'Importing %s as imagePlane' % imagePath
		pre = translator.getAllNodes()
		translator.importImage(imagePath, 'imagePlane')
		post = translator.getAllNodes()
		nodes = translator.newNodes(pre, post)
		types = translator.nodeToTypeList(nodes)
		self.assertTrue('imageplane' in types)
		translator.removeNodes(nodes)

		# image as referencePlane
		print 'Importing %s as referencePlane' % imagePath
		pre = translator.getAllNodes()
		translator.importImage(imagePath, 'referencePlane')
		post = translator.getAllNodes()
		nodes = translator.newNodes(pre, post)
		types = translator.nodeToTypeList(nodes)
		self.assertTrue('polyplane' in types)
		self.assertTrue('file' in types)
		translator.removeNodes(nodes)

		# image sequence
		sequencePath = self.assetsRoot + 'seq.%04d.png'

		# sequence as materialEditor files
		print 'Importing %s as materialEditor files' % sequencePath
		pre = translator.getAllNodes()
		translator.importImageSequence(sequencePath, 'materialEditor')
		post = translator.getAllNodes()
		nodes = translator.newNodes(pre, post)
		types = translator.nodeToTypeList(nodes)
		self.assertTrue('file' in types)
		self.assertTrue('placedtexture' in types)
		count = types.count('file')
		self.assertEqual(count, 5)
		countPlaced = types.count('placedtexture')
		self.assertEqual(countPlaced, 5)
		translator.removeNodes(nodes)

		# sequence as imagePlanes
		print 'Importing %s as imagePlanes' % sequencePath
		pre = translator.getAllNodes()
		translator.importImageSequence(sequencePath, 'imagePlane')
		post = translator.getAllNodes()
		nodes = translator.newNodes(pre, post)
		types = translator.nodeToTypeList(nodes)
		self.assertTrue('imageplane' in types)
		count = types.count('imageplane')
		self.assertEqual(count, 5)
		translator.removeNodes(nodes)

		# sequence as referencePlanes
		print 'Importing %s as referencePlanes' % sequencePath
		pre = translator.getAllNodes()
		translator.importImageSequence(sequencePath, 'referencePlane')
		post = translator.getAllNodes()
		nodes = translator.newNodes(pre, post)
		types = translator.nodeToTypeList(nodes)
		self.assertTrue('polyplane' in types)
		count = types.count('polyplane')
		self.assertEqual(count, 5)
		translator.removeNodes(nodes)

def main():
	tryout.run(test)

if __name__ == '__main__':
	main()
