--//-----------------------------------------------------------------------------
--// InstanceReplacer.ms
--// By Grant Miller (blented@gmail.com)
--// v 1.0
--// Created On: 12/14/12
--// Modified On: 12/14/12
--// tested using Max 2012, Nuke 6.3v3, Softimage 2012, Maya 2012
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Required Files:
--// ieMax.ms
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Description:
--// Replaces instances w/ another object
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Revision History:
--//
--// v 1.00 Initial version
--//
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
(
--// Includes
--//-----------------------------------------------------------------------------
fileIn (MAX_TOOLS_ROOT + "lib/ieMax.ms")

--// Global Variables
--//-----------------------------------------------------------------------------

--// Functions
--//-----------------------------------------------------------------------------

fn publishCamera =
(
	publishDir = ieMaxGetPublishDir()
	if publishDir.count < 4 then
		return false

	frameRange = ((animationrange.start.frame as integer)as string + " - " + (animationrange.end.frame as integer) as string)

	objs = getCurrentSelection()
	shotCams = for o in objs where classof o == camera collect o
	for c in shotCams do
		setUserProp c "frameRange" frameRange

	camFile = publishDir + "camera.max"
	saveNodes objs camFile quiet:true
)

fn isControl o = (findString o.name "con" != undefined or findString o.name "ctrl" != undefined or superclassof o == shape or superclassof o == helper)

--// Script
--//-----------------------------------------------------------------------------
try ( destroydialog ::animManager )catch()

rollout animManager "Animation Manager v1.0" width:488 height:192
(
	groupBox grp1 "Proxy Scene" pos:[8,8] width:152 height:176
	groupBox grp2 "Final scene" pos:[168,8] width:152 height:176
	groupBox grp3 "Publishing" pos:[328,8] width:152 height:96

	button btnSelectMainCons "Select Main Cons" pos:[16,24] width:136 height:32
	button btnSaveAnimation "Save Animation" pos:[16,104] width:136 height:32
	button btnLoadAnimation "Load Animation" pos:[176,104] width:136 height:32
	button btnSaveCamera "Save Camera" pos:[16,144] width:136 height:32
	button btnLoadCamera "Load Camera" pos:[176,144] width:136 height:32
	button btnPublishAnimation "Publish Animation" pos:[336,24] width:136 height:32
	button btnSaveProps "Save Props" pos:[16,64] width:136 height:32
	button btnMergeProps "Merge Props" pos:[176,64] width:136 height:32
	button btnBetterLinkConstraint "Better Link Constraint" pos:[176,24] width:136 height:32
	button btnPublishCamera "Publish Camera" pos:[336,64] width:136 height:32

	local mainCons = #()

	on btnSelectMainCons pressed  do
	(
		-- get all "_CON_Main" in the scene
		mainCons = for s in $* where findString s.name "_CON_Main" != undefined collect s
		select mainCons
	)

	on btnSaveProps pressed do
	(
		props = getCurrentSelection()
		if props.count < 1 then
		(
			print "Please select the props you wish to save"
			return false
		)
		publishDir = ieMaxGetPublishDir()
		if publishDir.count < 4 then
			return false

    	propFile = publishDir + "props.max"
    	saveNodes props propFile quiet:true
	)

	on btnSaveAnimation pressed  do
	(
		mainCons = getCurrentSelection()
		if mainCons.count < 1 then
		(
			print "Please select the CON_Main for each character you wish to save"
			return false
		)
		publishDir = ieMaxGetPublishDir()
		if publishDir.count < 4 then
			return false

		-- get full hierarchy for each con
		userAttr = #()
		userVal = #()
		for con in mainCons do
		(
			conParts = filterString con.name "_"
			conName = conParts[1]
			fullHierarchy = ieMaxGetFullHierarchy con
			-- we only save animation for the ctrl's and con's to keep things (somewhat) fast
			filteredHierarchy = for o in fullHierarchy where (isControl o) collect o
			select filteredHierarchy

			-- save animation using con prefix as a base name
			saveFile = publishDir + conName + "_anim.xaf"
			saveResult = LoadSaveAnimation.saveAnimation saveFile (getCurrentSelection()) userAttr userVal animatedTracks:false
			if saveResult == true then
				print conName + " saved successfully"
			else
				print conName + " was not saved"
		)
		select mainCons
	)

	on btnMergeProps pressed  do
	(
		publishDir = ieMaxGetPublishDir()
		if publishDir.count < 4 then
			return false

    	propFile = publishDir + "props.max"
		objectNames = getMAXFileObjectNames propFile
		namesToMerge = #()
		for o in objectNames do
		(
			obj = getNodeByName o
			if not isValidNode obj then
				append namesToMerge o
		)
		mergeMaXFile propFile namesToMerge #useSceneMtlDups #alwaysReparent quiet:true
		select (for o in namesToMerge collect getNodeByName o)
	)

	on btnLoadAnimation pressed  do
	(
		undo "Load Animation" on
		(
			mainCons = getCurrentSelection()
			if mainCons.count < 1 then
			(
				print "Please select the CON_Main for each character you wish to save"
				return false
			)
			publishDir = ieMaxGetPublishDir()
			if publishDir.count < 4 then
				return false

			-- get full hierarchy for each con
			userAttr = #()
			userVal = #()
			for con in mainCons do
			(
				conParts = filterString con.name "_"
				conName = conParts[1]
				fullHierarchy = ieMaxGetFullHierarchy con

				-- we only load animation for the ctrl's and con's to keep things (somewhat) fast
				filteredHierarchy = for o in fullHierarchy where (isControl o) collect o
				select filteredHierarchy

				-- load animation using con prefix as a base to find file
				saveFile = publishDir + conName + "_anim.xaf"
				if not doesFileExist saveFile then
				(
					print "Could not find saved animation file for: " + conName + " at: " + saveFile
				)
				else
				(
					deleteKeys fullHierarchy #allKeys
					loadResult = LoadSaveAnimation.loadAnimation saveFile (getCurrentSelection()) relative:false insert:false
					if loadResult == true then
						print conName + " loaded successfully"
					else
						print conName + " was not loaded"
				)
			)
		)
	)

	on btnPublishCamera pressed  do
	(
		publishCamera()
	)
	on btnSaveCamera pressed do
	(
		publishCamera()
	)

	on btnLoadCamera pressed  do
	(
		publishDir = ieMaxGetPublishDir()
		if publishDir.count < 4 then
			return false

    	camFile = publishDir + "camera.max"
		objectNames = getMAXFileObjectNames camFile
		for o in objectNames do
		(
			cam = getNodeByName o
			if isValidNode cam then
				delete cam
		)
		mergeMaXFile camFile quiet:true
		select (for o in objectNames collect getNodeByName o)
	)

	on btnPublishAnimation pressed do
	(
		publishDir = ieMaxGetPublishDir()
		if publishDir.count < 4 then
			return false

		holdMaxFile()

		ieMaxRemoveXRefScenes()
		saveMaxFile (publishDir + "animation.max") useNewFile:false quiet:true

		fetchMaxFile quiet:true
	)

	on btnBetterLinkConstraint pressed do
	(
		userSel = getCurrentSelection()
		for obj in userSel do
		(
			ogTransform = obj.transform
			obj.Transform.controller = Link_Constraint ()
			obj.transform = ogTransform
		)
	)
)

createDialog animManager 488 192 style:#(#style_SysMenu, #style_ToolWindow)
)








