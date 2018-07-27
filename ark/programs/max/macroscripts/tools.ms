macroScript splitMesh category:"Ingenuity" tooltip:"Split Mesh on UV Seam"
(
	mesh = $
	channel = 1
	local obj = copy mesh
	convertToMesh obj
--//  repeat until all elements have been detached
	while obj.numfaces > 0 do
	(
		face_array = #(1)
		i = 0
--//		repeat until the counter is higher than the faces stored in the array
		while i < face_array.count do (
			i += 1
--//			get all map vertices used by the current map face in the collection array:
			verts = meshop.getMapVertsUsingMapFace obj channel #(face_array[i])
--//			get all map faces used by these map vertices -
			--this gives us all neighbours of the current map face
			faces = meshop.getMapFacesUsingMapVert obj channel verts
			--make sure only unique faces are written to the array
			for f in faces where findItem face_array f == 0 do
				append face_array f
		)
		--once all connected faces in an element are collected,
		--create a new empty EMesh:
		newMesh = Editable_mesh()
		--detach the collected faces and assign to the EMesh's TriMesh
		newMesh.mesh = meshop.detachFaces obj face_array delete:true asMesh:true
		--Copy the transformation of the original object
		newMesh.transform = mesh.transform
		--Assign a unique name based on the original one
		newMesh.name = uniquename (mesh.name +"_UVsplit")
		--assign a random wirecolor to the new mesh
		newMesh.wireColor = color (random 0 255) (random 0 255) (random 0 255)
	)
	delete obj --delete the clone which has no faces at this point
	delete mesh --delete the original
)
macroScript vertexBake category:"Ingenuity" tooltip:"Vertex Bake"
(
	try(destroyDialog bakeRoll)catch()
	global mapChannel = 1
	image = 0

	rollout bakeRoll "Vertex Bake" width:160 height:42
	(
		editText edtImage "" pos:[36,4] width:96 height:16
		label lblImage "Image:" pos:[4,4] width:32 height:16
		button btnImage "..." pos:[132,4] width:24 height:16
		editText edtMapChannel "" pos:[36,22] width:32 height:16
		label lblMapChannel "UVs:" pos:[12,22] width:24 height:16
		button btnBake "Bake" pos:[68,22] width:88 height:16
	
		on bakeRoll open do (
			edtMapChannel.text = mapChannel as string;
		)
		on btnImage pressed do (
			image = selectBitmap caption:"Bake image:"
			if image != undefined then
				edtImage.text = image.filename
		)
		on btnBake pressed do (
			undo off (
				width = image.width-1
				height = image.height-1
				mapChannel = edtMapChannel.text as integer;
		
				if (image != undefined) and (mapChannel != undefined) then
					ready = true
		
				try(
					numFaces = $.numFaces
					numVerts = $.numVerts
					setNumCPVVerts $ numVerts
					numUVVerts = meshop.getNumMapVerts $ mapChannel
				)catch(
					format "Please select an Editable Mesh.\n"
					ready = false
				)
		
				if ready then (
					meshTrans = #()
		
					--for each face, get the uv verts and mesh verts
					--there is a one to one correspondence between uv faces and mesh faces
					--uv verts and and mesh verts are also listed in the same order
					--i.e. x y z are the same across uvVerts[x,y,z] and meshVerts[x,y,z]
					for f = 1 to numFaces do (
						--uvVerts[1] translates to meshVerts[1]
						uvVerts = meshop.getMapFace $ mapChannel f
						meshVerts = getFace $ f
		
						--when passed a uv vert, mesh trans returns the mesh vert
						meshTrans[uvVerts[1]] = meshVerts[1]
						meshTrans[uvVerts[2]] = meshVerts[2]
						meshTrans[uvVerts[3]] = meshVerts[3]
					)
		
					for v = numUVVerts to 1 by -1 do (
						uv = meshop.getMapVert $ mapChannel v
						coord = point2 (uv.x*width) ((1-uv.y)*height)
						color = getPixels image coord 1
						setVertColor $ meshtrans[v] color[1]
						update $
					)
				)--end ready if
			)--end undo off
		)--end bake pressed
	)--end rollout
	createDialog bakeRoll
)

