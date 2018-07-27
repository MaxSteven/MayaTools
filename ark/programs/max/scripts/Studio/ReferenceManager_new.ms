--// Make unique "Material names"
--// object names have to be unique
--// cache button

--// doesn't properly delete controls when Update Selected is run (only rig/controls related)

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
fn isRoot nodeName = return (toLower (substring nodeName 1 8) == "xrefroot")

--// Compares scene settings with cam settings
fn fnSettingsCheck start end rate =
(
	if frameRate != rate OR animationRange.start != start OR animationRange.end != end then
    return false
  else
    return true
)
--// Used for publishing to allow for deep referencing
fn fnCleanOut =
(
	objs = getCurrentSelection()

--// Deletes xrefRoot
	for o in objs do
	(
		try
    (
			refName = getAppData o objData.refName
			refNameLength = refName.count
			xRefRoot = getNodeByName (rootPrefix + refName)
			delete xRefRoot
		)
    catch()
	)
--// Removes the "::refName" from the ctrl and con objects
	for o in objs do
	(
		try
    (
			refName = getAppData o objData.refName
			refNameLength = refName.count
			for o in objs do o.name = substring o.name 1 (o.name.count - refNameLength - refSplitLength)
		)
    catch()
	)
)

--// converts a string "[0,20,50]" to a point3
fn fnStringToPoint3 v =
(
	local pa = filterString v "[],"
	val = point3 (pa[1] as float) (pa[2] as float) (pa[3] as float)
	return val
)

--// makes sure all rig controls have "con" in the name to be filtered properly when published
fn fnHierarchyToRig =
(
	for s in objects do
	(
--// if it has no children or it's a control or the main CON then it is already good to go
		if not ((s.children.count == 0 and (superclassof s == GeometryClass) and (classof s != BoneGeometry)) or (isCon s.name or isCtrl s.name)) then
    (
			s.name = "con_" + s.name
		)
	)
)

--// Clicks the "OK" button on loading envelopes for the skin modifier
fn pressEnvelopeLoadOk =
(
  WindowHandle = DialogMonitorOPS.GetWindowHandle()
  dialogName = UIAccessor.GetWindowText WindowHandle
  if dialogName != undefined and matchpattern dialogName pattern:"*Load Envelopes*" then
	  UIAccessor.PressButtonByName WindowHandle "OK"
  return true
)

--// gets both children/parents of obj's heirarchy
fn getHierarchy objs =
(
  hierarchy = objs
  for obj in objs do
  (
		hierarchy += obj.children
    if (obj.parent != undefined) then
      hierarchy += obj.parent
	)
  return hierarchy
)

--// creates the reference name for a given object/refname combo
fn getRefName objName refName =
(
  splitLoc = findstring objName refSplit
  if splitLoc != undefined then
    objName = substring objName 1 (splitLoc - 1)
  return objName + refSplit + refName
)

--// Stores the integer
--// ro is the reference manager's offset for appdata
ro = 87632
struct objData
(
  skinPosPOS = ro+1,
  skinPosROT = ro+2,
  skinPosSCA = ro+3,
  boneNames = ro+4,
  skinEnvelopes = ro+5,
  objectName = ro+6,
  materialName = ro+7,
  refName = ro+8,
  refFile = ro+9,
  animStart = ro+10,
  animEnd = ro+11,
  framerate = ro+12
)

fn fnSkinPoseUserProps arr =
(
	for obj in arr do
  (
		in coordsys parent
    (
			myRot = quatToEuler obj.rotation
			POS = obj.pos
			ROT = [myRot.x, myRot.y, myRot.z]
			SCA = obj.scale
			setAppData obj objData.skinPosPOS POS
			setAppData obj objData.skinPosROT ROT
			setAppData obj objData.skinPosSCA SCA
		)
	)
)

fn fnSkinPoseSet arr =
(
	for obj in arr do
  (
		try
    (
			obj.skinPos = fnStringToPoint3 (getAppData obj objData.skinPosPOS)
			obj.skinRot = fnStringToPoint3 (getAppData obj objData.skinPosROT)
			obj.skinScale = fnStringToPoint3 (getAppData obj objData.skinPosSCA)
		)
    catch()
	)
)

fn fnSkinPoseSwitch objs state:#false =
(
  if state then
    for o in objs do o.skinPoseMode = true
  else
    for o in objs do o.skinPoseMode = false
)

