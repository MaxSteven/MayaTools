import sys

from translators import QtGui, QtCore

class Command(object):
	def __init__(self, name, function, shortcut):
		self.name = name
		self.function = function
		shortcut = shortcut.lower()

		ctrlPressed = shiftPressed = altPressed = False
		if 'ctrl' in shortcut:
			ctrlPressed = True
		if 'alt' in shortcut:
			altPressed = True
		if 'shift' in shortcut:
			shiftPressed = True

		shortcut = shortcut.replace(' ','')
		shortcut = shortcut.replace('ctrl','')
		shortcut = shortcut.replace('shift','')
		shortcut = shortcut.replace('alt','')
		shortcut = shortcut.replace('+','')

		self.shortcut = shortcut
		# done in reverse order to maintain ctrl + alt + shift modifier ordering
		if shiftPressed:
			self.shortcut = 'shift+'+ self.shortcut
		if altPressed:
			self.shortcut = 'alt+' + self.shortcut
		if ctrlPressed:
			self.shortcut = 'ctrl+' + self.shortcut

	def execute(self):
		self.function()

class Example(QtGui.QMainWindow):

	def __init__(self):
		super(Example, self).__init__()

		self.commands = {}
		self.keyCodes = {}
		for enum in dir(QtCore.Qt):
			if 'Key_' in enum:
				self.keyCodes[int(getattr(QtCore.Qt,enum))] = enum.replace('Key_','').lower()

		self.registerCommand('test',self.test,'b')
		self.registerCommand('test',self.test,'Ctrl + Shift + v')
		self.registerCommand('test',self.test,'Alt + ctrl+n')

		self.initUI()

	def initUI(self):
		self.keyCode = QtGui.QLabel(self)
		self.keyCode.move(30,30)

		self.ctrlPressed = False
		self.shiftPressed = False
		self.altPressed = False

		self.setGeometry(300, 300, 300, 150)
		self.setWindowTitle('Key Codes')
		self.show()

	def registerCommand(self, name, function, shortcut):
		newCommand = Command(name, function, shortcut)
		self.commands[newCommand.shortcut] = newCommand

	def test(self):
		print 'works'

	def keyReleaseEvent(self, e, context=None):
		if e.key() == QtCore.Qt.Key_Control:
			self.ctrlPressed = False
			return
		if e.key() == QtCore.Qt.Key_Shift:
			self.shiftPressed = False
			return
		if e.key() == QtCore.Qt.Key_Alt:
			self.altPressed = False
			return

	def keyPressEvent(self, e):

		if e.key() == QtCore.Qt.Key_Control:
			self.ctrlPressed = True
			return
		if e.key() == QtCore.Qt.Key_Shift:
			self.shiftPressed = True
			return
		if e.key() == QtCore.Qt.Key_Alt:
			self.altPressed = True
			return


		if e.key() not in self.keyCodes:
			print 'could not find pressed key'
			return

		shortcut = self.keyCodes[e.key()]

		# done in reverse order to maintain ctrl + alt + shift modifier ordering
		if self.shiftPressed:
			shortcut = 'shift+'+ shortcut
		if self.altPressed:
			shortcut = 'alt+' + shortcut
		if self.ctrlPressed:
			shortcut = 'ctrl+' + shortcut

		# if we find a command for the shortcut we pressed, run it
		if shortcut in self.commands:
			self.commands[shortcut].execute()

		# elif e.key() > 47 and e.key() < 58:
		# 	key = str(e.key() - 48)
		# elif e.key() > 64 and e.key() < 91:
		# 	letters = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
		# 	# self.keyCode.setText(str(e.key()))
		# 	key = letters[e.key()-65]
		# else:
		# 	key = e.key()

		# shortcut = key.lower()
		# for c in self.commands:
		# 	if c.shortcut == shortcut:
		# 		c.execute()

	def mousePressEvent(self, e):
		pass

def main():

	app = QtGui.QApplication(sys.argv)
	ex = Example()
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()
