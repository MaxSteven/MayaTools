# python
import lx

lx.eval1('view3d.sameAsActive false')
if lx.eval1('view3d.inactiveInvisible ?') == False:
	lx.eval('view3d.wireframeOverlay none inactive')

if lx.eval1('view3d.wireframeOverlay ?') == 'none':
	lx.eval('view3d.wireframeOverlay colored active')
else:
	lx.eval('view3d.wireframeOverlay none active')
