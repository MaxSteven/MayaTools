# python
import lx

if lx.eval1('select.symmetryState ?') == 'x':
	lx.eval('select.symmetryState none')
else:
	lx.eval('select.symmetryState x')
