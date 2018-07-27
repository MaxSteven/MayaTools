try(destroyDialog ::rlShapeOrder)catch()
rollout rlShapeOrder "Shape Order"
(
	local theShape = undefined
	
	fn fnShapeFilter obj = superclassof obj == Shape

	fn fnSortRadialDistance obj1 obj2 refPt: = (
		distance refPt obj1.center - distance refPt obj2.center
	)
	
	fn RemoveItemFromArray arr itm = (
		local idx = findItem arr itm
		if idx == 0 then false else deleteItem arr idx
	)
	
	fn fnShapeOrder = (
		if theShape != undefined and isValidNode theShape do
		(
			_pathObjs = #()
			_testObjs = for o in selection where superclassof o == GeometryClass collect o
			range = theShape.render_thickness --diameter
			for o in _testObjs do o.wirecolor = gray
			resetLengthInterp()
			
			for idx = 1 to (numSplines theShape) do
			(		
				for i = 0.0 to 1.0 by .05 do
				(
					x = interpCurve3D theShape idx i
					
					_batch = #()
					for o in _testObjs do
					(
						nodeCenter = o.center
						result = distance nodeCenter x
						
						if result <= range do 
						(
							appendIfUnique _batch o
						)
						qsort _batch fnSortRadialDistance refPt:x --sort by distance to the given point on the spline
					)
						
					for o in _batch do 
					(
						RemoveItemFromArray _testObjs o --clear out objects already in use
						appendIfUnique _pathObjs o
					)
				)
			)
			clearselection()
			for o in _pathObjs do selectmore o --correct selection
			
 			--//wirecolor variation from red to yellow
			count = _pathObjs.count
			for i = 1 to count do
			(
				if count != 0 do
				(
					local k = (i as float) / count
					_pathObjs[i].wirecolor = yellow * (1 - k) + red * k
				)
			)
		)
	)	
	
	label lbRedObjEdge "" style_sunkenedge:true width:162 height:24 pos:[7,10]
	button btnClearRefObj "X" width:26 height:22 pos:[142,11]
	pickbutton pbRefObj "Pick Reference Shape" width:134 height:22 pos:[8,11] filter:fnShapeFilter
	button btnShapeOrder "Order Selection"width:160 height:30 pos:[10,40] tooltip:"YELLOW = first | RED = last"
	
	on pbRefObj picked obj do 
	(
		theShape = if obj != undefined then obj else undefined
		pbRefObj.text = if obj != undefined then obj.name else "Pick Reference Shape"
	)
	on btnClearRefObj pressed do
	(
		theShape = undefined
		pbRefObj.text = "Pick Reference Shape"
	)
	on btnShapeOrder pressed do
	(
-- 		t1 = timestamp()
-- 		m1 = heapfree
		fnShapeOrder()
-- 		format "time:% memory:%\n" (timestamp() - t1) (m1 - heapfree)
	)
)
createDialog rlShapeOrder 180 80 style:#(#style_SysMenu, #style_ToolWindow)