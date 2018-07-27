
# import sys
import os
# import glob
# import re
import json
# import time

import arkInit
arkInit.init()
# import ieOS
import cOS
import arkUtil
import settingsManager
globalSettings = settingsManager.globalSettings()
# import nuke
# import arkNuke
# import nukeUtil

class NukeScript(object):

	args = False
	options = {}

	def __init__(self):
		pass

	def parseArgs(self, args):
		print 'Nuke Script: parseArgs'

		"""takes an array of arguments
			1 - input file
			2 - output file
			3 - JSON dictionary of options"""
		args = cOS.getArgs(args)
		print 'raw args:', args

		if 'options' in args:
			self.options = json.loads(args['options'].replace("'",'"'))
			self.options = arkUtil.unicodeToString(self.options)
		else:
			self.options = {}

		try:
			print 'trying'
			with open(globalSettings.TEMP + 'nukePythonStartup') as f:
				info = json.load(f)
			print 'updating:', info
			self.options.update(info)

		except Exception as err:
			if os.path.isfile(globalSettings.TEMP + 'nukePythonStartup'):
				print err


		print 'options:', self.options

	def getOption(self, name, default=None):
		if name in self.options:
			return self.options[name]
		return default
