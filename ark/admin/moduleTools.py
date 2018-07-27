
# Standard Modules
import compileall
import json
import os
import shutil
import sys

# Our Modules
import arkInit
arkInit.init()
arkRoot = arkInit.arkRoot

import cOS
import arkUtil
import tryout
from tryout import colors
import removeCompiledFiles
import settingsManager
globalSettings = settingsManager.globalSettings()
# import copyWrapper
# import folderSync

# for formatting
lineLength = 50

# C:\ie\ark\programs\nuke

def loadModuleOptions():
	global arkRoot
	# with open(arkRoot + 'tools.sublime-project') as f:
	with open(arkRoot + 'ark/tools.sublime-project') as f:
		contents = f.read()

	options = json.loads(contents)
	options = arkUtil.unicodeToString(options)

	cleanedModules = []
	for module in options['folders']:
		module['path'] = module['path'].replace('../','')
		cleanedModules.append(module)

	return cleanedModules

def getModuleNames():
	options = loadModuleOptions()
	return [module['path'] for module in options]

def getModuleOptions(moduleName):
	if moduleName not in getModuleNames():
		raise Exception('Invalid module name: ' + moduleName)
	for moduleOptions in loadModuleOptions():
		if moduleOptions['path'] == moduleName:
			return moduleOptions

def getModuleFiles(moduleName, **kwargs):
	options = getModuleOptions(moduleName)

	# default values for includes
	args = {
		'fileIncludes': False,
		'folderIncludes': False,
		'folderExcludes': [],
		'fileExcludes': [],
		'includeAfterExclude': False,
		'filesOnly': True,
	}

	# pull them from the module's options
	if 'folder_exclude_patterns' in options:
		args['folderExcludes'] = options['folder_exclude_patterns']
	if 'file_exclude_patterns' in options:
		args['fileExcludes'] = options['file_exclude_patterns']

	# always ignore .git directory

	for key in args.keys():
		if key in kwargs:
			args[key] = kwargs[key]

	# always ignore the .git folder
	# add if it's not already in folderExcludes
	if '.git' not in args['folderExcludes']:
		args['folderExcludes'].append('.git')

	print 'getModuleFiles args:'
	for k, v in args.iteritems():
		print k, ':', v

	return cOS.getFiles(
			arkRoot + options['path'],
			**args)

def compileAllModules(quiet=True):
	options = loadModuleOptions()
	for module in options:
		files = getModuleFiles(
			module['path'],
			fileIncludes=['*.py'])

		for filename in files:
			if not quiet:
				print 'Compiling:', filename
			result = compileall.compile_file(
				filename,
				force=True,
				quiet=True)
			if not result:
				raise Exception('Compile failed:', filename)

# kwargs can include files/folders to exclude and include, with exclude evaluated first
# then include back files/folders initially ignored
def publishTools(destination, modules, quiet=False, **kwargs):
	args = {
		'fileIncludes': False,
		'folderIncludes': False,
		'folderExcludes': [],
		'fileExcludes': [],
		'includeAfterExclude': True,
		'filesOnly': True,
	}

	# Parse fileExcludes from kwargs
	for arg in args.keys():
		if arg in kwargs:
			args[arg] = kwargs[arg]

	# Before copying, compile all modules
	print '\nCompiling all local modules...'
	compileAllModules()

	directory = cOS.normalizeDir(destination)

	# Make sure publishing folder exists
	try:
		os.makedirs(directory)
	except OSError:
		if not os.path.isdir(directory):
			raise
	print '\nPublished tools directory %s, continuing...' % directory

	for module in modules:
		print '\nPublishing:', module

		files = getModuleFiles(module, **args)

		# Add certain .py files back for compatability
		# Seperately, as fileIncludes Setup.py will not intersect fileExcludes['*.py'], for example
		# includes = getModuleFiles(module, **fileIncludes)
		# files += includes

		# Parse source path root
		source = arkRoot + getModuleOptions(module)['path']
		source = cOS.normalizeDir(source)

		# Make destination folder
		destination = directory + module
		destination = cOS.normalizeDir(destination)

		try:
			os.mkdir(destination)
			print 'Creating module destination %s' % destination
		except OSError:
			if not os.path.isdir(destination):
				raise

		# Copy files to new folder
		for file in files:
			relPath = cOS.normalizePath(os.path.relpath(file, source))
			destPath = destination + relPath
			pathInfo = cOS.getPathInfo(destPath)
			subDir = cOS.normalizeDir(pathInfo['dirname'])

			# Recursively make any subdirs if they don't already exists
			try:
				os.makedirs(subDir)
			except OSError:
				if not os.path.isdir(subDir):
					raise

			# Copy file path with fast copy
			# fix: copyWrapper should handle this systen check
			try:
				cOS.copy(file, destPath)

				if not quiet:
					print 'copying: %s > %s' % (file, destPath)
			except Exception as err:
				print 'Error copying file ' + file
				# raise err

		# Clean up remote
		print '\nCleaning up remote. Walking %s\n' % (destination)
		fileCount = 0
		dirCount = 0
		for walkRoot, walkDirs, walkFiles in os.walk(destination):
			walkRoot = cOS.normalizeDir(walkRoot)
			# Remove any files that shouldn't be there
			for f in walkFiles:
				remoteFile = walkRoot + f
				localFile = remoteFile.replace(destination, source)
				# If file not in published set, remove
				if localFile not in files:
					out = cOS.removeFile(remoteFile)
					if not quiet:
						print 'remove remote:', remoteFile
					if out != True:
						print 'error removing file %s: %s' % (remoteFile, out)
					else:
						fileCount += 1

			# Remove directories that shouldn't be there
			for dir in walkDirs:
				remoteDir = walkRoot + dir
				localDir = remoteDir.replace(destination, source)
				if not os.path.isdir(localDir):
					if not quiet:
						print 'removing remote dir:', remoteDir
					out = cOS.removeDir(remoteDir)
					if out != True:
						print 'error removing dir %s: %s' % (remoteDir, out)
					else:
						dirCount += 1

		print 'Removed %s remote files from remote %s.' % (fileCount, destination)
		print 'Removed %s remote dirs from remote %s.' % (dirCount, destination)
		print 'Copied %s files from %s to %s' % (len(files), source, destination)

	print '\nPublishing complete.\n'

	print '\nZipping tools...\n'
	shutil.make_archive(directory[:-1] + '.tmp', 'zip', directory[:-1])
	cOS.removeFile(directory[:-1] + '.zip')
	os.rename(directory[:-1] + '.tmp.zip', directory[:-1] + '.zip')
	print '\nZipping complete.\n'

	print '\nRemoving local compiled files...'
	removeCompiledFiles.main()
	print '\nRemoved local compiled files. Publishing complete.\n'
	return True

