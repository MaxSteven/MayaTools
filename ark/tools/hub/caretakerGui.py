
import json

import arkInit
arkInit.init()
import os
import cOS
import shutil
import subprocess
import time

import settingsManager
globalSettings = settingsManager.globalSettings()

import translators
translator = translators.getCurrent()
# from translators import QtGui
from translators import QtCore
from translators import QtSlot

import baseWidget



url = 'http://' + globalSettings.DATABASE_ROOT
if globalSettings.DATABASE_PORT != '80':
	url += ':' + globalSettings.DATABASE_PORT
# url += '/login'

options = {
	'title': 'Caretaker: Hub',
	'width': 1280,
	'height': 800,
	# 'x': 100,
	# 'y': 100,
	'margin': '0 0 0 0',
	'knobs': [
		{
			'name': 'web',
			'dataType': 'Web',
			'url': url,
		},
	]
}


class AppHelper(QtCore.QObject):

	def __init__(self, parent=None):
		super(AppHelper, self).__init__(parent)

	@QtSlot(str)
	def log(self, text):
		print text

	@QtSlot()
	def back(self):
		self.parent().parent().back()

	@QtSlot(str)
	def submit(self, data):
		self.parent().submit(json.loads(data))


class LocalStorage(QtCore.QObject):
	pass

# File system operations for asset manager
class AssetHelper(QtCore.QObject):

	def __init__(self, parent=None):
		super(AssetHelper, self).__init__(parent)

	@QtSlot(str, str)
	def launchFile(self, exe, path):
		# maybe add timeout
		while not os.path.exists(path):
			time.sleep(1)

		if os.path.isfile(path):
			cmd = exe + ' ' + path
			print cmd.split(' ')
			subprocess.Popen(cmd.split(' '))
		else:
			raise ValueError("%s isn't a file" % path)

	@QtSlot(str, str)
	def fileExists(self, path, extension):
		fileIncludes = ['*.' + extension]
		print cOS.getFiles(path, fileIncludes)
		return len(cOS.getFiles(path, fileIncludes)) > 0

	@QtSlot(str, str)
	def initializeFile(self, sourceFile, path):
		try:
			os.makedirs('/'.join(path.split('/')[0:-1]))
		except:
			pass
		if os.path.isfile(path):
			raise Exception('destination file exists: ' + path)
		if not os.path.isfile(sourceFile):
			raise Exception('source file does not exist: ' + sourceFile)
		shutil.copy2(sourceFile, path)

	@QtSlot()
	def test(self):
		path = 'R:/Test_Project/Workspaces/GF4_402/GF4_402_0210/Comp/'
		ext = '.nk'
		fileIncludes = ['*' + ext]
		# print cOS.getFiles(path)
		print cOS.getFiles(path, fileIncludes)
		return cOS.getFiles(path, fileIncludes)

class WebGui(baseWidget.BaseWidget):

	defaultOptions = {
		'minimize': True,
		'maximize': True,
	}

	def postShow(self):
		self.appHelper = AppHelper(self)
		self.getKnob('web').setCookieWhitelist(['oauthToken'])
		self.getKnob('web').addJavascriptObject('appHelper', self.appHelper)

		self.localStorage = LocalStorage(self)
		self.getKnob('web').addJavascriptObject('localStorage', self.localStorage)
		# self.getKnob('web').linkClicked.connect(self.onLinkClicked)
		self.getKnob('web').on('pageLoad', self.onPageLoad)

		self.assetHelper = AssetHelper(self)
		self.getKnob('web').addJavascriptObject('assetHelper', self.assetHelper)
		print self.options['maximize']

	# def onLinkClicked(self, url):
		# print 'clicked:', url
	# 	if 'logout' in url:
	# 		self.getKnob('web').removeCookies()

	def onPageLoad(self, url):
		print 'loaded:', url
		cookies = self.getKnob('web').getCookies()
		for cookie in cookies:
			if cookie.name() == 'oauthToken':
				try:
					with open(globalSettings.ARK_CONFIG + 'key.user.dat', 'w') as f:
						f.write(cookie.value())
					print 'oauthToken saved:', cookie.value()
				except Exception as err:
					print 'Error saving oauthToken:'
					print err


def gui():
	return WebGui(options=options)

def main():
	translator.launch(WebGui, options=options)

if __name__ == '__main__':
	main()
