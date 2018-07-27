--JokerMartini@hotmail.com
--JokerMartini.com
--Instructions
	--EdgeWelds 
	--Intersecting Welds - first object in the selection is the master object. all over objects in the selection are cut into the master object resulting in making welds.
	--Add dent map
	--Checkmap blurred
	
try(destroyDialog ::rlWelder)catch()
rollout rlWelder "Welder"
(	
	groupbox gpSettings "Weld Settings" pos:[10,8] width:180 height:124
	label lbThickness "Thickness:" pos:[19,26]
	spinner spThickness "" fieldwidth:55 range:[0,999999999,2.5] type:#worldUnits pos:[112,26]
	label lbSides "Side Segments:" pos:[19,46]
	spinner spSides "" fieldwidth:55 range:[3,999999999,10] type:#integer pos:[112,46]
	label lbAngle "Angle:" pos:[19,66] visible:true
	spinner spSplineAngle fieldwidth:55 range:[-999999999.9,999999999.9,0.0] type:#float pos:[112,66] visible:true
	label lbSharpCorners "Sharp Corners:" pos:[19,86]
	label lbSharp1 "1:" pos:[115,86]
	checkbox cbSharpCorners1 "" width:19 pos:[130,86] checked:true
	label lbSharp2 "2:" pos:[150,86]
	checkbox cbSharpCorners2 "" width:19 pos:[165,86] checked:false
	label lbPresets "Presets:" pos:[19,106] visible:true
	button btnFlatPreset "Flat" height:16 width:32 pos:[115,106] visible:true
	button btnConvexPreset "CX" height:16 width:32 pos:[147,106] visible:true
	
	groupbox gpWeldBumpType "Weld Bump Type" pos:[10,136] width:180 height:42
	radiobuttons rbWeldBumpType labels:#("Noise", "Cellular", "None") columns:3 pos:[19,156] default:2
	groupbox gpWeldBumpSettings "" pos:[10,171] width:180 height:182
	label lbNoiseScale "Noise Scale:" pos:[19,186] visible:false
	spinner spNoiseScale "" fieldwidth:55 range:[0.0,999999999.9,15.0] type:#float pos:[112,186] visible:false
	label lbNoiseStrength "Noise Strength:" pos:[19,206] visible:false
	spinner spXNoiseStrength "X:" fieldwidth:55 range:[-999999999.9,999999999.9,0.5] type:#worldUnits pos:[102,206] visible:false
	spinner spYNoiseStrength "Y:" fieldwidth:55 range:[-999999999.9,999999999.9,1.0] type:#worldUnits pos:[102,226] visible:false
	spinner spZNoiseStrength "Z:" fieldwidth:55 range:[-999999999.9,999999999.9,0.5] type:#worldUnits pos:[102,246] visible:false
	label lbDisplaceStrength "Strength:" pos:[19,186] visible:true
	spinner spDisplaceStrength "" fieldwidth:55 range:[-999999999.9,999999999.9,1.0] type:#worldUnits pos:[112,186] visible:true
	label lbCellularSize "Size:" pos:[19,206] visible:true
	spinner spCellularSize "" fieldwidth:55 range:[0.0001,999999999.9,4.0] type:#float pos:[112,206] visible:true
	label lbCellularSpread "Spread:" pos:[19,226] visible:true
	spinner spCellularSpread "" fieldwidth:55 range:[0.0001,999999999,0.2] type:#float pos:[112,226] visible:true
	label lbCellularIterations "Iterations:" pos:[19,246] visible:true
	spinner spCellularIterations "" fieldwidth:55 range:[1.0,999999999,1.0] type:#float pos:[112,246] visible:true
	label lbCellularFractal "Fractal:" pos:[19,266] visible:true
	checkbox cbCellularFractal "" width:19 pos:[165,266] checked:true
	label lbCellularThresholds "Thresholds:" pos:[19,286] visible:true
	spinner spLowCellularThresholds "Low:" fieldwidth:55 range:[0.0,1.0,0.0] type:#float pos:[89,286] visible:true
	spinner spMidCellularThresholds "Mid:" fieldwidth:55 range:[0.0,1.0,0.5] type:#float pos:[92,306] visible:true
	spinner spHighCellularThresholds "High:" fieldwidth:55 range:[0.0,1.0,1.0] type:#float pos:[87,326] visible:true
	button btnEdgeWelds "Edge Welds" width:70 height:24 pos:[10,356] tooltip:"Creates a weld along the selected edge."
	button btnIntersectingWelds "Intersecting Welds" width:110 height:24 pos:[80,356] tooltip:"Creates a welds along the interesecting edges."
	
	
	
	--//Functions
	---------------------------------------------------------------
	fn fnCheckSelection = (--//Makes sure all objects selected are that of the Geometry Class or Shape Class
		for obj in selection do 
		(
			if (superClassOf obj != GeometryClass and superClassOf obj != Shape)
			do return false
		)
		return true
	)

	fn getSubArray sourceArray index forward =	(--//Breaks up array as needed
		tmpArray = #()
		-- Assign variables assuming forward
		start_idx = index
		end_idx = sourceArray.count
		-- Not forward, we want front portion of the array
		if forward != True then
		(
			start_idx = 1
			end_idx = index
		)
		-- Loop array appending items to temp array
		for i = start_idx to end_idx do
		(
			append tmpArray sourceArray[i]
		)
		return tmpArray
	)
	
	fn fnEdgesToSpline obj = (--//Converts edge selection to spline
		obj.EditablePoly.createShape "weld7Unique" off obj
		theWeld = (getNodeByName "weld7Unique")
		theWeld.wirecolor = red
		theWeld.baseObject.render_renderable = true
		theWeld.baseObject.render_displayRenderMesh = true
		theWeld.baseObject.render_mapcoords = true
		theWeld.baseObject.render_thickness = spThickness.value
		theWeld.baseObject.render_sides = spSides.value
		theWeld.name = (uniqueName "Weld_")
		case rbWeldBumpType.state of
		(
			1:(
				addModifier theWeld (Turbosmooth sepBySmGroups:cbSharpCorners1.state)
				addModifier theWeld (Noisemodifier seed:1 scale:spNoiseScale.value fractal:true roughness:1 strength:[spXNoiseStrength.value,spYNoiseStrength.value,spZNoiseStrength.value])
				addModifier theWeld (Turbosmooth sepBySmGroups:cbSharpCorners2.state)
			)
			2:(
				addModifier theWeld (Turbosmooth sepBySmGroups:cbSharpCorners1.state)
				addModifier theWeld (Displace map:(cellular size:spCellularSize.value spread:spCellularSpread.value iteration:spCellularIterations.value fractal:cbCellularFractal.state lowThresh:spLowCellularThresholds.value midThresh:spMidCellularThresholds.value highThresh:spHighCellularThresholds.value) strength:spDisplaceStrength.value lumCenterEnable:true useMap:true)
				addModifier theWeld (Turbosmooth sepBySmGroups:cbSharpCorners2.state)
			)
			3:(
				--addModifier theWeld (Turbosmooth sepBySmGroups:cbSharpCorners2.state)
			)
		)
		select theWeld
	)
	
	fn fnIntersectingWelds = (--//Creates weld for interesecting geometry
		--//Locals
		local weldObjArr = #()
		local tmpWeldObj = undefined
		
		for obj in selection do (appendIfUnique weldObjArr (convertToPoly (snapshot obj)))
		ProBoolean.createBooleanObjects weldObjArr[1] (getSubArray weldObjArr 2 true) 2 1 0
		ProBoolean.SetMakeQuad weldObjArr[1] true
		tmpWeldObj = convertToPoly weldObjArr[1]
		fnEdgesToSpline tmpWeldObj
		delete tmpWeldObj			
	)
		
	fn fnDisplaceMapChange prop val =	(
		undo on (
			for i = 1 to selection.count do
			(
				Obj = selection[i]
				for m in Obj.modifiers where (classOf m == Displace) and (classof m.map == Cellular) do
				setproperty m.map prop val
			)
		)
	)
	
	fn fnModifierChange mody prop val = (
		undo on (
			for i = 1 to selection.count do
			(
				Obj = selection[i]
				for m in Obj.modifiers where (classOf m == mody) do
				setproperty m prop val
			)
		)
	)
	
	fn fnNoiseModChange val dir:#x = (
		undo on (
			for i = 1 to selection.count do
			(
				Obj = selection[i]
				for m in Obj.modifiers where (classOf m == Noisemodifier) do
				case dir of 
				(
					#x: m.strength.x = val
					#y: m.strength.y = val
					#z: m.strength.z = val
				)
			)
		)	
	)
	
	fn fnTurboSmoothSharpCorners dir state = (
		undo on (
			for i = 1 to selection.count do
			(
				Obj = selection[i]
				ts = for m in Obj.modifiers where (classOf m == turbosmooth) collect m
				if ts.count >= dir do ts[dir].sepBySmGroups = state -- top of the stack turbosmooth
			)
		)
	)
	
	fn fnSplineAdjustments prop val = (
		undo on (
			tempArr = for obj in selection where classof obj.baseobject == SplineShape collect obj
			for obj in tempArr do setproperty obj prop val
		)
	)
	--//Button Actions
	---------------------------------------------------------------	
	on rbWeldBumpType changed state do (
		case state of (
			1: (
					lbNoiseScale.visible = spNoiseScale.visible = lbNoiseStrength.visible = spXNoiseStrength.visible = spYNoiseStrength.visible = spZNoiseStrength.visible = true
					lbCellularSize.visible = spCellularSize.visible = lbCellularSpread.visible = spCellularSpread.visible = lbCellularIterations.visible = spCellularIterations.visible = lbDisplaceStrength.visible = spDisplaceStrength.visible = lbCellularFractal.visible = cbCellularFractal.visible = spLowCellularThresholds.visible = spMidCellularThresholds.visible = spHighCellularThresholds.visible = lbCellularThresholds.visible = false
				)
			2: (
					lbNoiseScale.visible = spNoiseScale.visible = lbNoiseStrength.visible = spXNoiseStrength.visible = spYNoiseStrength.visible = spZNoiseStrength.visible = false
					lbCellularSize.visible = spCellularSize.visible = lbCellularSpread.visible = spCellularSpread.visible = lbCellularIterations.visible = spCellularIterations.visible = lbDisplaceStrength.visible = spDisplaceStrength.visible = lbCellularFractal.visible = cbCellularFractal.visible = spLowCellularThresholds.visible = spMidCellularThresholds.visible = spHighCellularThresholds.visible = lbCellularThresholds.visible = true
				)
			3: (
					lbNoiseScale.visible = spNoiseScale.visible = lbNoiseStrength.visible = spXNoiseStrength.visible = spYNoiseStrength.visible = spZNoiseStrength.visible = lbCellularSize.visible = spCellularSize.visible = lbCellularSpread.visible = spCellularSpread.visible = lbCellularIterations.visible = spCellularIterations.visible = lbDisplaceStrength.visible = spDisplaceStrength.visible = lbCellularFractal.visible = cbCellularFractal.visible = spLowCellularThresholds.visible = spMidCellularThresholds.visible = spHighCellularThresholds.visible = lbCellularThresholds.visible = false
				)
		)
	)
	
	on btnEdgeWelds pressed do (
		if selection.count == 1 and superclassof selection[1] == GeometryClass then
		(
			setCommandPanelTaskMode #create 
			disableSceneRedraw()
			if classof selection[1] != Editable_Poly then 
			(
				tmpWeldObj = convertToPoly (snapshot selection[1])
				try(fnEdgesToSpline tmpWeldObj)catch()
				delete tmpWeldObj
			)else(
				try(fnEdgesToSpline selection[1])catch()
			)
			enableSceneRedraw()
			redrawViews()	
		)
		else messagebox "Make sure that only one Geometry Object is selected."
	)

	on btnIntersectingWelds pressed do (
		if fnCheckSelection() and selection.count >= 2 then 
		(
			setCommandPanelTaskMode #create 
			disableSceneRedraw()
			try(fnIntersectingWelds())catch()
			enableSceneRedraw()
			redrawViews()	
		)
		else messagebox "Make sure that only Geometry or Shape Objects are selected."
	)
	
	--//Fine Tuning
	on spCellularSize changed val do fnDisplaceMapChange #size val
	on spCellularSpread changed val do fnDisplaceMapChange #spread val
	on spCellularIterations changed val do fnDisplaceMapChange #iteration val
	on cbCellularFractal changed state do fnDisplaceMapChange #fractal state
	on spLowCellularThresholds changed val do fnDisplaceMapChange #lowThresh val
	on spMidCellularThresholds changed val do fnDisplaceMapChange #midThresh val
	on spHighCellularThresholds changed val do fnDisplaceMapChange #highThresh val
	on spDisplaceStrength changed val do fnModifierChange Displace #strength val
	on spNoiseScale changed val do fnModifierChange Noisemodifier #scale val
	on spXNoiseStrength changed val do fnNoiseModChange val dir:#x
	on spYNoiseStrength changed val do fnNoiseModChange val dir:#y
	on spZNoiseStrength changed val do fnNoiseModChange val dir:#z
	on cbSharpCorners1 changed state do fnTurboSmoothSharpCorners 2 state
	on cbSharpCorners2 changed state do fnTurboSmoothSharpCorners 1 state
	on spThickness changed val do fnSplineAdjustments #thickness val
	on spSides changed val do fnSplineAdjustments #sides val
	on spSplineAngle changed val do fnSplineAdjustments #angle val
	on btnFlatPreset pressed do (
		spSplineAngle.value = -15.0
		spSides.value = 3
		cbSharpCorners1.checked = true
		cbSharpCorners2.checked = false
	)
	on btnConvexPreset pressed do (
		spSplineAngle.value = 0.0
		spSides.value = 10
		cbSharpCorners1.checked = true
		cbSharpCorners2.checked = true
	)
	
	
)
createDialog rlWelder 200 390 --358