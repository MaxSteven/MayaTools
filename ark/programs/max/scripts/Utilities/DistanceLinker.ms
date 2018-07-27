try (destroydialog ::rlDistanceLinker) catch()
rollout rlDistanceLinker "Distance Linker" width:312 height:288
(
	button btnSelectNoParents "Select Objs w/o Parents" pos:[10,10] width:130 height:20
	button ui_btn_selectnochildren "Select Objs w/o Children" pos:[150,10] width:130 height:20
	listbox ui_lbx_children "Children:" pos:[10,40] width:130 height:10
	listbox ui_lbx_parents "Parents:" pos:[150,40] width:130 height:10
	button btn_refreshchildren "Refresh" pos:[10,192] width:130 height:24
	button btn_refreshparents "Refresh" pos:[150,192] width:130 height:24
	button ui_btn_parent "Run Distance Linker" pos:[10,230] width:270 height:30
	
	local childobjects = #()
	local parentobjects = #()
		
	on btn_refreshchildren pressed do ---need to subract from parent array and refresh both arrays
	(
		sel = selection as array
		for o = 1 to sel.count do
		(
			for i = 1 to parentobjects.count do
			(
				testval = (finditem parentobjects sel[o])
				if testval > 0 then
				(
					deleteitem parentobjects testval
				)
			)
		)
		--------------------
		parentuinames = #()
		for o in parentobjects do
		(
			append parentuinames o.name
		)
		ui_lbx_parents.items = parentuinames
		-----------------
		childobjects = sel
		childuinames = #()
		for o in childobjects do
		(
			append childuinames o.name
		)
		ui_lbx_children.items = childuinames
	)
	
	on btn_refreshparents pressed do  ---need to subract from child array and refresh both arrays
	(
		sel = selection as array
		for o = 1 to sel.count do
		(
			for i = 1 to childobjects.count do
			(
				testval = (finditem childobjects sel[o])
				if testval > 0 then
				(
					deleteitem childobjects testval
				)
			)
		)
		--------------------
		childuinames = #()
		for o in childobjects do
		(
			append childuinames o.name
		)
		ui_lbx_children.items = childuinames
		-----------------
		parentobjects = sel
		parentuinames = #()
		for o in parentobjects do
		(
			append parentuinames o.name
		)
		ui_lbx_parents.items = parentuinames
	)
		
	on ui_btn_parent pressed do
	(
		local childcount = childobjects.count
		local parentcount = parentobjects.count
		if childcount > 0 then
		(
			if parentcount > 0 then
			(
				for i = 1 to childcount do
				(
					distarray = #()
					for o = 1 to parentcount do
					(
						append distarray (distance childobjects[i].center parentobjects[o].center) --center is property that returns point3 center of boundingbox
						min = amin distarray
						closestobj = parentobjects[finditem distarray min]
						childobjects[i].parent = undefined
						if (finditem childobjects[i].children closestobj) > 0 then
						(
							deleteitem childobjects[i].children closestobj
						)
						else()
						childobjects[i].parent = closestobj
					)
				)
			)
			else 
			(
				Messagebox ("No Parent Objects... wtf")
			)
		)
		else 
		(
			Messagebox ("No Children Objects... wtf!?")
		)
	)
	
	on ui_btn_selectnochildren pressed do
	(
		nochildren = #()
		for o in parentobjects do
		(
			if o.children.count == 0 then
				append nochildren o
		)
		max select none
		select nochildren
	)
	
	on btnSelectNoParents pressed do
	(
		noParents = #()
		noParents = for obj in objects where obj.parent == undefined collect obj
		max select none
		select noParents
	)
)
createdialog rlDistanceLinker 290 270 style:#(#style_SysMenu, #style_ToolWindow)
