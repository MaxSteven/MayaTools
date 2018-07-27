import unittest
import os, sys, inspect, subprocess
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

import copyWrapper

class TestCopy(unittest.TestCase):

	def setUp(self):
		os.system('mkdir sandbox')
		os.system('echo "This is the first test file." | cat >> sandbox/file1')
		os.system('echo "This file should be overwritten" | cat >> sandbox/file3')

	def tearDown(self):
		os.system('rm -rf sandbox')

	def test_copy_single_file_exists(self):
		copyWrapper.copy('sandbox/file1', 'sandbox/file2', '')
		self.assertTrue(os.path.isfile('sandbox/file2'))

	def test_copy_single_file_matches_content(self):
		copyWrapper.copy('sandbox/file1', 'sandbox/file2', '')
		self.assertEqual(subprocess.check_output(['cat', 'sandbox/file2']), subprocess.check_output(['cat', 'sandbox/file1']))

	def test_error_file_does_not_exist(self):
		output = copyWrapper.copy('sandbox/DOESNTEXIST', 'sandbox/file2', '')
		self.assertTrue(output)

	def test_file_overwrite(self):
		copyWrapper.copy('sandbox/file1', 'sandbox/file3', '')
		self.assertEqual(subprocess.check_output(['cat', 'sandbox/file3']), subprocess.check_output(['cat', 'sandbox/file1']))

	def test_create_subdirectories(self):
		copyWrapper.copy('sandbox/file1', 'sandbox/testdir1/testdir2/testdir3/file2', '')
		self.assertEqual(subprocess.check_output(['cat', 'sandbox/testdir1/testdir2/testdir3/file2']), subprocess.check_output(['cat', 'sandbox/file1']))

if __name__ == '__main__':
	unittest.main()