# Our modules
import arkInit
arkInit.init()

import cOS
import os
import translators
translator = translators.getCurrent()

import settingsManager
globalSettings = settingsManager.globalSettings()

def main():
	mayaExecute = 'C:/Program Files/Autodesk/Maya2016/bin/mayapy.exe'

	testCommand = [
		'"' + mayaExecute + '"',
		'"' + cOS.getDirName(os.path.abspath(__file__)) + 'test_mayaTranslator/runMayaTests.py' + '"',
	]
	testCommand = ' '.join(testCommand)
	out, err = cOS.getCommandOutput(testCommand)
	if out:
		print out
	if err:
		print err

if __name__ == '__main__':
	main()