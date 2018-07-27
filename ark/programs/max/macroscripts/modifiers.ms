--increase turbosmooth iterations
--acts on the first turbosmooth found in the modifier stack
macroScript SmoothUp category:"Ingenuity" tooltip:"Smooth Up"
(
	on isEnabled return (selection.count > 0)
	on execute do (
		max modify mode
		done = false
		i = 1
    obj = (getCurrentSelection())[1]
    
		while obj.modifiers[i] != undefined and done == false do
    (
      modClass = classof obj.modifiers[i]
			if modClass == TurboSmooth or modClass == TurboSmooth_Pro then
      (
				obj.modifiers[i].iterations += 1
				done = true
			)
			i += 1
		)
		if done == false then
    (
			obj = modPanel.getCurrentObject()
			addMod Turbosmooth
			modPanel.setCurrentObject obj
			showEndResult = true
		)
	)
)

macroScript TurboSmoothPro category:"Ingenuity" tooltip:"Turbosmooth Pro"
(
  objs = getCurrentSelection()
  if objs == #() then
    return false
  m = TurboSmooth_Pro()
	addmodifier objs m
)

macroScript QuadChamfer category:"Ingenuity" tooltip:"Quad Chamfer"
(
  objs = getCurrentSelection()
  if objs == #() then
    return false
  m = Quad_Chamfer()
	addmodifier objs m
)

--decrease turbosmooth iterations
--removes the modifier if iterations fall below 1
macroScript SmoothDown category:"Ingenuity" tooltip:"Smooth Down"
(
	on isEnabled return (selection.count > 0)
	on execute do (
		max modify mode
		i = 1
    obj = (getCurrentSelection())[1]
		while obj.modifiers[i] != undefined do
    (
      modClass = classof obj.modifiers[i]
			if modClass == TurboSmooth or modClass == TurboSmooth_Pro then
      (
        mod = obj.modifiers[i]
				if mod.iterations > 1 then
        (
					mod.iterations -= 1
				) else (
					level = subObjectLevel          
					for o in getCurrentSelection() do deleteModifier o mod
					subObjectLevel = level
					showEndResult = false
					exit
				)
			)
			i += 1
		)
	)
)

--toggles turbosmooth on and off
macroScript SmoothToggle category:"Ingenuity" tooltip:"Smooth Toggle"
(
	on isEnabled return (selection.count > 0)
	on execute do (
		i = 1
    obj = (getCurrentSelection())[1]
		while obj.modifiers[i] != undefined do
    (
      modClass = classof obj.modifiers[i]
			if modClass == TurboSmooth or modClass == TurboSmooth_Pro then
				obj.modifiers[i].enabled = not obj.modifiers[i].enabled
			i += 1
		)
	)
)

--add smooth modifier and automatically turn it on
macroScript SmoothAutoOn category:"Ingenuity" tooltip:"Auto-on Smooth Mod."
(
	on isEnabled return	( selection.count >=1)
	on execute do (
		addModifier $ (smooth())
		for obj in $ do	obj.modifiers[#Smooth].autosmooth = on
	)
)

--add uvw map and change to real world coords and box mode
macroScript BoxUnwrapRealWorld category:"Ingenuity" tooltip:"Box UVW RealWorld"
(
	macros.run "Modifiers" "Uvwmap"
	for sel in $ do	(
		sel.modifiers[#UVW_Mapping].maptype = 4
		sel.modifiers[#UVW_Mapping].realWorldMapSize = on
		sel.modifiers[#UVW_Mapping].utile = 1
		sel.modifiers[#UVW_Mapping].vtile = 1
		sel.modifiers[#UVW_Mapping].length = 1
		sel.modifiers[#UVW_Mapping].width = 1
		sel.modifiers[#UVW_Mapping].height = 1
	)
)

--add surface modifier and automatically set steps to 0
macroScript SurfaceNoSteps category:"Ingenuity" tooltip:"Surface No Steps"
(
	on isEnabled return	( selection.count>=1)
	on execute do (
		AddMod surface
		for sel in $ do	sel.modifiers[#Surface].steps = 0
	)
)

--add mesh smooth modifier and automatically change sub-d type to classic
macroScript MeshSmoothClassic category:"Ingenuity" tooltip:"Classic Mesh Smooth"
(
	on isEnabled return	( selection.count>=1)
	on execute do (
		macros.run "Modifiers" "MeshSmooth"
		for sel in $ do	
			sel.modifiers[#MeshSmooth].subdivMethod = 0
	)
)

-- Remove Top Modifier from stack
macroScript RemoveTopModifier category:"Ingenuity" tooltip:"Remove Top Modifier"
(
 	on isEnabled return	( selection.count==1 and $.modifiers.count > 0 )
	on execute do ( deleteModifier $ 1 )
)

-- Go to the the bottom of the modifier stack
macroScript GotoBaseObj category:"Ingenuity" tooltip:"Goto Base Object"
(
 	on isEnabled return	( selection.count==1 )
	on execute do ( 
		modPanel.setCurrentObject $.baseObject
		subObjectLevel = 0
	)
)

-- Go to object level 0
macroScript GotoObjectLevel category:"Ingenuity" tooltip:"Goto Object Level"
(
 	on isEnabled return	( selection.count==1 )
	on execute do ( 
		subObjectLevel = 0
	)
)
