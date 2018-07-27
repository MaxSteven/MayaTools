
import os
os.environ['ARK_CURRENT_APP'] = 'max'

import sys
sys.path.append('C:/Python27/Lib/site-packages/')
import arkInit
arkInit.init()

import DropdownMenu
import settingsManager
globalSettings = settingsManager.globalSettings()
# import MaxPlus

app = None

def initMenu():
	global app
	# app = DropdownMenu.DropDownDialog()
	print "about to launch"
	app = DropdownMenu.DropDownDialog()
	print "launched"


	app.addCommand(name='Refresh',
		imports='programs/max/startup/maxMenuInit.py',
		python='import maxMenuInit; reload(maxMenuInit); maxMenuInit.launchMenu()')

	## Smart Tools
	app.addCommand(name='Smart Tools/Smart Open Tool',
		imports='ark/tools/smartTools/smartOpen.py',
		python='import smartOpen; smartOpen.main();')

	app.addCommand(name='Smart Tools/Smart Save Tool',
		imports='ark/tools/smartTools/smartSave.py',
		python='import smartSave; smartSave.main();')

	## Publish Tools
	app.addCommand(name='Publish Tools/Publish Assets',
		imports='ark/tools/publishTools/publishAsset/publishAssetGUI.py',
		python='import publishAssetGUI; publishAssetGUI.main()')

	app.addCommand(name='Publish Tools/Import Assets',
		imports='ark/tools/publishTools/importAsset/importAssetGUI.py',
		python='import importAssetGUI; importAssetGUI.main()')

	app.addCommand(name='Publish Tools/View Assets',
		imports='ark/tools/publishTools/viewAsset/viewAssetGUI.py',
		python='import viewAssetGUI; viewAssetGUI.main()')

	app.addCommand(name='Publish Tools/Publish Animation',
		imports='ark/tools/publishTools/publishAnimation/publishAnimationGUI.py',
		python='import publishAnimationGUI; publishAnimationGUI.main()')

	app.addCommand(name='Publish Tools/Publish Camera',
		imports='ark/tools/publishTools/publishCamera/publishCameraGUI.py',
		python='import publishCameraGUI; publishCameraGUI.main()')

	## Animation Library
	app.addCommand(name='Animation/Animation Library',
		imports='ark/tools/animationLibrary/animationLibraryGUI.py',
		python='import animationLibraryGUI; animationLibraryGUI.main()')

	## Utilities
	app.addCommand(name='Utilities/Repath',
		imports='ark/tools/repath/repath.py',
		python='repath.main()')

	## Studio
	app.addCommand(name='Studio/Shot Manager',
		imports='ark/tools/shotManager/ShotManager.py',
		python='import ShotManager; ShotManager.launch()')

	app.addCommand(name='Studio/Run Weaver',
		imports='weaver/Weaver.py',
		python='Weaver.main()')

	app.addCommand(name='Macros/IFK Chain',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"IFKChain\"\')')

	app.addCommand(name='Studio/Save like a Pro',
		imports='',
		python='translator.saveIncrementWithInitials()',
		shortcut='Alt+Shift+s')

	app.addCommand(name='Studio/Reference Manager',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"ReferenceManager\"\')')

	app.addCommand(name='Studio/Shepherd Submit',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"SubmitJob\"\')')

	## Macros
	app.addCommand(name='Macros/Scene Rescale',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"SceneRescale\"\')')
	app.addCommand(name='Macros/TurnRender',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"TurnRender\"\')')

	app.addCommand(name='Macros/Animation Stopwatch',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"AnimationStopwatch\"\')')

	app.addCommand(name='Macros/Pivot to Center',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"PivotToCenter\"\')')

	app.addCommand(name='Macros/Pivot to Obj Center',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"PivotToObjCenter\"\')')

	app.addCommand(name='Macros/Pivot to Obj Pivot',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"PivotToObjPivot\"\')')

	app.addCommand(name='Macros/Rigging Tools',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"RiggingTools\"\')')

	app.addCommand(name='Macros/UVW Element Select',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"UVWElementSelect\"\')')

	app.addCommand(name='Macros/UVW Rotate 180',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"UVWRotate180\"\')')

	app.addCommand(name='Macros/UVW Soft Selection',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"UVWSoftSelection\"\')')

	app.addCommand(name='Macros/Toggle Silhouette',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"ToggleSilhouette\"\')')

	app.addCommand(name='Macros/Toggle Materials',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"ToggleMaterials\"\')')

	app.addCommand(name='Macros/Remove Material',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"RemoveMaterial\"\')')

	app.addCommand(name='Macros/Make Planar X',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"MakePlanarX\"\')')

	app.addCommand(name='Macros/Make Planar Y',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"MakePlanarY\"\')')

	app.addCommand(name='Macros/Make Planar Z',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"MakePlanarZ\"\')')

	app.addCommand(name='Macros/Select by Angle Toggle',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"SelectByAngleToggle\"\')')

	app.addCommand(name='Macros/Convert to SubObj 1',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"ConvertToVertex\"\')')

	app.addCommand(name='Macros/Convert to SubObj 2',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"ConvertToEdge\"\')')

	app.addCommand(name='Macros/Convert to SubObj 3',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"ConvertToSubObj3\"\')')

	app.addCommand(name='Macros/Convert to SubObj 4',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"ConvertToSubObj4\"\')')

	app.addCommand(name='Macros/Convert to SubObj 5',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"ConvertToSubObj5\"\')')

	app.addCommand(name='Macros/Remove Top Modifier',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"RemoveTopModifier\"\')')

	app.addCommand(name='Macros/Goto Base Object',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"GotoBaseObj\"\')')

	app.addCommand(name='Macros/Grid Place',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"gridPlace\"\')')

	app.addCommand(name='Macros/Goto Object Level',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"GotoObjectLevel\"\')')

	app.addCommand(name='Macros/Clear Grids',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"ClearGrids\"\')')

	app.addCommand(name='Macros/Transform Center Cycle',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"transformCycle\"\')')

	app.addCommand(name='Macros/Easy Bake',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"EasyBake\"\')')

	app.addCommand(name='Macros/Bone Controller',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"boneController\"\')')

	app.addCommand(name='Macros/Bone Align',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"boneAlign\"\')')

	app.addCommand(name='Macros/Bone Pos Match',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"bonePosMatch\"\')')

	app.addCommand(name='Macros/Preserve UV Toggle',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"preserveUVToggle\"\')')

	app.addCommand(name='Macros/UVW Align UVs V',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"alignUVsV\"\')')

	app.addCommand(name='Macros/UVW Align UVs U',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"alignUVsU\"\')')

	app.addCommand(name='Macros/Relax',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"relax\"\')')

	app.addCommand(name='Macros/Grow Loop',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"growLoop\"\')')

	app.addCommand(name='Macros/Grow Ring',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"growRing\"\')')

	app.addCommand(name='Macros/Show Frozen in Gray',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"grayFrozen\"\')')

	app.addCommand(name='Macros/Bake Animation',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"BakeAnimation\"\')')

	app.addCommand(name='Macros/Place Tool',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"PlaceTool\"\')')

	app.addCommand(name='Macros/Explode By Element',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"ExplodeByElement\"\')')

	app.addCommand(name='Macros/Visibility Toggle',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"VisibilityToggle\"\')')

	app.addCommand(name='Macros/Sync PFlow Layers',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"SyncPFlowLayers\"\')')

	app.addCommand(name='Macros/Select By Wirecolor',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"msSelectByWireColor\"\')')

	app.addCommand(name='Macros/Select By Material',
		imports='',
		python='translator.executeNativeCommand(\'macros.run \"Ingenuity\" \"msSelectByMaterial\"\')')


	maxScriptDirectory = globalSettings.MAX_TOOLS_ROOT + 'scripts/'
	for root, dirs, files in os.walk(maxScriptDirectory):
		rootFolder = root.split('/')[-1]
		if rootFolder.strip():
			for f in files:
				scriptName = f.split('.')[0]
				app.addCommand(name=rootFolder + '/' + scriptName,
					imports='',
					python='translator.executeNativeCommand(\'filein(\"' + root + '/' + f + '\")\')')


def launchMenu():
	global app

	if app== None:
		initMenu()

	DropdownMenu.showMenu(app)