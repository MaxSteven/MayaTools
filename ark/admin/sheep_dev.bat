net use r: \\ramburglar\ramburglar_work 123456 /user:smb /persistent:yes
net use q: \\raidcharles\raidcharles_work\work 123456 /user:smb /persistent:yes

python %ARK_ROOT%shepherd/shepherd/sheep.py --skipInstall 1
pause
