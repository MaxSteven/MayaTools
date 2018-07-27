
import re

import arkInit
arkInit.init()

import os
import cOS

import settingsManager
globalSettings = settingsManager.globalSettings()

validPlatforms = ['windows', 'linux', 'mac']

osType = 'windows'
def setOS(osName=None):
	global osType
	if not osName:
		osType = 'windows'
		if cOS.isLinux():
			osType = 'linux'
		elif cOS.isMac():
			osType = 'mac'
	elif osName.lower() in validPlatforms:
		osType = osName.lower()
	else:
		raise Exception('Invalid os: ' + osName)

# call setOS to properly set the OS
setOS()

def translatePath(path, osName=None):
	if not osName:
		global osType
		osName = osType
	else:
		osName = osName.lower()
		if osName not in validPlatforms:
			raise Exception('Invalid os: ' + osName)

	path = cOS.unixPath(path)
	# for each drive entry in PATHS
	for drive, paths in globalSettings.PATHS.iteritems():
		osPath = paths[osName]
		# for each OS in that drive entry
		for replaceOS, replacePath in paths.iteritems():
			# replace if the OS isn't the current os
			if replaceOS != osName:
				# only replace from the beginning of the path
				# keeps /some/drive/footage/whatever/ from getting replaced
				path = re.sub(r'^%s' % replacePath, osPath, path)

	return path

def localizePath(path):
	'''
	converts network path to localCache path if localCache is set
	'''
	if not path:
		return None
	path = cOS.unixPath(path)

	# Linux path used because no matter which OS, or file state,
	# if at any point it was localized even if to a different cache folder
	# it will always contain ramburglar and raidcharles

	# EXAMPLES OF POSSIBLE CASES
	# 'R:/A/B/C'						==>		cacheDir/ramburglar/A/B/C
	# '/ramburglar/A/B/C'				==>		cacheDir/ramburglar/A/B/C
	# 'N:/testCache/ramburglar/A/B/C 	==> 	cacheDir/ramburglar/A/B/C
	# 'cacheDir/ramburglar/A/B/C'		==>		cacheDir/ramburglar/A/B/C
	# 'Q:/A/B/C'						==>		cacheDir/raidcharles/A/B/C
	# '/raidcharles/A/B/C'				==>		cacheDir/raidcharles/A/B/C
	# 'N:/testCache/raidcharles/A/B/C'	==>		cacheDir/raidcharles/A/B/C
	# 'cacheDir/raidcharles/A/B/C'		==>		cacheDir/raidcharles/A/B/C
	# 'D:/A/B/C' 						==>		'D:/A/B/C'

	linuxPath = translatePath(path, osName='linux')

	for root in globalSettings.PATHS.keys():
		if root in linuxPath:
			# partition will make it: ['testCache/', 'ramburglar', '/AB/CX.pqr']
			path = ''.join(linuxPath.partition(root)[1:])
			# path = 'ramburglar/AB/CX.pqr'
			localCache = os.environ.get('ARK_CACHE')
			if not localCache:
				print 'ERROR: Localization failed. Local Cache not set.'
				return path

			# localCache value will always end with /
			localizedPath = localCache + path
			return localizedPath

	return path

