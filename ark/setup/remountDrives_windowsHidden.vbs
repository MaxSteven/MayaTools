Set WshShell = CreateObject("WScript.Shell")
WshShell.Run chr(34) & "%ARK_ROOT%\ark\setup\remountDrives_windows.bat" & Chr(34), 0
Set WshShell = Nothing
