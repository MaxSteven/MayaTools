--//-----------------------------------------------------------------------------
--// TurnRender.ms
--// By Grant Miller (blented@gmail.com)
--// v 1.05
--// Created On: 03/03/08
--// Modified On: 04/30/08
--// tested using Max 2008
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Required Files:
--// ieMax
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Description:
--// Renders model turns of characters and objects in a consistent size
--// and format.  Also includes object information like polycount and
--// filename.
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Revision History:
--//
--// v 1.00 Initial version
--//
--// v 1.01 Added the ability to render rigs, fixed some minor bugs
--//
--// v 1.02 Fixed a bug that was causing non-rigs to lose their materials
--//        when rendered
--//
--// v 1.03 Changed the default background color to white and fixed a bug where
--//        spamming remove obj or camera could cause an error
--//
--// v 1.04 Changed to include concept art, also fixed it so short, fat objects
--//        always have their feet lining up, changed the way tall skinny objects
--//        like staves are spaced out, added the ability to create a camera from
--//        the current viewport, toggle safe frames, general efficiency improvements
--//
--//v 1.05  Fixed several special case bugs with regards to render cropping
--//
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
(
--// Includes
--//-----------------------------------------------------------------------------
fileIn (MAX_TOOLS_ROOT + "lib/ieMax.ms")

--// Globals
--//-----------------------------------------------------------------------------
global renderObjects = #()
global createdObjs = #()
global selectionMin
global selectionMax
global camList = #()
global customCams = #()
global groundPlane
global camLightRotate = #()
global camDim = #()
global lightDummy
global renders = #()
global finalRender
global fileName
global turnRenderRoll
global turnRenderFloater
global rigMats = #()
global conceptImage

--// Options Vars
--//-----------------------------------------------------------------------------
global camPadPercent = 1.1
global camOn = #(true,true,true,false,false,false)
global wireColor = color 255 255 255
global bkgdColor = color 255 255 255
settingsData = "TurnRenderSettingsData"
global outputWidth = ieMaxGetProp settingsData "outputWidth"
global outputHeight = ieMaxGetProp settingsData "outputHeight"
if (outputWidth == undefined) then outputWidth = 320
if (outputHeight == undefined) then outputHeight = 320
renderWidth = outputWidth
renderHeight = outputHeight
global bOrtho = true
global bWireframe = true
global bShaded = true
global bPolycount = true
global bFilename = true
global bCleanup = true
global bGI = false
global bRig = false
global splineThickness = .5

--// Variables
--//-----------------------------------------------------------------------------
bbDim = [0,0,0]
camDist = [0,0,0]
bbCenter = [0,0,0]
camOffset = [0,0,0]
camFOV = 45
camOrder = #(1,3,2,4,5,6) --//front right back left top bottom
triCount = 0
imageBorder = 4
aoRange = 1
renderHeader = 36

--// Functions
--//-----------------------------------------------------------------------------
fn calcCamDistances =
(
--//  cam distance = .5(bounding box dimension) / tan(.5(camera fov))
  camFOVMult = 1 / tan (0.5 * camFOV)
  xCamDist = 0.5 * bbDim.x * camFOVMult * camPadPercent
  yCamDist = 0.5 * bbDim.y * camFOVMult * camPadPercent
  zCamDist = 0.5 * bbDim.z * camFOVMult * camPadPercent

--//  cam distance is whatever the larger of the two distances is. This is done to ensure that the entire object fits in the frame
  maxCamDist = ieMaxMax xCamDist (ieMaxMax yCamDist zCamDist)
  camDist.x = maxCamDist
  camDist.y = maxCamDist
  camDist.z = maxCamDist
--//  camDist.x = ieMaxMax yCamDist zCamDist
--//  camDist.y = ieMaxMax xCamDist zCamDist
--//  camDist.z = ieMaxMax xCamDist yCamDist
)

fn calcTriCount =
(
  triCount = 0
  for o in renderObjects do
  (
    polycountFail = false
    try ( addModifier o (Turn_to_Poly()) )
    catch ( polycountFail = true )
    if not polycountFail then
    (
      o.modifiers[1].limitPolySize = true
      o.modifiers[1].maxPolySize = 3
      triCount += getNumFaces o
      deleteModifier o 1
    )
    else
    (
      triCount = 0
      print "Tri count failed, please be sure to select only geometry objects to render."
    )
  )
)

fn calcCamOffsets =
(
--//  camera is placed at cam distance + offset - half the bounding box so that the cam's fov lines up perfectly with the bounding box of the object
  camOffset.x = camDist.x + .5 * bbDim.x
  camOffset.y = camDist.y + .5 * bbDim.y
  camOffset.z = camDist.z + .5 * bbDim.z
)

fn createCameras =
(
  frontCamPos = [bbCenter.x, bbCenter.y - camOffset.y, bbCenter.z]
  backCamPos = [bbCenter.x, bbCenter.y + camOffset.y, bbCenter.z]
  rightCamPos = [bbCenter.x + camOffset.x,bbCenter.y, bbCenter.z]
  leftCamPos = [bbCenter.x - camOffset.x,bbCenter.y, bbCenter.z]
  topCamPos = [bbCenter.x, bbCenter.y, bbCenter.z + camOffset.z]
  bottomCamPos = [bbCenter.x, bbCenter.y, bbCenter.z - camOffset.z]

  frontCamera = ieMaxMakeCam "FrontCam" frontCamPos camDist.y camFOV bOrtho
  backCamera = ieMaxMakeCam "BackCam" backCamPos camDist.y camFOV bOrtho
  rightCamera = ieMaxMakeCam "RightCam" rightCamPos camDist.x camFOV bOrtho
  leftCamera = ieMaxMakeCam "LeftCam" leftCamPos camDist.x camFOV bOrtho
  topCamera = ieMaxMakeCam "TopCam" topCamPos camDist.z camFOV bOrtho
  bottomCamera = ieMaxMakeCam "BottomCam" bottomCamPos camDist.z camFOV bOrtho

--//  set camera rotation (top camera does not need to be rotated)
  in coordsys local frontCamera.rotation = (quat 0.707107 0 0 0.707107)
  in coordsys local backCamera.rotation = (quat 0 -0.707107 -0.707107 0)
  in coordsys local rightCamera.rotation = (quat 0.5 0.5 0.5 0.5)
  in coordsys local leftCamera.rotation = (quat 0.5 -0.5 -0.5 0.5)
  in coordsys local bottomCamera.rotation = (quat -1 0 0 0)

  camList[1] = frontCamera
  camList[2] = backCamera
  camList[3] = rightCamera
  camList[4] = leftCamera
  camList[5] = topCamera
  camList[6] = bottomCamera

  for c = 1 to 6 do append createdObjs camList[c]

  camLightRotate[1] = (quat 0 0 0 1)
  camLightRotate[2] = (quat 0 0 -1 0)
  camLightRotate[3] = (quat 0 0 0.707107 0.707107)
  camLightRotate[4] = (quat 0 0 -0.707107 0.707107)
  camLightRotate[5] = (quat 0 -0.707107 0.707107 0)
  camLightRotate[6] = (quat 0.707107 0 0 0.707107)
)

fn addCustomCams =
(
  for c = 1 to customCams.count do
  (
--//    everything is offset by 6 because that many cams already exist in the array
    camList[c + 6] = customCams[c]
    camLightRotate[c + 6] = (quat 0 0 0 1)
    camOn[c + 6] = true
  )
)

fn createLights =
(
  lightDist = camDist.x * 4
  mainLight = targetSpot name:"MainLight" rgb:(color 255 255 255) multiplier:.5 transform:(matrix3 [0,1,0] [0,0,1] [1,0,0] [-lightDist * (tan 35),-lightDist, lightDist * (tan 40)]) target:(Targetobject transform:(matrix3 [1,0,0] [0,1,0] [0,0,1] [0,0,0]))
  fillLight = targetSpot name:"FillLight" rgb:(color 255 255 255) multiplier:.2 transform:(matrix3 [0,1,0] [0,0,1] [1,0,0] [lightDist * (tan 50),-lightDist, lightDist * (tan 15)]) target:(Targetobject transform:(matrix3 [1,0,0] [0,1,0] [0,0,1] [0,0,0]))
  backLight = targetSpot name:"BackLight" rgb:(color 255 255 255) multiplier:.5 transform:(matrix3 [0,1,0] [0,0,1] [1,0,0] [0,lightDist, lightDist * (tan 50)]) target:(Targetobject transform:(matrix3 [1,0,0] [0,1,0] [0,0,1] [0,0,0]))
  ambientColor = color 128 128 128

  lightDummy = ieMaxRootDummy()
  lightDummy.name = "LightRootDummy"
  ieMaxMultiLink #(mainLight,mainLight.target,fillLight,fillLight.target,backLight,backLight.target) lightDummy
  lightDummy.pos = bbCenter

  append createdObjs mainLight
  append createdObjs fillLight
  append createdObjs backLight
  append createdObjs lightDummy
)

fn createGroundPlane =
(
  groundPlane = Plane length:(bbDim.y * 4) width:(bbDim.x * 4) pos:[bbCenter.x, bbCenter.y, bbCenter.z - .5 * bbDim.z] lengthSegs:1 widthSegs:1
  groundPlane.material = standardMaterial diffuse:(color 0 0 0)
  groundPlane.material.opacityMap = Ambient_Reflective_Occlusion__3dsmax bright:(color 0 0 0) dark:(color 255 255 255) samples:32 max_distance:aoRange falloff:4 spread:1
  append createdObjs groundPlane
)

fn calcCameraCrop =
(
  largestDim = ieMaxMax bbDim.x (ieMaxMax bbDim.y bbDim.z)

  camDim[1] = camDim[2] = [bbDim.x / largestDim,bbDim.z / largestDim]
  camDim[3] = camDim[4] = [bbDim.y / largestDim,bbDim.z / largestDim]
  camDim[5] = camDim[6] = [bbDim.x / largestDim,bbDim.y / largestDim]

)

fn makeWireframe =
(
  for o in renderObjects do
  (
    if (o.material != undefined) then
    (
      o.material = compositeMaterial baseMaterial:o.material
      o.material.materialList[2] = standardMaterial diffuse:wireColor selfIllumAmount:100 wire:on
    )
    else if (ieMaxIsGeometry o) then
    (
      o.material = compositeMaterial baseMaterial:(standardMaterial diffuse:(color 128 128 128))
      o.material.materialList[2] = standardMaterial diffuse:wireColor selfIllumAmount:100 wire:on
    )
  )
)

fn unWireframe =
(
  for o in renderObjects do
  (
    if (o.material != undefined) then
    (
      o.material = o.material.baseMaterial
    )
  )
)

fn renderCameras =
(
  progressStart "Rendering..."
  squareDim = ieMaxMax outputWidth outputHeight
  for c = 1 to camList.count do
  (
    if camOn[c] then
    (
      lightDummy.position = [0,0,0]
      lightDummy.rotation = camLightRotate[c]
      lightDummy.position = bbCenter
      if ( c < 7) then
      (
        renders[c] = render camera:camList[c] progressBar:false outputWidth:squareDim outputHeight:squareDim
      )
      else
      (
        renders[c] = render camera:camList[c] progressBar:false outputWidth:outputWidth outputHeight:outputHeight
      )
--//      display renders[c]
    )
    progressUpdate (100 * c / camList.count)
  )
  progressEnd()
)

fn combineSection =
(
  sectionHeight = 0
  sectionWidth = 0
  squareDim = ieMaxMax outputWidth outputHeight
  local renderHeight
  minWidth = floor ((ieMaxMax outputWidth outputHeight) / 3)

--//get the section height (max of all render heights * crop)
--//also add up cropped render widths
  for c in camOrder do
  (
    if (camOn[c]) then
    (
      renderHeight = renders[c].height * camDim[c].y
      if (renderHeight > sectionHeight) then sectionHeight = renderHeight
      sectionWidth += ieMaxMax (renders[c].width * camDim[c].x) minWidth
    )
  )


  if (sectionHeight == 0) then
    sectionHeight = outputHeight

  for c = 1 to customCams.count do
  (
    renderHeight = renders[c+6].height
    if (renderHeight > sectionHeight) then sectionHeight = renderHeight
    sectionWidth += ieMaxMax renders[c+6].width minWidth
  )
  sectionBitmap = bitmap sectionWidth sectionHeight color:bkgdColor

--//  for ortho cams go in order and crop them
  xPos = 0
  xOffset = 0
  yOffset = 0
  for c in camOrder do
  (
    if (camOn[c]) then
    (
--//      get the cropped witdth and height, this is how big the actual image we'll be pasting is
      croppedWidth = squareDim * camDim[c].x
      croppedHeight = squareDim * camDim[c].y
--//      if the cropped width is less than the min width then offset it when we paste it
      if (croppedWidth < minWidth) then
        xOffset = .5 * (minWidth - croppedWidth)
      else
        xOffset = 0
--//      calculate the width and height offsets for where to start sampling from when we paste
      widthOffset = .5 * (squareDim - croppedWidth)
      heightOffset = .5 * (squareDim - croppedHeight)
      yOffset = .5 * (sectionHeight - croppedHeight)
--//      create a cropping box from the data we've generated so far
      imageCrop = box2 widthOffset heightOffset (squareDim - widthOffset) (squareDim - heightOffset)
--//      paste the bitmap into the section bitmap at xpos + offset, yoffset
      pasteBitmap renders[c] sectionBitmap imageCrop (point2 (xPos + xOffset) yOffset)

      xPos += ieMaxMax croppedWidth minWidth
    )
  )

  for c = 1 to customCams.count do
  (
    imageCrop = box2 0 0 outputWidth outputHeight
    pasteBitmap renders[c+6] sectionBitmap imageCrop (point2 xPos 0)
    xPos += outputWidth
  )

  return sectionBitmap
)

fn isolateScene =
(
  if (not bRig) then
  (
    select (renderObjects + customCams + groundPlane)
    macros.run "Tools" "Isolate_Selection"
  )
)

fn enableRigRender =
(
  for o = 1 to renderObjects.count do
  (
    if (renderObjects[o].material != undefined) then
      append rigMats renderObjects[o].material
    else
      append rigMats undefined

    renderObjects[o].material = standardMaterial opacity:50
  )
  for s in $* where superClassOf s == shape do
  (
    s.render_renderable = true
    s.render_displayRenderMesh = true
    s.thickness = splineThickness
    s.sides = 12
  )
  for b in $* where classof b == BoneGeometry do
    b.renderable = true
)
fn disableRigRender =
(
  for o = 1 to renderObjects.count do
    renderObjects[o].material = rigMats[o]

  for s in $* where superClassOf s == shape do
  (
    s.render_renderable = false
    s.render_displayRenderMesh = false
  )
  for b in $* where classof b == BoneGeometry do
    b.renderable = false
)

fn triCountOverlay =
(
--//  letters and numbers are 14 x 24
  triCountString = triCount as string
  commaCount = floor((triCountString.count)/ 3)
  totalChar =triCountString.count + commaCount + 5 --plus 5 for " tris"
  triOverlayWidth = totalChar * 14
  triStartPoint = point2 (finalRender.width - triOverlayWidth - imageBorder) imageBorder

  finalTriString = ""
  charPos = triCountString.count
  if (commaCount > 0) then
  (
    while charPos > 1 do
    (
      finalTriString = (substring triCountString (charPos-2) 3) + finalTriString
      if (charPos > 3) then finalTriString = "," + finalTriString
      if (charPos-3 <= 3) then
      (
        finalTriString = (substring triCountString 1 (charPos-3)) + finalTriString
        charPos = 0
      )
      charPos -= 3
    )
  )
  else
  (
    finalTriString = triCountString
  )

  finalTriString += " tris"
  finalRender = ieMaxOverlayString triStartPoint finalTriString finalRender
)

fn filenameOverlay =
(
  if (maxFileName != "") then
  (
    fileString = ieMaxStripFileExtension maxFileName
    filenameStartPoint = point2 imageBorder imageBorder
    finalRender = ieMaxOverlayString filenameStartPoint fileString finalRender
  )
)

fn captionOverlay captionString =
(
  captionStartPoint = point2 imageBorder (finalRender.height - 24 - imageBorder)
  finalRender = ieMaxOverlayString captionStartPoint captionString finalRender
)

fn copyrightOverlay =
(
  copyright = openBitmap "$ui\icons\Ingenuity_copyright.tga"
  startPoint = point2 (finalRender.width - copyright.width - imageBorder) (finalRender.height - copyright.height - imageBorder)
  pasteBitmap copyright finalRender (point2 0 0) startPoint type:#blend
)

fn sceneCleanup =
(
  for o in createdObjs do try( delete o )catch()
  createdObjs = #()
  camList = #()
)

--// Script
--//-----------------------------------------------------------------------------
rollout turnRenderRoll "Turn Renderer" width:248 height:504
(
  fn camFilter obj =
  (
    (classOf obj == FreeCamera or classOf obj == TargetCamera)
  )

  GroupBox grpCameras "Cameras" pos:[8,200] width:232 height:160
  pickbutton btnAddCam "Add Cam" pos:[144,320] width:56 height:16 filter:camFilter
  button btnAllCams "Auto" pos:[200,320] width:32 height:16
  listbox lbxCustomCams "Custom Cams:" pos:[144,216] width:88 height:6
  label lblStandardCams "Standard Cams:" pos:[16,216] width:96 height:16
  label lblImageHeight "Image Height:" pos:[112,24] width:72 height:16
  label lbl13 "Image Width:" pos:[112,48] width:72 height:16
  GroupBox grpRenderSettings "Render Settings" pos:[8,8] width:232 height:184
  listbox lbxRenderObjects "Objects:" pos:[16,24] width:88 height:7
  button ckbAddSelected "Add Selected" pos:[16,152] width:88 height:16
  label lblPadding "Padding %:" pos:[112,72] width:72 height:16
  GroupBox grpAdditional "Additional Settings" pos:[8,368] width:232 height:96
  button btnRemoveObject "Remove" pos:[16,168] width:48 height:16
  button btnClearObjects "Clear" pos:[64,168] width:40 height:16
  checkbutton ckbSafeFrame "SafeFrame" pos:[144,336] width:56 height:16 checked:displaySafeFrames
  button btnCamFromView "View" pos:[200,336] width:32 height:16
  label lbl46 "Display:" pos:[112,120] width:72 height:16
  edittext edtCaption "" pos:[64,416] width:168 height:16
  label lblCaption "Caption:" pos:[16,416] width:40 height:16
  label lbl12 "Concept:" pos:[16,440] width:48 height:16
  button btnPickConceptImage "..." pos:[208,440] width:24 height:16
  button btnRenderTurn "Render Turn" pos:[8,472] width:232 height:24
  edittext edtConceptImage "" pos:[64,440] width:136 height:16

--//  all these get default values from pre-defined global variables
  checkbutton ckbFront "Front" pos:[56,288] width:32 height:24 checked:camOn[1]
  checkbutton ckbBack "Back" pos:[56,240] width:32 height:16 checked:camOn[2]
  checkbutton ckbRight "Right" pos:[88,256] width:32 height:32 checked:camOn[3]
  checkbutton ckbLeft "Left" pos:[24,256] width:32 height:32 checked:camOn[4]
  checkbutton ckbTop "Top" pos:[56,256] width:32 height:16 checked:camOn[5]
  checkbutton ckbBtm "Btm" pos:[56,272] width:32 height:16 checked:camOn[6]
  spinner spnImgHeight "" pos:[184,24] width:48 height:16 range:[0,10000,outputHeight] type:#integer scale:10
  spinner spnImgWidth "" pos:[184,48] width:48 height:16 range:[0,10000,outputWidth] type:#integer scale:10
  spinner spnPadding "" pos:[184,72] width:48 height:16 range:[0,200,10] type:#integer scale:1
  checkbox chkOrtho "Orthographic" pos:[16,320] width:88 height:16 checked:bOrtho
  checkbox chkGI "Global Illumination" pos:[112,96] width:120 height:16 checked:bGI
  checkbox chkWireframe "Wire" pos:[184,136] width:48 height:16 checked:bWireframe
  checkbox chkShaded "Shaded" pos:[112,136] width:56 height:16 checked:bShaded
  checkbox chkPolycount "Tri Count" pos:[112,152] width:72 height:16 checked:bPolycount
  checkbox chkFilename "File" pos:[184,152] width:40 height:16 checked:bFilename
  checkbox chkCleanup "Delete Render Objs" pos:[16,336] width:120 height:16 checked:bCleanup
  checkbox chkRig "Rig Thick:" pos:[112,168] width:72 height:16 checked:bRig
  spinner spnSplineThickness "" pos:[184,168] width:48 height:16 type:#worldunits scale:.1 range:[.001,1000,splineThickness] enabled:bRig
  colorPicker cpBackground "Background" pos:[16,384] width:104 height:24 color:bkgdColor title:"Background Color"
  colorPicker cpWireframe "Wireframe" pos:[136,384] width:96 height:24 color:wireColor title:"Wireframe Color"

  fn renderViews =
  (
  --//  turn the frame buffer off so each render doesn't pop up individually
    rendShowVFB = false
    MRRender = renderers.current = mental_ray_renderer()
  --//  render settings, sparse at the moment, will tweak more later
    MRRender.MinimumSamples = 0
    MRRender.MaximumSamples = 2
  --//  Mitchell
    MRRender.filter = 3

    if bGI then
    (
      MRRender.FinalGatherEnable2 = true
      MRRender.FinalGatherDensity = .4
      MRRender.FinalGatherAccuracy = 75
      MRRender.FinalGatherInterpolationSamples = 30
      MRRender.FinalGatherBounces = 1
    )
    else
    (
      MRRender.FinalGatherEnable2 = false
    )

    if (bRig) then enableRigRender()
    turnSections = #()
    if (edtConceptImage.text != "" and conceptImage != undefined) then
      append turnSections conceptImage
    if (bShaded) then
    (
      renderCameras()
      append turnSections (combineSection())
    )
    if (bWireframe) then
    (
      makeWireframe()
      renderCameras()
      append turnSections (combineSection())
      unWireframe()
    )
    if (bRig) then disableRigRender()

    finalHeight = renderHeader * 2
    finalWidth = 0
    for i in turnSections do
    (
      finalHeight += i.height
      if (i.width > finalWidth) then finalWidth = i.width
    )

    finalRender = bitmap finalWidth finalHeight color:bkgdColor

    yPos = renderHeader
    for i in turnSections do
    (
      xPos = floor ((finalWidth - i.width) / 2)
      pasteBitmap i finalRender (point2 0 0) (point2 xPos yPos)
      yPos += i.height
    )
  )

  fn addSelectedObjects =
  (
    selectedObjects = ieMaxCopyUserSelection()
    if (selectedObjects != undefined) then
    (
      for i in selectedObjects do
      (
        if ((findItem renderObjects i) == 0) then
        (
          append lbxRenderObjects.items i.name
          lbxRenderObjects.items = lbxRenderObjects.items
          append renderObjects i
        )
      )
    )
  )

  fn addCam obj =
  (
    if ((findItem customCams obj) == 0) then
    (
      append lbxCustomCams.items obj.name
      lbxCustomCams.items = lbxCustomCams.items
      append customCams obj
    )
  )

  fn validateLists =
  (
    renderObjects = ieMaxValidateNodes renderObjects
    lbxRenderObjects.items = #()
    for o in renderObjects do
      append lbxRenderObjects.items o.name
    lbxRenderObjects.items = lbxRenderObjects.items

    customCams = ieMaxValidateNodes customCams
    lbxCustomCams.items = #()
    for o in customCams do
      append lbxCustomCams.items o.name
    lbxCustomCams.items = lbxCustomCams.items
  )

  on turnRenderRoll open do
  (
    addSelectedObjects()
    backgroundColor = bkgdColor
    if (conceptImage != undefined) then
      edtConceptImage.text = conceptImage.filename
  )
  on turnRenderRoll close do
  (
    ieMaxSetProp settingsData "outputWidth" outputWidth
    ieMaxSetProp settingsData "outputHeight" outputHeight
    displaySafeFrames = false
    completeRedraw()
  )
  on cpBackground changed col do backgroundColor = col
  on cpWireframe changed col do wireColor = col

  on chkWireframe changed state do
  (
    bWireframe = state
    if (not bWireframe and not bShaded) then
    (
      chkWireframe.checked = bWireframe = true
    )
  )
  on chkShaded changed state do
  (
    bShaded = state
    if (not bWireframe and not bShaded) then
    (
      chkShaded.checked = bShaded = true
    )
  )

  on chkGI changed state do bGI = state
  on chkPolycount changed state do bPolycount = state
  on chkFilename changed state do bFilename = state
  on chkOrtho changed state do bOrtho = state
  on chkCleanup changed state do bCleanup = state
  on chkRig changed state do
  (
    bRig = state
    spnSplineThickness.enabled = state
  )
  on spnSplineThickness changed val do splineThickness = val
  on ckbFront changed state do camOn[1] = state
  on ckbBack changed state   do camOn[2] = state
  on ckbRight changed state do camOn[3] = state
  on ckbLeft changed state   do camOn[4] = state
  on ckbTop changed state   do camOn[5] = state
  on ckbBtm changed state   do camOn[6] = state

  on btnAddCam picked obj do
  (
    if (obj != undefined) then addCam obj
  )

  on btnAllCams pressed  do
  (
    for obj in $* do
    (
      if not (obj.isHidden or obj.isFrozen) then
        if (classOf obj == FreeCamera or classOf obj == TargetCamera) then addCam obj
    )
  )

  on lbxCustomCams doubleClicked sel do
  (
    if (sel > 0) then
    (
      deleteItem lbxCustomCams.items sel
      deleteItem customCams sel
      lbxCustomCams.items = lbxCustomCams.items
    )
  )
  on btnCamFromView pressed  do
  (
    userSel = getCurrentSelection()
    local c
    wcol = (color 5 54 179)
    targdist = getscreenscalefactor [0,0,0]
--//    get viewport tm
    viewfov = getVIewFOV()
    cXform =  Inverse(viewport.getTM())

    if (viewport.Gettype() == #view_persp_user) then
    (
--//      creates a camera, and assigns the current Vport Transforms
      c = Freecamera  targetDistance:targdist isSelected:on wirecolor:wcol
      c.fov = viewfov
      c.orthoProjection = false
      c.Transform = cXform
      viewport.setcamera c
      c.type = #target
      c.target.wirecolor = wcol
      addCam c
    )
    select userSel
  )
  on spnImgHeight changed val do
  (
    outputHeight = val
    renderHeight = val
  )
  on spnImgWidth changed val do
  (
    outputWidth = val
    renderWidth = val
  )
  on spnPadding changed val do camPadPercent = 1 + val * .01
  on ckbAddSelected pressed do addSelectedObjects()
  on btnRemoveObject pressed  do
  (
    if (lbxRenderObjects.selection > 0) then
    (
      selObj = lbxRenderObjects.selection
      deleteItem lbxRenderObjects.items selObj
      deleteItem renderObjects selObj
      lbxRenderObjects.items = lbxRenderObjects.items
    )
  )
  on lbxRenderObjects doubleClicked sel do
  (
    if (sel > 0) then
    (
      deleteItem lbxRenderObjects.items sel
      deleteItem renderObjects sel
      lbxRenderObjects.items = lbxRenderObjects.items
    )
  )
  on btnClearObjects pressed  do
  (
    lbxRenderObjects.items = #()
    renderObjects = #()
    lbxRenderObjects.items = lbxRenderObjects.items
  )
  on btnPickConceptImage pressed do
  (
    conceptImage = selectBitmap caption:"Concept Image:"
    if (conceptImage != undefined) then
      edtConceptImage.text = conceptImage.filename
  )
  on edtConceptImage changed text do conceptImage = openBitmap text
  on ckbSafeFrame changed state do
  (
    max safeframe toggle
  )
  on btnRenderTurn pressed  do
  (
    if (renderObjects.count > 0) then
    (
      validateLists()
      sceneCleanup()
      othroCamOn = false
      for c = 1 to 6 do if camOn[c] then othroCamOn = true
      if (othroCamOn or (customCams.count > 0)) then
      (
        bbDim = ieMaxCalcBoundingBox renderObjects
        bbCenter = ieMaxCalcBBCenter renderObjects
        calcTriCount()

--//        dev only, remove after testing
--//        Box lengthsegs:1 widthsegs:1 heightsegs:1 length:bbDim.y width:bbDim.x height:bbDim.z mapcoords:off pos:[bbCenter.x,bbCenter.y,bbCenter.z - .5 * bbDim.z] isSelected:off name:"renderBB"

--//        defines how far away from the selection each camera is placed
        calcCamDistances()
--//        offsets in each direction based on cam distances
        calcCamOffsets()
        createCameras()
        createLights()
--//        how much each image can be cropped horizontally (tall skinny things)
        calcCameraCrop()
        if (customCams.count > 0) then addCustomCams()

        createGroundPlane()

--//        make sure the render scene dialog is closed, otherwise changes made to render settings don't stick sometimes
        renderDialogOpen = false
        if renderSceneDialog.isOpen() then
        (
          renderDialogOpen = true
          renderSceneDialog.close()
        )

        isolateScene()
        renderViews()

        copyrightOverlay()
        if (bPolycount) then triCountOverlay()
        if (bFilename) then filenameOverlay()
        if (edtCaption.text != "") then captionOverlay edtCaption.text

        display finalRender

        if bCleanup then sceneCleanup()

--//        turn the frame buffer back on
        rendShowVFB = true
        if renderDialogOpen then
          renderSceneDialog.open()

--//        overlay
--//        get polycount and scene information
--//        overlay information
--//        display final render
      )
      else
      (
        messageBox "Please select at least 1 camera to render through." title:"No Active Cameras"
      )
    )
    else
    (
      messageBox "Please add the objects you wish to render." title:"No Render Objects"
    )
  )
  on turnRenderRoll rolledUp state do
  (
    if (state) then
      turnRenderFloater.size.y += turnRenderRoll.height
    else
      turnRenderFloater.size.y -= turnRenderRoll.height
  )
)

if turnRenderFloater != undefined then CloseRolloutFloater turnRenderFloater
floaterWidth = (turnRenderRoll.width + 20)
floaterHeight = (turnRenderRoll.height + 30)
turnRenderFloater = newRolloutFloater "Turn Renderer v1.05" floaterWidth floaterHeight 130 130
addRollout turnRenderRoll turnRenderFloater

)
-------------------------------------------------------------------------------