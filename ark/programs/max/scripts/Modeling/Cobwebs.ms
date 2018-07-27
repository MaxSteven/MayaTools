/*
--bugs
--Add Surface Follow
 */
 
try(destroyDialog ::rlCobwebs)catch()
rollout rlCobwebs "Cobwebs"
(
	-- VARIABLES
	global _genPFPts = #()
	local refObjs = #()
	local autoCenter = [0,0,0]
	local trgObj = undefined
	local subTrgObj = undefined
	local MAINGrp = 10
	local SUBGrp = 230
	local DCOGrp = 425
	local GRAGrp = 445
	local mainStrandCount = 0
	local knotTypes = #(#smooth,#corner,#bezier,#bezierCorner)
	local _particleMaps = #()
	
	groupbox gpMainStrands "Main Strands" pos:[10,10] width:270 height:210
		label lbMainLocation "Start Location:" pos:[20,MAINGrp+20]
		dropdownlist dlMainLocation "" items:#("Pivot","Verts","Edges","Surface","Volume") width:69 selection:4 pos:[110,MAINGrp+15] tooltip:"Controls the starting position of each strand."
		label lbLocationSpacer "-" pos:[188,MAINGrp+20]
		checkbutton cbUniqueMain "Unique" width:70 height:21 checked:true pos:[200,MAINGrp+15] tooltip:"Doesn't allow the same position to be used for the both the starting and ending position of a single strand."
		label lbMainFormat "Format type:" pos:[20,MAINGrp+45]
		dropdownlist dlMainFormat "" items:#("Random","Center","Order","Ivy","Target") width:69 selection:1 pos:[110,MAINGrp+40] tooltip:"Controls the method used to arrange the ending positions for each strand."
		label lbFormatSpacer "-" pos:[188,MAINGrp+45]
		checkbox cbLoopOrder "Loop" pos:[200,MAINGrp+45] visible:false
		spinner spIvyGrow "Time:" fieldwidth:32 range:[animationrange.start,animationrange.end,10] type:#integer pos:[200,MAINGrp+45] visible:false
		pickbutton pbTrgObject "PICK OBJECT" width:70 height:21 pos:[200,MAINGrp+40] visible:false
 		label lbStrands "# Strands:" pos:[20,MAINGrp+70]
		spinner spnMainNum "" fieldwidth:60 range:[2,999999999,20] type:#Integer pos:[107,MAINGrp+70]
 		label lbStrandsSpacer "-" pos:[188,MAINGrp+70]
		spinner spRandStepSpacing "Noise:" fieldwidth:28 range:[0,1,0.0] type:#float pos:[200,MAINGrp+70]
 		label lbKnots "Subdivisions:" pos:[20,MAINGrp+95]
		spinner spSteps "" fieldwidth:60 range:[0,10,1] type:#integer pos:[107,MAINGrp+95]
		label lbKnotsSpacer "-" pos:[188,MAINGrp+95]
		dropdownlist dlKnotType "" items:#("Smooth","Corner","Bezier", "Bezier Corner") width:69 selection:1 pos:[200,MAINGrp+93]
		label lbMainGravityAffectX "Gravity X:" pos:[20,MAINGrp+120] 
		spinner spMGXMin "" fieldwidth:60 range:[-999999999,999999999,-0] type:#worldunits pos:[107,MAINGrp+120]
		spinner spMGXMax "-  " fieldwidth:60 range:[-999999999,999999999,0] type:#worldunits pos:[187,MAINGrp+120]
		label lbMainGravityAffectY "Gravity Y:" pos:[20,MAINGrp+140]
		spinner spMGYMin "" fieldwidth:60 range:[-999999999,999999999,0] type:#worldunits pos:[107,MAINGrp+140]
		spinner spMGYMax "-  " fieldwidth:60 range:[-999999999,999999999,0] type:#worldunits pos:[187,MAINGrp+140]		
		label lbMainGravityAffectZ "Gravity Z:" pos:[20,MAINGrp+160]
		spinner spMGZMin "" fieldwidth:60 range:[-999999999,999999999,-10] type:#worldunits pos:[107,MAINGrp+160]
		spinner spMGZMax "-  " fieldwidth:60 range:[-999999999,999999999,0] type:#worldunits pos:[187,MAINGrp+160]
		label lbLengthSolver "Length Solver:" pos:[20,MAINGrp+185]
  		checkbox cbLengthSolver "" checked:true pos:[110,MAINGrp+185]  tooltip:"Longer splines are affected by gravity more so than a short spline."
		
	groupbox gpSubStrands "Sub Strands" pos:[10,SUBGrp] width:270 height:185
		label lbSubLocation "Start Location:" pos:[20,SUBGrp+20]
		checkbutton cbIncludeEnds "Include Ends" width:70 height:21 checked:true pos:[110,SUBGrp+15] tooltip:"Allows substrands to begin or end at either ending knot of the main strands" 
		label lbSubLocationSpacer "-" pos:[188,SUBGrp+20]
		checkbutton cbUniqueSub "Unique" width:70 height:21 checked:true pos:[200,SUBGrp+15] tooltip:"Doesn't allow the same position to be used for the both the starting and ending position of a single strand."
		label lbSubFormat "Format type:" pos:[20,SUBGrp+45]
		dropdownlist dlSubFormat "" items:#("Random","Radial","Spiral","Target") width:69 selection:1 pos:[110,SUBGrp+40]
		label lbSubFormatSpacer "-" pos:[188,SUBGrp+45]
		pickbutton pbSubTrgObject "PICK OBJECT" width:70 height:21 pos:[200,SUBGrp+40] visible:false
 		label lbSubNum "# Sub Strands:" pos:[20,SUBGrp+70]
 		spinner spnSubNum "" fieldwidth:60 range:[0,999999999,0] type:#Integer pos:[107,SUBGrp+70]
		label lbSubStrandSpacer "-" pos:[188,SUBGrp+70]
		spinner spSubKnotSpacing "Noise:" fieldwidth:28 range:[0,1,0] type:#float pos:[200,SUBGrp+70]
		label lbSubGravityAffectX "Gravity X:" pos:[20,SUBGrp+95] 
		spinner spSGXMin "" fieldwidth:60 range:[-999999999,999999999,0] type:#worldunits pos:[107,SUBGrp+95]
		spinner spSGXMax "-  " fieldwidth:60 range:[-999999999,999999999,0] type:#worldunits pos:[187,SUBGrp+95]
		label lbSubGravityAffectY "Gravity Y:" pos:[20,SUBGrp+115]
		spinner spSGYMin "" fieldwidth:60 range:[-999999999,999999999,0] type:#worldunits pos:[107,SUBGrp+115]
		spinner spSGYMax "-  " fieldwidth:60 range:[-999999999,999999999,0] type:#worldunits pos:[187,SUBGrp+115]		
		label lbSubGravityAffectZ "Gravity Z:" pos:[20,SUBGrp+135]
		spinner spSGZMin "" fieldwidth:60 range:[-999999999,999999999,-5] type:#worldunits pos:[107,SUBGrp+135]
		spinner spSGZMax "-  " fieldwidth:60 range:[-999999999,999999999,0] type:#worldunits pos:[187,SUBGrp+135]
 		label lbRandGaps "Random Gaps %:" pos:[20,SUBGrp+160]	
  		spinner spRandGaps "" fieldwidth:60 range:[0,100,0] type:#float pos:[107,SUBGrp+160]	

	groupbox gpDistanceCutoff "Distance Cutoff Range" pos:[10,DCOGrp] width:270 height:75
		label lbCutoffRange "Cutoff Range:" pos:[20,DCOGrp+20]
		spinner spCutoffMin "" fieldwidth:60 range:[-999999999,999999999,1] type:#worldunits pos:[107,DCOGrp+20] tooltip:"Minimum required length, if the splines length is less then this value then it's removed"
		spinner spCutoffMax "-  " fieldwidth:60 range:[-999999999,999999999,200] type:#worldunits  pos:[187,DCOGrp+20] tooltip:"Maximum required length, if the splines length is greater then this value then it's removed"
		label lbCuttoffAffect "Affect:" pos:[20,DCOGrp+50]
		checkbutton cbDCOMain "Main Strands" width:70 height:21 checked:false pos:[110,DCOGrp+45]
		label lbCutoffAffectSpacer "-" pos:[188,DCOGrp+50]
		checkbutton cbDCOSub "Sub Strands" width:70 height:21 checked:false pos:[200,DCOGrp+45]
	button btnHelp "?" width:20 height:40 pos:[10,510] tooltip:"Help File"
	button btnCreateCobwebs "Create Cobwebs" width:250 height:40 pos:[30,510]
	
	on btnHelp pressed do (shelllaunch "http://jokermartini.com/2012/05/09/cobwebs/" "")
	on ckXRange changed state do (ckXRange.text = if state then "X -X" else "X")
	on ckYRange changed state do (ckYRange.text = if state then "Y -Y" else "Y")
	on ckZRange changed state do (ckZRange.text = if state then "Z -Z" else "Z")
	on dlMainFormat selected idx do 
	(
		cbLoopOrder.visible = if idx == 3 then true else false
		spIvyGrow.visible = if idx == 4 then true else false
		pbTrgObject.visible = if idx == 5 then true else false
	)
	on dlSubFormat selected idx do 
	(
		pbSubTrgObject.visible = if idx == 4 then true else false
	)
	
	
	--//FUNCTIONS
	fn fnPFPoints nodes amount:10 location:4 = (		
		pfp = PF_Source name:"pf_points" X_Coord:0 Y_Coord:0 Quantity_Viewport:100 Show_Logo:off Show_Emitter:off
		
		particleFlow.BeginEdit()
		op1 = Birth name:"pfp_birth" amount:amount Emit_Stop:currenttime Emit_Start:currenttime
		op2 = Position_Object name:"pfp_place" Emitter_Objects:nodes Location:location Lock_On_Emitter:on Random_Seed:(random 1 1000000000)
		
		source  = ""
		source += "on ChannelsUsed pCont do (pCont.usePosition = on) \n"
		source += "on Proceed pCont do for k=1 to pCont.NumParticles() do\n"
		source += "	_genPFPts[pCont.particleIndex = k] = pCont.particlePosition\n"
		
		op3 = Script_Test name:"pfp_test" Proceed_Script:source
		ev1 = Event name:"pfp_event"
		ev1.AppendAction op1
		ev1.AppendAction op2
		ev1.AppendAction op3
		
		pfp.AppendInitialActionList ev1
		particleFlow.EndEdit()
		particleFlow.delete pfp
	)
		
	fn fnSurfaceFollow surfaceObjs: =
	(
		theForce = Wind pos:[20,20,0] strength:0 windtype:0 turbulence:5 frequency:1 
		pfSys = PF_Source name:(uniquename "PF_SplineDrawer") Quantity_Viewport:100 Show_Logo:off Show_Emitter:off
		
		particleFlow.BeginEdit()
		
		op1 = Birth Emit_Start:animationRange.start Emit_Stop:spIvyGrow.value amount:spnMainNum.value
		op2 = Speed()
		op3 = Rotation()
		op4 = Position_Object Emitter_Objects:surfaceObjs
		op5 = Lock_Bond Lock_On_Objects:surfaceObjs Lock_Type:1 Restrict_Position_To_Surface:on Position_Dampening_Type:1	Use_No_Acceleration_Zone:on Zone_Radius:1000 
		op6 = Force Force_Space_Warps:#(theForce)
		ev1 = Event()
		particleFlow.EndEdit()
		
		ev1.AppendAction op1
		ev1.AppendAction op2
		ev1.AppendAction op3
		ev1.AppendAction op4
		ev1.AppendAction op5
		ev1.AppendAction op6
		pfSys.AppendInitialActionList ev1
		pfSys
		
		--collect the positions for each particle
		completeredraw()
 		count = pfSys.NumParticles()
		_particleMaps = for p = 1 to count collect (#())
		
 		for t = (animationRange.start+1) to spIvyGrow.value do
 		(
			slidertime = t
			for p = 1 to count do
			(
				pfSys.particleIndex = p
				append _particleMaps[p] pfSys.particlePosition 	
			)
 		)
		particleFlow.BeginEdit()
		particleFlow.delete pfSys
		particleFlow.EndEdit()
		delete theForce
	)
	
	fn RemoveItemFromArray arr itm = (
		local idx = findItem arr itm
		if idx == 0 then false else deleteItem arr idx
	)

	fn fnRadialSort web = (
		knotsPosArr = for idx = 1 to (numSplines web) collect (getKnotPoint web idx 1) --get the first not in each main strand
		
		--Radial sorting
		radialPosArr = #(knotsPosArr[1])
		itm = knotsPosArr[1]
		while knotsPosArr.count != 1 do
		(
			minDist = amin (for p in knotsPosArr where p != itm collect distance itm p)
			nextnode = (for p in knotsPosArr where p != itm and (distance itm p) == minDist collect p)[1]
			knotsPosArr = RemoveItemFromArray knotsPosArr itm
			itm = nextnode ; append radialPosArr itm
		)
		
		--//Spline ordering based on radial array
		_radialSplineIdx = #()
		for i = 1 to radialPosArr.count do
		(
			for idx = 1 to (numSplines web) do
			(
				theKnot = (getKnotPoint web idx 1)
				if theKnot == radialPosArr[i] do append _radialSplineIdx idx
			)
		)
		return _radialSplineIdx --the order in which the splines are required to make a radial web
	)

	fn fnRandomKnotSpacing web idx val = (	
		for idx = 1 to numSplines web do
		(
			for i = 2 to numSegments web idx do
			(	
				pos = getKnotPoint web idx i
				newPos = ((getKnotPoint web idx i)-(((getKnotPoint web idx i) - ((getKnotPoint web idx (i-1))))*(random -val val)))
				setKnotType web idx i #smooth
				setKnotPoint web idx i newPos	
			)
		)
		--updateShape web
	)

	fn fnFindAverageLenth web = (
		avgPathLength = 0
		numSp = numSplines web
		for idx = 1 to numSp do
		(
			pathLength = curveLength web idx
			avgPathLength += pathLength
		)
		avgPathLength = avgPathLength/numSp
		return avgPathLength
	)
	
	fn fnDrapeWeb web idx secType:"Main" = (
		pathLength = curveLength web idx
		
		--Add middle sagging knot
		pt = subdivideSegment web idx 1 1
		setSegmentType web idx 1 #curve
		setSegmentType web idx 2 #curve
		setKnotType web idx 2 #smooth
		
		--Adjusting position of the knot
		genX = if secType == "Main" then (random spMGXMin.value spMGXMax.value) else (random spSGXMin.value spSGXMax.value)
		genY = if secType == "Main" then (random spMGYMin.value spMGYMax.value) else (random spSGYMin.value spSGYMax.value)
		genZ = if secType == "Main" then (random spMGZMin.value spMGZMax.value) else (random spSGZMin.value spSGZMax.value)
		
		xOffset = if cbLengthSolver.state then ((pathLength*genX)/(fnFindAverageLenth web)) else (genX)
		yOffset = if cbLengthSolver.state then ((pathLength*genY)/(fnFindAverageLenth web)) else (genY)
		zOffset = if cbLengthSolver.state then ((pathLength*genZ)/(fnFindAverageLenth web)) else (genZ)
			
		kPos = getKnotPoint web idx 2
		kPos.x += xOffset
		kPos.y += yOffset
		kPos.z += zOffset
		setKnotPoint web idx 2 kPos
	)
	
	fn fnSubdivide web idx steps = (
		for subD = 1 to steps do 
		(
			for s in (numSegments web idx) to 1 by - 1 do
			(
				knot = subdivideSegment web idx s 1
			)
		)
	)
	
	fn fnCreateMains idx ptA ptB web: = (
		knotType = knotTypes[dlKnotType.selection]
		
		idx = addnewSpline web
		addKnot web idx #corner #curve ptA
		addKnot web idx #corner #curve ptB
		--//Reset Tangets
		if knotType == #bezier OR knotType == #bezierCorner then
		(
			setKnotType web idx 1 #smooth
			setKnotType web idx 2 #smooth
			setKnotType web idx 1 knotType
			setKnotType web idx 2 knotType
		)else(
			setKnotType web idx 1 knotType
			setKnotType web idx 2 knotType
		)
		fnDrapeWeb web idx secType:"Main" --make middle knot & apply gravity to middle knot
		if spRandStepSpacing.value != 0.0 do fnRandomKnotSpacing web idx spRandStepSpacing.value --randomize the spacing of the knots on each spline
		fnSubdivide web idx spSteps.value--subdivide spline
	)
	
	fn fnCreateSubs ptA ptB web: = (
		idx = addnewSpline web
		addKnot web idx #corner #line ptA
		addKnot web idx #corner #line ptB
		fnDrapeWeb web idx secType:"Sub" --make middle knot & apply gravity to middle knot
		if spSubKnotSpacing.value != 0.0 do fnRandomKnotSpacing web idx spSubKnotSpacing.value --randomize the spacing of the knots on each spline
	)
	
	fn fnSplineLengthCheck pt1 pt2 = (
		dMin = spCutoffMin.value
		dMax = spCutoffMax.value
		
		pathLength = distance pt1 pt2
		if pathLength <= dMin OR pathLength >= dMax then return false else return true
	)
	
	fn fnAverageCenter arr = (
		local autoCenter = [0,0,0]
		local count = arr.count
		
		if arr.count >= 1 then (
			for itm in arr do autoCenter += itm.pos
			autoCenter /= count
			return autoCenter
		)else(
			return [0,0,0]
		)
	)
		
	fn shuffleIndexes count = --unique Random order
	(
		list = #() 	
		list.count = count
		for k = 1 to count do 
		(
			i = random 1 k
			list[k] = list[i]
			list[i] = k
		)
		return list
	)
	
	fn fnRandomGaps web: =
	(
		orginalTotal = numSplines web
		killRange = [(mainStrandCount+1),orginalTotal]	
		subStrandNum = killRange[2] - killRange[1]
		killCount = ceil((spRandGaps.value * .01)*subStrandNum)
		minLimit = orginalTotal - killCount
		
		while orginalTotal > minLimit do
		( 
			_mixedOrder = for s in (shuffleIndexes (numSplines web)) where s > mainStrandCount collect s   -- mix all the spline idx up & only collect spline idx higher than the number of main strands
			deleteSpline web _mixedOrder[1]
			orginalTotal = numSplines web
		)
	)
	
	fn fnCreateSubStrands web: = (
		--collect points
		if cbIncludeEnds.state then range = [1,(numknots web 1)] else range = [2,(numknots web 1)-1] --Step 4:Include the original position points of the main strands if chosen 
		_webPtsArr = #()
			
		for k in range[1] to range[2] do
		(
			for idx = 1 to (numSplines web) do 
			(
				theKnot = getKnotPoint web idx k
				append _webPtsArr theKnot
			)
		)
		
		_webPtsArr = if cbUniqueSub.state then makeUniqueArray _webPtsArr else _webPtsArr --make unique if checked
			
		--Ordering of pts
		sIdx = shuffleIndexes _webPtsArr.count --(returns arry)
		eIdx = shuffleIndexes _webPtsArr.count --(returns arry)
		
		--OPTIONS SPLINE CREATION
		if dlSubFormat.selection == 1 do ( --RANDOM						
			o = 1 --used to count number of loops so we can have a more substrands than main strands
			for i = 1 to spnSubNum.value do
			(
				ptA = _webPtsArr[sIdx[o]]
				ptB = _webPtsArr[eIdx[o]]
				
				if cbDCOSub.state then (
					if fnSplineLengthCheck ptA ptB do fnCreateSubs ptA ptB web:web--length checker tests true then create main strand
				)else(
					fnCreateSubs ptA ptB web:web--length checker tests true then create main strand
				)
					
				o += 1
				if o >= _webPtsArr.count do --shuffle and reloop
				(
					o = 1
					sIdx = shuffleIndexes _webPtsArr.count --(returns arry)
					eIdx = shuffleIndexes _webPtsArr.count --(returns arry)
				)
			)
		)
		
		if dlSubFormat.selection == 2 OR dlSubFormat.selection == 3 do ( --RADIAL or SPIRAL
			if spnSubNum.value >= 1 do
			(				
				_RadSplineOrder = fnRadialSort web
				
				--Collect knots based on _RadSplineOrder and from first knot to last
				if cbIncludeEnds.state then range = [1,(numknots web 1)] else range = [2,(numknots web 1)-1] --Step 4:Include the original position points of the main strands if chosen 
				
				for o in range[1] to range[2] do --number of rings
				(
					for r = 1 to _RadSplineOrder.count do -- connect to each subspline to make a loop
					(
						sIdx = _RadSplineOrder[r]
						eIdx = _RadSplineOrder[r+1]
						
						--calculations for RADIAL or SPIRAL
						if dlSubFormat.selection == 2 then (
							next = o
						)else(
							next = if o >= range[2] then o else (o+1)
						)
						
						ptA = getKnotPoint web sIdx o
						ptB = if r >= (_RadSplineOrder.count) then (getKnotPoint web (_RadSplineOrder[1]) next) else (getKnotPoint web eIdx o) --if it is the last knot in the ring the link it back to the first one to make a compelte ring
						
						if cbDCOSub.state then (
							if fnSplineLengthCheck ptA ptB do fnCreateSubs ptA ptB web:web--length checker tests true then create main strand
						)else(
							fnCreateSubs ptA ptB web:web--length checker tests true then create main strand
						)
					)
				)
			)
		)
		
		if dlSubFormat.selection == 4 do ( --TARGET
			--collect target points
			if subTrgObj != undefined and isValidNode subTrgObj then
			(
				if superclassof subTrgObj != GeometryClass then 
				(
					_subTrgPtsArr = #(subTrgObj.pos)
				)else(
					fnPFPoints #(subTrgObj) amount:(spnSubNum.value) location:3 -- create pf system and collect all the point 3 values on surface
					_subTrgPtsArr = copy _genPFPts #nomap
				)
			)else(_subTrgPtsArr = #([0,0,0]))
				
			o = 1 --used to count number of loops so we can have a more substrands than main strands
			for i = 1 to spnSubNum.value do
			(
				ptA = _webPtsArr[sIdx[o]]
				ptB = _subTrgPtsArr[random 1 _subTrgPtsArr.count]
				
				if cbDCOSub.state then (
					if fnSplineLengthCheck ptA ptB do fnCreateSubs ptA ptB web:web--length checker tests true then create main strand
				)else(
					fnCreateSubs ptA ptB web:web--length checker tests true then create main strand
				)
					
				o += 1
				if o >= _webPtsArr.count do --shuffle and reloop
				(
					o = 1
					sIdx = shuffleIndexes _webPtsArr.count --(returns arry)
					eIdx = shuffleIndexes _webPtsArr.count --(returns arry)
				)
			)	
		)
		if spRandGaps.value != 0.0 do fnRandomGaps web:web
	)
	
	fn fnCreateMainStrands web: = (
		_genPFPts = #() --reset
		_genPtsMain = #()
		_thePts = #()
		_trgPtsArr = #()
		
		--COLLECTING points
		for obj in refObjs do (
			fnPFPoints #(obj) amount:(spnMainNum.value) location:(dlMainLocation.selection - 1) -- step 1: create pf system and collect all the point 3 values from the particles
			_tmpArr = copy _genPFPts #nomap
			_tmpArr = if cbUniqueMain.state then makeUniqueArray _tmpArr else _tmpArr --make unique if checked
			append _genPtsMain _tmpArr
		)
		for p = 1 to _genPtsMain.count do for itm in _genPtsMain[p] do append _thePts itm --put all sub arrays into one master array
		
		--Ordering of pts
		sIdx = shuffleIndexes _thePts.count --(returns arry)
		eIdx = shuffleIndexes _thePts.count --(returns arry)
		
		loop = if _thePts.count < spnMainNum.value then _thePts.count else spnMainNum.value --corrects error: make unique results in "lower number of points" then "Amount"
			
		--OPTIONS SPLINE CREATION
		if dlMainFormat.selection == 1 do ( --RANDOM			
			for i = 1 to loop do
			(
				ptA = _thePts[sIdx[i]]
				ptB = _thePts[eIdx[i]]
						
				if cbDCOMain.state then (
					if fnSplineLengthCheck ptA ptB do fnCreateMains idx ptA ptB web:web--length checker tests true then create main strand
				)else(
					fnCreateMains idx ptA ptB web:web--length checker tests true then create main strand
				)
			)			
		)
		if dlMainFormat.selection == 2 do ( --CENTER
			cPt = fnAverageCenter refObjs
			for i = 1 to loop do
			(
				ptA = _thePts[sIdx[i]]
				ptB = cPt
						
				if cbDCOMain.state then (
					if fnSplineLengthCheck ptA ptB do fnCreateMains idx ptA ptB web:web--length checker tests true then create main strand
				)else(
					fnCreateMains idx ptA ptB web:web--length checker tests true then create main strand
				)
			)
		)
		if dlMainFormat.selection == 3 do ( --ORDER
			if refObjs.count >= 2 do (
				sector = 1
				for i = 1 to loop do
				(
					if cbLoopOrder.state then (
						--Point A start
						subGrpA = sector -- choose a starting sub group
						grpA = _genPtsMain[subGrpA] -- the subgroup array
						sIdx = shuffleIndexes grpA.count -- after choosing sub group then come up with a unique random order (returns arry)				
						ptA = grpA[sIdx[1]] -- dont bother using "i" here since the above line of code randomly shuffles every look changing the pt3 being used
						--Point B end
						subGrpB = if subGrpA == _genPtsMain.count then 1 else subGrpA + 1 --loop back around to start
						grpB = _genPtsMain[subGrpB] -- the subgroup array
						eIdx = shuffleIndexes grpB.count -- after choosing sub group then come up with a unique random order (returns arry)				
						ptB = grpB[eIdx[1]]
						
						if sector >= _genPtsMain.count then sector = 1 else sector += 1
					)else(
						--Point A start
						subGrpA = sector -- choose a random sub group
						grpA = _genPtsMain[subGrpA] -- the subgroup array
						sIdx = shuffleIndexes grpA.count -- after choosing sub group then come up with a unique random order (returns arry)				
						ptA = grpA[sIdx[1]]
						--Point B end
						subGrpB = subGrpA + 1
						grpB = _genPtsMain[subGrpB] -- the subgroup array
						eIdx = shuffleIndexes grpB.count -- after choosing sub group then come up with a unique random order (returns arry)				
						ptB = grpB[eIdx[1]]
						
						if sector >= (_genPtsMain.count - 1) then sector = 1 else sector += 1
					)
						
					if cbDCOMain.state then (
						if fnSplineLengthCheck ptA ptB do fnCreateMains idx ptA ptB web:web--length checker tests true then create main strand
					)else(
						fnCreateMains idx ptA ptB web:web--length checker tests true then create main strand
					)
				)
			)
		)
		if dlMainFormat.selection == 4 do ( --SURFACE FOLLOW
			fnSurfaceFollow surfaceObjs:refObjs
			
			for i = 1 to _particleMaps.count do
			(
				idx = addnewSpline web
				for o = 1 to _particleMaps[i].count do
				(
					sector = _particleMaps[i]
					addKnot web idx #smooth #curve sector[o]
				)
			)
		)
		
		if dlMainFormat.selection == 5 do ( --TARGET
			if trgObj != undefined and isValidNode trgObj then
			(
				if superclassof trgObj != GeometryClass then 
				(
					_trgPtsArr = #(trgObj.pos)
				)else(
					fnPFPoints #(trgObj) amount:(spnMainNum.value) location:3 -- create pf system and collect all the point 3 values on surface
					_trgPtsArr = copy _genPFPts #nomap
				)
			)else(_trgPtsArr = #([0,0,0]))
			
			for i = 1 to loop do
			(
				ptA = _thePts[sIdx[i]]
				ptB = _trgPtsArr[random 1 _trgPtsArr.count]
						
				if cbDCOMain.state then (
					if fnSplineLengthCheck ptA ptB do fnCreateMains idx ptA ptB web:web--length checker tests true then create main strand
				)else(
					fnCreateMains idx ptA ptB web:web--length checker tests true then create main strand
				)
			)
		)
		mainStrandCount = numSplines web
	)
	
	fn fnCreateCobwebs = (
		refObjs = for obj in selection where superclassof obj == GeometryClass collect obj --objects that will have cobwebs created on them
		
		if refObjs.count >= 1 do
		(			
			theWeb = splineShape name:(uniqueName "Cobweb_") render_displayRenderMesh:false optimize:false wirecolor:yellow--our web shape
			clearlistener()
			fnCreateMainStrands web:theWeb --step 1: Create Main Strands
			if numSplines theWeb >= 1 do fnCreateSubStrands web:theWeb --step 1: Create Sub Strands
			updateShape theWeb
			select theWeb
		)
	)
	
	
	--//BUTTON ACTIONS
	on pbSubTrgObject picked obj do
	(
		if obj != undefined then
		(
			subTrgObj = obj
			pbSubTrgObject.text = obj.name
		)else(
			subTrgObj = undefined
			pbSubTrgObject.text = "PICK OBJECT"
		)
	)		
	
	
	on pbTrgObject picked obj do
	(
		if obj != undefined then
		(
			trgObj = obj
			pbTrgObject.text = obj.name
		)else(
			trgObj = undefined
			pbTrgObject.text = "PICK OBJECT"
		)
	)
	
	on btnCreateCobwebs pressed do
	(
		fnCreateCobwebs()
	)	
)
createDialog rlCobwebs 290 560 style:#(#style_SysMenu, #style_ToolWindow)