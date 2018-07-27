
# import sys
import os

from datetime import date

from Translator import Translator
from qt import QtGui
from qt import QtCore

import re

# ieTools
#-----------------------------------------------------------------------------
import arkInit
arkInit.init()

import cOS
# import ieCommon
import arkUtil
import settingsManager
globalSettings = settingsManager.globalSettings()

import caretaker
ct = caretaker.getCaretaker()
import hou
# import threading
import pyqt_houdini

class Houdini(Translator):

	keyDict = {
		'passNames': 1000
	}

	def __init__(self):
		super(Houdini, self).__init__()
		self.settings.append(canUse=True,
			renderNodeType='rop',
			hasFrames=True,
			hasPasses=True,
			hasDeep=True,
			hasKeyCommands=False,
			closeOnSubmit=False,
			singleArkInit=True,
			jobTypes=['Render'],
			# jobTypes=['Render', 'Cache'],
			appHandlesSubmit=False)

		self.nodeReplaceList= {}

	def getProgram( self):
		return( 'Houdini')

	# Data Storage
	########################################

	def setData(self, key, val=None):
		data = {}
		if val is None:
			if isinstance(key, dict):
				data = dict(key)
			else:
				data[key] = key
		else:
			data[key] = val

		for key, val in data.iteritems():
			obj = hou.node('/obj')
			obj.setUserData(str(self.keyDict[key]), val)

	def getData(self, key=None):
		fileInfo = hou.node('/obj').userDataDict()
		if key:
			if str(self.keyDict[key]) in fileInfo.keys():
				return fileInfo[str(self.keyDict[key])]
			return ''
		return fileInfo

	def removeData(self, key):
		hou.node('/obj').destroyUserData(str(self.keyDict[key]))

	# Nodes
	########################################
	def getNodesByType(self, nodeType):
		toReturn = []
		for n in hou.node('/').allSubChildren():
			if nodeType.lower() in str(type(n)).lower() or str(type(n)).lower() in nodeType.lower():
				toReturn.append(n.path())

		if len( toReturn) == 0:
			return False
		else:
			return toReturn

	# File Info
	########################################
	def getFilename(self):
		return hou.hipFile.path()

	def saveFile(self, fileName=None):

		if( fileName== None):
			hou.hipFile.save(self.getFilename())
		else:
			hou.hipFile.save( fileName)

	def openFile(self, fileName):
		hou.hipFile.load(fileName)

	def getFileInfo(self):
		fileInfo = {}

		fileName = self.getFilename()
		fileInfo['baseName'] = fileName.split('/')[-1].split('.')[0]
		# fileInfo['width'] = hou.node('/obj/ipr_camera').parm('resx').eval()
		# fileInfo['height'] = hou.node('/obj/ipr_camera').parm('resy').eval()
		# fileInfo['deviceAspectRatio'] = float(fileInfo['width']) / float(fileInfo['height'])
		fileInfo['fps'] = hou.expandString('$FPS')
		fileInfo['isStereo'] = False
		fileInfo['version'] = None

		fileInfo['pathInfo'] = ct.pathInfo(fileName)
		fileInfo['userInfo'] = ct.userInfo

		if 'project_info' in fileInfo['pathInfo'] and fileInfo['pathInfo']['project_info'] and fileInfo['pathInfo']['project_info']['short_name']:
			fileInfo['short_name'] = fileInfo['pathInfo']['project_info']['short_name']

		if (fileName):
			fileParts = fileName.split('/')
			if (len(fileParts) > 3 and fileParts[2].upper() == 'WORKSPACES'):
				fileInfo['shotName'] = fileParts[3]
			elif len(fileParts) > 3:
				fileInfo['shotName'] = fileParts[2] + '-' + fileParts[3]
			fileInfo['version'] = cOS.getVersion(fileName)

			fileInfo['version'] = arkUtil.pad(int(fileInfo['version']), 3)
			fileInfo['jobName'] = fileParts[1]

			fileInfo['jobRoot'] = globalSettings.SHARED_ROOT + fileInfo['jobName'] + '/'
			today = date.today()

			fileInfo['postingRoot'] = fileInfo['jobRoot'] + 'POSTINGS/' + str(today.year) + '_' + arkUtil.pad(today.month, 2) + '_' + arkUtil.pad(today.day, 2) + '/'

		fileInfo['startFrame'] =  hou.playbar.playbackRange()[0]
		fileInfo['endFrame'] = hou.playbar.playbackRange()[1]
		fileInfo['frameCount'] = fileInfo['endFrame'] - fileInfo['startFrame']

		return fileInfo

	def isFileDirty(self):
		return hou.hipFile.hasUnsavedChanges()

	def saveIncrementWithInitials(self):
		if not ct.userInfo or 'initials' not in ct.userInfo:
			return

		newScript = self.getFilename()[:-6] + ct.userInfo['initials'] + '.nk'
		newScript = cOS.incrementVersion(newScript)

		hou.hipFile.save(newScript)

	# Rendering
	########################################
	def getDefaultJobName(self):
		self.getFilename().split('/')[-1][:-4]

	def getRenderProperties(self, node):
		if node and hou.node(node).parm('camera'):
			node = hou.node(node)
			try:
				properties = {
						'width': hou.node(node.parm('camera').eval()).parm('resx').eval(),
						'height': hou.node(node.parm('camera').eval()).parm('resy').eval(),
						'startFrame':  hou.playbar.playbackRange()[0],
						'endFrame': hou.playbar.playbackRange()[1],
						'shadingLevel': '%sx%s' % (node.parm('vm_samplesx').eval(), node.parm('vm_samplesy').eval()),
						'shading_level': '%sx%s' % (node.parm('vm_samplesx').eval(), node.parm('vm_samplesy').eval()),
						'program': 'hip',
						'jobType': 'Houdini_Mantra'
						}
				return properties

			except:
				return False

		return {
				'startFrame':  hou.playbar.playbackRange()[0],
				'endFrame': hou.playbar.playbackRange()[1],
				'program': 'hip',
				'jobType': 'Houdini_Cache',
				'hasFrames': False,
				'single_node': True
			}

	def getOutputFilename(self, outputRoot, jobData):
		print 'jobType:', jobData['jobType'], jobData['jobType'] == 'Houdini_Cache'
		if jobData['jobType'] == 'Houdini_Cache':
			print 'returning:', hou.node(jobData['node']).parm('sopoutput').unexpandedString()

			try:
				result= hou.node(jobData['node']).parm('sopoutput').unexpandedString()
				return result

			except:
				return False
		else:
			return outputRoot + ('/renders/v%03d/' % jobData['version']) + \
						jobData['name'] + '.%04d.exr'

	def setOutputFilename(self, outputFile, jobData):
		outputFile = outputFile.replace('%04d','$F4')
		print 'node:', jobData['node']
		print 'OutputFile:', outputFile
		print type(jobData['node'])
		print type(outputFile)

		if jobData['jobType'] == 'Houdini_Cache':
			ropNode = hou.node(str(jobData['node']))
			ropNode.parm('sopoutput').set(str(outputFile))

		elif jobData['deep']:
			hou.node(str(jobData['node'])).parm('vm_picture').set(str(outputFile))
			hou.node(str(jobData['node'])).parm('vm_deepresolver').set('camera')
			deepFilename = str(outputFile).replace('.$F4.exr','_deep.$F4.exr')
			hou.node(str(jobData['node'])).parm('vm_dcmfilename').set(deepFilename)
		else:
			hou.node(str(jobData['node'])).parm('vm_picture').set(str(outputFile))

	# Pre's
	########################################
	def preRender(self):
		pass

	def preSubmit(self, jobData):
		hou.setSessionModuleSource('')
		hipPath = os.path.dirname(hou.hipFile.path())
		hipPath = re.sub(r'[\\/]+', '/', hipPath)

		for node in hou.node('/').allSubChildren():
			for parm in node.parms():
				try:
					val = str(parm.unexpandedString())
					if '$HIP' in val:
						print 'replacing $HIP:', val
						parm.set(val.replace('$HIP', hipPath))
						self.nodeReplaceList[ node]= hipPath
				except:
					pass

		self.saveFile()

	def postSubmit( self, jobData):
		for node, hipPath in self.nodeReplaceList.items():
			for parm in node.parms():
				try:
					val = str(parm.unexpandedString())
					if hipPath in val:
						print 'replacing {}:'.format( hipPath), val
						parm.set(val.replace(hipPath, '$HIP'))
				except:
					pass

	def renderSetup(self, jobData):
		pass
