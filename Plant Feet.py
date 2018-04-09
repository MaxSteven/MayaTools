# Plant Feet

import maya.cmds as mc

FeetOffset = mc.getAttr('FeetBase.translateY')
currentOffset = mc.getAttr('Rig.translateY')
mc.setAttr('Rig.translateY', currentOffset + (-1 * FeetOffset))