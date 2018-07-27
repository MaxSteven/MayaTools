'''
The goal of this file is that some of the more
generic methods in translator can be moved in here.

'''

import cOS
import os
import settingsManager
globalSettings = settingsManager.globalSettings()

def processAlembic(filepath, frameRange, fps=24):
	command = (os.environ.get('ARK_PYTHON') +
			' ' + globalSettings.HOUDINI_PROCESS_ALEMBIC +
			' -o ' + filepath +
			' -fr ' + frameRange +
			' -fps ' + fps +
			' -farm False')

	(out, err) = cOS.getCommandOutput(command)
	print 'process alembic output:', out
	print 'process alembic errors:', err

	if err:
		return err
	else:
		return True