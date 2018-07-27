--//-----------------------------------------------------------------------------
--// StereoControl.ms
--// By Grant Miller (grant.miller@Ingenuity.com)
--// v 1.0
--// Created On: 10/08/10
--// Modified On: 10/08/10
--// tested using Max 2011
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Required Files:
--// ieMax
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Description:
--// Controls stereo camera setup (io, ia)
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Revision History:
--//
--// v 1.00 Initial version
--//
--// v 1.1
--// Changed the way the whole thing works
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
(
--// Includes
--//-----------------------------------------------------------------------------

--// Globals
--//-----------------------------------------------------------------------------
global stereoControlRoll
global stereoControlFloater

--// Variables
--//-----------------------------------------------------------------------------

--// Script
--//-----------------------------------------------------------------------------
stereoAttributes = attributes stereoControls
(  
  parameters main rollout:stereoControlRoll
  (
    io type:#worldunits ui:spnIO default:10
    targetDistance type:#worldunits ui:spnTargetDistance default:10	  
    camLeft type:#string
    camRight type:#string
    camConverge type:#string
  )

  rollout stereoControlRoll "Stereo Controls" width:160 height:168
  (
    label lbl1 "IO:" pos:[8,48] width:22 height:16
    label lbl5 "Target Distance:" pos:[8,72] width:80 height:16

    spinner spnIO "" pos:[96,48] width:56 height:16 range:[0,9999,10] type:#worldunits
    spinner spnTargetDistance "" pos:[96,72] width:56 height:16 range:[0,99999,10] type:#worldunits
    button btnSwapViews "Swap Views" pos:[8,8] width:144 height:32

    on spnTargetDistance changed val do
    (
      cConverge = getNodeByName camConverge
      cLeft = getNodeByName camLeft
      cConverge.transform = cLeft.transform
      in coordsys local move cConverge [0,0,-val]
    )
    on spnIO changed val do
    (
      cRight = getNodeByName camRight
      cLeft = getNodeByName camLeft
      cRight.transform = cLeft.transform
      in coordsys local move cRight [val,0,0]
    )
    on btnSwapViews pressed  do
    (
      cam = viewport.getCamera()
      if (cam != undefined) then
      (
        if (findString cam.name "left" != undefined) then
        (
          cRight = getNodeByName camRight
          viewport.setCamera cRight
        )
        else
        (
          cLeft = getNodeByName camLeft
          viewport.setCamera cLeft
        )  
      )
      else
      (
        cLeft = getNodeByName camLeft
        viewport.setCamera cLeft
      )
    )
  )
)
userSel = getCurrentSelection()
if (userSel.count == 1 and (classof userSel[1] == Freecamera or classof userSel[1] == Targetcamera)) then
(
  camLeft = userSel[1]
  baseName = camLeft.name
  camLeft.name = uniqueName "camera_left"  
  if (classof camLeft == Targetcamera) then
  (
    camRight = FreeCamera()
    camRight.transform = camLeft.transform
    if (camLeft.fov.controller != undefined) then
      camRight.fov.controller = camLeft.fov.controller
    else
    (
      camRight.fov.controller = camLeft.fov.controller = Bezier_Float()
    )
  )
  else
  (
    camRight = instance camLeft
  )
  camRight.name = uniqueName "camera_right"
  setTransformLockFlags camRight #{2,3,4,5,6,7,8,9}
  camConverge = point name:(uniqueName "camera_converge") centermarker:false size:20 axistripod:false cross:true box:true constantscreensize:true
  camConverge.transform = camLeft.transform
  camConverge.pos += camLeft.dir * -5
  setTransformLockFlags camConverge #{1,2,4,5,6,7,8,9}
  camUpNode = copy camConverge
  camUpNode.constantscreensize = false
  camUpNode.box = false
  camUpNode.size = 5
  camUpNode.isFrozen = true
  camUpNode.isHidden = true
  camUpNode.parent = camLeft
  camUpNode.name = uniqueName "camera_upNode"
  setTransformLockFlags camUpNode #all
  in coordsys local move camUpNode [0,1,0]
  rc = LookAt_Constraint()
  rc.appendTarget camConverge 1
  rc.target_axis = 2 --//Z Axis 
  rc.target_axisFlip = true
  rc.pickUpNode = camUpNode
  rc.upnode_world = false
  rc.StoUp_axis = 1 --// Y Axis
  rc.viewline_length_abs = true
  deleteKeys camRight.pos.controller
  deleteKeys camRight.scale.controller
  camRight.rotation.controller = rc
  
  addmodifier camConverge (EmptyModifier())
  camConverge.modifiers[1].name = "Stereo Controls"
  custAttributes.add camConverge.modifiers[1] stereoAttributes
  camConverge.modifiers[1].camLeft = camLeft.name
  camConverge.modifiers[1].camRight = camRight.name
  camConverge.modifiers[1].camConverge = camConverge.name
  camConverge.parent = camLeft
  camRight.parent = camLeft
)
--//if stereoControlFloater != undefined then CloseRolloutFloater stereoControlFloater
--//floaterWidth = (stereoControlRoll.width + 20)
--//floaterHeight = (stereoControlRoll.height + 30)
--//stereoControlFloater = newRolloutFloater "Stereo Control v1.00" floaterWidth floaterHeight 130 130
--//addRollout stereoControlRoll stereoControlFloater
)
--//--//-----------------------------------------------------------------------------