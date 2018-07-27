try(destroyDialog ::rlRigidBodyCont)catch()
rollout rlRigidBodyCont "Rigid Body Constraint"
(
	local parentObj = undefined
	
	label lbParent "Parent:" pos:[10,10]
	pickbutton pkParentObj "Pick Parent" width:100 height:24 pos:[80,6]
	label lbBreakable "Breakable:" pos:[10,40]
	checkbox cbBreakable "" pos:[80,40]
	label lbMaxForce "Max Force" pos:[10,70]
	spinner spMaxForce "" fieldwidth:88 range:[.01,999999999.9,100.0] pos:[80,70]
	label lbMaxTorque "Max Torque:" pos:[10,100]
	spinner spMaxTorque "" fieldwidth:88 range:[.01,999999999.9,10.0] pos:[80,100]
	button btnApplyRBC "Apply" width:170 height:24 pos:[8,130]
	
	on spMaxForce changed val do
	(
		for obj in selection do 
		(
			if classof obj == UConstraint do
			(
				obj.maxForce = val
			)
		)
	)
	
	on spMaxTorque changed val do
	(
		for obj in selection do 
		(
			if classof obj == UConstraint do
			(
				obj.maxTorque = val
			)
		)
	)
	
	on pkParentObj picked obj do
	(
		if obj != undefined then
		(
			parentObj = obj
			pkParentObj.text = obj.name
		)
	)
	
	on btnApplyRBC pressed do
	(
		for obj in selection do
		(
			childObj = obj
			objConstraints = UConstraint body0:parentObj body1:childObj breakable:true maxForce:spMaxForce.value maxTorque:spMaxTorque.value
		)
	)
)
createDialog rlRigidBodyCont 186 162



 