trackingObj = $cam_baked

maxDist= 4000

allPositions = #()
startFrame = animationrange.start.frame as integer
endFrame = animationrange.end.frame as integer
for t in startFrame to endFrame do
(
	at time t append allPositions (trackingObj.pos)
)

closeClouds = #()
for cloud in getCurrentSelection() do
(
	-- cloud.wirecolor = color 0 255 0
	for pos in allPositions do
	(
		if (distance cloud.pos pos) < maxDist then
		(
			-- cloud.wirecolor = color 255 0 0
			append closeClouds cloud
		)
	)
)

select closeClouds
-- select (for cloud in getCurrentSelection() where cloud.wirecolor.red > 0 collect cloud)
