
/*---------------------------------------------------------------------------------------------------------
-- Information:
-----------------------------------------------------------------------------------------------------------
# Title: MorphX2 Functions and UI
# FileDescription: 
# Copyright: Lumonix

Modify at own risk


---------------------------------------------------------------------------------------------------------*/



--memory:
heapsize += 1500000


-- Declare:
GLOBAL MorphX2Ops
GLOBAL MorphX2Mod

struct c_morphxkvfl
	(
	cacheval,
	networkpath = "",
	endofStruct
	)
morphxkvfl = c_morphxkvfl()



----------------------------------------------------------------------------------------------------
-- RC MENU for Morph Channel
----------------------------------------------------------------------------------------------------
RCMenu MorphX2ChannelUI
(
	MenuItem pickMorph "Pick Morph Target"
	MenuItem MorphFromStack "Morph From Stack"

	seperator sep1
	MenuItem renameMorph "Rename"
	MenuItem delTarget "Delete Morph"

	seperator sep2
	MenuItem includeMX2 "Include MorphX2"

	on MorphX2ChannelUI open do
	(
		includeMX2.checked = MorphX2Ops.includeMX2
	)

	on includeMX2 picked do
	(
		MorphX2Ops.includeMX2 = not MorphX2Ops.includeMX2
		popupmenu MorphX2ChannelUI pos:MorphX2Ops.lastMenuPos
	)

	on pickMorph picked do
	(
		local obj = pickObject "Pick Morph Target"
		if isvalidNode obj == true then
		(
			local succes = MorphX2Ops.addMorph selection[1] MorphX2Ops.activeMod obj MorphX2Ops.activeMod.activeMorph includeX2:MorphX2Ops.includeMX2
			MorphX2Ops.refreshUI MorphX2Ops.activeMod
			if succes == false then messagebox "Could not add morph target (Vertex count did not match)"
		)
	)

	on MorphFromStack picked do
	(
		local succes = MorphX2Ops.addMorphFromStack selection[1] MorphX2Ops.activeMod MorphX2Ops.activeMod.activeMorph includeX2:MorphX2Ops.includeMX2
		MorphX2Ops.refreshUI MorphX2Ops.activeMod
		if succes == false then messagebox "Could not add morph target (Vertex count did not match)"
	)

	on renameMorph picked do
	(
		MorphX2Ops.setText = MorphX2Ops.activeMod.delegate.getName MorphX2Ops.activeMod.activeMorph
		MorphX2Ops.enterText caption:"Morph Name"
		if  MorphX2Ops.lastText != "" then
		(
			MorphX2Ops.activeMod.delegate.setName MorphX2Ops.lastText MorphX2Ops.activeMod.activeMorph
			MorphX2Ops.refreshUI MorphX2Ops.activeMod
		)
	)

	on delTarget picked do
	(
		if querybox "Are you sure you want to delete this morph target (no undo)?" then
		(
			MorphX2Ops.delMorph selection[1] MorphX2Ops.activeMod MorphX2Ops.activeMod.activeMorph
			MorphX2Ops.refreshUI MorphX2Ops.activeMod
		)
	)
)--end









