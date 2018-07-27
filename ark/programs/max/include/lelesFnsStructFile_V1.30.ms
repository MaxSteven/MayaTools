	struct lelesFns 
	(
		
		fn printMsg =
		(
			messageBox theMsg
			theMsg=""
		),
		
		fn closeRendDiag =
		(
			if renderSceneDialog.isOpen() then 
				(
					renderSceneDialog.close()
					true
				)
			else false
	-- 		if not renderSceneDialog.isOpen() do print "Closed the Render Dialog"
		),
		
		fn openRendDiag wasOpen=
		(
			if wasOpen do renderSceneDialog.open()
	-- 		print "Reopened the Render Dialog"
		),

		fn fixRenderStep =
		(
			closeRendDiag()
			rendNThFrame = 1
			rendTimeType = 2
			openRendDiag()
		),
		
		fn checkSetVray = 
		(
			-- 	check / set VRay
			if (renderers.current.classID as string == "#(1941615238, 2012806412)") then renderers.current else 
			(
				if (queryBox "Want me to set VRay as your production renderer?") then 
					(
						(renderers.current = (for i in RendererClass.classes where matchPattern (i as string) pattern:"V_Ray_Adv*" do exit with i()) )
						renderers.current
					)
					else messagebox "Don't blame ME if i don't do what you want me to!"
			)
	-- 		print "Performed Current Renderer Check"
		),
		
		fn resetVray =
		(
			renderers.current=Default_Scanline_Renderer()
			(cr = renderers.current = (for i in RendererClass.classes where matchPattern (i as string) pattern:"V_Ray_Adv*" do exit with i()) )
		),
		
		fn deactivateRenderRegion =
		(
			vrayVFBSetRegionEnabled false
		),

		fn fixVrayHDRIMemLimit =
		(
			try
			(
				(getclassinstances vrayhdri)[1].hdri_memLimit = 0
				(getclassinstances vrayhdri)[1].clear_memory=false
			)
			catch
			(
	-- 			print "no vrayHDRIs present in this scene!"
			)
		),
		
		fn parseEnvironmentSettings doEnv doOverride doFile doGi doAdv doLC doOutput doUI=
		(
			cr = renderers.current
			format "---------------------------------------------------------------------------\n"
			renderSettingsArray=#()
			if doEnv do
			(
				for p in (getPropNames cr) where ( (findstring (p as string) "environment_") != undefined ) do 
				(
					append renderSettingsArray #(p, (getProperty cr p))
					format "Collected Property [%] With Value [%]\n" p (getProperty cr p)
				)
			)
			if doOverride do
			(
				for p in (getPropNames cr) where ( (findstring (p as string) "_overrideMtl_") != undefined ) do 
				(
					append renderSettingsArray #(p, (getProperty cr p))
					format "Collected Property [%] With Value [%]\n" p (getProperty cr p)
				)
			)
			if doFile do
			(
				for p in (getPropNames cr) where ( ( (findstring (p as string) "file") != undefined ) and ( ( (matchpattern (p as string) pattern:"*splitfile*") == false ) and ( (matchpattern (p as string) pattern:"*rawfile*") == false ) ) ) do 
				(
					append renderSettingsArray #(p, (getProperty cr p))
					format "Collected Property [%] With Value [%]\n" p (getProperty cr p)
				)
			)
			if doGI do
			(
				for p in (getPropNames cr) where ( (findstring (p as string) "gi") != undefined ) do 
				(
					append renderSettingsArray #(p, (getProperty cr p))
					format "Collected Property [%] With Value [%]\n" p (getProperty cr p)
				)
			)
			if doAdv do
			(
				for p in (getPropNames cr) where ( (findstring (p as string) "adv") != undefined ) do 
				(
					append renderSettingsArray #(p, (getProperty cr p))
					format "Collected Property [%] With Value [%]\n" p (getProperty cr p)
				)
			)
			if doLC do
			(	
				for p in (getPropNames cr) where ( (findstring (p as string) "lightcache") != undefined ) do 
				(
					append renderSettingsArray #(p, (getProperty cr p))
					format "Collected Property [%] With Value [%]\n" p (getProperty cr p)
				)
			)
			if doOutput do
			(
				for p in (getPropNames cr) where ( (findstring (p as string) "output_") != undefined ) do 
				(
					append renderSettingsArray #(p, (getProperty cr p))
					format "Collected Property [%] With Value [%]\n" p (getProperty cr p)
				)
			)
			if doUI do
			(
				for p in (getPropNames cr) where ( (findstring (p as string) "ui_view") != undefined ) do 
				(
					append renderSettingsArray #(p, (getProperty cr p))
					format "Collected Property [%] With Value [%]\n" p (getProperty cr p)
				)
			)			
			print "Parsed Render Settings"
			renderSettingsArray
		),

		fn restoreEnvironmentSettings renderSettingsArray =
		(
			format "==========================================================\n"
			for p in renderSettingsArray do
			(
				try 
				(
					setProperty renderers.current p[1]  p[2]
	 				format "Property [%] Set to [%]\n" p[1]  p[2]
				) 
				catch 
				(
	 				format "--Failed To Set Property [%] to [%]\n" p[1]  p[2]
				)
			)
			print "Restored Render Settings"
		),
		
		fn setResolution resType overscanAmount=			--restype : "Half" "Base" "Double"   overscanAmount: float mult
		(
			case resType of 
			(
				"Half" :
				(
					renderWidth=floor (1024*overscanAmount)			
					renderHeight=floor (540*overscanAmount)
				)
				"Base" :
				(
					renderWidth=floor (2048*overscanAmount)			
					renderHeight=floor (1080*overscanAmount)
				)
				"Double" :
				(
					renderWidth=floor (4096*overscanAmount)			
					renderHeight=floor (2160*overscanAmount)
				)
			)

		),
		
		fn clearOutputs  =
		(
			rendOutputFilename=""
			cr.output_rawFileName=""
			cr.output_splitFileName=""
		),	
		
		fn clearBGs =
		(
			cr.environment_gi_on=cr.environment_rr_on=cr.environment_refract_on=false
			environmentMap = undefined
			backgroundColor = black
			for l in lights where classof l == vraylight do
			(
				if l.type == 1 do l.invisible = true
			)
		),
		
		fn clearMatEd =
		(
			for i=1 to 24 do meditmaterials[i] = vraymtl()
		),
		
		fn resetGBufferIDs =
		(
			objects.gbufferChannel=0
			print "Reset ALL object GBuffer IDs to 0"
		),

		fn activateREs =
		(
			re.SetElementsActive true
			print "Activated the Render Elements!"
		),

		fn cleanREs cleanType =
		(
				local numOldElements=0 
				elementKeepList = #( "*VrayExtraTex*", "*MultiMatteElement*", "*VRayLightSelect*", "*VRayMtlSelect*", "*VRayObjectSelect*" )
				re = maxOps.GetCurRenderElementMgr()
				if cleanType ==2 then		--full clean
				(
					re.RemoveAllRenderElements()
	-- 				print "Removed ALL the old RenderElements"
	-- 				freescenebitmaps()
				)
				else 	if cleanType ==1 then	--partial clean
				(
					for n = (re.numrenderelements()- 1) to 0 by -1 do
						(
							local foundit=false
							local el = re.getrenderelement n
							for pat in elementKeepList do 
							(
								if matchpattern el.elementname pattern:pat do 
								(
									foundit=true
	-- 								theMsg+= ("found and KEPT a " + el.elementname + " element!\n")
								)
							)
							if not foundit then 
							(
	-- 							theMsg+= ("found and REMOVED a " + el.elementname + " element!\n")
								re.RemoveRenderElement el
							)
							else numOldElements+=1
						)
	-- 				print "Removed SOME of the old RenderElements"
				)
				else							--no clean
				(
	-- 				print "Removed NONE of the old RenderElements"
				)
		),
		
		fn addREs REsType =
		(
			case REsType of
			(
				"Beauty":
				(
					elemList = #( VrayDiffuseFilter, VrayGlobalIllumination, VRayLighting, VRayReflection, VrayReflectionFilter, VrayMtlReflectGlossiness ,
								VRayRefraction, VrayRefractionFilter, VRaySelfIllumination, VrayShadows, VRaySpecular, VraySSS2)
					elemBaseNamesList=#("diffuse", "GI", "lighting", "reflect", "reflectFilter", "reflectGloss","refract", "refractFilter", "selfIllum", "shadow", "specular", "SSS")
					for r=1 to elemList.count do 
					(
						local theElement = (elemList[r]) elementName:elemBaseNamesList[r]
						re.AddRenderElement theElement
						theMsg+="Added a " + theElement.elementName + " Render Element\n"
					)
				)
				"Utility":
				(
					elemList = #( VRaySamplerInfo, VRaySamplerInfo, VRaySamplerInfo, VRayVelocity)  --VRaySamplerInfo, VRaySamplerInfo, VrayZDepth,VRayVelocity
					elemBaseNamesList=#("nrmWorldNoMB", "pntWorldNoMB", "UVnoMB_01", "velocity")
					-- then add all the ones we need, and configure those that need  it
					for r=1 to elemList.count do 
					(
						local theElement = (elemList[r]) elementName:elemBaseNamesList[r]
						re.AddRenderElement theElement
						case r of 
						(
							1:	(
									theElement.type=1
									theElement.coord_system=0
								)
							2:	(
									theElement.type=0
									theElement.point_multiplier=1.0
									theElement.coord_system=0
								)
							3:	(
									theElement.type=4
								)
							4: (
								theElement.clamp_velocity=false
								)
						)
						re.SetRenderElementFilename (r-1) ""
						theMsg+="Added a " + theElement.elementName + " Render Element\n"
					)
				)
				"AO":
				(
					theAOMap=VrayDirt()
					theAOMap.radius =200
					theAOMap.subdivs = 32
					elementList = #( VRayExtraTex )
					theElement = (elementlist[1])()
					re.AddRenderElement theElement
					theElement.texture=theAoMap
					theElement.elementName="exTex_AO"
					theElement.consider_for_antialiasing=false
					theMsg+= "Added the AO Render Element!\n"
				)
				"MM":
				(
					------------------------------------------>  IDMtl_ <------------------------------------------
					theMultiSubs = getclassinstances Multimaterial
					theCount=0
					for m in theMultisubs do
					(
						if ((matchpattern m.name pattern:"*bubbleship*") or (matchpattern m.name pattern:"*drone*")) do theCount = m.materialIDList.count
					)
					
					if theCount != 0 do 
					(
						theBaseNumOfMMs = ceil (theCount/3.0)
						MMEIndex = 1
						theMME = MultiMatteElement()
						theMME.MatID=true
						theMME.elementname="IDMtl_"+ ((ceil (MMEIndex/3.0))as integer ) as string
						re.AddRenderElement theMME
						theMME.R_gbufIDOn = theMME.G_gbufIDOn = theMME.B_gbufIDOn =false
						NSSIndex = 0
						elemIndex=0
						for i = 1 to theCount do
						(
							MMEIndex+=1
							NSSIndex += 1
							if NSSIndex > 3 do 
							(
								NSSIndex = 1
								theMME = MultiMatteElement()
								theMME.MatID=true
								theMME.elementname ="IDMtl_"+ ((ceil (MMEIndex/3.0))as integer ) as string
								theMME.R_gbufIDOn = theMME.G_gbufIDOn = theMME.B_gbufIDOn =false
								re.AddRenderElement theMME 
							)
							case NSSIndex of
							(
								1: (
										theMME.R_gbufIDOn = true
										theMME.R_gbufID = i
									)
								2:(
										theMME.G_gbufIDOn = true
										theMME.G_gbufID = i
									)
								3:(
										theMME.B_gbufIDOn = true
										theMME.B_gbufID = i
									)
							)--end case
						)--end i loop
						if theBaseNumOfMMs!= 0 do theMsg+= ("Added "+ (theBaseNumOfMMs as integer) as string + " Material ID Multi Matte Elements\n" )
					)
					------------------------------------------>  IDObj_ <------------------------------------------
					gBufIDs=#()
					for o in objects where o.gbufferChannel!=0 do appendIfUnique gBufIDs o.gbufferChannel
					theCount=gBufIDs.count
					sort gBufIDs
	-- 				print gBufIDs
					if theCount != 0 do 
					(
						theBaseNumOfMMs = ceil (theCount/3.0)
						MMEIndex = 1
						theMME = MultiMatteElement()
						theMME.MatID=false
						theMME.elementname="IDObj_"+((ceil (MMEIndex/3.0))as integer ) as string
						re.AddRenderElement theMME
						theMME.R_gbufIDOn = theMME.G_gbufIDOn = theMME.B_gbufIDOn =false
						theMME.affect_matte_objects=false
						NSSIndex = 0
						for i = 1 to theCount do
						(
							MMEIndex+=1
							NSSIndex += 1
							if NSSIndex > 3 do 
							(
								NSSIndex = 1
								theMME = MultiMatteElement()
								theMME.elementname="IDObj_"+ ((ceil (MMEIndex/3.0))as integer ) as string
								re.AddRenderElement theMME 
								theMME.R_gbufIDOn = theMME.G_gbufIDOn = theMME.B_gbufIDOn =false
								theMME.affect_matte_objects=false
							)

							case NSSIndex of
							(
								1: (
										theMME.R_gbufIDOn = true
										theMME.R_gbufID = gBufIDs[i]
									)
								2:(
										theMME.G_gbufIDOn = true
										theMME.G_gbufID = gBufIDs[i]
									)
								3:(
										theMME.B_gbufIDOn = true
										theMME.B_gbufID = gBufIDs[i]
									)
							)--end case
						)--end i loop
						if theBaseNumOfMMs!= 0 do theMsg+= ("Added "+ (theBaseNumOfMMs as integer) as string + " Object ID Multi Matte Elements\n" )
					)
				)
				"exposimeter":
				(
					elemList = #(  VRaySamplerInfo)
					elemBaseNamesList=#( "PPos")
					for i=1 to elemList.count do
					(
						theElement = (elemList[i]) elementName:elemBaseNamesList[i]
						if i==1 then 
						(
							theElement.type=0
							theElement.coord_system=0
						)
						else
						(
							theElement.zdepth_min=0
							theElement.zdepth_max=1
							theElement.invert_zdepth=false
							theElement.clamp_zdepth=false							
						)
						re.AddRenderElement theElement
						theMsg+="Added a " + theElement.elementName + " Render Element\n"
					)
				)
			)
		),
		
		fn resetVrayProps =
		(
			for g in geometry do 
			(
				setUserPropBuffer g ""
			)
		),
		
		fn resetVrayPropsObject obj =
		(
			setUserPropBuffer obj ""
		),
		
		fn AFtheView =
		(
			startTime=timestamp()
			theDists=#()
			theInts=#()
			theMidDists=#()
			theObjs=for o in geometry where (not o.ishidden and o.renderable) collect o
			coordSysTM =getViewTM()
			invCoordSysTM = inverse coordSysTM				
-- 			camRay=ray invCoordSysTM.row4 -invCoordSysTM.row3
-- 			theInts=intersectRayScene camRay
			for y=0 to ((getViewSize())[2]-1) by 3 do
				(
					for x=0 to ((getViewSize())[1]-1) by 3 do
						(
							camRay=(mapScreenToWorldRay [x,y])
							theHit =(intersectRayScene camRay)
							if theHit.count!=0 do
								(
									for i in theHit do
										(
											append theDists (distance i[2].pos camray.pos)
										)
								)
							if ( close_enough x (((getViewSize())[1]-1)/2) 100000 ) and ( close_enough y (((getViewSize())[2]-1)/2) 100000 ) do
-- 							if [x,y] == [((getViewSize())[1]-1)/2,((getViewSize())[2]-1)/2] do 
								(
									if theHit.count!=0 do
									(
										for i in theHit do
											(
												append theMidDists (distance i[2].pos camray.pos)
											)
									)
								)
-- 							append theDists #((distance theHit camray.pos),theInts[i][2])
						)
				)

			if theDists.count!=0 do
			(
				sort theDists
				theOutArray=#(theDists[1],theDists[theDists.count])
				if theMidDists.count!=0 then
				(
					sort theMidDists
					append theOutArray theMidDists[1]
-- 					print theMidDists
				)
				else 
				(
					append theOutArray 0
				)
-- 				qsort theDists compareFn 

-- 				theMsg+= ("It took "+(timestamp()-startTime) as string+" ms. to choose and intesect "+theObjs.count as string+" objects\n")
				return theOutArray

			)
		),
		
		fn AFtheView2 thePPosVals camRay=		
		(
			theDists=#()
			theSortedDists=()
			theNormalisedDists=#()
			theInts=#()
			theOutArray=#()

			
			for p in thePPosVals do 
			(
				append theDists (distance p camRay.pos)	
			)
			if theDists.count!=0 do
			(
				theSortedDists = sort theDists
				theMaxAbsDist = theSortedDists[theSortedDists.count]
				for d in theDists do
				(
					append theNormalisedDists (d/theMaxAbsDist)
				)
				
				return theOutArray=#(theNormalisedDists,theMaxAbsDist)
				
			)
			
		),
		
		fn storeVRayFBData =
		(

		),
		
		fn reStoreVRayFBData=
		(

		)


	)

