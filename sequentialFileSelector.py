#!urs/bin/python
import sys
import os
from tkinter import filedialog
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
        self.folderPath = filedialog.askdirectory(initialdir = fileRoot)
        try:
            filesList = [f for f in os.listdir(self.folderPath) if os.path.isfile(os.path.join(self.folderPath, f))]
        except:
            print("Cancelled operation!")
            return

        filesList.sort()
        i = 0
        # New Logic to rename sequential files in QList
        while i < len(filesList):
            filePieces = filesList[i].split(".")
            if len(filePieces) <= 2:
                self.filesList.append(filesList[i])
                i+=1
            else:
                try:
                    int(filePieces[-2])
                    fileSections = filesList[i].partition(filePieces[-2])
                    leftFileSection = fileSections[0]
                    rightFileSection = fileSections[2]
                    j = i
                    while j<len(filesList) and leftFileSection == fileSections[0] and rightFileSection == fileSections[2]:
                        j+=1
                        try:
                            filePiece = filesList[j].split(".")[-2]
                            newFileSections = filesList[j].partition(filePiece)
                            leftFileSection = newFileSections[0]
                            rightFileSection = newFileSections[2]
                        except IndexError:
                            print("Done!")

                    self.filesList.append(fileSections[0]+"%0"+str(len(fileSections[1]))+fileSections[2]+ " " + str(int(filePieces[-2])) +"-"+str(int(filePieces[-2])+j-i-1))
                    i = j
                
                except ValueError:
                    self.filesList.append(filesList[i])
                    i+=1

                # OLD LOGIC
                    # j = i
                    # filePiece = filePieces[]
                    # print(filePiece)
                    # while filePiece == filePieces[0]:
                    #     filePiece = filesList[j].rsplit(".")[0]
                    #     print(j)
                    #     if j > range(len(filesList) - 1):
                    #         return
                    #     j += 1
                    # 
                    # print(i)
                    # i = j

        print(self.filesList)
        self.fileListWidget.addItems(self.filesList)

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

                # OLD LOGIC: 
                # Abandoned because it won't work in case sequence numbers are not sequential like split.001 and split.003 
                # padding = int(secondHalf.partition(".")[0])
                # pad = ""
                # i = 0
                # while i-1<padding:
                #     pad += "0"
                #     i += 1
                
                # indexRange = secondHalf.rpartition(".")[2].split()[1]
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