def globalizePath(path):
	'''
	converts a path to network path if contains network Path Root
	'''
	if not path:
		return None
	path = cOS.unixPath(path)

	# Linux path used because no matter which OS, or file state,
	# if at any point it was localized even if to a different cache folder
	# it will always contain ramburglar and raidcharles
	# that's why converting to linux path is necessary

	# EXAMPLES OF POSSIBLE CASES
	# 'N:/testCache/ramburglar/A/B/C 	==> 	/ramburglar/A/B/C
	#									==>		R:/A/B/C
	# 'cacheDir/ramburglar/A/B/C'		==>		/ramburglar/A/B/C
	#									==>		R:/A/B/C
	# 'N:/testCache/raidcharles/A/B/C'	==>		/raidcharles/A/B/C
	#									==>		Q:/A/B/C
	# 'cacheDir/raidcharles/A/B/C'		==>		/raidcharles/A/B/C
	#									==>		Q:/A/B/C
	# 'R:/A/B/C'						==>		/ramburglar/A/B/C
	#									==>		R:/A/B/C
	# '/ramburglar/A/B/C'				==>		/ramburglar/A/B/C
	#									==>		R:/A/B/C
	# 'Q:/A/B/C'						==>		/raidcharles/A/B/C
	#									==>		Q:/A/B/C
	# '/raidcharles/A/B/C'				==>		/raidcharles/A/B/C
	#									==>		Q:/A/B/C
	# 'D:/A/B/C' 						==>		'D:/A/B/C'

	linuxPath = translatePath(path, osName='linux')
	for root in globalSettings.PATHS.keys():
		if root in linuxPath:
			# partition will make it: ['testCache/', 'ramburglar', '/AB/CX.pqr']
			path = ''.join(linuxPath.partition(root)[1:])

			# get linux path and translate it
			return translatePath('/' + path)

	return path

def searchPath(searchFolders, name, lvl):
	if len(name) == 0:
		return searchFolders
	else:
		return searchPath([f for g in searchFolders for f in cOS.getFolderContents(g)
			if f.split('/')[lvl].lower() == name[0].lower()],
			name[1:], lvl + 1)

# fixes slashes and drive name to current os, returns paths that exist
def translatePathSearch(path, osName=None):
	if cOS.isWindows():
		path = re.sub(r'\\ ', r' ', path)
	path = translatePath(path, osType)
	foundPaths = []

	if cOS.isLinux() and (os.path.isdir(path) or os.path.isfile(path)):
		foundPaths = [path]
	else:
		pathSplit = path.split('/')
		if len(pathSplit) > 0:
			root = pathSplit[0] + '/'
			if cOS.isWindows():
				pathSplit = pathSplit[1:]
			pathSplit = [p for p in pathSplit if not p == '']

			if os.path.isdir(root):
				foundPaths = searchPath([root], pathSplit, 1)

	# escape spaces
	if cOS.isLinux():
		return [re.sub(r' ', r'\\ ', p) for p in foundPaths]
	else:
		return foundPaths

def getRoot(path):
	path = cOS.normalizeDir(path)
	for drive, paths in globalSettings.PATHS.iteritems():
		for k in paths.keys():
			if paths[k] in path:
				return paths[k]

# fix: project should remove any roots not just shared root
def removeSharedRoot(path):
	# Remove shared root prefix from path
	if path.startswith(globalSettings.SHARED_ROOT):
		return path[len(globalSettings.SHARED_ROOT):]
	else:
		raise Exception('Path does not start with share root: ' +
			globalSettings.SHARED_ROOT)

def getEnvironmentPath(envStringFormat, path):
	# Get environment variables based on footage, raidcharles or ramburglar
	environmentVariables = globalSettings.DRIVES
	for envVariable in environmentVariables:

		# get environment variables based on the OS
		roots = [
			globalSettings.get(envVariable.upper() + '_WIN'),
			globalSettings.get(envVariable.upper() + '_LINUX')
		]

		envString = envStringFormat % envVariable.lower()

		for root in roots:
			# remove trailing slash on root if present
			if root.endswith('/') or root.endswith('\\'):
				root = root[:-1]

			# search for root lower() to lower() and replace
			if path.lower().startswith(root.lower()):
				path = envString + path[len(root):]

	return path

def nonEnvironmentPath(envStringFormat, path):
	# Get environment variables based on footage, raidcharles or ramburglar
	environmentVariables = globalSettings.DRIVES
	for envVariable in environmentVariables:
		realRoot = globalSettings.get(envVariable.upper())
		envString = envStringFormat % envVariable.lower()
		# remove trailing slash on root if present
		if realRoot.endswith('/') or realRoot.endswith('\\'):
			realRoot = realRoot[:-1]

		# search for root lower() to lower() and replace
		if path.lower().startswith(envString.lower()):
			path = realRoot + path[len(envString):]

	return path

