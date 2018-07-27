-------------------------------------------------------------------------------
-- ieMax
-- By Grant Miller (blented@gmail.com)
-- v 1.1
-- Created On: 02/29/08
-- Modified On: 08/19/11
-- tested using Max 2012
-------------------------------------------------------------------------------
--
-------------------------------------------------------------------------------
-- Description:
-- A library of functions needed by the Ingenuity Scripts.
-------------------------------------------------------------------------------
--
-------------------------------------------------------------------------------
-- Revision History:
--
-- v 1.00 Initial version
--
-- v 1.01 Added ieMaxLog, ieMaxFormatNum, ieMaxCalcBBCenter, ieMaxCalcBoundingBox,
-- 				ieMaxValidateNodes, ieMaxMin, ieMaxMax
--
-- v 1.02 Added ieMaxGetCharBox, ieMaxOverlayString
--
-- v 1.03 Added ieMaxSetProp, ieMaxGetProp, ieMaxSaveArray,
-- 				ieMaxLoadArray, ieMaxSaveString, ieMaxLoadString, ieMaxIsGeometry
--
-- v 1.04 Added ieMaxMakeBB, ieMaxRound, ieMaxAttach, ieMaxGetModifier
--
-- v 1.05 Fixed a few issues with 3ds Max 2009, also some bugs w/
--				various functions that cropped up post-E-Day
--
-- v 1.06 Added ieMaxFreezeTM, ieMaxExplodeByElement, ieMaxGetSplineMatrix
--
-- v 1.10 Added loads of stuff, moved to Ingenuity
--
-------------------------------------------------------------------------------
--
-------------------------------------------------------------------------------
-- Initialization Start (disabled during development)
-------------------------------------------------------------------------------
global ieMaxInit
--if ieMaxInit != true then
(

-------------------------------------------------------------------------------
-- Globals
-------------------------------------------------------------------------------

-- Files
global ieMaxSaveArray
global ieMaxLoadArray
global ieMaxSaveString
global ieMaxLoadString
global ieMaxGetAllFilesInDir
global ieMaxGetAllFilesInDirRecursive
global ieMaxStripFileExtension
global ieMaxStripSpaces
global ieMaxUnitSetup
global ieMaxGetMatRefFile
global ieMaxBaseFilename
global ieMaxForwardSlashes
global ieMaxExecuteCommand

-- Nodes
global ieMaxCopyUserSelection
global ieMaxValidateNodes
global ieMaxCalcBoundingBox
global ieMaxCalcBBCenter
global ieMaxMakeBB
global ieMaxIsGeometry
global ieMaxIsCharacter
global ieMaxYawNode
global ieMaxSetProp
global ieMaxGetProp
global ieMaxGetPropCount
global ieMaxGetPropNames
global ieMaxDumpPropNames
global ieMaxDeleteProp
global ieMaxClearProp
global ieMaxPivotToCenter
global ieMaxPivotToObjCenter
global ieMaxPivotToObjPivot
global ieMaxGetModifier
global ieMaxFreezeTM
global ieMaxGetSplineMatrix
global ieMaxSelectNodeByName
global ieMaxGetNodesByName

-- Strings
global ieMaxReverseString
global ieMaxLog
global ieMaxGetCharBox
global ieMaxOverlayString
global ieMaxFormatNum
global ieMaxStringToArray
global ieMaxArrayToString
global ieMaxParseDateTime
global ieMaxLaterDate
global ieMaxMakeDateString
global ieMaxPNum
global ieMaxJoinArray

--Arrays
global ieMaxArraySlice

--Layers
global ieMaxGetLayer

-- Constraints
global ieMaxMultiLink

-- Creation
global ieMaxRootDummy
global ieMaxMakeCam

-- Math
global ieMaxMin
global ieMaxMax
global ieMaxAverage
global ieMaxAvgArray
global ieMaxFloatToInt
global ieMaxRound

-- Modeling
global ieMaxAttach
global ieMaxExplodeByElement

-- Rigging
global ieMaxGetRoot
global ieMaxGetChildren
global ieMaxGetFullHierarchy

-- Studio
global ieMaxGetProjectRoot
global ieMaxGetWorkspaceRoot
global ieMaxGetWorkspace
global ieMaxGetUserInitials
global ieMaxGetPublishDir
global ieMaxRemoveXRefScenes

-- Rendering
global ieMaxIsRenderDialogOpen = false
global ieMaxIsVRayCurrent
global ieMaxIsMaxwellCurrent
global ieMaxGetRenderFrameRange
global ieMaxPreSubmit
global ieMaxPostSubmit

-------------------------------------------------------------------------------
-- Varibles
-------------------------------------------------------------------------------
targetSystemScale = 10
targetUnitType = #Centimeters

-------------------------------------------------------------------------------
-- Files
-------------------------------------------------------------------------------
fn ieMaxLoadArray fileName =
	(
		loadedArray = #()
		filePath = (getdir #scripts) + "\\Ingenuity\\config\\" + fileName
		readFile = openFile filePath mode:"r"
		if (readFile != undefined) then
		(
			while (not eof readFileyou ) do
			(
				data = readLine readFile
				append loadedArray data
			)
			close readFile
		)
		return loadedArray
	)
fn ieMaxSaveArray fileName arrayToSave =
	(
		filePath = (getdir #scripts) + "\\Ingenuity\\config\\" + fileName
		saveFile = openFile filePath mode:"w+"
		if (saveFile == undefined) then
			saveFile = createFile filePath

		for i in arrayToSave do
			format (i + "\n") to:saveFile

		close saveFile
	)
fn ieMaxLoadString fileName =
	(
		loadedArray = #()
		filePath = (getdir #scripts) + "\\Ingenuity\\config\\" + fileName
		readFile = openFile filePath mode:"r"
		if (readFile != undefined) then
		(
			return readLine readFile
			close readFile
		)
		return ""
	)
fn ieMaxSaveString fileName stringToSave =
	(
		filePath = (getdir #scripts) + "\\Ingenuity\\config\\" + fileName
		saveFile = openFile filePath mode:"w+"
		if (saveFile == undefined) then
			saveFile = createFile filePath

		format (stringToSave + "\n") to:saveFile
		close saveFile
	)
fn ieMaxGetAllFilesInDir startDir recursive type =
	(
		fileList = #()
		ieMaxGetAllFilesInDirRecursive startDir rec type fileList
		return fileList
	)
fn ieMaxGetAllFilesInDirRecursive startDir recursive type fileList =
	(
		currentFiles = getFiles (startDir + "*." + (type as string))
		for file in currentFiles do append fileList file
		if recursive == true then
		(
			subDirs = getDirectories (startDir + "*.*")
			for file in subDirs do ieMaxGetAllFilesInDirRecursive file recursive type fileList
		)
	)
fn ieMaxStripFileExtension fileName =
	(
--		reversed to ensure we find the last "." since you can have multiple dots in a filename
		fileName = ieMaxReverseString fileName
		locationOfCut = findString fileName "."
		fileNameReversed = substring fileName (locationOfCut + 1) fileName.count
		return ieMaxReverseString fileNameReversed
	)
fn ieMaxStringToArray str =
	(
		strArray = #()
		strArray = for i = 1 to str.count collect str[i]
		return strArray
	)
fn ieMaxArrayToString ary =
	(
		aryString = ""
		for a in ary do aryString += (a as string)
		return aryString
	)
fn ieMaxStripSpaces spacedString =
	(
		return substituteString spacedString " " ""
	)
fn ieMaxUnitsetup =
	(
		units.SystemScale = targetSystemScale
		units.SystemType = targetUnitType
		units.DisplayType = #Metric
		units.MetricType = #Meters
		gridPrefs.spacing = 1
	)
fn ieMaxGetMatRefFile xrefFile:false =
	(
		--if we've passed an xref filename then build the filePath and fileName from that
		if xrefFile != false then
		(
			fileParts = filterString xrefFile "\\"
			filePath = ieMaxJoinArray (ieMaxArraySlice fileParts 1 -1) "\\"
			fileName = fileParts[fileParts.count]
		)
		--otherwise get them from the current max file
		else
		(
			filePath = maxFilePath
			fileName = maxFileName
		)
		matFileDir = (ieMaxJoinArray (ieMaxArraySlice (filterString filePath "\\") 1 -1) "\\") + "MATERIALS\\"
		if (not isDirectoryWriteable matFileDir) then
			makeDir matFileDir all:true
		fileNameParts = filterString fileName "_."
		return matFileDir + fileNameParts[1] + "_mat.max"
	)
fn ieMaxBaseFilename filename =
	(
		fileParts = filterString filename "\\."
		return fileParts[fileParts.count-1]
	)

fn ieMaxForwardSlashes filename =
	(
		return (substituteString filename "\\" "/")
	)


fn ieMaxExecuteCommand command =
	(
		print "Command:"
		print command
		print ("execute " + command)
		result = execute command
		f = openFile (MAX_TOOLS_ROOT + "temp/maxResult.txt") mode: "w"
		format "%" result to:f
		close f
	)

-------------------------------------------------------------------------------
-- Nodes
-------------------------------------------------------------------------------
--change this to use getCurrentSelection() at some point
fn ieMaxCopyUserSelection =
	(
		return getCurrentSelection()
	)

fn ieMaxValidateNodes nodeList=
	(
		cleanList = deepCopy nodeList
		deletedCount = 0
		for i = 1 to nodeList.count do
		(
			if not (IsValidNode nodeList[i]) then
			(
				deleteItem cleanList (i - deletedCount)
				deletedCount += 1
			)
		)
		return cleanList
	)

fn ieMaxCalcBoundingBox bbObjects =
	(
		userSel = getCurrentSelection()
		bbDim = [0,0,0]
		select bbObjects
		selectionMin = $.min
		selectionMax = $.max
		bbDim.x = abs (selectionMin.x - selectionMax.x)
		bbDim.y = abs (selectionMin.y - selectionMax.y)
		bbDim.z = abs (selectionMin.z - selectionMax.z)
		select userSel

		return bbDim
	)

fn ieMaxCalcBBCenter bbObjects =
	(
		objs = getCurrentSelection()
		bBox = box()

		objMin = $.min
		objMax = $.max

		boxX = (objMin.x + objMax.x) * .5
		boxY = (objMin.y + objMax.y) * .5
		boxZ = objMin.z

		bBox.pos = [boxX, boxY, boxZ]

		bBox.width = objMax.x - objMin.x
		bBox.length = objMax.y - objMin.y
		bBox.height = objMax.z - objMin.z

		return bBox
	)

fn ieMaxMakeBB bbObjects =
	(
		userSel = getCurrentSelection()
		bbCenter = ieMaxCalcBBCenter bbObjects
		bBox = convertToPoly(Box pos:bbCenter widthsegs:1 heightsegs:1  width:0 height:0 length:0 isSelected:off)
		ieMaxPivotToCenter bBox
		select bbObjects
		bbMin = $.min
		bbMax = $.max

		ieMaxLog "bbObjects" bbObjects
		ieMaxLog "bbMin" bbMin
		ieMaxLog "bbMax" bbMax

		select bBox

	--		move box faces: 1 z min	2 z max	3 y min	4 x max	5 y max	6 x min
		$.EditablePoly.SetSelection #Face #{1}
		move $.selectedFaces [0,0,bbMin.z - bbCenter.z]

		$.EditablePoly.SetSelection #Face #{2}
		move $.selectedFaces [0,0,bbMax.z - bbCenter.z]

		$.EditablePoly.SetSelection #Face #{4}
		move $.selectedFaces [bbMax.x - bbCenter.x,0,0]

		$.EditablePoly.SetSelection #Face #{6}
		move $.selectedFaces [bbMin.x - bbCenter.x,0,0]

		$.EditablePoly.SetSelection #Face #{3}
		move $.selectedFaces [0,bbMin.y - bbCenter.y,0]

		$.EditablePoly.SetSelection #Face #{5}
		move $.selectedFaces [0,bbMax.y - bbCenter.y,0]

		return bBox
	)

fn ieMaxIsGeometry obj =
	(
--		geometry isn't hidden or frozen
--		it doesn't have a parent or children either because that's what bones have and nobody likes bones
		if (not isValidNode obj) then return false
		return (not obj.isHidden and \
						not obj.isFrozen and \
						superClassOf obj == GeometryClass and \
						obj.parent == undefined and \
						obj.children.count == 0)
	)

fn ieMaxIsCharacter obj =
	(
		for m = 1 to obj.modifiers.count do
		(
			if (obj.modifiers[m].name == "Skin") then
				return true
		)
		return false
	)

fn ieMaxYawNode rootBone rotateAmount =
	(
		rotateDummy = ieMaxRootDummy()
		rootBone.parent = rotateDummy
		rotate rotateDummy (angleaxis rotateAmount [0,0,1])
		rootBone.parent = undefined --may be unnecessary
		delete rotateDummy
	)

fn ieMaxSetProp propHolder propName propValue =
	(
		propNode = getNodeByName propHolder
		if (propNode == undefined) then
		(
			propNode = ieMaxRootDummy()
			propNode.name = propHolder
			propNode.isHidden = true
			propNode.isFrozen = true
		)
		setUserProp propNode propName propValue
	)

fn ieMaxGetProp propHolder propName =
	(
		propNode = getNodeByName propHolder
		if (propNode != undefined) then
		(
			return getUserProp propNode propName
		)
		return undefined
	)

fn ieMaxGetPropCount propHolder =
	(
		propNode = getNodeByName propHolder
		if (propNode != undefined) then
		(
			propString = getUserPropBuffer propNode
			if (propString != "") then
			(
				propCount = 0
				newLineLoc = findString propString "\n"
				while (newLineLoc != undefined) do
				(
					propString = substring propString (newLineLoc+1) propString.count
					newLineLoc = findString propString "\n"
					propCount += 1
				)
				return propCount
			)
		)
		return 0
	)

fn ieMaxDumpPropNames propHolder =
	(
		propList = #()
		propNode = getNodeByName propHolder
		if (propNode != undefined) then
		(
			propString = getUserPropBuffer propNode
			if (propString != "") then
			(
				newLineLoc = findString propString "\n"
				while (newLineLoc != undefined) do
				(
					nameCut = (findString propString "=") - 2 --minus 2 because it's name = not name=
					append propList (substring propString 1 nameCut)
					propString = substring propString (newLineLoc+1) propString.count
					newLineLoc = findString propString "\n"
				)
			)
		)
		return propList
	)

fn ieMaxClearProp propHolder =
	(
		propNode = getNodeByName propHolder
		if (propNode != undefined) then	setUserPropBuffer propNode ""
	)

fn ieMaxDeleteProp propHolder propToDelete =
	(
		propNode = getNodeByName propHolder
		if (propNode != undefined) then
		(
			propNames = ieMaxDumpPropNames propHolder
			propValues = for n in propNames collect ieMaxGetProp propHolder n
			propIndex = findItem propNames propToDelete
			if (propIndex != 0) then
			(
				deleteItem propNames propIndex
				deleteItem propValues propIndex
				propString = ""
				for n = 1 to propNames.count do
					propString += propNames[n] + " = " + propValues[n] + "\n"
				ieMaxClearProp propHolder
				setUserPropBuffer propNode propString
			)
		)
	)
fn ieMaxPivotToCenter obj =
	(
		obj.pivot = ieMaxCalcBBCenter obj
	)
fn ieMaxPivotToObjCenter obj tarObj =
	(
		obj.pivot = ieMaxCalcBBCenter tarObj
	)
fn ieMaxPivotToObjPivot obj tarObj =
	(
		obj.pivot = tarObj.pivot
	)
fn ieMaxGetModifier obj modClass =
	(
		for m = 1 to obj.modifiers.count do
			if (classOf obj.modifiers[m] == modClass) then
				return m
--otherwise
		return undefined
	)

mapped fn ieMaxFreezeTM obj mode:#{1..2} =
	(
		if mode[1] then
		(
			local posList = position_List()
			obj.position.controller = posList
			posList[1].controller = position_xyz()
			posList[2].controller = position_xyz()
			posList.active = 2
			posList.setName 1 "Frozen Pos"
			posList.setName 2 "Zero Pos"
		)
		if mode[2] then
		(
			local rotList = rotation_List()
			obj.rotation.controller = rotList
			rotList[1].controller = euler_xyz()
			rotList[2].controller = euler_xyz()
			rotList.active = 2
			rotList.setName 1 "Frozen Rot"
			rotList.setName 2 "Zero Rot"
		)
		if mode[3] then
		(
			local scaleList = scale_List()
			obj.scale.controller = scaleList
			scaleList[1].controller = bezier_scale()
			scaleList[2].controller = bezier_scale()
			scaleList.active = 2
			scaleList.setName 1 "Frozen Scale"
			scaleList.setName 2 "Zero Scale"
		)
		return true
	)
fn ieMaxGetSplineMatrix obj sp k =
	(
		p1 = getKnotPoint obj sp k
		p2 = getOutVec obj sp k --out vector of p1 on the spline (tangent handle)
		p2 = p2 - p1 --vector from p1 to p2
		p2 = normalize p2
		pathMatrix = arbAxis p2 --matrix 3 with p2 as an up direction
		p = [p2.x,p2.y] --2D vector point at p2 from p1
		p = normalize p
		f = [0,-1]
		if (p.x < 0) then
			zRotate = -acos (f.x * p.x + f.y * p.y)
		else if (p.x > 0) then
			zRotate = acos (f.x * p.x + f.y * p.y)
		else
			zRotate = 1.5708
		zQuat = quat zRotate p2
		rotate pathMatrix zQuat
		return (translate pathMatrix p1)
	)
fn ieMaxSelectNodeByName n =
	(
		select (getNodeByName n)
	)
fn ieMaxGetNodesByName names =
(
	objs = #()
	if names != undefined then
	(
		for n in names do
		(
		o = getNodeByName n
		if (o != undefined) then
			append objs o
		)
	)
	return objs
)

-------------------------------------------------------------------------------
-- Strings
-------------------------------------------------------------------------------
fn ieMaxReverseString s =
	(
		newString = ""
		if s.count != 0 then
			for i = s.count to 1 by -1 do newString += s[i]
		return newString
	)
fn ieMaxLog logString logValue =
	(
		format (logString + ": " + "%\n") logValue
	)
fn ieMaxGetCharBox letter =
	(
		charString = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789,. "
		charArray = #()
		for c = 1 to charString.count do
			charArray[c] = charString[c]

		charIndex = findItem charArray letter
		return box2 ((charIndex-1)*14) 0 14 24
	)
fn ieMaxOverlayString startPoint overString overlayBitmap =
	(
		charSheet = openBitmap "$ui\icons\Ingenuity_font.tga"
		for c = 1 to overString.count do
		(
			charBox = ieMaxGetCharBox overString[c]
			pasteBitmap charSheet overlayBitmap charBox startPoint type:#blend
			startPoint.x += charBox.w
		)
		return overlayBitmap
	)
fn ieMaxFormatNum n digits =
	(
		numString = n as string
		numString = ieMaxReverseString numString
		locationOfCut = findString numString "."
		if (locationOfCut != undefined) then
			numString = substring numString (ieMaxMax 1 (locationOfCut - digits)) numString.count
		return ieMaxReverseString numString
	)
fn ieMaxParseDateTime timeToParse =
	(
--		returns a 6 element array with: month, day, year, military hours, minutes, seconds
		timeString = ieMaxStringToArray timeToParse
		sepPoint = #()
		for c = 1 to timeString.count do
			if (timeString[c] == "/" or timeString[c] == " " or timeString[c] == ":") then append sepPoint c

--		ensure the last one is always the end
		append sepPoint timeString.count

		timeString = timeToParse
		timeArray = #()
		timeArray[1] = (substring timeString 1 (sepPoint[1] - 1)) as integer
		for i = 1 to 5 do
			timeArray[i+1] = (substring timeString (sepPoint[i] + 1) (sepPoint[i+1] - sepPoint[i] - 1)) as integer

--		7th element should be \n, but 6th will be \n if no AM PM
		if (sepPoint[7] != undefined) then
		(
			amPM = substring timeString (sepPoint[6] + 1) timeString.count
			if (amPM == "PM") then timeArray[4] += 12
		)
		return timeArray
	)
fn ieMaxLaterDate dateOne dateTwo =
	(
--		returns true if date two is later than date one
		if (dateTwo[3] > dateOne[3]) then
			return true
		else if (dateTwo[3] == dateOne[3]) then
			if (dateTwo[1] > dateOne[1]) then
				return true
			else if (dateTwo[1] == dateOne[1]) then
				if (dateTwo[2] > dateOne[2]) then
					return true
				else if (dateTwo[2] == dateOne[2]) then
					if (dateTwo[4] > dateOne[4]) then
						return true
					else if (dateTwo[4] == dateOne[4]) then
						if (dateTwo[5] > dateOne[5]) then
							return true
						else if (dateTwo[5] == dateOne[5]) then
							if (dateTwo[6] > dateOne[6]) then
								return true

--		otherwise
		return false
	)
fn ieMaxMakeDateString dateToPrint =
	(
		d = deepCopy dateToPrint
		for i = 1 to 6 do
			if (d[i] < 10) then d[i] = "0" + (d[i] as string)

		return ((d[1] as string) + "/"  + (d[2] as string) + "/" + (d[3] as string) + " " + (d[4] as string) + ":" + (d[5] as string) + ":" + (d[6] as string))
	)
fn ieMaxPNum num =
(
--	if num is integer-ish return no decimals
	if num == (num as integer) then
	(
		return (formattedPrint (num as float) format:"0.0f")
	--	else return decimals w/ zeros trimmed
	)
	else
	(
		str = formattedPrint num format:"f"
		zeros = true
		end = str.count
		while zeros do
		(
			if ((substring str end 1) == "0") then
			(
				end -= 1
			)
			else if ((substring str end 1) == ".") then
			(
				end -= 1
				exit --get out of the loop so we don't turn 1000.000 into 1
			)
			else
			(
				zeros = false
			)
		)
	)
	return (substring str 1 end)
)
fn ieMaxJoinArray v delimeter =
(
	newString = ""
	for s in v do
		newString += s + delimeter
	return newString
)

-------------------------------------------------------------------------------
-- Arrays
-------------------------------------------------------------------------------
fn ieMaxArraySlice v start end =
(
	newArray = #()
	if (end < 1) then
		end = v.count + end
	for i = start to end do
		append newArray v[i]
	return newArray
)

-------------------------------------------------------------------------------
-- Layers
-------------------------------------------------------------------------------
fn ieMaxGetLayer layerName =
(
	namedLayer = LayerManager.getLayerFromName layerName
	if (namedLayer == undefined) then
		namedLayer = LayerManager.newLayerFromName layerName
	return namedLayer
)

-------------------------------------------------------------------------------
-- Constraints
-------------------------------------------------------------------------------
fn ieMaxMultiLink linkItems linkNode =
	(
		try
		(
			if (linkItems.count > 0) then
				for i in linkItems do i.parent = linkNode
		)
		catch
		(
			if (linkItems != undefined) then
				linkItems.parent = linkNode
		)
	)

-------------------------------------------------------------------------------
-- Creation
-------------------------------------------------------------------------------
fn ieMaxRootDummy bSize:10 =
	(
		return Dummy pos:[0,0,0] boxsize:[bSize,bSize,bSize] isSelected:off
	)
fn ieMaxMakeCam name pos targetDist fov orthographic =
	(
		Freecamera fov:fov orthoProjection:orthographic targetDistance:targetDist nearclip:1 farclip:10000 nearrange:0 farrange:10000 mpassEnabled:off mpassRenderPerPass:off pos:pos isSelected:off name:name
	)

-------------------------------------------------------------------------------
-- Math
-------------------------------------------------------------------------------
fn ieMaxMax one two =
	(
		if (one > two) then
			one
		else
			two
	)
fn ieMaxMin one two =
	(
		if (one > two) then
			two
		else
			one
	)
fn ieMaxAverage one two = (one + two) / 2.0
fn ieMaxAvgArray avgArray =
	(
		total = 0
		for i in avgArray do
			total += i
		if (total > 0) then return total /= avgArray.count
		else return undefined
	)
fn ieMaxFloatToInt floatNum =
	(
		floatString = floatNum as string
		cutLoc = findString floatString "."
		if (cutLoc != undefined) then return ((substring floatString 1 (cutLoc - 1)) as integer)
		cutLoc = findString floatString "f"
		if (cutLoc != undefined) then return ((substring floatString 1 (cutLoc - 1)) as integer)
		return undefined
	)
fn ieMaxRound floatNum =
	(
		ceilNum = ceil floatNum
		if (ceilNum - floatNum < 0.5) then return ceilNum
		return (floor floatNum)
	)

-------------------------------------------------------------------------------
-- Modeling
-------------------------------------------------------------------------------
fn ieMaxAttach	attachObjs =
	(
		deleteObjs = #()
		for o = 1 to attachObjs.count do
		(
			if (ieMaxIsGeometry attachObjs[o]) then
				Try(ConvertTo attachObjs[o] Editable_Poly)Catch(append deleteObjs o)
			else
				append deleteObjs o
		)

		ieMaxLog "attachObjs" attachObjs
		ieMaxLog "deleteObjs" deleteObjs

		i = 0
		for o in deleteObjs do
		(
			deleteItem attachObjs (o-i)
			i += 1
		)

		baseObj = attachObjs[1]

		for o = 2 to attachObjs.count do
			if (classOf attachObjs[o] == Editable_Poly) then
				baseObj.EditablePoly.attach attachObjs[o] baseObj

		select baseObj
	)
fn ieMaxExplodeByElement obj =
	(
		max modify mode
		curObj = modPanel.getCurrentObject()
		objClass = classof curObj
		if (objClass == Editable_Poly) then
		(
			while ((polyop.getNumFaces obj) > 0) do
				polyop.detachFaces obj (polyop.getElementsUsingFace obj 1) asNode:true name:(uniqueName obj.name) delete:true
			delete obj
		)
		else if (objClass == Edit_Poly) then
		(
			subObjectLevel = 4
			curObj.SetSelection #Face #{}
			while (curObj.getNumFaces() > 0) do
			(
				curObj.Select #Face #{1}
				curObj.convertSelection #Face #Element
				curObj.DetachToObject (uniqueName obj.name)
			)
			delete obj
		)
	)

-------------------------------------------------------------------------------
-- Rigging
-------------------------------------------------------------------------------

	fn ieMaxGetRoot node =
	(
		if isvalidnode node then
		(
			while node.parent != undefined do
				node = node.parent
			return node
		)
	)

	fn ieMaxGetChildren node =
	(
		local tmpArr = #()
		for c in node.children do
		(
			append tmpArr c
			join tmpArr (ieMaxGetChildren c)
		)
		tmpArr --omitting "return" is faster!
	)

	fn ieMaxGetFullHierarchy objs =
	(
		-- allows us to pass a single object or nothing at all
		if classof objs != Array then
			objs = #(objs)

		fullHierarchy = #()
		parents = makeUniqueArray (for o in objs collect (ieMaxGetRoot o))
		for p in parents do
		(
			fullHierarchy += ieMaxGetChildren p
			fullHierarchy += p
		)
		return fullHierarchy
	)

-------------------------------------------------------------------------------
-- Studio
-------------------------------------------------------------------------------
	fn ieMaxGetProjectRoot =
	(
		fileParts = filterstring maxFilePath "\\"
		projectRoot = ""
		if fileParts.count < 3 then
		(
			print "Please save your file first"
			return ""
		)
		for i = 1 to 2 do projectRoot += fileParts[i] + "\\"
		return projectRoot
	)

	fn ieMaxGetWorkspaceRoot =
	(
		fileParts = filterstring maxFilePath "\\"
		workspaceRoot = ""
		if fileParts.count < 4 then
		(
			print "Please save your file first"
			return ""
		)
		for i = 1 to 4 do workspaceRoot += fileParts[i] + "\\"
		return workspaceRoot
	)

	fn ieMaxGetWorkspace =
	(
		fileParts = filterstring maxFilePath "\\"
		workspaceRoot = ""
		if fileParts.count < 4 then
		(
			print "Please save your file first"
			return ""
		)
		return fileParts[4]
	)

	fn ieMaxGetUserInitials =
	(
		if maxFileName == "" then
			return "xxx"
		baseFilename = ieMaxStripFileExtension maxFileName
		splitName = filterString baseFilename "_"
		initials = splitName[splitName.count]
		if initials.count < 5 then
			return initials
		return "xxx"
	)

	fn ieMaxGetPublishDir =
	(
		workspaceRoot = ieMaxGetWorkspaceRoot()
		if workspaceRoot.count < 5 then
			return ""

		publishDir = workspaceRoot + "Publish\\"
		makeDir publishDir all:true

		return publishDir
	)

	fn ieMaxRemoveXRefScenes =
	(
		xrefCount = xrefs.getXRefFileCount()
		format "Removing scene references:\n"
		while xRefCount > 0 do
		(
			ref = xrefs.getXRefFile 1
			format (ref.filename + "\n")
			delete ref
			xrefCount -= 1
		)
	)

-- Rendering

	fn ieMaxIsVRayCurrent = matchPattern (renderers.production as string) pattern:"*V_RAY*"

	fn ieMaxIsMaxwellCurrent = matchPattern (renderers.production as string) pattern:"*Maxwell*"

	fn ieMaxGetRenderFrameRange =
	(
		return case rendTimeType of
		(
			1: (SliderTime.frame as integer) as string
			2: (animationrange.start.frame as integer)as string + "-" + (animationrange.end.frame as integer) as string
			3: ((rendStart.frame as integer)as string + "-" + (rendEnd.frame as integer) as string)
			4: rendPickupFrames
		)
	)

	fn ieMaxPreSubmit =
	(
		local curRenderer = renderers.production

		ieMaxIsRenderDialogOpen = renderSceneDialog.isOpen()
		if ieMaxIsRenderDialogOpen do
			renderSceneDialog.close()
		renderSceneDialog.update()

		-- store settings before modifying them
		originalRenderHeight = renderHeight
		originalRenderWidth = renderWidth

		-- fix: re-enable eventually
		-- add camera padding
		-- if spnPadding.value > 0 do
		-- (
		-- 	padVal = rlShepherd.spnPadding.value
		-- 	selCam = rlShepherd.dlRenderCam.selected --quick fix for camera variable
		-- 	renderCam = (AddRenderPadding selCam padVal)
		-- )

		for obj in objects where classof renderCam == FreeCamera or classof renderCam == Targetcamera do
			-- uncheck camera's multi-pass render effect
			obj.mpassEnabled = false

		-- Turn off environment maps in Environments & Effects dialog
		useEnvironmentMap = off
		-- Make environment background color be black
		backgroundColor = black

		-- VRay render settings
		if ieMaxIsVRayCurrent() do
		(
			rendSaveFile = false -- turn off max save output
			rendOutputFilename = "" -- clear max's render output path

			-- curRenderer.output_rawExrDeep = if cbEnableDeepEXR.checked then true else false --Vray DEEP EXR
			curRenderer.output_on = true --Enable Built-In Frame Buffer
			curRenderer.output_saveRawFile = true --Vray Raw Image File (Render to Vray raw Image File checkbox)
			curRenderer.output_useram = true --Render to Memory Frame buffer
			curRenderer.output_genpreview = true --Generate preview
			curRenderer.output_getsetsfrommax = true -- getResolution from max
			curRenderer.output_splitgbuffer = false -- checkbox split render channels save
			vrayVFBSetRegionEnabled(false) --disable render region
		)

		-- maxwell render settings
		if ieMaxIsMaxwellCurrent() do
		(
			rendSaveFile = false -- turn off max save output
			rendOutputFilename = "" -- clear max's render output path

			-- Render Channels
			curRenderer.rlDirectCausticsReflection = false
			curRenderer.rlDirectCausticsRefraction = false
			curRenderer.rlIndirectCausticsReflection = false
			curRenderer.rlIndirectCausticsRefraction = false
			curRenderer.gsChannelEmbedChannels = true
			curRenderer.gsChannelRGB = true
			curRenderer.gsChannelAlpha = true
			curRenderer.gsChannelShaddow = false
			curRenderer.gsChannelMaterialId = true
			curRenderer.gsChannelNormals = true
			curRenderer.gsChannelNormalsSpace = 0
			curRenderer.gsChannelPosition = true
			curRenderer.gsChannelPositionsSpace = 0
			curRenderer.gsChannelObjectId = true
			curRenderer.gsChannelCustomAlpha = true

			curRenderer.gsGenerateMXSOutput = true
			curRenderer.gsMaxwellSequenceRendering = true

			curRenderer.gsGenerateMXIOutput = true

			curRenderer.gsRenderer = 0 -- Production renderer, not Draft
			curRenderer.gsLowPriority = false
		)

		-- default render settings
		-- if (not ieMaxIsVRayCurrent()) AND (not ieMaxIsMaxwellCurrent()) do
		-- (
		-- 	rendSaveFile = true -- turn on max save output
		-- 	rendOutputFilename = outputFilePath
		-- )

		-- restore settings
		renderHeight = originalRenderHeight
		renderWidth = originalRenderWidth

		-- Delete camera if the job required that it create a new camera with padding
		-- if spnPadding.value > 0 do
		-- (
		-- 	local camNode = getNodeByName renderCam
		-- 	if isValidNode camNode do
		-- 	(
		-- 		delete camNode
		-- 	)
		-- )
	)

	fn ieMaxPostSubmit =
	(
		if ieMaxIsVRayCurrent() do
			-- Vray Raw Image File (Render to Vray raw Image File checkbox)
			renderers.current.output_saveRawFile = false

		if ieMaxIsRenderDialogOpen == true then
			renderSceneDialog.open()
	)

-------------------------------------------------------------------------------
-- Initialization End
-------------------------------------------------------------------------------
 format "ieMax v 2.0 has been loaded.\n"
 ieMaxInit = true
)
-------------------------------------------------------------------------------