# 		sys.path.append(globalSettings.SHEPHERD_ROOT)
# 		import submit
# 		return submit.submitJob(jobData)


# # 		# export .IFD's
# # 		# for framePair in jobData['framerange'].split(','):
# # 		# 	frameParts = framePair.split('-')
# # 		# 	start = int(frameParts[0])
# # 		# 	end = start
# # 		# 	if len(frameParts) > 1:
# # 		# 		end = int(frameParts[1])
# # 		# 	contents += '''hou.node('%s').render(frame_range=(%d,%d))\n''' % (jobData['node'], start, end)

# # 		# contents += '\nhou.releaseLicense()\n'

# # 		# shepherd submit
# # 		contents = '''
# # import sys
# # sys.path.append('c:/Python27/lib/site-packages')
# # import arkInit
# # arkInit.init()

# # import settingsManager
# globalSettings = settingsManager.globalSettings()
# # sys.path.append(globalSettings.SHEPHERD_ROOT)
# # import submit

# # # submit job
# # jobData = {
# # 	'''
# # 		for key, val in jobData.iteritems():
# # 			contents += "\t'%s': '%s',\n" % (str(key), str(val))
# # 		contents += '''}

# # print submit.submitJob(jobData)
# # 	'''

# # 		print 'contents:\n',contents


