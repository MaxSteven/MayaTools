import hou
import traceback
import sys

import arkInit
arkInit.init()

import arkUtil

import translators
translator = translators.getCurrent()
from deadline import jobTypes
from deadline import arkDeadline
ad = arkDeadline.ArkDeadline()

# from CallDeadlineCommand import CallDeadlineCommand

try:
    import arkFTrack
    pm = arkFTrack.getPM()

except Exception as err:
    print( traceback.format_exc() )
    print( "no Ftrack" )
    raise err

# import SubmitHoudiniToDeadlineFunctions as SHTDFunctions

if not pm.getTask():
    raise Exception('No Task, can\'t render without one')

from CallDeadlineCommand import CallDeadlineCommand

path = CallDeadlineCommand( [ "-GetRepositoryPath", "submission/Houdini/Main" ] ).strip()
if path != "":
  path = path.replace( "\\", "/" )

  # Add the path to the system path
  if path not in sys.path :
      print "Appending \"" + path + "\" to system path to import SubmitDeadlineRop module"
      sys.path.append( path )

  #Import the script and call the main() function
import SubmitDeadlineRop

dlSubmittedIDs = {}
wedgeSubmittedIDs = {}
hipFile = hou.hscriptExpression('$HIPFILE')
hipFolder = hou.hscriptExpression('$HIP')

def SubmitToDeadline():
    global dlSubmittedIDs
    dlNode = hou.pwd()

    if not dlNode.isLocked():
        dependentNodes = dlNode.inputs()
        dlSubmittedIDs = {}

        # for every node in node.inputs() run PrepareNodeForSubmission()
        ResetWedgeSubmittedIDs()
        for renderNode in dependentNodes:
            PrepareNodeForSubmission( renderNode, dlNode )

def ResetWedgeSubmittedIDs():
    global wedgeSubmittedIDs
    wedgeSubmittedIDs = {}

