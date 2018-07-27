Set WshShell = CreateObject("WScript.Shell")
WshShell.Run chr(34) & "%ARK_ROOT%\ark\tools\hub\hub.bat" & Chr(34), 0
Set WshShell = Nothing
