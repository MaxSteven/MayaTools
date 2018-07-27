# convertVersion function

# import arkInit
# arkInit.init()

# import translators
# translator = translators.getCurrent()

# import settingsManager
# globalSettings = settingsManager.globalSettings()

from database import Database
database = Database()
database.connect()

# from caretaker import Caretaker
# caretaker = Caretaker()

import shepherd

result = False

def convertVersion(versionInfo, conversionInfo):

	print database\
		.update('version')\
		.where('_id','is',versionInfo['_id'])\
		.set('updated', 1)\
		.execute()

	job = database\
		.findOne('shepherdJob')\
		.where('output','contains', conversionInfo['name'])\
		.where('file','is', versionInfo['path'])\
		.options('getLinks', ['project','shot'])\
		.execute()

	if not job:
		print 'Could not create shepherdJob to convert'
		return False

	# sheep = shepherd.Sheep()

	# def onComplete(sheepInfo, jobInfo, data):
	# 	global result
	# 	result = True
	# 	sheep.exit()

	# def onError(sheepInfo, jobInfo, data):
	# 	global result
	# 	result = False
	# 	sheep.exit()

	# sheep.init({
	# 		'tags': 'convert',
	# 		'installPrograms': False,
	# 		'killJobProcesses': False,
	# 		'jobLoop': False,
	# 		'checkIn': False,
	# 	})

	# sheep.jobInfo = job
	# sheep.on('complete', onComplete)
	# sheep.on('error', onError)
	shepherd.runJob(job)

	global result

	return result
