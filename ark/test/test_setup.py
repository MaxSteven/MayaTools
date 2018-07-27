
# Standard modules
import os
from expects import *


# Our modules
import arkInit
arkInit.init()

import tryout
import ark
import cOS

class test(tryout.TestSuite):
	title = 'test/test_setup.py'

	def checkSetup(self):
		arkSetup = ark.Setup()
		arkSetup.setup()

		if cOS.isWindows():
			self.assertEqual(
				arkSetup.arkRoot,
				'c:/ie/')
			print 'ark setup.arkpython is ' + arkSetup.arkPython
			self.assertEqual(
				arkSetup.arkPython.lower(),
				'c:/python27/python.exe')
			self.assertEqual(
				arkSetup.arkPythonLib.lower(),
				'c:/python27/lib/site-packages/')

		self.assertTrue(arkSetup.configDir + 'default.json')

		self.assertTrue(not os.path.isfile(
			os.environ['USERPROFILE'] + '/_netrc'))

		# should have unique computer name
		computerName = os.environ.get('ARK_COMPUTER_NAME')
		self.assertTrue(computerName is not None)
		arkSetup.setup()
		# should stay the same
		self.assertEqual(computerName, os.environ.get('ARK_COMPUTER_NAME'))


if __name__ == '__main__':
	tryout.run(test)
