c:
set GIT_ASK_YESNO=false

cd c:\ie\ark
del c:\ie\ark\.git\index.lock
git reset --hard
git checkout master
git reset --hard
git clean -xdf
git pull https://ingenuityworker:zombies2012@github.com/ingenuityengine/ark

cd c:\ie\arkUtil
del c:\ie\arkUtil\.git\index.lock
git reset --hard
git checkout master
git reset --hard
git clean -xdf
git pull https://ingenuityworker:zombies2012@github.com/ingenuityengine/arkutil

cd c:\ie\caretaker
del c:\ie\caretaker\.git\index.lock
git reset --hard
git checkout master
git reset --hard
git pull https://ingenuityworker:zombies2012@github.com/ingenuityengine/caretaker

cd c:\ie\cloudManager
del c:\ie\cloudManager\.git\index.lock
git reset --hard
git checkout master
git reset --hard
git pull https://ingenuityworker:zombies2012@github.com/ingenuityengine/cloudManager

cd c:\ie\coren
del c:\ie\coren\.git\index.lock
git reset --hard
git checkout master
git reset --hard
git pull https://ingenuityworker:zombies2012@github.com/ingenuityengine/coren

cd c:\ie\cOS
del c:\ie\cOS\.git\index.lock
git reset --hard
git checkout master
git reset --hard
git clean -xdf
git pull https://ingenuityworker:zombies2012@github.com/ingenuityengine/cos

cd c:\ie\database
del c:\ie\database\.git\index.lock
git reset --hard
git checkout master
git reset --hard
git pull https://ingenuityworker:zombies2012@github.com/ingenuityengine/database

cd c:\ie\settingsManager
del c:\ie\settingsManager\.git\index.lock
git reset --hard
git checkout master
git reset --hard
git clean -xdf
git pull https://ingenuityworker:zombies2012@github.com/ingenuityengine/settingsmanager

cd c:\ie\shepherd
del c:\ie\shepherd\.git\index.lock
git reset --hard
git checkout master
git reset --hard
git clean -xdf
git pull https://ingenuityworker:zombies2012@github.com/ingenuityengine/shepherd

cd c:\ie\translators
del c:\ie\translators\.git\index.lock
git reset --hard
git checkout master
git reset --hard
git clean -xdf
git pull https://ingenuityworker:zombies2012@github.com/ingenuityengine/translators

cd c:\ie\weaver
del c:\ie\weaver\.git\index.lock
git reset --hard
git checkout master
git reset --hard
git clean -xdf
git pull https://ingenuityworker:zombies2012@github.com/ingenuityengine/weaver
