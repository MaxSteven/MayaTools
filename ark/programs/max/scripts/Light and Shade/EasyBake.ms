--//-----------------------------------------------------------------------------
--// EasyBake.ms
--// By Grant Miller (blented@gmail.com)
--// v 1.0
--// Created On: 05/09/08
--// Modified On: 05/10/08
--// tested using Max 2008
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Required Files:
--// ieMax
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Description:
--// Eases the process of baking out diffuse, occlusion, wire, and other maps.
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Revision History:
--//
--// v 1.00 Initial version
--//
--// v 1.01 Updated some environment variables and save directories in order
--//        to support 3dsMax 2009
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
(
--// Includes
--//-----------------------------------------------------------------------------
fileIn (MAX_TOOLS_ROOT + "lib/ieMax.ms")

--// Globals
--//-----------------------------------------------------------------------------
global easyBakeRoll
global easyBakeFloater
global bakeProps

--// Variables
--//-----------------------------------------------------------------------------
AODist = 10
wireColor = (color 255 255 255)
defaultSize = 1024
channels = #(false,false,false,false,false,false) --//dif spec shadow light wire AO
saveDir = "$maps\\"
imageType = ".bmp"

--// Functions
--//-----------------------------------------------------------------------------
--//macroScript vertexBake category:"Ingenuity" tooltip:"Vertex Bake"
--//(
--//  try(destroyDialog bakeRoll)catch()
--//  global mapChannel = 1
--//  image = 0
--//
--//  rollout bakeRoll "Vertex Bake" width:160 height:42
--//  (
--//    editText edtImage "" pos:[36,4] width:96 height:16
--//    label lblImage "Image:" pos:[4,4] width:32 height:16
--//    button btnImage "..." pos:[132,4] width:24 height:16
--//    editText edtMapChannel "" pos:[36,22] width:32 height:16
--//    label lblMapChannel "UVs:" pos:[12,22] width:24 height:16
--//    button btnBake "Bake" pos:[68,22] width:88 height:16
--//
--//    on bakeRoll open do (
--//      edtMapChannel.text = mapChannel as string;
--//    )
--//    on btnImage pressed do (
--//      image = selectBitmap caption:"Bake image:"
--//      if image != undefined then
--//        edtImage.text = image.filename
--//    )
--//    on btnBake pressed do (
--//      undo off (
--//        width = image.width-1
--//        height = image.height-1
--//        mapChannel = edtMapChannel.text as integer;
--//
--//        if (image != undefined) and (mapChannel != undefined) then
--//          ready = true
--//
--//        try(
--//          numFaces = $.numFaces
--//          numVerts = $.numVerts
--//          setNumCPVVerts $ numVerts
--//          numUVVerts = meshop.getNumMapVerts $ mapChannel
--//        )catch(
--//          format "Please select an Editable Mesh.\n"
--//          ready = false
--//        )
--//
--//        if ready then (
--//          meshTrans = #()
--//
--//          --for each face, get the uv verts and mesh verts
--//          --there is a one to one correspondence between uv faces and mesh faces
--//          --uv verts and and mesh verts are also listed in the same order
--//          --i.e. x y z are the same across uvVerts[x,y,z] and meshVerts[x,y,z]
--//          for f = 1 to numFaces do (
--//            --uvVerts[1] translates to meshVerts[1]
--//            uvVerts = meshop.getMapFace $ mapChannel f
--//            meshVerts = getFace $ f
--//
--//            --when passed a uv vert, mesh trans returns the mesh vert
--//            meshTrans[uvVerts[1]] = meshVerts[1]
--//            meshTrans[uvVerts[2]] = meshVerts[2]
--//            meshTrans[uvVerts[3]] = meshVerts[3]
--//          )
--//
--//          for v = numUVVerts to 1 by -1 do (
--//            uv = meshop.getMapVert $ mapChannel v
--//            coord = point2 (uv.x*width) ((1-uv.y)*height)
--//            color = getPixels image coord 1
--//            setVertColor $ meshtrans[v] color[1]
--//            update $
--//          )
--//        )--end ready if
--//      )--end undo off
--//    )--end bake pressed
--//  )--end rollout
--//  createDialog bakeRoll
--//)
--// Script
--//-----------------------------------------------------------------------------
rollout easyBakeRoll "Easy Bake" width:232 height:344
(
  GroupBox grp1 "Map Types" pos:[8,72] width:216 height:232
  label lbl1 "Width:" pos:[16,48] width:32 height:16
  label lbl2 "Height:" pos:[104,48] width:40 height:16
  label lbl4 "Dist:" pos:[120,192] width:24 height:16
  button btnAutoAODist "A" pos:[200,192] width:16 height:16
  button btnBrowseVertMap "..." pos:[200,240] width:16 height:16
  button btnVertexPaint "Vertex Paint" pos:[136,272] width:80 height:24
  editText edtVertMap "" pos:[120,240] width:80 height:16
  button btnRender "Bake Selected" pos:[8,312] width:216 height:24
  checkbutton ckbMapToVerts "Map to Verts" pos:[16,240] width:96 height:24
  checkbox chkAOVerts "AO to Verts" pos:[120,216] width:80 height:16
  radioButtons rdoPresetSizes "Preset Sizes:" pos:[16,8] width:204 height:30 labels:#("128", "256", "512", "1024") columns:4 default:4
  spinner spnImageWidth "" pos:[48,48] width:48 height:16 range:[32,2048,defaultSize] type:#integer scale:32
  spinner spnImageHeight "" pos:[144,48] width:48 height:16 range:[32,2048,defaultSize] type:#integer scale:32
  checkButton ckbDiffuse "Diffuse" pos:[16,88] width:96 height:24 checked:channels[1]
  checkButton ckbSpecular "Specular" pos:[120,88] width:96 height:24 checked:channels[2]
  checkButton ckbShadow "Shadow" pos:[16,120] width:96 height:24 checked:channels[3]
  checkButton ckbLighting "Lighting" pos:[120,120] width:96 height:24 checked:channels[4]
  checkButton ckbWire "Wire" pos:[16,152] width:96 height:24 checked:channels[5]
  colorPicker cpWireColor "Wire Color:" pos:[120,152] width:96 height:24 color:wireColor
  checkbutton ckbAO "Ambient Occlusion" pos:[16,184] width:96 height:48 checked:channels[6]
  spinner spnAODist "" pos:[144,192] width:56 height:16 range:[0,9999,AODist] type:#worldunits scale:1
  checkbutton ckbToggleVertexColors "Toggle Vertex Colors" pos:[16,272] width:112 height:24

  fn renderElem bakeType objName =
  (
    bakeElem = execute(bakeType + "Map()")
    bakeElem.outputSzX = spnImageWidth.value
    bakeElem.outputSzY = spnImageHeight.value
    bakeElem.fileType = saveDir + objName + "_" + bakeType + imageType

    if (bakeType == "specular") then
      bakeElem.lightingOn = true

    bakeProps.removeAllBakeElements()
    bakeProps.addBakeElement bakeElem
    render rendertype:#bakeSelected outputsize:[spnImageWidth.value,spnImageHeight.value] vfb:false
    bakeProps.removeAllBakeElements()
    display bakeElem.bitmap
  )
  fn calcAODist =
  (
    userSel = getCurrentSelection()
    if (userSel.count == 1) then
    (
      objBB = ieMaxCalcBoundingBox userSel
      maxDim = ieMaxMax objBB.x (ieMaxMax objBB.y objBB.z)
      spnAODist.value = maxDim * .2
    )
  )

  on easyBakeRoll open do
  (
    calcAODist()
  )
  on rdoPresetSizes changed state do
  (
    case state of
    (
      1: spnImageHeight.value = spnImageWidth.value = 128
      2: spnImageHeight.value = spnImageWidth.value = 256
      3: spnImageHeight.value = spnImageWidth.value = 512
      4: spnImageHeight.value = spnImageWidth.value = 1024
    )
  )
  on btnAutoAODist pressed do
  (
    calcAODist()
  )
  on btnBrowseVertMap pressed do
  (
    vertImage = selectBitmap caption:"Vertex Bake Image:"
    if vertImage != undefined then
      edtVertMap.text = image.filename
  )
  on btnRender pressed  do
  (
    renderDialogOpen = false
    if renderSceneDialog.isOpen() then
    (
      renderDialogOpen = true
      renderSceneDialog.close()
    )

    userSel = getCurrentSelection()

    if (userSel.count < 1) then
    (
      messageBox "Please select the object you wish to bake" title:"No Baking Object"
    )
    else
    (
      renderers.current = mental_ray_renderer()
      renderers.current.FinalGatherEnable2 = false
      for obj in userSel do
      (
        if (ieMaxIsGeometry obj) then
        (
          bakeProps = obj.INodeBakeProperties
          bakeProps.removeAllBakeElements()
          bakeProps.bakeEnabled = true
          bakeProps.bakeChannel = 1

          maxDim = ieMaxMax spnImageWidth.value spnImageHeight.value
          edgePadding = 4
          if (maxDim >= 2048) then
            edgePadding = 4
          else if (maxDim >= 1024) then
            edgePadding = 2
          else
            edgePadding = 1

          bakeProps.nDilations = edgePadding

          if ckbWire.checked then
          (
            if (mcrUtils.ValidMod Unwrap_UVW) then
            (
              AddMod Unwrap_UVW
              obj.modifiers[1].setMapChannel 1
              obj.modifiers[1].renderuv_width = spnImageWidth.value
              obj.modifiers[1].renderuv_height = spnImageHeight.value
              obj.modifiers[1].renderuv_edgeColor = cpWireColor.color
              obj.modifiers[1].renderuv_seamColor = cpWireColor.color
              obj.modifiers[1].renderUV (saveDir + obj.name + "_Wire" + imageType)
              deleteModifier obj 1
            )
          )
          if ckbDiffuse.checked then
          (
            bakeElem = renderElem "diffuse" obj.name
          )
          if ckbSpecular.checked then
          (
            bakeElem = renderElem "specular"  obj.name
          )
          if ckbShadow.checked then
          (
            originalMaterial = obj.material
            originalBkgdColor = backgroundColor
            backgroundColor = (color 255 255 255)

            obj.material = matteShadow opaqueAlpha:true
            bakeElem = diffuseMap()
            bakeElem.shadowsOn = true
            bakeElem.lightingOn = true
            bakeElem.outputSzX = spnImageWidth.value
            bakeElem.outputSzY = spnImageHeight.value
            bakeElem.fileType = saveDir + obj.name + "_ShadowMap" + imageType

            bakeProps.removeAllBakeElements()
            bakeProps.addBakeElement bakeElem
            render rendertype:#bakeSelected outputsize:[spnImageWidth.value,spnImageHeight.value] vfb:false
            bakeProps.removeAllBakeElements()
            display bakeElem.bitmap

            obj.material = originalMaterial
            backgroundColor = originalBkgdColor
          )
          if ckbLighting.checked then
          (
            bakeElem = renderElem "lighting" obj.name
          )
          if ckbAO.checked then
          (
            bakeElem = Ambient_Occlusion()
            bakeElem.outputSzX = spnImageWidth.value
            bakeElem.outputSzY = spnImageHeight.value
            bakeElem.fileType = saveDir + obj.name + "_AmbientOcclusion" + imageType

            bakeElem.falloff = 1
            bakeElem.spread = .8
            bakeElem.samples = 64
            bakeElem.maxDistance = spnAODist.value

            bakeProps.removeAllBakeElements()
            bakeProps.addBakeElement bakeElem
            render rendertype:#bakeSelected outputsize:[spnImageWidth.value,spnImageHeight.value] vfb:false
            bakeProps.removeAllBakeElements()
            display bakeElem.bitmap
          )
          if (ckbMapToVerts.checked) then
          (
            vertImage = openBitmap edtVertMap.text
            if (vertImage != undefined) then
            (
              width = vertImage.width-1
              height = vertImage.height-1
              mapChannel = edtMapChannel.text as integer;

              try
              (
                numFaces = $.numFaces
                numVerts = $.numVerts
                setNumCPVVerts $ numVerts
                numUVVerts = meshop.getNumMapVerts $ mapChannel
              )
              catch
              (
                format "Please select an Editable Mesh.\n"
                ready = false
              )

              if ready then
              (
                meshTrans = #()

--//                for each face, get the uv verts and mesh verts
--//                there is a one to one correspondence between uv faces and mesh faces
--//                uv verts and and mesh verts are also listed in the same order
--//                i.e. x y z are the same across uvVerts[x,y,z] and meshVerts[x,y,z]
                for f = 1 to numFaces do
                (
--//                  uvVerts[1] translates to meshVerts[1]
                  uvVerts = meshop.getMapFace $ mapChannel f
                  meshVerts = getFace $ f

--//                  when passed a uv vert, mesh trans returns the mesh vert
                  meshTrans[uvVerts[1]] = meshVerts[1]
                  meshTrans[uvVerts[2]] = meshVerts[2]
                  meshTrans[uvVerts[3]] = meshVerts[3]
                )

                for v = numUVVerts to 1 by -1 do
                (
                  uv = meshop.getMapVert $ mapChannel v
                  coord = point2 (uv.x*width) ((1-uv.y)*height)
                  color = getPixels image coord 1
                  setVertColor $ meshtrans[v] color[1]
                  update $
                )
              )
            )
            else
              messageBox "Unable to open the image chosen for vertex baking." title:"Image Error"
          )
        )
      )
    )
    if renderDialogOpen then
      renderSceneDialog.open()
  )
  on easyBakeRoll rolledUp state do
  (
    if (state) then
      easyBakeFloater.size.y += easyBakeRoll.height
    else
      easyBakeFloater.size.y -= easyBakeRoll.height
  )
)

if easyBakeFloater != undefined then CloseRolloutFloater easyBakeFloater
floaterWidth = (easyBakeRoll.width + 20)
floaterHeight = (easyBakeRoll.height + 30)
easyBakeFloater = newRolloutFloater "Easy Bake v1.00" floaterWidth floaterHeight 130 130
addRollout easyBakeRoll easyBakeFloater
)
--//-----------------------------------------------------------------------------