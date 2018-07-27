# -----------------------------------------------------------------------------
#  batchComp.py
#  By Grant Miller (blented@gmail.com)
#  v 1.0
#  Created On: 12/21/12
#  Modified On: 12/21/12
#  tested using Max 2012, Nuke 6.3v4, Softimage 2012, Maya 2012
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
#  Required Files:
#  ieMax.ms
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
#  Description:
#  Replaces instances w/ another object
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
#  Revision History:
#
#  v 1.00 Initial version
#
# -----------------------------------------------------------------------------

import sys
import os
# import nuke
# import arkNuke
import arkInit
arkInit.init()
# import ieOS
import arkNuke
import fileseq

# searchDir = sys.argv[1]
searchDir = 'Q:/Fairy_Tale_Academy/WORKSPACES/'

allWorkspaces = os.listdir(searchDir)
numToComp = 0
i = 0
for workspaceName in allWorkspaces:
	if 'TEA' in workspaceName:
		workspaceRoot = searchDir + workspaceName + '/'
		renderPath = workspaceRoot + 'Renders/v001/'
		if os.path.isdir(renderPath):
			sequences = fileseq.findSequencesOnDisk(renderPath)
			for seq in sequences:
				if 'all' in seq.basename():
					print workspaceName + ': %s-%s' % (seq.start(),seq.end())
					print

					renderFile = renderPath + seq.basename() + '%04d.exr'

					readNode = nuke.nodes.Read(file=renderFile,first=seq.start(),last=seq.end())
					try:
						exrCam = arkNuke.cameraFromEXR(readNode)
					except:
						print 'Could not create EXR cam for: ' + workspaceName
						exrCam = False

					compGizmo = nuke.nodes.CompControls_FTA()
					compGizmo.setInput(0,readNode)
					if exrCam:
						compGizmo.setInput(1,exrCam)

					writeFile = 'Q:/Fairy_Tale_Academy/HD_RENDERS/' + workspaceName + '/' + workspaceName + '_%04d.tga'
					writeNode = nuke.nodes.Write(name='WriteFinal',file=writeFile,file_type='exr',beforeRender='arkNuke.beforeRender',afterRender='')
					writeNode.setInput(0, compGizmo)

					nuke.root()['first_frame'].setValue(seq.start())
					nuke.root()['last_frame'].setValue(seq.end())
					nuke.root()['format'].setValue('HD')

					scriptFile = workspaceRoot + 'Comp/' + workspaceName + '_comp_v01_ghm.nk'
					nuke.scriptSave(scriptFile)

					# delete all the nodes in the current comp
					for n in nuke.allNodes():
						nuke.delete(n)

					i += 1
	if numToComp and i >= numToComp:
		break

# Execute:
# "C:\Program Files\Nuke6.3v4\Nuke6.3.exe" -t Q:\USERS\Grant_Miller\dev\tools\Nuke\python\batchComp.py
