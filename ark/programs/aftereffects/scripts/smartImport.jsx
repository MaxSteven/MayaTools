{
	/* 	I took the original Smart Import script from Adobe and modified it to be much more robust and to fit our workflow.
		Spencer Tweed, SMP, Nov 2015. Tested on AE CS6, on Windows.
		v0.2 Got recursive imports working, recognizing image sequences and such.
		v1.0 Recursive importing of all files in a folder structure, with a first iteration GUI. No real features yet.
		v1.1 Added "skip existing"
		v1.2 Added "FPS" and reworked "Skip existing" a bit. Also fixed bug where all imports were set to "skip existing"
	*/

	// Holders to be used later
	var filesToAdd = [];
	var specialComp = null;
	var specialLayer = null;

	function GetProjectChildItems (selectedFolder)
	{
		if (selectedFolder == null) {
			var myItems = app.project.items;
		} else {
			var myItems = selectedFolder.items;
		}

		// Recursion to step through all sub-folders and grab their childrens
		var itemsNameArray = [null];
		function HideYourKids (myItems, itemsNameArray) {
			
			for (var i = 0; i < myItems.length; i++) {

				if (myItems[i+1] instanceof FootageItem) {
					itemsNameArray[itemsNameArray.length] = myItems[i+1].name;
				}

				if (myItems[i+1] instanceof FolderItem) {
					HideYourKids(myItems[i+1].items, itemsNameArray);
				}
			}
		
			return itemsNameArray;
		}

		return HideYourKids(myItems, itemsNameArray);
	}

	function ST_SmartImport(baseFolder, targetFiles, skipExisting, FPS, selectedFolder, picInPic)
	{
		
		var i = 0;

		// We now can import multiple shots, so loop through them all
		for (i = 0; i < targetFiles.length; i++) {

			// Find plates folder
            var dir = baseFolder.toString();
            dir = dir + '/';
            dir = dir + targetFiles[i].toString();
            dir = dir + '/Plates';
			var targetFolder = Folder(dir);

			if (targetFolder != null) {
                // Reset holders
                filesToAdd = [];

                // For each shot imported, we need to make a layer, a comp, and a folder
                specialComp = null;
                specialLayer = null;
                specialFolder = null;
                
				function importSafeWithError(importOptions, selectedFolder)
				{
					try
					{
						// To be honest, I don't think you're allowed to NOT select a folder anymore
						if (selectedFolder != null)
						{
							if (skipExisting != true)
							{
								var importedFile = app.project.importFile(importOptions);

								importedFile.parentFolder = selectedFolder;
								importedFile.mainSource.conformFrameRate = FPS;
							}
							else
							{

								// skip existing. needs optomization
								var itemsNameArray = GetProjectChildItems(selectedFolder);
								var importedFile = app.project.importFile(importOptions);

								// thingamajig to see if this is already in the project.
								var n = -1, N = itemsNameArray.length;
								while (++n<N && itemsNameArray[n]!==importedFile.name);
								var doesItemExist = n<N ? n: -1;
								if (doesItemExist != -1)
								{
									//already exists, lets get rid of it. Not fast, but effective.
									importedFile.remove();
								}
								else
								{
									importedFile.parentFolder = selectedFolder;
									importedFile.mainSource.conformFrameRate = FPS;
								}
							}
						}
						else
						{
							// If we don't want to skip duplicate sequences
							if (skipExisting != true)
							{

								// Import each file
								importedFile = app.project.importFile(importOptions);
								importedFile.mainSource.conformFrameRate = FPS;



								// Search for offline sequence, use it as composition for the scene
								if (importedFile.name.search("_Offline") >= 0)
								{
									var currentName = importedFile.name;
									newName = currentName.replace("_Offline", "");
									importedFile.name = newName.substring(0, newName.indexOf('.'));

									var newComp = app.project.items.addComp(newName.substring(0, newName.indexOf('.')), importedFile.width, importedFile.height, importedFile.pixelAspect, importedFile.duration, FPS);
									newComp.layers.add(importedFile);
									specialLayer = newComp.layer(1);

									specialFolder = app.project.items.addFolder(newName.substring(0, newName.indexOf('.')))

									importedFile.parentFolder = specialFolder
									newComp.parentFolder = specialFolder

									var i;
									for (i = 0; i < filesToAdd.length; i++) {
										filesToAdd[i].parentFolder = specialFolder
										newComp.layers.add(filesToAdd[i]);
									}

									specialLayer.moveToBeginning();

									if (picInPic == true)
									{
										specialLayer.transform.position.setValue([512,270,0]);
										specialLayer.transform.scale.setValue([25,25,25]);
									}

									newComp.openInViewer();
									specialComp = newComp;

								}
								else
								{

									filesToAdd.push(importedFile);

									if (specialComp != null)
									{
										importedFile.parentFolder = specialFolder;
										specialComp.layers.add(importedFile);
										specialLayer.moveToBeginning();
									}
								}

							}
							else
							{
								// Skip existing. needs optomization
								var itemsNameArray = GetProjectChildItems(selectedFolder);
								var importedFile = app.project.importFile(importOptions);

								// thingamajig to see if this is already in the project.
								var n= -1, N = itemsNameArray.length;
								while (++n<N && itemsNameArray[n]!==importedFile.name);

								var doesItemExist = n<N ? n: -1;
								if (doesItemExist != -1)
								{
									//already exists, lets get rid of it. Not fast, but effective.
									//alert("Skipping: " + importedFile.name);
									importedFile.remove();

								}
								else
								{
									
									importedFile.mainSource.conformFrameRate = FPS;

									if (importedFile.name.search("_Offline") >= 0)
									{
										var currentName = importedFile.name;
										newName = currentName.replace("_Offline", "");
										importedFile.name = newName;

										importedFile.name = newName.substring(0, newName.indexOf('.'));
										var newComp = app.project.items.addComp(newName.substring(0, newName.indexOf('.')), importedFile.width, importedFile.height, importedFile.pixelAspect, importedFile.duration, FPS);
										newComp.layers.add(importedFile);
										specialLayer = newComp.layer(1);

										specialFolder = app.project.items.addFolder(newName.substring(0, newName.indexOf('.')));

										importedFile.parentFolder = specialFolder;
										newComp.parentFolder = specialFolder;

										var i;
										for (i = 0; i < filesToAdd.length; i++) {
											filesToAdd[i].parentFolder = specialFolder;
											newComp.layers.add(filesToAdd[i]);
										}

										specialLayer.moveToBeginning();

										if (picInPic == true)
										{
											specialLayer.transform.position.setValue([512,270,0]);
											specialLayer.transform.scale.setValue([25,25,25]);
										}

										newComp.openInViewer();
										specialComp = newComp;

									}
									else
									{

										filesToAdd.push(importedFile);

										if (specialComp != null)
										{
											importedFile.parentFolder = specialFolder;
											specialComp.layers.add(importedFile);
											specialLayer.moveToBeginning();
										}
									}
								}
							}
						}

					} catch (error) {
						alert(error.toString() + importOptions.file.fsName, scriptName);
					}
				}


				function processFolder(theFolder, selectedFolder)
				{
					// Make sure folder is sorted
					var files = theFolder.getFiles().sort();
                        
					// Prune the array for sequences
					var movieFileCheck = new RegExp("(mov|avi|mpg)$", "i");

					// Regex for seeing if we have at least 4 numbers in the file name
					var searcher = new RegExp("\\d{4,}"); 

					for (var i = 0; i < files.length; i++) {
						
						// Go through the array and strip out all elements that are the same once their numbers have been removed with a regex
						if (i > 0) {
							currentResult = searcher.exec(files[i].name); //check if a sequence
							if (currentResult) { // it is a sequence
								// first parse out hte comparison strings - current item and item before
								var testNameBefore = files[i-1].name;

								//if we have a sequence before our current item, we need to delete the numbers.
								var beforeNum = searcher.exec(testNameBefore);
								if (beforeNum) {
									var testNameBefore = testNameBefore.replace(beforeNum[0], "");	//remove the numbers from the file before
								}

								var testNameCurrent = files[i].name.replace(currentResult[0], "");	//remove the numbers from the current frame

								//compare to the element before it and delete if the same!!
								if (testNameBefore == testNameCurrent) {
									files.splice(i, 1);
									i--;
								}
							}
						}
					}

					//so now we import everything in the array. We check if it is a sequence, and if so we import it as such. If it is a folder, we recurse.
					for (index in files) {
						if (files[index] instanceof File) {
							//check for sequence
							var sequenceStartFile = searcher.exec(files[index].name);
							if (sequenceStartFile) {
								//alert("Importing as sequence: " + files[index].name);
								var importOptions = new ImportOptions(files[index]);
								importOptions.sequence = true;
								importSafeWithError(importOptions, selectedFolder);
							} else {
								//guess it wasn't a sequence!
								//alert("Importing: " + files[index].name);
								try {
									var importOptions = new ImportOptions(files[index]);
									importSafeWithError(importOptions, selectedFolder);
								} catch (error) {
									// Ignore errors.
								}
							}
						}
						if (files[index] instanceof Folder) {
							processFolder(files[index], selectedFolder); //recursion
						}
					}
				}

				processFolder(targetFolder, selectedFolder);
			}
		}
		
	}


	//---------------------------------------------------- BUILD THE UI ----------------------------------------------------\\
	var stSmartImportWin = new Window("palette", "ST Smart Importer");
		stSmartImportWin.orientation = "column";
		//stSmartImportWin.margins = [3,3,3,3];
		stSmartImportWin.border = [3,3,3,3];
		var groupOne = stSmartImportWin.add("group");
			groupOne.add("statictext", undefined, "Path:");
			var path = groupOne.add("edittext", [0,0,400,18]);
			groupOne.add("statictext", undefined, "FPS:");
			var FPS = groupOne.add("edittext", [0,0,35,18]);
				FPS.text = 23.976;

		var groupTwo = stSmartImportWin.add("group");
			groupTwo.orientation = "row";
			var folderviewer = groupTwo.add("ListBox", [0,0,400,300], [], {multiselect: true});

		var groupThree = stSmartImportWin.add("group");
			//var optionsPanel = groupTwo.add("panel", undefined, "Options");
			groupThree.orientation = "row";
			var smartSettingsChk = groupThree.add("checkbox", undefined, "Smart settings");
			var folderStructureChk = groupThree.add("checkbox", undefined, "Maintain folder structure");
			var skipExistingChk = groupThree.add("checkbox", undefined, "Skip existing");
			var picInPicChk = groupThree.add("checkbox", undefined, "Picture-in-Picture");

		var groupFour = stSmartImportWin.add("group");
			var chooseFolderBtn = groupFour.add("button", undefined, "Choose folder");
			var importBtn = groupFour.add("button", undefined, "Import!");

	//skipExistingChk.value = true;
	//skipExistingChk.enabled = false;
	folderStructureChk.enabled = false;
	smartSettingsChk.enabled = false;

	//-------| Event listeners
	chooseFolderBtn.onClick = function () {

		if (path.text == '') {
        	var targetFolder = Folder.selectDialog("Select Folder to Import From...");
        	var files = targetFolder.getFiles();
			files.sort()
			files.reverse()
        	var i = 0;
        	for (i = 0; i < files.length; i++) {
        		if (files[i] instanceof Folder) {
					var checker = 0;

        			var l = 0;
        			for (l = 0; l < folderviewer.items.length; l++) {
        				if (folderviewer.items[l].toString() == files[i].name.toString()) {
        					checker = 1;
        				}
        			}

        			if (checker == 0) {
	        			folderviewer.add("ITEM", files[i].name, 0);
        			}
        		}
        	}
        	targetFolder = targetFolder.toString().split("/");
        	targetFolder.pop();
        	targetFolder = targetFolder.join("/");
        	path.text = Folder.decode(targetFolder);

        } else {
        	var dir = Folder(path.text);
        	var files = dir.getFiles();
			files.sort()
			files.reverse()
        	var i = 0;
        	for (i = 0; i < files.length; i++) {
        		if (files[i] instanceof Folder) {
        			var checker = 0;

        			var l = 0;
        			for (l = 0; l < folderviewer.items.length; l++) {
        				if (folderviewer.items[l].toString() == files[i].name.toString()) {
        					checker = 1;
        				}
        			}

        			if (checker == 0) {
	        			folderviewer.add("ITEM", files[i].name, 0);
        			}
        		}
        	}
        }
	}

	importBtn.onClick = function () {
	     var baseFolder = new Folder(Folder.encode(path.text));
		var targetFiles = folderviewer.selection;
		ST_SmartImport(baseFolder, targetFiles, skipExistingChk.value, FPS.text, app.project.activeItem, picInPicChk.value);
		//stSmartImportWin.close();
	}

	stSmartImportWin.center();
	stSmartImportWin.show();
}
