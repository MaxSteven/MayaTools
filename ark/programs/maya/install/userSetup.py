#!/usr/bin/env python

# Add paths to PYTHONPATH
import sys
import os


print "#--------------------------USERSETUP-----------------------#"
os.environ['ARK_CURRENT_APP'] = 'maya'

if sys.platform.startswith('linux'):
    sys.path.append('/usr/lib/python2.7/site-packages/')
if sys.platform.startswith('win'):
    sys.path.append('C:/Python27/Lib/site-packages/')

import arkInit
arkInit.init()

import settingsManager
globalSettings = settingsManager.globalSettings()

sys.path.append(globalSettings.MAYA_SCRIPT_ROOT)

import initMaya
initMaya.init()

import translators
translator = translators.getCurrent()

print "#-----------------------END USERSETUP-------------------#"
