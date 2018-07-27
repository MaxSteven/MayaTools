
# import re
import boto
import boto.s3.connection
import tinys3
import time
import logging
import os

import arkInit
arkInit.init()
# import ieOS
import cOS

import arkUtil
import settingsManager
globalSettings = settingsManager.globalSettings()


# fix: move this stuff to a log utils file
logger = logging.getLogger('s3manager')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s: %(message)s", "%Y-%m-%d %H:%M:%S")
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)


class S3Manager(object):

	# fix: get these from somewhere secure
	bucketPrefix = 'in63u4t3-'
	s3_access_key = 'AKIAIC6XTD6Y2QFD7N4Q'
	s3_secret_key = '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'
	poolSize = 8

	def __init__(self):
		self.locations = boto.s3.connection.Location

	def connect(self, location=None):
		self.conn = boto.connect_s3(self.s3_access_key, self.s3_secret_key)
		# self.tinyConn = tinys3.Connection(self.s3_access_key, self.s3_secret_key)
		self.pool = tinys3.Pool(self.s3_access_key, self.s3_secret_key, size=self.poolSize)
		# self.setLocation(location)

	def setLocation(self, location):
		# fix: shouldn't hard code this
		if location == None:
			self.location = self.locations.USWest2
		else:
			self.location = location

	def setBucket(self, bucketName):
		allBuckets = self.listBuckets()
		self.bucketName = self.makeBucketName(bucketName)
		if self.bucketName in allBuckets:
			self.bucket = self.getBucket(bucketName)
		else:
			self.bucket = self.createBucket(bucketName)
		logger.info('bucket set: ' + self.bucketName)

	def listBuckets(self):
		return [b.name for b in self.conn.get_all_buckets()]

	def makeBucketName(self, name):
		# fix: better test
		if self.bucketPrefix not in name:
			return self.bucketPrefix + name
		return name

	def createBucket(self, name):
		logger.info('createBucket')
		bucketName = self.makeBucketName(name)
		return self.conn.create_bucket(bucketName)

	def getBucket(self, name):
		logger.info('getBucket')
		bucketName = self.makeBucketName(name)
		return self.conn.get_bucket(bucketName)

	def createKey(self, key):
		logger.info('createKey')
		k = boto.s3.key.Key(bucket=self.bucket)
		k.key = key
		return k

	def lookupKey(self, keyName):
		return self.bucket.lookup(keyName)

	def uploadFile(self, filename, replace=True, cb=None, reduced_redundancy=True):
		keyName = cOS.universalPath(filename)
		f = open(filename, 'rb')
		# headers = {}
		headers = {
					'x-amz-meta-modified': str(arkUtil.utcNow())
				  }

		if reduced_redundancy:
			headers['x-amz-storage-class'] = 'REDUCED_REDUNDANCY'

		return self.pool.upload(key=keyName,
							local_file=f,
							bucket=self.bucketName,
							headers=headers,
							close=True)

	def downloadFile(self,
						keyName,
						replaceIfOlder=False,
						confirmSuccess=True):
		key = self.lookupKey(keyName)
		if not key:
			logger.error('Could not find file: ' + keyName)
			return False

		filename = cOS.osPath(key.name)
		dirname = os.path.dirname(filename)

		if not os.path.isdir(dirname):
			os.makedirs(dirname)
			dirExists = os.path.isdir(dirname)
		else:
			dirExists = True

		if not dirExists:
			logger.error('Could not create directory: ' + filename)
			return False

		if os.path.isfile(filename):
			local_modTime = int(os.path.getmtime(filename) + time.timezone)
			remote_modTime = int(key.get_metadata('modified'))
			if remote_modTime <= local_modTime and not replaceIfOlder:
				logger.info('Newer: ' + filename)
				return True

		logger.info('Copying: ' + filename)
		key.get_contents_to_filename(filename)
		if confirmSuccess:
			return os.path.isfile(filename)
		return True

if __name__ == '__main__':
	# boto: 	22.8mb 		169 sec = .134 mb/s
	# ftp: 		22.8mb 		 68 sec = .335 mb/s
	# tinys3: 	22.8mb 		 52 sec = .438 mb/s

	renderFile = 'Q:/Test_Project/WORKSPACES/render_test/3D/maxwell_v01_ghm.max'
	saveLocation = 'Q:/Test_Project/WORKSPACES/render_test_s3/3D/simpleTest_v001_ghm.mxs'

	startTime = time.time()
	s3 = S3Manager()
	s3.connect()
	logger.info('connected in: %.3f second' % (time.time() - startTime))
	s3.setBucket('qdrive')
	logger.info('bucket created / found in: %.3f second' % (time.time() - startTime))

	response = s3.uploadFile(renderFile)

	# for r in s3.pool.as_completed([request]):
	# 	help(r)
	# 	print r
	# result = response.result()
	# help(result)

	logger.info('Upload started: %s' % renderFile)

	lastUpdate = uploadStart = time.time()
	while response.running():
		if time.time() - lastUpdate > 5:
			logger.info('Uploading: ' + renderFile)
			lastUpdate = time.time()

	logger.info('file stored in: %.3f second' % (time.time() - startTime))
