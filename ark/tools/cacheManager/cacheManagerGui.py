
import os
import time

import arkInit
arkInit.init()

import translators
translator = translators.getCurrent()

import baseWidget
import cOS

import settingsManager
globalSettings = settingsManager.globalSettings()

options = {
	'title': 'Cache Manager',
	'width': 460,
	'height': 220,
	# 'x': 100,
	# 'y': 100,
	# 'margin': '0 0 0 0',
	'knobs': [
		{
			'name': 'heading',
			'dataType': 'heading',
			'value': 'Cache Manager'
		},
		# {
		# 	'name': 'Cache Directory',
		# 	'dataType': 'directory',
		# 	'value': 'c:/temp',
		# 	'directory': 'c:/temp',
		# },
		{
			'name': 'Progress',
			'dataType': 'progress'
		},
		{
			'name': 'Cache Selected',
			'dataType': 'pythonButton',
			'callback': 'cacheSelected',
		},
		{
			'name': 'Cache All',
			'dataType': 'pythonButton',
			'callback': 'cacheAll',
		},
		{
			'name': 'Uncache Selected',
			'dataType': 'pythonButton',
			'callback': 'uncacheSelected',
		},
		{
			'name': 'Uncache All',
			'dataType': 'pythonButton',
			'callback': 'uncacheAll',
		},
		{
			'name': 'Remove Old Files',
			'dataType': 'pythonButton',
			'callback': 'removeOldFiles',
		},
	]
}


class CacheManager(baseWidget.BaseWidget):

	def cacheAll(self):
		nodes = translator.getCacheableNodes()
		self.cache(nodes)

	def cacheSelected(self):
		nodes = translator.getSelectedNodes()
		self.cache(nodes)

	def cache(self, nodes):
		progress = self.getKnob('Progress')
		progress.setValue(0)
		nodeCount = len(nodes)
		for i, node in enumerate(nodes):
			translator.cacheNode(node)
			progress.setValue((i + 1) / nodeCount)
		progress.setValue(100)

	def uncacheSelected(self):
		nodes = translator.getSelectedNodes()
		self.uncache(nodes)

	def uncacheAll(self):
		nodes = translator.getCacheableNodes()
		self.uncache(nodes)

	def uncache(self, nodes):
		for node in nodes:
			translator.uncacheNode(node)

	def removeOldFiles(self):
		print 'removeOldFiles'
		tenDays = 60 * 60 * 24 * 10
		threshold = time.time() - tenDays
		print 'searching:', globalSettings.TEMP
		for root, dirs, files in os.walk(globalSettings.TEMP):
			rootDir = cOS.normalizeDir(root)
			for f in files:
				filepath = rootDir + f
				modifiedTime = os.path.getmtime(filepath)
				if modifiedTime < threshold:
					try:
						os.remove(filepath)
						print 'Removing:', filepath
					except:
						print 'Failed to remove:', filepath
						pass

def gui(parent=None):
	return CacheManager(parent=parent, options=options)

def launch(parent=None, *args, **kwargs):
	kwargs['newWindow'] = True
	kwargs['options'] = options
	translator.launch(CacheManager, parent, *args, **kwargs)


if __name__ == '__main__':
	launch()
