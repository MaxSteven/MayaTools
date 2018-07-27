--//add lock for wiggle (offset) 
--//refresh list is buggy
--Group Selection
 --1. Scrambled = for each object do random value for each key
 --2. Linear = for selection do random value once
 
--Unchecked Group Selection
 --1. Scrambled = for each object do random value for each key
 --2. Linear = for each object do random value once


try(destroyDialog ::rlAmplifier)catch()
rollout rlAmplifier "Amplifier"
(
	/*Variables*/
	local trackCanvas = #()
	
	/*Functions*/
	fn registerTrack track = (
		theID = track.name			
		searchIndex = findItem trackCanvas theID
		if searchIndex == 0 then (
			append trackCanvas theID			
		)			
	)
	
	
	fn getKeyedControllers theObject =
	(
		tags = #()
		scanList = #(#(theObject,#()))
		cnt = 0
		while cnt < scanList.count do
		(
			cnt +=1
			currentObj = scanList[cnt][1]
			currentTag = deepCopy scanList[cnt][2]
			childCount = try(currentObj.numSubs)catch(0)
			if(childCount > 0) then
			(		
				for i = 1 to currentObj.numSubs do
					(							
						newTag = deepCopy currentTag
						append newTag i
						append scanList #(currentObj[i], newTag)
					)
			) else
			(
				if currentObj != undefined then (
					keyCount = try(currentObj.keys.count) catch(0)
					--if keyCount > 0 then if(keysAreUnique currentObj.keys) then append tags (deepCopy currentTag)		
					if keyCount > 0 then append tags (deepCopy currentTag)					
				)
			)
		)		
		return tags 
	)
	
	
	fn getController _object _id _at:"this"=
	(			
		_idlength = _id.count
		if _at == "parent" then _at = -1
		if _at == "root" then _at = 1
		if _at == "this" then _at = _idlength
		if _at < 0 then
		(
			_newIndex = _idlength + _at
			if _newIndex <= 0 then _newIndex = 1			
		)
		if _at > 0 then
		(
			_newIndex = _at
			if _newIndex > _idlength then _newIndex = _idlength
		)
		if _newIndex == undefined then _newIndex = _idlength
		_ctrl = _object[_id[1]]
		for i = 2 to _newIndex do	_ctrl = _ctrl[_id[i]]	
		return _ctrl
	)
	
	
	fn updateTracks =
	(
		trackCanvas = #()
		totalObjects = selection.count
		if totalObjects > 0 then
		(	
			for obj in selection do 
			(
				animatedTracks = getKeyedControllers obj
				for tag in animatedTracks do
				(
					_controller = getController obj tag
					registerTrack _controller
				)						
			)				
		)
		rlAmplifier.lbxAvailTracks.items = trackCanvas			
	)
	
	
	fn selectTracks = 
	(
		selectedTracks = #()
		itm = rlAmplifier.lbxAvailTracks.selection
		sel =  (itm as array)[1]
		if sel != undefined then for i = rlAmplifier.lbxAvailTracks.items.count to 1 by -1 where itm[i] do append selectedTracks trackCanvas[i]				
		for obj in selection do 
		(
			animatedTracks = getKeyedControllers obj
			for tag in animatedTracks do
			(
				_controller = getController obj tag
				deselectKeys _controller
				theId = _controller.name
				searchIndex = findItem selectedTracks theID
				if searchIndex != 0 then selectKeys _controller
			)						
		)						
		affectSelectedOnly = true
	)
	
	
	fn deleteTracks =
	(
		undo on 
		(
			for obj in selection do 
			(
				animatedTracks = getKeyedControllers obj
				for tag in animatedTracks do
				(
					_controller = getController obj tag
					deleteKeys _controller #selection
				)						
			)
		)
		rlAmplifier.lbxAvailTracks.selection = #{}
	)
	
	
	fn fnAmplifyKeys = 
	(		
		clearlistener()
		_animObjs = for obj in selection collect obj
			
		for o = 1 to _animObjs.count do 
		(
			obj = _animObjs[o]
			singleVAL = random (rlAmplifier.spnWiggleMin.value) (rlAmplifier.spnWiggleMax.value) --one random value per-Object "united"
				
			animatedTracks = getKeyedControllers obj
			for tag in animatedTracks do
			(
				_controller = getController obj tag
				theId = _controller.name
				
				userKeys = _controller.controller.keys
				if userKeys.count > 0 do
				(
					start = if rlAmplifier.cbSkipFirstKey.state then 2 else 1
					end = if rlAmplifier.cbSkipLastKey.state then (userKeys.count-1) else userKeys.count
					for k = start to end where (isKeySelected _controller.controller k) do
					(
						multiVAL = random (rlAmplifier.spnWiggleMin.value) (rlAmplifier.spnWiggleMax.value) --one random value per-Key "unique"
						theVal = if rlAmplifier.rbAmplifierFormat.state == 1 then multiVAL else singleVAL
						if rlAmplifier.cbOrderIntensify.state do theVal *= o --intensify in order
						theKeysValue = userKeys[k].value += theVal
						if rlAmplifier.cbSnapIntegers.state do userKeys[k].value = userKeys[k].value as integer --snap to whole integer
						--format "%----%\n" obj.name theKeysValue
					)
				)
			)						
		)						
	)

	fn updateHandler ev nd =
	(
		updateTracks()			
	)
	
	groupbox gbxAvailableTracks "Availabe Tracks" width:200 height:210 pos:[10,6]
	button btnDeleteTracks "Delete" width:180 height:16 pos:[20,188]
	multiListBox lbxAvailTracks width:180 height:12 items:#() pos:[20,26]
	label lbKeysFormat "Keys format:" pos:[10,230]
	radiobuttons rbAmplifierFormat "" labels:#("Unique","United") pos:[102,230] tooltip:"Unique: Each selected key gets a unique amplified value.   United: Each object's selected animation will be uniquely amplified as a whole."
	label lbSnapIntegers "Snap to integers:" pos:[10,255]
	checkbox cbSnapIntegers "" width:20 checked:false pos:[103,255] tooltip:"The amplifier value will be a whole number."
	label lbSkipFirstKey "Skip first key:" pos:[10,280]
	checkbox cbSkipFirstKey "" width:20 checked:true pos:[103,280] tooltip:"Skips the first key in each object's selected keys."
	label lbSkipLastKey "Skip last key:" pos:[10,305]
	checkbox cbSkipLastKey "" width:20 checked:false pos:[103,305] tooltip:"Skips the last key in each object's selected keys."
	label lbOrderIntensify "Order Intensify:" pos:[10,330]
	checkbox cbOrderIntensify "" width:20 checked:false pos:[103,330] tooltip:"Based of the order of the selected objects the applied amplifier value will increase."
	groupbox gbxKeyVariation "Amplifier Variation" width:200 height:75 pos:[10,350]
		label lbFrOffsetMax "Max:" pos:[20,375]
		label lbFrOffsetMin "Min:" pos:[20,395]
		spinner spnWiggleMax fieldwidth:90 range:[-9999999,9999999,2.5] type:#float scale:0.1 pos:[90,375]
		spinner spnWiggleMin fieldwidth:90 range:[-9999999,9999999,0.0] type:#float scale:0.1 pos:[90,395]	
		button btnRunWiggler "Run Wiggler" height:30 width:200 pos:[10,430] enabled:true
	
	on rbtnKeysAffected changed state do (
		case state of (
			1: (btnRunWiggler.enabled = true)
			2: (btnRunWiggler.enabled = false)
		)
	)

	on lbxAvailTracks selected itm do (
		selectTracks()
	)
	
	on lbxAvailTracks doubleclicked itm do (
		lbxAvailTracks.selection=#{1..(lbxAvailTracks.items.count)}
		selectTracks()
	)
	
	on btnRunWiggler pressed do
	(		
		fnAmplifyKeys()
	)
	
	on btnDeleteTracks pressed do
	(
		deleteTracks()
	)
	
	on rlAmplifier open do
	(
		updateTracks()
		callbackContainer = NodeEventCallback mouseUp:false delay:500 all:updateHandler
	)
	
	on rlAmplifier close do
	(
		callbackContainer = undefined; gc light:true;
	)
)
createDialog rlAmplifier  220 470 style:#(#style_SysMenu, #style_ToolWindow)