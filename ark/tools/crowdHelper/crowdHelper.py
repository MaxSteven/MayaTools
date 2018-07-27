
import os
import shutil

import arkInit
arkInit.init()

import cOS


def duplicatePerson(root, person, newName):
	oldFolder = root + person + '/'
	newFolder = root + newName + '/'
	print oldFolder, ' > ', newFolder
	cOS.copyTree(oldFolder, newFolder)

	for folder in os.listdir(newFolder):
		root = newFolder + folder + '/'
		for f in os.listdir(root):
			os.rename(root + f, root + f.replace(person, newName))
