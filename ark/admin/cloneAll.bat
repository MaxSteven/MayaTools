c:
mkdir c:\ie
cd c:\ie

git clone http://github.com/ingenuityengine/arkMath
git clone http://github.com/ingenuityengine/arkUtil
git clone http://github.com/ingenuityengine/caretaker
git clone http://github.com/ingenuityengine/coren
git clone http://github.com/ingenuityengine/coren_proxy
git clone http://github.com/ingenuityengine/cOS
git clone http://github.com/ingenuityengine/database
git clone http://github.com/ingenuityengine/ingenuity_site
git clone http://github.com/ingenuityengine/logmont
git clone http://github.com/ingenuityengine/settingsManager
git clone http://github.com/ingenuityengine/shepherd
git clone http://github.com/ingenuityengine/storageManager
git clone http://github.com/ingenuityengine/translators
git clone http://github.com/ingenuityengine/tryout
git clone http://github.com/ingenuityengine/weaver

cd /ie/ark
git checkout refactor

cd /ie/arkUtil
git checkout refactor

cd /ie/caretaker
git checkout new_schema

cd /ie/coren
git checkout restyle

cd /ie/cOS
git checkout refactor

cd /ie/database
git checkout refactor

cd /ie/ingenuity_site
git checkout redesign

cd /ie/logmont
git checkout develop

cd /ie/settingsManager
git checkout develop

cd /ie/shepherd
git checkout refactor

cd /ie/translators
git checkout refactor

cd /ie/tryout
git checkout develop

cd /ie/weaver
git checkout develop