def PrepareNodeForSubmission( renderNode, dlNode ):
    print '==================================================='
    print 'PreparingNodeForSubmission'
    print '==================================================='
    global dlSubmittedIDs
    global wedgeSubmittedIDs
    print '======== Current Wedge IDs ==========='
    print wedgeSubmittedIDs
    print '======================================='

    bypassed = renderNode.isBypassed()
    locked =  renderNode.isLocked()
    isDeadline = ( renderNode.type().description() == "Deadline" )

    depJobIds = []

    if not locked:
        if renderNode.type().name() == 'ie_customwedge':
            # Wedge submission logic
            wedges = arkUtil.parseFrameRange(renderNode.parm('renderRange').rawValue())
            numberOfWedges = len(wedges)
            print '============= Found custom wedge! ================='
            print 'WedgeNode:', renderNode.name()
            print '==================================================='
            for i in range(numberOfWedges):
                print 'Setting wedge:', wedges[i]
                print('submitting ' + str(i + 1) + ' wedge')

                # APPLY WEDGE VALUE IN THE WEDGE NUMBER PARAMETER AND SUBMIT TO FARM
                renderNodePathText = renderNode.path().replace('/', '_')
                renderNode.parm('wedgeNum').set(wedges[i])
                print 'Saving File'
                # SAVING FILE AFTER SETTING WEDGE VALUES
                hou.hipFile.save(
                                    file_name=hipFile.replace('.hip', '_' + str(wedges[i]) + '_' + renderNodePathText + '_wedge.hip'),
                                    save_to_recent_files=False
                                )
                dependentNodes = renderNode.inputs()
                futureDlNode = dlNode
                if isDeadline and not bypassed:
                    futureDlNode = renderNode

                # recursively calls PrepareNodeForSubmission up the chain
                for depNode in dependentNodes:
                    # if depNode.path() not in dlSubmittedIDs.keys():
                    print '====== Preparing input node for custom wedge ======'
                    print 'depNode:', depNode.name()
                    print 'futureDlNode: ', futureDlNode.name()
                    print '==================================================='
                    if renderNode.path() not in wedgeSubmittedIDs.keys():
                        wedgeSubmittedIDs = {renderNode.path(): []}

                    wedgeIDs = PrepareNodeForSubmission(depNode, futureDlNode)
                    if wedgeIDs:
                        wedgeSubmittedIDs[renderNode.path()].extend(wedgeIDs)
                        print '\n' + str(wedgeSubmittedIDs)
                    i += 1

                if renderNode.path() not in dlSubmittedIDs.keys():
                    dlSubmittedIDs[ renderNode.path() ] = []
                dlSubmittedIDs[ renderNode.path() ].extend(depJobIds)

            renderNodePath = renderNode.path()
            dlNodePath = dlNode.path()
            # Saves current file as original file
            print '=========================== Saving current file to original file! ========================='
            hou.hipFile.save(
                                file_name=hipFile,
                                save_to_recent_files=True
                            )

            SubmitWedgeCleanupJob(wedgeSubmittedIDs, hipFolder, renderNode)

        else:
            # Regular submission logic
            print '======== Encountered Non-Wedge, Submitting ============='
            print 'renderNode:', renderNode.name()
            print '========================================================'
            dependentNodes = renderNode.inputs()
            futureDlNode = dlNode
            if isDeadline and not bypassed:
                futureDlNode = renderNode

            # recursively calls PrepareNodeForSubmission up the chain
            for depNode in dependentNodes:
                # if depNode.path() not in dlSubmittedIDs.keys():
                print '======= Preparing input node for non-wedge ========'
                print 'depNode:', depNode.name()
                print '==================================================='
                PrepareNodeForSubmission( depNode, futureDlNode )

                # SETTING REGULAR DEPENDENCIES
                if depNode.path() in dlSubmittedIDs.keys():
                    depJobIds.extend( dlSubmittedIDs[ depNode.path() ] )

                # SETTING WEDGE DEPENDENCIES
                if depNode.path() in wedgeSubmittedIDs.keys():
                    print '========== Setting Dependencies of ' + depNode.path() + ' =============='
                    print str(wedgeSubmittedIDs[depNode.path()])
                    print '======================================================================'
                    depJobIds.extend(wedgeSubmittedIDs[depNode.path()])


            # submits the node
            if not renderNode.isBypassed() and not isDeadline:
                print '========== Submitting non-wedge node! ============='
                print 'renderNode:', renderNode.name()
                print 'dlNode:', dlNode.name()
                print '==================================================='
                if renderNode.path() not in dlSubmittedIDs.keys():
                    dlSubmittedIDs[ renderNode.path() ] = []

                print '========================================================='
                if renderNode.type().name() == 'ifd':
                    print 'MANTRA PATH:'
                    print renderNode.parm('vm_picture').eval()
                    print 'IFD PATH:'
                    print renderNode.parm('soho_diskfile').eval()
                elif renderNode.type().name() == 'ie_customgeo':
                    print 'BGEO PATH:'
                    print renderNode.parm('cacheNodePath').evalAsNode().parm('filename').eval()
                print '========================================================='

                # SAVING FILE BEFORE SUBMISSION
                print '======================== Submitting ' + hou.hipFile.basename() + '============================'
                submittedNodeIDs = SubmitDeadlineRop.nodeSubmission( renderNode, dlNode, depJobIds )
                PostSubmitEnvironment(submittedNodeIDs)
                if renderNode.type().name() == 'ifd':
                    SubmitCleanupJob(submittedNodeIDs)
                    SubmitDraftJob(submittedNodeIDs, renderNode, dlNode)

                dlSubmittedIDs[ renderNode.path() ].extend(submittedNodeIDs)
                return submittedNodeIDs

            else:
                if renderNode.path() not in dlSubmittedIDs.keys():
                    dlSubmittedIDs[ renderNode.path() ] = []
                dlSubmittedIDs[ renderNode.path() ].extend(depJobIds)
                return None

