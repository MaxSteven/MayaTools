# python

import os
import sys

from StringIO import StringIO
import traceback
import lx
import lxu.command


class LaunchScript(lxu.command.BasicCommand):

	def __init__(self):
		lxu.command.BasicCommand.__init__(self)

		# define path as a require string parameter
		self.dyna_Add('Script', lx.symbol.sTYPE_STRING)

	def basic_Execute(self, msg, flags):
		scriptPath = self.dyna_String(0)

		try:
			with open(scriptPath) as f:
				text = f.read()
		except Exception:
			result = traceback.format_exc()
			return self.showResult(result)

		# fix syntax error if last line is a comment with no new line
		if not text.endswith('\n'):
			text = text + '\n'

		# compile
		result = None
		compileSuccess = False

		try:
			scriptType = 'exec'
			if text.count('\n') == 1:
				scriptType = 'single'
			compiled = compile(text, '<string>', scriptType)
			compileSuccess = True
		except Exception:
			result = traceback.format_exc()
			compileSuccess = False

		oldStdOut = sys.stdout

		if compileSuccess :
			# override stdout to capture exec results
			outBuffer = StringIO()
			sys.stdout = outBuffer

			try:
				# set expected python magic variables
				context = globals()
				context['__file__'] = scriptPath
				context['__name__'] = '__main__'
				sys.argv = [scriptPath]

				# append the dirname to path so we can require files like normal
				sys.path.append(os.path.dirname(scriptPath))

				exec(compiled, context)
			except Exception:
				# remove refernces to this command and the calling scripteditor host
				# script from the traceback output
				formatted_lines = traceback.format_exc().splitlines()
				formatted_lines.pop(2)
				formatted_lines.pop(1)
				result = '\n'.join(formatted_lines)
			else:
				result = outBuffer.getvalue()

		sys.stdout = oldStdOut

		self.showResult(result)

	def showResult(self, result):
		print 'Script Result: \n'
		print result




def main():
	lx.bless(LaunchScript, 'launchScript')

main()