macroScript surfaceShade category:"Ingenuity" tooltip:"Surface Shade"
(
	
	whiteInput = 1
	blackInput = 0
	whiteOutput = 1
	blackOutput = 0
	intensity = 1
	invertShade = false
	clampOcclusion = false
	vColors = #()
	vertCount = $.verts.count
	faceCount = $.faces.count

	fn dCopy fromArray toArray = (
		for i = fromArray.count to 1 by -1 do toArray[i] = fromArray[i]
	)

	--gets curvature information for mesh
	fn calcInfo = (
		--local vars
		baseObj = $.baseObject
		vertCount = $.verts.count
		faceCount = $.faces.count
		faceNormals = #()
		faceCenters = #()
		faceOffsets = #()
		vFaceCounts = #()

		for i = vertcount to 1 by -1 do vColors[i] = 0

		--the next two loops store normals and face counts
		--in arrays so they're not recalculated each iteration
		nextUpdate = 10
		progressStart "Collecting Normals:"
		progressUpdate 0.1
		
		--assign 0 to last element so that maxscript can allocate memory
		faceNormals[faceCount] = 0
		faceCenters[faceCount] = 0
		faceOffsets[faceCount] = 0
		for f = 1 to faceCount do (
			if (100.0 * f/faceCount) > nextUpdate then (
				progressUpdate (100.0 * f / faceCount)
				nextUpdate += 10
			)
			faceNormals[f] = polyOp.getFaceNormal baseObj f
			faceCenters[f] = polyOp.getFaceCenter baseObj f
			faceOffsets[f] = faceCenters[f] + faceNormals[f]*.05
		)
		progressEnd()

		nextUpdate = 10
		progressStart "Collecting Vert Info:"
		progressUpdate 0.1
		--memory allocation
		vFaceCounts[vertCount] = 0
		for v = 1 to vertCount do (
			if (100.0 * v/vertCount) > nextUpdate then (
				progressUpdate (100.0 * v / vertCount)
				nextUpdate += 10
			)
			vFaces = (polyop.getFacesUsingVert baseObj v) as array
			vFaceCounts[v] = vFaces.count
		)
		progressEnd()

		--then for each face we get it's normal and neighbors via vert
		--and find the dot product between the face and it's neighbors
		--keeping in mind that -1 is inverted or parallel and 0 is perpendicular
		--we store the average and use it later to colorize the mesh
		nextUpdate = 10
		progressStart "Calculating Curvature:"
		progressUpdate 0.1
		for f = 1 to faceCount do (
			if (100.0 * f/faceCount) > nextUpdate then (
				progressUpdate (100.0 * f / faceCount)
				nextUpdate += 10
			)

			--gets face vector and finds its neighbors
			faceVector = faceNormals[f]
			faceCenter = faceCenters[f]
			faceOffset = faceOffsets[f]
			faceVerts = polyOp.getVertsUsingFace baseObj f
			sFaces = (polyOp.getFacesUsingVert baseObj faceVerts) as array

			--calculates the dot product between the faceVector and its neighbors
			avg = 0.0
			for s = 1 to sFaces.count do (
			 centerDistance = distance faceCenter faceCenters[sFaces[s]]
			 offsetDistance = distance faceOffset faceOffsets[sFaces[s]]
			 difference = offsetDistance - centerDistance
			 --only add difference to average for differences less than zero (occluded)
				if clampOcclusion then (
				 	if difference < 0 then avg += difference
				) else (
					avg += difference
				)
			)
			avg /= sFaces.count

			--the dot average is then divided by the vert's face count and added to the vcolors array
			for v in faceVerts do vColors[v] += (avg / vFaceCounts[v])
		)
		progressEnd()

		--moves the vColors into an all-positive range
		vColorMin = amin vColors
		for v = 1 to vertCount do vColors[v] -= vColorMin

		--normalizes the range to 0-1
		vColorMax = amax vColors
		for v = 1 to vertCount do vColors[v] /= vColorMax

		--normalizes the range to -1 to 1
		for v = 1 to vertCount do vColors[v] = (vColors[v] - .5) * 2
	)--end calcInfo

	rollout shadeRoll "Shade Params" width:128 height:160
	(
		label lblWhiteInput "White Input:" pos:[12,4] width:64 height:16
		spinner spnWhiteInput "" pos:[76,4] width:48 height:16 range:[0.001,1,1] type:#float
		label lblBlackInput "Black Input:" pos:[12,24] width:64 height:16
		spinner spnBlackInput "" pos:[76,24] width:48 height:16 range:[0,0.999,0] type:#float
		label lblWhiteOutput "White Output:" pos:[4,44] width:72 height:16
		spinner spnWhiteOutput "" pos:[76,44] width:48 height:16 range:[0.001,1,1] type:#float scale:0.1
		label lblBlackOutput "Black Output:" pos:[4,65] width:72 height:16
		spinner spnBlackOutput "" pos:[76,65] width:48 height:16 range:[0,0.999,0] type:#float scale:0.1
		label lblIntensity "Intensity:" pos:[28,86] width:48 height:16
		spinner spnIntensity "" pos:[76,86] width:48 height:16 range:[1,10,1] type:#float
		label lblInvert "Invert:" pos:[36,105] width:40 height:16
		checkbox chkInvert "" pos:[76,105] width:16 height:16
		checkbox chkClamp "" pos:[76,122] width:16 height:16
		button btnRefresh "Refresh" pos:[12,140] width:52 height:16 toolTip:"Refresh vert color calculation"
		button btnShade "Shade" pos:[64,140] width:52 height:16 toolTip:"Shade object with last calculated vert colors."
		label lblClamp "Clamp:" pos:[36,122] width:40 height:16

		on spnwhiteInput changed val do
			whiteInput = spnwhiteInput.value
		on spnblackInput changed val do
			blackInput = spnblackInput.value
		on spnwhiteOutput changed val do
			whiteOutput = spnwhiteOutput.value
		on spnblackOutput changed val do
			blackOutput = spnblackOutput.value
		on spnIntensity changed val do
			intensity = spnIntensity.value
		on chkInvert changed state do
			invertShade = chkInvert.state
		on chkClamp changed state do
			clampOcclusion = chkClamp.state
		--init
		on shadeRoll open do (
			max modify mode
			clampOcclusion = false
			if selection.count == 1 and classof (modPanel.getCurrentObject()) == Editable_Poly then (
				calcInfo()
			) else (
				format "Please select an Editable Poly.\n"
			)
		)
		on btnShade pressed  do (
			max modify mode
			if selection.count==1 and classof (modPanel.getCurrentObject()) == Editable_Poly and vColors.count > 0 then (
				--color adjustment:
				--vColors start at a -1 to 1 range
				--the final value is calculated by multiplying intensity and calculating color shifts
				vEdit = #()
				dCopy vColors vEdit

				--adjust the range by multiplying the intensity
				for v = 1 to vertCount do vEdit[v] *= intensity

				--clamp the result from -1 to 1
				for v = 1 to vertCount do (
					if vEdit[v] < -1 then vEdit[v] = -1
					else if vEdit[v] > 1 then vEdit[v] = 1
				)

				--invert if necessary
				if invertShade then for v = 1 to vertCount do vEdit[v] *= -1

				--make the range positive
				for v = 1 to vertCount do
					vEdit[v] = (vEdit[v]+1)/2.0

				--move the colors into the blackInput - whiteInput range
		 		for v = 1 to vertCount do (
				 	vEdit[v] -= blackInput
				 	if vEdit[v] < 0 then vEdit[v] = 0
				)
				for v = 1 to vertCount do (
					vEdit[v] /= whiteInput
					if vEdit[v] > 1 then vEdit[v] = 1
				)

				--then adjust the range by the black and white offsets
				vMin = amin vEdit
				minDifference = vMin - blackOutput
				for v = 1 to vertCount do vEdit[v] -= minDifference

				vMax = amax vEdit
				maxDifference = whiteOutput / vMax
				for v = 1 to vertCount do vEdit[v] *= maxDifference

				--once we're done messing with the colors we assign them
				nextUpdate = 10
				progressStart "Assigning Shading:"
				progressUpdate 0.1
				for v = 1 to vertCount do (
					if (100.0 * v/vertCount) > nextUpdate then (
						progressUpdate (100.0 * v / vertCount)
						nextUpdate += 10
					)
					c = int(vEdit[v]*255)
					polyOp.setVertColor $ 0 $.verts[v] (color c c c)
				)

				$.showvertexcolors = true
				progressEnd()
				completeRedraw()
			) else (
				format "Please select an Editable Poly.\n"
			)--end editable poly if
		) --end shade pressed
		on btnRefresh pressed do (
			max modify mode
			if selection.count==1 and classof (modPanel.getCurrentObject()) == Editable_Poly then (
				vColors = #()
				calcInfo()
			) else (
				format "Please select an Editable Poly\.n"
			)
		)
	) --end rollout
	createDialog shadeRoll 128 160 350 300
)--end macroscript

