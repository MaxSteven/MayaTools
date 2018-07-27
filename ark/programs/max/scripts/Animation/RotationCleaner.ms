try(destroyDialog ::rlCleanRotationKeys)catch()
rollout rlCleanRotationKeys "Clean Rotation Keys"
(
	
	fn fnCleanRotationKeys node: axis: = (
		if rlCleanRotationKeys.rbTransform.state == 1 then
		(
			if axis == "X" do subCtrl = node.position.controller.X_Position.controller
			if axis == "Y" do subCtrl = node.position.controller.Y_Position.controller 
			if axis == "Z" do subCtrl = node.position.controller.Z_Position.controller
		)else(
			if axis == "X" do subCtrl = node.rotation.controller.X_Rotation.controller 
			if axis == "Y" do subCtrl = node.rotation.controller.Y_Rotation.controller 
			if axis == "Z" do subCtrl = node.rotation.controller.Z_Rotation.controller
		)
		
		if classof node.rotation.controller == Euler_XYZ do
		(
			if classof subCtrl == bezier_float do
			(
				totalKeys = numKeys subCtrl
				
				if totalKeys > 2 do --only run if there are more than 2 keys on the objects given controller
				(
					count = 0
					staticKey = (getKey subCtrl 1).value --used as static key to compare to, to see when object moves
					deselectKeys subCtrl --clear selection before commiting to changes
					for k = 2 to (totalKeys-1) do
					(
						thisKey = (getKey subCtrl k).value
						
						if thisKey != staticKey do --only delete the key if it is not the same as the first key
						(
							selectKey subCtrl k
							count += 1
						)
					)
					if count != 0 do deleteKeys subCtrl #selection --only try and delete keys if there is atleast 1 selected
				)
			)
		)
	)
	
	radiobuttons rbTransform "" labels:#("Position","Rotation") columns:2 pos:[9,10] default:1
 	button btnX "Clean X" width:120 height:25 pos:[10,30]
	button btnY "Clean Y" width:120 height:25 pos:[10,60]
	button btnZ "Clean Z" width:120 height:25 pos:[10,90]
	
	on btnX pressed do (
		for obj in selection do
		(
			fnCleanRotationKeys node:obj axis:"X"
		)
	)
	on btnY pressed do (
		for obj in selection do
		(
			fnCleanRotationKeys node:obj axis:"Y"
		)
	)
	on btnZ pressed do (
		for obj in selection do
		(
			fnCleanRotationKeys node:obj axis:"Z"
		)
	)


)
createDialog rlCleanRotationKeys 140 125  style:#(#style_SysMenu, #style_ToolWindow)