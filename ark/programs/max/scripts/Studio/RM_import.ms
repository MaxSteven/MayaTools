(
	struct refData (xGroup,xIdx,xType,xObjName)
	REFDATA = refData()
 	REFDATA.xGroup = 3578691 --xCtrl name
 	REFDATA.xIdx = 3578692 --xCtrl group number
	REFDATA.xType = 3578693 --xCtrl type 'Master' or 'Child' used to filter objects when deleting
	REFDATA.xObjName = 3578694 --original name of the object before autoRenameDups is executed

	try (destroydialog ::rlReferenceManager)catch()
	rollout rlReferenceManager "Reference Manager"
	(
		-- local _elementDir = (pathConfig.removePathLeaf maxfilepath) + @"\PUBLISHED\"
		local _elementsPath = #()
		local _propsBank= #()
		struct propsSt (name,wirecolor,transform,material,ffx)

		button btnRefresh "Refresh" height:24 width:120
		multilistbox mlbElements "" height:10 width:120
		button btnReference "Import Selected" height:36 width:120
		button btnUpdateRefs "Update Selected" height:36 width:120
		group "Update Options" (
			checkbox cbTransforms "Transforms" checked:false
			checkbox cbMaterials "Materials" checked:false
			checkbox cbWirecolor "Wirecolor" checked:true
			checkbox cbFumeFX "FumeFX (Lights)" checked:false
		)

		fn fnUpdateList = (
-- 			clearlistener()
			_elementsPath = (getFiles (_elementDir + "*.max"))
			sort _elementsPath
			_elementsFileName = for f in _elementsPath collect filenameFromPath f
			mlbElements.items = _elementsFileName
		)

		fn fnSetAppData obj _refGrp _refIdx _refType _ObjName= (
			setappdata obj REFDATA.xGroup (_refGrp as string)
			setappdata obj REFDATA.xIdx (_refIdx as string)
			setappdata obj REFDATA.xType (_refType as string)
			setappdata obj REFDATA.xObjName (_ObjName as string)
		)


		fn fnResetToOrigin obj = (
			obj.pos = [0,0,0] --place the xGroup at origin
			obj.scale = [1,1,1]
			in coordsys (transmatrix obj.transform.pos) obj.rotation = (eulerangles 0 0 0)
		)

		fn fnImportObjects filepath:undefined grpName:undefined grpIdx:1 xCtrl:undefined = (
			if doesFileExist filepath do (
				refObjNames = getMAXFileObjectNames filepath
				mergeMaxFile filepath refObjNames #select #alwaysReparent #AutoRenameDups #renameMtlDups  quiet:true
				refNodes = getCurrentSelection()

				for o = 1 to refNodes.count do (
					obj = refNodes[o]
					orgName = refObjNames[o]
 					fnSetAppData obj grpName grpIdx "Child" orgName
 					if obj.parent == undefined do obj.parent = xCtrl
				)
				refNodes
			)
		)

		fn fnStoreUserOptions nodeArr = (
			--local _curTM = for o in curObjs collect #(o.name,o.transform.controller) --store objectName & transform controllers for current ref objects
			--if classof o == FumeFX do (append _propsBank (#(o.name, o.lights)))
			_propsBank =#()

			for o in nodeArr do (
				append _propsBank ( propsSt \
					name:(getappData o REFDATA.xObjName) \
					wirecolor:o.wirecolor \
					transform:o.controller \
					material:o.material \
					ffx:(if classof o == FumeFX then (o.lights as array) else undefined)
				)
			)
		)

		fn findItemByName items name = (
			for s in items where s.name == name do
				return s
			return undefined
		)

		fn fnCheckRigCtrls obj = (
			--if superclassof obj == Helper AND classof obj == IK_Chain_Object then (return false) else (return true)
			--format "%---%\n" (obj.name) (classof obj)
			--if classof obj == BoneGeometry OR classof obj == IK_Chain_Object OR obj.name == "R_Finger_Master_help" then (return false) else (return true)
			if classof obj == BoneGeometry OR classof obj == IK_Chain_Object then (return false) else (return true)
		)

		fn fnTransformTransfer o matching = ( --Fixes bug on objects that have controllers other than PRS or with constraints
			if classof matching.transform != classof o.controller then
			(
				--incoming controller type is different then the currently existing one do nothing
			)else(
				--incoming controller type matches previously existing one.
				if classof o.controller == PRS then  --sub controller checks, if passes then copy over the sub-controller
				(
					if classof o.controller[1].controller != Position_Constraint do (
						o.controller[1].controller = matching.transform[1]
					)
					if classof o.controller[2].controller != Orientation_Constraint AND classof o.controller[2].controller != Lookat_Constraint() do (
						o.controller[2].controller = matching.transform[2]
					)
					if classof o.controller[3].controller == ScaleXYZ do (
						o.controller[3].controller = matching.transform[3]
					)
				)else(
					o.controller = matching.transform
				)
			)
		)

		fn fnRestoreUserOptions nodeArr = (
			for o in nodeArr do (
				matching = findItemByName _propsBank (getappData o REFDATA.xObjName)

				/*WIRECOLOR*/
				if cbWirecolor.state AND matching != undefined do (o.wirecolor = matching.wirecolor)

				/*TRANSFORMS*/
				if cbTransforms.state AND matching != undefined AND (fnCheckRigCtrls o) do (fnTransformTransfer o matching)

				/*MATERIALS*/
				if cbMaterials.state AND matching != undefined do (o.material = matching.material)

				/*FUMEFX*/
				if classof o == FumeFX AND cbFumeFX.state AND matching.ffx != undefined do (
					for lite in matching.ffx do (
						o.AddLight lite
					)
				)
			)
		)

		fn fnReference method:#ImportRefs = (
			setCommandPanelTaskMode #create
			if mlbElements.selection.count >= 1 do with animate off (
				local toSel = #() --used to collect and select xRef controls

				for i in mlbElements.selection do (
					itm = i
					refFile = _elementsPath[itm] --files complete path ex. "Q:\\Projects\Avatar\Shot001\bunnies.max"
					refGroup = getFilenameFile _elementsPath[itm] -- group name ex. "Bunnies"

					if method == #ImportRefs do (
						--Calculate version number and create control for incoming objects
						ver = sort (for o in helpers where (getappData o REFDATA.xGroup) == refGroup collect (getappData o REFDATA.xIdx) as integer) --version numbers of active references in the scene
						verIdx = if ver.count !=0 then (ver[ver.count]+1) else 1
						theCtrl = point size:(units.decodevalue "75.00cm") name:("xCtrl::" + refGroup + "_" + verIdx as string) pos:[0,0,0] wirecolor:yellow centermarker:false axisTripod:false cross:true box:true constantScreenSize:false drawontop:false
						fnSetAppData theCtrl refGroup verIdx "Master" (theCtrl.name)

						refNodes = fnImportObjects filepath:refFile grpName:refGroup grpIdx:verIdx xCtrl:theCtrl

						append toSel theCtrl
					)--END ImportRefs Method


					if method == #UpdateRefs do (
						local ctrlsCOL = for o in helpers where (getappData o REFDATA.xGroup) == refGroup AND (getappData o REFDATA.xType) == "Master" collect o --collect all xGroup's matching selected list item

						for ctrl in ctrlsCOL do (--if there are multiple refs of the same item then loop through each one
							curIdx = getappData ctrl REFDATA.xIdx --current group idx in the loop
							curGroup = getappData ctrl REFDATA.xGroup --current group name in the loop
							curObjs = for o in objects where (getappData o REFDATA.xGroup) == curGroup AND (getappData o REFDATA.xIdx) == curIdx AND (getappData o REFDATA.xType) == "Child" collect o --get all the objects associated with this ref group and version exclude:xCtrl

							local orgCtrlTM = ctrl.transform
							fnResetToOrigin ctrl

							fnStoreUserOptions curObjs --STORE User Options
							delete curObjs --REMOVE OLD OBJECTS

							refNodes = fnImportObjects filepath:refFile grpName:curGroup grpIdx:curIdx xCtrl:ctrl

							fnRestoreUserOptions refNodes --RESTORE User Options
							ctrl.transform = orgCtrlTM --restore original transform to xCtrl

							append toSel ctrl
						)--END looping through controls
					)--END UpdateRefs Method

				)--END list selection looping
				select toSel
			)--END animate off
		)--END function


		on btnReference pressed do (fnReference method:#ImportRefs)
		on btnUpdateRefs pressed do (fnReference method:#UpdateRefs)

		on mlbElements doubleClicked idx do (
			with animate off (
				local toSel = #()
				refGroup = getFilenameFile _elementsPath[idx]-- group name ex. "Bunnies"
				toSel = for o in helpers where (getappData o REFDATA.xGroup) == refGroup collect o
				select toSel
			)
		)

		on btnRefresh pressed do (fnUpdateList())
		on rlReferenceManager open do (fnUpdateList())
	)
	createDialog rlReferenceManager 150 style:#(#style_SysMenu, #style_ToolWindow)
)