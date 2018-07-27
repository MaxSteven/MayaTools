# running
# execfile('C:/ie/ark/programs/houdini/houdini13.0/python/removeRelativePaths.py')

import os
import re



hipPath = os.path.dirname(hou.hipFile.path())
hipPath = re.sub(r'[\\/]+', '/', hipPath)

for node in hou.node('/').allSubChildren():
	for parm in node.parms():
		try:
			val = str(parm.unexpandedString())
			if '$HIP' in val:
				print 'replacing $HIP:', val
				parm.set(val.replace('$HIP', hipPath))
		except:
			pass



