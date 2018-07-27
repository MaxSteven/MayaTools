
# Standard modules
import os
import shutil

# from expects import *

# Our modules
import arkInit
arkInit.init()

import tryout
import moduleTools
import cOS

class test(tryout.TestSuite):
	title = 'test/test_compileTools.py'

	def compileAllModules(self):
		extension = cOS.getExtension(__file__)
		compiledFile = __file__.replace('.' + extension, '.pyc')
		print 'compiledFile:', compiledFile
		try:
			os.remove(compiledFile)
		except:
			if os.path.isfile(compiledFile):
				raise

		moduleTools.compileAllModules()
		self.assertTrue(os.path.isfile(compiledFile))

	def getModuleNames(self):
		names = moduleTools.getModuleNames()
		print('names:', names)
		self.assertIn('ark', names)
		self.assertIn('coren', names)
		self.assertIn('weaver', names)

	def getModuleOptions(self):
		options = moduleTools.getModuleOptions('ark')
		print('options:', options)
		self.assertIn('folder_exclude_patterns', options)

	def getModuleFiles(self):
		# kwargs = {'fileIncludes':['*.pyc']}
		# files = moduleTools.getModuleFiles('ark', **kwargs)

		files = moduleTools.getModuleFiles('ark')
		print('files:\n')
		for file in files:
			print (file)
			self.assertTrue(not '.git' in file)

		# self.assertIn('folder_exclude_patterns', options)

	def publishTools(self):
		testDest = 'C:/temp/testPublish'
		testModules = ['arkMath', 'cOS']
		moduleTools.publishTools(testDest, testModules)
		files = cOS.collectAllFiles(testDest)
		for file in files:
			path = file['path']
			print path
			self.assertTrue(not '.git' in path)
			self.assertTrue(not path.endswith('.py'))

		# Delete test files
		try:
			shutil.rmtree(testDest)
		except Exception:
			raise

		self.assertTrue(not os.path.isdir(testDest))

if __name__ == '__main__':
	tryout.run(test)
