--//-----------------------------------------------------------------------------
--// AnimationStopwatch.ms
--// By Grant Miller (blented@gmail.com)
--// v 1.0
--// Created On: 03/19/08
--// Modified On: 03/19/08
--// tested using Max 2008
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Required Files:
--// ieMax
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Description:
--// Used to calculate animation times
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
global animationStopwatchRoll
global animationStopwatchFloater

--// Variables
--//-----------------------------------------------------------------------------
fps = 30
milisecondTime = 0
seconds = #()
frames = #()

--// Script
--//-----------------------------------------------------------------------------
rollout animationStopwatchRoll "Animation Stopwatch" width:312 height:240
(
  label lblFps "FPS:" pos:[224,8] width:24 height:16
  label lblSeconds "Seconds:" pos:[8,8] width:48 height:16
  label lblFrames "Frames:" pos:[120,8] width:40 height:16
  button btnToFrames "to Frames ->" pos:[8,32] width:96 height:24
  button btnToSeconds "<- to Seconds" pos:[120,32] width:96 height:24
  spinner spnFPS "" pos:[248,8] width:56 height:16 range:[0,1000,fps]
  spinner spnFrames "" pos:[160,8] width:56 height:16 range:[0,1000,0]
  spinner spnSeconds "" pos:[56,8] width:56 height:16 enabled:true range:[0,1000,0]
  listbox lbxAverageTimes "Average Times" pos:[8,64] width:208 height:9
  checkbutton ckbStart "Start" pos:[224,32] width:80 height:200
  button btnClear "Clear" pos:[112,208] width:104 height:24
  button btnRemove "Remove" pos:[8,208] width:104 height:24
  timer tmrTime "Timer" pos:[200,56] width:24 height:24 enabled:true interval:100 active:false

  fn updateAverages =
  (
    lbxAverageTimes.items = #()
    if (seconds.count > 0) then
    (
      for i = 1 to seconds.count do
        append lbxAverageTimes.items ((seconds[i] as string) + " seconds     " + (frames[i] as string) + " frames")

      append lbxAverageTimes.items "---------------------------------------------------------------"
      append lbxAverageTimes.items (((ieMaxAvgArray seconds) as string) + " seconds     " + ((ieMaxAvgArray frames) as string) + " frames")
      lbxAverageTimes.items = lbxAverageTimes.items
    )
  )
  fn removeAverage =
  (
    timeCount = lbxAverageTimes.items.count
    userSelection = lbxAverageTimes.selection
    if (userSelection != undefined) then
    (
--//      if you don't have the average or the dashes highlighted
      if (userSelection != timeCount and userSelection != (timeCount - 1)) then
      (
        oldSelection = userSelection
        deleteItem seconds userSelection
        deleteItem frames userSelection
        updateAverages()

        if (oldSelection < lbxAverageTimes.items.count) then
          lbxAverageTimes.selection = oldSelection
        else if (lbxAverageTimes.items.count > 0) then
          lbxAverageTimes.selection = lbxAverageTimes.items.count
      )
    )
  )

  on animationStopwatchRoll open do
  (
    setFocus ckbStart
  )
  on btnToFrames pressed  do
  (
    spnFrames.value = spnSeconds.value * spnFPS.value
  )
  on btnToSeconds pressed  do
  (
    spnSeconds.value = spnFrames.value / spnFPS.value
  )
  on ckbStart changed state do
  (
    if (state) then
    (
      ckbStart.caption = "Stop"
      milisecondTime = 0
      tmrTime.active = true
    )
    else
    (
      ckbStart.caption = "Start"
      tmrTime.active = false
      append seconds spnSeconds.value
      append frames spnFrames.value
      updateAverages()
    )
  )
  on btnClear pressed  do
  (
    lbxAverageTimes.items = #()
    lbxAverageTimes.items = lbxAverageTimes.items
    seconds = #()
    frames = #()
  )
  on btnRemove pressed  do removeAverage()
  on lbxAverageTimes doubleClicked sel do removeAverage()
  on tmrTime tick  do
  (
    milisecondTime += 1
    spnSeconds.value = milisecondTime * 0.1
    spnFrames.value = spnSeconds.value * spnFPS.value
  )
  on animationStopwatchRoll rolledUp state do
  (
    if (state) then
      animationStopwatchFloater.size.y += animationStopwatchRoll.height
    else
      animationStopwatchFloater.size.y -= animationStopwatchRoll.height
  )
)

if (animationStopwatchFloater != undefined) then CloseRolloutFloater animationStopwatchFloater
floaterWidth = (animationStopwatchRoll.width + 20)
floaterHeight = (animationStopwatchRoll.height + 30)
animationStopwatchFloater = newRolloutFloater "Animation Stopwatch v1.00" floaterWidth floaterHeight 130 130
addRollout animationStopwatchRoll animationStopwatchFloater
)
--//-----------------------------------------------------------------------------