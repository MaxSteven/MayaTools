# running
# execfile('C:/ie/ark/programs/houdini/houdini13.0/python/swapNodes.py')

import hou

sourceNode = hou.node('obj/lab')


sourceNodeTuple = (sourceNode,)
selectedNodes = list(hou.selectedNodes())

while len(selectedNodes) > 0:
	node = selectedNodes.pop()
	# fix: assumes object level, should get your current level instead
	newNode = hou.copyNodesTo(sourceNodeTuple, hou.node('obj'))[0]
	for parm in node.parms():
		try:
			try:
				newNode.parm(parm.name()).set(parm.unexpandedString())
			except:
				newNode.parm(parm.name()).set(parm.eval())
		except:
			print 'Could not set:', parm.name()
	nodeName = node.name()
	position = node.position()
	node.destroy()
	newNode.setName(nodeName)
	newNode.setPosition(position)
