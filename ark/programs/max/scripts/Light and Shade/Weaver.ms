--//-----------------------------------------------------------------------------
--// Weaver.ms
--// By Grant Miller (blented@gmail.com)
--// v 1.0
--// Created On: 01/20/12
--// Modified On: 01/20/12
--// tested using Max 2012, Nuke 6.3v1, Softimage 2012, Maya 2012
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Required Files:
--// ieMax.ms
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Description:
--// Master hubbing program for scene assembly within IE's pipeline
--// Brings in cameras, caches, etc
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

--// Script
--//-----------------------------------------------------------------------------
try ( destroydialog ::weaverRoll )catch()

idStart = 89000
struct matDataIDs
(
  ogReflection = idStart+1,
  ogRefraction = idStart+2
)
matData = matDataIDs()

fn matManager mat mode =
(
	if classof mat == Multimaterial then
	(
		for subM in mat.materiallist do
			matManager subm mode
	)
	else if classof mat == VRayMtl then
	(
		print mat.name
    if mode == "reflectionOff" then
    (
		  mat.texmap_reflection_on = false
		  setAppData mat matData.ogReflection (mat.reflection as string)
		  setAppData mat matData.ogReflection (mat.reflection as string)
  		mat.reflection = color 0 0 0
    )
    else if mode == "reflectionOn" then
    (
		  mat.texmap_reflection_on = true
      if (getAppData mat matData.ogReflection) != undefined then
        mat.reflection = execute (ogReflection)
    )
    else if mode == "refractionOff" then
    (
		  mat.texmap_refraction_on = false
		  setAppData mat matData.ogRefraction (mat.refraction as string)
  		mat.refraction = color 0 0 0
    )
    else if mode == "refractionOn" then
    (
		  mat.texmap_refraction_on = true
      if (getAppData mat matData.ogRefraction) != undefined then
        mat.refraction = execute (getAppData mat matData.ogRefraction)
    )
	)
	return false
)

rollout weaverRoll "Weaver v.10"
(
  button btnReflectionOff "Reflections Off"
  button btnReflectionOn "Reflections On"
  button btnRefractionOff "Refraction Off"
  button btnRefractionOn "Refraction On"

  on btnReflectionOff pressed do
  (
    for o in scenematerials do
	    matManager o "reflectionOff"
  )
  on btnReflectionOn pressed do
  (
    for o in scenematerials do
	    matManager o "reflectionOn"
  )
  on btnRefractionOff pressed do
  (
    for o in scenematerials do
	    matManager o "refractionOff"
  )
  on btnRefractionOn pressed do
  (
    for o in scenematerials do
	    matManager o "refractionOn"
  )
)

createDialog weaverRoll 100 200 style:#(#style_SysMenu, #style_ToolWindow)
)