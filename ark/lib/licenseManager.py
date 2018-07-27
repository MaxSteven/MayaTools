
import arkInit
arkInit.init()

import cOS

import settingsManager
globalSettings = settingsManager.globalSettings()

def getHoudiniLicenseServer():
	out, err = cOS.getCommandOutput(globalSettings.HOUDINI_LICENSE_EXE + ' -l')
	if not out:
		return False
	out = out.split('\n')
	return out[2].split(':')[-1].strip()

def setHoudiniLicenseServer(server):
	out, err = cOS.getCommandOutput(globalSettings.HOUDINI_LICENSE_EXE + ' -S ' + server)
	print out

def main():
	getHoudiniLicenseServer()
	setHoudiniLicenseServer('172.16.0.29')
	getHoudiniLicenseServer()
	setHoudiniLicenseServer('iegrant')
	getHoudiniLicenseServer()



if __name__ == '__main__':
	main()
