
# Standard modules
from expects import *
# import time

# Our modules
import arkInit
arkInit.init()

import tryout
# import cOS
import translators
translator = translators.getCurrent()


class test(tryout.TestSuite):
	title = 'test/test_nuke.py'
	timeout = 10

	# Setup
	##################################################
	def setUpClass(self):
		self.testRoot = cOS.getDirName(__file__)
		self.scriptPath = self.testRoot + 'test_v001_ghm.nk'
		self.assetsRoot = cOS.upADir(self.testRoot) + 'test_assets/'

	# Basics
	##################################################
	def basics(self):
		self.assertEqual(translator.program, 'nuke')
		self.assertEqual(translator.fileExtension, 'nk')

	def getSceneData(self):
		translator.setSceneData('things','awesome')
		data = translator.getSceneData('things')

		self.assertEqual(data, 'awesome')

		translator.setSceneData('passes',['one','two','three'])
		data = translator.getSceneData('passes')

		self.assertIn('one', data)
		self.assertIn('two', data)
		self.assertIn('three', data)

	def setSceneData(self):
		translator.setSceneData('cool','yes')

		self.assertEqual(translator.program, 'nuke')
		self.assertEqual(translator.fileExtension, 'nk')

	def getFilename(self):
		translator.closeFile()
		filename = translator.getFilename()
		self.assertEqual(filename, '')

	def openFile(self):
		translator.openFile(self.scriptPath)
		filename = translator.getFilename()

		self.assertEqual(filename, self.scriptPath)
		allNodes = translator.getAllNodes()
		self.assertTrue(len(allNodes) > 3)

	def saveFile(self):
		translator.openFile(self.scriptPath)
		newFilename = self.testRoot + 'test_v002_ghm.nk'
		translator.saveFile(newFilename)
		filename = translator.getFilename()

		self.assertEqual(filename, newFilename)
		self.assertTrue(os.path.isfile(newFilename))
		os.remove(newFilename)

	def getAllNodes(self):
		translator.openFile(self.scriptPath)
		nodes = translator.getAllNodes()

		print 'Nodes:'
		for node in nodes:
			print node.name()

		self.assertTrue(nodes[0].name() != '')
		allNodes = translator.getAllNodes()
		self.assertTrue(len(allNodes) > 3)

	def getNodesByName(self):
		translator.openFile(self.scriptPath)
		node = translator.getNodeByName('Write1')
		self.assertTrue('write' in node.name().lower())

	def getNodesByType(self):
		translator.openFile(self.scriptPath)
		nodes = translator.getNodesByType('write')

		print 'Write nodes:'
		for node in nodes:
			print node.name()

		self.assertTrue('write' in nodes[0].name().lower())

	# can't test selection as
	# the Nuke gui opens and pops us out of the tests
	# def selectNodes(self):
	# 	translator.openFile(self.scriptPath)
	# 	node = translator.getNodeByName('Noise1')
	# 	translator.selectNodes(node)
	# 	nodes = translator.getSelectedNodes()

	# 	print 'Selected nodes:'
	# 	for node in nodes:
	# 		print node.name()

	# 	self.assertEqual(len(nodes), 1)
	# 	self.assertTrue('noise' in nodes[0].name().lower())

	# can't run createInstance, don't really know why
	# def createInstance(self):
	# 	translator.openFile(self.scriptPath)
	# 	node = translator.getNodeByName('Noise1')
	# 	instance = translator.createInstance(node)
	# 	self.assertEqual(instance.name(), node.name())

	def removeNodes(self):
		translator.openFile(self.scriptPath)
		node = translator.getNodeByName('Noise1')
		translator.removeNodes(node)
		nodes = translator.getAllNodes()
		names = [n.name() for n in nodes]
		self.assertTrue('Noise1' not in names)

	def getRenderProperties(self):
		# clear the render node so we use the root format
		translator.setOption('renderNode', None)

		# comp width height
		translator.openFile(self.scriptPath)
		self.assertEqual(
			translator.getRenderProperty('width'),
			1920)
		self.assertEqual(
			translator.getRenderProperty('height'),
			1080)

		# getRenderNode and setRenderNode
		translator.setRenderNode(
			translator.getNodeByName('Write1'))
		self.assertEqual(
			translator.getRenderNode().name(),
			'Write1')

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
				'nuke')
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
		translator.openFile(self.scriptPath)
		translator.setRenderNode(
			translator.getNodeByName('Write1'))

		translator.setOutputFilename('foo/bar.%04d.jpg')
		self.assertEqual(
			translator.getOutputFilename(),
			'foo/bar.%04d.jpg')

	def animationProperties(self):
		translator.openFile(self.scriptPath)

		# getFPS
		self.assertEqual(
			translator.getFPS(),
			23.976)

		# getAnimationRange
		animRange = translator.getAnimationRange()
		self.assertEqual(
			animRange['startFrame'],
			1001)
		self.assertEqual(
			animRange['endFrame'],
			1275)

		# setAnimationRange
		translator.setAnimationRange(950, 1050)
		animRange = translator.getAnimationRange()
		self.assertEqual(
			animRange['startFrame'],
			950)
		self.assertEqual(
			animRange['endFrame'],
			1050)
		translator.setAnimationRange(1001, 1275)

		translator.setAnimationFrame(1010)
		self.assertEqual(
			translator.getAnimationFrame(),
			1010)

	def IO(self):
		translator.openFile(self.scriptPath)

		# alembic geometry
		translator.importAlembicGeometry(
			self.assetsRoot + 'redCube.abc')
		nodes = translator.getNodesByType('readGeo')
		self.assertEqual(len(nodes), 1)
		self.assertTrue(
			'redCube.abc' in nodes[0].getProperty('file'))
		translator.removeNodes(nodes)

		# alembic camera
		translator.importAlembicCamera(
			self.assetsRoot + 'camera_modo.abc')
		nodes = translator.getNodesByType('camera')
		self.assertEqual(len(nodes), 1)
		self.assertTrue(
			'camera_modo.abc' in nodes[0].getProperty('file'))
		translator.removeNodes(nodes)

		# fbx geometry
		translator.importFBXGeometry(
			self.assetsRoot + 'triangle.fbx')
		nodes = translator.getNodesByType('readGeo')
		self.assertEqual(len(nodes), 1)
		self.assertTrue(
			'triangle.fbx' in nodes[0].getProperty('file'))
		translator.removeNodes(nodes)

		# fbx camera
		translator.importFBXCamera(
			self.assetsRoot + 'camera_modo.fbx')
		nodes = translator.getNodesByType('camera')
		self.assertEqual(len(nodes), 1)
		self.assertTrue(
			'camera_modo.fbx' in nodes[0].getProperty('file'))
		translator.removeNodes(nodes)

		# obj geometry
		translator.importOBJGeometry(
			self.assetsRoot + 'triangle.obj')
		nodes = translator.getNodesByType('readGeo')
		self.assertEqual(len(nodes), 1)
		self.assertTrue(
			'triangle.obj' in nodes[0].getProperty('file'))
		translator.removeNodes(nodes)

		# image
		translator.importImage(
			self.assetsRoot + 'image.jpg')
		nodes = translator.getNodesByType('read')
		self.assertEqual(len(nodes), 1)
		self.assertTrue(
			'image.jpg' in nodes[0].getProperty('file'))
		translator.removeNodes(nodes)

		# image sequence
		translator.importImageSequence(
			self.assetsRoot + 'seq.%04d.png')
		nodes = translator.getNodesByType('read')
		self.assertEqual(len(nodes), 1)
		self.assertTrue(
			'seq.%04d.png' in nodes[0].getProperty('file'))
		self.assertEqual(
				nodes[0].getProperty('first'),
				1001)
		self.assertEqual(
				nodes[0].getProperty('last'),
				1005)
		translator.removeNodes(nodes)


def main():
	tryout.run(test)

if __name__ == '__main__':
	main()
