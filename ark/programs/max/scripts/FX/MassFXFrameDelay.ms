try(destroyDialog ::rlMassFXDelay)catch()
rollout rlMassFXDelay "MassFX Frame Delay"
(
	local targetObj = undefined
	
	/*
	Sorts objects based on their distance from the targetObj
	------------------------------------------------------------------------------------------------------------------------------*/
	fn fnDistanceSortedArray =
	(
		fn dist_comp obj1 obj2 =
		(
			distance targetObj obj1 - distance targetObj obj2
		)
		local objs = selection as array
		
		qsort objs dist_comp		
		return objs
	)

	/*
	Sets the frame on the objects MASSFX modifiers
	------------------------------------------------------------------------------------------------------------------------------*/
	fn fnProcessTiming arr: =
	(
		setCommandPanelTaskMode #create
		arr = if rlMassFXDelay.cbSelOrder.state then arr else if targetObj != undefined AND isValidNode targetObj then fnDistanceSortedArray() else arr
		totalDuration = rlMassFXDelay.spnTotalDuration.value
		seqSize = (selection.count/totalDuration)
		startframe = rlMassFXDelay.spnInitialStart.value
		endframe = (startframe + totalDuration)
		loopCounter = 0
		
		seqIdx = 1
		for obj in arr do
		(
			loopCounter += 1
			
			if loopCounter == (seqSize+1) do
			(
				seqIdx +=1
				loopCounter = 1
			)
			
			--//Place frame number manipulation here
			if classof (obj.modifiers[1]) == MassFX_RBody do
			(
				wiggle = (random (rlMassFXDelay.spnWiggleMin.value)(rlMassFXDelay.spnWiggleMax.value))
				delay = seqIdx + wiggle + startframe
					
				obj.modifiers[1].type = 2
				obj.modifiers[1].manualSetup = on
				obj.modifiers[1].switchType = on
				obj.modifiers[1].switchTypeAtFrame = delay
			)
			--format "%_%\n" seqIdx obj.name
		)
		
		-- for variation from yellow to blue
		for i = 1 to (cnt = arr.count) do
		if cnt != 0 do
		(
		  local k = (i as float) / cnt
		  arr[i].wirecolor = red * (1 - k) + yellow * k
		)
	)
	
	pickbutton pbtnTargetObj "Pick Distance Object" width:180 height:24 pos:[10,10]
	label lbInitialStart "Initial Start Frame:" pos:[10,50]
	spinner spnInitialStart "" range:[-999999999,999999999,1] type:#integer fieldwidth:70 pos:[108,50]
	label lbTotalDuration "Total Duration:" pos:[10,75]
	spinner spnTotalDuration"" range:[1,999999999,10] type:#integer fieldwidth:70 pos:[108,75]
	
	groupbox gpDelayVariation "Delay Variation" width:180 height:65 pos:[10,100]
	label lbMinVariation "Min:" pos:[20,120]
	spinner spnWiggleMin "" range:[-999999999,999999999,-1] type:#integer fieldwidth:60 pos:[108,120]
	label lbMaxVariation "Max:" pos:[20,140]
	spinner spnWiggleMax "" range:[-999999999,999999999,1] type:#integer fieldwidth:60 pos:[108,140]
	checkbox cbSelOrder "Selection Order" pos:[100,175]
	button btnGo "GO" width:180 height:30 pos:[10,200]
	
	
	on pbtnTargetObj picked obj do
	(
		if obj != undefined do
		(
			targetObj = obj
			pbtnTargetObj.text = obj.name
			btnGo.enabled = true
		)
	)
	
	on btnGo pressed do
	(
		fnProcessTiming arr:(selection as array)
	)
	
)
createDialog rlMassFXDelay 200 240 style:#(#style_SysMenu, #style_ToolWindow)
