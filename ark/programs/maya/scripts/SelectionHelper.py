# import pymel.core as pm

import arkInit
arkInit.init()
import translators
translator = translators.getCurrent()
from translators import QtGui, QtCore

class SelectionHelpers(QtGui.QDialog):
	def __init__(self, parent=None, **kwargs):
		super(SelectionHelpers, self).__init__(parent)

		grid = QtGui.QGridLayout()
		grid.setVerticalSpacing(10)

		self.polycountEdit = QtGui.QSpinBox(minimum=0,
											maximum=100000000,
											singleStep=1000,
											value=10000)
		self.selectByFaceCountButton = QtGui.QPushButton('Select By Face Count')
		self.selectByFaceCountButton.clicked.connect(self.selectByFaceCount)

		grid.addWidget(self.polycountEdit, 1, 0)
		grid.addWidget(self.selectByFaceCountButton, 1, 1)

		self.setLayout(grid)

		self.setGeometry(300, 300, 350, 100)
		self.setWindowTitle('Selection Helpers')
		self.show()

	def selectByFaceCount(self):
		faceThreshold = int(self.polycountEdit.value())

		nodesToSelect = []

		meshes = pm.ls(type='mesh')
		for mesh in meshes:
			if mesh.numFaces() > faceThreshold:
				nodesToSelect.append(mesh)

		pm.select(nodesToSelect)


def launch(*args, **kwargs):
	translator.launch(SelectionHelpers, *args, **kwargs)

if __name__ == '__main__':
	launch()
