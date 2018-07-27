# Standard modules

# Our modules
import arkInit
arkInit.init()
import Deadline.DeadlineConnect as Connect
import socket
deadlineIP = str(socket.gethostbyname(socket.gethostname()))
port = 8082
connection = Connect.DeadlineCon(deadlineIP, port)

import cOS
import arkUtil

pluginMap = {
	'Maya_VRayStandalone': [
		{
			'Animation': 1,
			'Build': '64bit',
			'CountRenderableCameras': 0,
			'IgnoreError211': 0,
			'Renderer': 'vrayExport',
			'UseLocalAssetCaching': 0,
			'Version': 2016,
		},
		{
			'Height': 0,
			'SeparateFilesPerFrame': 0,
			'Threads': 0,
			'Width': 0,
		}
	],
	'Nuke_Comp': [
		{
			'BatchMode': True,
			'BatchModeIsMovie': False,
			'ContinueOnError': False,
			'EnforceRenderOrder': False,
			'GpuOverride': 0,
			'NukeX': False,
			'PerformanceProfiler': False,
			'RamUse': 0,
			'RenderMode': 'Use Scene Settings',
			'StackSize': 0,
			'Threads': 0,
			'UseGpu': False,
			'Version': 10.0,
		}
	],
}

def submitJob(jobData):
	pluginInfo = getPluginFromJob(jobData)[0]
	pathInfo = cOS.getPathInfo(jobData['output'])
	padding = cOS.getPadding(jobData['output'])

	jobInfo = {
		'Name': jobData['name'],
		'BatchName': jobData['name'],
		'UserName': 'ie',
		'Frames': jobData['frameRange'],
		'ChunkSize': jobData.get('chunkSize', 1) if jobData.get('chunkSize', 1) else 1,
		'MachineLimit': jobData.get('sheepLimit', 0),
		'Priority': jobData['priority'],
		'OutputFilename0': pathInfo.get('basename').replace('%0' + str(padding) + 'd', '#' * padding),
		'OutputDirectory0': pathInfo.get('dirname')
	}
	if cOS.isLinux():
		print 'Not intended for Linux'
		return False

	result = False
	if jobData.get('jobType') == 'Maya_VRayStandalone':
		jobInfo2 = jobInfo.copy()
		jobInfo.update({
			'Plugin': 'MayaBatch',
		})
		print 'jobInfo:', jobInfo
		pluginInfo.update({
			'OutputFilePath': jobInfo.get('OutputDirectory0'),
			'OutputFilePrefix': jobInfo.get('OutputFilename0').split('.#')[0],
			'ProjectPath': '/'.join(jobData.get('output').split('/')[:3]),
			'VRayExportFile': jobInfo.get('OutputDirectory0') + jobInfo.get('OutputFilename0').split('.#')[0] + '.' + ('#' * padding) + '.vrscene',
			'Camera': jobData['node'],
			'SceneFile': jobData.get('sourceFile'),
			'ImageWidth': jobData.get('width'),
			'ImageHeight': jobData.get('height'),
		})
		print 'pluginInfo:', pluginInfo
		jobInfo2.update({
			'Plugin': 'Vray',
		})
		pluginInfo2 = getPluginFromJob(jobData)[1]
		pluginInfo2.update({
			'SeparateFilesPerFrame': 1,
		})

		frames = arkUtil.parseFrameRange(jobData.get('frameRange'))

		for i in frames:
			jobInfo.update({
				'Frames': str(i)
			})
			pluginInfo.update({
				'VRayExportFile': jobInfo.get('OutputDirectory0') + jobInfo.get('OutputFilename0').split('.#')[0] + '.' + arkUtil.pad(i, padding) + '.vrscene',
			})
			result = connection.Jobs.SubmitJob(jobInfo, pluginInfo)
			jobInfo2.update({
				'Frames': str(i),
				'JobDependencies': result['_id'],
			})
			pluginInfo2.update({
				'InputFilename': pluginInfo.get('VRayExportFile'),
			})
			result = connection.Jobs.SubmitJob(jobInfo2, pluginInfo2)


	elif jobData.get('jobType') == 'Nuke_Comp':
		jobInfo.update({
			'Plugin': 'Nuke',
		})
		print 'jobInfo:', jobInfo
		pluginInfo.update({
			'SceneFile': jobData.get('file'),
		})
		print 'pluginInfo:', pluginInfo
		result = connection.Jobs.SubmitJob(jobInfo, pluginInfo)
	else:
		print 'invalid jobType'

	return result


