'''
Uploads the output mov of a Draft job to Ftrack
Gets taskID and username from the extra job params,
and parses version number from the infile path.

'''
import json
import re
import arkInit
arkInit.init()

import arkFTrack
import cOS
import pathManager
pm = arkFTrack.getPM()

import settingsManager
globalSettings = settingsManager.globalSettings()

def __main__(*args):
	deadlinePlugin = args[0]
	job = deadlinePlugin.GetJob()

	# input frames
	outFile = re.findall('"([^"]*)"', job.GetJobPluginInfoKeyValue('ScriptArg17'))
	outFile = [pathManager.translatePath(f) for f in outFile]

	# mov file
	inFile = job.GetJobPluginInfoKeyValue('ScriptArg18')

	# parse version from the folder of the inFile
	# path/to/shot_v0002/file.exr -> 2
	version = cOS.getVersion(inFile.split('/')[-2])

	# TODO possibly unnecesary
	with open(globalSettings.ARK_ROOT + 'arkFTrack/config/ftrack_event_server.json') as f:
		contents = json.load(f)

	pm.getSession(api_key=contents['api_key'], api_user=contents['user'])

	taskID = job.JobExtraInfo3
	userID = pm.getUser(job.JobExtraInfo1)['id']
	task = pm.get('Task', taskID)

	# get asset from task
	asset = pm.getAsset(task)

	versionData = {
		'user_id': userID,
		'version': version,
		'task_id': task['id']
	}

	print 'Uploading version {} on asset "{}"" for task "{}":'.format(
		versionData['version'], asset['name'], task['name']
	)
	print outFile
	jobs = pm.uploadFile(asset, outFile, versionData=versionData, overwrite=True)
	print jobs

