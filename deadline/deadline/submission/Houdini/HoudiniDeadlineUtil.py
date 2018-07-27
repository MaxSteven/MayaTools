import os
import arkInit
arkInit.init()

import translators
translator = translators.getCurrent()

import cOS

import hou

import settingsManager
globalSettings = settingsManager.globalSettings()

def IE_SubmitJobsToDeadline(nodes):
	import IE_SubmitDeadlineRop

	nodes = setParameters(nodes)

	hou.hipFile.save()

	IE_SubmitDeadlineRop.SubmitToDeadline()

def setParameters(nodes):
	if not len(nodes):
		print 'no nodes found'
		return

	currentFile = translator.getFilename()
	currentDir = cOS.getDirName(currentFile)
	version = str(cOS.getVersion(currentFile)).zfill(4)
	wedgeNodes = [wNode for wNode in nodes if wNode.type().name() == 'ie_customwedge']
	ignoreNodes = []
	if len(wedgeNodes):
		for wNode in wedgeNodes:
			wedgeNodeInputs = wNode.inputAncestors()
			ignoreNodes.extend([node for node in wedgeNodeInputs])
			setAncestors(wNode, wedgeNodeInputs)

	for node in nodes:
		name = node.type().name()
		if node not in ignoreNodes and not node.isLocked():
			if 'ifd' in name:
				node.parm('vm_picture').set(
						setPaths(node, folder='renders', version=version, render=True, wedge=None, ext='exr', trashPath=False))
				node.parm('soho_diskfile').set(
						setPaths(node, folder='ifds', version=version, render=True, wedge=None, ext='ifd.sc', trashPath=False))
				node.parm('vm_dcmfilename').set(
						setPaths(node, folder='renders', version=version, render=True, wedge=None, ext='exr', trashPath=False, deep=True))
				node.parm('soho_outputmode').set(True)
				node.parm('soho_mkpath').set(True)

			elif 'geometry' in name:
				node.parm('mkpath').set(True)

			elif 'alembic' in name:
				node.parm('render_full_range').set(False)
				node.parm('mkpath').set(True)

			elif 'cacheRop' in name:
				extension = node.parm('ext').evalAsString()
				trash = node.parm('cache_to_trash').eval()
				node.parm('filename').lock(0)
				node.parm('filename').set(
					setPaths(node, ext=extension, wedge=None, trashPath=trash))
				node.parm('filename').lock(1)

			elif 'cacheAlembicRop' in name:
				s = node.parm('is_sim').evalAsString()
				trash = node.parm('cache_to_trash').eval()
				node.parm('filename').lock(0)
				node.parm('filename').set(
					setPaths(node, single=s, wedge=None, ext='abc', trashPath=trash))
				node.parm('filename').lock(1)

			elif 'customGeo' in name:
				print 'custom Geo'

	return nodes

def setAncestors(root, nodes):
	if not len(nodes) or not root.type().name() == 'ie_customwedge':
		return

	for node in nodes:
		name = node.type().name()

		if 'ifd' in name:
			version = cOS.getVersion(translator.getFilename())
			node.parm('vm_picture').set(
				setPaths(node, folder='renders', version=version, render=True, wedge=root, ext='exr', trashPath=False))
			node.parm('soho_diskfile').set(
				setPaths(node, folder='ifds', version=version, render=True, wedge=root, ext='ifd.sc', trashPath=False))
			node.parm('soho_outputmode').set(True)
			node.parm('soho_mkpath').set(True)

		elif 'cacheRop' in name:
			extension = node.parm('ext').evalAsString()
			trash = node.parm('cache_to_trash').eval()

			node.parm('filename').lock(0)
			node.parm('filename').set(
				setPaths(node, ext=extension, wedge=root, trashPath=trash))
			node.parm('filename').lock(1)

		elif 'cacheAlembicRop' in name:
			s = node.parm('is_sim').evalAsString()
			trash = node.parm('cache_to_trash').eval()

			node.parm('filename').lock(0)
			node.parm('filename').set(
				setPaths(node, single=s, wedge=root, ext='abc', trashPath=trash))
			node.parm('filename').lock(1)

		elif 'customGeo' in name:
			print 'custom Geo'

		print node

