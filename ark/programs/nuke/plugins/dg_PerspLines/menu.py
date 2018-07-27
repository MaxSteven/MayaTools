import nuke


nuke.menu('Nodes').addCommand('dgTools/PerspLines/dg_PerspLines','nuke.createNode("dg_PerspLines")','')

nuke.menu('Nodes').addCommand('dgTools/PerspLines/dg_Horizon','dg_PerspLines_Horizon()','')

nuke.menu('Nuke').addCommand('dgTools/PerspLines/Align camera for 2 selected nodes','dg_PerspLines_AlignCamera()', 'Shift+V')



def dg_PerspLines_Horizon():
	nodes=nuke.selectedNodes()
	if not len(nodes)==2:
		nuke.message('Illegal amount of selected nodes.\nPlease select exactly two dg_PerspLines nodes')
		return
	for n in nodes:
		if not n.Class()=='dg_PerspLines':
			nuke.message('One of selected nodes is not dg_PerspLines')
			return
	i=1
	if nodes[0].input(0)==nodes[1]:
		i=0
	
	dg_PerspLines_selectOnly(nodes[i])
	
	n=nuke.createNode('dg_Horizon')
	n['vp1'].setExpression(nodes[0].name()+'.PT')
	n['vp2'].setExpression(nodes[1].name()+'.PT')