-- deleteKeys $ #allKeys

-- ctrls = getCurrentSelection()
-- userAttr = #()
-- userVal = #()
-- LoadSaveAnimation.saveAnimation "c:/dev/test/anim.xaf" ctrls userAttr userVal animatedTracks:false

-- ctrls = getCurrentSelection()
-- LoadSaveAnimation.loadAnimation "c:/dev/test/anim.xaf" ctrls relative:false

-- CreateAlembicMetadataModifier $ "material" "boobs"

-- fn getMetadata obj keyName caseSensitive:false =
-- (
-- 	if not isValidNode obj then
-- 		return undefined
-- 	metaDataMod = obj.modifiers["Alembic Metadata"]
-- 	if metaDataMod == undefined then
-- 		return undefined

-- 	attributeCount = custAttributes.count metaDataMod
-- 	for i = 1 to attributeCount do
-- 	(
-- 		metaData = custAttributes.get metaDataMod i
-- 		if ((stricmp metaData._name keyName) == 0 and caseSensitive == false) or (metaData._name == keyName) then
-- 			return metaData._value
-- 	)
-- 	return undefined
-- )
-- fn setMetadata obj keyName keyValue caseSensitive:false =
-- (
-- 	if not isValidNode obj then
-- 		return undefined
-- 	metaDataMod = obj.modifiers["Alembic Metadata"]
-- 	if metaDataMod != undefined then
-- 	(
-- 		attributeCount = custAttributes.count metaDataMod
-- 		for i = 1 to attributeCount do
-- 		(
-- 			metaData = custAttributes.get metaDataMod i
-- 			if ((stricmp metaData._name keyName) == 0 and caseSensitive == false) or (metaData._name == keyName) then
-- 			(
-- 				metaData._value = keyValue as string
-- 				return true
-- 			)
-- 		)
-- 	)
-- 	return (CreateAlembicMetadataModifier obj keyName keyValue)
-- )
-- fn prepExport objs =
-- (
-- 	for obj in objs do
-- 	(
-- 		topMod = obj.modifiers[1]
-- 		if classof topMod == TurboSmooth or classof topMod == TurboSmooth_Pro then
-- 		(
-- 			setMetaData obj "subd_viewportIterations" topMod.iterations
-- 			if (topMod.useRenderIterations == true) then
-- 				setMetaData obj "subd_renderIterations" topMod.renderIterations
-- 			else
-- 				setMetaData obj "subd_renderIterations" topMod.iterations
-- 			deleteModifier obj topMod
-- 		)
-- 		if obj.material != undefined then
-- 			setMetaData obj "material" obj.material.name
-- 		setMetaData obj "layer" obj.layer.name
-- 	)
-- )
-- fn metaSmooth objs =
-- (
-- 	for obj in objs do
-- 	(
-- 		viewportIterations = getMetadata obj "subd_viewportIterations"
-- 		renderIterations = getMetadata obj "subd_renderIterations"
-- 		if viewportIterations != undefined or renderIterations != undefined then
-- 			smoothMod = TurboSmooth()
-- 		if viewportIterations != undefined then
-- 			smoothMod.iterations = viewportIterations as integer
-- 		if renderIterations != undefined then
-- 		(
-- 			smoothMod.useRenderIterations = true
-- 			smoothMod.renderIterations = renderIterations as integer
-- 		)
-- 		addModifier obj smoothMod
-- 	)
-- )

