
# Standard modules
import sys
import os
import subprocess

# Our modules
import arkInit
arkInit.init()
import cOS

'''
Input:
source file (string),
destination file (string),
arguments (string)
Output:
tuple (out, err).  Strings of what the copy command
produces to stdout, stderr
'''

def copyWithSubprocess(cmd):
	process = subprocess.Popen(' '.join(cmd), shell=True)
	output = process.communicate()
	return output

# Create subdirectories needed
def makeSubdirectories(dest):
	root = cOS.getDirName(dest)
	try:
		os.makedirs(root)
	# raise anything but an exists err
	except Exception as err:
		if err.errno != 17:
			return err

def copy(source, destination, arguments=''):
	source = cOS.normalizePath(source)
	destination = cOS.normalizePath(destination)

	cmd = False
	if cOS.isLinux() or cOS.isMac():
		cmd = ['yes | cp -f', arguments, '"' + source + '"', '"' + destination + '"']
	elif cOS.isWindows():
		cmd = ['copy /b/v/y ', '"' + source + '"', '"' + destination + '"', arguments]

	# If on a supported platform
	if cmd:
		makeSubdirectories(destination)
		return copyWithSubprocess(cmd)

def copyTree(source, destination, arguments=''):
	source = cOS.normalizePath(source)
	destination = cOS.normalizePath(destination)
	# ensure trailing slash on source
	if source[-1] != '/':
		source = source + '/'
	# remove the trailing slash from destionation
	if destination[-1] == '/':
		destination = destination[:-1]


	cmd = None
	if cOS.isLinux() or cOS.isMac():
		# raise Exception('no clue about copy tree on linux or mac')
		cmd = ['yes | cp -rf', arguments, '"' + source + '"', '"' + destination + '"']
	elif cOS.isWindows():
		source = source.replace('/', '\\') + '*.*'
		destination = destination.replace('/', '\\')
		cmd = ['xcopy', '/Y', '/E', '/I', '"' + source + '"', '"' + destination + '"', arguments]

	# If on a supported platform
	if cmd:
		makeSubdirectories(destination)
		return copyWithSubprocess(cmd)

if __name__ == '__main__':
	# result = copyTree('c:/trash/copyTest/', 'c:/trash/yay/')
	# xcopy /Y /E /I "R:\Real_ONeals_s01\Final_Renders\TRO_102\EXR_Linear\TRO_102_05_0010_v013\*.*" "R:\Real_ONeals_s01\Deliverables\TRO_102\TRO_102_VFX_EXR_Linear_20151008\TRO_102_05_0010_v013"
	result = copyTree('R:/Real_ONeals_s01/Final_Renders/TRO_102/EXR_Linear/TRO_102_05_0010_v013/', 'R:/Real_ONeals_s01/Deliverables/TRO_102/TRO_102_VFX_EXR_Linear_20151008/TRO_102_05_0010_v013/')
	print result
