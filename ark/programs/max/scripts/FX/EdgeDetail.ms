try(destroyDialog ::rlFXEdgeDetail)catch()
rollout rlFXEdgeDetail "FX Edge-Detail"
(
	--//Functions
	fn GeoFilter o = (superClassOf o == GeometryClass)

	fn fnSpeedAtTime =
	(
		obj = if selection.count == 1 then selection[1] else pickObject prompt:"Pick an object" filter:GeoFilter
		testValues = #()
		frameValues = #()
		
		if obj != undefined then
		(
			for t in animationrange.start to animationrange.end by 1 do
			(
				at time t currTransform = obj.center
				at time (t-1f) preTransform = obj.center
				
				changeInTransform = currTransform - preTransform
				t1 = (abs changeInTransform[1]) as float
				t2 = (abs changeInTransform[2]) as float
				t3 = (abs changeInTransform[3]) as float
				
				append testValues t1
				append testValues t2
				append testValues t3
			)
			sort testValues --//order lowest to highest
			
			--//Speed at frame
			at time slidertime currTransform = obj.center
			at time (slidertime-1f) preTransform = obj.center
			
			changeInTransform = currTransform - preTransform
			t1 = (abs changeInTransform[1]) as float
			t2 = (abs changeInTransform[2]) as float
			t3 = (abs changeInTransform[3]) as float
			
			append frameValues t1
			append frameValues t2
			append frameValues t3
			sort frameValues --//order lowest to highest
			
			return #(frameValues[3],testValues[1],testValues[testvalues.count])
		)else(
			return #(0.0,0.0,0.0)
		)
	)

	label lbTolerance "Minimum Speed:" pos:[15,15]
	spinner spnTolerance "" fieldwidth:55 range:[0,999999999,0] type:#worldunits pos:[98,15] tooltip:"Minimum speed an object must be moving in order to get edge detail."
	button btnGetSpeedInfo "Get Speed" height:57 pos:[100,45] tooltip:"Pick and object to finds its speed information within the active framerange."
	label lbCurTime "Cur:" pos:[15,45]
	edittext etCurSpeed "" text:"0.0" width:50 pos:[40,45] readonly:true
	label lbMin "Min:" pos:[15,65]
	edittext etMinSpeed "" text:"0.0" width:50 pos:[40,65] readonly:true
	label lbMax "Max:" pos:[15,85]
	edittext etMaxSpeed "" text:"0.0" width:50 pos:[40,85] readonly:true
	label lbDetailSize "Detail Size:" pos:[15,115]
	spinner spnDetailSize "" fieldwidth:55 range:[0,999999999,4] type:#worldunits pos:[98,115] tooltip:"Minimum speed an object must be moving in order to get edge detail."
	label lbSubdivide "Subdivide:" pos:[15,140]
	checkbox cbsubdivide "" pos:[101,140] checked:true
	button btnRunEdgeDetail "Run Edge-Detail" width:151 height:30 pos:[15,165]
	
	on btnGetSpeedInfo pressed do
	(
		speeds = fnSpeedAtTime()
		etCurSpeed.text = speeds[1] as string
		etMinSpeed.text = speeds[2] as string
		etMaxSpeed.text = speeds[3] as string 
	)
	
	on spnDetailSize changed val do
	(
		fxClasses = #(subdivide)
		currObjs = for obj in selection where superclassof obj == GeometryClass collect obj
		
		for obj in currObjs do
		(
			for i = obj.modifiers.count to 1 by -1 where findItem fxClasses (classof obj.modifiers[i]) != 0 do 
			(
				obj.modifiers[i].size = val
			)
		)
	)
	
	on btnRunEdgeDetail pressed do
	(
		tol = spnTolerance.value --//higher the tolerance the faster the object has to be moving
		objCollection = for obj in selection where superclassof obj == GeometryClass collect (#(obj,false))
		
		for t in animationrange.start to animationrange.end by 1 do
		(
			for itm in objCollection where itm[2] != true do
			(
				obj = itm[1]
				
				at time t currTransform = obj.center
				at time (t-1f) preTransform = obj.center
				
				changeInTransform = currTransform - preTransform
				t1 = (abs changeInTransform[1])
				t2 = (abs changeInTransform[2])
				t3 = (abs changeInTransform[3])
				
				if t1 >= tol OR t2 >= tol OR t3 >= tol then
				(
					obj.wirecolor = red
					fxSub = (subdivide name:"FX_Subdivide" size:5)
					fxTurbo = (TurboSmooth name:"FX_TurboSmooth" iterations:0.0)	
					if cbsubdivide.state do addmodifier obj fxSub
					addmodifier obj fxTurbo	
					
					--// Key the turbosmooth iteration
					theTrack = fxTurbo.iterations.controller = bezier_float () --assign controller to subAnim to make keyable
					OFFKey = addNewKey theTrack (t - 2f)
					OFFKey.value = 0.0
					theTrack.keys[1].inTangentType = #step
					theTrack.keys[1].outTangentType = #step
					ONKey = addNewKey theTrack (t - 1f)
					ONKey.value = 1.0
					theTrack.keys[2].inTangentType = #step
					theTrack.keys[2].outTangentType = #step
					
					itm[2] = true --set "pass" state to true so we don't double key it
				)
				else
				(
					obj.wirecolor = yellow
					itm[2] = false -- keep it in the loop of things
				)
			)
		)
	)
)
createDialog rlFXEdgeDetail 180 210 style:#(#style_SysMenu, #style_ToolWindow)