/*
-- Duration
	• 
-- End to End (LEVELS: Object) 
	- Moves keys to align up against each other one after another in time with the option of direction and overlap amount
	• Props
		- first selected key of each Level
		- last selected key of each Level
-- Random
	- Move each level's key/s in time randomly with the option of a frame snap
	• Props
		- selected key/s of each Level
		- selected key/s of each Level
-- Shift
	- Moves each level's key/s in time "x" amount or with an incremental multiplier
	• Props
		- selected key/s of each Level
		- selected key/s of each Level
-- Time Slider
	- Moves keys based on direction to be aligned to the time slider, all objects either "start" or "end" at time of slider
	• Props
		- first or last selected key of each Level
*/

try(destroyDialog ::rlTimeShifter)catch()
rollout rlTimeShifter "Time Shifter"
(
	struct dataSt (n,trackName,controller)
	struct mapper (
		minOffset,
		maxOffset,
		fn map keyTime = return keyTime + random minOffset maxOffset
	)
	
	local _dataArr = #()
	local _keyArr = #()
	
	fn recurseSubAnims n = ( -- this function returns all the animated controllers and there sub controllers
		for i=1 to n.numSubs do
		(
			con=(getSubAnim n i).controller
			if con!=undefined do 
			(
				if (numKeys con)>0 do
				(
					d = dataSt()
					d.n=n
					d.trackName= (getSubAnimName n i)
					d.controller=con
					append _dataArr d
				)
			)
			recurseSubAnims n[i]
		)
	)
	
	fn recurseGetKeys n = ( -- this function returns all the frame numbers of the currently selected keys of the supplied object
		for i=1 to n.numSubs do
		(
			con=(getSubAnim n i).controller
			if con!=undefined do 
			(
				if (numKeys con)>0 do
				(
					for k in con.keys where k.selected do (
						appendifUnique _keyArr (k.time as integer/ticksPerFrame)
					)
				)
			)
			recurseGetKeys n[i]
		)
		sort _keyArr --//order keys lowest to highest
		return _keyArr
	)
	
	fn fnGetKeys theNodes = (
		_keyArr = #() --used for the collection of keys for the looping of each node
		_tmpAr = #() --collection of keys from entire supplied collection of nodes
		for n in theNodes do (
			_keyArr = recurseGetKeys n -- replace array with new keys
			join _tmpAr _keyArr
		)
		sort _tmpAr
		return _tmpAr
	)
	
	fn fnTimeShiftRandom level:"Key" range:[0,0] frameSnap:true = (
		_objArr = selection as array
		minVal = if frameSnap then (range[1] as integer) else (range[1] as float)
		maxVal = if frameSnap then (range[2] as integer) else (range[2] as float)
		
		if level == "Key" do (-- each Key individually
			for obj in _objArr do (
				mapKeys obj (mapper minOffset:minVal maxOffset:maxVal) #selection
			)			
		)
		if level == "Object" do (-- each Object individually
			for obj in _objArr do (
				moveVal = random minVal maxVal
				moveKeys obj moveVal #selection 
			)
		)
		if level == "Selection" do (-- entire Selection
			moveVal = random minVal maxVal
			for obj in _objArr do (
				moveKeys obj moveVal #selection 
			)
		)
		if level == "Track" do (-- each track individually
			trackNames=#()
			for obj in _objArr do (
				_dataArr = #()
				recurseSubAnims obj -- get all controllers
				
				for d in _dataArr do -- apply to each controller
				(
					moveVal = random minVal maxVal
					moveKeys d.controller moveVal #selection
				)
			)
		)
	)
	
	fn fnTimeShiftShift level:"Key" shiftVal:0.0 incremental:true = (
		_objArr = selection as array
		
		if level == "Key" do (-- each Key individually
			trackNames=#()
			for obj in _objArr do (
				_dataArr = #()
				recurseSubAnims obj -- get all controllers
				
				for d in _dataArr do -- apply to each controller
				(
					keyCount = d.controller.keys.count
					if keyCount > 0 do
					(
						for k = 1 to keyCount where (isKeySelected d.controller k) do
						(
							moveVal = if incremental then (shiftVal * k) else shiftVal
							try(d.controller.keys[k].time += moveVal)catch() --bugs out on parent controllers ex:Position_XYZ, Euler_XYZ
						)
					)
				)
			)
		)
		if level == "Object" do (-- each Object individually
			for i = 1 to _objArr.count do (
				obj = _objArr[i]
				moveVal = if incremental then (shiftVal * i) else shiftVal
				moveKeys obj moveVal #selection 
			)
		)
		if level == "Selection" do (-- entire Selection
			moveVal = shiftVal
			for obj in _objArr do (
				moveKeys obj moveVal #selection 
			)
		)
		if level == "Track" do (-- each track individually
			trackNames=#()
			for obj in _objArr do (
				_dataArr = #()
				recurseSubAnims obj -- get all controllers
				
				for i = 1 to _dataArr.count do -- apply to each controller
				(
					d = _dataArr[i]
					moveVal = if incremental then (shiftVal * i) else shiftVal
					moveKeys d.controller moveVal #selection
				)
			)
		)
	)
	
	fn fnTimeShiftSliderTime level:"Object" direction:1 = ( --1 = "after" ,  2 = "before"
		_objArr = selection as array
		
		if _objArr.count >= 1 do (
			if level == "Object" do (-- each Object individually
				for obj in _objArr do
				(
					_ObjKeys = fnGetKeys #(obj) --variable contains array of selected keys
					
					if _ObjKeys.count >= 1 do (
						_heroKey = if direction == 2 then _ObjKeys[_ObjKeys.count] else _ObjKeys[1]-- the objects first or last key
						_sliderTime = slidertime as integer/ticksPerFrame
						_timeDif = (_sliderTime - _heroKey) --default of "0" results in no overlap
						moveKeys obj _timeDif #selection	
					)
				)
			)
			if level == "Selection" do (-- entire Selection
				
				_colKeys = fnGetKeys _objArr --variable contains array of all selected keys
				
				if _colKeys.count >= 1 do (
					_heroKey = if direction == 2 then _colKeys[_colKeys.count] else _colKeys[1]-- the objects first or last key
					_sliderTime = slidertime as integer/ticksPerFrame
					_timeDif = (_sliderTime - _heroKey) --default of "0" results in no overlap
					moveKeys _objArr _timeDif #selection	
				)
			)
		)
	)
	
	fn fnTimeShiftEndToEnd level:"Object" overlap:0 direction:2 = ( --1 = "after" ,  2 = "before"
		_objArr = selection as array
		
		if _objArr.count > 1 do (
			if level == "Object" do (-- each Object individually
				for i = 2 to _objArr.count by 1 do
				(
					_preObj = _objArr[i-1]
					_nextObj = _objArr[i]
					_preObjKeys = fnGetKeys #(_preObj) --variable contains array of selected keys
					_nextObjKeys = fnGetKeys #(_nextObj) --variable contains array of selected keys
					
					if _preObjKeys.count >= 1 do (
						_preEndKey = if direction == 2 then _preObjKeys[1] else _preObjKeys[_preObjKeys.count] -- previous objects ending animation KEY
						_nextStartKey = if direction == 2 then _nextObjKeys[_nextObjKeys.count] else _nextObjKeys[1] -- next objects starting animation KEY
						if direction == 2 then (overlap *= -1) else overlap
						_timeDif = (_preEndKey - _nextStartKey) - overlap --default of "0" results in no overlap
						moveKeys _nextObj _timeDif #selection	
					)
				)
			)
		)
	)
	
	label lbMethod "Method:" pos:[20,13]
	dropdownlist dlMethod items:#("Duration","End to End","Random","Shift","Time Slider") selection:3 width:100 pos:[100,10]
	--Properties
	groupbox gpProperties "Properties" width:200 height:110 pos:[10,43]
		label lbLevel "Level:" pos:[19,63]
		dropdownlist dlLevel items:#("Key","Object","Selection","Track") width:100 pos:[100,60]
		--random
		label lbOffsetRange "Offset range:" pos:[19,90] visible:true
		spinner spnOffsetMin fieldwidth:40 range:[-9999999,9999999,-2.5] type:#float scale:0.1 pos:[97,90] visible:true
		spinner spnOffsetMax fieldwidth:40 range:[-9999999,9999999,2.5] type:#float scale:0.1 pos:[149,90] visible:true
		label lbFrameSnap "Frame Snap:" pos:[19,120] visible:true
		checkbox cbFrameSnap "" width:20 checked:false pos:[100,120] tooltip:"The wiggle value will be a whole number." visible:true
		--shift
		label lbShiftAmount "Shift amount:" pos:[19,90] visible:false
		spinner spnShiftAmount fieldwidth:40 range:[-9999999,9999999,1.0] type:#float scale:0.1 pos:[97,90] visible:false
		label lbShiftIncremental "Incremental:" pos:[19,120] visible:false
		checkbox cbShiftIncremental "" width:20 checked:false pos:[100,120] tooltip:"The wiggle value will be a whole number." visible:false
		--end to end
		label lbOverlap "Overlap:" pos:[19,90] visible:false
		spinner spnOverlap"" fieldwidth:40 range:[-9999999,9999999,0] type:#integer pos:[97,90] visible:false
		label lbDirection "Direction:" pos:[19,120] visible:false
		radiobuttons rbDirection "" labels:#("After","Before") pos:[100,120] visible:false
		--time slider
		label lbTsDirection "Direction:" pos:[19,90] visible:false
		radiobuttons rbTsDirection "" labels:#("After","Before") pos:[100,90] visible:false
	button btnRunTimeShifter "Run Time Shifter" width:200 height:30 pos:[10,165]
	
	fn fnUpdateProps = (
		method = dlMethod.selected
		
		if method == "Random" do (
			dlLevel.items = #("Key","Object","Selection","Track")
			lbOffsetRange.visible = spnOffsetMin.visible = spnOffsetMax.visible = lbFrameSnap.visible = cbFrameSnap.visible = true --random
			lbShiftAmount.visible = spnShiftAmount.visible = lbShiftIncremental.visible = cbShiftIncremental.visible = false -- shift
			lbOverlap.visible = spnOverlap.visible = lbDirection.visible = rbDirection.visible = false --end to end
			rbTsDirection.visible = lbTsDirection.visible = false --time slider
		)
		
		if method == "Shift" do (
			dlLevel.items = #("Key","Object","Selection","Track")
			lbOffsetRange.visible = spnOffsetMin.visible = spnOffsetMax.visible = lbFrameSnap.visible = cbFrameSnap.visible = false --random
			lbShiftAmount.visible = spnShiftAmount.visible = lbShiftIncremental.visible = cbShiftIncremental.visible = true -- shift
			lbOverlap.visible = spnOverlap.visible = lbDirection.visible = rbDirection.visible = false --end to end
			rbTsDirection.visible = lbTsDirection.visible = false --time slider
		)
		
		if method == "Duration" do (
			dlLevel.items = #("Fill me in")
			lbOffsetRange.visible = spnOffsetMin.visible = spnOffsetMax.visible = lbFrameSnap.visible = cbFrameSnap.visible = false --random
			lbShiftAmount.visible = spnShiftAmount.visible = lbShiftIncremental.visible = cbShiftIncremental.visible = false -- shift
			lbOverlap.visible = spnOverlap.visible = lbDirection.visible = rbDirection.visible = false --end to end
			rbTsDirection.visible = lbTsDirection.visible = false --time slider
		)
		
		if method == "End to End" do (
			dlLevel.items = #("Object")
			lbOffsetRange.visible = spnOffsetMin.visible = spnOffsetMax.visible = lbFrameSnap.visible = cbFrameSnap.visible = false --random
			lbShiftAmount.visible = spnShiftAmount.visible = lbShiftIncremental.visible = cbShiftIncremental.visible = false -- shift
			lbOverlap.visible = spnOverlap.visible = lbDirection.visible = rbDirection.visible = true --end to end
			rbTsDirection.visible = lbTsDirection.visible = false --time slider
		)
		
		if method == "Time Slider" do (
			dlLevel.items = #("Object","Selection")
			rbTsDirection.visible = lbTsDirection.visible = true --time slider
			lbOffsetRange.visible = spnOffsetMin.visible = spnOffsetMax.visible = lbFrameSnap.visible = cbFrameSnap.visible = false --random
			lbShiftAmount.visible = spnShiftAmount.visible = lbShiftIncremental.visible = cbShiftIncremental.visible = false -- shift
			lbOverlap.visible = spnOverlap.visible = lbDirection.visible = rbDirection.visible = false --end to end
		)
	)
	
	on dlMethod selected idx do (
		fnUpdateProps()
	)
	
	on btnRunTimeShifter pressed do (
		method = dlMethod.selected
		selLevel = dlLevel.selected
		
		clearlistener()
		t1 = timestamp()
		m1 = heapfree
		
		if method == "Random" do (
			fnTimeShiftRandom level:selLevel range:[spnOffsetMin.value,spnOffsetMax.value] frameSnap:cbFrameSnap.state
		)
		
		if method == "Shift" do (
			fnTimeShiftShift level:selLevel shiftVal:(spnShiftAmount.value as float) incremental:cbShiftIncremental.state
		)
		
		if method == "Duration" do (
		)
		
		if method == "End to End" do (
			fnTimeShiftEndToEnd level:selLevel overlap:spnOverlap.value direction:rbDirection.state
		)
		
		if method == "Time Slider" do (
			fnTimeShiftSliderTime level:selLevel direction:rbTsDirection.state
		)
		format "time:% memory:%\n" (timestamp() - t1) (m1 - heapfree)
	)
	
)
createDialog rlTimeShifter  220 205 style:#(#style_SysMenu, #style_ToolWindow)