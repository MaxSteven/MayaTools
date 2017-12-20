import maya.cmds as mc
control1Attr = 'R_innerBrow_CTL.translateY'
blendshapeAttr1 = 'R_allShapes_eyes.browRaise_lipPucker'
blendshapeAttr2 = 'R_allShapes_eyes.upperLipRaiser_BrowDepressor'
control = control1Attr.split('.')[0]


remapPositive = mc.shadingNode("remapValue", asUtility=True, n = control.split('_')[0]+'Positive_RMV')
mc.setAttr(remapPositive + '.inputMin', 0)
mc.setAttr(remapPositive + '.inputMax', 1)
mc.setAttr(remapPositive + '.outputMin', 0)
mc.setAttr(remapPositive + '.outputMax', 1)
remapNegative = mc.shadingNode("remapValue", asUtility=True, n = control.split('_')[0]+'Negative_RMV')
mc.setAttr(remapNegative + '.inputMin', 0)
mc.setAttr(remapNegative + '.inputMax', -1)
mc.setAttr(remapNegative + '.outputMin', 0)
mc.setAttr(remapNegative + '.outputMax', 1)

mc.connectAttr(control1Attr, remapPositive + '.inputValue')
mc.connectAttr(control1Attr, remapNegative + '.inputValue')
mc.connectAttr(remapPositive + '.outValue', blendshapeAttr1)
mc.connectAttr(remapNegative + '.outValue', blendshapeAttr2)

mc.transformLimits(control, ety = (1,1), ty = (-1, 1))