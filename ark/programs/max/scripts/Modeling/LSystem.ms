--//-----------------------------------------------------------------------------
--// LSystem.ms
--// By Grant Miller (grant.miller@Ingenuity.com)
--// v 1.0
--// Created On: 01/12/10
--// Modified On: 01/12/10
--// tested using Max 2010
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Required Files:
--// ieMax
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Description:
--// Creates L Systems... it's better if you just read the wiki
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
global lSystemRoll
global lSystemFloater
global rules = #()
global turtleNodes = #()
global jMeshes = #()
global kMeshes = #()
global mMeshes = #()
global jCount, kCount, mCount
struct rule (symbol, replacement, probability, leftContext, rightContext, condition)
global step, stepScale, ang, angScale, thickness, thicknessScale, sides, steps, splineType
global startingStep
global generation = 1

--// Variables
--//-----------------------------------------------------------------------------

--// Script
--//-----------------------------------------------------------------------------
rollout lSystemRoll "LSystem" width:336 height:752
(
  GroupBox grp1 "Generation" pos:[8,8] width:320 height:168
  GroupBox grp2 "Variables" pos:[8,184] width:320 height:72
  GroupBox grp3 "Geometry" pos:[8,264] width:320 height:112
  GroupBox grp4 "Meshes" pos:[8,384] width:320 height:176

  label lbl1 "Initiator:" pos:[25,32] width:47 height:16
  label lbl2 "Rule 1:" pos:[24,56] width:47 height:16
  label lbl3 "Rule 2:" pos:[24,80] width:47 height:16
  label lbl4 "Rule 3:" pos:[24,104] width:47 height:16
  label lbl5 "Rule 4:" pos:[24,128] width:47 height:16
  label lbl6 "Rule 5:" pos:[24,152] width:47 height:16
  label lbl7 "Step:" pos:[16,208] width:32 height:16
  label lbl8 "Step Scale:" pos:[120,208] width:56 height:16
  label lbl9 "Angle:" pos:[16,232] width:40 height:16
  label lbl10 "Angle Scale:" pos:[120,232] width:64 height:16
  label lbl11 "Sides:" pos:[64,280] width:32 height:16
  label lbl12 "Interpolation:" pos:[32,328] width:64 height:16
  label lbl13 "Thickness:" pos:[48,304,.1] width:53 height:16
  label lbl14 "Thickness Scale:" pos:[16,352] width:80 height:16
  label lbl15 "Output:" pos:[8,600] width:53 height:16
  label lbl31 "Iterations:" pos:[8,568] width:53 height:16

  edittext edtInitiator "" pos:[72,32] width:248 height:16 text:"FFA"
  edittext edtRule1 "" pos:[71,56] width:249 height:16 text:"A=FA:.5"
  edittext edtRule2 "" pos:[71,80] width:249 height:16 text:"A=!\"[B]////[B]////[+B]:.5"
  edittext edtRule3 "" pos:[71,104] width:249 height:16 text:"B=F&FA[F[^^J]////[^+^J]////[^-^J]]:.5"
  edittext edtRule4 "" pos:[71,128] width:249 height:16 text:"B=F^F[A]:.5"
  edittext edtRule5 "" pos:[71,152] width:249 height:16 text:""
  edittext edtOutput "" pos:[8,616] width:320 height:128

  spinner spnStep "" pos:[56,208] width:56 height:16 range:[-9999,9999,10] type:#worldunits
  spinner spnStepScale "" pos:[184,208] width:56 height:16 range:[-9999,9999,.9] type:#float
  spinner spnAngle "" pos:[56,232] width:56 height:16 range:[-9999,9999,30] type:#float
  spinner spnAngleScale "" pos:[184,232] width:56 height:16 range:[-9999,9999,.9] type:#float
  spinner spnSides "" pos:[104,280] width:56 height:16 range:[1,9999,8] type:#integer
  spinner spnSteps "" pos:[104,328] width:56 height:16 range:[1,9999,3] type:#integer
  spinner spnThickness "" pos:[104,304] width:56 height:16 range:[-9999,9999,7] type:#worldunits
  spinner spnThicknessScale "" pos:[104,352] width:56 height:16 range:[-9999,9999,.9] type:#float
  spinner spnIterations "" pos:[60,568] width:56 height:16 range:[0,9999,26] type:#float scale:1
  radioButtons rdoSplineType "Spline Type" pos:[184,280] width:65 height:46 labels:#("Linear", "Smooth")

  button btnGenerate "Generate" pos:[128,568] width:144 height:24
  listbox lbxJMeshes "J Meshes:" pos:[16,400] width:96 height:7
  button btnAddJ "Add Selected" pos:[16,520] width:96 height:16
  button btnClearJ "Clear" pos:[16,536] width:96 height:16
  listbox lbxKMeshes "K Meshes:" pos:[120,400] width:96 height:7
  button btnAddK "Add Selected" pos:[120,520] width:96 height:16
  button btnClearK "Clear" pos:[120,536] width:96 height:16
  listbox lbxMMeshes "M Meshes:" pos:[224,400] width:96 height:7
  button btnAddM "Add Selected" pos:[224,520] width:96 height:16
  button btnClearM "Clear" pos:[224,536] width:96 height:16

  fn parseRule text =
  (
    text = ieMaxStripSpaces text
    parsed = filterString text "="
    if (parsed.count == 2) then
    (
      prob = filterString parsed[2] ":"
      if (prob.count == 2) then
      (
        parsed[2] = prob[1]
        prob = prob[2] as float
      )
      else
        prob = 1

      append rules (rule symbol:parsed[1] replacement:parsed[2] probability:prob)
    )
  )
  fn addTurtleNode obj objParent =
  (
     append turtleNodes obj
     if (objParent != undefined) then
       setUserProp obj "parent" objParent.name
  )
  fn turtleDraw tSpline tLoc =
  (
    if (splineType == 1) then
      addKnot tSpline 1 #corner #line tLoc
    else if (splineType == 2) then
      addKnot tSpline 1 #smooth #curve tLoc
  )
  fn turtleWord w tLoc tDir tParent =
  (
    tSpline = SplineShape thickness:thickness sides:sides steps:steps render_displayRenderMesh:true render_renderable:true render_autosmooth:true render_threshold:60
    tSpline.name = uniquename ("tSpline_")
    tSpline.transform = transMatrix tLoc
    addNewSpline tSpline
    c = 1
    while (c <= w.count) do
    (
      if (w[c] == "F") then
      (
        if (numKnots tSpline < 1) then
          turtleDraw tSpline tLoc

        m = rotate (MatrixFromNormal [0,0,1]) tDir
        tLoc += step * [m[1][3],m[2][3],m[3][3]]
        turtleDraw tSpline tLoc
--//        format "tLoc: %\n" tLoc
      )
      else if (w[c] == "+") then tDir *= quat ang [0,-1,0]
      else if (w[c] == "-") then tDir *= quat -ang [0,-1,0]
      else if (w[c] == "/") then tDir *= quat -ang [0,0,-1]
      else if (w[c] == "&") then tDir *= quat ang [-1,0,0]
      else if (w[c] == "^") then tDir *= quat -ang [-1,0,0]
      else if (w[c] == "\"") then step *= stepScale
      else if (w[c] == "_") then step /= stepScale
      else if (w[c] == "!") then thickness *= thicknessScale
      else if (w[c] == "?") then thickness /= thicknessScale
      else if (w[c] == ";") then ang *= angScale
      else if (w[c] == "@") then ang /= angScale
      else if (w[c] == "J" and jCount > 0) then
      (
        obj = jMeshes[random 1 jCount]
        obj = instance obj
        obj.pos = tLoc
        in coordsys local obj.rotation = tDir
        obj.scale *= step / startingStep
        addTurtleNode obj tSpline
      )
      else if (w[c] == "[") then
      (
        tempStep = step
        tempAngle = ang
        tempThickness = thickness
        c += turtleWord (substring w (c+1) -1) tLoc tDir tSpline
        step = tempStep
        ang = tempAngle
        thickness = tempThickness
      )
      else if (w[c] == "]") then exit
--//      format "letter: %\n" w[c]
--//      format "tDir: %\n" tDir
--//      format "-----\n"
      c += 1
    )
--//    format "exit c: %\n" c
--//    format "letter: %\n" w[c]
--//    format "tDir: %\n" tDir
--//    format "tLoc: %\n" tLoc
--//    format "-----\n"
    if ((numKnots tSpline) > 1) then
    (
      updateShape tSpline
      cX = tSpline.transform
      tSpline.transform = ieMaxGetSplineMatrix tSpline 1 1
      tSpline.objectOffsetRot = cX.rotationPart - tSpline.transform.rotationPart
    )
    else
    (
      d = dummy boxSize:([step * .5, step * .5, step * .5]) transform:tSpline.transform name:tSpline.name
      delete tSpline
      tSpline = d
    )
    addTurtleNode tSpline tParent
    return c
  )
  fn parentTurtles =
  (
    for t in turtleNodes do
    (
      p = getUserProp t "parent"
      if (p != undefined) then
      (
        np = getNodeByName p
        t.parent = np
      )
    )
  )
  fn linkTurtles t gen =
  (
--//      np = t.parent
      np = $controller
      scaleOffset = (gen - 1) as string
      scaleScript = (t.scale as string) + " * [amax 0.0 (amin 1.0 (Scale.x - " + scaleOffset + ")),amax 0.0 (amin 1.0 (Scale.y - " + scaleOffset + ")),amax 0.0 (amin 1.0 (Scale.z - " + scaleOffset + "))]"
      t.parent = undefined --//remove
      if (t.children.count > 0) then
      (
        for c in t.children do
          linkTurtles c (gen + 1)
      )
      paramWire.connect np[#transform][3] t[#transform][3] scaleScript
  )

  on btnAddJ pressed do
  (
    userSel = getCurrentSelection()
    for obj in userSel do
    (
      append lbxJMeshes.items obj.name
      lbxJMeshes.items = lbxJMeshes.items
      append jMeshes obj
    )
  )
  on btnGenerate pressed  do
  (
    edtOutput.text = ""
    rules = #()
    turtleNodes = #()
    parseRule edtRule1.text
    parseRule edtRule2.text
    parseRule edtRule3.text
    parseRule edtRule4.text
    parseRule edtRule5.text

    word = ieMaxStripSpaces edtInitiator.text
    r = 1
    ruleCount = rules.count
    for i = 1 to (floor spnIterations.value) do
    (
      word = ieMaxStringToArray word
      c = 1
      wordCount = word.count
      while (c <= wordCount) do
      (
        if (word[c] == rules[r].symbol) then
        (
          if (rules[r].probability == 1.0 or (random 0.0 1.0) >= rules[r].probability) then
            word[c] = rules[r].replacement
        )
        c += 1
      )
      word = ieMaxArrayToString word
      edtOutput.text += word + "\n"
      r += 1
      if (r > ruleCount) then r = 1
    )

    step = startingStep = spnStep.value
    stepScale = spnStepScale.value
    ang = spnAngle.value
    angScale = spnAngleScale.value
    thickness = spnThickness.value
    thicknessScale = spnThicknessScale.value
    sides = spnSides.value
    steps = spnSteps.value
    splineType = rdoSplineType.state
    jCount = jMeshes.count
    kCount = kMeshes.count
    mCount = mMeshes.count

    turtleWord word [0,0,0] (quat 0 0 0 1) undefined
    parentTurtles()
    t = 1
    turtleCount = turtleNodes.count
    while (t <= turtleCount) do
    (
      if (classOf turtleNodes[t] == Dummy) then
      (
        if (turtleNodes[t].children != undefined) then
        (
          for c in turtleNodes[t].children do
            c.parent = turtleNodes[t].parent
        )
        delete turtleNodes[t]
        deleteItem turtleNodes t
        turtleCount -= 1
      )
      else
      (
        t += 1
      )
    )
    for t in turtleNodes where classOf t == Dummy do removeEmptyTurtle t
    generation = 1
    --for t in turtleNodes where t.parent == undefined do linkTurtles t 1
    completeRedraw()
  )
  on lSystemRoll open do
  (
  )
  on lSystemRoll close do
  (
  )
  on lSystemRoll rolledUp state do
  (
    if (state) then
      lSystemFloater.size.y += lSystemRoll.height
    else
      lSystemFloater.size.y -= lSystemRoll.height
  )
)

if lSystemFloater != undefined then CloseRolloutFloater lSystemFloater
floaterWidth = (lSystemRoll.width + 20)
floaterHeight = (lSystemRoll.height + 30)
lSystemFloater = newRolloutFloater "LSystem v1.00" floaterWidth floaterHeight 130 130
addRollout lSystemRoll lSystemFloater
)
--//--//-----------------------------------------------------------------------------