## INTERACTIVE ROLLING CHASSIS MODELLING AND AUTO-RIGGING TOOL
## Made by Shobhit Khinvasaara
## MFA thesis project.
## Date: 08/08/2016

#################################################################################################
## Store WheelAxle.ma and Frame.ma in your D drive before you run this program
## run directly or add to shelf.



import PySide.QtCore as qc
import PySide.QtGui as qg

import maya.cmds as mc

import re

class Main_UI(qg.QDialog):
	def __init__(self):
		qg.QDialog.__init__(self)
		self.setWindowFlags(qc.Qt.WindowStaysOnTopHint)
		self.setWindowTitle("Chassis Modeling")

		self.setLayout(qg.QVBoxLayout())
		self.layout().setContentsMargins(5,5,5,5)
		self.layout().setSpacing(5)

		RenameLayout = qg.QHBoxLayout()
		self.layout().addLayout(RenameLayout)

		self.RenameButton = qg.QPushButton("Rename")
		self.RenameTextBox = qg.QLineEdit()
		self.RenameButton.clicked.connect(self.renameComponent)
		RenameLayout.addWidget(self.RenameButton)
		RenameLayout.addWidget(self.RenameTextBox)

		AxleFrameListLayout = qg.QHBoxLayout()
		self.layout().addLayout(AxleFrameListLayout)

		FunctionsTab = qg.QTabWidget()
		self.layout().addWidget(FunctionsTab)

		GeneralFunctionsLayout = qg.QHBoxLayout()
		self.layout().addLayout(GeneralFunctionsLayout)

		AxleListLayout = qg.QVBoxLayout()
		AxleFrameListLayout.addLayout(AxleListLayout)

		FrameListLayout = qg.QVBoxLayout()
		AxleFrameListLayout.addLayout(FrameListLayout)

		self.WheelAxleObjectList = []
		self.WheelAxleNameList = []

		self.FrameObjectList = []
		self.FrameNameList = []

		self.WheelAxleListWidget = qg.QListWidget(self)
		self.WheelAxleListWidget.setSelectionMode(qg.QAbstractItemView.ExtendedSelection)
		self.WheelAxleListWidget.itemClicked.connect(self.selectWheelAxle)

		AxleListLayout.addWidget(qg.QLabel("Axle List"))

		AxleListLayout.addWidget(self.WheelAxleListWidget)

		self.FrameListWidget = qg.QListWidget(self)
		self.FrameListWidget.setSelectionMode(qg.QAbstractItemView.ExtendedSelection)
		self.FrameListWidget.itemClicked.connect(self.selectFrame)

		FrameListLayout.addWidget(qg.QLabel("Frame List"))

		FrameListLayout.addWidget(self.FrameListWidget)

		self.ClearModelButton = qg.QPushButton("Clear Model")
		self.ClearModelButton.clicked.connect(self.clearModel)
		self.BakeModelButton = qg.QPushButton("Bake Model")
		self.BakeModelButton.clicked.connect(self.bakeModel)
		self.RigModelButton = qg.QPushButton("Rig Model")
		self.RigModelButton.clicked.connect(self.rigModel)

		self.RigNameTextBox = qg.QLineEdit()

		WheelAxleShockTab = qg.QWidget()

		FrameTab = qg.QWidget()

		WheelAxleShockLayout = qg.QHBoxLayout()
		WheelAxleLayout = qg.QVBoxLayout()
		ShockLayout = qg.QVBoxLayout()

		WheelAxleShockLayout.addLayout(WheelAxleLayout)
		WheelAxleShockLayout.addLayout(ShockLayout)

		WheelAxleSliderLayout = qg.QHBoxLayout()

		WheelSliderLayout = qg.QVBoxLayout()

		WheelSliderLayout.addWidget(qg.QLabel("Wheel"))

		WheelWidthSliderLayout = qg.QHBoxLayout()
		self.WheelWidthSlider = qg.QSlider()
		self.WheelWidthSlider.setOrientation(qc.Qt.Horizontal)
		self.WheelWidthSlider.setRange(1, 50)
		self.WheelWidthSlider.setValue(10)
		self.WheelWidthSlider.sliderPressed.connect(self.openUndoChunk)
		self.WheelWidthSlider.sliderMoved.connect(self.changeWheelWidth)
		self.WheelWidthSlider.sliderReleased.connect(self.closeUndoChunk)
		WheelWidthSliderLayout.addWidget(self.WheelWidthSlider)
		WheelWidthSliderLayout.addWidget(qg.QLabel("Wheel Width"))
		WheelSliderLayout.addLayout(WheelWidthSliderLayout)

		TireTypeSliderLayout = qg.QHBoxLayout()
		self.TireTypeSlider = qg.QSlider()
		self.TireTypeSlider.setOrientation(qc.Qt.Horizontal)
		self.TireTypeSlider.setRange(0,3)
		self.TireTypeSlider.setValue(0)
		self.TireTypeSlider.sliderPressed.connect(self.openUndoChunk)
		self.TireTypeSlider.sliderReleased.connect(self.closeUndoChunk)
		self.TireTypeSlider.sliderMoved.connect(self.changeTireType)
		TireTypeSliderLayout.addWidget(self.TireTypeSlider)
		TireTypeSliderLayout.addWidget(qg.QLabel("Tire Type"))
		WheelSliderLayout.addLayout(TireTypeSliderLayout)

		WheelSizeSliderLayout = qg.QHBoxLayout()
		self.WheelSizeSlider = qg.QSlider()
		self.WheelSizeSlider.setOrientation(qc.Qt.Horizontal)
		self.WheelSizeSlider.setRange(1,20)
		self.WheelSizeSlider.setValue(10)
		self.WheelSizeSlider.sliderPressed.connect(self.openUndoChunk)
		self.WheelSizeSlider.sliderReleased.connect(self.closeUndoChunk)
		self.WheelSizeSlider.sliderMoved.connect(self.changeWheelSize)
		WheelSizeSliderLayout.addWidget(self.WheelSizeSlider)
		WheelSizeSliderLayout.addWidget(qg.QLabel("Wheel Size"))
		WheelSliderLayout.addLayout(WheelSizeSliderLayout)

		WheelShapeSliderLayout = qg.QHBoxLayout()

		WheelOutShapeSliderLayout = qg.QVBoxLayout()
		self.WheelOutShapeSlider = qg.QSlider()
		WheelOutShapeSliderLayout.addWidget(qg.QLabel("Out Width"))
		self.WheelOutShapeSlider.setRange(1,10)
		self.WheelOutShapeSlider.setValue(10)
		self.WheelOutShapeSlider.sliderPressed.connect(self.openUndoChunk)
		self.WheelOutShapeSlider.sliderReleased.connect(self.closeUndoChunk)		
		self.WheelOutShapeSlider.sliderMoved.connect(self.changeWheelOutShape)
		WheelOutShapeSliderLayout.addWidget(self.WheelOutShapeSlider)
		WheelShapeSliderLayout.addLayout(WheelOutShapeSliderLayout)

		WheelMidShapeSliderLayout = qg.QVBoxLayout()
		self.WheelMidShapeSlider = qg.QSlider()
		WheelMidShapeSliderLayout.addWidget(qg.QLabel("Mid Width"))
		self.WheelMidShapeSlider.setRange(1,10)
		self.WheelMidShapeSlider.setValue(10)
		self.WheelMidShapeSlider.sliderPressed.connect(self.openUndoChunk)
		self.WheelMidShapeSlider.sliderReleased.connect(self.closeUndoChunk)		
		self.WheelMidShapeSlider.sliderMoved.connect(self.changeWheelMidShape)
		WheelMidShapeSliderLayout.addWidget(self.WheelMidShapeSlider)
		WheelShapeSliderLayout.addLayout(WheelMidShapeSliderLayout)

		WheelInShapeSliderLayout = qg.QVBoxLayout()
		self.WheelInShapeSlider = qg.QSlider()
		WheelInShapeSliderLayout.addWidget(qg.QLabel("In Width"))
		self.WheelInShapeSlider.setRange(1,10)
		self.WheelInShapeSlider.setValue(10)
		self.WheelInShapeSlider.sliderPressed.connect(self.openUndoChunk)
		self.WheelInShapeSlider.sliderReleased.connect(self.closeUndoChunk)	
		self.WheelInShapeSlider.sliderMoved.connect(self.changeWheelInShape)
		WheelInShapeSliderLayout.addWidget(self.WheelInShapeSlider)
		WheelShapeSliderLayout.addLayout(WheelInShapeSliderLayout)

		WheelCenterShapeSliderLayout = qg.QVBoxLayout()
		self.WheelCenterShapeSlider = qg.QSlider()
		WheelCenterShapeSliderLayout.addWidget(qg.QLabel("Center Width"))
		self.WheelCenterShapeSlider.setRange(1,10)
		self.WheelCenterShapeSlider.setValue(10)
		self.WheelCenterShapeSlider.sliderPressed.connect(self.openUndoChunk)
		self.WheelCenterShapeSlider.sliderReleased.connect(self.closeUndoChunk)			
		self.WheelCenterShapeSlider.sliderMoved.connect(self.changeWheelCenterShape)
		WheelCenterShapeSliderLayout.addWidget(self.WheelCenterShapeSlider)

		WheelShapeSliderLayout.addLayout(WheelCenterShapeSliderLayout)

		WheelSliderLayout.addLayout(WheelShapeSliderLayout)
		WheelAxleSliderLayout.addLayout(WheelSliderLayout)

		AxleSliderLayout = qg.QVBoxLayout()

		AxleSliderLayout.addWidget(qg.QLabel("Axle"))

		AxleHeightSliderLayout = qg.QHBoxLayout()
		self.AxleHeightSlider = qg.QSlider()
		self.AxleHeightSlider.setOrientation(qc.Qt.Horizontal)
		self.AxleHeightSlider.setRange(-50,50)
		self.AxleHeightSlider.setValue(0)
		self.AxleHeightSlider.sliderPressed.connect(self.openUndoChunk)
		self.AxleHeightSlider.sliderMoved.connect(self.changeAxleHeight)
		self.AxleHeightSlider.sliderReleased.connect(self.closeUndoChunk)
		AxleHeightSliderLayout.addWidget(self.AxleHeightSlider)
		AxleHeightSliderLayout.addWidget(qg.QLabel("Axle Height"))
		AxleSliderLayout.addLayout(AxleHeightSliderLayout)

		AxleThicknessSliderLayout = qg.QHBoxLayout()
		self.AxleThicknessSlider = qg.QSlider()
		self.AxleThicknessSlider.setOrientation(qc.Qt.Horizontal)
		self.AxleThicknessSlider.setRange(1,20)
		self.AxleThicknessSlider.setValue(10)
		self.AxleThicknessSlider.sliderPressed.connect(self.openUndoChunk)
		self.AxleThicknessSlider.sliderReleased.connect(self.closeUndoChunk)	
		self.AxleThicknessSlider.sliderMoved.connect(self.changeAxleThickness)
		AxleThicknessSliderLayout.addWidget(self.AxleThicknessSlider)
		AxleThicknessSliderLayout.addWidget(qg.QLabel("Axle Thickness"))
		AxleSliderLayout.addLayout(AxleThicknessSliderLayout)

		AxleWidthSliderLayout = qg.QHBoxLayout()
		self.AxleWidthSlider = qg.QSlider()
		self.AxleWidthSlider.setOrientation(qc.Qt.Horizontal)
		self.AxleWidthSlider.setRange(-20,80)
		self.AxleWidthSlider.setValue(10)
		self.AxleWidthSlider.sliderPressed.connect(self.openUndoChunk)
		self.AxleWidthSlider.sliderReleased.connect(self.closeUndoChunk)		
		self.AxleWidthSlider.sliderMoved.connect(self.changeAxleWidth)
		self.AxleWidthSlider.setOrientation(qc.Qt.Horizontal)
		AxleWidthSliderLayout.addWidget(self.AxleWidthSlider)
		AxleWidthSliderLayout.addWidget(qg.QLabel("Axle Width"))
		AxleSliderLayout.addLayout(AxleWidthSliderLayout)

		WheelAxleSliderLayout.addLayout(AxleSliderLayout)

		WheelAxleButtonLayout = qg.QHBoxLayout()

		self.AddWheelAxleButton = qg.QPushButton("Add Wheel-Axle")
		self.AddWheelAxleButton.clicked.connect(self.createNewWheelAxle)
		self.DeleteWheelAxleButton = qg.QPushButton("Delete Wheel-Axle")
		self.DeleteWheelAxleButton.clicked.connect(self.deleteWheelAxle)
		self.ResetWheelButton = qg.QPushButton("Reset Wheel")
		self.ResetWheelButton.clicked.connect(self.resetWheel)
		self.ResetAxleButton = qg.QPushButton("Reset Axle")
		self.ResetAxleButton.clicked.connect(self.resetAxle)

		WheelAxleButtonLayout.addWidget(self.AddWheelAxleButton)
		WheelAxleButtonLayout.addWidget(self.DeleteWheelAxleButton)
		WheelAxleButtonLayout.addWidget(self.ResetWheelButton)
		WheelAxleButtonLayout.addWidget(self.ResetAxleButton)

		WheelAxleLayout.addLayout(WheelAxleSliderLayout)
		WheelAxleLayout.addLayout(WheelAxleButtonLayout)

		#Shocks UI#############
		ShocksLabel = qg.QLabel("Shocks")
		ShockLayout.addWidget(ShocksLabel)

		ShockDistanceSliderLayout = qg.QHBoxLayout()
		self.ShockDistanceSlider = qg.QSlider()
		self.ShockDistanceSlider.setOrientation(qc.Qt.Horizontal)
		self.ShockDistanceSlider.setRange(-30,70)
		self.ShockDistanceSlider.setValue(0)
		self.ShockDistanceSlider.sliderPressed.connect(self.openUndoChunk)
		self.ShockDistanceSlider.sliderReleased.connect(self.closeUndoChunk)
		self.ShockDistanceSlider.sliderMoved.connect(self.changeShockDistance)
		ShockDistanceSliderLayout.addWidget(self.ShockDistanceSlider)
		ShockDistanceSliderLayout.addWidget(qg.QLabel("Shock Distance"))
		ShockLayout.addLayout(ShockDistanceSliderLayout)

		SpringWidthSliderLayout = qg.QHBoxLayout()
		self.SpringWidthSlider = qg.QSlider()
		self.SpringWidthSlider.setOrientation(qc.Qt.Horizontal)
		self.SpringWidthSlider.setRange(1,20)
		self.SpringWidthSlider.setValue(6)
		self.SpringWidthSlider.sliderPressed.connect(self.openUndoChunk)
		self.SpringWidthSlider.sliderReleased.connect(self.closeUndoChunk)
		self.SpringWidthSlider.sliderMoved.connect(self.changeSpringWidth)
		SpringWidthSliderLayout.addWidget(self.SpringWidthSlider)
		SpringWidthSliderLayout.addWidget(qg.QLabel("Spring Width"))
		ShockLayout.addLayout(SpringWidthSliderLayout)

		CoilRadiusSliderLayout = qg.QHBoxLayout()
		self.CoilRadiusSlider = qg.QSlider()
		self.CoilRadiusSlider.setOrientation(qc.Qt.Horizontal)
		self.CoilRadiusSlider.setRange(0,20)
		self.CoilRadiusSlider.setValue(3)
		self.CoilRadiusSlider.sliderMoved.connect(self.changeCoilRadius)
		CoilRadiusSliderLayout.addWidget(self.CoilRadiusSlider)
		CoilRadiusSliderLayout.addWidget(qg.QLabel("Coil Radius"))
		ShockLayout.addLayout(CoilRadiusSliderLayout)

		CoilsSliderLayout = qg.QHBoxLayout()
		self.CoilsSlider = qg.QSlider()
		self.CoilsSlider.setOrientation(qc.Qt.Horizontal)
		self.CoilsSlider.setRange(5,150)
		self.CoilsSlider.setValue(51)
		self.CoilsSlider.sliderPressed.connect(self.openUndoChunk)
		self.CoilsSlider.sliderReleased.connect(self.closeUndoChunk)
		self.CoilsSlider.sliderMoved.connect(self.changeCoils)
		CoilsSliderLayout.addWidget(self.CoilsSlider)
		CoilsSliderLayout.addWidget(qg.QLabel("Coils"))
		ShockLayout.addLayout(CoilsSliderLayout)

		PistonWidthSliderLayout = qg.QHBoxLayout()
		self.PistonWidthSlider = qg.QSlider()
		self.PistonWidthSlider.setOrientation(qc.Qt.Horizontal)
		self.PistonWidthSlider.setRange(1,30)
		self.PistonWidthSlider.setValue(10)
		self.PistonWidthSlider.sliderPressed.connect(self.openUndoChunk)
		self.CoilsSlider.sliderReleased.connect(self.closeUndoChunk)		
		self.PistonWidthSlider.sliderMoved.connect(self.changePistonWidth)
		PistonWidthSliderLayout.addWidget(self.PistonWidthSlider)
		PistonWidthSliderLayout.addWidget(qg.QLabel("Piston Width"))
		ShockLayout.addLayout(PistonWidthSliderLayout)

		self.ShockResetButton = qg.QPushButton("Reset Shocks")
		self.ShockResetButton.clicked.connect(self.resetShocks)
		ShockLayout.addWidget(self.ShockResetButton)
		#################################################################################################################
		FrameLayout = qg.QVBoxLayout()

		FrameFrontBackSliderLayout = qg.QHBoxLayout()
		FrameLayout.addLayout(FrameFrontBackSliderLayout)

		FrameFrontSliderLayout = qg.QVBoxLayout()

		FrameFrontSliderLayout.addWidget(qg.QLabel("Front"))

		FrameFrontShockHeightLayout = qg.QHBoxLayout()
		FrameFrontShockHeightLayout.addWidget(qg.QLabel("Shock Height"))
		self.FrameFrontShockHeightSlider =qg.QSlider()
		self.FrameFrontShockHeightSlider.setOrientation(qc.Qt.Horizontal)
		self.FrameFrontShockHeightSlider.setRange(-100,100)
		self.FrameFrontShockHeightSlider.setValue(0)
		self.FrameFrontShockHeightSlider.sliderPressed.connect(self.openUndoChunk)
		self.FrameFrontShockHeightSlider.sliderReleased.connect(self.closeUndoChunk)		
		self.FrameFrontShockHeightSlider.sliderMoved.connect(self.changeFrameFrontShockHeight)
		FrameFrontShockHeightLayout.addWidget(self.FrameFrontShockHeightSlider)
		FrameFrontSliderLayout.addLayout(FrameFrontShockHeightLayout)

		FrameFrontShockTZLayout = qg.QHBoxLayout()
		FrameFrontShockTZLayout.addWidget(qg.QLabel("Shock TZ"))
		self.FrameFrontShockTZSlider =qg.QSlider()
		self.FrameFrontShockTZSlider.setOrientation(qc.Qt.Horizontal)
		self.FrameFrontShockTZSlider.setRange(-100,100)
		self.FrameFrontShockTZSlider.setValue(0)
		self.FrameFrontShockTZSlider.sliderPressed.connect(self.openUndoChunk)
		self.FrameFrontShockTZSlider.sliderReleased.connect(self.closeUndoChunk)
		self.FrameFrontShockTZSlider.sliderMoved.connect(self.changeFrameFrontShockTZ)
		FrameFrontShockTZLayout.addWidget(self.FrameFrontShockTZSlider)
		FrameFrontSliderLayout.addLayout(FrameFrontShockTZLayout)

		FrameFrontShockNWLayout = qg.QHBoxLayout()
		FrameFrontShockNWLayout.addWidget(qg.QLabel("Shock Narrow-Wide"))
		self.FrameFrontShockNWSlider =qg.QSlider()
		self.FrameFrontShockNWSlider.setOrientation(qc.Qt.Horizontal)
		self.FrameFrontShockNWSlider.setRange(-10,80)
		self.FrameFrontShockNWSlider.setValue(0)
		self.FrameFrontShockNWSlider.sliderPressed.connect(self.openUndoChunk)
		self.FrameFrontShockNWSlider.sliderReleased.connect(self.closeUndoChunk)		
		self.FrameFrontShockNWSlider.sliderMoved.connect(self.changeFrameFrontShockNW)
		FrameFrontShockNWLayout.addWidget(self.FrameFrontShockNWSlider)
		FrameFrontSliderLayout.addLayout(FrameFrontShockNWLayout)

		FrameFrontBackSliderLayout.addLayout(FrameFrontSliderLayout)

		FrameBackSliderLayout = qg.QVBoxLayout()

		FrameBackSliderLayout.addWidget(qg.QLabel("Back"))

		FrameBackShockHeightLayout = qg.QHBoxLayout()
		FrameBackShockHeightLayout.addWidget(qg.QLabel("Shock Height"))
		self.FrameBackShockHeightSlider =qg.QSlider()
		self.FrameBackShockHeightSlider.setOrientation(qc.Qt.Horizontal)
		self.FrameBackShockHeightSlider.setRange(-100,100)
		self.FrameBackShockHeightSlider.setValue(0)
		self.FrameBackShockHeightSlider.sliderPressed.connect(self.openUndoChunk)
		self.FrameBackShockHeightSlider.sliderReleased.connect(self.closeUndoChunk)
		self.FrameBackShockHeightSlider.sliderMoved.connect(self.changeFrameBackShockHeight)		
		FrameBackShockHeightLayout.addWidget(self.FrameBackShockHeightSlider)
		FrameBackSliderLayout.addLayout(FrameBackShockHeightLayout)

		FrameBackShockTZLayout = qg.QHBoxLayout()
		FrameBackShockTZLayout.addWidget(qg.QLabel("Shock TZ"))
		self.FrameBackShockTZSlider =qg.QSlider()
		self.FrameBackShockTZSlider.setRange(-100,100)
		self.FrameBackShockTZSlider.setValue(0)
		self.FrameBackShockTZSlider.sliderPressed.connect(self.openUndoChunk)
		self.FrameBackShockTZSlider.sliderReleased.connect(self.closeUndoChunk)		
		self.FrameBackShockTZSlider.sliderMoved.connect(self.changeFrameBackShockTZ)
		self.FrameBackShockTZSlider.setOrientation(qc.Qt.Horizontal)
		FrameBackShockTZLayout.addWidget(self.FrameBackShockTZSlider)
		FrameBackSliderLayout.addLayout(FrameBackShockTZLayout)

		FrameBackShockNWLayout = qg.QHBoxLayout()
		FrameBackShockNWLayout.addWidget(qg.QLabel("Shock Narrow-Wide"))
		self.FrameBackShockNWSlider =qg.QSlider()
		self.FrameBackShockNWSlider.setOrientation(qc.Qt.Horizontal)
		self.FrameBackShockNWSlider.setRange(-10,80)
		self.FrameBackShockNWSlider.setValue(0)
		self.FrameBackShockNWSlider.sliderPressed.connect(self.openUndoChunk)
		self.FrameBackShockNWSlider.sliderReleased.connect(self.closeUndoChunk)		
		self.FrameBackShockNWSlider.sliderMoved.connect(self.changeFrameBackShockNW)
		FrameBackShockNWLayout.addWidget(self.FrameBackShockNWSlider)
		FrameBackSliderLayout.addLayout(FrameBackShockNWLayout)

		FrameFrontBackSliderLayout.addLayout(FrameBackSliderLayout)

		FrameAngleHeightTypeSliderLayout = qg.QVBoxLayout()

		FrameAngleLayout = qg.QHBoxLayout()
		FrameAngleLayout.addWidget(qg.QLabel("Frame Angle"))
		self.FrameAngleSlider =qg.QSlider()
		self.FrameAngleSlider.setOrientation(qc.Qt.Horizontal)
		self.FrameAngleSlider.setRange(-30,30)
		self.FrameAngleSlider.setValue(0)
		self.FrameAngleSlider.sliderPressed.connect(self.openUndoChunk)
		self.FrameAngleSlider.sliderReleased.connect(self.closeUndoChunk)		
		self.FrameAngleSlider.sliderMoved.connect(self.changeFrameAngle)
		FrameAngleLayout.addWidget(self.FrameAngleSlider)
		FrameAngleHeightTypeSliderLayout.addLayout(FrameAngleLayout)

		FrameHeightLayout = qg.QHBoxLayout()
		FrameHeightLayout.addWidget(qg.QLabel("Frame Height"))
		self.FrameHeightSlider =qg.QSlider()
		self.FrameHeightSlider.setOrientation(qc.Qt.Horizontal)
		self.FrameHeightSlider.setRange(0,100)
		self.FrameHeightSlider.setValue(0)
		self.FrameHeightSlider.sliderPressed.connect(self.openUndoChunk)
		self.FrameHeightSlider.sliderReleased.connect(self.closeUndoChunk)		
		self.FrameHeightSlider.sliderMoved.connect(self.changeFrameHeight)
		FrameHeightLayout.addWidget(self.FrameHeightSlider)
		FrameAngleHeightTypeSliderLayout.addLayout(FrameHeightLayout)

		FrameLayout.addLayout(FrameAngleHeightTypeSliderLayout)

		FrameButtonsLayout = qg.QHBoxLayout()

		self.AddFrameButton = qg.QPushButton("Add Frame")
		self.AddFrameButton.clicked.connect(self.createNewFrame)
		FrameButtonsLayout.addWidget(self.AddFrameButton)

		self.DeleteFrameButton = qg.QPushButton("Delete Frame")
		self.DeleteFrameButton.clicked.connect(self.deleteFrame)
		FrameButtonsLayout.addWidget(self.DeleteFrameButton)

		self.ResetFrameButton = qg.QPushButton("Reset Frame")
		self.ResetFrameButton.clicked.connect(self.resetFrame)
		FrameButtonsLayout.addWidget(self.ResetFrameButton)

		FrameLayout.addLayout(FrameButtonsLayout)

		WheelAxleShockTab.setLayout(WheelAxleShockLayout)
		FrameTab.setLayout(FrameLayout)

		FunctionsTab.addTab(WheelAxleShockTab, "Wheel Axle Shock Tab")
		FunctionsTab.addTab(FrameTab, "Frame Tab")

		GeneralFunctionsLayout.addWidget(self.ClearModelButton)
		GeneralFunctionsLayout.addWidget(self.BakeModelButton)
		GeneralFunctionsLayout.addWidget(self.RigModelButton)
		GeneralFunctionsLayout.addWidget(self.RigNameTextBox)

	def openUndoChunk(self):
		mc.undoInfo(openChunk = True)

	def closeUndoChunk(self):
		mc.undoInfo(closeChunk = True)

	def selectWheelAxle(self):
		WheelAxleObject = self.getWheelAxleObject(self.WheelAxleListWidget.currentItem().text())
		print str(WheelAxleObject) + " selected!"
		mc.select(str(WheelAxleObject)+"_WheelAxle_CTL")
		self.setWheelAxleSliderValues(WheelAxleObject)

	def setWheelAxleSliderValues(self, WheelAxleObject):
		self.WheelWidthSlider.setValue(WheelAxleObject.WheelAxleAttributes["Width"]*10)
		self.TireTypeSlider.setValue(WheelAxleObject.WheelAxleAttributes["Tire_Type"])
		self.WheelSizeSlider.setValue(WheelAxleObject.WheelAxleAttributes["Size"]*10)
		self.WheelCenterShapeSlider.setValue(WheelAxleObject.WheelAxleAttributes["Center_Radius"]*10)
		self.WheelOutShapeSlider.setValue(WheelAxleObject.WheelAxleAttributes["Shape_Values"][0]*10)
		self.WheelMidShapeSlider.setValue(WheelAxleObject.WheelAxleAttributes["Shape_Values"][1]*10)
		self.WheelInShapeSlider.setValue(WheelAxleObject.WheelAxleAttributes["Shape_Values"][2]*10)
		self.AxleWidthSlider.setValue(WheelAxleObject.WheelAxleAttributes["Axle_Width"]*10)
		self.AxleHeightSlider.setValue(WheelAxleObject.WheelAxleAttributes["Axle_Height"]*10)
		self.AxleThicknessSlider.setValue(WheelAxleObject.WheelAxleAttributes["Axle_Thickness"]*10)
		self.SpringWidthSlider.setValue(WheelAxleObject.WheelAxleAttributes["Spring_Width"]*10)
		self.CoilRadiusSlider.setValue(WheelAxleObject.WheelAxleAttributes["Coil_Radius"]*100)
		self.CoilsSlider.setValue(WheelAxleObject.WheelAxleAttributes["Coils"]*10)
		self.PistonWidthSlider.setValue(WheelAxleObject.WheelAxleAttributes["Piston_Width"]*10)
		self.ShockDistanceSlider.setValue(WheelAxleObject.WheelAxleAttributes["Shock_Distance"]*10)

	def selectFrame(self):
		FrameObject = self.getFrameObject(self.FrameListWidget.currentItem().text())
		print str(FrameObject)+" selected!"
		mc.select(str(FrameObject)+"_FrameControl_CRV", add = True)
		self.setFrameSliderValues(FrameObject)

