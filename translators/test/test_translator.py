
# Standard modules
from expects import *
import time

# Our modules
import arkInit
arkInit.init()

import tryout
import translators

class test(tryout.TestSuite):
	title = 'test/test_translator.py'

	# Basics
	##################################################
	def set_options(self):
		translator = translators.getCurrent()
		translator.setOptions(sup='yes', x=12)
		self.assertEqual(translator.getOption('sup'), 'yes')
		self.assertEqual(translator.getOption('x'), 12)
		self.assertIn('sup', translator.getOptions())
		self.assertIn('x', translator.getOptions())

	def set_reuseCurrentTranslator(self):
		translator = translators.getCurrent()
		translator.setOptions(sup='yes', x=12)

		newTranslator = translators.getCurrent()
		self.assertEqual(newTranslator.getOption('sup'), 'yes')
		self.assertEqual(newTranslator.getOption('x'), 12)
		self.assertIn('sup', newTranslator.getOptions())
		self.assertIn('x', newTranslator.getOptions())

	# Events
	##################################################
	def on(self, done):
		translator = translators.getCurrent()
		translator.off()

		def emitted():
			done()

		translator.on('thing', emitted)
		translator.emit('thing')

	def on_with_event(self, done):
		translator = translators.getCurrent()
		translator.off()

		def emitted(arg):
			expect(arg).to(equal('test'))
			done()

		translator.on('thing', emitted)
		translator.emit('thing', 'test')

	def on_with_kwargs(self, done):
		translator = translators.getCurrent()
		translator.off()

		def emitted(arg, some=False):
			expect(arg).to(equal('test'))
			expect(some).to(equal('thing'))
			done()

		translator.on('thing', emitted)
		translator.emit('thing', 'test', some='thing')

	def once(self, done):
		translator = translators.getCurrent()
		translator.off()

		self.calls = 0

		def emitted():
			self.calls += 1

		translator.once('thing', emitted)
		translator.emit('thing')
		translator.emit('thing')
		translator.emit('thing')
		expect(self.calls).to(equal(1))
		done()

	def off_all(self, done):
		translator = translators.getCurrent()
		translator.off()

		def emitted():
			raise Exception("shouldn't be called")

		translator.on('thing', emitted)
		translator.off('thing')
		translator.emit('thing')
		done()

	def off_specific(self, done):
		translator = translators.getCurrent()
		translator.off()

		def emitted():
			print 'fine'

		def nope():
			raise Exception("shouldn't be called")

		translator.on('thing', emitted)
		translator.on('thing', nope)
		translator.off('thing', nope)
		translator.emit('thing')
		done()

	def delayed_callback(self, done):
		translator = translators.getCurrent()
		translator.off()

		def emitted():
			done()

		translator.on('thing', emitted)
		time.sleep(1)
		translator.emit('thing')

	# PySide
	##################################################
	def get_qt(self):
		translators.QtGui
		translators.QtCore

		self.assertTrue(translators.QtGui is not None)
		self.assertTrue(translators.QtCore is not None)

if __name__ == '__main__':
	tryout.run(test)
