----------------------------------------
--Surface Shade--
----------------------------------------

whiteInput = 1
blackInput = 0
whiteOutput = 1
blackOutput = 0
intensity = 1
invertShade = false

baseObj = $.baseObject
vertCount = $.verts.count
faceCount = $.faces.count
faceNormals = #()
vFaceCounts = #()

fn dCopy fromArray toArray = (
  for i = fromArray.count to 1 by -1 do toArray[i] = fromArray[i]
)

vColors = #()
for i = vertcount to 1 by -1 do vColors[i] = 0

--the next two loops store normals and face counts
--in arrays so they're not recalculated each iteration
nextUpdate = 10
progressStart "Collecting Normals:"
progressUpdate 0.1
for f = 1 to faceCount do (
  if (100.0 * f/faceCount) > nextUpdate then (
    progressUpdate (100.0 * f / faceCount)
    nextUpdate += 10
  )
  faceNormals[f] = normalize(polyOp.getFaceNormal baseObj f)
)
progressEnd()

nextUpdate = 10
progressStart "Collecting Vert Info:"
progressUpdate 0.1
for v = 1 to vertCount do (
  if (100.0 * v/vertCount) > nextUpdate then (
    progressUpdate (100.0 * v / vertCount)
    nextUpdate += 10
  )
  vFaces = (polyop.getFacesUsingVert baseObj v) as array
  vFaceCounts[v] = vFaces.count
)
progressEnd()

--then for each face we get it's normal and neighbors via vert
--and find the dot product between the face and it's neighbors
--keeping in mind that -1 is inverted or parallel and 0 is perpendicular
--we store the average and use it later to colorize the mesh
nextUpdate = 10
progressStart "Calculating Curvature:"
progressUpdate 0.1
for f = 1 to faceCount do (
  if (100.0 * f/faceCount) > nextUpdate then (
    progressUpdate (100.0 * f / faceCount)
    nextUpdate += 10
  )

  --gets face vector and finds its neighbors
  faceVector = faceNormals[f]
  faceVerts = polyOp.getVertsUsingFace baseObj f
  sFaces = (polyOp.getFacesUsingVert baseObj faceVerts) as array

  --calculates the dot product between the faceVector and its neighbors
  dotAverage = 0.0
  for s = 1 to sFaces.count do dotAverage += length(faceVector + faceNormals[sFaces[s]])
--   for s = 1 to sFaces.count do dotAverage += dot faceVector faceNormals[sFaces[s]]

  dotAverage /= sFaces.count

  --the dot average is then divided by the vert's face count and added to the vcolors array
  for v in faceVerts do vColors[v] += (dotAverage / vFaceCounts[v])
)
progressEnd()

--moves the vColors into an all-positive range
vColorMin = amin vColors
for v = 1 to vertCount do vColors[v] -= vColorMin

--normalizes the range to 0-1
vColorMax = amax vColors
for v = 1 to vertCount do vColors[v] /= vColorMax

--normalizes the range to -1 to 1
for v = 1 to vertCount do vColors[v] = (vColors[v] - .5) * 2

rollout shadeRoll "Shade Params" width:136 height:216
(
  label lblWhiteInput "White Input:" pos:[16,8] width:64 height:16
  spinner spnWhiteInput "" pos:[80,8] width:48 height:16 range:[0.001,1,1] type:#float
  label lblBlackInput "Black Input:" pos:[16,32] width:64 height:16
  spinner spnBlackInput "" pos:[80,32] width:48 height:16 range:[0,0.999,0] type:#float
  label lblWhiteOutput "White Output:" pos:[8,56] width:72 height:16
  spinner spnWhiteOutput "" pos:[80,56] width:48 height:16 range:[0.001,1,1] type:#float scale:0.1
  label lblBlackOutput "Black Output:" pos:[8,80] width:72 height:16
  spinner spnBlackOutput "" pos:[80,80] width:48 height:16 range:[0,0.999,0] type:#float scale:0.1
  label lblIntensity "Intensity:" pos:[32,104] width:48 height:16
  spinner spnIntensity "" pos:[80,104] width:48 height:16 range:[1,10,1] type:#float
  label lblInvert "Invert:" pos:[40,128] width:40 height:16
  checkbox chkInvert "" pos:[80,128] width:16 height:16
  button btnShade "Shade" pos:[16,152] width:104 height:24
  button btnFinished "Finished" pos:[16,184] width:104 height:24

  on spnwhiteInput changed val do
    whiteInput = spnwhiteInput.value
  on spnblackInput changed val do
    blackInput = spnblackInput.value
  on spnwhiteOutput changed val do
    whiteOutput = spnwhiteOutput.value
  on spnblackOutput changed val do
    blackOutput = spnblackOutput.value
  on spnIntensity changed val do
    intensity = spnIntensity.value
  on chkInvert changed state do
    invertShade = chkInvert.state

  on btnShade pressed  do (
    --color adjustment:
    --vColors start at a -1 to 1 range
    --the final value is calculated by multiplying intensity and calculating color shifts
    vEdit = #()
    dCopy vColors vEdit

    --adjust the range by multiplying the intensity
    for v = 1 to vertCount do vEdit[v] *= intensity
    
    --clamp the result from -1 to 1
    for v = 1 to vertCount do (
      if vEdit[v] < -1 then vEdit[v] = -1
      else if vEdit[v] > 1 then vEdit[v] = 1
    )

    --invert if necessary
    if invertShade then for v = 1 to vertCount do vEdit[v] *= -1


    --make the range positive
    for v = 1 to vertCount do
      vEdit[v] = (vEdit[v]+1)/2.0
    
    --move the colors into the blackInput - whiteInput range
     for v = 1 to vertCount do (
       vEdit[v] -= blackInput
       if vEdit[v] < 0 then vEdit[v] = 0
    )
    for v = 1 to vertCount do (
      vEdit[v] /= whiteInput
      if vEdit[v] > 1 then vEdit[v] = 1
    )

    --then adjust the range by the black and white offsets
    vMin = amin vEdit
    minDifference = vMin - blackOutput
    for v = 1 to vertCount do vEdit[v] -= minDifference

    vMax = amax vEdit
    maxDifference = whiteOutput / vMax
    for v = 1 to vertCount do vEdit[v] *= maxDifference

    --once we're done messing with the colors we assign them
    nextUpdate = 10
    progressStart "Assinging Shading:"
    progressUpdate 0.1
    for v = 1 to vertCount do (
      if (100.0 * v/vertCount) > nextUpdate then (
        progressUpdate (100.0 * v / vertCount)
        nextUpdate += 10
      )
      c = int(vEdit[v]*255)
      polyOp.setVertColor $ 0 $.verts[v] (color c c c)
    )
    
    $.showvertexcolors = true
    progressEnd()
    completeRedraw()
  )
  on btnFinished pressed do
    destroyDialog shadeRoll
)
createDialog shadeRoll 136 216 350 300