#TO FIX!
	def setFrameSliderValues(self, FrameObject):
		self.FrameFrontShockHeightSlider.setValue(FrameObject.FrameAttributes["Front_Shock_Height"]*10)
		self.FrameBackShockHeightSlider.setValue(FrameObject.FrameAttributes["Back_Shock_Height"]*10)
		self.FrameFrontShockTZSlider.setValue(FrameObject.FrameAttributes["Front_Shock_TZ"]*10)
		self.FrameBackShockTZSlider.setValue(FrameObject.FrameAttributes["Back_Shock_TZ"]*10)
		self.FrameFrontShockNWSlider.setValue(FrameObject.FrameAttributes["Front_Shock_NW"]*10)
		self.FrameBackShockNWSlider.setValue(FrameObject.FrameAttributes["Back_Shock_NW"]*10)
		self.FrameAngleSlider.setValue(FrameObject.FrameAttributes["Frame_Angle"]*10)
		self.FrameHeightSlider.setValue(FrameObject.FrameAttributes["Frame_Height"]*10)

	#SPECIFIC FUNCTIONS
	def createNewWheelAxle(self):
		print "Function called Successfully"
		newName = self.generateWheelAxleName("WheelAxle")

		newWheelAxle = WheelAxle(newName)

		self.WheelAxleItem = qg.QListWidgetItem()
		self.WheelAxleItem.setText(str(newWheelAxle))
		self.WheelAxleListWidget.addItem(self.WheelAxleItem)

		self.WheelAxleObjectList.append(newWheelAxle)
		self.WheelAxleNameList.append(str(newWheelAxle))

		self.WheelAxleListWidget.setCurrentRow(-1)
		self.FrameListWidget.setCurrentRow(-1)

	def generateWheelAxleName(self, newName):
		index = 1
		testName = newName+"_"+str(index)
		for name in self.WheelAxleNameList:
			print self.RenameTextBox.text()
			if testName in name:
				index +=1
				testName = newName+"_"+str(index)

		return testName
		
	def getWheelAxleObject(self, WheelAxleName):
		if WheelAxleName!= None:
			for obj in self.WheelAxleObjectList:
				if WheelAxleName == str(obj):
					return obj
		else:
			return None

	def createNewFrame(self):
		newName = self.generateFrameName("Frame")
		#CODE TO DETERMINE WHICH AXLE IS FRONT AND WHICH AXLE IS BACK
		WheelAxleObject1 = self.getWheelAxleObject(self.WheelAxleListWidget.selectedItems()[0].text())
		WheelAxleObject2 = self.getWheelAxleObject(self.WheelAxleListWidget.selectedItems()[1].text())

		WheelAxleObject1Position = mc.xform(str(WheelAxleObject1)+"_WheelAxle_CTL", ws = True, query = True, translation = True)[2]
		print WheelAxleObject1Position
		WheelAxleObject2Position = mc.xform(str(WheelAxleObject2)+"_WheelAxle_CTL", ws = True, query = True, translation = True)[2]
		print WheelAxleObject2Position

		if WheelAxleObject1.WheelAxleAttributes["Frame_Connect"] == 1 or WheelAxleObject2.WheelAxleAttributes["Frame_Connect"] == 1:
			print "Frame already connected to the selected Axles! Aborting!"
			return

		if WheelAxleObject1Position >= WheelAxleObject2Position:
			frontWheelAxle = WheelAxleObject1
			backWheelAxle = WheelAxleObject2

		else:
			frontWheelAxle = WheelAxleObject2
			backWheelAxle = WheelAxleObject1

		newFrame = Frame(newName, frontWheelAxle, backWheelAxle)
		
		self.FrameItem = qg.QListWidgetItem()
		self.FrameItem.setText(str(newFrame))
		self.FrameListWidget.addItem(self.FrameItem)

		self.FrameObjectList.append(newFrame)
		self.FrameNameList.append(str(newFrame))

		self.WheelAxleListWidget.setCurrentRow(-1)
		self.FrameListWidget.setCurrentRow(-1)

	def generateFrameName(self, newName):
		index = 1
		testName = newName+"_"+str(index)
		for name in self.FrameNameList:
			print self.RenameTextBox.text()
			if testName in name:
				print name
				index +=1
				testName = newName+"_"+str(index)

		return testName 

	def getFrameObject(self, FrameName):
		if FrameName!= None:	
			for obj in self.FrameObjectList:
				if FrameName == str(obj):
					return obj
		else:
			return None

	def deleteWheelAxle(self):
		WheelAxleObject = self.getWheelAxleObject(self.WheelAxleListWidget.currentItem().text())
		self.WheelAxleListWidget.takeItem(self.WheelAxleListWidget.currentRow())
		self.WheelAxleNameList.remove(str(WheelAxleObject))
		self.WheelAxleObjectList.remove(WheelAxleObject)
		WheelAxleObject.deleteWheelAxleObject()

	def deleteFrame(self):
		FrameObject = self.getFrameObject(self.FrameListWidget.currentItem().text())
		self.FrameListWidget.takeItem(self.FrameListWidget.currentRow())
		self.FrameNameList.remove(str(FrameObject))
		self.FrameObjectList.remove(FrameObject)
		FrameObject.deleteFrameObject()

	def resetWheel(self):
		self.WheelWidthSlider.setValue(10)
		self.TireTypeSlider.setValue(0)
		self.WheelSizeSlider.setValue(10)
		self.WheelOutShapeSlider.setValue(10)
		self.WheelMidShapeSlider.setValue(10)
		self.WheelInShapeSlider.setValue(10)
		self.WheelCenterShapeSlider.setValue(10)

		if WheelAxleObject != None:
			WheelAxleObject.resetWheelObject()

		else:
			print "Wheel Axle object not found"
		
	def resetAxle(self):
		WheelAxleObject = self.getWheelAxleObject(self.WheelAxleListWidget.currentItem().text())
		self.AxleHeightSlider.setValue(0)
		self.AxleThicknessSlider.setValue(10)
		self.AxleWidthSlider.setValue(10)

		if WheelAxleObject != None:
			WheelAxleObject.resetAxleObject()

		else:
			print "Wheel Axle object not found"

	def resetShocks(self):
		WheelAxleObject = self.getWheelAxleObject(self.WheelAxleListWidget.currentItem().text())
		self.ShockDistanceSlider.setValue(0)
		self.SpringWidthSlider.setValue(6)
		self.CoilRadiusSlider.setValue(3)
		self.CoilsSlider.setValue(51)
		self.PistonWidthSlider.setValue(10)

		if WheelAxleObject != None:
			WheelAxleObject.resetShocksObject()

		else:
			print "Wheel Axle Object not found"

	def resetFrame(self):
		FrameObject = self.getWheelAxleObject(self.FrameListWidget.currentItem().text())
		self.FrameFrontShockHeightSlider.setValue(0)
		self.FrameFrontShockTZSlider.setValue(0)
		self.FrameFrontShockNWSlider.setValue(0)
		self.FrameBackShockHeightSlider.setValue(0)
		self.FrameBackShockTZSlider.setValue(0)
		self.FrameBackShockNWSlider.setValue(0)
		self.FrameAngleSlider.setValue(0)
		self.FrameHeightSlider.setValue(0)
		if FrameObject != None:
			FrameObject.resetFrameObject()

		else:
			print "Frame Object not found"


	def changeWheelWidth(self, value):
		WheelAxleObject = self.getWheelAxleObject(self.WheelAxleListWidget.currentItem().text())
		if WheelAxleObject != None:
			WheelAxleObject.changeWheelWidth(value)
		else:
			print "Wheel object not found"


	def changeWheelSize(self, value):
		WheelObject = self.getWheelAxleObject(self.WheelAxleListWidget.currentItem().text())
		if WheelObject != None:
			WheelObject.changeWheelSize(value)
		else:
			print "Wheel object not found"

	def changeTireType(self, value):
		WheelObject = self.getWheelAxleObject(self.WheelAxleListWidget.currentItem().text())
		if WheelObject != None:
			WheelObject.changeTireType(value)
		else:
			print "Wheel object not found"

	def changeWheelOutShape(self, value):
		WheelObject = self.getWheelAxleObject(self.WheelAxleListWidget.currentItem().text())
		if WheelObject != None:
			WheelObject.changeWheelOutShape(value)
		else:
			print "Wheel object not found"

	def changeWheelMidShape(self, value):
		WheelObject = self.getWheelAxleObject(self.WheelAxleListWidget.currentItem().text())
		if WheelObject != None:
			WheelObject.changeWheelMidShape(value)
		else:
			print "Wheel object not found"

	def changeWheelInShape(self, value):
		WheelObject = self.getWheelAxleObject(self.WheelAxleListWidget.currentItem().text())
		if WheelObject != None:
			WheelObject.changeWheelInShape(value)
		else:
			print "Wheel object not found"

	def changeWheelCenterShape(self, value):
		WheelObject = self.getWheelAxleObject(self.WheelAxleListWidget.currentItem().text())
		if WheelObject != None:
			WheelObject.changeWheelCenterShape(value)
		else:
			print "Wheel object not found"

	def changeAxleHeight(self, value):
		AxleObject = self.getWheelAxleObject(self.WheelAxleListWidget.currentItem().text())
		if AxleObject != None:
			AxleObject.changeAxleHeight(value)
		else:
			print "Wheel object not found"

	def changeAxleThickness(self, value):
		AxleObject = self.getWheelAxleObject(self.WheelAxleListWidget.currentItem().text())
		if AxleObject != None:
			AxleObject.changeAxleThickness(value)
		else:
			print "Wheel object not found"

	def changeAxleWidth(self, value):
		AxleObject = self.getWheelAxleObject(self.WheelAxleListWidget.currentItem().text())
		if AxleObject != None:
			AxleObject.changeAxleWidth(value)
		else:
			print "Wheel object not found"

	def changeSpringWidth(self, value):
		ShockObject = self.getWheelAxleObject(self.WheelAxleListWidget.currentItem().text())
		if ShockObject != None:
			ShockObject.changeSpringWidth(value)
		else:
			print "Wheel object not found"

	def changeCoilRadius(self, value):
		ShockObject = self.getWheelAxleObject(self.WheelAxleListWidget.currentItem().text())
		if ShockObject != None:
			ShockObject.changeCoilRadius(value)
		else:
			print "Wheel object not found"

	def changeCoils(self, value):
		ShockObject = self.getWheelAxleObject(self.WheelAxleListWidget.currentItem().text())
		if ShockObject != None:
			ShockObject.changeCoils(value)
		else:
			print "Wheel object not found"

	def changePistonWidth(self, value):
		ShockObject = self.getWheelAxleObject(self.WheelAxleListWidget.currentItem().text())
		if ShockObject != None:
			ShockObject.changePistonWidth(value)
		else:
			print "Wheel object not found"

	def changeShockDistance(self, value):
		ShockObject = self.getWheelAxleObject(self.WheelAxleListWidget.currentItem().text())
		
		if ShockObject != None:
			ShockObject.changeShockDistance(value)
		else:
			print "Wheel Object not found"

	def changeFrameFrontShockHeight(self, value):
		FrameObject = self.getFrameObject(self.FrameListWidget.currentItem().text())
		if FrameObject != None:
			FrameObject.changeFrameFrontShockHeight(value)
		else:
			print "Wheel object not found"

	def changeFrameFrontShockTZ(self, value):
		FrameObject = self.getFrameObject(self.FrameListWidget.currentItem().text())
		if FrameObject != None:
			FrameObject.changeFrameFrontShockTZ(value)
		else:
			print "Frame object not found"

	def changeFrameFrontShockNW(self, value):
		FrameObject = self.getFrameObject(self.FrameListWidget.currentItem().text())
		if FrameObject != None:
			FrameObject.changeFrameFrontShockNW(value)
		else:
			print "Frame object not found"

	def changeFrameBackShockHeight(self, value):
		FrameObject = self.getFrameObject(self.FrameListWidget.currentItem().text())
		if FrameObject != None:
			FrameObject.changeFrameBackShockHeight(value)
		else:
			print "Frame object not found"

	def changeFrameBackShockTZ(self, value):
		FrameObject = self.getFrameObject(self.FrameListWidget.currentItem().text())
		if FrameObject != None:
			FrameObject.changeFrameBackShockTZ(value)
		else:
			print "Frame object not found"

	def changeFrameBackShockNW(self, value):
		FrameObject = self.getFrameObject(self.FrameListWidget.currentItem().text())
		if FrameObject != None:
			FrameObject.changeFrameBackShockNW(value)
		else:
			print "Frame object not found"

	def changeFrameAngle(self, value):
		FrameObject = self.getFrameObject(self.FrameListWidget.currentItem().text())
		if FrameObject != None:
			FrameObject.changeFrameAngle(value)
		else:
			print "Frame object not found"

	def changeFrameHeight(self, value):
		FrameObject = self.getFrameObject(self.FrameListWidget.currentItem().text())
		if FrameObject != None:
			FrameObject.changeFrameHeight(value)
		else:
			print "Frame object not found"

	def changeFrameType(self, value):
		AxleObject = self.getFrameObject(self.FrameListWidget.currentItem().text())
		if FrameObject != None:
			FrameObject.changeFrameType(value)
		else:
			print "Frame object not found"
	
	#GENERAL FUNCTIONS
	def renameComponent(self):
		if self.WheelAxleListWidget.currentRow() != -1:
			WheelAxleObject = self.getWheelAxleObject(self.WheelAxleListWidget.currentItem().text())
			self.WheelAxleNameList.remove(str(WheelAxleObject))
			newWheelName = self.generateWheelAxleName(self.RenameTextBox.text())
			WheelAxleObject.rename(newWheelName)
			self.WheelAxleNameList.append(newWheelName)
			self.WheelAxleListWidget.currentItem().setText(str(WheelAxleObject))
			print "I SHOULD NOT BE HERE!"

		if self.FrameListWidget.currentRow() != -1:
			FrameObject = self.getFrameObject(self.FrameListWidget.currentItem().text())
			self.FrameNameList.remove(str(FrameObject))
			newFrameName = self.generateFrameName(self.RenameTextBox.text())
			FrameObject.rename(newFrameName)
			self.FrameNameList.append(newFrameName)
			self.FrameListWidget.currentItem().setText(str(FrameObject))
			print "I SHOULD BE HERE!"

		self.WheelAxleListWidget.setCurrentRow(-1)
		self.FrameAxleList.setCurrentRow(-1)

	def clearModel(self):
		print self.WheelAxleNameList
		print self.WheelAxleListWidget.count()
		count = self.WheelAxleListWidget.count()
		print count
		while self.WheelAxleListWidget.count()>0:
			wheelAxle = self.getWheelAxleObject(self.WheelAxleListWidget.item(0).text())
			self.WheelAxleListWidget.takeItem(0)
			self.WheelAxleNameList.remove(str(wheelAxle))
			self.WheelAxleObjectList.remove(wheelAxle)
			wheelAxle.deleteWheelAxleObject()

		for i in range(self.FrameListWidget.count()):
			frame = self.getFrameObject(self.FrameListWidget.item(i).text())
			self.FrameListWidget.takeItem(i)
			self.FrameNameList.remove(str(frame))
			self.FrameObjectList.remove(frame)
			frame.deleteFrameObject()

	def bakeModel(self):
		bakeName = self.RigNameTextBox.text()
		worldGroup = mc.group(em = True, n = bakeName+"_World_GRP")
		mc.delete("*Constraint*")
		for i in range(self.WheelAxleListWidget.count()):
			bakeWheelAxleName = bakeName+"_"+str(i)
			wheelAxle = self.getWheelAxleObject(self.WheelAxleListWidget.item(i).text())
			wheelAxle.bakeWheelAxle(bakeWheelAxleName, worldGroup)

		for i in range(self.FrameListWidget.count()):
			frame = self.getFrameObject(self.FrameListWidget.item(i).text())
			frame.bakeFrame(bakeName, worldGroup)

		mc.undoInfo(openChunk = True, state = True)

		self.close()

	def rigModel(self):
		rigName = self.RigNameTextBox.text()
		self.worldControl = mc.circle(nr = (0, 1, 0), c = (0,0,0), r = 4, name = rigName+"_World_CTL")[0]
		mc.addAttr(self.worldControl, ln = "RollSwitch", attributeType = "bool", keyable = True)
		mc.setAttr(self.worldControl+".overrideEnabled", 1)
		mc.setAttr(self.worldControl+".overrideColor", 17)
		rigGroup = mc.group(self.worldControl, n = rigName+"_World_GRP")
		print self.worldControl
		for i in range(self.WheelAxleListWidget.count()):
			print i
			wheelRigName = rigName+"_"+str(i)
			wheelAxle = self.getWheelAxleObject(self.WheelAxleListWidget.item(i).text())
			wheelAxle.rigWheelAxle(self.worldControl, wheelRigName)

		for i in range(self.FrameListWidget.count()):
			frame = self.getFrameObject(self.FrameListWidget.item(i).text())
			frame.rigFrame(self.worldControl, rigName)

		#Removing unnecessary bindPose nodes
		mc.delete("*bindPose*")

		mc.undoInfo(openChunk = True, state = True)

		self.close()

