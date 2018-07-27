rollout rlTargetLight "Target VrayLight"
(
	button btnTargetLight "Vray Target Light" width:130 height:30 pos:[10,10]
	button btnRevertLight "Revert to Vray Light" width:130 height:30 pos:[10,50]
	
	on btnTargetLight pressed do
	(
		for obj in selection where classof obj == VRayLight do
		(
			theLight = obj
			lightTarget = point size:20 Box:on cross:off axistripod:off centermarker:off pos:[0,0,0] name:(theLight.name + "_target") wirecolor:yellow
			
			if classof theLight.rotation.controller != LookAt_Constraint do
			(
				theCtrl = LookAt_Constraint viewline_length_abs:off target_axis:2 upnode_axis:1 StoUP_axis:1 target_axisFlip:on
				theCtrl.appendTarget lightTarget 50
				theLight.rotation.controller = theCtrl	
			)
			if classof theLight.rotation.controller == LookAt_Constraint do
			(
				theCtrl = theLight.rotation.controller
				theCtrl.appendTarget lightTarget 50
				theLight.rotation.controller = theCtrl	
			)
			select lightTarget
		)
	)
	
	on btnRevertLight pressed do
	(
		for obj in selection where classof obj == VRayLight do
		(
			theLight = obj
			theLight.rotation.controller = Euler_XYZ ()	
		)
	)		
)
createDialog rlTargetLight 150 90 style:#(#style_SysMenu, #style_ToolWindow)