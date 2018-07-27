(
	try(DestroyDialog ::rlDitto)catch()

	local AnimObjs = #()
	local StaticObjs = #()

	rollout rlDitto "Ditto"
	(
		local setButtons
		
		function fnDeleteKeys targetObj track axis = -- delete keys
		(	
			--sliderTime = 0f
			selectKeys targetObj.transform.controller[track]
			deleteKeys targetObj.transform.controller[track] #selection
		)
		
		fn compareNames str1 str2 = stricmp str1.name str2.name
			
		fn fnAddItmsLst lst arr = ( -- add Objects to list
			userSel = for obj in selection where (classOf obj != XRefObject) collect obj --xref objects don't have controllers
			
			if userSel.count >= 1 do
			(				
				for o in userSel do (appendIfUnique arr o) -- apend new object to array
				qSort arr compareNames
				lst.items = for i in arr collect i.name -- update list with array
			)
		)
		
		fn fnRemoveItmsLst lst arr = ( -- remove objects from list
			local currSel = lst.selection
			for i = lst.items.count to 1 by -1 where currSel[i] do (deleteItem arr i)
			lst.items = for i in arr collect i.name -- update list with array
			lst.selection = #{}
		)
		
		fn fnMoveItmUpLst lst arr = ( -- moves objects up list
			local itm = lst.selection 
			for t = 2 to itm.count do
			(
			if (itm[t] and not itm[t - 1]) then
				(
				swap arr[t] arr[t - 1]
				deleteItem itm t
				append itm (t - 1)
				)
			)
			lst.items = for i in arr collect i.name -- update list with array
			lst.selection = itm	
		)
		
		fn fnMoveItmDownLst lst arr = ( -- moves objects down list
			local itm = lst.selection
			for t = itm.count - 1  to 1 by -1 do
			(
			if (itm[t] and not itm[t + 1]) then
				(
				swap arr[t] arr[t + 1]
				deleteItem itm t
				append itm (t + 1)
				)
			)
			lst.items = for i in arr collect i.name -- update list with array
			lst.selection = itm	
		)
		
		fn fnClearLst lst arr = ( -- clears list
			for i = lst.items.count to 1 by -1 do (deleteItem arr i)
			lst.items = for i in arr collect i.name -- update list with array
			lst.selection = #{}
		)
		
		fn fnSetButtons lst lstMU lstMD = 
		(
			local currSel = lst.selection
			local currCount = lst.items.count
			local cnt = 0, enable = false
				
			if currCount > 0 then
				(
				for i = 1 to currSel.count do
					( 
					if currSel[i] then 
						cnt += 1
					)
				if (cnt > 0) and (cnt != currcount) then
					enable = true
				)
			lstMU.enabled = enable
			lstMD.enabled = enable
		)
		
		fn fnUpdateListsCount =
		(
			rlDitto.lbAnimObjsCount.text = AnimObjs.count as string
			rlDitto.lbStaticObjsCount.text = StaticObjs.count as string
		)
		
		MultiListBox mlbxAnimatedObjects "Animated Objects:" pos:[10,7] width:150 height:12
			label lbAnimObjsCount "0" style_sunkenedge:true pos:[104,7] width:55 height:16
			button btnAddAnimObj "+" pos:[10,185] width:30 height:24
			button btnRemoveAnimObjs "-" pos:[40,185] width:30 height:24
			button btnClearAnimObjs "X" pos:[70,185] width:30 height:24
			button btnMoveUpAnimObj"^" pos:[100,185] width:30 height:24
			button btnMoveDownAnimObj "v" pos:[130,185] width:30 height:24
		button btnRefresh "$" height:30 width:30 pos:[161,23] tooltip:"Selects objects in lists based on what's selected in the scene."
		button btnSelList "-$-" height:30 width:30 pos:[161,53] tooltip:"Selects objects in the scene based on what's selected in the lists."
		--button btnMoveToKT ">" height:40 width:24 pos:[130,65]
		--button btnRemoveFromKT "<" height:40 width:24 pos:[130,105]
		--button btnClearKT "X" height:40 width:24 pos:[130,145]
		MultiListBox mlbxStaticObjects "Static Objects:" pos:[192,7] width:150 height:12
			label lbStaticObjsCount "0" style_sunkenedge:true pos:[286,7] width:55 height:16
			button btnAddStaticObj "+" pos:[192,185] width:30 height:24
			button btnRemoveStaticObjs "-" pos:[222,185] width:30 height:24
			button btnClearStaticObjs "X" pos:[252,185] width:30 height:24
			button btnMoveUpStaticObj"^" pos:[282,185] width:30 height:24
			button btnMoveDownStaticObj "v" pos:[312,185] width:30 height:24
		groupbox gpbxSettings "Settings" pos:[10,216] width:330 height:94
			label lbCopyTracks "Tracks To Copy:" pos:[19,236]
			checkbox ckbxPosition "Position" pos:[109,236] checked:true
			checkbox ckbxRoation "Rotation" pos:[189,236] checked:true
			checkbox ckbxScale "Scale" pos:[269,236] checked:false
			label lbTransformType "Transform Type:" pos:[19,256]
			radiobuttons rbtnTransformType "" labels:#("Relative      ","Absolute") pos:[109,256]
		groupbox gpbxDeleteKeys "" pos:[10,272] width:330 height:38
			label lbdeleteExKeys "Delete existing keys on static objects:" pos:[19,286]
			checkbox ckbxDeleteExKeys "" pos:[269,286] checked:true
			button btnApplyDitto "Apply" pos:[10,320] width:330 height:30
		
		on mlbxAnimatedObjects rightclick do (mlbxAnimatedObjects.selection = #{})
		on mlbxStaticObjects rightclick do (mlbxStaticObjects.selection = #{})
		
		on mlbxAnimatedObjects selectionEnd do (fnSetButtons mlbxAnimatedObjects btnMoveUpAnimObj btnMoveDownAnimObj)
		on mlbxStaticObjects selectionEnd do (fnSetButtons mlbxStaticObjects btnMoveUpStaticObj btnMoveDownStaticObj)	
		
		on btnRefresh pressed do 
		(		  
			local sel = selection as array
			local arr = #{}
			for o in sel where findItem mlbxAnimatedObjects.items o.name != 0 do arr[findItem mlbxAnimatedObjects.items o.name] = true
			mlbxAnimatedObjects.selection = arr
		  
			arr = #{}
			for o in sel where findItem mlbxStaticObjects.items o.name != 0 do arr[findItem mlbxStaticObjects.items o.name] = true
			mlbxStaticObjects.selection = arr  
			
			fnSetButtons mlbxAnimatedObjects btnMoveUpAnimObj btnMoveDownAnimObj
			fnSetButtons mlbxStaticObjects btnMoveUpStaticObj btnMoveDownStaticObj
			fnUpdateListsCount()
		)
		
		on btnSelList pressed do
		(
			clearSelection()
			listAnimObjs = mlbxAnimatedObjects.selection
			listStaticObjs = mlbxStaticObjects.selection
			select (for o in listAnimObjs collect AnimObjs[o])
			selectmore (for o in listStaticObjs collect StaticObjs[o])
		)
		
		on btnAddAnimObj pressed do -- Add Objects
		(
			fnAddItmsLst mlbxAnimatedObjects AnimObjs
			fnSetButtons mlbxAnimatedObjects btnMoveUpAnimObj btnMoveDownAnimObj
			fnUpdateListsCount()
		)
		
		on btnRemoveAnimObjs pressed do -- Removes Object fromt list
		(
			fnRemoveItmsLst mlbxAnimatedObjects AnimObjs
			fnSetButtons mlbxAnimatedObjects btnMoveUpAnimObj btnMoveDownAnimObj
			fnUpdateListsCount()
		)
		
		on btnMoveUpAnimObj pressed do -- Moves objects up list
		( 
			fnMoveItmUpLst mlbxAnimatedObjects AnimObjs
			fnUpdateListsCount()
		)
		
		on btnMoveDownAnimObj pressed do 
		(
			fnMoveItmDownLst mlbxAnimatedObjects AnimObjs
			fnUpdateListsCount()
		)
		
		on btnClearAnimObjs pressed do
		(
			fnClearLst mlbxAnimatedObjects AnimObjs
			fnSetButtons mlbxAnimatedObjects btnMoveUpAnimObj btnMoveDownAnimObj
			fnUpdateListsCount()
		)
		
		--//Static Objects
		on btnAddStaticObj pressed do -- Add Objects
		(
			fnAddItmsLst mlbxStaticObjects StaticObjs
			fnSetButtons mlbxStaticObjects btnMoveUpStaticObj btnMoveDownStaticObj
			fnUpdateListsCount()
		)
		
		on btnRemoveStaticObjs pressed do -- Removes Object fromt list
		(
			fnRemoveItmsLst mlbxStaticObjects StaticObjs
			fnSetButtons mlbxStaticObjects btnMoveUpStaticObj btnMoveDownStaticObj
			fnUpdateListsCount()
		)
		
		on btnMoveUpStaticObj pressed do -- Moves objects up list
		( 
			fnMoveItmUpLst mlbxStaticObjects StaticObjs
			fnUpdateListsCount()
		)
		
		on btnMoveDownStaticObj pressed do 
		(
			fnMoveItmDownLst mlbxStaticObjects StaticObjs
			fnUpdateListsCount()
		)
		
		on btnClearStaticObjs pressed do
		(
			fnClearLst mlbxStaticObjects StaticObjs
			fnSetButtons mlbxStaticObjects btnMoveUpStaticObj btnMoveDownStaticObj
			fnUpdateListsCount()
		)
		
		on btnApplyDitto pressed do
		(
			undo on
			(
				if (AnimObjs.count == StaticObjs.count) then
				(
					for i in 1 to AnimObjs.count do 
					(
						--AnimObjs[i].wirecolor = StaticObjs[i].wirecolor
						local orgPos = StaticObjs[i].pos -- store original position
						if ckbxDeleteExKeys.state do
						(
							if ckbxPosition.state do (fnDeleteKeys StaticObjs[i] 1 1)
							if ckbxRoation.state do (fnDeleteKeys StaticObjs[i] 2 2)
							if ckbxScale.state do (fnDeleteKeys StaticObjs[i] 3 3)	
						)
						
						case rbtnTransformType.state of
						(
						1: (--Relative
								posController = copy AnimObjs[i].transform.controller[1].controller  
								rotController = copy AnimObjs[i].transform.controller[2].controller
								scaController = copy AnimObjs[i].transform.controller[3].controller 
								if ckbxPosition.state do (StaticObjs[i].transform.controller[1].controller = posController)
								if ckbxRoation.state do (StaticObjs[i].transform.controller[2].controller = rotController)
								if ckbxScale.state do (StaticObjs[i].transform.controller[3].controller = scaController)
								StaticObjs[i].pos = orgPos
							)
						2: (--Absolute
								posController = copy AnimObjs[i].transform.controller[1].controller  
								rotController = copy AnimObjs[i].transform.controller[2].controller
								scaController = copy AnimObjs[i].transform.controller[3].controller 
								if ckbxPosition.state do (StaticObjs[i].transform.controller[1].controller = posController)
								if ckbxRoation.state do (StaticObjs[i].transform.controller[2].controller = rotController)
								if ckbxScale.state do (StaticObjs[i].transform.controller[3].controller = scaController)
							)
						)
					)
				)
				else
				(
					messagebox "List count mismatch!\nThe number of objects in each list must match."
				)
			)
		)
	)
	createDialog rlDitto 352 360
)