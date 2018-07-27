
# http://stackoverflow.com/questions/15686501/qt-qtablewidget-column-resizing
import os
import atexit
# import datetime

import arrow
import traceback

import arkInit
arkInit.init()

import arkUtil
import settingsManager
globalSettings = settingsManager.globalSettings()

from knob import Knob
import translators
from translators import QtCore, QtGui
from translators import QtWebKit
from translators import QWebPage
from translators import QWebView
from translators import QtNetwork

try:
	from ftrack_connect.ui.widget.timer import Timer
	from ftrack_connect.ui.widget.web_view import WebViewWidget
	from ftrack_connect.connector import PanelComInstance
except:
	pass

# QtWebKit.QWebSettings.globalSettings().setAttribute(QtWebKit.QWebSettings.DeveloperExtrasEnabled, True)

class CookieJar(QtNetwork.QNetworkCookieJar):

	cookiesToIgnore = [
		'connect.sid'
	]

	def __init__(self, parent):
		super(CookieJar, self).__init__(parent)
		self.cookieFile = globalSettings.ARK_CONFIG + 'cookies.dat'
		self.cookiesToKeep = False

	def setCookieWhitelist(self, cookiesToKeep):
		self.cookiesToKeep = arkUtil.ensureArray(cookiesToKeep)

	def loadAll(self):
		print 'loading cookies'
		cookies = []
		try:
			with open(self.cookieFile, 'r') as f:
				for line in f:
					cookies += QtNetwork.QNetworkCookie.parseCookies(line)
			self.setAllCookies(cookies)
		except Exception as err:
			print 'Could not load cookies'
			print err

	def saveAll(self):
		print 'saving cookies'
		try:
			with open(self.cookieFile, 'w') as f:
				for cookie in self.allCookies():
					# if not cookie.isSessionCookie():
					if cookie.name() not in self.cookiesToIgnore and \
						(not self.cookiesToKeep or \
							cookie.name() in self.cookiesToKeep):
						f.write(cookie.toRawForm() + '\n')
		except Exception as err:
			print 'Could not save cookies'
			print err

	def removeAll(self):
		print 'removing cookies'
		try:
			os.remove(self.cookieFile)
		except Exception as err:
			print 'Could not remove cookies'
			print err


class WebPage(QWebPage):
	def javaScriptConsoleMessage(self, msg, line, source):
		source = source.split('/')[-1]
		print '\n%s %d: %s' % (source, line, msg)


class Web(Knob, translators.Events):

	useFullRow = True
	showLabel = False
	defaultOptions = {
		'url': 'http://google.com',
	}

	def __init__(self, name, value=None, options={}):
		super(Web, self).__init__(name, value, options)
		translators.Events.__init__(self)
		self.javascriptObjects = {}

	def setCookieWhitelist(self, cookiesToKeep):
		self.cookieJar.setCookieWhitelist(cookiesToKeep)

	def loadUrl(self, url):
		# print 'load:', url
		self.cookieJar.loadAll()
		url = QtCore.QUrl.fromUserInput(url)
		self.url = url.toString()
		self.widget.load(url)

	def onPageLoad(self, url):
		# print 'page loaded'
		frame = self.widget.page().mainFrame()
		for name, obj in self.javascriptObjects.iteritems():
			print 'adding:', name
			frame.addToJavaScriptWindowObject(name, obj)

		self.cookieJar.saveAll()
		self.cookies = self.widget.page().networkAccessManager().cookieJar().allCookies()
		self.emit('pageLoad', self.url)

	def addJavascriptObject(self, name, obj):
		# print 'adding js obj: ', obj
		self.javascriptObjects[name] = obj

	def getCookies(self):
		return self.cookies

	def createWidget(self):
		self.widget = QWebView()
		self.widget.settings().setAttribute(
			QtWebKit.QWebSettings.DeveloperExtrasEnabled,
			True)
		self.widget.setZoomFactor(4)
		self.widget.setTextSizeMultiplier(4)

		networkAccessManager = QtNetwork.QNetworkAccessManager()
		self.cookieJar = CookieJar(networkAccessManager)
		self.cookieJar.loadAll()
		networkAccessManager.setCookieJar(self.cookieJar)

		print 'making page'
		page = WebPage()
		page.setNetworkAccessManager(networkAccessManager)
		self.widget.setPage(page)
		print 'set page to :'
		print page
		self.widget.loadFinished.connect(self.onPageLoad)
		if 'url' in self.options and self.options['url']:
			self.loadUrl(self.options['url'])

	def updateWidgetValue(self):
		pass

	def setValueFromWidget(self):
		pass

