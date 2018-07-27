import sys
# import os
# import glob
import re
# import json
# import time

import arkInit
arkInit.init()
# import ieOS
import cOS

# import arkUtil
import settingsManager
globalSettings = settingsManager.globalSettings()
import nuke
import arkNuke
import pathManager

from nukeScript import NukeScript

class ImageConverter(NukeScript):

	args = False
	options = {}
	thumbnailNode = False
	# pretty good default, 90% of our work..
	fps = 23.976
	# stupidly, the colorspaces are named differently in the
	# colorspace and write nodes
	# RGB is what the value of the knob is for Linear.  This is crazyness I realize. #blameTheFoundry
	colorspaceMap = {
		'linear': 'RGB',
		'sRGB': 'sRGB\tsRGB (~2.20)',
		'rec709': 'rec709\trec709 (~1.95)',
		'Cineon': 'Cineon',
		'REDLog': 'REDLog',
		'AlexaV3LogC': 'AlexaV3LogC',
		'SLog': 'SLog',
		'SLog3': 'SLog3',
	}


	def __init__(self):
		print 'Converter: __init__'

	def createThumbnailNodes(self):
		print 'Converter: createThumbnailNodes'

		thumbnailOutput = cOS.removeExtension(self.outFile) + '_thumb.jpg'

		# thumbnailHeight is height propritionally scaled the same as the width then ensured to be a multiple of 4
		thumbScale = self.getOption('thumbScale',globalSettings.THUMBNAIL_SCALE)

		thumbReformat = nuke.nodes.Reformat(type='scale')
		thumbReformat['scale'].setValue(float(thumbScale))
		thumbReformat.setInput(0, self.readNode)

		outputColorspace = self.getOption('thumbColorspace', 'sRGB')
		self.thumbnailNode = nuke.nodes.Write(name='Write_Thumbnail',
										file=thumbnailOutput,
										file_type='jpg',
										beforeRender='',
										colorspace=outputColorspace,
										afterRender='')

		self.thumbnailNode['_jpeg_quality'].setValue(.75)
		self.thumbnailNode.setInput(0, thumbReformat)
		return self.thumbnailNode

	def createReadNodes(self):
		print 'Converter: createReadNodes'

		# get the list of input objects
		inputs = self.getOption('inputs')

		# get the appendClip node
		appendNode = nuke.toNode('append')

		handles = self.getOption('handles', 0)
		formattedSequence = re.compile('.+? [0-9]+-[0-9]+')

		# loop over the input objects and add the read nodes
		self.totalLength = 0

		xStart = arkNuke.getXPos(appendNode)
		yStart = arkNuke.getYPos(appendNode)

		for n, readInfo in enumerate(inputs):
			# raw value, no colorspace conversion
			readNode = nuke.nodes.Read(raw=True)

			# handle image sequences
			if formattedSequence.match(readInfo['file']):
				print 'Converter: Using frame range from formatted sequence'
			elif '%' in readInfo['file']:
				print 'Converter: Calculating frame range'
				readInfo['file'] = cOS.getFrameRangeText(readInfo['file'])

			print 'Converter: Reading ', readInfo['file']
			# set file via fromUserText() to auto-populate
			# first and last frame
			readNode['file'].fromUserText(readInfo['file'])

			if readNode.metadata() and 'input/frame_rate' in readNode.metadata():
				self.fps = round(readNode.metadata()['input/frame_rate'], 3)
			# try to get the values from readInfo if they exist
			if 'start' in readInfo and 'end' in readInfo:
				start = readInfo['start']
				end = readInfo['end']
			# otherwise pull them from the read node itself
			else:
				# add shot length to totalLength, subtracting handles
				start = readNode['first'].getValue()
				end = readNode['last'].getValue()

			# handles * 2 cuz start and end handles
			# +1 because it's start-end inclusive
			self.totalLength += end - start - handles * 2 + 1

			# subtract out handles
			readNode['first'].setValue(int(start + handles))
			readNode['last'].setValue(int(end - handles))
			readNode['on_error'].setValue('black')

			print 'Converter: %d - %d %d frames' % (start, end, end - start +1 - handles * 2)

			# set position
			readNode.setXpos(xStart + n * 120)
			readNode.setYpos(yStart - 240)

			appendNode.setInput(n, readNode)

			# if the first read node has an alpha channel
			# then disable the addAlpha node
			if n == 0 and 'rgba.alpha' in nuke.channels(readNode):
				nuke.toNode('addAlpha')['disable'].setValue(True)

	def setIncomingColorspace(self):
		print 'Converter: setIncomingColorspace'

		colorspace = self.getOption('inputColorspace', 'linear')
		if colorspace in self.colorspaceMap:
			colorspace = self.colorspaceMap[colorspace]

		nuke.toNode('colorspace')['colorspace_in'].setValue(colorspace)

	def setFormat(self):
		print 'Converter: setFormat'

		resize = self.getOption('resize', 1)
		# strip out invalid characters
		reformat = re.sub('[^0-9x\.]', '', str(resize))
		reformatNode = nuke.toNode('reformat')

		# reformat can be in two forms:
		# 1920x1080 or .5, this handles both
		if 'x' in reformat:
			reformatNode['type'].setValue('to box')
			reformatNode['box_fixed'].setValue(True)
			width, height = [int(n) for n in reformat.split('x')]
			# if writing out an mov or mp4 the dimensions
			# must be a multiple of 4
			if '.mov' or '.mp4' in self.getOption('output'):
				width = int(int(width) * .25) * 4
				height = int(int(height) * .25) * 4

			reformatNode['box_width'].setValue(width)
			reformatNode['box_height'].setValue(height)
		elif reformat:
			reformatNode['type'].setValue('scale')
			reformatNode['scale'].setValue(float(reformat))

		# defaults for additional resize options
		resizeType = self.getOption('resizeType', 'width')
		resizeFilter = self.getOption('resizeFilter', 'Cubic')
		resizeBlackOutside = self.getOption('resizeBlackOutside', True)
		resizePreserveBoundingBox = self.getOption('resizePreserveBoundingBox', False)

		# set additional options straight w/ a simple map
		additonalOptions = {
			'resize': resizeType,
			'filter': resizeFilter,
			'black_outside': resizeBlackOutside,
			'pbb': resizePreserveBoundingBox,
		}
		for k,v in additonalOptions.iteritems():
			reformatNode[k].setValue(v)

	def setSlate(self):
		print 'Converter: setSlate'

		burnInNode = nuke.toNode('burnIn')
		slateNode = nuke.toNode('slate')
		nodes = [slateNode, burnInNode]

		slateNode['slateFrame'].setValue(self.startFrame)

		slateOptions = [
			'project',
			'shot',
			'version',
			'artist',
			'notes',
			'burnIn',
			'maskOpacity'
		]
		# pull options from args
		# they're all prefixed w/ slate
		# ex: slateArtist
		for node in nodes:
			for option in slateOptions:
				optionName = 'slate' + option[0].upper() + option[1:]
				if optionName in self.options:
					try:
						if optionName == 'slateMaskOpacity':
							node[option].setValue(self.getOption(optionName, 0))
						else:
							node[option].setValue(str(self.getOption(optionName, '')))
					except Exception as e:
						print 'Error setting:', optionName, self.getOption(optionName, '')
						print e

		if self.getOption('slateBurnIn', False):
			burnInNode['disable'].setValue(False)
		else:
			burnInNode['disable'].setValue(True)

		if not self.useSlate:
			slateNode['disable'].setValue(True)


	def setRanges(self):
		print 'Converter: setRanges'

		self.startFrame = int(self.getOption('startFrame', 1000))
		# append clip normalizes the frame range
		# so the first frame is 1, not 0
		# to calculate the frameOffset we take startFrame and
		# subtract 1
		offset = self.startFrame - 1

		# if we're using a slate add 1 for the slate frame
		# if self.useSlate:
		# 	offset += 1

		nuke.toNode('timeOffset')['time_offset'].setValue(offset)

		# if length is 30 and start is 1000 we render 1000-1029
		self.endFrame = int(self.startFrame + self.totalLength - 1)

		# plus 2 for slate start and end frame
		# if self.useSlate:
		# 	self.endFrame += 2

		nuke.root()['first_frame'].setValue(self.startFrame)
		nuke.root()['last_frame'].setValue(self.endFrame)
		self.fps = float(self.getOption('fps', self.fps))
		nuke.root()['fps'].setValue(self.fps)

	def setWriteNode(self):
		print 'Converter: setWriteNode'

		self.writeNode = nuke.toNode(self.getOption('codec'))
		self.writeNode['beforeRender'].setValue('')
		self.writeNode['beforeFrameRender'].setValue('')
		self.writeNode['afterRender'].setValue('')
		self.writeNode['afterFrameRender'].setValue('')
		self.writeNode['renderProgress'].setValue('')
		try:
			self.writeNode['mov64_fps'].setValue(self.fps)
		except:
			pass

		if not self.writeNode:
			raise Exception('Invalid codec: ' + self.getOption('codec'))
			return sys.exit(1)

		outputColorspace = str(self.getOption('outputColorspace'))
		self.writeNode['colorspace'].setValue(outputColorspace)
		nuke.toNode('colorspaceText')['message'].setValue(outputColorspace)

		self.writeNode['file'].setValue(self.getOption('output'))
		arkNuke.beforeRender(self.writeNode)

	def setThumbnailNode(self):
		print 'Converter: setThumbnailNode'

		# set the frame
		self.thumbnailFrame = int(self.getOption('thumbnailFrame',
			self.totalLength * .5 + self.startFrame))

		# set the reformat
		thumbnailWidth = self.getOption('thumbnailWidth', globalSettings.THUMBNAIL_WIDTH)
		thumbnailHeight = self.getOption('thumbnailHeight', globalSettings.THUMBNAIL_HEIGHT)
		nuke.toNode('thumbnailReformat')['box_width'].setValue(thumbnailWidth)
		nuke.toNode('thumbnailReformat')['box_height'].setValue(thumbnailHeight)

		# set the thumbnail output
		filename = self.getOption('finalOutput', self.getOption('output'))
		if '%' in filename:
			base = '.'.join(filename.split('.')[:-2])
		else:
			base = '.'.join(filename.split('.')[:-1])

		parts = base.split('/')
		parts.insert(1, 'Caretaker')
		root = '/'.join(parts)
		cOS.makeDirs(root)
		filename = root + '.thumbnail.jpg'
		print 'Converter: Thumbnail filename:', filename

		self.thumbnailNode = nuke.toNode('thumbnail')
		self.thumbnailNode['beforeRender'].setValue('')
		self.thumbnailNode['beforeFrameRender'].setValue('')
		self.thumbnailNode['afterRender'].setValue('')
		self.thumbnailNode['afterFrameRender'].setValue('')
		self.thumbnailNode['renderProgress'].setValue('')
		self.thumbnailNode['file'].setValue(filename)
		cOS.makeDirs(filename)

	def applyCDL(self):
		print 'Converter: applyCDL'

		cdl = self.getOption('cdl', {
				'slope': [1.0, 1.0, 1.0],
				'offset': [0, 0, 0],
				'power': [1.0, 1.0, 1.0],
				'saturation': 1.0,
			})

		cdlNode = nuke.toNode('applyShotColor')

		print 'Setting CDL:', cdlNode.name()
		cdlNode['slope'].setValue(cdl['slope'])
		cdlNode['offset'].setValue(cdl['offset'])
		cdlNode['power'].setValue(cdl['power'])
		cdlNode['saturation'].setValue(cdl['saturation'])

		if cdl:
			print 'CDL Applied'
			print 'slope:', cdl['slope']
			print 'offset:', cdl['offset']
			print 'power:', cdl['power']
			print 'saturation:', cdl['saturation']

	def applyLUT(self):
		print 'Converter: applyLUT'
		lutNode = nuke.toNode('applyShotColor')
		lutNode['useLut'].setValue(False)

		lut = self.getOption('lut')
		lutWorkingSpace = self.getOption('lutWorkingSpace')
		if not lut or not lutWorkingSpace:
			print 'bad lut data:', lut, lutWorkingSpace
			return

		print 'Setting LUT:', lutNode.name()
		lutNode['useLut'].setValue(True)
		lut = pathManager.translatePath(lut)
		lutNode['file'].setValue(lut)

		lutNode['working_space'].setValue(lutWorkingSpace)

		print 'LUT Applied'
		print 'file:', self.getOption('lut')
		print 'working_space:', self.getOption('lutWorkingSpace')

	def applyColorTransform(self):
		colorTransform = self.getOption('colorTransform', 'None')
		applyShotColorNode = nuke.toNode('applyShotColor')

		try:
			applyShotColorNode['disable'].setValue(False)
			result = applyShotColorNode['colorTransform'].setValue(colorTransform)

			if result:
				print 'Converter: %s transform Applied!!' % colorTransform
		except:
			applyShotColorNode['colorTransform'].setValue('None')
			print 'Converter: Failed to apply: %s' % colorTransform

	def createScript(self):
		print 'Converter: createScript'

		# open the formats script
		nuke.scriptOpen(globalSettings.SHEPHERD_ROOT + 'assets/formats.nk')

		# get this early as it's used throughout
		self.useSlate = self.getOption('slate', True)

		self.createReadNodes()
		self.setIncomingColorspace()

		self.setFormat()

		self.setRanges()
		self.setWriteNode()
		self.setThumbnailNode()

		self.setSlate()
		self.applyCDL()
		self.applyLUT()
		self.applyColorTransform()

		nuke.root()['onScriptLoad'].setValue('')
		nuke.root()['onScriptSave'].setValue('')
		nuke.root()['onScriptClose'].setValue('')
		nuke.scriptSave(globalSettings.TEMP + 'imageConversion.nk')

	def execute(self, start=None, end=None):
		print 'Converter: Rendering frame range: %s-%s' % (self.startFrame, self.endFrame)
		nuke.execute(self.writeNode.name(), self.startFrame, self.endFrame)

		print 'Converter: Creating thumbnail'
		nuke.execute(self.thumbnailNode.name(), self.thumbnailFrame, self.thumbnailFrame)

		conversionDuration = self.endFrame - self.startFrame
		print 'Conversion Duration:', conversionDuration