--// Find all Skinned objects in the scene and save out the weights
fn fnSaveOutWeights objs =
(
	filePathParts = filterstring maxFilePath "\\"
  --// Only save out the weights if we are in the rig file
	if filePathParts[filePathParts.count] == "RIG" do
	(
		fnSkinPoseUserProps objs
		for o in objs do if superclassof o == geometryClass do
		(
      --// When there is a skin modifier proceed to save the weights
			for m in o.modifiers where classof m == skin do
			(
				if m.enabled == true do
				(
					displayTempPrompt  ("Saving Weights" + " '" + o.name as string + "'...") 999999

					--// Saving out the weights
					boneNames = #()

          --//get the number of bones in skin modifier
					numBones = skinOps.GetNumberBones o.modifiers[m.name]
					max modify mode
					modPanel.setCurrentObject o.modifiers[m.name]

          --//try to delete previous skinning if possible
					try
          (
            deleteFile (maxfilepath + o.name as string + ".env")
          )
          catch()

					envelopes = (maxfilepath + o.name as string + ".env")
					skinOps.saveEnvelope o.modifiers[m.name] envelopes

					--// Store the bones used in the skin modifier
          --// Add to an array the name of all the bones in the skin modifier
					for b = 1 to numBones do
          (
						boneObject = skinOps.GetBoneName o.modifiers[m.name] b 1 --//0 = transform  |  1 = object name
						append boneNames boneObject
					)
					setAppData o objData.boneNames boneNames
					setAppData o objData.skinEnvelopes envelopes

					max create mode
					removeTempPrompt()
				)
			)
		)
	)
)

--// Loads in the envelope weights for the objects with a skin modifer
fn fnLoadEnvelopeWeights objs =
(
	for o in objs do if superclassof o == geometryClass do
	(
    --// When there is a skin modifier proceed to save the weights
		for m in o.modifiers where classof m == skin do
		(
			DialogMonitorOPS.RegisterNotification pressEnvelopeLoadOk ID:#refManagerEnvelopes

			if m.enabled == true do
			(
				displayTempPrompt  ("Loading Weights" + " '" + o.name as string + "'...") 999999

				select o
				max modify mode

				modPanel.setCurrentObject o.modifiers[m.name]

				--//Remove all current bones in skin Modifier
				numBones = skinOps.GetNumberBones o.modifiers[m.name] --//get the number of bones in skin modifier
				for b = 1 to numBones do (--//Repeatly removes the bones in the list until they are all removed
					skinOps.buttonRemove o.modifiers[m.name]
				)

				--// Get list of bones used in skin modifier (found in user props of object)
				envelopes = getAppData o objData.skinEnvelopes as string
				boneNames = getAppData o objData.boneNames
        --// turns an (array as a string) back to an array
				boneNamesArr = execute boneNames
				boneArr = #()
				boneArr = ieMaxGetNodesByName boneNamesArr
				modPanel.setCurrentObject o.modifiers[m.name]
				for b in boneArr do (
					skinOps.addbone o.modifiers[m.name] b -1
				)

				--// o.modifiers[m.name].filter_vertices = on
				forceCompleteRedraw() -- Need to use completeRedraw() or the weights wont load when in a loop......RUBBISH!
				skinOps.loadEnvelope o.modifiers[m.name] envelopes

				DialogMonitorOPS.Enabled = true

				max create mode
				removeTempPrompt()
			)
		)
	)
)

fn getRoots objs =
(
  return for o in objs where o.parent == undefined collect o
)

fn getGeometryNames objectNames curSceneObjectNames =
(
	geometryNames = #()
	for o in objectNames do
	(
		if (isCtrl o or isCon o) then
		(
			if (findItem curSceneObjectNames o == 0) then
				append geometryNames o
		)
		else
			append geometryNames o
	)
	return geometryNames
)

fn updateReference refFile fileObjectNames curSceneObjectNames =
(
  refObjectNames = getGeometryNames fileObjectNames curSceneObjectNames
  print "Merging Objects:"
  print refObjectNames
  mergeMaxFile refFile refObjectNames #select #alwaysReparent #useSceneMtlDups quiet:true
  return (ieMaxGetNodesByName refObjectNames)
)

fn mergeObjects refFile fileObjectNames =
(
  print "Merging:"
  print fileObjectNames
  if (fileObjectNames.count > 0) then
  (
    mergeMaxFile refFile #alwaysReparent #useSceneMtlDups quiet:true
    return (ieMaxGetNodesByName fileObjectNames)
  )
  else
    return #()
)

