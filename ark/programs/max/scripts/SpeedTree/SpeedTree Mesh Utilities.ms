-------------------------------------------------------------------------------------------------
--	SpeedTree Mesh Exporter - 3D Studio MAX Version
--
--	For exporting an object for use with SpeedTree Modeler
--
--	Workflow:
--		-Create a model in 3ds Max you wish to use in the SpeedTree Modeler
--		-Run this script via "MAXScript->Run Script..."
--		-Use the tools on the rollout to process the mesh and export it for use in SpeedTree
--
--	Note: If you intend to modify this script please make a copy and modify that.  This file
--	is subject to modification or deletion during software updates.
--
--	*** INTERACTIVE DATA VISUALIZATION (IDV) PROPRIETARY INFORMATION ***
--
--	This software is supplied under the terms of a license agreement or
--	nondisclosure agreement with Interactive Data Visualization and may
--	not be copied or disclosed except in accordance with the terms of
--	that agreement.
--
--      Copyright (c) 2003-2011 IDV, Inc.
--      All Rights Reserved.
--
-------------------------------------------------------------------------------------------------

-- Initialization
setCommandPanelTaskMode mode:#utility

fn DeclareGlobals = (
	global stm, stmTools, stmForest, stmUnits  -- Predefine rollout names
	global LastFileName, cObject
	global arrSelected = #()
	global strOldSystemScale = units.SystemScale
	global strOldSystemType = units.SystemType
	global fConversionScalar
)
DeclareGlobals()

if (stm != undefined AND stm.open) do DestroyDialog stm
if (stmTools != undefined AND stmTools.open) do DestroyDialog stmTools
if (stmForest != undefined AND stmForest.open) do DestroyDialog stmForest
if (stmUnits != undefined AND stmUnits.open) do DestroyDialog stmUnits

mx_ini = getMAXIniFile() -- Recall utility preferences
iniUtilityPath = getINISetting mx_ini "IDV" "stm_utilitypath"
iniCenterOrigin = getINISetting mx_ini "IDV" "stm_origin"
if iniCenterOrigin == "" then iniCenterOrigin = false
iniStmFormat = getINISetting mx_ini "IDV" "stm_format"
if iniStmFormat == "" then iniStmFormat = 1
iniWeldAll = getINISetting mx_ini "IDV" "stm_weldall"
if iniWeldAll == "" then iniWeldAll = true
iniWeldTexCoords = getINISetting mx_ini "IDV" "stm_weldtexcoords"
if iniWeldTexCoords == "" then iniWeldTexCoords = true
iniShowNormals = getINISetting mx_ini "IDV" "stm_shownormals"
if iniShowNormals == "" then iniShowNormals = false
iniShowVertexColors = getINISetting mx_ini "IDV" "stm_showvertcolors"
if iniShowVertexColors == "" then iniShowVertexColors = false
iniSrtExtension = getINISetting mx_ini "IDV" "stm_srtext"
if iniSrtExtension == "" then iniSrtExtension = true
iniSelectionSet = getINISetting mx_ini "IDV" "stm_selectionset"
if iniSelectionSet == "" then iniSelectionSet = true
iniConvertUnits = false

-- predefine function names
fn UpdateList = ()
fn ConvertSceneUnits = ()
fn CreateRollouts = ()
fn	getCObject = ()
fn	ProjectNormals = ()
fn	FlipNormals = ()
fn	CleanUpFaces = ()
fn ConvertToTriFoil = ()
fn	CleanUpStreaks = ()
fn ClampDetailTexture = ()
fn AddDetailLayer = ()
fn	SetPivot = ()
fn	CreateFloat = ()
fn	ExportSTF = ()
fn	RenameInSelection = ()
fn	ImportSWA = ()
fn	ImportSTF = ()
fn UnitizeMesh = ()
fn stmRemoveScripts = ( 
	callbacks.removeScripts id:#stmChange
)

fn stmCallbacks = (
	callbacks.addScript #selectionSetChanged "UpdateList()" id:#stmChange
	callbacks.addScript #unitsChange "UpdateList()" id:#stmChange	
	callbacks.addScript #nodeRenamed "UpdateList()" id:#stmChange	
	callbacks.addScript #modPanelObjPostChange "UpdateList()" id:#stmChange
	callbacks.addScript #filePreOpen "if stm.open do DestroyRollouts()"
	callbacks.addScript #systemPreReset "if stm.open do DestroyRollouts()" 
	callbacks.addScript #systemPreNew "if stm.open do DestroyRollouts()" 
	callbacks.addScript #filePostMerge "if stm.open do CreateRollouts()" 
	callbacks.addScript #filePostOpen "if stm.open do CreateRollouts()"
	callbacks.addScript #systemPostReset "if stm.open do CreateRollouts()"
	callbacks.addScript #systemPostNew "if stm.open do CreateRollouts()" 
)

fn getAppVersion = (
	appVersion = maxVersion()
	return appVersion[1] / 1000
)
appVersion = getAppVersion()

------------------------------------------------------------------------------------------------
-- Rollouts -----------------------------------------------------------------------------------

utility stmTools "SpeedTree Mesh Tools" (
	group "Project Normals" (
		checkbox cbAutoProject "Auto update" offset:[28,-2] align:#center visible:false checked:true
		label lblProjectionStyle "Proj. style" offset:[0,2] align:#left
		dropDownList ddProjectionStyle width:85 height:20 items:#("Spherical", "Cylindrical") selection:1 offset:[2,-22] align:#right
		label lblProjectionAxis "Proj. axis" offset:[0,3] align:#left
		dropDownList ddProjectionAxis width:85 height:20 items:#("X axis", "Y axis", "Z axis") selection:2 offset:[2,-22] align:#right
		label lblProjectionSkew "Skew" offset:[0,7] align:#left
		edittext txtProjectionSkew text:"0.5" fieldWidth:40 offset:[1,-20] align:#right
		slider slProjectBias range:[-1,1,0.5]  ticks:2 width: 70 height:20 offset:[-33,-33] align:#right
		button btnProjectNormals "Project Normals Now" width:140 enabled:false offset:[-1,0]
		label lblLine1 "_________________________" offset:[-7,-5] align:#left
		button btnFlipNormals "Flip normals" across:4 offset:[16,3] enabled:false
		checkButton XSelect "X" width:18 offset:[32,3]
		checkButton YSelect "Y" width:18 offset:[21,3]
		checkButton ZSelect "Z" width:18 offset:[10,3] checked:true
	)
	
	group "Geometry Tools" (
		button btnSetPivot "Set pivot to:" align:#left offset:[-3,0] enabled:false
		dropDownList ddPivotLocation width:61 height:20 items:#("Origin", "Center") selection:1 offset:[3,-26] align:#right
		button btnCleanFaces "Remove faces <" width:88 offset:[-27,-1] enabled:false
		spinner spCleanBias range:[0.0,0.04,0.002] scale:0.001 fieldwidth:38 offset:[2,-23] 
		button btnConvertToTriFoil "Convert to \"Tri-Foil\"" width:141 offset:[-1,2] enabled:false
	)
	
	group "Texture Tools" (
		button btnCleanStreaks "Select streaked triangles" align:#left offset:[-3,0] width:141 enabled:false
		button btnClampDetail "Clamp detail tex coords" align:#left offset:[-3,0] width:141
		button btnAddDetailLayer "Add detail layer to material" align:#left offset:[-3,0] width:141
	)
	
	button btnCreateFloater "" width:15 height:15 pos:[143,13] enabled:true	
	
	on ddProjectionStyle selected sel do (
		if (cbAutoProject.checked AND stmTools.inDialog) then if (selection.count > 0) do ProjectNormals "" "" ""
	)
	
	on ddProjectionAxis selected sel do (
		if (cbAutoProject.checked AND stmTools.inDialog) then if (selection.count > 0) do ProjectNormals "" "" ""
	)
	
	on txtProjectionSkew entered txt do (
		if txt != "" then (
			try  (
				val = execute txt 
				slProjectBias.value = val as float
			) 
			catch  (
				slProjectBias.value = 0.0
				txtProjectionSkew.text = "0.0"
			)
		) else (
			slProjectBias.value = 0.0
			txtProjectionSkew.text = "0.0"
		)
		
		if (cbAutoProject.checked AND stmTools.inDialog) then if (selection.count > 0) do ProjectNormals "" "" ""
	)
	
	on slProjectBias changed val do (
		txtProjectionSkew.text = substring (val as string) 1 5
		if (cbAutoProject.checked AND stmTools.inDialog) then if (selection.count > 0) do ProjectNormals "" "" ""
	)
	
	on btnProjectNormals pressed do (
		if (selection.count > 0) then (
			ProjectNormals "" "" ""
		) else (
			messageBox "No mesh object(s) selected." title:"Error" beep:false
		)
	)

	on btnFlipNormals pressed do (
		if (selection.count > 0) then (
			FlipNormals()
		) else (
			messageBox "No mesh object(s) selected." title:"Error" beep:false
		)
	)
	
	on btnCleanFaces pressed do (
		if (selection.count > 0) then (
			CleanUpFaces()
		) else (
			messageBox "No mesh object(s) selected." title:"Error" beep:false
		)
	)
	
	on btnConvertToTriFoil pressed do (
		if (selection.count > 0) then (
			ConvertToTriFoil()
		) else (
			messageBox "No mesh object(s) selected." title:"Error" beep:false
		)
	)
	
	on btnCleanStreaks pressed do (
		if (selection.count > 0) then (
			CleanUpStreaks()
		) else (
			messageBox "No mesh object(s) selected." title:"Error" beep:false
		)
	)
	
	on btnSetPivot pressed do (
		if (selection.count > 0) then (
			SetPivot cObject stmTools.ddPivotLocation.selected
		) else (
			messageBox "No mesh object(s) selected." title:"Error" beep:false
		)
	)
	
	on btnClampDetail pressed do (
		if (selection.count > 0) then (
			ClampDetailTexture()
		) else (
			messageBox "No mesh object(s) selected." title:"Error" beep:false
		)
	)
	
	on btnAddDetailLayer pressed do (
		if (selection.count > 0) then (
			AddDetailLayer()
		) else (
			messageBox "No mesh object(s) selected." title:"Error" beep:false
		)
	)
	
	on btnCreateFloater pressed do (
		CreateFloat stmTools 410
		stmTools.cbAutoProject.visible = true
	)
)


utility stmForest "World Building Tools" (
	group "Forest Data Exporter" (
		button btnMakeSTF "Export Selection" height:18 width:105 offset:[0,5]
		label lblWorldDataOptions "Options:" align:#left offset:[5,3]
		radiobuttons rbWorldDataFormat labels:#("SWA", "STF") align:#left offset:[15,0] default:1
		checkbox cbSrtExtension "Add \".SRT\" to entries" offset:[15,-2] checked:(iniSrtExtension as BooleanClass)
		checkbox cbCreateSelectionSet "Save selection set" offset:[15,-2] checked:(iniSelectionSet as BooleanClass)
		label lblRename "Rename In Selection:" align:#left offset:[5,8]
		edittext txtFindString "find string" fieldwidth:73 offset:[15,0]
		edittext txtSubstituteString "substitute" fieldwidth:73 offset:[15,-3]
		button btnRenameInSelection "Rename In Selection" height:18 width:125 offset:[9,0]
	)
	
	group "Forest Data Importer" (
		button btnLoadSWA "Select SWA File..." height:18 width:105
		button btnLoadSTF "Select STF File..." height:18 width:105
	)
	
	button btnCreateFloater "" width:15 height:15 pos:[143,13] enabled:true
	
	on btnMakeSTF pressed do (	
		ExportSTF()
	)
	
	on cbSrtExtension changed optionState do setINISetting mx_ini "IDV" "stm_srtext" (optionState as string)
	on cbCreateSelectionSet changed optionState do setINISetting mx_ini "IDV" "stm_selectionset" (optionState as string)
	
	on btnRenameInSelection pressed do (
		RenameInSelection()
	)

	on btnLoadSWA pressed do (
		ImportSWA()
	)
	
	on btnLoadSTF pressed do (
		ImportSTF()
	)
	
	on btnCreateFloater pressed do CreateFloat stmForest 300
)


