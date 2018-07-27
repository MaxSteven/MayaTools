import sys

import arkInit
arkInit.init()
import cOS

import settingsManager
globalSettings = settingsManager.globalSettings()
import nuke
import arkNuke

from nukeScript import NukeScript

import translators
translator = translators.getCurrent()

'''
options
	inputImage
	outputPath
	inputColorspace
	outputColorspace
	topLeft
	topMid
	topRight
	bottomLeft
	bottomMid
	bottomRight

'''
# "C:/Program Files/Nuke10.0v4/Nuke10.0.exe" -V 2 -t C:/ie/ark/programs/nuke/python/imageWatermark.py -options "{'outputColorspace': 'sRGB', 'inputColorspace': 'sRGB', 'outputPath': 'C:/Trash/v0004/TPT_0010_testarosa.%04d.jpg', 'inputImage': 'r:/Test_Project/Workspaces/publish/TPT_0010/renders/v0004/TPT_0010_testarosa.%04d.exr'}"
# "C:/Program Files/Nuke10.0v4/Nuke10.0.exe" -V 2 -t C:/ie/ark/programs/nuke/python/imageWatermark.py -options "{'outputColorspace': 'sRGB', 'inputColorspace': 'sRGB', 'outputPath': 'C:/Trash/v0004/TPT_0010_testarosa.%04d.jpg', 'inputImage': 'r:/Test_Project/Workspaces/publish/TPT_0010/renders/v0004/TPT_0010_testarosa.%04d.exr', 'bottomLeft': 'frame', 'bottomMid': 'bottomMid'}"
# "C:/Program Files/Nuke10.0v4/Nuke10.0.exe" -V 2 -t C:/ie/ark/programs/nuke/python/imageWatermark.py -options "{'outputColorspace': 'sRGB', 'inputColorspace': 'sRGB', 'outputPath': 'C:/Trash/v0004/TPT_0010_testarosa.%04d.jpg', 'inputImage': 'r:/Test_Project/Workspaces/publish/TPT_0010/renders/v0004/TPT_0010_testarosa.%04d.exr', 'bottomLeft': 'frame', 'bottomMid': 'bottomMid', 'bottomRight': 'cameraShape2', 'topLeft': '<-', 'topMid': '--', 'topRight': '->'}"
# "C:/Program Files/Nuke10.0v4/Nuke10.0.exe" -V 2 -t C:/ie/ark/programs/nuke/python/imageWatermark.py -options "{'outputColorspace': 'sRGB', 'inputColorspace': 'sRGB', 'outputPath': 'C:/Trash/v0004/TPT_0010_testarosa.%04d.jpg', 'inputImage': 'r:/Test_Project/Workspaces/publish/TPT_0010/renders/v0004/TPT_0010_testarosa.%04d.exr', 'bottomLeft': 'frame', 'bottomMid': 'bottomMid', 'bottomRight': 'cameraShape2', 'topLeft': '<-', 'topMid': '--', 'topRight': '->'}"
# "C:/Program Files/Nuke10.0v4/Nuke10.0.exe" -V 2 -t C:/ie/ark/programs/nuke/python/imageWatermark.py -options "{'outputColorspace': 'sRGB', 'inputColorspace': 'linear', 'outputPath': 'C:/Trash/v0004/TPT_0010_testarosa.%04d.jpg', 'inputImage': 'r:/Test_Project/Workspaces/publish/TPT_0010/renders/v0004/TPT_0010_testarosa.%04d.exr', 'bottomLeft': 'frame', 'bottomMid': 'bottomMid', 'bottomRight': 'cameraShape2', 'topLeft': '<-', 'topMid': '--', 'topRight': '->'}"
# "C:/Program Files/Nuke10.0v4/Nuke10.0.exe" -V 2 -t C:/ie/ark/programs/nuke/python/imageWatermark.py -options "{'outputColorspace': 'linear', 'inputColorspace': 'linear', 'outputPath': 'C:/Trash/v0004/TPT_0010_testarosa.%04d.exr', 'inputImage': 'r:/Test_Project/Workspaces/publish/TPT_0010/renders/v0004/TPT_0010_testarosa.%04d.exr', 'bottomLeft': 'frame', 'bottomMid': 'bottomMid', 'bottomRight': 'cameraShape2', 'topLeft': '<-', 'topMid': '-mid-', 'topRight': '->'}"

