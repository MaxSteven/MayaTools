-------------------------------------------------------------------------------------------------
--	SpeedTree .fbx importer
--
--	Use this script to import .fbx files exported from the SpeedTree Modeler to prepare
--  them for rendering with Mental Ray or VRay.
--
--	Workflow:
--		-Model a tree in the SpeedTree Modeler
--		-Export the tree as a mesh, choose fbx as the file type, and select one of the 3ds Max presets
--		-Run this script via "MAXScript->Run Script..."
--		-Go to the utilities tab and press the button on the "SpeedTree Importers" rollout that matches the preset you chose in SpeedTree
--		-Browse to the mesh you exported and import it
--		-This script will load and process the mesh to prepare it for rendering
--
--	Note: If you intend to modify this script please make a copy and modify that.  This file
--	is subject to modification or deletion during software updates.
--
--
--	*** INTERACTIVE DATA VISUALIZATION (IDV) PROPRIETARY INFORMATION ***
--
--	This software is supplied under the terms of a license agreement or
--	nondisclosure agreement with Interactive Data Visualization and may
--	not be used, copied, or disclosed except in accordance with the terms of
--	that agreement.
--
--      Copyright (c) 2003-2012 IDV, Inc.
--      All Rights Reserved.
--


-- Initialization
setCommandPanelTaskMode mode:#utility

global stFbxImporters
global maxIni = getMAXIniFile()

fn HasBlendData obj =
(
	--if map channels 3 and 4 exist, we're blending branch intersections
	if SuperClassOf obj == GeometryClass AND classOf  obj.baseObject == Editable_Mesh then
	(
		bHasBlendData = meshop.getMapSupport obj 3 AND meshop.getMapSupport obj 4
	)
	else if SuperClassOf  obj == GeometryClass AND classOf  obj.baseObject == Editable_Poly then
	(
		bHasBlendData = polyop.getMapSupport obj 3 AND polyop.getMapSupport obj 4
	)
)

fn IsLeaf mat =
(
	--this is the best indicator that we have enough data to do reflection, refraction, and translucency
	return mat.specularMap != undefined
)

fn ProcessSeasonData obj = 
(
	local bHasSeasonData = false
	if SuperClassOf obj == GeometryClass AND classOf  obj.baseObject == Editable_Mesh then
	(
		bHasSeasonData = meshop.getMapSupport obj 2
		if bHasSeasonData == true then
		(
			nNumVertices = meshop.getNumTVerts obj

			bHasSeasonData = false
			for i = 1 to nNumVertices do
			(
				pCoord = meshop.getMapVert obj 2 i
				
				if pCoord.y <= -999.0 then
				(
					bHasSeasonData = true
				)
			)
		)
	)
	
	return bHasSeasonData
)

fn CreateBlendingComposite map =
(
	--create a composite map that implements branch seam intersection blending
	local matComposite = CompositeTexture()
	
	--make two copies of the base texture
	matComposite.mapList[1] = copy map;
	matComposite.mapList[2] = copy map;
	
	--the blended tex coords are in map channel 4 (these are computed by SpeedTree)
	matComposite.mapList[2].coordinates.mapChannel = 4;
	
	
	--here we get the blend weight from the 'red' part of map channel 3 (SpeedTree computes this and stores it here in the .fbx file)
	matComposite.mask[2] = Output();
	matComposite.mask[2].map1 = Vertex_Color();
	matComposite.mask[2].map1.map = 3;
	matComposite.mask[2].map1.subid = 1;
	matComposite.mask[2].output.invert = true
	matComposite.mask[2].output.clamp = true
	
	return matComposite
)

