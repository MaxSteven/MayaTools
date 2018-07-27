/*
Maxwell light lister additions
History:
2012-04-15 | v1 | initial release | Eric Mehl
2012-04-16 | v1.1 | fixed bug with scanning the scene for multi-materials | EM
2012-04-17 | v1.2 | added ability to change material name in the light lister

TO DO:
* Add support for sky lights - waiting for fix to max plugin by Next Limit to expose variables needed

*/

-- MacroScript File
-- Created:       Jan 15 2002
-- Last Modified: May 05 2007
-- Light Lister Script 2.8
-- Version: 3ds max 6
-- Author: Alexander Esppeschit Bicalho [discreet]
--***********************************************************************************************
-- MODIFY THIS AT YOUR OWN RISK

/* History
- added support for mr_Sky, mr_SkyPortal, and mr_Sun (LAM)
- fixed mentalray shadow map list bug by zhangy
- Added product switcher: this macro file can be shared with all Discreet products
- Added Support to Mental Ray Lights and Plugin Script lights - this uses 4 functions to manage Delegate properties
- Added Support to Blur_Adv. Shadows and mental Ray shadows
- Enabled Luminaire support
- Enabled Deletion Callback
- Removed Blur Adv. Shadows from the UI (they're still in the Engine) since PF's spec calls for that
- Fixed divide by 0 on adding mr lights to the list
- Fixed an incorrect try/catch loop that would crash the script when radiosity was present
- Fixed crash on Refresh after deleting light - maxwellLLister.UIControlList not reset, contained deleted node (LAM)
- Added support for MultiProduct (IFDEFs for #VIZR) (AB)
- Added support to Global Shadow Generator - when a Global Shadow Generator is changed, the Refresh button is
  highlighted to warn the user he needs a refresh
- Fixed problem when launching the Light Lister when lights have manipulators enabled
- Added LineOffset and YOffset to help Japanese/Chinese localization
*/

/*

macros.run "Lights and Cameras" "Light_list"

This Light Lister supports all new lights in 3ds max 5:

- Photometric Lights
- Skylights
- IES Sun

It also supports the new shadows types:

- Area Shadows
- Adv. Raytraced shadows

*/