# # 		# systemThread = threading.Thread(target=os.system, args=('"' + globalSettings.HOUDINI_ROOT + 'bin/hython.exe" %s %s' % (jobData['filename'], commandFilepath),))
# # 		# systemThread.start()
# # 		# os.system('"' + globalSettings.HOUDINI_ROOT + 'bin/hython.exe" %s %s && pause' % (jobData['filename'], commandFilepath))

# # 		# fix: submit should have an async submit, this should be party of it?
# # 		# cOS.runPython(commandFilepath)
# # 		# print globalSettings.PYTHON + ' ' + commandFilepath
# # 		# print 'command:\n', '"' + globalSettings.HOUDINI_ROOT + 'bin/hython.exe" %s %s && pause' % (jobData['filename'], commandFilepath)

	def repath( self, sourcePath, destinationPath):
		'''
		Change all paths from sourcePath to destinationPath, removing relative paths in the process
		'''

		sourcePath = cOS.unixPath(sourcePath)
		destinationPath = cOS.unixPath(destinationPath)

		hipPath = os.path.dirname(hou.hipFile.path())
		hipPath = re.sub(r'[\\/]+', '/', hipPath)

		for node in hou.node('/').allSubChildren():
			for parm in node.parms():
				try:
					val = str(parm.unexpandedString())
					if '$HIP' in val:
						print 'replacing $HIP:', val
						parm.set(val.replace('$HIP', hipPath))

					val = val.replace('\\','/')
					# fix: hax for now
					if sourcePath + '/assets' not in val.lower():
						parm.set(re.sub(r'[qQ]:[\\/]', 'R:/', val))
				except:
					pass


	# PySide
	########################################
	def getQTApp(self):
		app = QtGui.QApplication.instance()
		if not app:
			print 'No app instance found, creating'
			app = QtGui.QApplication
			pyqt_houdini.exec_(app)
		return app

	# def launch(self, Dialog, qApplication=None, *args, **kwargs):
	# 	app = self.getQTApp()
	# 	dialog = Dialog(app.activeWindow(), *args, **kwargs)
	# 	return dialog

	def launch(self, Dialog, parent=None, newWindow=None, *args, **kwargs):
		if parent is not None:
			newWindow = True

		if parent:
			print 'have parent'
			ex = Dialog(parent, *args, **kwargs)
			if newWindow:
				ex.setWindowFlags(QtCore.Qt.Window)
			ex.show()
		else:
			print 'using activeWindow'
			ex = Dialog(QtGui.QApplication.activeWindow(), *args, **kwargs)
			if newWindow:
				ex.setWindowFlags(QtCore.Qt.Window)
			ex.show()

		return ex
