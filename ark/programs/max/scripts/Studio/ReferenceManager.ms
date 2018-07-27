-- Make unique "Material names"
-- object names have to be unique
-- cache button

--//-----------------------------------------------------------------------------
--// PublishTools.ms
--// By Grant Miller (blented@gmail.com)
--// v 1.0
--// Created On: 08/18/11
--// Modified On: 08/18/11
--// tested using Max 2012
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Required Files:
--// ieMax.ms
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Description:
--// Publishes 3dsMax files for IE's pipeline
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Revision History:
--//
--// v 1.00 Initial version
--//
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
(
--// Includes
--//-----------------------------------------------------------------------------
fileIn (MAX_TOOLS_ROOT + "lib/ieMax.ms")

--// Variables
--//-----------------------------------------------------------------------------
maxFilePaths = #()
maxFileNames = #()
fileDir = ""
rootPrefix = "XREFROOT_"
xRefPrefix = "XREF_"
ctrlPrefix = "XCTRL_"
refSplit = "::"
refSplitLength = refSplit.count

--// Functions
--//-----------------------------------------------------------------------------
fn isCtrl nodeName = return (toLower (substring nodeName 1 4) == "ctrl")
fn isCon nodeName = return (toLower (substring nodeName 1 3) == "con")
fn getRefName objName refName =
(
  splitLoc = findstring objName refSplit
  if splitLoc != undefined then
    objName = substring objName 1 (splitLoc - 1)
  return objName + refSplit + refName
)
fn getRoots objs =
(
  return for o in objs where o.parent == undefined collect o
)
fn genXRef refFile fileObjectNames =
(
  refObjectNames = for o in fileObjectNames where (not isCtrl o and not isCon o) collect o
  print "Merging Objects:"
  print refObjectNames
  xrefs.addNewXRefObject refFile refObjectNames modifiers:#xref manipulators:#xref dupMtlNameAction:#useScene
  return (ieMaxGetNodesByName refObjectNames)
)
fn mergeControls refFile fileObjectNames =
(
  controlNames = for o in fileObjectNames where (isCtrl o or isCon o) collect o
  print "Merging as controls:"
  print controlNames
  if (controlNames.count > 0) then
  (
    mergeMaxFile refFile controlNames #select
    return (ieMaxGetNodesByName controlNames)
  )
  else
    return #()
)
fn setRefProps objs refName refFile =
(
  for o in objs do
  (
    setUserProp o "objectName" o.name
	  if (o.material != undefined) then
		  setUserProp o "materialName" o.material.name
    setUserProp o "refName" refName
    setUserProp o "refFile" refFile
    o.name = getRefName o.name refName
  )
)
fn removeNestedReferences objs =
(
  for o in objs do
  (
    if classof o == XRefObject then
    (
      newBase = src = o.getSourceObject false
      while classof src == XRefObject do
      (
        src = src.getSourceObject false
        if (classof src == XRefObject) then
          newBase = src
      )
      if classof newBase == XRefObject then
      (
        baseFile = newBase.filename
        baseItem = newBase.srcItemName
        objXRefMgr.setRecordSrcFile o.xrefrecord baseFile
        o.srcItemName = baseItem
        if (o.material != undefined and classof o.material == XRef_Material) then
          o.material.srcItemName = baseItem
        setUserProp o "refFile" baseFile
      )
    )
  )
)
fn assignXRefMaterials objs =
(
  for o in objs do
  (
    --//when we merge in published files, their materials are already xref'd to the MATERIALS/ref_mat.max file
    --//this removes the "nested" xrefing, going back to the original xref'd material
    if o.material != undefined and classof o.material == XRef_Material then
    (
      srcMat = o.material.getSourceMaterial false
      while classof srcMat == XRef_Material do
      (
        o.material = srcMat
        srcMat = srcMat.getSourceMaterial false
      )
      --//o.material.name = substring o.material.srcItemName 5 -1
    )
  )
)
fn updateReference refName =
(
  xRefRoot = getNodeByName (rootPrefix + refName)
  xRefTransform = xRefRoot.transform
  xRefRoot.transform = matrix3 1
  xRefObjs = for o in objects where (getUserProp o "refName" == refName AND classof o == XRefObject) collect o
  sceneMats = #()
  matObjs = #()
  for o in xRefObjs do
  (
    matIndex = findItem sceneMats o.material
    if matIndex == 0 then
    (
      append sceneMats o.material
      matIndex = sceneMats.count
      matObjs[matIndex] = #()
    )
    append matObjs[matIndex] o.name
  )
  delete xRefObjs

  ctrlObjs = for o in objects where (getUserProp o "refName" == refName AND (isCtrl o.name OR isCon o.name)) collect o
  refNameLength = refName.count
--//remove the "::refName" from the ctrl and con objects
  for o in ctrlObjs do o.name = substring o.name 1 (o.name.count - refNameLength - refSplitLength)

  refFile = getUserProp xRefRoot "refFile"
  if (refFile != undefined) then
  (
    fileObjectNames = getMAXFileObjectNames refFile
    xRefObjs = genXRef refFile fileObjectNames
    setRefProps xRefObjs refName refFile
  )
  else
  (
    print "Could not update selected reference"
  )
--//swap the ctrl and con objects back to their ref names
  for o in ctrlObjs do o.name = getRefName o.name refName
  objRoots = getRoots (ctrlObjs + xRefObjs)
  for o in objRoots do o.parent = xRefRoot
  xRefRoot.transform = xRefTransform

  for o in xRefObjs do
  (
    for n = 1 to matObjs.count do
    (
      if findItem matObjs[n] o.name != 0 then
        o.material = sceneMats[n]
    )
  )
)
fn getPublishFile =
(
  if maxfilename == "" then
  (
    messageBox "Please save your max file before publishing" title:"No filename"
    return ""
  )
  versionLoc = findstring maxfilename "_v"
  if versionLoc == undefined then
    versionLoc = maxfilename.count - 3
  publishName = substring maxfilename 1 (versionLoc - 1)

  pathParts = filterString maxfilepath "\\"
  if pathParts[pathParts.count] == "3DSMAX" then
    publishDir = maxfilepath + "PUBLISH"
  else
    publishDir = (ieMaxJoinArray (ieMaxArraySlice pathParts 1 -1) "\\") + "PUBLISH\\"

  if not isDirectoryWriteable publishDir then
    makeDir publishDir all:true

  return publishDir + publishName + ".max"
)
fn mergeConflicts refFile =
(
  recordCount = objXRefMgr.recordCount
  for i = 1 to recordCount do
  (
    r = objXRefMgr.getRecord i
    if r.srcFileName == refFile then
    (
      objXRefMgr.MergeRecordIntoScene r
      i -= 1
      recordCount -= 1
    )
  )
)
--// Script
--//-----------------------------------------------------------------------------
try (destroydialog ::publishRoll)catch()
rollout publishRoll "PublishTools v1.00" width:440 height:320
(
	GroupBox grpReferences "References:" pos:[295,24] width:137 height:88
	GroupBox grpMaterials "Materials:" pos:[295,120] width:137 height:64
	GroupBox grpPublish "Publish" pos:[7,272] width:425 height:40

	label lbLocationPath "" pos:[0,0] width:440 height:16 style_sunkenedge:true
	dropdownList ddlLocations "" pos:[8,24] width:136 height:21 items:#("Shot Assets", "Project Assets", "Global Assets") selection:1
	multiListBox mlbMaxFiles "Files:" pos:[8,48] width:136 height:13
	multiListBox mlbXRefs "References:" pos:[152,48] width:136 height:13
	button btnRefSel "Reference Selected " pos:[8,240] width:136 height:24
	button btnUpdateSel "Update Selected" pos:[296,40] width:136 height:24
	button btnUpdateAll "Update All" pos:[296,64] width:136 height:24
	button btnRemoveSel "Remove Selected" pos:[296,88] width:136 height:24
	button btnMakeLocalCopies "Make Local Copies" pos:[296,136] width:136 height:24
	button btnPublishMats "Materials for Selected" pos:[136,288] width:144 height:24
	button btnLoadOriginalMats "Load Originals" pos:[296,160] width:136 height:24
	button btnPublishGeo "Selected Geometry" pos:[8,288] width:120 height:24
	button btnRefreshRefs "Refresh" pos:[152,240] width:64 height:24
	button btnSelectRefRoot "Select Reference Roots" pos:[296,192] width:136 height:24
	button btnToggleRefRoots "Hide Ref Roots" pos:[296,216] width:136 height:24
	button btnDeleteUnresolved "Delete Unresolved Refs" pos:[296,240] width:136 height:24
	button btnSelectAll "Select All" pos:[224,240] width:64 height:24
	button btnPublishSel "Selected Geo and Mats" pos:[288,288] width:144 height:24

--// Functions
--//-----------------------------------------------------------------------------
--//shows all the references in the current scene
  fn updateReferenceList =
  (
    mlbXRefs.items = for o in objects where (findString o.name "XREFROOT_" != undefined) collect (substring o.name 10 -1)
    mlbXRefs.items = mlbXRefs.items
  )
  --//Gets the .max files and there directory paths
  fn getTheFiles root pattern type:#Publish =
  (
    dir_array = GetDirectories (root+"/*")
    for d in dir_array do
    join dir_array (GetDirectories (d+"/*"))
    append dir_array (root+"/*")

    my_files = #()
    case type of
    (
      #Publish:(
        for d in dir_array do
        (
          pathParts = filterstring (d as string) "\\"
          tempdir = ""
          if pathParts[pathParts.count] == "PUBLISH" then
            join my_files (getFiles (d + pattern))
        )
      )
      #MaxFiles:(
        for f in dir_array do
          join my_files (getFiles (f + pattern))
      )
    )
    return sort my_files
  )
  --//Populates the list with the filenames if possible, and updates the status bar with dir path
  fn fnUpdateFilesList =
  (
    maxFileNames = #()
    if maxFilePaths.count >=1 then
      maxFileNames = for f in maxFilePaths collect (filterString (filenamefrompath f) ".")[1]
    mlbMaxFiles.items = maxFileNames
    lbLocationPath.text = fileDir
  )
  --//Path builder returns a path
  fn fnPathBuilder idx =
  (
    if (maxfilepath != "") then
    (
      pathParts = filterstring (maxfilepath as string) "\\"
      rootDir = ""
      for p = 1 to idx do
        rootDir += pathParts[p] + "\\"
      if doesFileExist rootDir then
        return rootDir
    )
    return ""
  )
  fn getFilePaths itm =
  (
    maxfilePaths = #()
    fileDir = ""
    if itm == 1 then
    (
      if doesFileExist (maxfilepath + "PUBLISH") then
      (
        fileDir = maxfilepath + "PUBLISH"
        maxFilePaths = getTheFiles fileDir "*.max" type:#MaxFiles
      )
      else if doesFileExist ((ieMaxJoinArray (ieMaxArraySlice (filterString maxfilepath "\\") 1 -1) "\\") +"PUBLISH") then
      (
        fileDir = (ieMaxJoinArray (ieMaxArraySlice (filterString maxfilepath "\\") 1 -1) "\\") +"PUBLISH"
        maxFilePaths = getTheFiles fileDir "*.max" type:#MaxFiles
      )
    )
    else if itm == 2 then
    (
      if doesFileExist ((fnPathBuilder 2)+"GLOBAL_ASSETS") then
      (
        fileDir = (fnPathBuilder 2)+"GLOBAL_ASSETS"
        maxFilePaths = getTheFiles fileDir "*.max" type:#Publish
      )
    )
    else if itm == 3 then
    (
      fileDir = getSavePath initialDir:"Q:\ASSETS\MODELS"
      if fileDir != undefined then
        maxFilePaths = getTheFiles fileDir "*.max" type:#MaxFiles
      else
        fileDir = ""
    )
  )
  fn referenceSelected =
  (
    updateReferenceList()
    refFile = false
    for sel in mlbMaxFiles.selection do
    (
      refFile = maxFilePaths[sel]

      if refFile != false and doesFileExist refFile then
      (
        fileObjectNames = getMAXFileObjectNames refFile
        ctrlObjs = mergeControls refFile fileObjectNames
        xRefObjs = genXRef refFile fileObjectNames

    --//figure out what number to put after this (laser001 if it's the first, laser092 if we've got several)
        baseName = filterString refFile "\\."
        baseName = baseName[baseName.count - 1]
        refNum = 1
        for n = 1 to mlbXRefs.items.count do
        (
          refName = mlbXRefs.items[n]
          stringLoc = findString refName baseName
          if (stringLoc != undefined) then
          (
            num = filterString refName "_"
            num = num[num.count] as integer
            if (num >= refNum) then
            refNum = num + 1
          )
        )
        refName = baseName + "_" + (formattedPrint refNum format:"04d")
        append mlbXRefs.items refName
        mlbXRefs.items = mlbXRefs.items

    --//    Set the refName so we can know where these things came from
        xRefRoot = point name:(rootPrefix + refName)
        setUserProp xRefRoot "refFile" refFile
        setUserProp xRefRoot "refName" refName

    --//        set xref properties on all the objects
        allObjects = ctrlObjs + xRefObjs
        setRefProps allObjects refName refFile
        removeNestedReferences allObjects
        assignXRefMaterials allObjects
--//        needed to update the material references
        objXRefMgr.UpdateAllRecords()

        objRoots = getRoots (ctrlObjs + xRefObjs)
        for o in objRoots do o.parent = xRefRoot
        userSel = getCurrentSelection()
        if userSel.count < 1 then
          select xRefRoot
      )
      else
      (
        messageBox ("Couldn't find file: " + refFile) title:"Bad Reference File"
      )
    )
  )
  fn publishObjs publishFile objs justMaterials:false justGeo:false =
  (
    if publishFile == "" or objs.count < 1 then
      return false

    --//get a materials layer and delete everything that's on it
    matLayer = ieMaxGetLayer "MATERIALS"
    matLayer.nodes &matNodes
    matLayer.isHidden = true
    delete matNodes

    objMaterials = #()
    --//go through the xref materials and merge back in the originals (this should be a button)
    for o in objs do
    (
      if (o.material != undefined) then
      (
        while (classof o.material == XRef_Material) do
          o.material = o.material.GetSourceMaterial true
        appendIfUnique objMaterials o.material
      )
    )

    --//make cubes for each scene material
    publishName = ieMaxBaseFilename publishFile
    if justMaterials == true then
      publishName = substituteString publishName "_mat" ""
    yOffset = random 500 2000
    for n = 1 to objMaterials.count do
    (
      matName = objMaterials[n].name
      objMaterials[n].name = getRefName matName publishName
      sceneMaterials[objMaterials[n].name].name = objMaterials[n].name
      showTextureMap objMaterials[n] true
      matLayer.addNode (box wirecolor:(color 128 128 128) width:20 length:20 height:20 lengthsegs:1 widthsegs:1 heightsegs:1 pos:[n*50,yOffset,0] material:objMaterials[n] name:("mat_" + objMaterials[n].name) renderable:false mapcoords:true)
    )
    --//xref the cubes, delete them, then bring them back in as references
    matLayer.nodes &matNodes

    matFile = ieMaxGetMatRefFile xrefFile:publishFile
    mergeConflicts matFile

    if justGeo == false then
      saveNodes matNodes matFile
    nodeNames = for n in matNodes collect n.name
    delete matNodes

    xrefs.addNewXRefObject matFile nodeNames modifiers:#xref manipulators:#xref dupMtlNameAction:#useXRefed
    if justMaterials == false then
    (
      format "Publishing the following:\n"
      for o in objs do format (o.name + "\n")
      mergeConflicts publishFile
      saveNodes objs publishFile
    )
  )
  fn updateDialog =
  (
    if ddlLocations.selection < 1 then
      getFilePaths 1
    else
      getFilePaths ddlLocations.selection
    fnUpdateFilesList()
    updateReferenceList()
  )
  fn publishSelected justGeo:false =
  (
    if objects.count > 0 then
    (
      max hold
      publishFile = getPublishFile()
      objects = getCurrentSelection()
      for o in objects where superclassof o == camera do
      (
        setTransformLockFlags o #all
        setUserProp o "animStart" animationRange.start
        setUserProp o "animEnd" animationRange.end
        setUserProp o "framerate" framerate
      )

--//      This bit adds the publish name to all the layers so they come across as "Stadium_chairs" instead of "chairs"
      publishName = ieMaxBaseFilename publishFile
      pubLen = publishName.count
--//      Here we make a layer called "base" for all the 0 (default) objects to live on
      defaultLayer = LayerManager.getLayer 0
      defaultLayer.nodes &defaultNodes
      baseLayer = ieMaxGetLayer "base"
      for o in defaultNodes do baseLayer.addNode o

      for i = 1 to LayerManager.count do
      (
        l = LayerManager.getLayer (i-1)
        if (substring l.name 1 pubLen) != publishName then
          l.setName (publishName + refSplit + l.name)
      )
      publishObjs publishFile objects justGeo:justGeo
      fetchMaxFile quiet:true
    )
    else
    (
      messageBox "Please select the objects you wish to publish" title:"No Objects Selected"
    )
  )