fn CreateBlendingDetailComposite mapDiffuse mapDetail mapMask =
(
	--create a composite map that implements branch seam intersection blending with detail maps present
	local matComposite = CompositeTexture()
	
	--layer 1: the base map
	matComposite.mapList[1] = copy mapDiffuse;
	
	--layer 2: the base map again, this time blended (tex coords in map channel 4 as computed by SpeedTree)
	matComposite.mapList[2] = copy mapDiffuse;
	matComposite.mapList[2].coordinates.mapChannel = 4;
	matComposite.mask[2] = Output();
	matComposite.mask[2].map1 = Vertex_Color();
	--here we get the blend weight from the 'red' part of map channel 3 (SpeedTree computes this and stores it here in the .fbx file)
	matComposite.mask[2].map1.map = 3;
	matComposite.mask[2].map1.subid = 1;
	matComposite.mask[2].output.invert = true
	matComposite.mask[2].output.clamp = true
	
	--layer 3: the detail map
	matComposite.mapList[3] = copy mapDetail;
	matComposite.mapList[3].coordinates.mapChannel = 2
	--blend layer 3 based on alpha of detail texture
	matComposite.mask[3] = copy mapMask;
	matComposite.mask[3].monoOutput = 1
	matComposite.mask[3].RGBOutput = 1

	--layer 4: the detail map again, this time blended (tex coords in map channel 5 as computed by SpeedTree)
	matComposite.mapList[4] = copy mapDetail;
	matComposite.mapList[4].coordinates.mapChannel = 5
	--blend based on detail texture alpha and the weight from map channel 3
	matComposite.mask[4] = RGB_Multiply();
	matComposite.mask[4].map1 = copy mapMask
	matComposite.mask[4].map1.monoOutput = 1
	matComposite.mask[4].map1.RGBOutput = 1
	matComposite.mask[4].map1.coordinates.mapChannel = 5
	matComposite.mask[4].map2 = Output();
	matComposite.mask[4].map2.map1 = Vertex_Color();
	matComposite.mask[4].map2.map1.map = 3;
	matComposite.mask[4].map2.map1.subid = 1;
	matComposite.mask[4].map2.output.invert = true
	matComposite.mask[4].map2.output.clamp = true
	
	return matComposite
)

fn FindAlphaFromMap map =
(
	--get the best alpha map available (separate image if it exists, otherwise use the alpha channel of the diffuse map)
	local mapAlpha = undefined
	local mapBitmapSource = undefined
	
	if (classOf map == CompositeTexture) then
	(
		mapBitmapSource = map.mapList[1]
	)
	else if (classOf map == BitmapTexture) then
	(
		mapBitmapSource = map
	)
	
	if (mapBitmapSource != undefined) then
	(
		mapBitmapSource.alphasource = 2
		local strFilename = mapBitmapSource.filename
		
		if (strFilename != undefined) then
		(
			local alphaFile = (getFilenamePath strFilename) + (getFilenameFile strFilename) + "_Alpha" + (getFilenameType strFilename)
			format alphaFile
			format "\n"
			if doesfileexist alphaFile then
			(
				--use the separate alpha if the user requested it
				mapAlpha = copy mapBitmapSource;
				mapAlpha.filename = alphaFile;
			)
			else
			(
				--otherwise, use the alpha from the diffuse map
				mapAlpha = copy mapBitmapSource;
				mapAlpha.monoOutput = 1
				mapAlpha.RGBOutput = 1
				mapAlpha.alphasource = 0
			)
		)
	)
	
	return mapAlpha
)