--interactive vertex weight tool
--move the mouse left and right to decrease or increase vertex weight
--holding shift will slow the process, while ctrl will speed it up
macroScript vertexWeight category:"Ingenuity" tooltip:"Vertex Weight"
(
	on isEnabled return	( classOf selection[1].baseobject == Editable_Poly )
	on execute do (
		global origWeight = $.editablepoly.getvertexdata 1 1 true
		global curWeight = origWeight
		global baseX = mouse.pos.x
		
		fn vertWeight msg ir obj faceNum shift ctrl alt =
		(			
			if (msg == #freemove) then (
				curWeight = $.editablepoly.getvertexdata 1 1 true
				if (mouse.pos.x > basex) then (
					if shift then ($.EditablePoly.setVertexData 1 (curWeight + .05))
					else if ctrl then ($.EditablePoly.setVertexData 1 (curWeight + 1))
					else ($.EditablePoly.setVertexData 1 (curWeight + .25))
					
					baseX = mouse.pos.x
				) else (
					if shift then ($.EditablePoly.setVertexData 1 (curWeight - .05))
					else if ctrl then ($.EditablePoly.setVertexData 1 (curWeight - 1))
					else ($.EditablePoly.setVertexData 1 (curWeight - .25))
					
					baseX = mouse.pos.x
				)
			)
			
			if (msg == #mouseAbort) then (
				$.EditablePoly.setVertexData 1 origWeight
				return #end
			)
			if (msg != #mousePoint) then (
				return #continue
			) else (
				curWeight = $.editablepoly.getvertexdata 1 1 true
				return #end
			)
		)	
		vW = mouseTrack trackCallBack:vertWeight
	)
)

