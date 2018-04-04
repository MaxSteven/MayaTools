from PyQt4 import QtGui

import sys

if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	screenShotPixmap = QtGui.QPixmap()
	img = screenShotPixmap.grabWindow(QtGui.QApplication.desktop().winId(), x = 1206, y = 672, width = 183, height = 717)
	img.save('C:/rigTestFolder/screenTest.png')

	sys.exit(app.exec_())
