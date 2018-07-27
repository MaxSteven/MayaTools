import os
import inspect
import Qt

QtGui = None
QtCore = None
QtWebKit = None
QtNetwork = None
QtSignal = None
QtSlot = None
QEvent = None

if os.environ.get('ARK_CURRENT_APP') in ['houdini']:
	# IN CASE WE SWITCH TO Hutil QT build again
	# from hutil.PySide2 import QtCore, QtNetwork
	# from hutil.Qt import QtGui
	# from hutil.Qt.QtCore import Signal as QtSignal
	# from hutil.Qt.QtCore import Slot as QtSlot
	# from hutil.Qt.QtCore import QEvent
	# from hutil.Qt import QtWebKit
	# from hutil.Qt.QtWebKit import QWebView, QWebPage

	print 'Using PySide2 without QtWebKit :('
	from PySide2 import QtCore, QtNetwork
	from PySide2 import QtWidgets
	from PySide2 import QtGui
	for name in dir(QtWidgets):
		obj = getattr(QtWidgets, name)
		if inspect.isclass(obj):
			try:
				setattr(QtGui, name, obj)

			except:
				print "Couldn't setAttr: " + name

	from PySide2.QtCore import Signal as QtSignal
	from PySide2.QtCore import Slot as QtSlot
	from PySide2.QtCore import QEvent
	from PySide2.QtWebEngineWidgets import QWebEngineView as QWebView
	from PySide2.QtWebEngineWidgets import QWebEnginePage as QWebPage

	# from Qt.QtWebEngineWidgets import QWebEngineChannel as QWebChannel
	# from PySide2.QtWebEngineWidgets import QWebEngineSettings as QWebSettings

elif os.environ.get('ARK_CURRENT_APP') in ['nuke_cl', 'houdini_cl']:
	print 'Command line, using fake PyQt'
	class QtGui(object):
		QWidget = object
		QPushButton = object
		QLabel = object
		QDialog = object

	class QtSignal(object):
		QtSignal = object
		def __init__(self, *args):
			pass

	class QEvent(object):
		QEvent = object

	class QtCore(object):
		QtCore = object

	class QtNetwork(object):
		QNetworkCookieJar = object

	class fakeQWebSettings(object):
		pass
		# globalSettings = fakeGlobalSettings()

	class QtWebKit(object):
		QtWebKit = object
		# QWebSettings = fakeQWebSettings()

	class QWebPage(object):
		QWebPage = object

	class QWebView(object):
		QWebView = object

else:
	print 'Using Qt'
	import Qt
	from Qt import QtGui, QtCore
	from Qt import  QtNetwork
	try:
		from Qt import QtWebKit
		from Qt.QtWebKit import QWebView, QWebPage

	except ImportError as err:
		del QtWebKit
		print 'Importing QtWebEngineWidgets'
		from Qt import QtWebKitWidgets as QtWebKit
		from Qt.QtWebKitWidgets import QWebView
		from Qt.QtWebKitWidgets import QWebPage
		# from Qt.QtWebKit import QWebEngineChannel as QWebChannel
		# from Qt.QtWebKit import QWebEngineSettings as QWebSettings

		from Qt import QtWidgets
		for name in dir(QtWidgets):
			obj = getattr(QtWidgets, name)
			if inspect.isclass(obj):
				try:
					setattr(QtGui, name, obj)

				except:
					print obj
					print "Couldn't setAttr: " + name


	from Qt.QtCore import Signal as QtSignal
	from Qt.QtCore import Slot as QtSlot
	from Qt.QtCore import QEvent
