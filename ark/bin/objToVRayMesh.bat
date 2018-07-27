set file=%1
set baseName=%file:~0,-4%
"C:\Program Files\Chaos Group\V-Ray\3dsmax 2016 for x64\tools\ply2vrmesh.exe" %file% %baseName%.vrmesh
pause