(
	global
		particlesToSplines,
		particlesToSplinesFN,
		particlesToSplines_ss;
	
	fn particlesToSplinesFN pId = (
		try(
			myTime = ((currentTime as integer)/ticksPerFrame)+1
			( getKnotPoint particlesToSplines_ss pId myTime )
		)catch([0,0,0])
	)

	try(destroyDialog particlesToSplines)catch()
	rollout particlesToSplines "ParticlesToSplines" width:160 height:48
	(
		
		button p2s_btn "Particles to Splines" pos:[8,8] width:144 height:32
		
		on p2s_btn pressed do
		(
			mySel = (getCurrentSelection())
			if mySel.count > 0 AND classof mySel[1] == PF_Source then
			(
				myPFlow = mySel[1]
				particlesToSplines_ss = SplineShape()
				particlesToSplines_ss.name = "Splines_"+myPFlow.name
				particlesToSplines_ss.transform = myPFlow.transform
				particlesToSplines_ss.wirecolor = myPFlow.wirecolor
				
				ParticleIds = #()
				for t=animationRange.start to animationRange.end do
				(
					sliderTime = t
					for pIndex=1 to myPFlow.numParticles() do
					(
						myParticleId = myPFlow.getParticleID pIndex
						isNew = appendIfUnique ParticleIds myParticleId
						if isNew then (
							addNewSpline particlesToSplines_ss
							for t2 = animationRange.start to sliderTime do ( addKnot particlesToSplines_ss myParticleId #corner #line (myPFlow.getParticlePositionByID myParticleId) )
						)else
						(
							addKnot particlesToSplines_ss myParticleId #corner #line (myPFlow.getParticlePositionByID myParticleId)
						)
					)
				)
				updateShape particlesToSplines_ss
				
				
				myTxt = "on ChannelsUsed pCont do\n"
				myTxt += "(\n"
				myTxt += "\tpCont.usePosition = true\n"
				myTxt += "\tpCont.useTime = true\n"
				myTxt += "\tpCont.useEventTime = true\n"
				myTxt += ")\n"
				myTxt += "\n"
				myTxt += "on Init pCont do ()\n"
				myTxt += "\n"
				myTxt += "on Proceed pCont do \n"
				myTxt += "(\n"
				myTxt += "\tcount = pCont.NumParticles()\n"
				myTxt += "\n"
				myTxt += "\tfor pIndex=1 to count do\n"
				myTxt += "\t(\n"
				myTxt += "\t\tmyParticleId = pCont.getParticleID pIndex\n"
				myTxt += "\t\tmyPosition = particlesToSplinesFN myParticleId\n"
				myTxt += "\t\tpCont.setParticlePositionByID myParticleId myPosition\n"
				myTxt += "\t)\n"
				myTxt += ")\n"
				myTxt += "\n"
				myTxt += "on Release pCont do ()\n"
				
				setclipboardText myTxt
				
				messagebox "The script is copied to the clipboard"
			)
		)
	)
	createDialog particlesToSplines
)