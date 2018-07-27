import os
import sys
import cOS
import json
import subprocess
import hou

def main():

	args = cOS.getArgs(sys.argv)
	options = json.loads(args['options'].replace("'",'"'))

	ncFile = options['ncFile']
	cmdFile = options['cmdFile']
	exportLoc = options['exportLoc']

	if ncFile == None or ncFile == '' or not os.path.exists(ncFile):
		print "ERROR: Export location not found"
		return

	if cmdFile == None or cmdFile == '':
		print "ERROR: CMD file not found"
		return

	if exportLoc == None or exportLoc == '' or not os.path.exists(exportLoc):
		print "ERROR: Export location not found"
		return

	hou.hipFile.load(ncFile)
	hou.hscript('opscript -G -r / > ' + cmdFile)

	appVersion = hou.applicationVersionString()
	file = "C:\\Program Files\\Side Effects Software\\Houdini " + appVersion + "\\bin\\hython2.7.exe"
	script = "C:\\ie\\ark\\tools\\houdiniNCConverter\\assets\\convertHip.py"
	options = {
		'cmdFile': str(cmdFile),
		'exportLoc': str(exportLoc)
	}
	subprocess.call([file, script, "-options", str(options)])

if __name__ == '__main__':
	main()