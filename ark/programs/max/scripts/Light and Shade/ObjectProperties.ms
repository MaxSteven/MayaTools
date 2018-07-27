--Used to get Vray Object Properties
--	getUserPropBuffer $

try(destroyDialog ::rlObjectProperties)catch()
rollout rlObjectProperties "Object Properties"
(
	fn fnDisplayUpdate count = (
	displayTempPrompt (count as string + " - Objects Sucessfuly Changed") 1000
	)
	
	groupbox gpVRObjProps "VRay Object Properties" width:180 height:48 pos:[10,6]
	button btnMatteObj "Matte Obj" height:20 width:80 pos:[20,24]
	button btnUnMatteObj "Unmatte Obj" height:20 width:80 pos:[100,24]
	groupbox gpObjProps "Object Properties" width:180 height:125 pos:[10,60]
	button btnRenderable "Renderable" height:20 width:80 pos:[20,80]
	button btnNonRenderable "NonRenderable" height:20 width:80 pos:[100,80]
	button btnVisible "Visible-Cam" height:20 width:80 pos:[20,105]
	button btnInvisible "Invisible-Cam" height:20 width:80 pos:[100,105]
	button btnVisibleRR "Reflect-Refract" height:20 width:80 pos:[20,130]
	button btnInvisibleRR "No Refl/Refr" height:20 width:80 pos:[100,130]
	button btnCastShadows "Cast Shadows" height:20 width:80 pos:[20,155]
	button btnNoShadows "No Shadows" height:20 width:80 pos:[100,155]
	
	--//Matte Object
	on btnMatteObj pressed do 
	(
		for obj in selection do
		(
			setUserProp obj "VRay_MoBlur_GeomSamples" 2
			setUserProp obj "VRay_GI_Generate" False
			setUserProp obj "VRay_GI_Receive" False
			setUserProp obj "VRay_GI_Multipier" 0.000000
			setUserProp obj "VRay_GI_GenerateMultipier" 0.000000
			setUserProp obj "VRay_GI_SubdivsMultiplier" 0.000000
			setUserProp obj "VRay_Caustics_Generate" False
			setUserProp obj "VRay_Caustics_Receive" False
			setUserProp obj "VRay_Caustics_Multipier" 0.000000
			setUserProp obj "VRay_MoBlur_DefaultGeomSamples" True
			setUserProp obj "VRay_Matte_Enable" True
			setUserProp obj "VRay_Matte_Alpha" -1.000000
			setUserProp obj "VRay_Matte_Shadows" False
			setUserProp obj "VRay_Matte_ShadowAlpha" False
			setUserProp obj "VRay_Matte_ShadowColor" [0,0,0]
			setUserProp obj "VRay_Matte_ShadowBrightness" 0.000000
			setUserProp obj "VRay_Matte_ReflectionAmount" 0.000000
			setUserProp obj "VRay_Matte_RefractionAmount" 0.000000
			setUserProp obj "VRay_Matte_GIAmount" 0.000000
			setUserProp obj "VRay_Matte_GI_OtherMattes" True
			setUserProp obj "VRay_GI_SurfaceID" 0
			setUserProp obj "VRay_GI_VisibleToGI" False
			setUserProp obj "VRay_GI_VisibleToReflections" False
			setUserProp obj "VRay_GI_VisibleToRefractions" False
			fnDisplayUpdate selection.count
		)
	)	
	on btnUnMatteObj pressed do 
	(
		for obj in selection do 
		(
			setUserProp obj "VRay_MoBlur_GeomSamples" 2
			setUserProp obj "VRay_GI_Generate" True
			setUserProp obj "VRay_GI_Receive" True
			setUserProp obj "VRay_GI_Multipier" 1.000000
			setUserProp obj "VRay_GI_GenerateMultipier" 1.000000
			setUserProp obj "VRay_GI_SubdivsMultiplier" 1.000000
			setUserProp obj "VRay_Caustics_Generate" True
			setUserProp obj "VRay_Caustics_Receive" True
			setUserProp obj "VRay_Caustics_Multipier" 1.000000
			setUserProp obj "VRay_MoBlur_DefaultGeomSamples" True
			setUserProp obj "VRay_Matte_Enable" False
			setUserProp obj "VRay_Matte_Alpha" 1.000000
			setUserProp obj "VRay_Matte_Shadows" False
			setUserProp obj "VRay_Matte_ShadowAlpha" False
			setUserProp obj "VRay_Matte_ShadowColor" [0,0,0]
			setUserProp obj "VRay_Matte_ShadowBrightness" 1.000000
			setUserProp obj "VRay_Matte_ReflectionAmount" 1.000000
			setUserProp obj "VRay_Matte_RefractionAmount" 1.000000
			setUserProp obj "VRay_Matte_GIAmount" 1.000000
			setUserProp obj "VRay_Matte_GI_OtherMattes" True
			setUserProp obj "VRay_GI_SurfaceID" 0
			setUserProp obj "VRay_GI_VisibleToGI" True
			setUserProp obj "VRay_GI_VisibleToReflections" True
			setUserProp obj "VRay_GI_VisibleToRefractions" True
			fnDisplayUpdate selection.count			
		)
	)
	
	--//Renderable
	on btnRenderable pressed do for obj in selection do (
		obj.renderable = true
		fnDisplayUpdate selection.count
	)
	on btnNonRenderable pressed do for obj in selection do (
		obj.renderable = false
		fnDisplayUpdate selection.count
	)
	
	--//Visible to camera
	on btnVisible pressed do for obj in selection do (
		obj.primaryVisibility = true 
		fnDisplayUpdate selection.count
	)
	on btnInvisible pressed do for obj in selection do (
		obj.primaryVisibility = false
		fnDisplayUpdate selection.count
	)
	
	--//Visible to reflections/refractions
	on btnVisibleRR pressed do for obj in selection do (
		obj.secondaryVisibility  = true 
		fnDisplayUpdate selection.count
	)
	on btnInvisibleRR pressed do for obj in selection do (
		obj.secondaryVisibility  = false
		fnDisplayUpdate selection.count
	)
	
	--//Casts shadows 
	on btnCastShadows pressed do for obj in selection do (
		obj.castShadows = true 
		fnDisplayUpdate selection.count
	)
	on btnNoShadows pressed do for obj in selection do (
		obj.castShadows = false
		fnDisplayUpdate selection.count
	)
)
createDialog rlObjectProperties 200 195