def makeReadNode(node):
	parent = node.parent()
	# Make a new File SOP
	filenode = parent.createNode('file')
	filenode.moveToGoodPosition()
	filenode.setName('READ_{}'.format(node.name()))
	filenode.setColor(hou.Color(0.584, 0.776, 1))
	# Get the path
	fname = node.parm('sopoutput').eval()
	ext = node.parm('ext').eval()
	if node.parm('trange').eval() == 1:
		split = fname.split('.')
		if ext == 0 or ext == 1:
			split[-3] = '$F4'
		else:
			split[-2] = '$F4'
		s = '.'
		filenode.parm('file').set(s.join(split))
	else:
		filenode.parm('file').set(fname)

def autoversion(node):
	get_hip_version = node.parm("get_version")
	if get_hip_version == 1:
		hipname = hou.getenv('HIPNAME')
		v = ''.join([c for c in hipname if c.isdigit()])
		node.parm('v').set(v)

def checksaved():
	file = hou.hipFile
	if file.hasUnsavedChanges:
		hou.ui.displayMessage('Save before submitting!')

# Some global Vars
def setPaths(node, ext=None, folder='Publish', version=None, single=False, trashPath=True, wedge=None, render=False, deep=False):
	op = ''
	if node.parm('cacheName'):
		op = '`chs("cacheName")`'
	else:
		op = '`$OS`'

	# Current Frame only
	trange = node.parm('trange').eval()

	# Version
	currentFile = hou.hipFile.path()

	versionNumber = version or node.parm('version').eval()

	if versionNumber:
		v = 'v' + str(versionNumber).zfill(4)
	else:
		v = 'v0001'
	# Frame
	frame = int(hou.frame())

	# Extension
	if ext == None:
		parm = node.parm('ext')
		value = parm.eval()
		ext = parm.menuLabels()[value]

	# Remove the last task folder from path
	hip = os.path.dirname(hou.getenv('HIP'))

	f = folder
	if node.parm('is_publish'):
		if not node.parm('is_publish').eval():
			f = 'geo'

	# taskname = hou.getenv('TASKNAME')
	taskname = os.path.basename(hou.getenv('HIP'))
	taskOp = taskname
	if op:
		taskOp += '_' + op

	if wedge != None:
		w = 'wedgeNum_' + '`ch("{}")`'.format(wedge.parm('wedgeNum').path())
		taskOp = os.path.join(taskOp, w)

	if trashPath:
		hipParts = hip.partition('/')
		hip = 'r:/_trash/' + hipParts[-1]

	taskOpRange = taskOp
	if not render and single:
		if trange == 0:
			framerange = '`$F4`-`$F4`'
		else:
			framerange = '`ch("{}")`-`ch("{}")`'.format('f1','f2')

		taskOpRange = '{}_{}'.format(taskOpRange, framerange)

	vBase = v
	if deep:
		vBase += '.deep'


	# single frame
	if trange == 0 or single:
		basename = '{}_{}.{}'.format(taskOpRange, vBase, ext)
		basenameParticle = '{}_{}_particle.{}'.format(taskOpRange, vBase, ext)
	# sequences
	else:
		basename = '{}_{}.{}.{}'.format(taskOpRange, vBase, '$F4', ext)
		basenameParticle = '{}_{}_particle.{}.{}'.format(taskOpRange, vBase, '$F4', ext)

	path = os.path.join(hip, f, taskOp, v, basename).replace('\\', '/')

	if node.parm('filename_particle'):
		particlePath = os.path.join(hip, f, taskOp, v, basenameParticle).replace('\\', '/')
		node.parm('filename_particle').set(particlePath)
	# Populate the parameter
	return path

def copyFromTrash(node):
	if not node:
		print 'No valid node'
		return False

	path = node.parm('filename').eval()

	if '_trash' not in path:
		print 'The node path is not in trash!'
		return False

	trange = node.parm('trange').eval()

	if trange != 0:
		lastFramePath = node.parm('filename').evalAsStringAtFrame(node.parm('f2').eval())
		if not os.path.exists(lastFramePath):
			print 'Last frame does not exist! Please wait for your render to finish'
			return False

	try:
		cacheDir = cOS.getDirName(path)
		publishDir = cacheDir.replace('_trash/', '')
		cOS.makeDirs(cOS.getDirName(publishDir))
		cOS.copyTree(cacheDir, publishDir)

		return True
	except Exception as e:
		print 'Unable to copy files from trash!'
		print e
		return False
