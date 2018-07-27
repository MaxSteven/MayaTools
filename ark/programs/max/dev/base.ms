--//-----------------------------------------------------------------------------
--// ForestManager.ms
--// By Grant Miller (blented@gmail.com)
--// v 1.0
--// Created On: 10/25/12
--// Modified On: 10/25/12
--// tested using Max 2012
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Required Files:
--// ieMax.ms
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Description:
--// Mass modification of Forest objects
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

--// Globals
--//-----------------------------------------------------------------------------
global forestFloater
--// Script
--//-----------------------------------------------------------------------------

try(destroyDialog ::forestRoll)catch()
rollout forestRoll "Forest Manager" width:300 height:100
(
--// units_x = Density
--// mapname = distribution file (change from c:/ to q:/)
--// distmap = custom distribution map
--// reserved6 = freeze All Forest objects

  local vPos = 10
  local vSpace = 20
  local leftx = 20
  local rightx = 100

	label lbUnits_X "Units X:" pos:[leftX,vPos]
--//   spinner spnUnits_X "" pos:[rightX,vPos] width:100 height:16 range:[-9999,9999,2000] type:#worldunits
  button btnTimes10 "10x Less Dense" width:100 height:20 pos:[(rightx),vPos] tooltip:"Multiply the selected object's density by 10"
	button btnDividedBy10 "10x More Dense" width:100 height:20 pos:[(rightx + 100),vPos] tooltip:"Divide the selected object's density by 10"


  on forestRoll open do
  (

  )
  on forestRoll close do
  (

  )
  on btnTimes10 clicked do
  (
    userSel = getCurrentSelection()
    disableSceneRedraw()
    max create mode
    for s in userSel do s.units_x *= 10
    enableSceneRedraw()
    completeRedraw()
  )
  on btnDividedBy10 clicked do
  (
    userSel = getCurrentSelection()
    disableSceneRedraw()
    max create mode
    for s in userSel do s.units_x /= 10
    enableSceneRedraw()
    completeRedraw()
  )
)

createDialog forestRoll 300 100 style:#(#style_SysMenu, #style_ToolWindow)
)
--//-----------------------------------------------------------------------------
