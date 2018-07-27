try(destroyDialog ::rlRandomTransform)catch()
rollout rlRandomTransform "Object Random"
(	
	--//Variables
	------------------------------------------------------------------------
	local mX,mY,mZ, rX, rY, rZ, sX, sY, sZ
	
	
	
	--//UI
	------------------------------------------------------------------------
	label lbX "X" pos:[115,10]
	label lbY "Y" pos:[175,10]
	label lbZ "Z" pos:[240,10]
	label lbMove "" width:269 height:40 style_sunkenedge:true pos:[10,30]
	checkbutton cbtnMove "POS" width:38 height:38 pos:[11,31]
	checkbutton cbXMMinLock " Min: " height:16 width:40 pos:[49,53] enabled:false
	checkbutton cbXMMaxLock " Max: " height:16 width:40 pos:[49,31] enabled:false
	spinner spnXMMin "" fieldwidth:54 range:[-9999,9999,-1] type:#worldunits pos:[86,53] enabled:false
 	spinner spnXMMax "" fieldwidth:54 range:[-9999,9999,1] type:#worldunits pos:[86,31] enabled:false
 	spinner spnYMMin "" fieldwidth:54 range:[-9999,9999,-1] type:#worldunits pos:[149,53] enabled:false
 	spinner spnYMMax "" fieldwidth:54 range:[-9999,9999,1] type:#worldunits pos:[149,31] enabled:false
 	spinner spnZMMin "" fieldwidth:54 range:[-9999,9999,-1] type:#worldunits pos:[212,53] enabled:false
 	spinner spnZMMax "" fieldwidth:54 range:[-9999,9999,1] type:#worldunits pos:[212,31] enabled:false
	label lbRotate "" width:269 height:40 style_sunkenedge:true pos:[10,80]
	checkbutton cbtnRotate "ROT" width:38 height:38 pos:[11,81]
	checkbutton cbXRMinLock " Min: " height:16 width:40 pos:[49,103] enabled:false
	checkbutton cbXRMaxLock " Max: " height:16 width:40 pos:[49,81] enabled:false
	spinner spnXRMin "" fieldwidth:54 range:[-9999,9999,-1] type:#worldunits pos:[86,103] enabled:false
 	spinner spnXRMax "" fieldwidth:54 range:[-9999,9999,1] type:#worldunits pos:[86,81] enabled:false
 	spinner spnYRMin "" fieldwidth:54 range:[-9999,9999,-1] type:#worldunits pos:[149,103] enabled:false
 	spinner spnYRMax "" fieldwidth:54 range:[-9999,9999,1] type:#worldunits pos:[149,81] enabled:false
 	spinner spnZRMin "" fieldwidth:54 range:[-9999,9999,-1] type:#worldunits pos:[212,103] enabled:false
 	spinner spnZRMax "" fieldwidth:54 range:[-9999,9999,1] type:#worldunits pos:[212,81] enabled:false
	label lbScale "" width:269 height:40 style_sunkenedge:true pos:[10,130]
	checkbutton cbtnScale "SCA" width:38 height:38 pos:[11,131]
	checkbutton cbXSMinLock " Min%: " height:16 width:40 pos:[49,153] enabled:false
	checkbutton cbXSMaxLock " Max%: " height:16 width:40 pos:[49,131] enabled:false
	spinner spnXSMin "" fieldwidth:54 range:[-9999,9999,-1] type:#worldunits pos:[86,153] enabled:false
 	spinner spnXSMax "" fieldwidth:54 range:[-9999,9999,1] type:#worldunits pos:[86,131] enabled:false
 	spinner spnYSMin "" fieldwidth:54 range:[-9999,9999,-1] type:#worldunits pos:[149,153] enabled:false
 	spinner spnYSMax "" fieldwidth:54 range:[-9999,9999,1] type:#worldunits pos:[149,131] enabled:false
 	spinner spnZSMin "" fieldwidth:54 range:[-9999,9999,-1] type:#worldunits pos:[212,153] enabled:false
 	spinner spnZSMax "" fieldwidth:54 range:[-9999,9999,1] type:#worldunits pos:[212,131] enabled:false
	label lbUniformScale "Uniform Scale:" pos:[10,180] enabled:false
	checkbox ckbxUniformScale "" width:20 checked:true pos:[265,180] enabled:false
	label lbTransformType "Transform Type:" pos:[10,200]
	radiobuttons rbtnTransformType labels:#("Absolute", "Relative") pos:[155,200] default:2
	button btnApply "Apply Random Transform" width:269 height:28 pos:[10,222]
	
	--//Functions
	------------------------------------------------------------------------
	fn fnObjMove = (
		mX = (random spnXMMin.value spnXMMax.value)
		mY = (random spnYMMin.value spnYMMax.value)
		mZ = (random spnZMMin.value spnZMMax.value)
	)
	
	fn fnObjRotate =	(
		rX = (random spnXRMin.value spnXRMax.value) as float
		rY = (random spnYRMin.value spnYRMax.value) as float
		rZ = (random spnZRMin.value spnZRMax.value) as float
	)
	
	fn fnObjScale = (
		sX = random ((spnXSMin.value)*0.01) ((spnXSMax.value)*0.01)
		sY = random ((spnYSMin.value)*0.01) ((spnYSMax.value)*0.01)
		sZ = random ((spnZSMin.value)*0.01) ((spnZSMax.value)*0.01)
	)
	
	fn fnMoveButtons = (
		if cbtnMove.state then (--//If master control enabled
			cbXMMinLock.enabled = cbXMMaxLock.enabled = true
			if cbXMMinLock.state then (--//Min lock enabled
				spnXMMin.enabled = true
				spnYMMin.enabled = spnZMMin.enabled = false
				spnYMMin.value = spnZMMin.value = spnXMMin.value
			)else(
				spnYMMin.enabled = spnZMMin.enabled = spnXMMin.enabled = true
			)
		if cbXMMaxLock.state then (--//Max lock enabled
				spnXMMax.enabled = true
				spnYMMax.enabled = spnZMMax.enabled = false
				spnYMMax.value = spnZMMax.value = spnXMMax.value
			)else(
				spnYMMax.enabled = spnZMMax.enabled = spnXMMax.enabled = true
			)
		)else(--//If master control is disabled
			cbXMMinLock.enabled = cbXMMaxLock.enabled = spnXMMin.enabled = spnXMMax.enabled = spnYMMin.enabled = spnYMMax.enabled = spnZMMin.enabled = spnZMMax.enabled = false
		)
	)
	
	fn fnRotateButtons = (
		if cbtnRotate.state then (--//If master control enabled
			cbXRMinLock.enabled = cbXRMaxLock.enabled = true
			if cbXRMinLock.state then (--//Min lock enabled
				spnXRMin.enabled = true
				spnYRMin.enabled = spnZRMin.enabled = false
				spnYRMin.value = spnZRMin.value = spnXRMin.value
			)else(
				spnYRMin.enabled = spnZRMin.enabled = spnXRMin.enabled = true
			)
		if cbXRMaxLock.state then (--//Max lock enabled
				spnXRMax.enabled = true
				spnYRMax.enabled = spnZRMax.enabled = false
				spnYRMax.value = spnZRMax.value = spnXRMax.value
			)else(
				spnYRMax.enabled = spnZRMax.enabled = spnXRMax.enabled = true
			)
		)else(--//If master control is disabled
			cbXRMinLock.enabled = cbXRMaxLock.enabled = spnXRMin.enabled = spnXRMax.enabled = spnYRMin.enabled = spnYRMax.enabled = spnZRMin.enabled = spnZRMax.enabled = false
		)
	)
	
	fn fnScaleButtons = (
		if cbtnScale.state then (--//If master control enabled
			cbXSMinLock.enabled = cbXSMaxLock.enabled = lbUniformScale.enabled = ckbxUniformScale.enabled = true
			if cbXSMinLock.state then (--//Min lock enabled
				spnXSMin.enabled = true
				spnYSMin.enabled = spnZSMin.enabled = false
				spnYSMin.value = spnZSMin.value = spnXSMin.value
			)else(
				spnYSMin.enabled = spnZSMin.enabled = spnXSMin.enabled = true
			)
		if cbXSMaxLock.state then (--//Max lock enabled
				spnXSMax.enabled = true
				spnYSMax.enabled = spnZSMax.enabled = false
				spnYSMax.value = spnZSMax.value = spnXSMax.value
			)else(
				spnYSMax.enabled = spnZSMax.enabled = spnXSMax.enabled = true
			)
		)else(--//If master control is disabled
			lbUniformScale.enabled = ckbxUniformScale.enabled = cbXSMinLock.enabled = cbXSMaxLock.enabled = spnXSMin.enabled = spnXSMax.enabled = spnYSMin.enabled = spnYSMax.enabled = spnZSMin.enabled = spnZSMax.enabled = false
		)
	)
	
	
	
	--//Button Actions
	------------------------------------------------------------------------
	on cbtnMove changed state do fnMoveButtons()
	on cbXMMinLock changed state do fnMoveButtons()
	on cbXMMaxLock changed state do fnMoveButtons()
	on spnXMMin changed val do fnMoveButtons()
 	on spnXMMax changed val do fnMoveButtons()
 	on spnYMMin changed val do fnMoveButtons()
 	on spnYMMax changed val do fnMoveButtons()
 	on spnZMMin changed val do fnMoveButtons()
 	on spnZMMax changed val do fnMoveButtons()
	
	on cbtnRotate changed state do fnRotateButtons()
	on cbXRMinLock changed state do fnRotateButtons()
	on cbXRMaxLock changed state do fnRotateButtons()
	on spnXRMin changed val do fnRotateButtons()
 	on spnXRMax changed val do fnRotateButtons()
 	on spnYRMin changed val do fnRotateButtons()
 	on spnYRMax changed val do fnRotateButtons()
 	on spnZRMin changed val do fnRotateButtons()
 	on spnZRMax changed val do fnRotateButtons()
	
	on cbtnScale changed state do fnScaleButtons()
	on cbXSMinLock changed state do fnScaleButtons()
	on cbXSMaxLock changed state do fnScaleButtons()
	on spnXSMin changed val do fnScaleButtons()
 	on spnXSMax changed val do fnScaleButtons()
 	on spnYSMin changed val do fnScaleButtons()
 	on spnYSMax changed val do fnScaleButtons()
 	on spnZSMin changed val do fnScaleButtons()
 	on spnZSMax changed val do fnScaleButtons()
	
	on btnApply pressed do
	(
		undo on
		(
			case rbtnTransformType.state of 
			(
				1:	(	for obj in selection do -- Absolute
						(
							fnObjMove() 
							if (cbtnMove.checked == true) do (obj.position = [mX,mY,mZ])
							fnObjRotate()
							if (cbtnRotate.checked == true) do (in coordsys (transmatrix obj.transform.pos) obj.rotation = (eulerangles rX rY rZ))
							fnObjScale()
							if (cbtnScale.checked == true) do (obj.scale = [sX, sY, sZ] if ckbxUniformScale.checked == true do (obj.scale = [sX, sX, sX]))
						)
					)
					
				2:	(	for obj in selection do -- Relative
						(
							fnObjMove()
							if (cbtnMove.checked == true) do (move obj [mX,mY,mZ])
							fnObjRotate()
							if (cbtnRotate.checked == true) do (in coordsys local rotate obj (EulerAngles rX rY rZ))
							fnObjScale()
							if (cbtnScale.checked == true) do (obj.scale = [(obj.scale.x * sX), (obj.scale.y * sY), (obj.scale.z * sZ)] if ckbxUniformScale.checked == true do (obj.scale = [(obj.scale.x * sX), (obj.scale.x * sX), (obj.scale.x * sX)]))
						)
					)
			)
		)
	)
)
createDialog rlRandomTransform 289 260 style:#(#style_SysMenu, #style_ToolWindow)