utility stmUnits "Convert Units & Transforms" (
	
	group "Unit Converter" (		
		checkbox cbConvertSize "Size" checked:true
		checkbox cbConvertPos "Position" checked:false offset:[50,-20]
		label lblConvertFrom "From" offset:[0,4] align:#left
		dropDownList ddConvertFrom width:80 height:20 items:#("millimeters", "centimeters", "meters", "kilometers", "inches", "feet", "miles") offset:[-25,-22] align:#right selection:6	--selection:(iniStmFormat as integer) 
		label lblConvertTo "To" offset:[8,3] align:#left
		dropDownList ddConvertTo width:80 height:20 items:#("scene units", "millimeters", "centimeters", "meters", "kilometers", "inches", "feet", "miles") offset:[-25,-22] align:#right selection:1	--selection:(iniStmFormat as integer) 
		label lblConversionRatio "Scale -> 0.25 original" offset:[0,0] align:#left
		button btnConvertUnits "Convert Selected" width:140 height:20 offset:[0,0]
	)
	
	on ddConvertFrom selected selection do ConvertSceneUnits()
	on ddConvertTo selected selection do ConvertSceneUnits()
	on btnConvertUnits pressed do (
		undo on (	
			GetcObject()
			if (cObject != undefined) then (
				for s in arrSelected do (
					if stmUnits.cbConvertSize.checked == true then s.scale = s.scale / fConversionScalar
					if stmUnits.cbConvertPos.checked == true then (
						s.pos.x = s.pos.x / fConversionScalar
						s.pos.x = s.pos.x / fConversionScalar
						s.pos.x = s.pos.x / fConversionScalar
					)
				)
			)
		)
	)
	
	group "\"Unitize\" Mesh" (
		label lblUnitizeScalar "Scale results by" offset:[0,0] align:#left	
		spinner spUnitizeScalar  range:[1,100,5] type:#float fieldwidth:40 enabled:true offset:[2,-20] align:#right	
		button btnUnitizeMesh "Unitize Selected" width:140 height:20
	)
	
	on btnUnitizeMesh pressed do (
		UnitizeMesh(stmUnits.spUnitizeScalar.value)
	)
	
	group "Copy Transforms" (
		checkbox cbCopyPosition "Copy Position" checked:true
		checkbox cbCopyRotation "Copy Rotation" checked:true
		checkbox cbCopyScale "Copy Scale" checked:true
		checkbox cbHideTarget "Hide target after copy" offset:[0,10]
		pickbutton pbChooseTarget "- Select target -"  width:140 height:20 offset:[0,0]		
	)
	
	button btnCreateFloater "" width:15 height:15 pos:[143,13] enabled:true	
	
	on pbChooseTarget picked targetObj do (
		undo on (
			objPosX = targetObj.pos.x
			objPosY = targetObj.pos.y
			objPosZ = targetObj.pos.z
			if targetObj.rotation != undefined then objRot = targetObj.rotation
			else objRot = (quat 0 0 0 1)
			objScale = targetObj.scale
			
			GetcObject()
			if (cObject != undefined) then (
				for s in arrSelected do (
					if targetObj != s then (
						if stmUnits.cbCopyRotation.checked == true then
							s.rotation = objRot
						
						if stmUnits.cbCopyPosition.checked == true then
							s.position = [objPosX, objPosY, objPosZ]
						
						if stmUnits.cbCopyScale.checked == true then
							s.scale = objScale
						
						if stmUnits.cbHideTarget.checked == true then
							hide targetObj
					)
				)
			)
		)
	)
	
	on btnCreateFloater pressed do CreateFloat stmUnits 355
)


-----------------------------------------------------------------------------------------------
-- GetcObject ------------------------------------------------------------------------------

fn GetcObject = (
	global cObject = undefined
	if (selection.count > 0) then (
		arrSelected = #()
		sArray = selection as array
		for s in sArray do (
			sClass = classOf s		
			sSuperClass = SuperClassOf s
			if (sSuperClass == GeometryClass) then (
				if cObject == undefined then cObject = s
				join arrSelected #(s)
			)
		)
	)
)


-----------------------------------------------------------------------------------------------
-- Set Pivot (to scene origin) --------------------------------------------------------------

fn SetPivot obj loc = (
	undo on (
		if (obj != undefined) then (
			arrSelection = (selection as array)
			if (isGroupMember obj == true) then (
				isGrouped = true
				for g in arrSelection where (isGroupHead g == true) do (setGroupOpen g true)
			) else isGrouped = false
			
			select obj
			if (loc == "Origin") then obj.pivot = [0,0,0]
			else centerPivot obj
			if (isGrouped == true) then for g in arrSelection where (isGroupHead g == true) do (setGroupOpen g false)
			select arrSelection
		)
		else 	messageBox message title:"Please select a mesh object." beep:false	
	)
)


-----------------------------------------------------------------------------------------------
-- Project Normals -------------------------------------------------------------------------

fn ProjectNormals pnstyle pnaxis pnskew = (
	stmRemoveScripts()
	
	with redraw off (
		undo on (
			GetcObject()
			if (cObject != undefined) then (
				arrSelection = (selection as array)
				
				if (isGroupMember cObject == true) then (
					isGrouped = true
					for g in arrSelection where (isGroupHead g == true) do (setGroupOpen g true)
					
				) else isGrouped = false
				
				max modify mode
				select cObject
				
				bBreakVerts = false
				if (cObject.modifiers["Projection Mesh"] == undefined) then (
					addModifier cObject(Edit_Mesh())
					cObject.modifiers[1].name = "Projection Mesh"
					bBreakVerts = true
				) else if (cObject.modifiers[2] != cObject.modifiers["Projection Mesh"] OR cObject.modifiers[1] != cObject.modifiers["Project Normals"]) then (
					deleteModifier cObject cObject.modifiers["Projection Mesh"]
					addModifier cObject(Edit_Mesh())
					cObject.modifiers[1].name = "Projection Mesh"
					bBreakVerts = true
				)
				
				if (bBreakVerts) then (
					modPanel.setCurrentObject cObject.modifiers["Projection Mesh"]				
					SubObjectLevel = 1
					vCount = getNumVerts cObject
					setVertSelection cObject cObject.modifiers["Projection Mesh"] #{1..vCount}
					meshOps.break cObject.modifiers["Projection Mesh"]
					setVertSelection cObject cObject.modifiers["Projection Mesh"] #{}	
					SubObjectLevel = 0
					modPanel.setCurrentObject cObject
				)
				
				-- Match indeces of vertices and normals
				vertIdArr = #()
				fCount = getNumFaces cObject.mesh
				vertIdArr[fCount * 3] = 0	-- initialize size of array by setting last value
				
				h = 1
				for f = 1 to fCount do (
					for v = 1 to 3 do (
						vertIdArr[h] = (getFace cObject.mesh f)[v] as integer
						h = h + 1
					)
				)
				
				vCount = vertIdArr.count
				for i = 1 to vCount do (
					k = i + 1
					while (k <= vertIdArr.count) do (
						if vertIdArr[k] == vertIdArr[i] then deleteitem vertIdArr k
						else k = k + 1
					)
				)
				
				if pnstyle == "" then (
					projectionStyle = stmTools.ddProjectionStyle.selected
				) else projectionStyle = pnstyle
				
				if pnaxis == "" then (
					projectionAxis = stmTools.ddProjectionAxis.selected
				) else projectionAxis = pnaxis
				
				if pnskew == "" then (
					projectionSkew = stmTools.slProjectBias.value
				) else projectionSkew = pnskew
				
				custAttribIndex = 0
--				-- This section looks for custom attributes to projected objects (disabled for SpeedTree 6.1)
-- 				i = 1
-- 				custAttribsCount = custAttributes.count cObject
-- 				if custAttribsCount > 0 then (
-- 					while (i <= custAttribsCount AND custAttribIndex == 0) do (
-- 						ca = custAttributes.get cObject i
-- 						if ca.name == "projectNormalsData" then (
-- 							custAttribIndex = i
-- 							ca.projectStyle = projectionStyle
-- 							ca.projectAxis = projectionAxis
-- 							ca.projectSkew = projectionSkew
-- 							
-- 							projectNormalsStyleInt = projectNormalsAxisInt = 1
-- 							if projectionStyle == "Cylindrical" then projectNormalsStyleInt = 2
-- 							if projectionAxis == "Y axis" then projectNormalsAxisInt = 2
-- 							if projectionAxis == "Z axis" then projectNormalsAxisInt = 3
-- 								
-- 							cObject.projectionParams.style_dd.selection = projectNormalsStyleInt
-- 							cObject.projectionParams.axis_dd.selection = projectNormalsAxisInt
-- 						) else (
-- 							i = i + 1
-- 						)
-- 					)
-- 				)
-- 				
				if custAttribIndex == 0 then (
					projectNormalsAttribs= attributes projectNormalsData (
						parameters main rollout:projectionParams (
							projectStyle type: #string default:stmTools.ddProjectionStyle.selected
							projectAxis type: #string default:stmTools.ddProjectionAxis.selected
							projectSkew type: #float ui:skew default: 0.5
							cbLoadProjection type: #boolean ui:load default:true
						)
						rollout projectionParams "Project Normals" (
							dropDownList style_dd "Style" items: #("Spherical", "Cylindrical") selection:stmTools.ddProjectionStyle.selection
							dropDownList axis_dd "Axis" items: #("X axis", "Y axis", "Z axis") selection:stmTools.ddProjectionAxis.selection
							spinner skew "Skew" type: #float range:[-1,1,(stmTools.txtProjectionSkew.text as float)] align:#left
							checkbox  load "Load on selection" checked: cbLoadProjection
							
							on style_dd selected i do projectStyle = style_dd.items [i]
							on axis_dd selected i do projectAxis = axis_dd.items [i]
						)
					)
					
--					-- This section adds custom attributes to projected objects (disabled for SpeedTree 6.1)
-- 					custAttributes.add cObject projectNormalsAttribs
-- 					cObject.projectNormalsData.projectStyle = stmTools.ddProjectionStyle.selected
-- 					cObject.projectNormalsData.projectAxis = stmTools.ddProjectionAxis.selected
-- 					cObject.projectNormalsData.projectSkew = (stmTools.txtProjectionSkew.text as float)
				)
				
				if (cObject.modifiers["Project Normals"] == undefined) then (
					addModifier cObject(Edit_Normals())
					cObject.modifiers[1].name = "Project Normals"
						
				) else if (cObject.modifiers[1] != cObject.modifiers["Project Normals"]) then (
					deleteModifier cObject cObject.modifiers["Project Normals"]
					addModifier cObject(Edit_Normals())
					cObject.modifiers[1].name = "Project Normals"
				)
				
				SubObjectLevel = 0
				cObject.modifiers["Project Normals"].Reset()		
				cObject.modifiers["Project Normals"].displayLength = 1				
				num = cObject.modifiers["Project Normals"].GetNumNormals()
				cObject.modifiers["Project Normals"].SetSelection #{1..num}
				cObject.modifiers["Project Normals"].Unify()
				
				rayStart = cObject.center	
				if (projectionStyle == "Spherical") then (	
					
					if (projectionAxis == "X axis") do (
						objLength = cObject.max.x - cObject.min.x
						objLength = objLength * (projectionSkew * 2)
						rayStart.x = rayStart.x - objLength
						
						objHeight = cObject.max.z - cObject.min.z
						objZOffset = objHeight * projectionSkew
						rayStart.z = rayStart.z - abs(objZOffset)
					)
					
					if (projectionAxis == "Y axis") do (
						objLength = cObject.max.y - cObject.min.y
						objLength = objLength * (projectionSkew * 2)
						rayStart.y = rayStart.y - objLength
						
						objHeight = cObject.max.z - cObject.min.z
						objZOffset = objHeight * projectionSkew
						rayStart.z = rayStart.z - abs(objZOffset)
					)
					
					if (projectionAxis == "Z axis") do (
						objLength = cObject.max.z - cObject.min.z
						objLength = objLength * (projectionSkew * 2)
						rayStart.z = rayStart.z - objLength
						
						objHeight = cObject.max.y - cObject.min.y
						objYOffset = objHeight * projectionSkew
						rayStart.y = rayStart.y - abs(objYOffset)
					)
				)
				
				vCount = vertIdArr.count	
				for n = 1 to vCount do (
					if projectionStyle == "Spherical" then (	-- Change normal to vector from object's center
						getVector = (getVert cObject vertIdArr[n]) - rayStart
					) else (-- Change normal to vector from object's center line
						if (projectionAxis == "X axis") do (
							objLength = cObject.max.x - cObject.min.x
							objLength = objLength*(projectionSkew)
							skewedX =  (getVert cObject vertIdArr[n]).x - objLength
							getVector = (getVert cObject vertIdArr[n]) - (point3 skewedX rayStart.y rayStart.z)
						)
						
						if (projectionAxis == "Y axis") do (
							objLength = cObject.max.y - cObject.min.y
							objLength = objLength*(projectionSkew)
							skewedY =  (getVert cObject vertIdArr[n]).y - objLength
							getVector = (getVert cObject vertIdArr[n]) - (point3 rayStart.x skewedY rayStart.z)
						)
						
						if (projectionAxis == "Z axis") do (
							objLength = cObject.max.z - cObject.min.z
							objLength = objLength*(projectionSkew)
							skewedZ =  (getVert cObject vertIdArr[n]).z - objLength
							getVector = (getVert cObject vertIdArr[n]) - (point3 rayStart.x rayStart.y skewedZ)
						)
					)
					
					objRotation = cObject.transform.rotationpart as matrix3
					objRotation = inverse objRotation
					getVector = getVector * objRotation
					
					cObject.modifiers["Project Normals"].SetNormal n getVector
					cObject.modifiers["Project Normals"].MakeExplicit()
				)
				
				
				cObject.modifiers["Project Normals"].SetSelection #{}
				SubObjectLevel = 0
				
				
				if (isGrouped == true) then for g in arrSelection where (isGroupHead g == true) do (setGroupOpen g false)
				select arrSelection
				
			) else 	messageBox message title:"Please select a mesh object." beep:false	
		)
	)
	stmCallbacks()
	if (stmTools.inDialog == false) then
		setCommandPanelTaskMode mode:#utility
		
	if (bBreakVerts) then ProjectNormals pnstyle pnaxis pnskew
)


