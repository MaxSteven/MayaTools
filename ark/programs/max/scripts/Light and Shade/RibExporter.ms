--//-----------------------------------------------------------------------------
--// ribExporter.ms
--// By Grant Miller (blented@gmail.com)
--// v 1.0
--// Created On: 03/21/09
--// Modified On: 02/06/10
--// tested using Max 2010
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Required Files:
--// ieMax.ms
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Description:
--// Prepares and exports 3dsMax Scenes in Renderman's RIB file format
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Revision History:
--//
--// v 1.0 Initial version
--//
--// v 1.1 Updated ui, reconfigured to support rush development
--//
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
(
--// Includes
--//-----------------------------------------------------------------------------
fileIn (MAX_TOOLS_ROOT + "lib/ieMax.ms")

--// Globals
--//-----------------------------------------------------------------------------

--// Variables
--//-----------------------------------------------------------------------------

--// Functions
--//-----------------------------------------------------------------------------

--// Script
--//----------------------------------------------------------------------------
max modify mode
sliderTime = 0f

--//General Vars
numFaces = polyop.getNumFaces
numVerts = polyop.getNumVerts
material = try($.material.name)catch($.name)
if material == "" then format "Material was undefined.\n"
saveFile = stringStream ""
actualSaveFile = openFile ("c:\\projects\\rush\\assets\\ribs\\export.rib") mode:"wt"

--//Mapping Vars
numUVVertsOne = polyop.getNumMapVerts $ 1

chOnePos = #() --//per uv vert position for channel 1
uvTrans = #() --//given mesh vert, get corresponding uv vert
vertPos = #() --//per mesh vert position (object-space)
meshTrans = #() --//given uv vert, get corresponding mesh vert

--//get texture coords for each uvVert in total map verts
  for v = numUVVertsOne to 1 by -1 do
  (
    chOnePos[v] = polyop.getMapVert $ 1 v
  )

--//for each face, get the uv verts and mesh verts
--//there is a one to one correspondence between uv faces and mesh faces
--//uv verts and and mesh verts are also listed in the same order
--//i.e. x y z are the same across uvVerts[x,y,z] and meshVerts[x,y,z]
  for f = 1 to numFaces do (
    --//uvVerts[1] translates to meshVerts[1]
    uvVerts = polyop.getMapFace $ 1 f
    meshVerts = polyop.getFaceVerts $ f

    --//when passed a uv vert, mesh trans returns the mesh vert
    for n = 1 to uvVerts.count do
    (
      meshTrans[uvVerts[n]] = meshVerts[n]
      uvTrans[meshVerts[n]] = uvVerts[n]
    )
  )

--//iterate through UVFaces because that's the order the verts are coming in
  format "#//RenderMan RIB-Structure 1.0\n" to:saveFile
  format "Format % % %\n" renderWidth renderHeight renderPixelAspect to:saveFile
  format "ShadingRate 1\n" to:saveFile
  format "Projection \"perspective\" \"fov\" %\n" $Camera01.fov to:saveFile
  format "Clipping 0.01 1000000\n" to:saveFile
  format "LightSource \"distantlight\" 1" to:saveFile

  format "#// Camera transformation\n" to:saveFile
  format "ConcatTransform [\n" to:saveFile
  r = $camera01.transform.row1
  format "% % % %\n" (ieMaxPNum(r.x)) (ieMaxPNum(r.z)) (ieMaxPNum(-r.y)) 0 to:saveFile
  r = $camera01.transform.row2
  format "% % % %\n" (ieMaxPNum(r.x)) (ieMaxPNum(r.z)) (ieMaxPNum(-r.y)) 0 to:saveFile
  r = $camera01.transform.row3
  format "% % % %\n" (ieMaxPNum(r.x)) (ieMaxPNum(r.z)) (ieMaxPNum(-r.y)) 0 to:saveFile
  r = $camera01.transform.row4
  format "% % % %\n" (ieMaxPNum(-r.x)) (ieMaxPNum(-r.z)) (ieMaxPNum(r.y)) 1 to:saveFile
  format "]\n" to:saveFile
  format "MakeTexture \"c:\\render\\textures\\grid.tif\" \"c:\\render\\textures\\grid.tx\" \"periodic\" \"periodic\" \"gaussian\" 2 2\n" to:saveFile
  format "WorldBegin\n" to:saveFile
  format "AttributeBegin\n" to:saveFile

  format "Surface \"test\"\n" to:saveFile
  format "\"texturename\" \"c:\\render\\textures\\grid.tx\"\n" to:saveFile

  format "SubdivisionMesh \"catmull-clark\"\n" to:saveFile
  format "[" to:saveFile
  for f = 1 to numFaces do
  (
    face = polyop.getFaceVerts $ f
    format ("% ") face.count to:saveFile
  )
  format "]\n[" to:saveFile

  for f = 1 to numFaces do
  (
    face = polyop.getFaceVerts $ f
    for v in face do
    (
      format ("% ") (v-1) to:saveFile
    )
  )
  format "]\n[\"interpolateboundary\"][0 0][][]\n\"P\" [" to:saveFile

  for v = 1 to numVerts do
  (
    vp = polyop.getVert $ v
    format ("% % % ") (ieMaxPNum(vp.x)) (ieMaxPNum(vp.z)) (ieMaxPNum(vp.y)) to:saveFile
  )
  format "]\n\"st\" [" to:saveFile

  for v = 1 to numVerts do
  (
    vp = polyop.getMapVert $ 1 uvTrans[v]
    format ("% % ") (ieMaxPNum(vp.x)) (ieMaxPNum(-vp.y)) to:saveFile
  )
  format "]\n" to:saveFile

  format "AttributeEnd\n" to:saveFile
  format "WorldEnd\n" to:saveFile

  format "%" (saveFile as string) to:actualSaveFile

  close actualSaveFile
  close saveFile
)