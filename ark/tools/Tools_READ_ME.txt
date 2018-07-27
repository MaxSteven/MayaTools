'''
Author: Carlo Cherisier
Date 10/27/14
Tools
'''


# Smart Tools #

Objective: Allow users to open and save files faster, with proper naming conventions.

	smartOpen- allows user to quickly open files using Max and Maya; and eventually Houdini and Nuke. The tool uses reads in the Project folders located on the R:/ drive, then from the selected Department (Model, Rig, Lighting Asset, FX Asset, Anim, Lighting Scene, FX Scene) it lists each Asset/ Shot folder.

	When opening a file, the script will save out data within the scene file such as the Project name, Department name, Asset name, and the File name. This is so that the smartSave Tool will know where to save the file when called upon.

	smartSave- allows users to quickly save files using Max and Maya; and eventually Houdini and Nuke. The tools reads the data within an open scene to save the file in its proper location. Also, the script automatically versions up the file when saving and allows the users to leave notes to themselves or others when they want.

# Data Decoder #

Objective: Stores information such as smartOpen/ Save project path, published Assets, published camera settings, file notes, and Shot information: number Asset, their name, type, and version.


# Publish Tools #

Objective: Saves files in set folder location; allows all Artist to find and use the new Asset; allows Artist to update Assets; allows Artist to save out Asset animation and material; allows Artist to import (Max), reference (Maya), and remove an asset into a scene; allows users to export out Alembic, Max, Maya, and OBJ files out for any Asset.

	publishAsset- Allows users to save out an Alembic, Max, Maya, and/ or OBJ file out for any Asset. Save publishes in the Project/ Project_Assets/ Asset/ Published/ Department/ Version folder. Also, it store the information for all published Assets in the Project/ Data/ Department folder.

		To call script in Max:
			python.execute("
			import sys;
			sys.path.append('c:/ie/ark/tools/publishTools');
			import publishAsset; publishAsset.main();
			")

		To call script in Maya:
			import sys
			sys.path.append('c:/ie/ark/tools/publishTools')
			import publishAsset
			reload( publishAsset)
			publishAsset.main()

	importAsset- Allows users to import/ reference Assets into their scene. They have the option of bringing in the HiRez, LowRez, BoundingBox, Vray Proxy, or Almebic file into the scene if it has been published.

		To call script in Max:
			python.execute("
			import sys;
			sys.path.append('c:/ie/ark/tools/publishTools');
			import importAsset; importAsset.main();
			")

		To call script in Maya:
			import sys
			sys.path.append('c:/ie/ark/tools/publishTools')
			import importAsset
			reload( importAsset)
			importAsset.main()


	publishAnimation- Allows users to save out the animation of a selected Asset in the scene.

		To call script in Max:
			python.execute("
			import sys;
			sys.path.append('c:/ie/ark/tools/publishTools');
			import publishAnimation; publishAnimation.main();
			")

		To call script in Maya:
			import sys
			sys.path.append('c:/ie/ark/tools/publishTools')
			import publishAnimation
			reload( publishAnimation)
			publishAnimation.main()

	publishCamera- Allows user to save out selected camera information (such as animation and setting properties). Also, it converts Vray cameras into Max or Maya camera with the proper settings applied.

		To call script in Max:
			python.execute("
			import sys;
			sys.path.append('c:/ie/ark/tools/publishTools');
			import publishCamera; publishCamera.main();
			")

		To call script in Maya:
			import sys
			sys.path.append('c:/ie/ark/tools/publishTools')
			import publishCamera
			reload( publishCamera)
			publishCamera.main()

	publishMaterial- Allows users to save and load Multi-Sub materials on a selected Asset. It will place the published materials in the Project/ Project_Assets/ Asset/ Published/ Material folder.

		To call script in Max:
			python.execute("
			import sys;
			sys.path.append('c:/ie/ark/tools/publishTools');
			import publishMaterial; publishMaterial.main();
			")

		To call script in Maya:
			import sys
			sys.path.append('c:/ie/ark/tools/publishTools')
			import publishMaterial
			reload( publishMaterial)
			publishMaterial.main()

	viewAsset- Allows users to view all the published Assets in a scene. From this tool one can update an Asset, delete an Asset, select one or multiple Assets, and change the Asset Type from HiRez to LowRez or Vray Poxy, or Bounding Box.

		To call script in Max:
			python.execute("
			import sys;
			sys.path.append('c:/ie/ark/tools/publishTools');
			import viewAsset; viewAsset.main();
			")

		To call script in Maya:
			import sys
			sys.path.append('c:/ie/ark/tools/publishTools')
			import publishTools
			reload( publishTools)
			publishTools.viewAsset()


## Animation Library ##
Objective: Save animationand load animation out on any published Asset within

## Object








