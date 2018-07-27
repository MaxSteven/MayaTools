--//-----------------------------------------------------------------------------
--// Publisher.ms
--// By Grant Miller (blented@gmail.com)
--// v 1.0
--// Created On: 12/04/12
--// Modified On: 12/04/12
--// tested using Max 2012, Nuke 6.3v3, Softimage 2012, Maya 2012
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Required Files:
--// ieMax.ms
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Description:
--// Temporary publishing program, eventually to be rewritten in Python
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Revision History:
--//
--// v .10 Alpha version
--//
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
(
--// Includes
--//-----------------------------------------------------------------------------
fileIn (MAX_TOOLS_ROOT + "lib/ieMax.ms")


--// Global Variables
--//-----------------------------------------------------------------------------

--// Functions
--//-----------------------------------------------------------------------------

fn getRoot node =
(
	if isvalidnode node then
	(
		while node.parent != undefined do
			node = node.parent
		return node
	)
)

fn getChildren node =
(
	local tmpArr = #()
	for c in node.children do
	(
		append tmpArr c
		join tmpArr (getChildren c)
	)
	tmpArr --omitting "return" is faster!
)

fn getFullHierarchy objs =
(
  --// allows us to pass a single object or nothing at all
  if classof objs != Array then
    objs = #(objs)

  fullHierarchy = #()
  parents = makeUniqueArray (for o in objs collect (getRoot o))
  for p in parents do
  (
	  fullHierarchy += getChildren p
	  fullHierarchy += p
  )
  return fullHierarchy
)

fn getRootTransform objs roots =
(
  rootTransform = matrix3 1
  select objs
  if roots != false and classof roots != Array and isValidNode roots then
    roots = #(roots)

	if classof roots == Array and roots.count == 1 then
	(
		rootTransform = roots[1].transform
    if rootTransform.scale != [1,1,1] then
      rootTransform = scale rootTransform (1/rootTransform.scale)
		rootTransform.pos.z = $.min.z
	)
	else
	(
		rootTransform.pos = ($.min + $.max) * .5
		rootTransform.pos.z = $.min.z
	)
  return rootTransform
)

fn makeRoot objs =
(
	max create mode

	roots = #()
	for obj in objs do
	(
		--// get all the items w/ no parent or w/ a parent outside of the selection
		if (findItem objs obj.parent) == 0 then
		(
			if obj.parent != undefined then
				format (obj.name + " was parent outside of the selected items.\n")
			append roots obj
		)
	)

	--// place a dummy at their center, with the z at the minimum
	rootPoint = point()
	rootPoint.transform = getRootTransform objs roots

	for obj in roots do obj.parent = rootPoint

	select rootPoint
	return rootPoint
)

fn instanceHierarchy objs newParent =
(
	if classof objs != Array and isValidNode objs then
		objs = #(objs)
	local tmpArr = #()
	for obj in objs do
	(
		n = instance obj
		if newParent != false then
			n.parent = newParent
		append tmpArr n
		join tmpArr (instanceHierarchy obj.children n)
	)
	tmpArr --//omitting "return" is faster!
)


--// Script
--//-----------------------------------------------------------------------------

try ( destroydialog ::publishRoll )catch()

rollout publishRoll "Publisher v.10"
(
  button btnPrepSelected "Prep Selected"
  button btnNewAsset "New Asset"
  --//button btnUpdateAsset "Update Asset"

  on btnPrepSelected pressed do
  (
    userSel = getCurrentSelection()
    if userSel.count > 0 then
      makeRoot userSel
  )
  on btnNewAsset pressed do
  (

--//   try(destroyDialog ::rlAssetName)catch()
--// 			rollout rlAssetName "New Job Name"
--// 			(
--// 				edittext etAssetName "New:" fieldwidth:150 top:true pos:[10,10]
--// 				listbox lbJobNames "" items:#() width:179 height:6 pos:[10,34]
--//
--// 				on etAssetName entered txt do
--// 				(
--// 					--//Repalce "spaces" with "_"
--// 					noSpace = " "
--// 					add_ = "_"
--// 					txt = substituteString txt noSpace add_
--// 					--//Add new job name
--// 					appendIfUnique jobNamesArr txt
--// 					lbJobNames.items = jobNamesArr
--// 					etAssetName.text = ""
--// 					try(destroyDialog ::rlAssetName)catch()
--// 					fnUpdateJobNameList()
--// 					--//Select job name just added
--// 					if jobNamesArr.count >= 1 do (
--// 						dlJobName.selection = jobNamesArr.count
--// 						jobName = dlJobName.selected as string
--// 						fnValidateUserSettings()
--// 					)
--// 				)
--//
--// 				on lbJobNames doubleClicked itm do
--// 				(
--// 					temp = lbJobNames.items
--// 					deleteItem temp itm
--// 					lbJobNames.items = temp
--// 					setappdata rootnode data_jobNamesArr (with printallelements on temp as string)
--// 					fnUpdateJobNameList()
--// 					fnValidateUserSettings()
--// 				)
--//
--// 				on rlAssetName close do
--// 				(
--// 				)
--//
--// 				on rlAssetName open do
--// 				(
--// 					setfocus etAssetName
--// 				)
--// 			)
--// 			createDialog rlAssetName 200 126 modal:true style:#(#style_SysMenu, #style_ToolWindow)
--//

    userSel = getCurrentSelection()

    --// move the selected objects to the origin
    rootPoint = makeRoot userSel
    ogTransform = rootPoint.transform
    rootPoint.transform = matrix3 1

    --// choose a department and save selected as the first version of that file
    saveFile = "Q:/Test_Project/GLOBAL_ASSETS/Stool/3D/Stool_v001_ghm.max"
    saveNodes userSel saveFile quiet:true

    select userSel
    --// export the selected objects as the first Alembic publish
    --// ensure unique names of all selected objects
    startFrame = "0"
    endFrame = "1"
    exportString = "filename=Q:/Test_Project/GLOBAL_ASSETS/Stool/3D/Publish/Stool_v001.abc;in=" + startFrame + ";out=" + endFrame + ";step=1;subStep=1;meshTopology=3;uvs=1;materialIDs=1;exportSelected=1;normals=1"
    ExocortexAlembic.createExportJobs(exportString)

    --// create an empty layer to import the alembic files to
    activeLayer = LayerManager.current
    importLayerName = "__import_" + (random 100 999) as string
    importLayer = LayerManager.newLayerFromName importLayerName
    importLayer.current = true

    importString = "filename=Q:/Test_Project/GLOBAL_ASSETS/Stool/3D/Publish/Stool_v001.abc;normals=1;UVs=1;materialIDs=1;attach=0;visibility=1"
    ExocortexAlembic.createImportJob(importString)

    --// place objects on the layers they should be on
    --// metaData = custAttributes.get $.modifiers["Alembic Metadata"] 1

    --// get the imported nodes from the import layer
    importedNodes = #()
    importLayer.nodes &importedNodes
    newObjs = #()
    timeControl = false
    for obj in importedNodes do
    (
	    if classof obj == AlembicTimeControl then
        timeControl = obj
      else
		    newObjs += obj
    )
    assetRoot = makeRoot newObjs

    --// move the time control to it's own layer
    if timeControl != false then
    (
      tcLayer = LayerManager.getLayerFromName "__timeControl"
      if tcLayer == undefined then
        tcLayer = LayerManager.newLayerFromName "__timeControl"
      tcLayer.addNode
    )

    --// replace each instance with the cached Alembic file
    allInstances = #()
    instances = #()
    transforms = #()
    for obj in userSel do
    (
	    InstanceMgr.GetInstances obj &instances
      allInstances += instances
    )
    for i in allInstances do
	  (
      --// if the object has no parent or the parent is outside of the instances, we'll try to replace it
		  if i.parent == undefined or findItem allInstances i.parent == 0 then
			(
        objectAndChildren = getChildren i
        objectAndChildren += i
        transforms += #(getRootTransform objectAndChildren i)
      )
	  )
    delete allInstances

    for t in transforms do
    (
      instancedObjs = instanceHierarchy assetRoot false
      instanceRoots = makeUniqueArray (for o in instancedObjs collect (getRoot o))
      for root in instanceRoots do
        root.transform = t
    )

    activeLayer.current = true
    layerManager.deleteLayerByName importLayerName
  )
)

createDialog publishRoll 100 200 style:#(#style_SysMenu, #style_ToolWindow)
)
