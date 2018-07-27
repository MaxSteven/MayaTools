# python

import modo
import math
import lx
import re

import traceback

# RUNNING FROM COMMAND LINE:
# Call the command on the following line EXACTLY (without of course the Python comment hashtag)
# modo.exe "-cmd:@C:/ie/ark/tools/objScreenshot/firstModoscript.py <filename> <destname> JPG"
# Notes: for some reason the quotes need to start before the -cmd flag
# any of these arguments will need to be curlybraced if they include spaces e.g. {C:/Sports & Hobbies/thing.obj}
# Currently these args are parsed in THIS script. Ideally Modo would do this but their args parsing makes like
# zero sense. Also this doesn't yet work with modo_cl

def main():
	args = re.findall('\[[^\]]*\]|{[^\}]*\}|\"[^\"]*\"|\S+',lx.arg())
	print('args are', args)
	print('args from modo are', lx.args())
	args = [x.strip('{}""') for x in  args]
	fileName = args[0]
	dest = args[1]
	fileFormat = args[2] if args>2 else None
	makeScreenShot(fileName, dest, fileFormat)

def makeScreenShot(fileName, imagePath, fileFormat='JPG'):
	'''
		Makes a JPG screenshot of fileName and saves it at imagePath.
	'''

	print('got here with args', fileName, imagePath, fileFormat)

	#First load correct loaderOptions
	if fileName.endswith('abc'):
		lx.eval('loaderOptions.Alembic false false false false true 0.0 2')
	elif fileName.endswith('fbx'):
	 	lx.eval('loaderOptions.fbx false true false false false false false false false false false false false false 0')
	elif fileName.endswith('obj'):
	 	lx.eval('loaderOptions.wf_OBJ false false true')

	scene = modo.Scene()

	# Start with a clean slate for cameras and meshes
	for camera in scene.items('camera'):
		scene.removeItems(camera)
	for mesh in scene.items('mesh'):
			scene.removeItems(mesh)

	# Import the mesh and place a camera
	lx.eval('!!scene.open "%s" import' % fileName)
	scene.addCamera('Preview')
	previewCam = scene.camera('Preview')
	scene.select(previewCam)

	print('import')


	#Find the outer limits of the bounding boxes
	bboxes = [item.geometry.boundingBox for item in scene.items('mesh')]
	def absoluteMin(posn, iterable):
		return min(l[0][posn] for l in iterable)

	def absoluteMax(posn, iterable):
		return max(l[1][posn] for l in iterable)

	bbox = ([absoluteMin(i, bboxes) for i in range(3)], [absoluteMax(i, bboxes) for i in range(3)])

	# Figure out what the smallest edge is to get a sense of most important bounding box side
	# Also keep track of the scale that the object is at its max
	deltas = [bbox[1][i]- bbox[0][i] for i in range(3)]
	smallestEdge = deltas.index(min(deltas))
	longestEdge = max(deltas)


	print('bbox')


	# Place camera proportional to dimensions of mesh
	posnVector = [bbox[0][i]+0.6*deltas[i] for i in range(len(bbox[0]))]
	posnVector[smallestEdge] += 2*longestEdge

	previewCam.position.set((posnVector))
	#Set field of view: technically some crazy expression but realistically 50 works mostly
	#	if deltas[smallestEdge] > 0:
	#		hfov = 2.5* math.atan(longestEdge/(4*deltas[smallestEdge]))*180/math.pi
	hfov = 50
	lx.eval('camera.hfov %s' % hfov)


	#Figure out where the camera should be pointed to
	# Broken up in two movements: a rotateY and a rotateX
	targetVector = [bbox[0][i]+0.5*deltas[i] for i in range(3)]

	direction = [targetVector[i] - posnVector[i] for i in range(3)]
	lenDirection = math.sqrt(sum(x**2 for x in direction))
	unitDir = [x/lenDirection for x in direction]

	projectedUnitDir = [unitDir[0], 0, unitDir[2]]
	length = math.sqrt(sum(x**2 for x in projectedUnitDir))
	projectedUnitDir = [x/length for x in projectedUnitDir]

	rotateY = math.acos(-projectedUnitDir[2]) #used to ahve minus

	dotProd = sum(unitDir[i]*projectedUnitDir[i] for i in range(3))
	rotateX = math.acos(dotProd)
	if unitDir[1] <0:
		rotateX = -rotateX

	previewCam.rotation.set((rotateX, rotateY, 0))


	print('camera')


	#Set environment to invisible
	for environment in scene.items(modo.constants.ENVIRONMENT_TYPE):
		environment.channel('visCam').set(False)

	#Set render options
	lx.eval('render.res axis:1 res:200')
	lx.eval('render.res axis:0 res:200')
	scene.select('Render')

	cmd = 'item.channel outPat <none>'
	lx.eval(cmd)

	lx.eval('render fileName:"%s" format:%s' % (imagePath, fileFormat))

	print('render')

	# close the scene and quit
	# lx.eval('!!scene.close')
	# lx.eval('!!app.quit')
	# sys.exit(0)

try:
	main()
except:
	print traceback.format_exc()

