try(destroyDialog ::rlCameraFlashes)catch()
rollout rlCameraFlashes "Camera Flashes"
(
	-- VARIABLES
	global _genPFPts = #()
	local flashCam = undefined
	local flashCloud = undefined
	local VRShadows = VRayShadow()
	local GRPLights = 125
	--local camLst = for o in objects where superclassof o == camera collect o.name
	
	fn GeoFilter obj = superclassof obj == GeometryClass
	
	fn fnObjectsToLayer str nodes: = ( --Places given nodes on supplied layer name
		if nodes == unsupplied do nodes = #()--objects as array
			
		layers = for i = 1 to LayerManager.count - 1 collect (LayerManager.getLayer i).name
		if findItem layers str != 0 then
		(
			layer = LayerManager.getLayerFromName str
		)else(
			layer = layermanager.newLayerFromName str
		)
		
		layer.wirecolor = orange
		
		for obj in nodes do 
		(
			layer.addNode obj
		)
	)
	
	fn shuffleIndexes count = --unique Random order
	(
		list = #() 	
		list.count = count
		for k = 1 to count do 
		(
			i = random 1 k
			list[k] = list[i]
			list[i] = k
		)
		return list
	)
	
	-- MAIN UI
	label lbFlashCamera"Camera:" pos:[10,15]
	button btnRefreshCamLst "R" width:20 height:21 pos:[190,12]
	dropdownlist lstCamera "" width:100 pos:[90,12] items:#()
	label lbFlashCloud "Flash Cloud:" pos:[10,45]
	pickbutton pbFlashCloud "PICK GEO" width:120 height:24 filter:GeoFilter pos:[90,40]
	label lbNumFlashes"# flashes/s:" pos:[10,75]
	spinner spnNumFlashes "" range:[1,999999999,6] fieldwidth:111 type:#integer pos:[87,74]
	label lbRange "Range:" pos:[10,100]
	spinner spnStart "" range:[animationrange.start,animationrange.end,animationrange.start] fieldwidth:45 type:#integer pos:[87,99]
	spinner spnEnd  "- " range:[animationrange.start,animationrange.end,animationrange.end] fieldwidth:45 type:#integer pos:[146,99]
	groupbox gpLights "Lights" width:200 height:95 pos:[10,GRPLights]
		label lbLightMultiplier "On/Off:" pos:[20,GRPLights+20]
		spinner spOn "" range:[0.0,100.0,1.0] fieldwidth:40 type:#float pos:[87,GRPLights+19]
		spinner spOff "- " range:[0.0,100.0,0.0] fieldwidth:40 type:#float pos:[141,GRPLights+19]
		label lbLightVariation "On Variation:" pos:[20,GRPLights+45]
		spinner spLightVariation "" range:[0.0,1.0,.25] fieldwidth:40 type:#float pos:[87,GRPLights+44] tooltip:"0.0 = no variation , .5 = 50% intensity variation ranging from .75 - 1"
		label lbFarAttenuation "Attenuation:" pos:[20,GRPLights+70]
		spinner spStartAtt "" range:[0.0,999999999,365.76] fieldwidth:40 type:#worldunits pos:[87,GRPLights+69]
		spinner spEndAtt "- " range:[0.0,999999999,500] fieldwidth:40 type:#worldunits pos:[141,GRPLights+69]
	label lbDeleteFlashes "Delete previous flashes:" pos:[10,230] 
	checkbox cbDeleteFlashes "" pos:[197,230]
	button btnCreateFlashes "Create Flashes" pos:[10,255] width:200 height:35
	
	-- FUNCTIONS
	fn fnPFPoints nodes amount:10 location:3 = (	
		_genPFPts = #() --reset		
		pfp = PF_Source name:"pf_points" X_Coord:0 Y_Coord:0 Quantity_Viewport:100 Show_Logo:off Show_Emitter:off
		
		particleFlow.BeginEdit()
		op1 = Birth name:"pfp_birth" amount:amount Emit_Stop:currenttime Emit_Start:currenttime
		op2 = Position_Object name:"pfp_place" Emitter_Objects:nodes Location:location Lock_On_Emitter:on Random_Seed:(random 1 1000000000)
		
		source  = ""
		source += "on ChannelsUsed pCont do (pCont.usePosition = on) \n"
		source += "on Proceed pCont do for k=1 to pCont.NumParticles() do\n"
		source += "	_genPFPts[pCont.particleIndex = k] = pCont.particlePosition\n"
		
		op3 = Script_Test name:"pfp_test" Proceed_Script:source
		ev1 = Event name:"pfp_event"
		ev1.AppendAction op1
		ev1.AppendAction op2
		ev1.AppendAction op3
		
		pfp.AppendInitialActionList ev1
		particleFlow.EndEdit()
		particleFlow.delete pfp
	)
	
	fn fnAddKey ctrl: val: theTime: = (
		newKey = addnewkey ctrl theTime
		newKey.value = val
	)
	
	fn fnAnimateFlahes lite: card: theTime: = (
		lite.multiplier.controller = bezier_float()
		card.visibility = on
		card.visibility.controller = bezier_float()
		
		liteCtrl = lite.multiplier.controller
		cardCtrl = card.visibility.controller 
		
		offValue = spOff.value
		onValue = spOn.value - (rlCameraFlashes.spOn.value * rlCameraFlashes.spLightVariation.value) --examples:1-(1*.25)
 		onRange = (random onValue rlCameraFlashes.spOn.value)
		
		fnAddKey ctrl:liteCtrl val:offValue theTime:(theTime-1) --off time
		fnAddKey ctrl:liteCtrl val:onRange theTime:theTime --on time
		fnAddKey ctrl:liteCtrl val:offValue theTime:(theTime+2) --off time
		
		fnAddKey ctrl:cardCtrl val:0.0 theTime:(theTime-1) --off time
		fnAddKey ctrl:cardCtrl val:1.0 theTime:theTime --on time
		fnAddKey ctrl:cardCtrl val:0.0 theTime:(theTime+1) --off time
	)
	
	fn fnCreateFlashes = (
		local camObj = getNodeByName lstCamera.items[lstCamera.selection]
		flashCam = if isValidNode camObj then camObj else undefined
			
		if flashCam != undefined AND flashCloud != undefined do 
		( 
			-- PART 1: figure out how many particles need to be generated for the given framerange in order to meet the desired number of flashes per second
			fps = frameRate
			numFlashes = spnNumFlashes.value
			numFrames = spnEnd.value - spnStart.value
			seconds = ceil numFrames / fps
			totalFlashes = (seconds * numFlashes) as integer
			
			fnPFPoints #(flashCloud) amount:(totalFlashes) location:3 -- create pf system and collect all the point 3 values on surface
			_genPts = copy _genPFPts #nomap
			
			if _genPts.count >= 1 do
			(
				_camflashes= #()
				setCommandPanelTaskMode #create --for speed increase
				camFlashMTL = VRayLightMtl multiplier:1.5 opacity_multiplyColor:on texmap: (Bitmaptexture fileName:@"Q:\ASSETS\TEXTURES\Flares\fxFlare\LG_Flare_001.png") opacity_texmap:(Bitmaptexture fileName:@"Q:\ASSETS\TEXTURES\Flares\fxFlare\LG_Flare_001.png")
				camFlashMTL.opacity_texmap.preMultAlpha = off
				
				local theCard = Plane wirecolor:blue width:100.0 length:100.0 widthsegs:1 lengthsegs:1 castShadows:off
				theCard.rotation.controller = Orientation_Constraint ()
				theCard.rotation.controller.appendTarget flashCam 100
				theCard.material = camFlashMTL
				
				clearlistener()
				-- PART 2:Create the flash cards and omni lights
				idx = shuffleIndexes _genPts.count --random ordering of the flashes
				itm = 1 --used to choose which array item to use in the shuffled idx array
				for start = 0 to (numFrames-1) by fps do --loop through the timeline and for every second generate "X" number of random flashes
				(
					for f = 1 to numFlashes do
					(
						flashTime = random start (start + fps) --frame in time at which the flash should take place
						
						--card creation
						ptPos =  _genPts[idx[itm]] -- point 3 position
						flasher = copy theCard
						flasher.name = (uniqueName"FX_camFlash_")
						flasher.pos = ptPos
						flasher.wirecolor = blue
							
						--light creation
						flasherLite = omniLight name:(uniqueName "FX_camFlashLite_") multiplier:1.5 castShadows:true wirecolor:yellow useFarAtten:true farAttenStart:120.0 farAttenEnd:1000.0 pos:ptPos shadowGenerator:VRShadows --//Create Omni Light
						
						--animation keying
						fnAnimateFlahes lite:flasherLite card:flasher theTime:flashTime
						
						append _camFlashes flasher
						append _camFlashes flasherLite
						if itm >= _genPts.count then itm = 1 else itm += 1
					)
				)
				fnObjectsToLayer "FX_Flashes" nodes:_camflashes
				delete theCard
			)
		)
	)
	
	on btnRefreshCamLst pressed do (lstCamera.items = for o in objects where superclassof o == camera collect o.name)
	
	on btnCreateFlashes pressed do 
	(
		if cbDeleteFlashes.state do
		(
			_killGrp = for obj in $FX_camFlash* collect obj
			for obj in _killGrp do delete obj
		)
		fnCreateFlashes()
	)
	
	on pbFlashCloud picked obj do (
		if obj !=undefined do	(
			flashCloud = obj
			pbFlashCloud.text = obj.name
		)
	)
	
	on spStartAtt changed val do
	(
		_flashLights = for obj in selection where classof obj == Omnilight collect obj
		for obj in _flashLights do obj.farAttenStart = val
		if spEndAtt.value <= val do 
		(
			spEndAtt.value = val
			for obj in _flashLights do obj.farAttenEnd = spEndAtt.value
		)
	)
	
	on spEndAtt changed val do
	(
		_flashLights = for obj in selection where classof obj == Omnilight collect obj
		for obj in _flashLights do obj.farAttenEnd = val
		if spStartAtt.value >= val do 
		(
			spStartAtt.value = val
			for obj in _flashLights do obj.farAttenStart = spStartAtt.value
		)
	)
	
	on rlCameraFlashes open do (lstCamera.items = for o in objects where superclassof o == camera collect o.name)
)
createDialog rlCameraFlashes 220 305 style:#(#style_SysMenu, #style_ToolWindow)