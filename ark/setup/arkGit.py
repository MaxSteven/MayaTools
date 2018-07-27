
import arkInit
arkInit.init()
import os
import cOS
import errno
import subprocess
import re
import shutil

# duplicated from cOS
def normalizeDir(path):
	'''
	Dirs always use forward slashses and have a trailing slash.
	'''
	path = unixPath(path)

	# lower case drive leters
	if path[1] == ':':
		path = path[0].lower() + path[1:]

	if path[-1] != '/':
		path += '/'

	return path

# duplicated from cOS
def unixPath(path):
	'''
	Changes backslashes to forward slashes and
	removes successive slashes, ex \\ or \/
	'''
	# lower case drive leters
	if path[1] == ':':
		path = path[0].lower() + path[1:]

	return re.sub(r'[\\/]+', '/', path)

# duplicated in Setup currently
def getCommandOutput(command, **kwargs):
	try:
		out = subprocess.check_output(
			command,
			stderr=subprocess.STDOUT,
			**kwargs)
		if out[-1] == '\n':
			out = out[:-1]
		return out.lower()
	except subprocess.CalledProcessError as err:
		return err.out.lower()
	except:
		return False

def ensureGlobalConfig(key, value):
	# set name if not already set
	out, err = getCommandOutput('git config --global --get ' + key)
	if not out:
		command = 'git config --global user.name "' + value + '"'
		print 'Setting git', key,'to:', value
		out, err = getCommandOutput(command)
	else:
		print 'git', key, 'already set to:', out

def removeFile(path):
	try:
		os.remove(path)
	except OSError as err:
		# raise any error that's not "doesn't exist"
		if err.errno != errno.ENOENT:
			raise

def removeFolder(path):
	try:
		shutil.rmtree(path)
	except:
		# raise the error if the directory is still there
		if os.path.isdir(path):
			raise

def hardReset(path, clean=False):
	lockFile = os.path.join(path, '.git','index.lock')
	removeFile(lockFile)
	getCommandOutput('git reset --hard', cwd=path)
	getCommandOutput('git checkout master', cwd=path)
	out, err = getCommandOutput('git reset --hard', cwd=path)
	if clean:
		getCommandOutput('git clean -xdf', cwd=path)
	return out

def cloneRepo(path, repo):
	print 'Cloning:', repo, 'to:', path
	getCommandOutput('git clone ' + repo, cwd=path)

def pullRepo(path, repo):
	print 'Updating:', repo, 'at:', path
	getCommandOutput('git pull ' + repo, cwd=path)

def updateRepo(path, force=False):
	'''
	Update or clone a repository on disk:
		- if path is a file not a directory return false
			- if force is true the file will be removed
			and a fresh repo will be cloned
		- if path is a directory but not a repo return false
			- if force is true the directory will be removed
			and a fresh repo will be cloned
		- if path is a repo but it's lost it's git link delete
		delete it and clone a fresh one
		- if path doesn't exist clone a fresh repo
		- if path is a repo and branch is master hard reset
		and git pull
		- if path is a repo and branch isn't master
		do nothing because
	'''

	# if the path is a file not a folder
	exists = os.path.exists(path)
	isDir = os.path.isdir(path)
	if exists and not isDir:
		# if we're not forcing it, just bail
		if not force:
			print 'arkGit:', path, 'is a file not a path'
			return False

		# otherwise remove the file and clone a fresh repo
		removeFile(path)
		return cloneRepo(path)


	# if the path is a folder but not a git repo
	gitFolder = os.path.join(path, '.git')
	out, err = getCommandOutput('git status')
	isARepo = os.path.isdir(gitFolder) and \
		'on branch' in out

	if not isARepo:
		# if we're not forcing it, just bail
		if not force:
			print 'arkGit:', path, 'is not a git repository'
			return False

		# otherwise remove the folder and clone a fresh repo
		removeFolder(path)
		return cloneRepo(path)


	origin = getCommandOutput(
		'git config --get remote.origin.url',
		cwd=path)
	# if the directory has lost it's remote
	# remove the folder and clone a fresh repo
	if not origin:
		removeFolder(path)
		return cloneRepo(path)

	# get the branch we're on
	out, err = getCommandOutput('git branch', cwd=path)
	branch = False
	for line in out.split('\n'):
		if line.startswith('* '):
			branch = line[2:]
	print 'branch:', branch

	# if we're on master reset and pull the changes
	if branch and branch == 'master':
		out = hardReset()
		return pullRepo()

	# if we're not on master, just bail
	print "Not on master, you're on your own..."
	return False

def tag(version, message, cwd):
	tagCommand = [
			'git tag',
			'-a',
			version,
			'-m',
			message
			]
	cOS.getCommandOutput(' '.join(tagCommand), cwd)

def getMostRecentTag(cwd):
	return cOS.getCommandOutput('git describe --tags', cwd)[0]

def pushTags(cwd):
	cOS.getCommandOutput('git push --tags', cwd)

def main():
	# getRepoStatus('c:/ie/ark')
	out, err = getCommandOutput('git status', cwd='c:/jklsdf')
	print 'out:', out

if __name__ == '__main__':
	main()
