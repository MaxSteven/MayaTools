# import copy
import os
import sys
import argparse

import arkInit
arkInit.init()

import cOS

os.environ['ARK_CURRENT_APP'] = 'none'
from shepherd import submit
import shepherd

import settingsManager
globalSettings = settingsManager.globalSettings()

def process(filepath, options):
	# print 'filepath:', filepath

	pathInfo = cOS.getPathInfo(filepath)
	name = pathInfo['basename']

	# set up options
	jobOptions = {
		'submitToFarm': True
	}

	# this is how defaults are done
	jobOptions.update(options)

	print 'options:', jobOptions

	if not jobOptions.get('frameRange'):
		jobOptions['frameRange'] = '1001'

	if not jobOptions.get('fps'):
		jobOptions['fps'] = 24

	# make a shepherdJob
	jobInfo = {
		'program': 'houdini',
		'name': name,
		'sourceFile': filepath,
		'singleNode': True,
		'options': {'frameRange': jobOptions['frameRange']},
		'fps': jobOptions['fps'],
		'output': filepath.replace('.abc', '_processed.abc'),
		'priority': 100,
		'jobType': 'Houdini_ProcessAlembic',
	}

	# render it with Sheep
	if jobOptions['submitToFarm']:
		submit.submitJob(jobInfo)
	else:
		shepherd.runJob(jobInfo)

def main(args):
	parser = argparse.ArgumentParser()
	parser.add_argument('-o' )
	parser.add_argument('-fr')
	parser.add_argument('-fps')
	parser.add_argument('-farm')
	args = parser.parse_args()

	options = {
		'frameRange': args.fr,
		'fps': args.fps,
		'submitToFarm': not args.farm or 'true' in args.farm.lower(),
	}
	
	process(args.o, options)

if __name__ == '__main__':
	main(sys.argv)
