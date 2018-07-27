macroScript grindRender category:"Ingenuity" tooltip:"Grind Render" Icon:#("Ingenuity",13) silentErrors:hideErrors
(	
--// Globals
---------------------------------------------------
	global tempIEVFB
	
	
	
--//Variables
---------------------------------------------------
	local iniGrindRS = "$scripts/grindRenderSettings.ini"
		
	
	
--//Functions
---------------------------------------------------
	fn fnProcessGrindRenderer =
	(
		curRen = renderers.production
		theVRRenderer = Vray()
		vr = renderers.current
		re = maxOps.GetCurRenderElementMgr()
		theManager = maxOps.GetRenderElementMgr #Production
		
		orgElementsState = (re.GetElementsActive()) -- get original settings for render elements
		orgMotionBlurState = vr.moblur_on -- get original settings for motion blur
			
		--//Create settings ini file if it doesn't exist
		if not (doesFileExist iniGrindRS) then
		(
			fnSaveSettings 1
			
			)else(
			
			rendWidth = getINISetting iniGrindRS "RenderSettings" "Width"
			rendHeight = getINISetting iniGrindRS "RenderSettings" "Height"
			elementsActive = getINISetting iniGrindRS "RenderSettings" "Elements Active"
			motionBlurActive = getINISetting iniGrindRS "RenderSettings" "Motion Blur" 
		)
		
		if (classof curRen == classof theVRRenderer) do -- If Vray Frame buffer on then turn it off for test render then turn back on
		(
			vrVFB = curRen.output_on
			curRen.output_on = false
			
			if motionBlurActive == "True" then -- User decides whether or not to display elements
			(
				vr.moblur_on = true  --render Elements  
				)else(
				vr.moblur_on = false -- dont render elements
			)
		)
		
		if elementsActive == "True" then -- User decides whether or not to display elements
		(
			re.SetElementsActive true  --render Elements  
			)else(
			re.SetElementsActive false -- dont render elements
		)
		
		try(undisplay tempIEVFB)catch()
		tempIEVFB = bitmap 1 1
		display tempIEVFB		
		grindRender = render to:tempIEVFB frame:#current outputwidth:(rendWidth as integer) outputheight:(rendHeight as integer) vfb:true progressbar:true
		
		--//Reset render elements active settings 
		if (classof curRen == classof theVRRenderer) do (curRen.output_on = vrVFB)
		re.SetElementsActive orgElementsState 
		vr.moblur_on = orgMotionBlurState
	)
	
	fn fnPromptGrindRendererSettings = 
	(
		try(destroyDialog ::rlGrindRenderer)catch()
		rollout rlGrindRenderer " Grind Renderer Settings"
		(
			--//Functions
		---------------------------------------------------
			fn labelFactory ctrl txt = --//dotNet labels
			(
				local theLab = ctrl 
				theLab.Font = theFont
				theLab.BackColor = (dotNetClass "System.Drawing.Color").fromARGB 31 29 28
				theLab.ForeColor = (dotNetClass "System.Drawing.Color").fromARGB 255 255 255
				theLab.TextAlign = theLab.TextAlign.MiddleLeft
				theLab.Text = txt
				theLab
			)
			
			fn buttonFactory ctrl txt =
			(
				local theBut = ctrl
				theBut.Font = theFont
				theBut.flatStyle=theBut.flatStyle.flat
				theBut.flatAppearance.BorderSize = 1
				theBut.flatappearance.bordercolor = (dotNetClass "System.Drawing.Color").fromARGB 0 0 0
				theBut.BackColor = (dotNetClass "System.Drawing.Color").fromARGB 204 204 204
				theBut.ForeColor = (dotNetClass "System.Drawing.Color").fromARGB 0 0 0
				theBut.flatappearance.mouseoverbackcolor = (dotNetClass "System.Drawing.Color").fromARGB 204 204 204 --73 124 159 
				theBut.flatappearance.mousedownbackcolor = (dotNetClass "System.Drawing.Color").fromARGB 73 124 159 --238 137 34
				theBut.TextAlign = theBut.TextAlign.MiddleCenter
				theBut.Text = txt
				theBut
			)
			
			fn MasterFactory ctrl txt =
			(
				local theBut = ctrl
				theBut.Font = theFont
				theBut.flatStyle=theBut.flatStyle.flat
				theBut.flatAppearance.BorderSize = 1
				theBut.flatappearance.bordercolor = (dotNetClass "System.Drawing.Color").fromARGB 0 0 0
				theBut.BackColor = (dotNetClass "System.Drawing.Color").fromARGB 58 58 58 
				theBut.ForeColor = (dotNetClass "System.Drawing.Color").fromARGB 255 255 255
				theBut.flatappearance.mouseoverbackcolor = (dotNetClass "System.Drawing.Color").fromARGB 58 58 58 --73 124 159 
				theBut.flatappearance.mousedownbackcolor = (dotNetClass "System.Drawing.Color").fromARGB 73 124 159 --238 137 34
				theBut.TextAlign = theBut.TextAlign.MiddleCenter
				theBut.Text = txt
				theBut
			)
			
			fn cmbBoxFactory ctrl = --//dotNet dropdown lists
			(
				local theCtrl = ctrl
				theCtrl.DropDownStyle = theCtrl.DropDownStyle.DropDownList
				theCtrl.flatStyle=theCtrl.flatStyle.flat
				theCtrl.BackColor = (dotNetClass "System.Drawing.Color").fromARGB 204 204 204
				theCtrl.FlatStyle = theCtrl.FlatStyle.Flat 
				theCtrl.items.addrange #("True","False")
				theCtrl.SelectedIndex = 1
				theCtrl
			)
			
			fn spinnerFactory ctrl size = --//dotNet dropdown lists
			(
				local theLab = ctrl 
				theLab.Font = theFont
				theLab.BackColor = (dotNetClass "System.Drawing.Color").fromARGB 204 204 204
				theLab.ForeColor = (dotNetClass "System.Drawing.Color").fromARGB 0 0 0
				theLab.TextAlign = theLab.TextAlign.MiddleLeft
				local tmpSize = size as string
				theLab.Text = tmpSize
				theLab
			)
			
			fn fnSaveSettings val =
			(
				if val == 0 then
				(
					setINISetting iniGrindRS "RenderSettings" "Elements Active" (rlGrindRenderer.dlRenderElements.SelectedItem as string)
					setINISetting iniGrindRS "RenderSettings" "Motion Blur" (rlGrindRenderer.dlMotionBlur.SelectedItem as string)
					
					)else(--//Bypass previous settings and only save the checkbox settings
					
					setINISetting iniGrindRS "RenderSettings" "Width" ((RenderWidth/val) as string)
					setINISetting iniGrindRS "RenderSettings" "Height" ((RenderHeight/val) as string)
					setINISetting iniGrindRS "RenderSettings" "Elements Active" (rlGrindRenderer.dlRenderElements.SelectedItem as string)
					setINISetting iniGrindRS "RenderSettings" "Motion Blur" (rlGrindRenderer.dlMotionBlur.SelectedItem as string)
				)
				print "Saved Settings"
			)
			
			fn fnUpdateUI =
			(
				rlGrindRenderer.lbRendWidth.text = getINISetting iniGrindRS "RenderSettings" "Width"
				rlGrindRenderer.lbRendHeight.text = getINISetting iniGrindRS "RenderSettings" "Height"
			)
			
		--//UI Controls
		---------------------------------------------------	
			dotNetControl lbPresets "Label" pos:[0,0] width:110 height:21
			dotNetControl lbRenderWidth "Label" pos:[0,22] width:110 height:21
			dotNetControl lbRenderHeight "Label" pos:[0,44] width:110 height:21
			dotNetControl lbRenderElements "Label" pos:[0,66] width:110 height:21
			dotNetControl lbMotionBlur "Label" pos:[0,88] width:110 height:21
			
			dotNetControl btnFifth "button" pos:[111,0] width:30 height:21
			dotNetControl btnQuater "button" pos:[141,0] width:30 height:21
			dotNetControl btnThird "button" pos:[171,0] width:30 height:21
			dotNetControl btnHalf "button" pos:[201,0] width:30 height:21
			dotNetControl btnFull "button" pos:[231,0] width:30 height:21
			
			dotNetControl lbRendWidth "Label" pos:[111,22] width:150 height:21
			dotNetControl lbRendHeight "Label" pos:[111,44] width:150 height:21
			dotNetControl dlRenderElements "Combobox" pos:[111,66] width:150 height:21
			dotNetControl dlMotionBlur "Combobox" pos:[111,88] width:150 height:21
			
			dotNetControl btnGrindRenderClose "button" pos:[0,110] width:261 height:36
			
			on btnFull MouseClick e do 
			(
				fnSaveSettings 1
				fnUpdateUI()
			)
			on btnHalf MouseClick e do 
			(
				fnSaveSettings 2
				fnUpdateUI()
			)
			on btnThird MouseClick e do 
			(
				fnSaveSettings 3
				fnUpdateUI()
			)
			on btnQuater MouseClick e do 
			(
				fnSaveSettings 4
				fnUpdateUI()
			)
			on btnFifth MouseClick e do 
			(
				fnSaveSettings 5
				fnUpdateUI()
			)
			
			on dlRenderElements SelectionChangeCommitted e do (fnSaveSettings 0)
			
			on dlMotionBlur SelectionChangeCommitted e do (fnSaveSettings 0)
			
			on btnGrindRenderClose MouseClick e do
			(
				try(destroyDialog ::rlGrindRenderer)catch()
				fnProcessGrindRenderer()
			)
			
			on rlGrindRenderer open do
			(			
				--//Stylize the UI
				labelFactory lbPresets " Render Sizes:"
				labelFactory lbRenderWidth " Render Width:"
				labelFactory lbRenderHeight " Render Height:"
				labelFactory lbRenderElements " Render Elements:"
				labelFactory lbMotionBlur " Motion Blur:"
				buttonFactory btnFifth "1/5"
				buttonFactory btnQuater "1/4"
				buttonFactory btnThird "1/3"
				buttonFactory btnHalf "1/2"
				buttonFactory btnFull "1/1"
				cmbBoxFactory dlRenderElements
				cmbBoxFactory dlMotionBlur
				MasterFactory btnGrindRenderClose "Close and Render"
				spinnerFactory lbRendWidth renderWidth
				spinnerFactory lbRendHeight renderHeight
				
				--//Create settings ini file if it doesn't exist
				if not (doesFileExist iniGrindRS) do (fnSaveSettings 1)
				
				--//Adjust UI items to reflect existing settings
				lbRendWidth.text = getINISetting iniGrindRS "RenderSettings" "Width"
				lbRendHeight.text = getINISetting iniGrindRS "RenderSettings" "Height"
				dlRenderElements.SelectedItem = getINISetting iniGrindRS "RenderSettings" "Elements Active"
				dlMotionBlur.SelectedItem = getINISetting iniGrindRS "RenderSettings" "Motion Blur" 
			)
		)
		createDialog rlGrindRenderer 261 146 style:#(#style_SysMenu, #style_ToolWindow) 
	)


	
--//Actions
---------------------------------------------------
	if keyboard.shiftPressed then --//Prompt Grind Renderer Settings
	(
		fnPromptGrindRendererSettings()
		)else ( --//Process a temp Render
		fnProcessGrindRenderer()
	)
) 