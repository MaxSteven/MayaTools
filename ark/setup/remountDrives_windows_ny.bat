::unmount drives if they exist, ignore if they're in use
IF EXIST Q:\ (
	echo N | net use q: /d
)
IF EXIST R:\ (
	echo N | net use r: /d
)
IF EXIST S:\ (
	echo N | net use s: /d
)

::TIMEOUT /t 20

::remount all unmounted drives
::sometimes need to wait and keep trying
IF NOT EXIST Q:\ (
	:repeatq
	TIMEOUT /t 1 & net use q: \\10.26.16.252\wutanglang_work\work\q a123456!ny /user:smbny /persistent:yes || goto :repeatq
)
IF NOT EXIST R:\ (
	:repeatr
	TIMEOUT /t 1 & net use r: \\10.26.16.252\wutanglang_work\work\r a123456!ny /user:smb /persistent:yes || goto :repeatr
)
IF NOT EXIST S:\ (
	:repeats
	TIMEOUT /t 1 & net use s: \\172.16.0.54\Repo a123456! /user:smb /persistent:yes || goto :repeats
)
exit
