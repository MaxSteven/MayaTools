import initNuke
initNuke.init()

# Import to bootstrap foundry api.
try:
	import ftrack_connect_nuke
	import ftrack_connect
except:
	print 'No ftrack'

# hide default ftrack panels for now
# try:
#     # part of nuke
#     import foundry.assetmgr
# except:
#     # included in ftrack-connect-foundry
#     import assetmgr_nuke

import nuke

import animatedSnap3D
import DeadlineNukeClient


menubar = nuke.menu("Nuke")
tbmenu = menubar.addMenu("&Thinkbox")
tbmenu.addCommand("Submit Nuke To Deadline", DeadlineNukeClient.main, "")

##Hagbarth Tools
toolbar = nuke.toolbar("Nodes")
m = toolbar.addMenu("Hagbarth Tools", icon="h_tools.png")
m.addCommand("StickIt", "nuke.createNode(\"h_stickit\")", icon="h_stickit.png")


nuke.menu("Nodes").addCommand("3DE4/LD_3DE4_Anamorphic_Standard_Degree_4", "nuke.createNode('LD_3DE4_Anamorphic_Standard_Degree_4')")
nuke.menu("Nodes").addCommand("3DE4/LD_3DE4_Anamorphic_Rescaled_Degree_4", "nuke.createNode('LD_3DE4_Anamorphic_Rescaled_Degree_4')")
nuke.menu("Nodes").addCommand("3DE4/LD_3DE4_Anamorphic_Degree_6", "nuke.createNode('LD_3DE4_Anamorphic_Degree_6')")
nuke.menu("Nodes").addCommand("3DE4/LD_3DE4_Radial_Standard_Degree_4", "nuke.createNode('LD_3DE4_Radial_Standard_Degree_4')")
nuke.menu("Nodes").addCommand("3DE4/LD_3DE4_Radial_Fisheye_Degree_8", "nuke.createNode('LD_3DE4_Radial_Fisheye_Degree_8')")
nuke.menu("Nodes").addCommand("3DE4/LD_3DE_Classic_LD_Model", "nuke.createNode('LD_3DE_Classic_LD_Model')")

try:
	if nuke.env[ 'studio' ]:
		import DeadlineNukeFrameServerClient
		tbmenu.addCommand("Reserve Frame Server Slaves", DeadlineNukeFrameServerClient.main, "")
except:
	pass
try:
	import DeadlineNukeVrayStandaloneClient
	tbmenu.addCommand("Submit VRay Standalone to Deadline", DeadlineNukeVrayStandaloneClient.main, "")
except:
	pass

import json
import os
# import time

# import cOS
import settingsManager
globalSettings = settingsManager.globalSettings()


nuke.menu("Nodes").addCommand("3DE4/LD_3DE4_Anamorphic_Standard_Degree_4", "nuke.createNode('LD_3DE4_Anamorphic_Standard_Degree_4')")
nuke.menu("Nodes").addCommand("3DE4/LD_3DE4_Anamorphic_Rescaled_Degree_4", "nuke.createNode('LD_3DE4_Anamorphic_Rescaled_Degree_4')")
nuke.menu("Nodes").addCommand("3DE4/LD_3DE4_Anamorphic_Degree_6", "nuke.createNode('LD_3DE4_Anamorphic_Degree_6')")
nuke.menu("Nodes").addCommand("3DE4/LD_3DE4_Radial_Standard_Degree_4", "nuke.createNode('LD_3DE4_Radial_Standard_Degree_4')")
nuke.menu("Nodes").addCommand("3DE4/LD_3DE4_Radial_Fisheye_Degree_8", "nuke.createNode('LD_3DE4_Radial_Fisheye_Degree_8')")
nuke.menu("Nodes").addCommand("3DE4/LD_3DE_Classic_LD_Model", "nuke.createNode('LD_3DE_Classic_LD_Model')")

# try:
# 	with open(globalSettings.TEMP + 'nukePythonStartup') as f:
# 		info = json.load(f)
# 		print 'startup info:', info
# 		if info.get('startupScript'):
# 			print 'running startup script:', info.get('startupScript')
# 			execfile(info.get('startupScript'))

# 	# remove the startup file
# 	# cOS.removeFile(globalSettings.TEMP + 'nukePythonStartup')

# except Exception as err:
# 	if os.path.isfile(globalSettings.TEMP + 'nukePythonStartup'):
# 		print err
