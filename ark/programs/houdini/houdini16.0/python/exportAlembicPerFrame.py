# run it:
# execfile('C:/ie/ark/programs/houdini/houdini13.0/python/exportAlembicPerFrame.py')
import hou




# STUFF TO CHANGE

# asset variables
ropNodePath = 'obj/export_hair/cache'
name = 'fur'
version = 'v026'

# time variables
start = 1001
end = 1034


# DO NOT TOUCH BELOW THIS LINE

ropNode = hou.node(ropNodePath)
ropNode.parm('trange').set(0)
ropNode.parm('mkpath').set(1)
for f in range(start,end):
	hou.setFrame(f)
	# ropNode.parm('filename').set('$HIP/../cache/%s/%s/%s.%04d.abc' % (name, version, name, hou.frame()))
	ropNode.parm('filename').set('$HIP/cache/%s/%s/%s.%04d.abc' % (name, version, name, hou.frame()))
	ropNode.render()
