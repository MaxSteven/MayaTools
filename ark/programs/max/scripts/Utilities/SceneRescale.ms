--//-----------------------------------------------------------------------------
--// SceneRescale.ms
--// By Grant Miller (blented@gmail.com)
--// v 1.03
--// Created On: 02/29/08
--// Modified On: 04/11/08
--// tested using Max 2008
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Required Files:
--// ieMax
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Description:
--// Allows you to rescale a selection or an entire scene in order to conform
--// to a set System Scale.
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Revision History:
--//
--// v 1.00 Initial version
--//
--// v 1.01 Added the ability to create a "scale box" by typing in the desired
--//         object dimensions.
--//
--// v 1.02 Added the ability to create a "human scale box", added support for
--//        rescaling rigs, added checks to ensure the scene is always rescaled
--//        before any individual geometry scaling, and some general improvements
--//        with regards to the Target Dimensions and Object Dimensions
--//
--// v 1.03 Added multiple scale reference objects to size models against
--//        improve even further the rescaling workflow with regards to multiple
--//        iterative rescalings of the same object
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
(
--// Includes
--//-----------------------------------------------------------------------------
fileIn (MAX_TOOLS_ROOT + "lib/ieMax.ms")

--// Globals
--//-----------------------------------------------------------------------------
global makeDummy
global rootDummy
global calcResize
global linkAndScale
global setSystemScale
global rescaleRoll
global rescaleFloater

--// Variables
--//-----------------------------------------------------------------------------
targetSystemScale = 10
targetUnitType = #Centimeters
rescalePercent = 1
targetScale = [0,0,0]
objectDim = [0,0,0]
objRescale = [0,0,0]
scaledRigs = #()
scaleDummies = #()
sRef = "$ui\\icons\\Ingenuity_scaleRef.bmp"

--// Functions
--//-----------------------------------------------------------------------------
fn makeDummy =
(
  rootDummy = ieMaxRootDummy()
  rootDummy.name = uniqueName "sceneScaleDummy"
  append scaleDummies rootDummy
  return rootDummy
)
fn cleanDummies =
(
  for d in scaleDummies do
    if (isValidNode d) then delete d

  scaledRigs = #()
)
fn calcResize =
(
   unitResize = units.SystemScale / targetSystemScale
  typeResize = 1

  if (targetUnitType == #Centimeters) then
  (
    if (units.SystemType == #Inches) then
--//        2.54 cm in an inch
      typeResize = 2.54
    else if (units.SystemType == #Feet) then
--//        30.48 cm in a foot
      typeResize = 30.48
    else if (units.SystemType == #Miles) then
--//        160934.4 cm in a mile
      typeResize = 160934.4
    else if (units.SystemType == #Millimeters) then
--//        .1 cm in a millimeter
      typeResize = .1
    else if (units.SystemType == #Centimeters) then
--//        1 cm in a centimeter
      typeResize = 1
    else if (units.SystemType == #Meters) then
--//        100 cm in a meter
      typeResize = 100
    else if (units.SystemType == #Kilometers) then
--//        100,000 cm in a kilometer
      typeResize = 100000
  )
  else if (targetUnitType == #inches) then
  (
    if (units.SystemType == #Inches) then
--//        1 in in an inch
      typeResize = 1
    else if (units.SystemType == #Feet) then
--//        12 in in a foot
      typeResize = 12
    else if (units.SystemType == #Miles) then
--//        63,360 in a mile
      typeResize = 63360
    else if (units.SystemType == #Millimeters) then
--//        0.0393700787 in in a millimeter
      typeResize = 0.0393700787
    else if (units.SystemType == #Centimeters) then
--//        0.393700787 in in a a centimeter
      typeResize = 0.393700787
    else if (units.SystemType == #Meters) then
--//        39.3700787 in in a meter
      typeResize = 39.3700787
    else if (units.SystemType == #Kilometers) then
--//        39,370.0787 in in a kilometer
      typeResize = 39370.0787
  )
  rescalePercent = unitResize * typeResize
)
fn scaleCharacter obj newScale =
(
  skinIndex = 0
  for m = 1 to obj.modifiers.count do
    if (obj.modifiers[m].name == "Skin") then skinIndex = m

  select obj
  max modify mode
  modPanel.setCurrentObject $.modifiers[#Skin]
  if (skinOps.getNumberBones $.modifiers[skinIndex] > 0) then
  (
    rootBone = getnodebyname (skinOps.getBoneName obj.modifiers[skinIndex] 1 1)
    while (rootBone.parent != undefined) do rootBone = rootBone.parent

--//    remove the skin modifier from the selected object, as we are going to rescale the rig and the skin can't be on there
    deleteModifier obj skinIndex
--//    scale the character node
    rootDummy = makeDummy()
    ieMaxMultiLink obj rootDummy
    rootDummy.scale = newScale
    delete rootDummy

--//    if we haven't already scaled the rig then scale it as well
    if (findItem scaledRigs rootBone == 0) then
    (
      print ("Scaling " + rootBone.name + " to " + (newScale as string))
      rootDummy = makeDummy()
      ieMaxMultiLink rootBone rootDummy
      rootDummy.scale = newScale
      delete rootDummy
      append scaledRigs rootBone
    )
  )
)
fn linkAndScale linkItems newScale =
(
  undo "Scene Rescale" on
  (
    nonCharGeometry = #()
    for i in linkItems do
    (
      if (ieMaxIsCharacter i) then
      (
        messageBox (i.name + " was flagged as a character, be sure to paste the copied skin modifier back on the model after rescaling.") title:"Skin Paste Reminder"
        scaleCharacter i newScale
      )
      else if (ieMaxIsGeometry i) then
      (
        append nonCharGeometry i
      )
    )

    rootDummy = makeDummy()
    if (nonCharGeometry.count > 0) then
      ieMaxMultiLink nonCharGeometry rootDummy

    rootDummy.scale = newScale
    setSystemScale()
    cleanDummies()
  )
)
fn setSystemScale =
(
  units.SystemScale = targetSystemScale
  units.SystemType = targetUnitType
)
fn checkSystemScale =
(
  if (units.SystemScale == targetSystemScale and units.SystemType == targetUnitType) then
    return true
--//  otherwise
  else
    messageBox "The scene scale does not match the defined target scale.  The scene should be rescaled before rescaling objects or creating scale reference." title:"Scene Scale Mismatch"
  return false
)
fn checkObjScale obj =
(
  if (obj.scale == [1,1,1]) then
    return true
--//  otherwise
  return false
)

--// Script
--//-----------------------------------------------------------------------------
rollout rescaleRoll "Scene Rescale" width:232 height:592
(
  label lbl1 "File Scale:" pos:[16,32] width:56 height:16
  label lblFileScale "unknown" pos:[72,32] width:144 height:16
  label lbl4 "Rescale:" pos:[64,112] width:56 height:16
  label lblRescalePercent "unknown" pos:[112,112] width:104 height:16
  button btnRescaleSelection "Rescale Selection" pos:[48,136] width:144 height:24
  button btnRescaleAll "Rescale All" pos:[48,160] width:144 height:24
--//  dropdownList ddlTargetUnitType "" pos:[120,48] width:96 height:21 items:#(#inches, #feet, #miles, #millimeters, #centimeters, #meters, #kilometers) selection:5
--//  We just do centimeters and inches right now, can easily add more upon request
  dropdownList ddlTargetUnitType "" pos:[112,72] width:96 height:21 items:#(#inches, #centimeters) selection:2
  label lbl8 "1 Unit = " pos:[24,72] width:40 height:16
  spinner spnTargetSystemScale "" pos:[64,72] width:46 height:16 range:[0.01,100,targetSystemScale]
  GroupBox grp1 "Target Scale:" pos:[16,56] width:200 height:48
  GroupBox grpSceneRescale "Scene Scale" pos:[8,8] width:216 height:184
  GroupBox grp5 "Object Scale" pos:[8,200] width:216 height:312
  button btnObjRescaleSelection "Rescale Selection" pos:[48,456] width:144 height:24
  button btnObjRescaleAll "Rescale All" pos:[48,480] width:144 height:24
  button btnGetDim "Get Dimensions of Selection" pos:[48,304] width:144 height:24
  label lbl16 "Object Dimensions:" pos:[56,224] width:112 height:16
  label lbl17 "Width (X):" pos:[53,360] width:54 height:16
  spinner spnDimX "" pos:[103,360] width:80 height:16 range:[0,10000,0] type:#worldunits scale:1
  label lbl18 "Target Dimensions (0 = proportionate):" pos:[16,336] width:200 height:16
  label lbl19 "Length (Y):" pos:[48,384] width:56 height:16
  spinner spnDimY "" pos:[103,384] width:80 height:16 range:[0,10000,0] type:#worldunits scale:1
  label lbl20 "Height (Z):" pos:[50,408] width:56 height:16
  spinner spnDimZ "" pos:[103,408] width:80 height:16 range:[0,10000,0] type:#worldunits scale:1
  label lblWidthLable "Width (X):" pos:[67,248] width:53 height:16
  button btnCreateScaleBox "Create Dimension Box" pos:[48,432] width:144 height:24
  Timer tmrUnits "Set Units" pos:[16,480] width:24 height:24 interval:5000
  label lbl142 "Height (Z):" pos:[64,280] width:56 height:16
  label lbl143 "Length (Y):" pos:[62,264] width:58 height:16
  label lblX "" pos:[120,248] width:96 height:16
  label lblY "" pos:[120,264] width:96 height:16
  label lblZ "" pos:[120,280] width:96 height:16
  GroupBox grpScaleRef "Scale Reference" pos:[8,520] width:216 height:64
  button btnCreateHuman "" pos:[16,544] width:32 height:32 images:#(sRef, undefined, 5, 1, 1, 1, 1)
  button btnCreateChair "" pos:[56,544] width:32 height:32 images:#(sRef, undefined, 5, 2, 2, 2, 2)
  button btnCreateCounter "" pos:[96,544] width:32 height:32 images:#(sRef, undefined, 5, 3, 3, 3, 3)
  button btnCreateTable "" pos:[136,544] width:32 height:32 images:#(sRef, undefined, 5, 4, 4, 4, 4)
  button btnCreateBed "" pos:[176,544] width:32 height:32 images:#(sRef, undefined, 5, 5, 5, 5, 5)

  fn setUnitDisplay =
  (
    units.DisplayType = #Metric
    units.MetricType = #Meters
    gridPrefs.spacing = 1
  )
  fn updateRescale =
  (
    lblRescalePercent.text = (rescalePercent * 100) as string + " %"
  )
  fn updateSceneScale =
  (
    lblFileScale.text = "1 unit = " + (units.SystemScale as string) + " " + units.SystemType
  )
  fn unitScale x = (x * units.SystemScale / 100) as string
  fn getSelectionDim showWarning =
  (
    userSelection = #()
    userSelection = getCurrentSelection()
    if (userSelection.count > 0) then
      objectDim = ieMaxCalcBoundingBox userSelection
    else if showWarning then
      messageBox "Please select the objects you wish to measure." title:"No Selection"

    lblX.text = (ieMaxFormatNum (unitScale objectDim.x) 2) + "m"
    lblY.text = (ieMaxFormatNum (unitScale objectDim.y) 2) + "m"
    lblZ.text = (ieMaxFormatNum (unitScale objectDim.z) 2) + "m"
  )
  fn checkScale =
  (
    numScaled = 0
    if (targetScale.x != 0) then numScaled += 1
    if (targetScale.y != 0) then numScaled += 1
    if (targetScale.z != 0) then numScaled += 1
    return numScaled
  )
  fn getRescale =
  (
--//    only one value was changed, get all three values from it's ratio
    numScaled = checkScale()
    if (numScaled == 1) then
    (
      if (targetScale.x != 0) then
        objRescale.x = objRescale.y = objRescale.z = targetScale.x / objectDim.x
      else if (targetScale.y != 0) then
        objRescale.x = objRescale.y = objRescale.z = targetScale.y / objectDim.y
      else if (targetScale.z != 0) then
        objRescale.x = objRescale.y = objRescale.z = targetScale.z / objectDim.z
    )
--//    only two were changed, average between them for the third (stupidly long)
    else if (numScaled == 2) then
    (
      if (targetScale.x != 0) then
      (
        if (targetScale.y != 0) then
        (
          objRescale.x = targetScale.x / objectDim.x
          objRescale.y = targetScale.y / objectDim.y
          objRescale.z = ieMaxAverage objRescale.x objRescale.y
        )
        else if (targetScale.z != 0) then
        (
          objRescale.x = targetScale.x / objectDim.x
          objRescale.z = targetScale.z / objectDim.z
          objRescale.y = ieMaxAverage objRescale.x objRescale.z
        )
      )
      else if (targetScale.y != 0) then
      (
        if (targetScale.x != 0) then
        (
          objRescale.y = targetScale.y / objectDim.y
          objRescale.x = targetScale.x / objectDim.x
          objRescale.z = ieMaxAverage objRescale.x objRescale.y
        )
        else if (targetScale.z != 0) then
        (
          objRescale.y = targetScale.y / objectDim.y
          objRescale.z = targetScale.z / objectDim.z
          objRescale.y = ieMaxAverage objRescale.x objRescale.z
        )
      )
      else if (targetScale.z != 0) then
      (
        if (targetScale.y != 0) then
        (
          objRescale.z = targetScale.z / objectDim.z
          objRescale.y = targetScale.y / objectDim.y
          objRescale.x = ieMaxAverage objRescale.z objRescale.y
        )
        else if (targetScale.x != 0) then
        (
          objRescale.z = targetScale.z / objectDim.z
          objRescale.x = targetScale.x / objectDim.x
          objRescale.y = ieMaxAverage objRescale.x objRescale.z
        )
      )
    )
--//    all three were changed
    else
    (
      objRescale.x = targetScale.x / objectDim.x
      objRescale.y = targetScale.y / objectDim.y
      objRescale.z = targetScale.z / objectDim.z
    )
    return objRescale
  )
--//  any file this script is open in should get set properly
  on tmrUnits tick  do
  (
    setUnitDisplay()
    updateSceneScale()
  )
  on spnTargetSystemScale changed val do
  (
    targetSystemScale = spnTargetSystemScale.value
    calcResize()
    updateRescale()
  )

  on spnDimX changed val do targetScale.x = val
  on spnDimY changed val do targetScale.y = val
  on spnDimZ changed val do targetScale.z = val
  on rescaleRoll open do
  (
    updateSceneScale()
    calcResize()
    updateRescale()
    getSelectionDim false
    setUnitDisplay ()
  )
  on ddlTargetUnitType selected sel do
  (
    targetUnitType = ddlTargetUnitType.items[ddlTargetUnitType.selection]
    calcResize()
    updateRescale()
  )
  on btnRescaleSelection pressed  do
  (
    userSelection = ieMaxCopyUserSelection()
    cleanDummies()
    userSelection = #()
    userSelection = ieMaxCopyUserSelection()
    if (userSelection != undefined) then
      linkAndScale userSelection [rescalePercent,rescalePercent,rescalePercent]
    else
      messageBox "Please select the objects you wish to rescale." title:"No Selection"

    updateSceneScale()
    if (userSelection != undefined) then select userSelection
  )
  on btnRescaleAll pressed do
  (
    userSelection = ieMaxCopyUserSelection()
     cleanDummies()
    allObjects = #()
    allObjects = for obj in $* where obj != rootDummy collect obj
    if (allObjects != undefined) then
      linkAndScale allObjects [rescalePercent,rescalePercent,rescalePercent]
    else
      messageBox "There is nothing in the scene to rescale." title:"No Nodes"

    updateSceneScale()
    if (userSelection != undefined) then select userSelection
  )
  on btnGetDim pressed do getSelectionDim true
  on btnObjRescaleAll pressed do
  (
    cleanDummies()
    numScaled = checkScale()
    userSel = getCurrentSelection()
    if (checkSystemScale()) then
    (
      if (numScaled > 0) then
      (
        allObjects = #()
        allObjects = for obj in $* where obj != rootDummy collect obj
        if (allObjects != undefined) then
        (
          if (objectDim != [0,0,0]) then
          (
            if ((ieMaxCalcBoundingBox userSel) != objectDim) then
            (
              if (queryBox "Selection dimensions do not match the current rescaling dimensions, continue the rescale operation?" title:"Dimension Mismatch") then
              (
                objRescale = getRescale()
                linkAndScale userSelection objRescale
              )
            )
            else
            (
              objRescale = getRescale()
              linkAndScale allObjects objRescale
            )
          )
          else
          (
            userSelection = #()
            userSelection = ieMaxCopyUserSelection()
            if (userSelection != undefined) then
            (
              if (queryBox "No object dimensions were defined.  Would you like to use the dimensions of your current selection?" title:"Missing Object Dimensions") then
              (
                getSelectionDim false
                objRescale = getRescale()
                linkAndScale allObjects objRescale
              )
            )
            else
            (
              messageBox "Please select the object you wish to rescale and press 'Get Dimensions of Selection'" title:"Missing Object Dimensions"
            )
          )
        )
        else
        (
          messageBox "There is nothing in the scene to rescale." title:"No nodes..."
        )
      )
      else
      (
        messageBox "Please enter Target Dimensions." title:"No Target Dimensions"
      )
    )
    select userSel
    getSelectionDim false
  )
  on btnObjRescaleSelection pressed do
  (
    cleanDummies()
    numScaled = checkScale()
    userSel = getCurrentSelection()
    if (checkSystemScale()) then
    (
      if (numScaled > 0) then
      (
        userSelection = #()
        userSelection = ieMaxCopyUserSelection()
        if (userSelection != undefined) then
        (
          if (objectDim != [0,0,0]) then
          (
            if ((ieMaxCalcBoundingBox userSel) != objectDim) then
            (
              if (queryBox "Selection dimensions do not match the current rescaling dimensions, continue the rescale operation?" title:"Dimension Mismatch") then
              (
                objRescale = getRescale()
                linkAndScale userSelection objRescale
              )
            )
            else
            (
              objRescale = getRescale()
              linkAndScale userSelection objRescale
            )
          )
          else
          (
            if (queryBox "No object dimensions were defined.  Would you like to use the dimensions of your current selection?" title:"Missing Object Dimensions") then
            (
              getSelectionDim false
              objRescale = getRescale()
              linkAndScale userSelection objRescale
            )
            else
            (
              messageBox "Please select the object you wish to rescale and press 'Get Dimensions of Selection'" title:"Missing Object Dimensions"
            )
          )
        )
        else
        (
          messageBox "Please select the objects you wish to rescale." title:"No Selection"
        )
      )
      else
      (
        messageBox "Please enter Target Dimensions." title:"No Target Dimensions"
      )
    )
    select userSel
    getSelectionDim false
  )
  on btnCreateScaleBox pressed do
  (
    if (checkSystemScale()) then
    (
      userSel = getCurrentSelection()
      existingScaleBox = getNodeByName "TargetDimensions"
      if (existingScaleBox != undefined) then delete existingScaleBox
      numScaled = checkScale()
      if (numScaled > 0) then
      (
        rescaleBB = Box lengthsegs:1 widthsegs:1 heightsegs:1 mapcoords:off pos:[0,0,0] isSelected:off name:"TargetDimensions"
        if (targetScale.x != 0) then rescaleBB.width = targetScale.x else rescaleBB.width = 6
        if (targetScale.y != 0) then rescaleBB.length = targetScale.y else rescaleBB.length = 6
        if (targetScale.z != 0) then rescaleBB.height = targetScale.z else rescaleBB.height = 6
        select userSel
      )
      else
      (
        messageBox "Please enter Target Dimensions." title:"No Target Dimensions"
      )
    )
  )
  on btnCreateHuman pressed do
  (
    if (checkSystemScale()) then
    (
      userSel = getCurrentSelection()
      disableSceneRedraw()
      items = #()
      append items (Box lengthsegs:1 widthsegs:1 heightsegs:1 length:6 width:6 height:15 mapcoords:on pos:[0,0,0] isSelected:on)
      append items (Box lengthsegs:1 widthsegs:1 heightsegs:1 length:4 width:4 height:3 mapcoords:on pos:[0,0,0] isSelected:on)
      items[2].pos = [0,0,15]
      ieMaxAttach items
      $.name = "Human Scale Ref"
      $.wirecolor = color 107 157 242
      select userSel
      enableSceneRedraw()
      completeRedraw()
    )
  )
  on btnCreateChair pressed do
  (
    if (checkSystemScale()) then
    (
      userSel = getCurrentSelection()
      disableSceneRedraw()
      items = #()
      append items (Box lengthsegs:1 widthsegs:1 heightsegs:1 length:5 width:5 height:1 mapcoords:on pos:[0,0,4] isSelected:on)
      append items (Box lengthsegs:1 widthsegs:1 heightsegs:1 length:1 width:1 height:4 mapcoords:on pos:[1.5,1.5,0] isSelected:on)
      append items (instance items[2])
      items[3].pos = [1.5,-1.5,0]
      append items (instance items[2])
      items[4].pos = [-1.5,1.5,0]
      append items (instance items[2])
      items[5].pos = [-1.5,-1.5,0]
      append items (Box lengthsegs:1 widthsegs:1 heightsegs:1 length:1 width:4 height:4 mapcoords:on)
      items[6].pos = [0,2.5,6]
      ieMaxAttach items
      $.name = "Chair Scale Ref"
      $.wirecolor = color 107 157 242
      select userSel
      enableSceneRedraw()
      completeRedraw()
    )
  )
  on btnCreateCounter pressed do
  (
    if (checkSystemScale()) then
    (
      userSel = getCurrentSelection()
      disableSceneRedraw()
      items = #()
      append items (Box lengthsegs:1 widthsegs:1 heightsegs:1 length:6 width:20 height:1 mapcoords:on pos:[0,3,8] isSelected:on)
      append items (Box lengthsegs:1 widthsegs:1 heightsegs:1 length:1 width:20 height:8 mapcoords:on pos:[0,0.5,0] isSelected:on)
      ieMaxAttach items
      $.name = "Counter Scale Ref"
      $.wirecolor = color 107 157 242
      select userSel
      enableSceneRedraw()
      completeRedraw()
    )
  )
  on btnCreateTable pressed do
  (
    if (checkSystemScale()) then
    (
      userSel = getCurrentSelection()
      disableSceneRedraw()
      items = #()
      append items (Box lengthsegs:1 widthsegs:1 heightsegs:1 length:14 width:14 height:1 mapcoords:on pos:[0,0,7] isSelected:on)
      append items (Box lengthsegs:1 widthsegs:1 heightsegs:1 length:1 width:1 height:7 mapcoords:on pos:[6.5,-6.5,0] isSelected:on)
      append items (instance items[2])
      items[3].pos = [6.5,6.5,0]
      append items (instance items[2])
      items[4].pos = [-6.5,6.5,0]
      append items (instance items[2])
      items[5].pos = [-6.5,-6.5,0]
      ieMaxAttach items
      $.name = "Table Scale Ref"
      $.wirecolor = color 107 157 242
      select userSel
      enableSceneRedraw()
      completeRedraw()
    )
  )
  on btnCreateBed pressed do
  (
    if (checkSystemScale()) then
    (
      userSel = getCurrentSelection()
      disableSceneRedraw()
      items = #()
      append items (Box lengthsegs:1 widthsegs:1 heightsegs:1 length:20 width:10 height:4 mapcoords:on pos:[0,0,0] isSelected:on)
      append items (Box lengthsegs:1 widthsegs:1 heightsegs:1 length:3 width:8 height:1 mapcoords:on pos:[0,7.5,4] isSelected:on)
      ieMaxAttach items
      $.name = "Bed Scale Ref"
      $.wirecolor = color 107 157 242
      select userSel
      enableSceneRedraw()
      completeRedraw()
    )
  )
  on rescaleRoll close do
  (
    cleanDummies()
  )
  on rescaleRoll rolledUp state do
  (
    if (state) then
      rescaleFloater.size.y += rescaleRoll.height
    else
      rescaleFloater.size.y -= rescaleRoll.height
  )
)

if rescaleFloater != undefined then CloseRolloutFloater rescaleFloater
floaterWidth = (rescaleRoll.width + 20)
floaterHeight = (rescaleRoll.height + 30)
rescaleFloater = newRolloutFloater "Scene Rescale v1.03" floaterWidth floaterHeight 130 130
addRollout rescaleRoll rescaleFloater
)
--//-----------------------------------------------------------------------------
