--Make planar hotkeys
macroScript MakePlanarX category:"Ingenuity" tooltip:"Make Planar X"
(
	if (classof (modPanel.getCurrentObject()) == Edit_Poly) then (
		for sel in $ do (
			sel.modifiers["Edit Poly"].setOperation #MakePlanarInX
			sel.modifiers[#Edit_Poly].Commit ()
		)
	) else if (classof (modPanel.getCurrentObject()) == Editable_Poly) then (
		$.EditablePoly.MakePlanarIn #X
	)
)
macroScript MakePlanarY category:"Ingenuity" tooltip:"Make Planar Y"
(
	if (classof (modPanel.getCurrentObject()) == Edit_Poly) then (
		for sel in $ do (
			sel.modifiers["Edit Poly"].setOperation #MakePlanarInY
			sel.modifiers[#Edit_Poly].Commit ()
		)
	) else if (classof (modPanel.getCurrentObject()) == Editable_Poly) then (
		$.EditablePoly.MakePlanarIn #Y
	)
)
macroScript MakePlanarZ category:"Ingenuity" tooltip:"Make Planar Z"
(
	if (classof (modPanel.getCurrentObject()) == Edit_Poly) then (
		for sel in $ do (
			sel.modifiers["Edit Poly"].setOperation #MakePlanarInZ
			sel.modifiers[#Edit_Poly].Commit ()
		)
	) else if (classof (modPanel.getCurrentObject()) == Editable_Poly) then (
		$.EditablePoly.MakePlanarIn #Z
	)
)

--turns of constraints, since max doesn't do it properly for edit poly modifiers... sigh...
macroScript ConstrainNone category:"Ingenuity" tooltip:"Contrain to None"
(
	if (classof (modPanel.getCurrentObject()) == Edit_Poly) then (
		if (selection.count > 1) then (
			$[1].modifiers["Edit Poly"].constrainType = 0
		) else (
			$.modifiers["Edit Poly"].constrainType = 0
		)
	) else if (classof (modPanel.getCurrentObject()) == Editable_Poly) then (
		$.constrainType = 0
	)
)
--toggles select by angle and ignore backfacing
macroScript SelectByAngleToggle category:"Ingenuity" tooltip:"Select by Angle Toggle"
(
	if (classof (modPanel.getCurrentObject()) == Edit_Poly) then (
		if (selection.count > 1) then (
			$[1].modifiers["Edit Poly"].selectByAngle = not $[1].modifiers["Edit Poly"].selectByAngle
			$[1].modifiers["Edit Poly"].ignoreBackfacing = not $[1].modifiers["Edit Poly"].ignoreBackfacing
		) else (
			$.modifiers["Edit Poly"].selectByAngle = not $.modifiers["Edit Poly"].selectByAngle
			$.modifiers["Edit Poly"].ignoreBackfacing = not $.modifiers["Edit Poly"].ignoreBackfacing
		)
	) else if (classof (modPanel.getCurrentObject()) == Editable_Poly) then (
		$.selectByAngle = not $.selectByAngle
		$.ignoreBackfacing = not $.ignoreBackfacing
	)
)

--Soft selection hotkeys
macroScript GrowSoftSelection10 category:"Ingenuity" tooltip:"Grow Soft Sel. by 10"
(
	if (classof (modPanel.getCurrentObject()) == Edit_Poly) then (
		if (selection.count > 1) then
			$[1].modifiers["Edit Poly"].falloff += 10
		else
			$.modifiers["Edit Poly"].falloff += 10
	) else if (classof (modPanel.getCurrentObject()) == Editable_Poly) then (
		$.falloff += 10
	)
)
macroScript GrowSoftSelection1 category:"Ingenuity" tooltip:"Grow Soft Sel. by 1"
(
	if (classof (modPanel.getCurrentObject()) == Edit_Poly) then (
		if (selection.count > 1) then
			$[1].modifiers["Edit Poly"].falloff += 1
		else
			$.modifiers["Edit Poly"].falloff += 1
	) else if (classof (modPanel.getCurrentObject()) == Editable_Poly) then (
		$.falloff += 1
	)
)
macroScript ShrinkSoftSelection10 category:"Ingenuity" tooltip:"Shrink Soft Sel. by 10"
(
	if (classof (modPanel.getCurrentObject()) == Edit_Poly) then (
		if (selection.count > 1) then
			if ($[1].modifiers["Edit Poly"].falloff > 10) then $[1].modifiers["Edit Poly"].falloff -= 10
		else
			if ($.modifiers["Edit Poly"].falloff > 10) then $.modifiers["Edit Poly"].falloff -= 10
	) else if (classof (modPanel.getCurrentObject()) == Editable_Poly) then (
		if ($.falloff > 10) then $.falloff -= 10
	)
)
macroScript ShrinkSoftSelection1 category:"Ingenuity" tooltip:"Shrink Soft Sel. by 1"
(
	if (classof (modPanel.getCurrentObject()) == Edit_Poly) then (
		if (selection.count > 1) then
			if ($[1].modifiers["Edit Poly"].falloff > 1) then $[1].modifiers["Edit Poly"].falloff -= 1
		else
			if ($.modifiers["Edit Poly"].falloff > 1) then $.modifiers["Edit Poly"].falloff -= 1
	) else if (classof (modPanel.getCurrentObject()) == Editable_Poly) then (
		if ($.falloff > 1) then $.falloff -= 1
	)
)
macroScript GrowPinch category:"Ingenuity" tooltip:"Grow Pinch by .25"
(
	if (classof (modPanel.getCurrentObject()) == Edit_Poly) then (
		if (selection.count > 1) then
			$[1].modifiers["Edit Poly"].pinch += .25
		else
			$.modifiers["Edit Poly"].pinch += .25
	) else if (classof (modPanel.getCurrentObject()) == Editable_Poly) then (
		$.pinch += .25
	)
)
macroScript ShrinkPinch category:"Ingenuity" tooltip:"Shrink Pinch by .25"
(
	if (classof (modPanel.getCurrentObject()) == Edit_Poly) then (
		if (selection.count > 1) then
			$[1].modifiers["Edit Poly"].pinch -= .25
		else
			$.modifiers["Edit Poly"].pinch -= .25
	) else if (classof (modPanel.getCurrentObject()) == Editable_Poly) then (
		$.pinch -= .25
	)
)

--//edge and vertex weight scripts
macroScript IncreaseEdgeWeight category:"Ingenuity" tooltip:"Increase Edge Weight"
(
 	on isEnabled return	( selection.count==1 and classOf selection[1].baseobject == Editable_Poly )
	on execute do
  (
    $.EditablePoly.setEdgeData 1 1
    numSel = 0
    allSame = false
    edgeWeight = $.EditablePoly.getEdgeData 0 numSel allSame
    $.EditablePoly.setEdgeData 0 (edgeWeight + .5)
  )
)
macroScript DecreaseEdgeWeight category:"Ingenuity" tooltip:"Decrease Edge Weight"
(
 	on isEnabled return	( selection.count==1 and classOf selection[1].baseobject == Editable_Poly )
	on execute do
  (
    $.EditablePoly.setEdgeData 1 1
    numSel = 0
    allSame = false
    edgeWeight = $.EditablePoly.getEdgeData 0 numSel allSame
    if (edgeWeight - .5 <= 0) then
    (
      $.EditablePoly.setEdgeData 1 1
      $.EditablePoly.setEdgeData 0 0
    )
    else
    (
      $.EditablePoly.setEdgeData 0 (edgeWeight - .5)
    )
  )
)
macroScript RemoveEdgeCrease category:"Ingenuity" tooltip:"Remove Edge Crease"
(
 	on isEnabled return	( selection.count==1 and classOf selection[1].baseobject == Editable_Poly )
	on execute do
  (
    $.EditablePoly.setEdgeData 1 0
    $.EditablePoly.setEdgeData 0 1
  )
)
macroScript RemoveVertWeight category:"Ingenuity" tooltip:"Remove Vert Weight"
(
 	on isEnabled return	( selection.count==1 and classOf selection[1].baseobject == Editable_Poly )
	on execute do ( $.EditablePoly.setVertexData 1 1 )
)

--Sub-object selction scripts
macroScript GotoVertex_KeepSel category:"Ingenuity" tooltip:"SubObj 1 w/ Selection"
(
	fromlevel = case subobjectLevel of (
		1: #Vertex
		2: #Edge
		3: #Border
		4: #Face
		5: #Element
	)
	undo "ConvertSelection" on (
	try (
		if (classof (modPanel.getCurrentObject()) == Edit_Poly) then (
			itemList = #()
			--get item count (errors if only one things is selected)
			if ($ != undefined) then try(itemCount = $.count)catch(itemCount = 1)
			else itemCount = 0
			--if somethings selected then
			if (itemCount > 1) then for i = 1 to itemCount do itemList[i] = $[i]
			else if (itemCount == 1) then itemList[1] = $

			for sel in itemList do (
				select sel
				$.modifiers["Edit Poly"].ConvertSelection fromlevel #Vertex
			)
			select itemList
		) else if (classof (modPanel.getCurrentObject()) == Editable_Poly) then (
			$.EditablePoly.ConvertSelection fromlevel #Vertex
		)
	) catch()
	)
	subobjectLevel = 1
)
macroScript GotoEdge_KeepSel category:"Ingenuity" tooltip:"SubObj 2 w/ Selection"
(
	fromlevel = case subobjectLevel of (
		1: #Vertex
		2: #Edge
		3: #Border
		4: #Face
		5: #Element
	)
	undo "ConvertSelection" on (
	try (
		if (classof (modPanel.getCurrentObject()) == Edit_Poly) then (
			itemList = #()
			--get item count (errors if only one things is selected)
			if ($ != undefined) then try(itemCount = $.count)catch(itemCount = 1)
			else itemCount = 0
			--if somethings selected then
			if (itemCount > 1) then for i = 1 to itemCount do itemList[i] = $[i]
			else if (itemCount == 1) then itemList[1] = $

			for sel in itemList do (
				select sel
				$.modifiers["Edit Poly"].ConvertSelection fromlevel #Edge
			)
			select itemList
		) else if (classof (modPanel.getCurrentObject()) == Editable_Poly) then (
			$.EditablePoly.ConvertSelection fromlevel #Edge
		)
	) catch()
	)
	subobjectLevel = 2
)
macroScript GotoBorder_KeepSel category:"Ingenuity" tooltip:"SubObj 3 w/ Selection"
(
	fromlevel = case subobjectLevel of (
		1: #Vertex
		2: #Edge
		3: #Border
		4: #Face
		5: #Element
	)
	undo "ConvertSelection" on (
	try (
		if (classof (modPanel.getCurrentObject()) == Edit_Poly) then (
			itemList = #()
			--get item count (errors if only one things is selected)
			if ($ != undefined) then try(itemCount = $.count)catch(itemCount = 1)
			else itemCount = 0
			--if somethings selected then
			if (itemCount > 1) then for i = 1 to itemCount do itemList[i] = $[i]
			else if (itemCount == 1) then itemList[1] = $

			for sel in itemList do (
				select sel
				$.modifiers["Edit Poly"].ConvertSelection fromlevel #Border
			)
			select itemList
		) else if (classof (modPanel.getCurrentObject()) == Editable_Poly) then (
			$.EditablePoly.ConvertSelection fromlevel #Border
		)
	) catch()
	)
	subobjectLevel = 3
)
macroScript GotoPolygon_KeepSel category:"Ingenuity" tooltip:"SubObj 4 w/ Selection"
(
	fromlevel = case subobjectLevel of (
		1: #Vertex
		2: #Edge
		3: #Border
		4: #Face
		5: #Element
	)
	undo "ConvertSelection" on (
	try (
		if (classof (modPanel.getCurrentObject()) == Edit_Poly) then (
			itemList = #()
			--get item count (errors if only one things is selected)
			if ($ != undefined) then try(itemCount = $.count)catch(itemCount = 1)
			else itemCount = 0
			--if somethings selected then
			if (itemCount > 1) then for i = 1 to itemCount do itemList[i] = $[i]
			else if (itemCount == 1) then itemList[1] = $

			for sel in itemList do (
				select sel
				$.modifiers["Edit Poly"].ConvertSelection fromlevel #Face
			)
			select itemList
		) else if (classof (modPanel.getCurrentObject()) == Editable_Poly) then (
			$.EditablePoly.ConvertSelection fromlevel #Face
		)
	) catch()
	)
	subobjectLevel = 4
)
macroScript GotoElement_KeepSel category:"Ingenuity" tooltip:"SubObj 5 w/ Selection"
(
	fromlevel = case subobjectLevel of (
		1: #Vertex
		2: #Edge
		3: #Border
		4: #Face
		5: #Element
	)
	undo "ConvertSelection" on (
	try (
		if (classof (modPanel.getCurrentObject()) == Edit_Poly) then (
			itemList = #()
			--get item count (errors if only one things is selected)
			if ($ != undefined) then try(itemCount = $.count)catch(itemCount = 1)
			else itemCount = 0
			--if somethings selected then
			if (itemCount > 1) then for i = 1 to itemCount do itemList[i] = $[i]
			else if (itemCount == 1) then itemList[1] = $

			for sel in itemList do (
				select sel
				$.modifiers["Edit Poly"].ConvertSelection fromlevel #Element
			)
			select itemList
		) else if (classof (modPanel.getCurrentObject()) == Editable_Poly) then (
			$.EditablePoly.ConvertSelection fromlevel #Element
		)
	) catch()
	)
	subobjectLevel = 5
)

--select two verts, make vert between
--select an edge, make vert in middle
macroscript InsertVertexAtMidpoint category:"Ingenuity" tooltip:"Ins. Vertex at Mid"
(
 	on isEnabled return	( selection.count==1 and (classof (modPanel.getCurrentObject()) == Editable_Poly) )
 	on execute do (
		baseObj = $.baseObject
		vertSel = polyOp.getVertSelection baseObj
		edgeSel = polyOp.getEdgeSelection baseObj
		if (subObjectLevel == 1 and (vertSel as array).count > 1) then (
			allEdges = polyop.getNumEdges baseObj

			-- initialize counts
			counts = #()
			for edg = allEdges to 1 by -1 do
				counts[edg] = 0
	
			for vert in vertSel do (
				edges = polyOp.getEdgesUsingVert baseObj #{vert}
				for edg in edges do
					counts[edg] += 1
			)
			
			newVerts = #()
			for common=1 to allEdges do
				if (counts[common] > 1) then
					append newVerts (polyOp.divideEdge baseObj common .5)

			polyOp.setVertSelection baseObj newVerts
		) else if (subObjectLevel == 2 and (edgeSel as array).count > 0) then (
			newVerts = #()
			for edg in edgeSel do
				append newVerts (polyOp.divideEdge baseObj edg .5)

			polyOp.setVertSelection baseObj newVerts
			subobjectlevel = 1
		)
		update $
	)
)

/* Build End Description
	-- reqs: epoly, 2 verts selected
	-- from the 2 verts, convert to edge selection
 1		2 	 3		|	1 	 2		3
 x -- x -- x		|	x -- x -- x
 |				 |		|	| 	 |		|
 |	 P1 	 x 4		|	| 	v7 -- x 4
 |				 |		|	| / 			|
 x ------- x 5		|	x ------- x 5
 6					|	6

x = vertex, -- = segment,  P1 = this poly / face
verts 2 and 4 are selected, Build End macroscript is run

convert selection to edge yields:
v2 =	e1-2	and e2-3
v4 =	e3-4	and e4-5

convert selection to face from v2 and v4 yields 3 faces each,
of which only P1 is similar between both selections

convert P1 face selection to edge yields a list of 6 edges (4 of which include original verts)
convert P1 face selection to vertex yields a list of 6 vertices (2 of which are original verts)

Insert Vertex in P1 such that:
e4-7 is || to e5-6	 and	 e2-7 is || e1-6
e2-e7 and e4-7 are of equal length
angle between e6-5 and e6-7 is equal to angle between e6-7 and e6-1
and no other edges exist (no tris, just 3 quads)

Insert Vertex tool on P1 creates 5 edges
do a per edge convert to vertex selection
and remove the edges which dont include the original 2 verts,
or v6 (the vert not sharing an edge with either original vert)

<face> = P1
v7 = $.EditablePoly.divideFace <face> #(0.5,0,0,0.5,0,0) select:on
edges = convert to edge selection
$.EditablePoly.ConvertSelection #Vertex #Edge
for edge in edges do
	if (get verts in edge does not contain v2,v4,v6) then remove it
*/
macroscript BuildEnd category:"Ingenuity" tooltip:"Build End"
(
	fn getCommon items fromType toType =
	(
		baseObj = $.baseObject
			common = #{}
			commonList = #()

		--init commonlist to zero
		for i = polyOp.getNumEdges $.baseObject to 1 by -1 do
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

	on isEnabled return ( selection.count==1 and classOf selection[1].baseobject == Editable_Poly and $.selectedVerts.count == 2)
	on execute do
	(
		vertSel = polyop.getVertSelection $
		verts = vertSel as array
		x2 = verts[1]
		x4 = verts[2]
		pOne = getCommon vertSel #Vertex #Face

		pVerts = #{}

		for f in pOne do (
			for a in (polyop.getVertsUsingFace $ f) do
				append pVerts a
		)

		a = polyop.getvertsusingedge $ (polyop.getedgesusingvert $ x2)
		b = polyop.getvertsusingedge $ (polyop.getedgesusingvert $ x4)

		x3 = a*b

		x1 = polyop.getvertsusingedge $ (polyop.getedgesusingvert $ x2)
		x1 = (x1 - #{x2}) - x3
		x1 = x1 * pVerts

		x5 = polyop.getvertsusingedge $ (polyop.getedgesusingvert $ x4)
		x5 = (x5 - #{x4}) - x3
		x5 = x5 * pVerts

		x6 = pverts - x5 - #{x4} - x3 - #{x2} - x1

		con1 = getCommon (x5+x6) #Vertex #Edge
		con1 = bitToInt con1
		tempVert = $.EditablePoly.divideEdge con1[1] 0.5

		polyop.setVertSelection $ (#{tempVert} + #{x2})
		$.EditablePoly.ConnectVertices()

		con2 = getCommon (#{tempVert} + #{x2}) #Vertex #Edge
		con2 = bitToInt con2
		newVert = $.EditablePoly.divideEdge con2[1] 0.5

		polyop.setVertSelection $ (#{newVert} + #{x4})
		$.EditablePoly.ConnectVertices()

		subobjectlevel = 2
		polyop.setEdgeSelection $ (getCommon (#{tempVert} + #{newVert}) #Vertex #Edge)
		$.EditablePoly.Remove()

		polyop.setVertSelection $ (#{newVert} + x6)
		$.EditablePoly.ConnectVertices()

		subobjectlevel = 1
		polyop.setVertSelection $ tempVert
		$.EditablePoly.Remove()
	)
)
