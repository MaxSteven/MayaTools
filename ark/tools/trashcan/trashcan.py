
import os

import arkInit
arkInit.init()

import cOS
import arkUtil

import settingsManager
globalSettings = settingsManager.globalSettings()

import translators
translator = translators.getCurrent()

import baseWidget
import shutil

trashFolder = globalSettings.SHARED_ROOT + '_trashcan/'
cOS.makeDirs(trashFolder)

def scanForShow(show):
	renderPath = cOS.join(show, 'Final_Renders')

	files = []
	exr = 'EXR_Linear'

	for episode in os.listdir(renderPath):
		showPath = cOS.join(renderPath, episode)

		if os.path.isdir(showPath):

			showItems = os.listdir(showPath)
			if exr in showItems:
				showItems.remove(exr)
				fullPath = cOS.join(showPath, exr)
				files.append(fullPath)

				for showItem in showItems:
					fullPath = cOS.join(showPath, showItem)
					deleteFile(showPath, fullPath)


	for f in files:
		trashOldVersions(f)



# Functions
##################################################
def getLatestVersions(files):
	files.sort()
	trash = []

	baseNames = {}

	for filename in files:
		baseName = arkUtil.replaceAll(filename, '[vV][0-9]+', '')
		version = cOS.getVersion(filename)

		if baseName in baseNames:
			if version > baseNames[baseName]['latestVersion']:
				trash.append(baseNames[baseName]['latestFile'])
				baseNames[baseName]['latestFile'] = filename
				baseNames[baseName]['latestVersion'] = version
			else:
				trash.append(filename)
		else:
			baseNames[baseName] = {
				'latestFile': filename,
				'latestVersion': version,
			}

	latest = [f for f in files if f not in trash]

	return latest

def trashOldVersions(folder):
	try:
		folder = cOS.normalizeDir(folder)
		files = os.listdir(folder)
	except:
		return 'Invalid folder: ' + folder

	latestVersions = getLatestVersions(files)
	trash = [folder + f for f in files if f not in latestVersions]


	for f in trash:
		deleteFile(folder, f)


	print '\n\nGreat success!'
	return True

def deleteFile(folder, file):
	trashName = file.replace(folder, trashFolder)

	print file, trashName, folder

	try:
		if os.path.isdir(trashName):
			print 'removing existing dir ', trashName
			os.rmdir(trashName)
		elif os.path.isfile(trashName):
			print 'removing existing file ', trashName
			os.remove(trashName)
		print 'removing the file ', file
		os.rename(file, trashName)
	except:
		return 'Error moving folder, maybe already in trash?: ' + file

# GUI
##################################################
options = {
	'title': 'Trashcan',
	'width': 460,
	'height': 200,
	'knobs': [
		{
			'name': 'folder',
			'dataType': 'directory',
			'value': 'r:/Fake Show/',
		},
		{
			'name': 'Trash Old Versions',
			'dataType': 'pythonButton',
			'callback': 'trashOldVersions'
		},
		{
			'name': 'Clear Workspaces of sc',
			'dataType': 'pythonButton',
			'callback': 'clearWorkspace'
		}
	]
}

class Trashcan(baseWidget.BaseWidget):

	def trashOldVersions(self):
		folder = self.getKnob('folder').getValue()

		scanForShow(folder)

	def clearWorkspace(self):
		shot = cOS.join(cOS.normalizePath(self.getKnob('folder').getValue()), 'Workspaces')
		trash = cOS.normalizePath('r:/_trashcan/')

		if os.path.isdir(shot) and os.path.isdir(trash):
			total = 0
			for root, dirs, files in os.walk(shot):
				for f in files:
					if f.endswith('.ifd.sc') or f.endswith('.bgeo.sc'):
						src = cOS.join(root, f)
						dest = cOS.join(trash, f)
						uniqueDest = dest

						counter = 0
						while os.path.isfile(uniqueDest):
							#print dest, 'already exists'
							uniqueDest = cOS.join(trash, str(counter) + f)
							counter += 1

						shutil.move(src, uniqueDest)
						print 'deleted:', uniqueDest
						total += 1

			print 'deleted a total of {} files! Woo!'.format(total)
		else:
			print 'The path you have selected does not exist!'

def gui():
	return Trashcan(options=options)

def main():
	translator.launch(Trashcan, options=options)

def test():
	trashOldVersions('C:/ie/ark/test/test_trashcan')

if __name__ == '__main__':
	main()