class WheelAxle():
	def __init__(self, wheelAxleName):
		print "WheelAxle Object created Successfully"
		try:
			mc.file("C:/autoRig/WheelAxle.ma", ignoreVersion = True, i = True, rpr = wheelAxleName, mergeNamespacesOnClash = True, options = "v=0", type = "mayaAscii", pr = True, ra = True)
		except RuntimeError:
			print "Runtime Error! Aborting!"

		mc.setAttr(wheelAxleName+"_WheelAxle_CTL.translateZ", 0.0)
		self.WheelAxleAttributes = {}
		self.WheelAxleAttributes["Name"] = wheelAxleName
		self.WheelAxleAttributes["Tire_Type"] = 0
		self.WheelAxleAttributes["Size"] = 1.0
		self.WheelAxleAttributes["Width"] = 1.0
		self.WheelAxleAttributes["Center_Radius"] = 1.0
		self.WheelAxleAttributes["Shape_Values"] = [1.0, 1.0, 1.0]
		self.WheelAxleAttributes["Position"] = mc.xform(wheelAxleName+"_WheelAxle_CTL", query = True, ws = True, translation = True)
		self.WheelAxleAttributes["Axle_Width"] = 1.0
		self.WheelAxleAttributes["Axle_Height"] = 0.0
		self.WheelAxleAttributes["Axle_Thickness"] = 1.0
		self.WheelAxleAttributes["Spring_Width"] = 0.6
		self.WheelAxleAttributes["Coil_Radius"] = 0.03
		self.WheelAxleAttributes["Coils"] = 5.1
		self.WheelAxleAttributes["Piston_Width"] = 1
		self.WheelAxleAttributes["Shock_Distance"] = 0
		self.WheelAxleAttributes["Frame_Connect"] = 0
		
		self.LeftWheelTypes = mc.listRelatives(wheelAxleName+"_WheelAxle_l_tireGeos_GRP", children = True)
		self.RightWheelTypes = mc.listRelatives(wheelAxleName+"_WheelAxle_r_tireGeos_GRP", children = True)
		print self.WheelAxleAttributes

		print self.LeftWheelTypes
		print self.RightWheelTypes

	def __str__(self):
		return self.WheelAxleAttributes["Name"]

	def rename(self, newName):
		oldName = self.WheelAxleAttributes["Name"]
		print oldName
		mc.select(oldName+"*")
		mc.select("*.vtx[*]", d = True)
		mc.select("*Shape*", d = True)
		mc.select("*Group*", d = True)
		mc.select("*group*", d = True)
		selectedObjects = mc.ls(sl = True)
		print selectedObjects
		for obj in selectedObjects:
			mc.lockNode(obj, lock = False)
		 	newNameSuffix = obj.rpartition(oldName)[2]
			mc.rename(obj, newName + newNameSuffix)

		self.WheelAxleAttributes["Name"] = newName
		print "Objects Renamed"

	def deleteWheelAxleObject(self):
		mc.selectType(allComponents = False)
		mc.select(self.WheelAxleAttributes["Name"]+"*")
		mc.delete()
		mc.select(self.WheelAxleAttributes["Name"]+"*")
		mc.delete()

	def resetWheelObject(self):
		self.WheelAxleAttributes["Type"] = 0
		self.WheelAxleAttributes["Size"] = 1.0
		self.WheelAxleAttributes["Width"] = 1.0
		self.WheelAxleAttributes["Center_Radius"] = 1.0
		self.WheelAxleAttributes["Shape_Values"] = [1.0, 1.0, 1.0]

		mc.setAttr(self.WheelAxleAttributes["Name"]+"_WheelAxle_ATR.WheelSize", value/50.0)
		mc.setAttr(self.WheelAxleAttributes["Name"]+"_WheelAxle_ATR.WheelShapeOut", value/50.0)
		mc.setAttr(self.WheelAxleAttributes["Name"]+"_WheelAxle_ATR.WheelShapeMid", value/50.0)
		mc.setAttr(self.WheelAxleAttributes["Name"]+"_WheelAxle_ATR.WheelShapeIn", value/50.0)
		mc.setAttr(self.WheelAxleAttributes["Name"]+"_WheelAxle_ATR.WheelCenter", value/50.0)

	def resetAxleObject(self):
		self.WheelAxleAttributes["Axle_Width"] = 1.0
		self.WheelAxleAttributes["Axle_Height"] = 0.0
		self.WheelAxleAttributes["Axle_Thickness"] = 1.0

		mc.setAttr(self.WheelAxleAttributes["Name"]+"_WheelAxle_ATR.AxleHeight", value/50.0)
		mc.setAttr(self.WheelAxleAttributes["Name"]+"_WheelAxle_ATR.AxleWidth", value/50.0)
		mc.setAttr(self.WheelAxleAttributes["Name"]+"_WheelAxle_ATR.AxleThickness", value/50.0)

	def resetShocksObject(self):
		self.WheelAxleAttributes["Spring_Width"] = 0.6
		self.WheelAxleAttributes["Coil_Radius"] = 0.03
		self.WheelAxleAttributes["Coils"] = 5.1
		self.WheelAxleAttributes["Piston_Width"] = 1

		mc.setAttr(self.WheelAxleAttributes["Name"]+"_WheelAxle_ATR.SpringWidth", 0.6)
		mc.setAttr(self.WheelAxleAttributes["Name"]+"_WheelAxle_ATR.CoilRadius", 0.03)
		mc.setAttr(self.WheelAxleAttributes["Name"]+"_WheelAxle_ATR.Coils", 5.1)
		mc.setAttr(self.WheelAxleAttributes["Name"]+"_WheelAxle_ATR.PistonWidth", 1)
		mc.setAttr(self.WheelAxleAttributes["Name"]+"_WheelAxle_ATR.ShockDistance", 0)

