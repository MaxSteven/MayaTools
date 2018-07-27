cam = FreeCamera()
dataFile = openFile @"C:\ie\Temp\camera.txt" mode:"r"
if (dataFile != undefined) then
(
	with animate on
	(
		l = readLine dataFile
		cam.name = l
		while not (eof dataFile) do
		(
			l = readLine dataFile	
			data = filterString l " "
			for n = 1 to data.count do
				data[n] = data[n] as float
			at time data[1] cam.transform = matrix3 [ data[2],-data[10],data[6] ] [ data[3],-data[11],data[7] ] [ data[4],-data[12],data[8] ] [ data[5],-data[13],data[9] ]
			at time data[1] setRendApertureWidth data[15]
			at time data[1] cam.fov = cameraFOV.MMtoFOV  data[14]
		)
	)
	close dataFile
	select cam
	viewport.setCamera cam
)
else
	messageBox "Could not find camera file" title:"No Cam File"