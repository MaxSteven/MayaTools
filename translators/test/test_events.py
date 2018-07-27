
# Standard modules
from expects import *
import time

# Our modules
import arkInit
arkInit.init()

import tryout
from translators import Events

class test(tryout.TestSuite):

	def on(self, done):
		events = Events()

		def emitted():
			done()

		events.on('thing', emitted)
		events.emit('thing')

	def on_with_event(self, done):
		events = Events()

		def emitted(arg):
			expect(arg).to(equal('test'))
			done()

		events.on('thing', emitted)
		events.emit('thing', 'test')

	def on_with_kwargs(self, done):
		events = Events()

		def emitted(arg, some=False):
			expect(arg).to(equal('test'))
			expect(some).to(equal('thing'))
			done()

		events.on('thing', emitted)
		events.emit('thing', 'test', some='thing')

	def once(self, done):
		events = Events()

		self.calls = 0

		def emitted():
			self.calls += 1

		events.once('thing', emitted)
		events.emit('thing')
		events.emit('thing')
		events.emit('thing')
		expect(self.calls).to(equal(1))
		done()

	def off_all(self, done):
		events = Events()

		def emitted():
			raise Exception("shouldn't be called")

		events.on('thing', emitted)
		events.off('thing')
		events.emit('thing')
		done()

	def off_specific(self, done):
		events = Events()

		def emitted():
			print 'fine'

		def nope():
			raise Exception("shouldn't be called")

		events.on('thing', emitted)
		events.on('thing', nope)
		events.off('thing', nope)
		events.emit('thing')
		done()

	def delayedCallback(self, done):
		events = Events()

		def emitted():
			done()

		events.on('thing', emitted)
		time.sleep(2)
		events.emit('thing')

if __name__ == '__main__':
	tryout.run(test)
