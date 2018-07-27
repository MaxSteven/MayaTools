(
global debugOutput
try(destroydialog nukeEmDialog)catch()
fn safestring stringvar =
(
	stringvar = filterstring stringvar " .|/\<>;:+=*&^%$#@!(){}][~`?\"'"
	safevar = ""
	for i =1 to (stringvar.count - 1) do safevar += (stringvar[i]+"_")
	safevar += stringvar[stringvar.count]
	safevar
)

fn getCamDetails selCam =
(
		local f_length, hap, vap
		struct camdatastruct  (f_length,hap,vap)
		if classof selCam == Main_Camera then
		(
			tmpFOV=selCam.lens.fov_type
			selCam.lens.fov_type=3
			f_length =selCam.lens.focal_length
			hap = selCam.lens.filmgate
			selCam.lens.fov_type=tmpFOV
		)
		else if classof selCam == VRayPhysicalCamera then
		(
			local tempDType,tempDM,focDist
			tempDType = units.DisplayType
			tempDMType = units.MetricType
			
			units.DisplayType = #metric
			units.MetricType = #millimeters
			
			if selCam.specify_focus==true then (focDist = units.formatValue (selCam.focus_distance)) else (focDist = units.formatValue (selCam.target_distance))
			
			units.MetricType = tempDMType
			units.DisplayType = tempDType
			
			focDist = "19343,392043\""
			focDist = filterstring focDist ".;:?//\"',abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
			focDist = (focDist[1]+"."+focDist[2]) as float
			if (focDist - selCam.focal_length) == 0.0 do (focDist += .01)
			
			f_length = ((focDist*selCam.focal_length)/(focDist - selCam.focal_length))*(selCam.zoom_factor)
			hap = selCam.film_width
		)
		else
		(
			tmpFOV = selCam.fovType
			selCam.fovType=2
			f_length = cameraFOV.FOVtoMM selCam.fov 
			hap = getRendApertureWidth()
			selCam.fovType = tmpFOV
		)
		vap=(hap/GetRendImageAspect())
		return camdatastruct f_length hap vap
)

fn getCamFOV camdata =
(
	return [(2*atan(camData.hap/(2*camData.f_length))),(2*atan(camData.vap/(2*camData.f_length)))]
)

fn reconcile3D pPos cam =
(
	fov = getCamFOV (getCamDetails cam)
	tempPoint = point pos:pPos
	pPos = in coordsys cam tempPoint.pos
	delete tempPoint
	pPos /= (pPos.z*-1)
	return (([pPos.x,pPos.y]/[(tan((FOV.x/2))),(tan((FOV.y/2)))])/2)+0.5
	--return (([(atan(pPos.x/(pPos.z*-1.0))),(atan(pPos.y/(pPos.z*-1.0)))]/fov)+0.5)
)

--VARIABLES
struct NukeEmStruct (selObj,selObjSettings,selCam,savePath)
global NukeEm = NukeEmStruct selObj:#() selObjSettings:#()
struct NukeExportLib (
	fn collectObjGeoSettings obj savepath sequence:false=
	(
		if sequence then 
		(
			filepath = (savepath+"\\"+(safestring Obj.name)+"\\Geo\\")+(safestring Obj.name)+"_%04d.obj"
		)
		else
		(
			filepath = (savepath+"\\"+(safestring Obj.name)+"\\Geo\\")+(safestring Obj.name)+"_0000.obj"
		)

		exportData = stringstream ""
		format "	file \"%\"\n" (substitutestring filepath "\\" "/")	to:exportData		-- Switch slash direction for nuke.							
		format "	read_texture_w_coord false\n" 								to:exportData		
		exportData
	),

	fn collectReadKnobs filepath =
	(
		openimg = openbitmap filepath
		exportData = stringstream ""
		format "	file \"%\"\n" (substitutestring filepath "\\" "/")	to:exportData		-- Switch slash direction for nuke.		)
		format "format \"% % 0 0 % % 1 \"\n" openimg.width openimg.height openimg.width openimg.height	to:exportData
		exportData
	),

	fn collectConstantKnobs colorvar channels:"rgba"=
	(
		colorvar /= 255
		exportData = stringstream ""
		format "channels %\n" (channels) to:exportData
		format "color {% % % %}\n" colorvar.r colorvar.g colorvar.b colorvar.a to:exportData
		exportData
	),

	fn CreateNukeNode NodeType NodeName CustomSettings NodePos:[0,0] inputnum:#null = 
	(
		ExportData = Stringstream ""
		
		format "\n% { \n" NodeType to:ExportData
		format "%" (if inputnum != #null then ("	inputs "+(inputnum as string)+"\n") else ("")) to:ExportData
		format "	name % \n " NodeName to:ExportData
		format "	xpos % \n" (NodePos.x as integer) to:ExportData
		format "	ypos % \n" (NodePos.y as integer)to:ExportData
		for i=1 to CustomSettings.count do (format "%" (CustomSettings[i] as string) to:ExportData) -- Add any other pre-formatted node settings
		format "}\n" to:ExportData	
		
		ExportData
	),
	
	fn getAnimationData objNode framerange:[0,100] =
	(
		struct animDataStruct (CamTransform, Transform, type)
		local AnimData = animDataStruct Transform:#() CamTransform:#() type:(superclassof objNode)
		-- Collect Transform Data
		for t in framerange.x to framerange.y do 
		(
			at time t
			(
				if AnimData.type == camera do 
				(
					append AnimData.CamTransform (getCamDetails objNode)
				)
				append AnimData.Transform objNode.transform
			)
		)
		AnimData
	),
	
	fn collectCameraKnobs AnimData framerange:[0,100] =
	(
		local outputScript
		
		outputScript = stringstream ""
		format "	focal {{curve " to:outputScript
		for j =1 to AnimData.camTransform.count do format "x% % " (j - 1 + framerange.x) (formattedprint AnimData.camTransform[j].f_length format:".8f") to:outputScript
		format "	}}\n"	to:outputScript
		format "	haperture {{curve " to:outputScript
		for j =1 to AnimData.camTransform.count do format "x% % " (j - 1 + framerange.x) (formattedprint AnimData.camTransform[j].hap format:".8f") to:outputScript
		format "	}}\n"	to:outputScript
		format "	vaperture {{curve " to:outputScript
		for j =1 to AnimData.camTransform.count do format "x% % " (j - 1 + framerange.x) (formattedprint AnimData.camTransform[j].vap format:".8f") to:outputScript
		format "	}}\n"	to:outputScript
		
		return outputScript
	),
	
	fn collectTransformKnobs AnimData rotOrder:"XZY" xformOrder:"SRT" framerange:[0,100] =
	(
		outputScript = stringstream ""
		format "	xform_order %
	rot_order %
	translate {\n		" xformOrder rotOrder to:outputScript

		-- Begin Transform Output -- 
		
		-- X
		format "{curve " to:outputScript
		for j =1 to AnimData.Transform.count do format "x% % " (j - 1 + framerange.x) (formattedprint AnimData.Transform[j].pos.x format:".8f") to:outputScript
		format "}\n		" to:outputScript
		-- Z
		format "{curve " to:outputScript
		for j =1 to AnimData.Transform.count do format "x% % " (j - 1 + framerange.x) (formattedprint AnimData.Transform[j].pos.z format:".8f") to:outputScript
		format "}\n		" to:outputScript
		-- Y
		format "{curve " to:outputScript
		for j =1 to AnimData.Transform.count do format "x% % " (j - 1 + framerange.x) (formattedprint (AnimData.Transform[j].pos.y*-1) format:".8f") to:outputScript
		format "}\n	" to:outputScript
		
		format "}\n	" to:outputScript 
		
		-- Begin Rotation Output -- 
		format "rotate {\n		" to:outputScript 
		for i = 1 to rotOrder.count do
		(
			if rotOrder[i] == "X" then
			(
				-- X
				if AnimData.type == camera then 
				(
					format "{curve " to:outputScript
					for j =1 to AnimData.Transform.count do format "x% % "  (j - 1 + framerange.x) (formattedprint ((quatToEuler2 AnimData.Transform[j].rotation).x-90) format:".8f") to:outputScript
					format "}\n		" to:outputScript
				)
				else 
				(
					format "{curve " to:outputScript
					for j =1 to AnimData.Transform.count do format "x% % "  (j - 1 + framerange.x) (formattedprint ((quatToEuler2 AnimData.Transform[j].rotation).x) format:".8f") to:outputScript
					format "}\n		" to:outputScript
				)
			)
			else if rotOrder[i] == "Z" then
			(
				-- Z
				format "{curve " to:outputScript
				for j =1 to AnimData.Transform.count do format "x% % "  (j - 1 + framerange.x) (formattedprint (quatToEuler2 AnimData.Transform[j].rotation).z format:".8f") to:outputScript
				format "}\n		" to:outputScript
			)
			else if rotOrder[i] == "Y" then
			(
				-- Y
				format "{curve " to:outputScript
				for j =1 to AnimData.Transform.count do format "x% % "  (j - 1 + framerange.x) (formattedprint (((quatToEuler2 AnimData.Transform[j].rotation).y)*-1) format:".8f") to:outputScript
				format "}\n"	to:outputScript
			)
			else ()
		)
		format "	}\n"	to:outputScript
		outputScript
	),
	
	fn createChanFile animData framerange:[0,100]=
	(
		chanData = stringstream ""
		for i = 1 to animData.Transform.count do
		(
			
			format "%  %  %  %  %  %  %" \
				((i - 1 + framerange.x) as string) \
				(formattedprint animData.Transform[i].pos.x format:".8f") \
				(formattedprint animData.Transform[i].pos.z format:".8f") \
				(formattedprint (animData.Transform[i].pos.y*-1) format:".8f") \
				(formattedprint (if animData.type != camera then ((quatToEuler2 animData.Transform[i].rotation).x) else ((quatToEuler2 animData.Transform[i].rotation).x-90)) format:".8f") \
				(formattedprint ((quatToEuler2 animData.Transform[i].rotation).z) format:".8f") \
				(formattedprint ((quatToEuler2 animData.Transform[i].rotation).y*-1) format:".8f") \				
				to:chanData
			if animData.type == camera do
			(
				format " % % %" \
					(formattedprint animData.CamTransform[i].f_length format:".8f")\
					(formattedprint animData.CamTransform[i].hap format:".8f")\
					(formattedprint animData.CamTransform[i].vap format:".8f")\
					to:chanData
			)
			format "\n" to:chanData
		)
		chanData
	),
	
	fn createCornerFile screenObj cam:undefined framerange:[0,100] cornerFormat:#pin bitmapDims:[320,480]=
	(
		if screenObj != undefined do
		(
			bb = nodeLocalBoundingBox screenObj
			tpoint = point pos:bb[1]
			planeCorners = #()
			append planeCorners (in coordsys screenObj tpoint.pos)
			delete tpoint
			append planeCorners [(planeCorners[1].x*-1),planeCorners[1].y,0]
			append planeCorners [(planeCorners[1].x*-1),(planeCorners[1].y*-1),0]
			append planeCorners [planeCorners[1].x,(planeCorners[1].y*-1),0]
			
			local pinString
			pinString = stringstream ""
			
			if cornerFormat == #pin then
			(
				format "#NukeEm Pin File v001#\n" to:pinString
				for i = 1 to 4 do
				(
					format "corner% {\n" i to:pinString
					for t in framerange.x to framerange.y do 
					(
						at time t 
						(
							pPos = (planeCorners[i]*screenObj.transform)
							format "%\t%\t%\t%\n" (t as integer) (formattedprint pPos.x format:".8f") (formattedprint pPos.y format:".8f") (formattedprint pPos.z format:".8f") to:pinString
						)
					)
					format "}\n" i to:pinString
				)
			)
			else if cornerFormat == #nk then
			(

				if cam != undefined and superclassof cam == camera do
				(
					format "CornerPin2D {\n" to: pinString
					for i = 1 to 4 do
					(
						pointAnimation = #()
						for t in framerange.x to framerange.y do
						(
							at time t
							(
								pPos = (planeCorners[i]*screenObj.transform)
								cornerPos = (reconcile3D pPos cam)
								append pointAnimation #(t,cornerPos)
							)
						)
						format "\tto% {\n" i to: pinString
							format "\t\t{curve*% " renderwidth to:pinString
								for o in pointAnimation do (format "x% % " (o[1] as integer) (formattedprint o[2].x format:".16f") to:pinString)
							format "}\n" to:pinString
							
							format "\t\t{curve*% " renderheight to:pinString
								for o in pointAnimation do (format "x% % " (o[1] as integer) (formattedprint o[2].y format:".16f") to:pinString)
							format "}\n" to:pinString
						format "}\n" to:pinString
					)
					format "from1 {0 0}\n" to:pinString
					format "from2 {% 0}\n" renderwidth to:pinString
					format "from3 {% %}\n" renderwidth renderheight to:pinString
					format "from4 {0 %}\n" renderheight to:pinString
					format "name CornerPin2D1\n" to:pinString
					format "selected true\n" to:pinString
					format "}\n" to:pinString
				)
			)
			else if cornerFormat == #jsx then
			(
				if cam != undefined and superclassof cam == camera do
				(
					format "var pinComp = app.project.items.addComp(\"cornerpin\",%,%,%,%/%,%);\n" renderwidth renderheight renderPixelAspect (framerange.y-framerange.x) frameRate frameRate to:pinString
					format "var pinSolid = pinComp.layers.addSolid([0,255,0] , \"max2afx\", %, %, pinComp.pixelAspect, pinComp.duration);\n" bitmapDims.x bitmapDims.y to:pinString
					format "pinSolid.opacity.setValue(50);\n" to:pinString
					format "var cornerpin = pinSolid.property(\"Effects\").addProperty(\"CC Power Pin\");\n" to:pinString
					for i = 1 to 4 do
					(
						case i of
						(
							1 : j = 4
							2 : j = 3
							3 : j = 1
							4 : j = 2
						)
						for t in framerange.x to framerange.y do
						(
							at time t
							(
								pPos = (planeCorners[j]*screenObj.transform)
								cornerPos = ((reconcile3D pPos cam)*([renderwidth,renderheight])) - ([(renderwidth-bitmapDims.x),(renderheight+bitmapDims.y)]/2)
								format "cornerpin.property(%).setValueAtTime(%/%,[%,%])\n" i t frameRate (formattedprint cornerPos.x format:".8f") (formattedprint (cornerPos.y*-1) format:".8f") to:pinString
							)
						)
					)
				)
			)
		)
		return pinString
	),

	fn getDiffuseNode DiffuseObj NodePosXY:[100,0] =
	(
		objdiffuse = undefined
		objopacity = undefined
		
		try
		(
			try
			(
				if DiffuseObj.material.diffusemap.bitmap.filename != undefined then
				(
					objdiffuse = DiffuseObj.material.diffusemap.bitmap.filename
				)
				else
				(
					objdiffuse = #solidcolor
				)
			)
			catch
			(
				objdiffuse = #solidcolor
			)
		)
		catch
		(
			objdiffuse = #solidcolor
		)
		
		try
		(
			objopacity = DiffuseObj.material.opacitymap.bitmap.filename
		)
		catch
		(
			objopacity = #null
		)
		
		
		if objdiffuse == #solidcolor then
		(
			try(
				objdiffuse = NukeExportLib.CreateNukeNode "Constant" ((safestring DiffuseObj.name)+"_Diffuse_Map") #(NukeExportLib.collectConstantKnobs (DiffuseObj.material.diffuse)) nodepos:[NodeposXY.x+(if objopacity != #null then 50 else 0),NodeposXY.y-35]  inputnum:0
			)
			catch
			(
				objdiffuse = NukeExportLib.CreateNukeNode "Constant" ((safestring DiffuseObj.name)+"_Diffuse_Map") #(NukeExportLib.collectConstantKnobs (DiffuseObj.wirecolor)) nodepos:[NodeposXY.x+(if objopacity != #null then 50 else 0),NodeposXY.y-35] inputnum:0
			)
		)
		else
		(
			objdiffuse = NukeExportLib.CreateNukeNode "Read" ((safestring DiffuseObj.name)+"_Diffuse_Map") #(NukeExportLib.collectReadKnobs (DiffuseObj.material.diffusemap.bitmap.filename)) nodepos:[NodeposXY.x+50,NodeposXY.y-35] inputnum:0	
		)

		if objopacity != #null then
		(
			objopacity = NukeExportLib.CreateNukeNode "Read" ((safestring DiffuseObj.name)+"_Opacity_Map") #(NukeExportLib.collectReadKnobs (objopacity)) nodepos:[NodeposXY.x-50,NodeposXY.y-35] inputnum:0
			format (objdiffuse as string) to:objopacity
			if DiffuseObj.material.opacitymap.MonoOutput == 0 then
			(
				format ((NukeExportLib.CreateNukeNode "Copy" ((safestring DiffuseObj.name)+"_Copy") #(" from0 rgba.red\nto0 rgba.alpha\n") nodepos:[NodeposXY.x,NodeposXY.y+50] inputnum:2) as string) to:objopacity
			)
			else
			(
				format ((NukeExportLib.CreateNukeNode "Copy" ((safestring DiffuseObj.name)+"_Copy") #(" from0 rgba.alpha\nto0 rgba.alpha\n") nodepos:[NodeposXY.x,NodeposXY.y+50] inputnum:2) as string) to:objopacity
			)
			format ((NukeExportLib.CreateNukeNode "Premult" ((safestring DiffuseObj.name)+"_Premult") #() nodepos:[NodeposXY.x,NodeposXY.y+100] inputnum:1) as string) to:objopacity
		)
		else (objopacity = objdiffuse)
		objopacity
	),
	
	fn getEnvironmentNode NodePosXY=
	(
		if UseEnvironmentMap and classof EnvironmentMap == Bitmaptexture then
		(
			objdiffuse = NukeExportLib.CreateNukeNode "Read" ("Environment_Map") #(NukeExportLib.collectReadKnobs (EnvironmentMap.bitmap.filename)) nodepos:NodeposXY inputnum:0	
		)
		else
		(
			objdiffuse = NukeExportLib.CreateNukeNode "Constant" ("Environment_Color") #(NukeExportLib.collectConstantKnobs (backgroundcolor)) nodepos:NodeposXY inputnum:0
		)
		objdiffuse
	),
	
	fn ExportGeo obj exportpath format:#obj sequence:false framerange:[0,100] =
	(
		completiontick =undefined
		if not sequence then 
		(
			framerange = [0,0]
			completiontick = (1 as float/(NukeEm.selObj.count))*100
		)
		else
		(
			completiontick = (1 as float/(NukeEmDialog.CustomGeoEnd.value-NukeEmDialog.CustomGeoStart.value*NukeEm.selObj.count))*100
		)
		exportlength = (framerange.y-framerange.x)

		for t in framerange.x to framerange.y do 
		(
			at time t 
			(
				local objFile
				if t > -1 then
				(
					paddedframenum = substring (((t+10000) as integer)as string) 2 5
				)
				else
				(
					paddedframenum = "-"+(substring (((t-10000) as integer)as string) 4 5)
				)
				
				objFile = exportpath+"\\"+(safestring obj.name)+"_"+paddedframenum+".obj"
				
				if doesFileExist objFile then deletefile objFile
				
				objpos = copy obj.pos.controller
				objrot = copy obj.rotation.controller
				-- for when I implement scale:
				-- objscale = copy obj.scale.controller 
				obj.pos = [0,0,0]
				obj.rotation = (quat 0 0 0 1)
					
					select obj
					exportFile objFile  #noPrompt selectedOnly:true
					deselect $
					
				obj.pos.controller = objpos
				obj.rotation.controller = objrot
				--obj.scale.controller = bobscale
			)
			NukeEmDialog.prgBar.value += completiontick
		)
	),
	
	fn importChan chanPath type:#point =
	(
		if chanPath != undefined and (doesfileexist chanPath) do
		(
			camtypes = #(#maxcam, #vraycam, #b2cam)
			objtypes = #(#point,#dummy,#selection)
			chanfile = openFile chanpath  mode:"r"
			struct chanKeyStruct (frame,pos,rot)
			chanKeys = #()
			while not eof chanfile do
			(
				local keys
				keys = (filterstring (readline chanfile) " \t")
				for i = 1 to keys.count do keys[i]=keys[i] as float
				append chanKeys (chanKeyStruct frame:(keys[1] as integer) pos:[keys[2],(keys[4]*-1),keys[3]] rot:(eulerangles keys[5] (keys[7]*-1) keys[6]))
			)
			
			case type of
			(
				#point: chanPoint = point()
				#dummy: chanPoint = Dummy()
				#maxcam:	chanPoint = Freecamera()
				#vraycam: chanPoint = VRayPhysicalCamera()
				#b2cam: chanPoint = Main_Camera()
				#selection:	if selection.count > 0 then (chanPoint = (selection as array)[1]) else (chaPoint = point())
			)
			
			chanPoint.name == getfilenamefile chanPath
			
			with animate on 
			(
				for i = 1 to chanKeys.count do
				(
					at time (chanKeys[i].frame as integer)
					(
						if (finditem objtypes type > 0) then	chanPoint.rotation.controller.X_Rotation = (chanKeys[i].rot).x 
						else if (finditem camtypes type > 0)  then chanPoint.rotation.controller.X_Rotation = (90+(chanKeys[i].rot).x)
						chanPoint.rotation.controller.Y_Rotation = (chanKeys[i].rot).y 
						chanPoint.rotation.controller.Z_Rotation = (chanKeys[i].rot).z 
						chanPoint.position = chanKeys[i].pos
					)
					i += 1
				)
			)
			return chanPoint
		)
	)
)

global NukeEm = NukeEmStruct selObj:#() selObjSettings:#()
global NukeEmDialog

fn cam_filt obj = (superClassOf obj == camera)
fn geo_filt obj = (superClassOf obj == geometryclass or superClassOf obj == helper)

rollout nukeEmDialog "Nuke 'Em v2.9.2" width:450 height:430
(
	groupbox NukeEmSetup "Object Setup" pos:[5,5] width:440 height:210
		button pickcam "Select Camera" pos:[10,40] width:122 height:27
		button selObjects "Select Objects" pos:[10,70] width:122 height:27
		button outputPathButton "Output Path" pos:[10,100] width:122 height:27
			
		checkbox CustomTimeCheck "Custom Frame Range" pos:[10,145] enabled:true
			
		label CustomStartLabel "S:" pos:[20,165] enabled:false
		spinner CustomStart "" pos:[32,165] range:[-9999,9999,2] enabled:false width:50 type:#integer
		button resetCustomS "reset" pos:[82,165] width:50 height:16 enabled:false
			
		label CustomEndLabel "E:" pos:[20,185] enabled:false
		spinner CustomEnd "" pos:[32,185] range:[-9999,9999,2] enabled:false width:50 type:#integer
		button resetCustomE "reset" pos:[82,185] width:50 height:16 enabled:false
			
			
		multilistbox SelectedObjectsLB "Objects" width:148 height:12 pos:[137,23] enabled:false
			
		groupbox ObjectExportGroup "Object Export Settings" pos:[286,33] width:154 height:168
			
			label GeoTypeLabel "File Format:" pos:[324,55] enabled:false
			dropdownlist GeoTypeDrop ""  pos:[385,50] width:50 items:#("OBJ","FBX") enabled:false
			
			label TransformLabel "Transform Order:" pos:[297,78] enabled:false
			dropdownlist TransformOrderDrop ""  pos:[385,75] width:50 items:#("SRT","STR","RST","RTS","TSR","TRS") enabled:false
			label RotationLabel "Rotation Order:" pos:[305,103] enabled:false
			dropdownlist RotationOrderDrop ""  pos:[385,100] width:50 items:#("XYZ","XZY","YXZ","YZX","ZXY","ZYX") enabled:false selection:2
			checkbox GeoSeqCheck "Geometry Sequence" pos:[300,125] 
			checkbox CustomGeoTimeCheck "Custom Geo-Seq Range" pos:[300,145] enabled:false
			label CustomGeoStartLabel "S:" pos:[300,165] enabled:false
			spinner CustomGeoStart "" range:[-9999,9999,2] pos:[310,165] enabled:false width:50 type:#integer
			label CustomGeoEndLabel "E:" pos:[372,165] enabled:false
			spinner CustomGeoEnd "" range:[-9999,9999,2] pos:[382,165] enabled:false width:50 type:#integer
			button resetCustomGeoS "reset" pos:[310,180] width:50 height:15 enabled:false
			button resetCustomGeoE "reset" pos:[382,180] width:50 height:15 enabled:false
		
		
	groupbox OutputGroup "Output Settings" pos:[5,220] height:125 width:440
		checkbox sceneGenerator "Create Scene Nodes" checked:true pos:[15,240] teooltip:"Create scene and scanline render nodes in Nuke."
		checkbox textureObjectsCheck "Create Shaders" checked:true pos:[15,257] tooltip:"Create scene and scanline render nodes in Nuke."
		checkbox CreateBackdropsCheck "Create Backdrops" enabled:false checked:false pos:[15,274] tooltip:"Create scene and scanline render nodes in Nuke."
		checkbox CreateEnvironmentCheck "Create Environment" checked:true pos:[15,291] tooltip:"Create scene and scanline render nodes in Nuke."
			
		checkbox NukeScriptCheck "Output Nuke Script" checked:false pos:[158,240] teooltip:"Create scene and scanline render nodes in Nuke."
		checkbox ShowNukeScriptCheck "Show Nuke Script" checked:false pos:[158,257] tooltip:"Create scene and scanline render nodes in Nuke."
		checkbox ChanFilesCheck "Output Chan Files" enabled:true checked:false pos:[158,274] tooltip:"Create scene and scanline render nodes in Nuke."
		checkbox GeoFilesCheck "Output Geo Files" enabled:true checked:true pos:[158,291] tooltip:"Create scene and scanline render nodes in Nuke."
			
		button nukeEm_btn "Nuke 'Em!" pos:[280,240] width:155 height:67 enabled:false tooltip:"Copies animation data to clipboard to be pasted in Nuke."
			
		progressBar PrgBar "ProgressBar" pos:[15,321] width:420 height:15 
	
	groupbox importGroup "Import" pos:[5,350] height:75 width:195
		button importChan_btn "Import Chan" pos:[10,370] height:25 width:80
		button importASCII_btn "Import ASCII" pos:[10,395] height:25 width:80 enabled:false
		dropdownlist chanTypeDrop "Object Type:" pos:[95,374] width:100 items:#("Point","Dummy","Selected Object","Max Cam", "Brazil 2 Cam", "Vray Cam")
		
	groupbox qExportGroup "Quick Export Selected" pos:[205,350] height:75 width:205
		
		button exportTrans_btn "Transform" pos:[210,370] height:25 width:65 enabled:true
		button exportObj_btn "Geo" pos:[275,370] height:25 width:30 enabled:true
		button exportNKPin_btn "NK Corner Pin File" pos:[210,395] height:25 width:95 enabled:true
		button export3DPin_btn "3D Corner Pin File" pos:[310,370] height:25 width:95
		button exportAEPin_btn "AE Corner Pin File" pos:[310,395] height:25 width:95
	--subrollout SubUtilityRollout "Utilities" width:450 pos:[0,357] height:60
	
	fn getNukeEmDialogtimeRanges =
	(
		if NukeEmDialog.CustomTimeCheck.checked then 
		(
			startTime = NukeEmDialog.CustomStart.value
			endtime = NukeEmDialog.CustomEnd.value
			geostartTime = NukeEmDialog.CustomGeoStart.value
			geoendtime = NukeEmDialog.CustomGeoEnd.value
		)
		else
		(
			startTime = animationRange.start
			endtime = animationRange.end
			if NukeEmDialog.customGeoTimeCheck.checked then
			(
				geostartTime = animationRange.start
				geoendtime = animationRange.end
			)
			else
			(
				geostartTime = NukeEmDialog.CustomGeoStart.value
				geoendtime = NukeEmDialog.CustomGeoEnd.value
			)
		)
		return #(startTime, endtime, geostartTime, geoendtime)
	)
			
	on NukeEmDialog open do
	(
		CustomGeoStart.value = CustomStart.value = animationRange.start
		CustomGeoEnd.value = CustomEnd.value = animationRange.end
	)
	
	on NukeEmDialog close do
	(
		NukeEmStruct = undefined
		NukeEm = undefined
		NukeExportLib = undefined
		geo_filt = undefined
		cam_filt = undefined
		gc()
	)
	
	on pickcam pressed do 
	(
		NukeEm.selCam = selectByName title: "Select a Camera" Filter:cam_filt single:true;
		If NukeEm.selCam != undefined do
		(
			pickcam.text = (safestring NukeEm.selCam.name)
			nukeEm_btn.enabled = true
		)
	)
	
	on selObjects pressed do 
	(
		selObjList=selectByName title: "Select single or multiple objects" Filter:geo_filt;
		if selObjList != undefined then NukeEm.selObj = selObjList
		if NukeEm.selObj.count >0  then
		(
			selObjects.text = (NukeEm.selObj.count as string)+" Objects Selected"
		)
		NukeEmDialog.SelectedObjectsLB.items = for o in NukeEm.selObj collect (safestring o.name)
		--nukeemdialog.selectedobjectslb.selection = #{1..(nukeemdialog.selectedobjectslb.items.count)}
		nukeEm_btn.enabled = true
	)
	
	on OutputPathButton pressed do
	(
		OutputPathVar = getSavePath initialDir:maxFilePath
		if OutputPathVar != undefined do
		(
			NukeEm.SavePath = OutputPathVar
			nukeEm_btn.enabled = true
			OutputPathVar = filterstring OutputPathVar "\\"
			OutputPathButton.text = "...\\"+(OutputPathVar[OutputPathVar.count])
		)
	)
	
	on CustomTimeCheck changed c do
	(
		if c == true then
		(
			CustomStartLabel.enabled = CustomStart.enabled = resetCustomS.enabled = CustomEndLabel.enabled = CustomEnd.enabled = resetCustomE.enabled = true
		)
		else
		(
			CustomStartLabel.enabled = CustomStart.enabled = resetCustomS.enabled = CustomEndLabel.enabled = CustomEnd.enabled = resetCustomE.enabled = false
		)
	)
	
	on CustomStart changed c do
	(
		if not customGeoTimeCheck.checked do (customGeoStart.value = c)
	)
	
	on CustomEnd changed c do
	(
		if not customGeoTimeCheck.checked do (customGeoEnd.value = c)
	)
	
	on GeoSeqCheck changed c do
	(
		if c == true then
		(
			CustomGeoTimeCheck.enabled = true
			if CustomGeoTimeCheck.checked == true then
			(
				CustomGeoStartLabel.enabled = CustomGeoStart.enabled = CustomGeoEndLabel.enabled = CustomGeoEnd.enabled = resetCustomGeoS.enabled = resetCustomGeoE.enabled = true
			)
			else 
			(
				CustomGeoStartLabel.enabled = CustomGeoStart.enabled = CustomGeoEndLabel.enabled = CustomGeoEnd.enabled = resetCustomGeoS.enabled = resetCustomGeoE.enabled = false
			)
		)
		else
		(
			CustomGeoTimeCheck.enabled = CustomGeoStartLabel.enabled = CustomGeoStart.enabled = CustomGeoEndLabel.enabled = CustomGeoEnd.enabled = resetCustomGeoS.enabled = resetCustomGeoE.enabled = false
		)			
	)
	
	on CustomGeoTimeCheck changed c do
	(
		if c == true then
		(
			CustomGeoStartLabel.enabled = CustomGeoStart.enabled = CustomGeoEndLabel.enabled = CustomGeoEnd.enabled = resetCustomGeoS.enabled = resetCustomGeoE.enabled = true
		)
		else 
		(
			CustomGeoStartLabel.enabled = CustomGeoStart.enabled = CustomGeoEndLabel.enabled = CustomGeoEnd.enabled = resetCustomGeoS.enabled = resetCustomGeoE.enabled = false
		)
	)
	
	on resetCustomS pressed do
	(
		customStart.value = animationrange.start
	)
	
	on resetCustomE pressed do
	(
		customEnd.value = animationrange.End
	)
	
	on resetCustomGeoS pressed do
	(
		customGeoStart.value = animationrange.start
	)
	
	on resetCustomGeoE pressed do
	(
		customGeoEnd.value = animationrange.End
	)
	
	on nukeEm_btn pressed do
	(
		undo "Export to Nuke" on
		(
		proceed = true
		if NukeEm.Savepath == undefined do
		(
			if GeoFilesCheck.checked and ((for o in NukeEm.selObj where classof o != target collect o).count) > 0 do proceed = false
			if ChanFilesCheck.checked do proceed = false
			if NukeScriptCheck.checked do proceed = false
		)
		if not proceed then
		(
			OutputPathVar = getSavePath initialDir:maxFilePath
			if OutputPathVar != undefined then
			(
				NukeEm.SavePath = OutputPathVar
				nukeEm_btn.enabled = true
				OutputPathVar = filterstring OutputPathVar "\\"
				OutputPathButton.text = "...\\"+(OutputPathVar[OutputPathVar.count])
				proceed = true
			)
			else
			(
				messagebox "You are attempting to output files.  Please choose an output path and try again."
			)
		)
		if proceed do
		(
			NukeScript = stringstream ""
			disableSceneRedraw()
			
			times = nukeEmDialog.getNukeEmDialogtimeRanges()
			local startTime = times[1]
			local endTime = times[2]
			local geoStartTime = times[3]
			local geoEndTime = times[4]

			if NukeEm.selCam != undefined then
			(
				local transformScript, animData
				animData = NukeExportLib.getAnimationData NukeEm.selCam  FrameRange:[startTime,endtime]
				transformScript = NukeExportLib.collectTransformKnobs (animData) xformOrder:(NukeEmDialog.TransformOrderDrop.selected) rotOrder:(NukeEmDialog.RotationOrderDrop.selected) FrameRange:[startTime,endtime]
				camScript = NukeExportLib.collectCameraKnobs (animData) FrameRange:[startTime,endtime]
				
				format ((NukeExportLib.CreateNukeNode "Camera" (safestring NukeEm.selCam.name) #((transformScript),(camScript)) NodePos:[150,100]) as string) to:NukeScript
				format "push [stack 0]\n push [stack 0]\n" to:NukeScript
				
				if NukeEmDialog.ChanFilesCheck.checked do
				(
					chanfile = createfile (NukeEm.SavePath+"\\"+(safestring NukeEm.selCam.name)+".chan")
					format ((NukeExportLib.createChanFile animData FrameRange:[startTime,endtime]) as string) to:chanfile
					close chanfile
				)
				
			)
			
			if NukeEm.selObj.count > 0 then
			(
				gwExportINI = getDir #plugcfg + "\\gw_objexp.ini" 
				GWObjPreset = getINISetting gwExportINI "General" "Preset"
				GWObjFlipZy = getINISetting gwExportINI "Geometry" "FlipZyAxis"
				GWObjExportMat = getINISetting gwExportINI "Material" "UseMaterial"

				setINISetting gwExportINI "General" "Preset" "Nuke"
				setINISetting gwExportINI "Geometry" "FlipZyAxis" "1"
				setINISetting gwExportINI "Material" "UseMaterial" "0"
				
				for i =1 to NukeEm.selObj.count do
				(
					local transformScript, animData
					animData = NukeExportLib.getAnimationData NukeEm.selObj[i]  FrameRange:[startTime,endtime]
					debugOutput  = AnimData
					transformScript = NukeExportLib.collectTransformKnobs (animData) xformOrder:NukeEmDialog.TransformOrderDrop.selected rotOrder:NukeEmDialog.RotationOrderDrop.selected FrameRange:[startTime,endtime]
					-- export each object to OBJ file
					NodeXPos = (((0-(NukeEm.selObj.count-1))/2)+(i-1))*200
					if (superclassof NukeEm.selObj[i] == geometryclass and classof NukeEm.selObj[i] != targetobject and NukeEm.savepath != undefined) do
					(
						makedir (NukeEm.savepath+"\\"+(safestring NukeEm.selObj[i].name)+"\\")
						if NukeEmDialog.GeoFilesCheck.Checked do 
						(
							makedir (NukeEm.savepath+"\\"+(safestring NukeEm.selObj[i].name)+"\\Geo")
							NukeExportLib.ExportGeo NukeEm.selObj[i] (NukeEm.SavePath+"\\"+(safestring NukeEm.selObj[i].name)+"\\Geo") sequence:NukeEmDialog.GeoSeqCheck.checked format:#obj FrameRange:[geostartTime,geoEndtime]
						)
						if NukeEmDialog.textureObjectsCheck.checked do
						(
							format ((NukeExportLib.getDiffuseNode NukeEm.selObj[i] nodeposxy:[NodeXPos,-200]) as string) to:NukeScript
						)
						format ((NukeExportLib.CreateNukeNode "ReadGeo" (safestring NukeEm.selObj[i].name) #((substitutestring (NukeExportLib.collectObjGeoSettings NukeEm.selObj[i] NukeEm.savepath sequence:(NukeEmDialog.GeoSeqCheck.checked)) "%" "\%")) nodepos:[NodeXPos, -50] inputnum:(if NukeEmDialog.textureObjectsCheck.checked then #null else 0)) as string) to:NukeScript
					)
					format ((NukeExportLib.CreateNukeNode "TransformGeo" (safestring NukeEm.selObj[i].name) #((transformScript)) nodepos:[NodeXPos, 0] inputnum:(if (superclassof NukeEm.selObj[i] == geometryclass and classof NukeEm.selObj[i] != targetobject) then #null else 0)) as string) to:NukeScript
					if NukeEmDialog.ChanFilesCheck.checked do
					(
						makedir (NukeEm.savepath+"\\"+(safestring NukeEm.selObj[i].name)+"\\chan")
						chanfile = createfile (NukeEm.SavePath+"\\"+(safestring NukeEm.selObj[i].name)+"\\chan\\"+(safestring NukeEm.selobj[i].name)+".chan")
						format ((NukeExportLib.createChanFile animData FrameRange:[startTime,endtime]) as string) to:chanfile
						close chanfile
					)
				)
				setINISetting gwExportINI "General" "Preset" GWObjPreset
				setINISetting gwExportINI "Geometry" "FlipZyAxis" GWObjFlipZy
				setINISetting gwExportINI "Material" "UseMaterial" GWObjExportMat
			)
			
			if sceneGenerator.checked then
			(
				if NukeEm.selCam != undefined then (inputs = NukeEm.selObj.count+1; renderInputs = 3)			
				else (inputs = NukeEm.selObj.count; renderInputs = 2)
				format "Scene {\ninputs " to:NukeScript
				format "%\n" inputs to:NukeScript
				format"name Scene1\nxpos 0\nypos 100\n}\n" to:NukeScript
				if not NukeEmDialog.CreateEnvironmentCheck.checked then (
					format "push 0\n" to:NukeScript
				)
				else
				(
					format ((NukeExportLib.getEnvironmentNode [-200,100]) as string) to:NukeScript
					format ((NukeExportLib.CreateNukeNode "Reformat" "Render_Output_Size" #("format \""+RenderWidth as string+" "+RenderHeight as string+" 0 0 "+RenderWidth as string+" "+RenderHeight as string+" "+RenderPixelAspect as string+" 3ds_Max_Render\"") nodepos:[-200,200]) as string) to:NukeScript
				)
				format "ScanlineRender {\ninputs " to:NukeScript
				format "%" renderInputs to:NukeScript
				format "\nname ScanlineRender1\nxpos 0\nypos 200\n}" to:NukeScript
			)
			setclipboardText NukeScript as string
			if NukeEmDialog.ShowNukeScriptCheck.checked do
			(
				debug = newscript()
				format "Root {
 inputs 0
 first_frame %
 last_frame %
 fps %
 format \" % % 0 0 % % 1 3dsmax_render\"
}\n" (substring (animationrange.start as string) 1 ((animationrange.start as string).count - 1)) (substring (animationrange.end as string) 1 ((animationrange.end as string).count - 1)) (framerate as string) (RenderWidth as string) (RenderHeight as string) (RenderWidth as string) (RenderHeight as string) to:debug
				
				format (substitutestring (NukeScript as string) "%" "\%") to:debug
			)
			if NukeEmDialog.NukeScriptCheck.checked do
			(
				nukefilename = if maxfilename != "" then (getfilenamefile maxfilename) else ("Untitled")
				nukefilepath = (NukeEm.SavePath+"\\"+NukeFileName+".nk")
				nukefile = createfile nukefilepath
				format "Root {
 inputs 0
 first_frame %
 last_frame %
 fps %
 format \" % % 0 0 % % 1 3dsmax_render\"
}\n" (substring (animationrange.start as string) 1 ((animationrange.start as string).count - 1)) (substring (animationrange.end as string) 1 ((animationrange.end as string).count - 1)) (framerate as string) (RenderWidth as string) (RenderHeight as string) (RenderWidth as string) (RenderHeight as string) to:nukefile
				format (substitutestring (NukeScript as string) "%" "\%") to:nukefile
				close nukefile
			)
			enableSceneRedraw()
			NukeEmDialog.prgBar.value=0
		) 
		) -- end undo
	)-- end NukeEm
	
	on importChan_btn pressed do
	(
		undo "Import Chan" on
		(
			chanFile = getOpenFilename caption:"Open A Chan File" types:"Chan (*.chan)|*.chan|All (*.*)|*.*|"
			if chanFile != undefined do
			(
				chanType = case NukeEmDialog.chanTypeDrop.selected of
				(
					"Point":#point
					"Dummy":#dummy
					"Selected Object":#selection
					"Max Cam":#maxcam
					"Brazil 2 Cam":#b2cam
					"Vray Cam":#vraycam
				)
				NukeExportLib.importChan chanFile type:chanType
			)
		)
	)
	
	on export3DPin_btn pressed do
	(
		disablesceneredraw()
		
		camString= stringstream ""
		cornerCam = undefined
		
		times = nukeEmDialog.getNukeEmDialogtimeRanges()
		local startTime = times[1]
		local endTime = times[2]
		
		if NukeEm.selCam == undefined then
		(
			cornerCam = selectByName title: "Select a Camera" Filter:cam_filt single:true;
		)
		else
		(
			cornerCam = NukeEm.selCam
		)
		if NukeEm.SavePath == undefined then
		(
			pinFile = getsavefilename caption:"Save Corner Pin File" filename:"CornerPin.pin" types:"Corner Pin (*.pin)|*.pin" historyCategory:"CornerPinPin"
		)
		else
		(
			pinFile = getsavefilename caption:"Save Corner Pin File" filename:(NukeEm.SavePath+"\CornerPin.pin") types:"Corner Pin (*.pin)|*.pin" historyCategory:"CornerPinPin"
		)
		if pinFile != undefined do
		(
			if cornerCam != undefined do
			(
			
			local transformScript, animData
			animData = NukeExportLib.getAnimationData cornerCam  FrameRange:[startTime,endtime]
				
			--	export Nuke Camera Node ---
			--	transformScript = NukeExportLib.collectTransformKnobs (animData) FrameRange:[startTime,endtime]
			--	camString = NukeExportLib.collectCameraKnobs (animData) FrameRange:[startTime,endtime]
			--	format ((NukeExportLib.CreateNukeNode "Camera" (safestring cornerCam.name) #((transformScript),(camScript)) NodePos:[150,100]) as string) to:camString
				
			format "Camera [%] {\n" (safestring cornerCam.name) to:camString
			format ((NukeExportLib.createChanFile animData FrameRange:[startTime,endtime]) as string) to:camString
			format "}" to:camString
				
			)
			
			pinFile = openFile pinFile mode:"w"
			selObj = (selection as array)[1]
			format ((NukeExportLib.createCornerFile selObj framerange:[startTime,endtime]) as string) to:pinFile
			format (camString as string) to:pinFile
			close pinFile
		)
		enablesceneredraw()
	)
	
	on exportAEPin_btn pressed do
	(
		
		times = nukeEmDialog.getNukeEmDialogtimeRanges()
		local startTime = times[1]
		local endTime = times[2]
		
		disablesceneredraw()
		cornerCam = undefined
		if NukeEm.selCam == undefined then
		(
			cornerCam = selectByName title: "Select a Camera" Filter:cam_filt single:true;
		)
		else
		(
			cornerCam = NukeEm.selCam
		)
		if cornerCam != undefined do
		(
			if NukeEm.SavePath == undefined then
			(
				pinFile = getsavefilename caption:"Save After Effects Corner Pin File" filename:"CornerPin.jsx" types:"Corner Pin (*.jsx)|*.jsx" historyCategory:"CornerPinJSX"
			)
			else
			(
				pinFile = getsavefilename caption:"Save After Effects Corner Pin File" filename:(NukeEm.SavePath+"\CornerPin.jsx") types:"Corner Pin (*.jsx)|*.jsx" historyCategory:"CornerPinJSX"
			)
			if pinFile != undefined do
			(
				rollout bitmapDimPrompt "AE Footage Dimensions" width:250
				(
					spinner dimWidth "Width:" type:#integer range:[0,32000,320] pos:[40,5] width:80
					spinner dimHeight "Height:" type:#integer range:[0,32000,480] pos:[145,5] width:80
					Button dimGo "Export"
					
					on dimGo pressed do
					(
						global AEDims
						AEDims = [dimWidth.value,dimHeight.value]
						DestroyDialog bitmapDimPrompt
					)
					
				)

				CreateDialog bitmapDimPrompt modal:true
				pinFile = openFile pinFile mode:"w"
				selObj = (selection as array)[1]
				format ((NukeExportLib.createCornerFile selObj cam:cornerCam framerange:[startTime,endTime] cornerFormat:#jsx bitmapdims:AEDims) as string) to:pinFile
				close pinFile
				AEDims = undefined
			)
		)
		enablesceneredraw()
	)
	
	on exportNKPin_btn pressed do
	(
		times = nukeEmDialog.getNukeEmDialogtimeRanges()
		local startTime = times[1]
		local endTime = times[2]
		
		disablesceneredraw()
		cornerCam = undefined
		if NukeEm.selCam == undefined then
		(
			cornerCam = selectByName title: "Select a Camera" Filter:cam_filt single:true;
		)
		else
		(
			cornerCam = NukeEm.selCam
		)
		if cornerCam != undefined do
		(
			if NukeEm.savePath == undefined then
			(
				pinFile = getsavefilename caption:"Save Nuke Corner Pin File" filename:"CornerPin.nk" types:"Nuke Script (*.nk)|*.nk" historyCategory:"CornerPinNK"
			)
			else
			(
				pinFile = getsavefilename caption:"Save Nuke Corner Pin File" filename:(NukeEm.SavePath+"\CornerPin.nk") types:"Nuke Script (*.nk)|*.nk" historyCategory:"CornerPinNK"
			)
			selObj = (selection as array)[1]
			pinNode = (NukeExportLib.createCornerFile selObj cam:cornerCam framerange:[startTime,endTime] cornerFormat:#nk)
			if pinFile != undefined do
			(
				pinFile = openFile pinFile mode:"w"
				format (pinNode as string) to:pinFile
				close pinFile
			)
		)
		setclipboardText (pinNode as string)
		enablesceneredraw()
	)
	
	on exportTrans_btn pressed do
	(
		local transformScript, animData, nukeScript
		
		times = nukeEmDialog.getNukeEmDialogtimeRanges()
		local startTime = times[1]
		local endTime = times[2]
		
		nukeScript = stringstream ""
		selObj = (Selection as array)[1]
		
		if selObj != undefined do
		(
			animData = NukeExportLib.getAnimationData selObj  FrameRange:[startTime,endtime]
			if superclassof selObj == camera then
			(
				transformScript = NukeExportLib.collectTransformKnobs (animData) xformOrder:(NukeEmDialog.TransformOrderDrop.selected) rotOrder:(NukeEmDialog.RotationOrderDrop.selected) FrameRange:[startTime,endtime]
				camScript = NukeExportLib.collectCameraKnobs (animData) FrameRange:[startTime,endtime]
				format ((NukeExportLib.CreateNukeNode "Camera" (safestring selObj.name) #((transformScript),(camScript)) NodePos:[0,0]) as string) to:NukeScript
			)
			else if (superclassof selObj == helper) or (superclassof selObj == geometryclass) then
			(
				transformScript = NukeExportLib.collectTransformKnobs (animData) xformOrder:NukeEmDialog.TransformOrderDrop.selected rotOrder:NukeEmDialog.RotationOrderDrop.selected FrameRange:[startTime,endtime]
				format ((NukeExportLib.CreateNukeNode "TransformGeo" (safestring selObj.name) #((transformScript)) nodepos:[0,0] inputnum:(if (superclassof selObj == geometryclass and classof selObj != targetobject) then #null else 0)) as string) to:NukeScript
			)
			setClipboardText (nukeScript as string)
		)
	)
	
	on exportObj_btn pressed do
	(
		local nukeScript, savePath
		
		local times = nukeEmDialog.getNukeEmDialogtimeRanges()
		local startTime = times[1]
		local endTime = times[2]
		local geoStartTime = times[3]
		local geoEndTime = times[4]
		
		local selObj = (selection as array)[1]
		
		nukeScript = stringstream ""
		
		if NukeEm.SavePath == undefined then
		(
			savePath = getSavePath initialDir:maxFilePath
		)
		else
		(
			savepath = nukeEm.savePath
		)
		
		if savePath != undefined do
		(
			if superclassof selObj == GeometryClass do
			(
				makedir (savePath+"\\"+(safestring selObj.name)+"\\Geo")
				NukeExportLib.ExportGeo selObj (SavePath+"\\"+(safestring selObj.name)+"\\Geo") sequence:NukeEmDialog.GeoSeqCheck.checked format:#obj FrameRange:[geostartTime,geoEndtime]
				format ((NukeExportLib.CreateNukeNode "ReadGeo" (safestring selObj.name) #((substitutestring (NukeExportLib.collectObjGeoSettings selObj savepath sequence:(NukeEmDialog.GeoSeqCheck.checked)) "%" "\%")) nodepos:[0,0] inputnum:(0)) as string) to:NukeScript
				setClipboardText (nukeScript as string)
			)
		)
	)
	
)-- end rollout
rollout NukeEmUtilDialog "Utilities" (
	button Utility1Button "Utility 1"
)
rollout NukeEmHelpDialog "Help" (
	button Help1Button "Help"
)

createDialog NukeEmDialog pos:[200,200]

--addsubrollout NukeEmDialog.SubUtilityRollout NukeEmUtilDialog
--addsubrollout NukeEmDialog.SubUtilityRollout NukeEmHelpDialog
)