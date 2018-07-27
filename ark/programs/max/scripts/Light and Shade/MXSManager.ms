--//-----------------------------------------------------------------------------
--// MXSManager.ms
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
global mxsSaveFile

--// Functions
--//-----------------------------------------------------------------------------

--// Script
--//-----------------------------------------------------------------------------
try ( destroydialog ::MXSManager )catch()

rollout MXSManager "MXS Manager v.10" width:240 height:128
(
	button btnSaveFile "Select Save File..." pos:[8,8] width:224 height:21
	checkbox chkSelected "Selected Only" pos:[13,32] width:90 height:15 checked:((getCurrentSelection()).count > 0)
	checkbox chkAnimation "Animation" pos:[13,52] width:70 height:15 checked:false
	button btnExportMXS "Export MXS" pos:[8,72] width:224 height:21
	button btnCreateMXSReference "Create MXS Reference" pos:[8,98] width:224 height:21

	fn getOutputPath =
	(
		if (maxfilepath.count < 1) then
			return ""
		rootParts = filterString maxfilepath "\\"
		-- fix: should put this in a library
		-- get the export root
		if (rootParts.count < 4) then
			return False
		root = ""
		for n = 1 to 4 do
			root += rootParts[n] + "/"
		return root + "cache/" + (substituteString maxfilename ".max" ".mxs")
	)
	fn getMXSSaveFile =
	(
		return getSaveFileName caption:"MXS Output" \
			filename:(getOutputPath()) \
			types:"Maxwell Scene (*.mxs)|*.mxs"
	)

	on btnSaveFile pressed do
	(
		mxsSaveFile = getMXSSaveFile()
		if (mxsSaveFile != undefined) then
		(
			fileParts = filterString mxsSaveFile "\\"
			-- fix: should put this in a library
			if (fileParts.count < 4) then
				return False
			file  = ""
			print fileParts.count
			for n = 4 to fileParts.count do
				file += "/" + fileParts[n]
			btnSaveFile.text = file
		)
	)
	on btnExportMXS pressed do
	(
		if (chkAnimation == false) then
		(
			ogRange = animationRange
			ogRenderTimeType = rendTimeType
			ogMoblur = renderers.current.gsMotionBlur
			ogMoblurSteps = renderers.current.gsMbSteps
			ogOpen = renderSceneDialog.isOpen

			renderSceneDialog.close()
			animationRange = interval 0f 0.1f
			rendTimeType = 1
			renderers.current.gsMotionBlur = 2
			renderers.current.gsMbSteps = 2
		)


		if (mxsSaveFile == undefined) then
		(
			messageBox "Please choose a save file first" caption:"No Save File"
			return false
		)
		if (cameras.count < 1) then
		(
			messageBox "No camera found in the scene, stupid I know..." caption:"No Camera"
			return false
		)

		maxwellExportMXS output:mxsSaveFile selectedObjects:chkSelected.checked animation:chkAnimation.checked appendFrameNrToImg:false camera:cameras[1]

		print "MXS output to:"
		print mxsSaveFile

		if (chkAnimation == false) then
		(
			animationRange = ogRange
			rendTimeType = ogRenderTimeType
			renderers.current.gsMotionBlur = ogMoblur
			renderers.current.gsMbSteps = ogMoblurSteps
			if (ogOpen == true) then
				renderSceneDialog.open()
		)

		-- -- THIS IS THE NEW STUFF
		-- for obj in objects where obj.modifiers[1] != undefined and obj.modifiers[1].name == "MXS Time Control" do
		-- (
		-- 	timeMod = obj.modifiers[1]
		-- 	frameNum = int(sliderTime)
		-- 	baseName = substring obj.mxsFile 1 (obj.mxsFile.count - 8)
		-- 	timeRange = timeMod.end - timeMod.start
		-- 	paddedFrame = (mod frameNum timeRange) + timeMod.start + timeMod.offset
		-- 	paddedFrame = formattedPrint (int(paddedFrame)) format:"4.4d"
		-- 	obj.mxsFile = baseName + paddedFrame + ".mxs"
		-- 	print obj.mxsFile
		-- )
	)
	on btnCreateMXSReference pressed do
	(
		local file
		if (mxsSaveFile != undefined) then
		(
			file = mxsSaveFile
		)
		else
		(
			file = getMXSSaveFile()
		)
		if (file != undefined) then
		(
			-- fix: should name MXSRef based on file
			refObject = MXSRef lod:0 ShowViewportPreview:false
			refObject.mxsFile = file
		)
	)
)

createDialog MXSManager 240 128 style:#(#style_SysMenu, #style_ToolWindow)
)
