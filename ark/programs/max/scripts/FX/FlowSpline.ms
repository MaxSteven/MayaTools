--//-----------------------------------------------------------------------------
--// FlowSpline.ms
--// By Grant Miller (blented@gmail.com)
--// v 1.0
--// Created On: 09/30/09
--// Modified On: 01/11/10
--// tested using Max 2010
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Required Files:
--// ieMax.ms
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Description:
--// Creates a spline for each particle in a pFlow where each frame of the
--// particle's animation is represented by a knot
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Revision History:
--//
--// v 1.00 Initial version
--//
--//-----------------------------------------------------------------------------

(
--// Includes
--//-----------------------------------------------------------------------------
fileIn (MAX_TOOLS_ROOT + "lib/ieMax.ms")

--// Globals
--//-----------------------------------------------------------------------------
global flowSplineRoll
global flowSplineFloater
global pFlow
global surfaceObj
global splineBase

--// Functions
--//-----------------------------------------------------------------------------
fn compareVerts pos1 pos2 thresh =
(
	if pos1.x < pos2.x + thresh and pos1.x > pos2.x - thresh then
		if pos1.y < pos2.y + thresh and pos1.y > pos2.y - thresh then
			if pos1.z < pos2.z + thresh and pos1.z > pos2.z - thresh then
				return true

	return false
)

fn ieMaxGetArrayProp dataName propName =
(
	prop = ieMaxGetProp dataName propName
	if (prop == undefined) then
		prop = #()
	else
		prop = execute prop
	return prop
)

--// Variables
--//-----------------------------------------------------------------------------
flowSplineData = "FlowSplineData"
splineSets = ieMaxGetArrayProp flowSplineData "splineSets"
flowOrder = ieMaxGetArrayProp flowSplineData "flowOrder"

--// Script
--//-----------------------------------------------------------------------------
rollout flowSplineRoll "Flow Spline" width:264 height:816
(
	fn pFlowFilter obj =
	(
		classof obj == PF_Source
	)
	fn surfaceFilter obj =
	(
		superClassOf obj == GeometryClass
	)
	fn splineFilter obj =
	(
		superClassOf obj == shape
	)

	GroupBox grp1 "Flow Splines" pos:[8,8] width:248 height:80
	GroupBox grp2 "Spline Meshing" pos:[8,584] width:248 height:224
	GroupBox grp3 "Surface Splines" pos:[8,96] width:248 height:104
	GroupBox grp16 "Flow Connect" pos:[8,336] width:248 height:240
	label lbl1 "Frame Skip:" pos:[16,56] width:64 height:16
	label lbl4 "Num Splines:" pos:[136,112] width:64 height:16
	label lbl9 "Min Knots:" pos:[16,144] width:64 height:16
	label lbl10 "Max Knots:" pos:[136,144] width:64 height:16
	pickbutton btnPFlow "Pick pFlow" pos:[16,24] width:112 height:24 filter:pFlowFilter
	pickbutton btnSurface "Pick Surface" pos:[16,112] width:112 height:24 filter:surfaceFilter
	pickbutton btnPickSpline "Pick Spline Set" pos:[16,224] width:112 height:24 filter:splineFilter
	button btnMakeFlowSplines "Make Flow Splines" pos:[136,24] width:112 height:24
	spinner spnFrameSkip "" pos:[80,56] width:48 height:16 range:[0,999,4] type:#integer
	listbox lbxMeshes "Meshes" pos:[16,600] width:112 height:8
	button btnAddSelectedMeshes "Add Selected" pos:[16,728] width:112 height:24
	button btnClearMeshes "Clear Mesh List" pos:[16,776] width:112 height:24
	button btnMakePathMeshes "Make Path Meshes" pos:[16,752] width:112 height:24
	button btnClearFlowSplines "Clear Flow Splines" pos:[136,56] width:112 height:24
	button btnClearPathMeshes "Clear Path Meshes" pos:[136,712] width:112 height:24
	button btnMakeSurfaceSplines "Make Surface Splines" pos:[16,168] width:112 height:24
	spinner spnNumSplines "" pos:[200,112] width:48 height:16 range:[1,999,10] type:#integer
	button btnClearSurfaceSplines "Clear Surface Splines" pos:[136,168] width:112 height:24
	listbox lbxSplineSets "Spline Sets" pos:[16,352] width:112 height:9
	listbox lbxFlowOrder "Flow Order" pos:[136,352] width:112 height:9
	button btnReset "Reset" pos:[16,520] width:112 height:24
	button btnOrderUp "Up" pos:[136,496] width:56 height:24
	button btnDeleteSet "Delete Set" pos:[16,544] width:112 height:24
	button btnOrderDown "Down" pos:[192,496] width:56 height:24
	spinner spnMinKnots "" pos:[80,144] width:48 height:16 range:[1,999,5] type:#integer
	spinner spnMaxKnots "" pos:[200,144] width:48 height:16 range:[1,999,10] type:#integer
	button btnFlowConnect "Connect" pos:[192,520] width:56 height:24
	button btnLink "Link" pos:[136,520] width:56 height:24
	button btnAddSet "Add Selected" pos:[16,496] width:112 height:24
	button btnDeleteFlowSplines "Delete Flow Splines" pos:[136,544] width:112 height:24
	GroupBox grp21 "Spline Prep" pos:[8,208] width:248 height:120
	spinner spnSplineCount "" pos:[80,256] width:48 height:16 range:[1,9999,300] type:#integer
	label lbl21 "Spline Count:" pos:[16,256] width:64 height:16
	button btnPrepSplines "Prep Splines" pos:[136,296] width:112 height:24
	spinner spnXJitter "" pos:[200,224] width:48 height:16 range:[0,9999,1] type:#worldunits
	label lbl23 "X Jitter:" pos:[160,224] width:40 height:16
	spinner spnYJitter "" pos:[200,248] width:48 height:16 range:[0,9999,1] type:#worldunits
	label lbl24 "Y Jitter:" pos:[160,248] width:40 height:16
	spinner spnZJitter "" pos:[200,272] width:48 height:16 range:[0,9999,1] type:#worldunits
	label lbl25 "Z Jitter:" pos:[160,272] width:40 height:16
	button btnReduceSpline "Reduce Spline" pos:[16,296] width:112 height:24
	spinner spnMapStart "" pos:[200,600] width:48 height:16 range:[-9999,9999,0] type:#integer
	label lbl11 "Map Start:" pos:[144,600] width:56 height:16
	spinner spnMapEnd "" pos:[200,656] width:48 height:16 range:[-9999,9999,96] type:#integer
	label lbl12 "Map End:" pos:[144,656] width:56 height:16
	button btnMapEnd "End Camera Map" pos:[136,680] width:112 height:24
	button btnMapStart "Start Camera Map" pos:[136,624] width:112 height:24

	fn updateSplineSets setName =
	(
		splineSets = ieMaxGetArrayProp flowSplineData "splineSets"
		if (splineSets == undefined) then splineSets = #()
		if (findItem splineSets (setName) == 0) then
		(
			append splineSets (setName)
			ieMaxSetProp flowSplineData "splineSets" splineSets
			lbxSplineSets.items = splineSets
			lbxSplineSets.items = lbxSplineSets.items
		)
	)

--//INIT
--//-----------------------------------------------------------------------------------------------------------------------------------
	on flowSplineRoll open do
	(
		lbxSplineSets.items = splineSets
		lbxSplineSets.items = lbxSplineSets.items
		lbxFlowOrder.items = flowOrder
		lbxFlowOrder.items = lbxFlowOrder.items

		userSel = getCurrentSelection()
		if (userSel.count > 0) then
		(
			if (pFlowFilter userSel[1]) then
			(
				pFlow = userSel[1]
				btnPFlow.text = userSel[1].name
			)
		)
	)
	on flowSplineRoll rolledUp state do
	(
		if (state) then
			flowSplineFloater.size.y += flowSplineRoll.height
		else
			flowSplineFloater.size.y -= flowSplineRoll.height
	)

--//FLOW SPLINES
--//-----------------------------------------------------------------------------------------------------------------------------------
	on btnPFlow picked obj do
	(
		pFlow = obj
		btnPFlow.text = obj.name
	)
	on btnMakeFlowSplines pressed do
	(
		enableEscape = true
		progressStart "Creating Flow Splines"
		if (pFlowFilter pFlow) then
		(
			delete (execute ("$'" + pFlow.name + "_flowSpline'*")) --//delete old flow splines from the SAME pFlow
			updateSplineSets pFlow.name
			local tStart = animationrange.start
			local tEnd = animationrange.end
			updateSplineSets pFlow.name
			particleCount = pFlow.numParticles()
			flowSpline = #()
			flowSpline[particleCount] = 0
			for p = 1 to particleCount do
			(
				pFlow.particleIndex = p
				particleID = pFlow.particleID
				if particleID > 0 do  --if the ID is positive,
				(
					flowSpline[p] = SplineShape pos:pFlow.particleTM.position
					flowSpline[p].name = uniquename (pFlow.name + "_flowSpline")
					addNewSpline flowSpline[p]
				)
			)
			frameSkip = spnFrameSkip.value + 1
			genMin = 0.5 * tEnd --//temp calculation
			genMax = tEnd
			stopGen = #()
			for p = 1 to particleCount do
			(
				stopGen[p] = random genMin genMax
			)
			for t = tStart to tEnd by frameSkip do
			(
				slidertime = t
				if getProgressCancel() then
					exit
				progressUpdate (100.0 * t / tEnd)

				for p = 1 to particleCount do
				(
					pFlow.particleIndex = p
					particleID = pFlow.particleID
					if (particleID > 0) then -- and tEnd < stopGen[p]) then  --if the ID is positive,
					(
						particlePosition = pFlow.particleTM.position
						addKnot flowSpline[p] 1 #smooth #curve particlePosition --1 is the spline index
--//            updateShape flowSpline
					)--id > 0
				)--//particle loop
			)--//particle loop
			for p = 1 to particleCount do
			(
				pFlow.particleIndex = p
				particleID = pFlow.particleID
				if (particleID > 0) then  --if the ID is positive,
				(
					updateShape flowSpline[p]
				)
			)
			progressEnd()
			enableEscape = false
		)--//pFlowClass
	)
	on btnClearFlowSplines pressed do
	(
		delete (execute ("$'" + pFlow.name + "_flowSpline'*")) --delete old flow splines from the same pFlow
	)

--//SURFACE SPLINES
--//-----------------------------------------------------------------------------------------------------------------------------------
	on btnSurface picked obj do
	(
		surfaceObj = obj
		btnSurface.text = obj.name
	)
	on btnMakeSurfaceSplines pressed do
	(
		if (surfaceFilter surfaceObj) then
		(
			updateSplineSets surfaceObj.name
			numVerts = polyop.getNumVerts surfaceObj
			surfaceSpline = #()
			numSplines = spnNumSplines.value
			surfaceSpline[numSplines] = 0
			for s = 1 to numSplines do
			(
				surfaceSpline[s] = SplineShape()
				surfaceSpline[s].name = uniquename (surfaceObj.name + "_surfaceSpline")
				addNewSpline surfaceSpline[s]
				numKnots = random 5 20
				for v = 1 to numKnots do
				(
					vertIndex = random 1 numVerts
					in coordsys world vertPos = polyop.getVert surfaceObj vertIndex
					addKnot surfaceSpline[s] 1 #smooth #curve vertPos --1 is the spline index
				)
				updateShape surfaceSpline[s]
			)
		)
	)
	on btnClearSurfaceSplines pressed do
	(
		delete (execute ("$'*_surfaceSpline'*")) --delete old surface splines from the same surface mesh
	)

--//SPLINE PREP
--//-----------------------------------------------------------------------------------------------------------------------------------
	on btnPickSpline picked obj do
	(
		splineBase = filterString obj.name "-"
		splineBase = splineBase[1]
		btnPickSpline.text = splineBase
	)
	on btnReduceSpline pressed do
	(
		userSel = getCurrentSelection()
		if (userSel.count == 1 and superClassOf userSel[1] == shape) then
		(
			spline = userSel[1]
			k = for s = 1 to (numKnots spline) where (mod s 2 == 0) collect s
			subObjectLevel = 1
			try(setKnotSelection $ 1 k)catch()
			max delete
		)
	)
	on btnPrepSplines pressed do
	(
		select (execute ("$'" + splineBase + "'*"))
		splineSet = getCurrentSelection()
--//make splineCount - splineSet.count number of splines
		for n = 1 to (spnSplineCount.value) do
		(
			splineIndex = random 1 splineSet.count
			spline = copy splineSet[splineIndex]
			spline.name = uniquename (splineBase + "_")
--//remove a random amount of knots from the front of the spline
--//      numSplineKnots = numKnots spline
--//      for m = (random 1 (floor (0.3 * numSplineKnots))) to numSplineKnots do deleteKnot spline 1 1
--//update the number of knots and then jitter all of their positions
			numSplineKnots = numKnots spline
			jitter = [0,0,0]
			for m = 1 to numSplineKnots do
			(
				knotPos = getKnotPoint spline 1 m
				jitter.x += random (-1 * spnXJitter.value) spnXJitter.value
				jitter.y += random (-1 * spnYJitter.value) spnYJitter.value
				jitter.z += random (-1 * spnZJitter.value) spnZJitter.value
				knotPos += jitter
				setKnotPoint spline 1 m knotPos
			)
		)
		if (lbxSplineSets.items.count < 1) then
			lbxSplineSets.items = #(splineBase)
		else if (findItem lbxSplineSets.items splineBase == 0) then
			append lbxSplineSets.items splineBase

		lbxSplineSets.items = lbxSplineSets.items
	)

--//FLOW CONNECT
--//-----------------------------------------------------------------------------------------------------------------------------------
	on lbxSplineSets doubleClicked sel do
	(
		if (sel > 0) then
		(
			append lbxFlowOrder.items lbxSplineSets.items[sel]
			deleteItem lbxSplineSets.items sel
			lbxSplineSets.items = lbxSplineSets.items --//required to properly update list
			lbxFlowOrder.items = lbxFlowOrder.items
			ieMaxSetProp flowSplineData "flowOrder" lbxFlowOrder.items
			ieMaxSetProp flowSplineData "splineSets" lbxSplineSets.items
		)
	)
	on lbxFlowOrder doubleClicked sel do
	(
		if (sel > 0) then
		(
			append lbxSplineSets.items lbxFlowOrder.items[sel]
			deleteItem lbxFlowOrder.items sel
			lbxSplineSets.items = lbxSplineSets.items
			lbxFlowOrder.items = lbxFlowOrder.items
			ieMaxSetProp flowSplineData "flowOrder" lbxFlowOrder.items
			ieMaxSetProp flowSplineData "splineSets" lbxSplineSets.items
		)
	)
	on btnAddSet pressed do
	(
		userSel = getCurrentSelection()
		if (userSel.count == 1 and superClassOf userSel[1] == shape) then
		(
			baseName = filterString userSel[1].name "_"
			baseName = baseName[1]
			if (lbxSplineSets.items.count < 1) then
				lbxSplineSets.items = #(baseName)
			else
				append lbxSplineSets.items baseName
		)
		lbxSplineSets.items = lbxSplineSets.items
	)
	on btnDeleteSet pressed do
	(
		sel = lbxSplineSets.selection
		if (sel > 0) then
		(
			delete (execute ("$'" + lbxSplineSets.items[sel] + "_'*"))
			deleteItem lbxSplineSets.items sel
			lbxSplineSets.items = lbxSplineSets.items --//required to properly update list
			ieMaxSetProp flowSplineData "splineSets" lbxSplineSets.items
		)
	)
	on btnReset pressed do
	(
		if (lbxSplineSets.items.count < 1) then
			lbxSplineSets.items = for s in lbxFlowOrder.items where s != "--link--" collect s
		else
			for s in lbxFlowOrder.items where s != "--link--" do append lbxSplineSets.items s
		lbxFlowOrder.items = #()
		lbxSplineSets.items = lbxSplineSets.items
		ieMaxSetProp flowSplineData "flowOrder" #()
		ieMaxSetProp flowSplineData "splineSets" lbxSplineSets.items
	)
	on btnOrderUp pressed do
	(
		sel = lbxFlowOrder.selection
		if (sel > 0) then
		(
			item = lbxFlowOrder.items[sel]
			deleteItem lbxFlowOrder.items sel
			insertionPoint = (amax (sel - 1) 1)
			insertItem item lbxFlowOrder.items insertionPoint
			lbxFlowOrder.selection = insertionPoint
			ieMaxSetProp flowSplineData "flowOrder" lbxFlowOrder.items
			lbxFlowOrder.items = lbxFlowOrder.items
		)
	)
	on btnOrderDown pressed do
	(
		sel = lbxFlowOrder.selection
		if (sel > 0) then
		(
			item = lbxFlowOrder.items[sel]
			deleteItem lbxFlowOrder.items sel
			insertionPoint = (amin (sel + 1) (lbxFlowOrder.items.count + 1))
			insertItem item lbxFlowOrder.items insertionPoint
			lbxFlowOrder.selection = insertionPoint
			lbxFlowOrder.items = lbxFlowOrder.items
			ieMaxSetProp flowSplineData "flowOrder" lbxFlowOrder.items
		)
	)
	on btnLink pressed do
	(
		sel = lbxFlowOrder.selection
		if (sel > 0) then
			insertItem "--link--" lbxFlowOrder.items sel
		else
			append lbxFlowOrder.items "--link--"
		ieMaxSetProp flowSplineData "flowOrder" lbxFlowOrder.items
		lbxFlowOrder.items = lbxFlowOrder.items
	)
	on btnDeleteFlowSplines pressed do
	(
		delete (execute ("$'flowConnect'*"))
	)
	on btnFlowConnect pressed do
	(
		if (lbxFlowOrder.items.count > 0) then
		(
			flowOrder = deepCopy lbxFlowOrder.items
			struct flowSet (index, spline, start, end, linkIndex)
			flowSets = #()
			flowNumber = 1
			splineParent = undefined
			do
			(
				linkPos = findItem flowOrder "--link--"
				if (linkPos > 0) then
				(
					stopPos = linkPos - 1
					deleteItem flowOrder linkPos
				)
				else
				(
					stopPos = flowOrder.count
				)
				flowSets[flowNumber] = #()
				for n = 1 to stopPos do
				(
					select (execute ("$'" + flowOrder[n] + "_'*"))
					splines = getCurrentSelection()
					for s = 1 to splines.count do
					(
						append (flowSets[flowNumber]) (flowSet spline:splines[s])
					)
				)
				flowNumber += 1
				for n = 1 to stopPos do deleteItem flowOrder 1
			) while flowOrder.count > 0

			--//connection count is the minimum spline count across all flow sets
			connectionCount = flowSets[1].count
			for n = 2 to flowSets.count do
			(
				connectionCount = amin flowSets[n].count connectionCount
			)

			for j = 1 to connectionCount do
			(
				for k = 1 to flowSets.count do
				(
					flowSets[k][j].start = getKnotPoint flowSets[k][j].spline 1 1
					flowSets[k][j].end = getKnotPoint flowSets[k][j].spline 1 (numKnots flowSets[k][j].spline)
					flowSets[k][j].index = j
				)
			)
			flowTo = deepCopy flowSets

--//go through each spline
			for j = 1 to connectionCount do
			(
--//get the first end knot of the first spline
--//then for each flow set after the first one
--//go through each spline left in the flowTo for that set and look for the start knot that's closest to the end knot
--//when that's found, set the spline of the closest knot as the previous spline in the previous flow set's link spline
--//update the end knot to the end knot of the current spline, delete the current spline from the current spline set (since we just used it as a link) then repeat

				endKnot = flowSets[1][j].end
				lastIndex = j
				local closestIndex
				local deleteIndex
				closest = 0
				for m = 2 to flowSets.count do
				(
					for s = 1 to flowTo[m].count do
					(
						d = length (flowTo[m][s].start - endKnot)
						if (d < closest or s == 1) then
						(
							deleteIndex = s
							closestIndex = flowTo[m][s].index
							closest = d
						)
					)
					lastIndex = flowSets[m-1][lastIndex].linkIndex = closestIndex
					endKnot = flowSets[m][closestIndex].end
					deleteItem flowTo[m] deleteIndex
				)
			)
			--//flow sets is made of an array of arrays, each array should be linked to the next
			--//loop through each flow spline
			for j = 1 to connectionCount do
			(
				in coordsys world
				(
					knotPos = #()
					linkIndex = j
					--//loop through each of the splines that we're connecting for the new flow spline
					for k = 1 to flowSets.count do
					(
						if (flowSets[k][linkIndex].spline.parent != undefined) then
							splineParent = flowSets[k][linkIndex].spline.parent

						for m = 1 to numKnots (flowSets[k][linkIndex].spline) do
							append knotPos (getKnotPoint flowSets[k][linkIndex].spline 1 m)

						linkIndex = flowSets[k][linkIndex].linkIndex
					)
				)

				flowConnect = SplineShape()
				flowConnect.name = uniquename ("flowConnect")
				addNewSpline flowConnect
				for k in knotPos do ( addKnot flowConnect 1 #smooth #curve k )
				updateShape flowConnect
				flowConnect.parent = splineParent
			)
		)
		else
		(
			print "Need more info"
		)
	)
	on btnClearFlowConnections pressed do
	(
		delete (execute ("$'*_flowConnect'*")) --delete old surface splines from the same surface mesh
	)

--//SPLINE MESHING
--//-----------------------------------------------------------------------------------------------------------------------------------
	on btnAddSelectedMeshes pressed do
	(
		userSel = getCurrentSelection()
		if (userSel.count > 0) then
		(
			meshes = for s in userSel where (ieMaxIsGeometry s) collect s.name
		)
		lbxMeshes.items = meshes
	)
	on btnClearMeshList pressed do ( lbxMeshes.items = #() )
	on lbxMeshes doubleClicked sel do
	(
		if (sel > 0) then
		(
			deleteItem lbxMeshes.items sel
			lbxMeshes.items = lbxMeshes.items --//required to properly update list
		)
	)
	on btnMakePathMeshes pressed do
	(
		if (lbxMeshes.items.count > 0 and lbxFlowOrder.items.count > 0) then
		(
--      delete (execute ("$'pathMesh_'*")) --delete old flow splines from the same pFlow
			tStart = animationrange.start
			--local tEnd = animationrange.end
			mStart = spnMapStart.value
			mEnd = spnMapEnd.value
			slidertime = spnMapStart.value
			if (lbxFlowOrder.items.count > 1) then
			(
				flowPaths = for s in $flowConnect* collect s
			)
			else
			(
				flowPaths = for s in (execute ("$" + lbxFlowOrder.items[1] + "_*")) collect s
			)
--//        flowPaths = for s in $flowConnect* collect s
			for flowPath in flowPaths do
			(
				meshNum = random 1 lbxMeshes.items.count
				pathMesh = reference (getNodeByName lbxMeshes.items[meshNum])
				pathMesh.name = uniquename ("pathMesh_")
				pathMesh.parent = flowPath.parent
				flowPath.parent = undefined
				pathMod = PathDeform()
				addModifier pathMesh pathMod

				pathMatrix = ieMaxGetSplineMatrix flowPath 1 1
				pathMod.path = flowPath
				pathMesh.transform = pathMatrix
				pathMod.axis = 2
				with animate on
				(
--          at time tStart pathMod.Percent_along_path = 8.0
--          at time tStart pathMod.Stretch = 0.25
						at time mStart pathMod.Percent_along_path = 77.0
						at time mStart pathMod.Stretch = 0.2
--          at time (mStart + (random 1 3)) pathMod.Percent_along_path = 23.0
--          at time (mStart + (random 1 3)) pathMod.Stretch = 0.2
--//          at time (mStart + 10) pathMod.Stretch = 0.5
--//          at time (mStart + 6) pathMod.Percent_along_path = 3.25
--//          at time (mStart + 6) pathMod.Stretch = 0.25
--//          at time (mStart + 24) pathMod.Stretch = 1.0
--//          at time (mEnd - 6) pathMod.Percent_along_path = 96.0
--          at time ((mStart + mEnd) * 0.5) pathMod.Stretch = 0.4
--          at time (mEnd - (random 1 3)) pathMod.Percent_along_path = 99.0
--          at time (mEnd - (random 1 3)) pathMod.Stretch = 0.2
						at time mEnd pathMod.Percent_along_path = 93.0
						at time mEnd pathMod.Stretch = 0.2
--//          at time (mEnd - 6) pathMod.Stretch = 1.0
--//          at time mEnd pathMod.Stretch = 0.75
--//          at time (mEnd + 6) pathMod.Stretch = 0.5
				)
			)
		)
	)
	on btnMapStart pressed do
	(
		slidertime = spnMapStart.value
		pathMeshes = select (execute ("$'pathMesh_'*"))
		pathMeshes = getCurrentSelection()
		for pathMesh in pathMeshes do
		(
			camera1 = cameraMap()
			camera1.name = "camera1"
			addModifier pathMesh camera1
			camera1.channel = 2
			camera1.cameraNode = $sceneCamera
			unwrap1 = UVWunwrap()
			unwrap1.name = "unwrap1"
			addModifier pathMesh unwrap1
			unwrap1.setMapChannel 2
		)
	)
	on btnMapEnd pressed do
	(
		slidertime = spnMapEnd.value
		pathMeshes = select (execute ("$'pathMesh_'*"))
		pathMeshes = getCurrentSelection()
		for pathMesh in pathMeshes do
		(
			camera2 = cameraMap()
			camera2.name = "camera2"
			addModifier pathMesh camera2
			camera2.channel = 3
			camera2.cameraNode = $sceneCamera
			unwrap2 = UVWunwrap()
			unwrap2.name = "unwrap2"
			addModifier pathMesh unwrap2
			unwrap2.setMapChannel 3
		)
	)
	on btnClearPathMeshes pressed do
	(
		delete (execute ("$'pathMesh_'*"))
	)
)

if flowSplineFloater != undefined then CloseRolloutFloater flowSplineFloater
floaterWidth = (flowSplineRoll.width + 20)
floaterHeight = (flowSplineRoll.height + 30)
flowSplineFloater = newRolloutFloater "FlowSpline" floaterWidth floaterHeight 130 130
addRollout flowSplineRoll flowSplineFloater
)
--//-----------------------------------------------------------------------------
