max create mode
for obj in objects do
(
	try
	(
		smoothIterations = 0
		smoothType = undefined
		for m in obj.modifiers do
		(
			if classOf m == TurboSmooth or classOf m == TurboSmooth_Pro then
			(
				if m.useRenderIterations == True then
					smoothIterations += m.renderIterations
				else
					smoothIterations += m.iterations

				m.iterations = 0
				smoothType = classof m
				setUserProp obj "smoothIterations" smoothIterations
				setUserProp obj "smoothType" (smoothType as string)
			)
		)

		ConvertTo obj Editable_Poly

		if smoothIterations > 0 and smoothType != undefined then
		(
			m = smoothType()
			m.iterations = 0

			if smoothType == Turbosmooth then
				m.useRenderIterations = True
			else if smoothType == TurboSmooth_Pro then
				m.useRenderIterations = 1

			m.renderIterations = smoothIterations
			addModifier obj m
		)
	)
	catch
	(
		print "Error converting:"
		print obj.name
	)
)
