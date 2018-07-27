
import os
import sys
import ast

import tempfile
import shutil

import arkInit
arkInit.init()

import cOS
import settingsManager
globalSettings = settingsManager.globalSettings()

'''
PROPER USAGE:
python archive.py <list of workspaces> <archive directory> <replace list>

ex:
python archive.py "['Q:/Qoros/Workspaces/0050/comp', 'Q:/Qoros/Workspaces/0060/comp']" "C:/archive/Qoros" "['q:/qoros','f:/qoros','q:\\qoros','f:\\qoros']"
'''


# python archive.py "['f:/qoros/workspaces/6010/comp','f:/qoros/workspaces/6020/comp','f:/qoros/workspaces/6030/comp','f:/qoros/workspaces/6040/comp','f:/qoros/workspaces/6050/comp','f:/qoros/workspaces/6060/comp','f:/qoros/workspaces/6070/comp','f:/qoros/workspaces/6080/comp','f:/qoros/workspaces/6090/comp','f:/qoros/workspaces/6100/comp','f:/qoros/workspaces/6110/comp','f:/qoros/workspaces/6120/comp','f:/qoros/workspaces/6130/comp','f:/qoros/workspaces/6140/comp','f:/qoros/workspaces/6150/comp','f:/qoros/workspaces/6160/comp','f:/qoros/workspaces/6170/comp','f:/qoros/workspaces/6180/comp','f:/qoros/workspaces/6190/comp','f:/qoros/workspaces/6200/comp','f:/qoros/workspaces/6210/comp','f:/qoros/workspaces/6220/comp','f:/qoros/workspaces/6230/comp','f:/qoros/workspaces/6240/comp','f:/qoros/workspaces/6250/comp','f:/qoros/workspaces/6260/comp','f:/qoros/workspaces/6270/comp','f:/qoros/workspaces/6280/comp','f:/qoros/workspaces/6290/comp','f:/qoros/workspaces/6300/comp','f:/qoros/workspaces/6310/comp','f:/qoros/workspaces/6320/comp','f:/qoros/workspaces/6330/comp','f:/qoros/workspaces/6340/comp','f:/qoros/workspaces/6350/comp','f:/qoros/workspaces/6360/comp','f:/qoros/workspaces/6370/comp','f:/qoros/workspaces/6380/comp','f:/qoros/workspaces/6390/comp','f:/qoros/workspaces/6400/comp','f:/qoros/workspaces/6410/comp','f:/qoros/workspaces/6420/comp','f:/qoros/workspaces/6430/comp','f:/qoros/workspaces/6440/comp','f:/qoros/workspaces/7000/comp','f:/qoros/workspaces/7005/comp','f:/qoros/workspaces/7010/comp','f:/qoros/workspaces/7015/comp','f:/qoros/workspaces/7020/comp']" "E:/archive" "['Q:/Qoros','F:/Qoros']"
# python archive.py "['f:/qoros/workspaces/6010/comp','f:/qoros/workspaces/6020/comp']" "E:/archive"
# python archive.py "['f:/qoros/workspaces/6010/comp','f:/qoros/workspaces/6020/comp']" "E:/archive" "['Q:/Qoros','F:/Qoros']"
# python archive.py "['f:/qoros/workspaces/6010/comp']" "E:/archive" "['Q:/Qoros','F:/Qoros']"
# python archive.py "['f:/qoros/workspaces/6030/comp']" "E:/archive" "['Q:/Qoros','F:/Qoros']"



def replaceInFile(filePath, replaceList):
	#Create temp file
	fileHandle, tmpPath = tempfile.mkstemp()
	with open(tmpPath,'w') as newFile:
		with open(filePath) as oldFile:
			for line in oldFile:
				it = iter(replaceList)
				for k,v in zip(it, it):
					line = line.replace(k, v)
				newFile.write(line)

	os.close(fileHandle)
	os.remove(filePath)
	shutil.move(tmpPath, filePath)

def archive(workspaces, archive, replaceList=None):

	archive = cOS.normalizeDir(archive)
	cOS.makeDirs(archive)

	for workspace in workspaces:
		workspace = cOS.normalizeDir(workspace)

		filesInWorkspace = [f for f in os.listdir(workspace) if '~' not in f]
		mostRecentFile = filesInWorkspace[max((cOS.getVersion(f), i) for i, f in enumerate(filesInWorkspace))[1]]
		fileToOpen = workspace + mostRecentFile
		archiveFilename = fileToOpen.replace('.nk','.archive.nk')
		shutil.copyfile(fileToOpen, archiveFilename)

		if replaceList:
			replaceInFile(archiveFilename, replaceList)

		scriptedCommand = ' '.join(['"' + globalSettings.NUKE_EXE + '"', 'backupRead.py', archiveFilename, archive])
		print scriptedCommand
		os.system(scriptedCommand)

if __name__ == '__main__':
	workspaces = sys.argv[1]
	arc = sys.argv[2]
	replaceList = sys.argv[3]
	workspaces = ast.literal_eval(workspaces)
	replaceList = ast.literal_eval(replaceList)

	archive(workspaces, arc, replaceList)