--// Button Actions
--//-----------------------------------------------------------------------------
	on publishRoll close do (callbacks.removeScripts id:#toolUpdate) --// Removes all callback actions
  on publishRoll open do
  (
		callbacks.addScript #filePostOpenProcess "publishRoll.updateDialog()" id:#toolUpdate --//updates dialog on new scene
		callbacks.addScript #systemPostNew "publishRoll.updateDialog()" id:#toolUpdate --//updates dialog on new scene
		callbacks.addScript #systemPostReset "publishRoll.updateDialog()" id:#toolUpdate --//updates dialog on new scene
    updateDialog()
  )
  on publishRoll lbuttondown pt do
  (
    updateDialog()
  )
  on ddlLocations selected itm do
  (
    updateDialog()
  )
  on btnRefreshRefs pressed do
  (
    updateDialog()
  )
  on btnSelectAll pressed do
  (
    mlbXRefs.selection = #{1..mlbXRefs.items.count}
  )
  on mlbMaxFiles doubleClicked itm do
  (
    clearlistener()
    maxfile = maxFilePaths[itm]
    this = maxFileNames[itm]
    print maxfile
    print this
    referenceSelected()
  )
  on btnRefSel pressed do
  (
    updateReferenceList()
    referenceSelected()
  )
	on btnSelectRefRoot pressed do
  (
    objs = #()
    for n in mlbXRefs.selection do
    (
      r = getNodeByName (rootPrefix + mlbXRefs.items[n])
      if r != undefined then
        append objs r
    )
    select objs
  )
	on btnToggleRefRoots pressed do
  (
    if findString btnToggleRefRoots.caption "Hide" != undefined then
    (
      for o in $XREFROOT_* do o.isHidden = true
      btnToggleRefRoots.caption = "Show Ref Roots"
    )
    else
    (
      for o in $XREFROOT_* do o.isHidden = false
      btnToggleRefRoots.caption = "Hide Ref Roots"
    )
  )
  on btnDeleteUnresolved pressed do
  (
    delete (for o in objects where classof o == XRefObject and o.unresolved == true collect o)
  )
  on btnUpdateSel pressed  do
  (
    updateDialog()
    refSelCount = (mlbXRefs.selection as array).count
    if (refSelCount > 0) then
    (
      disableSceneRedraw()
      for n in mlbXRefs.selection do
      (
        refName = mlbXRefs.items[n]
        updateReference refName
      )
      enableSceneRedraw()
    )
  )
  on btnUpdateAll pressed do
  (
    updateDialog()
    for refName in mlbXRefs.items do
    (
      disableSceneRedraw()
      updateReference refName
      enableSceneRedraw()
    )
  )
  on btnRemoveSel pressed do
  (
    refSelCount = (mlbXRefs.selection as array).count
    if (refSelCount > 0) then
    (
      for n in mlbXRefs.selection do
      (
        refName = mlbXRefs.items[n]
        refObjs = for o in objects where (getUserProp o "refName" == refName) collect o
        delete refObjs
      )
      items = #()
      for i = 1 to mlbXRefs.items.count do
      (
        if (findItem mlbXRefs.selection i == 0) then
          append items mlbXRefs.items[i]
      )
      mlbXRefs.items = items
    )
  )
  on btnMakeLocalCopies pressed do
  (
    refSelCount = (mlbXRefs.selection as array).count
    if refSelCount > 0 then
    (
      objs = #()
      for n in mlbXRefs.selection do
        objs += for o in objects where getuserprop o "refName" == mlbXRefs.items[n] collect o
    )
    else
    (
      objs = getCurrentSelection()
    )
	  if objs != undefined then
	  (
		  for o in objs do
		  (
		    if (o.material != undefined) then
		    (
          matIndex = 0
          for m = 1 to meditmaterials.count do
            if meditmaterials[m] == o.material then
              matIndex = m

			    while (classof o.material == XRef_Material) do
          (
			      o.material = o.material.GetSourceMaterial true
          )
          if matIndex != 0 then
            meditmaterials[matIndex] = o.material
          for n = 1 to sceneMaterials.count do
          (
            if sceneMaterials[n].name == o.material.name then
              for s in objects where o.material != undefined and s.material == sceneMaterials[n] do s.material = o.material
          )
		    )
		  )
	  )
  )
  on btnLoadOriginalMats pressed do
  (
    refFiles = #()
    refSelCount = (mlbXRefs.selection as array).count
    for n in mlbXRefs.selection do
    (
      for o in objects where getUserProp o refName == mlbXRefs.items[n] do
      (
        matName = getUserProp o "materialName"
        if matName != undefined then
        (
          if sceneMaterials[matName] != undefined then
            o.material = sceneMaterials[matName]
        )
      )
    )
    if refSelCount > 0 then
    (
      for n in mlbXRefs.selection do
      (
        refFile = undefined
        refRoot = getNodeByName (rootPrefix + mlbXRefs.items[n])
        if refRoot != undefined then
          refFile = getuserprop refRoot "refFile"
        if refFile != undefined then
          appendIfUnique refFiles refFile
      )
    )
    else
    (
      objs = getCurrentSelection()
      for o in objs do
      (
        refFile = undefined
        refFile = getuserprop o "refFile"
        if refFile != undefined then
          appendIfUnique refFiles refFile
        else
          appendIfUnique refFiles (getPublishFile())
      )
    )
    for refFile in refFiles do
    (
      matFile = substituteString refFile "PUBLISH\\" "MATERIALS\\"
      matFile = substituteString matFile ".max" "_mat.max"
      nodeNames = getMAXFileObjectNames matFile
      delete (ieMaxGetNodesByName nodeNames)
      xrefs.addNewXRefObject matFile nodeNames modifiers:#xref manipulators:#xref dupMtlNameAction:#useXRefed
    )
  )
  on btnPublishMats pressed do
  (
    refSelCount = (mlbXRefs.selection as array).count
    refFiles = #()
    objs = #()
    if refSelCount < 1 then
    (
      userSel = getCurrentSelection()
      if userSel.count > 0 then
      (
        for o in userSel do
        (
          refName = getUserProp o "refName"
          if refName != undefined then
            refRoot = getNodeByName (rootPrefix + refName)
          if refRoot != undefined then
          (
            refFile = ieMaxGetMatRefFile xreffile:(getuserprop refRoot "refFile")
            if refFile != undefined then
              appendIfUnique refFiles refFile
          )
        )
        if refFiles.count < 1 then
        (
          print refFiles
          refFiles = #(getPublishFile())
          objs = userSel
        )
      )
      else
        messageBox "Please first select an XRef from the list or objects in the scene" title:"Nothing selected"
    )
    else
    (
      for n in mlbXRefs.selection do
      (
        refRoot = getNodeByName (rootPrefix + mlbXRefs.items[n])
        refFile = false
        if refRoot != undefined then
        (
          refFile = ieMaxGetMatRefFile xreffile:(getuserprop refRoot "refFile")
          if refFile != undefined then
            appendIfUnique refFiles refFile
        )
      )
    )
    for refFile in refFiles do
    (
      if refFile != undefined then
      (
        if objs.count < 1 then
          objs = for o in objects where (getuserprop o "refFile" == refFile) collect o
        for o in objs do
        (
          if (o.material != undefined) then
          (
            while (classof o.material == XRef_Material) do
              o.material = o.material.GetSourceMaterial true
          )
        )
        print "objs:"
        print objs
        print "reffile:"
        print refFile
        publishObjs refFile objs justMaterials:true
      )
    )
  )
  on btnPublishSel pressed do
  (
    publishSelected()
  )
  on btnPublishGeo pressed do
  (
    publishSelected justGeo:true
  )
)
createDialog publishRoll 440 320 130 130 style:#(#style_SysMenu, #style_ToolWindow)
)
