--//-----------------------------------------------------------------------------
--// InstanceReplacer.ms
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
try ( destroydialog ::instanceReplacer )catch()

rollout instanceReplacer "Instance Replacer v1.0"
(
  pickbutton btnReplaceWith "Replace With..."
  button btnReplaceSelected "Replace Selected"
  checkbox chkKeepOriginal "Keep Original" checked:false
  button btnSelectInstancesOfSelected "Select All Instances of Selected"

  global replaceObj

  --//button btnUpdateAsset "Update Asset"

  on btnReplaceWith picked obj do
  (
    btnReplaceWith.text = obj.name
  replaceObj = obj
  )

  on btnReplaceSelected pressed do
  (
    undo "Replace Instances" on
    (
      if replaceObj == undefined then
      (
        print "Please pick an object first"
        return false
      )
      userSel = getCurrentSelection()

      allInstances = #()
      instances = #()
      for obj in userSel do
      (
        InstanceMgr.GetInstances obj &instances
        allInstances += instances
      )

      for obj in allInstances do
      (
        newObj = instance replaceObj
        newObj.transform = obj.transform
      )
      if not chkKeepOriginal.checked then
        delete allInstances
    )
  )

  on btnSelectInstancesOfSelected pressed do
  (
    userSel = getCurrentSelection()
    allInstances = #()
    instances = #()
    for obj in userSel do
    (
      InstanceMgr.GetInstances obj &instances
      allInstances += instances
    )
    select allInstances
  )
)

createDialog instanceReplacer 200 110 style:#(#style_SysMenu, #style_ToolWindow)
)