--interactive noise tool
--move the mouse left and right to decrease or increase noise
--holding shift will slow the process, while ctrl will speed it up
macroScript vertexNoise category:"Ingenuity" tooltip:"Vertex Noise"
(
	on isEnabled return	( classOf selection[1].baseobject == Editable_Poly )
	on execute do (

		global baseObj = $.baseobject
		
		global verts = polyop.getVertSelection baseObj as array
		global origPos = #()
		global vertVectors = #()
		global vertCount = verts.count

		for i = 1 to vertCount do
			origPos[i] = polyOp.getVert baseObj verts[i]				

		global randOffset = #()
		for i = 1 to vertCount do
			randOffset[i] = [(random -1.0 1.0), (random -1.0 1.0), (random -1.0 1.0)]
	
		global baseX = mouse.pos.x
		global offsetAmount = 0

		for i = 1 to vertCount do (
			iVector = 0
			iFaces = polyOp.getFacesUsingVert baseObj verts[i]
			iNormals = for f in iFaces collect polyOp.getFaceNormal baseObj f
				
			for n = 1 to iNormals.count do iVector += iNormals[n]

			iVector /= iNormals.count
			
			vertVectors[i] = iVector
		)

		fn vertNoise msg ir obj faceNum shift ctrl alt =
		(			
			if (msg == #freemove) then (
				if (mouse.pos.x > basex) then (
					if shift then offsetAmount = offsetAmount + .05
					else if ctrl then offsetAmount = offsetAmount + 1
					else offsetAmount = offsetAmount + .25

					baseX = mouse.pos.x
				) else (
					if shift then offsetAmount = offsetAmount - .05
					else if ctrl then offsetAmount = offsetAmount - 1
					else offsetAmount = offsetAmount - .25
		
					baseX = mouse.pos.x
				)
				for i = 1 to vertCount do
					polyOp.setVert baseObj verts[i] (origPos[i] + (vertVectors[i] * (randOffset[i]*offsetAmount)))
			)

			if (msg == #mouseAbort) then (
				for i = 1 to vertCount do
					polyOp.setVert baseObj verts[i] origPos[i]			

				return #end
			)	
			
			if (msg != #mousePoint) then return #continue
			else return #end
		)	
		vN = mouseTrack trackCallBack:vertNoise
	)
)

--interactive Push tool
--move the mouse left and right to decrease or increase push amount
--holding shift will slow the process, while ctrl will speed it up
macroScript vertexPush category:"Ingenuity" tooltip:"Vertex Push"
(
	on isEnabled return	( classOf selection[1].baseobject == Editable_Poly )
	on execute do (
		global baseObj = $.baseobject
		
		global verts = polyop.getVertSelection baseObj as array
		global origPos = #()
		global vertVectors = #()
		global vertCount = verts.count

		for i = 1 to vertCount do
			origPos[i] = polyOp.getVert baseObj verts[i]
	
		global baseX = mouse.pos.x
		global offsetAmount = 0

		for i = 1 to vertCount do (
			iVector = 0
			iFaces = polyOp.getFacesUsingVert baseObj verts[i]
			iNormals = for f in iFaces collect polyOp.getFaceNormal baseObj f
				
			for n = 1 to iNormals.count do iVector += iNormals[n]

			iVector /= iNormals.count
			
			vertVectors[i] = iVector
		)
		
		fn vertNoise msg ir obj faceNum shift ctrl alt =
		(			
			if (msg == #freemove) then (
				if (mouse.pos.x > basex) then (
					if shift then offsetAmount = offsetAmount + .05
					else if ctrl then offsetAmount = offsetAmount + 1
					else offsetAmount = offsetAmount + .25
					
					baseX = mouse.pos.x
				) else (
					if shift then offsetAmount = offsetAmount - .05
					else if ctrl then offsetAmount = offsetAmount - 1
					else offsetAmount = offsetAmount - .25
		
					baseX = mouse.pos.x
				)
				for i = 1 to vertCount do
					polyOp.setVert baseObj verts[i] (origPos[i] + (vertVectors[i] * offsetAmount))
			)

			if (msg == #mouseAbort) then (
				for i = 1 to vertCount do
					polyOp.setVert baseObj verts[i] origPos[i]			

				return #end
			)

			if (msg != #mousePoint) then return #continue
			else return #end
		)
		vN = mouseTrack trackCallBack:vertNoise
	)
)

--corner rounder 
--only works for corners with two edges
--used to create arches and other rounded elements
--note: somewhat buggy and finicky
macroscript roundCorner category:"Ingenuity" tooltip:"Round Corner"
(
	--rollout holders
	global segments = 8
	global xMult = 1
	global yMult = 1
	global radius = 5
	global inv = false
	global flip = false
	global switch = false

	fn getCommon items fromType toType =
	(
		baseObj = $.baseObject
    	common = #{}
    	commonList = #()

		for i = 1 to polyOp.getNumEdges $.baseObject do
			commonList[i] = 0

		for i in items do (
			if (fromType == #Vertex) then (
				if (toType == #Edge) then (
					converted = polyOp.getEdgesUsingVert baseObj i
				) else if (toType == #Face) then (
					converted = polyOp.getFacesUsingVert baseObj i
				)
			) else if (fromType == #Edge) then (
				if (toType == #Vertex) then (
					converted = polyOp.getVertsUsingEdge baseObj i
				) else if (toType == #Face) then (
					converted = polyOp.getFacesUsingEdge baseObj i
				)
			) else if (fromType == #Face) then (
				if (toType == #Vertex) then (
					converted = polyOp.getVertsUsingFace baseObj i
				) else if (toType == #Edge) then (
					converted = polyOp.getEdgesUsingFace baseObj i
				)
			)
			for n in converted do
				commonList[n] += 1
		)
		for i = 1 to commonList.count do
			if (commonList[i] > 1) then	common[i] = true

		--return
		common
	)

	fn threePointMatrix p1 p2 p3 =
	(
		v1 = normalize (p2 - p1)
		v3 = normalize (cross v1 (normalize (p3 - p1)))
		v2 = normalize (cross v3 v1)

		return matrix3 v1 v2 v3 p1
	)

    on isEnabled return ( selection.count==1 and classOf selection[1].baseobject == Editable_Poly)
	on execute do
	(
		--other vars
		global newVert = #()
		global baseObj = $
		global baseMesh = $
		global uScale = units.SystemScale

		global oldCoord = set coordSys world
		undo off global rGrid = grid length:50 width:50 grid:10
		global cornerVertPos = [0,0,0]
		global vertOnePos = [0,0,0]
		global vertTwoPos = [0,0,0]
		global oldGridPos = [0,0,0]
		global previousGrid = activeGrid

		rollout cornerRoll "Round Corners" width:256 height:176
		(
			label lblSegments "Segments:" pos:[72,8] width:64 height:16
			spinner spnSegments "" pos:[72,24] width:56 height:16 range:[1,256,segments] type:#integer scale:1
			label lblRadius "Radius:" pos:[160,8] width:64 height:16
			spinner spnRadius "" pos:[160,24] width:56 height:16 range:[0,999999,radius*uScale] type:#worldunits scale:1
			label lblXMult "x Multiplier:" pos:[72,48] width:64 height:16
			spinner spnXMult "" pos:[72,64] width:56 height:16 range:[0,100,xMult] type:#float scale:0.1
			label lblYMult "y Multiplier:" pos:[72,88] width:64 height:16
			spinner spnYMult "" pos:[72,104] width:56 height:16 range:[0,100,yMult] type:#float scale:0.1
			button btnSwap "Swap" pos:[16,80] width:48 height:24
			checkbox chkInvert "Invert" pos:[160,56] width:56 height:16 checked:inv
			checkbox chkFlip "Flip" pos:[160,80] width:56 height:16 checked:flip
			checkbox chkSwitch "Switch" pos:[160,104] width:56 height:16 checked:switch
			button btnApply "Apply" pos:[24,136] width:64 height:24
			button btnOk "OK" pos:[96,136] width:64 height:24
			button BtnCancel "Cancel" pos:[168,136] width:64 height:24
			Timer tmrUpdate "Timer" pos:[0,0] width:24 height:24 interval:100

			on spnSegments changed val do (
				--number of points along the arc
				segments = spnSegments.value
			)
			on spnRadius changed val do(
				--radius from center
				oldRadius = radius
				radius = spnRadius.value/uScale
				radiusDiff = radius - oldRadius
				undo off rGrid.pos = [rGrid.pos.x - (radiusDiff*xMult), rGrid.pos.y - (radiusDiff*xMult), rGrid.pos.z]

				redrawViews()
			)
			on spnXMult changed val do (
				--amount to stretch along the x axis (grid relative)
				oldXMult = xMult
				xMult = spnXMult.value
				xMultDiff = xMult - oldXMult
				undo off rGrid.pos = [rGrid.pos.x - (radius*xMultDiff), rGrid.pos.y, rGrid.pos.z]
			)
			on spnYMult changed val do (
				--amount to stretch along the y axis (grid relative)
				oldYMult = yMult
				yMult = spnYMult.value
				yMultDiff = yMult - oldYMult
				undo off rGrid.pos = [rGrid.pos.x, rGrid.pos.y - (radius*yMultDiff), rGrid.pos.z]
			)
			on btnSwap pressed do (
				oldXMult = xMult
				oldYMult = yMult
				swap xMult yMult
				xMultDiff = xMult - oldXMult
				yMultDiff = yMult - oldYMult
				undo off rGrid.pos = [rGrid.pos.x - (radius*xMultDiff), rGrid.pos.y - (radius*yMultDiff), rGrid.pos.z]

				spnXMult.value = xMult
				spnYMult.value = yMult
			)
			on chkInvert changed state do (
				if chkInvert.state then (
					inv = true
					in coordSys world oldGridPos = rGrid.pos
				) else (
					inv = false
					in coordSys world rGrid.pos = oldGridPos
				)
			)
			on chkFlip changed state do (
				flip = chkFlip.state
			)
			on chkSwitch changed state do (
				switch = chkSwitch.state
			)
			on btnApply pressed do (
				--same thing as ok
				badVerts = #{}
				step = 90.0 / segments
				for n = 1 to 64 do
					badVerts[newVert[n]] = true
				if flip then (
					for angle = 0 to 90 by step do
						badVerts[newVert[63-(angle/step)+1]] = false
				) else (
					for angle = 0 to 90 by step do
						badVerts[newVert[(angle/step)+1]] = false
				)
				baseObj.setSelection #Vertex badVerts
				baseObj.EditablePoly.Remove()

				destroyDialog cornerRoll
			)
			on btnOk pressed do (
				--closes dialog and removes unused verts
				badVerts = #{}
				step = 90.0 / segments
				for n = 1 to 64 do
					badVerts[newVert[n]] = true
				if flip then (
					for angle = 0 to 90 by step do
						badVerts[newVert[63-(angle/step)+1]] = false
				) else (
					for angle = 0 to 90 by step do
						badVerts[newVert[(angle/step)+1]] = false
				)
				baseObj.setSelection #Vertex badVerts
				baseObj.EditablePoly.Remove()

				destroyDialog cornerRoll
			)
			on BtnCancel pressed do (
				--last undo, release callback, and close
				destroyDialog cornerRoll
				max undo
			)
			on cornerRoll open do(
				redrawViews()
			)
			on cornerRoll close do (
				activeGrid = previousGrid
				undo off delete rGrid
			)
			on tmrUpdate tick  do
			(
				--does the actual positioning of the verts
				--every 10th of a second
				step = 90.0 / segments

				if inv then in coordSys world rGrid.pos = cornerVertPos

				if switch then (
					for v = 1 to 64 do
							in coordSys world polyOp.setVert baseObj newVert[v] vertTwoPos
				) else (
					for v = 1 to 64 do
						in coordSys world polyOp.setVert baseObj newVert[v] vertOnePos
				)

				if flip then (
					if inv then (
						for angle = 0 to 90 by step do
							polyOp.setVert baseObj newVert[63-(angle/step)+1] \
								[-(radius*sin(angle))*xMult, \
								-(radius*cos(angle))*yMult,0]
					) else (
						for angle = 0 to 90 by step do
							polyOp.setVert baseObj newVert[63-(angle/step)+1] \
								[(radius*sin(angle))*xMult, \
								(radius*cos(angle))*yMult,0]
					)
				) else (
					if inv then (
						for angle = 0 to 90 by step do
							polyOp.setVert baseObj newVert[(angle/step)+1] \
								[-(radius*sin(angle))*xMult, \
								-(radius*cos(angle))*yMult,0]
					) else (
						for angle = 0 to 90 by step do
							polyOp.setVert baseObj newVert[(angle/step)+1] \
								[(radius*sin(angle))*xMult, \
								(radius*cos(angle))*yMult,0]
					)
				)
				redrawViews()
			)
		)
		verts = polyOp.getVertSelection baseObj as array

		activegrid = undefined

		cornerVert = verts[1]
		cornerVertPos = polyop.getVert baseObj cornerVert

		--outer verts 'grown' from corner vert
		--corner vert is then removed from the set
		--and the result is converted into an array
		outerVerts = polyOp.getVertsUsingEdge baseObj \
					(polyOp.getEdgesUsingVert baseObj verts)
		outerVerts[cornerVert] = false
		outerVerts = outerVerts as array

		vertOnePos = polyop.getVert baseObj outerVerts[1]
		vertTwoPos = polyop.getVert baseObj outerVerts[2]

		--grid setup
		undo off rGrid.transform = threePointMatrix cornerVertPos vertOnePos vertTwoPos

		arcEdge = amin ((polyOp.getEdgesUsingVert baseObj cornerVert) as array)

		$.EditablePoly.SetSelection #Vertex #{cornerVert}
		baseObj.EditablePoly.Remove ()

		--begin grid coord sys operations
		--from here on everything is based from the center of the grid
		set coordsys grid
		undo off (
			activeGrid = rGrid
			rotate rGrid (eulerangles 0 0 180)

			cX = rGrid.pos.x - (radius*xMult)
			cY = rGrid.pos.y - (radius*yMult)
			cZ = rGrid.pos.z

			center = [cX,cY,cZ]
			rGrid.pos = center
		)
		for v = 1 to 64 do
			newVert[v] = polyOp.divideEdge baseObj arcEdge 0

		createDialog cornerRoll 256 176 800 300
		undo off hide rGrid
	)
)

--roundly chamfers edges
macroscript roundChamfer category:"Ingenuity" tooltip:"Round Chamfer"
(
	global r = 5
	global iter = 2
	global divAngle = 22.5
	global wholeMesh = false

	on isEnabled return (selection.count==1 and classOf selection[1].baseobject == Editable_Poly)
	on execute do (

		global first = true
		global doUpdate = true

		rollout chamRoll "Rounded Chamfer" width:184 height:136
		(
			spinner spnRadius "Radius:" pos:[48,8] width:88 height:16 range:[0,99999,r] type:#worldunits scale:1
			spinner spnIter "Iterations:" pos:[40,32] width:96 height:16 range:[0,64,iter] type:#integer scale:1
			spinner spnAngle "Angle:" pos:[56,56] width:80 height:16 range:[0,360,divAngle] type:#float scale:1
			checkbox chkWholeMesh "Whole Mesh" pos:[48,80] width:88 height:16 checked:wholeMesh
			Timer tmrUpdate "Timer" pos:[0,0] width:24 height:24 interval:100
			button btnOkay "OK" pos:[32,104] width:56 height:24
			button BtnCancel "Cancel" pos:[96,104] width:56 height:24

			on spnRadius changed val do (
				r = spnRadius.value
				doUpdate = true
			)
			on spnIter changed val do (
				iter = spnIter.value
				doUpdate = true
			)
			on spnAngle changed val do (
				divAngle = spnAngle.value
				doUpdate = true
			)
			on chkWholeMesh changed state do (
				wholeMesh = chkWholeMesh.state
				doUpdate = true
			)
			on tmrUpdate tick do (
				--main code block
				--runs on undos for the time being

				if doUpdate then (
					if first then first = false else (max undo)
					
					n = divAngle
					

					undo "update" on (
						for a = 1 to iter do (
							--visit the tutorials section at gotogrant.com for a full explanation
							--of the chamfer amount calculation
							z = 180-90-n
							i = 180 - 2*z
							h=2*r*tan(n)
							amount=(h/2)/cos(i)

							if wholeMesh then (
								if (subObjectLevel == 1) then polyOp.chamferVerts $ #{1..(polyOp.getNumVerts $)} amount 1
								else if (subObjectLevel == 2) then polyOp.chamferEdges $ #{1..(polyOp.getNumEdges $)} amount 1
							) else(
								if (subObjectLevel == 1) then polyOp.chamferVerts $ (polyOp.getVertSelection $) amount 1
								else if (subObjectLevel == 2) then polyOp.chamferEdges $ (polyOp.getEdgeSelection $) amount 1
							)

							n /= 2
						)
					)

					redrawViews()
					doUpdate = false
				)
			)
			on btnOkay pressed do (
				--destroy dialog
				destroyDialog chamRoll
			)
			on btnCancel pressed do (
				--one last undo
				max undo
				destroyDialog chamRoll
			)
		)

		createDialog chamRoll 184 136 800 300
	)
)

--returns length of selected edges
macroscript measurer category:"Ingenuity" tooltip:"Edge Length"
(
	on isEnabled return (selection.count==1 and classOf selection[1].baseobject == Editable_Poly)
	on execute do (
		global baseObj = $
		rollout measureRoll "Edg Len" width:112 height:64 (
			edittext edtLength "Length" pos:[8,8] width:96 height:16
			button btnOk "OK" pos:[40,32] width:48 height:24
			timer tmrUpdate "Timer" pos:[8,32] width:24 height:24 interval:100

			on btnOk pressed  do
				destroyDialog measureRoll
			on tmrUpdate tick do (
				len = 0
				try (
					edges = polyOp.getEdgeSelection baseObj
					for e in edges do (
						verts = (polyOp.getVertsUsingEdge baseObj e) as array
						len += distance (polyOp.getVert baseObj verts[1]) (polyOp.getVert baseObj verts[2])
					)
					if (edtLength.text != (len as string)) then
						edtLength.text = (len as string)
				) catch()
			)
		)
		createDialog measureRoll 112 64 800 300
	)
)

--places and activates a grid and switches to the grid coordinate system
--this version is placed on objects via ray intersection
macroScript gridPlace category:"Ingenuity" tooltip:"Grid Place"
(
	on isEnabled return	( selection.count==1 )
	on execute do 
	(
		global newGrid = grid length:50 width:50 grid:10
		global prevGrid = activeGrid		

		fn objNormal msg ir obj faceNum shift ctrl alt =
		(
			if (msg == #freeMove) then (
				if (ir != undefined) then (
					newGrid.pos = ir.pos
					newGrid.dir = ir.dir
					if ctrl then in coordSys local (rotate newGrid (eulerangles 90 0 0))
					if shift then in coordSys local (rotate newGrid (eulerangles 0 90 0))
					return #continue
				) else (
					return #continue
				)
			)
			
			if (msg == #mouseAbort) then (
				delete newGrid
				Toolmode.coordsys #World
				activeGrid = prevGrid
				return #end		
			)
	
			if (msg != #mousePoint) then (
				return #continue
			)
			else (
				Toolmode.coordsys #Grid
				activeGrid = newGrid
				return #end
			)
		)	

		gP = mouseTrack on:$ trackCallBack:objNormal snap:#3d
	)
)	

--places and activates a grid and switches to the grid coordinate system
--this version is placed on vertecies via snap
macroScript gridPlaceSnap category:"Ingenuity" tooltip:"Grid Place Snap"
(
	on isEnabled return	( selection.count==1 )
	on execute do 
	(
		global newGrid = grid length:50 width:50 grid:10
		global prevGrid = activeGrid		

		fn objNormal msg ir obj faceNum shift ctrl alt =
		(
			if (msg == #freeMove) then (
				if (ir != undefined) then (
					newGrid.pos = ir.pos
					newGrid.dir = ir.dir
					if ctrl then in coordSys local (rotate newGrid (eulerangles 90 0 0))
					if shift then in coordSys local (rotate newGrid (eulerangles 0 90 0))
					return #continue
				) else (
					return #continue
				)
			)
			
			if (msg == #mouseAbort) then (
				delete newGrid
				Toolmode.coordsys #World
				activeGrid = prevGrid
				return #end		
			)
	
			if (msg != #mousePoint) then (
				return #continue
			) else (
				Toolmode.coordsys #Grid
				activeGrid = newGrid
				return #end
			)
		)	

		gP = mouseTrack trackCallBack:objNormal snap:#3d
	)
)

--render mental ray ambient occlusion pass
--converts materials to render AO
--keeps displacement map and bump maps and their respective amounts
--to use select an object with mental ray ao material then run
macroScript MRAO category:"Ingenuity" tooltip:"MR AO Pass"
(
if ($ != undefined) then
	if ($.material != undefined) then (
		--environment setup
		backgroundColor = color 255 255 255
		useEnvironmentMap = off

		--mat get basemat so it can be assigned if no bump or displacement is found
		--also get the ao map so that it's instanced across the board
		baseMat = $.material
		aoMap = $.material.Surface

		--array for objs that didn't have the proper shader
		--(at this time either standard mat or arch and design)
		noWork = #()

		--get all the valid objects in the scene
		--items are removed from this list as their scene materials are found
		--and AO mats are assigned
		--if the object has no material then it's dead weight
		--and is added to slackers list and selected at the end
		objs = #()
		for o in $* do (
			if not(o.ishidden or o.isfrozen) then (
				if (o.material != undefined) then
		 			append objs o
		 	)
		)

		--finds $ and removes it from the obj list
		deleteItem objs (findItem objs $)

		--set initial count for progress bar updating
		initialCount = objs.count

		--for canceling via progress bar
		keepGoing = true

		--for keeping track of number of unique materials
		--printed at the end
		uniqueMats = 0

		progressStart "Assigning MR AO Mats..."

		--main loop, loops through each of the remaining objects in the obj list
		while (objs.count > 0 and keepGoing == true) do (
			--progress bar updating
			keepGoing = progressUpdate (100.0 - (100.0 * objs.count / initialCount))

			uniqueMats += 1

			--get current object
			o = objs[1]

			--first we get some information about o's material
			--if it's a standard material check for displacement, bump, and opacity maps
			if (classof o.material == StandardMaterial) then (
				if (o.material.bumpMapEnable and o.material.bumpMap != undefined) then (
					bumpOn = true
					bumpMap = o.material.bumpMap
					bumpAmt = (o.material.bumpMapAmount)/10
				) else bumpOn = false

				if (o.material.displacementMapEnable and o.material.displacementMap != undefined) then (
					dispMap = o.material.displacementMap
					dispAmt = o.material.displacementMapAmount / 10
					dispOn = true
				) else dispOn = false

				if (o.material.opacityMapEnable and o.material.opacityMap != undefined) then (
					cutoutMap = o.material.opacityMap
					cutoutOn = true
				) else cutoutOn = false

			--if it's an arch and design material check for displacement, bump, and cutout maps
			) else if (classof o.material == Arch___Design__mi) then (
				if (o.material.displacement_map_on and o.material.displacement_map != undefined) then (
					dispMap = o.material.displacement_map
					dispAmt = o.material.displacement_map_amt
					dispOn = true
				) else dispOn = false

      			if (o.material.bump_map_on and o.material.bump_map != undefined) then (
					bumpMap = o.material.bump_map
					bumpAmt = o.material.bump_map_amt
					bumpOn = true
				) else bumpOn = false

				if (o.material.cutout_map_on and o.material.cutout_map != undefined) then (
					cutoutMap = o.material.cutout_map
					cutoutOn = true
				) else cutoutOn = false

			--these are the only two shaders supported at this time
			--use 'classOf $.material' to show the material class name and
			--'showProerties $.material' to find map names and add other shaders
			--...and so if it's not a standard or arch and design material
			--then bump, disp, and cutout are false
			--and the obj is added to the noWork array, to be selected at the end
			) else (
				dispOn = false
				bumpOn = false
				cutoutOn = false
				append noWork o
			)

			--so now we know what material we have, but it's often shared among many
			--objects in the scene, so we'll find those objects and assign the same
			--AO mat to them as well

			--this bit gets the material name and sets the endpoint
			--the material name has stuff tacked on the front
			--that we don't need, so we have to parse it
			matName = o.material as string
			endPoint = 1

			for a = 1 to matName.count do if (matName[a] == ":") then endPoint = a-1
			matName = substring matName 1 endPoint

			--array of objects sharing o's material, filled in the next loop
			s = #()

			--this loop finds the scene objects that have the same
			--material as o
			--it finds o as well because it has not been removed from the obj list yet
			for comp in objs do (
				endPoint = 1
				compMatName = comp.material as string
				for a = 1 to compMatName.count do if (compMatName[a] == ":") then endPoint = a-1
				compMatName = substring compMatName 1 endPoint

				--if mats are a match then remove s from the obj list
				--and add it to the shared list
				if (matName == compMatName) then (
					deleteItem objs (findItem objs comp)
					append s comp
				)
			)

			--mat assignment
--			if cutoutOn then (
				if (dispOn and bumpOn) then (
					s.material = Arch___Design__mi mapM0:aoMap \
						displacement_map_on:true \
						displacement_map:dispMap \
						displacement_map_amt:dispAmt \
						bump_map_on:true \
						bump_map:bumpMap\
						bump_map_amt:bumpAmt \
						cutout_map_on:true \
						cutout_map:cutoutMap \
						refl_weight:0
				) else if (dispOn) then (
					s.material = Arch___Design__mi mapM0:aoMap \
						displacement_map_on:true \
						displacement_map:dispMap \
						displacement_map_amt:dispAmt \
						cutout_map_on:true \
						cutout_map:cutoutMap \
						refl_weight:0
				) else if (bumpOn) then (
					s.material = Arch___Design__mi mapM0:aoMap \
						bump_map_on:true \
						bump_map:bumpMap\
						bump_map_amt:bumpAmt \
						cutout_map_on:true \
						cutout_map:cutoutMap \
						refl_weight:0
				) else (
					s.material = Arch___Design__mi mapM0:aoMap \
						cutout_map_on:true \
						cutout_map:cutoutMap \
						refl_weight:0
				)
/* 			) else if (dispOn and bumpOn) then (
* 				s.material = mental_ray surface:aoMap \
* 					displaceOn:true \
* 					displacement:(Displacement_3D__3dsmax map:dispMap \
* 					mapAmount:dispAmt) \
* 					bumpOn:true \
* 					bump:(Bump__3dsmax map:bumpMap \
* 					multiplier:bumpAmt )
* 			) else if (dispOn) then (
* 				s.material = mental_ray surface:aoMap \
* 					displaceOn:true \
* 					displacement:(Displacement_3D__3dsmax map:dispMap \
* 					mapAmount:dispAmt) \
* 			) else if (bumpOn) then (
* 				s.material = mental_ray surface:aoMap \
* 					bumpOn:true \
* 					bump:(Bump__3dsmax map:bumpMap \
* 					multiplier:bumpAmt)
* 			) else (
* 				--if cutout, bump, or disp isn't on then obj gets an instance
* 				--of the original AO mat
* 				s.material = baseMat
* 			)  --end mat assignment
*/
		)  --end obj loop
		
		--remove progress bar
		progressEnd()

		print "Unique Mats:"
		print uniqueMats

		--select the items that didn't have a proper shader
		select noWork

	) else print "Select object with base AO material"
else print "Please select an object with base AO material"
) --end macroscript
