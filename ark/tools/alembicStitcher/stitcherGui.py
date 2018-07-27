

import sys
import os

import Queue
import threading

import arkInit
arkInit.init()

import translators
translator = translators.getCurrent()
from translators import QtGui, QtCore

import stitcher

# fix: add this to cOS if we use it a lot
def queueOutput(out, outQueue):
	if out:
		for line in iter(out.readline, ''):
			outQueue.put(line)
		out.close()

class AlembicStitcher(QtGui.QDialog):

	def __init__(self, parent=None):
		super(AlembicStitcher, self).__init__(parent)

		self.inputRoot = 'R:/'
		self.inputFile = False
		self.outputPath = False
		self.inputFile = 'R:/Salem/Workspaces/SLM_0090/FX/SLM_0090_v28a/Tar/Mesh_SLM_0090_tar_28a*.abc'
		self.outputPath = 'R:/Salem/Workspaces/SLM_0090/FX/tar_v028a.abc'

		self.inputButton = QtGui.QPushButton('Browse...', self)
		self.inputButton.clicked.connect(self.getFiles)

		self.outputButton = QtGui.QPushButton('Browse...', self)
		self.outputButton.clicked.connect(self.getOutputPath)

		stitchButton = QtGui.QPushButton('Stitch', self)
		stitchButton.clicked.connect(self.stitch)

		form = QtGui.QFormLayout()
		form.setLabelAlignment(QtCore.Qt.AlignRight)
		form.setVerticalSpacing(10)

		form.addRow('Files:', self.inputButton)
		form.addRow('Output:', self.outputButton)
		form.addRow('', stitchButton)

		self.setLayout(form)

		self.setGeometry(300, 300, 250, 100)
		self.setWindowTitle('Shepherd Submit')
		self.show()

	def getFiles(self):
		inputFile = QtGui.QFileDialog.getOpenFileName(
			self,
			'Select Any Alembic Frame',
			self.inputRoot,
			'Alembic Files (*.abc)')

		inputFile = str(inputFile[0])

		if not os.path.isfile(inputFile):
			self.inputFile = False
			self.inputButton.setText('Browse...')
			return

		inputFile = '.'.join(inputFile.split('.')[:-2]) + '*.abc'
		print inputFile
		self.inputRoot = os.path.dirname(inputFile)
		self.inputFile = inputFile
		self.inputButton.setText(self.inputFile)

	def getOutputPath(self):
		outputPath = QtGui.QFileDialog.getSaveFileName(
			self,
			'Select Stitched Output Path',
			self.inputRoot,
			'Alembic Files (*.abc)')

		outputPath = str(outputPath[0])

		if not os.path.isdir(os.path.dirname(outputPath)):
			self.outputPath = False
			self.outputButton.setText('Browse...')
			return

		print outputPath
		self.inputRoot = os.path.dirname(outputPath)
		self.outputPath = outputPath
		self.outputButton.setText(self.outputPath)

	def stitch(self):
		if not (self.inputFile and self.outputPath):
			msgBox = QtGui.QMessageBox()
			msgBox.setText('Invalid file paths chosen')
			msgBox.exec_()
			return

		self.progress = 0
		self.progressBar = QtGui.QProgressDialog(
			'Stitching files...',
			'Cancel',
			0, 100, self)
		self.progressBar.setWindowModality(QtCore.Qt.WindowModal)

		self.process = stitcher.stitch(self.inputFile, self.outputPath, self)

		self.out = ''
		self.err = ''

		self.outQueue = Queue.Queue()
		self.processThread = threading.Thread(
			target=queueOutput,
			args=(self.process.stdout, self.outQueue))
		# thread dies with the program
		self.processThread.daemon = True
		self.processThread.start()

		self.errQueue = Queue.Queue()
		errProcessThread = threading.Thread(
			target=queueOutput,
			args=(self.process.stderr, self.errQueue))
		errProcessThread.daemon = True
		errProcessThread.start()

		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.updateProgress)
		self.timer.start(100)

	def getProcessOutput(self):
		try:
			newOut = self.outQueue.get_nowait()
			print(newOut[:-1])
			self.out += newOut
		except:
			pass

		try:
			newErr = self.errQueue.get_nowait()
			print('\n####################################\n\
#############  ERROR:  #############\n\
####################################')

			print(newErr[:-1] + '\n\n')
			self.err += newErr
		except:
			pass

	def updateProgress(self):
		if self.process.is_running():
			self.getProcessOutput()
			self.progressBar.setValue(self.progress % 99)
			self.progress += 1
		else:
			self.doneStitching(True)

		if self.progressBar.wasCanceled():
			self.doneStitching()

	def doneStitching(self, result=False):
		self.timer.stop()
		self.progressBar.setValue(100)

		sys.stdout.flush()
		sys.stderr.flush()

		self.getProcessOutput()

		if result:
			self.inputFile = False
			self.outputPath = False
			self.inputButton.setText('Browse...')
			self.outputButton.setText('Browse...')

			msgBox = QtGui.QMessageBox()
			if not self.err:
				msgBox.setText('Stitching process successful')
			else:
				msgBox.setText('Stitching errors: ' + self.err)
			msgBox.exec_()
		else:
			msgBox = QtGui.QMessageBox()
			msgBox.setText('Stitching canceled')
			msgBox.exec_()


def stitch(files, output):
	pass


def main():
	app = QtGui.QApplication(sys.argv)
	ex = AlembicStitcher()
	sys.exit(app.exec_())


if __name__ == '__main__':
	main()