/* Expanding the Light Lister -- AB Jun 20, 2002

This Light Lister does not automatically support new light or shadow plugins.

For them to be supported, you need to make several changes in the script:

-- Class Definitions

Here the classes for each light types are defined. If you want to add a new light type, add a new class entry and list the
classes in the array
In the end of the script, each class definition is scanned and generates the UI entries.
You'll also need to change the script to parse and collect all instances of your class, as is done with the current code.

-- Properties

The function CreateControls generates the dynamic rollout containing all spinners, properties, etc.
The controls are grouped by light type and handle special cases like different parameter names for MAX lights and Photometric
lights. The On/Off checkbox is an example of how to handle a control that is tied to a property in a scene light.
In the example below, ControlName is the control name and Property is the property you want to expose/access.

	maxwellLLister.maxLightsRC.addControl #checkbox (("ControlName" + maxwellLLister.count as string) as name) "" \
		paramStr:("checked:" + (maxwellLLister.LightIndex[maxwellLLister.count][1].Property as string) + " offset:[8,-22] width:18")
	maxwellLLister.maxLightsRC.addHandler (("ControlName" + maxwellLLister.count as string) as name) #'changed state' filter:on \
		codeStr:("maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1].Property = state")

Notice the controls are all aligned using Offset. If you add a new control, you need to reorganize the remaining controls.

-- Exposing Shadow Plugins

Shadow plugins are harder to expose because each shadow has a different set of parameters, or even different parameter
names. The framework to expose them is similar to the one to expose the properties, but you need to create special cases
for each shadowplugin or each property.
For instance, if your shadow plugin class is myShadow and it exposes a Bias Property called myShadowBias, you'll need to
change the Bias Control and the Shadow Dropdown. In the Bias Control, you need to read the Bias value, and change the
event so it checks for the correct class and sets the property.
In the Shadow Dropdown event, you need to set the control state and value acording to the shadow class.

In any case, make sure you keep a copy of the original Light Lister so you can come back to it in case you have problems

*/
-- macroScript Maxwell_Light_List enabledIn:#("max", "viz", "vizr") category:"EM Tools"  internalCategory:"EM Tools"  ButtonText:"Light Lister..." tooltip:"Maxwell Light Lister"  Icon:#("hypothetical_icons",2)
(
Debug = false

struct maxwellLightListerStruct (onExecute,onIsChecked,onCloseDialogs,version, \
							GlobalLightParameters, LightInspectorSetup, LightInspectorFloater, ShadowPlugins, ShadowPluginsName, \
							maxwellLightsList, maxwellLightTypeStrings, maxwellColorStrings, maxwellLuminanceTypeStrings, maxwellUnitStrings, \
							maxwellEnviroStrings, maxwellEnviroLights, maxwellLightMatPairs, \
							maxLightsList, LSLightsList, SkyLightsList, SunLightsList, enableUIElements, \
							LuminairesList, maxLightsRC, CreateLightRollout, UIControlList, DeleteCallback, disableUIElements, \
							LightInspectorListRollout, LLUndoStr, count, lbcount, lightIndex, decayStrings, totalLightCount, \
							miLightsList, getLightProp, setLightProp, setShdProp, getShdProp, fnShadowClass, enableRefreshBtn, \
							mrSkyLightsList, mrSunLightsList, mrSkyPortalLightsList, MRSkyPortal_ShadowSamples, MRSkyPortal_Modes, \
							yOffset, LineOffset)

global maxwellLLister, LListerYOffset
if maxwellLLister == undefined or Debug == true then (maxwellLLister = maxwellLightListerStruct())

-- Strings for Localization

maxwellLLister.decayStrings = #("None","Inverse","Inv. Square")
maxwellLLister.maxwellLightTypeStrings = #("Color + Luminance","Temperature","MXI/HDR Texture")
maxwellLLister.maxwellColorStrings = #("RGB","Correlated")
maxwellLLister.maxwellLuminanceTypeStrings = #("Watts + Efficacy","Intensity","IES")
maxwellLLister.maxwellUnitStrings = #("Lumen","Lux","Candela","Nit")
maxwellLLister.maxwellEnviroStrings = #("Sky Dome", "Physical Sky")
maxwellLLister.LLUndoStr = "LightLister"

local dialogUp = false

-- End Strings

-- Positioning to help localization

LListerYOffset = 0
maxwellLLister.yOffset = LListerYOffset
maxwellLLister.LineOffset = 0

-- Useful Functions

fn subtractFromArray myArray mySub =
(
	tmpArray = #()
	for i in myArray do append tmpArray i
	for i in mySub do


	(
		itemNo = finditem tmpArray i
		local newArray = #()
		if itemNo != 0 do
		(
			for j in 1 to (itemNo-1) do append newArray tmpArray[j]
			for j in (itemNo+1) to tmpArray.count do append newArray tmpArray[j]
			tmpArray = newArray
		)
	)
	tmpArray
)

fn SortNodeArrayByName myArray =
(
qsort myArray (fn myname v1 v2 = (if v1.name < v2.name then 0 else 1))
myArray
)

fn copyArray array1 = for i in array1 collect i

fn wrapString inString =
(
	local string1In = "\\"
	local string1Out = "\\\\"
	local string2In = "\""
	local string2Out = "\\\""
	local temp_text_string = substituteString inString string1In string1Out
	temp_text_string = substituteString temp_text_string string2In string2Out
	temp_text_string = string2In + temp_text_string + string2In
	temp_text_string -- return value
)

fn disableUIElements array1 = for i in array1 do execute ("maxLightsRollout." + i as string + ".enabled = false")
maxwellLLister.disableUIElements = disableUIElements

fn enableRefreshBtn lightobj =
(
	if (maxwellLLister.GetLightProp lightObj #useGlobalShadowSettings) == true do
	(
		maxwellLLister.LightInspectorSetup.BtnReload.Checked = true
	)
)
maxwellLLister.enableRefreshBtn = enableRefreshBtn

fn getLightProp obj prop =
(
	if (isProperty obj prop) and not (isProperty obj #delegate) then
		getProperty obj prop
	else
		if isProperty obj #delegate then
			if isProperty obj.delegate prop then
				getProperty obj.delegate prop
			else undefined
		else undefined
)
maxwellLLister.getLightProp = getLightProp

fn setLightProp obj prop val =
(
	if (isProperty obj prop) and not (isProperty obj #delegate) then
		setProperty obj prop val
	else
		if isProperty obj #delegate then
			if isProperty obj.delegate prop then
				setProperty obj.delegate prop val
			else undefined
		else undefined
)
maxwellLLister.setLightProp = setLightProp

fn getShdProp obj prop =
(
	if (isProperty obj #shadowGenerator) and not (isProperty obj #delegate) then
		if (isProperty obj.ShadowGenerator prop) do getProperty obj.ShadowGenerator prop
	else
		if isProperty obj #delegate then
			if isProperty obj.delegate #ShadowGenerator then
				if (isProperty obj.delegate.ShadowGenerator prop) do getProperty obj.delegate.ShadowGenerator prop
			else undefined
		else undefined
)
maxwellLLister.getShdProp = getShdProp

fn setShdProp obj prop val =
(
	if (isProperty obj #shadowGenerator) and not (isProperty obj #delegate) then
		if (isProperty obj.ShadowGenerator prop) do
		(
			setProperty obj.ShadowGenerator prop val
			maxwellLLister.enableRefreshBtn obj
		)
	else
		if isProperty obj #delegate then
			if isProperty obj.delegate #ShadowGenerator then
				if (isProperty obj.delegate.ShadowGenerator prop) do
				(
					setProperty obj.delegate.ShadowGenerator prop val
					maxwellLLister.enableRefreshBtn obj
				)
			else undefined
		else undefined
)
maxwellLLister.setShdProp = setShdProp

fn fnShadowClass obj = classof (maxwellLLister.getLightProp obj #shadowGenerator)
maxwellLLister.fnShadowClass = fnShadowClass

-- Collect Shadow Plugins

/* -- Removed Automatic Shadow Plugin Collection

maxwellLLister.ShadowPlugins = (subtractFromArray shadow.classes #(Missing_Shadow_Type))
qSort maxwellLLister.ShadowPlugins (fn namesort v1 v2 = if ((v1 as string)as name) > ((v2 as string)as name) then 1 else 0)
maxwellLLister.ShadowPluginsName = for i in maxwellLLister.ShadowPlugins collect i as string

*/

-- Hardcoded shadow plugins to the ones available

	maxwellLLister.ShadowPlugins = #(Adv__Ray_Traced, mental_ray_Shadow_Map, Area_Shadows, shadowMap, raytraceShadow)
	maxwellLLister.ShadowPluginsName = #("Adv. Ray Traced", "mental_ray_Shadow_Map", "Area Shadows", "Shadow Map", "Raytrace Shadow")

/* -- uncomment if you want the Blur Shadows
maxwellLLister.ShadowPlugins = #(Adv__Ray_Traced, mental_ray_Shadow_Map, Area_Shadows, Blur_Adv__Ray_Traced, shadowMap, raytraceShadow)
maxwellLLister.ShadowPluginsName = #("Adv. Ray Traced", "mental_ray_Shadow_Map", "Area Shadows", "Blur Adv. Ray Traced","Shadow Map", "Raytrace Shadow")
*/
	maxwellLLister.MRSkyPortal_ShadowSamples = for i = 1 to 10 collect (2^i) as string
	maxwellLLister.MRSkyPortal_Modes = #("Existing", "Envir.", "Custom") -- correspond to mode values of 2, 0, 1

-- Main Function

local CreateLightRollout

fn createLightRollout myCollection selectionOnly:false =
(
	maxwellLLister.LightInspectorSetup.pbar.visible = true

	-- Class Definitions

	maxLights = #(TargetDirectionallight, targetSpot, Directionallight, Omnilight, freeSpot)
	SkyLights = #(IES_Sky, Texture_Sky, Skylight)
	SunLights = #(IES_Sun) -- AB: Jun 20, 2002
	LSLights = #(Free_Area, Target_Area, Free_Linear, Target_Linear, Free_Point, Target_Point,
					   Free_Sphere, Target_Sphere, Free_Disc, Target_Disc, Free_Cylinder, Target_Cylinder)
	Luminaires = #(Luminaire)
	mrLights = #(miAreaLight, miAreaLightomni)
	mrSkyLight = #(mr_sky)
	mrSunLight = #(mr_sun)
	mrSkyPortalLight = #(mr_sky_portal)

	maxwellLights = #(Maxwell_Material)

	-- Scene parser

	SceneLights = MyCollection as array
	sceneMaxLights = #()
	sceneLSLights = #()
	sceneSkyLights = #()
	sceneSunLights = #()
	sceneLuminaires = #()
	scenemiLights = #()
	scenemrSkyLights = #()
	scenemrSunLights = #()
	scenemrSkyPortalLights = #()
	sceneMaxwellLights = #()
	sceneMaxwellEnviroLights = false

	for i in SceneLights do
	(
		LightClass = classof i
		if findItem MaxLights LightClass != 0 do append sceneMaxLights i
		if findItem LSLights LightClass != 0 do append sceneLSLights i
		if findItem SkyLights LightClass != 0 do append sceneSkyLights i
		if findItem SunLights LightClass != 0 do append sceneSunLights i
		if findItem Luminaires LightClass != 0 do append sceneLuminaires i
		if findItem mrLights LightClass != 0 do append scenemiLights i
		if findItem mrSkyLight LightClass != 0 do append scenemrSkyLights i
		if findItem mrSunLight LightClass != 0 do append scenemrSunLights i
		if findItem mrSkyPortalLight LightClass != 0 do append scenemrSkyPortalLights i
	)

	if classof renderers.current == MaxwellRenderer then (
		maxwellLLister.maxwellLightMatPairs = #()	--this will be an array storing two element arrays that have 1: emitter instance 2: parent material instance
		--collect maxwell lights by scanning materials
		for mat in sceneMaterials do (
			if (classof mat) == Maxwell_Material then (
				lyrs = mat.Layers
				for i in lyrs do (
					if (i.Emitter != undefined) then (
						i.Emitter.name = mat.name	--change the name of the emitter to the material name so it is available for creating controls
						append sceneMaxwellLights #(i.Emitter)	--append the actual emitter instance, and wrap it in an array to be consistent with other light entries
						append maxwellLLister.maxwellLightMatPairs #(i.Emitter,mat)
					)
				)
			)
			else if (classof mat) == MultiMaterial then (	--handle lights that are embedded in multi sub materials
				for j in mat.materialList where (classof j) == Maxwell_Material do (
					lyrs = j.Layers
					for i in lyrs do (
						if (i.Emitter != undefined) then (
							i.Emitter.name = mat.name	--change the name of the emitter to the material name so it is available for creating controls
							append sceneMaxwellLights #(i.Emitter)	--append the actual emitter instance, and wrap it in an array to be consistent with other light entries
							append maxwellLLister.maxwellLightMatPairs #(i.Emitter,j)
						)
					)
				)
			)
		)

		sceneMaxwellEnviroLights = true
		renderSceneDialog.close() 	--max won't update the changes to the render scene dialog if it is open.
	)

	-- Collect Light Instances and build array to be displayed

	tmpParser = #( \
		tmpsceneMaxLights = copyArray sceneMaxLights, \
		tmpscenemiLights = copyArray scenemiLights, \
		tmpscenemrSkyLights = copyArray scenemrSkyLights, \
		tmpscenemrSunLights = copyArray scenemrSunLights, \
		tmpscenemrSkyPortalLights = copyArray scenemrSkyPortalLights, \
		tmpsceneLSLights = copyArray sceneLSLights, \
		tmpsceneSkyLights = copyArray sceneSkyLights, \
		tmpsceneSunLights = copyArray sceneSunLights, \
		tmpsceneLuminaires = copyArray sceneLuminaires \
	)

	ListParser = #( \
		maxwellLLister.maxLightsList = #(), \
		maxwellLLister.miLightsList = #(), \
		maxwellLLister.mrSkyLightsList = #(), \
		maxwellLLister.mrSunLightsList = #(), \
		maxwellLLister.mrSkyPortalLightsList = #(), \
		maxwellLLister.LSLightsList = #(), \
		maxwellLLister.SkyLightsList = #(), \
		maxwellLLister.SunLightsList = #(), \
		maxwellLLister.LuminairesList = #() \
	)

	maxwellLLister.maxwellLightsList = copyArray sceneMaxwellLights	--no need to filter the maxwell list, so directly add it here and omit from tmpParser list
	maxwellLLister.maxwellEnviroLights = sceneMaxwellEnviroLights

	for i in 1 to tmpParser.count do
	(
		while tmpParser[i].count > 0 do
		(
			tmpNode = tmpParser[i][1].baseObject
			depends = refs.dependents tmpNode
			discard = #()
			for k in depends do if classof k != classof tmpNode or (superclassof k != light and superclassof k != helper) do append discard k
			for k in depends do
				try
				(
					if classof k == DaylightAssemblyHead or classof k == ParamBlock2ParamBlock2 then
						append discard k
					else
						if k.AssemblyMember and not k.AssemblyHead and classof k.parent != DaylightAssemblyHead do append discard k
				)
				catch()
			depends2 = subtractFromArray depends discard
			depends = SortNodeArrayByName depends2
			if depends.count > 0 do append listParser[i] depends
			tmpParser[i] = subtractFromArray tmpParser[i] (discard + depends)
		)
	)

	mwELights = 0
	if maxwellLLister.maxwellEnviroLights then (mwElights = 5) 	--hard coded since each environment light is listed even if it is unused

	maxwellLLister.totalLightCount = 	maxwellLLister.maxLightsList.count + \
								maxwellLLister.LSLightsList.count + \
								maxwellLLister.SkyLightsList.count + \
								maxwellLLister.SunLightsList.count + \
								maxwellLLister.LuminairesList.count + \
								maxwellLLister.miLightsList.count + \
								maxwellLLister.mrSkyLightsList.count + \
								maxwellLLister.mrSkyPortalLightsList.count + \
								maxwellLLister.mrSunLightsList.count + \
								maxwellLLister.maxwellLightsList.count + \
								mwELights

	--print maxwellLLister.totalLightCount

	-- build controls and rollouts

	-- MAX Lights

	/*
		Rollout Creator Example...

		rci = rolloutCreator "myRollout" "My Rollout"
		rci.begin()
			rci.addControl #button #myButton "My Button" paramStr:"Height:60 width:70"
			rci.addHandler #myButton #pressed filter:on codeStr:"MessageBox @Isn't this cool@ title:@Wow@"
		createDialog (rci.end())
	*/

	maxwellLLister.maxLightsRC = rolloutCreator "maxLightsRollout" "Lights" -- Localize the 2nd string only
	maxwellLLister.maxLightsRC.setSourceDefinitionScriptFilename (getSourceFileName())
	maxwellLLister.maxLightsRC.begin()
  	-- print maxwellLLister.maxLightsRC.str.count

	maxwellLLister.maxLightsRC.addText "fn clearCheckButtons = for i in maxwellLLister.LightInspectorListRollout.controls do if classof i == checkButtonControl do if i.checked do i.checked = false\n"

	maxwellLLister.count = 1
	maxwellLLister.lbCount = 1
	maxwellLLister.LightIndex = #()
	maxwellLLister.UIControlList = #(#(),#())

	fn WriteTitle hasShadow:true hasDecay:false hasSize:false isLuminaire:false isMRSky:false isMRSun:false isMRSkyPortal:false Multip:"Multiplier" isMaxwellLight:false = -- Localize this string
	(
		-- Start Localization

		local lbName
		fn lbName =
		(
			if maxwellLLister.lbCount == undefined do maxwellLLister.lbCount = 1
			maxwellLLister.lbCount += 1
			("LB" + maxwellLLister.lbCount as string) as name
		)

		if isLuminaire == false do maxwellLLister.maxLightsRC.addControl #label (lbname()) "On" paramStr:(" align:#left offset:[8," + (-3 + maxwellLLister.yOffset + maxwellLLister.LineOffset) as string + "]")
		local labeloffset = if isLuminaire == false then -18 else -3
		maxwellLLister.maxLightsRC.addControl #label (lbname()) "Name" paramStr:(" align:#left offset:[28," + (labelOffset + maxwellLLister.yOffset) as string + "]")
		if ProductAppID == #VIZR then
		(
			maxwellLLister.maxLightsRC.addControl #label (lbname()) Multip paramStr:(" align:#left offset:[182,"+ (-18 + maxwellLLister.yOffset) as string + "]")
			maxwellLLister.maxLightsRC.addControl #label (lbname()) "Color" paramStr:(" align:#left offset:[240,"+ (-18 + maxwellLLister.yOffset) as string + "]")
		)
		else if isMaxwellLight == false then
		(
			maxwellLLister.maxLightsRC.addControl #label (lbname()) Multip paramStr:(" align:#left offset:[102,"+ (-18 + maxwellLLister.yOffset) as string + "]")
			if not (isMRSky or isMRSun) do
				maxwellLLister.maxLightsRC.addControl #label (lbname()) "Color" paramStr:(" align:#left offset:[160,"+ (-18+ maxwellLLister.yOffset) as string + "]")
		)

		if hasShadow do
		(
			if ProductAppID == #VIZR then
				maxwellLLister.maxLightsRC.addControl #label (lbname()) "Shadows" paramStr:" align:#left offset:[270,-18]"
			else
			(
				maxwellLLister.maxLightsRC.addControl #label (lbname()) "Shadows" paramStr:(" align:#left offset:[190,"+ (-18 + maxwellLLister.yOffset) as string + "]")
				maxwellLLister.maxLightsRC.addControl #label (lbname()) "Map Size" paramStr:(" align:#left offset:[332,"+ (-18 + maxwellLLister.yOffset) as string + "]")
				maxwellLLister.maxLightsRC.addControl #label (lbname()) "Bias" paramStr:(" align:#left offset:[390,"+ (-18 + maxwellLLister.yOffset) as string + "]")
				maxwellLLister.maxLightsRC.addControl #label (lbname()) "Sm.Range" paramStr:(" align:#left offset:[443,"+ (-18+ maxwellLLister.yOffset) as string + "]")
				maxwellLLister.maxLightsRC.addControl #label (lbname()) "Transp." paramStr:(" align:#left offset:[495,"+ (-18+ maxwellLLister.yOffset) as string + "]")
				maxwellLLister.maxLightsRC.addControl #label (lbname()) "Int." paramStr:(" align:#left offset:[535,"+ (-18 + maxwellLLister.yOffset) as string + "]")
				maxwellLLister.maxLightsRC.addControl #label (lbname()) "Qual." paramStr:(" align:#left offset:[570,"+ (-18 + maxwellLLister.yOffset) as string + "]")
			)
		)
		if hasDecay and ProductAppID != #VIZR do
		(
			maxwellLLister.maxLightsRC.addControl #label (lbname()) "Decay" paramStr:(" align:#left offset:[612,"+ (-18 + maxwellLLister.yOffset) as string + "]")
			maxwellLLister.maxLightsRC.addControl #label (lbname()) "Start" paramStr:(" align:#left offset:[690,"+ (-18+ maxwellLLister.yOffset) as string + "]")
		)
		if hasSize and ProductAppID != #VIZR do
		(
			maxwellLLister.maxLightsRC.addControl #label (lbname()) "Length" paramStr:(" align:#left offset:[612,"+ (-18 + maxwellLLister.yOffset) as string + "]")
			maxwellLLister.maxLightsRC.addControl #label (lbname()) "Width/Radius" paramStr:(" align:#left offset:[671,"+ (-18 + maxwellLLister.yOffset) as string + "]")
		)
		if isMRSky do
		(
				maxwellLLister.maxLightsRC.addControl #label (lbname()) "Haze" paramStr:(" align:#left offset:[161,"+ (-18 + maxwellLLister.yOffset) as string + "]")
				maxwellLLister.maxLightsRC.addControl #label (lbname()) "H Height" paramStr:(" align:#left offset:[218,"+ (-18 + maxwellLLister.yOffset) as string + "]")
				maxwellLLister.maxLightsRC.addControl #label (lbname()) "H Blur" paramStr:(" align:#left offset:[277,"+ (-18 + maxwellLLister.yOffset) as string + "]")
				maxwellLLister.maxLightsRC.addControl #label (lbname()) "Ground" paramStr:(" align:#left offset:[333,"+ (-18+ maxwellLLister.yOffset) as string + "]")
				maxwellLLister.maxLightsRC.addControl #label (lbname()) "Night" paramStr:(" align:#left offset:[382,"+ (-18+ maxwellLLister.yOffset) as string + "]")
				maxwellLLister.maxLightsRC.addControl #label (lbname()) "Redness" paramStr:(" align:#left offset:[420,"+ (-18 + maxwellLLister.yOffset) as string + "]")
				maxwellLLister.maxLightsRC.addControl #label (lbname()) "Saturation" paramStr:(" align:#left offset:[480,"+ (-18 + maxwellLLister.yOffset) as string + "]")
				maxwellLLister.maxLightsRC.addControl #label (lbname()) "UseAerialPersp" paramStr:(" align:#left offset:[540,"+ (-18 + maxwellLLister.yOffset) as string + "]")
				maxwellLLister.maxLightsRC.addControl #label (lbname()) "AerialPersp" paramStr:(" align:#left offset:[620,"+ (-18 + maxwellLLister.yOffset) as string + "]")
		)
		if isMRSun do
		(
				maxwellLLister.maxLightsRC.addControl #label (lbname()) "Shadows" paramStr:(" align:#left offset:[159,"+ (-18 + maxwellLLister.yOffset) as string + "]")
				maxwellLLister.maxLightsRC.addControl #label (lbname()) "Softness" paramStr:(" align:#left offset:[211,"+ (-18 + maxwellLLister.yOffset) as string + "]")
				maxwellLLister.maxLightsRC.addControl #label (lbname()) "Samples" paramStr:(" align:#left offset:[258,"+ (-18 + maxwellLLister.yOffset) as string + "]")
				maxwellLLister.maxLightsRC.addControl #label (lbname()) "Targeted" paramStr:(" align:#left offset:[304,"+ (-18+ maxwellLLister.yOffset) as string + "]")
				maxwellLLister.maxLightsRC.addControl #label (lbname()) "Distance" paramStr:(" align:#left offset:[353,"+ (-18+ maxwellLLister.yOffset) as string + "]")
				maxwellLLister.maxLightsRC.addControl #label (lbname()) "Inherit" paramStr:(" align:#left offset:[426,"+ (-18 + maxwellLLister.yOffset) as string + "]")
				maxwellLLister.maxLightsRC.addControl #label (lbname()) "Haze" paramStr:(" align:#left offset:[463,"+ (-18 + maxwellLLister.yOffset) as string + "]")
				maxwellLLister.maxLightsRC.addControl #label (lbname()) "H Height" paramStr:(" align:#left offset:[513,"+ (-18 + maxwellLLister.yOffset) as string + "]")
				maxwellLLister.maxLightsRC.addControl #label (lbname()) "Redness" paramStr:(" align:#left offset:[561,"+ (-18 + maxwellLLister.yOffset) as string + "]")
				maxwellLLister.maxLightsRC.addControl #label (lbname()) "Saturation" paramStr:(" align:#left offset:[609,"+ (-18 + maxwellLLister.yOffset) as string + "]")
				maxwellLLister.maxLightsRC.addControl #label (lbname()) "Use Targ" paramStr:(" align:#left offset:[663,"+ (-18 + maxwellLLister.yOffset) as string + "]")
				maxwellLLister.maxLightsRC.addControl #label (lbname()) "Radius" paramStr:(" align:#left offset:[712,"+ (-18 + maxwellLLister.yOffset) as string + "]")
		)
		if isMRSkyPortal do
		(
				maxwellLLister.maxLightsRC.addControl #label (lbname()) "Shadows" paramStr:(" align:#left offset:[190,"+ (-18 + maxwellLLister.yOffset) as string + "]")
				maxwellLLister.maxLightsRC.addControl #label (lbname()) "Extend" paramStr:(" align:#left offset:[240,"+ (-18 + maxwellLLister.yOffset) as string + "]")
				maxwellLLister.maxLightsRC.addControl #label (lbname()) "Samples" paramStr:(" align:#left offset:[280,"+ (-18 + maxwellLLister.yOffset) as string + "]")
				maxwellLLister.maxLightsRC.addControl #label (lbname()) "Length" paramStr:(" align:#left offset:[335,"+ (-18+ maxwellLLister.yOffset) as string + "]")
				maxwellLLister.maxLightsRC.addControl #label (lbname()) "Width" paramStr:(" align:#left offset:[408,"+ (-18+ maxwellLLister.yOffset) as string + "]")
				maxwellLLister.maxLightsRC.addControl #label (lbname()) "Flip Flux" paramStr:(" align:#left offset:[478,"+ (-18 + maxwellLLister.yOffset) as string + "]")
				maxwellLLister.maxLightsRC.addControl #label (lbname()) "Visible" paramStr:(" align:#left offset:[525,"+ (-18 + maxwellLLister.yOffset) as string + "]")
				maxwellLLister.maxLightsRC.addControl #label (lbname()) "Transparency" paramStr:(" align:#left offset:[560,"+ (-18 + maxwellLLister.yOffset) as string + "]")
				maxwellLLister.maxLightsRC.addControl #label (lbname()) "Source" paramStr:(" align:#left offset:[640,"+ (-18 + maxwellLLister.yOffset) as string + "]")
		)
		if isMaxwellLight do
		(
			maxwellLLister.maxLightsRC.addControl #label (lbname()) "Light Type" paramStr:(" align:#left offset:[102,"+ (-18 + maxwellLLister.yOffset) as string + "]")
			maxwellLLister.maxLightsRC.addControl #label (lbname()) "Color Type" paramStr:(" align:#left offset:[160,"+ (-18 + maxwellLLister.yOffset) as string + "]")
			maxwellLLister.maxLightsRC.addControl #label (lbname()) "Emission" paramStr:(" align:#left offset:[215,"+ (-30 + maxwellLLister.yOffset) as string + "]")
			maxwellLLister.maxLightsRC.addControl #label (lbname()) "Color" paramStr:(" align:#left offset:[223,"+ (-6 + maxwellLLister.yOffset) as string + "]")
			maxwellLLister.maxLightsRC.addControl #label (lbname()) "Correlated" paramStr:(" align:#left offset:[265,"+ (-30 + maxwellLLister.yOffset) as string + "]")
			maxwellLLister.maxLightsRC.addControl #label (lbname()) "Color" paramStr:(" align:#left offset:[277,"+ (-6 + maxwellLLister.yOffset) as string + "]")
			maxwellLLister.maxLightsRC.addControl #label (lbname()) "Lum. Type" paramStr:(" align:#left offset:[330,"+ (-18 + maxwellLLister.yOffset) as string + "]")
			maxwellLLister.maxLightsRC.addControl #label (lbname()) "Watts" paramStr:(" align:#left offset:[395,"+ (-18 + maxwellLLister.yOffset) as string + "]")
			maxwellLLister.maxLightsRC.addControl #label (lbname()) "Efficacy" paramStr:(" align:#left offset:[445,"+ (-18 + maxwellLLister.yOffset) as string + "]")
			maxwellLLister.maxLightsRC.addControl #label (lbname()) "Luminance" paramStr:(" align:#left offset:[495,"+ (-18 + maxwellLLister.yOffset) as string + "]")
			maxwellLLister.maxLightsRC.addControl #label (lbname()) "IES" paramStr:(" align:#left offset:[625,"+ (-30 + maxwellLLister.yOffset) as string + "]")
			maxwellLLister.maxLightsRC.addControl #label (lbname()) "Intensity" paramStr:(" align:#left offset:[610,"+ (-6 + maxwellLLister.yOffset) as string + "]")
			maxwellLLister.maxLightsRC.addControl #label (lbname()) "Temp." paramStr:(" align:#left offset:[670,"+ (-18 + maxwellLLister.yOffset) as string + "]")
			maxwellLLister.maxLightsRC.addControl #label (lbname()) "MXI / HDR" paramStr:(" align:#left offset:[720,"+ (-30 + maxwellLLister.yOffset) as string + "]")
			maxwellLLister.maxLightsRC.addControl #label (lbname()) "Intensity" paramStr:(" align:#left offset:[723,"+ (-6 + maxwellLLister.yOffset) as string + "]")
		)
		-- End Localization
	)

	fn CreateControls hasShadow:true hasDecay:false hasSize:false Multiplier:#multiplier ColorType:#Color isLuminaire:false isMRSky:false isMRSun:false isMRSkyPortal:false isMaxwellLight:false = -- AB: Jun 20, 2002
	(

		-- Selection Checkbox

		if isMaxwellLight == false then (
			local isLightSelected = false

			for i in maxwellLLister.LightIndex[maxwellLLister.count] where (not isLightSelected) do isLightSelected = i.isSelected

		)

		maxwellLLister.UIControlList[1][maxwellLLister.count] = maxwellLLister.LightIndex[maxwellLLister.count][1]
		maxwellLLister.UIControlList[2][maxwellLLister.Count] = #()	--this needs to execute for all luminaires

		if isMaxwellLight == false then (	--use the checkbutton for traditional lights
			maxwellLLister.maxLightsRC.addControl #checkbutton (("LightSel" + maxwellLLister.count as string) as name) "" \
				paramStr:("checked:" + (isLightSelected as string) + " offset:[-5,"+ (-2+ maxwellLLister.yOffset + maxwellLLister.LineOffset) as string + "] align:#left" +\
						" width:10 height:20 ")
			maxwellLLister.maxLightsRC.addHandler (("LightSel" + maxwellLLister.count as string) as name) #'changed state' filter:on \
				codeStr: \
				(
				"clearCheckButtons();if state then (max modify mode;select maxwellLLister.LightIndex[" + maxwellLLister.count as string + "];LightSel" + (maxwellLLister.count as string) + ".checked = true); else max select none"
				)

			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightSel" + maxwellLLister.count as string) as name)
		)

		else (	--for maxwell lights, use a regular button since it's a little unclear how to elegantly handle the 'selected' state
			maxwellLLister.maxLightsRC.addControl #button (("LightSel" + maxwellLLister.count as string) as name) "" \
				paramStr:(" offset:[-5,"+ (-2+ maxwellLLister.yOffset + maxwellLLister.LineOffset) as string + "] align:#left" +" width:10 height:20 ")
			maxwellLLister.maxLightsRC.addHandler (("LightSel" + maxwellLLister.count as string) as name) #pressed filter:on \
				codeStr: \
				(
				"for i in maxwellLLister.maxwellLightMatPairs do (" + \
				"	if i[1] == maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] then (selset = for j in objects where (j.material == i[2]) collect j;select selSet))"
				)	-- first find out which material this emitter is part of (using previously stored emitter / material pair array) then scan all objects and select those with the right material

			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightSel" + maxwellLLister.count as string) as name)
		)

		-- On/Off

		if isLuminaire == false do
		(
			if isMaxwellLight == false then (
				maxwellLLister.maxLightsRC.addControl #checkbox (("LightOn" + maxwellLLister.count as string) as name) "" \
					paramStr:("checked:" + ((maxwellLLister.GetlightProp maxwellLLister.LightIndex[maxwellLLister.count][1] #on) as string) + " offset:[8,"+ (-22+ maxwellLLister.yOffset) as string + "] width:18")
				maxwellLLister.maxLightsRC.addHandler (("LightOn" + maxwellLLister.count as string) as name) #'changed state' filter:on \
					codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #on state")

				append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightOn" + maxwellLLister.count as string) as name)
			)
			else (
				maxwellLLister.maxLightsRC.addControl #checkbox (("LightOn" + maxwellLLister.count as string) as name) "" \
					paramStr:("checked:" + ((maxwellLLister.GetlightProp maxwellLLister.LightIndex[maxwellLLister.count][1] #enabled) as string) + " offset:[8,"+ (-22+ maxwellLLister.yOffset) as string + "] width:18")
				maxwellLLister.maxLightsRC.addHandler (("LightOn" + maxwellLLister.count as string) as name) #'changed state' filter:on \
					codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #enabled state")

				append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightOn" + maxwellLLister.count as string) as name)
			)

		)

		-- Light Name

		local isUsingEdittextOffset = 0, editTextSize = 75, vizRoffset = 0
		if ProductAppID == #vizR do (editTextSize += 80; vizRoffset += 80)

		if maxwellLLister.LightIndex[maxwellLLister.count].count == 1 then
		(
			local wrappedName = wrapString maxwellLLister.LightIndex[maxwellLLister.count][1].name
			maxwellLLister.maxLightsRC.addControl #edittext (("LightName" + maxwellLLister.count as string) as name) "" \
				paramStr:(" text:" + wrappedName + " width:" + editTextSize as string +  \
				" height:16 offset:[23,"+ (-21+ maxwellLLister.yOffset) as string + "] height:21")
			if isMaxwellLight == false then (	--code for normal light is the same
				maxwellLLister.maxLightsRC.addHandler (("LightName" + maxwellLLister.count as string) as name) #'entered txt' filter:on \
					codeStr:("maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1].name = txt")
			)
			else (
				maxwellLLister.maxLightsRC.addHandler (("LightName" + maxwellLLister.count as string) as name) #'entered txt' filter:on \
				codeStr: \
					(
					"for i in maxwellLLister.maxwellLightMatPairs do (" + \
					"	if i[1] == maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] then (i[2].name = txt))"
					)	-- first find out which material this emitter is part of (using previously stored emitter / material pair array), then change the material's name
			)

			isUsingEdittextOffset = 4
		)
		else	--I think this only executes for Luminaires, but I'm not 100% sure - EM
		(
			theNames = for j in maxwellLLister.LightIndex[maxwellLLister.count] collect j.name
			sort theNames
			namelist = "#("
			for j in 1 to theNames.count do
				(
				local wrappedName = wrapString theNames[j]
				append namelist wrappedName
				if j != theNames.count do append namelist ","
				)
			append namelist ")"
			maxwellLLister.maxLightsRC.addControl #dropDownList (("LightName" + maxwellLLister.count as string) as name) "" filter:on\
				paramStr:(" items:" + NameList + " width:" + ((editTextSize-2) as string) + " offset:[27,"+ (-22+ maxwellLLister.yOffset) as string + "] ")
		)

		append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightName" + maxwellLLister.count as string) as name)

		-- Light Multiplier

		-- AB: Jun 20, 2002
		-- Increased Limits for the spinners from 10,000 to 1,000,000
		if isMaxwellLight == false then (
			if Multiplier == #multiplier or Multiplier == #skymult then
			(
				local lowerLimit = -1000000
				local upperLimit = 1000000
				if isMRSky do
				(
					lowerLimit = 0
					upperLimit = 15
				)
				if isMRSun do
				(
					lowerLimit = 0
					upperLimit = 10
				)
				if isMRSkyPortal do
				(
					lowerLimit = 0
				)

				maxwellLLister.maxLightsRC.addControl #spinner (("LightMult" + maxwellLLister.count as string) as name) "" \
					paramStr:("range:[" + lowerLimit as string + "," + upperLimit as string + "," + \
					(maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1] Multiplier) as string + "] type:#float " + \
					"fieldwidth:45 align:#left offset:[" +  (100 + vizRoffset) as string + \
					"," + (isUsingEdittextOffset-24+maxwellLLister.yOffset) as string + "] enabled:" + \
					((if isProperty maxwellLLister.LightIndex[maxwellLLister.count][1] Multiplier then \
					if maxwellLLister.LightIndex[maxwellLLister.count][1].multiplier.controller != undefined then \
					maxwellLLister.LightIndex[maxwellLLister.count][1].multiplier.controller.keys.count >= 0 else true \
					else try(if isProperty maxwellLLister.LightIndex[maxwellLLister.count][1].delegate Multiplier then \
					if maxwellLLister.LightIndex[maxwellLLister.count][1].delegate.multiplier.controller != undefined then \
					maxwellLLister.LightIndex[maxwellLLister.count][1].delegate.multiplier.controller.keys.count >= 0 else true) catch(true)\
					) as string))
				maxwellLLister.maxLightsRC.addHandler (("LightMult" + maxwellLLister.count as string) as name) #'changed val' filter:on \
					codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #"+ multiplier + " val")
			)
			else if Multiplier == #intensity then
			(
				maxwellLLister.maxLightsRC.addControl #spinner (("LightMult" + maxwellLLister.count as string) as name) "" \
					paramStr:("range:[-1000000,1000000," + (maxwellLLister.LightIndex[maxwellLLister.count][1].intensity as string) + "] type:#float " + \
					"fieldwidth:45 align:#left offset:[" +  (100 + vizRoffset) as string + \
					"," + (isUsingEdittextOffset-24+maxwellLLister.yoffset) as string + "] enabled:" + \
					((if isProperty maxwellLLister.LightIndex[maxwellLLister.count][1] #intensity then \
					if maxwellLLister.LightIndex[maxwellLLister.count][1].intensity.controller != undefined then \
					maxwellLLister.LightIndex[maxwellLLister.count][1].intensity.controller.keys.count >= 0 else true \
					else try(if isProperty maxwellLLister.LightIndex[maxwellLLister.count][1].delegate #intensity then \
					if maxwellLLister.LightIndex[maxwellLLister.count][1].delegate.intensity.controller != undefined then \
					maxwellLLister.LightIndex[maxwellLLister.count][1].delegate.intensity.controller.keys.count >= 0 else true) catch(true)\
					) as string))
				maxwellLLister.maxLightsRC.addHandler (("LightMult" + maxwellLLister.count as string) as name) #'changed val' filter:on \
					codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #intensity val")
			)
			else if Multiplier == #dimmer then
			(
				maxwellLLister.maxLightsRC.addControl #spinner (("LightMult" + maxwellLLister.count as string) as name) "" \
					paramStr:("range:[-1000000,1000000," + (maxwellLLister.LightIndex[maxwellLLister.count][1].dimmer as string) + "] type:#float " + \
					"fieldwidth:45 align:#left offset:[" + (100 + vizRoffset) as string + "," + \
					(isUsingEdittextOffset-24+maxwellLLister.yOffset) as string + "]")
				maxwellLLister.maxLightsRC.addHandler (("LightMult" + maxwellLLister.count as string) as name) #'changed val' filter:on \
					codeStr:("maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1].dimmer = val")
			)

			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightMult" + maxwellLLister.count as string) as name)

			-- Light Color

			-- AB: Jun 20, 2002
			-- Added ColorType parameter to the function, so I can call FilterColor for Photometric Lights

			if ColorType == #Color or ColorType == #FilterColor or ColorType == #rgbFilter then
			(
				maxwellLLister.maxLightsRC.addControl #colorpicker (("LightCol" + maxwellLLister.count as string) as name) "" \
					paramStr:("color:" + (maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1] ColorType) as string + \
					" offset:[" + (158 + vizRoffset) as string + ","+ (-23+ maxwellLLister.yOffset) as string + "] width:25")
				maxwellLLister.maxLightsRC.addHandler (("LightCol" + maxwellLLister.count as string) as name) #'changed val' filter:on \
					codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #" + ColorType as string + " val")
				append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightCol" + maxwellLLister.count as string) as name)
			)
		)

		if hasShadow do
		(

			-- Shadow On/Off

			maxwellLLister.maxLightsRC.addControl #checkbox (("LightShdOn" + maxwellLLister.count as string) as name) "" \
				paramStr:("checked:" + (maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1].baseObject #castshadows as string)+ \
				" offset:[" + (190 + vizRoffset) as string + ","+ (-22+ maxwellLLister.yOffset) as string + "] width:15")
			maxwellLLister.maxLightsRC.addHandler (("LightShdOn" + maxwellLLister.count as string) as name) #'changed state' filter:on \
				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1].baseobject #castshadows state")

			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightShdOn" + maxwellLLister.count as string) as name)

			-- Shadow Plugin

			if ProductAppID != #VIZR do
			(

			local LLshadowClass = maxwellLLister.fnShadowClass maxwellLLister.LightIndex[maxwellLLister.count][1]
			local LLshadowGen = (maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1] #shadowGenerator)


			maxwellLLister.maxLightsRC.addControl #dropDownList (("LightShd" + maxwellLLister.count as string) as name) "" filter:on\
				paramStr:(" items:" + maxwellLLister.ShadowPluginsName as string + " width:110 offset:[210,"+ (-24+ maxwellLLister.yOffset) as string + "]" + \
				"selection:(finditem maxwellLLister.ShadowPlugins (maxwellLLister.fnShadowClass maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1]))")

			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightShd" + maxwellLLister.count as string) as name)

			-- Light Map Size

			local mapSizeTmp = 512

			if LLshadowClass == shadowMap do
				mapSizeTmp = LLshadowGen.mapSize

			maxwellLLister.maxLightsRC.addControl #spinner (("LightMapSiz" + maxwellLLister.count as string) as name) "" \
				paramStr:("range:[0,10000," + (mapSizeTmp as string) + "] type:#integer " + \
				"fieldwidth:45 align:#left offset:[330,"+ (-24+ maxwellLLister.yOffset) as string + "] enabled:" \
				+ (LLshadowClass == shadowMap or LLShadowClass == mental_ray_shadow_map) as string)
			maxwellLLister.maxLightsRC.addHandler (("LightMapSiz" + maxwellLLister.count as string) as name) #'changed val' filter:on \
				codeStr:("maxwellLLister.setShdProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #mapSize val")

			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightMapSiz" + maxwellLLister.count as string) as name)

			-- Light Bias

			local BiasTmp = \
				case LLshadowClass of
				(
					shadowMap:			LLShadowGen.mapBias
					raytraceShadow:		LLShadowGen.raytraceBias
					Area_Shadows:		LLShadowGen.ray_Bias
					Adv__Ray_Traced:	LLShadowGen.ray_Bias
					Blur_Adv__Ray_Traced:	LLShadowGen.ray_Bias
					default:			1.0
				)

			maxwellLLister.maxLightsRC.addControl #spinner (("LightBias" + maxwellLLister.count as string) as name) "" \
				paramStr:("range:[0,10000," + (BiasTmp as string) + "] type:#float " + \
				"fieldwidth:45 align:#left offset:[388,"+ (-21+ maxwellLLister.yOffset) as string + "] enabled:" \
				+ (LLShadowClass == shadowMap or LLShadowClass == raytraceShadow or LLShadowClass == Blur_Adv__Ray_Traced or\
				LLShadowClass == Area_Shadows or LLShadowClass == Adv__Ray_Traced) as string)
			maxwellLLister.maxLightsRC.addHandler (("LightBias" + maxwellLLister.count as string) as name) #'changed val' filter:on \
				codeStr: \
				(
				"local propname = case (maxwellLLister.fnShadowClass maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1]) of\n" + \
				"(shadowMap:#mapbias; raytraceShadow:#raytraceBias; Area_Shadows:#ray_bias; Adv__Ray_Traced:#ray_bias; Blur_Adv__Ray_Traced:#ray_bias;default:0)\n" + \
				"if propname != 0 do maxwellLLister.SetShdProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] propName val"
				)

			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightBias" + maxwellLLister.count as string) as name)

			-- Light Sample Range

			local smpRangeTmp = 4.0
			local smpRangeStr = "#samplerange"   --fix the mr shadow sample problem here.
			if LLShadowClass == shadowMap  then	smpRangeTmp = LLShadowGen.samplerange
			else if LLShadowClass == mental_ray_Shadow_Map do (
				smpRangeTmp = LLShadowGen.Sample_Range
				smpRangeStr = "#Sample_Range"
			)

			maxwellLLister.maxLightsRC.addControl #spinner (("LightSmpRange" + maxwellLLister.count as string) as name) "" \
				paramStr:("range:[0,50," + (smpRangeTmp as string) + "] type:#float " + \
				"fieldwidth:45 align:#left offset:[446,"+ (-21+ maxwellLLister.yOffset) as string + "] enabled:" + (LLShadowClass == shadowMap or LLShadowClass == mental_ray_shadow_map) as string)
			maxwellLLister.maxLightsRC.addHandler (("LightSmpRange" + maxwellLLister.count as string) as name) #'changed val' filter:on \
				codeStr:("maxwellLLister.SetShdProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] "+smpRangeStr+" val")

			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightSmpRange" + maxwellLLister.count as string) as name)

			-- Transparency On/Off

			maxwellLLister.maxLightsRC.addControl #checkbox (("LightTrans" + maxwellLLister.count as string) as name) "" \
				paramStr:("checked:" + \
						((if LLShadowClass == Area_Shadows or LLShadowClass == Adv__Ray_Traced or LLShadowClass == Blur_Adv__Ray_Traced then \
						LLShadowGen.shadow_Transparent else false) as string) + \
						" offset:[508,"+ (-20+ maxwellLLister.yOffset) as string + "] width:15 enabled:" + \
						((LLShadowClass == Area_Shadows or LLShadowClass == Adv__Ray_Traced or LLShadowClass == Blur_Adv__Ray_Traced) as string))
			maxwellLLister.maxLightsRC.addHandler (("LightTrans" + maxwellLLister.count as string) as name) #'changed state' filter:on \
				codeStr:("maxwellLLister.setShdProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #shadow_Transparent state")

			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightTrans" + maxwellLLister.count as string) as name)

			-- Integrity

			maxwellLLister.maxLightsRC.addControl #spinner (("LightInteg" + maxwellLLister.count as string) as name) "" \
				paramStr:("type:#integer fieldwidth:30 align:#left range:[1,15," + \
						((if LLShadowClass == Area_Shadows or LLShadowClass == Blur_Adv__Ray_Traced or\
						LLShadowClass == Adv__Ray_Traced then \
						LLShadowGen.pass1 else 1) as string) + \
						"] offset:[521,"+ (-21+ maxwellLLister.yOffset) as string + "] width:15 enabled:" + \
						((LLShadowClass == Area_Shadows or LLShadowClass == Blur_Adv__Ray_Traced or\
						LLShadowClass == Adv__Ray_Traced) as string))
			maxwellLLister.maxLightsRC.addHandler (("LightInteg" + maxwellLLister.count as string) as name) #'changed val' filter:on \
				codeStr:("maxwellLLister.setShdProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #pass1 val")

			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightInteg" + maxwellLLister.count as string) as name)

			-- Quality

			maxwellLLister.maxLightsRC.addControl #spinner (("LightQual" + maxwellLLister.count as string) as name) "" \
				paramStr:("type:#integer fieldwidth:30 align:#left range:[1,15," + \
						((if LLShadowClass == Area_Shadows or LLShadowClass == Blur_Adv__Ray_Traced or \
						LLShadowClass == Adv__Ray_Traced then \
						LLShadowGen.pass2 else 2) as string) + \
						"] offset:[565,"+ (-21+ maxwellLLister.yOffset) as string + "] width:15 enabled:" + \
						((LLShadowClass == Area_Shadows or LLShadowClass == Blur_Adv__Ray_Traced or \
						LLShadowClass == Adv__Ray_Traced) as string))
			maxwellLLister.maxLightsRC.addHandler (("LightQual" + maxwellLLister.count as string) as name) #'changed val' filter:on \
				codeStr:("maxwellLLister.setShdProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #pass2 val")

			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightQual" + maxwellLLister.count as string) as name)

			-- Shadow Plugin dropdown handler

			maxwellLLister.maxLightsRC.addHandler (("LightShd" + maxwellLLister.count as string) as name) #'selected i' filter:on \
				codeStr:(\
					"maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #shadowGenerator (maxwellLLister.ShadowPlugins[i]());" + \
					"local shdClass = maxwellLLister.fnShadowClass maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1]\n" + \
					"LightMapSiz" + maxwellLLister.count as string + ".enabled = LightSmpRange" + maxwellLLister.count as string + ".enabled = (shdClass == shadowMap or shdClass == mental_ray_shadow_map)\n" + \
					"LightTrans" + maxwellLLister.count as string + ".enabled = LightInteg" + maxwellLLister.count as string + ".enabled = LightQual" + maxwellLLister.count as string + ".enabled = " + \
					"shdClass == Adv__Ray_Traced or shdClass == Blur_Adv__Ray_Traced or shdClass == Area_Shadows\n" + \
					"LightBias" + maxwellLLister.count as string + ".enabled = (shdClass == Area_Shadows or shdClass == shadowMap or " + \
					"shdClass == Blur_Adv__Ray_Traced or shdClass == raytraceShadow or shdClass ==  Adv__Ray_Traced)\n" + \
					"if (val = maxwellLLister.getShdProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #mapSize) != undefined do LightMapSiz" + \
						maxwellLLister.count as string + ".value = val\n" + \
					"if (val = maxwellLLister.getShdProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #sampleRange) != undefined do LightSmpRange" + \
						maxwellLLister.count as string + ".value = val\n" + \
					"if (val = maxwellLLister.getShdProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #pass1) != undefined do LightInteg" + \
						maxwellLLister.count as string + ".value = val\n" + \
					"if (val = maxwellLLister.getShdProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #pass2) != undefined do LightQual" + \
						maxwellLLister.count as string + ".value = val\n" + \
					"if (val = maxwellLLister.getShdProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #mapBias) != undefined do LightBias" + \
						maxwellLLister.count as string + ".value = val\n" + \
					"if (val = maxwellLLister.getShdProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #ray_Bias) != undefined do LightBias" + \
						maxwellLLister.count as string + ".value = val\n" + \
					"if (val = maxwellLLister.getShdProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #raytraceBias) != undefined do LightBias" + \
						maxwellLLister.count as string + ".value = val\n" + \
					"if (val = maxwellLLister.getShdProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #shadow_Transparent) != undefined do LightTrans" + \
						maxwellLLister.count as string + ".checked = val\n" + \
					"maxwellLLister.enableRefreshBtn maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1]"
					)
			) -- end VIZR
		) -- end has Shadow


		if hasDecay and ProductAppID != #VIZR do
		(

			-- Decay selection

			maxwellLLister.maxLightsRC.addControl #dropDownList (("LightDecay" + maxwellLLister.count as string) as name) "" filter:on\
				paramStr:(" items:" + maxwellLLister.decayStrings as string + " width:80 offset:[612,"+ (-24+ maxwellLLister.yOffset) as string + "]" + \
				"selection:(maxwellLLister.getLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #attenDecay)")
			maxwellLLister.maxLightsRC.addHandler (("LightDecay" + maxwellLLister.count as string) as name) #'selected i' filter:on \
				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #attenDecay i")

			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightDecay" + maxwellLLister.count as string) as name)


			-- Decay Start

			maxwellLLister.maxLightsRC.addControl #spinner (("LightDecStart" + maxwellLLister.count as string) as name) "" \
				paramStr:("range:[0,10000," + ((maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1] #decayRadius) as string) + "] type:#worldunits " + \
				"fieldwidth:45 align:#left offset:[690,"+ (-24+ maxwellLLister.yOffset) as string + "]")
			maxwellLLister.maxLightsRC.addHandler (("LightDecStart" + maxwellLLister.count as string) as name) #'changed val' filter:on \
				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #decayRadius val")

			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightDecStart" + maxwellLLister.count as string) as name)
		) -- end hasDecay

		if hasSize and ProductAppID != #VIZR do
		(
				-- Light Length
				local lightType = maxwellLLister.LightIndex[maxwellLLister.count][1].type
				local hasLength = lightType == #Free_Line or lightType == #Target_Line or
										lightType == #Free_Rectangle or lightType == #Target_Rectangle or
										lightType == #Free_Cylinder or lightType == #Target_Cylinder
				maxwellLLister.maxLightsRC.addControl #spinner (("LSLightLength" + maxwellLLister.count as string) as name) "" \
					paramStr:("range:[0,100000," + (maxwellLLister.LightIndex[maxwellLLister.count][1].light_length as string) + "] type:#worldunits " + \
					"fieldwidth:45 align:#left offset:[610,"+ (-21+ maxwellLLister.yOffset) as string + "] enabled:" \
					+ (hasLength as string))
				maxwellLLister.maxLightsRC.addHandler (("LSLightLength" + maxwellLLister.count as string) as name) #'changed val' filter:on \
					codeStr:("maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1].length = val")

				append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LSLightLength" + maxwellLLister.count as string) as name)

				-- Light Width / Radius

				local hasWidth = lightType == #Free_Rectangle or lightType == #Target_Rectangle
				local hasRadius = lightType == #Free_Cylinder or lightType == #Target_Cylinder or
										lightType == #Free_Disc or lightType == #Target_Disc or
										lightType == #Free_Sphere or lightType == #Target_Sphere
				if hasWidth then
				(
					maxwellLLister.maxLightsRC.addControl #spinner (("LSLightWidth" + maxwellLLister.count as string) as name) "" \
						paramStr:("range:[0,100000," + (maxwellLLister.LightIndex[maxwellLLister.count][1].light_Width as string) + "] type:#worldunits " + \
						"fieldwidth:45 align:#left offset:[669,"+ (-21+ maxwellLLister.yOffset) as string + "] enabled:" \
						+ (hasWidth as string))
					maxwellLLister.maxLightsRC.addHandler (("LSLightWidth" + maxwellLLister.count as string) as name) #'changed val' filter:on \
						codeStr:("maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1].light_Width = val")
				)
				else
				(
					maxwellLLister.maxLightsRC.addControl #spinner (("LSLightWidth" + maxwellLLister.count as string) as name) "" \
						paramStr:("range:[0,100000," + (maxwellLLister.LightIndex[maxwellLLister.count][1].light_Radius as string) + "] type:#worldunits " + \
						"fieldwidth:45 align:#left offset:[669,"+ (-21+ maxwellLLister.yOffset) as string + "] enabled:" \
						+ (hasRadius as string))
					maxwellLLister.maxLightsRC.addHandler (("LSLightWidth" + maxwellLLister.count as string) as name) #'changed val' filter:on \
						codeStr:("maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1].light_Radius = val")
				)

				append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LSLightWidth" + maxwellLLister.count as string) as name)

		)

		if isMRSky do
		(
			-- Haze
			maxwellLLister.maxLightsRC.addControl #spinner (("LightHaze" + maxwellLLister.count as string) as name) "" \
				paramStr:("range:[0,15," + ((maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1] #haze) as string) + "] type:#float " + \
				"fieldwidth:45 align:#left offset:[158,"+ (-21+ maxwellLLister.yOffset) as string + "]")
			maxwellLLister.maxLightsRC.addHandler (("LightHaze" + maxwellLLister.count as string) as name) #'changed val' filter:on \
				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #haze val")
			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightHaze" + maxwellLLister.count as string) as name)

			-- HorizonHeight
			maxwellLLister.maxLightsRC.addControl #spinner (("LightHHeight" + maxwellLLister.count as string) as name) "" \
				paramStr:("range:[-10,10," + ((maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1] #HorizonHeight) as string) + "] type:#float " + \
				"fieldwidth:45 align:#left offset:[216,"+ (-21+ maxwellLLister.yOffset) as string + "]")
			maxwellLLister.maxLightsRC.addHandler (("LightHHeight" + maxwellLLister.count as string) as name) #'changed val' filter:on \
				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #HorizonHeight val")
			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightHHeight" + maxwellLLister.count as string) as name)

			-- HorizonBlur
			maxwellLLister.maxLightsRC.addControl #spinner (("LightHBlur" + maxwellLLister.count as string) as name) "" \
				paramStr:("range:[0,10," + ((maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1] #HorizonBlur) as string) + "] type:#float " + \
				"fieldwidth:45 align:#left offset:[274,"+ (-21+ maxwellLLister.yOffset) as string + "]")
			maxwellLLister.maxLightsRC.addHandler (("LightHBlur" + maxwellLLister.count as string) as name) #'changed val' filter:on \
				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #HorizonBlur val")
			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightHBlur" + maxwellLLister.count as string) as name)

			-- GroundColor
			maxwellLLister.maxLightsRC.addControl #colorpicker (("LightGroundCol" + maxwellLLister.count as string) as name) "" \
				paramStr:("color:" + (maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1] #GroundColor) as string + \
				" offset:[" + (335 + vizRoffset) as string + ","+ (-23+ maxwellLLister.yOffset) as string + "] width:25")
			maxwellLLister.maxLightsRC.addHandler (("LightGroundCol" + maxwellLLister.count as string) as name) #'changed val' filter:on \
				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #GroundColor val")
			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightGroundCol" + maxwellLLister.count as string) as name)

			-- NightColor
			maxwellLLister.maxLightsRC.addControl #colorpicker (("LightNightCol" + maxwellLLister.count as string) as name) "" \
				paramStr:("color:" + (maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1] #NightColor) as string + \
				" offset:[" + (380 + vizRoffset) as string + ","+ (-25+ maxwellLLister.yOffset) as string + "] width:25")
			maxwellLLister.maxLightsRC.addHandler (("LightNightCol" + maxwellLLister.count as string) as name) #'changed val' filter:on \
				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #NightColor val")
			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightNightCol" + maxwellLLister.count as string) as name)

			-- Redness
			maxwellLLister.maxLightsRC.addControl #spinner (("LightRedness" + maxwellLLister.count as string) as name) "" \
				paramStr:("range:[-1,1," + ((maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1] #Redness) as string) + "] type:#float " + \
				"fieldwidth:45 align:#left offset:[419,"+ (-23+ maxwellLLister.yOffset) as string + "]")
			maxwellLLister.maxLightsRC.addHandler (("LightRedness" + maxwellLLister.count as string) as name) #'changed val' filter:on \
				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #Redness val")
			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightRedness" + maxwellLLister.count as string) as name)

			-- Saturation
			maxwellLLister.maxLightsRC.addControl #spinner (("LightSaturation" + maxwellLLister.count as string) as name) "" \
				paramStr:("range:[0,2," + ((maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1] #Saturation) as string) + "] type:#float " + \
				"fieldwidth:45 align:#left offset:[477,"+ (-21+ maxwellLLister.yOffset) as string + "]")
			maxwellLLister.maxLightsRC.addHandler (("LightSaturation" + maxwellLLister.count as string) as name) #'changed val' filter:on \
				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #Saturation val")
			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightSaturation" + maxwellLLister.count as string) as name)

			-- UseAerialPerspective
			maxwellLLister.maxLightsRC.addControl #checkbox (("LightUseAerPersp" + maxwellLLister.count as string) as name) "" \
				paramStr:("checked:" + (maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1] #UseAerialPerspective as string)+ \
				" offset:[" + (570 + vizRoffset) as string + ","+ (-21+ maxwellLLister.yOffset) as string + "] width:15")
			maxwellLLister.maxLightsRC.addHandler (("LightUseAerPersp" + maxwellLLister.count as string) as name) #'changed state' filter:on \
				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #UseAerialPerspective state")
			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightUseAerPersp" + maxwellLLister.count as string) as name)

			-- AerialPerspective
			maxwellLLister.maxLightsRC.addControl #spinner (("LightAerialPersp" + maxwellLLister.count as string) as name) "" \
				paramStr:("range:[0,1e8," + ((maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1] #AerialPerspective) as string) + "] type:#worldunits " + \
				"fieldwidth:60 align:#left offset:[618,"+ (-21+ maxwellLLister.yOffset) as string + "]")
			maxwellLLister.maxLightsRC.addHandler (("LightAerialPersp" + maxwellLLister.count as string) as name) #'changed val' filter:on \
				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #AerialPerspective val")
			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightAerialPersp" + maxwellLLister.count as string) as name)
		)

		if isMRSun do
		(
			-- Shadow On/Off
			maxwellLLister.maxLightsRC.addControl #checkbox (("LightShdOn" + maxwellLLister.count as string) as name) "" \
				paramStr:("checked:" + (maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1].baseObject #castshadows as string)+ \
				" offset:[" + (175 + vizRoffset) as string + ","+ (-22+ maxwellLLister.yOffset) as string + "] width:15")
			maxwellLLister.maxLightsRC.addHandler (("LightShdOn" + maxwellLLister.count as string) as name) #'changed state' filter:on \
				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1].baseobject #castshadows state")
			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightShdOn" + maxwellLLister.count as string) as name)

			-- shadowSoftness
			maxwellLLister.maxLightsRC.addControl #spinner (("LightShdSoft" + maxwellLLister.count as string) as name) "" \
				paramStr:("range:[0,50," + ((maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1] #shadowSoftness) as string) + "] type:#float " + \
				"fieldwidth:35 align:#left offset:[210,"+ (-20+ maxwellLLister.yOffset) as string + "]")
			maxwellLLister.maxLightsRC.addHandler (("LightShdSoft" + maxwellLLister.count as string) as name) #'changed val' filter:on \
				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #shadowSoftness val")
			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightShdSoft" + maxwellLLister.count as string) as name)

			-- shadowSamples
			maxwellLLister.maxLightsRC.addControl #spinner (("LightShdSamples" + maxwellLLister.count as string) as name) "" \
				paramStr:("range:[0,1000," + ((maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1] #shadowSamples) as string) + "] type:#integer " + \
				"fieldwidth:35 align:#left offset:[259,"+ (-20+ maxwellLLister.yOffset) as string + "]")
			maxwellLLister.maxLightsRC.addHandler (("LightShdSamples" + maxwellLLister.count as string) as name) #'changed val' filter:on \
				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #shadowSamples val")
			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightShdSamples" + maxwellLLister.count as string) as name)

			-- hasTarget
			maxwellLLister.maxLightsRC.addControl #checkbox (("LightHasTarg" + maxwellLLister.count as string) as name) "" \
				paramStr:("checked:" + (maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1] #hasTarget as string)+ \
				" offset:[" + (320 + vizRoffset) as string + ","+ (-21+ maxwellLLister.yOffset) as string + "] width:15")
			maxwellLLister.maxLightsRC.addHandler (("LightHasTarg" + maxwellLLister.count as string) as name) #'changed state' filter:on \
				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #hasTarget state")
			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightHasTarg" + maxwellLLister.count as string) as name)

			-- targetDistance
			maxwellLLister.maxLightsRC.addControl #spinner (("LightTargDist" + maxwellLLister.count as string) as name) "" \
				paramStr:("range:[0,1e8," + ((maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1].baseobject #targetDistance) as string) + "] type:#worldunits " + \
				"fieldwidth:60 align:#left offset:[352,"+ (-20+ maxwellLLister.yOffset) as string + "]")
			maxwellLLister.maxLightsRC.addHandler (("LightTargDist" + maxwellLLister.count as string) as name) #'changed val' filter:on \
				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1].baseobject #targetDistance val")
			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightTargDist" + maxwellLLister.count as string) as name)

			-- inherit
			maxwellLLister.maxLightsRC.addControl #checkbox (("LightInherit" + maxwellLLister.count as string) as name) "" \
				paramStr:("checked:" + (maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1] #inherit as string)+ \
				" offset:[" + (435 + vizRoffset) as string + ","+ (-21+ maxwellLLister.yOffset) as string + "] width:15")
			maxwellLLister.maxLightsRC.addHandler (("LightInherit" + maxwellLLister.count as string) as name) #'changed state' filter:on \
				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #inherit state")
			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightInherit" + maxwellLLister.count as string) as name)

			-- haze
			maxwellLLister.maxLightsRC.addControl #spinner (("LightHaze" + maxwellLLister.count as string) as name) "" \
				paramStr:("range:[0,15," + ((maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1] #haze) as string) + "] type:#float " + \
				"fieldwidth:35 align:#left offset:[463,"+ (-20+ maxwellLLister.yOffset) as string + "]")
			maxwellLLister.maxLightsRC.addHandler (("LightHaze" + maxwellLLister.count as string) as name) #'changed val' filter:on \
				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #haze val")
			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightHaze" + maxwellLLister.count as string) as name)

			-- horizonheight
			maxwellLLister.maxLightsRC.addControl #spinner (("LightHHeight" + maxwellLLister.count as string) as name) "" \
				paramStr:("range:[-10,10," + ((maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1] #horizonheight) as string) + "] type:#float " + \
				"fieldwidth:35 align:#left offset:[513,"+ (-21+ maxwellLLister.yOffset) as string + "]")
			maxwellLLister.maxLightsRC.addHandler (("LightHHeight" + maxwellLLister.count as string) as name) #'changed val' filter:on \
				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #horizonheight val")
			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightHHeight" + maxwellLLister.count as string) as name)

			-- redblueshift
			maxwellLLister.maxLightsRC.addControl #spinner (("LightRedness" + maxwellLLister.count as string) as name) "" \
				paramStr:("range:[-1,1," + ((maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1] #redblueshift) as string) + "] type:#float " + \
				"fieldwidth:35 align:#left offset:[563,"+ (-21+ maxwellLLister.yOffset) as string + "]")
			maxwellLLister.maxLightsRC.addHandler (("LightRedness" + maxwellLLister.count as string) as name) #'changed val' filter:on \
				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #redblueshift val")
			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightRedness" + maxwellLLister.count as string) as name)

			-- saturation
			maxwellLLister.maxLightsRC.addControl #spinner (("LightSaturation" + maxwellLLister.count as string) as name) "" \
				paramStr:("range:[0,2," + ((maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1] #saturation) as string) + "] type:#float " + \
				"fieldwidth:35 align:#left offset:[613,"+ (-21+ maxwellLLister.yOffset) as string + "]")
			maxwellLLister.maxLightsRC.addHandler (("LightSaturation" + maxwellLLister.count as string) as name) #'changed val' filter:on \
				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #saturation val")
			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightSaturation" + maxwellLLister.count as string) as name)

			-- usephotontarget
			maxwellLLister.maxLightsRC.addControl #checkbox (("LightUsePTarg" + maxwellLLister.count as string) as name) "" \
				paramStr:("checked:" + (maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1] #usephotontarget as string)+ \
				" offset:[" + (678 + vizRoffset) as string + ","+ (-21+ maxwellLLister.yOffset) as string + "] width:15")
			maxwellLLister.maxLightsRC.addHandler (("LightUsePTarg" + maxwellLLister.count as string) as name) #'changed state' filter:on \
				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #usephotontarget state")
			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightUsePTarg" + maxwellLLister.count as string) as name)

			-- photontarget
			maxwellLLister.maxLightsRC.addControl #spinner (("LightPhotonTarg" + maxwellLLister.count as string) as name) "" \
				paramStr:("range:[0,1e8," + ((maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1] #photontarget) as string) + "] type:#worldunits " + \
				"fieldwidth:60 align:#left offset:[700,"+ (-21+ maxwellLLister.yOffset) as string + "]")
			maxwellLLister.maxLightsRC.addHandler (("LightPhotonTarg" + maxwellLLister.count as string) as name) #'changed val' filter:on \
				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #photontarget val")
			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightPhotonTarg" + maxwellLLister.count as string) as name)
		)

		if isMRSkyPortal do
		(
			-- Shadow On/Off
			maxwellLLister.maxLightsRC.addControl #checkbox (("LightShdOn" + maxwellLLister.count as string) as name) "" \
				paramStr:("checked:" + (maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1].baseObject #castshadows as string)+ \
				" offset:[" + (210 + vizRoffset) as string + ","+ (-22+ maxwellLLister.yOffset) as string + "] width:15")
			maxwellLLister.maxLightsRC.addHandler (("LightShdOn" + maxwellLLister.count as string) as name) #'changed state' filter:on \
				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1].baseobject #castshadows state")
			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightShdOn" + maxwellLLister.count as string) as name)

			-- extend_shadows
			maxwellLLister.maxLightsRC.addControl #checkbox (("LightExtShad" + maxwellLLister.count as string) as name) "" \
				paramStr:("checked:" + (maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1] #extend_shadows as string)+ \
				" offset:[" + (250 + vizRoffset) as string + ","+ (-21+ maxwellLLister.yOffset) as string + "] width:15")
			maxwellLLister.maxLightsRC.addHandler (("LightExtShad" + maxwellLLister.count as string) as name) #'changed state' filter:on \
				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #extend_shadows state")
			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightExtShad" + maxwellLLister.count as string) as name)

			-- shadowSamples
			maxwellLLister.maxLightsRC.addControl #dropDownList (("LightShdSamples" + maxwellLLister.count as string) as name) "" filter:on\
				paramStr:(" items:" + maxwellLLister.MRSkyPortal_ShadowSamples as string + " width:52 offset:[278,"+ (-23+ maxwellLLister.yOffset) as string + "]" + \
				"selection:" + (((maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1] #shadowSamples) +1) as string))
			maxwellLLister.maxLightsRC.addHandler (("LightShdSamples" + maxwellLLister.count as string) as name) #'selected i' filter:on \
				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #shadowSamples (i-1)")
			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightShdSamples" + maxwellLLister.count as string) as name)

			-- length
			maxwellLLister.maxLightsRC.addControl #spinner (("LightLength" + maxwellLLister.count as string) as name) "" \
				paramStr:("range:[0,1e8," + ((maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1] #length) as string) + "] type:#worldunits " + \
				"fieldwidth:60 align:#left offset:[331,"+ (-24+ maxwellLLister.yOffset) as string + "]")
			maxwellLLister.maxLightsRC.addHandler (("LightLength" + maxwellLLister.count as string) as name) #'changed val' filter:on \
				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #length val")
			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightLength" + maxwellLLister.count as string) as name)

			-- light_width
			maxwellLLister.maxLightsRC.addControl #spinner (("LightWidth" + maxwellLLister.count as string) as name) "" \
				paramStr:("range:[0,1e8," + ((maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1] #light_width) as string) + "] type:#worldunits " + \
				"fieldwidth:60 align:#left offset:[406,"+ (-21+ maxwellLLister.yOffset) as string + "]")
			maxwellLLister.maxLightsRC.addHandler (("LightWidth" + maxwellLLister.count as string) as name) #'changed val' filter:on \
				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #light_width val")
			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightWidth" + maxwellLLister.count as string) as name)

				-- reversed
			maxwellLLister.maxLightsRC.addControl #checkbox (("LightFlipFlux" + maxwellLLister.count as string) as name) "" \
				paramStr:("checked:" + (maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1] #reversed as string)+ \
				" offset:[" + (490 + vizRoffset) as string + ","+ (-21+ maxwellLLister.yOffset) as string + "] width:15")
			maxwellLLister.maxLightsRC.addHandler (("LightFlipFlux" + maxwellLLister.count as string) as name) #'changed state' filter:on \
				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #reversed state")
			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightFlipFlux" + maxwellLLister.count as string) as name)

				-- Area_Visible
			maxwellLLister.maxLightsRC.addControl #checkbox (("LightAreaVisible" + maxwellLLister.count as string) as name) "" \
				paramStr:("checked:" + (maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1] #Area_Visible as string)+ \
				" offset:[" + (535 + vizRoffset) as string + ","+ (-21+ maxwellLLister.yOffset) as string + "] width:15")
			maxwellLLister.maxLightsRC.addHandler (("LightAreaVisible" + maxwellLLister.count as string) as name) #'changed state' filter:on \
				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #Area_Visible state")
			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightAreaVisible" + maxwellLLister.count as string) as name)

			-- transparency
			maxwellLLister.maxLightsRC.addControl #colorpicker (("LightTransparency" + maxwellLLister.count as string) as name) "" \
				paramStr:("color:" + (maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1] #transparency) as string + \
				" offset:[" + (580 + vizRoffset) as string + ","+ (-23+ maxwellLLister.yOffset) as string + "] width:25")
			maxwellLLister.maxLightsRC.addHandler (("LightTransparency" + maxwellLLister.count as string) as name) #'changed val' filter:on \
				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #transparency val")
			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightTransparency" + maxwellLLister.count as string) as name)

			-- mode
			maxwellLLister.maxLightsRC.addControl #dropDownList (("LightSourceMode" + maxwellLLister.count as string) as name) "" filter:on\
				paramStr:(" items:" + maxwellLLister.MRSkyPortal_Modes as string + " width:70 offset:[640,"+ (-24+ maxwellLLister.yOffset) as string + "]" + \
				"selection:" + (((mod ((maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1] #mode) + 1) 3) +1 ) as string))
			maxwellLLister.maxLightsRC.addHandler (("LightSourceMode" + maxwellLLister.count as string) as name) #'selected i' filter:on \
				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #mode (mod (i+1) 3)")
			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightSourceMode" + maxwellLLister.count as string) as name)
		)

		if isMaxwellLight do (
			-- light type
			maxwellLLister.maxLightsRC.addControl #dropDownList (("LightType" + maxwellLLister.count as string) as name) "" \
				paramStr:("items:" + maxwellLLister.maxwellLightTypeStrings as string + " width:50" + \
				" offset:[" + (100 + vizRoffset) as string + ","+ (-22+ maxwellLLister.yOffset) as string + "]" + \
					"selection:" + (((maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1] #Type) + 1) as string))

			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightType" + maxwellLLister.count as string) as name)

			-- color type
			maxwellLLister.maxLightsRC.addControl #dropDownList (("ColorType" + maxwellLLister.count as string) as name) "" \
				paramStr:("items:" + maxwellLLister.maxwellColorStrings as string + " width:50" + \
							" offset:[" + (160 + vizRoffset) as string + ","+ (-27+ maxwellLLister.yOffset) as string + "]" + \
							" selection:" + (((maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1] #ColorType) + 1) as string) + \
							" enabled:(("+ ((("LightType" + maxwellLLister.count as string) as name)) + ".selection==1))")
			maxwellLLister.maxLightsRC.addHandler (("ColorType" + maxwellLLister.count as string) as name) #'selected i' filter:on \
				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #ColorType (i-1)")
			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("ColorType" + maxwellLLister.count as string) as name)

			--emission color
			maxwellLLister.maxLightsRC.addControl #colorpicker (("EmissionColor" + maxwellLLister.count as string) as name) "" \
				paramStr:("color:" + (maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1] #RGB) as string + \
							" offset:[" + (220 + vizRoffset) as string + ","+ (-27+ maxwellLLister.yOffset) as string + "] width:25" + \
							" enabled:(("+ ((("LightType" + maxwellLLister.count as string) as name)) + ".selection==1) and \
							(("+ ((("ColorType" + maxwellLLister.count as string) as name)) + ".selection==1)))")
			maxwellLLister.maxLightsRC.addHandler (("EmissionColor" + maxwellLLister.count as string) as name) #'changed val' filter:on \
				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #RGB val")
			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("EmissionColor" + maxwellLLister.count as string) as name)

			--correlated color
			maxwellLLister.maxLightsRC.addControl #spinner (("CorrelatedColor" + maxwellLLister.count as string) as name) "" \
				paramStr:("range:[273,10000," + ((maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1] #CorrelatedColor) as string) + "] type:#float " + \
							"fieldwidth:40 align:#left offset:[265,"+ (-23+ maxwellLLister.yOffset) as string + "]" + \
							" enabled:(("+ ((("LightType" + maxwellLLister.count as string) as name)) + ".selection==1) and \
							(("+ ((("ColorType" + maxwellLLister.count as string) as name)) + ".selection==2)))")
			maxwellLLister.maxLightsRC.addHandler (("CorrelatedColor" + maxwellLLister.count as string) as name) #'changed val' filter:on \
				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #CorrelatedColor val")
			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("CorrelatedColor" + maxwellLLister.count as string) as name)

			-- luminance type
			maxwellLLister.maxLightsRC.addControl #dropDownList (("LuminanceType" + maxwellLLister.count as string) as name) "" \
				paramStr:("items:" + maxwellLLister.maxwellLuminanceTypeStrings as string + " width:50" + \
							" offset:[" + (330 + vizRoffset) as string + ","+ (-23+ maxwellLLister.yOffset) as string + "]" + \
							" selection:" + (((maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1] #LuminanceType) + 1) as string) + \
							" enabled:(("+ ((("LightType" + maxwellLLister.count as string) as name)) + ".selection==1))")
			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LuminanceType" + maxwellLLister.count as string) as name)

			-- watts
			maxwellLLister.maxLightsRC.addControl #spinner (("Watts" + maxwellLLister.count as string) as name) "" \
				paramStr:("range:[0,1e10," + ((maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1] #Watts) as string) + "] type:#float " + \
							"fieldwidth:40 align:#left offset:[385,"+ (-25+ maxwellLLister.yOffset) as string + "]" + \
							" enabled:(("+ ((("LightType" + maxwellLLister.count as string) as name)) + ".selection==1) and \
							(("+ ((("LuminanceType" + maxwellLLister.count as string) as name)) + ".selection==1)))")
			maxwellLLister.maxLightsRC.addHandler (("Watts" + maxwellLLister.count as string) as name) #'changed val' filter:on \
				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #Watts val")
			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("Watts" + maxwellLLister.count as string) as name)

			--efficacy
			maxwellLLister.maxLightsRC.addControl #spinner (("Efficacy" + maxwellLLister.count as string) as name) "" \
				paramStr:("range:[0,683," + ((maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1] #Efficacy) as string) + "] type:#float " + \
							"fieldwidth:40 align:#left offset:[440,"+ (-21+ maxwellLLister.yOffset) as string + "]" + \
							" enabled:(("+ ((("LightType" + maxwellLLister.count as string) as name)) + ".selection==1) and \
							(("+ ((("LuminanceType" + maxwellLLister.count as string) as name)) + ".selection==1)))")
			maxwellLLister.maxLightsRC.addHandler (("Efficacy" + maxwellLLister.count as string) as name) #'changed val' filter:on \
				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #Efficacy val")
			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("Efficacy" + maxwellLLister.count as string) as name)

			-- luminance
			maxwellLLister.maxLightsRC.addControl #spinner (("Luminance" + maxwellLLister.count as string) as name) "" \
				paramStr:("range:[0,1e10," + ((maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1] #Luminance) as string) + "] type:#float " + \
				"fieldwidth:40 align:#left offset:[495,"+ (-21+ maxwellLLister.yOffset) as string + "]" + \
				" enabled:(("+ ((("LightType" + maxwellLLister.count as string) as name)) + ".selection==1) and \
							(("+ ((("LuminanceType" + maxwellLLister.count as string) as name)) + ".selection==2)))")
			maxwellLLister.maxLightsRC.addHandler (("Luminance" + maxwellLLister.count as string) as name) #'changed val' filter:on \
				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #Luminance val")
			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("Luminance" + maxwellLLister.count as string) as name)

			--luminance Units
			maxwellLLister.maxLightsRC.addControl #dropDownList (("LuminanceUnit" + maxwellLLister.count as string) as name) "" \
				paramStr:("items:" + maxwellLLister.maxwellUnitStrings as string + " width:50" + \
				" offset:[" + (550 + vizRoffset) as string + ","+ (-23+ maxwellLLister.yOffset) as string + "]" + \
					"selection:" + (((maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1] #Unit) + 1) as string) + \
					" enabled:(("+ ((("LightType" + maxwellLLister.count as string) as name)) + ".selection==1) and \
							(("+ ((("LuminanceType" + maxwellLLister.count as string) as name)) + ".selection==2)))")
			maxwellLLister.maxLightsRC.addHandler (("LuminanceUnit" + maxwellLLister.count as string) as name) #'selected i' filter:on \
				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #Unit (i-1)")
			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LuminanceUnit" + maxwellLLister.count as string) as name)

			-- IES Intensity
			maxwellLLister.maxLightsRC.addControl #spinner (("IESIntensity" + maxwellLLister.count as string) as name) "" \
				paramStr:("range:[1,99999," + ((maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1] #IESIntensity) as string) + "] type:#float " + \
				"fieldwidth:40 align:#left offset:[610,"+ (-25+ maxwellLLister.yOffset) as string + "]" + \
				" enabled:(("+ ((("LightType" + maxwellLLister.count as string) as name)) + ".selection==1) and \
							(("+ ((("LuminanceType" + maxwellLLister.count as string) as name)) + ".selection==3)))")
			maxwellLLister.maxLightsRC.addHandler (("IESIntensity" + maxwellLLister.count as string) as name) #'changed val' filter:on \
				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #IESIntensity val")
			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("IESIntensity" + maxwellLLister.count as string) as name)

			--Temperature
			maxwellLLister.maxLightsRC.addControl #spinner (("Temperature" + maxwellLLister.count as string) as name) "" \
				paramStr:("range:[273,10000," + ((maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1] #Temperature) as string) + "] type:#float " + \
				"fieldwidth:40 align:#left offset:[665,"+ (-21+ maxwellLLister.yOffset) as string + "]" + \
				" enabled:(("+ ((("LightType" + maxwellLLister.count as string) as name)) + ".selection==2))")
			maxwellLLister.maxLightsRC.addHandler (("Temperature" + maxwellLLister.count as string) as name) #'changed val' filter:on \
				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #Temperature val")
			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("Temperature" + maxwellLLister.count as string) as name)

			--MXI / HDR Intensity
			maxwellLLister.maxLightsRC.addControl #spinner (("MXIHDRIntensity" + maxwellLLister.count as string) as name) "" \
				paramStr:("range:[0,1e10," + ((maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1] #MXIHDRIntensity) as string) + "] type:#float " + \
				"fieldwidth:40 align:#left offset:[720,"+ (-21+ maxwellLLister.yOffset) as string + "]" + \
				" enabled:(("+ ((("LightType" + maxwellLLister.count as string) as name)) + ".selection==3))")
			maxwellLLister.maxLightsRC.addHandler (("MXIHDRIntensity" + maxwellLLister.count as string) as name) #'changed val' filter:on \
				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #MXIHDRIntensity val")
			append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("MXIHDRIntensity" + maxwellLLister.count as string) as name)

			--dropdown event handlers must come at the end or else the controls they modify haven't been declared yet
			maxwellLLister.maxLightsRC.addHandler (("LightType" + maxwellLLister.count as string) as name) #'selected i' filter:on \
				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #Type (i-1) \n" + \
							"ColorType" + maxwellLLister.count as string + ".enabled=" + "(LightType" + maxwellLLister.count as string + ".selection==1)\n" + \
							"EmissionColor" + maxwellLLister.count as string + ".enabled=" + "((LightType" + maxwellLLister.count as string + ".selection==1) and \
																										(ColorType" + maxwellLLister.count as string + ".selection==1))\n" + \
							"CorrelatedColor" + maxwellLLister.count as string + ".enabled=" + "((LightType" + maxwellLLister.count as string + ".selection==1) and \
																										(ColorType" + maxwellLLister.count as string + ".selection==2))\n" + \
							"LuminanceType" + maxwellLLister.count as string + ".enabled=" + "(LightType" + maxwellLLister.count as string + ".selection==1)\n" + \
							"Watts" + maxwellLLister.count as string + ".enabled=" + "((LightType" + maxwellLLister.count as string + ".selection==1) and \
																										(LuminanceType" + maxwellLLister.count as string + ".selection==1))\n" + \
							"Efficacy" + maxwellLLister.count as string + ".enabled=" + "((LightType" + maxwellLLister.count as string + ".selection==1) and \
																										(LuminanceType" + maxwellLLister.count as string + ".selection==1))\n" + \
							"Luminance" + maxwellLLister.count as string + ".enabled=" + "((LightType" + maxwellLLister.count as string + ".selection==1) and \
																										(LuminanceType" + maxwellLLister.count as string + ".selection==2))\n" + \
							"LuminanceUnit" + maxwellLLister.count as string + ".enabled=" + "((LightType" + maxwellLLister.count as string + ".selection==1) and \
																										(LuminanceType" + maxwellLLister.count as string + ".selection==2))\n" + \
							"IESIntensity" + maxwellLLister.count as string + ".enabled=" + "((LightType" + maxwellLLister.count as string + ".selection==1) and \
																										(LuminanceType" + maxwellLLister.count as string + ".selection==3))\n" + \
							"Temperature" + maxwellLLister.count as string + ".enabled=" + "(LightType" + maxwellLLister.count as string + ".selection==2)\n" + \
							"MXIHDRIntensity" + maxwellLLister.count as string + ".enabled=" + "(LightType" + maxwellLLister.count as string + ".selection==3)")
			maxwellLLister.maxLightsRC.addHandler (("ColorType" + maxwellLLister.count as string) as name) #'selected i' filter:on \
				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #ColorType (i-1)\n" + \
							"EmissionColor" + maxwellLLister.count as string + ".enabled=" + "(ColorType" + maxwellLLister.count as string + ".selection==1)\n" + \
							"CorrelatedColor" + maxwellLLister.count as string + ".enabled=" + "(ColorType" + maxwellLLister.count as string + ".selection==2)")
			maxwellLLister.maxLightsRC.addHandler (("LuminanceType" + maxwellLLister.count as string) as name) #'selected i' filter:on \
				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #LuminanceType (i-1)\n" + \
							"Watts" + maxwellLLister.count as string + ".enabled=((LightType" + maxwellLLister.count as string + ".selection==1) and \
																										(LuminanceType" + maxwellLLister.count as string + ".selection==1))\n" + \
							"Efficacy" + maxwellLLister.count as string + ".enabled=((LightType" + maxwellLLister.count as string + ".selection==1) and \
																										(LuminanceType" + maxwellLLister.count as string + ".selection==1))\n" + \
							"Luminance" + maxwellLLister.count as string + ".enabled=((LightType" + maxwellLLister.count as string + ".selection==1) and \
																										(LuminanceType" + maxwellLLister.count as string + ".selection==2))\n" + \
							"LuminanceUnit" + maxwellLLister.count as string + ".enabled=((LightType" + maxwellLLister.count as string + ".selection==1) and \
																										(LuminanceType" + maxwellLLister.count as string + ".selection==2))\n" + \
							"IESIntensity" + maxwellLLister.count as string + ".enabled=((LightType" + maxwellLLister.count as string + ".selection==1) and \
																										(LuminanceType" + maxwellLLister.count as string + ".selection==3))")
		)
		if heapFree < 1000000 do heapsize += 1000000 -- AB Jun 20, 2002

	) -- end CreateControls

	local CanAddControls = true
	local LightCountLimit = 150 -- this sets the maximum number of lights displayed

	if maxwellLLister.maxLightsList.count > 0 do
	(

		-- Start Localization

		maxwellLLister.maxLightsRC.addControl #label #title "Standard Lights" paramStr:" align:#left"

		WriteTitle hasShadow:true hasDecay:true hasSize:false Multip:"Multiplier"

		-- End Localization

		for x in 1 to maxwellLLister.maxLightsList.count where (CanAddControls = maxwellLLister.count < LightCountLimit) do
		(

		append maxwellLLister.LightIndex maxwellLLister.maxLightsList[x]
		createControls hasShadow:true hasDecay:true
		maxwellLLister.count += 1
		maxwellLLister.LightInspectorSetup.pbar.value = maxwellLLister.count*100/maxwellLLister.totalLightCount

		) -- end For i in MAXLights

	) -- end MAXLights

	if maxwellLLister.LSLightsList.count > 0 and CanAddControls do -- AB: Jun 20, 2002
	(

		-- Start Localization

		maxwellLLister.maxLightsRC.addControl #label #LStitle "Photometric Lights" paramStr:" align:#left"

		WriteTitle hasShadow:true hasDecay:false hasSize:true Multip:"Intensity(cd)"

		-- End Localization

		for x in 1 to maxwellLLister.LSLightsList.count where (CanAddControls = maxwellLLister.count < LightCountLimit) do
		(
		append maxwellLLister.LightIndex maxwellLLister.LSLightsList[x]
		createControls hasShadow:true hasDecay:false hasSize:true Multiplier:#intensity colorType:#FilterColor
		maxwellLLister.count += 1
		maxwellLLister.LightInspectorSetup.pbar.value = maxwellLLister.count*100/maxwellLLister.totalLightCount
		) -- end For i in LS Lights


	) -- end if LS Lights

	if maxwellLLister.miLightsList.count > 0 and CanAddControls do -- AB: Jun 20, 2002
	(
		-- Start Localization

		maxwellLLister.maxLightsRC.addControl #label #miLightstitle "mental ray Area Lights" paramStr:" align:#left"
		WriteTitle hasShadow:true hasDecay:false hasSize:false Multip:"Multip." isLuminaire:false
		-- End Localization

		for x in 1 to maxwellLLister.miLightsList.count  where (CanAddControls = maxwellLLister.count < LightCountLimit) do
		(
		append maxwellLLister.LightIndex maxwellLLister.miLightsList[x]
		createControls hasShadow:true hasDecay:true hasSize:false
		maxwellLLister.count += 1
		maxwellLLister.LightInspectorSetup.pbar.value = maxwellLLister.count*100/maxwellLLister.totalLightCount
		) -- end For i in miLightsList

	) -- end miLightsList

	if maxwellLLister.LuminairesList.count > 0 and CanAddControls do -- AB: Jun 20, 2002
	(

		-- Start Localization

		maxwellLLister.maxLightsRC.addControl #label #Luminairetitle "Luminaires" paramStr:" align:#left"

		WriteTitle hasDecay:false hasSize:false Multip:"Dimmer" hasShadow:false isLuminaire:true

		-- End Localization

		for x in 1 to maxwellLLister.LuminairesList.count  where (CanAddControls = maxwellLLister.count < LightCountLimit) do
		(
		append maxwellLLister.LightIndex maxwellLLister.LuminairesList[x]
		createControls hasShadow:false hasDecay:false hasSize:false Multiplier:#dimmer colorType:#FilterColor isLuminaire:true
		maxwellLLister.count += 1
		maxwellLLister.LightInspectorSetup.pbar.value = maxwellLLister.count*100/maxwellLLister.totalLightCount
		) -- end For i in LS Lights

	) -- end Luminaires

	if maxwellLLister.SunLightsList.count > 0 and CanAddControls do
	(

		-- Start Localization

		maxwellLLister.maxLightsRC.addControl #label #Suntitle "Sun Lights" paramStr:" align:#left"

		WriteTitle hasShadow:true hasDecay:false hasSize:false Multip:"Intensity(lux)"

		-- End Localization

		for x in 1 to maxwellLLister.SunLightsList.count where (CanAddControls = maxwellLLister.count < LightCountLimit) do
		(
		append maxwellLLister.LightIndex maxwellLLister.SunLightsList[x]
		createControls hasShadow:true hasDecay:false hasSize:false
		maxwellLLister.count += 1
		maxwellLLister.LightInspectorSetup.pbar.value = maxwellLLister.count*100/maxwellLLister.totalLightCount
		) -- end For i in Sun Lights


	)


	if maxwellLLister.SkyLightsList.count > 0 and CanAddControls do
	(

		-- Start Localization

		maxwellLLister.maxLightsRC.addControl #label #Skytitle "Sky Lights" paramStr:" align:#left"

		WriteTitle hasShadow:false hasDecay:false hasSize:false Multip:"Multiplier"

		-- End Localization

		for x in 1 to maxwellLLister.SkyLightsList.count where (CanAddControls = maxwellLLister.count < LightCountLimit) do
		(
		append maxwellLLister.LightIndex maxwellLLister.SkyLightsList[x]
		createControls hasShadow:false hasDecay:false hasSize:false
		maxwellLLister.count += 1
		maxwellLLister.LightInspectorSetup.pbar.value = maxwellLLister.count*100/maxwellLLister.totalLightCount
		) -- end For i in Sky Lights
	)

	if maxwellLLister.mrSkyLightsList.count > 0 and CanAddControls do
	(

		-- Start Localization

		maxwellLLister.maxLightsRC.addControl #label #mrSkytitle "mr Sky Lights" paramStr:" align:#left"

		WriteTitle hasShadow:false isMRSky:true

		-- End Localization

		for x in 1 to maxwellLLister.mrSkyLightsList.count where (CanAddControls = maxwellLLister.count < LightCountLimit) do
		(
		append maxwellLLister.LightIndex maxwellLLister.mrSkyLightsList[x]
		createControls hasShadow:false hasDecay:false hasSize:false ColorType:#none isMRSky:true
		maxwellLLister.count += 1
		maxwellLLister.LightInspectorSetup.pbar.value = maxwellLLister.count*100/maxwellLLister.totalLightCount
		) -- end For i in mr Sky Lights
	)

	if maxwellLLister.mrSunLightsList.count > 0 and CanAddControls do
	(

		-- Start Localization

		maxwellLLister.maxLightsRC.addControl #label #mrSuntitle "mr Sun Lights" paramStr:" align:#left"

		WriteTitle hasShadow:false isMRSun:true

		-- End Localization

		for x in 1 to maxwellLLister.mrSunLightsList.count where (CanAddControls = maxwellLLister.count < LightCountLimit) do
		(
		append maxwellLLister.LightIndex maxwellLLister.mrSunLightsList[x]
		createControls hasShadow:false hasDecay:false hasSize:false ColorType:#none Multiplier:#skymult isMRSun:true
		maxwellLLister.count += 1
		maxwellLLister.LightInspectorSetup.pbar.value = maxwellLLister.count*100/maxwellLLister.totalLightCount
		) -- end For i in mr Sun Lights
	)

	if maxwellLLister.mrSkyPortalLightsList.count > 0 and CanAddControls do
	(

		-- Start Localization

		maxwellLLister.maxLightsRC.addControl #label #mrSkyPortaltitle "mr Sky Portal Lights" paramStr:" align:#left"

		WriteTitle hasShadow:false ColorType:#rgbFilter isMRSkyPortal:true

		-- End Localization

		for x in 1 to maxwellLLister.mrSkyPortalLightsList.count where (CanAddControls = maxwellLLister.count < LightCountLimit) do
		(
		append maxwellLLister.LightIndex maxwellLLister.mrSkyPortalLightsList[x]
		createControls hasShadow:false hasDecay:false hasSize:false ColorType:#rgbFilter isMRSkyPortal:true
		maxwellLLister.count += 1
		maxwellLLister.LightInspectorSetup.pbar.value = maxwellLLister.count*100/maxwellLLister.totalLightCount
		) -- end For i in mr_Sky_Portal Lights
	)

	if maxwellLLister.maxwellLightsList.count > 0 and CanAddControls do
	(
		-- Start Localization

		maxwellLLister.maxLightsRC.addControl #label #maxwellLighttitle "Maxwell Lights" paramStr:" align:#left"

		WriteTitle hasShadow:false isMaxwellLight:true

		-- End Localization

		for x in 1 to maxwellLLister.maxwellLightsList.count where (CanAddControls = maxwellLLister.count < LightCountLimit) do
		(
		append maxwellLLister.LightIndex maxwellLLister.maxwellLightsList[x]
		createControls hasShadow:false hasDecay:false hasSize:false isMaxwellLight:true
		maxwellLLister.count += 1
		maxwellLLister.LightInspectorSetup.pbar.value = maxwellLLister.count*100/maxwellLLister.totalLightCount
		) -- end For i in mr_Sky_Portal Lights
	)

	local lbNameMW
	fn lbNameMW =
	(
		if maxwellLLister.lbCount == undefined do maxwellLLister.lbCount = 1
		maxwellLLister.lbCount += 1
		("LB" + maxwellLLister.lbCount as string) as name
	)

	if maxwellLLister.maxwellEnviroLights do	--this is either true or false, create all enviroment lighting (enviro + IBL) since they are always present, but not always on
	(
		rnd = renderers.current
		local isUsingEdittextOffset = 0, editTextSize = 75, vizRoffset = 0

		--------------------------------------------------------------------------------------------------------------------------------------
		--BEGIN MAXWELL SKYLIGHT SECTION
		--THIS IS COMMENTED OUT FOR NOW UNTIL A NEW VERSION OF THE MAXWELL PLUGIN COMES OUT
		--THAT PROPERLY SUPPORTS THE INTENSITY AND BLEND FACTOR FOR THE SKY LIGHT
		--IT IS BROKEN AS OF 4/14/2012 AND SHOULD BE FIXED IN THE NEXT RELEASE
		--------------------------------------------------------------------------------------------------------------------------------------
-- 		--create environment light titles
-- 		maxwellLLister.maxLightsRC.addControl #label #maxwellEnvirotitle "Maxwell Environment Lights" paramStr:" align:#left"
-- 		maxwellLLister.maxLightsRC.addControl #label (lbnameMW()) "On" paramStr:(" align:#left offset:[8," + (-3 + maxwellLLister.yOffset + maxwellLLister.LineOffset) as string + "]")
-- 		maxwellLLister.maxLightsRC.addControl #label (lbnameMW()) "Light Type" paramStr:(" align:#left offset:[28,"+ (-3 + maxwellLLister.yOffset + maxwellLLister.LineOffset) as string + "]")
--  		maxwellLLister.maxLightsRC.addControl #label (lbnameMW()) "Color" paramStr:(" align:#left offset:[102,"+ (-18 + maxwellLLister.yOffset) as string + "]")
--  		maxwellLLister.maxLightsRC.addControl #label (lbnameMW()) "Color 90" paramStr:(" align:#left offset:[215,"+ (-18 + maxwellLLister.yOffset) as string + "]")
--  		maxwellLLister.maxLightsRC.addControl #label (lbnameMW()) "Blend Factor" paramStr:(" align:#left offset:[223,"+ (-18 + maxwellLLister.yOffset) as string + "]")
--  		maxwellLLister.maxLightsRC.addControl #label (lbnameMW()) "Intensity" paramStr:(" align:#left offset:[265,"+ (-18 + maxwellLLister.yOffset) as string + "]")
-- 		--create environment light controls
-- 		append maxwellLLister.LightIndex #(rnd)
-- 		maxwellLLister.UIControlList[1][maxwellLLister.count] = maxwellLLister.LightIndex[maxwellLLister.count][1]
-- 		maxwellLLister.UIControlList[2][maxwellLLister.Count] = #()	--this needs to execute for all luminaires

-- 		enviroOn = ((rnd.skyType!=2) as string)
-- 		maxwellLLister.maxLightsRC.addControl #checkbox (("LightOn" + maxwellLLister.count as string) as name) "" \
-- 					paramStr:("checked:" + (enviroOn) + " offset:[8,"+ (-2+ maxwellLLister.yOffset + maxwellLLister.LineOffset) as string + "] width:18")
-- 		append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightOn" + maxwellLLister.count as string) as name)
--
-- 		maxwellLLister.maxLightsRC.addControl #dropDownList (("EnviroType" + maxwellLLister.count as string) as name) "" \
-- 				paramStr:("items:" + maxwellLLister.maxwellEnviroStrings as string + " width:75" + \
-- 				" offset:[23,"+ (-22+ maxwellLLister.yOffset) as string + "]" + \
-- 					"selection:" + ((mod (rnd.skyType) 2) + 1) as string)
--
-- 		append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("EnviroType" + maxwellLLister.count as string) as name)
--
-- 		-- color
-- 		maxwellLLister.maxLightsRC.addControl #colorpicker (("EnviroColor" + maxwellLLister.count as string) as name) "" \
-- 				paramStr:("color:" + (maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1] #skyDomeColor) as string + \
-- 							" offset:[" + (190 + vizRoffset) as string + ","+ (-27+ maxwellLLister.yOffset) as string + "] width:25" + \
-- 							" enabled:("+ ((("EnviroType" + maxwellLLister.count as string) as name)) + ".selection==0)")
-- 		maxwellLLister.maxLightsRC.addHandler (("EnviroColor" + maxwellLLister.count as string) as name) #'changed val' filter:on \
-- 				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #skyDomeColor val")
-- 		append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("EnviroColor" + maxwellLLister.count as string) as name)

		--color 90
-- 		maxwellLLister.maxLightsRC.addControl #colorpicker (("EnviroColor90" + maxwellLLister.count as string) as name) "" \
-- 				paramStr:("color:" + (maxwellLLister.getLightProp maxwellLLister.LightIndex[maxwellLLister.count][1] #skyDomeColor90) as string + \
-- 							" offset:[" + (220 + vizRoffset) as string + ","+ (-27+ maxwellLLister.yOffset) as string + "] width:25" + \
-- 							" enabled:("+ ((("EnviroType" + maxwellLLister.count as string) as name)) + ".selection==1)")
-- 		maxwellLLister.maxLightsRC.addHandler (("EnviroColor90" + maxwellLLister.count as string) as name) #'changed val' filter:on \
-- 				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #skyDomeColor90 val")
-- 		append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("EnviroColor90" + maxwellLLister.count as string) as name)
--
-- 		--blend factor
-- 		maxwellLLister.maxLightsRC.addControl #spinner (("BlendFactor" + maxwellLLister.count as string) as name) "" \
-- 				paramStr:("range:[0.0,90,45 type:#float " + \
-- 				"fieldwidth:40 align:#left offset:[720,"+ (-21+ maxwellLLister.yOffset) as string + "]" + \
-- 				" enabled:(("+ ((("EnviroType" + maxwellLLister.count as string) as name)) + ".selection==0))")
-- 		maxwellLLister.maxLightsRC.addHandler (("BlendFactor" + maxwellLLister.count as string) as name) #'changed val' filter:on \
-- 				codeStr:("maxwellLLister.setLightProp maxwellLLister.LightIndex[" + maxwellLLister.count as string + "][1] #MXIHDRIntensity val")
-- 		append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("MXIHDRIntensity" + maxwellLLister.count as string) as name)
--
-- 		--intensity
-- 		maxwellLLister.maxLightsRC.addControl #spinner (("EnviroIntensity" + maxwellLLister.count as string) as name) "" \
-- 				paramStr:("range:[0,1e10," + renderers.current.skyDomeIntensity as string + "] type:#float " + \
-- 				"fieldwidth:40 align:#left offset:[720,"+ (-21+ maxwellLLister.yOffset) as string + "]" + \
-- 				" enabled:true")
-- 		maxwellLLister.maxLightsRC.addHandler (("EnviroIntensity" + maxwellLLister.count as string) as name) #'changed val' filter:on \
-- 				codeStr:("if " + ((("EnviroType" + maxwellLLister.count as string) as name)) + "==0 then (renderers.current.skyDomeIntensity = val)\n" +\
-- 							"else if " + ((("EnviroType" + maxwellLLister.count as string) as name)) + "==1 then (renderers.current.skyPhysicalIntensity = val)")
-- 		append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("EnviroIntensity" + maxwellLLister.count as string) as name)
--
--
-- 		--add defered event handlers here
-- 		maxwellLLister.maxLightsRC.addHandler (("LightOn" + maxwellLLister.count as string) as name) #'changed state' filter:on \
-- 					codeStr:("if state == true then (val ="+ ((("EnviroType" + maxwellLLister.count as string) as name)) + ".selection - 1) \nelse (val = 2)\n" + \
-- 								"renderers.current.skyType = val")
-- 		maxwellLLister.maxLightsRC.addHandler (("EnviroType" + maxwellLLister.count as string) as name) #'selected i' filter:on \
-- 				codeStr:("renderers.current.skyType = i-1 \n" + \
-- 							"EnviroColor" + maxwellLLister.count as string + ".enabled=" + "(EnviroType" + maxwellLLister.count as string + ".selection==0)\n" + \
-- 							"EnviroColor90" + maxwellLLister.count as string + ".enabled=" + "((EnviroType" + maxwellLLister.count as string + ".selection==0)\n" + \
-- 							"BlendFactor" + maxwellLLister.count as string + ".enabled=" + "((EnviroType" + maxwellLLister.count as string + ".selection==0)\n")
--
-- 		maxwellLLister.count += 1
-- 		maxwellLLister.LightInspectorSetup.pbar.value = maxwellLLister.count*100/maxwellLLister.totalLightCount
		--------------------------------------------------------------------------------------------------------------------------------------
		--END MAXWELL SKYLIGHT SECTION
		--------------------------------------------------------------------------------------------------------------------------------------

		--create IBL light titles
		maxwellLLister.maxLightsRC.addControl #label #maxwellIBLtitle "Maxwell IBL Lights" paramStr:" align:#left"
		maxwellLLister.maxLightsRC.addControl #label (lbnameMW()) "On" paramStr:(" align:#left offset:[8," + (-3 + maxwellLLister.yOffset + maxwellLLister.LineOffset) as string + "]")
		maxwellLLister.maxLightsRC.addControl #label (lbnameMW()) "Name" paramStr:(" align:#left offset:[28,"+ (-18 + maxwellLLister.yOffset + maxwellLLister.LineOffset) as string + "]")
		maxwellLLister.maxLightsRC.addControl #label (lbnameMW()) "Intensity" paramStr:(" align:#left offset:[102,"+ (-18 + maxwellLLister.yOffset + maxwellLLister.LineOffset) as string + "]")
 		maxwellLLister.maxLightsRC.addControl #label (lbnameMW()) "Use Background" paramStr:(" align:#left offset:[160,"+ (-18 + maxwellLLister.yOffset) as string + "]")
		--create IBL Light controls
		--create environment light controls
		append maxwellLLister.LightIndex #(rnd)
		maxwellLLister.UIControlList[1][maxwellLLister.count] = maxwellLLister.LightIndex[maxwellLLister.count][1]
		maxwellLLister.UIControlList[2][maxwellLLister.Count] = #()	--this needs to execute for all luminaires

		--all ibl lights enabled / disabled
		maxwellLLister.maxLightsRC.addControl #checkbox (("LightOn" + maxwellLLister.count as string) as name) "" \
					paramStr:("checked:" + renderers.current.ibeActivate as string + " offset:[8,"+ (-2+ maxwellLLister.yOffset + maxwellLLister.LineOffset) as string + "] width:18")
		append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightOn" + maxwellLLister.count as string) as name)
		maxwellLLister.maxLightsRC.addHandler (("LightOn" + maxwellLLister.count as string) as name) #'changed state' filter:on \
					codeStr:("renderers.current.ibeActivate = state")

		--global name
		maxwellLLister.maxLightsRC.addControl #label (lbnameMW()) "Global" paramStr:(" align:#left offset:[26,"+ (-21 + maxwellLLister.yOffset) as string + "]")

		--global intensity
		maxwellLLister.maxLightsRC.addControl #spinner (("iblGlobalIntensity" + maxwellLLister.count as string) as name) "" \
				paramStr:("range:[0,1e10," + renderers.current.ibeIntensityMultiplier as string + "] type:#float " + \
				"fieldwidth:40 align:#left offset:[102,"+ (-19+ maxwellLLister.yOffset) as string + "]" + \
				" enabled:true")
		maxwellLLister.maxLightsRC.addHandler (("iblGlobalIntensity" + maxwellLLister.count as string) as name) #'changed val' filter:on \
				codeStr:("renderers.current.ibeIntensityMultiplier = val")
		append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("iblGlobalIntensity" + maxwellLLister.count as string) as name)

		maxwellLLister.count += 1
		maxwellLLister.LightInspectorSetup.pbar.value = maxwellLLister.count*100/maxwellLLister.totalLightCount

		--background
		append maxwellLLister.LightIndex #(rnd)
		maxwellLLister.UIControlList[1][maxwellLLister.count] = maxwellLLister.LightIndex[maxwellLLister.count][1]
		maxwellLLister.UIControlList[2][maxwellLLister.Count] = #()	--this needs to execute for all luminaires
		--background enabled / disabled
		maxwellLLister.maxLightsRC.addControl #checkbox (("LightOn" + maxwellLLister.count as string) as name) "" \
					paramStr:("checked:" + renderers.current.ibeBgState as string + " offset:[8,"+ (-2+ maxwellLLister.yOffset + maxwellLLister.LineOffset) as string + "] width:18")
		append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightOn" + maxwellLLister.count as string) as name)
		maxwellLLister.maxLightsRC.addHandler (("LightOn" + maxwellLLister.count as string) as name) #'changed state' filter:on \
					codeStr:("renderers.current.ibeBgState = state")
		--background name
		maxwellLLister.maxLightsRC.addControl #label (lbnameMW()) "Background" paramStr:(" align:#left offset:[26,"+ (-21 + maxwellLLister.yOffset) as string + "]")

		--background intensity
		maxwellLLister.maxLightsRC.addControl #spinner (("iblBackgroundIntensity" + maxwellLLister.count as string) as name) "" \
				paramStr:("range:[0,1e10," + renderers.current.ibeBgIntensity as string + "] type:#float " + \
				"fieldwidth:40 align:#left offset:[102,"+ (-19+ maxwellLLister.yOffset) as string + "]" + \
				" enabled:true")
		maxwellLLister.maxLightsRC.addHandler (("iblBackgroundIntensity" + maxwellLLister.count as string) as name) #'changed val' filter:on \
				codeStr:("renderers.current.ibeBgIntensity = val")
		append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("iblBackgroundIntensity" + maxwellLLister.count as string) as name)

		maxwellLLister.count += 1
		maxwellLLister.LightInspectorSetup.pbar.value = maxwellLLister.count*100/maxwellLLister.totalLightCount

		--reflection
		append maxwellLLister.LightIndex #(rnd)
		maxwellLLister.UIControlList[1][maxwellLLister.count] = maxwellLLister.LightIndex[maxwellLLister.count][1]
		maxwellLLister.UIControlList[2][maxwellLLister.Count] = #()	--this needs to execute for all luminaires
		--reflection enabled / disabled
		maxwellLLister.maxLightsRC.addControl #checkbox (("LightOn" + maxwellLLister.count as string) as name) "" \
					paramStr:("checked:" + renderers.current.ibeReflectionState as string + " offset:[8,"+ (-2+ maxwellLLister.yOffset + maxwellLLister.LineOffset) as string + "] width:18")
		append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightOn" + maxwellLLister.count as string) as name)
		maxwellLLister.maxLightsRC.addHandler (("LightOn" + maxwellLLister.count as string) as name) #'changed state' filter:on \
					codeStr:("renderers.current.ibeReflectionState = state")
		--reflection name
		maxwellLLister.maxLightsRC.addControl #label (lbnameMW()) "Reflection" paramStr:(" align:#left offset:[26,"+ (-21 + maxwellLLister.yOffset) as string + "]")

		--reflection intensity
		maxwellLLister.maxLightsRC.addControl #spinner (("iblReflectionIntensity" + maxwellLLister.count as string) as name) "" \
				paramStr:("range:[0,1e10," + renderers.current.ibeReflectionIntensity as string + "] type:#float " + \
				"fieldwidth:40 align:#left offset:[102,"+ (-19+ maxwellLLister.yOffset) as string + "]" + \
				" enabled:(not renderers.current.ibeReflectionUseAsBg)")
		maxwellLLister.maxLightsRC.addHandler (("iblReflectionIntensity" + maxwellLLister.count as string) as name) #'changed val' filter:on \
				codeStr:("renderers.current.ibeReflectionIntensity = val")
		append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("iblReflectionIntensity" + maxwellLLister.count as string) as name)

		--reflection use background
		maxwellLLister.maxLightsRC.addControl #checkbox (("iblReflectionUseBg" + maxwellLLister.count as string) as name) "" \
					paramStr:("checked:" + renderers.current.ibeReflectionUseAsBg as string + " offset:[185,"+ (-21+ maxwellLLister.yOffset) as string + "] width:18")
		append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("iblReflectionUseBg" + maxwellLLister.count as string) as name)
		maxwellLLister.maxLightsRC.addHandler (("iblReflectionUseBg" + maxwellLLister.count as string) as name) #'changed state' filter:on \
					codeStr:("renderers.current.ibeReflectionUseAsBg = state \n" + \
								(("iblReflectionIntensity" + maxwellLLister.count as string) as name) + ".enabled = (not state)")

		maxwellLLister.count += 1
		maxwellLLister.LightInspectorSetup.pbar.value = maxwellLLister.count*100/maxwellLLister.totalLightCount

		--Refraction
		append maxwellLLister.LightIndex #(rnd)
		maxwellLLister.UIControlList[1][maxwellLLister.count] = maxwellLLister.LightIndex[maxwellLLister.count][1]
		maxwellLLister.UIControlList[2][maxwellLLister.Count] = #()	--this needs to execute for all luminaires
		--Refraction enabled / disabled
		maxwellLLister.maxLightsRC.addControl #checkbox (("LightOn" + maxwellLLister.count as string) as name) "" \
					paramStr:("checked:" + renderers.current.ibeRefractionState as string + " offset:[8,"+ (-2+ maxwellLLister.yOffset + maxwellLLister.LineOffset) as string + "] width:18")
		append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightOn" + maxwellLLister.count as string) as name)
		maxwellLLister.maxLightsRC.addHandler (("LightOn" + maxwellLLister.count as string) as name) #'changed state' filter:on \
					codeStr:("renderers.current.ibeRefractionState = state")
		--reflection name
		maxwellLLister.maxLightsRC.addControl #label (lbnameMW()) "Refraction" paramStr:(" align:#left offset:[26,"+ (-21 + maxwellLLister.yOffset) as string + "]")

		--reflection intensity
		maxwellLLister.maxLightsRC.addControl #spinner (("iblRefractionIntensity" + maxwellLLister.count as string) as name) "" \
				paramStr:("range:[0,1e10," + renderers.current.ibeRefractionIntensity as string + "] type:#float " + \
				"fieldwidth:40 align:#left offset:[102,"+ (-19+ maxwellLLister.yOffset) as string + "]" + \
				" enabled:(not renderers.current.ibeRefractionUseAsBg)")
		maxwellLLister.maxLightsRC.addHandler (("iblRefractionIntensity" + maxwellLLister.count as string) as name) #'changed val' filter:on \
				codeStr:("renderers.current.ibeRefractionIntensity = val")
		append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("iblRefractionIntensity" + maxwellLLister.count as string) as name)

		--reflection use background
		maxwellLLister.maxLightsRC.addControl #checkbox (("iblRefractionUseBg" + maxwellLLister.count as string) as name) "" \
					paramStr:("checked:" + renderers.current.ibeRefractionUseAsBg as string + " offset:[185,"+ (-21+ maxwellLLister.yOffset) as string + "] width:18")
		append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("iblRefractionUseBg" + maxwellLLister.count as string) as name)
		maxwellLLister.maxLightsRC.addHandler (("iblRefractionUseBg" + maxwellLLister.count as string) as name) #'changed state' filter:on \
					codeStr:("renderers.current.ibeRefractionUseAsBg = state \n" + \
								(("iblRefractionIntensity" + maxwellLLister.count as string) as name) + ".enabled = (not state)")

		maxwellLLister.count += 1
		maxwellLLister.LightInspectorSetup.pbar.value = maxwellLLister.count*100/maxwellLLister.totalLightCount

		--Illumination
		append maxwellLLister.LightIndex #(rnd)
		maxwellLLister.UIControlList[1][maxwellLLister.count] = maxwellLLister.LightIndex[maxwellLLister.count][1]
		maxwellLLister.UIControlList[2][maxwellLLister.Count] = #()	--this needs to execute for all luminaires
		--Refraction enabled / disabled
		maxwellLLister.maxLightsRC.addControl #checkbox (("LightOn" + maxwellLLister.count as string) as name) "" \
					paramStr:("checked:" + renderers.current.ibeIlluminationState as string + " offset:[8,"+ (-2+ maxwellLLister.yOffset + maxwellLLister.LineOffset) as string + "] width:18")
		append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("LightOn" + maxwellLLister.count as string) as name)
		maxwellLLister.maxLightsRC.addHandler (("LightOn" + maxwellLLister.count as string) as name) #'changed state' filter:on \
					codeStr:("renderers.current.ibeIlluminationState = state")
		--reflection name
		maxwellLLister.maxLightsRC.addControl #label (lbnameMW()) "Illumination" paramStr:(" align:#left offset:[26,"+ (-21 + maxwellLLister.yOffset) as string + "]")

		--reflection intensity
		maxwellLLister.maxLightsRC.addControl #spinner (("iblIlluminationIntensity" + maxwellLLister.count as string) as name) "" \
				paramStr:("range:[0,1e10," + renderers.current.ibeIlluminationIntensity as string + "] type:#float " + \
				"fieldwidth:40 align:#left offset:[102,"+ (-19+ maxwellLLister.yOffset) as string + "]" + \
				" enabled:(not renderers.current.ibeIlluminationUseAsBg)")
		maxwellLLister.maxLightsRC.addHandler (("iblIlluminationIntensity" + maxwellLLister.count as string) as name) #'changed val' filter:on \
				codeStr:("renderers.current.ibeIlluminationIntensity = val")
		append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("iblIlluminationIntensity" + maxwellLLister.count as string) as name)

		--reflection use background
		maxwellLLister.maxLightsRC.addControl #checkbox (("iblIlluminationUseBg" + maxwellLLister.count as string) as name) "" \
					paramStr:("checked:" + renderers.current.ibeIlluminationUseAsBg as string + " offset:[185,"+ (-21+ maxwellLLister.yOffset) as string + "] width:18")
		append maxwellLLister.UIControlList[2][maxwellLLister.Count] (("iblIlluminationUseBg" + maxwellLLister.count as string) as name)
		maxwellLLister.maxLightsRC.addHandler (("iblIlluminationUseBg" + maxwellLLister.count as string) as name) #'changed state' filter:on \
					codeStr:("renderers.current.ibeIlluminationUseAsBg = state \n" + \
								(("iblIlluminationIntensity" + maxwellLLister.count as string) as name) + ".enabled = (not state)")

		maxwellLLister.count += 1
		maxwellLLister.LightInspectorSetup.pbar.value = maxwellLLister.count*100/maxwellLLister.totalLightCount
	)

	-- Callback Handlers

	maxwellLLister.maxLightsRC.addHandler "maxLightsRollout" #'open' filter:off \
		codeStr:("maxwellLLister.DeleteCallback = when maxwellLLister.UIControlList[1] deleted obj do" + \
		"\n(\nlocal foundMe = findItem maxwellLLister.UIControlList[1] obj\n" + \
		"if foundMe > 0 do\n(\n" + \
		"maxwellLLister.disableUIElements maxwellLLister.UIControlList[2][foundMe]\n)\n)")

	maxwellLLister.maxLightsRC.addHandler "maxLightsRollout" #'close' filter:off \
		codeStr:"DeleteChangeHandler maxwellLLister.DeleteCallback"

	-- Removing the Refresh/ProgressBar

	maxwellLLister.LightInspectorSetup.pbar.value = 0
	maxwellLLister.LightInspectorSetup.pbar.visible = false

	-- AB: Jun 20, 2002
	-- Add a new control that tells users to use the selection mode if they had too many lights in the list

	if not CanAddControls and maxwellLLister.maxLightsRC.str != "" do
		maxwellLLister.maxLightsRC.addControl #label #lbLimitControls "The maximum number of Lights has been reached, please select fewer lights and use the Selected Lights option" \
			paramStr:" align:#center offset:[0,10]"

	if maxwellLLister.maxLightsRC.str != "" then maxwellLLister.maxLightsRC.end() else undefined
)

maxwellLLister.CreateLightRollout = CreateLightRollout

maxwellLLister.GlobalLightParameters =
(local GlobalLightParameters
rollout GlobalLightParameters "General Settings"
(

	-- Start Localization

	radioButtons rbtoggle labels:#("Selected Lights","All Lights")

	local lblOffset = -18 + (if LListeryOffset == undefined then 0 else LListerYOffset)

	label lb01 "On" align:#left offset:[-6,-3]
	label lb03 "Multiplier"  align:#left offset:[12,lblOffset]
	label lb03a "Multiplier (%)" align:#left offset:[81,lblOffset] visible:(ProductAppID == #vizR)
	label lb04 "Color"  align:#left offset:[67,lblOffset]
	label lb05 "Shadows"  align:#left offset:[96,lblOffset]
	label lb06 "Map Size"  align:#left offset:[229,lblOffset] visible:(ProductAppID != #VIZR)
	label lb07 "Bias"  align:#left offset:[286,lblOffset] visible:(ProductAppID != #VIZR)
	label lb08 "Sm.Range"  align:#left offset:[337,lblOffset] visible:(ProductAppID != #VIZR)
	label lb09 "Trans."  align:#left offset:[390,lblOffset] visible:(ProductAppID != #VIZR)
	label lb10 "Int."  align:#left offset:[424,lblOffset] visible:(ProductAppID != #VIZR)
	label lb11 "Qual."  align:#left offset:[461,lblOffset] visible:(ProductAppID != #VIZR)
	label lb12 "Decay"  align:#left offset:[505,lblOffset] visible:(ProductAppID != #VIZR)
	label lb13 "Start"  align:#left offset:[586,lblOffset] visible:(ProductAppID != #VIZR)
	label lb14 "Length"  align:#left offset:[643,lblOffset] visible:(ProductAppID != #VIZR)
	label lb15 "Width/Radius"  align:#left offset:[699,lblOffset] visible:(ProductAppID != #VIZR)
	-- End Localization

	checkBox lightOn "" width:15 checked:true offset:[-4,0]
	spinner lightInten "" fieldWidth:45 type:#float range:[-10000,10000,1500] align:#left offset:[10,-20+ LListeryOffset] visible:(ProductAppID == #vizR)
	checkBox lightMultOn "" width:15 checked:false offset:[81,-20+ LListeryOffset] visible:(ProductAppID == #vizR)
	spinner lightMult "" fieldWidth:45 type:#float range:[-10000,10000,1.0] align:#left offset:[10,-20+ LListeryOffset]
	colorPicker lightCol "" width:25 color:white offset:[66,-23+ LListeryOffset]
	checkBox shadowOn "" width:15 checked:true offset:[96,-22+ LListeryOffset]
	dropDownList shadowType width:115 items:maxwellLLister.ShadowPluginsName offset:[113,-23+ LListeryOffset] visible:(ProductAppID != #vizR)
	spinner ShadowMapSize "" fieldWidth:45 type:#integer range:[0,10000,512] align:#left offset:[227,-24+ LListeryOffset] visible:(ProductAppID != #VIZR)
	spinner ShadowBias "" fieldWidth:45 type:#float range:[0,10000,0.5] align:#left offset:[284,-21+ LListeryOffset] visible:(ProductAppID != #VIZR)
	spinner ShadowSmpRange "" fieldWidth:45 type:#float range:[0,50,4.0] align:#left offset:[341,-21+ LListeryOffset] visible:(ProductAppID != #VIZR)
	checkBox shadowTrans "" width:15 offset:[401,-20+ LListeryOffset] visible:(ProductAppID != #VIZR)
	spinner ShadowInteg "" fieldWidth:30 type:#integer range:[0,15,1] align:#left offset:[415,-21+ LListeryOffset] visible:(ProductAppID != #VIZR)
	spinner ShadowQual 	"" fieldWidth:30 type:#Integer range:[0,15,2] align:#left offset:[459,-21+ LListeryOffset] visible:(ProductAppID != #VIZR)
	dropDownList lightDecay width:80 items:maxwellLLister.decayStrings offset:[504,-23+ LListeryOffset] visible:(ProductAppID != #VIZR)
	spinner lightDecaySt "" fieldWidth:45 type:#float range:[0,10000,40] align:#left offset:[584,-24+ LListeryOffset] visible:(ProductAppID != #VIZR)
	spinner lightLength "" fieldWidth:45 type:#float range:[0,10000,40] align:#left offset:[641,-21+ LListeryOffset] visible:(ProductAppID != #VIZR)
	spinner lightWidth "" fieldWidth:45 type:#float range:[0,10000,40] align:#left offset:[697,-21+ LListeryOffset] visible:(ProductAppID != #VIZR)

	group ""
	(

	-- Start Localization

	colorpicker gTint "Global Tint:" color:lightTintColor visible:(ProductAppID != #VIZR) offset:[180,0]
	spinner gLevel "Global Level:" range:[0,10000,lightLevel]  fieldWidth:45 align:#left offset:[290,-22+ LListeryOffset] visible:(ProductAppID != #VIZR)
	colorPicker cpAmbient "Ambient Color" color:ambientColor offset:[420,-24+ LListeryOffset] visible:(ProductAppID != #VIZR)

	-- End Localization

	)

	on GlobalLightParameters open do
	(
		if ProductAppID == #vizR do
		(
			lightmult.range = [0,1000000.0,100.0]
			lb03.text = "Intensity (cd)"
			lb04.pos = lb04.pos + [88,0]
			lb05.pos = lb05.pos + [87,0]
			lightmult.pos = lightMult.pos + [87,0]
			lightCol.pos = lightCol.pos + [88,0]
			shadowOn.pos = shadowOn.pos + [88,0]
		)
		dialogUp = true
	)

	on GlobalLightParameters close do
	(
		dialogUp = false
		updateToolbarButtons()
	)

	on gtint changed val do lightTintColor = val
	on glevel changed val do lightLevel = val
	on cpAmbient changed val do ambientColor = val

	fn setCollectionProperty prop val CreateUndo:true =
	(
		if createUndo then
		(
			undo "LightLister" on
			(
				local myCollection = if rbToggle.state == 1 then Selection else Lights
				for i in myCollection do
				(
					setLightProp i.baseobject prop val
					setShdProp i.baseObject prop val
				)
			)
		)
		else
		(
			local myCollection = if rbToggle.state == 1 then Selection else Lights
			for i in myCollection do
			(
				setLightProp i.baseobject prop val
				setShdProp i.baseObject prop val
			)
		)
	)

	on lightOn changed state do setCollectionProperty #enabled state
	on lightCol changed val do
	(
		setCollectionProperty #color val CreateUndo:false
		setCollectionProperty #filter_Color val CreateUndo:false
		setCollectionProperty #filterColor val CreateUndo:false
	)
	on shadowOn changed state do setCollectionProperty #castShadows state
	on shadowTrans changed state do setCollectionProperty #shadow_transparent state
	on shadowInteg changed val do setCollectionProperty #pass1 val CreateUndo:false
	on shadowQual changed val do setCollectionProperty #pass2 val CreateUndo:false
	on lightWidth changed val do
	(
		setCollectionProperty #light_Width val CreateUndo:false
		setCollectionProperty #light_Radius val CreateUndo:false
	)
	on lightLength changed val do setCollectionProperty #length val CreateUndo:false
	on lightMult changed val do
	(
		setCollectionProperty #multiplier val CreateUndo:false
		if ProductAppID != #VIZR do setCollectionProperty #intensity val CreateUndo:false
		setCollectionProperty #dimmer val CreateUndo:false
	)
	on lightMultOn changed state do setCollectionProperty #useMultiplier state
	on lightInten changed val do setCollectionProperty #intensity val CreateUndo:false
	on ShadowMapSize changed val do setCollectionProperty #mapSize val CreateUndo:false
	on ShadowSmpRange changed val do setCollectionProperty #sampleRange val CreateUndo:false
	on lightDecaySt changed val do setCollectionProperty #decayRadius val CreateUndo:false
	on lightDecay selected d do setCollectionProperty #attenDecay d
	on shadowBias changed val do
	(
		setCollectionProperty #mapBias val CreateUndo:false
		setCollectionProperty #ray_Bias val CreateUndo:false
		setCollectionProperty #raytraceBias val CreateUndo:false
	)

	on shadowType selected j do
	(
		local myCollection = if rbToggle.state == 1 then Selection else Lights
		for i in myCollection do setLightProp i.baseobject #shadowGenerator (maxwellLLister.ShadowPlugins[j]())
	)

) -- end Rollout
) -- end structDef
local lblSelector

if ProductAppID == #VIZR then lblSelector = #("Scene","Selection","Batch Update") -- localize
	else lblSelector = #("All Lights","Selected Lights","General Settings") -- localize

maxwellLLister.LightInspectorSetup =
(local LightInspectorSetup
rollout LightInspectorSetup "Configuration" -- Localize
(
	radiobuttons rolloutSelector labels:lblSelector
	checkbutton btnReload "Refresh" align:#right offset:[0,-20] height:16 highlightColor:(color ((colorman.getcolor #activecommand).x *255) ((colorman.getcolor #activecommand).y *255)((colorman.getcolor #activecommand).z *255)) checked:false -- Localize
	progressBar pbar width:120 pos:(btnReload.pos - [125,-1])

	on rolloutSelector changed state do
	(
		rolloutSelector.state = state
		case rolloutSelector.state of
		(
		1:	(
			btnReload.visible = false
			try(RemoveRollout maxwellLLister.GlobalLightParameters maxwellLLister.LightInspectorFloater) catch()
			try(RemoveRollout maxwellLLister.LightInspectorListRollout maxwellLLister.LightInspectorFloater) catch()
			maxwellLLister.LightInspectorListRollout = maxwellLLister.CreateLightRollout (Lights as array + helpers as array)
			if maxwellLLister.LightInspectorListRollout != undefined do
				addRollout maxwellLLister.LightInspectorListRollout maxwellLLister.LightInspectorFloater
			maxwellLLister.maxLightsRC = undefined
			gc light:true
			btnReload.visible = true
			)
		2:	(
			btnReload.visible = false
			try(RemoveRollout maxwellLLister.GlobalLightParameters maxwellLLister.LightInspectorFloater) catch()
			try(RemoveRollout maxwellLLister.LightInspectorListRollout maxwellLLister.LightInspectorFloater) catch()
			maxwellLLister.LightInspectorListRollout = maxwellLLister.CreateLightRollout Selection
			if maxwellLLister.LightInspectorListRollout != undefined do
				addRollout maxwellLLister.LightInspectorListRollout maxwellLLister.LightInspectorFloater
			maxwellLLister.maxLightsRC = undefined
			gc light:true
			btnReload.visible = true
			)
		3:	(
			try(RemoveRollout maxwellLLister.GlobalLightParameters maxwellLLister.LightInspectorFloater) catch()
			try(RemoveRollout maxwellLLister.LightInspectorListRollout maxwellLLister.LightInspectorFloater) catch()
			addRollout maxwellLLister.GlobalLightParameters maxwellLLister.LightInspectorFloater
			btnReload.visible = false
			)
		)
	)

	on btnReload changed state do
	(
		rolloutSelector.changed rolloutSelector.state
		btnReload.checked = false
	)

	on LightInspectorSetup close do
	(
		callBacks.RemoveScripts id:#LListerRollout
		setIniSetting "$plugCfg/maxwellLLister.cfg" "General" "DialogPos" (maxwellLLister.LightInspectorFloater.Pos as string) -- do not localize
		setIniSetting "$plugCfg/maxwellLLister.cfg" "General" "DialogSize" (maxwellLLister.LightInspectorFloater.Size as string) -- do not localize
		setIniSetting "$plugCfg/maxwellLLister.cfg" "General" "LastState" (rolloutSelector.state as string) -- do not localize

		dialogUp = false
		updateToolbarButtons()
	)

	on LightInspectorSetup open do
	(
		if ProductAppID == #vizR do rolloutSelector.pos = rolloutSelector.pos - [30,0,0]
		pbar.visible = false
		local lastState = (getIniSetting "$plugCfg/maxwellLLister.cfg" "General" "LastState") as integer  -- do not localize
		if lastState == 0 do lastState = 1
		if lastState < 4 do
			rolloutSelector.changed lastState
		maxwellLLister.maxLightsRC = undefined
		gc light:true

		-- Callbacks to remove Floater
		callBacks.AddScript #systemPreReset "CloseRolloutFloater maxwellLLister.LightInspectorFloater" id:#LListerRollout  -- do not localize
		callBacks.AddScript #systemPreNew "CloseRolloutFloater maxwellLLister.LightInspectorFloater" id:#LListerRollout -- do not localize
		callBacks.AddScript #filePreOpen "CloseRolloutFloater maxwellLLister.LightInspectorFloater" id:#LListerRollout -- do not localize

		dialogUp = true
		updateToolbarButtons()
	)

) -- end Rollout
) -- end StructDef

on execute do
(

	-- Loading rollout size and position, if available

	local dialogPos, dialogSize

	dialogPos = execute (getIniSetting "$plugCfg/maxwellLLister.cfg" "General" "DialogPos") -- Do not localize
	dialogSize = execute (getIniSetting "$plugCfg/maxwellLLister.cfg" "General" "DialogSize") -- Do not localize

	if classof DialogPos != Point2 do dialogPos = [200,300]
	if classof DialogSize != Point2 do if ProductAppID != #VIZR then dialogSize = [800,300] else dialogSize = [360,300]

	if ProductAppID != #VIZR then DialogSize.x = 800 else DialogSize.x = 360

	try(closeRolloutFloater maxwellLLister.LightInspectorFloater) catch()
	maxwellLLister.LightInspectorFloater = newRolloutFloater "Light Lister" dialogSize.x dialogSize.y dialogPos.x dialogPos.y

	addRollout maxwellLLister.LightInspectorSetup maxwellLLister.LightInspectorFloater
	dialogUp = true
)

on closeDialogs do
(
		try(closeRolloutFloater maxwellLLister.LightInspectorFloater) catch( print "Error in LightLister" )
		dialogUp = false
)

on isChecked do
(
	dialogUp
)
)