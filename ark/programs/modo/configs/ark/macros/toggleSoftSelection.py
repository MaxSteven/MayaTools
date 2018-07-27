# python
import lx

if lx.eval1('tool.set falloff.softSelection ?') == 'off':
	lx.eval('tool.set falloff.softSelection on')
else:
	lx.eval('tool.set falloff.softSelection off')
