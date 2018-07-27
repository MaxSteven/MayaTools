--For any questions or concerns you might have just email me.
--// John Martini
--// JokerMartini@hotmail.com
--// http://www.JokerMartini.com
--// Hours Calculation - additional credit SwordSlayer
(
	try(destroyDialog rlFFXSim)catch()
			
--//Variables
	StartTime = undefined
	EndTime = undefined
	TotalHrs = undefined
	FFXObj = undefined
			
--//Functions
	fn FFXFilter obj = classof obj == FumeFX
		
	-- Hours Calculation - credit SwordSlayer	
	fn addDecimalPadding nr =
	(
		nr = if nr < 10 then ("0" + nr as string) else (nr as string)
	)
		
	-- Hours Calculation - credit SwordSlayer	
	fn dnFormatTime tm =
	(
		addDecimalPadding tm.Hours + ":" +
		addDecimalPadding tm.Minutes + ":" +
		addDecimalPadding tm.Seconds
	)
		
		
	-- Simulations Start	
	fn fnDefaultSim simobj = (
			if rlFFXSim.ckbxWaveSim.checked == true do (simObj.ExtraDetailType = 2) -- if needed Turn On Wavelet Turbulence before Default Sim
			simObj.selectedcache = 0
			simObj.runsimulation 0
		)	
	fn fnWaveletSim simobj = (
			simObj.selectedcache =0
			simObj.runsimulation 2
		)
	fn fnPostSim simobj = (
			if rlFFXSim.ckbxWaveSim.checked == true then (simObj.selectedcache = 1)else(simObj.selectedcache = 0)
			simObj.runsimulation 3
		)
		
		
	-- Simulations Continued
	fn fnDefaultSimCont simobj = (
			if rlFFXSim.ckbxWaveSim.checked == true do (simObj.ExtraDetailType = 2) -- if needed Turn On Wavelet Turbulence before Default Sim
			simObj.selectedcache = 0
			simObj.ContinueSimulation 0
		)	
	fn fnWaveletSimCont simobj = (
			simObj.selectedcache =0
			simObj.ContinueSimulation 2
		)
	fn fnPostSimCont simobj = (
			if rlFFXSim.ckbxWaveSim.checked == true then (simObj.selectedcache = 1)else(simObj.selectedcache = 0)
			simObj.ContinueSimulation 3
		)
		
		
	--Render Simulation
	fn fnRenderSim simobj = (
			if rlFFXSim.ckbxWaveSim.checked == true then (simObj.selectedcache = 1)else(simObj.selectedcache = 0)
			render framerange:#active outputfile:rendoutputfilename	
		)
		
	fn fnRunSimulation simObj = (
		if simObj == undefined then	(messagebox "Pick FFX Container")
		else
		(
			StartTime = localTime as string -- TimeStampStart
			start_time = (dotNetClass "System.DateTime").Now -- Hours Caclulate Start
			if rlFFXSim.ckbkDefaultSim.checked == true do (fnDefaultSim simObj)-- Deafult Sim
			if rlFFXSim.ckbxWaveSim.checked == true do (fnWaveletSim simObj) -- Wavelet Sim
			if rlFFXSim.ckbxPostSim.checked == true do (fnPostSim simObj) -- Post Sim
			if rlFFXSim.ckbxRender.checked == true do (fnRenderSim simObj) -- Render Sim
			EndTime = localTime as string -- TimeStampEnd
			TotalHrs = dnFormatTime (((dotNetClass "System.DateTime").Now).Subtract start_time) -- Hours Caclulate End
			print (simObj.name + " = " + StartTime + " • " + EndTime)
			print (simObj.name + " = " + TotalHrs + " H/M/S ")
		)
	)
	
	fn fnContSimulation simObj = (
		if simObj == undefined then	(messagebox "Pick FFX Container")
		else
		(
			StartTime = localTime as string -- TimeStampStart
			start_time = (dotNetClass "System.DateTime").Now -- Hours Caclulate Start
			if rlFFXSim.ckbkDefaultSim.checked == true do -- Deafult Sim Cont
				(
					fnDefaultSimCont simObj
					if rlFFXSim.ckbxWaveSim.checked == true do (fnWaveletSim simObj)
					if rlFFXSim.ckbxPostSim.checked == true do (fnPostSim simObj)
					if rlFFXSim.ckbxRender.checked == true do (fnRenderSim simObj)
				)
			if (rlFFXSim.ckbxWaveSim.checked == true and rlFFXSim.ckbkDefaultSim.checked == false) do -- Wavelet Sim Cont
				(
					fnWaveletSimCont simObj
					if rlFFXSim.ckbxPostSim.checked == true do (fnPostSim simObj)
					if rlFFXSim.ckbxRender.checked == true do (fnRenderSim simObj)
				) 
			
			if (rlFFXSim.ckbxPostSim.checked == true and rlFFXSim.ckbxWaveSim.checked == false and rlFFXSim.ckbkDefaultSim.checked == false)do -- Post Sim Cont
				(
					fnPostSimCont simObj
					if rlFFXSim.ckbxRender.checked == true do (fnRenderSim simObj)
				) 
			EndTime = localTime as string -- TimeStampEnd
			TotalHrs = dnFormatTime (((dotNetClass "System.DateTime").Now).Subtract start_time) -- Hours Caclulate End
			print (simObj.name + " = " + StartTime + " • " + EndTime)	
			print (simObj.name + " = " + TotalHrs + " H/M/S ")	 
		)
	)
		
--//Rollout UI	
	rollout rlFFXSim "FumeFX Sim+"
	(
		groupbox gpbxFumeFX "FumeFX" pos:[9,6] width:150 height:52
		pickbutton myFumeFX "choose container" pos:[18,24] width:132 height:24 filter:FFXFilter
		groupbox gpbxSettings "" pos:[9,51] width:150 height:98
		checkbox ckbkDefaultSim "Default Simulation" checked:true pos:[18,66]
		checkbox ckbxWaveSim "Wavelet Simulation" checked:true pos:[18,86]
		checkbox ckbxPostSim "Post Simulation" checked:false pos:[18,106]
		checkbox ckbxRender "Render Simulation" checked:false pos:[18,126]
		button btnRunSim "Run Sim" pos:[9,158] width:75 height:24
		button btnContSim "Continue Sim" pos:[84,158] width:75 height:24
		
		on myFumeFX picked obj do
		(
			FFXObj = obj
			myFumeFX.text = FFXObj.name
		)
		
		on btnRunSim pressed do (fnRunSimulation FFXObj)
		
		on btnContSim pressed do (fnContSimulation FFXObj)
	)
	createdialog rlFFXSim 168 192
)