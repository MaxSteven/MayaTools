(
	rollout RO "Random Material" width:170
	(
		local mats = #()
		
		radiobuttons typeSel "" labels:#("Material Editor","Scene Materials","Load: (.matlib)") width:(ro.width-10) align:#center
		multiListbox mlb "Materials" width:(ro.width-10) align:#center
		button btnrandomwire "Apply Random Materials" width:(ro.width-10) align:#center
		button btnAppend "Append" width:(ro.width-100) height:14 pos:[95,36] enabled:false
		
		fn fnAppendMatLib doAppend:false =
		(
			currItems = mlb.items
			newItems = for i in currentMaterialLibrary where superClassof i == material collect i.name
			if doAppend then join currItems newItems else currItems = newItems
			mlb.items = currItems
			newMats = for i in currentMaterialLibrary where superClassof i == material collect i
			if doAppend then join mats newMats else mats = newMats
		)		
		
		on RO open do
		(
			mlb.items = for i in meditMaterials collect i.name
			mats = for i in meditMaterials collect i
		)
		
		on typeSel changed i do
		(
			case i of
			(
				1 : 
				(
					mlb.items = for i in meditMaterials where superClassof i == material  collect i.name
					mats = for i in meditMaterials where superClassof i == material collect i
				)
				
				2 : 
				(
					mlb.items = for i in sceneMaterials where superClassof i == material  collect i.name
					mats = for i in sceneMaterials where superClassof i == material  collect i
				)
				
				3 : 
				(
					fileOpenMatLib()
					fnAppendMatLib()
					btnAppend.enabled = true
				)
			)
		)
		
		on btnappend pressed do
		(
			local oldMtlLib = getMatLibFileName()
			  fileOpenMatLib()
			  if oldMtlLib != getMatLibFileName()
				 do fnAppendMatLib doAppend:true
		/* 	local oldMtlLib = currentMaterialLibrary
			fileOpenMatLib()
			if oldMtlLib != currentMaterialLibrary do fnAppendMatLib doAppend:true */
		)
		
		
		on btnrandomwire pressed do
		(
			local mats2
			
			case typeSel.state of
			(
				1 : 
				(
					mats2 = for i = 1 to meditMaterials.count where mlb.selection[i] AND superClassof meditMaterials[i] == material collect meditMaterials[i]
				)
				
				2 : 
				(
					mats2 = for i = 1 to sceneMaterials.count where mlb.selection[i] AND superClassof sceneMaterials[i] == material  collect sceneMaterials[i]
				)
				3 : 
				(
					mats2 = for i = 1 to currentMaterialLibrary.count where mlb.selection[i] AND superClassof currentMaterialLibrary[i] == material  collect currentMaterialLibrary[i]
				)
			)
			
			local userSel = selection as array
			
			for bar in userSel where isValidNode bar while mats2.count > 0 do
			(
				bar.material = mats2[random 1 mats2.count]
			)
		)
	)
	
	createDialog RO
)