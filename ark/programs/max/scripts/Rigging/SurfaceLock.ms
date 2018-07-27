try(destroyDialog ::rlSurfaceLock)catch()
rollout rlSurfaceLock "Surface Lock"
(
		
	fn fnSizing obj = 
	( 
		bb = nodeLocalBoundingBox obj
		sizeX = abs (bb[1][1] - bb[2][1])
		sizeY = abs (bb[1][2] - bb[2][2])
		size = (sizeX + sizeY) / 2
		return size
	)

	fn fnFreezeTransform obj = 	
	( 		
		local CurObj = obj	
		
		if classof CurObj.rotation.controller != Rotation_Layer do
		(
			
			-- freeze rotation		
			CurObj.rotation.controller = Euler_Xyz() 		
			CurObj.rotation.controller = Rotation_list() 			
			CurObj.rotation.controller.available.controller = Euler_xyz() 		
			
			/* "Localization on" */  
			
			CurObj.rotation.controller.setname 1 "Frozen Rotation" 		
			CurObj.rotation.controller.setname 2 "Zero Euler XYZ" 		
			
			/* "Localization off" */  
			
			CurObj.rotation.controller.SetActive 2 		
		)
		if classof CurObj.position.controller != Position_Layer do
		(

			-- freeze position
			CurObj.position.controller = Bezier_Position() 			
			CurObj.position.controller = position_list() 			
			CurObj.position.controller.available.controller = Position_XYZ() 	

			/* "Localization on" */  
					
			CurObj.position.controller.setname 1 "Frozen Position" 	
			CurObj.position.controller.setname 2 "Zero Pos XYZ" 			
			
			/* "Localization off" */  
			
			CurObj.position.controller.SetActive 2 		

			-- position to zero
			CurObj.Position.controller[2].x_Position = 0
			CurObj.Position.controller[2].y_Position = 0
			CurObj.Position.controller[2].z_Position = 0
		)
	)

	fn fnFreezeRotation obj = 	
	( 		
		local CurObj = obj	
		
		if classof CurObj.rotation.controller != Rotation_Layer do
		(
			
			CurObj.rotation.controller = Euler_Xyz() 		
			CurObj.rotation.controller = Rotation_list() 		
			
			/* "Localization on" */
			
			CurObj.rotation.controller.available.controller = Euler_xyz() 		
			CurObj.rotation.controller.setname 1 "Initial Pose"	
			CurObj.rotation.controller.setname 2 "Keyframe XYZ"
			CurObj.rotation.controller.SetActive 2 		
		)
	)
	
	function fnDeleteKeys targetObj track axis =
	(	
		--sliderTime = 0f
		selectKeys targetObj.transform.controller[track]
		deleteKeys targetObj.transform.controller[track] #selection
	)
		
	groupbox gpInstructions "Instructions:" width:160 height:85 pos:[10,10]
	label lbInfo " 1.Select master controls \n 2.Press 'Run Surface Lock'\n 3.Pick surface object \n 4.Press 'Select Control' "width:130 height:56 pos:[20,30] --style_sunkenedge:true
	label lbTransAnim "Transfer control animation:" pos:[10,105]
	checkbox cbTransAnim "" pos:[155,105] checked:true
	button btnGO "Run Surface Lock" width:160 height:30 pos:[10,130]
 	button btnSelectControl "Select Controls" width:160 height:20 pos:[10,170]
	
	on btnSelectControl pressed do
	(
		clearSelection()
		try(select $ControlPt_*)catch()
	)
	
	on btnGo pressed do
	(
		if selection.count >= 1 do (
			_ctrls = #() --variable used to hold the newly created ctrls
			_comCtrls = selection as array -- contains the selected COM's (master controls) which will later be surface locked
			_DeformCtrl = ConformSpaceWarp Projection_Distance:0 Selected_Verts:0 Standoff_Distance:1 Icon_Size:(units.decodevalue ".5m") pos:[0,0,0]
			
			for _curCtrl in _comCtrls do (
				_theSize = (fnSizing _curCtrl) --get size of bounding box which is used to size the ctrls being created
				
				--//Create Controls 
				MasterCtrl = Star radius1:(_theSize/3) radius2:(_theSize/2.25) name:(uniqueName "SurfaceCtrl_") wirecolor:green fillet1:0 fillet2:0 numPoints:6 distort:0 pos:_curCtrl.pos render_displayRenderMesh:false renderable:off
				SurfacePt = Point size:(_theSize/2) wirecolor:green cross:on Box:on axistripod:off centermarker:off pos:_curCtrl.pos name:(uniqueName "SufacePt_")
				ControlPt = Point size:(_theSize/2) wirecolor:green cross:on Box:on axistripod:off centermarker:off pos:[_curCtrl.pos.x,_curCtrl.pos.y,_curCtrl.pos.z+(_theSize*2)] name:(uniqueName "ControlPt_")
				SurfacePlane = Plane lengthsegs:2 widthsegs:2 length:(_theSize/4) width:(_theSize/4) pos:ControlPt.pos renderable:off name:(uniqueName "SurfacePinCtrl_") wirecolor:green
				
				convertToMesh  SurfacePlane --//Converts to editmesh in order for "conform/surface locking" to work in max
				
				--//Control wiring
				bindSpaceWarp SurfacePlane _DeformCtrl
				aCtrl = Attachment node:SurfacePlane align:true
				_curCtrl.parent = MasterCtrl
				SurfacePlane.parent = ControlPt
				SurfacePt.pos.controller = aCtrl
				addNewKey aCtrl 0f 
				theAKey = AttachCtrl.getKey aCtrl 1
				theAKey.face = 0
				theAKey.coord = [0,0] 
				
				--//MasterCtrl transform setting
				fnFreezeTransform MasterCtrl
				fnFreezeRotation MasterCtrl
				
				--//MasterCtrl Position controller setup
				posCst = Position_Constraint relative:false
				MasterCtrl.pos.controller.Zero_Pos_XYZ.controller = posCst
				posConstraintInterface = posCst.constraints
				posConstraintInterface.appendTarget SurfacePt 50.0
				MasterCtrl.pos.controller.Available.controller = Position_XYZ()
				MasterCtrl.pos.controller.SetActive 3
				
				--//MasterCtrl Rotation controller setup
				rotCst = Orientation_Constraint relative:false local_world:0
				MasterCtrl.rotation.controller.Keyframe_XYZ.controller = rotCst
				rotConstraintInterface = rotCst.constraints
				rotConstraintInterface.appendTarget SurfacePt 50.0
				
				--TransferAnimation
				if cbTransAnim.state do (
					local _orgPos = _curCtrl.pos -- store original position
					
					posController = copy _curCtrl.transform.controller[1].controller  
					rotController = copy _curCtrl.transform.controller[2].controller
					scaController = copy _curCtrl.transform.controller[3].controller 
					
					fnDeleteKeys _curCtrl 1 1
					fnDeleteKeys _curCtrl 2 2
					fnDeleteKeys _curCtrl 3 3
					
					ControlPt.transform.controller[1].controller = posController
					ControlPt.transform.controller[2].controller = rotController
					ControlPt.transform.controller[3].controller = scaController
					ControlPt.pos = _orgPos
				)
				
				select _DeformCtrl
				max modify mode
			)			
		)
	)
)
createDialog rlSurfaceLock 180 200 style:#(#style_SysMenu, #style_ToolWindow)
