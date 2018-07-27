set file=%1
set fileBase=%file:~0,-9%
R:/Assets/Software/Stitcher/stitcher.exe --in %fileBase%*.abc --out %fileBase%abc
pause
