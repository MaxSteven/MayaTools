try(destroydialog ::rlRemoveMods)catch()
rollout rlRemoveMods "Remove Modifiers"
(
	local modsArray = #()
	
	fn fnGetActiveMods = (
		modsArray = #()
		for obj in objects do
		(
			for m in obj.modifiers do
			(
				test = findItem modsArray (classof m)
				if (findItem modsArray (classof m)) == 0 do
				(
					append modsArray (classof m)
				)
			)
		)
		rlRemoveMods.mlbActiveMods.items = for m in modsArray collect m as string
	)

	button btnRefresh "O" width:20 height:16 pos:[120,8] tooltip:"Updates the active mods list"
	MultiListBox mlbActiveMods "Active Scene Mods:" items:#() width:130 height:10 pos:[10,10]
	groupbox gbAffect "" width:130 height:55 pos:[10,155]
	label lbAffect "Affect:" pos:[20,170]
	radiobuttons rbAffect "" labels:#("Scene","Selection") columns:1 pos:[70,170] default:2
	button btnRemoveMod "Remove Mods" height:30 width:130 pos:[10,210]
	button btnDisMod "Disable" height:30 width:65 pos:[10,240]
	button btnEnMod "Enable" height:30 width:65 pos:[75,240]
	
	on btnRefresh pressed do fnGetActiveMods()
	on rlRemoveMods open do fnGetActiveMods()
	on mlbActiveMods doubleClicked itm do fnGetActiveMods()
	
	on btnRemoveMod pressed do
	(
		collection = if rbAffect.state == 1 then objects else selection
		
		itmSel = mlbActiveMods.selection as array
		modsToKill = for i = 1 to itmSel.count collect modsArray[itmSel[i]]
			
		for obj in collection do
		(
			for i = obj.modifiers.count to 1 by -1 where findItem modsToKill (classof obj.modifiers[i]) != 0 do 
			(
				deleteModifier obj obj.modifiers[i]
			)
		)
		fnGetActiveMods()
	)
	
	on btnDisMod pressed do
	(
		collection = if rbAffect.state == 1 then objects else selection
		
		itmSel = mlbActiveMods.selection as array
		modsToKill = for i = 1 to itmSel.count collect modsArray[itmSel[i]]
			
		for obj in collection do
		(
			for i = obj.modifiers.count to 1 by -1 where findItem modsToKill (classof obj.modifiers[i]) != 0 do 
			(
				obj.modifiers[i].enabled = false
			)
		)
		fnGetActiveMods()
	)
	
	on btnEnMod pressed do
	(
		collection = if rbAffect.state == 1 then objects else selection
		
		itmSel = mlbActiveMods.selection as array
		modsToKill = for i = 1 to itmSel.count collect modsArray[itmSel[i]]
			
		for obj in collection do
		(
			for i = obj.modifiers.count to 1 by -1 where findItem modsToKill (classof obj.modifiers[i]) != 0 do 
			(
				obj.modifiers[i].enabled = true
			)
		)
		fnGetActiveMods()
	)
	
)
createDialog rlRemoveMods 150 280 style:#(#style_SysMenu, #style_ToolWindow)
