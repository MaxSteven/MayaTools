# python
import lx

if lx.eval1('tool.set falloff.linear ?') == 'off':
	lx.eval('tool.set falloff.linear on')
else:
	lx.eval('tool.set falloff.linear off')
