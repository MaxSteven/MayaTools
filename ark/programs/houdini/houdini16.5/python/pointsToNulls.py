# running
# execfile('C:/ie/ark/programs/houdini/houdini13.0/python/pointsToNulls.py')


import hou


selectedNode = hou.selectedNodes()[0]

obj = hou.node('/obj')

# fix: for obj get the display node and get points from there

for i in range(len(selectedNode.geometry().points())):

	newNull = obj.createNode('null')

	newNull.parm('tx').setExpression('point("../Vortex",%d, "P", 0)' % i)
	newNull.parm('ty').setExpression('point("../Vortex",%d, "P", 1)' % i)
	newNull.parm('tz').setExpression('point("../Vortex",%d, "P", 2)' % i)

	newNull.parm('rx').setExpression('point("../Vortex",%d, "rot", 0)' % i)
	newNull.parm('ry').setExpression('point("../Vortex",%d, "rot", 1)' % i)
	newNull.parm('rz').setExpression('point("../Vortex",%d, "rot", 2)' % i)

	newNull.parm('sx').set(1)
	newNull.parm('sy').set(1)
	newNull.parm('sz').set(1)