#BAKE MODEL	
	def bakeWheelAxle(self, bakeName, worldGroup):
		TireType = self.WheelAxleAttributes["Tire_Type"]
		print TireType

	#	Code to delete meshes not in use
		LeftTyreGeos = mc.listRelatives(str(self)+"_WheelAxle_l_tireGeos_GRP", children = True)
		print LeftTyreGeos
		for i in range(len(LeftTyreGeos)):
			if i != TireType:
				print "come Left!"
				mc.delete(LeftTyreGeos[i])
		
		RightTyreGeos = mc.listRelatives(str(self)+"_WheelAxle_r_tireGeos_GRP", children = True)
		for i in range(len(RightTyreGeos)):
			if i != TireType:
				print "come Right!"
				mc.delete(RightTyreGeos[i])
	
		AxleGeo = mc.listRelatives(str(self)+"_WheelAxle_AxleGeos_GRP", children = True)[0]
		leftWheelGeo =  mc.listRelatives(str(self)+"_WheelAxle_l_wheelGeos_GRP", children = True)[0]
		rightWheelGeo =  mc.listRelatives(str(self)+"_WheelAxle_r_wheelGeos_GRP", children = True)[0]

		mc.delete(LeftTyreGeos[TireType], ch = True)
		mc.delete(RightTyreGeos[TireType], ch = True)
		mc.delete(AxleGeo, ch = True)
		mc.delete(leftWheelGeo, ch = True)
		mc.delete(rightWheelGeo, ch = True)

		#Code to unparent all visible meshes
		mc.parent(LeftTyreGeos[TireType], w = True)
		mc.parent(RightTyreGeos[TireType], w = True)
		mc.parent(AxleGeo, w = True)
		mc.parent(leftWheelGeo, w = True)
		mc.parent(rightWheelGeo, w = True)

		#Code to rename visible meshes
		leftTyreGeo = mc.rename(LeftTyreGeos[TireType], bakeName+"_L_Tyre_GEO")
		mc.xform(leftTyreGeo, cp = True)
		rightTyreGeo = mc.rename(RightTyreGeos[TireType], bakeName+"_R_Tyre_GEO")
		mc.xform(rightTyreGeo, cp = True)
		leftWheelGeo = mc.rename(leftWheelGeo, bakeName+"_L_Wheel_GEO")
		mc.xform(leftWheelGeo, cp = True)
		rightWheelGeo = mc.rename(rightWheelGeo, bakeName+"_R_Wheel_GEO")
		mc.xform(rightWheelGeo, cp = True)
		AxleGeo = mc.rename(AxleGeo, bakeName+"_Axle_GEO")
		mc.xform(AxleGeo, cp = True)

		for geo in mc.listRelatives(str(self)+"_r_ShockGEO_GRP", children = True):
			mc.delete(geo, ch = True)

		for geo in mc.listRelatives(str(self)+"_l_ShockGEO_GRP", children = True):
			mc.delete(geo, ch = True)

		for geo in mc.listRelatives(str(self)+"_r_WheelAxleConnectGeo_GRP", children = True):
			mc.delete(geo, ch = True)

		for geo in mc.listRelatives(str(self)+"_l_WheelAxleConnectGeo_GRP", children = True):
			mc.delete(geo, ch = True)

		#LEFT
		leftWheelGroup = mc.group(leftWheelGeo, leftTyreGeo, n = bakeName+"_L_WheelGeo_GRP")
		mc.xform(leftWheelGroup, cp = True)
		
		#RIGHT
		rightWheelGroup = mc.group(rightWheelGeo, rightTyreGeo, n = bakeName+"_R_WheelGeo_GRP")
		mc.xform(rightWheelGroup, cp = True)

		#AXLE
		axleGroup = mc.group(AxleGeo, n = bakeName+"_AxleGeo_GRP")
		mc.xform(axleGroup, cp = True)

		#Renaming Shock Rigs
		leftShockGeoGroup = mc.parent(str(self)+"_l_ShockGEO_GRP", w = True)
		leftShockGeoGroup = mc.rename(leftShockGeoGroup, bakeName+"_l_ShockGEO_GRP")
		leftShockGeoParts = mc.listRelatives(leftShockGeoGroup, allDescendents = True)
		for part in leftShockGeoParts:
			mc.rename(part, bakeName+part.partition(str(self))[2])

		rightShockGeoGroup = mc.parent(str(self)+"_r_ShockGEO_GRP", w = True)
		rightShockGeoGroup = mc.rename(rightShockGeoGroup, bakeName+"_r_ShockGEO_GRP")
		rightShockGeoParts = mc.listRelatives(rightShockGeoGroup, allDescendents = True)
		for part in rightShockGeoParts:
			mc.rename(part, bakeName+part.partition(str(self))[2])

		#Renaming WheelAxle Connection rigs
		leftWheelAxleConnectGeoGroup = mc.parent(str(self)+"_l_WheelAxleConnectGeo_GRP", w = True)
		leftWheelAxleConnectGeoGroup = mc.rename(leftWheelAxleConnectGeoGroup, bakeName+"_l_WheelAxleConnectGeo_GRP")
		leftWheelAxleConnectGeoParts = mc.listRelatives(leftWheelAxleConnectGeoGroup, allDescendents = True)
		for part in leftWheelAxleConnectGeoParts:
			mc.rename(part, bakeName+part.partition(str(self))[2])

		rightWheelAxleConnectGeoGroup = mc.parent(str(self)+"_r_WheelAxleConnectGeo_GRP", w = True)
		rightWheelAxleConnectGeoGroup = mc.rename(rightWheelAxleConnectGeoGroup, bakeName+"_r_WheelAxleConnectGeo_GRP")
		rightWheelAxleConnectGeoParts = mc.listRelatives(rightWheelAxleConnectGeoGroup, allDescendents = True)
		for part in rightWheelAxleConnectGeoParts:
			mc.rename(part, bakeName+part.partition(str(self))[2])

		mc.delete(str(self)+"*")

		mc.parent([leftWheelGroup, rightWheelGroup, axleGroup, leftShockGeoGroup, rightShockGeoGroup, leftWheelAxleConnectGeoGroup, rightWheelAxleConnectGeoGroup], worldGroup)

