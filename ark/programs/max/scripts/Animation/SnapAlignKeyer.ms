try(destroyDialog ::rlSnapAlignKey)catch()
rollout rlSnapAlignKey "Snap Align Keyer"
(
	local animNode = undefined

	groupbox gpbxMatchObject "Animated object to match:" width:165 height:55 pos:[10,10]
	pickbutton pbAnimNode "Pick Object" width:145 height:24 pos:[20,30]
	label lbStartFrame "Start Frame:" pos:[10,75]
	label lbEndFrame "End Frame:" pos:[10,95]
	spinner spnStartFrame range:[-99999,99999,animationrange.start] type:#integer fieldwidth:55 pos:[108,75]
	spinner spnEndFrame range:[-99999,99999,animationrange.end] type:#integer fieldwidth:55 pos:[108,95]
	checkbox ckbIgnoreScale "Ignore Scale" checked:true pos:[10,120]
	checkbox ckbtnTrackerObj "Create Tracker Object " pos:[10,140]
 	button btnBakeAnimation "Bake Animation" width:165 height:40 pos:[10,165]

	fn SnapMatchNodes =
	(
		local curSel = undefined

		if isValidNode animNode AND animNode != undefined then
		(
			curSel = if ckbtnTrackerObj.checked then
			(
				point size:30 centermarker:false axistripod:false cross:true box:true constantscreensize:true drawontop:true name:(uniqueName "Tracker_") wirecolor:[0,255,0]
			)else(
				getCurrentSelection()
			)

			with animate on
			(
				for t = spnStartFrame.value to spnEndFrame.value by 1 do
				(
					at time t
					(
						TM = if ckbIgnoreScale.checked then (orthogonalize animNode.transform) else animNode.transform
						curSel.transform = TM
					)
				)
			)

		)else(
			animNode = undefined
			pbAnimNode.text = "Pick Object"
			MessageBox "Pick an animated object"
			return()
		)
	)

	on pbAnimNode picked obj do
	(
		if obj != undefined then
		(
			pbAnimNode.text = obj.name
			animNode = obj
		)else(
			animNode = undefined
			pbAnimNode.text = "Pick Object"
		)
	)

	on btnBakeAnimation pressed do
	(
		SnapMatchNodes()
	)
)
createDialog rlSnapAlignKey 185 215  style:#(#style_SysMenu, #style_ToolWindow)