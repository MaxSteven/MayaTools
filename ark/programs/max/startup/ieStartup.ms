
-- backwards compatability w/ Max 2014 for now
if (python != undefined) then
	python.ExecuteFile (MAX_TOOLS_ROOT + "startup/initMax.py")

global ARK_TEMP = "C:/ie/temp/"
global ARK_PYTHON = "C:/Python27/python.exe"
-- // shouldn't need this anymore
global SHEPHERD_ROOT = ARK_ROOT + "../shepherd/shepherd/"
global SHEPHERD_REPOSITORY = "Q:/ASSETS/Tools/Shepherd/"

fileInGamma = 2.2
fileIn (MAX_TOOLS_ROOT + "lib/ieMax.ms")
fileIn (MAX_TOOLS_ROOT + "macroscripts/ieMacros.ms")
actionMan.executeAction 0 "370"  --// Tools: Show Selection Bracket Toggle
NitrousGraphicsManager.HardwareHitTestEnabled = false

if (VRay != undefined and classof (renderers.current) == classof (VRay())) then
(
	renderers.current.system_vrayLog_show = false
) --// Tools: Turns off VRay Log window
--//callbacks.addScript #filePreOpenProcess "callbackParams = callbacks.notificationParam(); scriptFile = (ieMaxStripFileExtension callbackParams[2]) + \".ms\"; if (doesFileExist scriptFile) then execute (openFile scriptFile)" id:#jsFileFunctions

--// fileIn (MAX_TOOLS_ROOT + "include/MorphX2.ms")
