--//-----------------------------------------------------------------------------
--// IERun.ms
--// By Grant Miller (blented@gmail.com) and John Martini (jokermartini@gmail.com)
--// v 2.0
--// Created On: 03/11/09
--// Modified On: 02/20/12
--// tested using Max 2012
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Required Files:
--// ieMax.ms
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Description:
--// Tool runner in 3dsMax
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Revision History:
--//
--// v 1.00 Initial version
--//
--// v 2.00 Changed to be a cascading folder
--//
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
(
--// Includes
--//-----------------------------------------------------------------------------
	fileIn (MAX_TOOLS_ROOT + "lib/ieMax.ms")

	local fullPath = undefined
	dir = MAX_TOOLS_ROOT + "scripts"
	dirArray = sort (GetDirectories (dir + "/*")) --//Get subfolders in directory

	dir = ARK_ROOT + "Common"
	dirArray += sort (GetDirectories (dir + "/*")) --//Get subfolders in directory

	foldersArray = for d in dirArray where (findString d "tools\\Common" == undefined) collect (trimright (filenameFromPath d) "\\") --// Array which stores just the names of the subfolders
	foldersArray += #("Common")

	local contextMenu = dotNetObject "System.Windows.Forms.ContextMenuStrip"
	local cursor = dotNetClass "System.Windows.Forms.Cursor"

	for i in foldersArray do
	(
		item = contextMenu.Items.Add i
		item.name = i
	)

	fn onPopup s e =
	(
		for b = 1 to foldersArray.count do
		(
			i = (s.Items.Find (foldersArray[b] as string) off)[1]
			i.DropDownItems.Clear()

			sFiles = #()
			if (dirArray[b] != undefined) then
				sFiles = getFiles (dirArray[b] + "*.ms*")
		  --pyFiles = getFiles (dirArray[b] + "*.py")
		  --sFiles += pyFiles

			fn fnRunScript s e = --//Run the selected script
			(
				print s.tag
				ext = getFilenameType s.tag

				if (ext == ".ms" or ext == ".mse") then
				(
					fileIn (s.tag)
				)
				else if (ext == ".py") then
				(
				  if (python == undefined) then
				  (
					format "Python execution ability not found, speak with your supervisor to ensure proper tools installation\n"
				  )
				  else
				  (
					filename = substituteString s.tag "\\" "/"
					try(print (python.run filename)) catch( format "There was an error importing the Python source file\n" )
					format (filename + "\n")
				  )
				)
			)

			if sFiles.count > 0 then --//Add the scripts to appropriate list
			(
				for n in sFiles do
				(
					scriptName = getFileNameFile n
					item = i.DropDownItems.Add scriptName
					item.name = scriptName
					item.tag = n --// variable "n" contains the fullpath extention

					dotnet.addEventHandler item "Click" fnRunScript
				)
			)
			else
			(
				item = i.DropDownItems.Add "No Scripts"
				item.enabled = off
			)
		)
	)
	dotnet.addEventHandler contextMenu "Opening" onPopup

	on execute do
	(
		contextMenu.Show(cursor.Position)
	)
)
