
# Standard modules
# import os
# import sys
# import requests

# Our modules
import arkInit
arkInit.init()
import arkUtil

import tryout
from caretaker import assetManager


class test(tryout.TestSuite):

	def setUp(self):
		pass

	# trash everything
	##################################################
	def tearDown(self):
		pass

	# actual tests
	##################################################

	def testAssetManager(self):
		paths = [
			'r:/Aeroplane/Workspaces/AER_Video/AER_Airplane_050/Publish/SprayPaintNozzle/',
			'r:/Aeroplane/Workspaces/AER_Video/AER_Airplane_050/Publish/SprayPaintNozzle/SprayPaintNozzle_1001-1020_v0007.abc',
			'r:/Caretaker/Assets/12345/12345678900000/22222222222/'
		]
		relativePath = '12345/12345678900000/22222222222/'
		for p in paths:
			print p
			print assetManager.getDataFromPath(p)
		print relativePath
		print assetManager.getDataFromPath(relativePath, absolutePath = False)

		self.assertTrue(assetManager.isAssetPath(paths[2]))

		self.assertEqual(arkUtil.parse('{this}', 'works').get('this'), 'works')
		self.assertEqual(arkUtil.parse('/Publish/{asdf}', '/Publish/thing').get('asdf'), 'thing')
		self.assertEqual(arkUtil.parse('does It {work}', 'does It asdf').get('work'), 'asdf')

		self.assertTrue(arkUtil.matchesData(assetManager._renderPathAbsoluteShort, {'project': 'a', 'sequence': 'b', 'shot': 'c', 'versionName': 'd'}))
		self.assertFalse(arkUtil.matchesData(assetManager._renderPathAbsoluteShort, {'project': 'a', 'shot': 'c', 'versionName': 'd'}))
		self.assertTrue(arkUtil.matchesData(assetManager._renderPathAbsoluteShort, {'project': 'a', 'sequence': 'b', 'shot': 'c', 'versionName': 'd', 'extra': 'e'}))

		self.assertTrue(assetManager.isAbsolutePath('r:/'))
		self.assertTrue(assetManager.isAbsolutePath('f:/'))
		self.assertTrue(assetManager.isAbsolutePath('q:/'))


if __name__ == '__main__':
	tryout.run(test)
