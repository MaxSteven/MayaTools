try(destroyDialog ::rlFXExtras)catch()
rollout rlFXExtras "FX Tools"
(
	-- -- -- /*Variables*/ -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
	local fxPuckDir = @"Q:\USERS\JokerMartini\Projects\FX_Debris\SYSTEMS\Puck\FX*.max"	
	local fxPuckFiles = #()
	local fxTrailingDir = @"Q:\USERS\JokerMartini\Projects\FX_Debris\SYSTEMS\Trailing\TFX*.max"	
	local fxTrailingFiles = #()
	local selRef = undefined 
	
	
	-- -- -- /*Functions*/ -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
 	fn fnUpdateFXSystems loc lst &files fltr = ( --Populates the dropdownlist with Puck systems
 		local newSystems = #()
 		local activeSystems = #()
 		--//Locate preset systems
 		files = getFiles loc
 		sort files
		
 		newSystems = for file in files collect (getFilenameFile file)
		
		--//Locate current scene systems
		pfFX = for p in objects where classof p == PF_Source AND (matchPattern p.name pattern:fltr ignoreCase:false) collect p
		for p in pfFX do
		(
			a = getclassinstances Position_Object target:p
			posOp = (refs.dependentnodes a[1] firstonly:on)
			
			b = getclassinstances Speed_By_Surface target:p
			spdSurfOp = (refs.dependentnodes b[1] firstonly:on)
			
			if posOp != undefined OR spdSurfOp != undefined do
			(
				appendIfUnique activeSystems p.name
			)
		)
		
		fxSystems = #("- - New Systems - -") + newSystems + #("- - Active Systems - -") + activeSystems
		lst.items = fxSystems
 	)
	
	fn fnMarginPFSystems pfNodes = (
		padding = 40
		nodeMargins = #(5) --intial padding in particle viewer
		nodeMargins = for itm in objects where classof itm == PF_Source OR classof itm == Event collect itm.getPViewRightBoundary() --get all the event margins on the right side
		sort nodeMargins -- put the margins in order from lowest to highest
		rightMargin = nodeMargins[nodeMargins.count] --the furthest right margin
		
		pfNodes = for i in pfNodes where classof i == PF_Source OR classof i == Event collect i --filter supplied nodes to make sure its only pf/event nodes
		for ev in pfNodes do --adjust the placement of the supplied pf nodes
		(
			x = y = 0 --variables to store the positions in
			ev.getPViewLocation &x &y --get and store the nodes pos in the given variables
			offset = rightMargin + x + padding
			ev.setPViewLocation offset y
		)		
	)

	fn fnObjectsToLayer str nodes: = ( --Places given nodes on supplied layer name
		if nodes == unsupplied do nodes = #()--objects as array
			
		layers = for i = 1 to LayerManager.count - 1 collect (LayerManager.getLayer i).name
		if findItem layers str != 0 then
		(
			layer = LayerManager.getLayerFromName str
		)else(
			layer = layermanager.newLayerFromName str
		)
		
		for obj in nodes do 
		(
			layer.wirecolor = orange
			layer.addNode obj
		)
	)
	
	fn fnCreateFXPuck fxClass = (
		fxData_CA = attributes FXExtras 	--Creates FX Modifier
		(
			parameters main rollout:rlFXUI
			(
				FXTimes type:#stringTab tabSize:0 tabSizeVariable:true -- changed the parameter name also changed tabsize to 0 so it would not add an undefined item to the array
				FXInput type:#string ui:etFXInput default:""
			)	
				
			rollout rlFXUI "FX Parameters" width:160 height:400
			(
				fn fnUpdates = (
					rlFXUI.cpUpdate.color = red
				)
				
				fn getFramesArrayFromString theString = 
				(
					theString = filterString (substituteString theString " - " "..") ","
					theFrames = for i in theString where not matchPattern i pattern:"*..*" collect i as integer
					for i in theString where matchPattern i pattern:"*..*" do 
					(
						local thePair = (for j in filterString i "." collect j as integer)
						local theStep = if thePair[1] > thePair[2] then -1 else 1
						for k = thePair[1] to thePair[2] by theStep do appendIfUnique theFrames k
					)
					sort theFrames 
				)
				
				groupbox gbHitTimes "FX Times" width:140 height:175 pos:[10,10] 
				multilistbox lbFXTimes "" width:120 height:7 pos:[20,30]
				edittext etFXInput "" text:"5,0,50" width:124 pos:[16,130]
				button btnAppendTime "Append" width:100 height:25 pos:[45,150]
				button btnClearTimes "X" width:25 height:25 pos:[20,150]
				button btnUpdateFX "Update FX" width:140 height:30 pos:[10,195] 		
				colorpicker cpUpdate "" color:red width:144 height:4 pos:[6,225] enabled:false
				
				on btnUpdateFX pressed do
				(
					if selection.count == 1 do
					(
						--//Recreated array with supplied times (bug:array limits to 20 then adds "...)"
						a = for t in FXTimes collect t as integer
						bakedFXTimes = "#("
						for n in a do bakedFXTimes += (n as string) + ", "
						bakedFXTimes = substring bakedFXTimes 1 (bakedFXTimes.count - 2) + ")"	
						if FXTimes.count == 0 do bakedFXTimes = #(0)
						obj = selection[1]
						
						obj.modifiers[#FX_Selector].Gizmo.controller.Position.controller.script = "fxTimes =" + bakedFXTimes as string + "\nif findItem fxTimes ((currentTime as integer)/TicksPerFrame) == 0 then \n([0,0,10]) else ([0, 0, 0])\n"
						cpUpdate.color = green
					)
				)
				
				on btnAppendTime rightclick do 
				(
					fnUpdates()
					etFXInput.text = ""
				)
				
				on lbFXTimes doubleclicked idx do
				(
					fnUpdates()
					tmpArr = deleteItem FXTimes idx
					lbFXTimes.items = for x in FXTimes collect x -- assigning the stringTab directly gives you an error so we go through and collect everyitem
				)
				
				on btnClearTimes pressed do
				(
					fnUpdates()
					FXTimes = #()
					lbFXTimes.items = for x in FXTimes collect x -- assigning the stringTab directly gives you an error so we go through and collect everyitem
				)
				
				on btnAppendTime pressed do
				(
					fnUpdates()
					if etFXInput.text != "" then
					(
						--//Append user input time range
						print "append times here"
						range = getFramesArrayFromString (etFXInput.text)
						for t in range do 
						(
							if t != undefined do appendIfUnique FXTimes (t as string)
						)
						etFXInput.text = ""
					)else(
						--//Append the current time sliderTime
						appendIfUnique FXTimes (((currentTime as integer)/TicksPerFrame) as string)
					)
					lbFXTimes.items = for x in FXTimes collect x -- assigning the stringTab directly gives you an error so we go through and collect everyitem
				)
				
				on rlFXUI open do
				(
					if FXTimes.count != 0 do -- this makes sure that the stringTab is not empty
					(
						lbFXTimes.items = for x in FXTimes collect x -- assigning the stringTab directly gives you an error so we go through and collect everyitem
					)
				)
			)
		)
		
		--create the puck object then add the mod
		setCommandPanelTaskMode #create
		if selRef != undefined then
		(
			pos = selRef[1].center
			rot = selRef[1].rotation
		)else(
			pos = [0,0,0]
			rot = (quat 0 0 0 1)
		)
		fxPuck = Cylinder smooth:on heightsegs:1 capsegs:2 sides:8 height:0.0 radius:12 mapcoords:on rotation:rot pos:pos isSelected:on name:(uniqueName ("FXPuck_" + fxClass + "_")) wirecolor:orange renderable:off
		convertTo fxPuck Editable_Poly --convert to Editable_Poly	
		polyop.deletefaces fxPuck #{1..24}

		--//FX modifiers setup
		addModifier fxPuck (Vol__Select name:"FX_Selector" level:2 volume:0)
		attr = addmodifier fxPuck (EmptyModifier ui:on)
		fxPuck.modifiers[#Attribute_Holder].name = "FX_Hit"
		fxPuck.modifiers[#FX_Selector].Gizmo.scale *= 1.1
		fxPuck.modifiers[#FX_Selector].Gizmo.controller.Position.controller = position_Script()
		fxPuck.modifiers[#FX_Selector].Gizmo.controller.Position.controller.script = "([0,0,10])" --set to off from the start so no particles are generated
		custAttributes.add fxPuck.modifiers[#FX_Hit] fxData_CA #unique
		setCommandPanelTaskMode #modify
		fnObjectsToLayer "FX_Pucks" nodes:fxPuck --add pucks to the correct layer
		--return selection[1]
	)
	
	fn fnObjsToSystem pf op nodes = ( --add objects to the supplied operator
		a = getclassinstances op target:(getNodeByName pf)
		Op = (refs.dependentnodes a[1] firstonly:on)
		if Op != undefined do
		(
			for o in nodes do
			(
				if classof op == Speed_By_Surface do appendIfUnique Op.Surface_Objects o
				if classof op == Position_Object do appendIfUnique Op.Emitter_Objects o
			)
		)
	)
	
	fn fnCreateFX lst &files = ( --Creates FX systems (selection = num | selected = name)
		idx = lst.selection
		fxSysName = lst.selected as string
		fxPucks = #()
		if selection.count >= 1 then selRef = selection as array else undefined 
		
		if (matchPattern fxSysName pattern:"- - *" ignoreCase:false) != true do
		(
			fxFile = files[idx-1]
			newFXRange = files.count + 1
			activeFXRange = files.count + 2
				
			--//Use New FX System otherwise skip this step
			if idx >= 2 AND idx <= newFXRange do
			(
				--//Merge New Particles system
				mObjNames = getmaxfileobjectnames fxFile -- get the object names from the file
				mergemaxfile fxFile mObjNames #AutoRenameDups #renameMtlDups #select -- merge in the objects and select them
				
				pfSys = for o in selection where classof o == PF_Source collect o.name
				fxSysName = pfSys[1]
				fnMarginPFSystems selection --space out the nodes in the particle viewer
			)
			
			if lst.name == "dlFXPuckSystems" do (
				for op in selection where classof op == Birth do --//Make birth range to current framerange with 30 frames padding
				(
					op.Emit_Start= (animationrange.start as integer ) - (30f as integer)
					op.Emit_Stop = (animationrange.end as integer ) + (30f as integer)
				)
				fxClass = (filterString fxSysName "_")[2] --//name of FX Class
				fnCreateFXPuck fxClass --creates fx puck to the correct layer
				
				curSel = getCurrentSelection()
				fnObjsToSystem fxSysName Speed_By_Surface curSel
				fnObjsToSystem fxSysName Position_Object curSel
			)
			if lst.name == "dlTrailingFXSystems" do (
				for op in selection where classof op == Birth do --//Make birth range to current framerange with 30 frames padding
				(
					op.Emit_Start= (animationrange.start as integer ) - (10f as integer)
					op.Emit_Stop = (animationrange.start as integer ) + (9f as integer)
				)
				a = getclassinstances Position_Object target:(getNodeByName fxSysName)
				Op = (refs.dependentnodes a[1] firstonly:on)
				if Op != undefined do select op
				setCommandPanelTaskMode #modify
			)
		)
	)
	
	-- -- -- /*Main UI Dialog*/ -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
	groupbox gpPuckFX "Puck Systems" width:220 height:60 pos:[15,15] 
	dropdownlist dlFXPuckSystems "" items:#() width:125 pos:[24,38]
	button btnCreatePuckFX "Create" width:64 height:29 pos:[160,34] 
	groupbox gpTailingFX "Trailing Systems" pos:[15,85] width:220 height:60
	dropdownlist dlTrailingFXSystems "" items:#() width:125 pos:[24,108]
	button btnCreateTrailingFX "Create" width:64 height:29 pos:[160,104]
	
	on btnCreatePuckFX pressed do
	(
		fnCreateFX dlFXPuckSystems &fxPuckFiles
		fnUpdateFXSystems fxPuckDir dlFXPuckSystems &fxPuckFiles "FX_*"
		fnUpdateFXSystems fxTrailingDir dlTrailingFXSystems &fxTrailingFiles "TFX_*"
	)
	
	on btnCreateTrailingFX pressed do
	(
		fnCreateFX dlTrailingFXSystems &fxTrailingFiles
		fnUpdateFXSystems fxPuckDir dlFXPuckSystems &fxPuckFiles "FX_*"
		fnUpdateFXSystems fxTrailingDir dlTrailingFXSystems &fxTrailingFiles "TFX_*"
	)
	
	on rlFXExtras open do
	(
		fnUpdateFXSystems fxPuckDir dlFXPuckSystems &fxPuckFiles "FX_*"
		fnUpdateFXSystems fxTrailingDir dlTrailingFXSystems &fxTrailingFiles "TFX_*"
	)
)
createDialog rlFXExtras 250 160 style:#(#style_SysMenu, #style_ToolWindow)