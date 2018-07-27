rollout rlMoveKeys "Offset Keys"
(
	groupbox gpbxOffSettings "Offset Settings" pos:[10,8] width:160 height:65
 	label lbMin "Min:" pos:[20,28]
 	label lbMax "Max:" pos:[20,48]
 	spinner spnMaxOff "" fieldwidth:50 range:[-99999.9,99999.9,-1.0] type:#float pos:[100,28]
 	spinner spnMinOff "" fieldwidth:50 range:[-99999.9,99999.9,1.0] type:#float pos:[100,48]
	groupbox gpbxSelSettings "" pos:[10,66] width:160 height:35
	label lbSelGroup "Group Selection:" pos:[20,78]
	button btnSelectHC "Select" height:16 width:40 pos:[102,78]
 	checkbox ckbxSelGroup "" width:21 pos:[148,78]
	checkbox ckbxSnapToFrames "Snap To Frames:" pos:[10,108]
 	button btnApply "Apply" width:160 height:24 pos:[10,128]
	
	on btnSelectHC pressed do
	(
		for obj in selection do
		(
			selectmore obj.children
		)
	)
	
	on btnApply pressed do
	(		
		undo on
		(
			offsetVal = if ckbxSnapToFrames.state then (random (spnMinOff.value as integer) (spnMaxOff.value as integer)) else ((random spnMinOff.value spnMaxOff.value) as float)
			for Obj in selection do
			(
				uniqueOffsetVal = if ckbxSnapToFrames.state then (random (spnMinOff.value as integer) (spnMaxOff.value as integer)) else ((random spnMinOff.value spnMaxOff.value) as float)
				if ckbxSelGroup.checked != true then
				(
					moveKeys Obj uniqueOffsetVal
				)else(
					moveKeys Obj offsetVal
				)
			)
		)
	)
)
createDialog rlMoveKeys 180 162
