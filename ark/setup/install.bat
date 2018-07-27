
REM network connections
REM ============================================================================================
net use r: \\ramburglar\ramburglar_work 123456 /user:smb /persistent:yes
net use q: \\raidcharles\raidcharles_work\work 123456 /user:smb /persistent:yes


REM setup python
REM ============================================================================================
msiexec /i R:\Assets\Tools\install\python27.msi
set PATH=%PATH%;C:\python27\
setx PATH=%PATH%;C:\python27\


REM install tight vnc
REM ============================================================================================
msiexec /i R:\Assets\Tools\install\tightvnc.msi


REM turn off UAC
REM ============================================================================================
C:\Windows\System32\cmd.exe /k %windir%\System32\reg.exe ADD HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System /v EnableLUA /t REG_DWORD /d 0 /f


REM copy git access file
REM ============================================================================================
xcopy _netrc %userprofile%


REM copy tools
REM ============================================================================================
c:
mkdir c:\ie
cd c:\ie

git clone https://github.com/IngenuityEngine/ark.git --depth=1 --no-single-branch
git clone https://github.com/IngenuityEngine/arkUtil.git --depth=1 --no-single-branch
git clone https://github.com/IngenuityEngine/caretaker.git --depth=1 --no-single-branch
git clone https://github.com/IngenuityEngine/cloudManager.git --depth=1 --no-single-branch
git clone https://github.com/IngenuityEngine/coren.git --depth=1 --no-single-branch
git clone https://github.com/IngenuityEngine/database.git --depth=1 --no-single-branch
git clone https://github.com/IngenuityEngine/settingsManager.git --depth=1 --no-single-branch
git clone https://github.com/IngenuityEngine/shepherd.git --depth=1 --no-single-branch
git clone https://github.com/IngenuityEngine/translators.git --depth=1 --no-single-branch


REM install_quiet
REM ============================================================================================
cd c:\ie\ark
python C:\ie\ark\setup\setup.py -quiet


REM run sheep
REM ============================================================================================
cd c:\ie\shepherd\bin
sheep.bat

