try (destroyDialog ::rlStandardtoVray)catch()
rollout rlStandardtoVray "Standard to Vray"
(
	button btnGo "Fix Selected Objects" width:130 height:40 pos:[10,10]

	on btnGo pressed do
	(
		for obj in selection do
		(
			if obj.material != undefined do (
				if classOf obj.material == Multimaterial do (
					local newMaterials =  #()
					
					for i = 1 to obj.material.count do (--//Loop through each material
						subMat = obj.material[i]
						
						--//Standard Shader Properties
						curDiffuseCol = subMat.diffuse
						curDiffuse = subMat.diffuseMap
						curBump = subMat.bumpMap
						curOpacity = subMat.opacityMap
						
						local vrayMat = VRayMtl diffuse:curDiffuseCol texmap_diffuse:curDiffuse texmap_bump:curBump texmap_opacity:curOpacity
						append newMaterials vrayMat
					)
					
					VrayMultiMat = Multimaterial materialList:newMaterials
					--meditMaterials[1] = VrayMultiMat
					obj.material = VrayMultiMat
					
				)--//End Multimat Material
				
				
				if classOf obj.material == Standard do (
					subMat = obj.material
					
					--//Standard Shader Properties
					curDiffuseCol = subMat.diffuse
					curDiffuse = subMat.diffuseMap
					curBump = subMat.bumpMap
					curOpacity = subMat.opacityMap
					
					local vrayMat = VRayMtl diffuse:curDiffuseCol texmap_diffuse:curDiffuse texmap_bump:curBump texmap_opacity:curOpacity
					
					obj.material = vrayMat
					
				)--//End Standard Material
			)	
		)
		print "Finished fixing materials"
	)

)
createdialog rlStandardtoVray 150 60
