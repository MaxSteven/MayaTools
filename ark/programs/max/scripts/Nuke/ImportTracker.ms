--//-----------------------------------------------------------------------------
--// ImportTracker.ms
--// By Grant Miller (blented@gmail.com)
--// v 1.0
--// Created On: 06/01/11
--// Modified On: 06/01/11
--// tested using Max 2011
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Required Files:
--// ieMax.ms
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Description:
--// Import's 2d trackers from nuke in to the 3dsMax
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Revision History:
--//
--// v 1.00 Initial version: import, change cam, update
--//
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
(
--// Includes
--//-----------------------------------------------------------------------------
fileIn (MAX_TOOLS_ROOT + "lib/ieMax.ms")

--// Globals
--//-----------------------------------------------------------------------------
global base, baseName, tWidth, tHeight

trackerAttributes = attributes trackerControls
(
  parameters main rollout:trackerControlRoll
  (
    zDepth type:#worldunits ui:spnZDepth default:10
  )

  rollout trackerControlRoll "Tracker Controls" width:160 height:32
  (
  	label lblZDepth "Z Depth:" pos:[8,8] width:48 height:16
  	spinner spnZDepth "" pos:[72,8] width:80 height:16 range:[0,99999,10] type:#worldunits
  )
)

--// Script
--//-----------------------------------------------------------------------------
rollout trackerRoll "Import Tracker" width:200 height:136
(
	dropdownList ddlCamera "" pos:[8,8] width:184 height:21
	button btnImportTracker "Import Tracker" pos:[8,40] width:184 height:24
	button btnChangeCamera "Change Camera for Selected" pos:[8,72] width:184 height:24
	button btnUpdateSelected "Update Selected with New Track" pos:[8,104] width:184 height:24

  fn updateCamList =
  (
    trackerRoll.ddlCamera.items = for i in cameras where superclassof i == Camera collect i.name
  )
  fn checkCam =
  (
    cam = ddlCamera.items[ddlCamera.selection]
    cam = getnodebyname cam
    if (superclassof cam != camera) then
    (
      messageBox "Please select a camera to use when importing" title:"No Camera Selected"
      return false
    )
    return cam
  )
  fn importTracker =
  (
    dataFile = openFile @"C:\ie\Temp\tracker.txt" mode:"r"
    if (dataFile == undefined) then
    (
	    messageBox "Could not find Tracker file" title:"No Tracker File"
      return false
    )
    base = Point()
    base.isFrozen = true
    base.isHidden = true
	  with animate on
	  (
		  baseName = readLine dataFile
		  base.name = baseName + "_base"
			l = readLine dataFile
      frameSize = filterString l " "
      tWidth = frameSize[1] as string
      tHeight = frameSize[2] as string
      dialogOpen = renderSceneDialog.isOpen()
      renderSceneDialog.close()
      renderWidth = tWidth as integer
      renderHeight = tHeight as integer
      if (dialogOpen) then
        renderSceneDialog.open()
		  while not (eof dataFile) do
		  (
			  l = readLine dataFile
			  data = filterString l " "
			  for n = 1 to data.count do
				  data[n] = data[n] as float
			  at time data[1] base.pos = [data[2], 0, data[3]]
		  )
	  )
	  close dataFile
  )
  on trackerRoll open do
  (
    ddlCamera.items = for i in cameras where superclassof i == Camera collect i.name
--//    callbacks.removeScripts #sceneNodeAdded id:#camUpdateCreated
--//    callbacks.removeScripts #nodeRenamed  id:#camUpdateRenamed
--//    callbacks.removeScripts #nodePostDelete  id:#camUpdateDeleted
--//	  callbacks.addScript #sceneNodeAdded "trackerRoll.updateCamList()" id:#camUpdateCreated
--//    callbacks.addScript #nodeRenamed "trackerRoll.updateCamList()" id:#camUpdateRenamed
--//    callbacks.addScript #nodePostDelete "trackerRoll.updateCamList()" id:#camUpdateDeleted
  )
  on trackerRoll close do
  (
    callbacks.RemoveScripts #sceneNodeAdded id:#camUpdate
    callbacks.RemoveScripts #nodeRenamed id:#camUpdateRenamed
    callbacks.RemoveScripts #nodePostDelete id:#camUpdateDeleted
  )
	on trackerRoll rolledUp state do
	(
		if (state) then
			f.size.y += trackerRoll.height
		else
			f.size.y -= trackerRoll.height
	)
  on btnImportTracker pressed do
  (
    cam = checkCam()
    if cam == false then return false
    importTracker()
    trackPoint = Point name:baseName
    addmodifier trackPoint (EmptyModifier())
    trackPoint.modifiers[1].name = "Tracker Controls"
    custAttributes.add trackPoint.modifiers[1] trackerAttributes
    trackPoint.modifiers[1].zDepth.controller = bezier_float()
    ps = position_script()
    ps.AddTarget "ref" base[3][1]
    ps.AddTarget "depth" trackPoint.modifiers[1].zDepth.controller
    ps.AddNode "cam" cam
    ps.script = @"hfov = cam.fov*.5
vfov = atan ((tan hfov) * renderheight/renderwidth)
wRat = renderWidth / " + tWidth + ".0
hRat = renderHeight / " + tHeight + ".0
x = depth*(tan hfov)*(ref.x*wRat - renderwidth * .5) / (renderwidth * .5)
y = depth*(tan vfov)*(ref.z*hRat - renderheight * .5) / (renderheight * .5)
z = -depth
[x,y,z] * cam.transform"
    trackPoint.position.controller = ps
    select trackPoint
  )
  on btnChangeCamera pressed do
  (
    cam = checkCam()
    if cam == false then return false
    userSel = getCurrentSelection()
    for s in userSel do
    (
      ps = s.position.controller
      if (classof ps == position_script) then
        ps.SetNode "cam" cam
    )
    slidertime -= 1
    slidertime += 1
  )
  on btnUpdateSelected pressed do
  (
    userSel = getCurrentSelection()
    if userSel.count > 1 then
    (
      messageBox "Please select a single tracker to update" title:"Invalid Selection"
      return false
    )
    userSel = userSel[1]
    ps = userSel.position.controller
    if (classof ps == position_script) then
    (
      b = getnodebyname (userSel.name + "_base")
      if (isvalidnode b) then delete b
      importTracker()
      ps.SetTarget "ref" base[3][1]
    )
    slidertime -= 1
    slidertime += 1
  )
)

if f != undefined then CloseRolloutFloater f
floaterWidth = (trackerRoll.width + 20)
floaterHeight = (trackerRoll.height + 30)
f = newRolloutFloater "Import Tracker v1.00" floaterWidth floaterHeight 130 130
addRollout trackerRoll f
)
--//-----------------------------------------------------------------------------