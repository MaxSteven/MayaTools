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
	houdiniExecute = 'C:/Program Files/Side Effects Software/Houdini 15.0.434/bin/hython.exe'

	testCommand = [
		'"' + houdiniExecute + '"',
		'"' + cOS.getDirName(os.path.abspath(__file__)) + 'test_houdiniTranslator/runHoudiniTests.py' + '"',
	]
	testCommand = ' '.join(testCommand)
	out, err = cOS.getCommandOutput(testCommand)
	if out:
		print out
	if err:
		print err

if __name__ == '__main__':
	main()