class imageWatermark(NukeScript):

	args = False
	thumbnailNode = False
	# pretty good default, 90% of our work..
	fps = 23.976

	def __init__(self):
		print 'Watermark: __init__'

	def setIncomingColorspace(self):
		print 'Watermark: setIncomingColorspace'

		colorspace = self.getOption('inputColorspace', 'linear')
		translator.getNodeByName('readNode').setProperty('colorspace', colorspace)

	def setWriteNode(self):
		print 'Watermark: setWriteNode'

		self.writeNode = translator.getNodeByName('writeNode')

		self.writeNode.setProperty('file', self.getOption('outputPath'))
		frameRange = cOS.getFrameRange(self.getOption('inputImage'))
		self.startFrame = frameRange['min']
		self.endFrame = frameRange['max']

		self.writeNode.setProperty('beforeRender', '')
		self.writeNode.setProperty('beforeFrameRender', '')
		self.writeNode.setProperty('afterRender', '')
		self.writeNode.setProperty('afterFrameRender', '')
		self.writeNode.setProperty('renderProgress', '')
		try:
			self.writeNode.setProperty('mov64_fps', self.fps)
		except:
			pass

		if not self.writeNode:
			raise Exception('Invalid codec: ' + self.getOption('codec'))
			return sys.exit(1)

		outputColorspace = str(self.getOption('outputColorspace'))
		self.writeNode.setProperty('colorspace', outputColorspace)

		arkNuke.beforeRender(self.writeNode.nativeNode())

	def parseKey(self, text):
		if (text == 'frame'):
			return '[format "%04i" [frame]]'
		else:
			return text

	def createScript(self):
		print 'Watermark: createScript'

		# open the watermark script
		nuke.scriptOpen(globalSettings.SHEPHERD_ROOT + 'assets/watermark.nk')

		topLeft = self.parseKey(self.getOption('topLeft', ''))
		topMid = self.parseKey(self.getOption('topMid', ''))
		topRight = self.parseKey(self.getOption('topRight', ''))
		bottomLeft = self.parseKey(self.getOption('bottomLeft', ''))
		bottomMid = self.parseKey(self.getOption('bottomMid', ''))
		bottomRight = self.parseKey(self.getOption('bottomRight', ''))

		translator.getNodeByName('topLeft').setProperty('message', topLeft)
		translator.getNodeByName('topMid').setProperty('message', topMid)
		translator.getNodeByName('topRight').setProperty('message', topRight)
		translator.getNodeByName('bottomLeft').setProperty('message', bottomLeft)
		translator.getNodeByName('bottomMid').setProperty('message', bottomMid)
		translator.getNodeByName('bottomRight').setProperty('message', bottomRight)

		self.setIncomingColorspace()

		self.setWriteNode()

		nuke.root()['onScriptLoad'].setValue('')
		nuke.root()['onScriptSave'].setValue('')
		nuke.root()['onScriptClose'].setValue('')
		nuke.scriptSave(globalSettings.TEMP + 'watermark.nk')

	def execute(self, start=None, end=None):
		print 'Watermark: Rendering frame range: %s-%s' % (self.startFrame, self.endFrame)
		nuke.execute(self.writeNode.name(), self.startFrame, self.endFrame)

if __name__ == '__main__':
	imageWatermark = imageWatermark()
	imageWatermark.parseArgs(sys.argv)
	imageWatermark.createScript()
	imageWatermark.execute()
