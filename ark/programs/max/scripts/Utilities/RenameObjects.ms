try(DestroyDialog ::rlRenamer)catch()
rollout rlRenamer "Rename Objects"
(
	--//Functions
	function objectSelected =
	(
		sel = selection as array
	)
	
	
	pickbutton pbtnFind "Find:" width:48 height:16 pos:[10,10]
	edittext etFindTXT "" fieldwidth:120 pos:[55,9]
	pickbutton pbtnReplace "Replace:" width:48 height:16 pos:[10,31]
	edittext etReplaceTXT "" fieldwidth:120 pos:[55,30]
	button btnRename "Apply Rename To Selection" width:170 height:24 pos:[10,56]
	
	on pbtnFind picked obj do
	( 
		if obj != undefined do
		(
			etFindTXT.text = obj.name
		)
	)
	
	on pbtnReplace picked obj do
	( 
		if obj != undefined do
		(
			etReplaceTXT.text = obj.name
		)
	)
	
	on btnRename pressed do (
		(
			nameChange = objectSelected()
			
			txt = ""
			
			f = etFindTXT.text
			r = etReplaceTXT.text
			searchString = ""
			
			if f == "" then (
				messagebox "Nothing to search for.  \nPlease type something into \"Find\" field." title:"Search Error" 
			)else(
				searchString= "*"+f+"*"
				for obj in selection do
				(
					if (matchPattern obj.name pattern: searchString) then (
						obj.name = substituteString obj.name f r
					)
				)
			)
		)
	)
	
	on rlRenamer open do (
		if selection.count >= 1 do
		(
			etFindTXT.text = selection[1].name
		)
	)
)
createDialog rlRenamer 190 89 style:#(#style_SysMenu, #style_ToolWindow)
