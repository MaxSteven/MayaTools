#python
#
# LoadImageMap
#
# Author: Mark Rossi
# Version: .4
# Compatibility: Modo 501/601
# Purpose: To load image maps into the shader tree and to control some of their visibility properties.
#
# Use: The script takes six arguments. The first two are mandatory: the name of the UV map, and the path of the image file. The order of these
#      arguments matters and they should be enclosed in quotation marks. When providing the file path, you can use any of the built-in modo aliases
#      that are listed in the dialog that appears when you run the script with the ? argument: @loadImageMap.py ?
#      You can also use a kit alias by prefixing the kit name with 'kit_'. If you don't use aliases then you must provide the absolute filename path.
#
#      The other three arguments are optional: swap, top, and shade. If you use swap then the script will look for an existing image map using
#      the specified file, and if one is found then it will be moved to the top of the shader tree. If you use top, then if the script creates
#      an image map item it will be placed at the top of the shader tree instead of in the sub-hierarchy of the current shader-tree selection. The
#      shade argument can be used to change the shading mode of all visible 3d viewports: wire (Wireframe), sket (Solid), vmap (Vertex Map),
#      shade (Shaded), tex (Texture), texmod (Shaded Texture), advgl (AdvancedOpenGL), shd1 (Gooch Tone), shd2 (Cel Shading), shd3 (Reflection).
#
# For example: @loadImageMap.py 'Texture' 'C:\My Images\image001.tga' swap top shade:advgl
#              @loadImageMap.py 'Unwrap' 'user:\Textures\tex.png'
#              @loadImageMap.py 'Bary' 'project:\images\scale01.tiff'
#              @loadImageMap.py 'UVMap' 'kit_myKitName:\clips\test.gif'
import os
import sys

import lx

def selMode():
	modes = ('vertex', 'edge', 'polygon', 'ptag', 'item', 'pivot', 'center')
	tests = (';'.join(modes[i:] + modes[:i]) for i in range(len(modes)))
	for m in modes:
		if lx.eval('select.typeFrom %s ?' %tests.next()): return m

def lxMSG(type, title, msg):
	lx.eval('dialog.setup %s' %type)
	lx.eval('dialog.title {%s}' %title)
	lx.eval('dialog.msg {%s}' %msg)
	lx.eval('dialog.open')
	sys.exit({'info':'LXe_OK', 'error':'LXe_ABORT'}[type])

def getClip():
	match = path.lower()
	for c in xrange(lx.eval('query layerservice clip.N ? all')):
		if lx.eval('query layerservice clip.file ? %s' %c).lower() == match:
			return lx.eval('query layerservice clip.name ? %s' %c)

args = lx.args()

if args[0] == '?':
	aliases = ' \n '.ljust(21, ' ') + '\n'.ljust(20, ' ').join(lx.evalN('query platformservice paths ?')) + '\n '
	lxMSG('info', 'LoadImageMap Help', 'These built-in aliases can be used \nto provide an image filename:\n%s' %aliases)

if len(args) < 2:
	lxMSG('error', 'Missing Arguments', 'You must provide both a UV map name and an image filename, in that order. Aborting.')

uvmap = args[0]
path  = os.path.normpath(args[1])
swap  = 'swap' in args
top   = 'top' in args
shade = [a[6:] for a in args[2:] if 'shade:' in a]

if ':' in path:
	root, path = path.split(':')
	path =  ''.join((lx.eval('query platformservice path.path ? %s' %root), path)) if root in lx.evalN('query platformservice paths ?') else \
			''.join((lx.eval('query platformservice alias ? {%s:}' %root), path))  if root[:4] == 'kit_' else \
		   ':'.join((root, path))

if not os.path.exists(path): lxMSG('error', 'File Not Found', 'The specified file cannot be found. Aborting.')

clip  = getClip()
smode = selMode()
done  = 0

layer = lx.eval('query layerservice layer.index ? main')
scene = lx.eval('query sceneservice scene.index ? main')
focus = lx.evalN('query sceneservice selection ? textureLayer')
items = lx.evalN('query sceneservice selection ? locator')

if shade:
	for w in xrange(lx.eval('query view3dservice view.N ?')):
		if lx.eval('query view3dservice view.type ? %s' %w) == 'MO3D':
			lx.eval('select.viewport set frame:%s viewport:%s' %lx.evalN('query view3dservice view.frame ? %s' %w))
			lx.eval('view3d.shadingStyle %s' %shade[0])

if swap and clip:
	for i in xrange(lx.eval('query sceneservice imageMap.N ?')):
		lx.eval('select.item %s set' %lx.eval('query sceneservice imageMap.id ? %s' %i))
		if lx.eval('texture.setImap ?') == clip:
			lx.eval('texture.parent Render -1')
			done = 1
			break

if not done:
	lx.eval('select.item Render set')
	lx.eval('shader.create constant')
	lx.eval('item.setType imageMap textureLayer')

	imap = lx.eval1('query sceneservice selection ? imageMap')
	for i in xrange(lx.eval('query layerservice texture.N ?')):
		if lx.eval('query layerservice texture.id ? %s' %i) == imap:
			lx.eval('select.subItem %s set' %lx.eval('query layerservice texture.locator ? %s' %i))
			break

	if top: lx.eval('texture.parent Render -1')
	else:
		if focus:
			focus  = focus[-1]
			parent = lx.eval('query sceneservice item.parent ? %s' %focus)
			index  = lx.evalN('query sceneservice item.children ? %s' %parent).index(focus) + 1
			lx.eval('texture.parent %s %s' %(parent, index))
		else:
			lx.eval('texture.parent Render 0')

	if clip: lx.eval('texture.setImap {%s}' %clip)
	else:
		lx.eval('clip.addStill {%s}' %path)
		clip = getClip()
		lx.eval('texture.setImap {%s}' %clip)

	lx.eval('texture.setProj uv')
	lx.eval('texture.setUV {%s}' %uvmap)

for i in items: lx.eval('select.item {%s} add' %i)
lx.eval('select.item {%s} set mediaClip' %clip)
lx.eval('select.type %s' %smode)