#AUTO-RIGGING WHEEL AXLE!!!!!
	def rigWheelAxle(self, worldControl, rigName = "Test"):
		TireType = self.WheelAxleAttributes["Tire_Type"]
		print TireType
		worldGroup = mc.listRelatives(worldControl, parent = True)

	#	Code to delete meshes not in use
		LeftTyreGeos = mc.listRelatives(str(self)+"_WheelAxle_l_tireGeos_GRP", children = True)
		print LeftTyreGeos
		for i in range(len(LeftTyreGeos)):
			if i != TireType:
				print "come Left!"
				mc.delete(LeftTyreGeos[i])
		
		RightTyreGeos = mc.listRelatives(str(self)+"_WheelAxle_r_tireGeos_GRP", children = True)
		for i in range(len(RightTyreGeos)):
			if i != TireType:
				print "come Right!"
				mc.delete(RightTyreGeos[i])
	
		axleGeo = mc.listRelatives(str(self)+"_WheelAxle_AxleGeos_GRP", children = True)[0]
		leftWheelGeo =  mc.listRelatives(str(self)+"_WheelAxle_l_wheelGeos_GRP", children = True)[0]
		rightWheelGeo =  mc.listRelatives(str(self)+"_WheelAxle_r_wheelGeos_GRP", children = True)[0]

		#Code to delete skin-clusters on visible meshes
		mc.delete(LeftTyreGeos[TireType], ch = True)
		mc.delete(RightTyreGeos[TireType], ch = True)
		mc.delete(axleGeo, ch = True)
		mc.delete(leftWheelGeo, ch = True)
		mc.delete(rightWheelGeo, ch = True)

		#Code to unparent all visible meshes
		mc.parent(LeftTyreGeos[TireType], w = True)
		mc.parent(RightTyreGeos[TireType], w = True)
		mc.parent(axleGeo, w = True)
		mc.parent(leftWheelGeo, w = True)
		mc.parent(rightWheelGeo, w = True)

		#Code to rename visible meshes
		leftTyreGeo = mc.rename(LeftTyreGeos[TireType], rigName+"_L_Tyre_GEO")
		mc.xform(leftTyreGeo, cp = True)
		rightTyreGeo = mc.rename(RightTyreGeos[TireType], rigName+"_R_Tyre_GEO")
		mc.xform(rightTyreGeo, cp = True)
		leftWheelGeo = mc.rename(leftWheelGeo, rigName+"_L_Wheel_GEO")
		mc.xform(leftWheelGeo, cp = True)
		rightWheelGeo = mc.rename(rightWheelGeo, rigName+"_R_Wheel_GEO")
		mc.xform(rightWheelGeo, cp = True)
		axleGeo = mc.rename(axleGeo, rigName+"_Axle_GEO")
		mc.xform(axleGeo, cp = True)

		#Code to delete skinClusters on shock rigs and instead put a parentConstraint
		mc.delete(str(self)+"_r_ShockShaft_GEO", ch = True)
		WheelAxle.unlockChannels(str(self)+"_r_ShockShaft_GEO")
		mc.delete(str(self)+"_r_ShockPiston_GEO", ch = True)
		WheelAxle.unlockChannels(str(self)+"_r_ShockPiston_GEO")
		mc.delete(str(self)+"_l_ShockShaft_GEO", ch = True)
		WheelAxle.unlockChannels(str(self)+"_l_ShockShaft_GEO")
		mc.delete(str(self)+"_l_ShockPiston_GEO", ch = True)
		WheelAxle.unlockChannels(str(self)+"_l_ShockPiston_GEO")

		mc.parentConstraint(str(self)+"_r_ShockPiston_JNT", str(self)+"_r_ShockPiston_GEO", maintainOffset = True)
		mc.parentConstraint(str(self)+"_r_ShockShaft_JNT", str(self)+"_r_ShockShaft_GEO", maintainOffset = True)
		mc.parentConstraint(str(self)+"_l_ShockPiston_JNT", str(self)+"_l_ShockPiston_GEO", maintainOffset = True)
		mc.parentConstraint(str(self)+"_l_ShockShaft_JNT", str(self)+"_l_ShockShaft_GEO", maintainOffset = True)

		#Code to preserve shock connection locators
		leftShockConnectLocator = mc.rename(str(self)+"_WheelAxle_l_Axle_ShockConnect_LOC", rigName + "_L_ShockConnect_LOC")
		mc.setAttr(leftShockConnectLocator+".visibility", 0)
		leftAxleShockPos = mc.getAttr(leftShockConnectLocator+".worldPosition[0]")[0]
		leftShockConnectLocator = mc.parent(leftShockConnectLocator, world = True)[0]
		mc.delete(str(self)+"_WheelAxle_leftAxle_JNT")

		rightShockConnectLocator = mc.rename(str(self)+"_WheelAxle_r_Axle_ShockConnect_LOC", rigName + "_R_ShockConnect_LOC")
		mc.setAttr(rightShockConnectLocator+".visibility", 0)
		rightAxleShockPos = mc.getAttr(rightShockConnectLocator+".worldPosition[0]")[0]
		rightShockConnectLocator = mc.parent(rightShockConnectLocator, world = True)[0]
		mc.delete(str(self)+"_WheelAxle_rightAxle_JNT")

		axleShockLocatorGroup = mc.group(leftShockConnectLocator, rightShockConnectLocator, n = rigName+"_axleShockLocator_GRP")

		#Code to group seperated meshes in proper order
		#LEFT
		leftWheelRollGeoGroup = mc.group(leftWheelGeo, leftTyreGeo, n = rigName+"_L_WheelRoll_GRP")
		leftWheelRotationGeoGroup = mc.group(leftWheelRollGeoGroup, n = rigName+"_L_WheelRot_GRP")
		leftWheelGroup = mc.group(leftWheelRotationGeoGroup, n = rigName+"_L_WheelGeo_GRP")

		#RIGHT
		rightWheelRollGeoGroup = mc.group(rightWheelGeo, rightTyreGeo, n = rigName+"_R_WheelRoll_GRP")
		rightWheelRotationGeoGroup = mc.group(rightWheelRollGeoGroup, n = rigName+"_R_WheelRot_GRP")
		rightWheelGroup = mc.group(rightWheelRotationGeoGroup, n = rigName+"_R_WheelGeo_GRP")

		#AXLE
		axleGroup = mc.group(axleGeo, n = rigName+"_AxleGeo_GRP")
		mc.xform(axleGroup, cp = True)

		#Renaming Shock Rigs
		leftShockParts = mc.listRelatives(str(self)+"_l_Shock_Rig_GRP", allDescendents = True)
		for part in leftShockParts:
			mc.rename(part, rigName+part.partition(str(self))[2])
		leftShockRigGroup = mc.rename(str(self)+"_l_Shock_Rig_GRP", rigName+"_l_Shock_Rig_GRP")
		leftShockGeoGroup = mc.parent(rigName+"_l_ShockGEO_GRP", w = True)

		rightShockParts =  mc.listRelatives(str(self)+"_r_Shock_Rig_GRP", allDescendents = True)
		for part in rightShockParts:
			mc.rename(part, rigName+part.partition(str(self))[2])
		rightShockRigGroup = mc.rename(str(self)+"_r_Shock_Rig_GRP", rigName+"_r_Shock_Rig_GRP")
		rightShockGeoGroup = mc.parent(rigName+"_r_ShockGEO_GRP", w = True)

		#Renaming WheelAxle Connection Rigs
		leftWheelAxleConnectParts = mc.listRelatives(str(self)+"_l_WheelAxleConnect_GRP", allDescendents = True)
		for part in leftWheelAxleConnectParts:
			print part
			mc.rename(part, rigName+part.partition(str(self))[2])
		leftWheelAxleConnectGroup = mc.rename(str(self)+"_l_WheelAxleConnect_GRP", rigName+"_l_WheelAxleConnect_GRP")
		mc.setAttr(leftWheelAxleConnectGroup+".visibility", 0)
		leftWheelAxleConnectGeoGroup = mc.parent(rigName+"_l_WheelAxleConnectGeo_GRP", w = True)

		rightWheelAxleConnectParts = mc.listRelatives(str(self)+"_r_WheelAxleConnect_GRP", allDescendents = True)
		for part in rightWheelAxleConnectParts:
			print part
			mc.rename(part, rigName+part.partition(str(self))[2])
		rightWheelAxleConnectGroup = mc.rename(str(self)+"_r_WheelAxleConnect_GRP", rigName+"_r_WheelAxleConnect_GRP")
		mc.setAttr(rightWheelAxleConnectGroup+".visibility", 0)
		rightWheelAxleConnectGeoGroup = mc.parent(rigName+"_r_WheelAxleConnectGeo_GRP", w = True)

	#Code to place controls and control groups at each wheel
		#LEFT WHEEL
		LeftWheelPos = mc.getAttr(leftWheelGroup+".rotatePivot")[0]
		leftWheelControl = mc.circle(nr = (0, 1, 0), c = (0,0,0), r = 2, name = rigName+"_l_wheel_CTL")[0]
		mc.setAttr(leftWheelControl+".translate", LeftWheelPos[0], 0, LeftWheelPos[2])
		mc.makeIdentity(leftWheelControl, apply=True, t=1, r=1, s=1, n=0)
		mc.setAttr(leftWheelControl+".overrideEnabled", 1)
		mc.setAttr(leftWheelControl+".overrideColor", 6)
		leftWheelControlGroup = mc.group(leftWheelControl, n = rigName+"_L_WheelControl_GRP")
		leftWheelRotationControl = mc.circle(nr = (1,0,0), c = (0,0,0), r = 1.5, name = rigName+"_l_wheelRot_CTL")[0]
		mc.setAttr(leftWheelRotationControl+".translate", LeftWheelPos[0], LeftWheelPos[1], LeftWheelPos[2])
		mc.makeIdentity(leftWheelRotationControl, apply = True, t = 1, r = 1, s = 1, n = 0)
		mc.connectAttr(leftWheelRotationControl+".rotateX", leftWheelRotationGeoGroup+".rotateX")
		mc.setAttr(leftWheelRotationControl+".overrideEnabled", 1)
		mc.setAttr(leftWheelRotationControl+".overrideColor", 15)
		leftWheelRotationControlGroup = mc.group(leftWheelRotationControl, n = rigName+"_l_wheelRotControl_GRP")
		leftWheelSquashControl =mc.circle(nr = (0, 1, 0), c = (0,0,0), r = .5, name = rigName+"_l_wheelSquash_CTL")[0]
		mc.setAttr(leftWheelSquashControl+".translate", LeftWheelPos[0], 0, LeftWheelPos[2])
		mc.makeIdentity(leftWheelSquashControl, apply = True, t = 1, r = 1, s = 1, n = 0)
		mc.setAttr(leftWheelRotationControl+".overrideEnabled", 1)
		mc.setAttr(leftWheelRotationControl+".overrideColor", 19)
		leftWheelSquashControlGroup = mc.group(leftWheelSquashControl, n = rigName+"_L_WheelSquash_GRP")
			
		#RIGHT WHEEL
		RightWheelPos = mc.getAttr(rightWheelGroup+".rotatePivot")[0]
		rightWheelControl = mc.circle(nr = (0, 1, 0), c = (0,0,0), r = 2, name = rigName+"_r_wheel_CTL")[0]
		mc.setAttr(rightWheelControl+".translate", RightWheelPos[0], 0, RightWheelPos[2])
		mc.makeIdentity(rightWheelControl, apply=True, t=1, r=1, s=1, n=0)
		mc.setAttr(rightWheelControl+".overrideEnabled", 1)
		mc.setAttr(rightWheelControl+".overrideColor", 13)
		rightWheelControlGroup = mc.group(rightWheelControl, n = rigName+"_R_WheelControl_GRP")
		rightWheelRotationControl = mc.circle(nr = (1,0,0), c = (0,0,0), r = 1.5, name = rigName+"_r_wheelRot_CTL")[0]
		mc.setAttr(rightWheelRotationControl+".translate", RightWheelPos[0], RightWheelPos[1], RightWheelPos[2])
		mc.makeIdentity(rightWheelRotationControl, apply = True, t = 1, r = 1, s = 1, n = 0)
		mc.connectAttr(rightWheelRotationControl+".rotateX", rightWheelRotationGeoGroup+".rotateX")
		mc.setAttr(rightWheelRotationControl+".overrideEnabled", 1)
		mc.setAttr(rightWheelRotationControl+".overrideColor", 12)
		rightWheelRotationControlGroup = mc.group(rightWheelRotationControl, n = rigName+"_r_wheelRotControl_GRP")
		rightWheelSquashControl =mc.circle(nr = (0, 1, 0), c = (0,0,0), r = .5, name = rigName+"_r_wheelSquash_CTL")[0]
		mc.setAttr(rightWheelSquashControl+".translate", RightWheelPos[0], 0, RightWheelPos[2])
		mc.makeIdentity(rightWheelSquashControl, apply = True, t = 1, r = 1, s = 1, n = 0)
		mc.setAttr(rightWheelSquashControl+".overrideEnabled", 1)
		mc.setAttr(rightWheelSquashControl+".overrideColor", 20)
		rightWheelSquashControlGroup = mc.group(rightWheelSquashControl, n = rigName+"_R_WheelSquash_GRP")

	#Parent constraint wheel groups to controls		
	 	mc.parentConstraint(leftWheelControl, leftWheelGroup, maintainOffset = True)
	 	mc.parentConstraint(leftWheelControl, rigName+"_l_wheelConnectDistance_LOC", maintainOffset = True)
	 	mc.parentConstraint(rightWheelControl, rightWheelGroup, maintainOffset = True)
	 	mc.parentConstraint(rightWheelControl, rigName+"_r_wheelConnectDistance_LOC", maintainOffset = True)
	
	#Setup Axle Control
	 	wheelAxleControl = mc.circle(nr = (0,1,0), c = (0,0,0), r = 3, name = rigName + "_wheelAxle_CTL")[0]
	 	mc.setAttr(wheelAxleControl+".overrideEnabled", 1)
	 	mc.setAttr(wheelAxleControl+".overrideColor", 17)
	 	axleControl = mc.circle(nr = (0,1,0), c = (0,0,0), r = 2, name = rigName + "_axle_CTL")[0]
	 	mc.setAttr(axleControl+".overrideEnabled", 1)
	 	mc.setAttr(axleControl+".overrideColor", 22)
		AxlePosition = mc.getAttr(axleGroup+".rotatePivot")[0]
	 	mc.setAttr(wheelAxleControl+".translate", AxlePosition[0], 0, AxlePosition[2])
	 	mc.makeIdentity(wheelAxleControl, apply=True, t=1, r=1, s=1, n=0)
	 	mc.setAttr(axleControl+".translate", AxlePosition[0], AxlePosition[1], AxlePosition[2])
	 	mc.makeIdentity(axleControl, apply=True, t=1, r=1, s=1, n=0)
	 	mc.parentConstraint(axleControl, axleGroup, maintainOffset = True)
	 	axleControlGroup = mc.group(axleControl, n = rigName+"_axleControl_GRP")
	 	mc.parent(axleControlGroup, wheelAxleControl)
	 	axleControlGroup = mc.group(wheelAxleControl, n = rigName+"_wheelAxleControl_GRP")
	 	mc.parent([leftWheelControlGroup, rightWheelControlGroup], wheelAxleControl)
	 	mc.parent(axleControlGroup, worldControl)
	
	#setup Wheel Squash

	# 	#LEFT WHEEL
		LeftWheelLatticeMesh = mc.lattice(leftTyreGeo, divisions = (10,10,10), objectCentered = True, ldv = (2,2,2), ol = True, name = rigName+"_L_wheel_LAT")
		leftWheelClusterHandle = mc.cluster(LeftWheelLatticeMesh[1]+".pt[0:9][0][0:10]", name = rigName+"_L_wheel_CLH")[1]
		mc.setAttr(leftWheelClusterHandle+".visibility", 0)
		leftWheelClusterHandleGroup = mc.group(leftWheelClusterHandle, n = rigName+"_L_WheelCluster_GRP")
		mc.setAttr(LeftWheelLatticeMesh[1]+".visibility", 0)
		leftWheelDistanceDimension = mc.distanceDimension(sp = (0,0,0), ep = mc.getAttr(leftWheelControl+".rotatePivot")[0])
		leftWheelDistanceLocators = mc.listConnections(leftWheelDistanceDimension)
		leftWheelStartingDistanceLocator = mc.rename(leftWheelDistanceLocators[0], rigName+"_L_WheelSP_LOC")
		mc.setAttr(leftWheelStartingDistanceLocator+".visibility", 0)
		mc.setAttr(leftWheelStartingDistanceLocator+".translate", LeftWheelPos[0], LeftWheelPos[1], LeftWheelPos[2])
		leftWheelEndingDistanceLocator = mc.rename(leftWheelDistanceLocators[1], rigName+"_L_WheelEP_LOC")
		mc.setAttr(leftWheelEndingDistanceLocator+".visibility", 0)
		leftWheelDistanceDimension = mc.rename(leftWheelDistanceDimension, rigName+"_L_Wheel_DD")
		mc.connectAttr(leftWheelSquashControl+".translateY", leftWheelEndingDistanceLocator+".translateY")
		mc.setAttr(leftWheelDistanceDimension+".visibility", 0)

		leftWheelRadius = mc.getAttr(leftWheelDistanceDimension+".distance")
		leftWheelScaleCompensate = mc.shadingNode("multiplyDivide", asUtility = True, n = rigName + "_L_WheelScaleComp_MDI")
		mc.connectAttr(leftWheelDistanceDimension+".distance", leftWheelScaleCompensate+".input1X")
		mc.connectAttr(worldControl+".scaleY", leftWheelScaleCompensate+".input2X")
		mc.setAttr(leftWheelScaleCompensate+".operation", 2)
		leftWheelScaleCondition = mc.shadingNode("condition", asUtility = True, n = rigName+"_L_WheelScale_CON")
		mc.connectAttr(leftWheelScaleCompensate+".outputX", leftWheelScaleCondition+".colorIfFalseR")
		mc.connectAttr(leftWheelScaleCompensate+".outputX", leftWheelScaleCondition+".firstTerm")
		mc.setAttr(leftWheelScaleCondition+".secondTerm", leftWheelRadius)
		mc.setAttr(leftWheelScaleCondition+".operation", 2)
		mc.setAttr(leftWheelScaleCondition+".colorIfTrueR", leftWheelRadius)
		leftWheelSquash = mc.shadingNode("multiplyDivide", asUtility = True, n = rigName+"_L_WheelSquash_MDI")
		mc.setAttr(leftWheelSquash+".input1X", leftWheelRadius)
		mc.connectAttr(leftWheelScaleCondition+".outColorR", leftWheelSquash+".input2X")
		mc.setAttr(leftWheelSquash+".operation", 2)
		mc.connectAttr(leftWheelSquash+".outputX", leftWheelClusterHandle+".scaleX")
		mc.connectAttr(leftWheelSquash+".outputX", leftWheelClusterHandle+".scaleZ")

		leftWheelTranslationCondition = mc.shadingNode("condition", asUtility = True, n = rigName+"_L_WheelTranslation_CON")
		mc.setAttr(leftWheelTranslationCondition+".colorIfFalseR", 0)
		mc.connectAttr(leftWheelSquashControl+".rotate", leftWheelClusterHandle+".rotate")
		mc.connectAttr(leftWheelSquashControl+".translateY", leftWheelTranslationCondition+".firstTerm")
		mc.connectAttr(leftWheelSquashControl+".translateY", leftWheelTranslationCondition+".colorIfTrueR")
		mc.setAttr(leftWheelTranslationCondition+".operation", 2)	
		mc.connectAttr(leftWheelTranslationCondition+".outColorR", leftWheelClusterHandle+".translateY")

	# 	#RIGHT WHEEL
		RightWheelLatticeMesh = mc.lattice(rightTyreGeo, divisions = (10,10,10), objectCentered = True, ldv = (2,2,2), ol = True, name = rigName+"_R_wheel_LAT")
		rightWheelClusterHandle = mc.cluster(RightWheelLatticeMesh[1]+".pt[0:9][0][0:10]", name = rigName+"_R_wheel_CLH")[1]
		mc.setAttr(rightWheelClusterHandle+".visibility", 0)
		mc.setAttr(RightWheelLatticeMesh[1]+".visibility", 0)
		rightWheelClusterHandleGroup = mc.group(rightWheelClusterHandle, n = rigName+"_R_WheelCluster_GRP")
		rightWheelDistanceDimension = mc.distanceDimension(sp = (0,0,0), ep = mc.getAttr(rightWheelControl+".rotatePivot")[0])
		rightWheelDistanceLocators = mc.listConnections(rightWheelDistanceDimension)
		rightWheelStartingDistanceLocator = mc.rename(rightWheelDistanceLocators[0], rigName+"_R_WheelSP_LOC")
		mc.setAttr(rightWheelStartingDistanceLocator+".translate", RightWheelPos[0], RightWheelPos[1], RightWheelPos[2])
		rightWheelEndingDistanceLocator = mc.rename(rightWheelDistanceLocators[1], rigName+"_R_WheelEP_LOC")
		rightWheelDistanceDimension = mc.rename(rightWheelDistanceDimension, rigName+"_R_Wheel_DD")
		mc.connectAttr(rightWheelSquashControl+".translateY", rightWheelEndingDistanceLocator+".translateY")
		mc.setAttr(rightWheelStartingDistanceLocator+".visibility", 0)
		mc.setAttr(rightWheelEndingDistanceLocator+".visibility", 0)
		mc.setAttr(rightWheelDistanceDimension+".visibility", 0)

		rightWheelRadius = mc.getAttr(rightWheelDistanceDimension+".distance")
		rightWheelScaleCompensate = mc.shadingNode("multiplyDivide", asUtility = True, n = rigName + "_R_WheelScaleComp_MDI")
		mc.connectAttr(rightWheelDistanceDimension+".distance", rightWheelScaleCompensate+".input1X")
		mc.connectAttr(worldControl+".scaleY", rightWheelScaleCompensate+".input2X")
		mc.setAttr(rightWheelScaleCompensate+".operation", 2)
		rightWheelScaleCondition = mc.shadingNode("condition", asUtility = True, n = rigName+"_R_WheelScale_CON")
		mc.connectAttr(rightWheelScaleCompensate+".outputX", rightWheelScaleCondition+".colorIfFalseR")
		mc.connectAttr(rightWheelScaleCompensate+".outputX", rightWheelScaleCondition+".firstTerm")
		mc.setAttr(rightWheelScaleCondition+".secondTerm", rightWheelRadius)
		mc.setAttr(rightWheelScaleCondition+".operation", 2)
		mc.setAttr(rightWheelScaleCondition+".colorIfTrueR", rightWheelRadius)
		rightWheelSquash = mc.shadingNode("multiplyDivide", asUtility = True, n = rigName+"_R_WheelSquash_MDI")
		mc.setAttr(rightWheelSquash+".input1X", rightWheelRadius)
		mc.connectAttr(rightWheelScaleCondition+".outColorR", rightWheelSquash+".input2X")
		mc.setAttr(rightWheelSquash+".operation", 2)
		mc.connectAttr(rightWheelSquash+".outputX", rightWheelClusterHandle+".scaleX")
		mc.connectAttr(rightWheelSquash+".outputX", rightWheelClusterHandle+".scaleZ")

		rightWheelTranslationCondition = mc.shadingNode("condition", asUtility = True, n = rigName+"_R_WheelTranslation_CON")
		mc.setAttr(rightWheelTranslationCondition+".colorIfFalseR", 0)
		mc.connectAttr(rightWheelSquashControl+".rotate", rightWheelClusterHandle+".rotate")
		mc.connectAttr(rightWheelSquashControl+".translateY", rightWheelTranslationCondition+".firstTerm")
		mc.connectAttr(rightWheelSquashControl+".translateY", rightWheelTranslationCondition+".colorIfTrueR")
		mc.setAttr(rightWheelTranslationCondition+".operation", 2)
		mc.connectAttr(rightWheelTranslationCondition+".outColorR", rightWheelClusterHandle+".translateY")

		#disconnecting Attrtibutes
		mc.disconnectAttr(str(self)+"_WheelAxle_l_PMA.output2Dx", leftShockConnectLocator+".translateX")
		mc.disconnectAttr(str(self)+"_WheelAxle_r_PMA.output2Dx", rightShockConnectLocator+".translateX")

		#Parenting various parts
		#LEFT WHEEL
		mc.parent(LeftWheelLatticeMesh[1], leftWheelControl)
		mc.parent(LeftWheelLatticeMesh[2], leftWheelControl)
		mc.parent(leftWheelClusterHandleGroup, worldGroup)
		mc.parent(leftWheelAxleConnectGroup, worldControl)
		LeftWheelDistanceGroup = mc.group(leftWheelDistanceDimension, leftWheelStartingDistanceLocator, leftWheelEndingDistanceLocator, n = rigName+"_L_WheelDist_GRP")
		mc.parent(LeftWheelDistanceGroup, leftWheelControlGroup)
		mc.parent(leftWheelSquashControlGroup, leftWheelControl)
		mc.parent(leftWheelRotationControlGroup, leftWheelControl)
		#RIGHT WHEEL
		mc.parent(RightWheelLatticeMesh[1], rightWheelControl)
		mc.parent(RightWheelLatticeMesh[2], rightWheelControl)
		mc.parent(rightWheelClusterHandleGroup, worldGroup)
		RightWheelDistanceGroup = mc.group(rightWheelDistanceDimension, rightWheelStartingDistanceLocator, rightWheelEndingDistanceLocator, n = rigName+"_R_WheelDist_GRP")
		mc.parent(RightWheelDistanceGroup, rightWheelControlGroup)
		mc.parent(rightWheelSquashControlGroup, rightWheelControl)
		mc.parent(rightWheelRotationControlGroup, rightWheelControl)

		#General parts
		GeoGroup = mc.group(leftWheelGroup, rightWheelGroup, axleGroup, leftShockGeoGroup, rightShockGeoGroup, leftWheelAxleConnectGeoGroup, rightWheelAxleConnectGeoGroup, n = rigName+"_WheelAxleGeo_GRP")
		
		mc.parent(axleShockLocatorGroup, axleControl)
		
		mc.parent(GeoGroup, worldGroup)
		
		mc.parent(leftShockRigGroup, wheelAxleControl)
		mc.parent(rightShockRigGroup, wheelAxleControl)
		
		mc.parent(leftWheelAxleConnectGroup, wheelAxleControl)
		mc.parent(rightWheelAxleConnectGroup, wheelAxleControl)

		#deleting original group
		mc.delete(str(self)+"_WheelAxleSystem_GRP")

		#	applying original shock positions
		mc.setAttr(rigName+"_L_ShockConnect_LOC.translate", leftAxleShockPos[0], leftAxleShockPos[1], leftAxleShockPos[2])
		mc.makeIdentity(rigName+"_L_ShockConnect_LOC", apply=True, t=1, r=1, s=1, n=0)
		mc.setAttr(rigName+"_R_ShockConnect_LOC.translate", rightAxleShockPos[0], rightAxleShockPos[1], rightAxleShockPos[2])
		mc.makeIdentity(rigName+"_R_ShockConnect_LOC", apply=True, t=1, r=1, s=1, n=0)

		#renaming useful Multiply Divide Nodes
		print mc.rename(str(self)+"_r_Shocks_rig_MDI", rigName+"_r_Shocks_rig_MDI")
		print mc.rename(str(self)+"_l_Shocks_rig_MDI", rigName+"_l_Shocks_rig_MDI")

		print mc.rename(str(self)+"_r_Shocks_Spring_rig_MDI", rigName+"_r_Shocks_Spring_rig_MDI")
		print mc.rename(str(self)+"_l_Shocks_Spring_rig_MDI", rigName+"_l_Shocks_Spring_rig_MDI")

		print mc.rename(str(self)+"_r_wheelAxleConnect_MDI", rigName+"_r_wheelAxleConnect_MDI")
		print mc.rename(str(self)+"_l_wheelAxleConnect_MDI", rigName+"_l_wheelAxleConnect_MDI")

		print mc.rename(str(self)+"_l_Shocks_piston_MDI", rigName+"_l_Shocks_Piston_MDI")
		print mc.rename(str(self)+"_r_Shocks_Piston_MDI", rigName+"_r_Shocks_Piston_MDI")

		print mc.rename(str(self)+"_l_wheelAxleConnectScaleCompensate_MDI", rigName+"_l_wheelAxleConnectScaleCompensate_MDI")
		print mc.rename(str(self)+"_r_wheelAxleConnectScaleCompensate_MDI", rigName+"_r_wheelAxleConnectScaleCompensate_MDI")

		print mc.rename(str(self)+"_l_Shocks_ShockSpring_POLY", rigName+"_l_Shocks_ShockSpring_POLY")
		print mc.rename(str(self)+"_r_Shocks_ShockSpring_POLY", rigName+"_r_Shocks_ShockSpring_POLY")

	#	Scale Compensation
		mc.scaleConstraint(worldControl, GeoGroup, maintainOffset = True)
		
		mc.disconnectAttr(rigName+"_r_Shoc_Position_CTL.scaleY", rigName+"_r_Shocks_rig_MDI.input1X")
		mc.connectAttr (worldControl+".scaleY", rigName+"_r_Shocks_rig_MDI.input1X")
		
		mc.disconnectAttr(rigName+"_r_wheelAxleConnect_CTL.scaleX", rigName+"_r_wheelAxleConnectScaleCompensate_MDI.input2X")
		mc.connectAttr(worldControl+".scaleY", rigName+"_r_wheelAxleConnectScaleCompensate_MDI.input2X")

		mc.disconnectAttr(rigName+"_l_Shoc_Position_CTL.scaleY", rigName+"_l_Shocks_rig_MDI.input1X")
		mc.connectAttr(worldControl+".scaleY", rigName+"_l_Shocks_rig_MDI.input1X")
		
		mc.disconnectAttr(rigName+"_l_wheelAxleConnect_CTL.scaleX", rigName+"_l_wheelAxleConnectScaleCompensate_MDI.input1X")
		mc.connectAttr(worldControl+".scaleY", rigName+"_l_wheelAxleConnectScaleCompensate_MDI.input1X")

	#	Code to connect Wheel rotations based on world translation
		mc.addAttr(wheelAxleControl, longName = "Roll", attributeType = "float", minValue = 0.1, defaultValue = 1.0, keyable = True)
		SlipMultiplyNode = mc.shadingNode("multiplyDivide", asUtility = True, n = rigName+"_Slip_MDI")
		mc.setAttr(SlipMultiplyNode+".operation", 1)
		mc.connectAttr(wheelAxleControl+".Roll", SlipMultiplyNode+".input1X")
		mc.setAttr(SlipMultiplyNode+".input2X", leftWheelRadius)
		pieMultiplierNode = mc.shadingNode("multiplyDivide", asUtility = True, n = rigName+"_pieMultiplier_MDI")
		mc.setAttr(pieMultiplierNode+".operation", 1)
		mc.setAttr(pieMultiplierNode+".input1X", 6.283)
		mc.connectAttr(SlipMultiplyNode+".outputX", pieMultiplierNode+".input2X")
		translationDivideNode = mc.shadingNode("multiplyDivide", asUtility = True, n = rigName+"_TranslationDivide_MDI")
		mc.setAttr(translationDivideNode+".operation", 2)
		mc.connectAttr(worldControl+".translateZ", translationDivideNode+".input1X")
		mc.connectAttr(pieMultiplierNode+".outputX", translationDivideNode+".input2X")
		radianConvertorNode = mc.shadingNode("multiplyDivide", asUtility = True, n = rigName+"_RadianConvertor_MDI")
		mc.setAttr(radianConvertorNode+".operation", 1)
		mc.setAttr(radianConvertorNode+".input2X", 360.0)
		mc.connectAttr(translationDivideNode+".outputX", radianConvertorNode+".input1X")
		rollSwitchCondition = mc.shadingNode("condition", asUtility = True, n = rigName+"_RollSwitch_CON")
		mc.connectAttr(worldControl+".RollSwitch", rollSwitchCondition+".firstTerm")
		mc.connectAttr(radianConvertorNode+".outputX", rollSwitchCondition+".colorIfTrueR")
		mc.setAttr(rollSwitchCondition+".secondTerm", 1)
		mc.setAttr(rollSwitchCondition+".colorIfFalseR", 0)

		mc.connectAttr(rollSwitchCondition+".outColorR", leftWheelRollGeoGroup+".rotateX")
		mc.orientConstraint(leftWheelRollGeoGroup, rigName+"_l_axleConnectDistance_LOC", maintainOffset = True, skip = ['y', 'z'])

		mc.connectAttr(rollSwitchCondition+".outColorR", rightWheelRollGeoGroup+".rotateX")
		mc.orientConstraint(rightWheelRollGeoGroup, rigName+"_r_axleConnectDistance_LOC", maintainOffset = True, skip = ['y','z'])

		mc.setAttr(rigName+"_l_wheelAxleConnect_CTL.visibility", 0)
		mc.setAttr(rigName+"_r_wheelAxleConnect_CTL.visibility", 0)

	@staticmethod
	def unlockChannels(mayaObj):
		mc.setAttr(mayaObj+".tx", lock = False)
		mc.setAttr(mayaObj+".ty", lock = False)
		mc.setAttr(mayaObj+".tz", lock = False)
		mc.setAttr(mayaObj+".rx", lock = False)
		mc.setAttr(mayaObj+".ry", lock = False)
		mc.setAttr(mayaObj+".rz", lock = False)
		mc.setAttr(mayaObj+".sx", lock = False)
		mc.setAttr(mayaObj+".sy", lock = False)
		mc.setAttr(mayaObj+".sz", lock = False)

	def changeWheelSize(self, value):
		self.WheelAxleAttributes["Size"] = value/10.0
		mc.setAttr(self.WheelAxleAttributes["Name"]+"_WheelAxle_ATR.WheelSize", value/10.0)

	def changeWheelWidth(self, value):
		self.WheelAxleAttributes["Width"] = value/10.0
		mc.setAttr(self.WheelAxleAttributes["Name"]+"_WheelAxle_ATR.WheelWidth", value/10.0)

	def changeTireType(self, value):
		for obj in self.LeftWheelTypes:
			mc.setAttr(obj+".visibility", 0)
		for obj in self.RightWheelTypes:
			mc.setAttr(obj+".visibility", 0)

		mc.setAttr(self.LeftWheelTypes[value]+".visibility", 1)
		mc.setAttr(self.RightWheelTypes[value] +".visibility", 1)

		self.WheelAxleAttributes["Tire_Type"] = value

	def changeWheelOutShape(self, value):
		self.WheelAxleAttributes["Shape_Values"][0] = value/10.0
		mc.setAttr(self.WheelAxleAttributes["Name"]+"_WheelAxle_ATR.WheelShapeOut", value/10.0)

	def changeWheelMidShape(self, value):
		self.WheelAxleAttributes["Shape_Values"][1] = value/10.0
		mc.setAttr(self.WheelAxleAttributes["Name"]+"_WheelAxle_ATR.WheelShapeMid", value/10.0)

	def changeWheelInShape(self, value):
		self.WheelAxleAttributes["Shape_Values"][2] = value/10.0
		mc.setAttr(self.WheelAxleAttributes["Name"]+"_WheelAxle_ATR.WheelShapeIn", value/10.0)

	def changeWheelCenterShape(self, value):
		self.WheelAxleAttributes["Center_Radius"] = value/10.0
		mc.setAttr(self.WheelAxleAttributes["Name"]+"_WheelAxle_ATR.WheelCenter", value/10.0)

	def changeAxleHeight(self, value):
		self.WheelAxleAttributes["Axle_Height"] =value/10.0
		mc.setAttr(self.WheelAxleAttributes["Name"]+"_WheelAxle_ATR.AxleHeight", value/10.0)

	def changeAxleThickness(self, value):
		self.WheelAxleAttributes["Axle_Thickness"] = value/10.0
		mc.setAttr(self.WheelAxleAttributes["Name"]+"_WheelAxle_ATR.AxleThickness", value/10.0)

	def changeAxleWidth(self, value):
		self.WheelAxleAttributes["Axle_Width"] = value/10.0
		mc.setAttr(self.WheelAxleAttributes["Name"]+"_WheelAxle_ATR.AxleWidth", value/10.0)

	def changeSpringWidth(self, value):
		self.WheelAxleAttributes["Spring_Width"] = value/10.0
		mc.setAttr(self.WheelAxleAttributes["Name"]+"_WheelAxle_ATR.SpringWidth", value/10.0)

	def changeCoilRadius(self, value):
		self.WheelAxleAttributes["Coil_Radius"] = value/10.0
		mc.setAttr(self.WheelAxleAttributes["Name"]+"_WheelAxle_ATR.CoilRadius", value/100.0)

	def changeCoils(self, value):
		self.WheelAxleAttributes["Coils"] = value/10.0
		mc.setAttr(self.WheelAxleAttributes["Name"]+"_WheelAxle_ATR.Coils", value/10.0)

	def changePistonWidth(self, value):
		self.WheelAxleAttributes["Piston_Width"] =value/10.0
		mc.setAttr(self.WheelAxleAttributes["Name"]+"_WheelAxle_ATR.PistonWidth", value/10.0)

	def changeShockDistance(self, value):
		self.WheelAxleAttributes["Shock_Distance"] = value/10.0
		mc.setAttr(self.WheelAxleAttributes["Name"]+"_WheelAxle_ATR.ShockDistance", value/10.0)


