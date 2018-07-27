
# Our modules
import arkInit
arkInit.init()

import moduleTools
import cOS



def main():
	modules = moduleTools.getModuleNames()

	for module in modules:
		print '\nUpdating:', module
		out, err = cOS.getCommandOutput(
			'git pull --rebase',
			cwd=arkInit.arkRoot + module)
		if out:
			print out
		if err:
			print err

	print 'Running Setup'

	import sys
	sys.path.append(arkInit.arkRoot + '/ark/setup')
	import Setup
	Setup.main()


if __name__ == '__main__':
	main()