-- objs = getCurrentSelection()
-- prepExport objs

-- metaData._name
-- metaData._value



-- -- xref stuff
-- xrefScenes = #("C:/Users/fx1/Documents/3dsMax/scenes/materials.max","C:/Users/fx1/Documents/3dsMax/scenes/rigFile.max")
-- for refFile in xrefScenes do
-- (
-- 	refScene = xrefs.addNewXRefFile refFile
-- )

-- print xrefs.getXRefFileCount()

-- xrefFiles = #("C:/Users/fx1/Documents/3dsMax/scenes/kinematic egg rig.max")
-- for refFile in xrefFiles do
-- (
-- 	objectNames = getMAXFileObjectNames refFile
-- 	xrefs.addNewXRefObject refFile objectNames modifiers:#xref manipulators:#xref dupMtlNameAction:#useScene
-- )

-- print xrefs.getXRefFileCount()
-- xrefCount = xrefs.getXRefFileCount()
-- for i = 1 to xrefCount do
-- (
-- 	ref = xrefs.getXRefFile i
-- 	print ref.filename
-- )

-- xrefCount = xrefs.getXRefFileCount()
-- i = 1
-- while i <= xrefCount do
-- (
-- 	ref = xrefs.getXRefFile i
-- 	print ref.filename
-- 	if ref.filename == "C:\\Users\\fx1\\Documents\\3dsMax\\scenes\\rigFile.max" then
-- 	(
-- 		delete ref
-- 		xrefCount -= 1
-- 		i -= 1
-- 	)
-- 	i += 1
-- )

