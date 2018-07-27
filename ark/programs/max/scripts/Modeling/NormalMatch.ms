--//-----------------------------------------------------------------------------
--// NormalMatch.ms
--// By Grant Miller (blented@gmail.com)
--// v 1.0
--// Created On: 07/25/08
--// Modified On: 07/25/08
--// tested using Max 2008
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Required Files:
--// ieMax
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Description:
--// Matches geometry normals for sleeves, skirts, etc.
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Revision History:
--//
--// v 1.00 Initial version
--//
--// v 1.01 Added matching threshhold for snapping in verts, also now manually
--//        makes verts explicit
--//
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
(
--// Includes
--//-----------------------------------------------------------------------------
fileIn (MAX_TOOLS_ROOT + "lib/ieMax.ms")

--// Globals
--//-----------------------------------------------------------------------------
global normalRoll
global normalFloater
global baseMesh
global matchMesh

--// Variables
--//-----------------------------------------------------------------------------

--// Functions
--//-----------------------------------------------------------------------------
fn compareVerts pos1 pos2 thresh =
(
  if pos1.x < pos2.x + thresh and pos1.x > pos2.x - thresh then
    if pos1.y < pos2.y + thresh and pos1.y > pos2.y - thresh then
      if pos1.z < pos2.z + thresh and pos1.z > pos2.z - thresh then
        return true

  return false
)
--// Script
--//-----------------------------------------------------------------------------
rollout normalRoll "Normal Match" width:112 height:144
(
fn geoFilter obj =
(
  (superClassOf obj == GeometryClass)
)

  pickbutton btnBaseMesh "Base Mesh" pos:[8,8] width:96 height:24 filter:geoFilter
  pickbutton btnMatchMesh "Match Mesh" pos:[8,40] width:96 height:24 filter:geoFilter
  button btnMatchNormals "Match Normals" pos:[8,72] width:96 height:24
  spinner spnWeldThreshhold "" pos:[8,120] width:96 height:16 range:[0,1000,0.01] type:#worldunits
  label lbl1 "Weld Threshhold:" pos:[8,104] width:88 height:16

  on normalRoll open do
  (
    userSel = getCurrentSelection()
    if userSel.count > 0 then
    (
      baseMesh = userSel[1]
      btnMatchMesh.text = userSel[1].name
    )
  )
  on normalRoll rolledUp state do
  (
    if (state) then
      normalFloater.size.y += normalRoll.height
    else
    normalFloater.size.y -= normalRoll.height
  )
  on btnBaseMesh picked obj do
  (
    baseMesh = obj
    btnBaseMesh.text = obj.name
  )
  on btnMatchMesh picked obj do
  (
    matchMesh = obj
    btnMatchMesh.text = obj.name
  )
  on btnMatchNormals pressed do
  (
    if (isValidNode baseMesh and isValidNode matchMesh) then
    (
      baseVertPos = #()
      for v in baseMesh.verts do
        append baseVertPos v.pos

      matchVertPos = #()
      for v in matchMesh.verts do
        append matchVertPos v.pos

      buddyVert = #()
      for v = 1 to matchMesh.verts.count do
      (
        for b = 1 to baseMesh.verts.count do
        (
          if (compareVerts  matchVertPos[v] baseVertPos[b] spnWeldThreshhold.value) then
          (
            buddyVert[v] = b
            polyOp.setVert matchMesh v baseVertPos[b]
          )
        )
      )

      select baseMesh
      subObjectLevel = 0
      AddMod EditNormals
      normalMod = $.modifiers["Edit Normals"]
      baseMeshNormals = #()
      normalVert = #{}

      for v = 1 to baseMesh.verts.count do (
  --//        get all normals using specified vert
        normalMod.ConvertVertexSelection #{v} &normalVert
  --//        add up all normals for specified vert and normalize
        vertNormals = 0
        for n in normalVert do vertNormals += normalMod.GetNormal n
        baseMeshNormals[v] = normalize vertNormals
      )

      select matchMesh
      subObjectLevel = 0
      AddMod EditNormals
      normalMod = $.modifiers["Edit Normals"]
      normalVert = #{}
      for v = 1 to matchMesh.verts.count do
      (
        if buddyVert[v] != undefined then
        (
  --//        get all normals using specified vert
          normalMod.ConvertVertexSelection #{v} &normalVert
  --//        set all vert's normals to it's buddy's vert normals
          for n in normalVert do
          (
            normalMod.SetNormal n baseMeshNormals[buddyVert[v]]
            normalMod.SetNormalExplicit n
          )
        )
      )
    )
  )
)

if normalFloater != undefined then CloseRolloutFloater normalFloater
floaterWidth = (normalRoll.width + 20)
floaterHeight = (normalRoll.height + 30)
normalFloater = newRolloutFloater "NM" floaterWidth floaterHeight 130 130
addRollout normalRoll normalFloater
)
--//-----------------------------------------------------------------------------
