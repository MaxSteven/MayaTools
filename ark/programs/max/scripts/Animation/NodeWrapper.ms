	try(destroydialog ::nodeWrapperRL)catch()	
	rollout nodeWrapperRL "nodeWrapper" width:150 height:90
	(			
		local _addSprings = false, _mass = 2000, _drag = 4, _color = (color 0 255 0), _wrapSize = 50
		fn setMass val =	(
			_mass = val
			for obj in selection do if (classOf obj.position.controller) == SpringPositionController then obj.position.controller.setMass val
		)
		fn setDrag val =
		(
			_drag = val		
			for obj in selection do if (classOf obj.position.controller) == SpringPositionController then obj.position.controller.setDrag val
		)		
		fn setColor val =
		(
			_color = val
			for obj in selection do if (classOf obj) == Point then obj.wirecolor = val
		)
		fn setWrapSize val =
		(
			_wrapSize = val
			for obj in selection do if (classOf obj) == Point then obj.size = val
		)
		fn process alt = ( 
			nodeBoxes = #()
			for obj in selection do 
			(
				append nodeBoxes (parentObj = Point())
				emptyPRS = copy parentObj.transform.controller
				parentObj.size = _wrapSize
				parentObj.box = true
				parentObj.name = uniqueName "nodeWrap"
				parentObj.wirecolor = _color
				if obj.parent != undefined then (at time sliderTime (parentObj.parent = obj.parent) )				
				parentObj.transform = obj.transform	
				parentObj.transform.controller = copy obj.transform.controller
				bebesKids = for kid in obj.children collect kid	
				if alt then for kid in bebesKids do ( at time sliderTime (kid.parent = undefined) )						
				at time sliderTime (obj.parent = parentObj)
				if alt then for kid in bebesKids do ( at time sliderTime (kid.parent = parentObj) )					
				obj.transform.controller = emptyPRS
				if _addSprings then 
				(
					obj.position.controller = SpringPositionController ()
					obj.position.controller.setMass _mass
					obj.position.controller.setDrag _drag
				)			
			)			
			if _addSprings == false then select (for obj in nodeBoxes collect obj)
		)		
		
		colorpicker colorPck "" color:_color modal:false pos:[3,6] height:20 width:42 alpha:true
		spinner wrapSize range:[0,10000,_wrapSize] type:#integer width:38 pos:[6,30] 
		button wrapEm "Wrap" pos:[48,6] height:40 width:96 
		checkbutton springEm "w\Curlies" pos:[6,50] height:34 width:70
		label massLbl "m" pos:[79,50]
		spinner massAmt pos:[88,50] range:[0,10000000,_mass] type:#float width:55
		label dragLbl "d" pos:[79,68]
		spinner dragAmt pos:[88,68] range:[0,10000000,_drag] type:#float width:55
		on wrapEm pressed do ( undo on (process false))
		on wrapEm rightclick do ( undo on (process true))
		on springEm changed val do _addSprings = val
		on massAmt changed val do setMass val
		on dragAmt changed val do setDrag val
		on colorPck changed val do setColor val
		on wrapSize changed val do setWrapSize val
	)
	createdialog nodeWrapperRL pos:[1720, 100]