class Frame():
	def __init__(self, frameName, frontWheelAxle, backWheelAxle):
		try:
			mc.file("C:/autoRig/Frame.ma", ignoreVersion = True, i = True, rpr = frameName, mergeNamespacesOnClash = True, options = "v=0", type = "mayaAscii", pr = True, ra = True)
		except RuntimeError:
			print "Runtime Error! Aborting!"

		self.FrameAttributes = {}
		self.FrameAttributes["Name"] = frameName
		self.FrameAttributes["Type"] = 0
		self.FrameAttributes["Front_Shock_Height"] = 0.0
		self.FrameAttributes["Back_Shock_Height"] = 0.0
		self.FrameAttributes["Front_Shock_TZ"] = 0.0
		self.FrameAttributes["Back_Shock_TZ"] = 0.0
		self.FrameAttributes["Front_Shock_NW"] = 0.0
		self.FrameAttributes["Back_Shock_NW"] = 0.0
		self.FrameAttributes["Frame_Angle"] = 0.0
		self.FrameAttributes["Frame_Height"] = 0.0
		self.FrameAttributes["Connected_Axles"] = [str(frontWheelAxle), str(backWheelAxle)]

		#CODE TO CONNECT THE FRONT AXLE TO FRAME FRONT AND BACK AXLE TO BACK FRAME

		mc.pointConstraint(frameName+"_frontRightShock_GRP", str(frontWheelAxle)+"_r_Frame_ShockConnect_LOC", maintainOffset = False)
		mc.pointConstraint(frameName+"_frontLeftShock_GRP", str(frontWheelAxle)+"_l_Frame_ShockConnect_LOC", maintainOffset = False)
		mc.pointConstraint(frameName+"_backRightShock_GRP", str(backWheelAxle)+"_r_Frame_ShockConnect_LOC", maintainOffset = False)
		mc.pointConstraint(frameName+"_backLeftShock_GRP", str(backWheelAxle)+"_l_Frame_ShockConnect_LOC", maintainOffset = False)

		frontWheelAxle.WheelAxleAttributes["Frame_Connect"] = 1
		backWheelAxle.WheelAxleAttributes["Frame_Connect"] = 1

		self.FrameTypes = mc.listRelatives(frameName+"_FrameGeos_GRP", children = True)
		print self.FrameTypes

	def __str__(self):
		return self.FrameAttributes["Name"]

	def rename(self, newName):
		oldName = self.FrameAttributes["Name"]
		print oldName
		mc.select(oldName+"*")
		mc.select("*.vtx[*]", d = True)
		mc.select("*Shape*", d = True)
		mc.select("*Group*", d = True)
		mc.select("*group*", d = True)
		selectedObjects = mc.ls(sl = True)
		print selectedObjects
		for obj in selectedObjects:
			mc.lockNode(obj, lock = False)
		 	newNameSuffix = obj.rpartition(oldName)[2]
			mc.rename(obj, newName + newNameSuffix)
		
		self.FrameAttributes["Name"] = newName
		print "Objects Renamed"

	def deleteFrameObject(self):
		mc.selectType(allComponents = False)
		mc.select(self.FrameAttributes["Name"]+"*")

		mc.delete()
		mc.select(self.FrameAttributes["Name"]+"*")
		mc.delete()
		mc.setAttr(self.FrameAttributes["Connected_Axles"][0]+"_r_Frame_ShockConnect_LOC.translate", 0,0,0)
		mc.setAttr(self.FrameAttributes["Connected_Axles"][0]+"_l_Frame_ShockConnect_LOC.translate", 0,0,0)
		mc.setAttr(self.FrameAttributes["Connected_Axles"][1]+"_r_Frame_ShockConnect_LOC.translate", 0,0,0)
		mc.setAttr(self.FrameAttributes["Connected_Axles"][1]+"_l_Frame_ShockConnect_LOC.translate", 0,0,0)

	def resetFrameObject(self):
		self.FrameAttributes["Type"] = 0
		self.FrameAttributes["Front_Shock_Height"] = 0.0
		self.FrameAttributes["Back_Shock_Height"] = 0.0
		self.FrameAttributes["Front_Shock_TZ"] = 0.0
		self.FrameAttributes["Back_Shock_TZ"] = 0.0
		self.FrameAttributes["Front_Shock_NW"] = 0.0
		self.FrameAttributes["Back_Shock_NW"] = 0.0
		self.FrameAttributes["Frame_Angle"] = 0.0
		self.FrameAttributes["Frame_Height"] = 0.0

		mc.setAttr(self.FrameAttributes["Name"]+"_FrameControl_CRV.FrontShockHeight", 0)
		mc.setAttr(self.FrameAttributes["Name"]+"_FrameControl_CRV.FrontFrameTZ", 0)
		mc.setAttr(self.FrameAttributes["Name"]+"_FrameControl_CRV.FrontFrameNarrowWide", 0)
		mc.setAttr(self.FrameAttributes["Name"]+"_FrameControl_CRV.BackShockHeight", 0)
		mc.setAttr(self.FrameAttributes["Name"]+"_FrameControl_CRV.BackFrameTZ", 0)
		mc.setAttr(self.FrameAttributes["Name"]+"_FrameControl_CRV.BackFrameNarrowWide", 0)
		mc.setAttr(self.FrameAttributes["Name"]+"_FrameControl_CRV.FrameAngle", 0)
		mc.setAttr(self.FrameAttributes["Name"]+"_FrameControl_CRV.FrameHeight", 0)

	def bakeFrame(self, bakeName, worldGroup):
		FrameType = self.FrameAttributes["Type"]

		FrameGeos = mc.listRelatives(str(self)+"_FrameGeos_GRP", children = True)
		for i in range(len(FrameGeos)):
			if i != FrameType:
				print "come Frame"
				mc.delete(FrameGeos[i])

		frameGeo = mc.rename(FrameGeos[FrameType], bakeName+"_Frame_GEO")
		frameGeoGroup = mc.rename(mc.listRelatives(frameGeo, parent = True)[0], bakeName+"_FrameGeo_GRP")
		mc.parent(frameGeoGroup, w = True)
		mc.delete(frameGeo, ch = True)

		mc.delete(str(self)+"*")

		mc.parent(frameGeoGroup, worldGroup)

	def rigFrame(self, worldControl, rigName = "Test"):
		FrameType = self.FrameAttributes["Type"]

		#Generating frame geos
		FrameGeos = mc.listRelatives(str(self)+"_FrameGeos_GRP", children = True)
		for i in range(len(FrameGeos)):
			if i != FrameType:
				print "come Frame!"
				mc.delete(FrameGeos[i])

		mc.delete(FrameGeos[FrameType], ch = True)

		mc.parent(FrameGeos[FrameType], w = True)

		worldGroup = mc.listRelatives(worldControl, parent = True)[0]

		mc.delete(str(self)+"_multiplyDivide4")

		#Extracting locators and cleaning up controls
		frameShockConnectorGroup = mc.rename(str(self)+"_FrameShockConnect_GRP", rigName+"_FrameShockConnect_GRP")
		frameShockConnectorGroup = mc.parent(frameShockConnectorGroup, w = True)[0]
		mc.setAttr(frameShockConnectorGroup+".visibility", 0)
		mc.delete(str(self)+"_FrameShockConnect_GRP_parentConstraint1")
		for obj in mc.listRelatives(frameShockConnectorGroup, children = True):
			mc.rename(obj, rigName+obj.partition(str(self))[2])

		#Generating frame controls
		frameGeo = mc.rename(FrameGeos[FrameType], rigName+"_Frame_GEO")
		mc.xform(frameGeo, cp = True)
		framePos = mc.getAttr(frameGeo+".rotatePivot")[0]
		frameGeoGroup = mc.group(frameGeo, n = rigName+"_FrameGeo_GRP")
		frameControl = mc.circle(nr = (0, 1, 0), c = (0,0,0), r = 4, name =rigName+"_Frame_CTL")[0]
		mc.setAttr(frameControl+".translate", framePos[0], framePos[1], framePos[2])
		mc.setAttr(frameControl+".overrideEnabled", 1)
		mc.setAttr(frameControl+".overrideColor", 17)
		mc.makeIdentity(frameControl, apply=True, t=1, r=1, s=1, n=0)
		frameControlGroup = mc.group(frameControl, n = rigName+"_FrameControl_GRP")

		mc.delete(str(self)+"_FrameRig_GRP")

		mc.parentConstraint(frameControl, frameGeo, maintainOffset = True)
		mc.parentConstraint(frameControl, frameShockConnectorGroup, maintainOffset = True)

		mc.parent(frameGeoGroup, worldGroup)
		mc.parent(frameShockConnectorGroup, worldControl)
		mc.parent(frameControlGroup, worldControl)

	def changeFrameType(self, value):
		for obj in self.FrameTypes:
			mc.setAttr(obj+".visibility", 0)

		mc.setAttr(obj+".visibility", 0)
		self.FrameAttributes["Type"] = value

	def changeFrameFrontShockHeight(self, value):
		self.FrameAttributes["Front_Shock_Height"] = value/10.0
		mc.setAttr(self.FrameAttributes["Name"]+"_FrameControl_CRV.FrontShockHeight", value/10.0)

	def changeFrameFrontShockTZ(self, value):
		self.FrameAttributes["Front_Shock_TZ"] = value/10.0
		mc.setAttr(self.FrameAttributes["Name"]+"_FrameControl_CRV.FrontFrameTZ", value/10.0)

	def changeFrameFrontShockNW(self, value):
		self.FrameAttributes["Front_Shock_NW"] = value/10.0
		mc.setAttr(self.FrameAttributes["Name"]+"_FrameControl_CRV.FrontFrameNarrowWide", value/10.0)		

	def changeFrameBackShockHeight(self, value):
		self.FrameAttributes["Back_Shock_Height"] = value/10.0
		mc.setAttr(self.FrameAttributes["Name"]+"_FrameControl_CRV.BackShockHeight", value/10.0)

	def changeFrameBackShockTZ(self, value):
		self.FrameAttributes["Back_Shock_TZ"] = value/10.0
		mc.setAttr(self.FrameAttributes["Name"]+"_FrameControl_CRV.BackFrameTZ", value/10.0)

	def changeFrameBackShockNW(self, value):
		self.FrameAttributes["Back_Shock_NW"] = value/10.0
		mc.setAttr(self.FrameAttributes["Name"]+"_FrameControl_CRV.BackFrameNarrowWide", value/10.0)

	def changeFrameAngle(self, value):
		self.FrameAttributes["Frame_Angle"] = value*1.0
		mc.setAttr(self.FrameAttributes["Name"]+"_FrameControl_CRV.FrameAngle", value*1.0)

	def changeFrameHeight(self, value):
		self.FrameAttributes["Frame_Height"] = value/10.0
		mc.setAttr(self.FrameAttributes["Name"]+"_FrameControl_CRV.FrameHeight", value/10.0)
		

MainUI = Main_UI()

MainUI.show()