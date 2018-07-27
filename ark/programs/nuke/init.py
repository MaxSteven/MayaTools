
# Standard modules
##################################################


import os
import nuke

if nuke.env['gui']:
	os.environ['ARK_CURRENT_APP'] = 'nuke'
else:
	os.environ['ARK_CURRENT_APP'] = 'nuke_cl'


# import sys
# import glob
# import math
# import random
import nuke


# Plugin Paths
##################################################
nuke.pluginAddPath('./gizmos')
nuke.pluginAddPath('./gizmos/ie')
nuke.pluginAddPath('./gizmos/old')
nuke.pluginAddPath('./python')
nuke.pluginAddPath('./icons')
nuke.pluginAddPath('./plugins')
nuke.pluginAddPath('./plugins/dg_PerspLines')
nuke.pluginAddPath('./plugins/cryptomatte')
nuke.pluginAddPath('./plugins/lensdistortion')

#Hagbarth Tools
nuke.pluginAddPath('./plugins/hagbarth')
nuke.pluginAddPath('./plugins/hagbarth/icons')
nuke.pluginAddPath('./plugins/hagbarth/tools')
nuke.pluginAddPath('./plugins/hagbarth/grapichs')
nuke.pluginAddPath('./plugins/hagbarth/python')
nuke.pluginAddPath('./plugins/RotoShapesToTrackers')

# Peregrine/pgBokeh
# nuke.pluginAddPath('Q:/USERS/Grant_Miller/software/Bokeh/Bokeh-v1.3.7_Nuke8.0-windows64/')

# add the ark python lib to the import paths
# so we can import arkInit
# arkPythonLib = os.environ.get('ARK_PYTHONLIB')
# nuke.pluginAddPath(arkPythonLib)

# Nuke gets pissed when you add site-packages as a
# plugin path as it tries to load psutil from there
# instead of using it's own psutil
arkRoot = os.environ.get('ARK_ROOT')
nuke.pluginAddPath(arkRoot + 'ark/setup/')

# Ingenuity Plugin Paths
# if arkInit.arkRoot:
# 	nuke.pluginAddPath(arkInit.arkRoot + 'Lib')

# Maxwell
# nuke.pluginAddPath('./plugins/Maxwell Render/plugin/icons')
# nuke.pluginAddPath('./plugins/Maxwell Render/plugin/python')

# Boundry VFX
# Note: changed from ./plugins/bfx to ./python/bfx
# for compatability with publishTools
nuke.pluginAddPath('./python/bfx')

# Our modules
##################################################
import arkInit
arkInit.init()
import cOS
import settingsManager
globalSettings = settingsManager.globalSettings()

# fast allocator, pro style
if 'NUKE_USE_FAST_ALLOCATOR' not in os.environ:
	cOS.setEnvironmentVariable('NUKE_USE_FAST_ALLOCATOR', 1)

# Ark Nuke stuff
import arkNuke
arkNuke.checkScript()

# this is run on every node that's created
# it ensures all the python callbacks and other misc
# things are set up right
nuke.addOnCreate(arkNuke.checkNodes)

# Knob defaults
##################################################
nuke.addFormat('2048 1024 LatLong_2k')
nuke.addFormat('2304 1296 1 HD Overscan 20%')
nuke.addFormat('2816 2304 2 detention_full')
nuke.addFormat('2112 1728 2 detention_hs_full')
nuke.addFormat('1920 784 detention_hd')

nuke.knobDefault('Root.format','1920 1080 HD')
nuke.knobDefault('Root.onScriptLoad','arkNuke.scriptLoad()')
nuke.knobDefault('Root.onScriptSave','arkNuke.scriptSave()')
nuke.knobDefault('Root.onScriptClose','arkNuke.scriptClose()')

nuke.knobDefault('Write.colorspace','sRGB')
nuke.knobDefault('Write.decoder','mov32')
nuke.knobDefault('Write.mov32_pixel_format','RGBA  16-bit (b64a)')
nuke.knobDefault('Write.jpeg._jpeg_quality', '1.0')

nuke.knobDefault('Mirror.Horizontal','1')
nuke.knobDefault('Mirror2.flop','1')
nuke.knobDefault('Project3D.project_on','both')
nuke.knobDefault('Kronos.timing2','Frame')

nuke.knobDefault('Roto.output','alpha')
nuke.knobDefault('Read.auto_alpha','True')
nuke.knobDefault('Bezier.output','alpha')
nuke.knobDefault('Viewer.frame_increment','8')
nuke.knobDefault('Viewer.far','1000000')

nuke.knobDefault('Shuffle.label','[value in]')

nuke.knobDefault('Blur.label','[value size]')
nuke.knobDefault('DirBlurWrapper.BlurLayer','rgba')
nuke.knobDefault('Tracker3.label','[value reference_frame]\n[value transform]')
nuke.knobDefault('Tracker4.label','[value reference_frame]\n[value transform]')
nuke.knobDefault('Defocus.label','[value defocus]')
nuke.knobDefault('OFXcom.frischluft.openfx.depthoffield_v1','[value radius]')
nuke.knobDefault('OFXcom.frischluft.openfx.outoffocus_v1','[value radius]')

nuke.knobDefault('TimeOffset.label','[value time_offset]')
nuke.knobDefault('Retime.label','[value input.first]-[value input.last]\n[value output.first]-[value output.last]')

nuke.knobDefault('Write.beforeRender','arkNuke.beforeRender()')

nuke.knobDefault('Precomp4.output','ie_output')
nuke.knobDefault('Precomp4.useOutput','1')
nuke.knobDefault('ColorLookup.channels','rgb')
nuke.knobDefault('Text.font', globalSettings.SHARED_ROOT + 'Assets/Fonts/Standard/arial.ttf')

# Change RotoPaint clipTo format to no clip
nuke.knobDefault("RotoPaint.cliptype", "none")
# Change Roto clipTo format to no clip
nuke.knobDefault("Roto.cliptype", "none"
)
# Preferences
################################################
preferencesNode = nuke.toNode('preferences')
# Path remapping from r:/ and R:/ on Windows to /ramburglar/ on Linux
preferencesNode.knob('platformPathRemaps').fromScript('r:/;-;/ramburglar/;R:/;-;/ramburglar/;q:/;-;/raidcharles/;Q:/;-;/raidcharles/;f:/;-;/footage/;F:/;-;/footage/;')

# localization settings
# localize from ramburglar, leave 10gb free on the cache drive, check for new files every 10 minutes
if cOS.isWindows():
	preferencesNode['autoLocalCachePath'].fromScript('r:/')
elif cOS.isLinux():
	preferencesNode['autoLocalCachePath'].fromScript('/ramburglar/')

preferencesNode['LocalizationSizeLimit'].fromScript('-10')
preferencesNode['LocalizationUpdatePeriodMinutes'].fromScript('10')
preferencesNode['LocalizationPolicyDefault'].fromScript('on')