def PostSubmitEnvironment(submittedIDs):
    print '================= Setting Environmment For Renders ====================='
    print 'Setting HIP as ' + hipFolder
    print 'Setting HIPFILE as ' + hipFile
    try:
        env = {
            'HIP': hipFolder,
            'HIPFILE': hipFile
        }
    except:
        print( traceback.format_exc() )
        print( "Job submitted without houdini HIP environment." )

    for jobID in submittedIDs:
        print 'Setting Environment to job:', jobID
        ad.updateJobData(jobID, {'Props.Env': env})
        dependencies = ad.getJob(jobID)['Props']['Dep']

        # set environment only if the job has dependencies
        if len(dependencies):
            ad.updateJobData(dependencies[0]['JobID'], {'Props.Env': env})

def SubmitCleanupJob(submittedIDs):
    for jobID in submittedIDs:
        job = ad.getJob(jobID)
        try:
            jobInfo = {
                'Name': job['Props']['Batch'] + '_Cleanup',
                'BatchName': job['Props']['Batch'],
                'Plugin': 'Python',
                'ExtraInfoKeyValue0': 'jobID=' + ','.join(submittedIDs),
                'JobDependencies': ','.join(submittedIDs)
                }

            pluginInfo = {
                'Shell': 'default',
                'Version': '2.7',
                'ShellExecute': True,
                'SingleFramesOnly': True,
                'ScriptFile': 'S:/custom/scripts/Jobs/postMantraJob.py'
            }

            submittedInfo = ad.submitJob(jobInfo, pluginInfo)
            print "cleanup job submitted"
        except:
            print( traceback.format_exc() )
            print "Job will be submitted without an IFD cleanup job."

def SubmitWedgeCleanupJob(submittedIDs, hipFolder, wedgeNode):
    wedgeNodePath = wedgeNode.path()
    wedgeNodePathText = wedgeNodePath.replace('/', '_')
    job = ad.getJob(submittedIDs[wedgeNodePath][0])
    try:
        jobInfo = {
            'Name': job['Props']['Batch'] + '_WedgeCleanup',
            'BatchName': job['Props']['Batch'],
            'Plugin': 'Python',
            'ExtraInfoKeyValue0': 'wedgeSubmittedIDs=' + ','.join(submittedIDs),
            'ExtraInfoKeyValue1': 'wedgedFolder=' + hipFolder,
            'ExtraInfoKeyValue2': 'wedgeNodePath=' + wedgeNodePath,
            'JobDependencies': ','.join(submittedIDs[wedgeNodePath])
            }

        pluginInfo = {
            'Shell': 'default',
            'Version': '2.7',
            'ShellExecute': True,
            'SingleFramesOnly': True,
            'ScriptFile': 'S:/custom/scripts/Jobs/postWedgeJob.py'
        }

        submittedInfo = ad.submitJob(jobInfo, pluginInfo)
        print "wedge cleanup job submitted"
    except:
        print( traceback.format_exc() )
        print "Job will be submitted without an Wedge cleanup job."

def SubmitDraftJob(submittedIDs, renderNode, dlNode):
    for jobIDs in submittedIDs:
        try:
            data = {
                'output': renderNode.parm('vm_picture').eval(),
                'priority': dlNode.parm('dl_priority').eval(),
                'frameRange': str(int(dlNode.parm('f1').eval())) + '-' + str(int(dlNode.parm('f2').eval())),
                'name': dlNode.parm('dl_job_name').eval(),
                'node': str(renderNode.path()),
                'program': 'houdini',
            }
            job = jobTypes.DeadlineJob.DeadlineJob()
            jobInfo = job.getDraftJobInfo(data)
            if not jobInfo:
                return

            jobInfo.update({
                'JobDependencies': jobIDs
            })
            pluginInfo = job.getDraftPluginInfo(data)
            ad.submitJob(jobInfo, pluginInfo)
        except:
            print( traceback.format_exc() )
            print "Job will be submitted without a draft job."