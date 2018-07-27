--bug (needs to apply to only selected objects and elements
--gw.wtext [100,100,0] "----------------------------------" color:green

try(destroyDialog ::rlIDTools)catch()
rollout rlIDTools "ID Tools"
(
	--//Variables
	---------------------------------------------------
	local theFont = dotnetobject "System.Drawing.Font" "Arial" 8
	
	--//Functions
	---------------------------------------------------
	fn labelFactory ctrl txt = --//dotNet labels
	(
		local theLab = ctrl 
		theLab.Font = theFont
		theLab.BackColor = (dotNetClass "System.Drawing.Color").fromARGB 20 20 20
		theLab.ForeColor = (dotNetClass "System.Drawing.Color").fromARGB 255 255 255
		theLab.TextAlign = theLab.TextAlign.MiddleLeft
		theLab.Text = txt
		theLab
	)
	
	fn buttonFactory ctrl txt =
	(
		local theBut = ctrl
		theBut.Font = theFont
		theBut.flatStyle=theBut.flatStyle.flat
		theBut.flatAppearance.BorderSize = 0
		theBut.flatappearance.bordercolor = (dotNetClass "System.Drawing.Color").fromARGB 20 20 20
		theBut.BackColor = (dotNetClass "System.Drawing.Color").fromARGB 70 70 70
		theBut.ForeColor = (dotNetClass "System.Drawing.Color").fromARGB 255 255 255
		theBut.flatappearance.mouseoverbackcolor = (dotNetClass "System.Drawing.Color").fromARGB 20 20 20 
		theBut.flatappearance.mousedownbackcolor = (dotNetClass "System.Drawing.Color").fromARGB 215 0 0
		theBut.TextAlign = theBut.TextAlign.MiddleCenter
		theBut.Text = txt
		theBut
	)
	

	--//UI Controls
	---------------------------------------------------

	dotNetControl lbMin "Label" pos:[10,10] width:72 height:30
	groupbox gpMin "" pos:[10,4] width:223 height:67
	spinner spMin "" pos:[85,17] range:[0,999999999,0] type:#integer fieldwidth:35 
	button btnMin "+" pos:[135,14] width:22 height:22
	dotNetControl lbMax "Label" pos:[10,41] width:72 height:30
	spinner spMax "" pos:[85,48] range:[0,999999999,0] type:#integer fieldwidth:35
	button btnMax "+" pos:[135,45] width:22 height:22
	button btnApplyRange "Apply" pos:[160,14] width:69 height:53
	
	dotNetControl lbAutoID "Label" pos:[10,80] width:72 height:30 --158 152 162 162
	groupbox gpAutoID "" pos:[10,74] width:223 height:36
	button btnUniqueID "Unique" pos:[88,84] width:44 height:22
	button btnMatIDs "Mat" pos:[135,84] width:30 height:22
	button btnWirecolorIDs "Wirecolor" pos:[168,84] width:61 height:22
	
	dotNetControl lbDisplay "Label" pos:[10,119] width:72 height:30
	groupbox gpDisplay"" pos:[10,113] width:223 height:36
	checkbutton btnInfo "Info" pos:[88,123] width:69 height:22
	button btnWirecolorDis "Wirecolor" pos:[160,123] width:69 height:22
	
	dotNetControl lbID "Label" pos:[10,158] width:72 height:30
	groupbox gpID"" pos:[10,152] width:223 height:36
	spinner spID "" pos:[85,165] range:[0,999999999,10] type:#integer fieldwidth:35 
	button btnIdPicker "<" pos:[135,162] width:22 height:22
	button btnSelect "Select" pos:[160,162] width:69 height:22
	
	dotNetControl lbWireSelect "Label" pos:[10,197] width:72 height:30
	groupbox gpWireSelect "" pos:[10,191] width:223 height:36
	button btnObjIDSelect "by Object ID" pos:[88,201] width:69 height:22
	button btnWireSelect "by Wirecolor" pos:[160,201] width:69 height:22
	
	on btnMin pressed do
	(
		for o in selection do o.gbufferchannel = spMin.value
	)
	
	on btnMax pressed do
	(
		for o in selection do o.gbufferchannel = spMax.value
	)
	
	on btnApplyRange pressed do
	(
		for i = 1 to selection.count do 
		(
			selection[i].gbufferchannel = (random spMin.value spMax.value)
		)
	)
	
	on btnIdPicker rightclick do 
	(
		obj = pickObject prompt:"select object"	
		
		if obj != undefined do
		(
			spID.value = obj.gbufferchannel
		)
	)
	
	on btnIdPicker pressed do 
	(
		if selection.count  >= 1 do
		(
			spID.value = selection[1].gbufferchannel
		)
	)
	
	on btnSelect pressed do
	(
		if keyboard.controlPressed or keyboard.shiftPressed then 
		(
			ObjArr = for obj in objects where obj.gbufferchannel == spID.value AND not obj.isHidden collect obj
			selectmore ObjArr
			
			)else (
			
			clearSelection()
			ObjArr = for obj in objects where obj.gbufferchannel == spID.value AND not obj.isHidden collect obj
			select ObjArr
		)
	)

	on btnInfo changed state do
	(
		fn showObjectNames=
		(
			gw.setTransform(Matrix3 1)
			for o in objects where not o.isHidden do
			(
			gw.text o.pos (o.gbufferchannel as string) color:yellow
			)
			gw.enlargeUpdateRect #whole
			gw.updateScreen()
			forceCompleteRedraw()
		)
		registerRedrawViewsCallback showObjectNames
		
		if state then 
		(
			showObjectNames()
			
			)else(
			
			unRegisterRedrawViewsCallback showObjectNames
			forceCompleteRedraw()
		)
	)
	
	on btnWirecolorDis pressed do
	(
		local objIDarr = #()
		local Colorsarr = #()
		
		for obj in selection do
		(
			appendIfUnique objIDarr obj.gbufferchannel
		)
		
		for i = 1 to objIDarr.count do 
		(
			appendIfUnique Colorsarr [random 0 255,random 0 255,random 0 255]
		)
		
		for obj in selection do 
		(
			idx = findItem objIDarr obj.gbufferchannel
			obj.wirecolor = Colorsarr[idx]
		)
	)

	on btnObjIDSelect pressed do
	(
		if selection.count >= 1 do
		(
			local objArr = for obj in objects where not obj.isHidden collect obj
			local objIDArr = for o in selection collect o.gbufferchannel
			
			matchingObjsArr = for o in objArr where (findItem objIDArr o.gbufferchannel != 0) collect o
			
			select matchingObjsArr
		)
	)

	on btnWireSelect pressed do
	(
		if selection.count >= 1 do
		(
			local objArr = for obj in objects where not obj.isHidden collect obj
			local colorsArr = for o in selection collect o.wirecolor
			
			matchingObjsArr = for o in objArr where (findItem colorsArr o.wirecolor != 0) collect o
			
			select matchingObjsArr
		)
	)
	
	on btnUniqueID pressed do 
	(
		selection.gbufferchannel = 0
		
		local currIdArr = sort (for obj in objects collect obj.gbufferchannel)
		
		for i = 1 to selection.count do
		(
			id = currIdArr[currIdArr.count] + i
			selection[i].gbufferchannel = id
		)
	)
	
	on btnWirecolorIDs pressed do
	(
		selection.gbufferchannel = 0
		
		local currIdArr = sort (for obj in objects collect obj.gbufferchannel)
		local colorsArr = #()
		
		for o in selection do appendIfUnique colorsArr o.wirecolor
		
		for c = 1 to colorsArr.count do --set an ID for each wirecolor group
		(
			local matchingObjs = for o in selection where o.wirecolor == colorsArr[c] collect o
			
			id = currIdArr[currIdArr.count] + c
			for obj in matchingObjs do obj.gbufferchannel = id
		)
	)

	on btnMatIDs pressed do
	(
		selection.gbufferchannel = 0
		
		local currIdArr = sort (for obj in objects collect obj.gbufferchannel)
		local sceneMats = for i in sceneMaterials where superClassof i == material  collect i
		
		for c = 1 to sceneMats.count do --set an ID for each material group
		(
			local matchingObjs = for o in selection where o.material == sceneMats[c] collect o
			
			id = currIdArr[currIdArr.count] + c
			for obj in matchingObjs do obj.gbufferchannel = id
		)
	)
	
-- 	on btnApplyRange pressed do (
-- 		if selection.count >= 1 do (
-- 			type = subobjectlevel	
-- 			
-- 			if type == 0 or type == undefined do (
-- 				print "objects"
-- 			)
-- 			if type == 4 do (
-- 				print "polygons"
-- 			)
-- 			if type == 5 do (
-- 				print "elements"
-- 			)
-- 		)
-- 	)

	on rlIDTools open do
	(
		labelFactory lbMin " ID Min:"
		labelFactory lbMax " ID Max:"
		labelFactory lbID " ID Selector:"
		labelFactory lbDisplay " ID Display:"
		labelFactory lbAutoID " Auto ID:"
		labelFactory lbWireSelect  " Select:"
	)
)
createDialog rlIDTools 241 234 style:#(#style_SysMenu, #style_ToolWindow) --bgColor:(color 58 58 58)