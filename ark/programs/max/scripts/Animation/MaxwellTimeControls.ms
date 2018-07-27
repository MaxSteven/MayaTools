fileIn (MAX_TOOLS_ROOT + "lib/ieMax.ms")

plugin SimpleMod MaxwellTimeControls
name:"Maxwell Time Controls"
classID:#(0x6a60f1c6, 0x2cdf0a3a)
replaceUI:off
silentErrors:off
version:1
(
	local curNode

	parameters params rollout:params
	(
		cacheBase type:#string default:"" ui:uiCacheBase animatable:off
		cacheStart type:#integer default:0 ui:uiCacheStart animatable:off
		cacheEnd type:#integer default:animationrange.end ui:uiCacheEnd animatable:off
		frameOffset type:#integer default:0 ui:uiFrameOffset animatable:off
		timeScale type:#integer default:1.0 ui:uiTimeScale animatable:off
		loop type:#Boolean default:true ui:uiLoop animatable:off

		on cacheBase set val do this.offsetCache()
		on cacheStart set val do this.offsetCache()
		on cacheEnd set val do this.offsetCache()
		on frameOffset set val do this.offsetCache()
		on timeScale set val do this.offsetCache()
		on loop set val do this.offsetCache()
	)

	rollout params "Parameters"
	(
		editText uiCacheBase "Cache Base: " fieldwidth:80 offset:[-9,8]
		spinner uiCacheStart "Cache Start: " fieldwidth:50 range:[-1e9,1e9,0] type:#integer align:#right offset:[-18,8]
		spinner uiCacheEnd "Cache End: " fieldwidth:50 range:[-1e9,1e9,0] type:#integer align:#right offset:[-18,0]
		spinner uiFrameOffset "Time Offset: " fieldwidth:50 range:[-1e9,1e9,0] type:#integer align:#right offset:[-18,8] tooltip:"The frame in-which the cache will begin playing."
		button uiGetTime "‹›" width:20 height:16 offset:[64,-21] tooltip:"Click this button to use the current timeslider position as the start frame of your cache."
		spinner uiTimeScale "Time Scale: " fieldwidth:50 range:[-1e9,1e9,1.0] type:#integer align:#right offset:[-18,0] tooltip:"The speed at which the cache plays back. Default 1.0"
		checkbox uiLoop "loop Cache" align:#right offset:[2,6]
		button uiRemove "Remove" width:140 align:#right offset:[2,6]

		on uiGetTime pressed do
		(
			frameOffset = slidertime
		)

		--This button removes the Animation Offset modifier and reverts all modified Script controls back to their original strings
		on uiRemove pressed do
		(
			-- local curNode = this.getNode()
			-- local str = "current * factor + offset"

			-- for i in #(1,3,4) do
			-- (
			-- 	if curNode != undefined do
			-- 	(
			-- 		this.updateFloatExpressionsRecursive curNode[i] str
			-- 	)
			-- )

			-- for i = curNode.modifiers.count to 1 by -1 do
			-- (
			-- 	m = curNode.modifiers[i]
			-- 	if classof m == MaxwellTimeControls do
			-- 	(
			-- 		deletemodifier curNode m
			-- 	)
			-- )
		)
	)

	fn getNode = (refs.dependentnodes this)[1]

	fn updateFloatExpressionsRecursive o str =
	(
		-- ctrl = o.controller

		-- if isKindOf ctrl Float_Expression do
		-- (
		-- 	ctrl.SetExpression str --set controller expression
		-- 	ctrl.Update() --updates controller
		-- 	format "Modified: %\n" ctrl
		-- )

		-- -- recurse loop
		-- for i = 1 to o.numsubs do updateFloatExpressionsRecursive o[i] str
	)

	fn offsetCache =
	(
		local curNode = getNode()
		if curNode == undefined then
			return false

		local curTime = slidertime as integer / ticksPerFrame
		local frame = curTime + this.frameOffset
		local framePadded = formattedPrint frame format:"04d"
		curNode.baseObject.mxsFile = substituteString this.cacheBase "####" framePadded
		-- local frameRange = (cacheEnd - cacheStart) / framerate
		-- 12.0f / framerate
		-- if loop then
		-- (
		-- 	tScale = timeScale as string
		-- 	timeOffset = (frameOffset/framerate as integer) as string
		-- 	fRange = frameRange as string
		-- 	cStart = (cacheStart / framerate as integer) as string
		-- 	fStart = (frameRange as string) as string

		-- 	str = "if(current*" + tScale + "-" + timeOffset + ">0," + \
		-- 			"mod (current*" + tScale + "-" + timeOffset + "," + fRange + ") + " + cStart + \
		-- 			",mod (current*" + tScale + "-" + timeOffset + "," + fRange + ") + " + cStart + "+ " + fStart + ")"

		-- )else(
		-- 	str = "(current*" + timeScale as string + "-" + (frameOffset/framerate as integer) as string + ") + " + (cacheStart / framerate as integer) as string
		-- )

		-- -- 1 : visibiliy , 3 : transform , 4 : baseObject & modifiers
		-- -- loops through each possible controller found on each node assigning the new string to each alembic related modifier
		-- for i in #(1,3,4) do
		-- (
		-- 	if curNode != undefined do
		-- 	(
		-- 		updateFloatExpressionsRecursive curNode[i] str
		-- 	)
		-- )
		print "set cache"
		print cacheBase
	)

	on attachedToNode obj do
	(
		if obj != undefined and classof obj.baseObject == MXSRef then
		(
			print "on"
			print obj.mxsFile
			this.cacheBase = substituteString (obj.mxsFile) ".mxs" "####.mxs"
			this.offsetCache()
		)
		else
		(
			print "nope"
			print obj
			-- deleteModifier obj this
		)
	)

	on create do
	(
	)
)