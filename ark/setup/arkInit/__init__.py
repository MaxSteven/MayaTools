'''
Sets up system paths for Ingenuity's tools
'''

import sys
import os
import site

initialized = False
arkRoot = False

def addImportPath(path):
	'''
	Adds the specified path to the beginning of sys.path
	'''
	if path not in sys.path:
		print 'Add import path:', path
		# sys.path.insert(0, path)
		sys.path.append(path)

def init():
	'''
	Set up import directories for ark
	'''
	global initialized
	global arkRoot
	arkRoot = os.environ.get('ARK_ROOT')

	if initialized:
		return

	addImportPath(arkRoot)

	# get the tools directory
	if 'ARK_ROOT' not in os.environ:
		raise Exception('Please run install before using the Ark toolset')

	# add the appropriate site packages to the system path
	if '2.7' in sys.version:
		print 'Using Python 2.7'
		# ark/setup contains initTools
		arkSetupRoot = arkRoot + 'ark/setup'
		# ark's site packages folder
		arkPackagePath = arkRoot + 'ark/setup/sitePackages/2.7'
		# site-packages folder for the current running
		# python instance
		pythonPackagePath = site.getsitepackages()[1]
		# global site-packages
		globalPackagePath = os.environ.get('ARK_PYTHONLIB')
	else:
		raise Exception('Unsupported Python version:' + sys.version)

	importPaths = [
		# setup root
		arkSetupRoot,
		# ark site packages
		arkPackagePath,
		# app-specific packages root
		pythonPackagePath,
		# global packages root
		globalPackagePath,
	]

	# packages inserted in reverse order
	importPaths.reverse()
	for p in importPaths:
		addImportPath(p)

	# initTools adds more system paths, specificall for ark
	import initTools
	initTools.init()

	initialized = True


if __name__ == '__main__':
	init()
