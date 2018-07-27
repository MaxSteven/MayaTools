try (destroydialog ::rlReferenceManager)catch()
rollout rlReferenceManager "Reference Manager"
(
	struct SceneMaterial (mat, nodes = #())

	fn findbymat list mat = (for k=1 to list.count where list[k].mat == mat do exit with k)--Material saving
	fn fnWriteToFile file data = (for i = 1 to data.count do (format "%\n" (data[i]) to:file))
	fn diffArray a b = (
		retArray = #()
		for element in a do (
			idx = finditem b element
			if idx == 0 then
			append retArray element
		)
		return retArray
	)

	fn fnOutputMatData theMat selNodes = (--Material saving
		-- publishMatsDir = (pathConfig.removePathLeaf maxfilepath) + @"\MATERIALS\"
		matfileDir = (publishMatsDir + theMat.name)
		makeDir matfileDir all:true
		matfilePath = (matfileDir +"/"+ theMat.name + ".txt")

		if doesfileExist matfilePath then (
			outputFile = openFile matfilePath mode:"a+" --Read in file objects and append new ones
			local existingObjs = #()
			if outputFile != undefined do (
				while not eof outputFile do (
					inputData = readLine outputFile
					append existingObjs inputData
				)
			)
			selNodes = (diffArray selNodes existingObjs)
		) else (
			outputFile = createFile matfilePath
		)
		fnWriteToFile outputFile selNodes
		close outputFile

		--save mat file
		for itm = 1 to currentmateriallibrary.count do (deleteItem currentmateriallibrary 1) --clears mat library
		append currentmateriallibrary theMat --//add mat to new library
		saveMaterialLibrary (matfileDir +"/"+ theMat.name + ".mat")
	)

	fn fnPublishSelectedMats = (
		mats = #()

		for node in selection do (
			if (k = findbymat mats node.mat) != OK then append mats[k].nodes node.name
			else append mats (SceneMaterial mat:node.mat nodes:#(node.name))
		)
		clearlistener()

		for m in mats do (fnOutputMatData m.mat m.nodes)
	)

	checkbox cbCache "Cache" checked:false
	button btnPublish "Publish Selected" height:24 width:120
	button btnPublishMats "Publish Selected Mats" height:24 width:120

	fn CheckFor objArr classLevel:superClassOf classType:light = (
		for obj in objArr do
			if classLevel obj == classType do return false
		true
	)

	fn CacheAlembic filePath = (
		jobString = ("filename=" + filePath)
		jobString += ";in=0"
		jobString += ";out=30"
		jobString += ";step=1"
		jobString += ";substep=1"
		jobString += ";normals=true"
		jobString += ";uvs=true"
		jobString += ";materialids=true"
		jobString += ";bindpose=true"
		jobString += ";exportselected=true"
		jobString += ";flattenhierarchy=true"
		jobString += ";automaticinstancing=true"
		jobString += ";transformCache=false"

		result = ExocortexAlembic.createExportJobs(jobString)
	)

	fn fnExportSelected = (
		curSel = getCurrentSelection()
		if curSel.count >= 1 do (
			--FILEPATH
			filename = getFilenameFile maxFilename
 			-- publishDir = (pathConfig.removePathLeaf maxfilepath) + @"\PUBLISHED\"
			filenamePath = publishDir + filename
			local _theFile = "" --used to test if file was created
			makeDir publishDir

			--PUBLISHING METHODS
			if cbCache.state then ( --CACHE
				_theFile = (filenamePath + ".abc")

				noLights = CheckFor curSel classType:Light
				noFumeFX = CheckFor curSel classLevel:classOf classType:FumeFX

				if noLights AND noFumeFX then (
						CacheAlembic _theFile
					)else(
						messagebox "Incompatible objects for caching."
				)
			)else( --SAVING
				_theFile = (filenamePath + ".max" )
				saveNodes curSel _theFile
			)

			publishStatus = if doesFileExist _theFile then "Success!" else "Failure!"
			displayTempPrompt ("Publishing of '"+ filename +"' was a " + publishStatus) 3000
		)
	)

	on btnPublish pressed do (fnExportSelected())
	on btnPublishMats pressed do (fnPublishSelectedMats())
)
createDialog rlReferenceManager 150 style:#(#style_SysMenu, #style_ToolWindow)
