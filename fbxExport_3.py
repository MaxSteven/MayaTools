import maya.cmds as mc

selection = mc.ls(sl=True)[0]
isReference=True
while isReference==True:
    referenceNode = mc.referenceQuery(selection, rfn = True, tr=True)
    referenceFile = mc.referenceQuery(referenceNode, filename=True)
    namespace = mc.referenceQuery(selection, namespace=True).replace(':', '')
    mc.file(referenceFile, importReference = True)
    isReference = mc.referenceQuery(selection, isNodeReferenced = True)

geoGroup = mc.listRelatives(selection, parent=True)[0]
geoObjects = [obj for obj in mc.listRelatives(geoGroup, allDescendents = True) if mc.objectType(obj)== 'mesh']
geoTransforms = [mc.listRelatives(obj, parent=True)[0] for obj in geoObjects]
bindJoints = []
for obj in geoTransforms:
    joints = mc.skinCluster(obj, query=True, weightedInfluence = True)
    bindJoints.extend(joints)

print namespace
mc.select(namespace + ':Human_rig', hi = True)
allObjects = mc.ls(sl=True)
newAllObjects = []
for obj in allObjects:
    print obj
    try:
        newObj = mc.rename(obj, obj.replace(namespace + ':', ''))
        newAllObjects.append(newObj)
    except:
        pass

mc.select(all=True)
allObjects = mc.ls(sl=True)
newAllObjects = []
for obj in allObjects:
    print obj
    try:
        newObj = mc.rename(obj, obj.replace(namespace + ':', ''))
        newAllObjects.append(newObj)
    except:
        pass

geo = selection.replace(namespace + ':', '')
mc.select('GroundBindRoot_JNT', hi = True)
allBindNodes = mc.ls(sl=True)
bakedNodes = []
for obj in allBindNodes:
    if 'Constraint' not in mc.objectType(obj):
        bakedNodes.append(obj)

mc.bakeResults(bakedNodes, simulation=True, t = (1,3),
            sampleBy = 1, disableImplicitControl=True,
            preserveOutsideKeys=True, sparseAnimCurveBake=False,
            removeBakedAttributeFromLayer=False, removeBakedAnimFromLayer=False,
            bakeOnOverrideLayer=False, minimizeRotation=True, controlPoints=False,
            shape=True
            )
scaleConnectedObjects = ['R_ArmRig_JNT', 'R_ForearmRig_JNT', 'R_WristRig_JNT',
                         'L_ArmRig_JNT', 'L_ForearmRig_JNT', 'L_WristRig_JNT',
                         'L_upLegRig_JNT', 'L_ShinRig_JNT', 'L_AnkleRig_JNT', 'L_FootBaseRig_JNT', 'L_BallRig_JNT',
                         'R_upLegRig_JNT', 'R_ShinRig_JNT', 'R_AnkleRig_JNT', 'R_FootBaseRig_JNT', 'R_BallRig_JNT']
for obj in scaleConnectedObjects:
    try:
        mc.disconnectAttr(obj + '.scale', obj.replace('Rig', 'Bind') + '.scale')
    except:
        print obj
        pass

mc.delete('World_CTL')

mc.delete('DO_NOT_TOUCH')

for obj in mc.listRelatives('Deformation', children=True):
    if obj != 'GroundBindRoot_JNT':
        mc.delete(obj)

newBindJoints = []

geoObjects = [obj for obj in mc.listRelatives('GEO', allDescendents = True) if mc.objectType(obj)== 'mesh']
geoTransforms = [mc.listRelatives(obj, parent=True)[0] for obj in geoObjects]
for obj in geoTransforms:
    joints = mc.skinCluster(obj, query=True, weightedInfluence = True)
    newBindJoints.extend(joints)

nonBindNodes = []
for obj in allBindNodes:
    if mc.objExists(obj) == True and obj not in newBindJoints:
        if not mc.listRelatives(obj, children = True):
            mc.delete(obj)

        else:
            nonBindNodes.append(obj)

for obj in nonBindNodes:
    if not mc.listRelatives(obj, children = True):
        mc.delete(obj)

mc.setAttr('Deformation.scaleX', 0.01)
mc.setAttr('Deformation.scaleY', 0.01)
mc.setAttr('Deformation.scaleZ', 0.01)