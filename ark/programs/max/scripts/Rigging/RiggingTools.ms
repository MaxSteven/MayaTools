--//-----------------------------------------------------------------------------
--// RiggingTools.ms
--// By Grant Miller (blented@gmail.com)
--// v 1.04
--// Created On: 03/31/08
--// Modified On: 05/01/08
--// tested using Max 2008
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Required Files:
--// ieMax
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Description:
--// Various rigging tools used to get character's skeletons up and running faster
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Revision History:
--//
--// v 1.00 Initial version
--//
--// v 1.01 Fixed the way points helpers are created as they are different than
--// most controls, also now selects the control on creation
--//
--// v 1.02 Fixed a bug with the bone transformation on mirrored bones that caused
--// controllers to be inaccurately positioned on non-root mirrored bones
--//
--// v 1.03 Properly initializes bones to behave as bone geometry (no stretching,
--//        auto-align, etc)
--//
--// v 1.04 Fixed the way the mirror bones feature mirrors controllers, changed the
--//        way the color switching works to make it a bit more intuitive.
--//
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
(
--// Includes
--//-----------------------------------------------------------------------------
fileIn (MAX_TOOLS_ROOT + "lib/ieMax.ms")

--// Globals
--//-----------------------------------------------------------------------------
global lastPoint
global lastCircle
global lastNGon
global lastRectangle
global lastStar
global lastRigObj
global riggingToolsRoll
global riggingToolsFloater

--// Variables
--//-----------------------------------------------------------------------------
leftColor = (color 28 28 177)
centerColor = (color 255 246 0)
rightColor = (color 176 26 26)

--//The ZPos of mirrored bones gets flipped on the Z axis
--//boneFlipTM = (angleaxis 90 [1,0,0]) as matrix3
boneFlipTM = matrix3 1
boneFlipTM[3] = [0,0,-1]
--// Functions
--//-----------------------------------------------------------------------------

--// Script
--//-----------------------------------------------------------------------------
--//attribute stuff:
--//want to be able to add attributes to a given object's attribute holder
--//should find automatically and select it when we start adding stuff
--//should be able to view / copy / paste a current object's attributes
--//also possibly save those attributes to a file
--//no need to build in lots of presets just build tools that allow building of presets
--//
--//rigging objects:
--//buttons for common rigging objects that auto-align to the currently selected whatever and scale accordingly
--// common:
--// pos:whatever
--// isSelected:on
--//Ngon radius:3.87188 nsides:8
--//Rectangle length:2.62631 width:1.19791
--//Circle radius:2.67006
--//Star radius1:4.75613 radius2:2.93605 numPoints:6
--//Point size:7.81871 cross:off
--//
--//misc:
--//mirror tools to mirror a rig and also to rename its bones based on a char match of user-entered first char
--//poke around objectoffsetpos and objectoffsetrot for the zeroing
--//
--//pivot tools:
--//align an object's pivot to its bb center
--//align an object's pivot to the bb center of a selected object(s)
--//align an object's pivot to select pivot
rollout riggingToolsRoll "Rigging Tools" width:208 height:512
(
  GroupBox grp1 "Rigging Objects" pos:[8,8] width:192 height:304

  colorPicker cpkLeftColor "" pos:[32,48] width:44 height:24 color:(color 28 28 177)
  colorPicker cpkCenterColor "" pos:[80,48] width:44 height:24 color:(color 255 246 0)
  colorPicker cpkRightColor "" pos:[128,48] width:44 height:24 color:(color 176 26 26)
  checkbutton ckbLeftColor "Left" pos:[36,32] width:40 height:16 checked:true
  checkbutton ckbCenterColor "Center" pos:[84,32] width:40 height:16
  checkbutton ckbRightColor "Right" pos:[132,32] width:40 height:16

  label lbl1 "Size:" pos:[91,88] width:48 height:16
  label lbl2 "Radius:" pos:[91,128] width:48 height:16
  label lbl3 "Radius:" pos:[91,152] width:48 height:16
  label lbl4 "Sides:" pos:[91,168] width:48 height:16
  label lbl5 "Length:" pos:[91,192] width:48 height:16
  label lbl6 "Width:" pos:[91,208] width:48 height:16
  label lbl7 "Radius1:" pos:[91,232] width:48 height:16
  label lbl8 "Radius2:" pos:[91,248] width:48 height:16
  label lbl9 "Points:" pos:[91,264] width:40 height:16
  button btnPoint "Point" pos:[19,88] width:64 height:32
  button btnCircle "Circle" pos:[19,128] width:64 height:16
  button btnNGon "NGon" pos:[19,152] width:64 height:32
  button btnRectangle "Rectangle" pos:[19,192] width:64 height:32
  button btnStar "Star" pos:[19,232] width:64 height:48
  spinner spnPointSize "" pos:[139,88] width:48 height:16 range:[0,1000,1] type:#worldunits scale:0.5
  checkbox chkPointCross "Cross" pos:[140,104] width:48 height:16
  spinner spnCircleRadius "" pos:[139,128] width:48 height:16 range:[0,10000,3] type:#worldunits scale:0.5
  spinner spnNGonRadius "" pos:[139,152] width:48 height:16 range:[0,10000,3] type:#worldunits scale:0.5
  spinner spnNGonSides "" pos:[139,168] width:48 height:16 range:[3,100,8] type:#integer scale:1
  spinner spnRectLength "" pos:[139,192] width:48 height:16 range:[0,10000,2] type:#worldunits scale:0.5
  spinner spnRectWidth "" pos:[139,208] width:48 height:16 range:[0,10000,2] type:#worldunits scale:0.5
  spinner spnStarRadius1 "" pos:[139,232] width:48 height:16 range:[0,10000,2] type:#worldunits scale:0.5
  spinner spnStarRadius2 "" pos:[139,248] width:48 height:16 range:[0,10000,3] type:#worldunits scale:0.5
  spinner spnStarPoints "" pos:[139,264] width:48 height:16 range:[3,100,6] type:#integer scale:1
  checkbox chkPivotAlign "Pivot Align" pos:[19,288] width:72 height:16 checked:true
  checkbox chkCenterAlign "Center Align" pos:[107,288] width:80 height:16

  button btnZeroTransform "Zero Object Transform" pos:[8,320] width:192 height:24
  checkbutton ckbAffectPivot "Affect Pivot" pos:[8,344] width:96 height:24
  button btnPivotToCenter "Pivot->Center" pos:[104,344] width:96 height:24
  button btnPivotToObjCenter "Pivot->Obj Center" pos:[8,368] width:96 height:24
  button btnPivotToObjPivot "Pivot->Obj Pivot" pos:[104,368] width:96 height:24

  GroupBox grp12 "Mirroring" pos:[8,400] width:192 height:104
  label lbl103 "Replace:" pos:[24,424] width:48 height:16
  label lbl104 "With:" pos:[120,424] width:24 height:16
  edittext edtReplace pos:[72,424] width:40 height:16 text:"L"
  edittext edtWith pos:[144,424] width:40 height:16 text:"R"
  radiobuttons rdoMirrorAxis "" pos:[80,448] width:97 height:16 labels:#("X", "Y", "Z") columns:3
  label lbl105 "Mirror Axis:" pos:[24,448] width:56 height:16
  button btnMirrorSelectedBones "Mirror Selected Bones" pos:[24,472] width:160 height:24

  tool placeRigObj
  (
    on mouseMove clickno do
    (
      lastRigObj.pos = worldPoint
    )
    on mousePoint clickno do
    (
      if (clickno == 1) then
        lastRigObj.pos = worldPoint
      else
        #stop
    )
  )
  fn getCurrentColor =
  (
    if (ckbLeftColor.checked) then return leftColor
    else if (ckbCenterColor.checked) then return centerColor
    else return rightColor
  )
  fn configRigObj rigObj =
  (
    rigObj.wireColor = getCurrentColor()

    userSel = getCurrentSelection()
    if (userSel.count < 1) then
    (
      startTool placeRigObj
      return true
    )
    else
    (
      rigObj.name = userSel[1].name + "Control"
    )

    if (classOf rigObj != Point) then
    (
      rigObj.transform = userSel[1].transform
      in coordsys local rotate rigObj (angleaxis -90 [0,1,0])
    )
    else
    (
      rigObj.pos = userSel[1].pos
    )

    if (chkPivotAlign.state != true) then
      rigObj.pos = ieMaxCalcBBCenter userSel
  )
  fn mirrorBoneChain rootBone parentBone mirrorTM =
  (
    startPos = rootBone.pos * mirrorTM
    if (rootBone.children.count > 0) then
      endPos = rootBone.children[1].pos * mirrorTM
    else
      endPos = ([1,0,0] * rootBone.transform) * mirrorTM

    zPos = ([0,0,1] * rootBone.transform) * mirrorTM
--//    if (rootBone.parent == undefined) then
--//      zPos = (startPos - zPos)
--//    else
      zPos = (zPos - startPos)
--//    zPos *= (quat 90 rootBone.pos)
    mirrorBone = BoneSys.createBone startPos endPos zPos
    mirrorBone.parent = parentBone
    mirrorBone.wireColor = getCurrentColor()
    mirrorBone.name = substituteString rootBone.name edtReplace.text edtWith.text

    if (rootBone.children.count > 0) then
    (
        for c in rootBone.children do
          mirrorBoneChain c mirrorBone mirrorTM
    )
  )
  fn mirrorBoneChainOld rootBone parentBone mirrorTM =
  (
    mirrorBone = copy rootBone

    if (superClassOf mirrorBone != shape) then
    (
      mirrorBone.setBoneEnable true 0
      setRenderable mirrorBone false
    )

    mirrorBone.transform *= mirrorTM
    mirrorBone.parent = parentBone
    mirrorBone.wireColor = getCurrentColor()

    replaceLoc = findString rootBone.name edtReplace.text
    if (replaceLoc != undefined) then
      mirrorBone.name = edtWith.text + (substring rootBone.name (replaceLoc + 1) rootBone.name.count)

    if (rootBone.children.count > 0) then
    (
        for c in rootBone.children do
          mirrorBoneChain c mirrorBone mirrorTM
    )
  )

--// Point
--//-----------------------------------------------------------------------------
  on btnPoint pressed  do
  (
    undo "Create Point" on
    (
      lastRigObj = lastPoint = Point size:spnPointSize.value cross:off box:on
      lastPoint.rotation = (quat 0 0 0 1)
      if (chkPointCross.state) then lastPoint.cross = on
      configRigObj lastPoint
      lastPoint.wireColor = (color 14 255 2)
      select lastPoint
    )
  )
  on spnPointSize changed val do
  (
    if (isValidNode lastPoint) then lastPoint.size = val
  )
  on chkPointCross changed state do
  (
    if (isValidNode lastPoint) then lastPoint.cross = state
  )

--// Circle
--//-----------------------------------------------------------------------------
  on btnCircle pressed  do
  (
    undo "Create Circle" on
    (
      lastRigObj = lastCircle = Circle radius:spnCircleRadius.value
      configRigObj lastCircle
      select lastCircle
    )
  )
  on spnCircleRadius changed val do
  (
    if (isValidNode lastCircle) then lastCircle.radius = val
  )

--// NGon
--//-----------------------------------------------------------------------------
  on btnNGon pressed  do
  (
    undo "Create NGon" on
    (
      lastRigObj = lastNGon = NGon radius:spnNGonRadius.value nsides:spnNGonSides.value
      configRigObj lastNGon
      select lastNGon
    )
  )
  on spnNGonRadius changed val do
  (
    if (isValidNode lastNGon) then lastNGon.radius = val
  )
  on spnNGonSides changed val do
  (
    if (isValidNode lastNGon) then lastNGon.nsides = val
  )

--// Rectangle
--//-----------------------------------------------------------------------------
  on btnRectangle pressed  do
  (
    undo "Create Rectangle" on
    (
      lastRigObj = lastRectangle = Rectangle length:spnRectLength.value width:spnRectWidth.value
      configRigObj lastRectangle
      select lastRectangle
    )
  )
  on spnRectLength changed val do
  (
    if (isValidNode lastRectangle) then lastRectangle.length = val
  )
  on spnRectWidth changed val do
  (
    if (isValidNode lastRectangle) then lastRectangle.width = val
  )

--// Star
--//-----------------------------------------------------------------------------
  on btnStar pressed  do
  (
    undo "Create Star" on
    (
      lastRigObj = lastStar = Star radius1:spnStarRadius1.value radius2:spnStarRadius2.value numPoints:spnStarPoints.value
      configRigObj lastStar
      select lastStar
    )
  )
  on spnStarRadius1 changed val do
  (
    if (isValidNode lastStar) then lastStar.radius1 = val
  )
  on spnStarRadius2 changed val do
  (
    if (isValidNode lastStar) then lastStar.radius2 = val
  )
  on spnStarPoints changed val do
  (
    if (isValidNode lastStar) then lastStar.numPoints = val
  )

  on chkPivotAlign changed state do chkCenterAlign.checked = not state
  on chkCenterAlign changed state do chkPivotAlign.checked = not state
  on cpkLeftColor changed col do
  (
    oldColor = leftColor
    for s in $* do
      if (s.wireColor == oldColor) then s.wireColor = col

    leftColor = col
    if (ckbLeftColor.checked and isValidNode lastRigObj) then
      lastRigObj.wireColor = col
  )
  on cpkCenterColor changed col do
  (
    oldColor = centerColor
    for s in $* do
      if (s.wireColor == oldColor) then s.wireColor = col

    centerColor = col
    if (ckbCenterColor.checked and isValidNode lastRigObj) then
      lastRigObj.wireColor = col
  )
  on cpkRightColor changed col do
  (
    oldColor = rightColor
    for s in $* do
      if (s.wireColor == oldColor) then s.wireColor = col

    rightColor = col
    if (ckbRightColor.checked and isValidNode lastRigObj) then
      lastRigObj.wireColor = col
  )
  on ckbLeftColor changed state do
  (
    if (state) then
    (
      ckbCenterColor.checked = false
      ckbRightColor.checked = false
      userSel = getCurrentSelection()
      if (userSel.count > 1) then userSel.wireColor = leftColor
      else if (isValidNode lastRigObj) then lastRigObj.wireColor = leftColor
    )
    else
    (
      ckbLeftColor.checked = true
    )
  )
  on ckbCenterColor changed state do
  (
    if (state) then
    (
      ckbLeftColor.checked = false
      ckbRightColor.checked = false
      userSel = getCurrentSelection()
      if (userSel.count > 1) then userSel.wireColor = centerColor
      else if (isValidNode lastRigObj) then lastRigObj.wireColor = centerColor
    )
    else
      ckbCenterColor.checked = true
  )
  on ckbRightColor changed state do
  (
    if (state) then
    (
      ckbLeftColor.checked = false
      ckbCenterColor.checked = false
      userSel = getCurrentSelection()
      if (userSel.count > 1) then userSel.wireColor = rightColor
      else if (isValidNode lastRigObj) then lastRigObj.wireColor = rightColor
    )
    else
      ckbRightColor.checked = true
  )
  on btnZeroTransform pressed do
  (
    userSel = getCurrentSelection()
    undo "Zero Object Transform" on
    (
      for o in userSel do
      (
        zeroPoint = Point cross:off box:off centerMarker:on size:1 wireColor:(color 128 0 0)
        zeroPoint.parent = o.parent
        zeroPoint.transform = o.transform
        zeroPoint.name = o.name + "_zero"
        zeroPoint.isHidden = zeroPoint.isFrozen = true
        o.parent = zeroPoint
      )
      select userSel
    )
  )
  on ckbAffectPivot changed state do
  (
    if (state) then maxOps.pivotMode = #pivotOnly
    else maxOps.pivotMode = #none
    completeRedraw()
  )
  on btnPivotToCenter pressed do
  (
    macros.run "Ingenuity" "PivotToCenter"
  )
  on btnPivotToObjCenter pressed do
  (
    macros.run "Ingenuity" "PivotToObjCenter"
  )
  on btnPivotToObjPivot pressed do
  (
    macros.run "Ingenuity" "PivotToObjPivot"
  )
  on btnMirrorSelectedBones pressed do
  (
    userSel = getCurrentSelection()
    if (userSel.count > 0) then
    (
--//      start out with an identity matrix
      mirrorTM = matrix3 1
--//      then change the rows based on mirror axis
      if (rdoMirrorAxis.state == 1) then
        mirrorTM[1] = [-1,0,0]
      else if (rdoMirrorAxis.state == 2) then
        mirrorTM[2] = [0,-1,0]
      else if (rdoMirrorAxis.state == 3) then
        mirrorTM[3] = [0,0,-1]

      local chainBone
      parentBones = #()
      for b in userSel do
      (
        if (b.parent != undefined) then
        (
          chainBone = b
          while (chainBone.parent != undefined) do
            chainBone = chainBone.parent

          if (findItem parentBones chainBone == 0) then
            append parentBones chainBone
        )
      )
      undo "Mirror Bones" on
      (
        for p in parentBones do
          mirrorBoneChain p undefined mirrorTM
      )
    )
    else
      messageBox "Please select the bones you wish to mirror." title:"No Bones Selected"
  )
  on riggingToolsRoll rolledUp state do
  (
    if (state) then
      riggingToolsFloater.size.y += riggingToolsRoll.height
    else
      riggingToolsFloater.size.y -= riggingToolsRoll.height
  )
)

if (riggingToolsFloater != undefined) then CloseRolloutFloater riggingToolsFloater
floaterWidth = (riggingToolsRoll.width + 20)
floaterHeight = (riggingToolsRoll.height + 30)
riggingToolsFloater = newRolloutFloater "Rigging Tools v1.04" floaterWidth floaterHeight 130 130
addRollout riggingToolsRoll riggingToolsFloater
)
--//-----------------------------------------------------------------------------