fn setRefProps objs refName refFile =
(
  for o in objs do
  (
    setAppData o objData.objectName o.name
	  if (o.material != undefined) then
		  setAppData o objData.materialName o.material.name
    setAppData o objData.refName refName
    setAppData o objData.refFile refFile
    o.name = getRefName o.name refName
  )
)

fn updateGeometry refName =
(
	xRefRoot = getNodeByName (rootPrefix + refName)
	xRefTransform = xRefRoot.transform
	refFile = getAppData xRefRoot objData.refFile
	currSceneObjNames = #()
	sceneMats = #()
	matObjs = #()
	--xRefRoot.transform = matrix3 1

	filePathParts = filterstring maxFilePath "\\"
	if filePathParts[filePathParts.count] == "3DSMAX" then --//If master file then just delete old and merge new
	(
		refGeometry = for o in objects where (getAppData o objData.refName == refName) collect o
--//		delete refGeometry
--//		print refFile
--//		reference in file again and reset initial offset
	)
	else
	(
		refGeometry = for o in objects where (getAppData o objData.refName == refName AND NOT isCtrl o.name AND NOT isCon o.name AND NOT isRoot o.name) collect o

		for o in refGeometry do
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
		delete refGeometry
	)

		--// All rig/heirarchy related controls
		ctrlObjs = for o in objects where (getAppData o objData.refName == refName AND (isCtrl o.name OR isCon o.name)) collect o
		refNameLength = refName.count
    --//remove the "::refName" from the ctrl and con objects
		for o in ctrlObjs do
      o.name = substring o.name 1 (o.name.count - refNameLength - refSplitLength)

		--// Get remaining scene object names
		currSceneObjNames = for o in objects where (getAppData o objData.refName == refName AND NOT isRoot o.name) collect o.name --//Gets and returns an array of the scene object names

		if (refFile != undefined) then
		(
			fileObjectNames = getMAXFileObjectNames refFile
			refGeometry = updateReference refFile fileObjectNames currSceneObjNames

			--// Skinning Takes place
      --// set each objects skin pose since it does not merge
			fnSkinPoseSet objects
      --// turn ON skin mode
			fnSkinPoseSwitch objects state:#true
      --// updates the skinning
			fnLoadEnvelopeWeights refGeometry
      --// turn OFF skin mode
			fnSkinPoseSwitch objects state:#false

			setRefProps refGeometry refName refFile
		)
		else
		(
			print "Could not update selected reference"
		)

		--// compare scene names to incoming names in fileObjectNames, then delete anything that's not in fileObjectNames
		for itemName in currSceneObjNames do
		(
			exists = findItem fileObjectNames itemName
			if exists == 0 do delete (getNodeByName itemName)
		)

		--// Updates the ctrlObjs array with all the updated objects
		ctrlObjs = for o in objects where (getAppData o objData.refName == refName AND (isCtrl o.name OR isCon o.name)) collect o

		--// swap the ctrl and con objects back to their ref names
		for o in ctrlObjs do
      o.name = getRefName o.name refName
		objRoots = getRoots (ctrlObjs + refGeometry)
		for o in objRoots do
      o.parent = xRefRoot
		xRefRoot.transform = xRefTransform

		for o in refGeometry do
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
try ( destroydialog ::publishRoll )catch()

rollout publishRoll "PublishTools v1.00"
(
	label lbLocationPath "" pos:[0,0] width:460 height:16 style_sunkenedge:true

	label lbPublish "Publish:" pos:[10,34]
	label lbEdge "" style_sunkenedge:true width:400 height:28 pos:[49,26]
	button btnPublishGeo "Selected Objects" pos:[50,27] width:134 height:26
	button btnPublishMats "Materials for Selected" pos:[184,27] width:132 height:26
	button btnPublishSel "Selected Objs and Mats" pos:[316,27] width:132 height:26

	checkbutton btnRefTools "« Ref Tools »" pos:[10,62] width:439 height:18
	groupbox gpRefTools "" width:439 height:199 pos:[10,74] visible: false

	label lbFiles "Files:" pos:[20,90]
	dropdownList ddlLocations "" pos:[48,86] width:94 height:21 items:#("Shot Assets", "Project Assets", "Global Assets") selection:1
	multiListBox mlbMaxFiles "" pos:[18,112] width:124 height:9

	button btnRefSel "Reference Selected " pos:[18,235] width:124 height:28
	label lbReferences "References:" pos:[156,90]
	multiListBox mlbXRefs "" pos:[156,112] width:124 height:9
	button btnRefreshRefs "Refresh" pos:[156,235] width:62 height:28
	button btnRemoveSel "Remove" pos:[218,235] width:62 height:28

	groupbox lbRefOpts "References:" width:144 height:96 pos:[294,90]
	label lbUpdateRefs "Update:" pos:[303,113]
	button btnUpdateSel "Selected" pos:[345,110] width:51 height:22
	button btnUpdateAll "All" pos:[396,110] width:34 height:22
	label lbRoots "Roots:" pos:[303,135]
	button btnSelectRefRoot "Select" pos:[345,132] width:51 height:22
	button btnToggleRefRoots "Hide" pos:[396,132] width:34 height:22
	button btnDeleteUnresolved "Delete Invalid" pos:[345,154] width:85 height:22

	groupbox lbMatOpts "Materials:" width:144 height:74 pos:[294,189]
	label lbUpdateMats "Update:" pos:[303,212]
	button btnLoadOriginalMats "Selected" pos:[345,209] width:51 height:22
	button btnLoadAllOriginalMats "All" pos:[396,209] width:34 height:22
	label lbEditMats "Edit:" pos:[303,234]
 	button btnMakeLocalCopies "Selected" pos:[345,231] width:51 height:22

	on btnRefTools changed state do
	(
		if state == on then
		(
			publishRoll.height = 283
			gpRefTools.visible = state
		)
    else
    (
			publishRoll.height = 86
			gpRefTools.visible = state
		)
	)


--// Functions
--//-----------------------------------------------------------------------------

  --// shows all the references in the current scene
  fn updateReferenceList =
  (
    mlbXRefs.items = for o in objects where (findString o.name "XREFROOT_" != undefined) collect (substring o.name 10 -1)
    mlbXRefs.items = mlbXRefs.items
  )

  --// Gets the .max files and there directory paths
  fn getMaxFiles root pattern type:#Publish =
  (
    dir_array = GetDirectories (root+"/*")
    for d in dir_array do
    join dir_array (GetDirectories (d+"/*"))
    append dir_array (root+"/*")

    my_files = #()
    if type == Publish then
    (
      for d in dir_array do
      (
        pathParts = filterstring (d as string) "\\"
        tempdir = ""
        if pathParts[pathParts.count] == "PUBLISH" then
          join my_files (getFiles (d + pattern))
      )
    )
    else if type == MaxFiles then
    (
      for f in dir_array do
        join my_files (getFiles (f + pattern))
    )
    return sort my_files
  )

  --// Populates the list with the filenames if possible, and updates the status bar with dir path
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
        maxFilePaths = getMaxFiles fileDir "*.max" type:#MaxFiles
      )
      else if doesFileExist ((ieMaxJoinArray (ieMaxArraySlice (filterString maxfilepath "\\") 1 -1) "\\") +"PUBLISH") then
      (
        fileDir = (ieMaxJoinArray (ieMaxArraySlice (filterString maxfilepath "\\") 1 -1) "\\") +"PUBLISH"
        maxFilePaths = getMaxFiles fileDir "*.max" type:#MaxFiles
      )
    )
    else if itm == 2 then
    (
      if doesFileExist ((fnPathBuilder 2) + "GLOBAL_ASSETS") then
      (
        fileDir = (fnPathBuilder 2) + "GLOBAL_ASSETS"
        maxFilePaths = getMaxFiles fileDir "*.max" type:#Publish
      )
    )
    else if itm == 3 then
    (
      fileDir = getSavePath initialDir:"Q:\ASSETS\MODELS"
      if fileDir != undefined then
        maxFilePaths = getMaxFiles fileDir "*.max" type:#MaxFiles
      else
        fileDir = ""
    )
  )
  fn referenceSelected refFile =
  (
    updateReferenceList()
    refFile = false

	--//Master root checker
	if refFile != false and doesFileExist refFile then
	(
	  fileObjectNames = getMAXFileObjectNames refFile
	  allObjects = mergeObjects refFile fileObjectNames

    --// If you're importing a camera then prompt scene settings check
	  for obj in allObjects where superclassof obj == camera do
    (
		  camStart = (getAppData obj objData.animStart as string) as integer
		  camEnd = (getAppData obj objData.animEnd as string) as integer
		  camRate = getAppData obj objData.framerate as integer

		  if not (fnSettingsCheck camStart camEnd camRate) do --False (scene settings do not match incoming camera settings)
		  (
			  camFRateInfo = ("Framerate: " + camRate as string )
			  camFRangeInfo = ("Frame Range: " + camStart as string + "-" + camEnd as string)
			  if queryBox ("Scene settings mismatch. \nDo you want to matching your incoming camera settings? \n\n" + obj.name + "\n" + camFRateInfo + "\n" + camFRangeInfo) beep:false do
			  (
				  animationRange = interval camStart camEnd
				  frameRate = camRate
			  )
		  )
	  )

	  --// figure out what number to put after this (laser001 if it's the first, laser092 if we've got several)
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

	  --// Set the refName so we can know where these things came from
	  xRefRoot = point name:(rootPrefix + refName)
	  setAppData xRefRoot objData.refFile refFile
	  setAppData xRefRoot objData.refName refName

	  --// set xref properties on all the objects
	  setRefProps allObjects refName refFile
	  --// needed to update the material references
	  objXRefMgr.UpdateAllRecords()
    --// (ctrlObjs + xRefObjs)
	  objRoots = getRoots allObjects
	  for o in objRoots do o.parent = xRefRoot

	  --// Links the cameras target object to the parent of the camera if it does not have a parent
	  --//Link the target obj to the same xrefRoot of its corresponding camera
    for o in allObjects where superclassof o == camera AND classof o == Targetcamera do
    (
     --//Camera Target
		  try
      (
			  target = o.target
			  if classof target == Targetobject AND target.parent == undefined do (target.parent = o.parent)
		  )
      catch()
	  )

	  userSel = getCurrentSelection()
	  if userSel.count < 1 then
	    select xRefRoot
	  )
	  else
	  (
	  messageBox ("Couldn't find file: " + refFile) title:"Bad Reference File"
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
    userSel = getCurrentSelection()
	  objects = getHierarchy userSel
	  fnHierarchyToRig()
	  fnSaveOutWeights objects -- Save skinned objects weights
	  for o in objects do o.name = (substituteString o.name refSplit "_") --//Replace "::" with "_"

      for o in objects where superclassof o == camera do
      (
        setTransformLockFlags o #all
        setAppData o objData.animStart animationRange.start
        setAppData o objData.animEnd animationRange.end
        setAppData o objData.framerate framerate
        --// If the camera has a target then lock the target object transform
		    try
        (
          --//Camera Target
			    target = o.target
			    if classof target == Targetobject do (setTransformLockFlags target #all)
		    )
        catch()
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


	on mlbMaxFiles doubleClicked itm do
	(
		clearlistener()
		maxfile = maxFilePaths[itm]
		this = maxFileNames[itm]
		print maxfile
		print this
		refFile = maxFilePaths[itm]
		referenceSelected refFile
	)

	on mlbXRefs doubleClicked itm do
	(
		refName = mlbXRefs.items[itm]
		refObjs = for o in objects where (getAppData o objData.refName == refName) collect o
		delete refObjs

		items = #()
		for i = 1 to mlbXRefs.items.count do
		(
			if (findItem mlbXRefs.selection i == 0) then
			append items mlbXRefs.items[i]
		)
		mlbXRefs.items = items
	)

	on btnRefSel pressed do
	(
		updateReferenceList()
		for sel in mlbMaxFiles.selection do
		(
			refFile = maxFilePaths[sel]
			referenceSelected refFile
		)
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
			btnToggleRefRoots.caption = "Show"
		)
		else
		(
			for o in $XREFROOT_* do o.isHidden = false
			btnToggleRefRoots.caption = "Hide"
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
				updateGeometry refName
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
			updateGeometry refName
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
				refObjs = for o in objects where (getAppData o objData.refName == refName) collect o
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
        objs += for o in objects where getAppData o objData.refName == mlbXRefs.items[n] collect o
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
      for o in objects where getAppData o objData.refName == mlbXRefs.items[n] do
      (
        matName = getAppData o objData.materialName
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
          refFile = getAppData refRoot objData.refFile
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
        refFile = getAppData o objData.refFile
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
          refName = getAppData o objData.refName
          if refName != undefined then
            refRoot = getNodeByName (rootPrefix + refName)
          if refRoot != undefined then
          (
            refFile = ieMaxGetMatRefFile xreffile:(getAppData refRoot objData.refFile)
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
          refFile = ieMaxGetMatRefFile xreffile:(getAppData refRoot objData.refFile)
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
          objs = for o in objects where (getAppData o objData.refFile == refFile) collect o
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
createDialog publishRoll 460 86 style:#(#style_SysMenu, #style_ToolWindow)--344
)
