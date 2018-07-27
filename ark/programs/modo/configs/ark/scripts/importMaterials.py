# python

import os
import re
import ConfigParser
import StringIO

import lx
lx.eval('log.masterClear')

import initModo
initModo.init()

import arkModo
import cOS

matRoot = "Q:/Assets/MODELS/MODELS_V2/Humans/Materials/"
encoding = 'utf-16'

uvMapName = 'UVChannel_1'

mats = arkModo.getSelectedTextureLayers()
for m in mats:
	lx.out('Processing:', m)
	arkModo.selectItem(m)

	index = arkModo.getItemIndex(m, 'mask', 'id')
	lx.out('index:', index)

	name = arkModo.getAttributeByIndex('name', index, 'mask')
	name = re.sub(r' \(.+\)', '', name)

	matFile = matRoot + name + '.ini'
	lx.out(matFile)
	# lx.out('Exists:', os.path.exists(matFile))
	config = ConfigParser.RawConfigParser()
	try:
		iniString = open(matFile, 'r').read()
	except IOError:
		lx.out('Mat file not found:', matFile)
		continue

	if encoding:
		iniString = iniString.decode(encoding)
	iniFilePointer = StringIO.StringIO(iniString)
	config = ConfigParser.RawConfigParser()
	config.readfp(iniFilePointer)

	for item in config.items('Textures'):
		lx.out('layer:', item[0], 'path:', cOS.unixPath(item[1]))

		imagePath = cOS.unixPath(item[1])

		lx.eval('shader.create constant')
		lx.eval('item.setType imageMap textureLayer')

		lx.eval('clip.addStill {%s}' % imagePath)
		clip = arkModo.getClipByFilename(imagePath)
		lx.eval('texture.setImap {%s}' % clip)

		lx.eval('texture.setProj uv')
		lx.eval('texture.setUV {%s}' % uvMapName)


# 	# arkModo.selectItem(m)

# # matFile = 'Q:/Assets/MODELS/MODELS_V2/Humans/Materials/Man012_Black_Slacks_GEO002__skin.ini'
# # # matFile = 'Q:/Assets/MODELS/MODELS_V2/Humans/Materials/wtf.txt'
# # # config = ConfigParser.RawConfigParser()
# # # config.read(matFile)

# # # for item in config.items('args'):
# # # 	print item

# # import binascii

# # with open(matFile) as f:
# # 	# c = f.read(45)
# # 	# while c:
# # 	# print('Contents:', binascii.b2a_uu(c))
# # 	# print('Contents:', f.read().decode('utf-16'))
# # 	# print('Contents:', f.read())
# # 	# print('Contents:', 'tits'.decode('utf-16'))
# # 		# c = f.read(45)
