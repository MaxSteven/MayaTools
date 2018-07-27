(
-- to do: light and shader subdivs heuristics based on glossiness/area

	global Arnie4Vray3Roll
	try (destroyDialog Arnie4Vray3Roll) catch()

	local lf=filein (MAX_TOOLS_ROOT + "/include/lelesFnsStructFile_v1.30.ms")
	local cr,wasRR
	local minRPP=maxRPP=lightsMinRPP=lightsMaxRPP=minShCPP=maxShCPP=minLtCPP=maxLtCPP=SSSRPP=GIRPP=minSSSRPP=maxSSSRPP=minGIRPP=maxGIRPP=0
	local dlSubDivs=GISubDivs=noiseBits=minSubdivs=maxSubdivs=globalMult=reflSubDivs=refrSubDivs=SSSSubDivs=subdivsResult=0
	local gBounces=2
	local sBounces=15
	local aAmt = 0.75
	global theWholeNodes=#()
	global numLights=0
	local oldRegion=#()

	fn getNumLights =
	(
		numLights=0
		for i=1 to lights.count where (classOf lights[i]!=targetObject)  do
		(
			try
				(
					if lights[i].on==true do numLights+=1
				)
			catch()
			try
				(
					if lights[i].enabled==true do numLights+=1
				)
			catch()
		)
	)

	fn changeSubdivs theNodes reflSubDivs refrSubDivs dlSubDivs GISubDivs noiseBits SSSSubDivs minSubdivs maxSubdivs gBounces sBounces globalMult aAmt =
	(
		global A4V3Node=undefined
		for n=1 to theNodes.count do
			(
				A4V3Node=theNodes[n]
				if (superClassOf A4V3Node == material) then
				(
-- 					print A4V3Node
					for theProp in (getPropNames A4V3Node) do
						(

-- 							generic changes
							if  (matchPattern  (theProp as string ) pattern:"*cutoff*")!=False do
								(
									execute ("A4V3Node."+theProp +"=1.0/(2^Arnie4Vray3Roll.spn10.value)")
-- 									print ("Set property " + theProp as string + " in object " + A4V3Node as string + " to 0.000" )
								)
							if  (matchPattern  (theProp as string ) pattern:"*brdf_fixDarkEdges*")!=False do
								(
									execute ("A4V3Node."+theProp +"=True")
-- 									print ("Set property " + theProp as string + " in object " + A4V3Node as string + " to Enabled")
								)

-- 								standard shaders
							if  (matchPattern  (theProp as string ) pattern:"*refl*subdivs*")!=False do									-- REFLECTION subdivs
								(
									execute("A4V3Node."+theProp +"="+(reflSubDivs as string))
-- 									print ("Set property " + theProp as string + " in object " + A4V3Node as string + " to "+reflSubDivs as string+ " subdivs" )
								)
							if  (matchPattern  (theProp as string ) pattern:"*refr*subdivs*")!=False do									-- REFRACTION subdivs
								(
									execute("A4V3Node."+theProp +"="+(refrSubDivs as string))
-- 									print ("Set property " + theProp as string + " in object " + A4V3Node as string + " to "+reflSubDivs as string+ " subdivs" )
								)
							if  (matchPattern  (theProp as string ) pattern:"*refl*maxDepth*")!=False do								--REFLECTION gBounces/sBounces
								(
									if (A4V3Node.reflection_glossiness < 1 or (A4V3Node.texmap_reflectionGlossiness != undefined and A4V3Node.texmap_reflectionGlossiness_on) ) then
										(
											execute ("A4V3Node."+theProp +"=" + gBounces as string)
-- 		 									print ("Set property " + theProp as string + " in object " + A4V3Node as string + " to 2")
										)
									else
										(
											execute ("A4V3Node."+theProp +"=" + sBounces as string)
		-- 									print ("Set property " + theProp as string + " in object " + A4V3Node as string + " to 2")
										)
								)
							if  (matchPattern  (theProp as string ) pattern:"*refr*maxDepth*")!=False do								--REFRACTION gBounces/sBounces
								(
									if (A4V3Node.refraction_glossiness < 1 or (A4V3Node.texmap_refractionGlossiness != undefined and A4V3Node.texmap_refractionGlossiness_on) ) then
										(
											execute ("A4V3Node."+theProp +"=" + gBounces as string)
		-- 									print ("Set property " + theProp as string + " in object " + A4V3Node as string + " to 2")
										)
									else
										(
											execute ("A4V3Node."+theProp +"=" + sBounces as string)
		-- 									print ("Set property " + theProp as string + " in object " + A4V3Node as string + " to 2")
										)
								)
-- 							SSS types
							if  (matchPattern  (theProp as string ) pattern:"*multiple_scattering*")!=False do
								(
									execute ("A4V3Node."+theProp +"=2")
-- 									print ("Set property " + theProp as string + " in object " + A4V3Node as string + " to Raytraced")
								)
							if  (matchPattern  (theProp as string ) pattern:"*scatter*subdivs*")!=False do
								(
									execute ("A4V3Node."+theProp +"="+ SSSSubdivs as string)
-- 									print ("Set property " + theProp as string + " in object " + A4V3Node as string + " to Raytraced")
								)
							if  (matchPattern  (theProp as string ) pattern:"*raytraced*subdivs*")!=False do
								(
									execute ("A4V3Node."+theProp +"="+ SSSSubdivs as string)
-- 									print ("Set property " + theProp as string + " in object " + A4V3Node as string + " to Raytraced")
								)
						)
				)
				else
				(
					sceneBBox=$objects.max-$objects.min
					sceneLinearSize=pow (sceneBBox[1]*sceneBBox[2]*sceneBBox[3]) (1.0/3)
					Case (classOf A4V3Node) of
					(
						VRayLight :
						(
-- 							if (A4V3Node.type==0 or A4V3Node.type==2 ) do
-- 							(
-- 								lightLinearSize=pow (A4V3Node.size0*A4V3Node.size1) (1.0/2)
-- 								lightNormalSize = lightLinearSize/sceneLinearSize
-- 								print lightNormalSize
-- 								subdivsResult=dlSubDivs * lightNormalSize * 24 -- ? wtf?!?!?
--
-- 							)
						)
						VRayIES : ()
						VRaySun : ()
					)
					for theProp in (getPropNames A4V3Node) do
						(
							if  (matchPattern  (theProp as string ) pattern:"*subdivs*")!=False do
								(
									if classof A4V3Node==VRayLight do
									(
										if  A4V3Node.type==1 then execute ("$"+A4V3Node.name+"."+theProp +"="+GISubDivs as string)
										else
										(
											if subdivsResult!=0 then
											(
												execute ("$"+A4V3Node.name+"."+theProp +"="+subdivsResult as string)
											)
											else
											(
												execute ("$"+A4V3Node.name+"."+theProp +"="+dlSubDivs as string)
											)
										)
									)
-- 									print ("Set Property " + theProp as string + " in object " + A4V3Node as string + " to " + dlSubDivs as string + " subdivs")
								)
							if  (matchPattern  (theProp as string ) pattern:"*cutoff*")!=False do
								(
									execute ("$"+A4V3Node.name+"."+theProp +"=1.0/(2^Arnie4Vray3Roll.spn10.value)")
-- 									print ("Set Property " + theProp as string + " in object " + A4V3Node as string + " to 0.000" )
								)
						)
				)
			)
	)

	fn setRenderSettings =
	(
		local rsa=#()
		rsa = lf.parseEnvironmentSettings True True True True True True True True
		print "Storing VRay FB data"
		wasRR=vrayVFBGetRegionEnabled()
		oldRegion=vrayVFBGetRegion()
-- 		vfbControl #historySelect 1
		vfbControl #historysave
-- 		renderers.current.closeVFB()
-- 		lf.storeVRayFBData()
-- 		print rsa
		lf.resetVray()
		lf.restoreEnvironmentSettings rsa
		local rdWasOpen=lf.closeRendDiag()
-- 		lf.reStoreVRayFBData()
		print "ReStoring VRay FB data"
		vfbControl #history true
		vfbControl #historySelect 0
		vfbControl #historyLoad
		vfbControl #historySelect 0
		vfbControl #historyRemove
		vrayVFBSetRegionEnabled wasRR
		vrayVFBSetRegion oldRegion[1] oldRegion[2] oldRegion[3] oldRegion[4]
		cr=renderers.current
		cr.showLastVFB()
		cr.mcgi_subdivs=GISubDivs
		cr.filter_on=False
		cr.dmc_balanceSubdivs=false
		cr.system_embree_on = true
		cr.system_raycaster_memLimit = 0
		cr.system_instancedObjects=0
		cr.mc_earlyTermination_threshold=1.0/(2^noiseBits)
		cr.imageSampler_type=1
		cr.twoLevel_baseSubdivs=minSubdivs
		cr.twoLevel_fineSubdivs=maxSubdivs
		cr.twoLevel_showSamples=False
		cr.twoLevel_useMCSamplerThresh=False
		cr.twoLevel_threshold=0.1
		cr.dmc_timeDependent=True
		cr.options_ray_bias=0.0001
		cr.options_probabilisticLights=False
		cr.options_maxRayIntensity_on=False
		cr.mc_subdivs_mult=globalMult
		cr.dmc_earlyTermination_amount=aAmt
		lf.openRendDiag rdWasOpen
	)

	rollout Arnie4Vray3Roll "Arnie4Vray3 V 1.20R" width:424 height:784
	(
		local Arnie4Vray3Roll
		GroupBox grp1 "Settings:" pos:[8,8] width:408 height:344

		GroupBox grp2 "Standard Shaders:" pos:[16,24] width:392 height:72

		label lbl1 "Glossy Refl. Subdivs:" pos:[24,48] width:128 height:16
		spinner spn1 "" pos:[152,48] width:56 height:16 range:[1,1024,16] type:#integer scale:1
		label lbl2 "Glossy Refr. Subdivs:" pos:[216,48] width:128 height:16
		spinner spn2 "" pos:[344,48] width:56 height:16 range:[1,1024,16] type:#integer scale:1
		label lbl3 "Glossy Bounces:" pos:[24,72] width:128 height:16
		spinner spn3 "" pos:[152,72] width:56 height:16 range:[1,1024,3] type:#integer scale:1
		label lbl4 "Straight Bounces:" pos:[216,72] width:128 height:16
		spinner spn4 "" pos:[344,72] width:56 height:16 range:[1,1024,15] type:#integer scale:1

		GroupBox grp3 "SSS/Skin Shaders:" pos:[16,104] width:392 height:48

		label lbl5 "SSS Subdivs:" pos:[24,128] width:128 height:16
		spinner spn5 "" pos:[152,128] width:56 height:16 range:[1,1024,12] type:#integer scale:1

		GroupBox grp4 "Lighting:" pos:[16,160] width:392 height:48

		label lbl6 "Direct Lighting Subdivs:" pos:[24,184] width:128 height:16
		spinner spn6 "" pos:[152,184] width:56 height:16 range:[1,1024,16] type:#integer scale:1
		label lbl7 "IBL/BF GI Subdivs:" pos:[216,184] width:128 height:16
		spinner spn7 "" pos:[344,184] width:56 height:16 range:[1,1024,24] type:#integer scale:1

		GroupBox grp5 "General Sampling Behaviour:" pos:[16,216] width:392 height:72

		label lbl8 "Global Subdivs Mult:" pos:[24,240] width:128 height:16
		spinner spn8 "" pos:[152,240] width:56 height:16 range:[0,1024,1] type:#float scale:0.001
		label lbl9 "Sampling Adaptive Amt.:" pos:[216,240] width:128 height:16
		spinner spn9 "" pos:[344,240] width:56 height:16 range:[0,100,0.75] type:#float scale:0.001
		label lbl10 "Noise Sens. (Bits):" pos:[24,264] width:128 height:16
		spinner spn10 "" pos:[152,264] width:56 height:16 range:[1,32,8] type:#integer scale:1

		GroupBox grp6 "Camera Sampling Behaviour:" pos:[16,296] width:392 height:48

		label lbl11 "Min AA Subdivs:" pos:[24,320] width:128 height:16
		spinner spn11 "" pos:[152,320] width:56 height:16 range:[1,1024,2] type:#integer scale:1
 		label lbl12 "Max AA Subdivs:" pos:[216,320] width:128 height:16
		spinner spn12 "" pos:[344,320] width:56 height:16 range:[1,1024,4] type:#integer scale:1

		GroupBox grp7 "Resulting Info:" pos:[8,360] width:408 height:280

		label lbl13 "" pos:[16,376] width:392 height:256

		groupBox grp8 "Easy Presets:" pos:[8,648] width:408 height:56

		button btn1 "Rough" pos:[10,672] width:64 height:24
		button btn2 "Clean (D)" pos:[78,672] width:64 height:24
		button btn3 "2Stops" pos:[146,672] width:64 height:24
		button btn4 "Awsm" pos:[214,672] width:64 height:24
		button btn5 "StdGeo" pos:[282,672] width:64 height:24
		button btn6 "FineGeo" pos:[350,672] width:64 height:24

		groupBox grp9 "aaaaand, Action!" pos:[8,712] width:408 height:64
		button btn7 "Make Scene Changes" pos:[16,736] width:392 height:32

		fn refreshVarsVals =
		(
			reflSubDivs=spn1.value
			refrSubDivs=spn2.value
			gBounces=spn3.value
			sBounces=spn4.value

			SSSSubDivs=spn5.value

			dlSubDivs=spn6.value
			GISubDivs=spn7.value

			globalMult=spn8.value
			aAmt=spn9.value
			noiseBits=spn10.value

			minSubdivs=spn11.value
			maxSubdivs=spn12.value
		)

		fn updateInfoLabel =
		(
			getNumLights()
			refreshVarsVals()
			/*
			minRPP=maxRPP=( (reflSubDivs*globalMult)^2 ) as integer
			lightsMinRPP=lightsMaxRPP=( (dlSubDivs*globalMult)^2 ) as integer
			minShCPP=( (reflSubDivs*globalMult*minSubdivs)^2 )  as integer
			maxShCPP=( (reflSubDivs*globalMult*maxSubdivs)^2 )  as integer
			minLtCPP=( (dlSubDivs*globalMult*minSubdivs)^2 ) as integer
			maxLtCPP=( (dlSubDivs*globalMult*maxSubdivs)^2 ) as integer
			SSSRPP=( (SSSSubDivs*globalMult)^2 ) as integer
			minSSSRPP= ( (SSSSubDivs*globalMult*minSubdivs)^2 )  as integer
			maxSSSRPP= ( (SSSSubDivs*globalMult*maxSubdivs)^2 )  as integer
			GIRPP=( (GISubDivs*globalMult)^2 ) as integer
			minGIRPP=( (GISubDivs*globalMult*minSubdivs)^2 )  as integer
			maxGIRPP=( (GISubDivs*globalMult*maxSubdivs)^2 )  as integer
			*/
			minRPP=maxRPP=( (reflSubDivs^2)*globalMult ) as integer
			lightsMinRPP=lightsMaxRPP=( (dlSubDivs^2)*globalMult ) as integer
			minShCPP=( ((reflSubDivs*minSubdivs)^2 )*globalMult)  as integer
			maxShCPP=( ((reflSubDivs*maxSubdivs)^2 )*globalMult)  as integer
			minLtCPP=( ((dlSubDivs*minSubdivs)^2 )*globalMult) as integer
			maxLtCPP=( ((dlSubDivs*maxSubdivs)^2 )*globalMult) as integer
			SSSRPP=( ((SSSSubDivs)^2 )*globalMult) as integer
			minSSSRPP= ( ((SSSSubDivs*minSubdivs)^2 )*globalMult)  as integer
			maxSSSRPP= ( ((SSSSubDivs*maxSubdivs)^2 )*globalMult)  as integer
			GIRPP=( ((GISubDivs)^2 )*globalMult) as integer
			minGIRPP=( ((GISubDivs*minSubdivs)^2 )*globalMult)  as integer
			maxGIRPP=( ((GISubDivs*maxSubdivs)^2 )*globalMult)  as integer

			/*
			minRPP=( (spn1.value*spn8.value)^2 ) as integer
			maxRPP=( (spn1.value*spn8.value)^2 ) as integer
			lightsMinRPP=( (spn6.value*spn8.value)^2 ) as integer
			lightsMaxRPP=( (spn6.value*spn8.value)^2 ) as integer
			minShCPP=( (spn1.value*spn8.value*spn11.value)^2 )  as integer
			maxShCPP=( (spn1.value*spn8.value*spn12.value)^2 )  as integer
			minLtCPP=( (spn2.value*spn8.value*spn11.value)^2 ) as integer
			maxLtCPP=( (spn2.value*spn8.value*spn12.value)^2 ) as integer
			SSSRPP=( (spn5.value*spn8.value)^2 ) as integer
			minSSSRPP= ( (spn5.value*spn8.value*spn11.value)^2 )  as integer
			maxSSSRPP= ( (spn5.value*spn8.value*spn12.value)^2 )  as integer
			GIRPP=( (spn7.value*spn8.value)^2 ) as integer
			minGIRPP=( (spn7.value*spn8.value*spn11.value)^2 )  as integer
			maxGIRPP=( (spn7.value*spn8.value*spn12.value)^2 )  as integer
			*/

			if (minShCPP>2101514800 or minShCPP < 0 )then minShCPP="LOADS!"
			if (maxShCPP>2101514800 or maxShCPP < 0 ) then maxShCPP="LOTS!"

			lbl13.caption="\t\t\t\tfixed\t|(max adaptive)\n"
			lbl13.caption+=("Base Shaders Samples :\t\t" + ((minRPP * (1-aAmt)) as integer ) as string +"\t|("+ minRPP as string + ")\n")
			lbl13.caption+=("Base SSS Samples :  \t\t" + ((SSSRPP * (1-aAmt)) as integer)as string +"\t|("+SSSRPP as string + ")\n")
			lbl13.caption+=("Base Lights Samples :\t\t" + ((lightsMinRPP * (1-aAmt)) as integer) as string +"\t|("+lightsMinRPP as string + ")\n")
			lbl13.caption+=("Base IBL/GI Samples :\t\t" + ((GIRPP * (1-aAmt)) as integer)as string +"\t|("+GIRPP as string + ")\n")
			lbl13.caption+=("Camera (AA) Samples:\t\t" + (spn11.value^2) as string + "\t|(" + (spn12.value^2) as string +")\n\n")
			lbl13.caption+="--------------------------------------------------------------------------------------------------\n"
			lbl13.caption+="\t\t\tmin fixed|(min adaptive)\t/max fixed|(max adaptive)\n"
			lbl13.caption+=("Total Shaders Samples: \t\t" + ((minShCPP * (1-aAmt)) as integer)as string + "|("+minShCPP as string +")\t/"+ ((maxShCPP * (1-aAmt)) as integer)as string +"|("+maxShCPP as string+")\n")
			lbl13.caption+=("Total SSS Samples: \t\t" + ((minSSSRPP * (1-aAmt)) as integer)as string + "|("+minSSSRPP as string +")\t/"+ ((maxSSSRPP * (1-aAmt)) as integer)as string +"|("+maxSSSRPP as string+")\n")
			lbl13.caption+=("Total Lights Samples: \t\t" + ((minLtCPP * (1-aAmt)) as integer)as string + "|("+minLtCPP as string +")\t/"+ ((maxLtCPP * (1-aAmt)) as integer)as string +"|("+maxLtCPP as string+")\n")
			lbl13.caption+=("Total IBL/GI Samples: \t\t" + ((minGIRPP * (1-aAmt)) as integer)as string + "|("+minGIRPP as string +")\t/"+ ((maxGIRPP * (1-aAmt)) as integer)as string +"|("+maxGIRPP as string+")\n")
			lbl13.caption+="--------------------------------------------------------------------------------------------------\n"
			lbl13.caption+=("Total Number Of Active Lights :\t" + numLights as string + "\n")

		)

		on Arnie4Vray3Roll open do
		(
			updateInfoLabel()
		)

		on spn1 changed val do
			updateInfoLabel()
		on spn2 changed val do
			updateInfoLabel()
		on spn3 changed val do
			updateInfoLabel()
		on spn4 changed val do
			updateInfoLabel()
		on spn5 changed val do
			updateInfoLabel()
		on spn6 changed val do
			updateInfoLabel()
		on spn7 changed val do
			updateInfoLabel()
		on spn8 changed val do
			updateInfoLabel()
		on spn9 changed val do
			updateInfoLabel()
		on spn10 changed val do
			updateInfoLabel()
		on spn11 changed val do
			updateInfoLabel()
		on spn12 changed val do
			updateInfoLabel()

		on btn1 pressed do
		(
			spn1.value = spn2.value = spn5.value = spn6.value = spn7.value = spn11.value = spn12.value = 2
			spn3.value = spn8.value = spn9.value = 1
			spn4.value = spn10.value = 5
			updateInfoLabel()
		)

		on btn2 pressed do
		(
			spn1.value = spn2.value = spn6.value = 16
			spn3.value = spn11.value = 2
			spn4.value = 15
			spn5.value = 12
			spn7.value = 24
			spn8.value = 1
			spn9.value = 0.75
			spn10.value = 8
			spn12.value = 4
			updateInfoLabel()
		)
		on btn3 pressed do
		(
			spn1.value = spn2.value = spn6.value = 24
			spn3.value = spn11.value = 2
			spn4.value = 15
			spn5.value = 20
			spn7.value = 32
			spn8.value = 0.889
			spn9.value = 0.75
			spn10.value = 10
			spn12.value = 4
			updateInfoLabel()
		)
		on btn4 pressed do
		(
			spn1.value = spn2.value = spn5.value = spn6.value = 32
			spn3.value = spn11.value = 2
			spn4.value = 15
			spn7.value = 48
			spn8.value = 0.5
			spn9.value = 0.5
			spn10.value = 12
			spn12.value = 4
			updateInfoLabel()
		)
		on btn5 pressed do
		(
			spn1.value = spn2.value = spn5.value = spn6.value = 1
			spn3.value = 3
			spn4.value = 15
			spn7.value = 2
			spn8.value = 32
			spn9.value = 0.0
			spn10.value = 12
			spn11.value = spn12.value = 4
			updateInfoLabel()
		)
		on btn6 pressed do
		(
			spn1.value = spn2.value = spn5.value = spn6.value = 1
			spn3.value = 3
			spn4.value = 15
			spn7.value = 2
			spn8.value = 2
			spn9.value = 0.0
			spn10.value = 12
			spn11.value = spn12.value = 16
			updateInfoLabel()
		)

		on btn7 pressed do
		(
			updateInfoLabel()
			theWholeNodes=#()
			for m in scenematerials do append theWholeNodes m
			join theWholeNodes (getClassInstances VrayMtl)
			join theWholeNodes (getClassInstances VrayFastSSS2)
			join theWholeNodes (getClassInstances VrayLightMtl)
			join theWholeNodes (getClassInstances VraySkinMtl)
			join theWholeNodes (getClassInstances VrayCarPaintMtl)
			join theWholeNodes (getClassInstances VrayHairMtl)
			join theWholeNodes (getClassInstances VrayOSLMtl)
			join theWholeNodes (getClassInstances VrayScatterVolume)
			for l in lights where classof l != targetObject do append theWholeNodes l
			theWholeNodes=makeUniqueArray theWholeNodes
			changeSubdivs theWholeNodes reflSubDivs refrSubDivs dlSubDivs GISubDivs noiseBits SSSSubDivs minSubdivs maxSubdivs gBounces sBounces globalMult aAmt
			setRenderSettings()
		)
	)
	createdialog Arnie4Vray3Roll style:#(#style_titlebar, #style_border, #style_sysmenu,#style_minimizebox,#style_maximizebox)
)
