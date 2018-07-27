# python

import re

import lx
import lxu
import lxu.select



# query sceneservice ' ?
# list all scene query operations

# query sceneservice types ?
# list all scene query types


def getSelectionMode():
	modes = ('vertex', 'edge', 'polygon', 'ptag', 'item', 'pivot', 'center')
	tests = (';'.join(modes[i:] + modes[:i]) for i in range(len(modes)))
	for m in modes:
		if lx.eval('select.typeFrom %s ?' % tests.next()):
			return m

def getCurrentLayer():
	'''
	No clue what 'layer' this refers to
	'''
	return lx.eval('query layerservice layer.index ? main')

def getCurrentScene():
	return lx.eval('query sceneservice scene.index ? main')

def getSelectedObjects():
	return lx.evalN('query sceneservice selection ? locator')

def getSelectedTextureLayers():
	return lx.evalN('query sceneservice selection ? textureLayer')

def selectItemByName(name, mode='set', itemType=None):
	# if itemType:
	return lx.eval('select.item {'+ name + '} ' + mode)

# expect a modo td api item
def getParent_TDAPI(item):
	return item.itemGraph('parent').connectedItems['Forward'][0]

# expect a modo td api item
def getChildren_TDAPI(item):
	return item.itemGraph('parent').connectedItems['Reverse']



# def getNodesByName(name):
# 	foundNode = False
# 	nodeCount = lx.eval1('query sceneservice camera.N ?')
# 	for n in range(nodeCount):
# 		cameraName = lx.eval1('query sceneservice camera.name ? ' + str(n))
# 		if cameraName == args['camera']:
# 			foundNode = True
# 			cameraID = lx.eval1('query sceneservice camera.id ? ' + str(n))
# 			cmd = 'render.camera ' + cameraID
# 			lx.out(cmd)
# 			lx.eval(cmd)
# 	if not foundNode:
# 		raise Exception('Node not found...honestly people')


def getItemsOfType(itemTypes):
	'''
	Returns all items of the specified type(s) as a list of Modo Python objects.
	Returns an empty list if no such items are found.

	Types:
	ADVANCEDMATERIAL, AREALIGHT, AUDIOCLIP, AUDIOFILE, BACKDROP, BEZIER, CAMERA,
	CAPSULE, CELLULAR, CELSHADER, CHECKER, CONSTANT, CURVE, CURVECONSTRAIN, CV,
	CYLINDERLIGHT, DEFAULTSHADER, DEFORM, DEFORMFOLDER, DEFORMGROUP, DOMELIGHT,
	DOTS, EDGETRANSSHADER, ENVIRONMENT, ENVMATERIAL, ENVSHADER, FALLOFF, FORCE,
	FURMATERIAL, FXSHADER, GENINFLUENCE, GLDRAW, GLOWSHADER, GLOWSHADER_BASEISOTROPY,
	GLOWSHADER_BASEROUGHNESS, GLOWSHADER_COATISOTROPY, GLOWSHADER_COATROUGHNESS,
	GLOWSHADER_GLOWAMP, GLOWSHADER_GLOWSIZE, GLOWSHADER_LAYERS, GRADIENT, GRID,
	GROUP, GROUPLOCATOR, IBLURFILTER, IBRIGHTFILTER, IGAMMAFILTER, IK2DLIMB,
	IMAGEFILTER, IMAGEMAP, ITEMINFLUENCE, LIGHT, LIGHTMATERIAL, LOCATOR, LOCDEFORM,
	MAPMIX, MASK, MDD, MDD2, MEDIACLIP, MESH, MESHINST, MORPHDEFORM, MORPHMIX,
	MULTIPARTICLE, NOISE, ORDEREDPARTICLE, PARTICLEOP, PHOTOMETRYLIGHT, PLOAD,
	POINTLIGHT, POLYRENDER, PROCESS, PROXY, PSIM, QUATERNION, RENDER, RENDEROUTPUT,
	REPLICATOR, ROTATION, SCALE, SCENE, SCHLICKSHADER, SHEAR, SINGLEPARTICLE,
	SPOTLIGHT, SUNLIGHT, TARGET, TEXTURELAYER, TEXTURELOC, TRANSFORM, TRANSLATION,
	TRISURF, UISTATE, VIDEOCLIP, VIDEOSEQUENCE, VIDEOSTILL, VMAPTEXTURE, VOLUME,
	WEIGHTCONTAINER, WOOD, XFRMCORE
	'''

	items = []
	sceneService = lx.service.Scene()
	scene = lxu.select.SceneSelection().current()

	for itemType in itemTypes:
		if isinstance(itemType, str):
			try:
				typeLookup = sceneService.ItemTypeLookup(itemType)
			except LookupError:
				raise LookupError('Item Type: %s not recognized' % itemType)
		elif isinstance(itemType, int):
			typeLookup = itemType
		else:
			continue

		itemCount = scene.ItemCount(typeLookup)
		items.extend((scene.ItemByIndex(typeLookup, n) for n in xrange(itemCount)))

	return items

