(
--//Variables
	timeConfiguration.PlaybackLoop = true
	timeConfiguration.realTimePlayback = true
--//Globals
	global StartFrame
	global StopChecker
	
	fn StopChecker StartFrame EndFrame action:#stop = 
	(
	if currentTime >= EndFrame OR (StartFrame > currentTime) then 
		(
		stopAnimation()
		if (StartFrame > currentTime) then sliderTime = EndFrame
		case action of 
		(
		#repeatForever: (StartFrame = StartFrame; sliderTime = StartFrame; playAnimation())
		default: ()
		)
		)
	StartFrame = currentTime
	)
	
--The Dialog	
rollout rlPlayRange "Play Range"
(
	global CheckAnimTime
	button btnGoToStart "Start" width:49 height:18 pos:[1,1] tooltip:"Go to start"
	checkbutton ckbtnPlay "Play" width:35 height:36 pos:[51,1]
	button btnGoToEnd "End" width:49 height:18 pos:[87,1] tooltip:"Go to end"
	spinner spnStartTime fieldwidth:39 type:#integer range:[animationRange.start,animationRange.end,animationRange.start] pos:[-1,21]
	spinner spnEndTime fieldwidth:39 type:#integer range:[animationRange.start,animationRange.end,animationRange.end] pos:[85,21]
	spinner spnJumpValue fieldwidth:25 type:#integer range:[-999999,999999,4] pos:[49,39]
	button btnJumpBackward "Jump -" width:49 height:16 pos:[1,39] tooltip:"Go to end"
	button btnJumpForward "Jump +" width:49 height:16 pos:[87,39] tooltip:"Go to end"
	
	on btnGoToStart pressed do (sliderTime = spnStartTime.value)	
	on btnGoToEnd pressed do (sliderTime = spnEndTime.value)

	
--//Jumper Button Actions
on btnJumpBackward pressed do
(
	s = (sliderTime as integer) / ticksPerFrame
	sliderTime = (s - spnJumpValue.value) as float
)
on btnJumpForward pressed do
(
	s = (sliderTime as integer) / ticksPerFrame
	sliderTime = (s + spnJumpValue.value) as float
)


--// Functions
	fn fnPlayAnimation StartFrame EndFrame loop:#once= 
	(
	unRegisterTimeCallback CheckAnimTime
	global StartFrame	
	local execString = "fn CheckAnimTime = (StopChecker " + StartFrame as string + " " + EndFrame as string + " action:#repeatForever" + ")"
	execute execString	
	sliderTime = StartFrame
	registerTimeCallback CheckAnimTime
	playAnimation()
	unRegisterTimeCallback CheckAnimTime
	)
	
--//Spinner Actions
	on spnStartTime changed value do 
	(
		spnStartTime.range = [animationRange.start,animationRange.end,value]
		if value <= animationRange.start then spnStartTime.value = animationRange.start
		if value >= (animationRange.end-1) then spnStartTime.value = animationRange.end-1
		if value >= (spnEndTime.value) then spnEndTime.value = value+1
	)
	on spnEndTime changed value do 
	(
		spnEndTime.range = [animationRange.start,animationRange.end,value]
		if value <= (animationRange.start+1) then spnEndTime.value = animationRange.start+1
		if value >= animationRange.end then spnEndTime.value = animationRange.end
		if value <= spnStartTime.value then spnStartTime.value = value-1
	)	
	
--//Play Actions
	on ckbtnPlay changed state do 
	(
		if state then 
		(
		ckbtnPlay.text = "Stop"	
		fnPlayAnimation spnStartTime.value spnEndTime.value loop:#repeatForever
		unRegisterTimeCallback CheckAnimTime
		ckbtnPlay.text = "Play"
		ckbtnPlay.checked = false
		) 
		else 
		(
		stopAnimation()
		unRegisterTimeCallback CheckAnimTime
		ckbtnPlay.text = "Play"	
		)
	)
	
	on rlPlayRange open do 
	(
	try (unRegisterTimeCallback CheckAnimTime)catch()
	)
	on rlPlayRange close do 
	(
	try (unRegisterTimeCallback CheckAnimTime)catch()
	)
		
)
	createDialog rlPlayRange 137 56 style:#(#style_SysMenu, #style_ToolWindow)
)