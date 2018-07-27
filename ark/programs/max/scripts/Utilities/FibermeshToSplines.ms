
fn splinesFromFibermesh obj =
(
	ConvertTo obj Editable_Poly

	local vertCount = polyop.getNumVerts obj
	local faceCount = obj.getNumFaces()
	local faceCountProgress = faceCount as float
	local facesToCheck = #{1..faceCount}

	local start = timeStamp()
	local hairSplines = splineShape()

	local elementNumber = 0
	local curFace
	local elementFaces, faceEdges
	local firstEdge, sideOneEdges, sideOneVerts
	local secondEdge, sideTwoEdges, sideTwoVerts
	local splineIndex
	local vertOnePos, vertTwoPos, averagePos

	progressStart "Creating splines..."
	progressUpdate 0.0

	 with undo off with redraw off
	 (
		while (facesToCheck as array).count > 0 do
		(
			elementNumber = elementNumber + 1

			curFace = (facesToCheck as array).count
			progressUpdate (100 - (curFace / faceCountProgress * 100.0))

			elementFaces = polyop.getElementsUsingFace obj #{curFace}
			faceEdges = polyop.getEdgesUsingFace obj elementFaces

			firstEdge = (faceEdges as array)[1]
			obj.EditablePoly.SetSelection #Edge #{firstEdge}
			obj.EditablePoly.buttonOp #SelectEdgeLoop
			sideOneEdges = obj.EditablePoly.GetSelection #Edge
			sideOneVerts = (polyop.getVertsUsingEdge obj sideOneEdges) as array

			-- secondEdge = (faceEdges as array)[3]
			-- obj.EditablePoly.SetSelection #Edge #{secondEdge}
			-- obj.EditablePoly.buttonOp #SelectEdgeLoop
			-- sideTwoEdges = obj.EditablePoly.GetSelection #Edge
			-- sideTwoVerts = (polyop.getVertsUsingEdge obj sideTwoEdges) as array

			splineIndex = addnewspline hairSplines

			for i = 1 to sideOneVerts.count do
			(
				vertOnePos = polyop.GetVert obj sideOneVerts[i]
				-- vertTwoPos = polyop.GetVert obj sideTwoVerts[i]
				-- averagePos = (vertOnePos + vertTwoPos) * .5
				-- addknot hairSplines splineIndex #corner #line (averagePos)
				addknot hairSplines splineIndex #corner #line (vertOnePos)
			)

			facesToCheck -= elementFaces
		)
	)

	updateshape hairSplines
	hairSplines.pivot = obj.pivot
	progressEnd()
	end = timeStamp()

	hairSplines.name = obj.name + "_splines"
	select hairSplines

	format "Processing took % seconds\n" ((end - start) / 1000.0)
)

splinesFromFibermesh $
