import maya.cmds as mc

control1Attr = 'R_chin_CTL.translateX'
blendshapeAttr1 = 'R_mouth_BSH.au_17'
puppetBlendshapeAttr1 = 'R_mouthPuppet_BSH.au_17_puppet'
# blendshapeAttr2 = 'R_mouth_BSH.au_35'
# puppetBlendshapeAttr2 = 'R_mouthPuppet_BSH.au_35_puppet'
control = control1Attr.split('.')[0]


remapPositive = mc.shadingNode("remapValue", asUtility=True, n = control.rpartition('_')[0]+'Positive_RMV')
mc.setAttr(remapPositive + '.inputMin', 0)
mc.setAttr(remapPositive + '.inputMax', 5)
mc.setAttr(remapPositive + '.outputMin', 0)
mc.setAttr(remapPositive + '.outputMax', 1)
# remapNegative = mc.shadingNode("remapValue", asUtility=True, n = control.rpartition('_')[0]+'Negative_RMV')
# mc.setAttr(remapNegative + '.inputMin', 0)
# mc.setAttr(remapNegative + '.inputMax', -5)
# mc.setAttr(remapNegative + '.outputMin', 0)
# mc.setAttr(remapNegative + '.outputMax', 1)

mc.connectAttr(control1Attr, remapPositive + '.inputValue')
# mc.connectAttr(control1Attr, remapNegative + '.inputValue')
mc.connectAttr(remapPositive + '.outValue', blendshapeAttr1)
mc.connectAttr(remapPositive + '.outValue', puppetBlendshapeAttr1)
# mc.connectAttr(remapNegative + '.outValue', blendshapeAttr2)
# mc.connectAttr(remapNegative + '.outValue', puppetBlendshapeAttr2)

control1Attr = control1Attr.replace('R_', 'L_')
blendshapeAttr1 = blendshapeAttr1.replace('R_', 'L_')
puppetBlendshapeAttr1 = puppetBlendshapeAttr1.replace('R_', 'L_')
# blendshapeAttr2 = blendshapeAttr2.replace('R_', 'L_')
# puppetBlendshapeAttr2 = puppetBlendshapeAttr2.replace('R_', 'L_')
control = control1Attr.split('.')[0]


remapPositive = mc.shadingNode("remapValue", asUtility=True, n = control.rpartition('_')[0]+'Positive_RMV')
mc.setAttr(remapPositive + '.inputMin', 0)
mc.setAttr(remapPositive + '.inputMax', 5)
mc.setAttr(remapPositive + '.outputMin', 0)
mc.setAttr(remapPositive + '.outputMax', 1)
# remapNegative = mc.shadingNode("remapValue", asUtility=True, n = control.rpartition('_')[0]+'Negative_RMV')
# mc.setAttr(remapNegative + '.inputMin', 0)
# mc.setAttr(remapNegative + '.inputMax', -5)
# mc.setAttr(remapNegative + '.outputMin', 0)
# mc.setAttr(remapNegative + '.outputMax', 1)

mc.connectAttr(control1Attr, remapPositive + '.inputValue')
# mc.connectAttr(control1Attr, remapNegative + '.inputValue')
mc.connectAttr(remapPositive + '.outValue', blendshapeAttr1)
mc.connectAttr(remapPositive + '.outValue', puppetBlendshapeAttr1)
# mc.connectAttr(remapNegative + '.outValue', blendshapeAttr2)
# mc.connectAttr(remapNegative + '.outValue', puppetBlendshapeAttr2)

# mc.transformLimits(control, ety = (1,1), ty = (-1, 1))