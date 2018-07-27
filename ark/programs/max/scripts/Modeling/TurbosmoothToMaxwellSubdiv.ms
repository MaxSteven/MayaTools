undo on
(
	for obj in $ do
	(
		if (classof obj.modifiers[1] == TurboSmooth and obj.modifiers[1].enabled == true) then
		(
			tsMod = obj.modifiers[1]
			iterations = tsMod.iterations
			if (tsMod.useRenderIterations == true) then
			(
				iterations = tsMod.renderIterations
			)
			tsMod.enabled = false
			maxwellMod = Maxwell_Subdivision subdivisionLevel:iterations
			addModifier obj maxwellMod
		)
	)
)



undo on
(
	for obj in $ do
	(
		onlyUVs = true
		smoothIter = 0
		for i = 1 to obj.modifiers.count do
		(
			if (classof obj.modifiers[1] == TurboSmooth and obj.modifiers[1].enabled == true) then
			(
				tsMod = obj.modifiers[1]
				if (tsMod.useRenderIterations == true) then
					smoothIter += tsMod.renderIterations
				else
					smoothIter += tsMod.iterations

				tsMod.enabled = false
			)
			else if (classof obj.modifiers[i] != Uvwmap) then
				onlyUVs = false
		)
		if (smoothIter > 0 and onlyUVs == true) then
		(
			maxwellMod = Maxwell_Subdivision subdivisionLevel:smoothIter
			addModifier obj maxwellMod
		)
	)
)




finishedObjects = #()
objInstances = #()

fn fixModifiers obj =
(
	print ("Checking " + obj.name)
	if (findItem finishedObjects obj != 0) then
	(
		print (obj.name + " was already checked")
		return false
	)

	keepChecking = true
	smoothIter = 0
	uvMods = #()

	i = 1
	modCount = obj.modifiers.count
	print (modCount as string + " modifiers")
	while i < modCount and keepChecking == true do
	(
		curMod
		if (classof curMod == TurboSmooth and curMod.enabled == true) then
		(
			if (curMod.useRenderIterations == true) then
				smoothIter += curMod.renderIterations
			else
				smoothIter += curMod.iterations

			curMod.enabled = false
		)
		else if (classof curMod == Uvwmap) then
		(
			append uvMods curMod
			deleteModifier obj i
			i -= 1
			modCount -= 1
		)
		else
			keepChecking = false
		i += 1
	)

	instanceCount = InstanceMgr.GetInstances obj objInstances
	finishedObjects += objInstances

	if (uvMods.count > 0) then
	(
		for inst in objInstances do
		(
			for mod in uvMods do
			(
				try
					deleteModifier inst mod
				catch ()
			)
		)
		for mod in uvMods do
		(
			addModifier obj mod
		)
	)

	if (smoothIter > 0) then
	(
		maxwellMod = Maxwell_Subdivision subdivisionLevel:smoothIter
		addModifier obj maxwellMod
	)
)

for obj in $ do
(
	fixModifiers obj
)



finishedObjects = #()
objInstances = #()

fn fixModifiers obj =
(
	print ("Checking " + obj.name)
	if (findItem finishedObjects obj != 0) then
	(
		print (obj.name + " was already checked")
		return false
	)

	keepChecking = true
	smoothIter = 0
	uvMods = #()

	i = 1
	modCount = obj.modifiers.count
	print (modCount as string + " modifiers")
	while i < modCount and keepChecking == true do
	(
		curMod
		if (classof curMod == TurboSmooth and curMod.enabled == true) then
		(
			if (curMod.useRenderIterations == true) then
				smoothIter += curMod.renderIterations
			else
				smoothIter += curMod.iterations

			curMod.enabled = false
		)
		else if (classof curMod == Uvwmap) then
		(
			append uvMods curMod
			deleteModifier obj i
			i -= 1
			modCount -= 1
		)
		else
			keepChecking = false
		i += 1
	)

	instanceCount = InstanceMgr.GetInstances obj objInstances
	finishedObjects += objInstances

	if (uvMods.count > 0) then
	(
		for inst in objInstances do
		(
			for mod in uvMods do
			(
				try
					deleteModifier inst mod
				catch ()
			)
		)
		for mod in uvMods do
		(
			addModifier obj mod
		)
	)

	if (smoothIter > 0) then
	(
		maxwellMod = Maxwell_Subdivision subdivisionLevel:smoothIter
		addModifier obj maxwellMod
	)
)

for obj in $ do
(
	fixModifiers obj
)
