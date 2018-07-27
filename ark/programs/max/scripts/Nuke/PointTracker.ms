--//-----------------------------------------------------------------------------
--// PointTracker.ms
--// By Grant Miller (grant.miller@Ingenuity.com)
--// v 1.0
--// Created On: 01/15/10
--// Modified On: 01/15/10
--// tested using Max 2010
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Required Files:
--// ieMax
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Description:
--// Transfers 3D points from 3dsMax to Nuke as Tracker3's
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
--// Revision History:
--//
--// v 1.00 Initial version
--// v 1.50 Resolution, Animation Range, Disabled Scene Redraw, Close Material Editor
--//-----------------------------------------------------------------------------

--//-----------------------------------------------------------------------------
(
--// Gloabls
	global pointTrackerRoll
	global pointTrackerFloater
	global saveFile
	global numElements
	global objs = #()
	
--//Variables
	imageType = ".exr"
	if (maxFileName != "") then
	(fileName = ieMaxStripFileExtension maxFileName)
	else
	(
	  messageBox "Please save your max file before using the Point Tracker Tool" title:"Invalid Max File Name"
	  return false
	)
	renderRoot = maxFilePath + "\\renders\\" + fileName + "\\"
	re = maxOps.GetCurRenderElementMgr()
	tCenter = point2 12 8

--Rollout Ui
	rollout rlMaxNukePT "Max-Nuke PT"
	(
		groupbox gpbxGeneralParameters "Objects To Track" width:160 height:220 pos:[10,6]
		listbox lbxObjs "" pos:[19,28] width:140 height:12
		button btnAddObjs "+" pos:[19,190] width:47 height:24
		button btnRemoveObjs "-" pos:[66,190] width:46 height:24
		button btnClearObjs "Clear" pos:[112,190] width:47 height:24
		groupbox gpbxResolution "Resolution" width:160 height:67 pos:[10,230]
		label lbWidth "Width:" pos:[19,250]
		label lbHeight "Height:" pos:[19,270]
		spinner spnRenWidth "" range:[1,32768,RenderWidth] fieldwidth:55 type:#integer pos:[92,250]
		spinner spnRenHeight "" range:[1,32768,RenderHeight] fieldwidth:55 type:#integer pos:[92,270]
		groupbox gpbxAnimRange "Animation Range" width:160 height:67 pos:[10,300]
		label lbAnimStart "Start:" pos:[19,320]
		label lbAnimEnd "End:" pos:[19,340]
		spinner spnStartTime "" range:[-9999999,9999999,animationrange.start] fieldwidth:55 type:#integer pos:[92,320]
		spinner spnEndTime "" range:[-9999999,9999999,animationrange.end] fieldwidth:55 type:#integer pos:[92,340]
		button btnGenerateNuke "Generate Nuke Script" pos:[10,374] width:136 height:24
		button btnNukeClipboard "©" width:24 height:24 pos:[146,374]
		button btnAETrack "AE Track -> Clipboard" pos:[10,398] width:160 height:24
		
		fn getTrackingData objs animOffset app =
		(
			oSliderTime = sliderTime
			local objectPositions = #()
			
			for t = (spnStartTime.value + animOffset) to (spnEndTime.value + animOffset) do
			for o in objs do (append objectPositions #())
			
			for t = (spnStartTime.value + animOffset) to (spnEndTime.value + animOffset) do
			(
				sliderTime = t - animOffset
				for o = 1 to objs.count do
				(
					ptPos = objs[o].pos
					ptPos *= viewport.getTM()
					screenOrigin = mapScreenToView [0,0] (ptPos.z) [spnRenWidth.value, spnRenHeight.value]
					endScreen = mapScreenToView [spnRenWidth.value, spnRenHeight.value] ptPos.z [spnRenWidth.value, spnRenHeight.value]
					worldSize = screenOrigin - endScreen
					xAspect = spnRenWidth.value / (abs worldSize.x)
					yAspect = spnRenHeight.value / (abs worldSize.y)
					if (app == 1) then
					objectPositions[o][t] = point2 (xAspect * (ptPos.x - screenOrigin.x)) (spnRenHeight.value - (-(yAspect * (ptPos.y - screenOrigin.y))))
					else if (app == 2) then
					objectPositions[o][t] = point2 (xAspect * (ptPos.x - screenOrigin.x)) (-(yAspect * (ptPos.y - screenOrigin.y)))
				)
			)
			sliderTime = oSliderTime
			return objectPositions
		)
		
		on btnAddObjs pressed do
		(
			userSel = getCurrentSelection()
			for o in userSel do
			(
				append lbxObjs.items o.name
				lbxObjs.items = lbxObjs.items
				append objs o
			)
			persistent global jsPointTrackerObjs = deepcopy objs
		)
		
		on btnRemoveObjs pressed do 
		(
			local sel = lbxObjs.selection
			local arr2 = lbxObjs.items
			if sel != 0 then (deleteItem arr2 sel)
			lbxObjs.items = arr2
			
			objs = #()
			for i=1 to lbxObjs.items.count do
			(
				append objs (getNodeByName lbxObjs.items[i])
			)
			
			persistent global jsPointTrackerObjs = deepcopy objs
		)
		
		on btnClearObjs pressed do
		(
			objs = #()
			lbxObjs.items = #()
			lbxObjs.items = lbxObjs.items
			persistent global jsPointTrackerObjs = deepcopy objs
		)
		
		
		on btnGenerateNuke pressed do
		(
			MatEditor.Close()
			disableSceneRedraw()
			saveFilePath = getSaveFileName caption:"Save Nuke Script As..." filename:(maxFilePath + "PointTrack.nk") types:"Nuke Scripts(*.nk)|*.nk"
			if (saveFilePath != undefined) then
			(
				actualSaveFile = openFile saveFilePath mode:"wt"
				saveFile = stringStream ""
				format "Root {\n inputs 0\n name %\n frame %\n first_frame % last_frame % fps %" saveFilePath spnStartTime.value spnStartTime.value spnEndTime.value frameRate to:saveFile
				format " format \"% % 0 0 % % 1 \"\n" spnRenWidth.value spnRenHeight.value spnRenWidth.value spnRenHeight.value name to:saveFile
				format " proxy_type scale\n proxy_format \"640 480 0 0 640 480 1 PC_Video\"\n}\n" to:saveFile
				if (objs.count > 0) then
				(
					animOffset = 1 - spnStartTime.value
					objectPositions = getTrackingData objs animOffset 1
					for o = 1 to objs.count do 
					(
						trackStringX = ""
						trackStringY = ""
						for t = (spnStartTime.value + animOffset) to (spnEndTime.value + animOffset) do
						(
							trackStringX += (ieMaxPNum objectPositions[o][t].x) + " "
							trackStringY += (ieMaxPNum objectPositions[o][t].y) + " "
						)
						format "Tracker3 {\n inputs 0\n track1 {{curve i %} {curve i %}}\n translate {{curve i %} {curve i %}}\n center {% %}\n name %\n}\n" trackStringX trackStringY trackStringX trackStringY (tCenter.x) (tCenter.y) (objs[o].name) to:saveFile
					)
					format "%" (substituteString (saveFile as string) "\\" "/") to:actualSaveFile
					close actualSaveFile
					--setclipboardText (saveFile as string)
					close saveFile
					format "Tracker File Saved\n"
				)
				else
				(messageBox "Please add the objects you wish to track" title:"Nothing to Track")
			)
			enableSceneRedraw()
		)
		
		on btnNukeClipboard pressed do --copies trackers to clipboard
		(
			MatEditor.Close()
			disableSceneRedraw()
			saveFile = stringStream ""
			
			if (objs.count > 0) then
				(
					animOffset = 1 - spnStartTime.value
					objectPositions = getTrackingData objs animOffset 1
					for o = 1 to objs.count do 
					(
						trackStringX = ""
						trackStringY = ""
						for t = (spnStartTime.value + animOffset) to (spnEndTime.value + animOffset) do
						(
							trackStringX += (ieMaxPNum objectPositions[o][t].x) + " "
							trackStringY += (ieMaxPNum objectPositions[o][t].y) + " "
						)
						format "Tracker3 {\n inputs 0\n track1 {{curve i %} {curve i %}}\n translate {{curve i %} {curve i %}}\n center {% %}\n name %\n}\n" trackStringX trackStringY trackStringX trackStringY (tCenter.x) (tCenter.y) (objs[o].name) to:saveFile
					)
					setclipboardText (saveFile as string)
					close saveFile
					format "Tracking Data Copied to Clipboard.  Select your canvas in Nuke, (ctrl+v)\n"
				)
				else
				(messageBox "Please add the objects you wish to track" title:"Nothing to Track")
			enableSceneRedraw()
		)
		
		on btnAETrack pressed do
		(
			MatEditor.Close()
			disableSceneRedraw()
			saveFile = stringStream ""
			format "Adobe After Effects 8.0 Keyframe Data\n\n\tUnits Per Second\t%\n\tSource Width\t100\n\tSource Height\t100\n\tSource Pixel Aspect Ratio\t1\n\tComp Pixel Aspect Ratio\t1\n\nTransform\tPosition\n\tFrame\tX pixels\tY Pixels\tZ Pixels\n" frameRate to:saveFile
			
			if (objs.count > 0) then
			(
				animOffset = 1 - spnStartTime.value
				objectPositions = getTrackingData (#(objs[1])) animOffset 2
				for o = 1 to objs.count do 
				(
					trackString = ""
					for t = (spnStartTime.value + animOffset) to (spnEndTime.value + animOffset) do
					(
						--//          x = ieMaxPNum (ieMaxRound objectPositions[o][t].x)
						x =  ieMaxPNum objectPositions[o][t].x
						--//          y = ieMaxPNum (ieMaxRound objectPositions[o][t].y)
						y =  ieMaxPNum objectPositions[o][t].y
						trackString += "\t" + (t as string) + "\t" + x + "\t" + y + "\t0\n"
					)
					format "%\nEnd of Keyframe Data\n" trackString to:saveFile
				)
				setclipboardText (saveFile as string)
				close saveFile
				format "Tracking Data Copied to Clipboard.  Select your layer in After Effects, press P and then Paste (ctrl+v)\n"
			)
			enableSceneRedraw()
		)
  
		on pointTrackerRoll open do
		(
			if (jsPointTrackerObjs != undefined) then
			(
				objs = #()
				objs = for o in jsPointTrackerObjs where isValidNode o collect o
				for o in objs do append lbxObjs.items o.name
				lbxObjs.items = lbxObjs.items
			)
		)
		
		on rlMaxNukePT close do
		(
			persistent global jsPointTrackerObjs = deepcopy objs
		)
	)
	createDialog rlMaxNukePT 180 432
)