
class Events(object):
	'''
	Simple events system that runs callbacks when a
	specified event is emitted.
	'''

	def __init__(self):
		self.events = {}

	def emit(self, eventName, *args, **kwargs):
		'''
		Runs all callbacks associated with the
		specified eventName
		'''
		if eventName not in self.events:
			return

		i = 0
		numEvents = len(self.events[eventName])
		while i < numEvents:
			self.events[eventName][i]['callback'](*args, **kwargs)

			if 'once' in self.events[eventName][i] and self.events[eventName][i]['once']:
				del self.events[eventName][i]
				numEvents -= 1
				i -= 1

			i += 1

	def on(self, eventName, callback, **kwargs):
		'''
		Runs callback when eventName is emitted, but only once
		'''
		# set events to an empty array if it's not already
		if eventName not in self.events:
			self.events[eventName] = []

		kwargs['callback'] = callback

		self.events[eventName].append(kwargs)

	def once(self, eventName, callback, **kwargs):
		'''
		Runs callback when eventName is emitted, but only once
		'''
		kwargs['once'] = True
		self.on(eventName, callback, **kwargs)

	def off(self, eventName=None, callback=None):
		'''
		When given a callback, removes that callback from the
		specified eventName, otherwise removes all callbacks
		from the specified eventName
		'''

		# if no event name, remove all callbacks
		if not eventName:
			self.events = {}
			return

		# bail if we don't have any callbacks for that event
		if eventName not in self.events or \
			len(self.events[eventName]) == 0:
			return

		# if we're not looking for a specific callback
		# then empty all the callbacks for that eventName
		if not callback:
			del self.events[eventName]
			return

		# otherwise find the specific callback we're looking
		# for and remove it

		i = 0
		numCallbacks = len(self.events[eventName])
		while i < numCallbacks:
			if self.events[eventName][i]['callback'] == callback:
				del self.events[eventName][i]
				i -= 1
				numCallbacks -= 1
			i += 1




if __name__ == '__main__':
	help(Events)
