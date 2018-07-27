
# Our modules
import arkInit
arkInit.init()

import cOS
import translators
translator = translators.getCurrent()

import settingsManager
globalSettings = settingsManager.globalSettings()

def main():
	testCommand = [
		'"' + globalSettings.NUKE_EXE + '"',
		'-V','2',
		'-i',
		'-t', cOS.getDirName(__file__) + 'test_nukeTranslator/runNukeTests.py',
	]
	testCommand = ' '.join(testCommand)
	print testCommand
	out, err = cOS.getCommandOutput(testCommand)
	if out:
		print out
	if err:
		print err

if __name__ == '__main__':
	main()
