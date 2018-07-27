--//get a materials layer and delete everything that's on it
matLayer = LayerManager.getLayerFromName "MATERIALS"
if matLayer == undefined then
	matLayer = LayerManager.newLayerFromName "MATERIALS"
matLayer.nodes &allNodes
delete allNodes

--//go through the xref materials and merge back in the originals (this should be a button)
for o in objects do
(
	if (classof o.material == XRef_Material) then
	(
		tempLib = loadTempMaterialLibrary (substituteString o.material.srcFileName ".max" ".mat")
		o.material = tempLib[substring o.material.srcItemName 5 -1]
	)
)

--//make cubes for each scene material
yOffset = random 500 2000
for n = 1 to sceneMaterials.count do
	if (classof sceneMaterials[n] != XRef_Material) then
		matLayer.addNode (box wirecolor:(color 128 128 128) width:20 length:20 height:20 lengthsegs:1 widthsegs:1 heightsegs:1 pos:[n*50,yOffset,0] material:sceneMaterials[n] name:("mat_" + sceneMaterials[n].name) renderable:false)

--//xref the cubes, delete them, then bring them back in as references
matLayer.nodes &allNodes
refFile = maxfilepath + "materials.max"
saveNodes allNodes refFile quiet:true
nodeNames = for n in allNodes collect n.name
delete allNodes
xrefs.addNewXRefObject refFile nodeNames modifiers:#xref manipulators:#xref dupMtlNameAction:#autoRename

--//saves the sceneMaterials to a library which we'll need later to load in local copies
saveTempMaterialLibrary sceneMaterials (maxFilePath + "materials.mat")

--//set the cube material names back to what they should be (they come in as "material #1" etc)
for n in nodeNames do
(
	matObj = getNodeByName n
	if (matObj != undefined and matObj.material != undefined) then
		matObj.material.name = substring matObj.name 5 -1
)

--//replace all the materials in the scene with their xref'd ones
for sceneMat in sceneMaterials do
(
	for sceneObj in objects where sceneObj.material == sceneMat do
	(
		matObj = getNodeByName ("mat_" + sceneMat.name)
		if (matObj != undefined and matObj.material != undefined) then
			sceneObj.material = matObj.material
	)
)

--//delete the temporary material cubes that we brought in
for n in nodeNames do
(
	matNode = getNodeByName n
	if matNode != undefined then
		delete matNode
)


/* 
IMPLEMENT THIS AS WELL, RETURNS SELECTED OBJECTS BACK TO ORIGINAL MATERIALS

userSel = getCurrentSelection()
for o in userSel do
(
	if (classof o.material == XRef_Material) then
	(
		tempLib = loadTempMaterialLibrary (substituteString o.material.srcFileName ".max" ".mat")
		o.material = tempLib[substring $.material.srcItemName 5 -1]
	)
)*/