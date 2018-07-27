(
	try(destroyDialog ::rlBakeAnimation)catch()

	local blockSize = 100.0
	local currentFrame
	local cachOutputPath = ""

	ObjsArr = #()

	fn fnAddItmsLst lst arr =
	( -- add Objects to list
		userSel = getCurrentSelection()
		if userSel.count >= 1 do
		(
			for o in userSel do (
				if superclassof o == shape or superclassof o == GeometryClass do ( --//Only add objects that are of geometry class of shape class
				appendIfUnique arr o
				)
			)
			lst.items = for i in arr collect i.name -- update list with array
		)
	)

	fn fnRemoveItmsLst lst arr =
	( -- remove objects from list
		local currSel = lst.selection
		for i = lst.items.count to 1 by -1 where currSel[i] do (deleteItem arr i)
		lst.items = for i in arr collect i.name -- update list with array
		lst.selection = #{}
	)

	fn fnClearLst lst arr =
	( -- clears list
		for i = lst.items.count to 1 by -1 do (deleteItem arr i)
		lst.items = for i in arr collect i.name -- update list with array
		lst.selection = #{}
	)

	fn fnValidateOutputPath = (
		if cachOutputPath != "" then (
			rlBakeAnimation.btnBakeAnimation.enabled = true
		)else(
			rlBakeAnimation.btnBakeAnimation.enabled = false
		)
		rlBakeAnimation.etOutput.text = cachOutputPath
	)

--Rollout Ui
	rollout rlBakeAnimation "Bake Animation"
	(
		groupbox gpbxGeneralParameters "Objects To Bake" width:160 height:220 pos:[10,6]
		multiListBox mlbxBakeObjs "" pos:[19,28] width:140 height:12
		button btnAddObjs "+" pos:[19,190] width:47 height:24
		button btnRemoveObjs "-" pos:[66,190] width:46 height:24
		button btnClearObjs "Clear" pos:[112,190] width:47 height:24
		groupbox gpbxAnimRange "Animation Range:" width:160 height:67 pos:[10,230]
		label lbAnimStart "Start:" pos:[19,250]
		label lbAnimEnd "End:" pos:[19,270]
		spinner spnStartTime "" range:[-9999999,9999999,animationrange.start] fieldwidth:55 type:#integer pos:[92,250]
		spinner spnEndTime "" range:[-9999999,9999999,animationrange.end] fieldwidth:55 type:#integer pos:[92,270]
		groupbox gpbxAnimStorage "Baked Output:" width:160 height:80 pos:[10,300]
		label lbType "Output:" pos:[19,320]
		radiobuttons rbOutputType "" labels:#("Point Cache","Morpher") columns:1 pos:[80,320] default:1
		edittext etOutput "" readonly:true width:130 pos:[12,355] enabled:true
		button btnOutputDir "..." height:17 width:20 pos:[142,355] enabled:true
		button btnBakeAnimation "Run Bake Animation" pos:[10,386] width:160 height:28 enabled:false

		on mlbxBakeObjs rightclick do (mlbxBakeObjs.selection = #{})
		on btnAddObjs pressed do (fnAddItmsLst mlbxBakeObjs ObjsArr)
		on btnRemoveObjs pressed do (fnRemoveItmsLst mlbxBakeObjs ObjsArr)
		on btnClearObjs pressed do (fnClearLst mlbxBakeObjs ObjsArr)

		on btnOutputDir pressed do (
			userPath = getSaveFileName caption:"Choose Cache Outpu File:" filename:"c:/test/test.txt"
			--userPath = getSavePath caption:"Choose Cache Output"

			if userPath != undefined then (
				cachOutputPath = userPath
			)else(
				cachOutputPath = ""
			)
			fnValidateOutputPath()
		)

		on rbOutputType changed state do (
			if state == 1 do (
				btnOutputDir.enabled = true
				fnValidateOutputPath()
			)
			if state == 2 do (
				btnOutputDir.enabled = false
				btnBakeAnimation.enabled = true
			)
		)

		fn animTime t =
		(
			return int(t + (0 - spnStartTime.value + 1))
		)

		on btnBakeAnimation pressed do
		(
			disableSceneRedraw()

			startFrame = spnStartTime.value
			endFrame = spnEndTime.value

			loops = (ceil ((endFrame-startFrame+1)/blockSize)) as integer --//Finds number of morphs needed

			if ObjsArr.count >= 1 do
			(
				undo off
				(
					blankObj = mesh name:(uniqueName "bakedObject_" numDigits:4) numverts:0 numfaces:0
					objs = #(blankObj)

					for s in ObjsArr do append objs s

					snapshots = #()

					for o = 1 to objs.count do --//Snapshot every object, and every frame
					(
						snapshots[o] = #()
						for t = startFrame to endFrame do
						(
							slidertime = t
							snapshots[o][(animTime t)] = snapshot objs[o]
						)
					)

					for t = startFrame to endFrame do
					(
						ConvertTo snapshots[1][(animTime t)] Editable_Poly --//Convert all snapshots to editable polys
						for s = 2 to snapshots.count do
						(
							snapshots[1][(animTime t)].EditablePoly.attach snapshots[s][(animTime t)] snapshots[1][(animTime t)] --//Attach objects of correpsonding frames (1 object per frame)
						)
					)

  					base = snapshots[1][(animTime startFrame)] --//First object in the animation is the main/base object

					for i = 1 to loops do (
						--//Each loop is a batch filling the morph target
						AddModifier base (Morpher())
						base.modifiers[i].Autoload_of_targets = 1 --//Make all morphers autoreload their targets
					)

					for i = 1 to loops do (
						for o = 0 to (blockSize-1) do (
							currentFrame = (o + (i-1)*blockSize + startFrame) as integer
							if (currentFrame <= endFrame) then (
								--//Add each targeted object to the appropriate morpher
								WM3_MC_BuildFromNode base.modifiers[i] (o as integer + 1) snapshots[1][(animTime currentFrame)]
								WM3_MC_Rebuild base.modifiers[i] (animTime (currentFrame-1))
								with animate on
								(
									at time (currentFrame-1) WM3_MC_SetValue base.modifiers[i] (o as integer + 1) 0.0
									at time currentFrame WM3_MC_SetValue base.modifiers[i] (o as integer + 1) 100.0
									at time (currentFrame+1) WM3_MC_SetValue base.modifiers[i] (o as integer + 1) 0.0
								)
							)
						)
					)

					for s = 2 to snapshots[1].count do
					(
						delete snapshots[1][s]
					)
					snapshots = undefined

 					base.wirecolor = blue
 					base.name = "BakedObjects"
					select base

					case rbOutputType.state of (
						1: (
								ptCache = (Point_Cache fileName:(cachOutputPath + "_.xml") recordStart:startFrame recordEnd:endFrame)
								addmodifier base ptCache
								cacheOps.RecordCache ptCache -- Perform point cache record.

								--//Delete morphers
								morpherCount = base.modifiers.count
								m = 1
								while m <= morpherCount do
								(
									if classof base.modifiers[m] == Morpher do
									(
										deleteModifier base m
										m -= 1
										morpherCount -= 1
									)
									m += 1
								)

								--messagebox "Sucessfully Completed"
							)
						2: messagebox "Sucessfully Completed"
					)
				)
			)
			enableSceneRedraw()
			completeRedraw()
		)
	)
	createDialog rlBakeAnimation 180 424
)