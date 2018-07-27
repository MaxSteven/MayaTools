import os
import re

def getFilename(filename, frame):
    num = str(frame)
    return re.sub('.vrscene', '_' + '0' * (4 - len(num)) + num + '.vrscene', filename)

def __main__(*args):
    deadlinePlugin = args[0]

    task = deadlinePlugin.GetCurrentTask()
    frameList = task.TaskFrameList
    vrayFile = deadlinePlugin.GetPluginInfoEntry('VRayExportFile')

    for f in frameList:
        path = getFilename(vrayFile, f)
        if not os.path.isfile(path):
            deadlinePlugin.FailRender('Post job script could not find file: ' + path)
        else:
            deadlinePlugin.LogInfo('Successfully found file: ' + path)