def getPluginFromJob(data):
	jobData = data
	jobType = data.get('jobType')

	if jobType in pluginMap:
		return pluginMap.get(jobType)
	else:
		raise Exception('invaldi job type', jobType)

def main(args=None):
	if not args:
		args = cOS.getArgs()
	submitJob(args)


if __name__ == '__main__':
	# pass
	# main()
	vrayTestJobData = {
		'node': 'cameraShape1',
		'program': 'vray',
		'farPlane': 10000.0,
		'name': u'GEO_0020_separate_batch',
		'chunkSize': None,
		'sourceFile': 'r:/Test_Project/Workspaces/publish/TPT_0010/3D/textureTest_v005.mb',
		'height': 1080,
		'priority': '50',
		'width': 1920,
		'version': 5,
		'frameRange': '1-5',
		'fps': 24,
		'output': 'r:/Test_Project/Workspaces/publish/TPT_0010/renders/GEO_0020/v0005/GEO_0020.%04d.exr',
		'previewPath': 'r:/Test_Project/Workspaces/publish/TPT_0010/renders/GEO_0020/v0005/GEO_0020.100.preview.exr',
		'jobType': u'Maya_VRayStandalone',
		'nearPlane': 0.1
	}
	print 'testing vray...'
	submitJob(vrayTestJobData)

	# nukeTestJobData = {
	# 	'node': 'Write1',
	# 	'program': 'nuke',
	# 	'farPlane': None,
	# 	'name': 'TPT_0010_comp_last_one',
	# 	'sourceFile': 'r:/Test_Project/Workspaces/publish/TPT_0010/Comp/render_test_v001_sak.nk',
	# 	'height': 1080,
	# 	'priority': '50',
	# 	'width': 1920,
	# 	'version': 1,
	# 	'frameRange': '1-3',
	# 	'nearPlane': None,
	# 	'fps': 24,
	# 	'output': 'r:/Test_Project/Workspaces/publish/TPT_0010/renders/v0001/nukeVRay.%04d.exr',
	# 	'previewPath': None,
	# 	'jobType': u'Nuke_Comp',
	# 	'chunkSize': 1
	#  }
	# print 'testing nuke...'
	# submitJob(nukeTestJobData)


# pluginMap = {
# 	'Maya_VRayStandalone': [
# 		{
# 			'Animation': 1,
# 			'Build': '64bit',
# 			'CountRenderableCameras': 0,
# 			'IgnoreError211': 0,
# 			'ImageHeight': 720,
# 			'ImageWidth': 1280,
# 			'Renderer': 'vrayExport',
# 			'UseLocalAssetCaching': 0,
# 			'Version': 2016,
# 			# 'OutputFilePath': 'R:/Test_Project/Workspaces/deadline/renders/vanni/newRender',
# 			# 'OutputFilePrefix': 'KFT_07_glass_090_tearface_090_cyborgeye_camera_07_glass_060Shape',
# 			# 'ProjectPath': 'R:/Test_Project/Workspaces/deadline/renders/',
# 			# 'VRayExportFile': 'R:/Test_Project/Workspaces/deadline/renders/vrscenes/renders9.vrscene',
# 			# 'Camera': 'camera_07_glass_060',
# 		},
# 		{
# 			'Height': 0,
# 			# 'InputFilename': R:/Test_Project/Workspaces/deadline/renders/vrscenes/renders9.vrscene,
# 			'SeparateFilesPerFrame': 0,
# 			'Threads': 0,
# 			'Width': 0,
# 		}
# 	],

# 	'Nuke_Comp': [
# 		{
# 			'BatchMode': True,
# 			'BatchModeIsMovie': False,
# 			'ContinueOnError': False,
# 			'EnforceRenderOrder': False,
# 			'GpuOverride': 0,
# 			'NukeX': False,
# 			'PerformanceProfiler': False,
# 			# 'PerformanceProfilerDir': '',
# 			'RamUse': 0,
# 			'RenderMode': 'Use Scene Settings',
# 			# 'SceneFile': r:/Test_Project/Workspaces/0010/Comp/0010_comp_v0043_sk.nk,
# 			'StackSize': 0,
# 			'Threads': 0,
# 			'UseGpu': False,
# 			'Version': 10.0,
# 			# 'Views': '',
# 		}
# 	],
# }

