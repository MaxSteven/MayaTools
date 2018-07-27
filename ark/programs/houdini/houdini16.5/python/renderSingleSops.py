# running
# execfile('C:/ie/ark/programs/houdini/houdini13.0/python/renderSingleSops.py')
import sys

import hou

import arkInit
arkInit.init()

import cOS
import settingsManager
globalSettings = settingsManager.globalSettings()

import translators
translator = translators.getCurrent()
print translator

sys.path.append(globalSettings.SHEPHERD_ROOT)
import submit

def submitShot(jobName, passedData):
	filePath = translator.getFilename()
	pathInfo = cOS.getPathInfo(filePath)
	version = cOS.getVersion(filePath)

	jobData = {
		'name': jobName,
		'version': version
	}

	# merge in the passed job data
	jobData.update(passedData)

	renderProps = translator.getRenderProperties(jobData['node'])

	# merge the renderProps into jobData
	# allows for unique per app render options like shadingLevel
	jobData.update(renderProps)

	# turn q:/qoros/workspaces/0010/3d/etc
	# into q:/qoros/workspaces/0010
	outputPath = '/'.join(pathInfo['dirname'].split('/')[:4])
	outputFile = translator.getOutputFilename(outputPath, jobData)
	cOS.makeDirs(str(outputFile))

	# accepts 1-10,20,40-90
	# frameRange = self.frameRange.text()
	jobData['output'] = outputFile
	jobData['filename'] = filePath
	jobData['saveFile'] = filePath
	# fix: once we get Coren it'll be jobType, not jobType
	# fix: remove from here
	# if len(translator.options.get('jobTypes')) > 1:
		# if self.jobType.currentText() == 'Cache':
		# 	jobData['jobType'] = '_'.join([jobData['jobType'].split('_')[0], 'Cache'])
		# 	jobData['jobType'] = jobData['jobType']
		# 	translator.options.get('appHandlesSubmit') = False
		# 	jobData['output'] = outputFile.replace('.exr', '.bgeo.gz').replace('renders', 'Cache')

	if 'hasFrames' not in jobData:
		jobData['hasFrames'] = translator.options.get('hasFrames')
	jobData['jobType'] = jobData['jobType']
	# print 'jobData:'
	# print jobData
	del jobData['startFrame']
	del jobData['endFrame']
	translator.setOutputFilename(outputFile, jobData)

	translator.preSubmit(jobData)
	translator.renderSetup(jobData)
	if not translator.options.get('appHandlesSubmit'):
		translator.renderSetup(jobData)
		print 'submitting job:', jobData
		result = submit.submitJob(jobData)
		print result

	translator.postSubmit(jobData)

def main():
	for node in hou.selectedNodes():
		node.setDisplayFlag(True)
		jobName = node.name()
		submitShot(jobName, {
								'node': '/obj/render/images_single',
								'deep': True,
								'framerange': '30-103',
								# 'framerange': '98-255',
								# 'framerange': '240-335',
								'priority': '520'
							})
		node.setDisplayFlag(False)

if __name__ == '__main__':
	main()


# 1st: 30-103
# 2nd: 98-250
# 3rd: 240-335
