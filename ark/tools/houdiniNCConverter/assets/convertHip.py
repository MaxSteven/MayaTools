import os
import sys
import cOS
import json
import subprocess
import hou

def main():

	args = cOS.getArgs(sys.argv)

	options = json.loads(args['options'].replace("'",'"'))

	cmdFile = options['cmdFile']
	exportLoc = options['exportLoc']

	if not cmdFile or cmdFile == '' or not os.path.exists(cmdFile):
		print "ERROR: CMD file not found"
		return

	if not exportLoc or exportLoc == '' or not os.path.exists(exportLoc):
		print "ERROR: Export location not found"
		return

	info = cOS.getPathInfo(cmdFile)
	name = info['name']

	hou.hscript('cmdread ' + cmdFile)
	hou.hipFile.save(exportLoc + name + '.hip')

if __name__ == '__main__':
	main()