--//-----------------------------------------------------------------------------
--// Ingenuity.mcr
--// macroScripts File
--// By Grant Miller (blented@gmail.com)
--// Created On: 02/29/08
--// Modified On: 06/30/08
--// tested using Max 2008
--//-----------------------------------------------------------------------------

--//seperate files for more macroscripts
fileIn (MAX_TOOLS_ROOT + "macroscripts/commonTasks.ms")
fileIn (MAX_TOOLS_ROOT + "macroscripts/modeling.ms")
fileIn (MAX_TOOLS_ROOT + "macroscripts/modifiers.ms")
fileIn (MAX_TOOLS_ROOT + "macroscripts/tools.ms")

--//hide or show errors
hideErrors = true

--//-----------------------------------------------------------------------------
--// Tons of macroscripts for tools
--//-----------------------------------------------------------------------------
(
macroScript IFKChain category:"Ingenuity" tooltip:"IFK Chain" silentErrors:hideErrors
(
	on isEnabled return selection.count == 1 or
						selection.count > 1 and
						(
							local h = selection[1].parent
							h != undefined and h.isSelected and isGroupHead h
						)

	on execute do
	(
		Global EC_OBJ, EC_TargetObj
		EC_OBJ = selection[1]

		-------------------------------------------------------------------------------------------
		-- Define Filter Function for PickObject Selection
		-------------------------------------------------------------------------------------------

		fn ChildFilt o = Filters.Is_Child EC_OBJ o or Filters.Is_Parent EC_OBJ o

		-------------------------------------------------------------------------------------------

		Animate off
		(
			EC_TargetOBJ = PickObject count:1 select:false filter:ChildFilt Message:"Select the final bone" count:#Multiple Rubberband:EC_OBJ.pos ForceListenerFocus:False

			If EC_TargetOBJ != #escape and EC_TargetOBJ != undefined then
			(
				root = undefined
				tip = undefined
				if Filters.Is_Child EC_OBJ EC_TargetOBJ then
				(
					root = EC_OBJ
					tip = EC_TargetOBJ
				)
				Else
				(
					tip = EC_OBJ
					root = EC_TargetOBJ
				)

				-- Shorten the chain - we only want the 1st 2 bones
				while (tip.parentNode != root) do ( tip = tip.parentNode )

				-- Setup the IK target
				ikTarg = Point()
				ikTargCtrl = CtrlIKTarget()
				ikTarg.controller = ikTargCtrl
				ikTargCtrl.RootNode = root
				ikTargCtrl.TipNode = tip

				-- The above is all that is necessary for an FK chain

				ikWeight = Bezier_Float()
				ikTargCtrl.IKTargetWeight.controller = ikWeight

				-- For full IFK, setup the controllers on the 2 bones as well.
				root.controller = IFK_Root()
				root.controller.TipNode = tip
				root.controller.IKTarget = ikTarg
				root.controller.IKTargetWeight.controller = ikWeight

				tip.controller = IFK_Tip()
				tip.controller.IKTarget = ikTarg
				tip.controller.IKTargetWeight.controller = ikWeight
			)

			Max Motion Mode
		)
	)
)


macroScript hairFromFibermesh category:"Ingenuity" tooltip:"Hair from Fibermesh" Icon:#("Ingenuity",1) silentErrors:hideErrors
(
	for obj in getCurrentSelection() do
	(
		subobjectLevel = 0
		convertTo obj PolyMeshObject
		subobjectLevel = 2
		max select all
		obj.setRingShift -40 true false
		obj.EditablePoly.createShape (obj.name + "_hair") on obj
	)
)

macroScript IERun category:"Ingenuity" tooltip:"IERun" Icon:#("Ingenuity",1) silentErrors:hideErrors
(
	-- fileIn (MAX_TOOLS_ROOT + "scripts/IERun.ms")
	python.execute("import sys; sys.path.append('c:/ie/ark/programs/max/startup/'); import initMax; print initMax.launchMenu()")
)
macroScript ReferenceManager category:"Ingenuity" tooltip:"ReferenceManager" Icon:#("BodyObjects",3) silentErrors:hideErrors
(
	fileIn (MAX_TOOLS_ROOT + "scripts/Studio/ReferenceManager.ms")
)
macroScript SubmitJob category:"Ingenuity" tooltip:"SubmitJob" Icon:#("Ingenuity",12) silentErrors:hideErrors
(
	print "Launching Shepherd Submit"
	python.ExecuteFile (ARK_ROOT + "../shepherd/shepherd/submit/ShepherdSubmit.py")
	-- fileIn (MAX_TOOLS_ROOT + "scripts/Studio/SubmitToShepherd.ms")
)

macroScript SceneRescale category:"Ingenuity" tooltip:"SceneRescale" Icon:#("Ingenuity",2) silentErrors:hideErrors
	(
		fileIn (MAX_TOOLS_ROOT + "scripts/Utilities/SceneRescale.ms")
	)
macroScript TurnRender category:"Ingenuity" tooltip:"TurnRender" Icon:#("Ingenuity",3) silentErrors:hideErrors
	(
		fileIn (MAX_TOOLS_ROOT + "scripts/Utilities/TurnRender.ms")
	)
--// macroScript ExportTools category:"Ingenuity" tooltip:"ExportTools" Icon:#("Ingenuity",4) silentErrors:hideErrors
--//   (
--//     fileIn (MAX_TOOLS_ROOT + "scripts/ExportTools.ms")
--//   )
macroScript AnimationStopwatch category:"Ingenuity" tooltip:"AnimationStopwatch" Icon:#("Ingenuity",5) silentErrors:hideErrors
	(
		fileIn (MAX_TOOLS_ROOT + "scripts/Animation/AnimationStopwatch.ms")
	)
macroScript ResetAllViews category:"Ingenuity" tooltip:"ResetAllViews" silentErrors:hideErrors
	(
		viewport.ResetAllViews()
		completeRedraw()
	)
macroScript PivotToCenter category:"Ingenuity" tooltip:"PivotToCenter" Icon:#("Ingenuity",6) silentErrors:hideErrors
	(
		userSel = getCurrentSelection()
		undo "Pivot To Center" on
		(
			for i in userSel do ieMaxPivotToCenter i
		)
	)
macroScript PivotToObjCenter category:"Ingenuity" tooltip:"PivotToObjCenter" Icon:#("Ingenuity",7) silentErrors:hideErrors
	(
		userSel = getCurrentSelection()
		undo "Pivot To Obj Center" on
		(
			if (userSel.count > 0) then
			(
				targetObject = pickObject message:"Select the object whose center you wish to align the selection's pivot to." \
												rubberBand:(ieMaxCalcBBCenter $) rubberBandColor:white select:false
				if (targetObject != undefined) then ieMaxPivotToObjCenter userSel targetObject
			)
		)
	)
macroScript PivotToObjPivot category:"Ingenuity" tooltip:"PivotToObjPivot" Icon:#("Ingenuity",8) silentErrors:hideErrors
	(
		userSel = getCurrentSelection()
		undo "Pivot To Obj Pivot" on
		(
			if (userSel.count > 0) then
			(
				targetObject = pickObject message:"Select the object whose pivot you wish to align the selection's pivot to." \
												rubberBand:(ieMaxCalcBBCenter $) rubberBandColor:white select:false
				if (targetObject != undefined) then ieMaxPivotToObjPivot userSel targetObject
			)
		)
	)
macroScript AnimationStopwatch category:"Ingenuity" tooltip:"RiggingTools" Icon:#("Ingenuity",9) silentErrors:hideErrors
	(
		fileIn (MAX_TOOLS_ROOT + "scripts/Rigging/RiggingTools.ms")
	)
--// macroScript TileTools category:"Ingenuity" tooltip:"TileTools" Icon:#("Ingenuity",10)
--//   (
--//     fileIn (MAX_TOOLS_ROOT + "scripts/TileTools.ms")
--//   )
macroScript UVWelementSelect category:"Ingenuity" tooltip:"UVW Element Select" buttonText:"UVW Elm Sel" silentErrors:hideErrors
	(
		userSel = getCurrentSelection()
		max modify mode
		for i in userSel do
		(
			modIndex = ieMaxGetModifier i Unwrap_UVW
			if (modIndex != undefined) then
			(
				state = i.modifiers[modIndex].getTVElementMode()
				i.modifiers[modIndex].setTVElementMode (not state)
			)
		)
	)
macroScript UVWrotate180 category:"Ingenuity" tooltip:"UVW Rotate 180" buttonText:"UVW Rt 180" silentErrors:hideErrors
	(
		userSel = getCurrentSelection()
		max modify mode
		for i in userSel do
		(
			modIndex = ieMaxGetModifier i Unwrap_UVW
			if (modIndex != undefined) then
			(
				i.modifiers[modIndex].unwrap.mirrorh ()
				i.modifiers[modIndex].unwrap.mirrorv ()
			)
		)
	)
macroScript UVWsoftSelection category:"Ingenuity" tooltip:"UVW Soft Selection" buttonText:"UVW Sf Sel" silentErrors:hideErrors
	(
		userSel = getCurrentSelection()
		max modify mode
		for i in userSel do
		(
			modIndex = ieMaxGetModifier i Unwrap_UVW
			if (modIndex != undefined) then
			(
				state = i.modifiers[modIndex].getEnableSoftSelection()
				i.modifiers[modIndex].setEnableSoftSelection (not state)
			)
		)
	)
)
macroScript ToggleSilhouette category:"Ingenuity" tooltip:"Toggle Silhouette" buttonText:"Tgl Silo" silentErrors:hideErrors
	(
		userSel = getCurrentSelection()
		if (viewport.GetRenderLevel() != #flat) then
		(
			viewport.setRenderLevel #flat
			displayColor.wireframe = #object
			displayColor.shaded = #object
			if (userSel.count > 0) then
				$.wirecolor = (color 0 0 0)
		)
		else
		(
			viewport.setRenderLevel #smoothhighlights
			displayColor.wireframe = #object
			displayColor.shaded = #material
			if (userSel.count > 0) then
				$.wirecolor = (color 123 226 53)
		)
	)
macroScript ToggleMaterials category:"Ingenuity" tooltip:"Toggle Materials" buttonText:"Tgl Mats" silentErrors:hideErrors
	(
		if (displayColor.shaded == #object) then
		(
			displayColor.wireframe = #object
			displayColor.shaded = #material
		)
		else
		(
			displayColor.wireframe = #object
			displayColor.shaded = #object
		)
	)
macroScript RemoveMaterial category:"Ingenuity" tooltip:"Remove Material" buttonText:"Rem Mat" silentErrors:hideErrors
	(
		userSel = getCurrentSelection()
		if (userSel.count > 0) then
			if (queryBox "Remove material from selected objects?" title:"Remove Material") then
				$.material = undefined
	)

--//-----------------------------------------------------------------------------
--// Modeling Macros
--//-----------------------------------------------------------------------------
--//Make planar hotkeys
macroScript MakePlanarX category:"Ingenuity" tooltip:"Make Planar X" buttonText:"Plnr X" silentErrors:hideErrors
	(
		userSel = getCurrentSelection()
		if (classof (modPanel.getCurrentObject()) == Edit_Poly) then
		(
			for o in userSel do
			(
				o.modifiers["Edit Poly"].setOperation #MakePlanarInX
				o.modifiers[#Edit_Poly].Commit ()
			)
		)
		else if (classof (modPanel.getCurrentObject()) == Editable_Poly) then
		(
			for o in userSel do
				o.EditablePoly.MakePlanarIn #X
		)
	)
macroScript MakePlanarY category:"Ingenuity" tooltip:"Make Planar Y" buttonText:"Plnr Y" silentErrors:hideErrors
	(
		userSel = getCurrentSelection()
		if (classof (modPanel.getCurrentObject()) == Edit_Poly) then
		(
			for o in userSel do
			(
				o.modifiers["Edit Poly"].setOperation #MakePlanarInY
				o.modifiers[#Edit_Poly].Commit ()
			)
		)
		else if (classof (modPanel.getCurrentObject()) == Editable_Poly) then
		(
			for o in userSel do
				o.EditablePoly.MakePlanarIn #Y
		)
	)
macroScript MakePlanarZ category:"Ingenuity" tooltip:"Make Planar Z" buttonText:"Plnr Z" silentErrors:hideErrors
	(
		userSel = getCurrentSelection()
		if (classof (modPanel.getCurrentObject()) == Edit_Poly) then
		(
			for o in userSel do
			(
				o.modifiers["Edit Poly"].setOperation #MakePlanarInZ
				o.modifiers[#Edit_Poly].Commit ()
			)
		)
		else if (classof (modPanel.getCurrentObject()) == Editable_Poly) then
		(
			for o in userSel do
				o.EditablePoly.MakePlanarIn #Z
		)
	)
--//Toggles select by angle and ignore backfacing as well
macroScript SelectByAngleToggle category:"Ingenuity" tooltip:"Select by Angle Toggle" buttonText:"Sel Ang" silentErrors:hideErrors
(
	if (classof (modPanel.getCurrentObject()) == Edit_Poly) then
	(
		if (selection.count > 1) then
		(
			$[1].modifiers["Edit Poly"].selectByAngle = not $[1].modifiers["Edit Poly"].selectByAngle
			$[1].modifiers["Edit Poly"].ignoreBackfacing = not $[1].modifiers["Edit Poly"].ignoreBackfacing
		)
		else
		(
			$.modifiers["Edit Poly"].selectByAngle = not $.modifiers["Edit Poly"].selectByAngle
			$.modifiers["Edit Poly"].ignoreBackfacing = not $.modifiers["Edit Poly"].ignoreBackfacing
		)
	)
	else if (classof (modPanel.getCurrentObject()) == Editable_Poly) then (
		$.selectByAngle = not $.selectByAngle
		$.ignoreBackfacing = not $.ignoreBackfacing
	)
)

--//Sub-object selction scripts
macroScript ConvertToVertex category:"Ingenuity" tooltip:"Convert to SubObj 1" silentErrors:hideErrors
(
	undo "ConvertSelection" on
	(
		if (classof (modPanel.getCurrentObject()) == Edit_Poly) then
		(
			userSel = getCurrentSelection()
			for sel in userSel do
			(
				select sel
				$.modifiers["Edit Poly"].ConvertSelection #CurrentLevel #Vertex
			)
			select userSel
		)
		else if (classof (modPanel.getCurrentObject()) == Editable_Poly) then
		(
			$.EditablePoly.ConvertSelection #CurrentLevel #Vertex
		)
	)
	subobjectLevel = 1
)
macroScript ConvertToEdge category:"Ingenuity" tooltip:"Convert to SubObj 2" silentErrors:hideErrors
(
	undo "ConvertSelection" on
	(
		if (classof (modPanel.getCurrentObject()) == Edit_Poly) then
		(
			userSel = getCurrentSelection()
			for sel in userSel do
			(
				select sel
				$.modifiers["Edit Poly"].ConvertSelection #CurrentLevel #Edge
			)
			select userSel
		)
		else if (classof (modPanel.getCurrentObject()) == Editable_Poly) then
		(
			$.EditablePoly.ConvertSelection #CurrentLevel #Edge
		)
	)
	subobjectLevel = 2
)
macroScript ConvertToBorders category:"Ingenuity" tooltip:"Convert to SubObj 3" silentErrors:hideErrors
(
	undo "ConvertSelection" on
	(
		if (classof (modPanel.getCurrentObject()) == Edit_Poly) then
		(
			userSel = getCurrentSelection()
			for sel in userSel do
			(
				select sel
				$.modifiers["Edit Poly"].ConvertSelection #CurrentLevel #Border
			)
			select userSel
		)
		else if (classof (modPanel.getCurrentObject()) == Editable_Poly) then
		(
			$.EditablePoly.ConvertSelection #CurrentLevel #Border
		)
	)
	subobjectLevel = 3
)
macroScript ConvertToFace category:"Ingenuity" tooltip:"Convert to SubObj 4" silentErrors:hideErrors
(
	undo "ConvertSelection" on
	(
		if (classof (modPanel.getCurrentObject()) == Edit_Poly) then
		(
			userSel = getCurrentSelection()
			for sel in userSel do
			(
				select sel
				$.modifiers["Edit Poly"].ConvertSelection #CurrentLevel #Face
			)
			select userSel
		)
		else if (classof (modPanel.getCurrentObject()) == Editable_Poly) then
		(
			$.EditablePoly.ConvertSelection #CurrentLevel #Face
		)
	)
	subobjectLevel = 4
)
macroScript ConvertToElement category:"Ingenuity" tooltip:"Convert to SubObj 5" silentErrors:hideErrors
(
	undo "ConvertSelection" on
	(
		if (classof (modPanel.getCurrentObject()) == Edit_Poly) then
		(
			userSel = getCurrentSelection()
			for sel in userSel do
			(
				select sel
				$.modifiers["Edit Poly"].ConvertSelection #CurrentLevel #Element
			)
			select userSel
		)
		else if (classof (modPanel.getCurrentObject()) == Editable_Poly) then
		(
			$.EditablePoly.ConvertSelection #CurrentLevel #Element
		)
	)
	subobjectLevel = 5
)

--//Remove Top Modifier from stack
macroScript RemoveTopModifier category:"Ingenuity" tooltip:"Remove Top Modifier" silentErrors:hideErrors
(
	on isEnabled return ( selection.count>=1)
	on execute do
	(
		for node in getCurrentSelection() do
			if node.modifiers.count > 0 then
				deleteModifier node 1
	)
)
--//Go to the the bottom of the modifier stack
macroScript GotoBaseObj category:"Ingenuity" tooltip:"Goto Base Object" silentErrors:hideErrors
(
	on isEnabled return ( selection.count == 1 )
	on execute do
	(
		max modify mode
		modPanel.setCurrentObject $
		subObjectLevel = 0
	)
)
--//Go to object level 0
macroScript GotoObjectLevel category:"Ingenuity" tooltip:"Goto Object Level" silentErrors:hideErrors
(
	on isEnabled return ( selection.count==1 )
	on execute do
		subObjectLevel = 0
)
--//places and activates a grid and switches to the grid coordinate system
--//this version is placed on objects via ray intersection
macroScript gridPlace category:"Ingenuity" tooltip:"Grid Place" silentErrors:hideErrors
(
	on isEnabled return ( selection.count==1 )
	on execute do
	(
		global newGrid = grid length:50 width:50 grid:10
		global prevGrid = activeGrid

		fn objNormal msg ir obj faceNum shift ctrl alt =
		(
			if (msg == #freeMove) then
			(
				if (ir != undefined) then
				(
					newGrid.pos = ir.pos
					newGrid.dir = ir.dir
					if ctrl then in coordSys local (rotate newGrid (eulerangles 90 0 0))
					if shift then in coordSys local (rotate newGrid (eulerangles 0 90 0))
					return #continue
				)
				else
				(
					return #continue
				)
			)

			if (msg == #mouseAbort) then
			(
				delete newGrid
				Toolmode.coordsys #World
				activeGrid = prevGrid
				return #end
			)

			if (msg != #mousePoint) then
			(
				return #continue
			)
			else
			(
				activeGrid = newGrid
				return #end
			)
		)

		gP = mouseTrack on:$ trackCallBack:objNormal snap:#3d
		Toolmode.coordsys #Grid
	)
)
--//clear grids
macroScript ClearGrids category:"Ingenuity" tooltip:"Clear Grids" silentErrors:hideErrors
(
	delete (for s in $grid* collect s)
)
--//Cycles through the three transform centers
macroScript transformCycle category:"Ingenuity" tooltip:"Transform Center Cycle" silentErrors:hideErrors
(
	if (getCoordCenter() == #System) then toolmode.pivotCenter()
	else if (getCoordCenter() == #Local) then toolmode.selectionCenter()
	else toolmode.transformCenter()
)
macroScript EasyBake category:"Ingenuity" tooltip:"EasyBake" Icon:#("Ingenuity",11) silentErrors:hideErrors
(
	fileIn (MAX_TOOLS_ROOT + "scripts/Light and Shade/EasyBake.ms")
)

macroScript boneController category:"Ingenuity" tooltip:"Bone Controller" silentErrors:hideErrors
(
	splineThickness = .03
	userSel = getCurrentSelection()
	findCont = true
	bCont = undefined
	for b in userSel do
	(
		b.boneEnable = false
		findingCont = true
		while findingCont do
		(
			bCont = b.parent
			if bCont != undefined then
			(
				if superClassOf bCont == shape then
				(
					bCont.render_renderable = true
					bCont.render_displayRenderMesh = true
					bCont.thickness = splineThickness
					bCont.sides = 3
					convertTo b (Editable_Poly)
					b.name = bCont.name

					b.EditablePoly.attach bCont b
					findingCont = false
				)
				else
				(
					b.parent = bCont.parent
					delete bCont
				) --//controller if
			) --//undefined if
		) --//while findCont

		b.boneEnable = true
	) --//for loop
)

macroScript boneAlign category:"Ingenuity" tooltip:"Bone Align" silentErrors:hideErrors
(
	if maxops.pivotmode != #pivotonly then
		maxops.pivotmode = #pivotonly

	userSel = getCurrentSelection()
	for b in userSel do
	(
		b.boneEnable = false
	)
	max align
)

macroScript bonePosMatch category:"Ingenuity" tooltip:"Bone Pos Match" silentErrors:hideErrors
(
	engineObjs = getCurrentSelection()
	rigBuddy = #()
	for n = 1 to engineObjs.count do
	(
		for r in $* do
		(
			if (engineObjs[n].name + "01") == r.name then
			(
				rigBuddy[n] = r
			)
		)
	)

	for n = 1 to engineObjs.count do
	(
		if engineObjs[n].parent == undefined then
		(
			engineObjs[n].position = rigBuddy[n].position
		)
	)
	for n = 1 to engineObjs.count do
	(
		if engineObjs[n].parent != undefined then
			engineObjs[n].position = rigBuddy[n].position
	)
)
--//Toggle Preserve UVs
macroScript preserveUVToggle category:"Ingenuity" tooltip:"Preserve UV Toggle" silentErrors:hideErrors
(
	if (classof (modPanel.getCurrentObject()) == Edit_Poly) then
	(
		userSel = getCurrentSelection()
		if (userSel.count > 0) then
		(
			userSel[1].modifiers["Edit Poly"].preserveUVs = not userSel[1].modifiers["Edit Poly"].preserveUVs
		)
	)
	else if (classof (modPanel.getCurrentObject()) == Editable_Poly) then
	(
		userSel = getCurrentSelection()
		if (userSel.count > 0) then
		(
			userSel[1].preserveUVs = not userSel[1].preserveUVs
		)
	)
)
--//Align UVs V
macroScript alignUVsV category:"Ingenuity" tooltip:"UVW Align UVs V" silentErrors:hideErrors
(
	if (classof (modPanel.getCurrentObject()) == Unwrap_UVW) then
	(
			userSel = getCurrentSelection()
			userSel[1].modifiers[#unwrap_uvw].scaleSelectedCenter 0 2
	)
)
--//Align UVs U
macroScript alignUVsU category:"Ingenuity" tooltip:"UVW Align UVs U" silentErrors:hideErrors
(
	if (classof (modPanel.getCurrentObject()) == Unwrap_UVW) then
	(
	userSel = getCurrentSelection()
			userSel[1].modifiers[#unwrap_uvw].scaleSelectedCenter 0 1
	)
)
--//Relax
macroScript relax category:"Ingenuity" tooltip:"Relax" silentErrors:hideErrors
(
	if (classof (modPanel.getCurrentObject()) == Edit_Poly) then
	(
		userSel = getCurrentSelection()
		if (userSel.count > 0) then
		(
			userSel[1].modifiers["Edit Poly"].ButtonOp #Relax
		)
	)
	else if (classof (modPanel.getCurrentObject()) == Editable_Poly) then
	(
		$.EditablePoly.Relax ()
	)
)
macroScript growLoop category:"Ingenuity" tooltip:"Grow Loop" silentErrors:hideErrors
(
	if (classof (modPanel.getCurrentObject()) == Edit_Poly) then
	(
		userSel = getCurrentSelection()
		if (userSel.count > 0) then
		(
			userSel[1].modifiers["Edit Poly"].LoopSelect 1 false true
			userSel[1].modifiers["Edit Poly"].LoopSelect -1 false true
		)
	)
	else if (classof (modPanel.getCurrentObject()) == Editable_Poly) then
	(
		$.setLoopShift 1 false true
		$.setLoopShift -1 false true
	)
)
macroScript growRing category:"Ingenuity" tooltip:"Grow Ring" silentErrors:hideErrors
(
	if (classof (modPanel.getCurrentObject()) == Edit_Poly) then
	(
		userSel = getCurrentSelection()
		if (userSel.count > 0) then
		(
			userSel[1].modifiers["Edit Poly"].RingSelect 1 false true
			userSel[1].modifiers["Edit Poly"].RingSelect -1 false true
		)
	)
	else if (classof (modPanel.getCurrentObject()) == Editable_Poly) then
	(
		$.setRingShift 1 false true
		$.setRingShift -1 false true
	)
)
macroScript grayFrozen category:"Ingenuity" tooltip:"Show Frozen In Gray" silentErrors:hideErrors
(
		userSel = getCurrentSelection()
		if (userSel.count > 0) then
		(
			for s in userSel do
				s.showFrozenInGray = not s.showFrozenInGray
	)
)
macroScript BakeAnimation category:"Ingenuity" tooltip:"Bake Animation" silentErrors:hideErrors
(
		fileIn (MAX_TOOLS_ROOT + "scripts/Animation/BakeAnimation.ms")
)
macroScript PlaceTool category:"Ingenuity" tooltip:"Place Tool" silentErrors:hideErrors
(
		fileIn (MAX_TOOLS_ROOT + "scripts/Utilities/PlaceTool.ms")
)
macroScript ExplodeByElement category:"Ingenuity" tooltip:"Expode By Element" silentErrors:hideErrors
(
	obj = getCurrentSelection()
	for o in obj do
		ieMaxExplodeByElement o
)
macroScript VisibilityToggle category:"Ingenuity" tooltip:"Visibility Toggle" silentErrors:hideErrors
(
	obj = getCurrentSelection()
	for o in obj do
	(
		try
		(
			v = o.visibility.controller.value
		)
		catch
		(
			o.visibility = bezier_float()
			v = o.visibility.controller.value
		)
		if (v == 1) then
			o.visibility.controller.value = 0
		else
			o.visibility.controller.value = 1
	)
)
macroScript SyncPFlowLayers category:"Ingenuity" tooltip:"Sync PFlow Layers" silentErrors:hideErrors
(
	particleFlow.synchronizeLayers true
)

macroScript msSelectByWirecolor	category:"Ingenuity" tooltip:"Select By Wirecolor" silentErrors:hideErrors
(
	if selection.count >= 1 then
	(
		userSel = getCurrentSelection()
		sel = #()
		for o in objects where not o.isHidden AND not o.isHiddenInVpt do
		(
			for u in userSel do
				if (o.wirecolor == u.wirecolor) then
					append sel o
		)
		select sel
	)
)

macroScript msSelectByMaterial category:"Ingenuity" tooltip:"Select By Material" silentErrors:hideErrors
(
	if selection.count >= 1 then
	(
		userSel = getCurrentSelection()
		sel = #()
		for o in objects where not o.isHidden AND not o.isHiddenInVpt do
		(
			for u in userSel do
				if (o.material == u.material) then
					append sel o
		)
		select sel
	)
)