def getNodesByName(name, itemType=-1):
	scene = lxu.select.SceneSelection().current()
	itemCount = scene.ItemCount(itemType)

	items = []
	for i in range (itemCount):
		item = scene.ItemByIndex(itemType, i)
		# if re.match(name, item.UniqueName()):
		# if name == item.UniqueName() or name == item.Name():
		if name == item.Name():
			items.append(item)

	return items

	# alt, non pythonic way

def getItemIndex(name, itemType='item', nameAttribute='name'):
	'''
	itemType:

	locator, mesh, light, camera, render, environment, textureLayer, transform,
	translation, rotation, dfrmcore, shader, scene, shaderFolder, advancedMaterial,
	mask, defaultShader, renderOutput, polyRender, lightMaterial, envMaterial, sunLight

	nameAttribute:

	name: normal object name
	id: uniqueName, what Modo uses internally (SUCKS!)

	'''

	numItems = lx.eval('query sceneservice %s.n ?' % itemType)
	for n in range (numItems):
		testName = lx.eval('query sceneservice %s.%s ? %s' % (itemType, nameAttribute, n))
		lx.out('name:', testName)
		testName = re.sub(r' \([A-Za-z]+\)', '', testName)
		lx.out('checking:', testName)
		if name == testName:
			return n


def getAttributeByIndex(attribute, index, itemType='item'):
	'''
	itemType:

	locator, mesh, light, camera, render, environment, textureLayer, transform,
	translation, rotation, dfrmcore, shader, scene, shaderFolder, advancedMaterial,
	mask, defaultShader, renderOutput, polyRender, lightMaterial, envMaterial, sunLight

	nameAttribute:

	name: normal object name
	id: uniqueName, what Modo uses internally (SUCKS!)

	'''

	return lx.eval('query sceneservice %s.%s ? %s' % (itemType, attribute, index))

def getChildren(name, itemType='item', nameAttribute='name'):
	'''
	itemType:

	scene, types, isType, selection, tags, pureLocators, graph, fwdLink, revLink,
	actionItem, cinema, channel, key, item, light, clip, locator, txLayer, deformer,
	group , pass, actor, proxy
	'''

	# itemID = lx.eval("query sceneservice %s.id ? %s" % (itemType, index)
	if isinstance(name, int):
		itemIndex = name
	else:
		itemIndex = getItemIndex(name, itemType, nameAttribute)

	lx.out(itemIndex)
	# itemID = getAttributeByIndex('id', itemIndex, itemType)
	# itemName = getAttributeByIndex('name', itemIndex, itemType)
	children = getAttributeByIndex('children', itemIndex, itemType)
	# if children:
	# 	for c in children:
	# 		lx.out(c)

	return children

	# name = lx.eval("query sceneservice txLayer.name ? %s" % i)
	# parent = lx.eval("query sceneservice txLayer.parent ? %s" % i)
	# children = lx.evalN("query sceneservice txlayer.children ? %s" % i)
	# lx.out("txLayer %s : id=%s <> name=%s <> parent=%s" % (i, id, name, parent))
	# for c in children:
	# 		lx.out(c)

def getClipByFilename(filename):
	filename = filename.lower()
	for c in xrange(lx.eval('query layerservice clip.N ? all')):
		if filename == lx.eval('query layerservice clip.file ? %s' % c).lower():
			return lx.eval('query layerservice clip.name ? %s' % c)


def getRenderItem():
	return lx.eval('query sceneservice polyRender.id ? 0')

def setChannelValue(item, channel, value):
	lx.out('channel.value value:%s channel:{%s:%s}' % (value, item, channel))
	return lx.eval('channel.value value:%s channel:{%s:%s}' % (value, item, channel))

if __name__ == '__main__':
	lx.eval('log.masterClear')

	objs = getSelectedObjects()

	# lx.out('getSelectionMode():')
	# lx.out(getSelectionMode())

	# lx.out('getCurrentLayer():')
	# lx.out(getCurrentLayer())

	# lx.out('getCurrentScene():')
	# lx.out(getCurrentScene())

	# lx.out('getSelectedTextureLayers():')
	# lx.out(getSelectedTextureLayers())
	# textures = getSelectedTextureLayers()
	# for tex in textures:
	# 	lx.out(tex)
	# 	index = getItemIndex(tex, 'mask', 'id')
	# 	# lx.out(index)
	# 	# name = getAttributeByIndex('name', index, 'mask')
	# 	# lx.out('name:', name)
	# 	kids = getChildren(index, 'mask')
	# 	selectItemByName(tex)
	# 	const = lx.eval('shader.create constant')
	# 	lx.out(const)
	# 	# for k in kids:
	# 	# 	index = getItemIndex(tex, 'mask', 'id')




	# # selectItemByName('Render')

	# # meshItem = getNodesByName('Mesh')
	# # lx.out(meshItem)

	# # help(meshItems[0])

	# # lx.out('getSelectedObjects():')
	# # lx.out(getCurrentScene())

	# renderItem = getRenderItem()

	# # always use animated noise
	# setChannelValue(renderItem, 'animNoise', 'true')
	# # no render region
	# setChannelValue(renderItem, 'region', 'false')
