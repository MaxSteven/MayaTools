
# Our modules
import arkInit
arkInit.init()

import tryout
import cOS

import pathManager

class test(tryout.TestSuite):

	def setOS(self):
		if cOS.isWindows():
			self.assertEqual(pathManager.os, 'windows')
		elif cOS.isLinux():
			self.assertEqual(pathManager.os, 'linux')
		elif cOS.isMac():
			self.assertEqual(pathManager.os, 'mac')

	def translatPath_windows(self):
		pathManager.setOS('windows')

		result = pathManager.translatePath('q:/some/path')
		self.assertEqual(
			result,
			'q:/some/path')

		result = pathManager.translatePath('q:/some/footage/path')
		self.assertEqual(
			result,
			'q:/some/footage/path')

		result = pathManager.translatePath('/ramburglar/some/footage/path')
		self.assertEqual(
			result,
			'r:/some/footage/path')

		# manually specify linux os
		result = pathManager.translatePath('/ramburglar/some/footage/path', 'linux')
		self.assertEqual(
			result,
			'/ramburglar/some/footage/path')

		result = pathManager.translatePath('Q:\\')
		self.assertEqual(
			result,
			'q:/')

		result = pathManager.translatePath('R:/someFile.txt')
		self.assertEqual(
			result,
			'r:/someFile.txt')

	def translatPath_linux(self):
		pathManager.setOS('linux')
		result = pathManager.translatePath('q:/some/path')
		self.assertEqual(
			result,
			'/raidcharles/some/path')

		result = pathManager.translatePath('q:/some/footage/path')
		self.assertEqual(
			result,
			'/raidcharles/some/footage/path')

		result = pathManager.translatePath('/ramburglar/some/footage/path')
		self.assertEqual(
			result,
			'/ramburglar/some/footage/path')

		# manually specify window os
		result = pathManager.translatePath('/ramburglar/some/footage/path', 'windows')
		self.assertEqual(
			result,
			'r:/some/footage/path')

		result = pathManager.translatePath('Q:\\')
		self.assertEqual(
			result,
			'/raidcharles/')

		result = pathManager.translatePath('R:/someFile.txt')
		self.assertEqual(
			result,
			'/ramburglar/someFile.txt')

	def translatPath_mac(self):
		pathManager.setOS('mac')
		result = pathManager.translatePath('q:/some/path')
		self.assertEqual(
			result,
			'/Volumes/raidcharles_work/work/some/path')

		result = pathManager.translatePath('q:/some/footage/path')
		self.assertEqual(
			result,
			'/Volumes/raidcharles_work/work/some/footage/path')

		result = pathManager.translatePath('/ramburglar/some/footage/path')
		self.assertEqual(
			result,
			'/Volumes/ramburglar_work/some/footage/path')

		# manually specify window os
		result = pathManager.translatePath('/ramburglar/some/footage/path', 'windows')
		self.assertEqual(
			result,
			'r:/some/footage/path')

		result = pathManager.translatePath('Q:\\')
		self.assertEqual(
			result,
			'/Volumes/raidcharles_work/work/')

		result = pathManager.translatePath('R:/someFile.txt')
		self.assertEqual(
			result,
			'/Volumes/ramburglar_work/someFile.txt')


if __name__ == '__main__':
	tryout.run(test)
