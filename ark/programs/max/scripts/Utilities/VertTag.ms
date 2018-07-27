try (destroydialog ::rlVertTag)catch()
rollout rlVertTag "Vert Tag 1.0"
(
	--//Variables
	local pinObj = undefined
	local pinSurface = undefined
	local numVerts = undefined
	
	--//Functions
	fn fnSurfaceFilter obj = classof obj == Editable_mesh
	
	groupbox gpbxObjects "Vert Tag Objects" width:180 height:105 pos:[10,6]
	edittext etPinObj "Pin Object:" fieldWidth:144 height:17 labelOnTop:true readOnly:true pos:[19,26]
	pickbutton pbtnPinObj "+" width:16 height:16 pos:[163,45] 
	edittext etSurfaceObj "Surface Object:" fieldWidth:144 height:17 labelOnTop:true readOnly:true pos:[19,66]
	pickbutton pbtnSurfaceObj "+" width:16 height:16 pos:[163,85] filter:fnSurfaceFilter
	groupbox gpbxProperties "Pin Object Properties" width:180 height:93 pos:[10,118]
 	label lbNumObjs "# Pin Objects:" width:160 height:18 pos:[19,138]
	label lbNumObjsVal "" pos:[114,138] width:65  height:16 style_sunkenedge:true
	label lbType "Pin Copy Type:" pos:[19,158] 
	radiobuttons rbCopyType labels:#("copy", "instance", "reference") columns:1 pos:[114,158] 
	button btnRunVertTag "Run Vert Tag" height:30 width:180 pos:[10,216] enabled:false
	
	on pbtnPinObj picked obj do
	(
		if obj != undefined do
		(
			pinObj= obj
			etPinObj.text = obj.name
			if pinSurface != undefined do btnRunVertTag.enabled = true
		)
	)
	
	on pbtnSurfaceObj picked obj do
	(
		if obj != undefined do
		(
			pinSurface= obj
			numVerts = obj.numverts
			etSurfaceObj.text = obj.name
			lbNumObjsVal.text = numVerts as string
			if pinObj != undefined do btnRunVertTag.enabled = true
		)
	)
	
	on btnRunVertTag pressed do
	(
		if IsValidNode pinObj and IsValidNode pinSurface then
		(
			disableSceneRedraw()
			for v = 1 to numVerts do
			(
				copyType = case rbCopyType.state of (
						1: copy
						2: instance
						3: reference 
					)
				local newPin = copyType pinobj
				newPin.pos.controller = position_script ()
				newPin.position.controller.script ="obj = $" + pinSurface.name + "; posVert = " + v as string + 
				"
				if IsValidNode obj and	IsKindOf obj Editable_mesh and obj.numVerts >= posVert then
				(getVert obj posVert) else ([0, 0, 0])
				"
			)
			enableSceneRedraw()
			completeredraw()
		)
		else 
		(
			Messagebox "A Vert Tag Object is not available!"
			pinObj = undefined
			pinSurface = undefined
			etPinObj.text = ""
			etSurfaceObj.text = ""
			btnRunVertTag.enabled = false
		)
	)

)
createDialog rlVertTag 200 256
	