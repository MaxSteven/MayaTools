try(destroyDialog ::rlVisibility)catch()

rollout rlVisibility "Visibility"
(
	local keyType = #linear
	
	--//Functions	
	fn fnkeyType state = -- Updates radiobutton key type
	(
		case state of
		(
			1: keyType = #step
			2: keyType = #linear
			3: keyType = #auto
		)
		print keyType
	)
	
	fn fnAddVisKey vis type= -- Add Visibility Key
	(
		for Obj in selection do
		(
			if classOf Obj[1].track != bezier_float do (Obj.visibility = bezier_float())
			VisTrack = Obj.visibility.controller
			newKey = addNewKey VisTrack currentTime --#select
			newKey.value = vis
			newKey.inTangentType = type 
			newKey.outTangentType = type
			--print ("Keys" + " " + sliderTime as string)
		)
	)
	
	fn fnDeleteVisKey = -- Delete Visibility Key
	(
		for Obj in selection do
		(
			if classOf Obj[1].track == bezier_float do 
			(
				VisTrack = Obj.visibility.controller
				deselectKeys VisTrack
				selectKeys VisTrack currentTime
				deleteKeys VisTrack #selection 
			)
		)
	)
	
	fn fnDeleteVisTrack = -- Delete Visibility Key
	(
		for Obj in selection do
		(
			if classOf Obj[1].track == bezier_float do 
			(
				VisTrack = Obj.visibility.controller
				VisTrack.value = 1.0
				deselectKeys VisTrack
				selectKeys VisTrack
				deleteKeys VisTrack #selection 
			)
		)
	)
	
	--//UI Controls
	groupbox gpbxKeyType "" width:198 height:38 pos:[10,6]
	label lbKeyType "Key:" pos:[19,21]
	radiobuttons rbtnkeyType "" width:52 height:48 labels:#("Step", "Linear", "Bezier") default:2 columns:3 pos:[45,21]
	button btnInvisible "Invisible" width:99 height:28 pos:[10,51] 
	button btnVisible "Visible" width:99 height:28 pos:[109,51]  
	button btnVis01 ".1" width:22 height:20 pos:[10,79] 
	button btnVis02 ".2" width:22 height:20 pos:[32,79] 	
	button btnVis03 ".3" width:22 height:20 pos:[54,79] 
	button btnVis04 ".4" width:22 height:20 pos:[76,79] 
	button btnVis05 ".5" width:22 height:20 pos:[98,79] 
	button btnVis06 ".6" width:22 height:20 pos:[120,79] 
	button btnVis07 ".7" width:22 height:20 pos:[142,79] 		
	button btnVis08 ".8" width:22 height:20 pos:[164,79] 
	button btnVis09 ".9" width:22 height:20 pos:[186,79]
	label lbEdgeB style_sunkenedge:true width:198 height:20 pos:[10,109]
	button btnDelVisKey "X - Visibility Key" width:98 height:18 pos:[11,110]
	button btnDelVisTrack "X - Visibility Track" width:98 height:18 pos:[109,110]
	
	on rbtnkeyType changed state do fnkeyType state
	on btnInvisible pressed do (fnAddVisKey 0.0 keyType)
	on btnVis01 pressed do (fnAddVisKey 0.1 keyType)
	on btnVis02 pressed do (fnAddVisKey 0.2 keyType)
	on btnVis03 pressed do (fnAddVisKey 0.3 keyType)
	on btnVis04 pressed do (fnAddVisKey 0.4 keyType)
	on btnVis05 pressed do (fnAddVisKey 0.5 keyType)
	on btnVis06 pressed do (fnAddVisKey 0.6 keyType)
	on btnVis07 pressed do (fnAddVisKey 0.7 keyType)
	on btnVis08 pressed do (fnAddVisKey 0.8 keyType)
	on btnVis09 pressed do (fnAddVisKey 0.9 keyType)
	on btnVisible pressed do (fnAddVisKey 1.0 keyType)
	on btnDelVisKey pressed do (fnDeleteVisKey())
	on btnDelVisTrack pressed do (fnDeleteVisTrack())

)
createDialog rlVisibility 220 140 style:#(#style_toolwindow, #style_sysmenu) 