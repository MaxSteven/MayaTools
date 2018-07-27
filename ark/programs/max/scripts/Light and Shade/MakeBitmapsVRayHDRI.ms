
fn makeBitmapsVRayHDRI objs =
(
	vrayBitmap2VRayHDRI exrConvert:false
	local mats = makeUniqueArray (for o in objs collect o.material)
	for m in mats do
	(
		for b in getClassInstances VRayHDRI do
			b.color_space = 2
	)
)

makeBitmapsVRayHDRI (getCurrentSelection())