def updateModule(module, quiet=False):
	moduleRoot = arkRoot + module
	if not quiet:
		print 'Updating:', module
	out, err = cOS.getCommandOutput('git pull', cwd=moduleRoot)
	if not quiet:
		print out, err
	return out, err

def updateAllModules(quiet=False):
	modules = getModuleNames()
	for module in modules:
		updateModule(module, quiet=quiet)

# Takes in boolean, bail=True/False. Defaults to True.
def testAll(callback=None, bail=True):
	modules = getModuleNames()
	# fix: temp, remove once all are in order
	modules = [
		'ark',
		'arkMath',
		'arkUtil',
		'cOS',
		'database',
		'logmont',
		'settingsManager',
		'shepherd',
		'translators',
		]

	moduleResults = []
	string = ''
	for module in modules:
		moduleRoot = arkInit.arkRoot + module
		folderFiles, folderPassed, folderFailed, folderError, folderMethod = \
		tryout.runFolder(moduleRoot + '/test/', callback, bail)
		moduleResults.append((module, folderFiles, folderPassed, folderFailed, folderError, folderMethod))
		# out, err = cOS.getCommandOutput('mocha test', cwd=moduleRoot)
		# String for Modules summary
		string += (str(module) + ', ')
		# If error raised and bail=True, stop module testing and print summary
		if folderError and bail:
			print 'Bailing...\n\nPrinting Module Summary...'
			break
	# Print out module summary
	tryout.colors('yellow', '\n\n Modules Summary:', tryout.colors.end + string[:-2])
	tryout.colors('yellow', '=' * lineLength + '\n')
	success = True
	for result in moduleResults:
		testModule = result[0]
		testFiles = result[1]
		testPassed = result[2]
		testFailed = result[3]
		testError = result[4]
		testMethod = result[5]
		if testFailed > 0:
			colors('red', testModule + colors.end + ': ' + str(testPassed) + ' passed, ' \
				+ str(testFailed) + ' failed in ' + str(testFiles) + ' files\n')
			success= False
			if bail:
				print 'Failing on test ' + testMethod + ' with:'
				colors('red', '\nError:\n')
				print testError
		else:
			colors('green', testModule + colors.end + ': ' + str(testPassed) \
				+ ' passed in ' + str(testFiles) + ' files\n')
	if success:
		print('All tests passed in all modules.\n')
	else:
		print('Module(s) failing test(s).\n')

def main(modules=None):
	# compile everything, takes no time, burn it down
	compileAllModules(quiet=False)

	modules = arkUtil.ensureArray(modules)
	for module in modules:
		files = getModuleFiles(
			module,
			fileExcludes=['*.py'])

		print '\n'.join(files)

	# modules = arkUtil.ensureArray(modules)
	# for module in modules:
	# 	updateModule(module)
	# updateAllModules()

if __name__ == '__main__':
	# main()
	if len(sys.argv) < 2:
		print('Specify a tool to update')
		print('ex: python C:/ie/ark/admin/updateModule.py ark')
	else:
		main(sys.argv[1])
