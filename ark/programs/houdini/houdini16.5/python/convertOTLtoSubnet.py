# running
# execfile('C:/ie/ark/programs/houdini/houdini13.0/python/convertOTLtoSubnet.py')

import hou

sels = hou.selectedNodes()
context = sels[0].parent()
for src in sels:
	dst = context.createNode('subnet',node_name='testname')
	dst.setPosition(src.position()+hou.Vector2(2,0))
	templatecode = src.parmTemplateGroup().asCode()

	# fix bugs of the templatecode
	templatecode=templatecode.replace(", ,", ',')
	templatecode=templatecode.replace('default_expression_language=hou.scriptLanguage.Hscripticon_names=([]),', '')

	exec templatecode # hou_parm_template_group automatically made by the code
	dst.setParmTemplateGroup(hou_parm_template_group)

	srccode = src.asCode()
	srccode = srccode.replace(src.name(),dst.name())
	srccode = srccode.replace(src.type().name(),dst.type().name())
	srccodelist = srccode.split('\n\n')
	srccodelist.pop(1) # delete node creation code
	srccode = '\n\n'.join(srccodelist)
	exec srccode # hou_node and hou_parent created by the code
	del hou_node
	del hou_parent
	hou.copyNodesTo(src.children(), dst)
