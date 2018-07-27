# running
# execfile('C:/ie/ark/projects/Western_Digital/exportClouds.py')

# cloud1
# - particles: 32

# cloud2
# - particles: 40

# cloud3
# - particles: 48

# cloud4
# - particles: 60

# cloud6
# - additional cloud noise: 5 height, .1 freq
# - particles: 72
# - vdb spheres: max rad: 75

# cloud5
# - vdb spheres: max rad: 80
# - noise: .8 freq, .75 height
# run it:
#

import hou
import os

# settings
numClouds = 6
# resolutions = {'1': .05, '2': .1}
resolutions = {'3': .3}

genBase = 'obj/CloudGen/'
particleTimes = [17, 32, 48, 66, 80, 96]
particleTimes = range(17, 17+6*14, 14)
particleTimes = [17, 26, 40, 55, 72, 87]
outputDir = 'Q:/final_girls/Project_Assets/cloud_dev/Cache/v002/'

# genBase = 'obj/FluffyCloudGen/'
# particleTimes = [48, 48, 48, 48, 48, 48]
# outputDir = 'Q:/Western_Digital/Project_Assets/clouds/Cache/Geo/v005_fluffy/'

# nodes
hou.node(genBase + 'OUT_CLOUD').setRenderFlag(True)
ropNode = hou.node(genBase + 'outputCloud')
step1Node = hou.node(genBase + 'step1')
step2Node = hou.node(genBase + 'step2')
outNode = hou.node(genBase + 'OUT_CLOUD')
import_cloud = hou.node(genBase + 'import_cloud')
cloudSelectParm = hou.parm('/obj/Clouds_Pulled_Individually/switch1/input')

try:
	os.makedirs(outputDir)
except:
	pass

for i in range(2, numClouds):

	# reset
	print 'reset start'
	print 'index:', i
	hou.setFrame(hou.playbar.playbackRange()[0])
	step1Node.setHardLocked(False)
	step2Node.setHardLocked(False)
	outNode.setHardLocked(False)
	cloudSelectParm.set(i)
	import_cloud.cook(force=True)
	import_cloud.setDisplayFlag(True)
	print 'reset done'

	# step 1
	print 'step1 start'
	step1Node.setDisplayFlag(True)
	step1Node.cook(force=True)
	step1Node.setHardLocked(True)
	print 'step1 end'

	# step 2
	print 'step2 start'
	step2Node.setDisplayFlag(True)
	# force cook frame 1 of particles
	step2Node.cook(force=True)
	hou.setFrame(particleTimes[i])
	step2Node.cook(force=True)
	step2Node.setHardLocked(True)
	print 'step2 end'

	# output
	print 'output start'
	outNode.setDisplayFlag(True)
	for lvl, res in resolutions.iteritems():
		outNode.setHardLocked(False)
		outNode.cook(force=True)
		outNode.setHardLocked(True)
		outputPath = outputDir + 'Cloud%d_lvl%s.0001.vdb' % (i + 1, lvl)
		print 'output:', outputPath
		print 'resolution:', resolutions[lvl]
		hou.parm(genBase + 'vdbfrompolygons1/voxelsize').set(res)
		ropNode.parm('sopoutput').set(outputPath)
		ropNode.render()
		print 'output end'