----------------------------------------------------------------------------------------------------
-- Structure
----------------------------------------------------------------------------------------------------
Global mpxLicChkd = false
Global mpxLicChk = true
Struct c_MorphX2Ops
(

	activeMod,
	modStates = #(),
	modID = 0,

	lastText = "",	-- for rename dialog
	setText = "",

	includeMX2 = false,
	lastMenuPos = [0,0],
	licRes = "",


	/* -----------------------------------------------------------------
	# Description  	: 	get parameter block of subAnim
	# Parameters 	: 
	# Returns    	: 	undefined or parameterblock referenceTarget
	*/ -----------------------------------------------------------------
	function morphX2GetParamBlock item = 
	( 
		local ret = undefined
		local v = refs.dependson item 
		for n in v do 
		(
			if classof n == ParamBlock2ParamBlock2 then ret = n
		) 

		ret -- RETURN
	),


	/*-----------------------------------------------------
	# Description  : Generic rollout for entering text
	# Parameters   :
	# Returns      : ok
	*/-----------------------------------------------------
	function enterText caption:"" =
	(
		rollout textRol caption
		(
			editText		textBox			""			width:100		align:#left offset:[-14,3] across:2
			button			okbtn			"OK"		width:24		align:#right offset:[10,0]
			on textRol open do
			(
				MorphX2Ops.lastText = ""
				textBox.text = MorphX2Ops.setText
				setFocus textRol.textBox
			)

			on textBox entered txt do
			(
				MorphX2Ops.lastText = txt
				destroyDialog textRol
			)
			on okbtn pressed do
			(
				MorphX2Ops.lastText = textBox.text
				destroyDialog textRol
			)
		)
		createDialog textRol width:130 height:40 style:#(#style_toolwindow, #style_sysmenu, #style_resizing) modal:true pos:(mouse.screenPos - [40,30])
		
		ok	-- RETURN
	),


	/* -----------------------------------------------------------------
	# Description  	: Disables modifiers above MorphX2 which is needed for some operations
	# Parameters 	:	<node>			node		:		node with morphX2 modifier
	# Returns    	: ok
	*/ -----------------------------------------------------------------
	function disableMods node =
	(
		modID = 0
		modStates = #()
		for i=1 to node.modifiers.count do
		(
			modStates[i] = node.modifiers[i].enabled
			if node.modifiers[i] == activeMod then modID = i
		)

		if modID != 0 then
		(
			for i=(modID-1) to 1 by -1 do
				node.modifiers[i].enabled = false
		)

		ok -- RETURN
	),


	/* -----------------------------------------------------------------
	# Description  	: Enables modifiers above MorphX2
	# Parameters 	:	<node>			node		:		node with morphX2 modifier
	# Returns    	: ok
	*/ -----------------------------------------------------------------
	function enableMods node =
	(
		if modID != 0 then
		(
			for i=(modID-1) to 1 by -1 do
				node.modifiers[i].enabled = modStates[i]
		)

		ok -- RETURN
	),


	/* -----------------------------------------------------------------
	# Description  	: 	addMorph
	# Parameters 	: 	<node>			node		:		Node that has the morphX2 modifier applied
						<modifier>		mod			:		MorphX2 modifier
						<node>			morphTarget	:		node that is the new morph target
						<integer>		index		:		index of target
						<mesh>			selMesh		:		mesh of node with morphX2 modifier (this can be supplied for grabbing mesh from stack or anything that is not the morphX2 node)
						<mesh>			objMesh		:		mesh of morphTarget (this can be supplied for grabbing mesh from stack or anything that is not a 'morph target node')
						<boolean>		includeX2	:		if false, disables all effect of morphX2, if true, disables only targets BELOW index of target (this is then a corrective morph on top of previous morphs)
	# Returns    	: 	true or false
	# Note			:	we must compare the BASE mesh of the node with modifier, otherwise we may be adding active morph target into the mix
	*/ -----------------------------------------------------------------
	function addMorph node mod morphTarget index objMesh:undefined selMesh:undefined includeX2:false = 
	( 
		local ret = false

		with animate off
		(
			if includeX2 == false then 
			(
				local mCnt = mod.delegate.getMorphCount()
				for i=1 to mCnt do mod.delegate.toggleMorph i true -- disable morph
				mod.blend = mod.blend	-- force update
			)
			disableMods node

			mod.delegate.addMorph index

			try
				(
				mod.blendvalues[index] = 0.0
				mod.blendvalues[index].controller = bezier_float()
				)
			catch()
			
			local mName = node.name
			if morphTarget != undefined then mName = morphTarget.name

			mod.delegate.setName mName index
	
			-- caluclate deltas for all verts (within threshold):
			local ids = #()
			local deltasX = #()
			local deltasY = #()
			local deltasZ = #()
			local deltasLength = #()
	
			if objMesh == undefined then objMesh = morphTarget.mesh
			if selMesh == undefined then selMesh = node.mesh			-- note: this could fail if i.e. a TurboSmooth was active on top of our node. must first disable the modifiers

			if objMesh.numverts == selMesh.numverts then
			(
				for i=1 to selMesh.numverts do
				(
					local dir = Normalize (objMesh.verts[i].pos - selMesh.verts[i].pos)
					local lngth = length (objMesh.verts[i].pos - selMesh.verts[i].pos)
					if lngth > mod.deltaTH then
					(
						append ids i
						append deltasX dir.x
						append deltasY dir.y
						append deltasZ dir.z
						append deltasLength lngth
					)
				)--end for i
		
				mod.delegate.setDelta index ids deltasX deltasY deltasZ deltasLength	-- feed delta axis individually due to point4 tab restrictions in SDK
				ret = true
			)

			-- restore values:
			enableMods node
			if includeX2 == false then 
			(
				local mCnt = mod.delegate.getMorphCount()
				for i=1 to mCnt do mod.delegate.toggleMorph i false -- enable morph
				mod.blend = mod.blend	-- force update
			)
		)--end animate off

		ret -- RETURN
	),


	/* -----------------------------------------------------------------
	# Description  	: 	add Morph From Stack instead of object
	# Parameters 	: 	<node>			node		:		Node that has the morphX2 modifier applied
						<modifier>		mod			:		MorphX2 modifier
						<integer>		index		:		index of target
						<boolean>		includeX2	:		if false, disables all effect of morphX2, if true, disables only targets BELOW index of target (this is then a corrective morph on top of previous morphs)
	# Returns    	: 	true or false
	*/ -----------------------------------------------------------------
	function addMorphFromStack node mod index includeX2:false = 
	( 
		-- grab base Mesh:
		local orgBlend = mod.blend	-- we must get the deltas WITHOUT having any morph targets active. We cannot disable the modifier since it would not work on non-mesh baseObjects anymore

		if includeX2 == false then
		(
			local mCnt = mod.delegate.getMorphCount()
			for i=1 to mCnt do mod.delegate.toggleMorph i true -- disable morph
			mod.blend = mod.blend	-- force update
		)

		disableMods node
		local selMesh = node.mesh

		-- grab morphed mesh:
		enableMods node
		local objMesh = node.mesh

		-- restore values:
		if includeX2 == false then 
		(
			local mCnt = mod.delegate.getMorphCount()
			for i=1 to mCnt do mod.delegate.toggleMorph i false -- enable morph
			mod.blend = mod.blend	-- force update
		)


		local res = addMorph node mod undefined index objMesh:objMesh selMesh:selMesh

		res -- RETURN
	),


	/*----------------------------------------------------------------------------------------
	# Description	:	
	# Parameters	: 
	# Returns		: 	true or false
	*/----------------------------------------------------------------------------------------
	function valmpx =
	(
		val = true
		try(
			pv = getdir #plugcfg + "\\mpxtk.cfg"
			local d=1
			
			if ((getfiles pv).count == 0) then
			(
				local fStream = createfile pv
				close fStream
				fStream = openFile pv mode:"w"
				format "1" to:fStream
				close fStream
			)
			
			fStream = openFile pv mode:"r"
			if (fStream != undefined) then
			(
				d = (readLine fStream) as integer
				close fStream
				fStream = openFile pv mode:"w"
				if (fStream != undefined) then
				(
					format "%" (d+1) to:fStream
					close fStream
					val = (d>29)
				)
			)
		)
		catch(val = false)
		
		val -- RETURN
	),

	/* -----------------------------------------------------------------
	# Description  	: 	del Morph
	# Parameters 	: 	<node>			node		:		Node that has the morphX2 modifier applied
						<modifier>		mod			:		MorphX2 modifier
						<integer>		index		:		index of target
	# Returns    	: 	ok
	*/ -----------------------------------------------------------------
	function delMorph node mod index = 
	( 
		mod.delegate.delMorph index
		-- deleting the item out of blendvalues here could cause our morphs and channels to be out of sync --
		ok -- RETURN
	),


	/* -----------------------------------------------------------------
	# Description  	: 	Colors the mesh to show which vertices are used by a morph target
	# Parameters 	: 	<node>			node		:		Node that has the morphX2 modifier applied
						<modifier>		mod			:		MorphX2 modifier
						<integer>		index		:		index of morphtarget to show. 0 if you do not want to show any
	# Returns    	: 	ok
	*/ -----------------------------------------------------------------
	function showMorph node mod index = 
	( 
		if index > mod.delegate.getMorphCount() then index = 0

		if index > 0 then
		(
			node.showVertexColors = on
			mod.delegate.setColorVerts index	-- enable display of vertex colors
		)
		else
		(
			node.showVertexColors = off
			mod.delegate.setColorVerts 0
		)
		ok -- RETURN
	),



	/* -----------------------------------------------------------------
	# Description  	: 	Rebuilds the UI
	# Parameters 	: 	<modifier>		modf			:		MorphX2 modifier
	# Returns    	: 	ok
	*/ -----------------------------------------------------------------
	function refreshUI modf = 
	( 
		-- get morphData Count to make sure our blendValues is synced (in case modifier reset due to changing vert count):
		local mCnt = modf.delegate.getMorphCount()
		for i=1 to mCnt do ( if modf.blendValues[i] == undefined then (modf.blendValues[i] = 0.0; modf.blendvalues[i].controller = bezier_float();) )

		-- update UI - show correct morphs in UI depending on scroll:

		local but = #(modf.MorphX2ModRol.morphA, modf.MorphX2ModRol.morphB, modf.MorphX2ModRol.morphC, modf.MorphX2ModRol.morphD, modf.MorphX2ModRol.morphE, modf.MorphX2ModRol.morphF, modf.MorphX2ModRol.morphG, modf.MorphX2ModRol.morphH, modf.MorphX2ModRol.morphI, modf.MorphX2ModRol.morphJ )
		local spin = #(modf.MorphX2ModRol.spinA, modf.MorphX2ModRol.spinB, modf.MorphX2ModRol.spinC, modf.MorphX2ModRol.spinD, modf.MorphX2ModRol.spinE, modf.MorphX2ModRol.spinF, modf.MorphX2ModRol.spinG, modf.MorphX2ModRol.spinH, modf.MorphX2ModRol.spinI, modf.MorphX2ModRol.spinJ )

		-- set text and values on UI:
		local ac = modf.activeMorph - modf.scroll

		for b=1 to but.count do spin[b].controller = undefined

		for b=1 to but.count do
		(
			local s = modf.scroll + b
			but[b].text = (s as string) + " - " + (modf.delegate.getName s)
			if b == ac then (but[b].checked = true)
			else but[b].checked = false
			
			if s <= modf.blendValues.count then 
			(
				local str = "blendValues_" + (s-1) as string -- 0-based
				if modf[str] != undefined and modf[str].controller != undefined then spin[b].controller = modf[str].controller
				else spin[b].value = modf.blendValues[s]

				-- below would crash if we assign a script float controller to the spinner:
				-- if modf.blendValues[s].controller != undefined then spin[b].controller = modf.blendValues[s].controller
			)
		)

		-- modf.MorphX2ModRol.scrollUp.text = (1 + modf.scroll) as string
		-- modf.MorphX2ModRol.scrollDown.text = (10 + modf.scroll) as string

		ok -- RETURN
	),



	/* -----------------------------------------------------------------
	# Description  	: 	Pop morph UI for active channel
	# Parameters 	: 	<modifier>		mod			:		MorphX2 modifier
	# Returns    	: 	ok
	*/ -----------------------------------------------------------------
	function popUI mod = 
	( 
		activeMod = mod
		lastMenuPos = mouse.screenPos
		popupmenu MorphX2ChannelUI pos:lastMenuPos
		ok -- RETURN
	),


	/* -----------------------------------------------------------------
	# Description  	: 	Pop morph UI for active channel
	# Parameters 	: 	<modifier>		mod			:		MorphX2 modifier
						<integer>		index		:		index of the morph target to update
						<float>			val			:		new value
	# Returns    	: 	ok
	*/ -----------------------------------------------------------------
	function updateBlendValue mod index val = 
	( 
		if index <= mod.blendValues.count then
		(
			mod.blendValues[index] = val
		)
		ok -- RETURN
	),


	endOfStruct
)