class FtrackWebView(Knob):
	useFullRow = True
	showLabel = False

	def createWidget(self):
		try:
			if os.getenv('ARK_CURRENT_APP') == 'maya':
				from ftrack_connect_maya.connector import Connector
			elif os.getenv('ARK_CURRENT_APP') == 'nuke':
				from ftrack_connect_nuke.connector import Connector
			elif os.getenv('ARK_CURRENT_APP') == 'houdini':
				from ftrack_connect_houdini.connector import Connector
			else:
				raise Exception('invalid app:', os.getenv('ARK_CURRENT_APP'))
			self.connector = Connector()

			self.widget = WebViewWidget(self.parent)
			self.widget.setObjectName('webview')

			# make as large as possible
			self.sizePolicy = QtGui.QSizePolicy(
				QtGui.QSizePolicy.Expanding,
				QtGui.QSizePolicy.Expanding)
			self.widget.setSizePolicy(self.sizePolicy)

			self.homeTaskId = os.getenv('FTRACK_TASKID')
			self.setObject(self.homeTaskId)

			panelComInstance = PanelComInstance.instance()
			panelComInstance.addInfoListener(self.updateObj)
		except:
			pass

	def updateWidgetValue(self):
		pass

	def setObject(self, taskId):
		'''Set object to *taskId*.'''
		obj = self.connector.objectById(taskId)
		url = obj.getWebWidgetUrl('info', theme='tf')
		self.widget.setUrl(url)

	def updateObj(self, taskId):
		'''Update with *taskId*.'''
		self.setObject(taskId)

class FtrackTimer(Knob):

	TIMELOG_PROMPT = 10 * 60 * 1000

	def __init__(self, name, value=None, options={}):
		super(self.__class__, self).__init__(name, value=value, options=options)
		import arkFTrack
		self.pm = arkFTrack.getPM()
		self.widget = Timer()
		self.task = self.pm.getTask()

	def createWidget(self):
		self.subscriptionID = self.pm.registerListener(
			'topic=ftrack.update and source.user.username={0}'.format(
			self.pm.getUsername()
		), self.syncTimer, subscriber={'id': 'ftrack.update.timer.{}'.format(self.task['id'])})

		self.setTimeFromRemote()

		# can't make a new QtSignal for whatever reason so hijack one of Timer's unused ones! this is awful
		self.timerNeedsSync = self.widget.paused

		# timer widget does not talk to ftrack on its own, so connect signals
		self.widget.started.connect(self.startEvent)
		self.widget.stopped.connect(self.stopEvent)

		self.timerNeedsSync.connect(self.sync)

	def showError(self, errorMsg):
		self.errorMsg = QtGui.QMessageBox()
		self.errorMsg.setText(errorMsg)
		self.errorMsg.setWindowModality(QtCore.Qt.NonModal)
		self.errorMsg.setStandardButtons(QtGui.QMessageBox.Ok)
		self.errorMsg.setDefaultButton(QtGui.QMessageBox.Ok)
		self.errorMsg.setWindowFlags(self.errorMsg.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
		self.errorMsg.setAttribute(QtCore.Qt.WA_DeleteOnClose)

		self.errorMsg.show()

	# when widget started, tell pm to start timer
	def startEvent(self):
		if not self.pm.startTimer(user=None, context=self.task):
			self.stopEvent()
			self.showError('Error starting timer!')

	# when widget stopped, tell pm to stop timer and set widget counter to 0
	def stopEvent(self):
		self.pm.stopTimer(user=None, context=self.task)
		self.getTimer().clear()
		self.getTimer()._updateInterface()

	def setTimeFromRemote(self, force=False):
		try:
			# try to sync the timer value to the remote timer value
			remoteTimer = self.pm.getTimer()
			localTimer = self.getTimer()
			if force or (remoteTimer and remoteTimer.get('context').get('id') == self.task['id']):
				value = arrow.now() - remoteTimer['start']

				# ftrack server time isn't quite synced
				if value.days < 0:
					# if server time is negative, just use 0
					seconds = 0
				else:
					seconds = value.seconds

				print 'Setting local timer to {} seconds'.format(seconds)
				self.getTimer().setTime(seconds)

				# set hidden attributes to avoid emitting anything
				if not localTimer._state == localTimer.RUNNING:
					localTimer._startTimer()
					localTimer._state = localTimer.RUNNING

				localTimer._updateInterface()
		except:
			traceback.print_exc()

	def sync(self, start):
		localTimer = self.getTimer()
		localRunning = localTimer.state() == 'RUNNING'

		try:
			if start and not localRunning:
				print 'Starting timer'
				self.setTimeFromRemote()

			elif not start and localRunning:
				print 'Stopping timer'
				localTimer.stop()
				localTimer.clear()
				localTimer._updateInterface()
		except:
			pass

	def syncTimer(self, event):
		if not len(event['data']['entities']) or not event['data']['entities'][0]['entityType'] == 'timer':
			return

		localTimer = self.getTimer()
		remoteTimer = event['data']['entities'][0]
		remoteTask = remoteTimer['changes']['context_id']['new'] or remoteTimer['changes']['context_id']['old']

		localRunning = localTimer.state() == 'RUNNING'
		remoteRunning = remoteTimer['action'] == 'add'
		try:
			# timers match
			if remoteTask == self.task['id']:
				if remoteRunning and not localRunning:
					# this timer started remotely
					self.timerNeedsSync.emit(True)

				elif not remoteRunning and localRunning:
					# this timer stopped remotely
					self.timerNeedsSync.emit(False)

			# timers don't match
			else:
				if localRunning and remoteRunning:
					# remote timer is running on a different task, stop this timer
					self.timerNeedsSync.emit(False)

		except:
			pass

	def getTimer(self):
		return self.widget

	# ignore default knob update
	def updateWidgetValue(self):
		pass

	# ignore default knob update
	def setValueFromWidget(self):
		pass
