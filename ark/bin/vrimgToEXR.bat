set file=%1
for /f %%a in ("%file%") do set fileBase=%%~na
set fileBase=%fileBase:~0,-4%
R:\ASSETS\Tools\core\vray\vrimg2exr.exe %fileBase%* -compression zips
pause