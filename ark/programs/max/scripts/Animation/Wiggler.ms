--//add lock for wiggle (offset) 
--//refresh list is buggy
--Group Selection
 --1. Scrambled = for each object do random value for each key
 --2. Linear = for selection do random value once
 
--Unchecked Group Selection
 --1. Scrambled = for each object do random value for each key
 --2. Linear = for each object do random value once


try(destroyDialog ::rlWiggler)catch()
rollout rlWiggler "Wiggler"
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
		rlWiggler.lbxAvailTracks.items = trackCanvas			
	)
	
	
	fn selectTracks = 
	(
		selectedTracks = #()
		itm = rlWiggler.lbxAvailTracks.selection
		sel =  (itm as array)[1]
		if sel != undefined then for i = rlWiggler.lbxAvailTracks.items.count to 1 by -1 where itm[i] do append selectedTracks trackCanvas[i]				
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
		rlWiggler.lbxAvailTracks.selection = #{}
	)
	
	
	fn fnScrambledKeys = 
	(		
		for obj in selection do 
		(
			animatedTracks = getKeyedControllers obj
			print "no"
			for tag in animatedTracks do
			(
				_controller = getController obj tag
				theId = _controller.name
				
				userKeys = _controller.controller.keys
				if userKeys.count > 0 do
				(
					for k = 1 to userKeys.count where (isKeySelected _controller.controller k) do
					(
						val = if rlWiggler.cbxSnapFrames.state then ((random (rlWiggler.spnWiggleMin.value as integer) (rlWiggler.spnWiggleMax.value as integer))as integer) else ((random (rlWiggler.spnWiggleMin.value as float) (rlWiggler.spnWiggleMax.value as float)) as float)
						userKeys[k].time += val
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
	label lbWiggleType "Wiggle Type:" pos:[10,230]
	radiobuttons rbtnWiggleType "" labels:#("Scrambled","Linear") pos:[93,230] tooltip:"Scrambled: Each selected key gets a unique wiggle value.   Linear: Each Object's selected animation will be uniquely wiggled as a whole."
	label lbSnapFrames "Snap frames:" pos:[10,255]
	checkbox cbxSnapFrames "" width:20 checked:false pos:[93,255] tooltip:"The wiggle value will be a whole number."
	label lbGroup "Group Selection:" pos:[10,280]
	checkbox ckbxGroup "" checked:false width:20 pos:[93,280] tooltip:"Treats entire selection as one object. Resulting in the entire selection only having one random wiggle value applied to all the objects."
	groupbox gbxKeyVariation "Wiggle Variation" width:200 height:66 pos:[10,305]
	label lbFrOffsetMax "Max:" pos:[20,330]
	label lbFrOffsetMin "Min:" pos:[20,350]
	spinner spnWiggleMax fieldwidth:90 range:[-9999999,9999999,2.5] type:#float scale:0.1 pos:[90,330]
	spinner spnWiggleMin fieldwidth:90 range:[-9999999,9999999,-2.5] type:#float scale:0.1 pos:[90,350]	
	button btnRunWiggler "Run Wiggler" height:30 width:200 pos:[10,380] enabled:true
	
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
		linearOffset = if cbxSnapFrames.state then ((random (spnWiggleMin.value as integer) (spnWiggleMax.value as integer))as integer) else ((random (spnWiggleMin.value as float) (spnWiggleMax.value as float)) as float)
		
		if ckbxGroup.checked then
		(
			case rbtnWiggleType.state of
			(
				1: (
					print "Scrambled Group"
					fnScrambledKeys()
				)
				2: (
					print "Linear Group"
					for obj in selection do
					(
						moveKeys obj linearOffset #selection
					)
				)
			)
			)else(
			case rbtnWiggleType.state of
			(
				1: (
					print "Scrambled Objects"
					fnScrambledKeys()
				)
				2: (
					print "Linear Objects"
					for obj in selection do
					(
						linearObjOffset = if cbxSnapFrames.state then ((random (spnWiggleMin.value as integer) (spnWiggleMax.value as integer))as integer) else ((random (spnWiggleMin.value as float) (spnWiggleMax.value as float)) as float)
						moveKeys obj linearObjOffset #selection
					)
				)
			)
		)
	)
	
	on btnDeleteTracks pressed do
	(
		deleteTracks()
	)
	
	on rlWiggler open do
	(
		updateTracks()
		callbackContainer = NodeEventCallback mouseUp:false delay:500 all:updateHandler
	)
	
	on rlWiggler close do
	(
		callbackContainer = undefined; gc light:true;
	)
)
createDialog rlWiggler  220 420 style:#(#style_SysMenu, #style_ToolWindow)