def getAllDriveRoots(osName=None):
	roots = []
	if not osName:
		osName = cOS.getOS()
	for root in globalSettings.PATHS.keys():
		roots.append(globalSettings.PATHS[root][osName])

	return roots

# currently made to only handles vrscenes
def replacePathInFile(filepath, replaceText, newText=''):
	with open(filepath, 'r') as file:
		filedata = file.read()

	filedata = filedata.replace(replaceText, newText)

	with open(filepath, 'w') as file:
		file.write(filedata)

def main():
	pass
	# print getRoot('Q:/Assets/TEXTURES/Grunge/Grunge_19.jpg')
	# replacePathInFile(globalSettings.TEMP + 'render.vrscene', '/root/maya/projects/default')
	# print getEnvironmentPath('$%s', 'r:/some/path/alembic.abc')
	# print getEnvironmentPath('${%s}', 'r:/some/path/alembic.abc')
	# print getEnvironmentPath('[getenv %s]', 'r:/some/path/alembic.abc')

	print localizePath('R:/A/B/C')
	print localizePath('/ramburglar/A/B/C')
	print localizePath('N:/testCache/ramburglar/A/B/C')
	print localizePath('N:/my_cache/ramburglar/A/B/C')

	print localizePath('D:/A/B/C')

	print localizePath('Q:/A/B/C')
	print localizePath('/raidcharles/A/B/C')
	print localizePath('N:/testCache/raidcharles/A/B/C')
	print localizePath('N:/my_cache/raidcharles/A/B/C')

	print globalizePath('N:/testCache/ramburglar/A/B/C')
	print globalizePath('N:/my_cache/ramburglar/A/B/C')
	print globalizePath('N:/testCache/raidcharles/A/B/C')
	print globalizePath('N:/my_cache/raidcharles/A/B/C')

	print globalizePath('/ramburglar/A/B/C')
	print globalizePath('R:/A/B/C')
	print globalizePath('/raidcharles/A/B/C')
	print globalizePath('Q:/A/B/C')

	print localizePath('D:/A/B/C')

	# print getEnvironmentPath('$%s', 'R:/some/path/alembic.abc')
	# print getEnvironmentPath('${%s}', 'R:/some/path/alembic.abc')
	# print getEnvironmentPath('[getenv %s]', 'R:/some/path/alembic.abc')

	# print getEnvironmentPath('$%s', '/ramburglar/some/path/alembic.abc')
	# print getEnvironmentPath('${%s}', '/ramburglar/some/path/alembic.abc')
	# print getEnvironmentPath('[getenv %s]', '/ramburglar/some/path/alembic.abc')

	# print nonEnvironmentPath('[getenv %s]', '[getenv ramburglar]/some/path/alembic.abc')
	# print nonEnvironmentPath('${%s}', '${ramburglar}/some/path/alembic.abc')
	# print nonEnvironmentPath('$%s', '$ramburglar/some/path/alembic.abc')

	# print nonEnvironmentPath('[getenv %s]', '[getenv raidcharles]/some/path/alembic.abc')
	# print nonEnvironmentPath('${%s}', '${raidcharles}/some/path/alembic.abc')
	# print nonEnvironmentPath('$%s', '$raidcharles/some/path/alembic.abc')

	# print nonEnvironmentPath('[getenv %s]', '[getenv footage]/some/path/alembic.abc')
	# print nonEnvironmentPath('${%s}', '${footage}/some/path/alembic.abc')
	# print nonEnvironmentPath('$%s', '$footage/some/path/alembic.abc')

	# print getEnvironmentPath('R:/Test/abc.abc')

	# print translatePathSearch('R:\Test_Project\Workspaces\publish\caseSensitive\somefolder\\')
	# print translatePathSearch('R:\Test_Project\Workspaces\publish\caSeSenSiTive\somefolder')
	# print translatePathSearch('R:\Test_Project\Workspaces\publish\caseSensitive\somefolder')
	# print translatePathSearch('R:\Test_Project\Workspaces\publish\CASESENSITIVE\somefolder')
	# print translatePathSearch('R:\Test_Project\Workspaces\publish\CASESENSITIVE2\\')

if __name__ == '__main__':
	main()
