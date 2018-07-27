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
	TIMEOUT /t 1 & net use q: \\raidcharles\raidcharles_work\work 123456 /user:smb /persistent:yes || goto :repeatq
)

IF NOT EXIST R:\ (
	:repeatr
	TIMEOUT /t 1 & net use r: \\ramburglar\ramburglar_work 123456 /user:smb /persistent:yes || goto :repeatr
)

IF NOT EXIST S:\ (
	:repeats
	TIMEOUT /t 1 & net use s: \\deadlinedata\Repo a123456! /user:smb /persistent:yes || goto :repeats
)

IF NOT EXIST F:\ (
	:repeatf
	TIMEOUT /t 1 & net use f: \\footage\armory R3nder! /user:render /persistent:yes || goto :repeatf
)

exit
