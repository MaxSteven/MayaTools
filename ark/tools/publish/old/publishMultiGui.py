#python
# launchScript "C:\ie\ark\tools\publish\publishMultiGui.py"

import os
import atexit

import arkInit
arkInit.init()

import translators
translator = translators.getCurrent()
from translators import QtCore
from translators import QtSignal

import baseWidget

import sys
sys.path.insert(0, os.path.dirname(__file__))

import multiFileHelpers
from publishMulti import PublishMulti


class PublishMultiGui(baseWidget.BaseWidget):

	submitted = QtSignal(dict)

	def postShow(self):
		self.threadSearcher = SearchManager()
		self.threadSearcher.setConnection(self.addData)

		# Ensures the first search has to be triggered by the
		# 'Search' button. From then on, changing the radio
		# or checkbox buttons will retrigger a search.
		self.searchUnLocked = False

		knob = self.getKnob('Search Progress')
		self.threadSearcher.signal.done.connect(knob.setMaximum)
		atexit.register(self.threadSearcher.terminate)

		knob = self.getKnob('Latest versions only')
		knob.widget.stateChanged.connect(self.searchFiles)

		knob = self.getKnob('Search mode')
		knob.widget.stateChanged.connect(self.searchFiles)

	def addData(self, data):
		data = [x.replace('\\', '/') for x in data]
		if self.getKnob('Latest versions only').getValue():
			allData = self.getKnob('files').getValue() + data
			allData = multiFileHelpers.listLatestVersions(allData)
			self.getKnob('files').removeAll()
			self.getKnob('files').addFiles(allData)
		else:
			self.getKnob('files').addFiles(data)

	def firstSearch(self):
		self.searchUnLocked = True
		self.searchFiles()


	def searchFiles(self):
		if not self.searchUnLocked:
			return

		self.getKnob('files').removeAll()
		sourcePath = self.getKnob('Directory').getValue()
		wildcard = self.getKnob('Search for').getValue()
		latestVersion = self.getKnob('Latest versions only').getValue()
		sequenceMode = self.getKnob('Search mode').getValue() == 'Sequence Mode'

		self.threadSearcher.setParams(sourcePath, wildcard, sequenceMode, latestVersion)
		self.threadSearcher.start()

	def submit(self):
		print '\nPublishing:\n'
		files = self.getKnob('files').getValue()
		self.submitted.emit({'files': files})



class MySignal(QtCore.QObject):
	done = QtSignal(int)



def workerSearch(sourcePath, wildcard, sequenceMode, singleDir=False):
	publishMulti = PublishMulti()
	if not singleDir:
		results = publishMulti.search(sourcePath, wildcard, sequenceMode)
	else:
		results = publishMulti.singleDirSearch(sourcePath, wildcard, sequenceMode)
	return results




### SearchManager: acts as rudimentary threadpool: allocates jobs to threads
### and will flag old threads when a new task has made them redundant.
class SearchManager(QtCore.QThread):
	def __init__(self):
		super(SearchManager, self).__init__()
		# self.pool = multiprocessing.Pool()
		self.signal = MySignal()

		#Forces the pool to terminate when the app is closed
		# atexit.register(self.pool.terminate)
		self.openProcesses = 0

	# setConnection: call with the slot that the Subthreads should connect to
	def setConnection(self, func):
		self.func = func

	def setParams(self, sourcePath, wildcard, sequenceMode, latestVersion):
		self.sourcePath = sourcePath
		self.wildcard = wildcard
		self.sequenceMode = sequenceMode
		self.latestVersion = latestVersion

	def run(self):
		self.signal.done.emit(0)
		results = workerSearch(self.sourcePath, self.wildcard, self.sequenceMode)
		self.func(results)
		self.signal.done.emit(100)
		# self.pool.terminate()
		# self.pool = multiprocessing.Pool()
		# dirList = [name for name in os.listdir(self.sourcePath) \
		# 			if os.path.isdir(os.path.join(self.sourcePath, name))]
		# self.signal.done.emit(0)
		# self.openProcesses = len(dirList)
		# for item in dirList:
		# 	self.pool.apply_async(workerSearch, args = (os.path.join(self.sourcePath, item), self.wildcard, self.sequenceMode), callback = self.func)

		# self.pool.apply_async(workerSearch, args = (self.sourcePath, self.wildcard, self.sequenceMode, True), callback = self.func)
		# self.pool.close()
		# self.pool.join()
		# self.signal.done.emit(100)



options = {
	'title': 'Multi Publish',
	'width': 700,
	'height': 800,
	# 'x': 100,
	# 'y': 100,
	'knobs':[
	{
		'name': 'heading',
		'dataType': 'heading',
		'value': 'Multi Publish'
	},
	{
		'name': 'Directory',
		'dataType': 'Directory',
		'value': 'C:/'
	},
	{
		'name': 'Search for',
		'dataType': 'Text',

	},
	{
		'name': 'Search mode',
		'dataType': 'radio',
		'value': 'Single File',
		'options': ['Single File', 'Sequence Mode']
	},
	{
		'name': 'Latest versions only',
		'value': False,
		'dataType': 'Checkbox'
	},
	{
		'name': 'Search',
		'dataType': 'PythonButton',
		'callback': 'firstSearch'
	},
	{
		'name': 'Search Progress',
		'dataType': 'progress'
	},
	{
		'name': 'files',
		'dataType': 'OpenFiles'
	},
	{
		'name': 'Publish',
		'dataType': 'PythonButton',
		'callback': 'submit'
	}

	]
}




def gui(parent=None):
	return PublishMultiGui(parent=parent, options=options)

def main():
	translator.launch(PublishMultiGui, None, options=options)

if __name__ == '__main__':
	main()