if __name__ == '__main__':
	imageConverter = ImageConverter()
	imageConverter.parseArgs(sys.argv)
	imageConverter.createScript()
	imageConverter.execute()

# "C:/Program Files/Nuke9.0v6/Nuke9.0.exe" -V 2 -t C:/ie/ark/programs/nuke/python/imageConverter.py -options "{'outputColorspace': 'sRGB', 'codec': 'h264_low', 'inColorspace': 'AlexaV3LogC', 'output': 'C:/Trash/formats/test.mov', 'inputs': [{'file': 'c:/Trash/sequence/sequence.%04d.jpg'}], 'resize': .5, 'resizeType': 'width', 'fps': 23.976, 'handles': 5, 'startFrame': 1001, 'slateArtist': 'Tom Brady', 'slateJob': 'Patriots', 'slateVersion': '2015', 'slateShot': 'Superbowl', 'slateNotes': 'Good job', 'slateBurnIn': true, 'slateMaskOpacity': 0.5}"
# "C:/Program Files/Nuke9.0v6/Nuke9.0.exe" -V 2 -t C:/ie/ark/programs/nuke/python/imageConverter.py -options "{'outputColorspace': 'sRGB', 'codec': 'h264_low', 'inColorspace': 'AlexaV3LogC', 'output': 'C:/Trash/formats/test.mov', 'inputs': [{'file': 'c:/Trash/sequence/sequence.%04d.jpg'}, {'file': 'c:/Trash/sequence/sequence2.%04d.jpg'}, {'file': 'c:/Trash/sequence/sequence.%04d.jpg'}, {'file': 'c:/Trash/sequence/sequence2.%04d.jpg'}], 'reformat': {'value': '.5', 'resizeType': 'width'}, 'fps': 23.976, 'handles': 5, 'startFrame': 1001, 'slateBurnIn': true, 'slateVersion': '027', 'slateArtist': 'Tom Brady'}"
# "C:/Program Files/Nuke9.0v6/Nuke9.0.exe" -V 2 -t C:/ie/ark/programs/nuke/python/imageConverter.py -options "{'outputColorspace': 'sRGB', 'codec': 'jpg_75', 'inColorspace': 'AlexaV3LogC', 'output': 'C:/Trash/formats/seq/test.%04d.jpg', 'inputs': [{'file': 'c:/Trash/sequence/sequence.%04d2.jpg'}], 'reformat': {'value': '.5', 'resizeType': 'width'}, 'fps': 23.976, 'handles': 5, 'startFrame': 1001, 'slateArtist': 'Tom Brady', 'slateJob': 'Patriots', 'slateVersion': '2015', 'slateShot': 'Superbowl', 'slateNotes': 'Good job', 'slateBurnIn': true, 'slateMaskOpacity': 0.5}"
# "C:/Program Files/Nuke9.0v6/Nuke9.0.exe" -V 2 -t C:/ie/ark/programs/nuke/python/imageConverter.py -options "{'slate': false, 'outputColorspace': 'linear', 'codec': 'exr_16bit_piz', 'inColorspace': 'sRGB', 'output': 'C:/Trash/formats/exr/test.%04d.exr', 'inputs': [{'file': 'c:/Trash/sequence/sequence2.%04d.jpg'}], 'reformat': {'value': '.5', 'resizeType': 'width'}, 'fps': 23.976, 'handles': 5, 'startFrame': 1001, 'slateArtist': 'Tom Brady', 'slateJob': 'Patriots', 'slateVersion': '2015', 'slateShot': 'Superbowl', 'slateNotes': 'Good job', 'slateBurnIn': true, 'slateMaskOpacity': 0.5}"
# "C:/Program Files/Nuke9.0v6/Nuke9.0.exe" -V 2 -t C:/ie/ark/programs/nuke/python/imageConverter.py -options "{'outputColorspace': 'AlexaV3LogC', 'codec': 'prores_422HQ', 'inColorspace': 'sRGB', 'output': 'C:/Trash/formats/prores_422HQ.mov', 'inputs': [{'file': 'c:/Trash/sequence/sequence2.%04d.jpg'}], 'fps': 23.976, 'handles': 0, 'startFrame': 1001, 'slateArtist': 'Tom Brady', 'slateJob': 'Patriots', 'slateVersion': '2015', 'slateShot': 'Superbowl', 'slateNotes': 'Good job', 'slateBurnIn': true, 'slateMaskOpacity': 0.5}"
# "C:/Program Files/Nuke9.0v6/Nuke9.0.exe" -V 2 -t C:/ie/ark/programs/nuke/python/imageConverter.py -options "{'outputColorspace': 'AlexaV3LogC', 'codec': 'prores_444', 'inColorspace': 'sRGB', 'output': 'C:/Trash/formats/prores_444.mov', 'inputs': [{'file': 'c:/Trash/sequence/sequence2.%04d.jpg'}], 'fps': 23.976, 'handles': 0, 'startFrame': 1001, 'slateArtist': 'Tom Brady', 'slateJob': 'Patriots', 'slateVersion': '2015', 'slateShot': 'Superbowl', 'slateNotes': 'Good job', 'slateBurnIn': true, 'slateMaskOpacity': 0.5}"
# "C:/Program Files/Nuke9.0v6/Nuke9.0.exe" -V 2 -t C:/ie/ark/programs/nuke/python/imageConverter.py -options "{'outputColorspace': 'AlexaV3LogC', 'codec': 'prores_444', 'inColorspace': 'AlexaV3LogC', 'output': 'C:/Trash/formats/prores_444_realFootage.mov', 'inputs': [{'file': 'r:/Agent_X_s01/Workspaces/AGX_104/AGX104_001_020/Plates/v001/AGX104_001_020_A_alexaLog.%04d.dpx'}], 'fps': 23.976, 'handles': 0, 'startFrame': 1001, 'slateArtist': 'Tom Brady', 'slateJob': 'Patriots', 'slateVersion': '2015', 'slateShot': 'Superbowl', 'slateNotes': 'Good job', 'slateMaskOpacity': 0.5}"
# "C:/Program Files/Nuke9.0v6/Nuke9.0.exe" -V 2 -t C:/ie/ark/programs/nuke/python/imageConverter.py -options "{'slate': false, 'outputColorspace': 'AlexaV3LogC', 'codec': 'prores_444', 'inColorspace': 'AlexaV3LogC', 'output': 'C:/Trash/formats/prores_444_realFootage_noSlate.mov', 'inputs': [{'file': 'r:/Agent_X_s01/Workspaces/AGX_104/AGX104_001_020/Plates/v001/AGX104_001_020_A_alexaLog.%04d.dpx'}], 'fps': 23.976, 'handles': 0, 'startFrame': 1001, 'slateArtist': 'Tom Brady', 'slateJob': 'Patriots', 'slateVersion': '2015', 'slateShot': 'Superbowl', 'slateNotes': 'Good job', 'slateMaskOpacity': 0.5}"
# "C:/Program Files/Nuke9.0v6/Nuke9.0.exe" -V 2 -t C:/ie/ark/programs/nuke/python/imageConverter.py -options "{'outputColorspace': 'AlexaV3LogC', 'codec': 'prores_444', 'inColorspace': 'AlexaV3LogC', 'output': 'C:/Trash/formats/prores_444_blackish_noSlate.mov', 'inputs': [{'file': 'R:/Black-ish_s01/Workspaces/BLA_108_03_040/Plates/BLA_108_03_040_Left_Alexa.%04d.dpx'}], 'fps': 23.976, 'handles': 0, 'startFrame': 1001, 'slateArtist': 'Tom Brady', 'slateJob': 'Patriots', 'slateVersion': '2015', 'slateShot': 'Superbowl', 'slateNotes': 'Good job', 'slateMaskOpacity': 0.5}"
# "C:/Program Files/Nuke9.0v6/Nuke9.0.exe" -V 2 -t C:/ie/ark/programs/nuke/python/imageConverter.py -options "{'outputColorspace': 'AlexaV3LogC', 'codec': 'prores_444', 'inColorspace': 'AlexaV3LogC', 'output': 'C:/Trash/formats/prores_444_blackish_noSlate.mov', 'inputs': [{'file': 'R:/Black-ish_s01/Workspaces/BLA_108_03_040/Plates/BLA_108_03_040_Left_Alexa.%04d.dpx'}], 'fps': 23.976, 'handles': 0, 'startFrame': 1001, 'slateArtist': 'Tom Brady', 'slateJob': 'Patriots', 'slateVersion': '2015', 'slateShot': 'Superbowl', 'slateNotes': 'Good job', 'slateMaskOpacity': 0.5, 'slateBurnIn': true}"
# "C:/Program Files/Nuke9.0v6/Nuke9.0.exe" -V 2 -t C:/ie/ark/programs/nuke/python/imageConverter.py -options "{'outputColorspace': 'AlexaV3LogC', 'codec': 'prores_444', 'inColorspace': 'sRGB', 'output': 'C:/Trash/formats/prores_444.mov', 'inputs': [{'file': 'c:/Trash/sequence/sequence2.%04d.jpg'}], 'fps': 23.976, 'handles': 0, 'startFrame': 1001, 'slateArtist': 'Tom Brady', 'slateJob': 'Patriots', 'slateVersion': '2015', 'slateShot': 'Superbowl', 'slateNotes': 'Good job', 'slateBurnIn': true, 'slateMaskOpacity': 0.5}"
