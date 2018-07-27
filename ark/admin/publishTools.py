# Standard modules
import argparse
import sys

# Our modules
import arkInit
arkInit.init()
arkRoot = arkInit.arkRoot
import moduleTools
import arkUtil
import settingsManager
globalSettings = settingsManager.globalSettings()

publishUsage = ('publishTools.py\n'
				'[-h HELP] [--modules MODULES] destination\n'
				'* --destination: (optional) directory to publish tools to. Default to R:/Assets/Tools/install/ie\n'
				'* --modules: (optional) Modules to publish. Else will use default set\n'
				'* --quiet: (optional) Default off (Verbose).'
				'* MODULES must be comma-delimited (no spaces)\n'
				'Examples:\n'
				'* python publishTools.py c:/ie/temp/published\n'
				'* python publishTools.py --modules cOS,translators,shepherd c:/ie/temp/published\n'
				)

parser = argparse.ArgumentParser(description='Publish all tools with filtering to destination path', usage=publishUsage)
parser.add_argument('--destination', help='(Optional) Directory to publish tools to. Default will use R:/Assets/Tools/install/ie')
parser.add_argument('--modules', help='(Optional) Modules to publish. Else will use default set')
parser.add_argument('--quiet', action='store_true', help='(Optional) Log less output')

# defaultModules and kwargs now set in default.json
defaultModules = globalSettings.DEFAULT_MODULES
toolsFilter = globalSettings.TOOLS_FILTER

def main(argv):
	args = parser.parse_args()
	if args.modules:
		# If args.modules set, verify syntax
		badChars = '[](){}'
		if any((char in badChars) for char in args.modules):
			print '\nSyntax: %s invalid input.' % args.modules
			sys.exit(publishUsage)
		args.modules = arkUtil.parseCommaArray(args.modules)
	if not args.modules:
		args.modules = defaultModules
	if not args.destination:
		args.destination = "%sAssets/Tools/install/ie" % globalSettings.SHARED_ROOT
	if not args.quiet:
		args.quiet = False

	print 'defaultModules:', defaultModules
	print 'toolsFilter:', toolsFilter

	moduleTools.publishTools(args.destination, args.modules, args.quiet, **toolsFilter)

if __name__ == '__main__':
	main(sys.argv)