-----------------------------------------------------------------------------------------------
-- Flip Normals (over an Axis) -------------------------------------------------------------

fn FlipNormals = (
	stmRemoveScripts()
	undo on (
		GetcObject()
		if (cObject != undefined) then (
			arrSelection = (selection as array)
			
			if (isGroupMember cObject == true) then (
				isGrouped = true
				for g in arrSelection where (isGroupHead g == true) do (setGroupOpen g true)
				
			) else isGrouped = false
			
			select cObject
			max modify mode
			if (cObject.modifiers["Project Normals"] != undefined) then (
				cObjectEditNormals = cObject.modifiers["Project Normals"]
			) else if (cObject.modifiers[#editnormals] != undefined) then (
				cObjectEditNormals = cObject.Edit_Normals
			) else if (cObject.modifiers[#editnormals] == undefined) then (
				addModifier cObject(Edit_Normals())
				cObjectEditNormals = cObject.Edit_Normals
			)
			
			XVal = 1
			YVal = 1
			ZVal = 1
			if stmTools.XSelect.checked == true then XVal = -1
			if stmTools.YSelect.checked == true then YVal = -1
			if stmTools.ZSelect.checked == true then ZVal = -1
			
			num = cObjectEditNormals.GetNumNormals()
			selectedNormals = cObjectEditNormals.GetSelection()
			if (selectedNormals == undefined OR (selectedNormals as array).count == 0) then
				selectedNormals = #{1..num}
		
			for i in selectedNormals do (
				cObjectEditNormals.SetSelection #{i}
				origNormal = cObjectEditNormals.GetNormal i
				
				if origNormal != undefined then (
					flippedNormal = (origNormal * [XVal,YVal,ZVal])
					cObjectEditNormals.SetNormal i flippedNormal
				)
				
				cObjectEditNormals.MakeExplicit()
			)
			
			cObjectEditNormals.SetSelection selectedNormals
			
			if (stmTools.inDialog == false) then
				setCommandPanelTaskMode mode:#utility
			
			if (isGrouped == true) then for g in arrSelection where (isGroupHead g == true) do (setGroupOpen g false)
			select arrSelection
		)
		else 	messageBox message title:"Please select a mesh object." beep:false	
	)
	stmCallbacks()
)


-----------------------------------------------------------------------------------------------
-- Clean Up Faces ---------------------------------------------------------------------------

fn CleanUpFaces = (
	undo on (
		GetcObject()
		if (cObject != undefined) then (
			arrSelection = (selection as array)
			
			if (isGroupMember cObject == true) then (
				isGrouped = true
				for g in arrSelection where (isGroupHead g == true) do (setGroupOpen g true)
				
			) else isGrouped = false
			select cObject	
					
			if (classof cObject.baseObject == Editable_Mesh AND classof cObject == Editable_Mesh) then (
				
				oldFaceCount = getNumFaces cObject
				oldVertCount = getNumVerts cObject
				
				global faceSel = #()
				fCount = cObject.numfaces
				for f = 1 to fCount do (
					if ((meshop.getFaceArea cObject #{f}) < stmTools.spCleanBias.value) then (
						append faceSel f
					)
				)
				
				setfaceselection cObject faceSEl
				meshop.deleteFaces cObject faceSel
				meshop.removeDegenerateFaces cObject	
				meshop.removeIllegalFaces cObject			
				isoVerts = meshop.getIsoVerts cObject
				meshop.deleteVerts  cObject isoVerts
				
				newFaceCount = getNumFaces cObject
				newVertCount = getNumVerts cObject
				
				message = (oldFaceCount - newFaceCount) as string + " triangles and " + (oldVertCount - newVertCount) as string + " vertices removed."
				messageBox message title:"Remove Small Faces Tool" beep:false	
				
			) else if  (classof cObject.baseObject == Editable_Poly AND classof cObject == Editable_Poly) then ( 
				
				oldFaceCount = polyop.getNumFaces cObject
				oldVertCount = polyop.getNumVerts cObject
				
				faceSel = #()
				fCount = cObject.numfaces
				for f = 1 to fCount do (
					if ((polyop.getFaceArea cObject f) < stmTools.spCleanBias.value) then (
						append faceSel f
					)
				)
				
				polyop.deleteFaces cObject faceSel
				newFaceCount = polyop.getNumFaces cObject
				newVertCount = polyop.getNumVerts cObject
				
				message = (oldFaceCount - newFaceCount) as string + " triangles and " + (oldVertCount - newVertCount) as string + " vertices removed. \n\n Please note that this tool is much more effective on editable mesh objects rather than editable polys since it can take into account individual triangles only with an editable mesh object."
				messageBox message title:"Remove Small Faces Tool" beep:false	
			) else (
				messageBox "This tool requires an editable mesh or poly object (without modifiers)." title:"Please select a mesh or poly object." beep:false	
			)
			
			if (isGrouped == true) then for g in arrSelection where (isGroupHead g == true) do (setGroupOpen g false)
			select arrSelection
		)
		else 	messageBox message title:"Please select a mesh or poly object." beep:false	
	)
)


------------------------------------------------------------------------------------------------
-- UnitizeMesh -------------------------------------------------------------------------------

fn UnitizeMesh unitScalar = (
	undo on (
		GetcObject()
		if (cObject != undefined) then (
			if (isGroupMember cObject == true AND isOpenGroupMember cObject == false) then (
				while (isGroupHead cObject == false) do 
					cObject = cObject.parent
				
				arrSelected = #(cObject)
			)
			
			for s in arrSelected do (
				Xdistance = s.max.x - s.min.x
				Ydistance = s.max.y - s.min.y
				Zdistance = s.max.z - s.min.z
				
				maxDistance = Xdistance
				if (YDistance > maxDistance) then maxDistance = Ydistance
				if (ZDistance > maxDistance) then maxDistance = Zdistance
				
				s.scale = (s.scale / maxDistance) * [unitScalar, unitScalar, unitScalar]
			)
		)
	)
)


------------------------------------------------------------------------------------------------
-- ConvertToTriFoil -------------------------------------------------------------------------

fn ConvertToTriFoil = (
	GetcObject()
	if (cObject != undefined) then (
		arrSelection = (selection as array)
		if (isGroupMember cObject == true) then (
			isGrouped = true
			for g in arrSelection where (isGroupHead g == true) do (setGroupOpen g true)
		) else isGrouped = false
		
		with redraw off (
			tmpFoil1 = snapshot cObject
			tmpFoil2 = snapshot cObject
			tmpFoil3 = snapshot cObject
			ResetXForm tmpFoil1
			ResetXForm tmpFoil2
			ResetXForm tmpFoil3
			ConvertToMesh tmpFoil1
			ConvertToMesh tmpFoil2
			ConvertToMesh tmpFoil3
			tmpFoil1.pos = [0, 0, 0]
			tmpFoil2.pos = [0, 0, 0]
			tmpFoil3.pos = [0, 0, 0]
			tmpFoil1.rotation = (matrix3 [1.78814e-007,0.707107,-0.707106] [0,0.707106,0.707107] [1,0,1.78814e-007] [0,0,0])
			tmpFoil2.rotation = (matrix3 [0.146447,0.853554,-0.5] [-0.853553,-0.146446,-0.5] [-0.5,0.5,0.707107] [0,0,0])
			tmpFoil3.rotation = (matrix3 [-0.146446,-0.853553,0.5] [0.853553,0.146447,0.5] [-0.5,0.5,0.707107] [0,0,0])
			meshop.attach tmpFoil1 tmpFoil2
			meshop.attach tmpFoil1 tmpFoil3
			
			ResetXForm tmpFoil1
			ConvertToMesh tmpFoil1
			select tmpFoil1
			UnitizeMesh(stmUnits.spUnitizeScalar.value)
			ProjectNormals "Spherical" "Y axis" 0.0
			maxOps.CollapseNodeTo tmpFoil1 2 true
			
			triFoilName = (cObject.name + "_Tri-Foil")
			if (getNodeByName triFoilName != undefined) then
				tmpFoil1.name = uniqueName triFoilName
			else
				tmpFoil1.name = triFoilName
		)
		
		if (isGrouped == true) then for g in arrSelection where (isGroupHead g == true) do (setGroupOpen g false)
		select arrSelection
	)
)


------------------------------------------------------------------------------------------------
-- CleanUpStreaks ---------------------------------------------------------------------------

fn CleanUpStreaks = (
	GetcObject()
	if (cObject != undefined) then (
		arrSelection = (selection as array)
		if (isGroupMember cObject == true) then (
			isGrouped = true
			for g in arrSelection where (isGroupHead g == true) do (setGroupOpen g true)
			
		) else isGrouped = false
		select cObject	
		
		arrStreakedFaces = #{}
		if (SuperClassOf cObject == GeometryClass AND classOf cObject.baseObject == Editable_Mesh) then (
			objFaces = cObject.numfaces
			for f = 1 to objFaces do (
				objFace = getTVFace cObject f
				v1 = getTVert cObject objFace[1]
				v2 = getTVert cObject objFace[2]
				v3 = getTVert cObject objFace[3]
				
				if (v1 == v2 OR v2 == v3 OR v1 == v3) then
					arrStreakedFaces[f] = true
			)
			
			setFaceSelection cObject arrStreakedFaces
			if arrStreakedFaces.count > 0 then (
				max modify mode
				SubObjectLevel = 3
			)
			message = (arrStreakedFaces as array).count as string + " triangles identified and selected."
			messageBox message title:"Select Streaked Triangles Tool" beep:false	
			
		) else if (SuperClassOf cObject == GeometryClass AND classOf cObject.baseObject == Editable_Poly) then (
			if (cObject.GetNumMapChannels() >= 2) then (
				activeMapChannel = 1
				while (cObject.GetMapChannelActive activeMapChannel == false AND activeMapChannel < 100) do
					activeMapChannel = activeMapChannel + 1
				
				objFaces = cObject.GetNumFaces()
				for f = 1 to objFaces do (
					local vertID = 0
					local faceVert = 1
					local arrTexCoords = #()
					while vertID != -1 do (
						local vertID = cObject.GetMapFaceVertex activeMapChannel f faceVert
						
						if vertID > 0 then (
							vertTexCoords = cObject.GetMapVertex activeMapChannel vertID
							if (findItem arrTexCoords vertTexCoords == 0) then (
								append arrTexCoords vertTexCoords
							) else (	-- mark as dirty
								arrStreakedFaces[f] = true
								vertID = -1						
							)
						)
						
						faceVert = faceVert + 1
					)
				)
				
				polyop.setFaceSelection cObject arrStreakedFaces
				if arrStreakedFaces.count > 0 then (
					max modify mode
					SubObjectLevel = 4
				)
				message = (arrStreakedFaces as array).count as string + " triangles identified and selected. \n\nPlease note some of the streaked triangles may be part of larger polys. For more accurate results apply this tool to an editable mesh object."
				messageBox message title:"Select Streaked Triangles Tool"  beep:false	
				
			) else (
				print "no active map channels"
			)
		) else (
			messageBox "This tool requires an editable mesh or poly object." title:"Please select a mesh or poly object." beep:false	
		)
			
		if (isGrouped == true) then for g in arrSelection where (isGroupHead g == true) do (setGroupOpen g false)
		select arrSelection
		
	) else messageBox message title:"Please select a mesh or poly object." beep:false	
)


------------------------------------------------------------------------------------------------
-- ClampDetailTexture ----------------------------------------------------------------------

fn ClampDetailTexture = (
	getCObject()
	if (cObject != undefined) then (
		arrSelection = (selection as array)
		if (isGroupMember cObject == true) then (
			isGrouped = true
			for g in arrSelection where (isGroupHead g == true) do (setGroupOpen g true)
		) else isGrouped = false
		select cObject
		if (SuperClassOf cObject == GeometryClass AND (classOf cObject.baseObject == Editable_Mesh OR classOf cObject.baseObject == Editable_Poly)) then (
			max modify mode
			undo on (
				startModifiers = cObject.modifiers.count
				modPanel.setCurrentObject cObject
				SubObjectLevel = 4
				modPanel.addModToSelection (UVWMap()) before:startModifiers
				modPanel.addModToSelection (UVW_Xform())
				modPanel.setCurrentObject cObject.modifiers[startModifiers + 2]
				cObject.modifiers[startModifiers + 2].maptype = 4
				cObject.modifiers[startModifiers + 2].utile = 0.0001
				cObject.modifiers[startModifiers + 2].vtile = 0.0001
				cObject.modifiers[startModifiers + 2].mapChannel = 2
				cObject.modifiers[startModifiers + 1].V_Offset = 0.99
				cObject.modifiers[startModifiers + 1].U_Offset = 0.01
				cObject.modifiers[startModifiers + 1].Map_Channel = 2
				maxOps.CollapseNodeTo cObject (startModifiers + 1) true
			)
		) else messageBox "This tool requires an editable mesh or poly object." title:"Please select a mesh or poly object." beep:false	
		
		if (stmTools.inDialog == false) then
			setCommandPanelTaskMode mode:#utility
		
		if (isGrouped == true) then for g in arrSelection where (isGroupHead g == true) do (setGroupOpen g false)
		select arrSelection
	)
)


------------------------------------------------------------------------------------------------
--  AddDetailLayer --------------------------------------------------------------------------

fn AddDetailLayer = (
	fileDetailTexture = getOpenFileName caption:"Select a detail texture (with alpha)" types:"Targa Image File (*.tga)|*.tga|PNG Image File (*.png)|*.png|TIFF Image File (*.tif)|*.tif|All Files (*.*)|*.*"
	if fileDetailTexture != undefined then (
		
		getCObject()
		if cObject != undefined AND appVersion >= 11 then (
			arrSelection = (selection as array)
			if (isGroupMember cObject == true) then (
				isGrouped = true
				for g in arrSelection where (isGroupHead g == true) do (setGroupOpen g true)
			) else isGrouped = false
			select cObject
			
			matCObject = cObject.material
			if classOf matCObject == StandardMaterial then (
				if (classOf matCObject.diffuseMap == BitmapTexture) then (
					fileOldBitmap = matCObject.diffuseMap.filename
					matCObject.diffuseMap = CompositeTexture()
					matCObject.diffuseMap.mapList[1] = BitmapTexture()
					matCObject.diffuseMap.mapList[1].filename = fileOldBitmap
					matCObject.diffuseMap.add()
					matCObject.diffuseMap.mapList[2] = BitmapTexture()
					matCObject.diffuseMap.mapList[2].filename = fileDetailTexture
					matCObject.diffuseMap.mapList[2].coordinates.mapChannel = 2
					
					if (matCObject.diffuseMap.mapList[2].bitmap.hasAlpha) then (
						matCObject.diffuseMap.mask[2] = copy matCObject.diffuseMap.mapList[2]
						matCObject.diffuseMap.mask[2].monoOutput = 1
						matCObject.diffuseMap.mask[2].RGBOutput = 1
						matCObject.diffuseMap.mask[2].alphasource = 0
					)
					
					showTextureMap matCObject matCObject.diffuseMap on
				) else if (classOf matCObject.diffuseMap == CompositeTexture) then (
					if (matCObject.diffuseMap.mapList.count == 2) then (
						matCObject.diffuseMap.mapList[2].filename = fileDetailTexture
						matCObject.diffuseMap.mask[2].filename = fileDetailTexture
					)						
				)
			) else messageBox "A standard material is required." title:"Error" beep:false	
			
			if (isGrouped == true) then for g in arrSelection where (isGroupHead g == true) do (setGroupOpen g false)
			select arrSelection
		)
	)
)


------------------------------------------------------------------------------------------------
-- ExportSTFFile ----------------------------------------------------------------------------

fn CompareInstNames n1 n2 = (
	case of (
		(n1.name < n2.name): -1
		(n1.name > n2.name): 1
		default: 0
	)
)

fn ExportSTF = (
	cObjects = selection as array
				
	if cObjects.count == 1 then exportSTFName = cObjects[1].name
	else exportSTFName = substring maxfilename 1 ((maxfilename as string).count - 4)
	
	if (stmForest.rbWorldDataFormat.state == 1) then ( -- SWA
		stfFilename = getSaveFileName "Export SWA" types:"SpeedTree World ASCII (*.swa)|*.swa|All Files (*.*)|*.*" filename:exportSTFName historyCategory:"SpeedTreeWorldFiles"
		bAsSWA = true
	) else ( -- STF
		stfFilename = getSaveFileName "Export STF" types:"SpeedTree Forest (*.stf)|*.stf|All Files (*.*)|*.*" filename:exportSTFName historyCategory:"SpeedTreeWorldFiles"
		bAsSWA = false
	)
	
	if stfFilename != undefined then (
		if stmForest.cbCreateSelectionSet.checked == true then (
			selectionSetName = getFilenameFile stfFilename
			SelectionSets[selectionSetName] = cObjects
		)
		
		if stfFilename != undefined then (
			stfFile = createFile stfFilename
			if stfFile != undefined then (
				o = 1
				iTreeRunningTotal = 0
				iInstRunningTotal = 0
				local isGrouped = false
				
				while (cObjects.count > 0) do (
					if (isGroupHead cObjects[o] == false) then (
							
						InstanceMgr.GetInstances cObjects[o] &oInstances
						if (oInstances.count > 1) then (
							selectedInstances = for n in oInstances where (areNodesInstances cObjects[o] n AND findItem cObjects n != 0) collect n
							qsort selectedInstances CompareInstNames
						) else selectedInstances = #(cObjects[o])
						
						strFirstInstanceName = selectedInstances[1].name
						if (stmForest.cbSrtExtension.checked == true) then
							strFirstInstanceName = strFirstInstanceName + ".SRT"
						
						if bAsSWA == true then (
							strFirstInstanceName = "\"" + strFirstInstanceName + "\""
							format "%\n" strFirstInstanceName to:stfFile
						) else (
							format "%\n" strFirstInstanceName to:stfFile
						)
						
						format "\t%\n" selectedInstances.count to:stfFile
						
						for s in selectedInstances do (
							sPosX = s.position.x
							sPosY = s.position.y
							sPosZ = s.position.z
							sRotAngle = s.rotation.angle * 0.0174532925
							sRotationMatrix = s.rotation as eulerAngles
							sRotationMatrix = sRotationMatrix as matrix3
							
							--transpose the matrix manually
							transRight = (point3 sRotationMatrix[1][1] sRotationMatrix[2][1] sRotationMatrix[3][1])
							transOut = (point3 sRotationMatrix[1][2] sRotationMatrix[2][2] sRotationMatrix[3][2])
							transUp = (point3 sRotationMatrix[1][3] sRotationMatrix[2][3] sRotationMatrix[3][3])
							sRotationMatrix = (matrix3 transRight transOut transUp [0,0,0])
							
							sRightMatrix = [1,0,0] * sRotationMatrix
							sUpMatrix = [0,0,1] * sRotationMatrix
							arrRightMatrix = #(sRightMatrix.x, sRightMatrix.y, sRightMatrix.z)
							arrUpMatrix = #(sUpMatrix.x, sUpMatrix.y, sUpMatrix.z)
							sScaleMatrix = s.scale
							sScale = sScaleMatrix[1]
							if (sScaleMatrix[2] > sScale) then sScale = sScaleMatrix[2]
							if (sScaleMatrix[3] > sScale) then sScale = sScaleMatrix[3]
							
							-- make ints
							if (mod sPosX 1 == 0.0) then sPosX = int(sPosX)
							if (mod sPosY 1 == 0.0) then sPosY = int(sPosY)
							if (mod sPosZ 1 == 0.0) then sPosZ = int(sPosZ)
							if (mod sRotAngle 1 == 0.0) then sRotAngle = int(sRotAngle)
							for v = 1 to 3 do if (mod arrRightMatrix[v] 1 == 0.0) then arrRightMatrix[v] = int(arrRightMatrix[v])
							for v = 1 to 3 do if (mod arrUpMatrix[v] 1 == 0.0) then arrUpMatrix[v] = int(arrUpMatrix[v])
							if (mod sScale 1 == 0.0) then sScale = int(sScale)
							
							if bAsSWA == true then -- SWA
								format "\t% % % % % % % % % %\n" sPosX sPosY sPosZ arrUpMatrix[1] arrUpMatrix[2] arrUpMatrix[3] arrRightMatrix[1] arrRightMatrix[2] arrRightMatrix[3] sScale to:stfFile
							else -- STF
								format "\t% % % % %\n" sPosX sPosY sPosZ sRotAngle sScale to:stfFile
							
							bFindS = findItem cObjects s
							if bFindS != 0 then deleteItem cObjects bFindS
						)
						iInstRunningTotal = iInstRunningTotal + selectedInstances.count
						iTreeRunningTotal = iTreeRunningTotal  + 1
						format "\n\n" to:stfFile
					) else deleteItem cObjects o
				)
				
				close stfFile
				strRunningTotal = (iTreeRunningTotal as string) + " trees (" + (iInstRunningTotal as string) + " instances) written to " + stfFilename
				print strRunningTotal
			)
		)
	)
)

fn RenameInSelection = (
	strToFind = stmForest.txtFindString.text
	strSubstitute = stmForest.txtSubstituteString.text
	StringLength = strToFind.count
	if (strToFind != "" AND strSubstitute != "") then (
		for s in (selection as array) do (
			StringPos = findString s.name strToFind
			if (StringPos != 0 AND StringPos != undefined) then
				s.name = (replace s.name StringPos StringLength strSubstitute)
		)
	) else print "Please provide a search term and substitute string."
)


------------------------------------------------------------------------------------------------
-- ImportSWAFile ----------------------------------------------------------------------------

fn ImportSWA = (
	
	arrObjects = #()
	arrObjNames = #()
	arrObjCount = #()
	arrTranslate = #()
	arrUpRotation = #()
	arrRightRotation = #()
	arrOutRotation = #()
	arrScale = #()
	
	-- initialize lengths for speedier bitArrays
	totalTime = 0	
	initObjs = 100
	initInsts = 25000	-- set this buffer to the max instances you expect to make
	arrObjects[initObjs] = ""
	arrObjNames[initObjs] = ""
	arrObjCount[initObjs] = 0
	arrTranslate[initInsts] = (point3 0 0 0)
	arrUpRotation[initInsts] = (point3 0 0 0)
	arrRightRotation[initInsts] = (point3 0 0 0)
	arrOutRotation[initInsts] = (point3 0 0 0)
	arrScale[initInsts] = 1

	swaFilename = getOpenFileName "Import SWA" types:"SpeedTree World ASCII (*.swa)|*.swa|All Files (*.*)|*.*"
	if swaFilename != undefined then (
		
		swaFile = openFile swaFilename
		if swaFile != undefined then (
			with redraw off (
				oCount = 0
				tCount = 0
				bReachedEnd = false
				while (bReachedEnd == false) do (
					swa_tree = ""
					while (swa_tree == "" OR swa_tree == "\t") do ( 
						if eof swaFile == false then (
							swa_tree = readLine swaFile
							swa_tree = (filterstring swa_tree "\"")[1]
							oCount = oCount + 1
						) else ( 
							bReachedEnd = true
							swa_tree = undefined
						)
					)
					
					if (swa_tree  != "" AND swa_tree != "\t" AND bReachedEnd == false) do (
						if (oCount <= initObjs) then 
							arrObjNames[oCount] = swa_tree
						else append arrObjNames swa_tree
							
						swa_count = (readLine swaFile) as integer
						if (oCount <= initObjs) then
							arrObjCount[oCount] = swa_count
						else append arrObjCount swa_count
						
						for t = 1 to swa_count do (
							tCount = tCount + 1
							pos_x = readValue swaFile
							pos_y = readValue swaFile
							pos_z = readValue swaFile
							upMatrix_x = readValue swaFile
							upMatrix_y = readValue swaFile
							upMatrix_z = readValue swaFile
							rightMatrix_x = readValue swaFile
							rightMatrix_y = readValue swaFile
							rightMatrix_z = readValue swaFile
							scale_factor = readValue swaFile
							
							if (tCount <= initInsts) then (
								arrTranslate[tCount] = (point3 pos_x pos_y pos_z)
								arrUpRotation[tCount] = (point3 upMatrix_x upMatrix_y upMatrix_z)
								arrRightRotation[tCount] = (point3 rightMatrix_x rightMatrix_y rightMatrix_z)
								arrOutRotation[tCount] = normalize (cross arrUpRotation[tCount] arrRightRotation[tCount])
								arrScale[tCount] = scale_factor
							) else (
								append arrTranslate (point3 pos_x pos_y pos_z)
								append arrUpRotation = (point3 upMatrix_x upMatrix_y upMatrix_z)
								append arrRightRotation = (point3 rightMatrix_x rightMatrix_y rightMatrix_z)
								append arrOutRotation = normalize (cross arrUpRotation[arrUpRotation.count] arrRightRotation[arrRightRotation.count])
								append arrScale scale_factor
							)
						)
					)
				)
				close swaFile
				
				arrObjects.count = oCount
				arrObjNames.count = oCount
				arrObjCount.count = oCount
				arrTranslate.count = tCount
				arrUpRotation.count = tCount
				arrRightRotation.count = tCount
				arrScale.count = tCount
				
				for o = 1 to oCount do (
					
					sceneObj = getNodeByName (arrObjNames[o] as string)
					if (sceneObj == undefined) then (
						strDlgTitle = "Select a proxy object for " + (arrObjNames[o] as string)
						sceneObj = selectByName single:true title:strDlgTitle buttonText:"Select Object" 
					)
					arrObjects[o] = sceneObj
				)
				
				inst = tally = 0
				undo on (
					for o = 1 to oCount do (
						
						sceneObj = arrObjects[o]
						if (sceneObj != undefined) then (
							
							thisSource = #(sceneObj)
							thisInst = undefined
							iCount = arrObjCount[o]
							for i = 1 to iCount do (
								maxOps.CloneNodes sceneObj cloneType:#instance expandHierarchy:true actualNodeList:&thisSource newNodes:&thisInst
								
								inst += 1
								tally += 1
								thisInst[1].position = arrTranslate[inst]
								thisInst[1].scale = (point3 arrScale[inst] arrScale[inst] arrScale[inst])
								
								in coordsys (transmatrix thisInst[1].transform.pos) (
									--transpose the matrix manually
									transRight = (point3 arrRightRotation[inst][1] arrOutRotation[inst][1] arrUpRotation[inst][1])
									transOut = (point3 arrRightRotation[inst][2] arrOutRotation[inst][2] arrUpRotation[inst][2])
									transUp = (point3 arrRightRotation[inst][3] arrOutRotation[inst][3] arrUpRotation[inst][3])
									thisInst[1].rotation = (matrix3 transRight transOut transUp [0,0,0])
								)
							)
						) else (
							inst += arrObjCount[o]
							tmpMessage = (arrObjNames[o] as string) + " was skipped by user or was undefined"
							print tmpMessage
						)				
					)
				)
				strTally = (tally as string) + " instances created"
			)
		)
	)
)


------------------------------------------------------------------------------------------------
-- ImportSTFFile ----------------------------------------------------------------------------

fn ImportSTF = (
	
	arrObjects = #()
	arrObjNames = #()
	arrObjCount = #()
	arrTranslate = #()
	arrRotate = #()
	arrScale = #()
	
	-- initialize lengths
	totalTime = 0	
	initObjs = 100
	initInsts = 25000
	arrObjects[initObjs] = ""
	arrObjNames[initObjs] = ""
	arrObjCount[initObjs] = 0
	arrTranslate[initInsts] = (point3 0 0 0)
	arrRotate[initInsts] = 0
	arrScale[initInsts] = 1

	stfFilename = getOpenFileName "Import STF" types:"SpeedTree Forest (*.stf)|*.stf|All Files (*.*)|*.*"
	if stfFilename != undefined then (
		
		stfFile = openFile stfFilename
		if stfFile != undefined then (
			oCount = 0
			tCount = 0
			bReachedEnd = false
			while (bReachedEnd == false) do (
				stf_tree = ""
				while (stf_tree == "" OR stf_tree == "\t") do ( 
					if eof stfFile == false then (
						stf_tree = readLine stfFile
						oCount = oCount + 1
					) else ( 
						bReachedEnd = true
						stf_tree = undefined
					)
				)
				
				if (stf_tree  != "" AND stf_tree != "\t" AND bReachedEnd == false) do (
					if (oCount <= initObjs) then 
						arrObjNames[oCount] = stf_tree
					else append arrObjNames stf_tree
						
					stf_count = (readLine stfFile) as integer
					if (oCount <= initObjs) then
						arrObjCount[oCount] = stf_count
					else append arrObjCount stf_count
					
					for t = 1 to stf_count do (
						tCount = tCount + 1
						pos_x = readValue stfFile
						pos_y = readValue stfFile
						pos_z = readValue stfFile
						rot_angle = readvalue stfFile
						scale_factor = readValue stfFile
						
						if (tCount <= initInsts) then (
							arrTranslate[tCount] = (point3 pos_x pos_y pos_z)
							arrRotate[tCount] = rot_angle
							arrScale[tCount] = scale_factor
						) else (
							append arrTranslate (point3 pos_x pos_y pos_z)
							append arrRotate rot_angle
							append arrScale scale_factor	
						)
					)
				)
			)
			close stfFile
			
			arrObjects.count = oCount
			arrObjNames.count = oCount
			arrObjCount.count = oCount
			arrTranslate.count = tCount
			arrRotate.count = tCount
			arrScale.count = tCount
			
			for o = 1 to oCount do (
				
				sceneObj = getNodeByName (arrObjNames[o] as string)
				if (sceneObj == undefined) then (
					strDlgTitle = "Select a proxy object for \"" + (arrObjNames[o] as string) + "\""
					sceneObj = selectByName single:true title:strDlgTitle buttonText:"Select Object" 
				)
				
				arrObjects[o] = sceneObj
			)
			
			inst = tally = 0						
			undo on (
				for o = 1 to oCount do (
					
					sceneObj = arrObjects[o]
					if (sceneObj != undefined) then (
						
						thisSource = #(sceneObj)
						thisInst = undefined
						iCount = arrObjCount[o]
						for i = 1 to iCount do (
							maxOps.CloneNodes sceneObj cloneType:#instance expandHierarchy:true actualNodeList:&thisSource newNodes:&thisInst
							
							inst += 1
							tally += 1
							thisInst[1].position = arrTranslate[inst]
							thisInst[1].scale = (point3 arrScale[inst] arrScale[inst] arrScale[inst])
							
							rotAngle = (arrRotate[inst] * 57.2957795) -- radians to degrees
							in coordsys (transmatrix thisInst[1].transform.pos) 
								thisInst[1].rotation = (angleAxis rotAngle [0,0,1])
						)
					) else (
						inst += arrObjCount[o]
						tmpMessage = (arrObjNames[o] as string) + " was skipped by user or was undefined"
						print tmpMessage
					)				
				)
			)
			strTally = (tally as string) + " instances created"
		)
	)
)


------------------------------------------------------------------------------------------------
-- ImportSavedCameras ---------------------------------------------------------------------

fn ImportSavedCameras = (
	arrTranslate = #()
	arrRotate = #()

	cameraFilename = getOpenFileName "Import Saved Cameras" types:"Saved Cameras (*.txt)|*.txt|All Files (*.*)|*.*"
	if cameraFilename != undefined then (
		
		cameraFile = openFile cameraFilename
		if cameraFile != undefined then (
			
			bReachedEnd = false
			while (bReachedEnd == false) do (
						
				pos_x = readValue cameraFile
				pos_y = readValue cameraFile
				pos_z = readValue cameraFile
				append arrTranslate (point3 pos_x pos_y pos_z)
				
				rot_z = readValue cameraFile
				rot_y = readValue cameraFile
				append arrRotate (point2 rot_z rot_y)
				
				if eof cameraFile == true then 
					bReachedEnd = true
			)
			close cameraFile
			
			undo on (
				cCount = arrTranslate.count
				for c = 1 to cCount do (
						
					cam = freeCamera()
					cam.fov = 60
					cam.rotation = (quat 0.5 -0.5 -0.5 0.5)
					resetXForm cam
					
					rotAngle = -(arrRotate[c].y * 57.2957795) -- radians to degrees
					cam.rotation =  (angleAxis rotAngle [0,1,0])	
					resetXForm cam
					
					rotAngle = (arrRotate[c].x * 57.2957795) -- radians to degrees
					cam.rotation = (angleAxis rotAngle [0,0,1])
					
					cam.position = arrTranslate[c]
				)
			)
		)
	)
)


------------------------------------------------------------------------------------------------
-- Create Float ------------------------------------------------------------------------------

fn CreateFloat bar height = (
		if (bar != undefined) AND bar.open do (
			removeRollout bar
			DestroyDialog bar
		)
		
		createDialog bar 162 height style:#(#style_toolwindow,#style_sysmenu) lockwidth:true lockheight:true
		if (bar.inDialog) then (
			bar.btnCreateFloater.visible = false
			UpdateList()
		)
)


-----------------------------------------------------------------------------------------------
-- The current selection set should be listed in the object list -------------------------

fn UpdateList = (
		disableSceneRedraw()
		GetcObject()
		if (selection.count > 0 AND cObject != undefined) then (
			sClass = classOf cObject			
			if (cObject.modifiers["Hair and Fur"] == undefined AND sClass != mr_Proxy AND sClass != Targetobject AND sClass != Missing_GeomObject AND sClass != SpeedTree_4 AND sClass != SpeedTree) then (
				stm.lblObjName.text = "- " + cObject.name + " -"
				stm.lblObjFaces.text = cObject.mesh.numfaces as string + " triangles"
				stm.lblObjFaces.enabled = true
				
				-- Get dimensions in display units
				oldTM = cObject.transform
				cObject.transform = matrix3 1
				mDimensions = cObject.max - cObject.min
				cObject.transform = oldTM
				xDim = substring ((mDimensions[1] * cObject.scale.x) as string) 1 7
				yDim = substring ((mDimensions[2] * cObject.scale.y) as string) 1 7
				zDim = substring ((mDimensions[3] * cObject.scale.z) as string) 1 7
					
			--	if (stm.cbConvertUnits.enabled == true AND stm.cbConvertUnits.checked == true) then (
			--		xDim = units.formatValue (mDimensions[1] * cObject.scale.x) 
			--		yDim = units.formatValue (mDimensions[2] * cObject.scale.y)
			--		zDim = units.formatValue (mDimensions[3] * cObject.scale.z)
			--	)
				
				stm.lblObjDimensions.text = "(" + xDim + ", " + yDim + ", " + zDim + ")"	
				stm.lblObjDimensions.enabled = true
				stm.btnExportMesh.enabled = true
				stm.btnExportByMaterial.enabled = true
				stmTools.btnFlipNormals.enabled = true
				stmTools.btnSetPivot.enabled = true
				stmTools.btnCleanFaces.enabled = true
				stmTools.btnConvertToTriFoil.enabled = true
				stmTools.btnCleanStreaks.enabled = true
				stmTools.btnClampDetail.enabled = true
				stmTools.btnAddDetailLayer.enabled = true
				stmTools.btnProjectNormals.enabled = true
				
				i = 1
				custAttribIndex = 0
				custAttribsCount = custAttributes.count cObject
				if custAttribsCount > 0 then (
					while (i <= custAttribsCount AND custAttribIndex == 0) do (
						ca = custAttributes.get cObject i
						if ca.name == "projectNormalsData" then (
							custAttribIndex = i
							if cObject.projectNormalsData.cbLoadProjection == true then (
								projectNormalsStyleInt = projectNormalsAxisInt = 1
								if cObject.projectNormalsData.projectStyle == "Cylindrical" then projectNormalsStyleInt = 2
								if cObject.projectNormalsData.projectAxis == "Y axis" then projectNormalsAxisInt = 2
								if cObject.projectNormalsData.projectAxis == "Z axis" then projectNormalsAxisInt = 3
								stmTools.ddProjectionStyle.selection = projectNormalsStyleInt
								stmTools.ddProjectionAxis.selection = projectNormalsAxisInt
								stmTools.slProjectBias.value = (cObject.projectNormalsData.projectSkew as float)
								stmTools.txtProjectionSkew.text = (cObject.projectNormalsData.projectSkew as string)
							)
						) else (
							i = i + 1
						)
					)
				)
				
			) else (
				stm.lblObjName.text = "- No mesh selected -"
				stm.lblObjFaces.text = "0 triangles"
				stm.lblObjFaces.enabled = false
				stm.lblObjDimensions.text = "(0, 0, 0)"
				stm.lblObjDimensions.enabled = false
				stm.btnExportMesh.enabled = false
				stm.btnExportByMaterial.enabled = false
				stmTools.btnProjectNormals.enabled = false
				stmTools.btnFlipNormals.enabled = false
				stmTools.btnSetPivot.enabled = false
				stmTools.btnCleanFaces.enabled = false
				stmTools.btnConvertToTriFoil.enabled = false
				stmTools.btnCleanStreaks.enabled = false
				stmTools.btnClampDetail.enabled = false
				stmTools.btnAddDetailLayer.enabled = false
			)
			
			stmForest.btnMakeSTF.enabled = true
			stmForest.btnRenameInSelection.enabled = true
			stmUnits.btnUnitizeMesh.enabled = true
			stmUnits.btnConvertUnits.enabled = true		
			stmUnits.pbChooseTarget.enabled = true
				
		) else (
			stm.lblObjName.text = "- No mesh selected -"
			stm.lblObjFaces.text = "0 triangles"
			stm.lblObjFaces.enabled = false
			stm.lblObjDimensions.text = "(0, 0, 0)"
			stm.lblObjDimensions.enabled = false
			stm.btnExportMesh.enabled = false
			stm.btnExportByMaterial.enabled = false
			stmTools.btnProjectNormals.enabled = false
			stmTools.btnFlipNormals.enabled = false
			stmTools.btnSetPivot.enabled = false
			stmTools.btnCleanFaces.enabled = false
			stmTools.btnConvertToTriFoil.enabled = false
			stmTools.btnCleanStreaks.enabled = false
			stmTools.btnClampDetail.enabled = false
			stmTools.btnAddDetailLayer.enabled = false
			stmForest.btnMakeSTF.enabled = false
			stmForest.btnRenameInSelection.enabled = false
			stmUnits.btnUnitizeMesh.enabled = false
			stmUnits.btnConvertUnits.enabled = false		
			stmUnits.pbChooseTarget.enabled = false
		)
		
		enableSceneRedraw()
)

fn AddChangeHandler = (
	UpdateList()
	if (selection.count > 0 AND getCommandPanelTaskMode() == #utility) then (
	--	when parameters selection change id:#stmChangeHandler do UpdateList()
	--	when parameters selection change id:#stmChangeHandler handleAt:#redrawViews do UpdateList()

	)
)

------------------------------------------------------------------------------------------------
-- Convert Units -----------------------------------------------------------------------------

fn ConvertUnits obj = (
	if (units.displayType != #Generic AND units.displayType != units.SystemType) do (
		
		global strOldSystemScale = units.SystemScale
		global strOldSystemType = units.SystemType	
		
		i = 1
		testValStart = 0
		while (testValStart == 0) do (
			tmpVert = getVert obj i
			if (tmpVert[1] != 0) then testValStart = tmpVert[1]
			else if (tmpVert[2] != 0) then testValStart = tmpVert[2]
			else if (tmpVert[3] != 0) then testValStart = tmpVert[3]
			i = i + 1
		)
		
		testValFormatted = units.formatValue testValStart
		scalarVal = 1
		if (units.displayType == #US) then (
			units.SystemScale = 1.0
			units.SystemType = #Inches
			
			if (units.USType == #Frac_Ft OR 
				units.USType == #Dec_Ft OR 
				units.USType == #Ft_Frac_In OR 
				units.USType == #Ft_Dec_In) then
					scalarVal = 0.083333 --  (1 / 12)
				
		) else if (units.displayType == #Metric) then (
			units.SystemScale = 1.0
			units.SystemType = #Meters
			
			if (units.MetricType == #Millimeters) then (scalarVal = 0.001)
			if (units.MetricType == #Centimeters) then (scalarVal = 0.01)
			if (units.MetricType == #Meters) then (scalarVal = 1.0)
			if (units.MetricType == #Kilometers) then (scalarVal = 1000)
		
		) else if (units.displayType == #Custom) then (
			units.SystemScale = 1.0
			units.SystemType = units.CustomUnit
			
			scalarVal = (1 / units.CustomValue)
		) 
		
		testValDecoded = (units.decodeValue testValFormatted) * scalarVal
		sizeConversion = testValDecoded / testValStart

		SetPivot obj "origin"
		obj.scale = obj.scale * sizeConversion
		
		units.SystemScale = strOldSystemScale	-- revert back to old system scale
		units.SystemType = strOldSystemType	

	)
)


------------------------------------------------------------------------------------------------
-- ExportObjFile ----------------------------------------------------------------------------

fn ExportObjFile thisMesh filePrefix = (
	
	if (thisMesh != undefined) then (
		cObject = thisMesh
	) else GetcObject()
	
	if (cObject != undefined) then (
		if (filePrefix == undefined) then (
			strFilename = getSaveFileName "Export OBJ" types:"Wavefront Object (*.obj)|*.obj|All Files (*.*)|*.*"
			LastFilename = (strFilename as string)
		) else (
			LastFilename = filePrefix
		)
		arrSelection = (selection as array)
		global isGrouped = false
		if (isGroupMember cObject == true) then (
			isGrouped = true
			for obj in selection where (isGroupHead obj == true) do (setGroupOpen obj true)
		) else isGrouped = false
		
		with redraw off (
			cMesh = snapshot cObject
			select cMesh
					
			if (stm.cbCenterOrigin.checked == true AND filePrefix != undefined) do (cMesh.pos = [0,0,0])
			
			if (LastFilename != undefined) then
				exportFile (LastFilename) #noPrompt selectedOnly:true
			
			if (isGrouped == true) then for g in arrSelection where (isGroupHead g == true) do (setGroupOpen g false)
			delete cMesh
		)
	)
)


-----------------------------------------------------------------------------------------------
-- Check Scale ------------------------------------------------------------------------------

fn CheckScale obj = (
	iCheckScale = obj.transform.determinantsign
	if iCheckScale == 1 then
	(
		ConvertToPoly obj
		ResetXForm obj
		ConvertToPoly obj
	)
	else if iCheckScale == -1 then
	(
		ConvertToPoly obj
		ResetXForm obj
		addModifier obj(normalModifier flip:true)
		ConvertToPoly obj
	)
)


------------------------------------------------------------------------------------------------
-- WriteVertex ------------------------------------------------------------------------------

fn WriteVertex cObject cMesh iFaceIndex iVertIndex pOutputFile iChannelOne iChannelTwo hasVertexColor matRotate useLegacy = (	
	
	aOut = #()
	cFace = getFace cMesh iFaceIndex
	pOut = getVert cMesh (cFace[iVertIndex] as integer)
	for i = 1 to 3 do if (mod pOut[i] 1 == 0.0) then aOut[i] = int(pOut[i]) as string else aOut[i] = pOut[i]
	format "% % % " aOut[1] aOut[2] aOut[3] to:pOutputFile 

	if cObject.modifiers["Project Normals"] != undefined then
			MeshEditNormals = cObject.modifiers["Project Normals"]
	else	MeshEditNormals = cObject.Edit_Normals
	
	iNormalID = MeshEditNormals.GetNormalID iFaceIndex iVertIndex
	pOut = MeshEditNormals.getNormal iNormalID	
	pOut = pOut * matRotate
	for i = 1 to 3 do if (mod pOut[i] 1 == 0.0) then aOut[i] = int(pOut[i]) as string else aOut[i] = pOut[i]
	format "% % % " aOut[1] aOut[2] aOut[3] to:pOutputFile
	
 	cTFace = meshop.getMapFace cMesh iChannelOne iFaceIndex 
	pOut = meshop.getMapVert cMesh iChannelOne (cTFace[iVertIndex] as integer)
	for i = 1 to 2 do if (mod pOut[i] 1 == 0.0) then aOut[i] = int(pOut[i]) as string else aOut[i] = pOut[i]
	format "% % " aOut[1] aOut[2] to:pOutputFile
	
	-- add extra options to 6.0 STM format
	if (useLegacy == 0) then (
		cTFace = meshop.getMapFace cMesh iChannelTwo iFaceIndex 
		pOut = meshop.getMapVert cMesh iChannelTwo (cTFace[iVertIndex] as integer)
		for i = 1 to 2 do if (mod pOut[i] 1 == 0.0) then aOut[i] = int(pOut[i]) as string else aOut[i] = pOut[i]
		format "% % " aOut[1] aOut[2] to:pOutputFile
		
		if (hasVertexColor == true) then (
			cFace = getVCFace cMesh iFaceIndex
			pOut = (getVertColor cMesh (cFace[iVertIndex] as integer) as point3) / 255
			for i = 1 to 3 do if (mod pOut[i] 1 == 0.0) then aOut[i] = int(pOut[i]) as string else aOut[i] = pOut[i]
		) else (	-- no vertex colors set so force white
			pOut = [1,1,1]
			aOut = #("1","1","1")
		)
		format"% % %\n" aOut[1] aOut[2] aOut[3] to:pOutputFile
	) else (
		format"\n" to:pOutputFile
	)
)


------------------------------------------------------------------------------------------------
-- ExportSTMFile ---------------------------------------------------------------------------

fn ExportSTMFile thisMesh filePrefix useLegacy = (
	if (thisMesh != undefined) then (
		cObject = thisMesh
	) else (
		GetcObject()
	)

	if (cObject != undefined) then (
		
		if (filePrefix == undefined) then (
			strFilename = getSaveFileName "Export STM" types:"SpeedTree Mesh (*.stm)|*.stm|All Files (*.*)|*.*"
			LastFilename = (strFilename as string)
		) else (
			LastFilename = filePrefix
		)
		
		-- Define variables
		pOutputFile = openFile LastFilename
		if pOutputFile != undefined then
			close pOutputFile
			deleteFile LastFilename
		pOutputFile = createFile LastFilename
		iChannel = 0
		hasEditMesh = false
		hasEditNormals = false		
			
		global isGrouped = false
		if (isGroupMember cObject == true) then (
			isGrouped = true
			for obj in selection where (isGroupHead obj == true) do (setGroupOpen obj true)
		) else isGrouped = false
		
		with redraw off (
			max modify mode
			select cObject	
			
			if (classof cObject.baseObject != Editable_Mesh AND cObject.modifiers[#edit_mesh] == undefined AND cObject.modifiers["Projection Mesh"] == undefined) then (
				addModifier cObject(Edit_Mesh()) before:100
				hasEditMesh = true
			)
			
			if (cObject.modifiers[#edit_normals] == undefined AND cObject.modifiers["Project Normals"] == undefined) then (
				addModifier cObject(Edit_Normals())
				SubObjectLevel = 0
				hasEditNormals = true
			) else (
				if (classOf cObject.modifiers[1] != Edit_Normals) then (
					addModifier cObject(Edit_Normals())
					SubObjectLevel = 0
					hasEditNormals = true
				)
			)
			
			global cSnapObject = snapshot cObject
			global cMesh = getNodeByName(cSnapObject.name)
			matRotate = cMesh.transform.rotationpart as matrix3
			
			if (stm.cbCenterOrigin.checked == true AND filePrefix != undefined) do (cMesh.pos = [0,0,0])
			
			-- map channels
			iMapChannels = (meshop.getNumMaps cMesh) - 1
			arrMapChannels = #()
			while (arrMapChannels.count < iMapChannels AND iChannel < 99) do (
				iChannel = iChannel + 1
				if (meshop.getMapSupport cMesh iChannel) then
					append arrMapChannels iChannel
			)
			iMapChannels = arrMapChannels.count 
			if (iMapChannels > 0) then (
				if iMapChannels < 2 then
					arrMapChannels[2] = arrMapChannels[1]
			
				-- vertex colors
				iNumCPVVerts = getNumCPVVerts cMesh
				defaultVCFaces cMesh
				hasVertexColor = true
				if (iNumCPVVerts == 0) then	-- doesn't have any vertex colors... force to white
					hasVertexColor = false
				
				format "%\n" cMesh.numFaces to:pOutputFile -- Write mesh file 
				fCount = cMesh.numFaces
				for iFace = 1 to fCount do  (
					WriteVertex cObject cMesh iFace 1 pOutputFile arrMapChannels[1] arrMapChannels[2] hasVertexColor matRotate useLegacy
					WriteVertex cObject cMesh iFace 2 pOutputFile arrMapChannels[1] arrMapChannels[2] hasVertexColor matRotate useLegacy
					WriteVertex cObject cMesh iFace 3 pOutputFile arrMapChannels[1] arrMapChannels[2] hasVertexColor matRotate useLegacy
				)
				
				delete cSnapObject
				close pOutputFile
				
			) else (
				AbortScript "No mapping coordinates found"	
				delete cSnapObject
				close pOutputFile
				pOutputFile = pOutputFile as string
				pOutputFile = (filterString pOutputFile "<>")[1]
				pOutputFile = replace pOutputFile 1 5 ""
				deleteFile pOutputFile			
			)
			if hasEditNormals == true do deleteModifier cObject 1
			if hasEditMesh == true do deleteModifier cObject cObject.modifiers[#edit_mesh]
			if (isGrouped == true) then for g in arrSelection where (isGroupHead g == true) do (setGroupOpen g false)
		)
	)
	else 	messageBox message title:"Please select a mesh object." beep:false
	
)


------------------------------------------------------------------------------------------------
-- ExportByMaterial ------------------------------------------------------------------------

fn ExportByMaterial = (
	cObjects = #()
	oldSelection = selection as array
	if (oldSelection.count > 0) then (
		for s in oldSelection do (
			sClass = classOf s		
			sSuperClass = SuperClassOf s
			if (sSuperClass == GeometryClass AND s.modifiers["Hair and Fur"] == undefined AND sClass != SpeedTree_4 AND sClass != SpeedTree AND sClass != mr_Proxy AND sClass != BoneGeometry AND sClass != Dummy) then (
				join cObjects #(s)
			)
		)
	)
	
	if cObjects.count >= 1 then (
		
		if cObjects.count == 1 then exportObjectName = cObjects[1].name
		else exportObjectName = substring maxfilename 1 ((maxfilename as string).count - 4)
		
		if (stm.ddModelFormat.selected == ".stm") then (
			strFilePrefix = getSaveFileName "Export STM Group By Material" types:"SpeedTree Mesh (*.stm)|*.stm|All Files (*.*)|*.*" filename:exportObjectName historyCategory:"SpeedTreeMeshFiles"
		) else (	-- OBJ
			strFilePrefix = getSaveFileName "Export OBJ Group By Material" types:"Wavefront Object (*.obj)|*.obj|All Files (*.*)|*.*" filename:exportObjectName historyCategory:"SpeedTreeMeshFiles"
		)
		
		if strFilePrefix != undefined then (
			cObjectNames = for n in cObjects collect n.name
			sort cObjectNames
			
			usedMats = #()
			usedMeshes = #()
			
			max modify mode
			with redraw off (
				for n = 1 to cObjectNames.count do (
					n = getNodeByName cObjectNames[n]
					if n != undefined then (
						o = snapshot n
						select o
						CheckScale o
						
						mat = o.material
						if mat != undefined AND SuperClassOf o == GeometryClass AND classOf o == Editable_Poly then (
							if classof mat == MultiMaterial then (
								usedIDs = #{}
								usedIDs.count = 99
								usedIdFaces = #()
									
								modPanel.setCurrentObject o ui:true
								polyop.CollapseDeadStructs o
								faceCount = polyop.getNumFaces o
								for f = 1 to faceCount do (
									thisID = polyop.getFaceMatID o f
									if (usedIDs[thisID] == false) then (
										usedIDs[thisID] = true
										usedIdFaces[thisID] = #{f}
									) else (
										if usedIdFaces[thisID] == undefined then
											usedIdFaces[thisID] = #{f}
										else append usedIdFaces[thisID] f
									)
								)
								
								uCount = usedIDs.count
								for u = 1 to uCount do (
									if usedIDs[u] == true then (
										m = 1
										bFoundMatch = false
										while bFoundMatch == false do (
											if usedMats[m] != undefined AND mat[u] != undefined AND mat[u] == usedMats[m] then (
												bFoundMatch = true
											) else (
												if m < usedMats.count then (
													m = m + 1
												) else (
													append usedMats mat[u]
													m = usedMats.count
													bFoundMatch = true											
												)
											)
										)
										
										tmpMeshPart = copy o
										select tmpMeshPart
										totalFaces = #{1..faceCount}
										otherFaces = totalFaces - usedIdFaces[u]
										polyop.deleteFaces tmpMeshPart otherFaces
										tmpMeshPart.material = undefined
										
										if (m <= usedMeshes.count) then (
											polyop.attach usedMeshes[m] tmpMeshPart --attachMat:#neither 
										) else (
											append usedMeshes tmpMeshPart
										)
									)
								)
								
								if (o != undefined) then delete o
								
							) else (
								m = 1
								mCount = usedMats.count
								bFoundMatch = false
								while bFoundMatch == false do (
									if mat == usedMats[m] then (
										bFoundMatch = true
									) else (
										if m < usedMats.count then (
											m = m + 1
										) else (
											append usedMats mat
											m = usedMats.count
											bFoundMatch = true
										)	
									)
								)
								
								modPanel.setCurrentObject o ui:true
								o.material = undefined
								
								if (m <= usedMeshes.count) then (
									polyop.attach usedMeshes[m] o --attachMat:#neither 
								) else (
									append usedMeshes o
								)
							)
						)
					)
				)
				
				exportMulti = multimaterial()
				exportMulti.count = usedMats.count
				exportMulti.materialList = usedMats
				
				iCount = usedMeshes.count
				for i = 1 to iCount do (					
					if (iCount > 1) then (
						tmpPath = getFilenamePath strFilePrefix
						tmpFilename = getFilenameFile strFilePrefix
						tmpFileType = getFilenameType strFilePrefix
						strIncrementedFilename = tmpPath + tmpFilename + "_" + (i as string) + tmpFileType
					) else strIncrementedFilename = strFilePrefix
					
					if (stm.ddModelFormat.selected == ".stm") then (
						ExportSTMFile usedMeshes[1] strIncrementedFilename
					) else (	-- OBJ
						ExportOBJFile usedMeshes[1] strIncrementedFilename
					)
					
					delete usedMeshes[1]
					deleteItem usedMeshes 1
				)
				strCount = (iCount as string) + " meshes exported by material."
				print strCount
			)
		)
		gc()
	)
	select oldSelection
)


------------------------------------------------------------------------------------------------
-- ImportSTMFile ---------------------------------------------------------------------------

fn ImportSTMFile = (
	vert_array = #()
	face_array = #()
	normal_array = #()
	tex_array_one = #()
	tex_array_two = #()
	color_array = #()
	bHandleExtraData = false

	stmFilename = getOpenFileName "Import STM" types:"SpeedTree Mesh (*.stm)|*.stm|All Files (*.*)|*.*"
	if stmFilename != undefined then (
		start = timeStamp()
		
		stmFile = openFile stmFilename
		if stmFile != undefined then (	
			-- First check for "extra data" including multiple texcoords and vertex colors
			seek stmFile 0
			num_faces = readValue stmFile
			num_verts = (num_faces * 3)
			
			versionCheck = readLine stmFile
			arrVersionCheck = filterString versionCheck " "
			if (arrVersionCheck.count > 8) then bHandleExtraData = true
			
			stm_name = getFilenameFile stmFilename
			if (getNodeByName stm_name != undefined) then
				stm_name = uniqueName stm_name
			
			seek stmFile 0
			readValue stmFile
			
			if stm.cbWeldAll.checked == true then (
				-- predefine the first triangle as used and store vertices
				arrWeldedToVerts = #{1..3}
				arrDupeVerts = #{}
				
				faceVert = 1
				faceCopy = #{1..3} as array
				for v = 1 to num_verts do (
					faceCopy[faceVert] = v
					
					vert_array[v] = (point3 (readValue stmFile) (readValue stmFile) (readValue stmFile))
					normal_x = float(int((readValue stmFile) * 100)) / 100
					normal_y = float(int((readValue stmFile) * 100)) / 100
					normal_z = float(int((readValue stmFile) * 100)) / 100
					normal_array[v] = (point3 normal_x normal_y normal_z)
					tex_array_one[v] = (point3 (readValue stmFile) (readValue stmFile) 0)
						
					if bHandleExtraData then (
						tex_array_two[v] = (point3 (readValue stmFile) (readValue stmFile) 0)
						color_array[v] = (color ((readValue stmFile) * 255) ((readValue stmFile) * 255) ((readValue stmFile) * 255))
					)
					
					-- first three verts always pass
					if v > 3 then (
						s = 1
						bFoundMatch = false
						while s <= v AND bFoundMatch == false do (
							if (arrDupeVerts[s] != true AND (vert_array[v] == vert_array[s]) AND (normal_array[v] == normal_array[s]) AND (tex_array_one[v] == tex_array_one[s])) then (
								bFoundMatch = true
								faceCopy[faceVert] = s
								arrWeldedToVerts[s] = true
								if arrWeldedToVerts[v] != true then
									arrDupeVerts[v] = true
							) else (
								s = s + 1
							)
						)
					)
					
					if faceVert == 3 then (
						append face_array (point3 faceCopy[1] faceCopy[2] faceCopy[3])
						faceVert = 1
					) else 
						faceVert = faceVert + 1
				)
				
			) else (
				for v = 1 to num_verts do (
					vert_array[v] = (point3 (readValue stmFile) (readValue stmFile) (readValue stmFile))
					normal_array[v] = (point3 (readValue stmFile) (readValue stmFile) (readValue stmFile))
					tex_array_one[v] = (point3 (readValue stmFile) (readValue stmFile) 0)
						
					if bHandleExtraData then (
						tex_array_two[v] = (point3 (readValue stmFile) (readValue stmFile) 0)
						color_array[v] = (color ((readValue stmFile) * 255) ((readValue stmFile) * 255) ((readValue stmFile) * 255))
					)
				)
				
				vert = 1
				for f = 1 to num_faces do (
					vert_x = vert
					vert = vert + 1
					vert_y = vert
					vert = vert + 1
					vert_z = vert
					vert = vert + 1
					append face_array (point3 vert_x vert_y vert_z)
				)
			)
			
			close stmFile
			stm_mesh = mesh vertices:vert_array tverts:tex_array_one faces:face_array
			stm_mesh.name = stm_name
			stm_mesh.wirecolor = (color 128 128 128)
			
			maxToolMode = toolmode.commandmode
			max modify mode
			buildTVFaces stm_mesh.mesh
			iCount = stm_mesh.mesh.numfaces
			for i = 1 to iCount do (
				setTVFace stm_mesh.mesh i (getFace stm_mesh.mesh i)
				setFaceSmoothGroup stm_mesh i 1
			)
			
			meshop.setNumMaps stm_mesh 3 keep:true	
			numTVerts = meshop.getNumMapVerts stm_mesh 2
			
			for v = 1 to numTVerts do (
				if bHandleExtraData then (
					meshop.setMapVert stm_mesh 2 v tex_array_two[v]
					setVertColor stm_mesh v color_array[v]
				) else (
					meshop.setMapVert stm_mesh 2 v tex_array_one[v]
					setVertColor stm_mesh v (color 255 255 255)
				)
			)
			
			prevSelection = (selection as array)
			select stm_mesh
			ResetXForm stm_mesh
			ConvertToMesh stm_mesh
			
			addModifier stm_mesh(Edit_Normals())
			num = stm_mesh.Edit_Normals.GetNumNormals()
			stm_mesh.Edit_Normals.SetSelection #{1..num}
				
			j = 1
			for i = 1 to num do (
				if (stm.cbWeldAll.checked == true) then (
					while (arrWeldedToVerts[j] == false AND j <= arrWeldedToVerts.count) do
						j = j + 1
				) else j = i
				
			--	setNormal stm_mesh i normal_array[i]
				stm_mesh.Edit_Normals.SetNormalExplicit i explicit:true
				stm_mesh.Edit_Normals.setNormal i normal_array[j]
				j = j + 1
			)
			
			stm_mesh.Edit_Normals.displayLength = 1
			stm_mesh.Edit_Normals.SetSelection #{}
			stm_mesh.Edit_Normals.SelLevel = 0
			ConvertToMesh stm_mesh
			
			if stm.cbWeldAll.checked == true then (
				meshop.deleteVerts stm_mesh arrDupeVerts
				
			-- )	
			-- if stm.cbWeldTexCoords.checked == true then (
				
				-- weld texture verts
				addModifier stm_mesh(unwrap_UVW())
				stm_mesh.Unwrap_UVW.setTVSubObjectMode 1
				stm_mesh.Unwrap_UVW.setSelectedGeomVerts #{1..num_verts}
				stm_mesh.Unwrap_UVW.edit()
				max select all
				stm_mesh.Unwrap_UVW.setWeldThreshold 0.0001
				stm_mesh.Unwrap_UVW.weldSelected()
							
-- 				addModifier stm_mesh(unwrap_UVW())
-- 				stm_mesh.Unwrap_UVW.setMapChannel 2
-- 				stm_mesh.Unwrap_UVW.setTVSubObjectMode 1
-- 				stm_mesh.Unwrap_UVW.setSelectedGeomVerts #{1..num_verts}
-- 				stm_mesh.Unwrap_UVW.edit()
-- 				max select all
-- 				stm_mesh.Unwrap_UVW.setWeldThreshold 0.001
-- 				stm_mesh.Unwrap_UVW.weldSelected()
			)
			
			ConvertToMesh stm_mesh
			if stm.cbShowNormals.checked == true then (
				addModifier stm_mesh(Edit_Normals())
				stm_mesh.Edit_Normals.SelLevel = 0
			)
			
			if stm.cbShowVertexColors.checked == true then
				stm_mesh.showVertexColors = true
			
			if prevSelection.count > 0 then (select prevSelection)
			else max select none
			
			toolmode.commandmode = maxToolMode
		)
	)
	
	end = timeStamp()
	if start != undefined then (
		execTime = ((end - start) / 1000.0)
		--print execTime
	)
)


-------------------------------------------------------------------------------------------------
-- AbortScript --------------------------------------------------------------------------------

fn AbortScript message = (
	units.SystemScale = strOldSystemScale	-- revert back to old system scale
	units.SystemType = strOldSystemType
	
	select arrSelection -- Reset original selection and close groups
	if (isGrouped == true) do for obj in selection where (isGroupHead obj == true) do (setGroupOpen obj false)
	
	messageBox message title:"Mesh Export Error" beep:false	
	enableSceneRedraw()
)


------------------------------------------------------------------------------------------------
-- Convert Scene Units ----------------------------------------------------------------------

fn ConvertSceneUnits = (
	
	strFrom = stmUnits.ddConvertFrom.selected
	case of (
		(strFrom == "millimeters") : valFrom = 0.001
		(strFrom == "centimeters"): valFrom = 0.01
		(strFrom == "meters"): valFrom = 1.0
		(strFrom == "kilometers") : valFrom = 1000
		(strFrom == "inches"): valFrom = 0.0254
		(strFrom == "feet"): valFrom = 0.3048
		(strFrom == "miles"): valFrom = 1609.344
		default: valFrom = 1.0
	)
	
	if (stmUnits.ddConvertTo.selected == "scene units") then strTo = units.SystemType as string
	else strTo = stmUnits.ddConvertTo.selected
	case of (
		(strTo == "millimeters") : valTo = 0.001
		(strTo == "centimeters"): valTo = 0.01
		(strTo == "meters"): valTo = 1.0
		(strTo == "kilometers") : valTo = 1000
		(strTo == "inches"): valTo = 0.0254
		(strTo == "feet"): valTo = 0.3048
		(strTo == "miles"): valTo = 1609.344
		default: valTo = 1.0
	)
	if (stmUnits.ddConvertTo.selected == "Scene units") then valTo = valTo * units.SystemScale
	
	fConversionScalar =  valTo / valFrom
	stmUnits.lblConversionRatio.text = "Scale -> " + substring((ValFrom / valTo) as string) 1 7
)


fn DestroyRollouts = (
	setCommandPanelTaskMode mode:#utility
	removeRollout stmTools
	removeRollout stmForest
	removeRollout stmUnits
	
	if (stm.inDialog == false AND stmTools.inDialog == false AND stmForest.inDialog == false  AND stmUnits.inDialog == false) then
		stmRemoveScripts()
	
	if (stFbxTools != undefined AND stFbxTools.open == false) do (
		stFbxTools.open = true
		removeRollout stFbxTools
	)
	
	if (stDispCalc != undefined) do removeRollout stDispCalc
	if (stFbxTools != undefined AND stFbxTools.inDialog) do DestroyDialog stFbxTools		
	if (stDispCalc != undefined AND stDispCalc.inDialog) do DestroyDialog stDispCalc
)


fn CreateRollouts = (
	DestroyRollouts()
	addRollout stm
	addRollout stmTools
	addRollout stmForest
	addRollout stmUnits
	stmTools.open = false	
	stmForest.open = false	
	stmUnits.open = false		
	stmCallbacks()
	ConvertSceneUnits()
	UpdateList()
)


------------------------------------------------------------------------------------------------
-- SpeedTree Mesh Utility ------------------------------------------------------------------

utility stm "SpeedTree Mesh Utilities" (
	
	group "STM/OBJ Mesh Export" (
		label lblObjName "- No mesh selected -"
		label lblObjFaces "0 triangles" offset:[0,-3] enabled:false
		label lblObjDimensions "(0, 0, 0)" offset:[0,-3] enabled:false
		checkBox cbCenterOrigin "Override offset" offset:[0,5] checked:(iniCenterOrigin as BooleanClass)
		label lblModelFormat "Model format:" offset:[0,3] align:#left
		dropDownList ddModelFormat width:62 height:20 items:#(".stm", ".stm legacy", ".obj") selection:(iniStmFormat as integer) offset:[2,-22] align:#right		
		button btnExportMesh "Export Mesh" width:140 height:26 offset:[0,2] enabled:false
		label lblLine1 "__Export By Material_________" offset:[-9,5] align:#left	
		label lblExportByMaterial "Use this option to export one\nmesh per material in selection." height:25 enabled:true offset:[-4,-2] align:#left
		button btnExportByMaterial "Export Selected By Material" width:140 height:26 offset:[5,5] enabled:false
	)
	
	group "STM Mesh Import" (
		label lblMeshImport "NOTE: This importer is not for\nimporting whole trees (use\nthe FBX Processor instead)." height:38 enabled:true offset:[-2,0] align:#left
		checkBox cbWeldAll "Weld mesh (slower)" offset:[0,5] checked:(iniWeldAll as BooleanClass) 
		--checkBox cbWeldTexCoords "Weld texture verts" offset:[0,-4] checked:(iniWeldTexCoords as BooleanClass) 
		checkBox cbShowNormals "Show normals" checked:(iniShowNormals as BooleanClass) offset:[0,-4]
		checkBox cbShowVertexColors "Show vertex colors" offset:[0,-4] checked:(iniShowVertexColors as BooleanClass)
		button btnImportMesh "Import Mesh (.stm)" width:140 height:26 offset:[0,3]
	)
	
	button btnCreateFloater "" width:15 height:15 pos:[143,13] enabled:true
	
	-- set initial states
	on cbCenterOrigin changed optionState do setINISetting mx_ini "IDV" "stm_origin" (optionState as string)
	on ddModelFormat selected selection do setINISetting mx_ini "IDV" "stm_format" (ddModelFormat.selection as string)
	
	on btnExportMesh pressed do (
		if (selection.count > 0) then (
			arrSelection = (selection as array)
			GetcObject()
			if (cObject != undefined) then (
				exportObjectName = cObject.name
				o = snapshot cObject
				select o
				CheckScale o
				
				if (stm.ddModelFormat.selected == ".stm") then (
					strFilename = getSaveFileName "Export STM" types:"SpeedTree Mesh (*.stm)|*.stm|All Files (*.*)|*.*" filename:exportObjectName historyCategory:"SpeedTreeMeshFiles"
					if (strFilename != undefined) then (
						global LastFilename = (strFilename as string)
						ExportSTMFile o strFilename 0	-- zero is for "not legacy"
					)
				) else if (stm.ddModelFormat.selected == ".stm legacy") then (
					strFilename = getSaveFileName "Export STM" types:"SpeedTree Mesh (*.stm)|*.stm|All Files (*.*)|*.*" filename:exportObjectName historyCategory:"SpeedTreeMeshFiles"
					if (strFilename != undefined) then (
						global LastFilename = (strFilename as string)
						ExportSTMFile o strFilename 1	-- one is for "legacy"
					)
				) else (	-- OBJ
					strFilename = getSaveFileName "Export OBJ" types:"Wavefront Object (*.obj)|*.obj|All Files (*.*)|*.*" filename:exportObjectName historyCategory:"SpeedTreeMeshFiles"
					if (strFilename != undefined) then (
						global LastFilename = (strFilename as string)
						ExportOBJFile o strFilename
					)
				)
				delete o
			)
			
			select arrSelection -- Reset original selection and close groups			
				
			EnableSceneRedraw()
			if (stm.inDialog == false) then
				setCommandPanelTaskMode mode:#utility
			
		) else (
			messageBox "Please select an object to export." title:"Mesh Export Error" beep:false
		)
	)
	
	on btnExportByMaterial pressed do (
		ExportByMaterial()
	)
	
	on cbWeldAll changed optionState do (
		setINISetting mx_ini "IDV" "stm_weldall" (optionState as string)
	)
	on cbWeldTexCoords changed optionState do setINISetting mx_ini "IDV" "stm_weldtexcoords" (optionState as string)
	on cbShowNormals changed optionState do setINISetting mx_ini "IDV" "stm_shownormals" (optionState as string)
	on cbShowVertexColors changed optionState do setINISetting mx_ini "IDV" "stm_showvertcolors" (optionState as string)
	on btnImportMesh pressed do (
		ImportSTMFile()
	)
	
	on btnCreateFloater pressed do (
		CreateFloat stm 435
		CreateRollouts()
	)
	
	on stm open do DestroyRollouts()
	on stm close do DestroyRollouts()
)


------------------------------------------------------------------------------------------------
-- Initialize Rollouts ------------------------------------------------------------------------

if (stm != undefined) do removeRollout stm
CreateRollouts()

stm.btnCreateFloater.images = #("bip_pivseldlg_i.bmp",undefined,2,1,1,2,2,true)
stmTools.btnCreateFloater.images = #("bip_pivseldlg_i.bmp",undefined,2,1,1,2,2,true)
stmUnits.btnCreateFloater.images = #("bip_pivseldlg_i.bmp",undefined,2,1,1,2,2,true)
stmForest.btnCreateFloater.images = #("bip_pivseldlg_i.bmp",undefined,2,1,1,2,2,true)

macroScript QuickSaveSTM category:"SpeedTree" ( ExportSTMFile() )