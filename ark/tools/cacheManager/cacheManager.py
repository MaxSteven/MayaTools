import os#, sys
# import time
# import subprocess

import arkInit
arkInit.init()

# import ieOS
import cOS
import settingsManager
globalSettings = settingsManager.globalSettings()
import translators
translator = translators.getCurrent()
# from keyCommands import Command
import maya.cmds as cmds

import copyWrapper
import folderSync

from translators import QtGui, QtCore

nodeTypes = ['maxwellReferencedMXS']
IENETWORKCACHE = 'r:/Assets/TOOLS/Shepherd/LocalCache/'


class CacheManager(QtGui.QDialog):

	def __init__(self, parent=None, **kwargs):
		super(CacheManager, self).__init__(parent)

		# different programs pass along different arguments
		# ex: Nuke passes node=<current_write_node>
		translator.setArgs(kwargs)

		self.setWindowTitle('Cache Manager')

		form = QtGui.QFormLayout()
		form.setLabelAlignment(QtCore.Qt.AlignLeft)
		form.setVerticalSpacing(10)

		hBox = QtGui.QHBoxLayout()
		self.cacheSelectionButton = QtGui.QPushButton('Cache Selection')
		cacheSelection = lambda: self.manageCache(True)
		self.cacheSelectionButton.clicked.connect(cacheSelection)
		hBox.addWidget(self.cacheSelectionButton)
		cacheAll = lambda: self.manageCache(False)
		self.cacheAllButton = QtGui.QPushButton('Cache All')
		self.cacheAllButton.clicked.connect(cacheAll)
		hBox.addWidget(self.cacheAllButton)
		form.addRow(hBox)

		hBox = QtGui.QHBoxLayout()
		self.resetSelectionButton = QtGui.QPushButton('Reset Selection to Network')
		resetSelection = lambda: self.setNodePathsToNetwork(True)
		self.resetSelectionButton.clicked.connect(resetSelection)
		hBox.addWidget(self.resetSelectionButton)
		self.resetAllButton = QtGui.QPushButton('Reset All to Network')
		resetAll = lambda: self.setNodePathsToNetwork(False)
		self.resetAllButton.clicked.connect(resetAll)
		hBox.addWidget(self.resetAllButton)
		form.addRow(hBox)

		hBox = QtGui.QHBoxLayout()
		self.exploreNetworkButton = QtGui.QPushButton('Open Network Cache')
		openNetwork = lambda: self.explore('Q:\\Assets\\TOOLS\\Shepherd\\localCache')
		self.exploreNetworkButton.clicked.connect(openNetwork)
		hBox.addWidget(self.exploreNetworkButton)
		self.exploreLocalButton = QtGui.QPushButton('Open Local Cache')
		openLocal = lambda: self.explore(globalSettings.LOCALCACHE.replace('/', '\\'))
		self.exploreLocalButton.clicked.connect(openLocal)
		hBox.addWidget(self.exploreLocalButton)
		form.addRow(hBox)

		self.setLayout(form)

		self.setGeometry(300, 300, 450, 100)
		self.show()

	def explore(self, loc):
		os.system('explorer ' + loc)

	def setNodePathsToNetwork(self, selection):
		cacheNodes = self.selectCacheNodes(selection)
		self.setNetworkPaths(cacheNodes)

	def setNetworkPaths(self, cacheNodes):
		n = []
		for node in cacheNodes:

			if (node in n):
				continue
			n.append(node)

			fileName = cmds.getAttr(cmds.ls(node)[0] + '.file')

			if 'r:/' in fileName.lower():
				continue

			networkPath = 'r:/'
			cmds.setAttr(cmds.ls(node)[0] + '.file', fileName.lower().replace(globalSettings.LOCALCACHE.lower(), networkPath), type='string')

	def manageCache(self, selection):
		cacheNodes = self.selectCacheNodes(selection)
		self.setNetworkPaths(cacheNodes)
		self.copyFiles(cacheNodes)
		self.substituteFilePaths(cacheNodes)

	def selectCacheNodes(self, selection):
		seen = []
		nodes = []
		if (selection):
			n = cmds.ls(sl=True)
		else:
			n = cmds.ls()
		for node in n:
			if node in seen:
				continue
			seen.append(node)
			if (cmds.listRelatives(node, allDescendents=True)):
				for child in cmds.listRelatives(node, allDescendents=True):
					try:
						if cmds.nodeType(child) in nodeTypes:
							nodes.append(child)
					except:
						pass

		return nodes

	def copyFiles(self, cacheNodes):

		n = []
		for node in cacheNodes:
			if (node in n):
				continue
			n.append(node)

			fileName = cmds.getAttr(cmds.ls(node)[0] + '.file')
			baseName = self.stripRoot(fileName)

			if 'c:/ie/localcache/' in fileName.lower():
				continue

			if not os.path.isfile(IENETWORKCACHE + baseName):
				print 'Copying File:', fileName
				copyWrapper.copy(fileName, IENETWORKCACHE + baseName, '')
			elif os.path.getmtime(fileName) > os.path.getmtime(IENETWORKCACHE + baseName):
				print 'Modified time later', fileName, baseName
				copyWrapper.copy(fileName, IENETWORKCACHE + baseName, '')
		folderSync.folderSync(globalSettings.LOCALCACHE, IENETWORKCACHE)

	def substituteFilePaths(self, cacheNodes):

		n = []
		for node in cacheNodes:

			if (node in n):
				continue
			n.append(node)

			fileName = cmds.getAttr(cmds.ls(node)[0] + '.file')
			fileName = cOS.unixPath(fileName.lower())
			# baseName = self.stripRoot(fileName)

			if 'c:/ie/localcache/' in fileName:
				continue

			# localPath = globalSettings.LOCALCACHE + baseName
			cmds.setAttr(cmds.ls(node)[0] + '.file', fileName.replace('r:/', globalSettings.LOCALCACHE), type='string')

	def stripRoot(self, f):
		f = cOS.unixPath(f)
	 	return '/'.join(f.split('/')[1:])

def main(parent=None, *args, **kwargs):
	# print globalSettings.CURRENT_APP
	translator.launch(CacheManager, parent, *args, **kwargs)

if __name__ == '__main__':
	main()

	print 'Cache Managing Completed.'
