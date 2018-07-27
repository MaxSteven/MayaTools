-- Viewport Background
-- Ram Player Loading
-- Creates Vray light mtl
-- Creates bitmap texture map and places in active material slot
-- Creates Vray dome light with image in texture slot
   -- faked hdri
   -- sphereical mapping
	-- mirror U
	-- mixmap Output
--FrameRangeBug

try(destroyDialog ::rlShotTools)catch()
rollout rlShotTools "Shot Tools"
(
	local platesDir = ""
	local filename = undefined
	
	fn fnMakeIFL theSeq = -- creates IFL sequence based off the sourced file
	(
		if filename != undefined do
		(
			baseName = trimRight (getFilenameFile filename) "1234567890"
			ioType = getFilenameType filename
			thePath = getFilenamePath filename
			pattern = (thePath + baseName + "*" + ioType)
			theIfl = createFile (theSeq + ".ifl")
			theFiles = sort (getFiles pattern)
			for f in theFiles do
			(
				format "%\n" (filenameFromPath f) to:theIfl
			)
			close theIfl
			--//UI Information update
			frameCount = (theFiles.count as string)
			rlShotTools.lbNumFr.text = frameCount
		) 
	)

	groupbox gpbxJob "Shot Reference" width:220 height:65 pos:[10,8]
	edittext etOutputDir text:platesDir width:180 height:17 pos:[14,26] readonly:true
	button btnSource "..." width:20 height:16 pos:[200,27]
	label lbSeq "Load as image sequence:" pos:[19,50]
	label lbNumFr "0" width:50 pos:[145,50]
	checkbox ckbxLoadSeq "" pos:[200,50] checked:true
	button btnViewportBkg "Viewport Background" width:110 height:18 pos:[10,80] tooltip:"Loads image/sequence into active viewport background."
	button btnRamPlayer "Ram Player" width:110 height:18 pos:[120,80] tooltip:"Loads image/sequence into ram player."
 	button btnLightMtl "LightMtl Texture" width:110 height:18 pos:[10,98] tooltip:"Creates VrayLightMtl with image/sequence as diffuse texture."
	button btnBitmap "Bitmap Texture" width:110 height:18 pos:[120,98] tooltip:"Creates image/sequence texture mape in active slot of material editor."
 	button btnDomeLight "DomeLight" width:110 height:18 pos:[10,116] tooltip:"Creates spherical dome light with image/sequence in texture slot."
 	button btnImagePlane "Image Plane" width:110 height:18 pos:[120,116] tooltip:"Creates image plane with image/sequence as texture with proper aspet ratio."
 	button btnStandardMat "Standard Self-Illum" width:110 height:18 pos:[10,134] tooltip:"Creates standard self illuminated material with image/sequence as diffuse texture."
	button btnCameraMap "Camera Map Selected" width:110 height:18 pos:[120,134] tooltip:"Camera maps the selected object with image/sequence as diffuse texture in a VrayLightMtl."
	
	on btnSource pressed do
	(
		dir = maxfilepath
		pathParts = filterstring dir "\\"
		rootDir = ""
		for p = 1 to (pathParts.count - 2) do rootDir += pathParts[p] + "\\"
		platesDir = (rootDir + "ASSETS\\")
		
		filename = getOpenFileName caption:"Shot Plates" filename:(platesDir) --types:"Object Preset(*.rtp)|*.rtp" \
		etOutputDir.text = if filename == undefined then "" else filename
		fnMakeIFL filename
	)
	
	--// Viewport Background
	on btnViewportBkg pressed do 
	(
		if filename != undefined and etOutputDir.text != "" do
		(
			if ckbxLoadSeq.state then 
			(--// Image Sequence
				fnMakeIFL filename
				backgroundImageFileName = (filename + ".ifl")
				setBkgFrameRange [0,(lbNumFr.text as integer),1]
				setBkgImageAnimate true
			)
			else
			(--// Image Still
				backgroundImageFileName = filename
				setBkgImageAnimate false
			)
			state = not viewport.DispBkgImage -- make vice versa
			viewport.DispBkgImage = state
			setBkgImageAspect #view
			InvalidateAllBackgrounds()
			completeRedraw()
		)
	)
	
	--// Camera Map
	on btnCameraMap pressed do
	(
		try(destroyDialog ::rlSceneCameras)catch()
		rollout rlSceneCameras "Scene Cameras"
		(			
			label lbSelCam "Map to camera:" pos:[10,10]
			dropdownlist dlCameras "" items:#() width:120 pos:[90,8] selection:0
			button btnApply "Apply Camera Map" width:200 height:24 pos:[10,36] tooltip:"Adds a CameraMap(WSM) modifier to each object in the selection if it doesn't already exist."
			
			on rlSceneCameras open do (
				dlCameras.items = for i in cameras where superclassof i == Camera collect i.name
			)
			
			on btnApply pressed do (
				cam = if dlCameras.selected != undefined then getNodeByName dlCameras.selected else undefined	
					
				if selection.count >= 1 and cam!= undefined then (
					for obj in selection do (
						if superclassof obj == GeometryClass or superclassof obj == shape do ( --Only applies to objects that are of geometry or shapes superclass
							if classof obj.modifiers[1] == SpaceCameraMap then (
								--//Camera Map Mod already exists
								obj.modifiers[1].camera = cam
								)else (
								--//Camera Map Mod does not exists
								addModifier obj (SpaceCameraMap camera:cam) --//Add world space camera map modifier with assigned camera
							)
						)
					)
				)else(
					messagebox "Not a valid selection and/or camera!"
				)
			)
		)
		createDialog rlSceneCameras 220 70 style:#(#style_SysMenu, #style_ToolWindow)
	)
	
	--// RamPlayer 
	on btnRamPlayer pressed do 
	(
		if filename != undefined and etOutputDir.text != "" do 
		(
			if ckbxLoadSeq.state then 
			(--// Image Sequence
				fnMakeIFL filename
				RAMPlayer (filename + ".ifl") ""
			) 
			else 
			(--// Image Still
				RAMPlayer filename ""
			)
		)
	)
	
	
	
	--// Vray Light Material 
	on btnLightMtl pressed do
	(
		if (filename != undefined) and (etOutputDir.text != "") do 
		(
			if ckbxLoadSeq.state then
			(--// Image Sequence
				fnMakeIFL filename
				LiteMat = VRayLightMtl texmap:(Bitmaptexture fileName:(filename + ".ifl"))
				assignNewName LiteMat
				meditmaterials[medit.GetActiveMtlSlot()] = LiteMat
				medit.UpdateMtlEditorBrackets()
				max mtledit
			) 
			else 
			(--// Image Still
				LiteMat = VRayLightMtl texmap:(Bitmaptexture fileName:filename)
				assignNewName LiteMat
				meditmaterials[medit.GetActiveMtlSlot()] = LiteMat
				medit.UpdateMtlEditorBrackets()
				max mtledit
			)
		)
	)
	
	
	
	--// Bitmap texturemap to active mtl slot 
	on btnBitmap pressed do
	(
		if (filename != undefined) and (etOutputDir.text != "") do 
		(
			if ckbxLoadSeq.state then
			(--// Image Sequence
				fnMakeIFL filename
				Plates = bitmaptexture fileName:(filename + ".ifl")
				meditmaterials[medit.GetActiveMtlSlot()] = Plates
				medit.UpdateMtlEditorBrackets()
				max mtledit
			) 
			else 
			(--// Image Still
				fnMakeIFL filename
				Plates = bitmaptexture fileName:filename
				meditmaterials[medit.GetActiveMtlSlot()] = Plates
				medit.UpdateMtlEditorBrackets()
				max mtledit
			)
		)
	)	
	
	
	
	--// Vray dome light with material 
	on btnDomeLight pressed do
	(
		if (filename != undefined) and (etOutputDir.text != "") do 
		(
			if ckbxLoadSeq.state then
			(--// Image Sequence
				fnMakeIFL filename
				domeLight = VRayLight texmap:(Bitmaptexture fileName:(filename + ".ifl")) dome_spherical:on type:1 multiplier:1.0 on:on castShadows:on rgb:(color 255 255 255) rgbFilter:(color 222.916 262.558 296.125) invisible:on intensityType:0 originalintensity:1500 useMultiplier:off shiftColorWhenDimming:off useFarAttenuation:off displayFarAttenuationGizmo:off startFarAttenuation:80 endFarAttenuation:200 contrast:0 softenDiffuseEdge:0 projector:off affectDiffuse:on affectSpecular:on ambientOnly:off targetDistance:240 light_length:122 light_width:61 light_Radius:13 atmosShadows:off atmosOpacity:100 atmosColorAmt:100 shadowMultiplier:1 shadowColorMapEnable:off shadowColor:(color 0 0 0) lightAffectsShadow:off useGlobalShadowSettings:off hotspot:30 falloff:60 showCone:off xRotation:0 yRotation:0 zRotation:0
				select domeLight
			) 
			else 
			(--// Image Still
				fnMakeIFL filename
				domeLight = VRayLight texmap:(Bitmaptexture fileName:filename) dome_spherical:on type:1 multiplier:1.0 on:on castShadows:on rgb:(color 255 255 255) rgbFilter:(color 222.916 262.558 296.125) invisible:on intensityType:0 originalintensity:1500 useMultiplier:off shiftColorWhenDimming:off useFarAttenuation:off displayFarAttenuationGizmo:off startFarAttenuation:80 endFarAttenuation:200 contrast:0 softenDiffuseEdge:0 projector:off affectDiffuse:on affectSpecular:on ambientOnly:off targetDistance:240 light_length:122 light_width:61 light_Radius:13 atmosShadows:off atmosOpacity:100 atmosColorAmt:100 shadowMultiplier:1 shadowColorMapEnable:off shadowColor:(color 0 0 0) lightAffectsShadow:off useGlobalShadowSettings:off hotspot:30 falloff:60 showCone:off xRotation:0 yRotation:0 zRotation:0
				select domeLight
			)
		)
	)
	
	
	--// Image Plane creates image with proper aspect ratio
	on btnImagePlane pressed do
	(
		if (filename != undefined) and (etOutputDir.text != "") do 
		(
			if ckbxLoadSeq.state then
			(--// Image Sequence
				fnMakeIFL filename 
				LiteMat = StandardMaterial diffuseMap:(Bitmaptexture fileName:(filename + ".ifl")) selfIllumAmount:0 showInViewport:true
				--LiteMat = VRayLightMtl texmap:(Bitmaptexture fileName:(filename + ".ifl")) showInViewport:true
				assignNewName LiteMat
			) 
			else 
			(--// Image Still
				LiteMat = StandardMaterial diffuseMap:(Bitmaptexture fileName:filename) selfIllumAmount:0 showInViewport:true
				--LiteMat = VRayLightMtl texmap:(Bitmaptexture fileName:filename) showInViewport:true
				assignNewName LiteMat
			)
			--Image Plane Creation
			bmpInfo = (getBitmapInfo filename)
			imgWidth = bmpInfo[3]
			imgHeight = bmpInfo[4]
			imgPlane = plane widthsegs:1 lengthsegs:1 width:(imgWidth*.5) length:(imgHeight*.5) pos:[0,0,0] rotation:(eulerangles -90 0 0) material:LiteMat 
		)
		forceCompleteRedraw()
	)
	
	
	--// Standard Material Self Illuminations
	on btnStandardMat pressed do
	(
		if (filename != undefined) and (etOutputDir.text != "") do 
		(
			if (filename != undefined) and (etOutputDir.text != "") do 
			(
				if ckbxLoadSeq.state then
				(--// Image Sequence
					fnMakeIFL filename
					StandardMat = StandardMaterial diffuseMap:(Bitmaptexture fileName:(filename + ".ifl")) selfIllumAmount:100 showInViewport:true
					assignNewName StandardMat
					meditmaterials[medit.GetActiveMtlSlot()] = StandardMat
					medit.UpdateMtlEditorBrackets()
					max mtledit
				) 
				else 
				(--// Image Still
					StandardMat = StandardMaterial diffuseMap:(Bitmaptexture fileName:filename) selfIllumAmount:100 showInViewport:true
					assignNewName StandardMat
					meditmaterials[medit.GetActiveMtlSlot()] = StandardMat
					medit.UpdateMtlEditorBrackets()
					max mtledit
				)
			)
		)
		forceCompleteRedraw()
	)
	
	on rlShotTools open do
	(
		etOutputDir.text = platesDir
	)
)
createDialog rlShotTools 240 160 style:#(#style_SysMenu, #style_ToolWindow)