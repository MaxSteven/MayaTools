# python
import lx

lx.eval1('view3d.sameAsActive false')

if lx.eval1('view3d.shadingStyle ?') == 'wire':
	lx.eval1('view3d.shadingStyle advgl')
	if lx.eval1('view3d.inactiveInvisible ?') == False:
		lx.eval1('view3d.shadingStyle advgl inactive')
else:
	lx.eval1('view3d.shadingStyle wire')
	if lx.eval1('view3d.inactiveInvisible ?') == False:
		lx.eval1('view3d.shadingStyle wire inactive')
