try(destroyDialog ::rlRenderMattes)catch()
rollout rlRenderMattes "Render Mattes"
(
	
/* Variables
----------------------------------------------------------------------------------------------------------------------------------*/	
	local unUsedLights = #()
	local curRen = renderers.production
	local theVRRenderer = Vray()
	local re = maxOps.GetCurRenderElementMgr()
	local theManager = maxOps.GetRenderElementMgr #Production
	
	
/* Collects all the lights currently being used in the render elements
----------------------------------------------------------------------------------------------------------------------------------*/
	fn fnCollectUsedLights = (
		renderSceneDialog.close()
		renderSceneDialog.update()
		re = maxOps.GetCurRenderElementMgr()
		numRE = (re.numrenderelements()-1)
		usedLightsCol = #() --empty out the array
		
		if numRE >= 0 do
		(
			for i in 0 to numRE by 1 do
			(
				theElement = re.GetRenderElement i
				if classof theElement == VRayLightSelect do
				(
					local lightArr = theElement.lights -- lights in active element
					
					if lightArr.count >= 1 do
					(
						for r = 1 to lightArr.count do
						(
							appendIfUnique usedLightsCol lightArr[r]
						)
					)
				)
			)
		)
		return usedLightsCol
	)	
	
	
/* Main UI Dialog
----------------------------------------------------------------------------------------------------------------------------------*/
	groupbox gpObjMattes "Object Mattes" width:146 height:145 pos:[10,10]
	button btnSelMattes "Selection Mattes" width:126 height:25 pos:[20,30]
	button btnLayerMattes "Layers Mattes" width:126 height:25 pos:[20,60]
	button btnSceneMaterials "Scene Materials" width:126 height:25 pos:[20,90]
	button btnSelectedMaterials "Selected Materials" width:126 height:25 pos:[20,120]
	
	groupbox gpLightMattes "Light Mattes" width:146 height:85 pos:[10,165]
	label lbGetLioghts "" style_sunkenedge:true width:126 height:25 pos:[20,185]
	button btnGetLights "Get UnMatted Lights" width:124 height:23 pos:[21,186]
	button btnSelLights "Selection Mattes" width:126 height:25 pos:[20,215]	
	
	
	/*Selection Based Materials
	----------------------------------------------------------------------------------------------------*/
	on btnSelMattes pressed do
	(
		selection.gbufferchannel = 0		
		try(destroyDialog ::rlMatteName)catch()
		rollout rlMatteName "Matte Name"
		(
			edittext etMatteName "Matte Name:" fieldWidth:140 labelOnTop:true pos:[12,20]
			
			on etMatteName entered txt do
			(
				if txt != "" do 
				(
					currIdArr = sort (for obj in objects collect obj.gbufferchannel)
					id = currIdArr[currIdArr.count] + 1
					selection.gbufferchannel = id
					
					--//Add Render Elements
					if (classof curRen == classof theVRRenderer) do --// Vray Renderer
					(
						re.addrenderelement (MultiMatteElement elementName:("M_" + txt) R_gbufIDOn:true R_gbufID:(id) G_gbufIDOn:false G_gbufID:0 B_gbufIDOn:false B_gbufID:0)
					)
				)
				try(destroyDialog ::rlMatteName)catch()
			)
			
			on rlMatteName open do
			(
				setfocus etMatteName
			)
		)
		createDialog rlMatteName 170 100 modal:true style:#(#style_SysMenu, #style_ToolWindow)
	)
	
	
	
	/*Layer Based Materials
	----------------------------------------------------------------------------------------------------*/
	on btnLayerMattes pressed do
	(
		for obj in objects where NOT obj.isHidden do obj.gbufferchannel = 0
		
		currIdArr = sort (for obj in objects collect obj.gbufferchannel)
		id = currIdArr[currIdArr.count]
		
		for i in 1 to layerManager.count-1 by 1 do
		(
			ilayer = layerManager.getLayer i
			theNodes = #()
			
			if ilayer.on do ( --//Only for layers that are actively visible
				ilayer.nodes &theNodes
				
				if theNodes.count >= 1 do
				(
					renderID = id + i
					theNodes.gbufferchannel = renderID
					
	 				--//Add Render Elements
	 				if (classof curRen == classof theVRRenderer) do --// Vray Renderer
	 				(
	 					re.addrenderelement (MultiMatteElement elementName:("M_"+ ilayer.name) R_gbufIDOn:true R_gbufID:(renderID) G_gbufIDOn:false G_gbufID:0 B_gbufIDOn:false B_gbufID:0)
	 				)
				)
			)
		)
	)
	
	
	
	/*Scene Materials
	----------------------------------------------------------------------------------------------------*/
	on btnSceneMaterials pressed do
	(
		curRen = renderers.production
		theVRRenderer = Vray()
		re = maxOps.GetCurRenderElementMgr()
		sceneMats = sceneMaterials
		
		fn getElementName elemName = --// add element to element manager with unique name so it shows in exr's
		(
			highestMatch = 0
			for n = 0 to (re.numrenderelements() - 1) do
			(
				el = re.getrenderelement n
				sameElement = findString el.elementName elemName
				if (sameElement != undefined) then
				(
					highestMatch = 1
					nameParts = filterString el.elementName elemName
					if (nameParts[1] != undefined) then
					(
						endNum = nameParts[1] as integer
						if (endNum != "" and endNum > highestMatch) then
							highestMatch = endNum
					)
				)
			)
			if (highestMatch == 0) then (return elemName) else (return elemName + (((highestMatch as integer) + 1) as string))
		)
		
		--//Object ID's assigning based off active materials
		for o in objects do
		(
			if o.material != undefined do
			(
				chan = findItem sceneMats o.material
				o.gbufferchannel = chan
			)
		)
		
		--//Add Render Elements
		if (classof curRen == classof theVRRenderer) do --// Vray Renderer
		(
			currIds = #()
			for o in objects where o.material != undefined do appendIfUnique currIds (o.gbufferchannel) -- if there is an actual material on the object then get that objects ID #
			sort currIds -- put the id's in numberical order
			
			print currIds.count
			for i = 1 to currIds.count do
			(
				re.addrenderelement (MultiMatteElement elementName:(getElementName("M_" + sceneMats[i].name as string)) R_gbufIDOn:true R_gbufID:(currIds[i]) G_gbufIDOn:false G_gbufID:0 B_gbufIDOn:false B_gbufID:0)
			)
		)
	)
	
	
	/*Selected Materials
	----------------------------------------------------------------------------------------------------*/
	on btnSelectedMaterials pressed do
	(
		if selection.count >= 1 do
		(
			selMats = #()
			for obj in selection where obj.material !=undefined do appendIfUnique selMats obj.material
			for i in 1 to selMats.count by 1 do
			(
				currIdArr = sort (for obj in objects collect obj.gbufferchannel)
				id = currIdArr[currIdArr.count] + 1
				
				for obj in objects where not obj.ishidden AND obj.material == selMats[i] do
				(
					obj.gbufferchannel = id
				)
				
				--//Add Render Elements
				if (classof curRen == classof theVRRenderer) do --// Vray Renderer
				(
					re.addrenderelement (MultiMatteElement elementName:(("M_" + selMats[i].name as string)) R_gbufIDOn:true R_gbufID:(id) G_gbufIDOn:false G_gbufID:0 B_gbufIDOn:false B_gbufID:0)
				)
			)
		)
	)
	
/* Selects unused lights
----------------------------------------------------------------------------------------------------------------------------------*/
	on btnGetLights pressed do
	(
		exLights = fnCollectUsedLights()	-- collect already used lights	
		unUsedLights = for node in lights where (findItem exLights node == 0) AND (superclassof node == light) collect node
		clearSelection()
		select unUsedLights
	)
	
/*Selection Based Mattes for lights
----------------------------------------------------------------------------------------------------*/
	on btnSelLights pressed do
	(
		exLights = fnCollectUsedLights() -- collect already used lights
		selLights = for node in selection where (superclassof node == light) collect node --get selected lights
		unUsedLights = for o in selLights where (findItem exLights o == 0) collect o --return unused lights
		
		if unUsedLights.count >= 1 do
		(			
			try(destroyDialog ::rlMatteName)catch()
			rollout rlMatteName "Matte Name"
			(
				edittext etMatteName "Matte Name:" fieldWidth:140 labelOnTop:true pos:[12,20]
				
				on etMatteName entered txt do
				(
					
					if txt != "" do 
					(
						--//Add Render Elements
						re = maxOps.GetCurRenderElementMgr()
						re.addrenderelement (VRayLightSelect elementName:("L_" + txt) lights:unUsedLights)
					)
					try(destroyDialog ::rlMatteName)catch()
				)
				
				on rlMatteName open do
				(
					setfocus etMatteName
				)
			)
			createDialog rlMatteName 170 100 modal:true style:#(#style_SysMenu, #style_ToolWindow)
		)
	)
)
createDialog rlRenderMattes 170 260 style:#(#style_SysMenu, #style_ToolWindow)