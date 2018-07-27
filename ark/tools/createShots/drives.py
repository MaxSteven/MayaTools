import subprocess
import sys

#on windows
#Get the fixed drives
if 'win' in sys.platform:
    drivelist = subprocess.Popen('wmic logicaldisk get name,description', shell=True, stdout=subprocess.PIPE)
    drivelisto, err = drivelist.communicate()
    driveLines = drivelisto.split('\n')
    print driveLines
