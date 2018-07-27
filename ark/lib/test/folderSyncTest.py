import unittest
import time
import os, sys, inspect, subprocess
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

import folderSync

class TestCopy(unittest.TestCase):

	def setUp(self):
		#Delay between file creation because ctime only goes down to seconds
		os.system('mkdir testdir1')
		os.system('mkdir testdir2')
		os.system('echo "File1 in testdir1 made before File1 in testdir2" | cat >> testdir1/file1')
		time.sleep(1)
		os.system('echo "File1 in testdir2 made after File1 in testdir1" | cat >> testdir2/file1')
		time.sleep(1)
		os.system('echo "File2 in testdir2 made before File2 in testdir1" | cat >> testdir2/file2')
		time.sleep(1)
		os.system('echo "File2 in testdir1 made after File2 in testdir2" | cat >> testdir1/file2')
		time.sleep(1)
		os.system('echo "File3 in testdir1 made before File3 in testdir2" | cat >> testdir1/file3')
		time.sleep(1)
		os.system('echo "File3 in testdir2 made after File3 in testdir1" | cat >> testdir2/file3')
		time.sleep(1)
		os.system('echo "File4 in testdir2 should be deleted." | cat >> testdir2/file4')
		time.sleep(1)
		os.system('echo "File5 in testdir1 should be copied into testdir2." | cat >> testdir1/file5')

	def tearDown(self):
		os.system('rm -rf testdir*')

	def test_file1_testdir1(self):
		folderSync.folderSync('testdir2', 'testdir1')
		self.assertEqual(subprocess.check_output(['cat', 'testdir1/file1']), '"File1 in testdir1 made before File1 in testdir2" \r\n')

	def test_file2_testdir1(self):
		folderSync.folderSync('testdir2', 'testdir1')
		self.assertEqual(subprocess.check_output(['cat', 'testdir1/file2']), '"File2 in testdir1 made after File2 in testdir2" \r\n')

	def test_file3_testdir1(self):
		folderSync.folderSync('testdir2', 'testdir1')
		self.assertEqual(subprocess.check_output(['cat', 'testdir1/file3']), '"File3 in testdir1 made before File3 in testdir2" \r\n')

	def test_file1_testdir2(self):
		folderSync.folderSync('testdir2', 'testdir1')
		self.assertEqual(subprocess.check_output(['cat', 'testdir2/file1']), '"File1 in testdir2 made after File1 in testdir1" \r\n')

	def test_file2_testdir2(self):
		folderSync.folderSync('testdir2', 'testdir1')
		self.assertEqual(subprocess.check_output(['cat', 'testdir2/file2']), subprocess.check_output(['cat', 'testdir1/file2']))

	def test_file3_testdir2(self):
		folderSync.folderSync('testdir2', 'testdir1')
		self.assertEqual(subprocess.check_output(['cat', 'testdir2/file3']), '"File3 in testdir2 made after File3 in testdir1" \r\n')

	def test_file4_testdir2(self):
		folderSync.folderSync('testdir2', 'testdir1')
		self.assertTrue(not os.path.isfile('testdir2/file4'))

	def test_file5_testdir2(self):
		folderSync.folderSync('testdir2', 'testdir1')
		self.assertEqual(subprocess.check_output(['cat', 'testdir2/file5']), subprocess.check_output(['cat', 'testdir1/file5']))

	def test_nonexistent_slave(self):
		folderSync.folderSync('testdir3', 'testdir1')
		self.assertEqual(len(subprocess.check_output(['ls', 'testdir3']).split()), 4)

	def test_nonexistent_master(self):
		ret = folderSync.folderSync('testdir2', 'DOESNTEXIST')
		self.assertEqual(ret, None)

	def test_forward_slash_at_end(self):
		folderSync.folderSync('testdir2/', 'testdir1/')
		self.assertEqual(subprocess.check_output(['cat', 'testdir2/file2']), subprocess.check_output(['cat', 'testdir1/file2']))

	def test_backslash_at_end(self):
		folderSync.folderSync('testdir2\\', 'testdir1\\')
		self.assertEqual(subprocess.check_output(['cat', 'testdir2/file2']), subprocess.check_output(['cat', 'testdir1/file2']))


if __name__ == '__main__':
	unittest.main()