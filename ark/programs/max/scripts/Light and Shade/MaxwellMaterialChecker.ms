--//-----------------------------------------------------------------------------
--// MaxwellMaterialChecker.ms
--// By Grant Miller (blented@gmail.com)
--// v 1.0
--// Created On: 12/14/12
--// Modified On: 12/14/12
--// tested using Max 2012, Nuke 6.3v3, Softimage 2012, Maya 2012
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Required Files:
--// ieMax.ms
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Description:
--// Replaces instances w/ another object
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

--// Global Variables
--//-----------------------------------------------------------------------------

--// Functions
--//-----------------------------------------------------------------------------

--// Script
--//-----------------------------------------------------------------------------
try ( destroydialog ::MaxwellMaterialChecker )catch()

rollout MaxwellMaterialChecker "Maxwell Material Checker v0.1"
(
  button btnSelectObjects "Select Objects with Non-Maxwell Materials"
  checkbox chkAllowMutli "Allow Multi/Sub-Object Materials" checked:false

  fn testMat mat =
  (
    if (classof mat == Multimaterial and chkAllowMutli.checked == true) then
    (
      for m in mat.materialList do
      (
        if (testMat m != true) then
          return false
      )
    )
    else if (classof mat != Maxwell_Material) then
      return false
    return true
  )

  on btnSelectObjects pressed do
  (
    objs = #()

    for o in objects do
    (
      if (o.material != undefined and (testMat o.material != true) ) then
        append objs o
    )

    select objs
  )
)

createDialog MaxwellMaterialChecker 250 60 style:#(#style_SysMenu, #style_ToolWindow)
)






