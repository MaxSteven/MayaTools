
# Standard modules
##################################################
import os
import sys

arkRoot = os.environ.get('ARK_ROOT')

def addImportPath(path):
	'''
	Adds the specified path to the beginning of sys.path
	'''
	if path not in sys.path:
		print 'Add import path:', path
		# sys.path.insert(0, path)
		sys.path.append(path)

def init():
	sys.path.append(arkRoot + 'ark/lib')
	sys.path.append(arkRoot + 'ark/ui')
	sys.path.append(arkRoot + 'ark/tools')
	sys.path.append(arkRoot + 'ark/admin')
	sys.path.append(arkRoot + 'ark/programs')
	sys.path.append(arkRoot + 'settingsManager')
	sys.path.append(arkRoot + 'coren/autoBackup')