fn ProcessMaterialForMentalRay obj mat bSeason =
(
	--get a new mental ray arch & design mtl to work with
	local matMentalRay = Arch___Design__mi()
	matMentalRay.name = mat.name
	
	bHasBlendData = HasBlendData obj
	bIsLeaf = IsLeaf mat
	
	--------------------------------------
	--diffuse map
	try
	(
		local mapDiffuse
		local mapShow = undefined
		if (classOf mat.diffuseMap == CompositeTexturemap) then
		(
			if (bHasBlendData == true and bIsLeaf == false) then
			(
				--detail maps and blended branch intersections are both present
				mapDiffuse = CreateBlendingDetailComposite mat.diffuseMap.mapList[1] mat.diffuseMap.mapList[2] mat.diffuseMap.mapList[2]
			)
			else
			(
				if (bSeason == true and bIsLeaf == true) then
				(
					--make the detail layer use the diffuse uv
					mapDiffuse = mat.diffuseMap
					mapDiffuse.mapList[2].coordinates.mapChannel = 1;
					
					--make a mask that uses the new, processed detail u
					mapDiffuse.mask[2] = Output();
					mapDiffuse.mask[2].map1 = Vertex_Color();
					--here we get the blend weight from the 'red' part of map channel 2 (processed by ProcessSeasonData)
					mapDiffuse.mask[2].map1.map = 2;
					mapDiffuse.mask[2].map1.subid = 1;
				)
				else
				(
					--detail maps are present (diffuse is fine as it is in the .fbx file)
					mapDiffuse = mat.diffuseMap
				)
			)
			mapShow = mapDiffuse.mapList[1]
		)
		else
		(
			if (bHasBlendData == true and bIsLeaf == false) then
			(
				--branch intersection blending data is present
				mapDiffuse = CreateBlendingComposite mat.diffuseMap
				mapShow = mapDiffuse.mapList[1]
			)
			else
			(
				--this is the vanilla case: no branch intersection blending and no detail maps
				mapDiffuse = mat.diffuseMap
				mapShow = mapDiffuse
			)
		)
		
		--make the actual diffuse map from the computed map, vertex color, and scalar amount
		matMentalRay.mapM0 = RGB_Multiply()
		matMentalRay.mapM0.map1 = mapDiffuse
		matMentalRay.mapM0.map2 = RGB_Multiply()
		matMentalRay.mapM0.map2.map1 = Vertex_Color()
		matMentalRay.mapM0.map2.map2 = Output()
		matMentalRay.mapM0.map2.map2.output.output_amount = stFbxImporters.spDiffuseScalar.value
		showTextureMap matMentalRay mapShow on
	)
	catch ( )
	
	--------------------------------------
	--bump map
	try
	(
		local mapBump
		if (classOf mat.diffuseMap == CompositeTexturemap) then
		(
			if (bHasBlendData and bIsLeaf == false) then
			(
				--detail maps and blended branch intersections are both present
				local mapHeight = FindAlphaFromMap mat.bumpMap.normal_map.mapList[1]
				local mapDetailHeight = FindAlphaFromMap mat.bumpMap.normal_map.mapList[2]
				mapBump = CreateBlendingDetailComposite mapHeight mapDetailHeight mat.diffuseMap.mapList[2]
			)
			else
			(
				--detail maps are present (need to fix up the data in the .fbx file to use bumps and get the mask from the diffuse layer to match blending)
				mapBump = mat.bumpMap.normal_map
				mapBump.mapList[1] = FindAlphaFromMap mapBump.mapList[1]
				mapBump.mapList[2] = FindAlphaFromMap mapBump.mapList[2]

				if (bSeason == true and bIsLeaf == true) then
				(
					mapBump.mapList[2].coordinates.mapChannel = 1;
					--make a mask that uses the new, processed detail u
					mapBump.mask[2] = Output();
					mapBump.mask[2].map1 = Vertex_Color();
					--here we get the blend weight from the 'red' part of map channel 2 (processed by ProcessSeasonData)
					mapBump.mask[2].map1.map = 2;
					mapBump.mask[2].map1.subid = 1;
				)
				else
				(
					mapBump.mask[2] = FindAlphaFromMap(copy mapDiffuse.mapList[2])
				)
			)
		)
		else
		(
			if (bHasBlendData and bIsLeaf == false) then
			(
				--branch intersection blending data is present
				local mapHeight = FindAlphaFromMap mat.bumpMap.normal_map
				mapBump = CreateBlendingComposite mapHeight
			)
			else
			(
				--this is the vanilla case: no branch intersection blending and no detail maps
				mapBump = FindAlphaFromMap mat.bumpMap.normal_map
			)
		)
		
		--make the actual bump map and assign the bump value
		matMentalRay.bump_map = mapBump
		if (bIsLeaf) then
			matMentalRay.bump_map_amt = 2.0 * matVRay.texmap_bump_multiplier * 0.5
		else
			matMentalRay.bump_map_amt = 2.0 * stFbxImporters.spBumpScalar.value
	)
	catch ( )
	
	--------------------------------------
	--opacity map
	try
	(
		local mapOpacity = FindAlphaFromMap mat.diffuseMap
		if (mapOpacity != undefined) then
		(
			matMentalRay.cutout_map = mapOpacity;
		)
	)
	catch ( )
	
	--------------------------------------
	--specular, refraction, and translucency for leaves
	try
	(
		if (bIsLeaf) then
		(
			--we've got a leaf, most likely -- proceeding like we do
			
			--use the assigned specular map
			matMentalRay.refl_color_map = copy mat.specularMap;
			matMentalRay.refl_color_map.output.output_amount = stFbxImporters.spSpecularScalar.value
			
			--use the diffuse for refraction
			matMentalRay.refr_color_map = copy matMentalRay.mapM0

			--manufacture a transluceny map that matches what SpeedTree does in the Modeler (we're mimicking the diffuse * color * 3.0 approach from the Modeler)
			local mapTransmission = FindAlphaFromMap mat.specularMap
			matMentalRay.refr_transw_map = copy mapTransmission
			matMentalRay.refr_transw_map.output.rgb_level = 3.0 * stFbxImporters.spTranslucencyScalar.value
			matMentalRay.refr_trans_on = true
			matMentalRay.refr_transc = mat.selfIllumColor
			
			--set parameters
			matMentalRay.refl_weight = 0.1
			matMentalRay.refl_gloss = mat.glossiness / 100
			matMentalRay.refl_hlonly = true
			
			matMentalRay.opts_backface_cull = false
			matMentalRay.opts_1sided = on
			matMentalRay.refr_weight = 0.1
			matMentalRay.refr_interp = on
		)
		else
		(
			matMentalRay.refl_color = color 0 0 0
		)
	)
	catch ( )
	
	return matMentalRay
)

fn ProcessMaterialForVRay obj mat bSeason =
(
	--get a new vray mtl to work with
	local matVRay = VRayMtl()
	matVRay.name = mat.name	

	bHasBlendData = HasBlendData obj
	bIsLeaf = IsLeaf mat
		
	--------------------------------------
	--diffuse map
	try
	(
		local mapDiffuse
		local mapShow = undefined
		if (classOf mat.diffuseMap == CompositeTexturemap) then
		(
			if (bHasBlendData and bIsLeaf == false) then
			(
				--detail maps and blended branch intersections are both present
				mapDiffuse = CreateBlendingDetailComposite mat.diffuseMap.mapList[1] mat.diffuseMap.mapList[2] mat.diffuseMap.mapList[2]
			)
			else
			(
				if (bSeason == true and bIsLeaf == true) then
				(
					--make the detail layer use the diffuse uv
					mapDiffuse = mat.diffuseMap
					mapDiffuse.mapList[2].coordinates.mapChannel = 1;
					
					--make a mask that uses the new, processed detail u
					mapDiffuse.mask[2] = Output();
					mapDiffuse.mask[2].map1 = Vertex_Color();
					--here we get the blend weight from the 'red' part of map channel 2 (processed by ProcessSeasonData)
					mapDiffuse.mask[2].map1.map = 2;
					mapDiffuse.mask[2].map1.subid = 1;
				)
				else
				(
					--detail maps are present (diffuse is fine as it is in the .fbx file)
					mapDiffuse = mat.diffuseMap
				)
			)
			mapShow = mapDiffuse.mapList[1]
		)
		else
		(
			if (bHasBlendData and bIsLeaf == false) then
			(
				--branch intersection blending data is present
				mapDiffuse = CreateBlendingComposite mat.diffuseMap
				mapShow = mapDiffuse.mapList[1]
			)
			else
			(
				--this is the vanilla case: no branch intersection blending and no detail maps
				mapDiffuse = mat.diffuseMap
				mapShow = mat.diffuseMap
			)
		)
		
		--make the actual diffuse map from the computed map, vertex color, and scalar amount
		matVRay.texmap_diffuse = RGB_Multiply()
		matVRay.texmap_diffuse.map1 = mapDiffuse
		matVRay.texmap_diffuse.map2 = RGB_Multiply()
		matVRay.texmap_diffuse.map2.map1 = Vertex_Color()
		matVRay.texmap_diffuse.map2.map2 = Output()
		matVRay.texmap_diffuse.map2.map2.output.output_amount = stFbxImporters.spDiffuseScalar.value
		showTextureMap matVRay mapShow on
	)
	catch ( )
	
	--------------------------------------
	--bump map
	try
	(
		local mapBump
		if (classOf mat.diffuseMap == CompositeTexturemap) then
		(
			if (bHasBlendData and bIsLeaf == false) then
			(
				--detail maps and blended branch intersections are both present
				local mapHeight = FindAlphaFromMap mat.bumpMap.normal_map.mapList[1]
				local mapDetailHeight = FindAlphaFromMap mat.bumpMap.normal_map.mapList[2]
				mapBump = CreateBlendingDetailComposite mapHeight mapDetailHeight mat.diffuseMap.mapList[2]
			)
			else
			(
				--detail maps are present (need to fix up the data in the .fbx file to use bumps and get the mask from the diffuse layer to match blending)
				mapBump = mat.bumpMap.normal_map
				mapBump.mapList[1] = FindAlphaFromMap mapBump.mapList[1]
				mapBump.mapList[2] = FindAlphaFromMap mapBump.mapList[2]
				
				if (bSeason == true and bIsLeaf == true) then
				(
					mapBump.mapList[2].coordinates.mapChannel = 1;
					mapBump.mask[2] = Output();
					mapBump.mask[2].map1 = Vertex_Color();
					--here we get the blend weight from the 'red' part of map channel 2 (processed by ProcessSeasonData)
					mapBump.mask[2].map1.map = 2;
					mapBump.mask[2].map1.subid = 1;
				)
				else
				(
					mapBump.mask[2] = FindAlphaFromMap(copy mapDiffuse.mapList[2])
				)
			)
		)
		else
		(
			if (bHasBlendData and bIsLeaf == false) then
			(
				--branch intersection blending data is present
				local mapHeight = FindAlphaFromMap mat.bumpMap.normal_map
				mapBump = CreateBlendingComposite mapHeight
			)
			else
			(
				--this is the vanilla case: no branch intersection blending and no detail maps
				mapBump = FindAlphaFromMap mat.bumpMap.normal_map
			)
		)
		
		--make the actual bump map and assign the bump value
		matVRay.texmap_bump = mapBump
		if (bIsLeaf) then
			matVRay.texmap_bump_multiplier = matVRay.texmap_bump_multiplier * 0.5
		else
			matVRay.texmap_bump_multiplier = 200 * stFbxImporters.spBumpScalar.value
	)
	catch ( )
	
	--------------------------------------
	--opacity map
	try
	(
		local mapOpacity = FindAlphaFromMap mat.diffuseMap
		if (mapOpacity != undefined) then
		(
			matVRay.texmap_opacity = mapOpacity;
			matVRay.texmap_opacity.filtering = 2 --alpha filtering disabled for vray performance gain
		)
	)
	catch ( )

	--------------------------------------
	--specular, refraction, and translucency for leaves
	try
	(
		if (bIsLeaf) then
		(
			--we've got a leaf, most likely -- proceeding like we do
			
			--we need to manufacture a reasonable specular map for the vray system (it's a brighter version of the diffuse with the mask applied)
			matVRay.texmap_reflection = RGB_Multiply()
			matVRay.texmap_reflection.map1 = RGB_Multiply()
			matVRay.texmap_reflection.map1.map1 = copy matVRay.texmap_diffuse.map1
			matVRay.texmap_reflection.map1.map2 = mat.specularMap
			
			matVRay.texmap_reflection.map2 = Output()
			matVRay.texmap_reflection.map2.output.output_amount = 3.0 * stFbxImporters.spSpecularScalar.value
			
			--use diffuse for refraction
			matVRay.texmap_refraction = copy matVRay.texmap_diffuse
			matVRay.refraction_affectShadows = true
			
			--manufacture a transluceny map that matches what SpeedTree does in the Modeler (we're mimicking the diffuse * color * 3.0 approach from the Modeler)
			local mapTransmission = FindAlphaFromMap mat.specularMap
			matVRay.texmap_translucent = RGB_Multiply()
			matVRay.texmap_translucent.map1 = RGB_Multiply()
			matVRay.texmap_translucent.map1.map1 = copy matVRay.texmap_diffuse
			matVRay.texmap_translucent.map1.map2 = copy mapTransmission
			matVRay.texmap_translucent.map1.map2.output.rgb_offset = 0.25 --the default of zero is typically too harsh
			matVRay.texmap_translucent.map2 = VRayColor()
			matVRay.texmap_translucent.map2.color = mat.selfIllumColor
			matVRay.texmap_translucent.map2.rgb_multiplier = 3.0 * stFbxImporters.spTranslucencyScalar.value
			
			--set parameters
			matVRay.reflection_glossiness = mat.glossiness / 100
			matVRay.reflection_fresnel = true
			matVRay.reflection_lockIOR = off
			matVRay.reflection_ior = 2.5
			matVRay.translucency_on = 3
			matVRay.translucency_color = color 0 0 0
		)
	)
	catch ( )
	
	return matVRay
)

fn ProcessMaterialForBasic obj mat bSeason =
(
	--get a new standard mtl to work with
	local matStandard = Standardmaterial()
	matStandard.name = mat.name	

	bHasBlendData = HasBlendData obj
	bIsLeaf = IsLeaf mat
	
	--------------------------------------
	--diffuse map
	try
	(
		local mapDiffuse
		local mapShow = undefined
		if (classOf mat.diffuseMap == CompositeTexturemap) then
		(
			if (bHasBlendData and bIsLeaf == false) then
			(
				--detail maps and blended branch intersections are both present
				mapDiffuse = CreateBlendingDetailComposite mat.diffuseMap.mapList[1] mat.diffuseMap.mapList[2] mat.diffuseMap.mapList[2]
			)
			else
			(
				if (bSeason == true and bIsLeaf == true) then
				(
					--make the detail layer use the diffuse uv
					mapDiffuse = mat.diffuseMap
					mapDiffuse.mapList[2].coordinates.mapChannel = 1;
					
					--make a mask that uses the new, processed detail u
					mapDiffuse.mask[2] = Output();
					mapDiffuse.mask[2].map1 = Vertex_Color();
					--here we get the blend weight from the 'red' part of map channel 2 (processed by ProcessSeasonData)
					mapDiffuse.mask[2].map1.map = 2;
					mapDiffuse.mask[2].map1.subid = 1;
				)
				else
				(
					--detail maps are present (diffuse is fine as it is in the .fbx file)
					mapDiffuse = mat.diffuseMap
				)
				
			)
			mapShow = mapDiffuse.mapList[1]
		)
		else
		(
			if (bHasBlendData and bIsLeaf == false) then
			(
				--branch intersection blending data is present
				mapDiffuse = CreateBlendingComposite mat.diffuseMap
				mapShow = mapDiffuse.mapList[1]
			)
			else
			(
				--this is the vanilla case: no branch intersection blending and no detail maps
				mapDiffuse = mat.diffuseMap
				mapShow = mapDiffuse
			)
		)
		
		--make the actual diffuse map from the computed map, vertex color, and scalar amount
		matStandard.diffuseMap = RGB_Multiply()
		matStandard.diffuseMap.map1 = mapDiffuse
		matStandard.diffuseMap.map2 = RGB_Multiply()
		matStandard.diffuseMap.map2.map1 = Vertex_Color()
		matStandard.diffuseMap.map2.map2 = Output()
		matStandard.diffuseMap.map2.map2.output.output_amount = stFbxImporters.spDiffuseScalar.value
		showTexturemap matStandard mapShow on
	)
	catch ( )
	
	--------------------------------------
	--bump map
	try
	(
		local mapBump
		if (classOf mat.diffuseMap == CompositeTexturemap) then
		(
			if (bHasBlendData and bIsLeaf == false) then
			(
				--detail maps and blended branch intersections are both present
				local mapHeight = FindAlphaFromMap mat.bumpMap.normal_map.mapList[1]
				local mapDetailHeight = FindAlphaFromMap mat.bumpMap.normal_map.mapList[2]
				mapBump = CreateBlendingDetailComposite mapHeight mapDetailHeight mat.diffuseMap.mapList[2]
			)
			else
			(
				--detail maps are present (need to fix up the data in the .fbx file to use bumps and get the mask from the diffuse layer to match blending)
				mapBump = mat.bumpMap.normal_map
				mapBump.mapList[1] = FindAlphaFromMap mapBump.mapList[1]
				mapBump.mapList[2] = FindAlphaFromMap mapBump.mapList[2]
				
				if (bSeason == true and bIsLeaf == true) then
				(
					mapBump.mapList[2].coordinates.mapChannel = 1;
					mapBump.mask[2] = Output();
					mapBump.mask[2].map1 = Vertex_Color();
					--here we get the blend weight from the 'red' part of map channel 2 (processed by ProcessSeasonData)
					mapBump.mask[2].map1.map = 2;
					mapBump.mask[2].map1.subid = 1;
				)
				else
				(
					mapBump.mask[2] = FindAlphaFromMap(copy mapDiffuse.mapList[2])
				)
			)
		)
		else
		(
			if (bHasBlendData and bIsLeaf == false) then
			(
				--branch intersection blending data is present
				local mapHeight = FindAlphaFromMap mat.bumpMap.normal_map
				mapBump = CreateBlendingComposite mapHeight
			)
			else
			(
				--this is the vanilla case: no branch intersection blending and no detail maps
				mapBump = FindAlphaFromMap mat.bumpMap.normal_map
			)
		)
		
		--make the actual bump map and assign the bump value
		matStandard.bumpMap = mapBump
		if (bIsLeaf) then
		(
			matStandard.bumpMapAmount = matStandard.bumpMapAmount * 0.5
		)
		else
		(
			matStandard.bumpMapAmount = 200 * stFbxImporters.spBumpScalar.value
		)
	)
	catch ( )

	--------------------------------------
	--opacity map
	try
	(
		local mapOpacity = FindAlphaFromMap mat.diffuseMap
		if (mapOpacity != undefined) then
		(
			matStandard.opacityMap = mapOpacity
		)
	)
	catch ( )
	
	--------------------------------------
	--specular, refraction, and translucency for leaves
	try
	(
		if (bIsLeaf) then
		(
			--just use what .fbx came in with
			matStandard.specularMap = mat.specularMap
			matStandard.glossiness = mat.glossiness
			matStandard.specularLevel = mat.specularLevel
		)
	)
	catch ( )
		
	return matStandard
)

fn ProcessObjectForMentalRay obj =
(
	bSeason = ProcessSeasonData obj
	--swap the material the .fbx importer made for a mental ray material that closely matches SpeedTree
	--includes detail maps, branch intersection blending, and translucency
	local mat = obj.material
	
	if (classof mat == MultiMaterial) then
	(
		for i = 1 to mat.numsubs do
		(
			if (classof mat.materialList[i] == StandardMaterial) then
			(
				mat.materialList[i] = ProcessMaterialForMentalRay obj mat.materialList[i] bSeason
			)
		)
	)
	else if (classof mat == StandardMaterial) then
	(
		obj.material = ProcessMaterialForMentalRay obj mat bSeason
	)
)

fn ProcessSelectedObjectsForMentalRay =
(
	--any object selected now is new so it needs to be processed for mental ray
	with redraw off
	for obj in selection do
	(
		if (classOf obj != BoneGeometry AND classOf obj != Dummy AND classOf obj != NURBSCurveshape ) then
		(
			ProcessObjectForMentalRay obj
		)
	)
)

fn ProcessObjectForVRay obj =
(
	bSeason = ProcessSeasonData obj
	--swap the material the .fbx importer made for a v-ray material that closely matches SpeedTree
	--includes detail maps, branch intersection blending, and translucency
	local mat = obj.material
	
	if (classof mat == MultiMaterial) then
	(
		for i = 1 to mat.numsubs do
		(
			if (classof mat.materialList[i] == StandardMaterial) then
			(
				mat.materialList[i] = ProcessMaterialForVRay obj mat.materialList[i] bSeason
			)
		)
	)
	else if (classof mat == StandardMaterial) then
	(
		obj.material = ProcessMaterialForVRay obj mat bSeason
	)
)

fn ProcessSelectedObjectsForVRay =
(
	--any object selected now is new so it needs to be processed for v-ray
	with redraw off
	for obj in selection do
	(
		if (classOf obj != BoneGeometry AND classOf obj != Dummy AND classOf obj != NURBSCurveshape ) then
		(
			ProcessObjectForVRay obj
		)
	)
)

fn ProcessObjectForBasic obj =
(
	bSeason = ProcessSeasonData obj
	--swap the material the .fbx importer made for a new material that closely matches SpeedTree
	--includes detail maps and branch intersection blending
	local mat = obj.material
	
	if (classof mat == MultiMaterial) then
	(
		for i = 1 to mat.numsubs do
		(
			if (classof mat.materialList[i] == StandardMaterial) then
			(
				mat.materialList[i] = ProcessMaterialForBasic obj mat.materialList[i] bSeason
			)
		)
	)
	else if (classof mat == StandardMaterial) then
	(
		obj.material = ProcessMaterialForBasic obj mat bSeason
	)
)

fn ProcessSelectedObjectsForBasic =
(
	--any object selected now is new so it needs to be processed to get closer to what SpeedTree does natively
	with redraw off
	for obj in selection do
	(
		if (classOf obj != BoneGeometry AND classOf obj != Dummy AND classOf obj != NURBSCurveshape ) then
		(
			ProcessObjectForBasic obj
		)
	)
)


utility stFbxImporters "SpeedTree Importers"
(
	--this is the rollout
	group "Multipliers"
	(
		--these options apply to all three importers
		spinner spBumpScalar "Bump:" range:[0.0,100.0,1.0] type:#float --fieldwidth:30 align:#left offset:[14,0]
		spinner spSpecularScalar "Specular:" range:[0.0,100.0,1.0] type:#float --fieldwidth:30 align:#left offset:[14,0]
		spinner spTranslucencyScalar "Translucency:" range:[0.0,10.0,1.0] type:#float --fieldwidth:30 align:#left offset:[14,0]
		spinner spDiffuseScalar "Diffuse:" range:[0.0,100.0,1.0] type:#float --fieldwidth:30 align:#left offset:[14,0]
	)
	
	--import buttons
	button btnImportFBXMentalRay "Import .fbx for Mental Ray" width:144 align:#center
	button btnImportFBXVRay "Import .fbx for V-Ray" width:144 align:#center
	button btnImportFBXBasic "Import basic .fbx" width:144 align:#center
	
	on btnImportFBXMentalRay pressed do
	(
		--import a .fbx made by SpeedTree with the standard .fbx importer and then process it for mental ray
		strSpeedTreeFBX = getOpenFilename caption:"Import Mesh from the SpeedTree Modeler" types:"SpeedTree FBX (*.fbx)|*.fbx|All Files (*.*)|*.*" historyCategory:"SpeedTreeFBX"
		
		if (strSpeedTreeFBX != undefined) then
		(
			importFile strSpeedTreeFBX --#noprompt
			
			ProcessSelectedObjectsForMentalRay()
		)
	)
	
	on btnImportFBXVRay pressed do
	(
		--import a .fbx made by SpeedTree with the standard .fbx importer and then process it for v-ray
		strSpeedTreeFBX = getOpenFilename caption:"Import Mesh from the SpeedTree Modeler" types:"SpeedTree FBX (*.fbx)|*.fbx|All Files (*.*)|*.*" historyCategory:"SpeedTreeFBX"
		
		if (strSpeedTreeFBX != undefined) then
		(
			importFile strSpeedTreeFBX --#noprompt
			
			ProcessSelectedObjectsForVRay()
		)
	)
	
	on btnImportFBXBasic pressed do
	(
		--import a .fbx made by SpeedTree with the standard .fbx importer and then process it 
		strSpeedTreeFBX = getOpenFilename caption:"Import Mesh from the SpeedTree Modeler" types:"SpeedTree FBX (*.fbx)|*.fbx|All Files (*.*)|*.*" historyCategory:"SpeedTreeFBX"
		
		if (strSpeedTreeFBX != undefined) then
		(
			importFile strSpeedTreeFBX --#noprompt
			
			ProcessSelectedObjectsForBasic()
		)
	)

	on stFbxImporters open do
	(
		--when the rollout opens, load the stored values of each control (makes the options 'sticky')
		for aControl in stFbxImporters.controls do
		(
			 try
			 (
				 case classof aControl of
				 (
					SpinnerControl: aControl.value = (readValue ((getIniSetting maxIni "SpeedTreeImporter" aControl.name) as stringStream))
				 )
			 )
			 catch()
		)	 
	)
	
	on stFbxImporters close do
	(
		--when the rollout closes, save the stored values of each control (makes the options 'sticky')
		for aControl in stFbxImporters.controls do
		(
			 try
			 (
				 case classof aControl of
				 (
					SpinnerControl: setIniSetting maxIni "SpeedTreeImporter" aControl.name (aControl.value as string)
				 )
			 )
			 catch()
		)	 
	)	
)	

-- rollout maintenance
addRollout stFbxImporters

