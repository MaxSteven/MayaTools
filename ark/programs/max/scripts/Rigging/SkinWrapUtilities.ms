--//-----------------------------------------------------------------------------
--// SkinWrapUtilities.ms
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
--// Utilities for quickly skinwrapping numerous objects
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
try ( destroydialog ::SkinWrapUtilities )catch()

rollout SkinWrapUtilities "SkinWrap Utilities v1.0" width:192 height:192
(
	spinner spnNumModifiersToSave "" pos:[120,48] width:64 height:16 range:[1,100,1] type:#integer
	label lbl1 "Number to Save:" pos:[8,48] width:88 height:16
	pickButton btnSkinnedObject "Pick Skinned Object..." pos:[8,8] width:176 height:32
	button btnSaveAndRemoveMod "1. Save and Remove Modifiers" pos:[8,72] width:176 height:32
	button btnSkinwrap "2. SkinWrap Selected" pos:[8,112] width:176 height:32
	button btnReapplyModifiers "3. Reapply Modifiers" pos:[8,152] width:176 height:32

	local savedModifiers = #()
	local skinnedObject

	on btnSaveAndRemoveMod pressed  do
	(
		-- save n modifiers off top and remove

		objs = getCurrentSelection()
		savedModifiers = #()
		for obj in objs do
		(
			append savedModifiers #(obj)
			for i = 1 to spnNumModifiersToSave.value do
			(
				modCount = amin obj.modifiers.count spnNumModifiersToSave.value
				for m = 1 to modCount do
				(
					append savedModifiers[savedModifiers.count] obj.modifiers[1]
					deleteModifier obj 1
				)
			)
		)
	)

	on btnSkinnedObject picked obj do
	(
		-- save global skinned object
		skinnedObject = obj
		btnSkinnedObject.text = obj.name
	)

	on btnSkinwrap pressed  do
	(
		-- skinwrap, convert, copy, remove both, paste

		if not isValidNode skinnedObject then
		(
			print "Please pick a skinned object first."
			return false
		)
		objs = getCurrentSelection()
		max modify mode
		for obj in objs do
		(
			select obj
			skinwrapMod = Skin_Wrap()
			addmodifier obj skinwrapMod
			skinwrapMod.meshList = #(skinnedObject)
			skinwrapMod.ConvertToSkin true
		)
		select objs
	)

	on btnReapplyModifiers pressed  do
	(
		-- reapply modifiers
		objs = getCurrentSelection()
		for obj in objs do
		(
			skinMod = obj.modifiers[1]
			deleteModifier obj 1
			deleteModifier obj 1
			addModifier obj skinMod
			for i = 1 to savedModifiers.count do
			(
				if obj == savedModifiers[i][1] then
				(
					for m = 2 to savedModifiers[i].count do
						addModifier obj savedModifiers[1][m]
				)
			)
		)
	)
)

createDialog SkinWrapUtilities 192 192 style:#(#style_SysMenu, #style_ToolWindow)
)
