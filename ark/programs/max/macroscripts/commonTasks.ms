--Copies last render to the clipboard
--requires AVGuard extensions which are aparently crap
-- macroScript copyRender3 category:"Ingenuity" tooltip:"Render to Clipboard 3.0"
-- (
-- 	renderBitmap = getLastRenderedImage()
-- 	setClipboardBitmap renderBitmap
-- )
--turns a selection of lights off
macroScript multiImport category:"Ingenuity" tooltip:"Multi Import"
(
	filePath = (getSavePath caption:"Import Directory")
	if (filePath != undefined) then (
		filePath += "\\*.obj"
		disableSceneRedraw()
		files = getFiles (filePath)
		print files
		for f in files do (
			importFile (f) #noPrompt
			AddMod smooth
			$.modifiers[#Smooth].smoothingBits = 1
			ConvertTo $ Editable_Poly
			clearSelection()
		)
		enableSceneRedraw()
		completeRedraw()
	)
)

macroScript materialToInstances category:"Ingenuity" tooltip:"Mat to Instances"
(
	try(
		if ($ != undefined and $.material != undefined) then
		(
			disableSceneRedraw()
			InstanceMgr.SetMtlOnInstances $ $.material
			enableSceneRedraw()
			completeRedraw()
		)
	) catch()
)

macroScript makeVrayMaterial category:"Ingenuity" tooltip:"Make Vray Material"
(
	meditmaterials[activeMeditSlot] = VRayMtl()
)

macroScript makeMaxwellMaterial category:"Ingenuity" tooltip:"Make Maxwell Material"
(
	meditmaterials[activeMeditSlot] = Maxwell_Material()
)

macroScript selectInstancesOfSelected category:"Ingenuity" tooltip:"Select All Instances"
(
    userSel = getCurrentSelection()
    allInstances = #()
    instances = #()
    for obj in userSel do
    (
      InstanceMgr.GetInstances obj &instances
      allInstances += instances
    )
    select allInstances
)

macroScript lightOff category:"Ingenuity" tooltip:"Light Off"
(
	for sel in $ do (
		if (classOf sel == DirectionalLight or \
		classOf sel == OmniLight or \
		classof sel == targetSpot or \
		classof sel == TargetDirectionallight or \
		classof sel == Free_Point or \
		classof sel == freeSpot or \
		classof sel == miAreaLightomni ) then (
			try (
				sel.enabled = false
				sel.omni_light.enabled = false
			)catch()
		)
	)
)

--turns a selection of lights on
macroScript lightOn category:"Ingenuity" tooltip:"Light On"
(
	on isEnabled return (selection.count > 0)
	on execute do (
		for sel in $ do
		(
			if (classOf sel == DirectionalLight or \
			classOf sel == OmniLight or \
			classof sel == targetSpot or \
			classof sel == TargetDirectionallight or \
			classof sel == Free_Point or \
			classof sel == freeSpot or \
			classof sel == miAreaLightomni ) then (
				try (
					sel.enabled = true
					sel.omni_light.enabled = true
				)catch()
			)
		)
	)
)

--renames a selection of objects given a base name
macroScript objRename category:"Ingenuity" tooltip:"Rename Objects"
(
	rollout renameRoll "Enter New Base Name"
	(
		fn renameObjs =
		(
			objs = getCurrentSelection()
			if renameRoll.chkRenameAllInstances.checked then
			(
				allObjs = #()
				instances = #()
				for o in objs do
				(
					InstanceMgr.GetInstances o &instances
					allObjs += instances
				)
				objs = makeUniqueArray allObjs
			)
			if renameRoll.edtBaseName.text != "" then
				for i in objs do i.name = uniquename (renameRoll.edtBaseName.text + "_")

			if renameRoll.chkAutoClose.checked == true then
				try ( destroydialog ::renameRoll )catch()
		)

		edittext edtBaseName ""
		button btnRenameObjs "Rename"
		checkbox chkRenameAllInstances "Rename All Instances" checked:true
		checkbox chkAutoClose "Auto Close" checked:true

		on btnRenameObjs pressed do
			renameObjs()

		on edtBaseName entered text do
			renameObjs()

		on renameRoll open do
			setFocus edtBaseName
	)
	try ( destroydialog ::renameRoll )catch()
	createDialog renameRoll 250 100
)

--pitches obj export file out to desktop for sculpting in zbrush or mudbox
macroScript fileOut category:"Ingenuity" tooltip:"Obj Out"
(
	--change this directory to modify where the obj out script exports to
	exportFile ("C:\Documents and Settings\grant.miller\Desktop\gport.obj") #noPrompt selectedOnly:true
)

--grabs the same obj export file and places it in the scene
macroScript fileIn category:"Ingenuity" tooltip:"Obj In"
(
	on execute do
	(
		disableSceneRedraw()

		--change this directory to modify where the obj in script imports from (should be the same as the directory above)
		importFile ("C:\Documents and Settings\grant.miller\Desktop\gport.obj") #noPrompt
		AddMod smooth
		$.modifiers[#Smooth].smoothingBits = 1
		ConvertTo $ Editable_Poly

		enableSceneRedraw()
		completeRedraw()
	)
)

--transform center cycle
macroScript transformCycle category:"Ingenuity" tooltip:"Trans. Center Cycle"
(
	if (getCoordCenter() == #System) then toolmode.pivotCenter()
	else if (getCoordCenter() == #Local) then toolmode.selectionCenter()
	else toolmode.transformCenter()
)

-- creates a cube at the origin with symmetry
macroScript BoxWithSymmetry category:"Ingenuity" tooltip:"Box With Symmetry"
(
	b = Box widthsegs:2 heightsegs:1 lengthsegs:1 length:100 width:100 height:100 pos:[0,0,0] isSelected:true
	ConvertTo b Editable_Poly
	polyOp.deleteFaces b #{1, 3, 5, 9, 10}
	addmodifier b (Symmetry())
)

macroScript ToggleCage category:"Ingenuity" tooltip:"Toggle Cage Display"
(
 	on isEnabled return	( selection.count==1 and classOf selection[1].baseobject == Editable_Poly )
	on execute do (
		$.showCage = not $.showCage
		try(
			if ($.modifiers[#Edit_Poly].showCage) then
				$.modifiers[#Edit_Poly].showCage = off
			else
				$.modifiers[#Edit_Poly].showCage = on
		)catch()
	)
)

macroScript ToggleVertexColors category:"Ingenuity" tooltip:"Toggle Vertex Colors"
(
	on isEnabled return	( selection.count==1 )
	on execute do ( for sel in $ do	sel.showvertexcolors = not sel.showvertexcolors )
)

--create spline from edge and then select it
macroScript SplineFromEdge category:"Ingenuity" tooltip:"Spline from Edge"
(
	on isEnabled return	( selection.count==1 and classOf selection[1].baseobject == Editable_Poly and $.selectedEdges.count > 0)
	on execute do (
		sName = uniqueName ($.name + "Spline")
		newShape = $.EditablePoly.createShape sName off $
		subobjectLevel = 0
		select (getNodeByName sname)
	)
)

--assign random wire color
macroScript RandomWireColor category:"Ingenuity" tooltip:"Random Wire Color"
(
	on isEnabled return	( selection.count>=1)
	on execute do (
		for sel in $ do (
			domColor = random 1 3
			if (domColor == 1) then
					sel.wirecolor = color (random 128 255) (random 0 128) (random 0 128)
			else if (domColor == 2) then
			 		sel.wirecolor = color (random 0 128) (random 128 255) (random 0 128)
			else
			 		sel.wirecolor = color (random 0 128) (random 0 128) (random 128 255)
		)
	)
)

--attach selected objects
macroScript AttachSelected category:"Ingenuity" tooltip:"Attach Selected"
(
	on isEnabled return (selection.count > 1)
	on execute do
	(

		disableSceneRedraw()
		userSel = getCurrentSelection()
		for obj in userSel do
			Try(ConvertTo obj Editable_Poly)Catch()

		baseObj = userSel[1]

		for obj in userSel do
		(
			if (obj != baseObj) then
			(
				if (classof obj == Editable_mesh) or (classof obj == Editable_Poly) then
					baseObj.EditablePoly.attach obj baseObj
			)
		)

		select baseObj
		baseObj.pivot = [($.min.x + $.max.x) * .5, ($.min.y + $.max.y) * .5, $.min.z]

		enableSceneRedraw()
		completeRedraw()
	)
)

--select non geometry objs
macroScript SelectNonMesh category:"Ingenuity" tooltip:"Select Non-Mesh Nodes"
(
	clearSelection()
	nonMesh = #()
	for s in $* do (
		if not(s.ishidden or s.isfrozen) then (
			if not(superClassOf s == GeometryClass) then
				append nonMesh s
		)
	)
	select nonMesh
)

--select all spline or line objects
macroScript SelectSpline category:"Ingenuity" tooltip:"Select Splines"
(
	clearSelection()
	splines = #()
	for s in $* do (
		if not(s.ishidden or s.isfrozen) then (
			if (superClassOf s == Shape) then
				append splines s
		)
	)
	select splines
)

--clear grids
macroScript ClearGrids category:"Ingenuity" tooltip:"Clear Grids"
(
	junk = #()
	for s in $grid* do (
		if not(s.ishidden or s.isfrozen) then append junk s
	)
	delete junk
)

--gets selection's material and place it in 1st material editor slot
macroScript grabMat category:"Ingenuity" tooltip:"Grab Mat"
(
  userSel = getCurrentSelection()
  if userSel.count > 0 then
  (
    for s=activeMeditSlot to (amin (userSel.count + activeMeditSlot - 1) 24) do
    (
      selectionIndex = s - activeMeditSlot + 1
      if (userSel[selectionIndex].material != undefined) then
        mEditMaterials[s] = userSel[selectionIndex].material
    )
    -- activeMeditSlot = (amin userSel.count 24)
  )
)

--gets entered material name and sticks it in 1st slot of mEdit
macroScript grabMatByName category:"Ingenuity" tooltip:"Grab Mat By Name"
(
	rollout matNameRollout "Material Name" (
		edittext matName ""
		button getMat "Get Mat by Name"
		on getMat pressed do (
			if matName.text != "" then (
				try ( meditMaterials[1] = sceneMaterials[matName.text] ) catch()
			)
		)
	)
	createDialog matNameRollout 250 50
)

--removes diffuse channel and sets diffuseColor to 128 gray
--useful for testing bump and displacement and for other
--misc rendered passes
macroScript removeDiffuse category:"Ingenuity" tooltip:"Remove Diffuse"
(
	noWork = #()
	for s in $* do (
		if not(s.ishidden or s.isfrozen) then (
			if (s.material != undefined) then (
				if (classOf s.material == Arch___Design__mi) then (
					s.material.diff_color = (color 128 128 128)
					s.material.mapM0 = undefined
				) else if (classOf s.material == StandardMaterial) then (
					s.material.diffuse = (color 128 128 128)
					s.material.diffuseMap = undefined
				) else append noWork s
			) else s.wireColor = (color 128 128 128)
		)
	)
	select noWork
)

macroScript setAllViews category:"Ingenuity" tooltip:"Set All Views"
(
  viewport.setLayout #layout_4
  cam = viewport.getCamera()
  if (isValidNode cam) then
  (
    for i = 1 to 4 do
    (
      viewport.activeViewport = i
      viewport.setCamera cam
    )
  )
)

macroScript clearMaterialEditor category:"Ingenuity" tooltip:"Clear Material Editor"
(
  for m = 1 to meditmaterials.count do
	  meditmaterials[m] = Maxwell_Material()
)

macroScript updateScripts category:"Ingenuity" tooltip:"Update Scripts"
(
  fileIn (MAX_TOOLS_ROOT + "macroscripts/ieMacros.ms")
)