--//-----------------------------------------------------------------------------
--// PlaceTools.ms
--// By Grant Miller (blented@gmail.com)
--// v 1.0
--// Created On: 03/11/09
--// Modified On: 03/11/09
--// tested using Max 2009
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Required Files:
--// ieMax.ms
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Description:
--// Used to place objects on surfaces in 3dsMax
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Revision History:
--//
--// v 1.00 Initial version
--//
--//-----------------------------------------------------------------------------



--//dum = $Dummy002
--//for o in getCurrentSelection() do
--//(
--//	dist = o.pos - dum.pos-- [d.pos.x - o.pos.x,d.pos.y - o.pos.y,d.pos.z-o.pos.z]
--//	dist = normalize dist
--// 	upVec = [0,0,1]
--//	dp = dot dist upVec
--//	t = acos dp
--//	c = cross upVec dist
--//	c = normalize c
--//	o.dir = c
--//	in coordsys local rotate o (eulerangles -90 0 0)
--//)



--//-----------------------------------------------------------------------------
(
--// Includes
--//-----------------------------------------------------------------------------
fileIn (MAX_TOOLS_ROOT + "lib/ieMax.ms")

--// Generic Globals
--//-----------------------------------------------------------------------------
global posControls
global rotControls
global scaleControls
global proxyControls
global proxyDefaults
global curObj
global objUtilitiesFloater
global objUtilitiesRoll
global objToolsRoll
global availableObjs
global totalObjFreq

--// Place Globals
--//-----------------------------------------------------------------------------
global surfaceMesh
global currentObj
global objDist
global targetObj

--// Generic Variables
--//-----------------------------------------------------------------------------
objData = "PlaceToolsObjData"
placeData = "PlaceToolsData"
proxyData = "ProxyToolsData"
localHit = [0,0,0]
localNormal = [0,0,0]
worldHit = [0,0,0]
worldNormal = [0,0,0]
radius = 0
str = 0
shiftPressed = false
altPressed = false
ctrlPressed = false
paintPressure = 0
bPlacingObj = false
minObjSpacing = 1
objList = #()
defaultFrequency = 1
currentLayerNumber = 1

--// General Functions
--//-----------------------------------------------------------------------------
fn instanceObj objName inst =
(
	instObj = getNodeByName objName
	if (inst) then
		newObj = instance instObj
	else
		newObj = copy instObj

	setUserPropBuffer newObj (getUserPropBuffer instObj)
	return newObj
)
fn buildObjList &objArray =
(
	objArray = #()
	for p in availableObjs do
	(
		objNode = getNodeByName p
		if (objNode != undefined) then
			append objArray p
	)
)
fn calcTotalFreq objList=
(
	totalObjFreq = 0
	for p in objList do
	(
		freq = ieMaxGetProp p "Frequency"
		if (freq != undefined) then totalObjFreq += freq
	)
	return totalObjFreq
)
fn getRandomObj objList =
(
	totalObjFreq = calcTotalFreq objList
	objRand = random 0.0 totalObjFreq
	testFreq = 0.0
	for p in objList do
	(
		objFreq = (ieMaxGetProp p "Frequency")
		if (objFreq != undefined) then testFreq += objFreq
		if (testFreq >= objRand) then return p
	)
)
fn getObjRotation objName =
(
	rndArray = #()
	rotProps = #("RotXMin", "RotXMax", "RotYMin", "RotYMax", "RotZMin", "RotZMax")
	for p = 1 to rotProps.count by 2 do
	(
		rotMin = (ieMaxGetProp objName rotProps[p])
		rotMax = (ieMaxGetProp objName rotProps[p+1])
		append rndArray (random rotMin rotMax)
	)
	return (point3 rndArray[1] rndArray[2] rndArray[3])
)
fn getObjScale objName =
(
	rndArray = #()
	rndScale = [0,0,0]
	scaleProps = #("ScaleXMin", "ScaleXMax", "ScaleYMin", "ScaleYMax", "ScaleZMin", "ScaleZMax")
	for p = 1 to scaleProps.count by 2 do
	(
		scaleMin = 100 + (ieMaxGetProp objName scaleProps[p])
		scaleMax = 100 + (ieMaxGetProp objName scaleProps[p+1])
		append rndArray (random scaleMin scaleMax)
	)
	rndScale.x = rndArray[1] * 0.01
	rndScale.y = rndArray[2] * 0.01
	rndScale.z = rndArray[3] * 0.01
	return rndScale
)
fn getRandomObjIndex objList =
(
	totalObjFreq = calcTotalFreq objList
	objRand = random 0.0 totalObjFreq
	testFreq = 0.0
	for p = 1 to objList.count do
	(
		objFreq = (ieMaxGetProp objList[p] "Frequency")
		if (objFreq != undefined) then testFreq += objFreq
		if (testFreq >= objRand) then return p
	)
)
fn remPrefix controlName =
(
--//  start at the fourth digit to remove the "spn" and "btn" prefixes
	return substring controlName 4 controlName.count
)
fn pointOffset ang len =
(
	newPt = [0,0,0]
	newPt.x = -len * (sin ang)
	newPt.y = len * (cos ang)
	return newPt
)
fn localRotate rotObj rotValue =
(
	coordsys local
	(
		rotate rotObj (angleaxis rotValue.z [0,0,1])
		rotate rotObj (angleaxis rotValue.x [1,0,0])
		rotate rotObj (angleaxis rotValue.y [0,1,0])
	)
)
fn initProxy proxyObj =
(
	isVRayProxy = (classOf proxyObj == VRayProxy)
	isMRProxy = (classOf proxyObj == mr_Proxy)
	if (not (isVRayProxy or isMRProxy)) then
		return false
	proxyName = proxyObj.name
	repMin = (getUserProp proxyObj "ReplaySpeedMin")
	repMax = (getUserProp proxyObj "ReplaySpeedMax")

	if (isVRayProxy) then
		proxyObj.anim_speed = (random repMin repMax)
	else
		proxyObj.AnimSpeed = (random repMin repMax)

	frameMin = (getUserProp proxyObj "FrameRangeMin")
	frameMax = (getUserProp proxyObj "FrameRangeMax")

	if (isVRayProxy) then
		proxyObj.anim_offset = int(random frameMin frameMax)
	else
		proxyObj.AnimOffset = int(random frameMin frameMax)

	pingPong = (getUserProp proxyObj "PingPongFrequency")
	if ((random 0 100) <= pingPong) then
	(
		if (isVRayProxy) then
			proxyObj.anim_type = 2
		else
			proxyObj.AnimPingPong = true
	)
)
fn makeNewObj objPos =
(
	objName = getRandomObj objList
	currentObj = instanceObj objName (objToolsRoll.chkInstanceObjs.state)

	currentObj.pos = objPos
	in coordSys local currentObj.scale = getObjScale objName
	localRotate currentObj (getObjRotation objName)
	initProxy currentObj
)
fn replaceObj obj =
(
	objName = getRandomObj objList
	currentObj = instanceObj objName (objToolsRoll.chkInstanceObjs.state)
--//  currentObj.transform = obj.transform
	currentObj.position = obj.position
	in coordSys local currentObj.scale = getObjScale objName
	localRotate currentObj (getObjRotation objName)
	initProxy currentObj
)
fn placeObj tMatrix obj:undefined =
(
	objName = getRandomObj objList
	currentObj = instanceObj objName (objToolsRoll.chkInstanceObjs.state)
	currentObj.transform = tMatrix
--//  currentObj.position = obj.position
	in coordSys local currentObj.scale = getObjScale objName
	localRotate currentObj (getObjRotation objName)
	initProxy currentObj
	if obj != undefined then
		currentObj.parent = obj
)
fn calcSurfacePos objPos =
(
	testRay = ray objPos [0,0,-1]
	testRay.pos.z = surfaceMesh.max.z + 1
	postHit = intersectRay surfaceMesh testRay
	objPos.z = postHit.pos.z
	return objPos
)
fn setDefaultProps objNames =
(
	for o in objNames do
	(
		obj = getNodeByName o
		if (isValidNode obj) then
		(
			posControls = #("PosXMin", "PosXMax", "PosYMin", "PosYMax", "PosZMin", "PosZMax")
			rotControls = #("RotXMin", "RotXMax", "RotYMin", "RotYMax", "RotZMin", "RotZMax")
			scaleControls = #("ScaleXMin", "ScaleXMax", "ScaleYMin", "ScaleYMax", "ScaleZMin", "ScaleZMax")
			proxyControls = #("ReplaySpeedMin", "ReplaySpeedMax", "FrameRangeMin", "FrameRangeMax", "PingPongFrequency")
			proxyDefaults = #(.8,1.2,animationRange.start,animationRange.end,.2)

			setUserProp obj "Frequency" defaultFrequency
			for i in posControls do setUserProp obj i 0
			for i in rotControls do setUserProp obj i 0
			for i in scaleControls do setUserProp obj i 1
			for i = 1 to proxyControls.count do setUserProp obj proxyControls[i] proxyDefaults[i]
		)
	)
)
--// Painting Functions
--//-----------------------------------------------------------------------------
fn initPainting =
(

)
fn strokeStart =
(
	thePainterInterface.undoStart()
)

fn strokePaintObjs =
(
--//  when you stroke paint posts then place one at the postSpacing interval and just calc the piece in between (get this working first)
--//  if you click and the distance is greater than one slat can span posts should be filled in accordingly
	thePainterInterface.getHitPointData &localHit &localNormal &worldHit &worldNormal &radius &str 0

--//  if lastObjPos is undefined then this is the first post we've painted this session
--//  if auto-connect is on we'll want to go through the posts and get the closest one and use that for the edge
--//  if auto-connect is off (implemented first) then we'll just place a new post down as normal

	if (not isValidNode currentObj) then
	(
		makeNewObj worldHit
		objDist = 0
	)
	else
		objDist = distance worldHit currentObj.pos

--//  if we've drawn far enough to be able to place another post...
	if (objDist > minObjSpacing) then
	(
		makeNewObj worldHit
	)
)
fn strokeEnd =
(
--//  thePainterInterface.getHitPressureData &shiftPressed &ctrlPressed &altPressed &paintPressure 0
--//  if (not shiftPressed) then
--//  (
--//    lastPost = undefined
--//    currentObj = undefined
--//  )
	thePainterInterface.undoAccept()
)
fn paintingCancel =
(
	thePainterInterface.undoCancel()
)
fn paintingEnd =
(
	objToolsRoll.ckbPlaceObjs.checked = false
	thePainterInterface.endPaintSession()
)
fn checkObjList =
(
	if (objList.count > 0) then
		return true
	 else
		messageBox "Could not find any Objects to Place.  Please ensure that at least one Object exists in the Object List." title:"No Objects Found"
)
fn getCurrentLayerNumber =
(
	ln = ieMaxGetProp placeData "layerNumber"
	if (ln != undefined) then
		return ln
	return 1
)
--// Script
--//-----------------------------------------------------------------------------
--//obj stuff
--//-------------
--//controls for importing objs to place from a file
--//controls for selecting objs to place from a scene
--//per-obj scale, position, and rotation jitter settings, per-obj frequency, all should be saved/loaded to max file
--//save and load them from the object themselves, that way on merge etc the settings stick, and on delete they go away
--//label for what the obj is flagged as (post, slat, etc)
--//
--//fence stuff
--//-------------
--//define terrain mesh
--//tool for placing fence posts
--//display thing above the fence posts that are hand-placed
--//displays line between the object's bounding center and the next one in the linked chain of posts
--//on post remove node.children[all].parent = node.parent
--//option for realtime update toggle
--//link chain editing
--//-select n posts break link
--//-select 2 posts and go into insert mode, placing next posts between those two
--//-select 2 posts and link them together
--//-select n posts and auto-link (break all links, walk through and find closest for each post)
rollout proxyUtilitiesRoll "Proxy Utilities" width:448 height:168
(
	button btnConvertSelected "Convert Selected Objects to .vRayMesh" pos:[8,136] width:432 height:24
	label lblExportFolder "Export Directory:" pos:[24,8] width:88 height:16
	edittext edtExportFolder "" pos:[112,8] width:296 height:16
	button btnPickExportFolder "..." pos:[416,8] width:24 height:16
	checkbox chkExportAnimation "Export Animation" pos:[8,32] width:104 height:16 checked:true
	dropdownList ddlFrameRange "" pos:[112,32] width:232 height:21 items:#("Scene animation range", "Custom range")
	spinner spnStartFrame "" pos:[112,64] width:80 height:16 range:[-9999,9999,0] type:#integer scale:1
	label lbl102 "Start Frame:" pos:[48,64] width:64 height:16
	spinner spnEndFrame "" pos:[264,64] width:80 height:16 range:[-9999,9999,100] type:#integer scale:1
	label lbl103 "End Frame:" pos:[208,64] width:56 height:16
	checkbox chkExportMulti "Export each object" pos:[208,88] width:192 height:16 checked:true
	checkbox chkCreateProxies "Automatically create proxies" pos:[8,88] width:192 height:16 checked:true
	spinner spnPreviewFaces "" pos:[112,112] width:80 height:16 range:[0,10000,20] type:#integer scale:1
	label lbl104 "Preview faces:" pos:[40,112] width:72 height:16

	on proxyUtilitiesRoll open do
	(
		edtExportFolder.text = maxFilePath + "cache"
	)
	on proxyUtilitiesRoll rolledUp state do
	(
		if (state) then
			objUtilitiesFloater.size.y += proxyUtilitiesRoll.height
		else
			objUtilitiesFloater.size.y -= proxyUtilitiesRoll.height
	)
	on btnPickExportFolder pressed do
	(
		if (edtExportFolder.text != "") then
			saveDir = getSavePath caption:"Export Folder:" initialDir:edtExportFolder.text
		else
			saveDir = getExportFolder 0

		if (saveDir != undefined) then
		(
			edtExportFolder.text = saveDir
			ieMaxSetProp proxyData "exportFolder" saveDir
		)
	)
	on btnConvertSelected pressed do
	(
		if (not (isDirectoryWriteable edtExportFolder.text)) then
			makeDir edtExportFolder.text all:true
		if (isDirectoryWriteable edtExportFolder.text) then
		(
			objs = getCurrentSelection()
			instancedObjs = #()
			for o in objs do
			(
				x = instance o
				append instancedObjs x
			)
			select instancedObjs
			objNames = for o in instancedObjs collect (o.name)
			if (ddlFrameRange.selection == 1) then
				vrayMeshExport meshFile:(edtExportFolder.text + "\\") autoCreateProxies:chkCreateProxies.state exportMultiple:chkExportMulti.state animation:chkExportAnimation.state animationRange:#scene animationRedrawViews:false maxPreviewFaces:spnPreviewFaces.value
			else
				vrayMeshExport meshFile:(edtExportFolder.text + "\\") autoCreateProxies:chkCreateProxies.state exportMultiple:chkExportMulti.state animation:chkExportAnimation.state animationRange:#explicit animationStart:spnStartFrame.value animationEnd:spnEndFrame.value animationRedrawViews:false maxPreviewFaces:spnPreviewFaces.value
			proxyNames = #()
			for n in objNames do
			(
				originalObj = getNodeByName n
				append proxyNames ("VRayProxy_" + n)
				obj = getNodeByName ("VRayProxy_" + n)
				if (isValidNode obj) then
				(
					if (isValidNode originalObj) then
					(
						if (originalObj.material != undefined) then
							obj.material = originalObj.material
					)
					bbCenter = ieMaxCalcBBCenter obj
					obj.pivot = [bbCenter.x,bbCenter.y,obj.min.z]
				)
			)
			join objUtilitiesRoll.lbxObjList.items proxyNames
			makeUniqueArray objUtilitiesRoll.lbxObjList.items
			objUtilitiesRoll.lbxObjList.items = objUtilitiesRoll.lbxObjList.items
			availableObjs = objUtilitiesRoll.lbxObjList.items
			setDefaultProps proxyNames
		)
		else
			messageBox "Can't find or write to the specified directory" title:"Directory error"
	)
)
rollout objUtilitiesRoll "Obj Utilities" width:440 height:368
(
	GroupBox grp2 "Position Ranges:" pos:[208,48] width:224 height:72
	GroupBox grp3 "Rotation Ranges:" pos:[208,128] width:224 height:72
	GroupBox grp4 "Scale Ranges:" pos:[208,208] width:224 height:72
	GroupBox grp10 "Proxy Ranges:" pos:[208,288] width:224 height:72
	label lbl1 "Roll (X):" pos:[229,144] width:40 height:16
	label lbl2 "Pitch (Y):" pos:[223,160] width:48 height:16
	label lbl3 "Yaw (Z):" pos:[224,176] width:50 height:16
	label lbl4 "X:" pos:[256,224] width:13 height:16
	label lbl8 "Y:" pos:[256,80] width:18 height:16
	label lbl7 "Z:" pos:[256,96] width:16 height:16
	label lbl9 "X:" pos:[256,64] width:13 height:16
	label lbl26 "Y:" pos:[255,242] width:18 height:16
	label lbl25 "Z:" pos:[255,258] width:16 height:16
	label lbl10 "to" pos:[344,176] width:16 height:16
	label lbl11 "to" pos:[344,160] width:16 height:16
	label lbl12 "to" pos:[344,144] width:16 height:16
	label lbl13 "to" pos:[344,256] width:16 height:16
	label lbl14 "to" pos:[344,240] width:16 height:16
	label lbl15 "to" pos:[344,224] width:16 height:16
	label lbl16 "to" pos:[344,96] width:16 height:16
	label lbl17 "to" pos:[344,80] width:16 height:16
	label lbl18 "to" pos:[344,64] width:16 height:16
	label lbl19 "Frequency:" pos:[213,24] width:88 height:16
	label lbl67 "Rep Spd:" pos:[219,304] width:48 height:16
	label lbl66 "to" pos:[344,304] width:16 height:16
	label lbl69 "Frm Rng:" pos:[221,320] width:48 height:16
	label lbl68 "to" pos:[344,320] width:16 height:16
	label lbl70 "Ping-Pong Frequency:" pos:[248,338] width:112 height:16
--//  controls that do things
	listbox lbxObjList "Objects to Place:" pos:[8,8] width:192 height:21
	button btnAddSelected "Add Selected" pos:[8,312] width:96 height:24
	button btnRemoveObj "Remove" pos:[8,336] width:96 height:24
	button btnSetAll "Set All" pos:[104,312] width:96 height:24
	button btnClearObjs "Clear" pos:[104,336] width:96 height:24
	spinner spnFrequency "" pos:[272,24] width:64 height:16 range:[0,1000,1]
	spinner spnPosXMin "" pos:[272,64] width:64 height:16 range:[-999999,999999,0]
	spinner spnPosXMax "" pos:[360,64] width:64 height:16 range:[-999999,999999,0]
	spinner spnPosYMin "" pos:[272,80] width:64 height:16 range:[-999999,999999,0]
	spinner spnPosYMax "" pos:[360,80] width:64 height:16 range:[-999999,999999,0]
	spinner spnPosZMin "" pos:[272,96] width:64 height:16 range:[-999999,999999,0]
	spinner spnPosZMax "" pos:[360,96] width:64 height:16 range:[-999999,999999,0]
	spinner spnRotXMin "" pos:[272,144] width:64 height:16 range:[-180,180,0]
	spinner spnRotXMax "" pos:[360,144] width:64 height:16 range:[-180,180,0]
	spinner spnRotYMin "" pos:[272,160] width:64 height:16 range:[-180,180,0]
	spinner spnRotYMax "" pos:[360,160] width:64 height:16 range:[-180,180,0]
	spinner spnRotZMin "" pos:[272,176] width:64 height:16 range:[-180,180,0]
	spinner spnRotZMax "" pos:[360,176] width:64 height:16 range:[-180,180,0]
	spinner spnScaleXMin "" pos:[272,224] width:64 height:16 range:[-99999,99999,1]
	spinner spnScaleXMax "" pos:[360,224] width:64 height:16 range:[-99999,99999,1]
	spinner spnScaleYMin "" pos:[272,240] width:64 height:16 range:[-99999,99999,1]
	spinner spnScaleYMax "" pos:[360,240] width:64 height:16 range:[-99999,99999,1]
	spinner spnScaleZMin "" pos:[272,256] width:64 height:16 range:[-99999,99999,1]
	spinner spnScaleZMax "" pos:[360,256] width:64 height:16 range:[-99999,99999,1]
	spinner spnReplaySpeedMin "" pos:[272,304] width:64 height:16 range:[-99999,99999,1]
	spinner spnReplaySpeedMax "" pos:[360,304] width:64 height:16 range:[-99999,99999,1]
	spinner spnFrameRangeMin "" pos:[272,320] width:64 height:16 range:[-99999,99999,animationRange.start] scale:1
	spinner spnFrameRangeMax "" pos:[360,320] width:64 height:16 range:[-99999,99999,animationRange.end] scale:1
	spinner spnPingPongFrequency "" pos:[360,336] width:64 height:16 range:[0,1,.2]

	fn removeObj =
	(
		if (lbxObjList.selection != undefined and lbxObjList.items.count > 0) then
		(
			oldSelection = lbxObjList.selection
			deleteItem lbxObjList.items lbxObjList.selection
			if (oldSelection < lbxObjList.items.count) then
				lbxObjList.selection = oldSelection
			else if (lbxObjList.items.count > 0) then
				lbxObjList.selection = lbxObjList.items.count

			availableObjs = lbxObjList.items = lbxObjList.items
		)
	)
	fn saveCurProp =
	(
		if (curObj != undefined) then
		(
			ieMaxSetProp curObj (remPrefix spnFrequency.name) spnFrequency.value
			for i in posControls do ieMaxSetProp curObj (remPrefix i.name) i.value
			for i in rotControls do  ieMaxSetProp curObj (remPrefix i.name) i.value
			for i in scaleControls do  ieMaxSetProp curObj (remPrefix i.name) i.value
			for i in proxyControls do  ieMaxSetProp curObj (remPrefix i.name) i.value
		)
	)
	fn getNewObj =
	(
		obj = lbxObjList.items[lbxObjList.selection]
		if (obj != undefined) then
		(
			val = ieMaxGetProp obj (remPrefix spnFrequency.name)
			if (val != undefined) then  spnFrequency.value = val else  spnFrequency.value = defaultFrequency

			for i in posControls do
			(
				val = ieMaxGetProp obj (remPrefix i.name)
				if (val != undefined) then i.value = val else i.value = 0
			)
			for i in rotControls do
			(
				val = ieMaxGetProp obj (remPrefix i.name)
				if (val != undefined) then i.value = val else i.value = 0
			)
			for i in scaleControls do
			(
				val = ieMaxGetProp obj (remPrefix i.name)
				if (val != undefined) then i.value = val else i.value = 1
			)
			 for n = 1 to proxyControls.count do
			 (
				 p = proxyControls[n]
				 val = ieMaxGetProp obj (remPrefix p.name)
				 if (val != undefined) then p.value = val else p.value = proxyDefaults[n]
			 )
		)
		curObj = lbxObjList.items[lbxObjList.selection]
	)
	on objUtilitiesRoll open do
	(
		posControls = #(spnPosXMin, spnPosXMax, spnPosYMin, spnPosYMax, spnPosZMin, spnPosZMax)
		rotControls = #(spnRotXMin, spnRotXMax, spnRotYMin, spnRotYMax, spnRotZMin, spnRotZMax)
		scaleControls = #(spnScaleXMin, spnScaleXMax, spnScaleYMin, spnScaleYMax, spnScaleZMin, spnScaleZMax)
		proxyControls = #(spnReplaySpeedMin, spnReplaySpeedMax, spnFrameRangeMin, spnFrameRangeMax, spnPingPongFrequency)
		proxyDefaults = #(1,1,0,0,0)
		availableObjs = ieMaxDumpPropNames objData

		if (availableObjs != undefined) then
		(
			for p in availableObjs do
			(
				if (isValidNode (getNodeByName p)) then
					append lbxObjList.items p
			)
			lbxObjList.items = lbxObjList.items
			if (lbxObjList.items.count > 0) then
			(
				curObj = lbxObjList.items[lbxObjList.selection]
				getNewObj()
			)
		)
	)
	on objUtilitiesRoll close do
	(
		ieMaxClearProp objData
		for p in lbxObjList.items do
			ieMaxSetProp objData p 0

		saveCurProp()
		curObj = undefined
	)
	on objUtilitiesRoll rolledUp state do
	(
		if (state) then
			objUtilitiesFloater.size.y += objUtilitiesRoll.height
		else
			objUtilitiesFloater.size.y -= objUtilitiesRoll.height
	)
	on lbxObjList selected sel do
	(
		saveCurProp()
		curObj = lbxObjList.items[sel]
		getNewObj()
	)
	on lbxObjList doubleClicked sel do
		removeObj()
	on btnAddSelected pressed do
	(
		selectedObjects = ieMaxCopyUserSelection()
		if (selectedObjects != undefined) then
		(
			for i in selectedObjects do
			(
				objName = i.name
				if ((findItem lbxObjList.items objname) == 0) then
					append lbxObjList.items objName
			)
			availableObjs = lbxObjList.items = lbxObjList.items
		)
		if (lbxObjList.items.count > 0) then
		(
			curObj = lbxObjList.items[lbxObjList.selection]
			getNewObj()
		)
	)
	on btnRemoveObj pressed do
		removeObj()
	on btnSetAll pressed do
	(
		if (queryBox ("Set all object properties based on current selection?") title:"Set All Confirmation") then
		(
			saveCurProp()
			baseObj = getNodeByName curObj
			if (isValidNode baseObj) then
			(
				baseBuffer = getUserPropBuffer baseObj

				for o in lbxObjList.items do
				(
					obj = getNodeByName o
					if (isValidNode obj) then
						setUserPropBuffer obj baseBuffer
				)
			)
		)
	)
	on btnClearObjs pressed do
	(
		lbxObjList.items = #()
		availableObjs = lbxObjList.items = lbxObjList.items
	)
)

--//Place Tools
--//-----------------------------------------------------------------------------
rollout objToolsRoll "Place Tools" width:520 height:168
(
	checkbutton ckbPlaceObjs "Paint Objects" pos:[24,128] width:144 height:24
	button btnPlaceOnSelection "Place On Selection" pos:[360,8] width:144 height:24
	spinner spnObjSpacing "" pos:[104,104] width:64 height:16 range:[-999999,999999,1] type:#worldunits
	label lbl23 "Object Spacing:" pos:[24,104] width:80 height:16
	checkbox chkInstanceObjs "Instance Objects" pos:[8,8] width:112 height:16
	button btnReplaceSelected "Replace Selected Objects" pos:[360,72] width:144 height:24
	GroupBox grpObjectPainting "Object Painting" pos:[8,48] width:169 height:112
	GroupBox grp6 "Particle Placement" pos:[184,48] width:160 height:112
	dropdownList ddlParticleSystem "" pos:[192,64] width:144 height:21
	button btnPlaceWithParticles "Place with Particles" pos:[192,96] width:144 height:24
	GroupBox grp7 "Refine Placement" pos:[352,48] width:160 height:112
	pickbutton btnPickSurfaceMesh "Pick Surface Mesh" pos:[16,64] width:152 height:24
	button btnRefreshParticleList "Refresh Particle List" pos:[192,128] width:144 height:24
	button btnPointSelected "Point Selected at Target" pos:[360,104] width:144 height:24
	pickButton btnOrientTarget "Orientation Target" pos:[120,8] width:144 height:24

	fn setSurfaceButton = btnSelectSurfaceMesh.caption = ("Mesh: " + surfaceMesh.name)
	on objToolsRoll open do
	(
		ddlParticleSystem.items = for o in $* where classof o == PF_Source collect o.name
		tMeshName = ieMaxGetProp placeData "surfaceMesh"
		if (tMeshName != undefined) then surfaceMesh = getNodeByName tMeshName
		if (isValidNode surfaceMesh) then
			btnPickSurfaceMesh.text = "Mesh: " + surfaceMesh.name
		else
			surfaceMesh = undefined

		oMeshName = ieMaxGetProp placeData "targetObj"
		if (oMeshName != undefined) then targetObj = getNodeByName oMeshName
		if (isValidNode targetObj) then
			btnOrientTarget.text = "Target: " + targetObj.name
		else
			targetObj = undefined

		currentLayerNumber = getCurrentLayerNumber()
	)
	on btnPickSurfaceMesh picked obj do
	(
		surfaceMesh = obj
		btnPickSurfaceMesh.text = "Mesh: " + obj.name
		ieMaxSetProp placeData "surfaceMesh" obj.name
	)
	on btnOrientTarget picked obj do
	(
		targetObj = obj
		btnOrientTarget.text = "Target: " + obj.name
		ieMaxSetProp placeData "targetObj" obj.name
	)
	on objToolsRoll close do
	(
	)
	on objToolsRoll rolledUp state do
	(
		if (state) then
			objUtilitiesFloater.size.y += objToolsRoll.height
		else
			objUtilitiesFloater.size.y -= objToolsRoll.height
	)
	on ckbPlaceObjs changed state do
	(
		objUtilitiesRoll.saveCurProp()

		buildObjList &objList

		if (checkObjList()) then
		(
			if (state) then
			(
				thePainterInterface.ScriptFunctions strokeStart strokePaintObjs strokeEnd paintingCancel paintingEnd
				thePainterInterface.pointGatherEnable = true
				thePainterInterface.drawTrace = false
				thePainterInterface.initializeNodes 0 #(surfaceMesh)
				thePainterInterface.offMeshHitType = 2
				thePainterInterface.startPaintSession()
			)
			else
				thePainterInterface.endPaintSession()
		)
	)
	on spnObjSpacing changed value do
	(
		minObjSpacing = value
	)
	on btnReplaceSelected pressed do
	(
		if (queryBox ("Replace all objects in scene?") title:"Replace All Confirmation") then
		(
			buildObjList &objList

			if (checkObjList()) then
			(
				objsToReplace = getCurrentSelection()
				for s in objsToReplace do
					replaceObj s
				delete objsToReplace
			)
		)
	)
	on btnPlaceWithParticles pressed do
	(
		pf = getNodeByName ddlParticleSystem.items[ddlParticleSystem.selection]
		if (isvalidNode pf) then
		(
			subobjectlevel = 0
			getUserProp
			max select none
			layerNumber = getCurrentLayerNumber()
			layerName = ("place_" + (layerNumber as string))
			placeLayer = LayerManager.getLayerFromName layerName
			if (placeLayer == undefined) then
				placeLayer = LayerManager.newLayerFromName layerName
			placeLayer.current = true
			pCount = pf.numParticles()
			if (queryBox ("Place objects for " + (pCount as string) + " particles?") title:"Particle Count Confirmation") then
			(
				buildObjList &objList
				if (checkObjList()) then
				(
					for i = 1 to pCount do
						placeObj (pf.getParticleTMByID i)
				)
			)
			ieMaxSetProp placeData "layerNumber" ((layerNumber as integer) + 1)
		)
		else
			messageBox "Please select the particle system to place objects with" title:"No Particle System"
	)
	on btnRefreshParticleList pressed do
	(
		ddlParticleSystem.items = for o in $* where classof o == PF_Source collect o.name
	)
	on btnPointSelected pressed do
	(
		if (isValidNode targetObj) then
		(
			for o in getCurrentSelection() do
			(
				dist = o.pos - targetObj.pos
				dist = normalize dist
				upVec = [0,0,1]
				dp = dot dist upVec
				t = acos dp
				c = cross upVec dist
				c = normalize c
				o.dir = c
				in coordsys local rotate o (eulerangles -90 0 0)
				in coordsys local rotate o (eulerangles 0 0 -90)
			)
		)
		else
			messageBox "Please first select a target object" title:"No target object found"
	)
	on btnPlaceOnSelection pressed do
	(
		userSel = getCurrentSelection()
		max select none
		buildObjList &objList

		layerNumber = getCurrentLayerNumber()
		layerName = ("place_" + (layerNumber as string))
		placeLayer = LayerManager.getLayerFromName layerName
		if (placeLayer == undefined) then
			placeLayer = LayerManager.newLayerFromName layerName
		placeLayer.current = true

		if (checkObjList()) then
		(
			for obj in userSel do
				placeObj obj.transform obj:obj
		)
	)
)

if (objUtilitiesFloater != undefined) then
	CloseRolloutFloater objUtilitiesFloater
floaterWidth = (objToolsRoll.width + 20)
floaterHeight = (proxyUtilitiesRoll.height + objUtilitiesRoll.height + objToolsRoll.height + 30 + 45)
objUtilitiesFloater = newRolloutFloater "Place Tools v1.60" floaterWidth floaterHeight 130 130
addRollout proxyUtilitiesRoll objUtilitiesFloater
addRollout objUtilitiesRoll objUtilitiesFloater
addRollout objToolsRoll objUtilitiesFloater
)
--//-----------------------------------------------------------------------------