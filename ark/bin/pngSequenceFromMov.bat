set file=%1
set imgFolder=%file:~0,-4%
mkdir %imgFolder%
for /f %%a in ("%file%") do set fileBase=%%~na
c:\ffmpeg\bin\ffmpeg.exe -i %file% %imgFolder%\%fileBase%_%%04d.png
pause
