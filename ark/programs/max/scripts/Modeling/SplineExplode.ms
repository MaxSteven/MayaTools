try(destroyDialog ::rlSplineExplode)catch()
rollout rlSplineExplode "Spline Explode"
(
	checkbox cbKeepOriginal "Keep Original" checked:true
	button btExplodeSplines "Explode Splines" width:180 height:30
	
	fn ExplodeSplines = 
	(
		splineShapes = for n in (getCurrentSelection()) where superclassof n == shape collect n
			
		if splineShapes.count >= 1 then
		(
			progressStart "Exploding"
			
			for sp in splineShapes do
			(
				Nsplines=numSplines(sp)
				for spl = 1 to Nsplines do 
				(
					ns=splineShape prefix:sp.name
					addnewspline ns
					for k = 1 to (numKnots sp spl) do
					(
						knotpos = getKnotPoint sp spl k
						segtype = getSegmentType sp spl 1
						knottype = getKnotType sp spl k
							
						if knottype == #bezier or knottype== #bezierCorner then 
						(
							addknot ns 1 knottype segtype knotpos (getInVec sp spl k) (getOutVec sp spl k)
						)
						else
						(
							addknot ns 1 knottype segtype knotpos
						)
					)
					if (isClosed sp spl) then close ns 1
					updateshape ns
				)
				progressUpdate (100.0*splineShapes.count)
			)
			progressEnd()
			
			if not cbKeepOriginal.checked do delete splineShapes
		) 
		else
		(		
			messagebox "Splines Only"	
		)
	)
	
	on btExplodeSplines pressed do
	(
		ExplodeSplines()
	)
)
createDialog rlSplineExplode 200 65  style:#(#style_SysMenu, #style_ToolWindow)