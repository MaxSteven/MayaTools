rm = RayMeshGridIntersect()
rm.Initialize 10

for o in objects do
	rm.addNode o

rm.buildGrid()
userSel = getCurrentSelection()
numSamples = 256
numSamples = numSamples as float
rayDirs = #()
root = int(sqrt numSamples) as float
for z = 1 to root do
(
	zDir = z / root
	for n = 1 to root do
	(
		ang = ((n-1) / root) * 360
		xDir = -1 * (sin ang)
		yDir = cos ang
		append rayDirs (normalize [xDir,yDir,zDir])
	)
)

for o in userSel do
(
	--obj = snapshotasmesh o
	obj = o
	for v = 1 to obj.numVerts do
	(
		vertPos = getVert obj v
		hits = 0
		for rayDir in rayDirs do--= 1 to numSamples do
		(
			--rayDir = normalize [random -1.0 1.0, random -1.0 1.0, random -1.0 1.0]
			hitCount = rm.intersectRay vertPos rayDir false
			if (hitCount > 0) then
				hits += 1
		)
		c = hits / numSamples * 255
		format "% hits out of % samples = %\n" hits numSamples c		
		meshop.setVertColor o 0 v (color c c c)
	)
	o.showvertexcolors = true
)