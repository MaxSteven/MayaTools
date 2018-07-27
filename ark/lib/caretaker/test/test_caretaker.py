
# Standard modules
# import os
# import sys
# import requests

# Our modules
import arkInit
arkInit.init()

from caretaker import Caretaker
import database
# import arkUtil
import tryout


class test(tryout.TestSuite):

	def setUp(self):
		self.caretaker = Caretaker()
		self.database = database.Database()
		self.database.connect()

		# project
		##################################################
		self.database.remove('project')\
			.where('name','is','CTTT_Project1')\
			.multiple()\
			.execute()

		self.projectOne = self.database\
			.create('project',
				{
					'name': 'CTTT_Project1',
					'folderName': 'CTTT_Project1Folder',
					'fps': 23.976,
					'shortName': 'CTTT1'
				})\
			.execute()[0]
		self.projectOneID = self.projectOne['_id']

		# sequence
		##################################################
		self.database.remove('sequence')\
			.where('name','is','CTTT_Seq1')\
			.multiple()\
			.execute()

		self.sequenceOne = self.database\
			.create('sequence',
				{
					'name': 'CTTT_Seq1',
					'project': self.projectOneID,
				})\
			.execute()[0]

		# shots
		##################################################
		self.database.remove('shot')\
			.where('name','is','CTTT1_0010')\
			.multiple()\
			.execute()

		self.shotOne = self.database\
			.create('shot',
				{
					'name': 'CTTT1_0010',
					'project': self.projectOneID,
					'frameCount': 64,
					'startFrame': 1001,
					'endFrame': 1064,
					'sequence': self.sequenceOne['_id'],
				})\
			.execute()[0]
		self.shotOneID = self.shotOne['_id']

		self.database.remove('shot')\
			.where('name','is','CTTT1_0020')\
			.multiple()\
			.execute()

		self.database\
			.create('shot',
				{
					'name': 'CTTT1_0020',
					'project': self.projectOneID,
					'frameCount': 275,
					'startFrame': 1001,
					'endFrame': 1275,
					'sequence': self.sequenceOne['_id'],
				 })\
			.execute()

		# asset types
		##################################################
		self.database.remove('assetType')\
			.where('name','is','CTTT_AssetType1')\
			.multiple()\
			.execute()
		self.assetType1 = self.database\
			.create('assetType',
				{
					'name': 'CTTT_AssetType1',
					'path': 'somePath/testPath'
				})\
			.execute()

		self.assetTypeOneID = self.assetType1[0]['_id']

		self.database.remove('assetType')\
			.where('name','is','CTTT_AssetType2')\
			.multiple()\
			.execute()
		assetType2 = self.database\
			.create('assetType',
				{
					'name': 'CTTT_AssetType2',
					'path': 'someOtherPath/otherPath'
				})\
			.execute()
		self.assetType2ID = assetType2[0]['_id']

		# assets
		##################################################
		self.database.remove('asset')\
			.where('name','is','CTTT_Asset1')\
			.multiple()\
			.execute()
		asset1 = self.database\
			.create('asset',
				{
					'name': 'CTTT_Asset1',
					'type': self.assetTypeOneID,
					'project': self.projectOneID,
					'shot': self.shotOneID,
				})\
			.execute()
		self.asset1 = asset1[0]
		self.asset1ID = self.asset1['_id']


		self.database.remove('asset')\
			.where('name','is','CTTT_Asset2')\
			.multiple()\
			.execute()
		asset2 = self.database\
			.create('asset',
				{
					'name': 'CTTT_Asset2',
					'type': self.assetType2ID,
					'project': self.projectOneID,
					'shot': self.shotOneID,
				})\
			.execute()
		self.asset2ID = asset2[0]['_id']

		# versions
		##################################################
		self.database.remove('version')\
			.where('path','is','asset/path/1')\
			.multiple()\
			.execute()
		self.database\
			.create('version',
				{
					'asset': self.asset1ID,
					'path': 'asset/path/1',
					'number': 8,
				}).execute()

		self.database.remove('version')\
			.where('path','in',['assetpath/2','assetpath/3','assetpath/4'])\
			.multiple()\
			.execute()

		self.database\
			.create('version',
				{
					'asset': self.asset2ID,
					'path': 'assetpath/2',
				}).execute()

		self.version1 = self.database\
			.create('version',
				{
					'asset': self.asset1ID,
					'number': 1,
					'path': 'assetpath/3',
				})\
			.execute()

		self.database\
			.create('version',
				{
					'asset': self.asset1ID,
					'number': 4,
					'path': 'assetpath/4',
				})\
			.execute()


	# trash everything
	##################################################
	def tearDown(self):
		self.database = database.Database()
		self.database.remove('shot')\
			.where('name', 'in', ['CTTT1_0010','CTTT1_0020'])\
			.multiple()\
			.execute()
		self.database.remove('assetType')\
			.where('name', 'in', ['CTTTest_Asset1', 'CTTT_AssetType2'])\
			.multiple()\
			.execute()
		self.database.remove('asset')\
			.where('name', 'in', ['CTTT_Asset1', 'CTTT_Asset2', 'CTTT1_0020'])\
			.multiple()\
			.execute()
		self.database.remove('project')\
			.where('name', 'is', 'CTTT_Project1')\
			.multiple()\
			.execute()
		self.database.remove('version')\
			.where('asset', 'is', self.asset1ID)\
			.multiple()\
			.execute()


	# actual tests
	##################################################
	def getProjectFromFolder(self):
		project = self.caretaker\
			.getProjectFromFolder('CTTT_Project1Folder')

		self.assertEqual(project['name'], 'CTTT_Project1')
		self.assertEqual(project['fps'], 23.976)

	def returnNoneForABadFolderName(self):
		project = self.caretaker\
			.getProjectFromFolder('falseName')

		self.assertTrue(project is None)

	def getShotFromName(self):
		shot = self.caretaker\
			.getShotFromName('CTTT1_0010')

		self.assertEqual(shot['name'], 'CTTT1_0010')
		self.assertEqual(shot['frameCount'], 64)

		shot = self.caretaker\
			.getShotFromName('CTTT1_0020')

		self.assertEqual(shot['name'], 'CTTT1_0020')
		self.assertEqual(shot['frameCount'], 275)

	def returnNoneForABadShotName(self):
		shot = self.caretaker.getShotFromName('falseName')

		self.assertTrue(shot is None)

		project = self.caretaker\
			.getProjectFromFolder('CTTT_Project1Folder')
		shot = self.caretaker\
			.getShotFromName('3242312', project['_id'])

		self.assertTrue(shot is None)

	def getShotFromNameAndProject(self):
		shot = self.caretaker\
			.getShotFromName('CTTT1_0020')

		self.assertEqual(shot['name'], 'CTTT1_0020')
		self.assertEqual(shot['frameCount'], 275)
		self.assertEqual(shot['project'], self.projectOneID)

	def returnNoneForABadProjectName(self):
		shot = self.caretaker\
			.getShotFromName('CTTT1_0020', 'blahalasdfiwer')

		self.assertTrue(shot is None)

	def getShotInfo(self):
		shot = self.caretaker.getShotFromName('CTTT1_0010')
		shotInfo = self.caretaker.getShotInfo(shot['_id'])

		self.assertEqual(shotInfo['name'], 'CTTT1_0010')
		self.assertEqual(shotInfo['startFrame'], 1001)
		self.assertEqual(shotInfo['project']['name'], 'CTTT_Project1')

	def returnNoneInfoForABadShot(self):
		othershot =  self.caretaker\
			.getShotInfo('adfweerqfadfzvce')

		self.assertTrue(othershot is None)

	def getAssetsFromShot(self):
		shot = self.caretaker.getShotFromName('CTTT1_0010')
		assets = self.caretaker.getAssetsFromShot(shot['_id'])

		self.assertEqual(len(assets), 2)
		self.assertTrue(assets[0]['name'] in ['CTTT_Asset1', 'CTTT_Asset2'])
		self.assertTrue(assets[1]['name'] in ['CTTT_Asset1', 'CTTT_Asset2'])
		self.assertNotEqual(assets[0]['name'], assets[1]['name'])

	def returnNoAssetsForBadShotID(self):
		assets = self.caretaker\
			.getAssetsFromShot('qeorijadlfkjw2eroiajdlk')
		self.assertTrue(assets is None)

	def getAssetsofACertainTypeFromShot(self):
		shot = self.caretaker.getShotFromName('CTTT1_0010')
		assets = self.caretaker\
			.getAssetsFromShot(shot['_id'], self.assetTypeOneID)

		self.assertEqual(len(assets), 1)
		self.assertEqual(assets[0]['name'], 'CTTT_Asset1')

	def returnNoAssetsIfAssetTypeDoesntExist(self):
		shot = self.caretaker.getShotFromName('CTTT1_0010')
		assets = self.caretaker\
			.getAssetsFromShot(shot['_id'], 'asdfadsflzcvcaldfsdc')

		self.assertTrue(assets is None)

	def getAssetFromPath(self):
		asset = self.caretaker.getAssetFromPath('assetpath/2')
		print 'asset:', asset
		self.assertEqual(asset['name'], 'CTTT_Asset2')

	def returnNoneAssetsFromBadPath(self):
		asset = self.caretaker\
			.getAssetFromPath('adsfeqwrfcvnzclvarwer')

		self.assertTrue(asset is None)

	def getVersionsforAnAsset(self):
		versions = self.caretaker.getAssetVersions(self.asset1ID)

		self.assertEqual(len(versions), 3)
		self.assertTrue(versions[0]['number'] in [1, 4, 8])
		self.assertTrue(versions[1]['number'] in [1, 4, 8])
		self.assertTrue(versions[2]['number'] in [1, 4, 8])

	def returnNoneIfANonExistentAssetIsQueried(self):
		versions = self.caretaker\
			.getAssetVersions('test_roflcopters')
		self.assertTrue(versions is None)

	def guildAssetPath(self):
		testPath = 'r:/Blackish_s03/Final_Renders/BLA_302/EXR_Linear/BLA_302_003_030_v002/BLA_302_003_030_v002.%04d.exr'
		projectInfo = {
			'folderName': 'Blackish_s03',
			'versionPadding': 3,
			'framePadding': 4
		}
		sequenceInfo = {'name': 'BLA_302'}
		shotInfo = {'name': 'BLA_302_003_030'}
		versionInfo = {'number': 2}
		path = self.caretaker\
			.buildAssetPath(
				None,
				versionInfo,
				projectInfo,
				sequenceInfo,
				shotInfo)

		self.assertEqual(path, testPath)

	def getAssetTypeFromName(self):
		assetType = self.caretaker.getAssetTypeFromName('CTTT_AssetType1')
		self.assertEqual(assetType['name'], 'CTTT_AssetType1')

	def getAssetTypeFromAsset(self):
		assetType = self.caretaker.getAssetTypeFromAsset(self.asset1)
		self.assertEqual(assetType['name'], 'CTTT_AssetType1')

	def addCompVersion(self):
		version = self.caretaker.addCompVersion(
			self.projectOne,
			'CTTT1_0020',
			12,
			'CTTT1_0020',
			self.sequenceOne,
			checkComp=False)

		print version
		testPath = 'r:/CTTT_Project1Folder/Final_Renders/CTTT_Seq1/EXR_Linear/CTTT1_0020_v0012/CTTT1_0020_v0012.%04d.exr'
		print version['path']
		print testPath
		self.assertEqual(version['path'], testPath)

if __name__ == '__main__':
	tryout.run(test)