MorphX2Ops = c_MorphX2Ops()


	/*----------------------------------------------------------------------------------------
	# Description	:	returns license key user has entered
	# Parameters	: 	
	# Returns	: 	string
	*/----------------------------------------------------------------------------------------
	function getMorphXLicenseKey =
	(
		morphxkvfl.cacheval
	)

	/*----------------------------------------------------------------------------------------
	# Description	:	returns the license path
	# Parameters	: 	
	# Returns	: 	string
	*/----------------------------------------------------------------------------------------
	function getMorphXLicensePath ext:".dat" =
	(
		local outPath = ""

		if morphxkvfl.networkpath == "" then
		(
			local licPath = ( (getDir #scripts) + "\\MorphX2\\License\\" + "MorphXLic" + ext)
			local cutStr = filterString licPath "\\"
			for i=1 to (cutStr.count-1) do 
			(
				append outPath cutStr[i]
				append outPath "\\\\"
			)
			append outPath cutStr[cutStr.count]
		)
		else
		(
			outPath = morphxkvfl.networkpath
		)
	
		outPath
	)
	
	/*----------------------------------------------------------------------------------------
	# Description	:	returns the license path
	# Parameters	: 	
	# Returns	: 	string
	*/----------------------------------------------------------------------------------------
	function getMorphXLicensePathRaw =
	(
		(getMorphXLicensePath ext:".org")
	)








----------------------------------------------------------------------------------------------------
-- Modifier
----------------------------------------------------------------------------------------------------
-- Note: the real modifier is C++, but we have a MXS UI around it:
plugin modifier MorphX2Mod
name:"MorphX2"
classID:#(0x568a14b2, 0x580ad4b0)
invisible:false
extends:Morpha
replaceUI:true
version:1
(

	local emptydummylocal

	function meshFilter obj = ( (obj != selection[1] and classof obj == Editable_mesh) )


	parameters MorphX2ModParams rollout:MorphX2ModRol
	(
		-- !!!! Warning, do NOT change the order of the items in this parameter block --
		blend			type:#float			default:1.0			animatable:true			UI:blendSpin
		blendvalues		type:#floatTab							animatable:true			tabSizeVariable:true

		-- !! anything below is not send via paramblock --
		deltaTH			type:#float			default:0.01		animatable:false		UI:deltaTHSpin
		activeMorph		type:#integer		default:0			animatable:false
		showMorph		type:#boolean		default:false		animatable:false		UI:showMorphChk
		scroll			type:#integer		default:0			animatable:false
	)

	on attachedToNode nodevar do 
	(
		this.delegate.setParameterBlock (MorphX2Ops.morphX2GetParamBlock this[1])	-- add maxscript parameter block to c++ plugin.
	)

	rollout MorphX2ModRol "MorphX2 - Version 1.11"
	(
		button			help			"?"					height:16	width:16			align:#left			across:2		offset:[-8,0]		tooltip:"Open MorphX2 help documentation"
		spinner			blendSpin		"Blend All:"		range:[0.0,9999.0,blend] 		type:#float			scale:0.01 		align:#right		offset:[10,0]		fieldwidth:40

		checkbutton		morphA			""					width:80		across:2		offset:[20,0]	height:16
		spinner			spinA			""					range:[-99,99,0]	type:#float		fieldwidth:40	offset:[10,0]	scale:0.01
		checkbutton		morphB			""					width:80		across:2		offset:[20,0]	height:16
		spinner			spinB			""					range:[-99,99,0]	type:#float		fieldwidth:40	offset:[10,0]	scale:0.01
		checkbutton		morphC			""					width:80		across:2		offset:[20,0]	height:16
		spinner			spinC			""					range:[-99,99,0]	type:#float		fieldwidth:40	offset:[10,0]	scale:0.01
		checkbutton		morphD			""					width:80		across:2		offset:[20,0]	height:16
		spinner			spinD			""					range:[-99,99,0]	type:#float		fieldwidth:40	offset:[10,0]	scale:0.01
		checkbutton		morphE			""					width:80		across:2		offset:[20,0]	height:16
		spinner			spinE			""					range:[-99,99,0]	type:#float		fieldwidth:40	offset:[10,0]	scale:0.01
		checkbutton		morphF			""					width:80		across:2		offset:[20,0]	height:16
		spinner			spinF			""					range:[-99,99,0]	type:#float		fieldwidth:40	offset:[10,0]	scale:0.01
		checkbutton		morphG			""					width:80		across:2		offset:[20,0]	height:16
		spinner			spinG			""					range:[-99,99,0]	type:#float		fieldwidth:40	offset:[10,0]	scale:0.01
		checkbutton		morphH			""					width:80		across:2		offset:[20,0]	height:16
		spinner			spinH			""					range:[-99,99,0]	type:#float		fieldwidth:40	offset:[10,0]	scale:0.01
		checkbutton		morphI			""					width:80		across:2		offset:[20,0]	height:16
		spinner			spinI			""					range:[-99,99,0]	type:#float		fieldwidth:40	offset:[10,0]	scale:0.01
		checkbutton		morphJ			""					width:80		across:2		offset:[20,0]	height:16
		spinner			spinJ			""					range:[-99,99,0]	type:#float		fieldwidth:40	offset:[10,0]	scale:0.01

		button			scrollUp		"^"					width:20	height:20	pos:(morphA.pos - [24,0])
		bitmap			scrollbar		""					width:20	height:166	pos:(scrollUp.pos + [0,20])
		button			scrollDown		"v"					width:20	height:20	pos:(scrollbar.pos + [0,166])

		checkbox		showMorphChk		"Show Active Morph Colors"

		spinner			deltaTHSpin		"Delta Threshold"	range:[0.0, 999.0, deltaTH]		type:#float			align:#right


		function updateShowMorph = ( if showMorph == true then (MorphX2Ops.showMorph selection[1] this activeMorph) else (MorphX2Ops.showMorph selection[1] this 0) )

		/*------------------------------------------------EVENT
		Open/Close:
		*/-----------------------------------------------------
		on MorphX2ModRol open do 
		(
			MorphX2Ops.activeMod = this
			MorphX2Ops.refreshUI this

			if MorphX2Ops.licRes != "ok" and (maxversion())[1] >= 14000 then 
				MorphX2Ops.licRes = this.delegate.getLicenseData()

			if MorphX2Ops.licRes != "ok" and not mpxLicChkd then
				(
				mpxLicChk = not MorphX2Ops.valmpx()
				mpxLicChkd = true
				)
			if (not mpxLicChk) then MorphX2ModRol.height=2
		)

		on MorphX2ModRol close do 
		(
		)

		on MorphX2ModRol rolledUp state do 
		(
			MorphX2Ops.activeMod = this
			MorphX2Ops.refreshUI this
		)


		/*------------------------------------------------EVENT
		Scroll:
		*/-----------------------------------------------------
		on scrollUp pressed do
		(
			scroll -= 1
			if scroll < 0 then scroll = 0
			MorphX2Ops.refreshUI this
		)

		on scrollDown pressed do
		(
			scroll += 1
			MorphX2Ops.refreshUI this
		)


		/*------------------------------------------------EVENT
		Morph buttons:
		*/-----------------------------------------------------
		on morphA changed state do ( activeMorph = (1+scroll); updateShowMorph(); MorphX2Ops.refreshUI this; MorphX2Ops.popUI this; )
		on morphB changed state do ( activeMorph = (2+scroll); updateShowMorph(); MorphX2Ops.refreshUI this; MorphX2Ops.popUI this; )
		on morphC changed state do ( activeMorph = (3+scroll); updateShowMorph(); MorphX2Ops.refreshUI this; MorphX2Ops.popUI this; )
		on morphD changed state do ( activeMorph = (4+scroll); updateShowMorph(); MorphX2Ops.refreshUI this; MorphX2Ops.popUI this; )
		on morphE changed state do ( activeMorph = (5+scroll); updateShowMorph(); MorphX2Ops.refreshUI this; MorphX2Ops.popUI this; )
		on morphF changed state do ( activeMorph = (6+scroll); updateShowMorph(); MorphX2Ops.refreshUI this; MorphX2Ops.popUI this; )
		on morphG changed state do ( activeMorph = (7+scroll); updateShowMorph(); MorphX2Ops.refreshUI this; MorphX2Ops.popUI this; )
		on morphH changed state do ( activeMorph = (8+scroll); updateShowMorph(); MorphX2Ops.refreshUI this; MorphX2Ops.popUI this; )
		on morphI changed state do ( activeMorph = (9+scroll); updateShowMorph(); MorphX2Ops.refreshUI this; MorphX2Ops.popUI this; )
		on morphJ changed state do ( activeMorph = (10+scroll); updateShowMorph(); MorphX2Ops.refreshUI this; MorphX2Ops.popUI this; )

		on spinA changed val do ( morphX2Ops.updateBlendValue this (1+scroll) val; )
		on spinB changed val do ( morphX2Ops.updateBlendValue this (2+scroll) val; )
		on spinC changed val do ( morphX2Ops.updateBlendValue this (3+scroll) val; )
		on spinD changed val do ( morphX2Ops.updateBlendValue this (4+scroll) val; )
		on spinE changed val do ( morphX2Ops.updateBlendValue this (5+scroll) val; )
		on spinF changed val do ( morphX2Ops.updateBlendValue this (6+scroll) val; )
		on spinG changed val do ( morphX2Ops.updateBlendValue this (7+scroll) val; )
		on spinH changed val do ( morphX2Ops.updateBlendValue this (8+scroll) val; )
		on spinI changed val do ( morphX2Ops.updateBlendValue this (9+scroll) val; )
		on spinJ changed val do ( morphX2Ops.updateBlendValue this (10+scroll) val; )



		/*------------------------------------------------EVENT
		show:
		*/-----------------------------------------------------
		on showMorphChk changed state do
		(
			updateShowMorph()
		)


		/*------------------------------------------------EVENT
		Help:
		*/-----------------------------------------------------
		on help pressed do
		(
			local file = (getDir #scripts) + "\\MorphX2\\Help\\index.html"
			shelllaunch file ""
		)


----------------------------------------
	)--end rollout



	rollout reg_rol "Register"	rolledup:true
		(

		group ""
			(
			label		lbl3	"Please support us by "
			label		lbl3a	"buying a license at:"
			hyperlink	lnk1	"http://www.lumonix.net" address:"http://www.lumonix.net"
			button	regCode		"Register"	width:140	tooltip:"Click here to enter your registration code"
			)

		on reg_rol open do
			(
			reg_rol.open = not mpxLicChk
			)

		on regCode pressed do
			(
			if ((maxversion())[1] >= 14000) then
				(
				MorphX2Ops.licRes = this.delegate.getLicenseData()
				if MorphX2Ops.licRes != "ok" then 
					(
					this.delegate.genLicense()
					MorphX2Ops.licRes = this.delegate.getLicenseData()
					if MorphX2Ops.licRes == "ok" then messagebox "Thank you! (Please Restart 3dsmax)"
					else messagebox "Failed! The Key you entered was not valid."
					)
				)
			)
		)



)--end plugin




