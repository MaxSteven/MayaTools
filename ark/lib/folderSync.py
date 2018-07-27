
# Standard modules
import os
import sys

# Our modules
import arkInit
arkInit.init()
import cOS
# import copyWrapper

'''
input:
- string file path to slave directory
- string file path to master directory

output:
- tuple of (files_copied, files_removed) where each element
is a list of strings.  On error returns nothing

notes:
- directories must be specified as correct file paths
(relative or absolute)
- permissions on files copied are preserved
- recursively copies subdirectory
- if master directory does not exist, returns None
- if slave directory does not exist, creates slave directory
'''

def folderSync(slave, master, quiet=True):
	print 'Folder Sync'

	slave = cOS.normalizeDir(slave)
	master = cOS.normalizeDir(master)

	# +- 5 seconds when comparing times
	timeBuffer = 5

	# collect master files
	filesToIgnore = [
		'Thumbs.db',
		'._.DS_Store',
		'.DS_Store',
		]
	masterFiles = []
	masterDirs = []
	for root, dirs, files in os.walk(master):
		root = cOS.normalizeDir(root)
		masterDirs.append(root)
		for f in files:
			if f not in filesToIgnore:
				masterFiles.append(root + f)

	# print 'masterFiles:', '\n'.join(masterFiles), '\n'

	# clean slave
	for root, dirs, files in os.walk(slave):
		root = cOS.normalizeDir(root)
		fileCount = len(files)

		# remove files that shouldn't be there
		for f in files:
			slaveFile = root + f
			masterFile = slaveFile.replace(slave, master)
			if masterFile not in masterFiles:
				# print 'remove:', slaveFile
				try:
					os.remove(slaveFile)
				except Exception as err:
					print 'could not remove:', slaveFile
				fileCount -= 1

		# remove directories that shouldn't be there
		masterRoot = root.replace(slave, master)
		if masterRoot not in masterDirs:
			try:
				os.rmdir(root)
				print 'removing empty directory:', root
			except Exception as err:
				print 'could not remove directory:', root

	# copy stuff that's newer
	for masterFile in masterFiles:
		slaveFile = masterFile.replace(master, slave)
		slaveRoot = cOS.getDirName(slaveFile)

		# Times that are newer are considered to be LESS THAN older times
		if not os.path.isfile(slaveFile) or \
			os.path.getmtime(masterFile) > os.path.getmtime(slaveFile) + timeBuffer:
			if not quiet:
				print 'copying:', masterFile, '>', slaveFile
			try:
				os.makedirs(slaveRoot)
			# raise anything but an exists err
			except Exception as err:
				if err.errno != 17:
					print 'error:', err
					return err
			# Copy with fast copy
			# fix: copyWrapper should handle this system check
			try:
				cOS.copy(masterFile, slaveFile)
			except Exception as err:
				print 'copy error:', err

			# if sys.platform.startswith('darwin') or sys.platform.startswith('linux'):
			# 	out = copyWrapper.copy(masterFile, slaveFile, '-pr')
			# elif sys.platform.startswith('win'):
			# 	out = copyWrapper.copy(masterFile, slaveFile, '-r')
			# if out and str(out) != '(None, None)':
			# 	print 'copy error:', out

if __name__ == '__main__':
	folderSync(sys.argv[1], sys.argv[2])
