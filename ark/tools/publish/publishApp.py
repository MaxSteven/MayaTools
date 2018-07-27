
import json
import urllib

import arkInit
arkInit.init()

import translators
translator = translators.getCurrent()
# from translators import QtGui
# from translators import QtCore

import steppedGui
import publishGui
import publishMultiGui
import publishWebGui

caretakerRoot = '127.0.0.1/'

class PublishApp(steppedGui.SteppedGui):

	def postShow(self):
		# new asset
		if self.options['mode'] == 'new':
			options = publishWebGui.options
			options['title'] = 'Select Program'
			options['knobs'][0]['url'] = caretakerRoot + 'publish/selectProgram'
			self.addStep({
					'widget': publishWebGui.WebGui(self, options),
					'callback': self.createAsset
				})

		# open asset
		elif self.options['mode'] == 'open':
			options = publishWebGui.options
			options['title'] = 'Open Asset'
			options['knobs'][0]['url'] = caretakerRoot + 'publish/selectAsset'
			self.addStep({
					'widget': publishWebGui.WebGui(self, options),
					'callback': self.createAsset
				})

		# single publish
		elif self.options['mode'] == 'publish':
			self.addStep({
					'widget': publishGui.gui(self),
					'callback': self.publishType
				})

		# multi publish
		elif self.options['mode'] == 'publishMulti':
			self.addStep({
					'widget': publishMultiGui.gui(self),
					'callback': self.multiPublishType
				})


		self.showStep()

	def createAsset(self):
		print 'createAsset()'

	def publishType(self, data):
		# print data
		options = publishWebGui.options
		options['title'] = 'Publish Type'

		# build the url
		url = caretakerRoot + 'publish/selectType?'
		webData = {
			'files': json.dumps(data['files'])
		}
		print webData
		url += urllib.urlencode(webData)

		options['knobs'][0]['url'] = url
		self.addStep({
			'widget': publishWebGui.WebGui(self, options),
			'callback': self.postPublish
			})
		self.next()

	def multiPublishType(self, data):
		# print data
		options = publishWebGui.options
		options['title'] = 'Asset Types'

		# build the url
		url = caretakerRoot + 'publish/newAssets?'
		webData = {
			'files': json.dumps(data['files'])
		}
		print webData
		url += urllib.urlencode(webData)

		options['knobs'][0]['url'] = url
		self.addStep({
			'widget': publishWebGui.WebGui(self, options),
			'callback': self.postPublish
			})
		self.next()

	def postPublish(self, data):
		print 'postMultiPublish()'
		print 'data:', data

	def postMultiPublish(self, data):
		print 'postMultiPublish()'
		print 'data:', data






options = {
		'margin': '0 0 0 0',
		# 'x': 100,
		# 'y': 100,
	}




def main(parent=None, newWindow=False, mode='new'):
	options['mode'] = mode
	translator.launch(PublishApp,
		parent=parent,
		options=options,
		newWindow=newWindow)


if __name__ == '__main__':
	main()
