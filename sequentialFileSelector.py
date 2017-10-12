#!urs/bin/python

import sys
import os
import PySide.QtCore as qc
import PySide.QtGui as qg
fileRoot = 'sequenceFileSelector/'

class SequentialFileSelector():
	def __init__(self):
		self.app = qg.QApplication(sys.argv)
		self.filesList = []
		self.folderPath = fileRoot
		self.mainDialog = qg.QDialog()
		self.mainLayout = qg.QVBoxLayout()
		self.mainDialog.setLayout(self.mainLayout)
		self.mainDialog.setWindowTitle("Sequential File Selector")
		self.fileListWidget = qg.QListWidget()
		self.fileListWidget.setSelectionMode(qg.QAbstractItemView.ExtendedSelection)
		self.mainLayout.addWidget(self.fileListWidget)
		self.buttonLayout = qg.QHBoxLayout()
		self.chooseButton = qg.QPushButton("Choose Folder")
		self.buttonLayout.addWidget(self.chooseButton)
		self.chooseButton.clicked.connect(self.chooseFolder)
		self.printButton = qg.QPushButton("Print Files")
		self.buttonLayout.addWidget(self.printButton)
		self.printButton.clicked.connect(self.printFiles)
		self.cancelButton = qg.QPushButton("Cancel")
		self.cancelButton.clicked.connect(self.cancel)
		self.buttonLayout.addWidget(self.cancelButton)
		self.mainLayout.addLayout(self.buttonLayout)
		self.mainDialog.show()
		sys.exit(self.app.exec_())

	def chooseFolder(self):
		self.folderPath = QtGui.QFileDialog.askdirectory(initialdir = fileRoot)
		try:
			filesList = [f for f in os.listdir(self.folderPath) if os.path.isfile(os.path.join(self.folderPath, f))]
		except:
			print("Cancelled operation!")
			return

		filesList.sort()
		i = 0
		collapsedList = []

		i = 0
		# New Logic to rename sequential files in QList
		# [abc_xyz.1001.png, abc_xyz.1002.png]
		while i < len(fileList):
			# [abc_xyz][1001][png]
			fileSections = fileList[i].split('.')

			# check if name is not an image sequence
			if len(fileSections) <= 2:
				collapsedList.append(fileList[i])
				i += 1
			else:
				try:
					# check if second last piece is a number or not
					int(fileSections[-2])

					# leftFileSection = [abc_xyz]
					leftFileSection = fileSections[0]

					# rightFileSection = [png]
					rightFileSection = fileSections[2]
					
					j = i

					# keep incrementing second loop till left and right sections are the same
					while j < len(fileList) and \
						leftFileSection == fileSections[0] and \
						rightFileSection == fileSections[2]:
						j += 1
						try:
							# [abc_xyz][1002][png]
							newFilePieces = fileList[j].split('.')

							# [abc_xyz]
							leftFileSection = newFilePieces[0]

							# [png]
							rightFileSection = newFilePieces[2]
						except IndexError:
							pass

					lastFrame = j
					collapsedList.append(fileSections[0] +
										'.%0' + str(len(fileSections[1])) + 'd.' +
										fileSections[2] + ' ' +
										str(int(fileSections[-2])) + '-' +
										str(int(fileSections[-2]) + lastFrame - i - 1))
					i = j

				except ValueError:
					collapsedList.append(fileList[i])
					i += 1

		self.fileListWidget.addItems(self.collapsedList)

	def printFiles(self):
		messageBox = qg.QMessageBox()
		selectedFiles = []
		if not self.fileListWidget.selectedItems():
			print("No files selected!")
			return
		for f in self.fileListWidget.selectedItems():
			if "%" in f.text():
				sequenceFileComponents = f.text().split("%")
				baseName = sequenceFileComponents[0]
				secondHalf = sequenceFileComponents[1]
				extension = secondHalf.rpartition(".")[2].split()[0]
				for File in os.listdir(self.folderPath):
					if baseName in File and extension in File:
						selectedFiles.append(File)

			else:
				selectedFiles.append(f.text())

		fileText = "Following files selected:"
		
		for f in selectedFiles:
			fileText += " " + f + " "
		
		messageBox.setText(fileText)
		messageBox.exec_()
		
	def cancel(self):
		self.mainDialog.close()

def main():
	tool = SequentialFileSelector()

if __name__=="__main__":main()